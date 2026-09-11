from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberOfPhonebookSearch = 5
        self.Models = {
            'Scopia XT5000': self.rvsn_12_468_XT5000,
            'Scopia XT4200': self.rvsn_12_468_XT1200,
            'Scopia XT1200': self.rvsn_12_468_XT1200,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraPresetFar': {'Parameters': ['Type'], 'Status': {}},
            'CameraPresetNear': {'Parameters': ['Type'], 'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'Layout': {'Status': {}},
            'PanTiltFar': {'Parameters': ['Camera Select'], 'Status': {}},
            'PanTiltNear': {'Parameters': ['Camera Select'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PIPMode': {'Status': {}},
            'ReceiveVolume': {'Status': {}},
            'SelfView': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'VideoPrivacy': {'Status': {}},
            'ZoomFar': {'Parameters': ['Camera Select'], 'Status': {}},
            'ZoomNear': {'Parameters': ['Camera Select'], 'Status': {}},
        }

        self.Name = re.compile('AT\[<DRN(.+)\r\s*(|[\x00-\xFF]+)AT\[<DRC')
        self.PhoneNumber = re.compile('AT\[<DR[1-8](.+)')
        self.NoRec = re.compile('AT\[<DR0A[0-9]{3}(2)(.+)')
        self.NoRecordFound = False
        self.Local = PhonebookGenerator()
        self.PhoneBook = {}
        self.StartingEntry = 1
        self.NumberOfButton = 5
        self.PhonebookSearch = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AT\[<CB([1567])(0[25789])\r'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'AT\[<SC(..)([35-9A])'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'AT\[<SV(-[0-4][0-9]|[0-2][0-9]|[0-9]|0[0-2][0-9])\r'), self.__MatchReceiveVolume, None)
            self.AddMatchString(re.compile(b'AT\[<SD(0[0-6])\r'), self.__MatchLayout, None)
            self.AddMatchString(re.compile(b'AT\[<ST([01])\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'AT\[<SS([01])\r'), self.__MatchSelfView, None)
            self.AddMatchString(re.compile(b'AT\[<SM([01])\r'), self.__MatchTransmitMute, None)
            self.AddMatchString(re.compile(b'AT\[<SP([01])\r'), self.__MatchVideoPrivacy, None)
            self.AddMatchString(re.compile(b'AT\[<IR([1-5])\r'), self.__MatchError, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self._NumberOfPhonebookSearch = value

    def UpdateCallStatus(self, value, qualifier):

        CallStatusCmdString = b'\xAA\xAA\x00\x00\x00\x08AT[?CB0\r'
        self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)

    def __MatchCallStatus(self, match, tag):

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

        TypeStates = {
            'Save': '6',
            'Recall': '5'
        }

        if int(value) in range(1, 17):
            Type = TypeStates[qualifier['Type']]
            CameraPresetFarCmdString = b'\xAA\xAA\x00\x00\x00\x0C' + 'AT[&SF011{}{:x}\r'.format(Type, int(value) - 1).encode()
            self.__SetHelper('CameraPresetFar', CameraPresetFarCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetFar')

    def SetCameraPresetNear(self, value, qualifier):

        TypeStates = {
            'Save': '6',
            'Recall': '5'
        }

        if int(value) in range(1, 17):
            Type = TypeStates[qualifier['Type']]
            CameraPresetNearCmdString = b'\xAA\xAA\x00\x00\x00\x0C' + 'AT[&SF010{}{:x}\r'.format(Type, int(value) - 1).encode()
            self.__SetHelper('CameraPresetNear', CameraPresetNearCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetNear')

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '#': '#',
            '*': '*'
        }

        DTMFCmdString = b'\xAA\xAA\x00\x00\x00\x08' + 'AT[&CF{}\r'.format(ValueStateValues[value]).encode()
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        if value == 'Dial':
            number = qualifier['Number']
            length = bytes([len(number) + 10])
            if number:
                if '.' in number:
                    CommandString = b'\xAA\xAA\x00\x00\x00' + length + b'AT[&CD181' + number.encode() + b'\r'  # IP
                    self.__SetHelper('Hook', CommandString, value, qualifier)
                else:
                    CommandString = b'\xAA\xAA\x00\x00\x00' + length + b'AT[&CD180' + number.encode() + b'\r'  # ISDN
                    self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Hang up':
            number = qualifier['Number']
            if number:
                if '.' in number:
                    CommandString = b'\xAA\xAA\x00\x00\x00\x09AT[&CH11\r'  # IP
                    self.__SetHelper('Hook', CommandString, value, qualifier)
                else:
                    CommandString = b'\xAA\xAA\x00\x00\x00\x09AT[&CH10\r'  # ISDN
                    self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Answer':
            CommandString = b'\xAA\xAA\x00\x00\x00\x13AT[&CG100000000010\r'  # Answer
            self.__SetHelper('Hook', CommandString, value, qualifier)
        elif value == 'Reject':
            CommandString = b'\xAA\xAA\x00\x00\x00\x13AT[&CG000000000010\r'  # Reject
            self.__SetHelper('Hook', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def SetIRRemoteEmulation(self, value, qualifier):

        IRRemoteEmulationStates = {
            '0': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW000\r',
            '1': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW001\r',
            '2': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW002\r',
            '3': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW003\r',
            '4': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW004\r',
            '5': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW005\r',
            '6': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW006\r',
            '7': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW007\r',
            '8': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW008\r',
            '9': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW009\r',
            '*': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW010\r',
            '#': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW011\r',
            'Power': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW013\r',
            '?': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW014\r',
            'Call': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW015\r',
            'Disconnect': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW016\r',
            'C': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW017\r',
            'Layout': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW025\r',
            'PIP': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW026\r',
            'Up': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW027\r',
            'Right': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW028\r',
            'Down': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW029\r',
            'Left': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW030\r',
            'Enter': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW031\r',
            'Memo': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW032\r',
            'Select': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW033\r',
            'Near': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW035\r',
            'Far': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW036\r',
            'Zoom Out': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW037\r',
            'Zoom In': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW038\r',
            'Video Privacy': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW039\r',
            'Volume Down': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW040\r',
            'Volume Up': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW041\r',
            'Mute': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW042\r',
            'Presentation': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW043\r',
            'Back': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW044\r',
            'Input': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW045\r',
            'Red': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW046\r',
            'Yellow': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW047\r',
            'Blue': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW048\r',
            'Green': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW049\r',
            'Phonebook': b'\xAA\xAA\x00\x00\x00\x0AAT[&SW018\r'
        }
        IRRemoteEmulationCmdString = IRRemoteEmulationStates[value]
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def SetLayout(self, value, qualifier):

        LayoutStates = {
            'Upper Left': b'\xAA\xAA\x00\x00\x00\x09AT[&SD01\r',
            'Upper Right': b'\xAA\xAA\x00\x00\x00\x09AT[&SD02\r',
            'Bottom Left': b'\xAA\xAA\x00\x00\x00\x09AT[&SD04\r',
            'Bottom Right': b'\xAA\xAA\x00\x00\x00\x09AT[&SD03\r',
            'POP': b'\xAA\xAA\x00\x00\x00\x09AT[&SD06\r',
            'PAP': b'\xAA\xAA\x00\x00\x00\x09AT[&SD05\r',
            'Off': b'\xAA\xAA\x00\x00\x00\x09AT[&SD00\r',
        }

        LayoutCmdString = LayoutStates[value]
        self.__SetHelper('Layout', LayoutCmdString, value, qualifier)

    def UpdateLayout(self, value, qualifier):

        LayoutCmdString = b'\xAA\xAA\x00\x00\x00\x07AT[?SD\r'
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
            'Up': '8U',
            'Down': '8D',
            'Left': '7L',
            'Right': '7R',
            'Stop': '0!'
        }
        PanTiltFarCmdString = b'\xAA\xAA\x00\x00\x00\x0C' + 'AT[&SF0{}1{}\r'.format(self.CameraSelectStates[qualifier['Camera Select']], ValueStateValues[value]).encode()
        self.__SetHelper('PanTiltFar', PanTiltFarCmdString, value, qualifier)

    def SetPanTiltNear(self, value, qualifier):

        ValueStateValues = {
            'Up': '8U',
            'Down': '8D',
            'Left': '7L',
            'Right': '7R',
            'Stop': '0!'
        }

        PanTiltNearCmdString = b'\xAA\xAA\x00\x00\x00\x0C' + 'AT[&SF0{}0{}\r'.format(self.CameraSelectStates[qualifier['Camera Select']], ValueStateValues[value]).encode()
        self.__SetHelper('PanTiltNear', PanTiltNearCmdString, value, qualifier)

    def SetPhonebookNavigation(self, value, qualifier):

        if value not in ['Up', 'Down', 'Page Up', 'Page Down']:
            self.Discard('Invalid Command for SetPhonebookNavigation')
        else:
            if 'Page' in value:
                if ('Down' in value and self.StartingEntry <= len(self.Local.Phonebook)) or 'Up' in value:
                    NumberOfAdvance = self.NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value and self.StartingEntry <= len(self.Local.Phonebook):
                start = self.StartingEntry + NumberOfAdvance
                if start > 201:
                    self.StartingEntry = 200
                else:
                    self.StartingEntry = start

            elif 'Up' in value:
                start = self.StartingEntry - NumberOfAdvance
                if start < 1:
                    self.StartingEntry = 1
                else:
                    self.StartingEntry = start

            entries = self.Local.GetEntry(self.StartingEntry, self.NumberOfButton, self.PhonebookSearch)
            button = 1
            for v in entries:
                self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                button += 1

    def SetPhonebookSearch(self, value, qualifier):

        self.StartingEntry = 1
        self.PhonebookSearch = value
        entries = self.Local.GetEntry(self.StartingEntry, self.NumberOfButton, self.PhonebookSearch)
        button = 1
        for v in entries:
            self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
            button += 1

    def SetPhonebookSearchSet(self, value, qualifier):

        if 1 <= value <= 10:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number:
                number = number[number.find(' : ') + 3:]
                self.SetHook('Dial', {'Number': number})
        else:
            self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        self.NoRecordFound = False
        self.UpdatePhonebookUpdate(None, None)

    def UpdatePhonebookUpdate(self, value, qualifier):

        i = 0
        newList = []
        while i < 1000 and not self.NoRecordFound:
            if i < 10:
                res = self.SendAndWait(b'\xAA\xAA\x00\x00\x00\x0AAT\x5B?DRA00' + str(i).encode() + b'\r', self.DefaultResponseTimeout, deliTag=b'OK\r')
            elif i < 100:
                res = self.SendAndWait(b'\xAA\xAA\x00\x00\x00\x0AAT\x5B?DRA0' + str(i).encode() + b'\r', self.DefaultResponseTimeout, deliTag=b'OK\r')
            else:
                res = self.SendAndWait(b'\xAA\xAA\x00\x00\x00\x0AAT\x5B?DRA' + str(i).encode() + b'\r', self.DefaultResponseTimeout, deliTag=b'OK\r')
            if res:
                StopQuery = self.NoRec.search(res.decode())
                if StopQuery:
                    self.NoRecordFound = True
                else:
                    try:
                        i += 1
                        NameGroup = self.Name.search(res.decode())
                        NAME = NameGroup.group(1)
                        PerEntryList = res.decode().split('\r')
                        for x in PerEntryList:
                            PhoneNumberGroup = self.PhoneNumber.search(x)
                            if PhoneNumberGroup:
                                Entry = PhoneNumberGroup.group(1)
                                if Entry != '':
                                    newList.append('{0} : {1}'.format(NAME, Entry))
                        self.Local.UpdatePhonebook(newList)
                        entries = self.Local.GetEntry(self.StartingEntry, self.NumberOfButton, self.PhonebookSearch)
                        button = 1
                        for v in entries:
                            self.WriteStatus('PhonebookSearchResult', '{0}'.format(v), {'Button': button})
                            button += 1
                    except (ValueError, IndexError):
                        self.Error(['Phonebook Update: Invalid/unexpected response'])
            else:
                self.NoRecordFound = True

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT[&ST1\r',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT[&ST0\r',
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = b'\xAA\xAA\x00\x00\x00\x07AT[?ST\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetReceiveVolume(self, value, qualifier):

        if -44 <= value <= 20:
            ReceiveVolumeCmdString = b'\xAA\xAA\x00\x00\x00\x0AAT[&SV' + str(value).encode().zfill(3) + b'\r'  # According to protocol Volume Audio Rx (3 bytes): "-44".."20", it should be "020"
            self.__SetHelper('ReceiveVolume', ReceiveVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReceiveVolume')

    def UpdateReceiveVolume(self, value, qualifier):

        ReceiveVolumeCmdString = b'\xAA\xAA\x00\x00\x00\x07AT[?SV\r'
        self.__UpdateHelper('ReceiveVolume', ReceiveVolumeCmdString, value, qualifier)

    def __MatchReceiveVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('ReceiveVolume', value, None)

    def SetSelfView(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT[&SS1\r',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT[&SS0\r'
        }

        SelfViewCmdString = ValueStateValues[value]
        self.__SetHelper('SelfView', SelfViewCmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):

        SelfViewCmdString = b'\xAA\xAA\x00\x00\x00\x07AT[?SS\r'
        self.__UpdateHelper('SelfView', SelfViewCmdString, value, qualifier)

    def __MatchSelfView(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SelfView', value, None)

    def SetTransmitMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT[&SM1\r',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT[&SM0\r'
        }

        TransmitMuteCmdString = ValueStateValues[value]
        self.__SetHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def UpdateTransmitMute(self, value, qualifier):

        TransmitMuteCmdString = b'\xAA\xAA\x00\x00\x00\x07AT[?SM\r'
        self.__UpdateHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def __MatchTransmitMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TransmitMute', value, None)

    def SetVideoPrivacy(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xAA\x00\x00\x00\x08AT[&SP1\r',
            'Off': b'\xAA\xAA\x00\x00\x00\x08AT[&SP0\r'
        }

        VideoPrivacyCmdString = ValueStateValues[value]
        self.__SetHelper('VideoPrivacy', VideoPrivacyCmdString, value, qualifier)

    def UpdateVideoPrivacy(self, value, qualifier):

        VideoPrivacyCmdString = b'\xAA\xAA\x00\x00\x00\x07AT[?SP\r'
        self.__UpdateHelper('VideoPrivacy', VideoPrivacyCmdString, value, qualifier)

    def __MatchVideoPrivacy(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoPrivacy', value, None)

    def SetZoomFar(self, value, qualifier):

        ValueStateValues = {
            'In': '9+',
            'Out': '9-',
            'Stop': '!'
        }

        ZoomFarCmdString = b'\xAA\xAA\x00\x00\x00\x0C' + 'AT[&SF0{}1{}\r'.format(self.CameraSelectStates[qualifier['Camera Select']], ValueStateValues[value]).encode()
        self.__SetHelper('ZoomFar', ZoomFarCmdString, value, qualifier)

    def SetZoomNear(self, value, qualifier):

        ValueStateValues = {
            'In': '9+',
            'Out': '9-',
            'Stop': '!'
        }

        ZoomNearCmdString = b'\xAA\xAA\x00\x00\x00\x0C' + 'AT[&SF0{}0{}\r'.format(self.CameraSelectStates[qualifier['Camera Select']], ValueStateValues[value]).encode()
        self.__SetHelper('ZoomNear', ZoomNearCmdString, value, qualifier)

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
        self.counter = 0

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
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def rvsn_12_468_XT5000(self):

        self.CameraSelectStates = {
            'HD1': '1',
            'HD2': '3',
            'HD3': '4',
            'HD4': '5',
            'DVI': '8',
            'USB': '2'
        }

    def rvsn_12_468_XT1200(self):

        self.CameraSelectStates = {
            'HD1': '1',
            'HD2': '3',
            'DVI': '8'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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


class PhonebookGenerator:
    def __init__(self):
        self.Phonebook = []

    def UpdatePhonebook(self, newBook):

        self.Phonebook = sorted(newBook)

    def GetEntry(self, start, number, searchName=None):
        print('start: ', start)
        print('number:', number)
        retList = []
        book = []
        end = start + number
        if searchName is not None and searchName != '':
            for k in self.Phonebook:
                if k.lower().find(searchName.lower()) == 0 or k.lower().find(' ' + searchName.lower()) > 0:
                    book.append(k)
        else:
            book = self.Phonebook
            
        retList = book[start:end]
        retList = sorted(retList)
        
        if len(retList) < number:
            retList.append('***End of list***')
            for _ in range(len(retList), number):
                retList.append('')
        return retList
        