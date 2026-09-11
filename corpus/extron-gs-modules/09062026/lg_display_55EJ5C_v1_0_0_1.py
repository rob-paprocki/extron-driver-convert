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
            'AspectRatio': {'Parameters': ['Display ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Display ID'], 'Status': {}},
            'Input': {'Parameters': ['Display ID'], 'Status': {}},
            'Keypad': {'Parameters': ['Display ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Display ID'], 'Status': {}},
            'PictureMode': {'Parameters': ['Display ID'], 'Status': {}},
            'Power': {'Parameters': ['Display ID'], 'Status': {}},
            'TileMode': {'Parameters': ['Display ID', 'Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters': ['Display ID', 'Tile ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Display ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9a-f]{2,3}) OK([0-9a-f]{2})x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'b ([0-9a-f]{2,3}) OK([0-9a-f]{2})x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x ([0-9a-f]{2,3}) OK([0-9]{2})x', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'a ([0-9a-f]{2,3}) OK0(1|0)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9a-f]{2,3}) OK0(1|0)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'(c|u|b|x|a|d) ([0-9a-f]{2,3}) NG(.*?)x', re.I), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Set by Program': '06',
            'Just Scan': '09',
            'Vertical Zoom': '30',
            'All Directional Zoom': '31'
        }

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetAspectRatio')
        if displayID:
            AspectRatioCmdString = 'kc {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')
        if displayID:
            AspectRatioCmdString = 'kc {0} FF\r'.format(displayID)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Set by Program',
            '09': 'Just Scan',
            '30': 'Vertical Zoom',
            '31': 'All Directional Zoom'
        }

        displayID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode().upper()]
        self.WriteStatus('AspectRatio', value, {'Display ID': str(displayID)})

    def SetAutoImage(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetAutoImage')
        if displayID:
            AutoImageCmdString = 'ju {0} 01\r'.format(displayID)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI (DTV)': '90',
            'HDMI (PC)': 'A0',
            'OPS (DTV)': '98',
            'OPS (PC)': 'A8',
            'DisplayPort (DTV)': 'C0',
            'DisplayPort (PC)': 'D0'
        }

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetInput')
        if displayID:
            InputCmdString = 'xb {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for UpdateInput')
        if displayID:
            InputCmdString = 'xb {0} FF\r'.format(displayID)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '90': 'HDMI (DTV)',
            'A0': 'HDMI (PC)',
            '98': 'OPS (DTV)',
            'A8': 'OPS (PC)',
            'C0': 'DisplayPort (DTV)',
            'D0': 'DisplayPort (PC)'
        }

        displayID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode().upper()]
        self.WriteStatus('Input', value, {'Display ID': str(displayID)})

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
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetKeypad')
        if displayID:
            KeypadCmdString = 'mc {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '43',
            'Up': '40',
            'Down': '41',
            'Right': '06',
            'Left': '07',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetMenuNavigation')
        if displayID:
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': '00',
            'Standard': '01',
            'Cinema': '02',
            'Sport': '03',
            'Game': '04',
            'Expert 1': '05',
            'Expert 2': '06',
            'APS': '08',
            'Calibration': '11'
        }

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetPictureMode')
        if displayID:
            PictureModeCmdString = 'dx {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for UpdatePictureMode')
        if displayID:
            PictureModeCmdString = 'dx {0} FF\r'.format(displayID)
            self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePictureMode')

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00': 'Vivid',
            '01': 'Standard',
            '02': 'Cinema',
            '03': 'Sport',
            '04': 'Game',
            '05': 'Expert 1',
            '06': 'Expert 2',
            '08': 'APS',
            '11': 'Calibration'
        }

        displayID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PictureMode', value, {'Display ID': str(displayID)})

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }
        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetPower')
        if displayID:
            PowerCmdString = 'ka {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for UpdatePower')
        if displayID:
            PowerCmdString = 'ka {0} FF\r'.format(displayID)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        displayID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        if 1 <= displayID <= 1000:
            self.WriteStatus('Power', value, {'Display ID': str(displayID)})
        else:
            self.__MatchError(['Invalid Response'])

    def SetTileMode(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetTileMode')

        Column = int(qualifier['Column'])
        Row = int(qualifier['Row'])

        if displayID and 1 <= Column <= 15 and 1 <= Row <= 15:
            Value = '{0:X}{1:X}'.format(Column, Row)
            TileModeCmdString = 'dd {0} {1}\r'.format(displayID, Value)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetTilePosition')

        TileID = int(qualifier['Tile ID'])

        if displayID and 1 <= TileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(displayID, TileID)
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
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for SetVideoMute')
        if displayID:
            VideoMuteCmdString = 'kd {0} {1}\r'.format(displayID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ID = qualifier['Display ID']
        if ID == 'Broadcast':
            displayID = '00'
        elif 1 <= int(ID) <= 1000:
            displayID = '{0:02X}'.format(int(ID))
        else:
            self.Discard('Invalid Command for UpdateVideoMute')
        if displayID:
            VideoMuteCmdString = 'kd {0} FF\r'.format(displayID)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        displayID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, {'Display ID': str(displayID)})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Display ID'] == 'Broadcast':
            self.Discard('Inappropriate Command for ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        CommandStates = {
            'c' : 'Aspect Ratio',
            'u' : 'Auto Image',
            'b' : 'Input',
            'x' : 'Picture Mode',
            'a' : 'Power',
            'd' : 'Video Mute',
        }

        command = CommandStates[match.group(1).decode()]
        device_id = int(match.group(2).decode().upper(),16)
        data = match.group(3).decode()
        value = '{0} Error occurred, Display ID:{1}, State:{2}'.format(command, device_id, data)
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
        self._DisplayID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PowerOff': {'Status': {}},
            'TileMode': {'Parameters': ['Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters': ['Tile ID'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2,3} OK([0-9a-f]{2})x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2,3} OK([0-9a-f]{2})x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x [0-9a-f]{2,3} OK([0-9]{2})x', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2,3} OK0(1|0)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'(c|u|b|x|d) ([0-9a-f]{2,3}) NG(.*?)x', re.I), self.__MatchError, None)

    @property
    def DisplayID(self):
        return self._DisplayID

    @DisplayID.setter
    def DisplayID(self, value):
        if value == 'Broadcast':
            self._DisplayID = '00'
        elif 1 <= int(value) <= 1000:
            self._DisplayID = '{0:02X}'.format(int(value))
        else:
            print('Driver level parameter DisplayID set to an invalid value')


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Set by Program': '06',
            'Just Scan': '09',
            'Vertical Zoom': '30',
            'All Directional Zoom': '31'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self._DisplayID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {0} FF\r'.format(self._DisplayID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Set by Program',
            '09': 'Just Scan',
            '30': 'Vertical Zoom',
            '31': 'All Directional Zoom'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ju {0} 01\r'.format(self._DisplayID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI (DTV)': '90',
            'HDMI (PC)': 'A0',
            'OPS (DTV)': '98',
            'OPS (PC)': 'A8',
            'DisplayPort (DTV)': 'C0',
            'DisplayPort (PC)': 'D0'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self._DisplayID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {0} FF\r'.format(self._DisplayID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '90': 'HDMI (DTV)',
            'A0': 'HDMI (PC)',
            '98': 'OPS (DTV)',
            'A8': 'OPS (PC)',
            'C0': 'DisplayPort (DTV)',
            'D0': 'DisplayPort (PC)'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Input', value, None)

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

        KeypadCmdString = 'mc {0} {1}\r'.format(self._DisplayID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '43',
            'Up': '40',
            'Down': '41',
            'Right': '06',
            'Left': '07',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DisplayID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': '00',
            'Standard': '01',
            'Cinema': '02',
            'Sport': '03',
            'Game': '04',
            'Expert 1': '05',
            'Expert 2': '06',
            'APS': '08',
            'Calibration': '11'
        }

        PictureModeCmdString = 'dx {0} {1}\r'.format(self._DisplayID, ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'dx {0} FF\r'.format(self._DisplayID)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00': 'Vivid',
            '01': 'Standard',
            '02': 'Cinema',
            '03': 'Sport',
            '04': 'Game',
            '05': 'Expert 1',
            '06': 'Expert 2',
            '08': 'APS',
            '11': 'Calibration'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'ka {0} 00\r'.format(self._DisplayID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetTileMode(self, value, qualifier):

        Column = int(qualifier['Column'])
        Row = int(qualifier['Row'])

        if 1 <= Column <= 15 and 1 <= Row <= 15:
            Value = '{0:X}{1:X}'.format(Column, Row)
            TileModeCmdString = 'dd {0} {1}\r'.format(self._DisplayID, Value)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        TileID = int(qualifier['Tile ID'])
        if 1 <= TileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(self._DisplayID, TileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self._DisplayID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0} FF\r'.format(self._DisplayID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DisplayID == '00':
            self.Discard('Inappropriate Command '+ command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        CommandStates = {
            'c': 'Aspect Ratio',
            'u': 'Auto Image',
            'b': 'Input',
            'x': 'Picture Mode',
            'd': 'Video Mute',
        }

        command = CommandStates[match.group(1).decode()]
        device_id = int(match.group(2).decode().upper(), 16)
        data = match.group(3).decode()
        value = '{0} Error occurred, Device ID:{1}, State:{2}'.format(command, device_id, data)
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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