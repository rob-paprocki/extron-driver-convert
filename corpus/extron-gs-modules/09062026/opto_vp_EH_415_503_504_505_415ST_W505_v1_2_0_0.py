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
        self.DeviceID = '1'
        self.Models = {
            'EH415': self.opto_1_491_1080415,
            'EH503': self.opto_1_491_1080Inp,
            'EH505': self.opto_1_491_WXGA,
            'W505': self.opto_1_491_WXGA,
            'X605': self.opto_1_491_XGA,
            'EH415ST': self.opto_1_491_1080,
            'EH504': self.opto_1_491_1080504,
            'EH504WIFI': self.opto_1_491_1080504,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 0 <= int(value) <= 99:
            self._DeviceID = int(value)
        else:
            print('Invalid DeviceID entered')

    def SetAspectRatio(self, value, qualifier):


        self.__SetHelper('AspectRatio', '~{0:02}60 {1}\r'.format(self.DeviceID,self.AspectRatioValues[value]), value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):


        res = self.__UpdateHelper('AspectRatio', '~{0:02}127 1\r'.format(self.DeviceID), value, qualifier)
        if res:     # OKn
            try:
                self.WriteStatus('AspectRatio', self.AspectRatioNames[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'On'  : '1',
            'Off' : '0'
        }

        self.__SetHelper('AudioMute','~{0:02}03 {1}\r'.format(self.DeviceID, AudioMuteValues[value]), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        AudioMuteCmdString = '~{0:02}356 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '~{0:02}01 1\r'.format(self.DeviceID), value, qualifier)

    def SetAVMute(self, value, qualifier):

        AVMuteValues = {
            'On'  : '1',
            'Off' : '0'
        }

        self.__SetHelper('AVMute','~{0:02}02 {1}\r'.format(self.DeviceID, AVMuteValues[value]), value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        AVMuteCmdString = '~{0:02}355 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionValues = {
            'Off' : '0',
            'CC1' : '1',
            'CC2' : '2'
        }

        self.__SetHelper('ClosedCaption','~{0:02}88 {1}\r'.format(self.DeviceID, ClosedCaptionValues[value]), value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'CC1', 
            '2' : 'CC2'
        }

        ClosedCaptionCmdString = '~{0:02}354 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeValues = {
            'On'  : '1',
            'Off' : '0'
        }

        self.__SetHelper('ExecutiveMode','~{0:02}103 {1}\r'.format(self.DeviceID, ExecutiveModeValues[value]), value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeValues = {
            'On'  : '1',
            'Off' : '0'
        }

        self.__SetHelper('Freeze','~{0:02}04 {1}\r'.format(self.DeviceID, FreezeValues[value]), value, qualifier)

    def SetInput(self, value, qualifier):

        
        if value in self.InputValues:
            self.__SetHelper('Input','~{0:02}12 {1}\r'.format(self.DeviceID, self.InputValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        res = self.__UpdateHelper('Input', '~{0:02}121 1\r'.format(self.DeviceID), value, qualifier)
        if res:     # OKn
            try:
                self.WriteStatus('Input', self.InputNames[res.strip()[2:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeCmdString = '~{0}110 {1}\r'.format(self.DeviceID, self.LampModeValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):


        res = self.__UpdateHelper('LampUsage', '~{0:02}108 1\r'.format(self.DeviceID), value, qualifier)
        if res:     # OKnnnn
            try:
                self.WriteStatus('LampUsage', int(res[2:-1]), qualifier)
            except (IndexError, ValueError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Up'    : '10',
            'Left'  : '11',
            'Down'  : '14',
            'Right' : '13',
            'Menu'  : '20',
            'Enter' : '12'
            }

        self.__SetHelper('MenuNavigation', '~{0:02}140 {1}\r'.format(self.DeviceID, MenuNavigationValues[value]), value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  :  '1',
            'Off' :  '0'
            }

        self.__SetHelper('Power', '~{0:02}00 {1}\r'.format(self.DeviceID, PowerStateValues[value]), value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        res = self.__UpdateHelper('Power', '~{0:02}124 1\r'.format(self.DeviceID), value, qualifier)
        if res:  # OKn
            try:
                self.WriteStatus('Power', PowerStateNames[res[2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 10
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            self.__SetHelper('Volume', '~{0:02}81 {1:02}\r'.format(self.DeviceID, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if response[0] == 'F':
            self.Error(['Failed to execute command'])
            response = ''
        return response
    
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            return self.__CheckResponseForErrors(command, res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def opto_1_491_WXGA(self):# EH505, W505
    
        
        self.AspectRatioValues = {
            '4:3'     : '1',
            '16:9'    : '2',
            '16:10'   : '3',
            'LBX'     : '5',
            'Native'  : '6',
            'Auto'    : '7'
        }
        self.AspectRatioNames = {
            '1' : '4:3',
            '2' : '16:9',
            '3' : '16:10',
            '5' : 'LBX',
            '6' : 'Native',
            '7' : 'Auto'
        }
        self.InputValues = {
            'HDMI'             : '1',
            'DVI-D'            : '2',
            'BNC'              : '4',
            'VGA 1'            : '5',
            'VGA 2'            : '6',
            'VGA 1 Component'  : '8',
            'S-Video'          : '9',
            'Video'            : '10',
            'VGA 2 Component'  : '13',
            'Component'        : '14',
            'DisplayPort'      : '20'
        }
        self.InputNames = {
            '0'  : 'None',
            '1'  : 'DVI-D',
            '2'  : 'VGA 1',
            '3'  : 'VGA 2',
            '4'  : 'S-Video',
            '5'  : 'Video',
            '6'  : 'BNC',
            '7'  : 'HDMI',
            '10' : 'Component',
            '15' : 'DisplayPort'
        }
        self.LampModeValues = {
            'Bright'  : '1', 
            'Eco'     : '2', 
            'Power'   : '5'
        }        

      
    def opto_1_491_1080415(self):# EH415
    
        
        self.AspectRatioValues = {
            '4:3'          : '1',
            '16:9'         : '2',
            'LBX'          : '5',
            'Native'       : '6',
            'Auto'         : '7'
        }
        self.AspectRatioNames = {
            '1' : '4:3',
            '2' : '16:9',
            '5' : 'LBX',
            '6' : 'Native',
            '7' : 'Auto'
        }
        self.InputValues = {
            'HDMI'        : '1',
            'VGA 1'       : '5',
            'VGA 2'       : '6',
            'S-Video'     : '9',
            'Video'       : '10',
            'DisplayPort' : '20'
        }
        self.InputNames = {
            '0'  : 'None',
            '2'  : 'VGA 1',
            '3'  : 'VGA 2',
            '4'  : 'Video',
            '5'  : 'S-Video',
            '7'  : 'HDMI',
            '15' : 'DisplayPort'
        }
        self.LampModeValues = {
            'Bright'  : '1', 
            'Eco'     : '2'
        }        

        
    def opto_1_491_XGA(self):# X605
    
        
        self.AspectRatioValues = {
            '4:3'          : '1',
            '16:9'         : '2',
            'Native'       : '6',
            'Auto'         : '7'
        }
        self.AspectRatioNames = {
            '1' : '4:3',
            '2' : '16:9',
            '6' : 'Native',
            '7' : 'Auto'
        }
        self.InputValues = {
            'HDMI'             : '1',
            'DVI-D'            : '2',
            'BNC'              : '4',
            'VGA 1'            : '5',
            'VGA 2'            : '6',
            'VGA 1 Component'  : '8',
            'S-Video'          : '9',
            'Video'            : '10',
            'VGA 2 Component'  : '13',
            'Component'        : '14',
            'DisplayPort'      : '20'
        }
        self.InputNames = {
            '0'  : 'None',
            '1'  : 'DVI-D',
            '2'  : 'VGA 1',
            '3'  : 'VGA 2',
            '4'  : 'S-Video',
            '5'  : 'Video',
            '6'  : 'BNC',
            '7'  : 'HDMI',
            '10' : 'Component',
            '15' : 'DisplayPort'
        }
        self.LampModeValues = {
            'Bright'  : '1', 
            'Eco'     : '2', 
            'Power'   : '5'
        }        

        
    def opto_1_491_1080(self):# for EH415ST
    
        
        self.AspectRatioValues = {
            '4:3'          : '1',
            '16:9'         : '2',
            'LBX'          : '5',
            'Native'       : '6',
            'Auto'         : '7'
        }
        self.AspectRatioNames = {
            '1' : '4:3',
            '2' : '16:9',
            '5' : 'LBX',
            '6' : 'Native',
            '7' : 'Auto'
        }
        self.InputValues = {
            'HDMI 1'      : '1',
            'HDMI 2'      : '15',
            'VGA 1'       : '5',
            'Video'       : '10'
        }
        self.InputNames = {
            '0'  : 'None',
            '2'  : 'VGA 1',
            '4'  : 'Video',
            '7'  : 'HDMI 1',
            '8'  : 'HDMI 2'
        }
        self.LampModeValues = {
            'Bright'  : '1', 
            'Eco'     : '2'
        }

 
    def opto_1_491_1080504(self):# for EH504
    
        
        self.AspectRatioValues = {
            '4:3'          : '1',
            '16:9'         : '2',
            'LBX'          : '5',
            'Native'       : '6',
            'Auto'         : '7'
        }
        self.AspectRatioNames = {
            '1' : '4:3',
            '2' : '16:9',
            '5' : 'LBX',
            '6' : 'Native',
            '7' : 'Auto'
        }
        self.InputValues = {
            'HDMI 1'           : '1',
            'HDMI 2'           : '15',
            'HDMI 3'           : '16',
            'VGA 1'            : '5',
            'VGA 1 Component'  : '8',
            'Video'            : '10'
        }
        self.InputNames = {
            '0'  : 'None',
            '2'  : 'VGA 1',
            '5'  : 'Video',
            '7'  : 'HDMI 1',
            '8'  : 'HDMI 2',
            '9'  : 'HDMI 3'
        }
        self.LampModeValues = {
            'Bright'  : '1', 
            'Eco'     : '2', 
            'Eco+'    : '3', 
            'Dynamic' : '4'
        }

                       
    def opto_1_491_1080Inp(self):# for EH503
    
        
        self.AspectRatioValues = {
            '4:3'          : '1',
            '16:9'         : '2',
            'LBX'          : '5',
            'Native'       : '6',
            'Auto'         : '7'
        }
        self.AspectRatioNames = {
            '1' : '4:3',
            '2' : '16:9',
            '5' : 'LBX',
            '6' : 'Native',
            '7' : 'Auto'
        }
        self.InputValues = {
            'HDMI'             : '1',
            'DVI-D'            : '2',
            'BNC'              : '4',
            'VGA 1'            : '5',
            'VGA 2'            : '6',
            'VGA 1 Component'  : '8',
            'S-Video'          : '9',
            'Video'            : '10',
            'VGA 2 Component'  : '13',
            'Component'        : '14',
            'DisplayPort'      : '20'
        }
        self.InputNames = {
            '0'  : 'None',
            '1'  : 'DVI-D',
            '2'  : 'VGA 1',
            '3'  : 'VGA 2',
            '4'  : 'S-Video',
            '5'  : 'Video',
            '6'  : 'BNC',
            '7'  : 'HDMI',
            '10' : 'Component',
            '15' : 'DisplayPort'
        }
        self.LampModeValues = {
            'Bright'  : '1', 
            'Eco'     : '2', 
            'Power'   : '5'
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

