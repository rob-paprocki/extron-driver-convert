from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
import time
from extronlib.system import ProgramLog

class DeviceSerialClass:
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
        self.Models = {
            'PN-R603': self.shrp_10_217_R,
            'PN-R703': self.shrp_10_217_R,
            'PN-R903': self.shrp_10_217_R,
            'PN-U423': self.shrp_10_217_U,
            'PN-V600': self.shrp_10_217_V,
            'PN-U473': self.shrp_10_217_U,
            'PN-U553': self.shrp_10_217_U,
            'PN-V601': self.shrp_10_217_V,
            'PN-V602': self.shrp_10_217_V,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AssignID': {'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'BezelAdjust': {'Parameters': ['Device ID', 'Bezel'], 'Status': {}},
            'BezelWidth': {'Parameters': ['Device ID', 'Side'], 'Status': {}},
            'BlackLevel': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'Colors': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'Enlarge': {'Parameters': ['Device ID'], 'Status': {}},
            'IDCheck': {'Status': {}},
            'ImageLocation': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureInPicture': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'Sharpness': {'Parameters': ['Device ID'], 'Status': {}},
            'Tint': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self.IDSent = False

        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '1'  


        self.Regex = compile(rb'\d{1,3} \d{3}\r\n|ERR\r\n|ERR \d\d\d\r\n')
 
    def DeviceIDHandler(self, Callback, value, qualifier):
        if qualifier and 'Device ID' in qualifier:
            if qualifier['Device ID'] == 'Broadcast' or qualifier['Device ID'] == '0':
                qualifier['Device ID'] = '0'
                if Callback.startswith('Update'):
                    self.Discard('Invalid Command')
                    return False
            elif not (1 <= int(qualifier['Device ID']) <= 255):
                self.Discard('Invalid Command')
                return False
            self.Callback = Callback
            self.valueCallback = value
            self.qualifierCallback = qualifier
            if self.SelectedID == qualifier['Device ID']:
                self.IDSent = False
                self.ExpiryTime = 0
                return True
            elif (self.ExpiryTime != 0) and (self.ExpiryTime <= time.monotonic()):
                self.IDSent = False
                self.ExpiryTime = 0
                self.Error(['Response timeout: Unable to set Device ID'])
            else:
                return self.IDLK_Callback()
        else:
            self.Discard('Invalid Command')

    def IDLK_Callback(self):
    
        if not self.IDSent:
            self.IDSent = True
            CmdString = 'IDLK{0:04d}\r\n'.format(int(self.qualifierCallback['Device ID']))
            self.SetIDLK(CmdString, None)
        else:
            getattr(self, self.Callback)(self.valueCallback, self.qualifierCallback)

    def SetIDLK(self, CmdString, qualifier):
        self.ExpiryTime = time.monotonic() + 5
        self.Send(CmdString)

        if self.qualifierCallback['Device ID'] == '0':
            self.SelectedID = '0'

        self.IDLK_Callback()

    def SetAssignID(self, value, qualifier):
        self.__SetHelper('AssignID', 'IDST001+\r\n', value, qualifier)

    def SetIDCheck(self, value, qualifier):
        self.__SetHelper('IDCheck', 'IDCK0000\r\n', value, qualifier)

    def __MatchDeviceOK(self, match, tag):
        self.SelectedID = str(int(match.group(2).decode()))

    def SetAspectRatio(self, value, qualifier):

        inputStatus = self.ReadStatus('Input', qualifier)  # get current input status
        if inputStatus and value in self.AspectRatioStateValues[inputStatus]:
            AspectRatioCmdString = 'WIDE{0: 4}\r\n'.format(self.AspectRatioStateValues[inputStatus][value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        inputStatus = self.ReadStatus('Input', qualifier)  # get current input status
        if inputStatus:
            if self.DeviceIDHandler('UpdateAspectRatio', value, qualifier):
                res = self.__UpdateHelper('AspectRatio', 'WIDE????\r\n', value, qualifier)
                if res:
                    try:
                        value = self.AspectRatioStateNames[inputStatus][int(res[0])]
                        self.WriteStatus('AspectRatio', value, qualifier)
                    except (KeyError, IndexError, ValueError):
                        self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': 1,
            'Off': 0,
            }
        if value in AudioMuteStateValues and self.DeviceIDHandler('SetAudioMute', value, qualifier):
            if qualifier['Device ID'] == '0':
                AudioMuteCmdString = 'MUTE{0: 3}+\r\n'.format(AudioMuteStateValues[value])
            else:
                AudioMuteCmdString = 'MUTE{0: 4}\r\n'.format(AudioMuteStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateNames = {
            1	: 'On',
            0	: 'Off'
        }

        if self.DeviceIDHandler('UpdateAudioMute', value, qualifier):
            res = self.__UpdateHelper('AudioMute', 'MUTE????\r\n', value, qualifier)
            if res:
                try:
                    value = AudioMuteStateNames[int(res[0])]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        if qualifier['Device ID'] == '0':
            self.__SetHelper('AutoImage', 'AGIN001+\r\n', value, qualifier)
        else:
            self.__SetHelper('AutoImage', 'AGIN0001\r\n', value, qualifier)
 

    def SetEnlarge(self, value, qualifier):

        EnlargeStateValues = {
            '2x2' : 1,
            '3x3' : 2,
            '4x4' : 3,
            '5x5' : 4,
            'Off' : 0,
            }
        if value in EnlargeStateValues and self.DeviceIDHandler('SetEnlarge', value, qualifier):
            if qualifier['Device ID'] == '0':
                EnlargeCmdString = 'EMAG{0: 3}+\r\n'.format(EnlargeStateValues[value])
            else:
                EnlargeCmdString = 'EMAG{0: 4}\r\n'.format(EnlargeStateValues[value])
            self.__SetHelper('Enlarge', EnlargeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEnlarge')

    def UpdateEnlarge(self, value, qualifier):

        EnlargeStateNames = {
            1	:	'2x2',
            2	:	'3x3',
            3	:	'4x4',
            4	:	'5x5',
            0	:	'Off',
            }

        if self.DeviceIDHandler('UpdateEnlarge', value, qualifier):
            res = self.__UpdateHelper('Enlarge', 'EMAG????\r\n', value, qualifier)
            if res:
                try:
                    value = EnlargeStateNames[int(res[0])]
                    self.WriteStatus('Enlarge', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetImageLocation(self, value, qualifier):

        ImageLocationStateValues = {
            '1x2' : 12,'1x3' : 13,'1x4' : 14,'1x5' : 15,
            '2x1' : 21,'2x2' : 22,'2x3' : 23,'2x4' : 24,'2x5' : 25,
            '3x1' : 31,'3x2' : 32,'3x3' : 33,'3x4' : 34,'3x5' : 35,
            '4x1' : 41,'4x2' : 42,'4x3' : 43,'4x4' : 44,'4x5' : 45,
            '5x1' : 51,'5x2' : 52,'5x3' : 53,'5x4' : 54,'5x5' : 55
            }

        if value in ImageLocationStateValues and self.DeviceIDHandler('SetImageLocation', value, qualifier):
            if qualifier['Device ID'] == '0':
                ImageLocationCmdString = 'EPHV{0: 3}+\r\n'.format(ImageLocationStateValues[value])
            else:
                ImageLocationCmdString = 'EPHV{0: 4}\r\n'.format(ImageLocationStateValues[value])
            self.__SetHelper('ImageLocation', ImageLocationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageLocation')

    def UpdateImageLocation(self, value, qualifier):

        ImageLocationStateNames = {
            12	: '1x2', 13	: '1x3',14 : '1x4',15	: '1x5',
            21	: '2x1', 22	: '2x2',23 : '2x3',24	: '2x4',25 :	'2x5',
            31	: '3x1', 32	: '3x2',33 : '3x3',34	: '3x4',35 :	'3x5',
            41	: '4x1', 42	: '4x2',43 : '4x3',44	: '4x4',45 :	'4x5',
            51	: '5x1', 52	: '5x2',53 : '5x3',54	: '5x4',55 :	'5x5'
            }

        if self.DeviceIDHandler('UpdateImageLocation', value, qualifier):
            res = self.__UpdateHelper('ImageLocation', 'EPHV????\r\n', value, qualifier)
            if res:
                try:
                    value = ImageLocationStateNames[int(res[0:2])]
                    self.WriteStatus('ImageLocation', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        if value in self.InputStateValues and self.DeviceIDHandler('SetInput', value, qualifier):
            if qualifier['Device ID'] == '0':
                InputCmdString = 'INPS{0: 3}+\r\n'.format(self.InputStateValues[value])
            else:
                InputCmdString = 'INPS{0: 4}\r\n'.format(self.InputStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        if self.DeviceIDHandler('UpdateInput', value, qualifier):
            res = self.__UpdateHelper('Input', 'INPS????\r\n', value, qualifier)
            if res:
                try:
                    value = self.InputStateNames[int(res[0:-6])]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On'  : 0,
            'Off' : 1,
            'On2' : 2,
            }
        if value in OnScreenDisplayStateValues and self.DeviceIDHandler('SetOnScreenDisplay', value, qualifier):
            if qualifier['Device ID'] == '0':
                OnScreenDisplayCmdString = 'LOSD{0: 3}+\r\n'.format(OnScreenDisplayStateValues[value])
            else:
                OnScreenDisplayCmdString = 'LOSD{0: 4}\r\n'.format(OnScreenDisplayStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateNames = {
            0 : 'On',
            1 : 'Off',
            2 : 'On2',
            }

        if self.DeviceIDHandler('UpdateOnScreenDisplay', value, qualifier):
            res = self.__UpdateHelper('OnScreenDisplay', 'LOSD????\r\n', value, qualifier)
            if res:
                try:
                    value = OnScreenDisplayStateNames[int(res[0])]
                    self.WriteStatus('OnScreenDisplay', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        PictureInPictureStateValues = {
            'PIP'	: 1,
            'PBP 1'	: 2,
            'PBP 2' : 3,
            'Off'	: 0,
            }
        if value in PictureInPictureStateValues and self.DeviceIDHandler('SetPictureInPicture', value, qualifier):
            if qualifier['Device ID'] == '0':
                PictureInPictureCmdString = 'MWIN{0: 3}+\r\n'.format(PictureInPictureStateValues[value])
            else:
                PictureInPictureCmdString = 'MWIN{0: 4}\r\n'.format(PictureInPictureStateValues[value])
            self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPicture')

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPictureStateNames = {
            1 : 'PIP',
            2 : 'PBP 1',
            3 : 'PBP 2',
            0 : 'Off'
            }
        if self.DeviceIDHandler('UpdatePictureInPicture', value, qualifier):
            res = self.__UpdateHelper('PictureInPicture', 'MWIN????\r\n', value, qualifier)
            if res:
                try:
                    value = PictureInPictureStateNames[int(res[0])]
                    self.WriteStatus('PictureInPicture', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        if value in self.PIPInputStateValues and self.DeviceIDHandler('SetPIPInput', value, qualifier):
            if qualifier['Device ID'] == '0':
                PIPInputCmdString = 'MWIP{0: 3}+\r\n'.format(self.PIPInputStateValues[value])
            else:
                PIPInputCmdString = 'MWIP{0: 4}\r\n'.format(self.PIPInputStateValues[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        if self.DeviceIDHandler('UpdatePIPInput', value, qualifier):
            res = self.__UpdateHelper('PIPInput', 'MWIP????\r\n', value, qualifier)
            if res:
                try:
                    value = self.PIPInputStateNames[int(res[0:-6])]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        if self.PIPSizeStateValues['Min'] <= int(value) <= self.PIPSizeStateValues['Max']:
            if qualifier['Device ID'] == '0':
                PIPSizeCmdString = 'MPSZ{0:>3}+\r\n'.format(value)
            else:
                PIPSizeCmdString = 'MPSZ{0:>4}\r\n'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        if self.DeviceIDHandler('UpdatePIPSize', value, qualifier):
            res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n', value, qualifier)
            if res:
                try:
                    value = res[0:-6]
                    if self.PIPSizeStateValues['Min'] <= int(value) <= self.PIPSizeStateValues['Max']:
                        self.WriteStatus('PIPSize', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : 1,
            'Off' : 0,
            }

        if value in PowerStateValues and self.DeviceIDHandler('SetPower', value, qualifier):
            if qualifier['Device ID'] == '0':
                PowerCmdString = 'POWR{0: 3}+\r\n'.format(PowerStateValues[value])
            else:
                PowerCmdString = 'POWR{0: 4}\r\n'.format(PowerStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Input signal waiting mode',
        }

        if self.DeviceIDHandler('UpdatePower', value, qualifier):
            res = self.__UpdateHelper('Power', 'POWR????\r\n', value, qualifier)
            if res:
                try:
                    value = PowerStateNames[res[0]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])
  
    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            if qualifier['Device ID'] == '0':
                VolCmdString = 'VOLM{0: 3}+\r\n'.format(value)
            else:
                VolCmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', VolCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolCmdString = 'VOLM????\r\n'

        if self.DeviceIDHandler('UpdateVolume', value, qualifier) :
            res = self.__UpdateHelper('Volume', VolCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 31:
                        self.WriteStatus('Volume', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 60:
            if qualifier['Device ID'] == '0':
                ContrastCmdString = 'CONT{0: 3}+\r\n'.format(value)
            else:
                ContrastCmdString = 'CONT{0: 4}\r\n'.format(value)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        if self.DeviceIDHandler('UpdateContrast', value, qualifier):
            res = self.__UpdateHelper('Contrast', 'CONT????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('Contrast', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])

    def SetBlackLevel(self, value, qualifier):

        if 0 <= value <= 60:
            if qualifier['Device ID'] == '0':
                BlackLevelCmdString = 'BLVL{0: 3}+\r\n'.format(value)
            else:
                BlackLevelCmdString = 'BLVL{0: 4}\r\n'.format(value)
            self.__SetHelper('BlackLevel', BlackLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlackLevel')

    def UpdateBlackLevel(self, value, qualifier):

        if self.DeviceIDHandler('UpdateBlackLevel', value, qualifier):
            res = self.__UpdateHelper('BlackLevel', 'BLVL????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('BlackLevel', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])

    def SetTint(self, value, qualifier):

        if 0 <= value <= 60:
            if qualifier['Device ID'] == '0':
                TintCmdString = 'TINT{0: 3}+\r\n'.format(value)
            else:
                TintCmdString = 'TINT{0: 4}\r\n'.format(value)
            self.__SetHelper('Tint', TintCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTint')

    def UpdateTint(self, value, qualifier):

        if self.DeviceIDHandler('UpdateTint', value, qualifier):
            res = self.__UpdateHelper('Tint', 'TINT????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('Tint', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])

    def SetColors(self, value, qualifier):

        if 0 <= value <= 60:
            if qualifier['Device ID'] == '0':
                ColorsCmdString = 'COLR{0: 3}+\r\n'.format(value)
            else:
                ColorsCmdString = 'COLR{0: 4}\r\n'.format(value)
            self.__SetHelper('Colors', ColorsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColors')

    def UpdateColors(self, value, qualifier):

        if self.DeviceIDHandler('UpdateColors', value, qualifier):
            res = self.__UpdateHelper('Colors', 'COLR????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('Colors', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])

    def SetSharpness(self, value, qualifier):

        if 0 <= value <= 24:
            if qualifier['Device ID'] == '0':
                SharpnessCmdString = 'SHRP{0: 3}+\r\n'.format(value)
            else:
                SharpnessCmdString = 'SHRP{0: 4}\r\n'.format(value)
            self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):

        if self.DeviceIDHandler('UpdateSharpness', value, qualifier):
            res = self.__UpdateHelper('Sharpness', 'SHRP????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 24:
                        self.WriteStatus('Sharpness', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])

    def SetBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO', 
            'Top'                   : 'BZCT', 
            'Bottom'                : 'BZCB', 
            'Right'                 : 'BZCR', 
            'Left'                  : 'BZCL'
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        bezelValue = qualifier['Bezel']
        if bezelValue in Bezel and value in ValueStateValues and self.DeviceIDHandler('SetBezelAdjust', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = '{0}   {1}+\r\n'.format(Bezel[qualifier['Bezel']], ValueStateValues[value])
            else:
                CmdString = '{0}   {1}\r\n'.format(Bezel[qualifier['Bezel']], ValueStateValues[value])
            self.__SetHelper('BezelAdjust', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBezelAdjust')

    def UpdateBezelAdjust(self, value, qualifier):


        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO????\r\n', 
            'Top'                   : 'BZCT????\r\n', 
            'Bottom'                : 'BZCB????\r\n', 
            'Right'                 : 'BZCR????\r\n', 
            'Left'                  : 'BZCL????\r\n'
        }

        Values = {
            1: 'On',
            0: 'Off'
        }

        if self.DeviceIDHandler('UpdateBezelAdjust', value, qualifier):
            res = self.__UpdateHelper('BezelAdjust', Bezel[qualifier['Bezel']], value, qualifier)
            if res:
                try:
                    self.WriteStatus('BezelAdjust', Values[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV', 
            'Short' : 'BEZH'
        }

        siveValue = qualifier['Side']
        if siveValue in Sides and 0 <= value <= 100 and self.DeviceIDHandler('SetBezelWidth', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = '{0}{1:3}+\r\n'.format(Sides[qualifier['Side']], value)
            else:
                CmdString = '{0}{1:4}\r\n'.format(Sides[qualifier['Side']], value)
            self.__SetHelper('BezelWidth', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBezelWidth')

    def UpdateBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV????\r\n', 
            'Short' : 'BEZH????\r\n'
        }

        if self.DeviceIDHandler('UpdateBezelWidth', value, qualifier):
            res = self.__UpdateHelper('BezelWidth', Sides[qualifier['Side']], value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 100:
                        self.WriteStatus('BezelWidth', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError, ValueError):
                    self.Error(['Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 31:
            if qualifier['Device ID'] == '0':
                CmdString = 'VLMP{0: 3}+\r\n'.format(value)
            else:
                CmdString = 'VLMP{0: 4}\r\n'.format(value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        if self.DeviceIDHandler('UpdateBrightness', value, qualifier) :
            res = self.__UpdateHelper('Brightness', 'VLMP????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 31:
                        self.WriteStatus('Brightness', value, qualifier)
                    else:
                        self.Error(['Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):


        if response:
            if response[:3] == 'ERR':
                ErrorString = '{0}:Communication error or incorrect command'.format(sourceCmdName)
                self.Error([ErrorString])
                response = ''
            if 'OK' in response:
                res = search('OK (\d\d\d)\r\n', response)
                self.SelectedID = str(int(res.group(1)))
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or (qualifier and qualifier['Device ID'] == '0'):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or (command != 'Heartbeat' and qualifier['Device ID'] == '0'):
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())



    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.IDSent = False
        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '0'
        
    def shrp_10_217_R(self):

        self.AspectRatioStateValues ={
            'DVI-I'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'D-SUB Component' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'D-SUB RGB' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'D-SUB Video'		 : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI 1 AV'       : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI 1 PC'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'HDMI 2 AV'   : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI 2 PC'   : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'DisplayPort'   	: {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'Toggle'    :   0
            }

        self.AspectRatioStateNames = {
           'DVI-I'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'D-SUB Component' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'D-SUB RGB' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'D-SUB Video'		 : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI 1 AV'       : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI 1 PC'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'HDMI 2 AV'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI 2 PC'   : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'DisplayPort'  	: {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            }

        self.InputStateValues = {
            'DVI-I'				: 1,
            'D-SUB RGB'			: 2,
            'D-SUB Component'	: 3,
            'D-SUB Video'		: 4,
            'HDMI 1 AV'			: 9,
            'HDMI 1 PC'			: 10,
            'HDMI 2 AV'			: 12,
            'HDMI 2 PC'			: 13,
            'DisplayPort'		: 14,
            }

        self.InputStateNames = {
            1	:	'DVI-I',
            2	:	'D-SUB RGB',
            3	:	'D-SUB Component',
            4	:	'D-SUB Video',
            9	:	'HDMI 1 AV',
            10	:	'HDMI 1 PC',
            12 	:	'HDMI 2 AV',
            13	:	'HDMI 2 PC',
            14	:	'DisplayPort',
            }

        self.PIPInputStateValues = {
            'DVI-I'				: 1,
            'D-SUB RGB'			: 2,
            'D-SUB Component'	: 3,
            'D-SUB Video'		: 4,
            'HDMI 1 AV'			: 9,
            'HDMI 1 PC'			: 10,
            'HDMI 2 AV'			: 12,
            'HDMI 2 PC'			: 13,
            'DisplayPort'		: 14,
            }

        self.PIPInputStateNames = {
            1	:	'DVI-I',
            2	:	'D-SUB RGB',
            3	:	'D-SUB Component',
            4	:	'D-SUB Video',
            9	:	'HDMI 1 AV',
            10	:	'HDMI 1 PC',
            12 	:	'HDMI 2 AV',
            13	:	'HDMI 2 PC',
            14	:	'DisplayPort',
            }

        self.PIPSizeStateValues = {
            'Min' : 1,
            'Max' : 64,
            }

    def shrp_10_217_U(self):

        self.AspectRatioStateValues ={
            'DVI-D'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Custom'	: 6,
                },
            'D-SUB' : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Custom'	: 6,
                },
            'Component' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Custom'	: 6,
                },
            'Video'		 : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Custom'	: 6,
                },
            'HDMI'       : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Custom'	: 6,
                },
            'DisplayPort'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Custom'	: 6,
                },
            'Toggle'    :   0
            }

        self.AspectRatioStateNames = {
           'DVI-D'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'D-SUB' : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'Component' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'Video'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'HDMI' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'DisplayPort'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    6   :  'Custom',
                },
            }

        self.InputStateValues = {
            'DVI-D'			: 1,
            'D-SUB'			: 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI'			: 9,
            'DisplayPort'	: 14,
            }

        self.InputStateNames = {
            1	:	'DVI-D',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI',
            14	:	'DisplayPort',
            }


        self.PIPInputStateValues = {
            'DVI-D'			: 1,
            'D-SUB'			: 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI'			: 9,
            'DisplayPort'	: 14,
            }

        self.PIPInputStateNames = {
            1	:	'DVI-D',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI',
            14	:	'DisplayPort',
            }

        self.PIPSizeStateValues = {
            'Min' : 0,
            'Max' : 2,
            }

    def shrp_10_217_V(self):

        self.AspectRatioStateValues ={
            'DVI-D PC'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'D-SUB' : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'Component' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'Video'		 : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'RGB'       : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'DVI-D AV'  : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'S-Video'   : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI AV'   : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI PC'   	: {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'Toggle'    :   0
            }

        self.AspectRatioStateNames = {
           'DVI-D PC'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'D-SUB' : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'Component' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'Video'		 : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'RGB'       : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'DVI-D AV'  : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'S-Video'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI AV'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI PC'   	: {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            }

        self.InputStateValues = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'RGB'		    : 6,
            'DVI-D AV'		: 7,
            'S-Video'		: 8,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            }

        self.InputStateNames = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            6	:	'RGB',
            7	:	'DVI-D AV',
            8 	:	'S-Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            }

        self.PIPInputStateValues = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'RGB'		    : 6,
            'DVI-D AV'		: 7,
            'S-Video'		: 8,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            }

        self.PIPInputStateNames = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            6	:	'RGB',
            7	:	'DVI-D AV',
            8 	:	'S-Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            }

        self.PIPSizeStateValues = {
            'Min' : 1,
            'Max' : 12,
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}



    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 


class DeviceEthernetClass:
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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {
            'PN-R603': self.shrp_10_217_R,
            'PN-R703': self.shrp_10_217_R,
            'PN-R903': self.shrp_10_217_R,
            'PN-U423': self.shrp_10_217_U,
            'PN-U473': self.shrp_10_217_U,
            'PN-U553': self.shrp_10_217_U,
            'PN-V600': self.shrp_10_217_V,
            'PN-V601': self.shrp_10_217_V,
            'PN-V602': self.shrp_10_217_V,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'BezelAdjust': {'Parameters':['Bezel'], 'Status': {}},
            'BezelWidth': {'Parameters':['Side'], 'Status': {}},           
            'BlackLevel': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Colors': { 'Status': {}},
            'Contrast': { 'Status': {}},
            'Enlarge': { 'Status': {}},
            'ImageLocation': { 'Status': {}},
            'Input': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureInPicture': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'Power': { 'Status': {}},
            'Sharpness': { 'Status': {}},
            'Tint': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.startPolling = False        

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'OK'), self.__MatchSuccess, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername( None, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword( None, None)

    def __MatchSuccess(self, match, tag):
        self.startPolling = True

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        
        inputStatus = self.ReadStatus('Input', qualifier) # get current input status
        if inputStatus and value in self.AspectRatioStateValues[inputStatus]:
            AspectRatioCmdString = 'WIDE{0: 4}\r\n'.format(self.AspectRatioStateValues[inputStatus][value])	# sub dictionary. change aspect ratio based on status
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        
        inputStatus = self.ReadStatus('Input', qualifier) # get current input status
        if inputStatus:
            AspectRatioCmdString = 'WIDE????\r\n'
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = self.AspectRatioStateNames[inputStatus][int(res)]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, ValueError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On' : 1,
            'Off' : 0,
            }
        if value in AudioMuteStateValues:
            AudioMuteCmdString = 'MUTE{0: 4}\r\n'.format(AudioMuteStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateNames = {
            1	: 'On',
            0	: 'Off'
        }

        AudioMuteCmdString = 'MUTE????\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteStateNames[int(res)]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'AGIN0001\r\n', value, qualifier)

    def SetEnlarge(self, value, qualifier):

        EnlargeStateValues = {
            '2x2' : 1,
            '3x3' : 2,
            '4x4' : 3,
            '5x5' : 4,
            'Off' : 0,
            }
        if value in EnlargeStateValues:
            EnlargeCmdString = 'EMAG{0: 4}\r\n'.format(EnlargeStateValues[value])
            self.__SetHelper('Enlarge', EnlargeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEnlarge')

    def UpdateEnlarge(self, value, qualifier):

        EnlargeStateNames = {
            1	:	'2x2',
            2	:	'3x3',
            3	:	'4x4',
            4	:	'5x5',
            0	:	'Off',
            }

        EnlargeCmdString = 'EMAG????\r\n'
        res = self.__UpdateHelper('Enlarge', EnlargeCmdString, value, qualifier)
        if res:
            try:
                value = EnlargeStateNames[int(res)]
                self.WriteStatus('Enlarge', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetImageLocation(self, value, qualifier):

        ImageLocationStateValues = {
            '1x2' : 12,'1x3' : 13,'1x4' : 14,'1x5' : 15,
            '2x1' : 21,'2x2' : 22,'2x3' : 23,'2x4' : 24,'2x5' : 25,
            '3x1' : 31,'3x2' : 32,'3x3' : 33,'3x4' : 34,'3x5' : 35,
            '4x1' : 41,'4x2' : 42,'4x3' : 43,'4x4' : 44,'4x5' : 45,
            '5x1' : 51,'5x2' : 52,'5x3' : 53,'5x4' : 54,'5x5' : 55
            }

        if value in ImageLocationStateValues:
            ImageLocationCmdString = 'EPHV{0: 4}\r\n'.format(ImageLocationStateValues[value])
            self.__SetHelper('ImageLocation', ImageLocationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageLocation')

    def UpdateImageLocation(self, value, qualifier):

        ImageLocationStateNames = {
            12	: '1x2', 13	: '1x3',14 : '1x4',15	: '1x5',
            21	: '2x1', 22	: '2x2',23 : '2x3',24	: '2x4',25 :	'2x5',
            31	: '3x1', 32	: '3x2',33 : '3x3',34	: '3x4',35 :	'3x5',
            41	: '4x1', 42	: '4x2',43 : '4x3',44	: '4x4',45 :	'4x5',
            51	: '5x1', 52	: '5x2',53 : '5x3',54	: '5x4',55 :	'5x5'
            }

        ImageLocationCmdString = 'EPHV????\r\n'
        res = self.__UpdateHelper('ImageLocation', ImageLocationCmdString, value, qualifier)
        if res:
            try:
                value = ImageLocationStateNames[int(res)]
                self.WriteStatus('ImageLocation', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        if value in self.InputStateValues:
            InputCmdString = 'INPS{0: 4}\r\n'.format(self.InputStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'INPS????\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On'  : 0,
            'Off' : 1,
            'On2' : 2,
            }
        if value in OnScreenDisplayStateValues:
            OnScreenDisplayCmdString = 'LOSD{0: 4}\r\n'.format(OnScreenDisplayStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateNames = {
            0 : 'On',
            1 : 'Off',
            2 : 'On2',
            }
        OnScreenDisplayCmdString = 'LOSD????\r\n'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateNames[int(res)]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        PictureInPictureStateValues = {
            'PIP'	: 1,
            'PBP 1'	: 2,
            'PBP 2' : 3,
            'Off'	: 0,
            }

        if value in PictureInPictureStateValues:
            PictureInPictureCmdString = 'MWIN{0: 4}\r\n'.format(PictureInPictureStateValues[value])
            self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPicture')

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPictureStateNames = {
            1 : 'PIP',
            2 : 'PBP 1',
            3 : 'PBP 2',
            0 : 'Off'
            }
        PictureInPictureCmdString = 'MWIN????\r\n'
        res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        if res:
            try:
                value = PictureInPictureStateNames[int(res)]
                self.WriteStatus('PictureInPicture', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        if value in self.PIPInputStateValues:
            PIPInputCmdString = 'MWIP{0: 4}\r\n'.format(self.PIPInputStateValues[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = 'MWIP????\r\n'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPInputStateNames[int(res)]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        if self.PIPSizeStateValues['Min'] <= int(value) <= self.PIPSizeStateValues['Max']:
            PIPSizeCmdString = 'MPSZ{0:>4}\r\n'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'MPSZ????\r\n'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = res[0:res.index('\r')]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : 1,
            'Off' : 0,
            }

        if value in PowerStateValues:
            PowerCmdString = 'POWR{0: 4}\r\n'.format(PowerStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Input signal waiting mode',
            }

        PowerCmdString = 'POWR????\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[0:1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            VolCmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', VolCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolCmdString = 'VOLM????\r\n'
        res = self.__UpdateHelper('Volume', VolCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 60:
            ContrastCmdString = 'CONT{0: 4}\r\n'.format(value)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        res = self.__UpdateHelper('Contrast', 'CONT????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Contrast',  int(res) , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetBlackLevel(self, value, qualifier):

        if 0 <= value <= 60:
            BlackLevelCmdString = 'BLVL{0: 4}\r\n'.format(value)
            self.__SetHelper('BlackLevel', BlackLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlackLevel')

    def UpdateBlackLevel(self, value, qualifier):

        res = self.__UpdateHelper('BlackLevel', 'BLVL????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('BlackLevel',  int(res) , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetTint(self, value, qualifier):

        if 0 <= value <= 60:
            TintCmdString = 'TINT{0: 4}\r\n'.format(value)
            self.__SetHelper('Tint', TintCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTint')

    def UpdateTint(self, value, qualifier):

        res = self.__UpdateHelper('Tint', 'TINT????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Tint',  int(res) , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetColors(self, value, qualifier):

        if 0 <= value <= 60:
            ColorsCmdString = 'COLR{0: 4}\r\n'.format(value)
            self.__SetHelper('Colors', ColorsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColors')

    def UpdateColors(self, value, qualifier):

        res = self.__UpdateHelper('Colors', 'COLR????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Colors',  int(res) , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetSharpness(self, value, qualifier):

        if 0 <= value <= 24:
            SharpnessCmdString = 'SHRP{0: 4}\r\n'.format(value)
            self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):

        res = self.__UpdateHelper('Sharpness', 'SHRP????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Sharpness',  int(res) , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO', 
            'Top'                   : 'BZCT', 
            'Bottom'                : 'BZCB', 
            'Right'                 : 'BZCR', 
            'Left'                  : 'BZCL'
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        bezelValue = qualifier['Bezel']
        if bezelValue in Bezel and value in ValueStateValues:
            CmdString = '{0}   {1}\r\n'.format(  Bezel[qualifier['Bezel']]   ,   ValueStateValues[value]  )
            self.__SetHelper('BezelAdjust', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBezelAdjust')

    def UpdateBezelAdjust(self, value, qualifier):


        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO????\r\n', 
            'Top'                   : 'BZCT????\r\n', 
            'Bottom'                : 'BZCB????\r\n', 
            'Right'                 : 'BZCR????\r\n', 
            'Left'                  : 'BZCL????\r\n'
        }

        Values = {
            1 : 'On', 
            0 : 'Off'
        }

        res = self.__UpdateHelper('BezelAdjust', Bezel[qualifier['Bezel']] , value, qualifier)
        if res:
            try:
                self.WriteStatus('BezelAdjust',   Values[int(res)]    , qualifier)
            except (ValueError, KeyError):
                self.Error(['Invalid/unexpected response'])

    def SetBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV', 
            'Short' : 'BEZH'
        }

        sidesValue = qualifier['Side']
        if sidesValue in Sides and 0 <= value <= 100 :
            CmdString = '{0}{1: 4}\r\n'.format(   Sides[qualifier['Side']]   ,     value   )
            self.__SetHelper('BezelWidth', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBezelWidth')

    def UpdateBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV????\r\n', 
            'Short' : 'BEZH????\r\n'
        }

        res = self.__UpdateHelper('BezelWidth', Sides[qualifier['Side']] , value, qualifier)
        if res:
            try:
                self.WriteStatus('BezelWidth',  int(res) , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VLMP{0: 4}\r\n'.format(value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):
        res = self.__UpdateHelper('Brightness', 'VLMP????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Brightness',    int(res)    , qualifier)
            except (ValueError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                ErrorString = '{0}:Communication error or incorrect command'.format(sourceCmdName)
                self.Error([ErrorString])
                response = ''
            elif response[:2] == 'OK':
                self.startPolling = True
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            if self.startPolling:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
            else:
                self.Discard('Invalid Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.startPolling:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

           

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.startPolling = False
        
    def shrp_10_217_R(self):

        self.AspectRatioStateValues ={
            'DVI-I'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'D-SUB Component' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'D-SUB RGB' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'D-SUB Video'		 : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI 1 AV'       : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI 1 PC'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'HDMI 2 AV'   : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI 2 PC'   : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'DisplayPort'   	: {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'Toggle'    :   0
            }

        self.AspectRatioStateNames = {
           'DVI-I'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'D-SUB Component' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'D-SUB RGB' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'D-SUB Video'		 : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI 1 AV'       : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI 1 PC'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'HDMI 2 AV'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI 2 PC'   : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'DisplayPort'  	: {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            }

        self.InputStateValues = {
            'DVI-I'				: 1,
            'D-SUB RGB'			: 2,
            'D-SUB Component'	: 3,
            'D-SUB Video'		: 4,
            'HDMI 1 AV'			: 9,
            'HDMI 1 PC'			: 10,
            'HDMI 2 AV'			: 12,
            'HDMI 2 PC'			: 13,
            'DisplayPort'		: 14,
            }

        self.InputStateNames = {
            1	:	'DVI-I',
            2	:	'D-SUB RGB',
            3	:	'D-SUB Component',
            4	:	'D-SUB Video',
            9	:	'HDMI 1 AV',
            10	:	'HDMI 1 PC',
            12 	:	'HDMI 2 AV',
            13	:	'HDMI 2 PC',
            14	:	'DisplayPort',
            }

        self.PIPInputStateValues = {
            'DVI-I'				: 1,
            'D-SUB RGB'			: 2,
            'D-SUB Component'	: 3,
            'D-SUB Video'		: 4,
            'HDMI 1 AV'			: 9,
            'HDMI 1 PC'			: 10,
            'HDMI 2 AV'			: 12,
            'HDMI 2 PC'			: 13,
            'DisplayPort'		: 14,
            }

        self.PIPInputStateNames = {
            1	:	'DVI-I',
            2	:	'D-SUB RGB',
            3	:	'D-SUB Component',
            4	:	'D-SUB Video',
            9	:	'HDMI 1 AV',
            10	:	'HDMI 1 PC',
            12 	:	'HDMI 2 AV',
            13	:	'HDMI 2 PC',
            14	:	'DisplayPort',
            }

        self.PIPSizeStateValues = {
            'Min' : 1,
            'Max' : 64,
            }

    def shrp_10_217_U(self):




        self.AspectRatioStateValues ={
            'DVI-D'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Custom'	: 6,
                },
            'D-SUB' : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Custom'	: 6,
                },
            'Component' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Custom'	: 6,
                },
            'Video'		 : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Custom'	: 6,
                },
            'HDMI'       : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Custom'	: 6,
                },
            'DisplayPort'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Custom'	: 6,
                },
            'Toggle'    :   0
            }

        self.AspectRatioStateNames = {
           'DVI-D'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'D-SUB' : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'Component' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'Video'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'HDMI' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    6   :  'Custom',
                },
            'DisplayPort'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    6   :  'Custom',
                },
            }

        self.InputStateValues = {
            'DVI-D'			: 1,
            'D-SUB'			: 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI'			: 9,
            'DisplayPort'	: 14,
            }

        self.InputStateNames = {
            1	:	'DVI-D',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI',
            14	:	'DisplayPort',
            }


        self.PIPInputStateValues = {
            'DVI-D'			: 1,
            'D-SUB'			: 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI'			: 9,
            'DisplayPort'	: 14,
            }

        self.PIPInputStateNames = {
            1	:	'DVI-D',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI',
            14	:	'DisplayPort',
            }

        self.PIPSizeStateValues = {
            'Min' : 0,
            'Max' : 2,
            }

    def shrp_10_217_V(self):




        self.AspectRatioStateValues ={
            'DVI-D PC'  : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'D-SUB' : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'Component' : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'Video'		 : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'RGB'       : {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'DVI-D AV'  : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'S-Video'   : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI AV'   : {
                    'Normal'	: 4,
                    'Wide'		: 1,
                    'Dot by Dot': 5,
                    'Zoom 1'	: 2,
                    'Zoom 2'	: 3,
                },
            'HDMI PC'   	: {
                    'Normal'	: 2,
                    'Wide'		: 1,
                    'Dot by Dot': 3,
                    'Zoom 1'	: 4,
                    'Zoom 2'	: 5,
                },
            'Toggle'    :   0
            }

        self.AspectRatioStateNames = {
           'DVI-D PC'  : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'D-SUB' : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'Component' : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'Video'		 : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'RGB'       : {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            'DVI-D AV'  : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'S-Video'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI AV'   : {
                    4   :  'Normal',
                    1   :  'Wide',
                    5   :  'Dot by Dot',
                    2   :  'Zoom 1',
                    3   :  'Zoom 2',
                },
            'HDMI PC'   	: {
                    2   :  'Normal',
                    1   :  'Wide',
                    3   :  'Dot by Dot',
                    4   :  'Zoom 1',
                    5   :  'Zoom 2',
                },
            }

        self.InputStateValues = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'RGB'		    : 6,
            'DVI-D AV'		: 7,
            'S-Video'		: 8,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            }

        self.InputStateNames = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            6	:	'RGB',
            7	:	'DVI-D AV',
            8 	:	'S-Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            }

        self.PIPInputStateValues = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'RGB'		    : 6,
            'DVI-D AV'		: 7,
            'S-Video'		: 8,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            }

        self.PIPInputStateNames = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            6	:	'RGB',
            7	:	'DVI-D AV',
            8 	:	'S-Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            }

        self.PIPSizeStateValues = {
            'Min' : 1,
            'Max' : 12,
            }    ######################################################    
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
