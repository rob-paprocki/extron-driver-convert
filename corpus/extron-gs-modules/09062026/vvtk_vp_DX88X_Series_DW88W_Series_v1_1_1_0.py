from extronlib.interface import SerialInterface, EthernetClientInterface

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
        self._DeviceID = '01'
        self.Models = {
            'DX881ST': self.vvtk_1_1880_A,
            'DW882ST': self.vvtk_1_1880_A,
            'DW884ST': self.vvtk_1_1880_B,
            'DX883ST': self.vvtk_1_1880_B,
            'DW814': self.vvtk_1_1880_C,
            'DX813': self.vvtk_1_1880_C,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat'			: {'Status': {}},
            '3DMode'			: {'Status': {}},
            '3DSyncInvert'		: {'Status': {}},
            'AspectRatio'		: {'Status': {}},
            'AutoImage'			: {'Status': {}},
            'Freeze'			: {'Status': {}},
            'Gamma'				: {'Status': {}},
            'Input'				: {'Status': {}},
            'LampMode'			: {'Status': {}},
            'LampUsage'			: {'Status': {}},
            'MenuNavigation'	: {'Status': {}},
            'Mute'				: {'Status': {}},
            'Power'				: {'Status': {}},
            'VideoMute'			: {'Status': {}},
            'Volume'			: {'Status': {}},
            'Zoom'				: {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 0 <= int(value) <= 98:
            self._DeviceID = value.zfill(2)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Frame Sequential': '0',
            'Top / Bottom' 		: '1',
            'Side-By-Side' 		: '2',
            'Frame Packing' 	: '3'
        }

        FormatCmdString = 'V{0}S0317{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier):

        ValueStateValues = {
            '0': 'Frame Sequential',
            '1': 'Top / Bottom',
            '2': 'Side-By-Side',
            '3': 'Frame Packing'
        }

        FormatCmdString = 'V{0}G0317\r'.format(self._DeviceID)
        res = self.__UpdateHelper('3DFormat', FormatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('3DFormat', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Update3DFormat')

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'Off' 		: '0',
            'DLP-Link': '1',
            'IR' 		: '2'
        }

        ModeCmdString = 'V{0}S0315{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)

    def Update3DMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'DLP-Link',
            '2': 'IR'
        }

        ModeCmdString = 'V{0}G0315\r'.format(self._DeviceID)
        res = self.__UpdateHelper('3DMode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('3DMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Update3DMode')

    def Set3DSyncInvert(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        SyncInvertCmdString = 'V{0}S0316{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DSyncInvert', SyncInvertCmdString, value, qualifier)

    def Update3DSyncInvert(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        SyncInvertCmdString = 'V{0}G0316\r'.format(self._DeviceID)
        res = self.__UpdateHelper('3DSyncInvert', SyncInvertCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('3DSyncInvert', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Update3DSyncInvert')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill' 		: '0',
            '4:3' 		: '1',
            '16:9' 		: '2',
            'Letterbox': '3',
            'Native' 	: '4',
            '2.35:1' 	: '5'
        }

        AspectRatioCmdString = 'V{0}S0301{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Fill',
            '1': '4:3',
            '2': '16:9',
            '3': 'Letterbox',
            '4': 'Native',
            '5': '2.35:1'
        }

        AspectRatioCmdString = 'V{0}G0301\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'V{0}S0408\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = 'V{0}S0304{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = 'V{0}G0304\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateFreeze')

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            '1.8': '0',
            '2.0': '1',
            '2.2': '2',
            '2.4': '3',
            'B&W': '4',
            'Linear': '5'
        }

        GammaCmdString = 'V{0}S0107{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        ValueStateValues = {
            '0': '1.8',
            '1': '2.0',
            '2': '2.2',
            '3': '2.4',
            '4': 'B&W',
            '5': 'Linear'
        }

        GammaCmdString = 'V{0}G0107\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateGamma')

    def SetInput(self, value, qualifier):

        InputCmdString = 'V{0}S020{1}\r'.format(self._DeviceID, self.SetInputStates[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'V{0}G0220\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInputStates[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': '0',
            'Normal': '1',
            'Dynamic Eco': '2'
        }

        LampModeCmdString = 'V{0}S0319{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Eco',
            '1': 'Normal',
            '2': 'Dynamic Eco'
        }

        LampModeCmdString = 'V{0}G0319\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'V{0}G0004\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu' 	: '11',
            'Up' 	: '01',
            'Down' 	: '02',
            'Left' 	: '03',
            'Right': '04',
            'Enter': '20'
        }

        MenuNavigationCmdString = 'V{0}S04{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = 'V{0}S0413\r'.format(self._DeviceID)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '2'
        }

        PowerCmdString = 'V{0}S000{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'V{0}G0007\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdatePowerStates[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = 'V{0}S0302{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = 'V{0}G0302\r'.format(self._DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        if self.SetValueConstraints['Min'] <= int(value) <= self.SetValueConstraints['Max']:
            VolumeCmdString = 'V{0}S0305{1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V{0}G0305\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min': -10,
            'Max': 10
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            ZoomCmdString = 'V{0}S0311{1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateZoom(self, value, qualifier):

        ZoomCmdString = 'V{0}G0311\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Zoom', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        response = response.decode()
        DEVICE_ERROR_CODES = {'F': "Error: Invalid Response/Command"}
        if response:
            if response in DEVICE_ERROR_CODES:
                ErrorString = sourceCmdName + DEVICE_ERROR_CODES[response]
                print(ErrorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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

    def vvtk_1_1880_A(self):

        self.SetInputStates = {
            'RGB 1' : '1',
            'RGB 2' : '2',
            'Video' : '4',
            'S-Video' : '5',
            'HDMI' : '6',
            }

        self.UpdateInputStates = {
            '1' : 'RGB 1',
            '2' : 'RGB 2',
            '4' : 'Video',
            '5' : 'S-Video',
            '6' : 'HDMI',
            }

        self.UpdatePowerStates = {
            '2' : 'On', 
            '1' : 'Off', 
            '0' : 'Reset', 
            '3' : 'Cooling'
            }

        self.SetValueConstraints = {
            'Min' : 0,
            'Max' : 30
            }


    def vvtk_1_1880_B(self):

        self.SetInputStates = {
            'RGB 1' : '1',
            'RGB 2' : '2',
            'Video' : '4',
            'S-Video' : '5',
            'HDMI 1' : '6',
            'HDMI 2' : '9',
            'HDMI 3' : '10'
            }

        self.UpdateInputStates = {
            '1' : 'RGB 1',
            '2' : 'RGB 2',
            '4' : 'Video',
            '5' : 'S-Video',
            '6' : 'HDMI 1',
            '9' : 'HDMI 2',
            '10' : 'HDMI 3'
            }

        self.UpdatePowerStates = {
            '2' : 'On', 
            '1' : 'Off', 
            '0' : 'Reset', 
            '3' : 'Cooling'
            }

        self.SetValueConstraints = {
            'Min' : 0,
            'Max' : 30
            }


    def vvtk_1_1880_C(self):
        
        self.SetInputStates = {
            'RGB 1' : '1',
            'RGB 2' : '2',
            'Video' : '4',
            'S-Video' : '5',
            'HDMI' : '6'
            }

        self.UpdateInputStates = {
            '1' : 'RGB 1',
            '2' : 'RGB 2',
            '4' : 'Video',
            '5' : 'S-Video',
            '6' : 'HDMI',
            }

        self.UpdatePowerStates = {
            '2' : 'On', 
            '1' : 'Off', 
            '0' : 'Off', 
            '3' : 'Cooling'
            }

        self.SetValueConstraints = {
            'Min' : 0,
            'Max' : 10
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
