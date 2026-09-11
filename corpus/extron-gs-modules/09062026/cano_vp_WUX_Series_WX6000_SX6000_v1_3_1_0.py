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
        self.Models = {
            'WUX5000': self.cano_1_320_ux,
            'WUX4000': self.cano_1_320_ux,
            'WX6000': self.cano_1_320_x,
            'SX6000': self.cano_1_320_x,
            'WUX6000': self.cano_1_320_wux,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ControlMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'ImageMode': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AspectStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'GET ASPECT\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.AspectUpdateStates[res[9:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE=ON\r',
            'Off': 'MUTE=OFF\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        AudioMuteCmdString = 'GET MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'AUTOPC\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetControlMode(self, value, qualifier):

        ValueStateValues = {
            'Remote': 'MODE=REMOTE\r',
            'Local': 'MODE=LOCAL\r'
        }

        ControlModeCmdString = ValueStateValues[value]
        self.__SetHelper('ControlMode', ControlModeCmdString, value, qualifier)

    def UpdateControlMode(self, value, qualifier):

        ValueStateValues = {
            'LOCAL': 'Local',
            'REMOTE': 'Remote'
        }

        ControlModeCmdString = 'GET MODE\r'
        res = self.__UpdateHelper('ControlMode', ControlModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('ControlMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateControlMode')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'NO_ERROR'					: 'Normal',
            'ABNORMAL_TEMPERATURE'		: 'Temperature Error',
            'FAULTY_LAMP'				: 'Lamp Error',
            'FAULTY_LAMP_COVER'			: 'Lamp Cover Error',
            'FAULTY_COOLING_FAN'		: 'Cooling Fan Error',
            'FAULTY_POWER_SUPPLY'		: 'Power Supply Error',
            'FAULTY_AIR_FILTER'			: 'Air Filter Error',
            'FAULTY_POWER_ZOOM'			: 'Zoom Error',
            'FAULTY_POWER_FOCUS'		: 'Focus Error',
            'FAULTY_POWER_LENS_SHIFT'	: 'Lens Shift Error',
            'FAULTY_LENS_CONNECTOR'		: 'Lens Connector Error'
        }

        DeviceStatusCmdString = 'GET ERR\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'KeyPad': 'KEYLOCK=MAIN\r',
            'Remote': 'KEYLOCK=RC\r',
            'Off'	: 'KEYLOCK=OFF\r'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'MAIN': 'KeyPad',
            'RC'	: 'Remote',
            'OFF'	: 'Off'
        }

        ExecutiveModeCmdString = 'GET KEYLOCK\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10:-1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'FREEZE=ON\r',
            'Off': 'FREEZE=OFF\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        FreezeCmdString = 'GET FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[9:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Standard'		: 'IMAGE=STANDARD\r',
            'Presentation'	: 'IMAGE=PRESENTATION\r',
            'Vivid Photo'	: 'IMAGE=VIVID_PHOTO\r',
            'Photo/sRGB'	: 'IMAGE=PHOTO_SRGB\r',
            'DICOM Sim'		: 'IMAGE=DCM_SIM\r',
            'Dynamic'		: 'IMAGE=DYNAMIC\r',
            'Video'			: 'IMAGE=VIDEO\r',
            'Cinema'		: 'IMAGE=CINEMA\r',
            'User 1'		: 'IMAGE=USER_1\r',
            'User 2'		: 'IMAGE=USER_2\r',
            'User 3'		: 'IMAGE=USER_3\r',
            'User 4'		: 'IMAGE=USER_4\r',
            'User 5'		: 'IMAGE=USER_5\r'
        }

        ImageModeCmdString = ValueStateValues[value]
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)

    def UpdateImageMode(self, value, qualifier):

        ValueStateValues = {
            'STANDARD'		: 'Standard',
            'PRESENTATION'	: 'Presentation',
            'VIVID_PHOTO'	: 'Vivid Photo',
            'PHOTO_SRGB'	: 'Photo/sRGB',
            'DCM_SIM'		: 'DICOM Sim',
            'DYNAMIC'		: 'Dynamic',
            'VIDEO'			: 'Video',
            'CINEMA'		: 'Cinema',
            'USER_1'		: 'User 1',
            'USER_2'		: 'User 2',
            'USER_3'		: 'User 3',
            'USER_4'		: 'User 4',
            'USER_5'		: 'User 5'
        }

        ImageModeCmdString = 'GET IMAGE\r'
        res = self.__UpdateHelper('ImageMode', ImageModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:-1]]
                self.WriteStatus('ImageMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateImageMode')

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'GET INPUT\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputUpdateStates[res[8:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'LAMP=NORMAL\r',
            'Silent': 'LAMP=SILENT\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            'NORMAL': 'Normal',
            'SILENT': 'Silent'
        }

        LampModeCmdString = 'GET LAMP\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'GET LMPT\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-4])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'RC MENU\r',
            'Up': 'RC UP\r',
            'Down': 'RC DOWN\r',
            'Left': 'RC LEFT\r',
            'Right': 'RC RIGHT\r',
            'Enter': 'RC OK\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'POWER ON\r',
            'Off': 'POWER OFF\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off',
            'OFF2ON': 'Warming',
            'ON2OFF': 'Cooling',
            'PMM': 'Standby'
        }

        PowerCmdString = 'GET POWER\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def UpdateSignalStatus(self, value, qualifier):

        ValueStateValues = {
            'NO_SIGNAL': 'No Signal',
            'DISPLAYING': 'Displaying Signal',
            'SETTING': 'Processing'
        }

        SignalStatusCmdString = 'GET SIGNALSTATUS\r'
        res = self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:-1]]
                self.WriteStatus('SignalStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSignalStatus')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'BLANK=ON\r',
            'Off': 'BLANK=OFF\r'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        VideoMuteCmdString = 'GET BLANK\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AVOL={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'GET AVOL\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[0] != 'g':
                print('Error Occured')
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
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

        

    def cano_1_320_x(self):
    
        
        self.AspectStateValues = {
            'Auto'	: 'ASPECT=AUTO\r',
            '4:3'	: 'ASPECT=4:3\r',
            '16:9'	: 'ASPECT=16:9\r',
            '16:10'	: 'ASPECT=16:10\r',
            'Zoom'	: 'ASPECT=ZOOM\r',
            'True'	: 'ASPECT=TRUE\r'
        }

        self.AspectUpdateStates = {
            'AUTO'  : 'Auto',
            '4:3'   : '4:3',
            '16:9'  : '16:9',
            '16:10' : '16:10',
            'TRUE'  : 'True',
            'ZOOM'  : 'Zoom'
        }
            
        self.InputStateValues = {
            'Digital PC' : 'INPUT=D-RGB\r',
            'Analog PC-1': 'INPUT=A-RGB1\r',
            'Analog PC-2': 'INPUT=A-RGB2\r',
            'Component'  : 'INPUT=COMP\r',
            'HDMI'       : 'INPUT=HDMI\r'
        }

        self.InputUpdateStates = {
            'D-RGB' : 'Digital PC',
            'A-RGB1': 'Analog PC-1',
            'A-RGB2': 'Analog PC-2',
            'COMP'  : 'Component',
            'HDMI'  : 'HDMI'
        }
    
    def cano_1_320_ux(self):
    
        
        self.AspectStateValues = {
            'Auto'	: 'ASPECT=AUTO\r',
            '4:3'	: 'ASPECT=4:3\r',
            '16:9'	: 'ASPECT=16:9\r',
            'Zoom'	: 'ASPECT=ZOOM\r',
            'True'	: 'ASPECT=TRUE\r',
            'Full'	: 'ASPECT=FULL\r'
        }

        self.AspectUpdateStates = {
            'AUTO'  : 'Auto',
            '4:3'   : '4:3',
            '16:9'  : '16:9',
            'TRUE'  : 'True',
            'ZOOM'  : 'Zoom',
            'FULL'  : 'Full'
        }

        self.InputStateValues = {
            'Digital PC' : 'INPUT=D-RGB\r',
            'Analog PC'  : 'INPUT=A-RGB\r',
            'Component'  : 'INPUT=COMP\r',
            'HDMI'       : 'INPUT=HDMI\r'
        }

        self.InputUpdateStates = {
            'D-RGB' : 'Digital PC',
            'A-RGB' : 'Analog PC',
            'COMP'  : 'Component',
            'HDMI'  : 'HDMI'
        }

    def cano_1_320_wux(self):
    
        
        self.AspectStateValues = {
            'Auto'  : 'ASPECT=AUTO\r',
            '4:3'   : 'ASPECT=4:3\r',
            '16:9'  : 'ASPECT=16:9\r',
            '16:10' : 'ASPECT=16:10\r',
            'Zoom'  : 'ASPECT=ZOOM\r',
            'True'  : 'ASPECT=TRUE\r'
        }

        self.AspectUpdateStates = {
            'AUTO'  : 'Auto',
            '4:3'   : '4:3',
            '16:9'  : '16:9',
            '16:10' : '16:10',
            'TRUE'  : 'True',
            'ZOOM'  : 'Zoom'
        }
            
        self.InputStateValues = {
            'Digital PC' : 'INPUT=D-RGB\r',
            'Analog PC-1': 'INPUT=A-RGB1\r',
            'Analog PC-2': 'INPUT=A-RGB2\r',
            'Component'  : 'INPUT=COMP\r',
            'HDMI'       : 'INPUT=HDMI\r',
            'LAN'        : 'INPUT=LAN\r',
            'USB'        : 'INPUT=USB\r'
        }

        self.InputUpdateStates = {
            'D-RGB' : 'Digital PC',
            'A-RGB1': 'Analog PC-1',
            'A-RGB2': 'Analog PC-2',
            'COMP'  : 'Component',
            'HDMI'  : 'HDMI',
            'LAN'   : 'LAN',
            'USB'   : 'USB'
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
