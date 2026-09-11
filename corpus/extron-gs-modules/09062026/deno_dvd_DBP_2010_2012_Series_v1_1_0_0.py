from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.Models = {
            'DBP-2010CI': self.deno_3_470_2010,
            'DBP-2012UDCI': self.deno_3_470_2012,
            'DBP-2012UD': self.deno_3_470_2012,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Angle': {'Status': {}},
            'AngleStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'CurrentChapterTrackNum': {'Status': {}},
            'CurrentTitleAlbumNum': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'DiscTypeStatus': {'Status': {}},
            'Function': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuCall': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RepeatMode': {'Status': {}},
            'Subtitle': {'Status': {}},
            'SubtitleLanguage': {'Status': {}},
            'Transport': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.set_angle_regex = re.compile(b'(\x15)|(\x02\x4B[\x00-\xFF]{6})')
        self.set_aspect_ratio_regex = re.compile(b'(\x15)|(\x02\x78[\x00-\xFF]{4})')
        self.set_function_regex = re.compile(b'(\x15)|(\x02[\x66\x65\x45\x68\x6B][\x00-\xFF]{4})')
        self.set_keypad_regex = re.compile(b'(\x15)|(\x02\x5A[\x00-\xFF]{4})')
        self.set_menu_call_regex = re.compile(b'(\x15)|(\x02[\x46\x47\x50][\x00-\xFF]{4})')
        self.set_menu_navigation_regex = re.compile(b'(\x15)|(\x02[\x48\x4D\x4E][\x00-\xFF]{4})')
        self.set_power_regex = re.compile(b'(\x15)|(\x02[\x20\x21]([\x00-\xFF]{4}|[\x00-\xFF]{18}))')
        self.set_repeat_mode_regex = re.compile(b'(\x15)|(\x02\x69[\x00-\xFF]{4})')
        self.set_subtitle_regex = re.compile(b'(\x15)|(\x02\x4A[\x00-\xFF]{11})')
        self.set_transport_regex = re.compile(b'(\x15)|(\x02[\x40\x41\x42\x6B\x69\x43\x44\x61]([\x00-\xFF]{4}|[\x00-\xFF]{11}|[\x00-\xFF]{5}))')
        self.set_zoom_regex = re.compile(b'(\x15)|(\x02\x6D[\x00-\xFF]{4})')

        self.set_command_regex_map = {
            'Angle': self.set_angle_regex,
            'AspectRatio': self.set_aspect_ratio_regex,
            'Function': self.set_function_regex,
            'Keypad': self.set_keypad_regex,
            'MenuCall': self.set_menu_call_regex,
            'MenuNavigation': self.set_menu_navigation_regex,
            'Power': self.set_power_regex,
            'RepeatMode': self.set_repeat_mode_regex,
            'Subtitle': self.set_subtitle_regex,
            'Transport': self.set_transport_regex,
            'Zoom': self.set_zoom_regex
        }

        self.update_device_status_regex = re.compile(b'(\x15)|(\x02\x30[\x00-\xFF]{26})')

        self.update_command_regex_map = {
            'DeviceStatus': self.update_device_status_regex
        }

    def SetAngle(self, value, qualifier):

        if self.AngleStateValues:
            CmdString = self.AngleStateValues[value]
        else:
            CmdString = b'\x02\x4B\x2B\x00\x00\x00\x00\x03\x37\x39'
        self.__SetHelper('Angle', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x02\x78\x31\x00\x00\x00\x00\x03\x41\x43',
            '16:9 Wide': b'\x02\x78\x32\x00\x00\x00\x00\x03\x41\x44',
            '4:3 Pan Scan': b'\x02\x78\x33\x00\x00\x00\x00\x03\x41\x45',
            '4:3 Letter Box': b'\x02\x78\x34\x00\x00\x00\x00\x03\x41\x46',
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        SubtitleLanguageStateNames = {
            b'\x31': 'Japanese',
            b'\x32': 'English',
            b'\x33': 'French',
            b'\x34': 'Deutsch',
            b'\x35': 'Italian',
            b'\x36': 'Espanol',
            b'\x37': 'Netherlands',
            b'\x38': 'Chinese',
            b'\x39': 'Russian',
            b'\x3A': 'Korean',
            b'\x3B': 'Other'
        }

        AngleStatusStateNames = {
            b'\x31': '1',
            b'\x32': '2',
            b'\x33': '3',
            b'\x34': '4',
            b'\x35': '5',
            b'\x36': '6',
            b'\x37': '7',
            b'\x38': '8',
            b'\x39': '9'
        }

        #DeviceStatusCmdString = b'HELLOW\r'  # TEsting string
        DeviceStatusCmdString = b'\x02\x30\x00\x00\x00\x00\x00\x03\x33\x33' # real command string
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                DiscTypeValue = self.DiscTypeStatusStateNames[res[3:4]]
                self.WriteStatus('DiscTypeStatus', DiscTypeValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Disc Type Status: Invalid/unexpected response'])

            try:
                DeviceStatusValue = self.DeviceStatusStateNames[res[9:10]]
                self.WriteStatus('DeviceStatus', DeviceStatusValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Device Status: Invalid/unexpected response'])

            try:
                PowerValue = 'On' if res[9:10] != b'\x30' else 'Off'
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Power Status: Invalid/unexpected response'])

            try:
                SubtitleValue = SubtitleLanguageStateNames[res[7:8]]
                self.WriteStatus('SubtitleLanguage', SubtitleValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Subtitle Status: Invalid/unexpected response'])

            try:
                AngleValue = AngleStatusStateNames[res[8:9]]
                self.WriteStatus('AngleStatus', AngleValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Angle Status: Invalid/unexpected response'])

            try:
                AlbumNumValue = int(res[11:14].decode())
                self.WriteStatus('CurrentTitleAlbumNum', AlbumNumValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Album Number Status: Invalid/unexpected response'])

            try:
                TrackNumValue = int(res[14:18].decode())
                self.WriteStatus('CurrentChapterTrackNum', TrackNumValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Track Number Status: Invalid/unexpected response'])

    def SetFunction(self, value, qualifier):

        FunctionStateValues = {
            'Clear': b'\x02\x66\x00\x00\x00\x00\x00\x03\x36\x39',
            'Program': b'\x02\x65\x00\x00\x00\x00\x00\x03\x36\x38',
            'Setup': b'\x02\x45\x00\x00\x00\x00\x00\x03\x34\x38',
            'Display': b'\x02\x68\x00\x00\x00\x00\x00\x03\x36\x42',
            'Random': b'\x02\x6B\x00\x00\x00\x00\x00\x03\x36\x45'
        }

        FunctionCmdString = FunctionStateValues[value]
        self.__SetHelper('Function', FunctionCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        KeypadCmdStates = {
            '0': b'\x02\x5A\x30\x00\x00\x00\x00\x03\x38\x44',
            '1': b'\x02\x5A\x31\x00\x00\x00\x00\x03\x38\x45',
            '2': b'\x02\x5A\x32\x00\x00\x00\x00\x03\x38\x46',
            '3': b'\x02\x5A\x33\x00\x00\x00\x00\x03\x39\x30',
            '4': b'\x02\x5A\x34\x00\x00\x00\x00\x03\x39\x31',
            '5': b'\x02\x5A\x35\x00\x00\x00\x00\x03\x39\x32',
            '6': b'\x02\x5A\x36\x00\x00\x00\x00\x03\x39\x33',
            '7': b'\x02\x5A\x37\x00\x00\x00\x00\x03\x39\x34',
            '8': b'\x02\x5A\x38\x00\x00\x00\x00\x03\x39\x35',
            '9': b'\x02\x5A\x39\x00\x00\x00\x00\x03\x39\x36',
            '+10': b'\x02\x5A\x3A\x00\x00\x00\x00\x03\x39\x37'
        }

        KeypadCmdString = KeypadCmdStates[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def SetMenuCall(self, value, qualifier):


        MenuCallCmdString = self.MenuCallStateValues[value]

        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up': b'\x02\x4D\x32\x00\x00\x00\x00\x03\x38\x32',
            'Down': b'\x02\x4D\x34\x00\x00\x00\x00\x03\x38\x34',
            'Left': b'\x02\x4D\x31\x00\x00\x00\x00\x03\x38\x31',
            'Right': b'\x02\x4D\x33\x00\x00\x00\x00\x03\x38\x33',
            'Enter': b'\x02\x4E\x00\x00\x00\x00\x00\x03\x35\x31',
            'Return': b'\x02\x48\x00\x00\x00\x00\x00\x03\x34\x42'
        }

        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerCommandState = {
            'On': b'\x02\x20\x00\x00\x00\x00\x00\x03\x32\x33',
            'Off': b'\x02\x21\x00\x00\x00\x00\x00\x03\x32\x34'
        }

        PowerCmdString = PowerCommandState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRepeatMode(self, value, qualifier):

        RepeatModeStateValues = {
            'Repeat': b'\x02\x69\x31\x00\x00\x00\x00\x03\x39\x44',
            'AB': b'\x02\x69\x32\x00\x00\x00\x00\x03\x39\x45'
        }

        RepeatModeCmdString = RepeatModeStateValues[value]
        self.__SetHelper('RepeatMode', RepeatModeCmdString, value, qualifier)

    def SetSubtitle(self, value, qualifier):

        if self.Subtitle:                #2010 model;
            SubtitleSkipStates = {
                'Forward': b'\x2B',
                'Reverse': b'\x2D'
            }
            SubtitleStateValues = {
                'Primary': (b'\x31', b'\x41\x39', b'\x41\x42'),
                'Primary Style': (b'\x32', b'\x41\x41', b'\x41\x43'),
                'Secondary': (b'\x33', b'\x41\x42', b'\x41\x44')
            }

            if qualifier['Subtitle Skip'] in SubtitleSkipStates:
                skip_direction_byte = SubtitleSkipStates[qualifier['Subtitle Skip']]
                subtitle_byte = SubtitleStateValues[value][0]
                checksum = SubtitleStateValues[value][1 if qualifier['Subtitle Skip'] == 'Forward' else 2]

                Subtitle2010CmdString = b'\x02\x4A' + skip_direction_byte + subtitle_byte + b'\x00\x00\x00\x03' + checksum
                self.__SetHelper('Subtitle', Subtitle2010CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command. for SetSubtitle2010')

        else:                               #2012 models
            SubtitleStateValues = {
            'Primary': b'\x02\x4A\x2B\x31\x00\x00\x00\x03\x41\x39',
            'Primary Style': b'\x02\x4A\x2B\x32\x00\x00\x00\x03\x41\x41',
            'Secondary': b'\x02\x4A\x2B\x33\x00\x00\x00\x03\x41\x42'
            }

            Subtitle2012CmdString = SubtitleStateValues[value]
            self.__SetHelper('Subtitle', Subtitle2012CmdString, value, qualifier)



    def SetTransport(self, value, qualifier):

        TransportStateValues = {
            'Play': b'\x02\x40\x00\x00\x00\x00\x00\x03\x34\x33',
            'Stop': b'\x02\x41\x00\x00\x00\x00\x00\x03\x34\x34',
            'Pause': b'\x02\x42\x00\x00\x00\x00\x00\x03\x34\x35',
            'Random': b'\x02\x6B\x00\x00\x00\x00\x00\x03\x36\x45',
            'Next': b'\x02\x43\x2B\x00\x00\x00\x00\x03\x37\x31',
            'Previous': b'\x02\x43\x2D\x00\x00\x00\x00\x03\x37\x33',
            'FFwd': b'\x02\x44\x2B\x00\x00\x00\x00\x03\x37\x32',
            'Rew': b'\x02\x44\x2D\x00\x00\x00\x00\x03\x37\x34',
            'Eject': b'\x02\x61\x00\x00\x00\x00\x00\x03\x36\x34'
        }

        TransportCmdString = TransportStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomCmdString = b'\x02\x6D\x00\x00\x00\x00\x00\x03\x37\x30'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Communication error.',
            b'\x30': 'Invalid command.',
            b'\x31': 'Inappropriate command format.',
            b'\x32': 'The track, the group, the title or the chapter you specified does not exist.',
            b'\x33': 'The time you specified does not exist.'
        }
        if len(response) == 1 and response[0:1] == b'\x15':
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            response = b''
        elif len(response) >= 3:
            if response[2:3] != b'\x20':
                if response[2:3] in DEVICE_ERROR_CODES:
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[2:3]])])
                else:
                    self.Error(['{0} {1}'.format(sourceCmdName, 'An unknown error occurred.')])

                response = b''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == "UserDefinedCommand":
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_command_regex_map[command])
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.update_command_regex_map[command])

            if not res:
                return b''
            else:
                return self.__CheckResponseForErrors(command, res)


    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False


    def deno_3_470_2010(self):
        self.AngleStateValues = {
            'Forward': b'\x02\x4B\x2B\x00\x00\x00\x00\x03\x37\x39',
            'Reverse': b'\x02\x4B\x2D\x00\x00\x00\x00\x03\x37\x42'
        }
        self.Subtitle = True
        self.DiscTypeStatusStateNames = {
            b'\x31': 'DVD Video',
            b'\x32': 'DVD Audio',
            b'\x33': 'VCD',
            b'\x34': 'CD-DA',
            b'\x35': 'CD-ROM',
            b'\x36': 'Unknown',
            b'\x37': 'SACD',
            b'\x38': 'DVD VR',
            b'\x39': 'BDMV',
            b'\x3A': 'BDAV'
        }

        self.DeviceStatusStateNames = {
            b'\x30': 'Standby',
            b'\x31': 'Disk Loading',
            b'\x32': 'Loading Complete',
            b'\x33': 'Tray Opening',
            b'\x34': 'Tray Closing',
            b'\x41': 'No Disc',
            b'\x42': 'Stopped',
            b'\x43': 'Playing',
            b'\x44': 'Paused',
            b'\x45': 'Scan',
            b'\x46': 'Searching',
            b'\x47': 'Setup',
            b'\x48': 'Playback Control',
            b'\x49': 'Resume Stop',
            b'\x4A': 'DVD Menu'
        }

        self.MenuCallStateValues = {
            'Root Menu':    b'\x02\x47\x00\x00\x00\x00\x00\x03\x34\x41',
            'Top Menu':     b'\x02\x46\x00\x00\x00\x00\x00\x03\x34\x39'
        }


    def deno_3_470_2012(self):
        self.AngleStateValues = False
        self.Subtitle = False
        self.DiscTypeStatusStateNames = {
            b'\x31': 'DVD Video',
            b'\x32': 'DVD Audio',
            b'\x34': 'CD-DA',
            b'\x35': 'CD-ROM',
            b'\x36': 'Unknown',
            b'\x37': 'SACD',
            b'\x38': 'DVD VR',
            b'\x39': 'BDMV',
            b'\x3A': 'BDAV',
            b'\x3B': 'AVCHD',
            b'\x3C': 'Web Stream',
            b'\x3D': 'DLNA',
            b'\x3E': 'AVCREC',
            b'\x3F': 'External Memory',
        }

        self.DeviceStatusStateNames = {
            b'\x30': 'Standby',
            b'\x31': 'Disk Loading',
            b'\x33': 'Tray Opening',
            b'\x34': 'Tray Closing',
            b'\x41': 'No Disc',
            b'\x42': 'Stopped',
            b'\x43': 'Playing',
            b'\x44': 'Paused',
            b'\x45': 'Scan',
            b'\x46': 'Searching',
            b'\x47': 'Setup',
            b'\x49': 'Resume Stop',
            b'\x4A': 'DVD Menu',
            b'\x4B': 'Home Menu'
        }

        self.MenuCallStateValues = {
            'Root Menu':    b'\x02\x47\x00\x00\x00\x00\x00\x03\x34\x41',
            'Top Menu':     b'\x02\x46\x00\x00\x00\x00\x00\x03\x34\x39',
            'Home':         b'\x02\x50\x00\x00\x00\x00\x00\x03\x35\x33'
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

