from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


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
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMute': {'Status': {}},
            'Power': {'Status': {}},
            'SoundMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.AspectRatio_Set = re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')
        self.AutoImage_Set = re.compile(b'(\x22[\x00-\xFF]{6})|(\xA2[\x00-\xFF]{6})')
        self.Freeze_Set = re.compile(b'(\x21\x98[\x00-\xFF]{2}\x01[\x00-\xFF]{2})|(\xA1\x98[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.Input_Set = re.compile(b'(\x22\x03[\x00-\xFF]{2}\x01[\x00-\xFF]{2})|(\xA2\x03[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.LampMode_Set = re.compile(b'(\x23\xB1[\x00-\xFF]{2}\x02\x07[\x00-\xFF]{2})|(\xA3\xB1[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.MenuNavigation_Set = re.compile(b'(\x22\x0F[\x00-\xFF]{2}\x01[\x00-\xFF]{2})|(\xA2\x0F[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.PictureMute_Set = re.compile(b'(\x22[\x00-\xFF]{3}\x00[\x00-\xFF])|(\xA2[\x00-\xFF]{3}\x02[\x00-\xFF]{3})')
        self.Power_Set = re.compile(b'(\x22[\x00-\xFF]{3}\x00[\x00-\xFF])|(\xA2[\x00-\xFF]{3}\x02[\x00-\xFF]{3})')
        self.SoundMute_Set = re.compile(b'(\x22[\x12-\x13][\x00-\xFF]{4})|(\xA2[\x00-\xFF]{3}\x02[\x00-\xFF]{3})')
        self.Volume_Set = re.compile(b'(\x23\x10[\x00-\xFF]{2}\x02[\x00-\xFF]{3})|(\xA3\x10[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')

        self.DeviceStatus_Update = re.compile(b'(\x20\x88[\x00-\xFF]{16})|(\xA0\x88[\x00-\xFF]{6})')
        self.FilterUsage_Update = re.compile(b'(\x23\x95[\x00-\xFF]{12})|(\xA3\x95[\x00-\xFF]{6})')
        self.Freeze_Update = re.compile(b'(\x20\xBF[\x00-\xFF]{2}\x10\x02[\x00-\xFF]{16})|(\xA0\xBF[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.Input_Update = re.compile(b'(\x20\x85[\x00-\xFF]{2}\x10[\x00-\xFF]{17})|(\xA0\x85[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.LampMode_Update = re.compile(b'(\x23\xB0[\x00-\xFF]{2}\x02\x07[\x00-\xFF]{2})|(\xA3\xB0[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.LampUsage_Update = re.compile(b'(\x23\x96[\x00-\xFF]{10})|(\xA3[\x00-\xFF]{7})')
        self.PictureMute_Update = re.compile(b'(\x20\x85[\x00-\xFF]{2}\x10[\x00-\xFF]{17})|(\xA0\x85[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.Power_Update = re.compile(b'(\x20\x85[\x00-\xFF]{2}\x10[\x00-\xFF]{17})|(\xA0\x85[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.SoundMute_Update = re.compile(b'(\x20\x85[\x00-\xFF]{2}\x10[\x00-\x01][\x00-\xFF]{16})|(\xA0\x85[\x00-\xFF]{2}\x02[\x00-\xFF]{3})')
        self.Volume_Update = re.compile(b'(\x23\x04[\x00-\xFF]{2}\x0D\x02[\x00-\xFF]{6}[\x00-\x1F]\x00[\x00-\xFF]{5})|(\xA3[\x00-\xFF]{7})')

        self.CommandDeliRex1 = {
            'AspectRatio': self.AspectRatio_Set,
            'AutoImage': self.AutoImage_Set,
            'Freeze': self.Freeze_Set,
            'Input': self.Input_Set,
            'LampMode': self.LampMode_Set,
            'MenuNavigation': self.MenuNavigation_Set,
            'PictureMute': self.PictureMute_Set,
            'Power': self.Power_Set,
            'SoundMute': self.SoundMute_Set,
            'Volume': self.Volume_Set
        }

        self.CommandDeliRex2 = {
            'DeviceStatus': self.DeviceStatus_Update,
            'FilterUsage': self.FilterUsage_Update,
            'Freeze': self.Freeze_Update,
            'Input': self.Input_Update,
            'LampMode': self.LampMode_Update,
            'LampUsage': self.LampUsage_Update,
            'PictureMute': self.PictureMute_Update,
            'Power': self.Power_Update,
            'SoundMute': self.SoundMute_Update,
            'Volume': self.Volume_Update
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Letter Box': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {

            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Cover Error',
            b'\x02\x00\x00\x00': 'Temperature Error',
            b'\x08\x00\x00\x00': 'Fan Error',
            b'\x10\x00\x00\x00': 'Fan Error',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Off',
            b'\x80\x00\x00\x00': 'Replace Lamp',

            b'\x00\x01\x00\x00': 'Lamp Life Expired',
            b'\x00\x02\x00\x00': 'Formatter Error',
            b'\x00\x04\x00\x00': 'Lamp 2 Off',
            b'\x00\x80\x00\x00': 'Extended Status',

            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temperature Sensor Error',
            b'\x00\x00\x08\x00': 'Lamp Not Present',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x40\x00': 'Replace Lamp 2',
            b'\x00\x00\x80\x00': 'Lamp 2 Life Expired',

            b'\x00\x00\x00\x01': 'Lamp 2 Not Present',
            b'\x00\x00\x00\x02': 'Lamp 2 Data Error',
            b'\x00\x00\x00\x04': 'Temperature Error Due to Dust',
            b'\x00\x00\x00\x08': 'Foreign Matter Sensor Error',
            b'\x00\x00\x00\x20': 'Ballast Communication Error',
            b'\x00\x00\x00\x40': 'Iris Calibration Error',
            b'\x00\x00\x00\x80': 'Lens Improperly Installed'
        }

        ExtendedStateValues = {
            b'\x01': 'Portrait Cover Side Up',
            b'\x02': 'Interlock Switch Open',
            b'\x04': 'System Error (Slave CPU)',
            b'\x08': 'System Error (Formatter)'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if res[13:14] != b'\x00':
                    value = ExtendedStateValues[res[13:14]]
                else:
                    value = ValueStateValues.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x95\x00\x00\x00\x98'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                filterValue = int(((res[8] << 24) + (res[7] << 16) + (res[6] << 8) + res[5]) / 3600)
                self.WriteStatus('FilterUsage', filterValue, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        FreezeCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[14:15]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer': b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'HDMI 1': b'\x02\x03\x00\x00\x02\x01\xA1\xA9',
            'HDMI 2': b'\x02\x03\x00\x00\x02\x01\xA2\xAA',
            'Video': b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'Apps': b'\x02\x03\x00\x00\x02\x01\x23\x2B',
            'HDBaseT': b'\x02\x03\x00\x00\x02\x01\xBF\xC7'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x01\x01': 'Computer',
            b'\x01\x21': 'HDMI 1',
            b'\x02\x21': 'HDMI 2',
            b'\x01\x02': 'Video',
            b'\x05\x07': 'Apps',
            b'\x01\x27': 'HDBaseT'
        }

        InputCmdString = b'\x00\x85\x00\x00\x01\x02\x88'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:9]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Auto Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco': b'\x03\xB1\x00\x00\x02\x07\x03\xC0',
            'Off': b'\x03\xB1\x00\x00\x02\x07\x00\xBD'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Auto Eco',
            b'\x02': 'Normal',
            b'\x03': 'Eco',
            b'\x00': 'Off'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6:7]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                lampHour = int(unpack('<I', res[7:11])[0] / 3600)
                self.WriteStatus('LampUsage', lampHour, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19',
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Exit': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        PictureMuteCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMute', PictureMuteCmdString, value, qualifier)

    def UpdatePictureMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PictureMuteCmdString = b'\x00\x85\x00\x00\x01\x03\x89'
        res = self.__UpdateHelper('PictureMute', PictureMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:6]]
                self.WriteStatus('PictureMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x04': 'On',
            b'\x00': 'Off',
            b'\x05': 'Cooling Down',
            b'\x06': 'Standby (Error)',
            b'\x0F': 'Standby (Power Saving)',
            b'\x10': 'Network Standby',
            b'\x01': 'Warming Up',
            b'\x02': 'Warming Up',
            b'\x03': 'Warming Up',
            b'\x09': 'Warming Up'
        }

        PowerCmdString = b'\x00\x85\x00\x00\x01\x01\x87'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10:11]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSoundMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x12\x00\x00\x00\x14',
            'Off': b'\x02\x13\x00\x00\x00\x15'
        }

        SoundMuteCmdString = ValueStateValues[value]
        self.__SetHelper('SoundMute', SoundMuteCmdString, value, qualifier)

    def UpdateSoundMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        SoundMuteCmdString = b'\x00\x85\x00\x00\x01\x03\x89'
        res = self.__UpdateHelper('SoundMute', SoundMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6:7]]
                self.WriteStatus('SoundMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Sound Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            checksum = 0x1D + value
            VolumeCmdString = pack('>11B', 0x03, 0x10, 0x00, 0x00, 0x05, 0x05, 0x00, 0x00, value, 0x00, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[12])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': "The command cannot be recognized.",
            b'\x00\x01': "The command is not supported by the model in use.",
            b'\x01\x00': "The specified value is invalid.",
            b'\x01\x01': "The specified input terminal is invalid.",
            b'\x01\x02': "The specified language is invalid.",
            b'\x02\x00': "Memory allocation error",
            b'\x02\x02': "Memory in use",
            b'\x02\x03': "The specified value cannot be set.",
            b'\x02\x04': "Forced onscreen mute on",
            b'\x02\x06': "Viewer error",
            b'\x02\x07': "No signal",
            b'\x02\x08': "A test pattern or filer is displayed.",
            b'\x02\x09': "No PC card is inserted",
            b'\x02\x0A': "Memory operation error",
            b'\x02\x0C': "An entry list is displayed.",
            b'\x02\x0D': "The command cannot be accepted because the power is off.",
            b'\x02\x0E': "The command execution failed.",
            b'\x02\x0F': "There is no authority necessary for the operation.",
            b'\x03\x00': "The specified gain number is incorrect.",
            b'\x03\x01': "The specified gain is invalid.",
            b'\x03\x02': "Adjustment failed."
        }

        if (response[0:1] == b'\xA0' or response[0:1] == b'\xA1' or response[0:1] == b'\xA2' or response[0:1] == b'\xA3') and response[5:7] in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[response[5:7]]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.CommandDeliRex1[command])
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                return self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.CommandDeliRex2[command])
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
