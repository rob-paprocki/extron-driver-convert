from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self.Models = {
            '8084i-G4-SMP': self.smrt_8084i,
            '8070i-G4-SMP': self.smrt_8070i,
            'SBID-8070i-G4-SMP': self.smrt_8070i,
            'SBID-8084i-G4-SMP': self.smrt_8084i,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'ProximityDetected': {'Status': {}},
            'ProximityDetection': {'Status': {}},
            'USBSource': {'Parameters': ['Port'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        try:
            CmdString = 'set aspectratio={0}\r'.format(self.AspectRatioState[value])
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)
        except KeyError:
            self.Error('Invalid command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        CmdString = 'get aspectratio\r'
        response = self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        if response:
            try:
                value = self.AspectRatioValues[response[-3:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, ValueError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Responses'])

    def SetAudioMute(self, value, qualifier):

        State = {
            'On': 'on',
            'Off': 'off',
        }

        CmdString = 'set mute={0}\r'.format(State[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        State = {
            'on': 'On',
            'ff': 'Off',
        }

        CmdString = 'get mute\r'

        response = self.__UpdateHelper('AudioMute', CmdString, value, qualifier)
        if response:
            try:
                value = State[response[-3:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Responses'])

    def SetInput(self, value, qualifier):

        try:
            CmdString = 'set input={0}\r'.format(self.InputState[value])
            self.__SetHelper('Input', CmdString, value, qualifier)
        except KeyError:
            self.Error('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        CmdString = 'get input\r'
        response = self.__UpdateHelper('Input', CmdString, value, qualifier)
        if response:
            try:
                if response[-3:-1].lower() == 'eo':
                    if re.findall(re.compile('S_Video', re.IGNORECASE), response)[0] in ['S_Video', 'S_VIDEO']:
                        value = 'S-Video'
                    else:
                        value = 'Video'
                else:
                    value = self.ReturnInputState[response[-3:-1].lower()]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, ValueError, IndexError):
                self.Error(['Input: Invalid/Unexpected Responses'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'get totalhours\r'
        response = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if response:
            try:
                findNumber = re.findall(re.compile('\d+'), response)
                if findNumber:
                    value = int(findNumber[0])
                    self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/Unexpected Responses'])

    def SetPower(self, value, qualifier):

        State = {
            'On': 'on',
            'Off': 'off',
            'Standby': 'standby'
        }

        CmdString = 'set powerstate={0}\r'.format(State[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        State = {
            'on': 'On',
            'ff': 'Off',
            'by': 'Standby',
            'dy': 'Ready'
        }

        CmdString = 'get powerstate\r'
        response = self.__UpdateHelper('Power', CmdString, value, qualifier)

        if response:
            try:
                value = State[response[-3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Power: Invalid/Unexpected Responses'])

    def SetProximityDetected(self, value, qualifier):

        ValueStateValues = {
            'Yes': 'set proximitydetected=yes\r',
            'No': 'set proximitydetected=no\r'
        }

        ProximityDetectedCmdString = ValueStateValues[value]
        self.__SetHelper('ProximityDetected', ProximityDetectedCmdString, value, qualifier)

    def UpdateProximityDetected(self, value, qualifier):

        ValueStateValues = {
            'es': 'Yes',
            'no': 'No'
        }

        ProximityDetectedCmdString = 'get proximitydetected\r'
        res = self.__UpdateHelper('ProximityDetected', ProximityDetectedCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('ProximityDetected', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Proximity Detected: Invalid/Unexpected Responses'])

    def SetProximityDetection(self, value, qualifier):

        ValueStateValues = {
            'On': 'set proximity=on\r',
            'Off': 'set proximity=off\r'
        }

        ProximityDetectionCmdString = ValueStateValues[value]
        self.__SetHelper('ProximityDetection', ProximityDetectionCmdString, value, qualifier)

    def UpdateProximityDetection(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'ff': 'Off'
        }

        ProximityDetectionCmdString = 'get proximity\r'
        res = self.__UpdateHelper('ProximityDetection', ProximityDetectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('ProximityDetection', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Proximity Detection: Invalid/Unexpected Responses'])

    def SetUSBSource(self, value, qualifier):

        PortStates = {
            '1': 'set usb1source',
            '2': 'set usb2source',
            '3': 'set usb3source'
        }

        try:
            USBSourceCmdString = '{0}{1}\r'.format(PortStates[qualifier['Port']], self.USBSourceState[value])
            self.__SetHelper('USBSource', USBSourceCmdString, value, qualifier)
        except KeyError:
            self.Error(['Invalid command for SetUSBSource'])

    def UpdateUSBSource(self, value, qualifier):

        USBSourceCmdString = 'get usb{0}source\r'.format(qualifier['Port'])
        res = self.__UpdateHelper('USBSource', USBSourceCmdString, value, qualifier)
        if res:
            try:
                value = self.USBSourceValues[res[-3:-1].lower()]
                self.WriteStatus('USBSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['USB Source: Invalid/Unexpected Responses'])

    def SetVideoMute(self, value, qualifier):

        State = {
            'On': 'on',
            'Off': 'off',
        }

        CmdString = 'set videomute={0}\r'.format(State[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        State = {
            'on': 'On',
            'ff': 'Off',
        }

        CmdString = 'get videomute\r'
        response = self.__UpdateHelper('VideoMute', CmdString, value, qualifier)
        if response:
            try:
                value = State[response[-3:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Responses'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'set volume={0}\r'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CmdString = 'get volume\r'
        response = self.__UpdateHelper('Volume', CmdString, value, qualifier)
        if response:
            try:
                value = int(response[7:-1])
                self.WriteStatus('Volume', int(value), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Responses'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res.decode())
            return res

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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

    def smrt_8070i(self):

        self.AspectRatioState = {
            '16:9': '16:9',
            '4:3': '4:3',
            '1:1': '1:1',
            'Zoom 1': 'zoom1',
            'Zoom 2': 'zoom2'
        }

        self.AspectRatioValues = {
            ':9': '16:9',
            ':3': '4:3',
            ':1': '1:1',
            'm1': 'Zoom 1',
            'm2': 'Zoom 2'
        }

        self.InputState = {
            'DVI': 'DVI',
            'VGA 1': 'VGA1',
            'VGA 2': 'VGA2',
            'Display Port': 'DisplayPort',
            'HDMI1': 'HDMI1',
            'HDMI2': 'HDMI2',
            'HDMI3/PC': 'HDMI3/PC',
            'S-Video': 'S_Video',
            'Video': 'Video',
            'DVD/HD': 'DVD/HD'
        }

        self.ReturnInputState = {
            'rt': 'Display Port',
            'vi': 'DVI',
            'a1': 'VGA1',
            'a2': 'VGA2',
            'i1': 'HDMI1',
            'i2': 'HDMI2',
            'pc': 'HDMI3/PC',
            'hd': 'DVD/HD',
            'i3': 'HDMI3/PC',
        }

        self.USBSourceState = {
            'DVI': '=DVI',
            'Display Port': '=DPort',
            'HDMI1': '=HDMI1',
            'HDMI2': '=HDMI2',
            'HDMI3/PC': '=HDMI3/PC',
            'Disable': '=Disable',
            'VGA1': '=VGA1',
            'VGA2': '=VGA2'
        }

        self.USBSourceValues = {
            'rt': 'Display Port',
            'le': 'Disable',
            'vi': 'DVI',
            'i1': 'HDMI1',
            'i2': 'HDMI2',
            'pc': 'HDMI3/PC',
            'a1': 'VGA1',
            'a2': 'VGA2',
            'i3': 'HDMI3/PC',
        }

    def smrt_8084i(self):

        self.AspectRatioState = {
            'Just Scan': 'justscan',
            '16:9': '16:9',
            '4:3': '4:3',
        }

        self.AspectRatioValues = {
            'an': 'Just Scan',
            ':9': '16:9',
            ':3': '4:3',
        }

        self.InputState = {
            'DVI': 'DVI',
            'VGA': 'VGA',
            'Display Port': 'DPort',
            'HDMI1': 'HDMI1',
            'HDMI2': 'HDMI2',
            'HDMI3/PC': 'HDMI3/PC',
            'Component': 'component',
            'Composite': 'composite',
        }

        self.ReturnInputState = {
            'rt': 'Display Port',
            'nt': 'Component',
            'te': 'Composite',
            'vi': 'DVI',
            'ga': 'VGA',
            'i1': 'HDMI1',
            'i2': 'HDMI2',
            'pc': 'HDMI3/PC',
            'i3': 'HDMI3/PC',
        }

        self.USBSourceState = {
            'VGA': '=VGA',
            'DVI': '=DVI',
            'Display Port': '=DPort',
            'HDMI1': '=HDMI1',
            'HDMI2': '=HDMI2',
            'HDMI3/PC': '=HDMI3/PC',
            'Disable': '=Disable',
        }

        self.USBSourceValues = {
            'rt': 'Display Port',
            'le': 'Disable',
            'ga': 'VGA',
            'vi': 'DVI',
            'i1': 'HDMI1',
            'i2': 'HDMI2',
            'pc': 'HDMI3/PC',
            'i3': 'HDMI3/PC',
        }

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
