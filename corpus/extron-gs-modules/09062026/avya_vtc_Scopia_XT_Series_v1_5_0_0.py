from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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
        self._NumberOfButton = 5

        self.Models = {
            'Scopia XT5000': self.avya_12_747_5000,
            'Scopia XT4200': self.avya_12_747_others,
            'Scopia XT1200': self.avya_12_747_others,
            'Scopia XTE240': self.avya_12_747_others,
            'Scopia XT7100': self.avya_12_747_7100,
            'Scopia XT4300': self.avya_12_747_others,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraPresetFar': {'Parameters': ['Type'], 'Status': {}},
            'CameraPresetNear': {'Parameters': ['Type'], 'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'Layout': {'Status': {}},
            'PanTiltFar': {'Parameters': ['CameraSelect'], 'Status': {}},
            'PanTiltNear': {'Parameters': ['CameraSelect'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Presentation': {'Status': {}},
            'PresentationStatus': {'Status': {}},
            'ReceiveVolume': {'Status': {}},
            'Recording': {'Parameters': ['Location'], 'Status': {}},
            'RecordingStatus': {'Status': {}},
            'SelfView': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'VideoPrivacy': {'Status': {}},
            'ZoomFar': {'Parameters': ['CameraSelect'], 'Status': {}},
            'ZoomNear': {'Parameters': ['CameraSelect'], 'Status': {}},
        }

        self.Name = compile('AT\[\<DRN(.+)\r\s*(|[\x00-\xFF]+)AT\[\<DRC')
        self.PhoneNumber = compile('AT\[\<DR[1-8](.+)')
        self.NoRec = compile('AT\[\<DR0A[0-9]{3}(2)(.+)')
        self.NoRecordFound = False
        self.Local = PhonebookGenerator()
        self.PhoneBook = {}
        self.StartingEntry = 1
        self._NumberOfButton = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'AT\[\<IR([1-5])\r'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'AT\[\<CB(0|1|5|6|7)(02|05|07|08|09).*?\r'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'AT\[\<SC(..)(7|8|A|9|6|3|5)'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'AT\[\<SR(1|0|2)\r'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'AT\[\<SV(-[0-4][0-9]|0[0-2][0-9])\r'), self.__MatchReceiveVolume, None)
            self.AddMatchString(compile(b'AT\[\<SD(01|02|03|04|05|06|00)\r'), self.__MatchLayout, None)
            self.AddMatchString(compile(b'AT\[\<ST(1|0)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(compile(b'AT\[\<SQ0(1|0)08.*?\r'), self.__MatchPresentationStatus, None)
            self.AddMatchString(compile(b'AT\[\<SNA(1|2|3|4|5).*?\r'), self.__MatchRecordingStatus, None)
            self.AddMatchString(compile(b'AT\[\<SS(1|0)\r'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'AT\[\<SM(1|0)\r'), self.__MatchTransmitMute, None)
            self.AddMatchString(compile(b'AT\[\<SP(1|0)\r'), self.__MatchVideoPrivacy, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self._NumberOfPhonebookSearch = int(value)

    def UpdateCallStatus(self, value, qualifier):

        CallStatusCmdString = b'\xAA\xAA\x00\x00\x00\x08AT\x5B?CB0\x0D'
        self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)

    def __MatchCallStatus(self, match, qualifier):

        CallStatusNames = {
            '09': 'Connected',
            '02': 'Not In Call',
            '08': 'Ringing',
            '07': 'Dialing',
            '05': 'Connected',
            '7': 'Connected',
            '8': 'Connected',
            'A': 'Not In Call',
            '9': 'Not In Call',
            '6': 'Ringing',
            '3': 'Dialing',
            '5': 'Dialing',
        }

        value = CallStatusNames[match.group(2).decode()]
        self.WriteStatus('CallStatus', value, None)

    def SetCameraPresetFar(self, value, qualifier):

        TypeStateValues = {
            'Recall': b'5',
            'Save': b'6'
        }
        Type = qualifier['Type']
        PresetStates = {
            0: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'0\x0D']),
            1: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'1\x0D']),
            2: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'2\x0D']),
            3: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'3\x0D']),
            4: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'4\x0D']),
            5: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'5\x0D']),
            6: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'6\x0D']),
            7: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'7\x0D']),
            8: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'8\x0D']),
            9: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'9\x0D']),
            10: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'A\x0D']),
            11: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'B\x0D']),
            12: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'C\x0D']),
            13: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'D\x0D']),
            14: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'E\x0D']),
            15: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF011', TypeStateValues[Type], b'F\x0D'])
        }

        if Type in TypeStateValues:
            CommandString = PresetStates[int(value)]
            self.__SetHelper('CameraPresetFar', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetFar')

    def SetCameraPresetNear(self, value, qualifier):

        TypeStateValues = {
            'Recall': b'5',
            'Save': b'6'
        }

        Type = qualifier['Type']
        PresetStates = {
            0: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'0\x0D']),
            1: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'1\x0D']),
            2: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'2\x0D']),
            3: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'3\x0D']),
            4: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'4\x0D']),
            5: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'5\x0D']),
            6: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'6\x0D']),
            7: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'7\x0D']),
            8: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'8\x0D']),
            9: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'9\x0D']),
            10: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'A\x0D']),
            11: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'B\x0D']),
            12: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'C\x0D']),
            13: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'D\x0D']),
            14: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'E\x0D']),
            15: b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF010', TypeStateValues[Type], b'F\x0D'])
        }

        if Type in TypeStateValues:
            CommandString = PresetStates[int(value)]
            self.__SetHelper('CameraPresetNear', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetNear')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SR1\x0D',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SR0\x0D'
        }

        DoNotDisturbCmdString = ValueStateValues[value]
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbCmdString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?SR\x0D'
        self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'On except Trusted'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DoNotDisturb', value, None)

    def SetDTMF(self, value, qualifier):

        DTMFStates = {
            '0': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF0\x0D',
            '1': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF1\x0D',
            '2': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF2\x0D',
            '3': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF3\x0D',
            '4': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF4\x0D',
            '5': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF5\x0D',
            '6': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF6\x0D',
            '7': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF7\x0D',
            '8': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF8\x0D',
            '9': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF9\x0D',
            '#': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF\x23\x0D',
            '*': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26CF\x2A\x0D',
        }

        CommandString = DTMFStates[value]
        self.__SetHelper('DTMF', CommandString, value, qualifier)

    def SetHook(self, value, qualifier):

        

        if value == 'Dial':
            number = qualifier['Number']
            if number:
                length = bytes([len(number) + 10])
                if '.' in number:
                    CommandString = b''.join([b'\xAA\xAA\x00\x00\x00', length, b'AT\x5B\x26CD181', number.encode(), b'\x0D'])
                    self.__SetHelper('Hook', CommandString, value, qualifier)
                else:
                    CommandString = b''.join([b'\xAA\xAA\x00\x00\x00', length, b'AT\x5B\x26CD180', number.encode(), b'\x0D'])
                    self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Hang up':
            number = qualifier['Number']
            if number:
                if '.' in number:
                    CommandString = b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26CH11\x0D'
                    self.__SetHelper('Hook', CommandString, value, qualifier)
                else:
                    CommandString = b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26CH10\x0D'
                    self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Answer':
            CommandString = b'\xAA\xAA\x00\x00\x00\x13AT\x5B\x26CG100000000010\x0D'
            self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Reject':
            CommandString = b'\xAA\xAA\x00\x00\x00\x13AT\x5B\x26CG000000000010\x0D'
            self.__SetHelper('Hook', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def SetIRRemoteEmulation(self, value, qualifier):

        IRRemoteEmulationStates = {
            '0': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW000\x0D',
            '1': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW001\x0D',
            '2': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW002\x0D',
            '3': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW003\x0D',
            '4': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW004\x0D',
            '5': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW005\x0D',
            '6': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW006\x0D',
            '7': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW007\x0D',
            '8': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW008\x0D',
            '9': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW009\x0D',
            '*': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW010\x0D',
            '#': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW011\x0D',
            'Power': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW013\x0D',
            '?': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW014\x0D',
            'Call': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW015\x0D',
            'Disconnect': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW016\x0D',
            'C': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW017\x0D',
            'Layout': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW025\x0D',
            'PIP': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW026\x0D',
            'Up': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW027\x0D',
            'Right': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW028\x0D',
            'Down': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW029\x0D',
            'Left': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW030\x0D',
            'Enter': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW031\x0D',
            'Memo': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW032\x0D',
            'Select': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW033\x0D',
            'Near': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW035\x0D',
            'Far': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW036\x0D',
            'Zoom Out': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW037\x0D',
            'Zoom In': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW038\x0D',
            'Video Privacy': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW039\x0D',
            'Volume Down': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW040\x0D',
            'Volume Up': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW041\x0D',
            'Mute': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW042\x0D',
            'Presentation': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW043\x0D',
            'Back': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW044\x0D',
            'Input': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW045\x0D',
            'Red': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW046\x0D',
            'Yellow': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW047\x0D',
            'Blue': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW048\x0D',
            'Green': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW049\x0D',
            'Phonebook': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SW018\x0D'
        }

        CommandString = IRRemoteEmulationStates[value]
        self.__SetHelper('IRRemoteEmulation', CommandString, value, qualifier)

    def SetLayout(self, value, qualifier):

        LayoutStates = {
            'Upper Left': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD01\x0D',
            'Upper Right': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD02\x0D',
            'Bottom Left': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD04\x0D',
            'Bottom Right': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD03\x0D',
            'POP': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD06\x0D',
            'PAP': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD05\x0D',
            'Off': b'\xAA\xAA\x00\x00\x00\x09AT\x5B\x26SD00\x0D',
        }

        LayoutCmdString = LayoutStates[value]
        self.__SetHelper('Layout', LayoutCmdString, value, qualifier)

    def UpdateLayout(self, value, qualifier):

        LayoutCmdString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?SD\x0D'
        self.__UpdateHelper('Layout', LayoutCmdString, value, qualifier)

    def __MatchLayout(self, match, tag):

        LayoutNames = {
            '00': 'Off',
            '01': 'Upper Left',
            '02': 'Upper Right',
            '03': 'Bottom Right',
            '04': 'Bottom Left',
            '05': 'PAP',
            '06': 'POP'
        }

        value = LayoutNames[match.group(1).decode()]
        self.WriteStatus('Layout', value, None)

    def SetPanTiltFar(self, value, qualifier):

        ValueStateValues = {
            'Up': b'18U',
            'Down': b'18D',
            'Left': b'17L',
            'Right': b'17R'
        }

        Camera = qualifier['CameraSelect']

        if Camera in self.CameraStates:
            if value == 'Stop':
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B\x26SF0', self.CameraStates[Camera], b'1!\x0D'])
            else:
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF0', self.CameraStates[Camera], ValueStateValues[value], b'\x0D'])
            self.__SetHelper('PanTiltFar', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltFar')

    def SetPanTiltNear(self, value, qualifier):

        ValueStateValues = {
            'Up': b'08U',
            'Down': b'08D',
            'Left': b'07L',
            'Right': b'07R'
        }
        Camera = qualifier['CameraSelect']

        if Camera in self.CameraStates:
            if value == 'Stop':
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B\x26SF0', self.CameraStates[Camera], b'0!\x0D'])
            else:
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF0', self.CameraStates[Camera], ValueStateValues[value], b'\x0D'])
            self.__SetHelper('PanTiltFar', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltNear')

    def SetPhonebookSearch(self, value, qualifier):
        self.Debug = True
        self.StartingEntry = 1
        entries = self.Local.GetEntry(self.StartingEntry, self._NumberOfButton, value)
        button = 1
        for v in entries:
            self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
            button += 1

    def SetPhonebookSearchSet(self, value, qualifier):

        if value < 1 or value > self._NumberOfButton:
            self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            self.Debug = True
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number and number != '***End of list***':
                number = number[number.find(' : ') + 3:]
            else:
                self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookNavigation(self, value, qualifier):

        if value not in ['Up', 'Down', 'Page Up', 'Page Down']:
            self.Discard('Invalid Command for SetPhonebookNavigation')
        else:
            self.Debug = True
            if 'Page' in value:
                NumberOfAdvance = self._NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                tv = self.StartingEntry + NumberOfAdvance
                if tv > 201:
                    start = 200
                    end = 200
                else:
                    start = tv
                    end = tv + self._NumberOfButton
                self.StartingEntry = start
            elif 'Up' in value:
                tv = self.StartingEntry - NumberOfAdvance
                end = self.StartingEntry - NumberOfAdvance + self._NumberOfButton
                if tv < 1:
                    start = 1
                else:
                    start = tv
                self.StartingEntry = start

            entries = self.Local.GetEntry(self.StartingEntry, self._NumberOfButton, None)
            button = 1
            for v in entries:
                self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                button += 1

    def SetPhonebookUpdate(self, value, qualifier):

        self.NoRecordFound = False
        self.UpdatePhonebookUpdate(None, None)

    def UpdatePhonebookUpdate(self, value, qualifier):

        i = 0
        newList = []
        while i < 1000 and self.NoRecordFound is False:
            if i < 10:
                if 'Serial' in self.ConnectionType:
                    QueryString = b''.join([b'AT\x5B?DRA00', str(i).encode(), b'\x0D'])
                else:
                    QueryString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B?DRA00' + str(i).encode() + b'\x0D'])
            elif i < 100:
                if 'Serial' in self.ConnectionType:
                    QueryString = b''.join([b'AT\x5B?DRA0', str(i).encode(), b'\x0D'])
                else:
                    QueryString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B?DRA0', str(i).encode(), b'\x0D'])
            else:
                if 'Serial' in self.ConnectionType:
                    QueryString = b''.join([b'AT\x5B?DRA', str(i).encode(), b'\x0D'])
                else:
                    QueryString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B?DRA', str(i).encode(), b'\x0D'])
            self.Debug = True
            res = self.SendAndWait(QueryString, self.DefaultResponseTimeout, deliTag=b'OK\r')
            if res:
                StopQuery = self.NoRec.search(res.decode("ascii", "ignore"))
                if StopQuery:
                    self.NoRecordFound = True
                else:
                    i += 1
                    PerEntryList = []
                    DictIndex = 0
                    NameGroup = self.Name.search(res.decode("ascii", "ignore"))
                    NAME = NameGroup.group(1)
                    PerEntryList = res.decode("ascii", "ignore").split('\x0D')
                    for x in PerEntryList:
                        PhoneNumberGroup = self.PhoneNumber.search(x)
                        if PhoneNumberGroup:
                            Entry = PhoneNumberGroup.group(1)
                            if Entry != '':

                                newList.append('{0} : {1}'.format(NAME, Entry))

                    self.Local.UpdatePhonebook(newList)
                    entries = self.Local.GetEntry(self.StartingEntry, self._NumberOfButton, None)
                    button = 1
                    for v in entries:
                        self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                        button += 1
            else:
                self.NoRecordFound = True

    def SetPIPMode(self, value, qualifier):

        PIPModeStates = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26ST1\x0D',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26ST0\x0D',

        }

        PIPModeCmdString = PIPModeStates[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?ST\x0D'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        PIPModeNames = {
            '1': 'On',
            '0': 'Off',
        }

        value = PIPModeNames[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\xAA\xAA\x00\x00\x00\x0BAT\x5B\x26SQ0108\x0D',
            'Stop': b'\xAA\xAA\x00\x00\x00\x0BAT\x5B\x26SQ0008\x0D'
        }

        PresentationCmdString = ValueStateValues[value]
        self.__SetHelper('Presentation', PresentationCmdString, value, qualifier)

    def UpdatePresentationStatus(self, value, qualifier):

        PresentationStatusCmdString = b'\xAA\xAA\x00\x00\x00\x08AT\x5B?SQ0\x0D'
        self.__UpdateHelper('PresentationStatus', PresentationStatusCmdString, value, qualifier)

    def __MatchPresentationStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Activated',
            '0': 'Not Activated'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationStatus', value, None)

    def SetReceiveVolume(self, value, qualifier):

        ReceiveVolumeConstraints = {
            'Min': -44,
            'Max': 20
        }
        if ReceiveVolumeConstraints['Min'] <= value <= ReceiveVolumeConstraints['Max']:
            ReceiveVolumeCmdString = b''.join([b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SV', str(value).encode().zfill(3), b'\x0D'])
            self.__SetHelper('ReceiveVolume', ReceiveVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReceiveVolume')

    def UpdateReceiveVolume(self, value, qualifier):

        CommandString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?SV\x0D'
        self.__UpdateHelper('ReceiveVolume', CommandString, value, qualifier)

    def __MatchReceiveVolume(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('ReceiveVolume', value, None)

    def SetRecording(self, value, qualifier):

        LocationStates = {
            'USB': b'1',
            'Server': b'2'
        }

        ValueStateValues = {
            'Start': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SNA1',
            'Pause': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SNA2',
            'Resume': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SNA3',
            'Stop': b'\xAA\xAA\x00\x00\x00\x0AAT\x5B\x26SNA4'
        }

        location = qualifier['Location']
        if location in LocationStates:
            RecordingCmdString = b''.join([ValueStateValues[value], LocationStates[location], b'\x0D'])
            self.__SetHelper('Recording', RecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecording')

    def UpdateRecordingStatus(self, value, qualifier):

        RecordingStatusCmdString = b'\xAA\xAA\x00\x00\x00\x08AT\x5B?SNA\x0D'
        self.__UpdateHelper('RecordingStatus', RecordingStatusCmdString, value, qualifier)

    def __MatchRecordingStatus(self, match, tag):

        ValueStateValues = {
            '2': 'Recording on USB',
            '4': 'Recording on Server',
            '5': 'Recording on Server Initiated',
            '3': 'Pause',
            '1': 'Stop'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordingStatus', value, None)

    def SetSelfView(self, value, qualifier):

        SelfViewStates = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SS1\x0D',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SS0\x0D',
        }

        SelfViewCmdString = SelfViewStates[value]
        self.__SetHelper('SelfView', SelfViewCmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):

        SelfViewCmdString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?SS\x0D'
        self.__UpdateHelper('SelfView', SelfViewCmdString, value, qualifier)

    def __MatchSelfView(self, match, tag):

        SelfViewNames = {
            '1': 'On',
            '0': 'Off',
        }

        value = SelfViewNames[match.group(1).decode()]
        self.WriteStatus('SelfView', value, None)

    def SetTransmitMute(self, value, qualifier):

        TransmitMuteStates = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SM1\x0D',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SM0\x0D',
        }

        TransmitMuteCmdString = TransmitMuteStates[value]
        self.__SetHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def UpdateTransmitMute(self, value, qualifier):

        TransmitMuteCmdString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?SM\x0D'
        self.__UpdateHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def __MatchTransmitMute(self, match, tag):

        TransmitMuteNames = {
            '1': 'On',
            '0': 'Off',
        }

        value = TransmitMuteNames[match.group(1).decode()]
        self.WriteStatus('TransmitMute', value, None)

    def SetVideoPrivacy(self, value, qualifier):

        VideoPrivacyStates = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SP1\x0D',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26SP0\x0D',
        }

        VideoPrivacyCmdString = VideoPrivacyStates[value]
        self.__SetHelper('VideoPrivacy', VideoPrivacyCmdString, value, qualifier)

    def UpdateVideoPrivacy(self, value, qualifier):

        VideoPrivacyCmdString = b'\xAA\xAA\x00\x00\x00\x07AT\x5B?SP\x0D'
        self.__UpdateHelper('VideoPrivacy', VideoPrivacyCmdString, value, qualifier)

    def __MatchVideoPrivacy(self, match, tag):

        VideoPrivacyNames = {
            '1': 'On',
            '0': 'Off',
        }

        value = VideoPrivacyNames[match.group(1).decode()]
        self.WriteStatus('VideoPrivacy', value, None)

    def SetZoomFar(self, value, qualifier):

        ValueStateValues = {
            'In': b'19+',
            'Out': b'19-'
        }

        Camera = qualifier['CameraSelect']

        if Camera in self.CameraStates:
            if value == 'Stop':
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B\x26SF0', self.CameraStates[Camera], b'1!\x0D'])
            else:
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF0', self.CameraStates[Camera], ValueStateValues[value], b'\x0D'])
            self.__SetHelper('ZoomFar', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomFar')

    def SetZoomNear(self, value, qualifier):

        ValueStateValues = {
            'In': b'09+',
            'Out': b'09-'
        }
        Camera = qualifier['CameraSelect']

        if Camera in self.CameraStates:
            if value == 'Stop':
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0BAT\x5B\x26SF0', self.CameraStates[Camera], b'0!\x0D'])
            else:
                CommandString = b''.join([b'\xAA\xAA\x00\x00\x00\x0CAT\x5B\x26SF0', self.CameraStates[Camera], ValueStateValues[value], b'\x0D'])
            self.__SetHelper('ZoomNear', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomNear')

    def __MatchErrors(self, match, tag):

        DeviceErrorCodes = {
            '1': 'Bad parameter',
            '2': 'Unknown message',
            '3': 'Wrong message length',
            '4': 'Bad mode',
            '5': 'Unable to execute command',
        }
        if match.group(1).decode() in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode()]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
                
        if 'Serial' in self.ConnectionType:
            self.Send(commandstring[6:])
        else:
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
                
            if 'Serial' in self.ConnectionType:
                self.Send(commandstring[6:])
            else:
                self.Send(commandstring)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self._SetOnConnectedString()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
    
    def _SetOnConnectedString(self,):
        if 'Serial' in self.ConnectionType:
            self.Send(b'AT\x5B\x26IPV\x0D')
        else:
            self.Send(b'\xAA\xAA\x00\x00\x00\x08AT\x5B\x26IPV\x0D')
            
    def avya_12_747_others(self):

        self.CameraStates = {
            'HD1': b'1',
            'HD2': b'2',
            'DVI': b'8'
        }

    def avya_12_747_5000(self):

        self.CameraStates = {
            'HD1': b'1',
            'HD2': b'3',
            'HD3': b'4',
            'HD4': b'5',
            'DVI': b'8'
        }

    def avya_12_747_7100(self):

        self.CameraStates = {
            'HD1': b'1',
            'HD2': b'3',
            'HD3': b'4',
            'HD4': b'5',
            'HD5': b'6',
            'DVI': b'8'
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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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


class PhonebookGenerator():
    def __init__(self):
        self.Phonebook=[]

    def UpdatePhonebook(self, newBook):
        """ UpdatePhonebook
        This take in dictionary with key as the name and value as the phone number.

        """
        self.Phonebook = sorted(newBook)

    def GetEntry(self, start, number, searchName = None):
        """ GetEntry
        start is the starting index in the phonebook. the first entry in the phonebook is 1
        number is the number of entry the method would return back to the user. Empty string
            will be used to fill in to the return list if the list is less than the requested 
            number. 
        match is default to None, but if is a string format that will be use to refine the
            the entry name.

        This method will return a list of entry and each entry is formatted as 'name : number'

        """
        retList = []
        book = []
        end = start + number
        matchstring = '^{0}'.format(searchName)
        findMatch = compile(matchstring)
        if searchName != None and searchName != '':
            for k in self.Phonebook:                
                if k.lower().find(searchName.lower()) == 0 or k.lower().find(' '+searchName.lower()) > 0:
                    book.append(k)
        else:
            book = self.Phonebook

        i = 1
        for name in book:
            if i >= start and i < end:
                retList.append(name)
            i += 1

        retList = sorted(retList)
        if i <= end:
            retList.append('***End of list***')
            i += 1
            for i in range(len(retList), end):
                retList.append('')
        return retList
