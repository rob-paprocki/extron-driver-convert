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
            self.AddMatchString(re.compile(b'm ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2,3}) OK(60|A0|90|70|80|D0|C0|A8|98)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x ([0-9A-F]{2,3}) OK([0-9]{2})x', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2,3}) OK0(1|0)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2,3}) OK([0-9a-f]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(u|i|j|c|e|m|b|a|d|f|x) ([0-9A-F]{2,3}) NG(.*?)x', re.I), self.__MatchError, None)
            self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')

    def deviceCheck(self, value):
        if value == 'Broadcast':
            ID = '00'
        elif 1 <= int(value) <= 1000:
            ID = '{0:02X}'.format(int(value))
        else:
            ID = None
        return ID

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Full Wide': '02',
            'Original': '06',
        }
        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__SetHelper('AspectRatio', 'kc {0} {1}\r'.format(DisplayID, States[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for AspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('AspectRatio', 'kc {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for AspectRatio')

    def __MatchAspectRatio(self, match, tag):

        States = {
            '02': 'Full Wide',
            '06': 'Original',
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('AspectRatio', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for AspectRatio')

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'ke {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('AudioMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for AudioMute')

    def UpdateAudioMute(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('AudioMute', 'ke {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for AudioMute')

    def __MatchAudioMute(self, match, tag):

        States = {
            '0': 'On',
            '1': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('AudioMute', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for AudioMute')

    def SetAutoImage(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for AutoImage')

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'km {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for ExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('ExecutiveMode', 'km {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for ExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('ExecutiveMode', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for ExecutiveMode')

    def SetInput(self, value, qualifier):

        States = {
            'RGB': '60',
            'HDMI 1 (PC)': 'A0',
            'HDMI 1 (DTV)': '91',
            'HDMI 2 (PC)': 'A1',
            'HDMI 2 (DTV)': '90',
            'DVI-D (PC)': '70',
            'DVI-D (DTV)': '80',
            'DISPLAYPORT (PC)': 'D0',
            'DISPLAYPORT (DTV)': 'C0',
            'OPS (PC)': 'A8',
            'OPS (DTV)': '98'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'xb {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('Input', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Input')

    def UpdateInput(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('Input', 'xb {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for Input')

    def __MatchInput(self, match, tag):

        States = {
            '60': 'RGB',
            'A0': 'HDMI 1 (PC)',
            '90': 'HDMI 1 (DTV)',
            'A1': 'HDMI 2 (PC)',
            '91': 'HDMI 2 (DTV)',
            '70': 'DVI-D (PC)',
            '80': 'DVI-D (DTV)',
            'D0': 'DISPLAYPORT (PC)',
            'C0': 'DISPLAYPORT (DTV)',
            'A8': 'OPS (PC)',
            '98': 'OPS (DTV)'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('Input', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for Input')

    def SetKeypad(self, value, qualifier):

        States = {
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

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'mc {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('Keypad', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Keypad')

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'mc {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('MenuNavigation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for MenuNavigation')

    def SetPictureMode(self, value, qualifier):

        States = {
            'Mall/QSR': '00',
            'General': '01',
            'Gov/Corp': '02',
            'Transportation': '03',
            'Education': '04',
            'Expert 1': '05',
            'Expert 2': '06',
            'APS': '08',
            'Photo': '09',
            'Calibration': '11'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'dx {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('PictureMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for PictureMode')

    def UpdatePictureMode(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('PictureMode', 'dx {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for PictureMode')

    def __MatchPictureMode(self, match, tag):

        States = {
            '00': 'Mall/QSR',
            '01': 'General',
            '02': 'Gov/Corp',
            '03': 'Transportation',
            '04': 'Education',
            '05': 'Expert 1',
            '06': 'Expert 2',
            '08': 'APS',
            '09': 'Photo',
            '11': 'Calibration'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('PictureMode', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for PictureMode')

    def SetPower(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'ka {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Power')

    def UpdatePower(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('Power', 'ka {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for Power')

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('Power', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for Power')

    def SetTileMode(self, value, qualifier):

        Col = int(qualifier['Column']) if 0 <= int(qualifier['Column']) <= 15 else ''
        Row = int(qualifier['Row']) if 0 <= int(qualifier['Row']) <= 15 else ''

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if Col and Row and DisplayID:
            Value = '{0:X}{1:X}'.format(Col, Row)
            CmdString = 'dd {0} {1}\r'.format(DisplayID, Value)
            self.__SetHelper('TileMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        TileID = int(qualifier['Tile ID'])

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if 1 <= TileID <= 225 and DisplayID:
            CmdString = 'di {0} {1:02X}\r'.format(DisplayID, TileID)
            self.__SetHelper('TilePosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            CmdString = 'kd {0} {1}\r'.format(DisplayID, States[value])
            self.__SetHelper('VideoMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for VideoMute')

    def UpdateVideoMute(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('VideoMute', 'kd {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for VideoMute')

    def __MatchVideoMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('VideoMute', States[match.group(2).decode()], {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for VideoMute')

    def SetVolume(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if 0 <= value <= 100 and DisplayID:
            CmdString = 'kf {0} {1:02X}\r'.format(DisplayID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DisplayID = self.deviceCheck(qualifier['Display ID'])
        if DisplayID:
            self.__UpdateHelper('Volume', 'kf {0} FF\r'.format(DisplayID), value, qualifier)
        else:
            self.Discard('Invalid Command for Volume')

    def __MatchVolume(self, match, tag):

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 1000:
            self.WriteStatus('Volume', int(match.group(2).decode(), 16), {'Display ID': str(ID)})
        else:
            self.Discard('Invalid Command for Volume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'OK' in response:
            return response
        elif 'NG' in response:
            self.Error(['Error occured in {}'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{} : Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

        State = {
            'u' : 'Auto Image',
            'i' : 'Tile Position',
            'c' : 'Aspect Ratio, Menu Navigation or Keypad',
            'e' : 'Audio Mute',
            'm' : 'Executive Mode',
            'b' : 'Input',
            'a' : 'Power',
            'd' : 'Video Mute, Tile Mode',
            'f' : 'Volume',
            'x' : 'Picture Mode'
        }
        
        temp1 = State[match.group(1).decode().lower()]
        temp2 = match.group(2).decode().upper()
        temp3 = match.group(3).decode()
        value = '{0} Error, DisplayID {1}: {2}'.format(temp1,temp2,temp3)
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

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}

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
        self.Models = {}

        self._DisplayID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
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

        States = {
            'Full Wide': '02',
            'Original': '06',
        }

        CmdString = 'kc {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        CmdString = 'ju {0} 01\r'.format(self._DisplayID)
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'RGB': '60',
            'HDMI 1 (PC)': 'A0',
            'HDMI 1 (DTV)': '91',
            'HDMI 2 (PC)': 'A1',
            'HDMI 2 (DTV)': '90',
            'DVI-D (PC)': '70',
            'DVI-D (DTV)': '80',
            'DISPLAYPORT (PC)': 'D0',
            'DISPLAYPORT (DTV)': 'C0',
            'OPS (PC)': 'A8',
            'OPS (DTV)': '98'
        }

        CmdString = 'xb {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        States = {
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

        CmdString = 'mc {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B',
            'Menu': '43'
        }

        CmdString = 'mc {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Mall/QSR': '00',
            'General': '01',
            'Gov/Corp': '02',
            'Transportation': '03',
            'Education': '04',
            'Expert 1': '05',
            'Expert 2': '06',
            'APS': '08',
            'Photo': '09',
            'Calibration': '11'
        }

        CmdString = 'dx {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        self.__SetHelper('PowerOff', 'ka {0} 00\r'.format(self._DisplayID), value, qualifier)

    def SetTileMode(self, value, qualifier):

        Col = int(qualifier['Column'])
        Row = int(qualifier['Row'])

        if 0 <= Col <= 15 and 0 <= Row <= 15:
            Value = '{0:X}{1:X}'.format(Col, Row)
            CmdString = 'dd {0} {1}\r'.format(self._DisplayID, Value)
            self.__SetHelper('TileMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        TileID = int(qualifier['Tile ID'])

        if 1 <= TileID <= 225:
            CmdString = 'di {0} {1:02X}\r'.format(self._DisplayID, TileID)
            self.__SetHelper('TilePosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'kd {0} {1}\r'.format(self._DisplayID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(self._DisplayID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
