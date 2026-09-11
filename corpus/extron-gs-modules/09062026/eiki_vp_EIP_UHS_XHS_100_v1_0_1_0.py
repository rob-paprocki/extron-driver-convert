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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSetting': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
        }        

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '5:4': 'ASPC   1\r',
            '4:3': 'ASPC   2\r',
            '16:10': 'ASPC   3\r',
            '16:9': 'ASPC   4\r',
            '1.88': 'ASPC   5\r',
            '2.35': 'ASPC   6\r',
            'Letterbox': 'ASPC   7\r',
            'Native': 'ASPC   8\r',
            'Unscaled': 'ASPC   9\r'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '1': '5:4',
            '2': '4:3',
            '3': '16:10',
            '4': '16:9',
            '5': '1.88',
            '6': '2.35',
            '7': 'Letterbox',
            '8': 'Native',
            '9': 'Unscaled'
        }

        AspectRatioCmdString = 'ASPC????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[3:4]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ADJS   1\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusState = {
            '0': 'Inlet Temp Over',
            '1': 'DMD Error',
            '2': 'Lamp Overheat',
            '3': 'Lamp Overheat',
            '6': 'Lamp Ballast Overheated',
            '7': 'Lamp Ballast Overheated',
            '10': 'Fan Error',
            '11': 'Fan Rotate Error',
            '12': 'Fan Rotate Error',
            '13': 'Fan Rotate Error',
            '14': 'Fan Rotate Error',
            '15': 'Fan Rotate Error',
            '16': 'Fan Rotate Error',
            '17': 'Fan Rotate Error',
            '18': 'Fan Rotate Error',
            '19': 'Fan Rotate Error',
            '20': 'Fan Rotate Error',
            '21': 'Fan Rotate Error',
            '22': 'Fan Rotate Error',
            '23': 'Fan Rotate Error',
            '27': 'DMD Failure',
            '28': 'Lamp Init Failure',
            '29': 'Lamp Lit Failure',
            '40': 'Lamp Lit Failure',
            '30': 'Ballast UART Error',
            '41': 'Ballast UART Error',
            '59': 'Ballast UART Error',
            '31': 'GPIO Failure',
            '32': 'Interlock Open',
            '33': 'GF9450 No Response',
            '34': 'System I2C Failure',
            '35': 'Software I2C Failure',
            '36': 'EEPROM Failure',
            '37': 'EDID Failure',
            '38': 'EEP Version Failure',
            '39': 'RST Gennum',
            '42': 'GT Inlet Error',
            '43': 'GT DMD Error',
            '47': 'Lamp Door Open',
            '48': 'Lamp Door Open',
            '49': 'LCU Failure',
            '50': 'LCU Failure',
            '51': 'Low Temp Start',
            '52': 'DDP3021 ASIC Error',
            '53': 'DDP3021 Main Error',
            '54': 'DDP3021 Slave Error',
            '55': 'Color Wheel Spin',
            '56': 'Temp Sensor Failure',
            '57': 'Over Temp FE',
            '58': 'Color Wheel Cover',
            '60': 'HDMI Decoder Failure',
            '62': 'AD9984 Failure',
            '63': 'Geo Boot Failure',
            '64': 'Lamp Went Out',
            '65': 'Lamp Went Out',
            '66': 'Motor Init Error'
        }

        DeviceStatusCmdString = 'ERRC????\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[3:-1]
                if value in DeviceStatusState:
                    self.WriteStatus('DeviceStatus', DeviceStatusState[value], qualifier)
                elif value not in DeviceStatusState:
                    self.WriteStatus('DeviceStatus', 'Normal', qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetInput(self, value, qualifier):

        InputState = {
            'HDMI': 'ISEL   1\r',
            'DVI': 'ISEL   2\r',
            'VGA': 'ISEL   3\r',
            'Component / BNC': 'ISEL   4\r',
            '3G-SDI': 'ISEL   5\r'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '1': 'HDMI',
            '2': 'DVI',
            '3': 'VGA',
            '4': 'Component / BNC',
            '5': '3G-SDI'
        }

        InputCmdString = 'ICHK????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[3:4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal': 'LMPM   2\r',
            'Eco': 'LMPM   1\r'
        }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            '2': 'Normal',
            '1': 'Eco'
        }

        LampModeCmdString = 'LMPM????\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[res[3:4]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampMode')

    def SetLampSetting(self, value, qualifier):

        LampSettingState = {
            'Single': 'LMPS   1\r',
            'Dual': 'LMPS   2\r'
        }

        LampSettingCmdString = LampSettingState[value]
        self.__SetHelper('LampSetting', LampSettingCmdString, value, qualifier)

    def UpdateLampSetting(self, value, qualifier):

        LampSettingState = {
            '1': 'Single',
            '2': 'Dual'
        }

        LampSettingCmdString = 'LMPS????\r'
        res = self.__UpdateHelper('LampSetting', LampSettingCmdString, value, qualifier)
        if res:
            try:
                value = LampSettingState[res[3:4]]
                self.WriteStatus('LampSetting', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampSetting')

    def UpdateLampUsage(self, value, qualifier):

        LampValue = qualifier['Lamp']

        if LampValue in ['1', '2']:
            if LampValue == '1':
                LampUsageCmdString = 'TLTT   1\r'
            elif LampValue == '2':
                LampUsageCmdString = 'TLTT   2\r'
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[0:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/Unexpected Response for UpdateLampUsage')
        else:
            print('Invalid Command')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': 'KYUP   1\r',
            'Down': 'KYDO   1\r',
            'Left': 'KYLE   1\r',
            'Right': 'KYRI   1\r',
            'Enter': 'KYEN   1\r'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
            'HDMI': 'PIPS   1\r',
            'DVI': 'PIPS   2\r',
            'VGA': 'PIPS   3\r',
            'Component / BNC': 'PIPS   4\r',
            '3G-SDI': 'PIPS   5\r'
        }

        PIPInputCmdString = PIPInputState[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputState = {
            '1': 'HDMI',
            '2': 'DVI',
            '3': 'VGA',
            '4': 'Component / BNC',
            '5': '3G-SDI'
        }

        PIPInputCmdString = 'PIPS????\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = PIPInputState[res[3:4]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'On': 'PINP   1\r',
            'Off': 'PINP   0\r'
        }

        PIPModeCmdString = PIPModeState[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeState = {
            '1': 'On',
            '0': 'Off'
        }

        PIPModeCmdString = 'PINP????\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeState[res[3:4]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPMode')

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Top Left': 'PIPP   1\r',
            'Top Right': 'PIPP   2\r',
            'Bottom Left': 'PIPP   3\r',
            'Bottom Right': 'PIPP   4\r',
            'Split-L-R': 'PIPP   5\r'
        }

        PIPPositionCmdString = PIPPositionState[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionState = {
            '1': 'Top Left',
            '2': 'Top Right',
            '3': 'Bottom Left',
            '4': 'Bottom Right',
            '5': 'Split-L-R'
        }

        PIPPositionCmdString = 'PIPP????\r'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = PIPPositionState[res[3:4]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPPosition')

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'PIPW   1\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 'POWR   1\r',
            'Off': 'POWR   0\r'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '2': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '3': 'Cooling Down',
            '4': 'Warning'
        }

        PowerCmdString = 'STAT????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': 'PIMU   1\r',
            'Off': 'PIMU   0\r'
        }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

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
                return res.decode()                   

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
