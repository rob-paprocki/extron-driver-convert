from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'Channel': { 'Status': {}},
            'IREmulator': { 'Status': {}},
            'Keyboard': { 'Status': {}},
            'SetChannel': { 'Status': {}},
            'SetForceChannel': { 'Status': {}},
            'Teleport': { 'Status': {}},
        }
                        

        self.AddMatchString(re.compile(b'CH_STATUS (\d{1,4}( \d{1,4})?) (REMOTE|LOCAL|RECORDING)\r'), self.__MatchChannel, None)
        self.AddMatchString(re.compile(b'CH_FAILED (NO_LIVE|RECORDING|MISSING_CHANNEL|MALFORMED_CHANNEL|INVALID_CHANNEL)\r'), self.__MatchError, 'Channel')
        self.AddMatchString(re.compile(b'MISSING_TELEPORT_NAME\r'), self.__MatchError, 'Teleport')
        self.AddMatchString(re.compile(b'INVALID_COMMAND\r'), self.__MatchError, 'Command')

        self.__set_channel_regex = re.compile('^\d{1,4}(?:-\d{1,4})?$')

    def __MatchChannel(self, match, tag):

        value = match.group(1).decode()
        value = value.split()
        value = '-'.join([c.lstrip('0') for c in value])
        self.WriteStatus('Channel', value, None)

    def SetIREmulator(self, value, qualifier):

        ValueStateValues = {
            'Up':                           'UP',
            'Down':                         'DOWN',
            'Left':                         'LEFT',
            'Right':                        'RIGHT',
            'Select':                       'SELECT',
            'TiVo':                         'TIVO',
            'Live TV':                      'LIVETV',
            'Guide':                        'GUIDE',
            'Info':                         'INFO',
            'Exit':                         'EXIT',
            'Thumbs Up':                    'THUMBSUP',
            'Thumbs Down':                  'THUMBSDOWN',
            'Channel Up':                   'CHANNELUP',
            'Channel Down':                 'CHANNELDOWN',
            'Mute':                         'MUTE',
            'Volume Down':                  'VOLUMEDOWN',
            'Volume Up':                    'VOLUMEUP',
            'TV Input':                     'TVINPUT',
            'Video Mode Fixed 480i':        'VIDEO_MODE_FIXED_480i',
            'Video Mode Fixed 480p':        'VIDEO_MODE_FIXED_480p',
            'Video Mode Fixed 720p':        'VIDEO_MODE_FIXED_720p',
            'Video Mode Fixed 1080i':       'VIDEO_MODE_FIXED_1080i',
            'Video Mode Hybrid':            'VIDEO_MODE_HYBRID',
            'Video Mode Hybrid 720p':       'VIDEO_MODE_HYBRID_720p',
            'Video Mode Hybrid 1080i':      'VIDEO_MODE_HYBRID_1080i',
            'Video Mode Native':            'VIDEO_MODE_NATIVE',
            'CC On':                        'CC_ON',
            'CC Off':                       'CC_OFF',
            'Options':                      'OPTIONS',
            'Aspect Correction Full':       'ASPECT_CORRECTION_FULL',
            'Aspect Correction Panel':      'ASPECT_CORRECTION_PANEL',
            'Aspect Correction Zoom':       'ASPECT_CORRECTION_ZOOM',
            'Aspect Correction Wide Zoom':  'ASPECT_CORRECTION_WIDE_ZOOM',
            'Play':                         'PLAY',
            'Forward':                      'FORWARD',
            'Reverse':                      'REVERSE',
            'Pause':                        'PAUSE',
            'Slow':                         'SLOW',
            'Replay':                       'REPLAY',
            'Advance':                      'ADVANCE',
            'Record':                       'RECORD',
            '0':                            'NUM0',
            '1':                            'NUM1',
            '2':                            'NUM2',
            '3':                            'NUM3',
            '4':                            'NUM4',
            '5':                            'NUM5',
            '6':                            'NUM6',
            '7':                            'NUM7',
            '8':                            'NUM8',
            '9':                            'NUM9',
            'Enter':                        'ENTER',
            'Clear':                        'CLEAR',
            'Action A':                     'ACTION_A',
            'Action B':                     'ACTION_B',
            'Action C':                     'ACTION_C',
            'Action D':                     'ACTION_D'
        }

        IREmulatorCmdString = 'IRCODE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('IREmulator', IREmulatorCmdString, value, qualifier)
    def SetKeyboard(self, value, qualifier):

        ValueStateValues = {
            'A':                'A',
            'B':                'B',
            'C':                'C',
            'D':                'D',
            'E':                'E',
            'F':                'F',
            'G':                'G',
            'H':                'H',
            'I':                'I',
            'J':                'J',
            'K':                'K',
            'L':                'L',
            'M':                'M',
            'N':                'N',
            'O':                'O',
            'P':                'P',
            'Q':                'Q',
            'R':                'R',
            'S':                'S',
            'T':                'T',
            'U':                'U',
            'V':                'V',
            'W':                'W',
            'X':                'X',
            'Y':                'Y',
            'Z':                'Z',
            'Minus':            'MINUS',
            'Equals':           'EQUALS',
            'Left Bracket':     'LBRACKET',
            'Right Bracket':    'RBRACKET',
            'Backslash':        'BACKSLASH',
            'Semicolon':        'SEMICOLON',
            'Quote':            'QUOTE',
            'Comma':            'COMMA',
            'Period':           'PERIOD',
            'Slash':            'SLASH',
            'Backquote':        'BACKQUOTE',
            'Keyboard Up':      'KBDUP',
            'Keyboard Down':    'KBDDOWN',
            'Keyboard Left':    'KBDLEFT',
            'Keyboard Right':   'KBDRIGHT',
            'Page Up':          'PAGEUP',
            'Page Down':        'PAGEDOWN',
            'Home':             'HOME',
            'End':              'END',
            'Caps':             'CAPS',
            'Left Shift':       'LSHIFT',
            'Right Shift':      'RSHIFT',
            'Insert':           'INSERT',
            'Backspace':        'BACKSPACE',
            'Delete':           'DELETE',
            'Enter':            'KBDENTER',
            'Stop':             'STOP',
            'Video on Demand':  'VIDEO_ON_DEMAND',
            'Space':            'SPACE'
        }

        KeyboardCmdString = 'KEYBOARD {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Keyboard', KeyboardCmdString, value, qualifier)
    def SetSetChannel(self, value, qualifier):

        if self.__set_channel_regex.match(value):
            SetChannelCmdString = 'SETCH {}\r'.format(value.replace('-', ' '))
            self.__SetHelper('SetChannel', SetChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetChannel')

    def SetSetForceChannel(self, value, qualifier):

        if self.__set_channel_regex.match(value):
            SetForceChannelCmdString = 'FORCECH {}\r'.format(value.replace('-', ' '))
            self.__SetHelper('SetForceChannel', SetForceChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetForceChannel')

    def SetTeleport(self, value, qualifier):

        ValueStateValues = {
            'TiVo Central': 'TIVO',
            'Live TV':      'LIVETV',
            'Guide':        'GUIDE',
            'Now Playing':  'NOWPLAYING'
        }

        TeleportCmdString = 'TELEPORT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Teleport', TeleportCmdString, value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        error_map = {
            'NO_LIVE':              'The DVR was not in Live TV at the time the command was issued.',
            'RECORDING':            'A recording was in progress.',
            'MISSING_CHANNEL':      'Missing at least one parameter for channel number.',
            'MALFORMED_CHANNEL':    'Channel was not a valid integer.',
            'INVALID_CHANNEL':      'Channel was not found in the TCD channel lineup.'
        }

        msg = ''

        if tag == 'Channel':
            msg = error_map[match.group(1).decode()]
        elif tag == 'Teleport':
            msg = 'Missing Teleport screen parameter.'
        elif tag == 'Command':
            msg = 'Invalid command.'

        self.Error(['An error occurred: {}'.format(msg)])

        ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')
            
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
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

