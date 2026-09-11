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
        self._DeviceID = '01'

        self.Models = {}

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
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2}) OK([0-1][0-9A-F])x',re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9A-F]{2}) OK0(1|0)x',re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm ([0-9A-F]{2}) OK0(1|0)x',re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2}) OK(91|90|80|70|60|A0|A1|C0|D0)x',re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'x ([0-9A-F]{2}) OK([0-9]{2})x',re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2}) OK0(1|0)x',re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2}) OK0(1|0)x',re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9A-F]{2}) OK([0-9a-f]{2})x',re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|m|b|a|d|f|x) ([0-9A-F]{1,2}) NG(.*?)x',re.I), self.__MatchError, None)
            
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'            : '01', 
            '16:9'           : '02', 
            'Zoom'           : '04', 
            'Set by Program' : '06', 
            'Just Scan'      : '09', 
            'Cinema Zoom 1'  : '10', 
            'Cinema Zoom 2'  : '11', 
            'Cinema Zoom 3'  : '12', 
            'Cinema Zoom 4'  : '13', 
            'Cinema Zoom 5'  : '14', 
            'Cinema Zoom 6'  : '15', 
            'Cinema Zoom 7'  : '16', 
            'Cinema Zoom 8'  : '17', 
            'Cinema Zoom 9'  : '18', 
            'Cinema Zoom 10' : '19', 
            'Cinema Zoom 11' : '1A', 
            'Cinema Zoom 12' : '1B', 
            'Cinema Zoom 13' : '1C', 
            'Cinema Zoom 14' : '1D', 
            'Cinema Zoom 15' : '1E', 
            'Cinema Zoom 16' : '1F'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01' : '4:3', 
            '02' : '16:9', 
            '04' : 'Zoom', 
            '06' : 'Set by Program', 
            '09' : 'Just Scan', 
            '10' : 'Cinema Zoom 1', 
            '11' : 'Cinema Zoom 2', 
            '12' : 'Cinema Zoom 3', 
            '13' : 'Cinema Zoom 4', 
            '14' : 'Cinema Zoom 5', 
            '15' : 'Cinema Zoom 6', 
            '16' : 'Cinema Zoom 7', 
            '17' : 'Cinema Zoom 8', 
            '18' : 'Cinema Zoom 9', 
            '19' : 'Cinema Zoom 10', 
            '1A' : 'Cinema Zoom 11', 
            '1B' : 'Cinema Zoom 12', 
            '1C' : 'Cinema Zoom 13', 
            '1D' : 'Cinema Zoom 14', 
            '1E' : 'Cinema Zoom 15', 
            '1F' : 'Cinema Zoom 16'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '00', 
            'Off' : '01'
        }

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'mc {0} 99\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'km {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB' : '60', 
            'DVI-D (PC)' : '70', 
            'DVI-D (DTV)' : '80', 
            'HDMI (DTV)' : '90', 
            'HDMI (PC)' : 'A0', 
            'DISPLAYPORT (DTV)' : 'C0', 
            'DISPLAYPORT (PC)' : 'D0', 
            'OPS (DTV)' : '91', 
            'OPS (PC)' : 'A1'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '60' : 'RGB', 
            '70' : 'DVI-D (PC)', 
            '80' : 'DVI-D (DTV)', 
            '90' : 'HDMI (DTV)', 
            'A0' : 'HDMI (PC)', 
            'C0' : 'DISPLAYPORT (DTV)', 
            'D0' : 'DISPLAYPORT (PC)', 
            '91' : 'OPS (DTV)', 
            'A1' : 'OPS (PC)'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode().upper()]
            self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : '10',
            '1' : '11',
            '2' : '12',
            '3' : '13',
            '4' : '14',
            '5' : '15',
            '6' : '16',
            '7' : '17',
            '8' : '18',
            '9' : '19'
            
        }

        KeypadCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : '40', 
            'Down'  : '41', 
            'Left'  : '07', 
            'Right' : '06', 
            'Enter' : '44', 
            'Back'  : '28', 
            'Exit'  : '5B', 
            'Menu'  : '43'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid'       : '00', 
            'Standard'    : '01', 
            'Cinema'      : '02', 
            'Sports'      : '03', 
            'Game'        : '04', 
            'Expert 1'    : '05', 
            'Expert 2'    : '06', 
            'APS'         : '08',
            'Photos'      : '09',
            'Calibration' : '11'
        }

        PictureModeCmdString = 'dx {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'dx {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '00' : 'Vivid', 
            '01' : 'Standard', 
            '02' : 'Cinema', 
            '03' : 'Sports', 
            '04' : 'Game', 
            '05' : 'Expert 1', 
            '06' : 'Expert 2', 
            '08' : 'APS',
            '09' : 'Photos',
            '11' : 'Calibration'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        PowerCmdString = 'ka {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, None)            

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().upper():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        if self._DeviceID == match.group(1).decode().upper():
            value = int(match.group(2), 16)
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        self.Send(commandstring)

    def __MatchError(self, match, tag):

        State = {
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'm' : 'Executive Mode',
            'b' : 'Input',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume',
            'x' : 'Picture Mode'
        }
        
        temp1 = State[match.group(1).decode().lower()]
        temp2 = match.group(2).decode().upper()
        temp3 = match.group(3).decode()
        value = '{0} Error, DeviceID {1}: {2}'.format(temp1,temp2,temp3)
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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