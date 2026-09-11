from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import unpack
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'PG701WU': self.view_1_4062_WU,
            'PX701HD': self.view_1_4062_HD,
            'PX703HD': self.view_1_4062_HD,
            'PX706HD': self.view_1_4062_PX706HD,
            }


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


        CmdString = b'\x06\x14\x00\x04\x00\x34\x12\x04' + self.AspectRatio[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        res = self.__UpdateHelper('AspectRatio', b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x04\x63' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio',  self.AspectRatioStates[res[7]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : b'\x06\x14\x00\x04\x00\x34\x14\x00\x01\x61', 
            'Off' : b'\x06\x14\x00\x04\x00\x34\x14\x00\x00\x60'
        }

        self.__SetHelper('AudioMute', States[value] , value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        States = {
            1 : 'On',       # 05 14 00 03 00 00 00 01 18
            0 : 'Off'       # 05 14 00 03 00 00 00 00 17
        }

        res = self.__UpdateHelper('AudioMute', b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x00\x61' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', States[res[7]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', b'\x06\x14\x00\x04\x00\x34\x12\x05\x00\x63' , value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On'    : b'\x06\x14\x00\x04\x00\x34\x13\x00\x01\x60', 
            'Off'   : b'\x06\x14\x00\x04\x00\x34\x13\x00\x00\x5F'
        }

        self.__SetHelper('Freeze', States[value] , value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        States = {
            1 : 'On',       # 05 14 00 03 00 00 00 01 18
            0 : 'Off'       # 05 14 00 03 00 00 00 00 17
        }

        res = self.__UpdateHelper('Freeze', b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x00\x60' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze',  States[res[7]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):


        CmdString = b'\x06\x14\x00\x04\x00\x34\x13\x01' + self.Input[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        res = self.__UpdateHelper('Input', b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x01\x61' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Input',  self.InputStates[res[7]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal'    : b'\x00\x6D', 
            'Eco'       : b'\x01\x6E',
            'Dynamic'   : b'\x02\x6F',
            'SuperEco'  : b'\x03\x70'
        }

        CmdString = b'\x06\x14\x00\x04\x00\x34\x11\x10' + States[value]
        self.__SetHelper('LampMode', CmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        States = {
            0 : 'Normal',       # 05 14 00 03 00 00 00 00 17
            1 : 'Eco',          # 05 14 00 03 00 00 00 01 18
            2 : 'Dynamic',      # 05 14 00 03 00 00 00 02 19
            3 : 'SuperEco'      # 05 14 00 03 00 00 00 03 1A
        }

        res = self.__UpdateHelper('LampMode', b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x10\x6E' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode',  States[res[7]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', b'\x07\x14\x00\x05\x00\x34\x00\x00\x15\x01\x63' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage',  unpack('>H', res[6:8])[0] , qualifier)     # 05 14 00 06 00 00 00 28 00 00 00 42
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up'        : b'\x0B\x5D', 
            'Down'      : b'\x0C\x5E', 
            'Left'      : b'\x0D\x5F', 
            'Right'     : b'\x0E\x60', 
            'Menu'      : b'\x0F\x61', 
            'Enter'     : b'\x15\x67', 
            'Exit'      : b'\x13\x65'
        }

        CmdString = b'\x02\x14\x00\x04\x00\x34\x02\x04' + States[value]
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On'    : b'\x06\x14\x00\x04\x00\x34\x11\x00\x00\x5D', 
            'Off'   : b'\x06\x14\x00\x04\x00\x34\x11\x01\x00\x5E'
        }

        self.__SetHelper('Power', States[value] , value, qualifier)

    def UpdatePower(self, value, qualifier):
        States = {
            1 : 'On',       # 05 14 00 03 00 00 00 01 18
            0 : 'Off'       # 05 14 00 03 00 00 00 00 17
        }

        CmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x00\x5E'
        res = self.__UpdateHelper('Power', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Power',  States[res[7]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        States = {
            'On'    : b'\x06\x14\x00\x04\x00\x34\x12\x09\x01\x68', 
            'Off'   : b'\x06\x14\x00\x04\x00\x34\x12\x09\x00\x67'
        }

        self.__SetHelper('VideoMute', States[value] , value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        States = {
            1 : 'On',       # 05 14 00 03 00 00 00 01 18
            0 : 'Off'       # 05 14 00 03 00 00 00 00 17
        }

        res = self.__UpdateHelper('VideoMute', b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x09\x68' , value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute',  States[res[7]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 20:
            CmdString = b'\x06\x14\x00\x04\x00\x34\x13\x2A' + bytes([value,value+137])
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        res = self.__UpdateHelper('Volume', b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x03\x64' , value, qualifier)    # 05 14 00 03 00 00 00 06 1D
        if res:
            try:
                self.WriteStatus('Volume',  int(res[7]) , qualifier)
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

    def view_1_4062_HD(self):


        self.AspectRatio = {
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

        self.Input = {
            'HDMI 1'    : b'\x03\x63',
            'HDMI 2'    : b'\x07\x67',
            'Computer'  : b'\x00\x60',
            'Component' : b'\x0B\x6B',
        }

        self.InputStates = {
            3 : 'HDMI 1',
            7 : 'HDMI 2',
            0 : 'Computer',
            11 : 'Component'
        }


    def view_1_4062_WU(self):


        self.AspectRatio = {
            'Auto'       : b'\x00\x62', 
            '4:3'        : b'\x02\x64', 
            '16:10'      : b'\x04\x66', 
            'Anamorphic' : b'\x05\x67', 
            '2.35:1'     : b'\x07\x69', 
            'Panorama'   : b'\x08\x6A'
        }
            

        self.AspectRatioStates = {
            0 : 'Auto', 
            2 : '4:3', 
            4 : '16:10',
            5 : 'Anamorphic',
            7 : '2.35:1',
            8 : 'Panorama'
            }

        self.Input = {
            'HDMI 1'    : b'\x03\x63',
            'HDMI 2'    : b'\x07\x67',
            'Computer'  : b'\x00\x60',
            'Component' : b'\x0B\x6B',
        }

        self.InputStates = {
            3 : 'HDMI 1',
            7 : 'HDMI 2',
            0 : 'Computer',
            11 : 'Component'
        }


    def view_1_4062_PX706HD(self):


        self.AspectRatio = {
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

        self.Input = {
            'HDMI 1'    : b'\x03\x63',
            'HDMI 2'    : b'\x07\x67',
            'Composite' : b'\x05\x65', 
            'Computer'  : b'\x00\x60',
            'Component' : b'\x0B\x6B',
        }

        self.InputStates = {
            3 : 'HDMI 1',
            7 : 'HDMI 2',
            5 : 'Composite',
            0 : 'Computer',
            11 : 'Component'
        }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)

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

