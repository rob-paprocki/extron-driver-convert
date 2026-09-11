from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack

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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }





                    

        
        if self.Unidirectional == 'False':
            self.updateRegex = re.compile(b'\x05\x14\x00[\x03|\x06]\x00\x00[\x00-\xFF]{3}')
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'  : b'\x06\x14\x00\x04\x00\x34\x12\x04\x00\x62',
            '4:3'   : b'\x06\x14\x00\x04\x00\x34\x12\x04\x02\x64',
            '16:9'  : b'\x06\x14\x00\x04\x00\x34\x12\x04\x03\x65',
            '16:10' : b'\x06\x14\x00\x04\x00\x34\x12\x04\x04\x66',
            '2.35:1' : b'\x06\x14\x00\x04\x00\x34\x12\x04\x07\x69'
        }

        self.__SetHelper('AspectRatio', ValueStateValues[value], value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0 : 'Auto',
            2 : '4:3',
            3 : '16:9',
            4 : '16:10',
            7 : '2.35:1'
        }

        AspectRatioCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x04\x63'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x06\x14\x00\x04\x00\x34\x14\x00\x01\x61',
            'Off' : b'\x06\x14\x00\x04\x00\x34\x14\x00\x00\x60'
        }

        self.__SetHelper('AudioMute', ValueStateValues[value], value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1 : 'On',
            0 : 'Off'
        }

        AudioMuteCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x00\x61'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x05\x00\x63'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x06\x14\x00\x04\x00\x34\x13\x00\x01\x60',
            'Off' : b'\x06\x14\x00\x04\x00\x34\x13\x00\x00\x5F'
        }

        self.__SetHelper('Freeze', ValueStateValues[value], value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1 : 'On',
            0 : 'Off'
        }

        FreezeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x00\x60'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'D-Sub / Comp'  : b'\x06\x14\x00\x04\x00\x34\x13\x01\x00\x60',
            'HDMI 1'        : b'\x06\x14\x00\x04\x00\x34\x13\x01\x03\x63',
            'HDMI 2'        : b'\x06\x14\x00\x04\x00\x34\x13\x01\x07\x67',
            'HDMI 3'        : b'\x06\x14\x00\x04\x00\x34\x13\x01\x09\x69',
            'Composite Video' : b'\x06\x14\x00\x04\x00\x34\x13\x01\x05\x65',
            'HDBaseT'       : b'\x06\x14\x00\x04\x00\x34\x13\x01\x0C\x6C'
        }

        self.__SetHelper('Input', ValueStateValues[value], value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0 : 'D-Sub / Comp',
            3 : 'HDMI 1',
            7 : 'HDMI 2',
            9 : 'HDMI 3',
            5 : 'Composite Video',
            12 : 'HDBaseT'
        }

        InputCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x01\x61'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : b'\x06\x14\x00\x04\x00\x34\x11\x10\x00\x6D',
            'Eco'    : b'\x06\x14\x00\x04\x00\x34\x11\x10\x01\x6E'
        }

        self.__SetHelper('LampMode', ValueStateValues[value], value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0 : 'Normal',
            1 : 'Eco'
        }

        LampModeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x10\x6E'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x15\x01\x63'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', unpack('>H', res[6:8])[0], qualifier)  # 05 14 00 06 00 00 00 28 00 00 00 42
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\x0B\x5D',
            'Down'      : b'\x0C\x5E',
            'Left'      : b'\x0D\x5F',
            'Right'     : b'\x0E\x60',
            'Menu'      : b'\x0F\x61',
            'Enter'     : b'\x15\x67',
            'Exit'      : b'\x13\x65'
        }

        MenuNavigationCmdString = b'\x02\x14\x00\x04\x00\x34\x02\x04' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x06\x14\x00\x04\x00\x34\x11\x00\x00\x5D',
            'Off' : b'\x06\x14\x00\x04\x00\x34\x11\x01\x00\x5E'
        }

        self.__SetHelper('Power', ValueStateValues[value], value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On',
            0 : 'Off'
        }

        PowerCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x00\x5E'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x06\x14\x00\x04\x00\x34\x12\x09\x01\x68',
            'Off' : b'\x06\x14\x00\x04\x00\x34\x12\x09\x00\x67'
        }

        self.__SetHelper('VideoMute', ValueStateValues[value], value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1 : 'On',
            0 : 'Off'
        }

        VideoMuteCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x09\x68'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', ValueStateValues[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 20:
            VolumeCmdString = b'\x06\x14\x00\x04\x00\x34\x13\x2A' + bytes([value,value+137])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x03\x64'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res[7]), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex)
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

