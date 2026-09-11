from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'DigitalZoom': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FocusMode': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'ImageSaving': { 'Status': {}},
            'Iris': { 'Status': {}},
            'IrisMode': { 'Status': {}},
            'LampSwitching': { 'Status': {}},
            'MemorySelect': { 'Status': {}},
            'MovieRecording': { 'Status': {}},
            'OSDMenu': { 'Status': {}},
            'OutputVideoSwitching': { 'Status': {}},
            'Pause': { 'Status': {}},
            'PIP': { 'Status': {}},
            'PlayMovie': { 'Status': {}},
            'PositiveNegative': { 'Status': {}},
            'Power': { 'Status': {}},
            'Resolution': { 'Status': {}},
            'Volume': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}}
        }

        self.Regex = re.compile(b'\x15|[\x00-\xFF]{8}')

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\x02AF0\x20\x20\x03'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetAutoIris(self, value, qualifier):

        AutoIrisCmdString = b'\x02IR1\x20\x20\x03'
        self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier): 

        self.UpdateFocusMode(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'On': b'\x02LL1\x20\x20\x03',
            'Off': b'\x02LL0\x20\x20\x03',
            }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier): 

        FocusModeStateNames = {
            b'\x00': 'Auto',
            b'\x01': 'Manual',
            b'\x02': 'Zoom',
           }
        DigitalZoomStateNames = {
            b'\x01': 'On',
            b'\x00': 'Off',
           }
           
        MemorySelectStateNames = {
            b'\x00': 'SD',
            b'\x01': 'USB',
           }
        FocusModeCmdString = b'\x02QS3\x20\x20\x03'
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = FocusModeStateNames[res[0:1]]
                self.WriteStatus('FocusMode', value,qualifier)
                value = DigitalZoomStateNames[res[1:2]]
                self.WriteStatus('DigitalZoom', value,qualifier)
                value = MemorySelectStateNames[res[4:5]]
                self.WriteStatus('MemorySelect', value,qualifier)
            except (KeyError,IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateImageRotation(self, value, qualifier): 

        self.UpdateIrisMode(value,qualifier)        

    def SetImageSaving(self, value, qualifier):

        ImageSavingCmdString = b'\x02CA0\x20\x20\x03'
        self.__SetHelper('ImageSaving', ImageSavingCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        IrisStateValues = {
            'Open': b'\x02IR\x2B\x20\x20\x03',
            'Close': b'\x02IR\x2D\x20\x20\x03',
            'Stop': b'\x02IR0\x20\x20\x03',
            }
        IrisCmdString = IrisStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def UpdateIrisMode(self, value, qualifier): 

        IrisModeStateNames = {
            b'\x01': 'Auto',
            b'\x02': 'Manual',
           }
        ImageRotationStateNames = {
            b'\x01': 'On',
            b'\x00': 'Off',
           }
        WhiteBalanceStateNames = {
            b'\x01': 'Auto',
            b'\x00': 'Manual',
            b'\x02': 'One Push',
           }
           
        ResolutionStateNames = {
            b'\x01' : 'SXGA', 
            b'\x02' : 'WXGA', 
            b'\x03' : 'XGA',  
            b'\x04' : '1080p',
            b'\x05' : '720p' 
        }   
           
        IrisModeCmdString = b'\x02QS2\x20\x20\x03'
        res = self.__UpdateHelper('IrisMode', IrisModeCmdString, value, qualifier)
        if res:
            try:
                value = IrisModeStateNames[res[0:1]]
                self.WriteStatus('IrisMode', value,qualifier)
                value = ImageRotationStateNames[res[2:3]]
                self.WriteStatus('ImageRotation', value,qualifier)
                value = WhiteBalanceStateNames[res[4:5]]
                self.WriteStatus('WhiteBalance', value,qualifier)
                value = ResolutionStateNames[res[6:7]]
                self.WriteStatus('Resolution', value,qualifier)
            except (KeyError,IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetLampSwitching(self, value, qualifier):

        LampSwitchingStateValues = {
            'On': b'\x02PL1\x20\x20\x03',
            'Off': b'\x02PL0\x20\x20\x03',
            }
        LampSwitchingCmdString = LampSwitchingStateValues[value]
        self.__SetHelper('LampSwitching', LampSwitchingCmdString, value, qualifier)

    def SetMovieRecording(self, value, qualifier):

        ValueStateValues = {
            'Stop' : b'\x02RC0\x20\x20\x03', 
            'Start' : b'\x02RC1\x20\x20\x03'
        }

        MovieRecordingCmdString = ValueStateValues[value]
        self.__SetHelper('MovieRecording', MovieRecordingCmdString, value, qualifier)

    def SetOSDMenu(self, value, qualifier):

        ValueStateValues = {
            'Up'           : b'\x02KE4\x20\x20\x03', 
            'Down'         : b'\x02KE5\x20\x20\x03', 
            'Left'         : b'\x02KE3\x20\x20\x03', 
            'Right'        : b'\x02KE2\x20\x20\x03', 
            'Menu / Enter' : b'\x02KE1\x20\x20\x03'
        }

        OSDMenuCmdString = ValueStateValues[value]
        self.__SetHelper('OSDMenu', OSDMenuCmdString, value, qualifier)

    def SetOutputVideoSwitching(self, value, qualifier):

        OutputVideoSwitchingStateValues = {
            'Camera': b'\x02AV0\x20\x20\x03',
            'RGB': b'\x02AV1\x20\x20\x03',
            'SD': b'\x02AV2\x20\x20\x03',
            }
        OutputVideoSwitchingCmdString = OutputVideoSwitchingStateValues[value]
        self.__SetHelper('OutputVideoSwitching', OutputVideoSwitchingCmdString, value, qualifier)

    def SetPause(self, value, qualifier):

        PauseStateValues = {
            'On': b'\x02FZ1\x20\x20\x03',
            'Off': b'\x02FZ0\x20\x20\x03',
            }
        PauseCmdString = PauseStateValues[value]
        self.__SetHelper('Pause', PauseCmdString, value, qualifier)
            
    def UpdatePIP(self, value, qualifier): 

        PIPStateNames = {
            b'\x01': 'On',
            b'\x00': 'Off',
           }
        PIPCmdString = b'\x02QS4\x20\x20\x03'
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                value = PIPStateNames[res[1:2]]
                self.WriteStatus('PIP', value,qualifier)
            except (KeyError,IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPlayMovie(self, value, qualifier):

        ValueStateValues = {
            'Play'   : b'\x02PM1\x20\x20\x03', 
            'Stop'   : b'\x02PM0\x20\x20\x03', 
            'Cueing' : b'\x02PM2\x20\x20\x03'
        }

        PlayMovieCmdString = ValueStateValues[value]
        self.__SetHelper('PlayMovie', PlayMovieCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On' : b'\x02PW1\x20\x20\x03',
            'Off': b'\x02PW0\x20\x20\x03',
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier): 
        
        LampSwitchingStateNames = {
            b'\x01': 'On',
            b'\x00': 'Off',
           }
        PositiveNegativeStateNames = {
            b'\x00': 'Positive',
            b'\x01': 'Negative',
           }
        OutputVideoSwitchingStateNames = {
            b'\x00': 'Camera',
            b'\x01': 'RGB',
            b'\x02': 'SD',
           }

        PauseStateNames = {
            b'\x01': 'On',
            b'\x00': 'Off',
           }

        PowerCmdString = b'\x02QS0\x20\x20\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:

                if res == b'\x15':
                    self.WriteStatus('Power', 'Off',qualifier)
                else:
                    self.WriteStatus('Power', 'On',qualifier)                
                
                    value = LampSwitchingStateNames[res[0:1]]
                    self.WriteStatus('LampSwitching', value,qualifier)                

                    value = PauseStateNames[res[6:7]]
                    self.WriteStatus('Pause', value,qualifier)

                    value = OutputVideoSwitchingStateNames[res[4:5]]
                    self.WriteStatus('OutputVideoSwitching', value,qualifier)
              
                    value = PositiveNegativeStateNames[res[2:3]]
                    self.WriteStatus('PositiveNegative', value,qualifier)

            except (KeyError,IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateMemorySelect(self, value, qualifier):

        self.UpdateFocusMode(value, qualifier)
        
    def SetResolution(self, value, qualifier):

        ValueStateValues = {
            'SXGA'  : b'\x02RL1\x20\x20\x03', 
            'WXGA'  : b'\x02RL2\x20\x20\x03', 
            'XGA'   : b'\x02RL3\x20\x20\x03', 
            '1080p' : b'\x02RL4\x20\x20\x03', 
            '720p'  : b'\x02RL5\x20\x20\x03'
        }

        ResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x02VL+\x20\x20\x03', 
            'Down' : b'\x02VL-\x20\x20\x03'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier): 

        self.UpdateIrisMode(value,qualifier)

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'Tele': b'\x02ZO\x2B\x20\x20\x03',
            'Wide': b'\x02ZO\x2D\x20\x20\x03',
            'Stop': b'\x02ZO0\x20\x20\x03',
            }
        ZoomCmdString = ZoomStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    
    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=1)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.Regex)
            if not res:
                return ''
            else:
                return res

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()