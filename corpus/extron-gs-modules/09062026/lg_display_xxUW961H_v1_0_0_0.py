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
        self.__DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK([0-9]{2})x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK([0-9]{2})x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK(00|01|10)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-fA-F]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(a|b|c|d|e|f|m) [0-9a-f]{2} NG(.*)x', re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')

    @property
    def DeviceID(self):
        return self.__DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self.__DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self.__DeviceID = '{0:02X}'.format(int(value))

    def SetPower(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'ka {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = 'ka {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(self.__DeviceID), value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': '01',
            '16:9': '02',
            'Original': '06',
            'Just Scan': '09'
        }

        CmdString = 'kc {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        CmdString = 'kc {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '01': '4:3',
            '02': '16:9',
            '06': 'Original',
            '09': 'Just Scan',
        }

        self.WriteStatus('AspectRatio', States[match.group(1).decode().upper()], None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'Off': '00',
            'On (Without OSD)': '01',
            'On (With OSD)': '10',
            }

        CmdString = 'kd {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        CmdString = 'kd {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '00': 'Off',
            '01': 'On (Without OSD)',
            '10': 'On (With OSD)',
        }

        self.WriteStatus('VideoMute', States[match.group(1).decode()], None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        CmdString = 'ke {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '0': 'On',
            '1': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(self.__DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        CmdString = 'kf {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1), 16), None)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        CmdString = 'km {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('ExecutiveMode', States[match.group(1).decode()], None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Enter': '44',
            'Exit': '5B',
            'Back': '28'
        }

        CmdString = 'mc {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'DTV': '00',
            'ATV': '10',
            'AV': '20',
            'Component': '40',
            'RGB': '60',
            'HDMI 1': '70',
            'HDMI 2': '80',
            'HDMI 3': '90',
        }

        CmdString = 'xb {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        CmdString = 'xb {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '00': 'DTV',
            '10': 'ATV',
            '20': 'AV',
            '40': 'Component',
            '60': 'RGB',
            '70': 'HDMI 1',
            '80': 'HDMI 2',
            '90': 'HDMI 3',
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'OK' in response:
            return response
        elif 'NG' in response:
            err = 'Error in command: {0}'.format(sourceCmdName)
            print('err for', command)
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        elif command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                print('Invalid/unexpected response for', command)
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.__DeviceID == '00':
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
            'a' : 'Power',
            'b' : 'Input',
            'c' : 'Aspect Ratio',
            'd' : 'Video Mute',
            'e' : 'Audio Mute',
            'f' : 'Volume',
            'm' : 'Executive Mode',
            }
            
        ErrorStr = 'Command: {0}. Error: {1}'.format( Commands[match.group(1).decode()] , match.group(2).decode() )
        print('ErrorStr for', command)


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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.__DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

      
    @property
    def DeviceID(self):
        return self.__DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self.__DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self.__DeviceID = '{0:02X}'.format(int(value))

    def SetPowerOff(self, value, qualifier):

        self.__SetHelper('PowerOff', 'ka {0} 00\r'.format(self.__DeviceID), value, qualifier)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(self.__DeviceID), value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': '01',
            '16:9': '02',
            'Original': '06',
            'Just Scan': '09'
        }

        CmdString = 'kc {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        States = {
            'Off': '00',
            'On (Without OSD)': '01',
            'On (With OSD)': '10',
        }

        CmdString = 'kd {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'kf {0} {1:02X}\r'.format(self.__DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Enter': '44',
            'Exit': '5B',
            'Back': '28'
        }

        CmdString = 'mc {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'DTV': '00',
            'ATV': '10',
            'AV': '20',
            'Component': '40',
            'RGB': '60',
            'HDMI 1': '70',
            'HDMI 2': '80',
            'HDMI 3': '90',
        }

        CmdString = 'xb {0} {1}\r'.format(self.__DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        CmdString = 'xb {0} FF\r'.format(self.__DeviceID)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
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