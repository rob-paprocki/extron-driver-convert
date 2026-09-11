from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceSerialClass:
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Display ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Display ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Display ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Display ID'], 'Status': {}},
            'EnergySaving': {'Parameters': ['Display ID'], 'Status': {}},
            'Input': {'Parameters': ['Display ID'], 'Status': {}},
            'Keypad': {'Parameters': ['Display ID'], 'Status': {}},
            'MasterPower': {'Status': {}},
            'MenuNavigation': {'Parameters': ['Display ID'], 'Status': {}},
            'PictureMode': {'Parameters': ['Display ID'], 'Status': {}},
            'Power': {'Parameters': ['Display ID'], 'Status': {}},
            'TileMode': {'Parameters': ['Display ID', 'Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters': ['Display ID', 'Tile ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Display ID'], 'Status': {}},
            'Volume': {'Parameters': ['Display ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2,3}) OK([0-9A-F]{2})x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'q ([0-9A-F]{2,3}) OK0(0|1|2|3|4|5)x', re.I), self.__MatchEnergySaving,
                                None)
            self.AddMatchString(re.compile(b'm ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2,3}) OK(60|A0|90|91|A1|70|80|D0|C0|A8|98)x', re.I),
                                self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x ([0-9A-F]{2,3}) OK([0-9]{2})x', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2,3}) OK([0-9a-f]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(u|i|j|c|e|m|b|a|d|f|x) ([0-9A-F]{2,3}) NG(.*?)x', re.I),
                                self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')

    @property
    def DisplayID(self):
        return self._DisplayID

    @DisplayID.setter
    def DisplayID(self, value):
        if value == 'Broadcast':
            self._DisplayID = '00'
        elif 1 <= int(value) <= 1000:
            self._DisplayID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': '02',
            'Just Scan': '09',
            'Original': '06',
            '4:3': '01',
            '58:9': '21',
            'Vertical Zoom': '30',
            'All Directional Zoom': '31'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            AspectRatioCmdString = 'kc {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            AspectRatioCmdString = 'kc {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '02': '16:9',
            '09': 'Just Scan',
            '06': 'Original',
            '01': '4:3',
            '21': '58:9',
            '30': 'Vertical Zoom',
            '31': 'All Directional Zoom'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('AspectRatio', value, {'Display ID': str(ID)})

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            AudioMuteCmdString = 'ke {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            AudioMuteCmdString = 'ke {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, {'Display ID': str(ID)})

    def SetAutoImage(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            AutoImageCmdString = 'ju {0} 01\r'.format(DisplayID)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetEnergySaving(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04',
            'Screen Off': '05'
        }

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'

        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            EnergySavingCmdString = 'jq {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('EnergySaving', EnergySavingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEnergySaving')

    def UpdateEnergySaving(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            EnergySavingCmdString = 'jq {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('EnergySaving', EnergySavingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEnergySaving')

    def __MatchEnergySaving(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Minimum',
            '2': 'Medium',
            '3': 'Maximum',
            '4': 'Automatic',
            '5': 'Screen Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('EnergySaving', value, {'Display ID': str(ID)})

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            ExecutiveModeCmdString = 'km {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            ExecutiveModeCmdString = 'km {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('ExecutiveMode', value, {'Display ID': str(ID)})

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB': '60',
            'HDMI 1(PC)': 'A0',
            'HDMI 1(DTV)': '90',
            'DVI-D (PC)': '70',
            'DVI-D (DTV)': '80',
            'DISPLAYPORT (PC)': 'D0',
            'DISPLAYPORT (DTV)': 'C0',
            'OPS (PC)': 'A8',
            'OPS (DTV)': '98',
            'HDMI 2(PC)': 'A1',
            'HDMI 2(DTV)': '91'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            InputCmdString = 'xb {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            InputCmdString = 'xb {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '60': 'RGB',
            'A0': 'HDMI 1(PC)',
            '90': 'HDMI 1(DTV)',
            '70': 'DVI-D (PC)',
            '80': 'DVI-D (DTV)',
            'D0': 'DISPLAYPORT (PC)',
            'C0': 'DISPLAYPORT (DTV)',
            'A8': 'OPS (PC)',
            '98': 'OPS (DTV)',
            'A1': 'HDMI 2(PC)',
            '91': 'HDMI 2(DTV)'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Input', value, {'Display ID': str(ID)})

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            KeypadCmdString = 'mc {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def UpdateMasterPower(self, value, qualifier):

        MasterPowerCmdString = 'ka {0} FF\r'.format(self.DisplayID)
        self.__UpdateHelper('MasterPower', MasterPowerCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': '00',
            'Standard': '01',
            'APS': '08',
            'Cinema': '02',
            'Sports': '03',
            'Game': '04',
            'Photos': '09',
            'Expert 1': '05',
            'Expert 2': '06',
            'Calibration': '11'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            PictureModeCmdString = 'dx {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            PictureModeCmdString = 'dx {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePictureMode')

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00': 'Vivid',
            '01': 'Standard',
            '08': 'APS',
            '02': 'Cinema',
            '03': 'Sports',
            '04': 'Game',
            '09': 'Photos',
            '05': 'Expert 1',
            '06': 'Expert 2',
            '11': 'Calibration'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('PictureMode', value, {'Display ID': str(ID)})

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            PowerCmdString = 'ka {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            PowerCmdString = 'ka {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, {'Display ID': str(ID)})

    def SetTileMode(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            Value = '{0:X}{1:X}'.format(int(qualifier['Column']), int(qualifier['Row']))
            TileModeCmdString = 'dd {0} {1}\r'.format(DisplayID, Value)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            TileID = int(qualifier['Tile ID'])
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(DisplayID, TileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            VideoMuteCmdString = 'kd {0} {1}\r'.format(DisplayID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            VideoMuteCmdString = 'kd {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('VideoMute', value, {'Display ID': str(ID)})

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 0 <= int(ID) <= 1000 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            DisplayID = '{0:02X}'.format(int(ID))
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(DisplayID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            ID = '0'
        if 1 <= int(ID) <= 1000:
            DisplayID = '{0:02X}'.format(int(ID))
            VolumeCmdString = 'kf {0} FF\r'.format(DisplayID)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        ID = int(match.group(1).decode(), 16)
        if 1 <= ID <= 1000:
            value = int(match.group(2).decode(), 16)
            self.WriteStatus('Volume', value, {'Display ID': str(ID)})

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'OK' in response:
            return response
        elif b'NG' in response:
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DisplayID == '00':
            self.Discard('Inappropriate Command ' + command)
        elif command not in ['MasterPower'] and 'Broadcast' in [qualifier['Display ID']]:
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

        State = {
            'u': 'Auto Image',
            'i': 'Tile Position',
            'c': 'Aspect Ratio, Menu Navigation or Keypad',
            'e': 'Audio Mute',
            'q': 'Energy Saving',
            'm': 'Executive Mode',
            'b': 'Input',
            'a': 'Power',
            'd': 'Video Mute, Tile Mode',
            'f': 'Volume',
            'x': 'Picture Mode'
        }

        temp1 = State[match.group(1).decode().lower()]
        temp2 = match.group(2).decode().upper()
        temp3 = match.group(3).decode()
        value = '{0} Error, DisplayID {1}: {2}'.format(temp1, temp2, temp3)
        self.Error([value])

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


class DeviceEthernetClass:
    def __init__(self):
        self.Debug = False
        self._DisplayID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'EnergySaving': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PowerOff': {'Status': {}},
            'TileMode': {'Parameters': ['Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters': ['Tile ID'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DisplayID(self):
        return self._DisplayID

    @DisplayID.setter
    def DisplayID(self, value):
        if value == 'Broadcast':
            self._DisplayID = '00'
        elif 1 <= int(value) <= 1000:
            self._DisplayID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': '02',
            'Just Scan': '09',
            'Original': '06',
            '4:3': '01',
            '58:9': '21',
            'Vertical Zoom': '30',
            'All Directional Zoom': '31'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ju {0} 01\r'.format(self.DisplayID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetEnergySaving(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04',
            'Screen Off': '05'
        }

        EnergySavingCmdString = 'jq {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('EnergySaving', EnergySavingCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB': '60',
            'HDMI 1(PC)': 'A0',
            'HDMI 1(DTV)': '90',
            'DVI-D (PC)': '70',
            'DVI-D (DTV)': '80',
            'DISPLAYPORT (PC)': 'D0',
            'DISPLAYPORT (DTV)': 'C0',
            'OPS (PC)': 'A8',
            'OPS (DTV)': '98',
            'HDMI 2(PC)': 'A1',
            'HDMI 2(DTV)': '91'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19'
        }

        KeypadCmdString = 'mc {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': '00',
            'Standard': '01',
            'APS': '08',
            'Cinema': '02',
            'Sports': '03',
            'Game': '04',
            'Photos': '09',
            'Expert 1': '05',
            'Expert 2': '06',
            'Calibration': '11'
        }

        PictureModeCmdString = 'dx {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'ka {0} 00\r'.format(self.DisplayID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetTileMode(self, value, qualifier):

        Value = '{0:X}{1:X}'.format(int(qualifier['Column']), int(qualifier['Row']))
        TileModeCmdString = 'dd {0} {1}\r'.format(self.DisplayID, Value)
        self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)

    def SetTilePosition(self, value, qualifier):

        TileID = int(qualifier['Tile ID'])
        TilePositionCmdString = 'di {0} {1:02X}\r'.format(self.DisplayID, TileID)
        self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self.DisplayID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self.DisplayID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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