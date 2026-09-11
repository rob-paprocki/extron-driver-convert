from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Keypad': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHorizontalPosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHorizontalSize': {'Parameters': ['Device ID'], 'Status': {}},
            'TileID': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMode': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'TileNaturalMode': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVerticalPosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVerticalSize': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2}) OK([0-9A-F]{2})x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9A-F]{2}) OK(01|00)x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm ([0-9A-F]{2}) OK(01|00)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2}) OK(20|40|60|80|90|A0|80|70|C0|D0|B0)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l ([0-9A-F]{2}) OK(01|00)x', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2}) OK(01|00)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'i ([0-9A-F]{2}) OK([0-9A-F]{2})x', re.I), self.__MatchTileID, None)
            self.AddMatchString(re.compile(b'z ([0-9A-F]{2}) OK(00|01)([0-9A-F]{2})([0-9A-F]{2})x', re.I), self.__MatchTileMode, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2}) OK(01|00)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2}) OK([0-9A-F]{1,2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|b|a|d|f|u|m|l) [0-9A-F]{2}NG(.*?)x', re.I), self.__MatchError, None)

    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return '00'
        elif 1 <= int(ID) <= 255:
            return '{0:02X}'.format(int(ID))
        else:
            print('Invalid Device ID provided')

    def SetAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'Just Scan': '09',
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1A',
            'Cinema Zoom 12': '1B',
            'Cinema Zoom 13': '1C',
            'Cinema Zoom 14': '1D',
            'Cinema Zoom 15': '1E',
            'Cinema Zoom 16': '1F'
        }

        CmdString = 'kc {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'kc {0} FF\r'.format(ID)
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
            '09': 'Just Scan',
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
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

        value = States[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Device ID': str(ID)})

    def SetAudioMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'ke {0} FF\r'.format(ID)
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
            '00': 'On',
            '01': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(2).decode()], {'Device ID': str(ID)})

    def SetAutoImage(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'ju {0} 01\r'.format(ID)
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'km {0} FF\r'.format(ID)
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('ExecutiveMode', States[match.group(2).decode()], {'Device ID': str(ID)})

    def SetInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'AV (CVBS)': '20',
            'Component': '40',
            'RGB': '60',
            'HDMI (DTV)': '90',
            'HDMI (PC)': 'A0',
            'DVI-D (DTV)': '80',
            'DVI-D (PC)': '70',
            'Display Port (DTV)': 'C0',
            'Display Port (PC)': 'D0',
            'SuperSign': 'B0'
        }

        CmdString = 'xb {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'xb {0} FF\r'.format(ID)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
           '20': 'AV (CVBS)',
           '40': 'Component',
           '60': 'RGB',
           '90': 'HDMI (DTV)',
           'A0': 'HDMI (PC)',
           '80': 'DVI-D (DTV)',
           '70': 'DVI-D (PC)',
           'C0': 'Display Port (DTV)',
           'D0': 'Display Port (PC)',
           'B0': 'SuperSign'
        }

        self.WriteStatus('Input', States[match.group(2).decode()], {'Device ID': str(ID)})

    def SetKeypad(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

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

        CmdString = 'mc {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Settings': '43',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }

        CmdString = 'mc {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'kl {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'kl {0} FF\r'.format(ID)
        self.__UpdateHelper('OnScreenDisplay', CmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('OnScreenDisplay', States[match.group(2).decode()], {'Device ID': str(ID)})

    def SetPower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'ka {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'ka {0} FF\r'.format(ID)
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
            '01': 'On',
            '00': 'Off'
        }

        value = States[match.group(2).decode()]
        self.WriteStatus('Power', value, {'Device ID': str(ID)})


    def SetTileHorizontalPosition(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if -50 <= value <= 0:
            h_pos = '{0:02X}'.format(value + 50)
            CmdString = 'de {0} {1}\r'.format(ID, h_pos)
            self.__SetHelper('TileHorizontalPosition', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileHorizontalPosition')

    def SetTileHorizontalSize(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if 0 <= value <= 50:

            h_size = '{0:02X}'.format(value)
            CmdString = 'dg {0} {1}\r'.format(ID, h_size)
            self.__SetHelper('TileHorizontalSize', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileHorizontalSize')

    def SetTileID(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if 1 <= int(value) <= 225:
            CmdString = 'di {0} {1:02X}\r'.format(ID, int(value))
            self.__SetHelper('TileID', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileID')

    def UpdateTileID(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'di {0} FF\r'.format(ID)
        self.__UpdateHelper('TileID', CmdString, value, qualifier)

    def __MatchTileID(self, match, tag):
        ID = int(match.group(1).decode(), 16)
        value = str(int(match.group(2).decode(), 16))
        self.WriteStatus('TileID', value, {'Device ID': str(ID)})

    def SetTileMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        Row = int(qualifier['Row'])
        Column = int(qualifier['Column'])

        if 2 <= Row <= 15 and 2 <= Column <= 15 and value in ['On', 'Off']:
            if value == 'On':
                CmdString = 'dd {0} {1:X}{2:X}\r'.format(ID, Row, Column)
                self.__SetHelper('TileMode', CmdString, value, qualifier)
            elif value == 'Off':
                CmdString = 'dd {0} 00\r'.format(ID)
                self.__SetHelper('TileMode', CmdString, value, qualifier)
            else:
                print('Invalid Command for SetTileMode')

    def UpdateTileMode(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'dz {0} FF\r'.format(ID)
        self.__UpdateHelper('TileMode', CmdString, value, qualifier)

    def __MatchTileMode(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }
        ID = int(match.group(1).decode(), 16)
        value = States[match.group(2).decode()]
        Row = str(int(match.group(3).decode(), 16))
        Column = str(int(match.group(4).decode(), 16))
        self.WriteStatus('TileMode', value, {'Device ID': str(ID), 'Row': Row, 'Column': Column})

    def SetTileNaturalMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'dj {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('TileNaturalMode', CmdString, value, qualifier)

    def SetTileVerticalPosition(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if 0 <= value <= 50:
            vpos = '{0:02X}'.format(value)
            CmdString = 'df {0} {1}\r'.format(ID, vpos)
            self.__SetHelper('TileVerticalPosition', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileVerticalPosition')

    def SetTileVerticalSize(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if 0 <= value <= 50:
            vsize = '{0:02X}'.format(value)
            CmdString = 'dh {0} {1}\r'.format(ID, vsize)
            self.__SetHelper('TileVerticalSize', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileVerticalSize')

    def SetVideoMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'kd {0} {1}\r'.format(ID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'kd {0} FF\r'.format(ID)
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        ID = int(match.group(1).decode(), 16)

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('VideoMute', States[match.group(2).decode()], {'Device ID': str(ID)})

    def SetVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(ID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        CmdString = 'kf {0} FF\r'.format(ID)
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        ID = int(match.group(1).decode(), 16)
        value = int(match.group(2).decode(), 16)
        self.WriteStatus('Volume', value, {'Device ID': str(ID)})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            'c' : 'Aspect Ratio/Key',
            'e' : 'Audio Mute',
            'b' : 'Input',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume',
            'm' : 'Executive Mode',
            'u' : 'Auto Image',
            'l' : 'On-Screen Display'
            }

        value = 'There was an error with {0} command for state {1}'.format(DEVICE_ERROR_CODES[match.group(1).decode()], match.group(3).decode())
        print(value)

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
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'TileHorizontalPosition': {'Status': {}},
            'TileHorizontalSize': {'Status': {}},
            'TileID': {'Status': {}},
            'TileMode': {'Parameters': ['Row', 'Column'], 'Status': {}},
            'TileNaturalMode': {'Status': {}},
            'TileVerticalPosition': {'Status': {}},
            'TileVerticalSize': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(
                re.compile(b'c [0-9A-F]{2} OK([0-9A-F]{2})x', re.I),
                self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9A-F]{2} OK(01|00)x', re.I),
                                self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9A-F]{2} OK(01|00)x', re.I),
                                self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(
                b'b [0-9A-F]{2} OK(20|40|60|80|90|A0|80|70|C0|D0|B0)x', re.I),
                                self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9A-F]{2} OK(01|00)x', re.I),
                                self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a [0-9A-F]{2} OK(01|00)x', re.I),
                                self.__MatchPower, None)
            self.AddMatchString(
                re.compile(b'i [0-9A-F]{2} OK([0-9A-F]{2})x', re.I),
                self.__MatchTileID, None)
            self.AddMatchString(re.compile(
                b'z [0-9A-F]{2} OK(00|01)([0-9A-F]{2})([0-9A-F]{2})x', re.I),
                                self.__MatchTileMode, None)
            self.AddMatchString(re.compile(b'd [0-9A-F]{2} OK(01|00)x', re.I),
                                self.__MatchVideoMute, None)
            self.AddMatchString(
                re.compile(b'f [0-9A-F]{2} OK([0-9A-F]{1,2})x', re.I),
                self.__MatchVolume, None)
            self.AddMatchString(
                re.compile(b'(c|e|b|a|d|f|u|m|l) [0-9A-F]{2}NG(.*?)x', re.I),
                self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 255:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            print(
                'DeviceID parameter should be a number between 0 and 255 or Broadcast')

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Just Scan': '09',
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1A',
            'Cinema Zoom 12': '1B',
            'Cinema Zoom 13': '1C',
            'Cinema Zoom 14': '1D',
            'Cinema Zoom 15': '1E',
            'Cinema Zoom 16': '1F'
        }

        CmdString = 'kc {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        CmdString = 'kc {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '09': 'Just Scan',
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
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

        value = States[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        CmdString = 'ke {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '00': 'On',
            '01': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetAutoImage(self, value, qualifier):

        CmdString = 'ju {0} 01\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        CmdString = 'km {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('ExecutiveMode', States[match.group(1).decode()], None)

    def SetInput(self, value, qualifier):

        States = {
            'AV (CVBS)': '20',
            'Component': '40',
            'RGB': '60',
            'HDMI (DTV)': '90',
            'HDMI (PC)': 'A0',
            'DVI-D (DTV)': '80',
            'DVI-D (PC)': '70',
            'Display Port (DTV)': 'C0',
            'Display Port (PC)': 'D0',
            'SuperSign': 'B0'
        }

        CmdString = 'xb {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        CmdString = 'xb {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '20': 'AV (CVBS)',
            '40': 'Component',
            '60': 'RGB',
            '90': 'HDMI (DTV)',
            'A0': 'HDMI (PC)',
            '80': 'DVI-D (DTV)',
            '70': 'DVI-D (PC)',
            'C0': 'Display Port (DTV)',
            'D0': 'Display Port (PC)',
            'B0': 'SuperSign'
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

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

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Settings': '43',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'kl {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        CmdString = 'kl {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('OnScreenDisplay', CmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('OnScreenDisplay', States[match.group(1).decode()],
                         None)

    def SetPower(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'ka {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = 'ka {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetTileHorizontalPosition(self, value, qualifier):

        if -50 <= value <= 0:
            h_pos = '{0:02X}'.format(value + 50)
            CmdString = 'de {0} {1}\r'.format(self._DeviceID, h_pos)
            self.__SetHelper('TileHorizontalPosition', CmdString, value,
                             qualifier)
        else:
            print('Invalid Command for SetTileHorizontalPosition')

    def SetTileHorizontalSize(self, value, qualifier):

        if 0 <= value <= 50:
            h_size = '{0:02X}'.format(value)
            CmdString = 'dg {0} {1}\r'.format(self._DeviceID, h_size)
            self.__SetHelper('TileHorizontalSize', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileHorizontalSize')

    def SetTileID(self, value, qualifier):

        if 1 <= int(value) <= 225:
            CmdString = 'di {0} {1:02X}\r'.format(self._DeviceID, int(value))
            self.__SetHelper('TileID', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileID')

    def UpdateTileID(self, value, qualifier):
        CmdString = 'di {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('TileID', CmdString, value, qualifier)

    def __MatchTileID(self, match, tag):
        value = str(int(match.group(1).decode(), 16))
        self.WriteStatus('TileID', value, None)

    def SetTileMode(self, value, qualifier):

        Row = int(qualifier['Row'])
        Column = int(qualifier['Column'])

        if 2 <= Row <= 15 and 2 <= Column <= 15 and value in ['On', 'Off']:
            if value == 'On':
                CmdString = 'dd {0} {1:X}{2:X}\r'.format(self._DeviceID, Row, Column)
                self.__SetHelper('TileMode', CmdString, value, qualifier)
            elif value == 'Off':
                CmdString = 'dd {0} 00\r'.format(self._DeviceID)
                self.__SetHelper('TileMode', CmdString, value, qualifier)
            else:
                print('Invalid Command for SetTileMode')

    def UpdateTileMode(self, value, qualifier):
        CmdString = 'dz {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('TileMode', CmdString, value, qualifier)

    def __MatchTileMode(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        Row = str(int(match.group(2).decode(), 16))
        Column = str(int(match.group(3).decode(), 16))
        value = States[match.group(1).decode()]
        self.WriteStatus('TileMode', value, {'Row': Row, 'Column': Column})

    def SetTileNaturalMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'dj {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('TileNaturalMode', CmdString, value, qualifier)

    def SetTileVerticalPosition(self, value, qualifier):

        if 0 <= value <= 50:
            vpos = '{0:02X}'.format(value)
            CmdString = 'df {0} {1}\r'.format(self._DeviceID, vpos)
            self.__SetHelper('TileVerticalPosition', CmdString, value,
                             qualifier)
        else:
            print('Invalid Command for SetTileVerticalPosition')

    def SetTileVerticalSize(self, value, qualifier):

        if 0 <= value <= 50:
            vsize = '{0:02X}'.format(value)
            CmdString = 'dh {0} {1}\r'.format(self._DeviceID, vsize)
            self.__SetHelper('TileVerticalSize', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetTileVerticalSize')

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'kd {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        CmdString = 'kd {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '01': 'On',
            '00': 'Off'
        }

        self.WriteStatus('VideoMute', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        CmdString = 'kf {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            'c': 'Aspect Ratio/Key',
            'e': 'Audio Mute',
            'b': 'Input',
            'a': 'Power',
            'd': 'Video Mute',
            'f': 'Volume',
            'm': 'Executive Mode',
            'u': 'Auto Image',
            'l': 'On-Screen Display'
        }

        value = 'There was an error with {0} command for state {1}'.format(
            DEVICE_ERROR_CODES[match.group(1).decode()],
            match.group(3).decode())
        print(value)

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback,
                                                'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result,
                                                                self._compile_list[
                                                                    regexString][
                                                                    'para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(
                        result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()


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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=9761, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()