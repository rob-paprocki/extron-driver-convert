from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LocalKeyLock': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteControllerKeyLock': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK(02|06)x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK0([10])x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2} OK0([10])x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK(60|90|A0|97|A7|C0|D0|98|A8)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'o [0-9a-f]{2} OK0([0-2])x'), self.__MatchLocalKeyLock, None)
            self.AddMatchString(re.compile(b'x [0-9a-f]{2} OK(00|01|02|03|04|05|06|08|09|11)x'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'l [0-9a-f]{2} OK0([10])x', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK0([10])x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'p [0-9a-f]{2} OK0([0-2])x'), self.__MatchRemoteControllerKeyLock, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK(01|00)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-f]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([ucembladfXpo]) [0-9a-f]{2} NG(.*)x', re.I), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 255:
            self._DeviceID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Full Wide': '02',
            'Original': '06'
        }

        CmdString = 'kc {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', 'kc {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '02': 'Full Wide',
            '06': 'Original'
        }

        self.WriteStatus('AspectRatio', States[match.group(1).decode()], None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '00',
            'Off': '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', 'ke {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '0': 'On',
            '1': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(self._DeviceID), value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'km {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        self.__UpdateHelper('ExecutiveMode', 'km {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('ExecutiveMode', States[match.group(1).decode()], None)

    def SetInput(self, value, qualifier):

        States = {
            'RGB': '60',
            'HDMI 1 (DTV)': '90',
            'HDMI 1 (PC)': 'A0',
            'HDMI3/HDMI2/DVI (DTV)': '97',
            'HDMI3/HDMI2/DVI (PC)': 'A7',
            'DisplayPort (DTV)': 'C0',
            'DisplayPort (PC)': 'D0',
            'OPS (DTV)': '98',
            'OPS (PC)': 'A8'
        }

        CmdString = 'xb {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'xb {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '60': 'RGB',
            '90': 'HDMI 1 (DTV)',
            'A0': 'HDMI 1 (PC)',
            '97': 'HDMI3/HDMI2/DVI (DTV)',
            'A7': 'HDMI3/HDMI2/DVI (PC)',
            'C0': 'DisplayPort (DTV)',
            'D0': 'DisplayPort (PC)',
            '98': 'OPS (DTV)',
            'A8': 'OPS (PC)'
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

    def SetLocalKeyLock(self, value, qualifier):

        States = {
            'On': '02',
            'On except Power': '01',
            'Off': '00'
        }

        CmdString = 'to {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('LocalKeyLock', CmdString, value, qualifier)

    def UpdateLocalKeyLock(self, value, qualifier):
        self.__UpdateHelper('LocalKeyLock', 'to {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchLocalKeyLock(self, match, tag):

        States = {
            '2': 'On',
            '1': 'On except Power',
            '0': 'Off'
        }

        self.WriteStatus('LocalKeyLock', States[match.group(1).decode()], None)

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
        self.__UpdateHelper('OnScreenDisplay', 'kl {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('OnScreenDisplay', States[match.group(1).decode()], None)

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

        CmdString = 'dx {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        self.__UpdateHelper('PictureMode', 'xd {0} FF\r'.format(self._DeviceID), value, qualifier)

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

        self.WriteStatus('PictureMode', States[match.group(1).decode()], None)

    def SetPower(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'ka {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'ka {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetRemoteControllerKeyLock(self, value, qualifier):

        States = {
            'On': '02',
            'On except Power': '01',
            'Off': '00'
        }

        CmdString = 'tp {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('RemoteControllerKeyLock', CmdString, value, qualifier)

    def UpdateRemoteControllerKeyLock(self, value, qualifier):
        self.__UpdateHelper('RemoteControllerKeyLock', 'tp {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchRemoteControllerKeyLock(self, match, tag):

        States = {
            '2': 'On',
            '1': 'On except Power',
            '0': 'Off'
        }

        self.WriteStatus('RemoteControllerKeyLock', States[match.group(1).decode()], None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '01',
            'Off': '00'
        }

        CmdString = 'kd {0} {1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'kd {0} FF\r'.format(self._DeviceID), value, qualifier)

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
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'kf {0} FF\r'.format(self._DeviceID), value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1), 16), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
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
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'm' : 'Executive Mode',
            'b' : 'Input',
            'l' : 'On Screen Display',
            'x' : 'Picture Mode',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume',
            'p' : 'Remote Controller Key Lock',
            'o' : 'Local Key Lock',
            }

        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        self.Error(['Command: {0}. Error: {1}'.format(temp1,temp2)])


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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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