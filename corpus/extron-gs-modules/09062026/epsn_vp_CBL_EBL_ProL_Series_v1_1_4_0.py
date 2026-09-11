from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'EB-L1405U': self.epsn_1_2213_A,
            'EB-L1100U': self.epsn_1_2213_B,
            'CB-L1405U': self.epsn_1_2213_A,
            'Pro L1405U': self.epsn_1_2213_A,
            'EB-L1500U': self.epsn_1_2213_A,
            'CB-L1500U': self.epsn_1_2213_A,
            'Pro L1500U': self.epsn_1_2213_A,
            'EB-L1505U': self.epsn_1_2213_A,
            'Pro L1505U': self.epsn_1_2213_A,
            'CB-L1505U': self.epsn_1_2213_A,
            'Pro L1100U': self.epsn_1_2213_B,
            'CB-L1100U': self.epsn_1_2213_B,
            'CB-L1200U': self.epsn_1_2213_B,
            'CB-L1300U': self.epsn_1_2213_B,
            'EB-L1200U': self.epsn_1_2213_B,
            'EB-L1300U': self.epsn_1_2213_B,
            'Pro L1200U': self.epsn_1_2213_B,
            'Pro L1300U': self.epsn_1_2213_B,
            'EB-L1715S': self.epsn_1_2213_B,
            'EB-L1710S': self.epsn_1_2213_B,
            'EB-L1515S': self.epsn_1_2213_B,
            'EB-L1510S': self.epsn_1_2213_B,
            'EB-L1755U': self.epsn_1_2213_A,
            'EB-L1750U': self.epsn_1_2213_A,
            'EB-L1505UH': self.epsn_1_2213_A,
            'EB-L1500UH': self.epsn_1_2213_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LensPositionCall': {'Status': {}},
            'LensPositionDelete': {'Status': {}},
            'LensPositionRegister': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'SplitScreen': {'Status': {}},
            'SplitScreenSource': {'Status': {}},
            'SplitScreenSwap': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=([0-6A]0)( 30)?\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'ERR=(0\d|0[A-F]|1[0-6])\r:'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(1[014]|3[013-5]|53|6[045]|8[013-5]|A[013]|B[014])\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[01])\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=(\d{1,5})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(0\d)\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=(\d{1,3})\r:'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '10',
            '16:9': '20',
            'Auto': '30',
            'Full': '40',
            'H-Zoom': '50',
            'Native': '60',
            'V-Zoom': 'A0',
            'Normal': '00'
        }

        AspectRatioCmdString = 'ASPECT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '10': '4:3',
            '20': '16:9',
            '30': 'Auto',
            '40': 'Full',
            '50': 'H-Zoom',
            '60': 'Native',
            'A0': 'V-Zoom',
            '00': 'Normal'
        }

        if match.group(2):
            value = 'Auto'
        else:
            value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        AVMuteCmdString = 'MUTE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Fan Error',
            '03': 'Lamp Failure at power on',
            '04': 'Internal Temperature is Abnormally High',
            '07': 'Lamp Cover Error',
            '06': 'Lamp Error',
            '08': 'Cinema Filter Error',
            '09': 'EDL Capacitor Disconnected',
            '0A': 'Auto Iris Error',
            '0B': 'Subsystem Error',
            '0C': 'Low Air Flow Error',
            '0D': 'Air Flow Error',
            '0E': 'Power Supply Error',
            '0F': 'Shutter Failure',
            '10': 'Cooling System Error',
            '11': 'Cooling System Error (Pump)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        FreezeCmdString = 'FREEZE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = 'SOURCE {0}\r'.format(self.SetInputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.UpdateInputStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '00',
            'Eco': '01'
        }

        LampModeCmdString = 'LUMINANCE {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Eco'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetLensPositionCall(self, value, qualifier):

        ValueStateValues = {
            '1': 'POPLP 01\r',
            '2': 'POPLP 02\r',
            '3': 'POPLP 03\r',
            '4': 'POPLP 04\r',
            '5': 'POPLP 05\r',
            '6': 'POPLP 06\r',
            '7': 'POPLP 07\r',
            '8': 'POPLP 08\r',
            '9': 'POPLP 09\r',
            '10': 'POPLP 10\r'
        }

        LensPositionCallCmdString = ValueStateValues[value]
        self.__SetHelper('LensPositionCall', LensPositionCallCmdString, value, qualifier)

    def SetLensPositionDelete(self, value, qualifier):

        ValueStateValues = {
            'All': 'ERASELP 00\r',
            '1': 'ERASELP 01\r',
            '2': 'ERASELP 02\r',
            '3': 'ERASELP 03\r',
            '4': 'ERASELP 04\r',
            '5': 'ERASELP 05\r',
            '6': 'ERASELP 06\r',
            '7': 'ERASELP 07\r',
            '8': 'ERASELP 08\r',
            '9': 'ERASELP 09\r',
            '10': 'ERASELP 10\r'
        }

        LensPositionDeleteCmdString = ValueStateValues[value]
        self.__SetHelper('LensPositionDelete', LensPositionDeleteCmdString, value, qualifier)

    def SetLensPositionRegister(self, value, qualifier):

        ValueStateValues = {
            '1': 'PUSHLP 01\r',
            '2': 'PUSHLP 02\r',
            '3': 'PUSHLP 03\r',
            '4': 'PUSHLP 04\r',
            '5': 'PUSHLP 05\r',
            '6': 'PUSHLP 06\r',
            '7': 'PUSHLP 07\r',
            '8': 'PUSHLP 08\r',
            '9': 'PUSHLP 09\r',
            '10': 'PUSHLP 10\r'
        }

        LensPositionRegisterCmdString = ValueStateValues[value]
        self.__SetHelper('LensPositionRegister', LensPositionRegisterCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': 'KEY 03\r',
            'Escape': 'KEY 05\r',
            'Enter': 'KEY 16\r',
            'Up': 'KEY 35\r',
            'Down': 'KEY 36\r',
            'Left': 'KEY 37\r',
            'Right': 'KEY 38\r'
        }

        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': 'OFF',
            'On': 'ON',
        }

        PowerCmdString = 'PWR {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '01': 'On',
            '02': 'Warming Up',
            '03': 'Cooling Down',
            '04': 'Off',
            '05': 'Off',
            '09': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        SplitScreenCmdString = 'SPS 01 {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)

    def SetSplitScreenSource(self, value, qualifier):

        SideStates = {
            'Left': '03',
            'Right': '04'
        }

        SplitScreenSourceCmdString = 'SPS {0} {1}\r'.format(SideStates[qualifier['Side']], self.SetInputStateValues[value])
        self.__SetHelper('SplitScreenSource', SplitScreenSourceCmdString, value, qualifier)

    def SetSplitScreenSwap(self, value, qualifier):

        SplitScreenSwapCmdString = 'SPS 05\r'
        self.__SetHelper('SplitScreenSwap', SplitScreenSwapCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 20
        }

        VolumeStateTable = {
            0: 0,
            1: 12,
            2: 24,
            3: 36,
            4: 48,
            5: 60,
            6: 73,
            7: 85,
            8: 97,
            9: 109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243
        }

        value = int(value)
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOL {0}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(int(match.group(1).decode()) / 12)
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.Error([match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def epsn_1_2213_A(self):

        self.SetInputStateValues = {
            'D-SUB': '10',
            'RGB': '11',
            'Component': '14',
            'HDMI': '30',
            'LAN': '53',
            'SDI': '60',
            'HDBaseT': '80',
            'DVI-D': 'A0',
            'BNC': 'B0',
            'BNC (RGB)': 'B1',
            'BNC (Component)': 'B4'
        }

        self.UpdateInputStateValues = {
            '10': 'D-SUB',
            '11': 'RGB',
            '14': 'Component',
            '30': 'HDMI',
            '53': 'LAN',
            '60': 'SDI',
            '80': 'HDBaseT',
            'A0': 'DVI-D',
            'B0': 'BNC',
            'B1': 'BNC (RGB)',
            'B4': 'BNC (Component)',
            '31': 'D-RGB',
            '33': 'RGB-Video',
            '34': 'YCbCr',
            '35': 'YPbPr',
            '64': 'SDI (YCbCr)',
            '65': 'SDI (YPbPr)',
            '81': 'HDBaseT (Digital-RGB)',
            '83': 'HDBaseT (RGB-Video)',
            '84': 'HDBaseT (YCbCr)',
            '85': 'HDBaseT (YPbPr)',
            'A1': 'DVI-D (Digital-RGB)',
            'A3': 'DVI-D (RGB-Video)'
        }

    def epsn_1_2213_B(self):

        self.SetInputStateValues = {
            'D-SUB': '10',
            'RGB': '11',
            'Component': '14',
            'HDMI': '30',
            'LAN': '53',
            'HDBaseT': '80',
            'DVI-D': 'A0',
            'BNC': 'B0',
            'BNC (RGB)': 'B1',
            'BNC (Component)': 'B4'
        }

        self.UpdateInputStateValues = {
            '10': 'D-SUB',
            '11': 'RGB',
            '14': 'Component',
            '30': 'HDMI',
            '53': 'LAN',
            '80': 'HDBaseT',
            'A0': 'DVI-D',
            'B0': 'BNC',
            'B1': 'BNC (RGB)',
            'B4': 'BNC (Component)',
            '31': 'D-RGB',
            '33': 'RGB-Video',
            '34': 'YCbCr',
            '35': 'YPbPr',
            '81': 'HDBaseT (Digital-RGB)',
            '83': 'HDBaseT (RGB-Video)',
            '84': 'HDBaseT (YCbCr)',
            '85': 'HDBaseT (YPbPr)',
            'A1': 'DVI-D (Digital-RGB)',
            'A3': 'DVI-D (RGB-Video)'
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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
