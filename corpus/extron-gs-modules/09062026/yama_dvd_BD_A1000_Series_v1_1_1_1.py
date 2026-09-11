from extronlib.interface import SerialInterface, EthernetClientInterface
import urllib.error
import urllib.request
import re
import base64

class DeviceSerialClass:

    def __init__(self):
        
        self.Debug = False

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Control': {'Status': {}},
            'Function': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RepeatMode': {'Status': {}},
            'Subtitles': {'Status': {}},
            'Zoom': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02@040([\x00-\xFF][\x00-\xFF])\x03'), self.__MatchPower, None)

    def SetControl(self, value, qualifier):

        ValueStateValues = {
            'Play'          : b'\x0207C820\x03',
            'Stop'          : b'\x0207C850\x03',
            'Pause'         : b'\x0207C830\x03',
            'Fast Forward'  : b'\x0207C870\x03',
            'Fast Reverse'  : b'\x0207C860\x03',
            'Skip +'        : b'\x0207CBA0\x03',
            'Skip -'        : b'\x0207CB90\x03',
            'Slow Forward'  : b'\x0207C8F0\x03',
            'Slow Reverse'  : b'\x0207C8E0\x03',
            'Open/Close'    : b'\x0207C810\x03',
            'Bluetooth'     : b'\x0207CBC0\x03',
            'Page +'        : b'\x0207CDF0\x03',
            'Page -'        : b'\x0207CDE0\x03',
            'Netflix'       : b'\x0207CFA0\x03',
            'YouTube'       : b'\x0207CFB0\x03',
            'Vudu'          : b'\x0207CFC0\x03'
        }

        if value in ValueStateValues:
            ControlCmdString = ValueStateValues[value]
            self.__SetHelper('Control', ControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetControl')
            
    def UpdateControl(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetFunction(self, value, qualifier):

        ValueStateValues = {
            'Clear'     : b'\x0207C9F0\x03',
            'Program'   : b'\x0207CA00\x03',
            'Setup'     : b'\x0207CAC0\x03'
        }
        if value in ValueStateValues:
            FunctionCmdString = ValueStateValues[value]
            self.__SetHelper('Function', FunctionCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFunction')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\x0207C940\x03',
            '2' : b'\x0207C950\x03',
            '3' : b'\x0207C960\x03',
            '4' : b'\x0207C970\x03',
            '5' : b'\x0207C980\x03',
            '6' : b'\x0207C990\x03',
            '7' : b'\x0207C9A0\x03',
            '8' : b'\x0207C9B0\x03',
            '9' : b'\x0207C9C0\x03',
            '0' : b'\x0207C930\x03'
        }

        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\x0207CB40\x03',
            'Down'      : b'\x0207CB30\x03',
            'Left'      : b'\x0207CB50\x03',
            'Right'     : b'\x0207CB60\x03',
            'Menu'      : b'\x0207CCF0\x03',
            'Enter'     : b'\x0207CB80\x03',
            'Return'    : b'\x0207CB70\x03',
            'Top Menu'  : b'\x0207CB10\x03',
            'Home'      : b'\x0207CEF0\x03'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x0207CF60\x03',
            'Off'   : b'\x0207CF70\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x02410000\x03'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'00'   : 'On',
            b'01'   : 'Off',
            b'10'   : 'Play',
            b'0B'   : 'Stop',
            b'11'   : 'Pause',
            b'40'   : 'Fast Forward',
            b'50'   : 'Fast Reverse',
            b'12'   : 'Slow Forward',
            b'13'   : 'Slow Reverse',
            b'02'   : 'Tray Open',
            b'03'   : 'Tray Close',
            b'04'   : 'Reading',
            b'09'   : 'No Disc',
            b'0C'   : 'Setting',
            b'0E'   : 'Home Menu',
            b'FF'   : 'Undefined Value',
            b'0D'   : 'Stop(Resume)',
        }

        value = ValueStateValues[match.group(1)]

        if value == 'On' or value == 'Off':
            if value == 'Off':
                self.WriteStatus('Control', 'System Off', None)
            self.WriteStatus('Power', value, None)
        else:
            self.WriteStatus('Control', value, None)

    def SetRepeatMode(self, value, qualifier):

        ValueStateValues = {
            'Repeat'    : b'\x0207CA30\x03',
            'AB'        : b'\x0207CA40\x03'
        }

        if value in ValueStateValues:
            RepeatModeCmdString = ValueStateValues[value]

            self.__SetHelper('RepeatMode', RepeatModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRepeatMode')

    def SetSubtitles(self, value, qualifier):

        SubtitlesCmdString = b'\x0207CAB\x03'
        self.__SetHelper('Subtitles', SubtitlesCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomCmdString = b'\x0207CD7\x03'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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


class DeviceHTTPClass():

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):
        self.Debug = False
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
 
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
 
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
           
        self.connectionCounter = 15
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Control': {'Status': {}},
            'Keypad': {'Status': {}},
            'MediaSource': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Random': {'Status': {}},
            'Repeat': {'Status': {}},
            'Shuffle': {'Status': {}},
            'Subtitles': {'Status': {}},
            'Tray': {'Status': {}}
        }

        self.ControlRegex = re.compile('<Status>(Play|Pause|Stop|Slow Forward|Slow Reverse|Fast Forward|Fast Reverse)</Status>')
        self.MediaSourceRegex = re.compile('<Input_Info><Status>(Not Select|DISC|USB|Network|Mediacenter|Setup|Netflix|YouTube|BlockBuster|FilmFresh|HuluPlus|Picasa|HomeMenu|Vudu|Maxdome|Dropbox|Spotify)</Status></Input_Info>')
        self.PowerRegex = re.compile('<Power>(On|Network Standby)</Power>')
        self.TrayRegex = re.compile('<Tray>(Open|Close|Error Stop)</Tray>')

    def SetControl(self, value, qualifier):

        ValueStateValues = {
            'Play': '<Play>Play</Play>',
            'Pause': '<Play>Pause</Play>',
            'Stop': '<Play>Stop</Play>',
            'Skip +' 	: '<Skip>Fwd</Skip>',
            'Skip -' 	   : '<Skip>Rev</Skip>','Slow Forward' : '<Slow>Fwd</Slow>',
            'Slow Reverse' :'<Slow>Rev</Slow>',
            'Fast Forward' :'<Fast>Fwd</Fast>',
            'Fast Reverse' :'<Fast>Rev</Fast>',
            'Angle'        :'<Stream>ANGLE</Stream>',
            'Audio'        :'<Stream>AUDIO</Stream>',
            'PinP'         : '<Stream>PinP</Stream>',
            '2nd Video'    : '<Stream>2nd Video</Stream>',
            '2nd Audio'    : '<Stream>2nd Audio</Stream>',
            'Normal'       : '<Trick_Play>Normal</Trick_Play>','SetA Point'   : '<Trick_Play>SetA Point</Trick_Play>',
            'A-B Repeat'   :'<Trick_Play>A-B Repeat</Trick_Play>'
        }

        ControlCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                           '<YAMAHA_AV cmd="PUT">' \
                           '<Main_Zone>' \
                           '<Play_Control>' \
                           '{0}' \
                           '</Play_Control>' \
                           '</Main_Zone>' \
                           '</YAMAHA_AV>'.format(ValueStateValues[value])
        self.__SetHelper('Control', value, qualifier, url='', data=ControlCmdString.encode())

    def UpdateControl(self, value, qualifier):

        ValueStateValues = {
            'Play': 'Play',
            'Pause': 'Pause',
            'Stop': 'Stop',
            'Slow Forward': 'Slow Forward',
            'Slow Reverse': 'Slow Reverse',
            'Fast Forward': 'Fast Forward',
            'Fast Reverse': 'Fast Reverse',
        }

        ControlCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                           '<YAMAHA_AV cmd="GET">' \
                           '<Main_Zone>' \
                           '<Play_Info>' \
                           '<Status>GetParam</Status>' \
                           '</Play_Info>' \
                           '</Main_Zone>' \
                           '</YAMAHA_AV>'

        res = self.__UpdateHelper('Control', value, qualifier, url='', data=ControlCmdString.encode())
        if res:
            try:
                value = ValueStateValues[re.findall(self.ControlRegex, res)[0]]
                self.WriteStatus('Control', value, None)
            except (KeyError, IndexError):
                print(['Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '0': '0'
        }

        KeypadCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                          '<YAMAHA_AV cmd="PUT">' \
                          '<Main_Zone>' \
                          '<Remote_Control>' \
                          '<Numeric>' \
                          '{0}' \
                          '</Numeric>' \
                          '</Remote_Control>' \
                          '</Main_Zone>' \
                          '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('Keypad', value, qualifier, url='', data=KeypadCmdString.encode())

    def SetMediaSource(self, value, qualifier):

        ValueStateValues = {
            'Media Center': 'Mediacenter',
            'Setup': 'Setup',
            'Netflix': 'Netflix',
            'YouTube': 'YouTube',
            'BlockBuster': 'BlockBuster',
            'Film Fresh': 'FilmFresh',
            'Hulu Plus': 'HuluPlus',
            'Picasa': 'Picasa',
            'Home Menu': 'HomeMenu',
            'Vudu': 'Vudu',
            'Maxdome': 'Maxdome',
            'Dropbox': 'Dropbox',
            'Spotify': 'Spotify'
        }
        MediaSourceCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                               '<YAMAHA_AV cmd="PUT">' \
                               '<Main_Zone>' \
                               '<DirectCall>' \
                               '<Home_Menu>' \
                               '{0}' \
                               '</Home_Menu>' \
                               '</DirectCall>' \
                               '</Main_Zone>' \
                               '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('MediaSource', value, qualifier, url='', data=MediaSourceCmdString.encode())

    def UpdateMediaSource(self, value, qualifier):

        ValueStateValues = {
            'Not Select': 'None Selected',
            'DISC': 'Disc',
            'USB': 'USB',
            'Network': 'Network',
            'Mediacenter': 'Media Center',
            'Setup': 'Setup',
            'Netflix': 'Netflix',
            'YouTube': 'YouTube',
            'BlockBuster': 'BlockBuster',
            'FilmFresh': 'Film Fresh',
            'HuluPlus': 'Hulu Plus',
            'Picasa': 'Picasa',
            'HomeMenu': 'Home Menu',
            'Vudu': 'Vudu',
            'Maxdome': 'Maxdome',
            'Dropbox': 'Dropbox',
            'Spotify': 'Spotify'
        }

        MediaSourceCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                               '<YAMAHA_AV cmd="GET">' \
                               '<Main_Zone>' \
                               '<Input_Info>' \
                               '<Status>GetParam</Status>' \
                               '</Input_Info>' \
                               '</Main_Zone>' \
                               '</YAMAHA_AV>'

        res = self.__UpdateHelper('MediaSource', value, qualifier, url='', data=MediaSourceCmdString.encode())
        if res:
            try:
                value = ValueStateValues[re.findall(self.MediaSourceRegex, res)[0]]
                self.WriteStatus('MediaSource', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '<Cursor>Up</Cursor>',
            'Down': '<Cursor>Down</Cursor>',
            'Left': '<Cursor>Left</Cursor>',
            'Right': '<Cursor>Right</Cursor>',
            'Enter': '<Cursor>Enter</Cursor>',
            'Return': '<Cursor>Return</Cursor>',
            'Top Menu': '<Menu>TOP MENU</Menu>',
            'Popup Menu': '<Menu>POPUP MENU</Menu>',
            'OSD On Screen': '<OSD>OnScreen</OSD>',
            'OSD Status': '<OSD>Status</OSD>',
            'Setup': '<Function>SETUP</Function>',
            'Home': '<Function>HOME</Function>',
            'Clear': '<Function>CLEAR</Function>',
            'Red': '<Color>RED</Color>',
            'Green': '<Color>GREEN</Color>',
            'Blue': '<Color>BLUE</Color>',
            'Yellow': '<Color>YELLOW</Color>'
        }

        MenuNavigationCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                                  '<YAMAHA_AV cmd="PUT">' \
                                  '<Main_Zone>' \
                                  '<Remote_Control>' \
                                  '{0}' \
                                  '</Remote_Control>' \
                                  '</Main_Zone>' \
                                  '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('MenuNavigation', value, qualifier, url='', data=MenuNavigationCmdString.encode())

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Network Standby'
        }

        PowerCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                         '<YAMAHA_AV cmd="PUT">' \
                         '<Main_Zone>' \
                         '<Power_Control>' \
                         '<Power>' \
                         '{0}' \
                         '</Power>' \
                         '</Power_Control>' \
                         '</Main_Zone>' \
                         '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('Power', value, qualifier, url='', data=PowerCmdString.encode())

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Network Standby': 'Off'
        }

        PowerCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                         '<YAMAHA_AV cmd="GET">' \
                         '<Main_Zone>' \
                         '<Power_Control>' \
                         '<Power>GetParam</Power>' \
                         '</Power_Control>' \
                         '</Main_Zone>' \
                         '</YAMAHA_AV>'

        res = self.__UpdateHelper('Power', value, qualifier, url='', data=PowerCmdString.encode())
        if res:
            try:
                value = ValueStateValues[re.findall(self.PowerRegex, res)[0]]
                self.WriteStatus('Power', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response')

    def SetRandom(self, value, qualifier):

        ValueStateValues = {
            'Chapter/Track/File': 'Random Chapter/Track/File',
            'Title': 'Random title',
            'All': 'Random All'
        }

        RandomCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                          '<YAMAHA_AV cmd="PUT">' \
                          '<Main_Zone>' \
                          '<Play_Control>' \
                          '<Trick_Play>' \
                          '{0}' \
                          '</Trick_Play>' \
                          '</Play_Control>' \
                          '</Main_Zone>' \
                          '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('Random', value, qualifier, url='', data=RandomCmdString.encode())

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Chapter/Track/File': 'Repeat Chapter/Track/File',
            'Title': 'Repeat title',
            'Folder': 'Repeat Folder'
        }

        RepeatCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                          '<YAMAHA_AV cmd="PUT">' \
                          '<Main_Zone>' \
                          '<Play_Control>' \
                          '<Trick_Play>' \
                          '{0}' \
                          '</Trick_Play>' \
                          '</Play_Control>' \
                          '</Main_Zone>' \
                          '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('Repeat', value, qualifier, url='', data=RepeatCmdString.encode())

    def SetShuffle(self, value, qualifier):

        ValueStateValues = {
            'Chapter/Track/File': 'Shuffle Chapter/Track/File',
            'Title': 'Shuffle title',
            'All': 'Shuffle All'
        }

        ShuffleCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                           '<YAMAHA_AV cmd="PUT">' \
                           '<Main_Zone>' \
                           '<Play_Control>' \
                           '<Trick_Play>' \
                           '{0}' \
                           '</Trick_Play>' \
                           '</Play_Control>' \
                           '</Main_Zone>' \
                           '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('Shuffle', value, qualifier, url='', data=ShuffleCmdString.encode())

    def SetSubtitles(self, value, qualifier):

        SubtitlesCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                             '<YAMAHA_AV cmd="PUT">' \
                             '<Main_Zone>' \
                             '<Play_Control>' \
                             '<Stream>' \
                             'SUBTITLE' \
                             '</Stream>' \
                             '</Play_Control>' \
                             '</Main_Zone>' \
                             '</YAMAHA_AV>'

        self.__SetHelper('Subtitles', value, qualifier, url='', data=SubtitlesCmdString.encode())

    def SetTray(self, value, qualifier):

        ValueStateValues = {
            'Open': 'Open',
            'Close': 'Close'
        }

        TrayCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                        '<YAMAHA_AV cmd="PUT">' \
                        '<Main_Zone>' \
                        '<Tray_Control>' \
                        '<Tray>' \
                        '{0}' \
                        '</Tray>' \
                        '</Tray_Control>' \
                        '</Main_Zone>' \
                        '</YAMAHA_AV>'.format(ValueStateValues[value])

        self.__SetHelper('Tray', value, qualifier, url='', data=TrayCmdString.encode())

    def UpdateTray(self, value, qualifier):

        ValueStateValues = {
            'Open': 'Open',
            'Close': 'Close',
            'Error Stop': 'Error Stop'
        }

        TrayCmdString = '<?xml version="1.0" encoding="utf-8"?>' \
                        '<YAMAHA_AV cmd="GET">' \
                        '<Main_Zone>' \
                        '<Play_Info>' \
                        '<Tray>GetParam</Tray>' \
                        '</Play_Info>' \
                        '</Main_Zone>' \
                        '</YAMAHA_AV>'

        res = self.__UpdateHelper('Tray', value, qualifier, url='', data=TrayCmdString.encode())
        if res:
            try:
                value = ValueStateValues[re.findall(self.TrayRegex, res)[0]]
                self.WriteStatus('Tray', value, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True        
        
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), 'YamahaRemoteControl/ctrl')
        headers = {'Content-Type': 'text/xml'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
                
        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), 'YamahaRemoteControl/ctrl')
        headers = {'Content-Type': 'text/xml'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback
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
        if self.connectionFlag == False:
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
                
class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()
