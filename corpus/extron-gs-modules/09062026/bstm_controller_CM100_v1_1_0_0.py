from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInput': {'Parameters': ['Input'], 'Status': {}},
            'CommunicationMode': {'Parameters': ['ID'], 'Status': {}},
            'InputEDID': {'Parameters': ['Input'], 'Status': {}},
            'OutputEthernetLinkStatus': {'Parameters': ['Output'], 'Status': {}},
            'OutputHDR': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'SetVideowallOutput': {'Parameters': ['Output', 'Rows', 'Columns', 'Rows Position', 'Colums Postion'], 'Status': {}},
            'TieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
        }

        self.getOutputEthernetLinkStatus = re.compile(b'Multicast IP:[\S\s]+Channel:[\S\s]+Ethernet Link Status:[\s]+(on|off)[\s]+Video Status:[\S\s]+Please Enter command:')

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 'AUDORG',
            'Analog': 'AUDANA',
            'Auto': 'AUDAUTO'
        }

        input = int(qualifier['Input'])
        if 1 <= input <= 762:
            AudioInputCmdString = 'IN{0:03d}{1}\r'.format(input, ValueStateValues[value])
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def SetCommunicationMode(self, value, qualifier):

        ValueStateValues = {
            'Transmitter': 'IN',
            'Receiver': 'OUT'
        }

        number = int(qualifier['ID'])
        if 1 <= number <= 762:
            CommunicationModeCmdString = '{0}{1:03d}GUEST\r'.format(ValueStateValues[value], number)
            self.__SetHelper('CommunicationMode', CommunicationModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCommunicationMode')

    def SetInputEDID(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1080p@60Hz, Audio 2CH PCM': '00',
            'HDMI 1080p@60Hz, Audio 5.1CH PCM/DTS/DOLBY': '01',
            'HDMI 1080p@60Hz, Audio 7.1CH PCM/DTS/DOLBY/HD': '02',
            'HDMI 1080i@60Hz, Audio 2CH PCM': '03',
            'HDMI 1080i@60Hz, Audio 5.1CH PCM/DTS/DOLBY': '04',
            'HDMI 1080i@60Hz, Audio 7.1CH PCM/DTS/DOLBY/HD': '05',
            'HDMI 1080p@60Hz/3D, Audio 2CH PCM': '06',
            'HDMI 1080p@60Hz/3D, Audio 5.1CH PCM/DTS/DOLBY': '07',
            'HDMI 1080p@60Hz/3D, Audio 7.1CH PCM/DTS/DOLBY/HD': '08',
            'HDMI 4K2K 4:4:4, Audio 2CH PCM': '09',
            'HDMI 4K2K 4:4:4, Audio 5.1CH PCM/DTS/DOLBY': '10',
            'HDMI 4K2K 4:4:4, Audio 7.1CH PCM/DTS/DOLBY/HD': '11',
            'DVI 1280x1024@60Hz, Audio None': '12',
            'DVI 1920x1080@60Hz, Audio None': '13',
            'DVI 1920x1200@60Hz, Audio None': '14',
            'Default EDID': '15',
            '4K2K 4:2:0 @ 60Hz, Audio 2CH PCM': '16',
            '4K2K 4:2:0 @ 60Hz, Audio 5.1CH PCM/DTS/DOLBY': '17',
            '4K2K 4:2:0 @ 60Hz, Audio 7.1CH PCM/DTS/DOLBY/HD': '18'
        }

        input = int(qualifier['Input'])
        if 1 <= input <= 762:
            InputEDIDCmdString = 'IN{0:03d}EDID{1}\r'.format(input, ValueStateValues[value])
            self.__SetHelper('InputEDID', InputEDIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputEDID')

    def UpdateOutputEthernetLinkStatus(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        output = int(qualifier['Output'])
        if 1 <= output <= 762:
            OutputEthernetLinkStatusCmdString = 'OUT{0:03d}STATUS\r'.format(output)
            res = self.__UpdateHelper('OutputEthernetLinkStatus', OutputEthernetLinkStatusCmdString, value, qualifier)
            if res:
                try:
                    temp = re.findall('(on|off)', res)
                    value = ValueStateValues[temp[0]]
                    self.WriteStatus('OutputEthernetLinkStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Output Ethernet Link Status: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateOutputEthernetLinkStatus')

    def SetOutputHDR(self, value, qualifier):

        ValueStateValues = {
            'On': 'HDRON',
            'Off': 'HDROFF'
        }

        output = int(qualifier['Output'])
        if 1 <= output <= 762:
            OutputHDRCmdString = 'OUT{0:03d}{1}\r'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputHDR', OutputHDRCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputHDR')

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '1080P@50Hz': '01',
            '1080P@60Hz': '02',
            '720P@60Hz': '03',
            '720P@50Hz': '04',
            '1280x1024@60Hz': '05',
            '1024x768@60Hz': '06',
            '1360x768@60Hz': '07',
            '1440x900@60Hz': '08',
            '1680x1050@60Hz': '09',
            '4K@30Hz': '10',
            '4K@24Hz': '11',
            'PASS': '00'
        }
        output = int(qualifier['Output'])
        if 1 <= output <= 762:
            OutputResolutionCmdString = 'OUT{0:03d}OUTRES{1}\r'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def SetSetVideowallOutput(self, value, qualifier):

        output = int(qualifier['Output'])
        row = int(qualifier['Rows'])
        column = int(qualifier['Columns'])
        rowpos = int(qualifier['Rows Position'])
        columnpos = int(qualifier['Colums Postion'])
        if 1 <= output <= 762 and 1 <= row <= 30 and 1 <= column <= 30 and 1 <= rowpos <= 30 and 1 <= columnpos <= 30:
            SetVideowallOutputCmdString = 'OUT{0:03d}VW{1:02d}X{2:02d}R{3:02d}C{4:02d}\r'.format(output, row - 1, column - 1, rowpos - 1, columnpos - 1)
            self.__SetHelper('SetVideowallOutput', SetVideowallOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetVideowallOutput')

    def SetTieCommand(self, value, qualifier):

        input = int(qualifier['Input'])
        output = int(qualifier['Output'])
        if 1 <= input <= 762 and 1 <= output <= 762:
            TieCommandCmdString = 'OUT{0:03d}FR{1:03d}\r'.format(output, input)
            self.__SetHelper('TieCommand', TieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTieCommand')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if 'Fail!' in response:
            self.Error(['Command fails or time out'])
            response = ''
        elif 'error command!' in response:
            self.Error(['Command has error'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.getOutputEthernetLinkStatus)
            
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except:
            return None


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()