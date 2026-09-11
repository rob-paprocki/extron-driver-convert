from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
from re import compile, search


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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionAnalog': {'Status': {}},
            'ClosedCaptionDigital': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NumberPad': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.SetRegex = compile(b'\x70[\x00-\x04][\x00-\xFF]')
        self.UpdateRegex = compile(b'\x70[\x00-\x02][\x02][\x00-\x01][\x00-\xFF]|\x70[\x00-\x02][\x03][\x01-\x07][\x00-\xFF]{2}|\x70[\x03-\x04][\x00-\xFF]')

    def CheckSumCalc(self, commandstring, header):
        csum = header[0]
        for i in range(0, len(commandstring)):
            csum = csum + commandstring[i]
        checksum = pack('B', csum & 0xFF)
        commandstring = b''.join([header, b'\x00', commandstring, checksum])
        return commandstring

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x00',
            'Full': b'\x01',
            'Zoom': b'\x02',
            'Normal': b'\x03',

            'Full 1': b'\x06',
            'Full 2': b'\x07'
        }

        inputState = self.ReadStatus('Input', None)
        if value == 'Normal':
            if inputState == 'PC':
                AspectRatioCmdString = b'\x44\x03\x01\x05'
            else:
                AspectRatioCmdString = b'\x44\x03\x01\x03'
        else:
            AspectRatioCmdString = b''.join([b'\x44\x03\x01', ValueStateValues[value]])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b''.join([b'\x06\x03\x01', ValueStateValues[value]])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\x06\xFF\xFF'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x10',
            'Down': b'\x11'
        }

        ChannelStepCmdString = b''.join([b'\x67\x03\x01', ValueStateValues[value]])
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        ClosedCaptionCmdString = b''.join([b'\x10\x03\x01', ValueStateValues[value]])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC1': b'\x01',
            'CC2': b'\x02',
            'CC3': b'\x03',
            'CC4': b'\x04',
            'Text1': b'\x05',
            'Text2': b'\x06',
            'Text3': b'\x07',
            'Text4': b'\x08'
        }

        ClosedCaptionAnalogCmdString = b''.join([b'\x10\x04\x02\x00', ValueStateValues[value]])
        self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'CC1': b'\x07',
            'CC2': b'\x08',
            'CC3': b'\x09',
            'CC4': b'\x0a',
            'Service1': b'\x01',
            'Service2': b'\x02',
            'Service3': b'\x03',
            'Service4': b'\x04',
            'Service5': b'\x05',
            'Service6': b'\x06'
        }

        ClosedCaptionDigitalCmdString = b''.join([b'\x10\x04\x02\x01', ValueStateValues[value]])
        self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': b'\x02\x01',
            'Video 1': b'\x03\x02\x01',
            'Video 2': b'\x03\x02\x02',
            'Component': b'\x03\x03\x01',
            'HDMI 1': b'\x03\x04\x01',
            'HDMI 2': b'\x03\x04\x02',
            'HDMI 3': b'\x03\x04\x03',
            'HDMI 4': b'\x03\x04\x04',
            'PC': b'\x03\x05\x01'
        }

        InputCmdString = b''.join([b'\x02', ValueStateValues[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x02\x01': 'Video 1',
            b'\x02\x02': 'Video 2',
            b'\x03\x01': 'Component',
            b'\x04\x01': 'HDMI 1',
            b'\x04\x02': 'HDMI 2',
            b'\x04\x03': 'HDMI 3',
            b'\x04\x04': 'HDMI 4',
            b'\x05\x01': 'PC'
        }

        InputCmdString = b'\x02\xFF\xFF'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[3] == 1:
                    value = 'TV'
                else:
                    value = ValueStateValues[res[3:5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left': b'\x01\x34',
            'Right': b'\x01\x33',
            'Up': b'\x01\x74',
            'Down': b'\x01\x75',
            'Home': b'\x01\x60',
            'Return': b'\x97\x23',
            'Select': b'\x01\x65',
            'Options': b'\x97\x36'
        }

        MenuNavigationCmdString = b''.join([b'\x67\x03', ValueStateValues[value]])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNumberPad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x01\x09',
            '1': b'\x01\x00',
            '2': b'\x01\x01',
            '3': b'\x01\x02',
            '4': b'\x01\x03',
            '5': b'\x01\x04',
            '6': b'\x01\x05',
            '7': b'\x01\x06',
            '8': b'\x01\x07',
            '9': b'\x01\x08',
            'Dot': b'\x97\x1D'
        }

        NumberPadCmdString = b''.join([b'\x67\x03', ValueStateValues[value]])
        self.__SetHelper('NumberPad', NumberPadCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x01'],
            'Off': [b'\x00']
        }

        PowerCmdString = b''.join([b'\x00\x02', ValueStateValues[value][0]])
        if value == 'On':
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        elif value == 'Off':
            self.__SetHelper('Power', b'\x01\x02\x01', value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x00\xFF\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoMuteCmdString = b''.join([b'\x0D\x03\x01', ValueStateValues[value]])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = b''.join([b'\x05\x03\x01', pack('B', value)])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x05\xFF\xFF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1: 'Limit Over (Abnormal End - over max value)',
            2: 'Limit Over (Abnormal End - under min value)',
            3: 'Command Canceled (Abnormal End)',
            4: 'Parse Error (Data Format Error)'
        }

        if len(response) == 3 and response[1] in DEVICE_ERROR_CODES:
            self.Error(['ERROR:{0}'.format(DEVICE_ERROR_CODES[response[1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = self.CheckSumCalc(commandstring, b'\x83')

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
