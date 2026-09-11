from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self._DeviceID = '01'
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LaserMode': { 'Status': {}},
            'LaserUsage': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }
            
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 0 <= int(value) <= 98:
            self._DeviceID = '{0:02d}'.format(int(value))
        else:
            self.Error(['Invalide DeviceID, range is from 0 to 98 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Fill'          : '0',
            '4:3'           : '1',
            '16:9'          : '2',
            'Letter Box'    : '3',
            'Native'        : '4',
            '2.35:1'        : '5'
        }
        
        if value in AspectRatioState:
            AspectRatioCmdString = 'V{0}S0301{1}\r'.format(self.DeviceID, AspectRatioState[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '0' : 'Fill',
            '1' : '4:3',
            '2' : '16:9',
            '3' : 'Letter Box',
            '4' : 'Native',
            '5' : '2.35:1'
        }

        AspectRatioCmdString = 'V{0}G0301\r'.format(self.DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'V{0}S0003\r'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        
        FreezeState = {
            'On'    : '1',
            'Off'   : '0'
        }
        
        if value in FreezeState:
            FreezeCmdString = 'V{0}S0304{1}\r'.format(self.DeviceID, FreezeState[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')
            
    def UpdateFreeze(self, value, qualifier):

        
        FreezeState = {
            '1' : 'On',
            '0' : 'Off'
        }

        FreezeCmdString = 'V{0}G0304\r'.format(self.DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'RGB'       : '01',
            'DVI'       : '03',
            'Video'     : '04',
            'HDMI 1'    : '06',
            'HDMI 2'    : '09',
            'HDMI 3'    : '12',
            'BNC'       : '07',
            'HDBaseT'   : '15'
        }
        
        if value in InputState:
            InputCmdString = 'V{0}S02{1}\r'.format(self.DeviceID, InputState[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputState = {
            '1' : 'RGB',
            '3' : 'DVI',
            '4' : 'Video',
            '6' : 'HDMI 1',
            '9' : 'HDMI 2',
            '12': 'HDMI 3',
            '7' : 'BNC',
            '15': 'HDBaseT'
        }

        InputCmdString = 'V{0}G0220\r'.format(self.DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLaserMode(self, value, qualifier):

        LaserModeState = {
            'Normal'            : '0',
            'Eco'               : '1',
            'Eco Plus'          : '2',
            'Dimming'           : '3',
            'Extreme Dimming'   : '4',
            'Custom Light'      : '5'
        }
        
        if value in LaserModeState:
            LaserModeCmdString = 'V{0}S0319{1}\r'.format(self.DeviceID, LaserModeState[value])
            self.__SetHelper('LaserMode', LaserModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLaserMode')
            
    def UpdateLaserMode(self, value, qualifier):

        LaserModeState = {
            '0' : 'Normal',
            '1' : 'Eco',
            '2' : 'Eco Plus',
            '3' : 'Dimming',
            '4' : 'Extreme Dimming',
            '5' : 'Custom Light'
            }

        LaserModeCmdString = 'V{0}G0319\r'.format(self.DeviceID)
        res = self.__UpdateHelper('LaserMode', LaserModeCmdString, value, qualifier)
        if res:
            try:
                value = LaserModeState[res[1:-1]]
                self.WriteStatus('LaserMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Laser Mode: Invalid/unexpected response'])

    def UpdateLaserUsage(self, value, qualifier):

        LaserUsageCmdString = 'V{0}G0004\r'.format(self.DeviceID)
        res = self.__UpdateHelper('LaserUsage', LaserUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LaserUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Laser Usage: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        PictureModeState = {
            'Presentation'  : '0',
            'Bright'        : '1',
            'Game'          : '2',
            'Movie'         : '3',
            'Vivid'         : '4',
            'TV'            : '5',
            'sRGB'          : '6',
            'DICOM SIM'     : '8',
            'User 1'        : '9',
            'User 2'        : '10'
        }
        
        if value in PictureModeState:
            PictureModeCmdString = 'V{0}S0108{1}\r'.format(self.DeviceID, PictureModeState[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')
            
    def UpdatePictureMode(self, value, qualifier):

        PictureModeState = {
            '0' : 'Presentation',
            '1' : 'Bright',
            '2' : 'Game',
            '3' : 'Movie',
            '4' : 'Vivid',
            '5' : 'TV',
            '6' : 'sRGB',
            '8' : 'DICOM SIM',
            '9' : 'User 1',
            '10' : 'User 2'
            }

        PictureModeCmdString = 'V{0}G0108\r'.format(self.DeviceID)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeState[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : '1',
            'Off'   : '2',
        }
        
        if value in PowerState:
            PowerCmdString = 'V{0}S000{1}\r'.format(self.DeviceID, PowerState[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '2' : 'On',
            '1' : 'Off',
            '3' : 'Cooling Down',
            '0' : 'Reset'
        }

        PowerCmdString = 'V{0}G0007\r'.format(self.DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[1:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On'    : '1',
            'Off'   : '0'
        }
        
        if value in VideoMuteState:
            VideoMuteCmdString = 'V{0}S0302{1}\r'.format(self.DeviceID, VideoMuteState[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')
            
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            '1' : 'On',
            '0' : 'Off'
            }

        VideoMuteCmdString = 'V{0}G0302\r'.format(self.DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[1:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'V{0}S0305{1}\r'.format(self.DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V{0}G0305\r'.format(self.DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min' : -10,
            'Max' : 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomCmdString = 'V{0}S0311{1}\r'.format(self.DeviceID, value)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        ZoomCmdString = 'V{0}G0311\r'.format(self.DeviceID)
        res = self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Zoom', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Zoom: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            response = response.decode()
            if response.startswith('F'):
                self.Error(['Failed to execute {} command'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self.DeviceID == 99:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == 99:
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

