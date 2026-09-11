from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'AspectRatio'		: {'Status': {}},
            'AutoImage'			: {'Status': {}},
            'Gamma'				: {'Status': {}},
            'Input'				: {'Status': {}},
            'LampMode'			: {'Status': {}},
            'LampPower'			: {'Status': {}},
            'LampStatus'		: {'Parameters': ['Lamp'], 'Status': {}},
            'LampUsage'			: {'Parameters': ['Lamp'], 'Status': {}},
            'OnScreenDisplay'	: {'Status': {}},
            'Power'				: {'Status': {}},
            'RecallPreset'		: {'Status': {}},
            'SavePreset'		: {'Status': {}},
            'Shutter'			: {'Status': {}},
            'VideoMute'			: {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Native': b'\x00',
            'Fill': b'\x01',
            'User': b'\x10',
            '1.33:1': b'\x14',
            '1.25:1': b'\x15',
            '1.78:1': b'\x16',
            '2.35:1': b'\x17',
            '1.66:1': b'\x18',
            '1.85:1': b'\x19',
            'Theater Scope': b'\x1A'
        }

        AspectRatioCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\x7A\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0: 'Native',
            1: 'Fill',
            16: 'User',
            20: '1.33:1',
            21: '1.25:1',
            22: '1.78:1',
            23: '2.35:1',
            24: '1.66:1',
            25: '1.85:1',
            26: 'Theater Scope'
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\x7A\x02'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x05\x62\x02'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            'Graphics': b'\x00',
            'NTSC': b'\x01',
            'PAL': b'\x02',
            'Linear': b'\x03',
            'Punch': b'\x04',
            'Parametric': b'\x05',
            'User': b'\x06'
        }

        GammaCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xC3\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        ValueStateValues = {
            0: 'Graphics',
            1: 'NTSC',
            2: 'PAL',
            3: 'Linear',
            4: 'Punch',
            5: 'Parametric',
            6: 'User'
        }

        GammaCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\xC3\x02'
        res = self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateGamma')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': b'\x00',
            'RGB 2': b'\x01',
            'DVI': b'\x02',
            'SDI': b'\x03',
            'Composite': b'\x04',
            'S-Video': b'\x05',
            'Component': b'\x06'
        }

        InputCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\x37\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0: 'RGB 1',
            1: 'RGB 2',
            2: 'DVI',
            3: 'SDI',
            4: 'Composite',
            5: 'S-Video',
            6: 'Component'
        }

        InputCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\x37\x02'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Dual' 		: b'\x00',
            'Alternate': b'\x01',
            'Single 1': b'\x02',
            'Single 2': b'\x03'
        }

        LampModeCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xC5\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Dual',
            1: 'Alternate',
            2: 'Single 1',
            3: 'Single 2'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\xC5\x02'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def SetLampPower(self, value, qualifier):

        ValueConstraints = {
            'Min': 80,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LampPowerCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xC6\x02\x00\x00\x00\x00\x00\x00', bytes([value])])
            self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLampPower')

    def UpdateLampPower(self, value, qualifier):

        LampPowerCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\xC6\x02'
        res = self.__UpdateHelper('LampPower', LampPowerCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('LampPower', value, qualifier)
            except (IndexError):
                print('Invalid/unexpected response for UpdateLampPower')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x10\x04\x00\x58\x58\x24\x00\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                lamp1 = int(unpack('<I', res[12:16])[0] / 3600)
                self.WriteStatus('LampUsage', lamp1, {'Lamp': '1'})
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

            try:
                lamp2 = int(unpack('<I', res[20:24])[0] / 3600)
                self.WriteStatus('LampUsage', lamp2, {'Lamp': '2'})
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x00',
            'Disable': b'\x01'
        }

        OnScreenDisplayCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xD7\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            0: 'Enable',
            1: 'Disable'
        }

        OnScreenDisplayCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\xD7\x02'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00',
            'Off': b'\x04',
        }

        PowerCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\x01\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        LampStates = {
            0: 'Lamp Not Installed',
            1: 'Off',
            2: 'Warming Up',
            3: 'On',
            4: 'Cooling Down',
            5: 'Ballast Communications Error',
            6: 'Lamp Timer Data Error',
            7: 'Lamp Error',
            8: 'Lamp Timer Expired'
        }

        PowerCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\x11\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                lamp1 = res[-2]
                lamp2 = res[-1]
                if lamp1 == 3 or lamp2 == 3:
                    self.WriteStatus('Power', 'On', qualifier)
                elif lamp1 == 2 or lamp2 == 2:
                    self.WriteStatus('Power', 'Warming Up', qualifier)
                elif lamp1 == 4 or lamp2 == 4:
                    self.WriteStatus('Power', 'Cooling Down', qualifier)
                elif lamp1 == 1 and lamp2 == 1:
                    self.WriteStatus('Power', 'Off', qualifier)
                else:
                    print('Multiple Lamp Errors for UpdatePower')
            except (IndexError):
                print('Invalid/unexpected response')

            try:
                lamp_status1 = LampStates[res[-2]]
                self.WriteStatus('LampStatus', lamp_status1, {'Lamp': '1'})
            except(KeyError, IndexError):
                print('Invalid/unexpected response')

            try:
                lamp_status2 = LampStates[res[-1]]
                self.WriteStatus('LampStatus', lamp_status2, {'Lamp': '2'})
            except(KeyError, IndexError):
                print('Invalid/unexpected response')

    def SetRecallPreset(self, value, qualifier):

        ValueStateValues = {
            'A': b'\x00',
            'B': b'\x01',
            'C': b'\x02',
            'D': b'\x03',
            'E': b'\x04',
            'F': b'\x05',
            'G': b'\x06',
            'H': b'\x07',
            'J': b'\x08',
            'K': b'\x09',
            'L': b'\x0A',
            'M': b'\x0B',
            'N': b'\x0C',
            'P': b'\x0D',
            'R': b'\x0E',
            'S': b'\x0F'
        }

        RecallPresetCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xE8\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)

    def SetSavePreset(self, value, qualifier):

        ValueStateValues = {
            'A': b'\x00',
            'B': b'\x01',
            'C': b'\x02',
            'D': b'\x03',
            'E': b'\x04',
            'F': b'\x05',
            'G': b'\x06',
            'H': b'\x07',
            'J': b'\x08',
            'K': b'\x09',
            'L': b'\x0A',
            'M': b'\x0B',
            'N': b'\x0C',
            'P': b'\x0D',
            'R': b'\x0E',
            'S': b'\x0F'
        }

        SavePresetCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xEA\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open': b'\x01',
            'Close': b'\x00'
        }

        ShutterCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xCF\x02\x00\x00', ValueStateValues[value]])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            0: 'Open',
            1: 'Close'
        }

        ShutterCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\xCF\x02'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateShutter')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00',
            'Off': b'\x01'
        }

        VideoMuteCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x58\x58\x01\xDC\x02\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            0: 'On',
            1: 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x19\x00\x58\x58\x02\xDC\x02'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring.ljust(32, b'\x00'))

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if command == 'LampUsage':
            res_len = 28
            commandstring = commandstring
        else:
            res_len = 19
            commandstring = commandstring.ljust(32, b'\x00')

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=res_len)
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
