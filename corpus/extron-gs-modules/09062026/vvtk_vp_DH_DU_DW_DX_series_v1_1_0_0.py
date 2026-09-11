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
        self._DeviceID = '01'
        self.Debug = False
        self.Models = {
            'DU3341': self.vvtk_1_2453_HDBaseT,
            'DH3331': self.vvtk_1_2453_HDBaseT,
            'DX3350': self.vvtk_1_2453_NonHDBaseT,
            'DW3320': self.vvtk_1_2453_NonHDBaseT,
            'DH3330': self.vvtk_1_2453_NonHDBaseT,
            'DU3340': self.vvtk_1_2453_NonHDBaseT,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DMode': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LampMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
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
            'Top / Bottom': '1',
            'Side-By-Side': '2',
            'Frame Packing': '3'
        }
        print(ValueStateValues[value])
        FormatCmdString = 'V{}S0317{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier):

        ValueStateValues = {
            '0': 'Frame Sequential',
            '1': 'Top / Bottom',
            '2': 'Side-By-Side',
            '3': 'Frame Packing'
        }

        FormatCmdString = 'V{}G0317\r'.format(self._DeviceID)
        res = self.__UpdateHelper('3DFormat', FormatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('3DFormat', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Update3DFormat')

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'DLP-Link': '1',
            'IR': '2'
        }
        ModeCmdString = 'V{}S0315{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)

    def Update3DMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'DLP-Link',
            '2': 'IR'
        }

        ModeCmdString = 'V{}G0315\r'.format(self._DeviceID)
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
        SyncInvertCmdString = 'V{}S0316{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DSyncInvert', SyncInvertCmdString, value, qualifier)

    def Update3DSyncInvert(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        SyncInvertCmdString = 'V{}G0316\r'.format(self._DeviceID)
        res = self.__UpdateHelper('3DSyncInvert', SyncInvertCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('3DSyncInvert', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Update3DSyncInvert')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': 'V{}S03010\r',
            '4:3': 'V{}S03011\r',
            '16:9': 'V{}S03012\r',
            'Letter Box': 'V{}S03013\r',
            'Native': 'V{}S03014\r',
            '2.35:1': 'V{}S03015\r'
        }
        AspectRatioCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'P0\r': 'Fill',
            'P1\r': '4:3',
            'P2\r': '16:9',
            'P3\r': 'Letter Box',
            'P4\r': 'Native',
            'P5\r': '2.35:1'
        }
        AspectRatioCmdString = 'V{}G0301\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'V{}S0003\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': 'V{}S01080\r',
            'Bright': 'V{}S01081\r',
            'Game': 'V{}S01082\r',
            'Movie': 'V{}S01083\r',
            'Vivid': 'V{}S01084\r',
            'TV': 'V{}S01085\r',
            'sRGB': 'V{}S01086\r',
            'DICOM SIM': 'V{}S01087\r',
            'User': 'V{}S01088\r'
        }
        DisplayModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'P0\r': 'Presentation',
            'P1\r': 'Bright',
            'P2\r': 'Game',
            'P3\r': 'Movie',
            'P4\r': 'Vivid',
            'P5\r': 'TV',
            'P6\r': 'sRGB',
            'P7\r': 'DICOM SIM',
            'P8\r': 'User'
        }
        DisplayModeCmdString = 'V{}G0108\r'.format(self._DeviceID)
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdateDisplayMode')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'V{}S03041\r',
            'Off': 'V{}S03040\r'
        }
        FreezeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'P1\r': 'On',
            'P0\r': 'Off'
        }
        FreezeCmdString = 'V{}G0304\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        InputCmdString = 'V{}S02{}\r'.format(self._DeviceID, self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'V{}G0220\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'V{}G0004\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('LampUsage', value, qualifier)
            except (IndexError, ValueError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': 'V{}S03190\r',
            'Normal': 'V{}S03191\r',
            'Dynamic Eco': 'V{}S03192\r'
        }
        LampModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            'P0\r': 'Eco',
            'P1\r': 'Normal',
            'P2\r': 'Dynamic Eco'
        }
        LampModeCmdString = 'V{}G0319\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdateLampMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'V{}S0001\r',
            'Off': 'V{}S0002\r'
        }
        PowerCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'P0\r': 'Reset',
            'P2\r': 'On',
            'P1\r': 'Off',
            'P3\r': 'Cooling'
        }
        PowerCmdString = 'V{}G0007\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'V{}S03021\r',
            'Off': 'V{}S03020\r'
        }
        VideoMuteCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'P1\r': 'On',
            'P0\r': 'Off'
        }
        VideoMuteCmdString = 'V{}G0302\r'.format(self._DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'V{}S0305{}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V{}G0305\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('Volume', value, qualifier)
            except (IndexError, ValueError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == 'F':
            print('Command {} failed to execute.'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 99:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 99:
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if res:
                return self.__CheckResponseForErrors(command, res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def vvtk_1_2453_HDBaseT(self):
        self.InputStateValues = {
            'RGB 1'         : '01', 
            'RGB 2'         : '02', 
            'DVI'           : '03', 
            'Video'         : '04', 
            'S-Video'       : '05', 
            'HDMI 1'        : '06', 
            'BNC'           : '07', 
            'Component'     : '08', 
            'HDMI 2'        : '09', 
            'HDBaseT'       : '15'
        }
        self.InputStateNames = {
            '1'  : 'RGB 1', 
            '2'  : 'RGB 2', 
            '3'  : 'DVI', 
            '4'  : 'Video', 
            '5'  : 'S-Video', 
            '6'  : 'HDMI 1', 
            '7'  : 'BNC', 
            '8'  : 'Component', 
            '9'  : 'HDMI 2', 
            '15' : 'HDBaseT'
        }

    def vvtk_1_2453_NonHDBaseT(self):
        self.InputStateValues = {
            'RGB 1'         : '01', 
            'RGB 2'         : '02', 
            'DVI'           : '03', 
            'Video'         : '04', 
            'S-Video'       : '05', 
            'HDMI 1'        : '06', 
            'BNC'           : '07', 
            'Component'     : '08', 
            'HDMI 2'        : '09'
        }
        self.InputStateNames = {
            '1'  : 'RGB 1', 
            '2'  : 'RGB 2', 
            '3'  : 'DVI', 
            '4'  : 'Video', 
            '5'  : 'S-Video', 
            '6'  : 'HDMI 1', 
            '7'  : 'BNC', 
            '8'  : 'Component', 
            '9'  : 'HDMI 2'
        }
        super().__init__(configs)
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
