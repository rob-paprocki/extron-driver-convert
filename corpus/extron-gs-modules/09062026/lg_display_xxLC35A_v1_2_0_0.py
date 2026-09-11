from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Keypad': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'NaturalMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'TileID': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMode': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'TilePosition': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'TileSize': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2}) OK([01][0-9A-F])x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9A-F]{2}) OK(0[01])x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2}) OK([6789A]0)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2}) OK(0[01])x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2}) OK(0[01])x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2}) OK([0-9A-F]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([ceubajidghf]) ([0-9A-F]{2}) NG.*?x', re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(?:OK|NG).*?x')

    def GetDeviceID(self, ID):
        try:
            if ID == 'Broadcast':
                return '00'
            elif 1 <= int(ID) <= 255:
                return '{0:02X}'.format(int(ID))
        except ValueError:
            pass

        self.Discard(['Invalid Command'])
        return ''

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':              '01',
            '16:9':             '02',
            'Zoom':             '04',
            'Set By Program':   '06',
            'Just Scan':        '09',
            'Cinema Zoom 1':    '10',
            'Cinema Zoom 2':    '11',
            'Cinema Zoom 3':    '12',
            'Cinema Zoom 4':    '13',
            'Cinema Zoom 5':    '14',
            'Cinema Zoom 6':    '15',
            'Cinema Zoom 7':    '16',
            'Cinema Zoom 8':    '17',
            'Cinema Zoom 9':    '18',
            'Cinema Zoom 10':   '19',
            'Cinema Zoom 11':   '1A',
            'Cinema Zoom 12':   '1B',
            'Cinema Zoom 13':   '1C',
            'Cinema Zoom 14':   '1D',
            'Cinema Zoom 15':   '1E',
            'Cinema Zoom 16':   '1F'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ID:
            AspectRatioCmdString = 'kc {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            AspectRatioCmdString = 'kc {0} FF\r'.format(ID)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Set By Program',
            '09': 'Just Scan',
            '10': 'Cinema Zoom 1',
            '11': 'Cinema Zoom 2',
            '12': 'Cinema Zoom 3',
            '13': 'Cinema Zoom 4',
            '14': 'Cinema Zoom 5',
            '15': 'Cinema Zoom 6',
            '16': 'Cinema Zoom 7',
            '17': 'Cinema Zoom 8',
            '18': 'Cinema Zoom 9',
            '19': 'Cinema Zoom 10',
            '1A': 'Cinema Zoom 11',
            '1B': 'Cinema Zoom 12',
            '1C': 'Cinema Zoom 13',
            '1D': 'Cinema Zoom 14',
            '1E': 'Cinema Zoom 15',
            '1F': 'Cinema Zoom 16'
        }

        ID = int(match.group(1).decode(), 16)

        if 1 <= ID <= 255:
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('AspectRatio', value, {'Device ID': str(ID)})
        else:
            self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '00',
            'Off':  '01'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            AudioMuteCmdString = 'ke {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            AudioMuteCmdString = 'ke {0} FF\r'.format(ID)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '00': 'On',
            '01': 'Off'
        }

        ID = int(match.group(1).decode(), 16)

        if 1 <= ID <= 255:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, {'Device ID': str(ID)})
        else:
            self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            AutoImageCmdString = 'ju {0} 01\r'.format(ID)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB':          '60',
            'HDMI (DTV)':   '90',
            'HDMI (PC)':    'A0',
            'DVI-D (PC)':   '70',
            'DVI-D (DTV)':  '80'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            InputCmdString = 'xb {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            InputCmdString = 'xb {0} FF\r'.format(ID)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = { 
            '60': 'RGB',
            'A0': 'HDMI (PC)',
            '90': 'HDMI (DTV)',
            '70': 'DVI-D (PC)',
            '80': 'DVI-D (DTV)'
        }

        ID = int(match.group(1).decode(), 16)

        if 1 <= ID <= 255:
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('Input', value, {'Device ID': str(ID)})
        else:
            self.Error(['Input: Invalid/unexpected response'])

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

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            KeypadCmdString = 'mc {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateMasterPower(self, value, qualifier):

        MasterPowerCmdString = 'ka {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('MasterPower', MasterPowerCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       '40',
            'Down':     '41',
            'Left':     '07',
            'Right':    '06',
            'Settings': '43',
            'OK':       '44',
            'Back':     '28',
            'Exit':     '5B'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNaturalMode(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            NaturalModeCmdString = 'dj {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('NaturalMode', NaturalModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            PowerCmdString = 'ka {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID and ID != self.DeviceID:
            PowerCmdString = 'ka {0} FF\r'.format(ID)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }
        
        ID = int(match.group(1).decode(), 16)

        if 1 <= ID <= 255:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, {'Device ID': str(ID)})
        else:
            self.Error(['Power: Invalid/unexpected response'])

    def SetTileID(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID and 1 <= int(value) <= 225:
            TileIDCmdString = 'di {0} {1:02X}\r'.format(ID, int(value))
            self.__SetHelper('TileID', TileIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileID')

    def SetTileMode(self, value, qualifier):

        Row = int(qualifier['Row'])
        Col = int(qualifier['Column'])
        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID and 0 <= Row <= 15 and 0 <= Col <= 15:
            TileModeCmdString = 'dd {0} {1:01X}{2:01X}\r'.format(ID, Row, Col)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        Row = int(qualifier['Row'])
        Col = int(qualifier['Column'])
        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID and 0 <= Row <= 50 and 0 <= Col <= 50:
            RowCmdString = 'df {0} {1:02X}\r'.format(ID, Row)
            ColCmdString = 'de {0} {1:02X}\r'.format(ID, Col)

            self.__SetHelper('TilePosition', RowCmdString + ColCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetTileSize(self, value, qualifier):

        Row = int(qualifier['Row'])
        Col = int(qualifier['Column'])
        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID and 0 <= Row <= 50 and 0 <= Col <= 50:
            RowCmdString = 'dh {0} {1:02X}\r'.format(ID, Row)
            ColCmdString = 'dg {0} {1:02X}\r'.format(ID, Col)

            self.__SetHelper('TileSize', RowCmdString + ColCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileSize')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }
        
        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            VideoMuteCmdString = 'kd {0} {1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            VideoMuteCmdString = 'kd {0} FF\r'.format(ID)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        ID = int(match.group(1).decode(), 16)

        if 1 <= ID <= 255:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('VideoMute', value, {'Device ID': str(ID)})
        else:
            self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID and 0 <= value <= 100:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(ID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if ID:
            VolumeCmdString = 'kf {0} FF\r'.format(ID)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        ID = int(match.group(1).decode(), 16)

        if 1 <= ID <= 255:
            value = int(match.group(2).decode(), 16)
            self.WriteStatus('Volume', value, {'Device ID': str(ID)})
        else:
            self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if 'NG' in response:
            self.Error(['{0}: An error occurred.'.format(sourceCmdName)])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
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

        error_map = {
            'c': 'Aspect Ratio/Keypad/Menu Navigation',
            'e': 'Audio Mute/Tile Position',
            'u': 'Auto Image',
            'b': 'Input',
            'a': 'Power',
            'j': 'Natural Mode',
            'i': 'Tile ID',
            'd': 'Tile Mode/Video Mute',
            'g': 'Tile Size',
            'h': 'Tile Size',
            'f': 'Tile Position/Volume'
        }
        value = match.group(1).decode().lower()
        self.Error(['{0} at display {1:d}: An error occurred.'.format(error_map.get(value, 'Unknown Command'),
                                                                      int(match.group(2).decode(), 16))])

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
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class DeviceEthernetClass:

    def __init__(self):

        self.Debug = False
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'NaturalMode': {'Status': {}},
            'Power Off':  {'Status': {}},
            'TileID': {'Status': {}},
            'TileMode': {'Status': {}},
            'TilePosition': {'Status': {}},
            'TileSize': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':              '01',
            '16:9':             '02',
            'Zoom':             '04',
            'Set By Program':   '06',
            'Just Scan':        '09',
            'Cinema Zoom 1':    '10',
            'Cinema Zoom 2':    '11',
            'Cinema Zoom 3':    '12',
            'Cinema Zoom 4':    '13',
            'Cinema Zoom 5':    '14',
            'Cinema Zoom 6':    '15',
            'Cinema Zoom 7':    '16',
            'Cinema Zoom 8':    '17',
            'Cinema Zoom 9':    '18',
            'Cinema Zoom 10':   '19',
            'Cinema Zoom 11':   '1A',
            'Cinema Zoom 12':   '1B',
            'Cinema Zoom 13':   '1C',
            'Cinema Zoom 14':   '1D',
            'Cinema Zoom 15':   '1E',
            'Cinema Zoom 16':   '1F'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '00',
            'Off':  '01'
        }

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ju {0} 01\r'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB':          '60',
            'HDMI (DTV)':   '90',
            'HDMI (PC)':    'A0',
            'DVI-D (PC)':   '70',
            'DVI-D (DTV)':  '80'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
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

        KeypadCmdString = 'mc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':       '40',
            'Down':     '41',
            'Left':     '07',
            'Right':    '06',
            'Settings': '43',
            'OK':       '44',
            'Back':     '28',
            'Exit':     '5B'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNaturalMode(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        NaturalModeCmdString = 'dj {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('NaturalMode', NaturalModeCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'ka {0} 00\r'.format(self.DeviceID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetTileID(self, value, qualifier):

        if 1 <= int(value) <= 225:
            TileIDCmdString = 'di {0} {1:02X}\r'.format(self.DeviceID, int(value))
            self.__SetHelper('TileID', TileIDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileID')

    def SetTileMode(self, value, qualifier):

        Row = int(qualifier['Row'])
        Col = int(qualifier['Column'])

        if 0 <= Row <= 15 and 0 <= Col <= 15:
            TileModeCmdString = 'dd {0} {1:01X}{2:01X}\r'.format(self.DeviceID, Row, Col)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        Row = int(qualifier['Row'])
        Col = int(qualifier['Column'])

        if 0 <= Row <= 50 and 0 <= Col <= 50:
            RowCmdString = 'df {0} {1:02X}\r'.format(self.DeviceID, Row)
            ColCmdString = 'de {0} {1:02X}\r'.format(self.DeviceID, Col)

            self.__SetHelper('TilePosition', RowCmdString + ColCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetTileSize(self, value, qualifier):

        Row = int(qualifier['Row'])
        Col = int(qualifier['Column'])

        if 0 <= Row <= 50 and 0 <= Col <= 50:
            RowCmdString = 'dh {0} {1:02X}\r'.format(self.DeviceID, Row)
            ColCmdString = 'dg {0} {1:02X}\r'.format(self.DeviceID, Col)

            self.__SetHelper('TileSize', RowCmdString + ColCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileSize')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self.DeviceID, value)
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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


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