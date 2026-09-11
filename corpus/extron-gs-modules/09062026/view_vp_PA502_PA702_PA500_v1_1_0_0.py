from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import unpack
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
            'PA502S': self.view_1_3032_PA502S,
            'PA502X': self.view_1_3032_PA502X,
            'PX702HD': self.view_1_3032_PX702HD,
            'PA501S': self.view_1_3032_PA501S,
            'PA500S': self.view_1_3032_PA500S,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VolumeLevelStatus': {'Status': {}},
            'VolumeStep': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.updateRegex = re.compile(b'\x05\x14\x00[\x03|\x06]\x00\x00[\x00-\xFF]{3}')

    def SetAspectRatio(self, value, qualifier):

        CmdString = b'\x06\x14\x00\x04\x00\x34\x12\x04' + self.AspectRatios[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        res = self.__UpdateHelper('AspectRatio', b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x04\x63', value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', self.AspectRatioStates[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': b'\x01\x61',
            'Off': b'\x00\x60'
            }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x14\x00' + States[value]
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            1: 'On',
            0: 'Off'
            }

        res = self.__UpdateHelper('AudioMute', b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x00\x61', value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', States[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', b'\x06\x14\x00\x04\x00\x34\x12\x05\x00\x63', value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On': b'\x01\x60',
            'Off': b'\x00\x5F'
            }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x13\x00' + States[value]
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            1: 'On',
            0: 'Off'
            }

        res = self.__UpdateHelper('Freeze', b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x00\x60', value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', States[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        CmdString = b'\x06\x14\x00\x04\x00\x34\x13\x01' + self.Inputs[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        res = self.__UpdateHelper('Input', b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x01\x61', value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', self.InputStates[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal': b'\x00\x6D',
            'Eco': b'\x01\x6E',
            'Dynamic': b'\x02\x6F',
            'SuperEco': b'\x03\x70'
            }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x11\x10' + States[value]
        self.__SetHelper('LampMode', CmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        States = {
            0: 'Normal',
            1: 'Eco',
            2: 'Dynamic',
            3: 'SuperEco'
            }

        res = self.__UpdateHelper('LampMode', b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x10\x6E', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode', States[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', b'\x07\x14\x00\x05\x00\x34\x00\x00\x15\x01\x63', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', unpack('>H', res[6:8])[0], qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': b'\x0B\x5D',
            'Down': b'\x0C\x5E',
            'Left': b'\x0D\x5F',
            'Right': b'\x0E\x60',
            'Menu': b'\x0F\x61',
            'Enter': b'\x15\x67',
            'Exit': b'\x13\x65'
            }

        CmdString = b'\x02\x14\x00\x04\x00\x34\x02\x04' + States[value]
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\x00\x00\x5D',
            'Off': b'\x01\x00\x5E'
            }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x11' + States[value]
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            0: 'On',
            1: 'Off'
            }

        res = self.__UpdateHelper('Power', b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x00\x5E', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': b'\x01\x68',
            'Off': b'\x00\x67'
            }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x12\x09' + States[value]
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        States = {
            1: 'On',
            0: 'Off'
            }

        res = self.__UpdateHelper('VideoMute', b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x09\x68', value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', States[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def UpdateVolumeLevelStatus(self, value, qualifier):

        res = self.__UpdateHelper('VolumeLevelStatus', b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x03\x64', value, qualifier)
        if res:
            try:
                self.WriteStatus('VolumeLevelStatus', int(res[7]), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume Level Status: Invalid/Unexpected Response'])

    def SetVolumeStep(self, value, qualifier):

        States = {
            'Up': b'\x01\x00\x61',
            'Down': b'\x02\x00\x62'
            }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x14' + States[value]
        self.__SetHelper('VolumeStep', CmdString, value, qualifier)

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

    def view_1_3032_PA500S(self):

        self.Inputs = {
            'VGA'    : b'\x00\x60', 
            'VGA 2'  : b'\x08\x68',    
            }

        self.InputStates = {
            0 : 'VGA', 
            8 : 'VGA 2', 
            }

        self.AspectRatios = {
            'Auto'       : b'\x00\x62', 
            '4:3'        : b'\x02\x64', 
            '16:9'       : b'\x03\x65', 
            'Anamorphic' : b'\x05\x67', 
            '2.35:1'     : b'\x07\x69', 
            }

        self.AspectRatioStates = {
            0 : 'Auto', 
            2 : '4:3', 
            3 : '16:9', 
            5 : 'Anamorphic',
            7 : '2.35:1', 
            }

    def view_1_3032_PA501S(self):

        self.Inputs = {
            'VGA'        : b'\x00\x60', 
            'Composite'  : b'\x05\x65',    
            }

        self.InputStates = {
            0 : 'VGA', 
            5 : 'Composite', 
            }

        self.AspectRatios = {
            'Auto'       : b'\x00\x62', 
            '4:3'        : b'\x02\x64', 
            '16:9'       : b'\x03\x65', 
            'Anamorphic' : b'\x05\x67', 
            '2.35:1'     : b'\x07\x69', 
            }

        self.AspectRatioStates = {
            0 : 'Auto', 
            2 : '4:3', 
            3 : '16:9', 
            5 : 'Anamorphic',
            7 : '2.35:1', 
            }

    def view_1_3032_PA502S(self):

        self.Inputs = {
            'VGA'        : b'\x00\x60', 
            'HDMI'       : b'\x03\x63',
            'Composite'  : b'\x05\x65',    
            }

        self.InputStates = {
            0 : 'VGA', 
            3 : 'HDMI', 
            5 : 'Composite', 
            }

        self.AspectRatios = {
            'Auto'       : b'\x00\x62', 
            '4:3'        : b'\x02\x64', 
            '16:9'       : b'\x03\x65', 
            'Anamorphic' : b'\x05\x67', 
            '2.35:1'     : b'\x07\x69', 
            }

        self.AspectRatioStates = {
            0 : 'Auto', 
            2 : '4:3', 
            3 : '16:9', 
            5 : 'Anamorphic',
            7 : '2.35:1', 
            }

    def view_1_3032_PA502X(self):

        self.Inputs = {
            'VGA'        : b'\x00\x60', 
            'HDMI'       : b'\x03\x63',
            'Composite'  : b'\x05\x65',    
            }

        self.InputStates = {
            0 : 'VGA', 
            3 : 'HDMI', 
            5 : 'Composite', 
            }

        self.AspectRatios = {
            'Auto'       : b'\x00\x62', 
            '4:3'        : b'\x02\x64', 
            '16:9'       : b'\x03\x65', 
            'Anamorphic' : b'\x05\x67', 
            '2.35:1'     : b'\x07\x69', 
            }

        self.AspectRatioStates = {
            0 : 'Auto', 
            2 : '4:3', 
            3 : '16:9', 
            5 : 'Anamorphic',
            7 : '2.35:1', 
            }

    def view_1_3032_PX702HD(self):

        self.Inputs = {
            'VGA'        : b'\x00\x60', 
            'HDMI'       : b'\x03\x63',
            'Composite'  : b'\x05\x65',    
            }

        self.InputStates = {
            0 : 'VGA', 
            3 : 'HDMI', 
            5 : 'Composite', 
            }

        self.AspectRatios = {
            'Auto'       : b'\x00\x62', 
            '4:3'        : b'\x02\x64', 
            '16:9'       : b'\x03\x65', 
            'Anamorphic' : b'\x05\x67', 
            '2.35:1'     : b'\x07\x69', 
            'Panorama'   : b'\x08\x6A'
            }

        self.AspectRatioStates = {
            0 : 'Auto', 
            2 : '4:3', 
            3 : '16:9', 
            5 : 'Anamorphic',
            7 : '2.35:1', 
            8 : 'Panorama'
            }

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