from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PlaybackStatus': {'Status': {}},
            'Power': {'Status': {}},
            'Random': {'Status': {}},
            'RandomStatus': {'Status': {}},
            'RCEmulation': {'Status': {}},
            'Repeat': {'Status': {}},
            'RepeatStatus': {'Status': {}},
            'Title_Chapter_TrackStatus': {'Parameters': ['Source', 'Type'], 'Status': {}},
            'Transport': {'Status': {}},
            'Tray': {'Status': {}},
            'TrayStatus': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!\x01\\x28\x00\x03([\x00-\x17][\x00-\x3B][\x00-\x3B])\x0D'), self.__MatchElapsedTime, None)
            self.AddMatchString(re.compile(b'!\x01\x2C\x00\x01(\x00|\x01|\x02|\x03|\x04|\x05|\x20)\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'!\x01\\x29\x00\x04(\x00|\x01)(\x00|\x01|\x02|\x03|\x04|\x0A)(\x81|\x01)(.)\x0D'), self.__MatchPlaybackStatus, None)
            self.AddMatchString(re.compile(b'!\x01\x00\x00\x01(\x00|\x01)\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'!\x01\x2D\x00\x03([\x00-\xFF]{3})\x0D'), self.__MatchTitle_Chapter_TrackStatus, None)
            self.AddMatchString(re.compile(b'!\x01(\x08|\x00|\x2C|\\x29|\\x28|\x2D)(\x82|\x83|\x84|\x85|\x86)[\x00-\xFF]{1,4}\x0D'), self.__MatchError, None)

    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = b'!\x01\x28\x01\xF0\x0D'
        self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)

    def __MatchElapsedTime(self, match, tag):

        value = '{:02}:{:02}:{:02}'.format(match.group(1)[0], match.group(1)[1], match.group(1)[2])
        self.WriteStatus('ElapsedTime', value, None)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'!\x01\x2C\x01\xF0\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Blu-ray',
            b'\x01': 'DVD-video',
            b'\x02': 'CD',
            b'\x03': 'Data Disc',
            b'\x04': 'USB Media',
            b'\x05': 'Network Media',
            b'\x20': 'No Media'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
                '0': b'!\x01\x08\x02\x19\x00\x0D',
                '1': b'!\x01\x08\x02\x19\x01\x0D',
                '2': b'!\x01\x08\x02\x19\x02\x0D',
                '3': b'!\x01\x08\x02\x19\x03\x0D',
                '4': b'!\x01\x08\x02\x19\x04\x0D',
                '5': b'!\x01\x08\x02\x19\x05\x0D',
                '6': b'!\x01\x08\x02\x19\x06\x0D',
                '7': b'!\x01\x08\x02\x19\x07\x0D',
                '8': b'!\x01\x08\x02\x19\x08\x0D',
                '9': b'!\x01\x08\x02\x19\x09\x0D'
            }
        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
                'Popup Menu': b'!\x01\x08\x02\x19\x43\x0D',
                'Top Menu': b'!\x01\x08\x02\x19\x42\x0D',
                'Left': b'!\x01\x08\x02\x19\x51\x0D',
                'Right': b'!\x01\x08\x02\x19\x50\x0D',
                'Up': b'!\x01\x08\x02\x19\x56\x0D',
                'Down': b'!\x01\x08\x02\x19\x55\x0D',
                'Home': b'!\x01\x08\x02\x19\x0B\x0D',
                'Cancel': b'!\x01\x08\x02\x19\x3A\x0D',
                'Return': b'!\x01\x08\x02\x19\x48\x0D',
                'OK': b'!\x01\x08\x02\x19\x57\x0D',
                'Red / A': b'!\x01\x08\x02\x19\x6B\x0D',
                'Green / B': b'!\x01\x08\x02\x19\x6C\x0D',
                'Yellow / C': b'!\x01\x08\x02\x19\x6D\x0D',
                'Blue / D': b'!\x01\x08\x02\x19\x6E\x0D'
            }
        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdatePlaybackStatus(self, value, qualifier):
        PlaybackStatusCmdString = b'!\x01\x29\x01\xF0\x0D'
        self.__UpdateHelper('PlaybackStatus', PlaybackStatusCmdString, value, qualifier)

    def __MatchPlaybackStatus(self, match, tag):

        TrayValues = {
            b'\x00': 'Open',
            b'\x01': 'Closed'
        }
        ValueStateValues = {
            b'\x00': 'Stop',
            b'\x01': 'Play',
            b'\x02': 'Pause',
            b'\x03': 'Resume-stop',
            b'\x0A': 'Other'
        }
        ScanningValues = {
            b'\x81': 'Rewind',
            b'\x01': 'Fast Forward'
        }
        RepeatValues = {
            0x10: 'One',
            0x20: 'All'
        }
        RandomValues = {
            1: 'On',
            0: 'Off'
        }
        self.WriteStatus('TrayStatus', TrayValues[match.group(1)], None)
        if match.group(2) == b'\x04':
            self.WriteStatus('PlaybackStatus', ScanningValues[match.group(3)], None)
        else:
            self.WriteStatus('PlaybackStatus', ValueStateValues[match.group(2)], None)
        PlaybackMode = match.group(4)[0]
        self.WriteStatus('RepeatStatus', RepeatValues[PlaybackMode & 0x30], None)
        self.WriteStatus('RandomStatus', RandomValues[PlaybackMode & 1], None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'!\x01\x08\x02\x19\x7B\x0D',
            'Off': b'!\x01\x08\x02\x19\x7C\x0D'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'!\x01\x00\x01\xF0\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetRandom(self, value, qualifier):

        RandomCmdString = b'!\x01\x08\x02\x19\x40\x0D'
        self.__SetHelper('Random', RandomCmdString, value, qualifier)

    def UpdateRandomStatus(self, value, qualifier):

        self.UpdatePlaybackStatus(value, qualifier)

    def SetRCEmulation(self, value, qualifier):

        ValueStateValues = {
            'Standby': b'!\x01\x08\x02\x19\x0C\x0D',
            'Search': b'!\x01\x08\x02\x19\x4C\x0D',
            '<<': b'!\x01\x08\x02\x19\x32\x0D',
            '>>': b'!\x01\x08\x02\x19\x34\x0D',
            '|<': b'!\x01\x08\x02\x19\x21\x0D',
            '>|': b'!\x01\x08\x02\x19\x20\x0D',
            'Display': b'!\x01\x08\x02\x19\x12\x0D',
            'Status': b'!\x01\x08\x02\x19\x4B\x0D',
            'HDMI': b'!\x01\x08\x02\x19\x58\x0D',
            'Trim': b'!\x01\x08\x02\x19\x25\x0D',
            'Angle': b'!\x01\x08\x02\x19\x49\x0D',
            'Zoom': b'!\x01\x08\x02\x19\x44\x0D',
            'Mode': b'!\x01\x08\x02\x19\x4D\x0D',
            'Audio': b'!\x01\x08\x02\x19\x45\x0D',
            'Subtitles': b'!\x01\x08\x02\x19\x41\x0D',
            'Setup': b'!\x01\x08\x02\x19\x4A\x0D',
            'Red/A': b'!\x01\x08\x02\x19\x6B\x0D',
            'Green/B': b'!\x01\x08\x02\x19\x6C\x0D',
            'Yellow/C': b'!\x01\x08\x02\x19\x6D\x0D',
            'Blue/D': b'!\x01\x08\x02\x19\x6E\x0D',
            'PIP Audio': b'!\x01\x08\x02\x19\x6A\x0D'
        }
        RCEmulationCmdString = ValueStateValues[value]
        self.__SetHelper('RCEmulation', RCEmulationCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):

        RepeatCmdString = b'!\x01\x08\x02\x19\x1D\x0D'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeatStatus(self, value, qualifier):
        self.UpdatePlaybackStatus(value, qualifier)

    def UpdateTitle_Chapter_TrackStatus(self, value, qualifier):

        Title_Chapter_TrackStatusCmdString = b'!\x01\x2D\x01\xF0\x0D'
        self.__UpdateHelper('Title_Chapter_TrackStatus', Title_Chapter_TrackStatusCmdString, value, qualifier)

    def __MatchTitle_Chapter_TrackStatus(self, match, tag):

        CurrentTitle, CurrentChapter = unpack('>BH', match.group(1))
        self.WriteStatus('Title_Chapter_TrackStatus', CurrentTitle, {'Source': 'DVD-Video', 'Type': 'Title'})
        self.WriteStatus('Title_Chapter_TrackStatus', CurrentChapter, {'Source': 'DVD-Video', 'Type': 'Chapter'})
        self.WriteStatus('Title_Chapter_TrackStatus', 0, {'Source': 'DVD-Video', 'Type': 'Track'})
        self.WriteStatus('Title_Chapter_TrackStatus', CurrentTitle, {'Source': 'Blu-ray', 'Type': 'Title'})
        self.WriteStatus('Title_Chapter_TrackStatus', CurrentChapter, {'Source': 'Blu-ray', 'Type': 'Chapter'})
        self.WriteStatus('Title_Chapter_TrackStatus', 0, {'Source': 'Blu-ray', 'Type': 'Track'})
        self.WriteStatus('Title_Chapter_TrackStatus', 0, {'Source': 'Other', 'Type': 'Title'})
        self.WriteStatus('Title_Chapter_TrackStatus', 0, {'Source': 'Other', 'Type': 'Chapter'})
        self.WriteStatus('Title_Chapter_TrackStatus', CurrentChapter, {'Source': 'Other', 'Type': 'Track'})

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
                'Play': b'!\x01\x08\x02\x19\x35\x0D',
                'Stop': b'!\x01\x08\x02\x19\x36\x0D',
                'Pause': b'!\x01\x08\x02\x19\x30\x0D',
                'Previous': b'!\x01\x08\x02\x19\x21\x0D',
                'Next': b'!\x01\x08\x02\x19\x20\x0D',
                'Rewind': b'!\x01\x08\x02\x19\x32\x0D',
                'Fast Forward': b'!\x01\x08\x02\x19\x34\x0D',
                'A-B': b'!\x01\x08\x02\x19\x69\x0D'
            }
        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetTray(self, value, qualifier):

        TrayCmdString = b'!\x01\x08\x02\x19\x2D\x0D'
        self.__SetHelper('Tray', TrayCmdString, value, qualifier)

    def UpdateTrayStatus(self, value, qualifier):

        self.UpdatePlaybackStatus(value, qualifier)

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

    def __MatchError(self, match, tag):

        Commands = {
            b'\x00' : 'Power',
            b'\x2C' : 'Input',
            b'\x29' : 'Transport',
            b'\x08' : 'RC5 IR',
            b'\x28' : 'Elapsed Time',
            b'\x2D' : 'Title/Chapter/Track Status'
        }
        Errors = {
            b'\x82' : 'Invalid Zone',
            b'\x83' : 'Command Not Recognised',
            b'\x84' : 'Parameter Not Recognised',
            b'\x85' : 'Command Invalid At This Time',
            b'\x86' : 'Invalid Data Length'
        }
        print('{}: {}'.format(Commands[match.group(1)],Errors[match.group(2)]))

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
    
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
                
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
