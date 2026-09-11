from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import math
import binascii


class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self._DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'TileMode': {'Parameters':['Column','Row'], 'Status': {}},
            'TilePosition': {'Parameters':['Tile ID'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK(01|02|04|06|07|09|10|11|12|13|14|15|16|17|18|19|1A|1B|1C|1D|1E|1F|0B)x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK0([10])x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK(60|90|A0|80|70|C0|D0)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK0([10])x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK0([10])x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-fA-F]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([cebadfi]) [0-9a-f]{2} NG(.*)x'), self.__MatchError, None)

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
            'Original'       : '06', 
            '14:9'           : '07', 
            'Just Scan'      : '09', 
            'Full Wide'      : '0B', 
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
            '06' : 'Original', 
            '07' : '14:9', 
            '09' : 'Just Scan', 
            '0B' : 'Full Wide', 
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

        value = ValueStateValues[match.group(1).decode()]
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

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'   : '00', 
            'Down' : '01'
        }

        ChannelCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB'              : '60', 
            'HDMI(DTV)'        : '90', 
            'HDMI(PC)'         : 'A0', 
            'DVI-D(DTV)'       : '80', 
            'DVI-D(PC)'        : '70', 
            'DisplayPort(DTV)' : 'C0', 
            'DisplayPort(PC)'  : 'D0'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '60' : 'RGB', 
            '90' : 'HDMI(DTV)', 
            'A0' : 'HDMI(PC)', 
            '80' : 'DVI-D(DTV)', 
            '70' : 'DVI-D(PC)', 
            'C0' : 'DisplayPort(DTV)', 
            'D0' : 'DisplayPort(PC)'
        }

        value = ValueStateValues[match.group(1).decode()]
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
            'Menu'  : '43', 
            'Enter' : '44', 
            'Exit'  : '5B', 
            'Back'  : '28'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

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

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetTileMode(self, value, qualifier):

        column = int(qualifier['Column'])
        row = int(qualifier['Row'])
        if 0 <= row <= 15 and 0 <= column <= 15: 
            Value = '{0:X}{1:X}'.format(column, row)
            TileModeCmdString = 'dd {0} {1}\r'.format(self._DeviceID, Value)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        TileID = int(qualifier['Tile ID'])
        if 1 <= TileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(self._DeviceID, TileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'            : '01', 
            'Off'           : '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off', 
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1), 16)
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        if 'OK' in response:
            return response
        elif 'NG' in response:
            err = 'Error in command: {0}'.format(sourceCmdName)
            self.Error([err])
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
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

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
        self.counter = 0

        State = {
            'c' : 'Aspect Ratio / Channel Step / Keypad / Menu Navigation',
            'e' : 'Audio Mute',
            'b' : 'Input',
            'a' : 'Power',
            'd' : 'Video Mute / Tile Mode',
            'f' : 'Volume',
            'i' : 'Tile Position'
            }
            
        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1,temp2)
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


class DeviceEthernetClass:

    def __init__(self):

        self.Debug = False
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}
        self._Writecommunity = 'lgecommer'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.CommandOIDDict = {
            'AspectRatio':          '1.3.6.1.4.1.7824.300.3.3.0',
            'AudioMute':            '1.3.6.1.4.1.7824.300.3.5.0',
            'Channel':              '1.3.6.1.4.1.7824.300.3.23.0',
            'ExecutiveMode':        '1.3.6.1.4.1.7824.300.3.13.0',
            'Input':                '1.3.6.1.4.1.7824.300.3.2.0',
            'Keypad':               '1.3.6.1.4.1.7824.300.3.23.0',
            'MenuNavigation':       '1.3.6.1.4.1.7824.300.3.23.0',
            'PowerOff':             '1.3.6.1.4.1.7824.300.3.1.0',
            'VideoMute':            '1.3.6.1.4.1.7824.300.3.4.0',
            'Volume':               '1.3.6.1.4.1.7824.300.3.6.0'
        }

        self.SNMP = SNMPDevice(self._Writecommunity, self.CommandOIDDict)

    @property
    def Writecommunity(self):
        return self._Writecommunity

    @Writecommunity.setter
    def Writecommunity(self, value):
        self._Writecommunity = str(value)
        self.SNMP = SNMPDevice(self._Writecommunity, self.CommandOIDDict)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'            : '01', 
            '16:9'           : '02', 
            'Zoom'           : '04', 
            'Original'       : '06', 
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

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'   : '00', 
            'Down' : '01'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB'              : '60', 
            'HDMI(DTV)'        : '90', 
            'HDMI(PC)'         : 'A0', 
            'DVI-D(DTV)'       : '80', 
            'DVI-D(PC)'        : '70', 
            'DisplayPort(DTV)' : 'C0', 
            'DisplayPort(PC)'  : 'D0'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

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

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : '40', 
            'Down'  : '41', 
            'Left'  : '07', 
            'Right' : '06', 
            'Menu'  : '43', 
            'Enter' : '44', 
            'Exit'  : '5B', 
            'Back'  : '28'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '00'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '{0:02X}'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = self.SNMP.encodeMsg('Set',command, commandstring)
        self.Send(commandstring)

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

    def __init__(self, Hostname, IPPort=161, Protocol='UDP', ServicePort=0, Model=None):
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


class SNMPDeviceException(Exception):
    pass


class SNMPDevice:

    def __init__(self, community, CommandOIDDict):

        self.community = community
        self.CommandOIDDict = CommandOIDDict
        self.oidList = {}
        for command in CommandOIDDict:
            self.oidList[command] = self.__BuildOID(self.CommandOIDDict[command])
        self.community = community
        self.communityString = b'\x04'+pack('>B', len(self.community))+self.community.encode()
        self.GetNext = False
        self.nextOID = None

    def addOID(self, command, oid):

        if command in self.oidList:
            raise SNMPDeviceException('Command/UID already associated with a different OID')
        self.oidList[command] = self.__BuildOID(oid)

    def getOID(self, command):

        if command not in self.oidList:
            raise SNMPDeviceException('Command/UID not in OID List of the device')
        return self.__RebuildOIDString(self.oidList[command])

    def decodeOID(self, msg, command = None, OID = None):

        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if OID is None and command is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')
        try:
            if OID is not None:
                oidIndex = msg.index(self.__BuildOID(OID))
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex-1]
            OID = msg[oidIndex: oidIndex+oidLength]
            value = self.__RebuildOIDString(OID)
            return value
        except ValueError:
            raise SNMPDeviceException('OID for that command/UID not found in the message')

    def encodeMsg(self, queryType, command=None, value = None, OID = None):

        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
            }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04'+ pack('>B', valueLen)+ valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:])/2)*2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02'+ pack('>B', valueLen)+ valueBytes
            else:
                raise TypeError('Value is not of type int or string')
        else:
            valueMsg = b'\x05\x00'
            
        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
            else:
                oid = self.oidList[command]
        else:
            oid = self.nextOID
            self.GetNext = False

        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg+valueMsg)) + oidMsg+valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(requestID+error+errorIndex+varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(snmpVersion+self.communityString+snmpPduMsg)) + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg            

    def encodeMsgMultiOID(self, queryType, command=None, value = None, OID = None, NextOID = None):

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
            }

        valueMsg = None
        pduLenMsg = None
        snmpLenMsg = None

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04'+ pack('>B', valueLen)+ valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:])/2)*2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02'+ pack('>B', valueLen)+ valueBytes
            else:
                pass
        else:
            valueMsg = b'\x05\x00'
            
        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
        else:
            oid = self.nextOID
            self.GetNext = False

        varbindListMsg= b''
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        for command2do in command:
            if NextOID:
                oid = self.oidList[command2do]+ pack('>B', NextOID)
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg+valueMsg)) + oidMsg+valueMsg
            varbindListMsg +=  varbindMsg
        if len(varbindListMsg) < 128:
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg
        elif len(varbindListMsg) < 4096:
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg))  + varbindListMsg

        pduLen = len(requestID+error+errorIndex+varbindListMsg)
        if pduLen < 128:
            pduLenMsg = pack('>B', pduLen)
        elif pduLen < 4096:
            pduLenMsg = b'\x81' + pack('>B', pduLen)

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg

        snmpLen = len(snmpVersion+self.communityString+snmpPduMsg)
        if snmpLen < 128:
            snmpLenMsg = pack('>B', snmpLen)
        elif snmpLen < 4096:
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg

    def decodeMsg(self, msg, command = None, OID = None):

        ValueTypeDict = {
            2  : 'Integer',
            4  : 'Octet String',
            5  : 'Null',
            6  : 'OID',
            64 : 'IPAdddress',
            65 : 'Counter32',
            66 : 'Gauge',
            67 : 'Timeticks',
            68 : 'Opaque',
            69 : 'NsapAddress',
            70 : 'Counter64',
            }

        oidIndex = -1
        valueType = '???'
        cutomOIDHex = None
        value = None

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. You must specify at least one')

        try:
            if OID is not None:
                cutomOIDHex = self.__BuildOID(OID)
                oidIndex = msg.index(cutomOIDHex)
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex-1]
            self.nextOID = msg[oidIndex: oidIndex+oidLength]
            valueIndex = oidIndex+oidLength
            valueType = ValueTypeDict[msg[valueIndex]]
            valueLen = msg[valueIndex+1]
            if valueType == 'Octet String':
                value = msg[valueIndex+2:valueIndex+2+valueLen].decode()
            elif valueType == 'Null':
                value = None
            elif valueType in  ['Integer', 'Timeticks', 'Counter32', 'Gauge']:
                valueBytes = msg[valueIndex+2:valueIndex+2+valueLen]
                value = int(binascii.hexlify(valueBytes), 16)
            elif valueType == 'OID':
                value = self.__RebuildOIDString(msg[valueIndex+2:valueIndex+2+valueLen])
            elif valueType == 'IPAdddress':
                valueBytes = msg[valueIndex+2:valueIndex+2+valueLen]
                ipAddress = [byte for byte in valueBytes]
                value = '.'.join([str(i) for i in ipAddress])
            error = self.__DecodeError(msg)
            if OID is not None:
                oidCheck = self.nextOID != cutomOIDHex
            else:
                oidCheck = self.nextOID != self.oidList[command]
            if oidCheck and error == 0:
                self.GetNext = True
                return error, value, self.encodeMsg('Get-Next', command = command)
            return error, value
        except ValueError:
            pass
        except KeyError:
            pass

    def __DecodeError(self, msg):

        try:
            pduIndex = msg.index(self.community.encode())+len(self.community.encode())
            requestIdIndex = pduIndex + 2
            ErrorIndex = requestIdIndex + 2 + msg[requestIdIndex+1]
            error = msg[ErrorIndex + 2]
            return error
        except ValueError:
            pass
                
    def __BuildOID(self, oidValue):

        try:
            oidValueNumberList = [int(i) for i in oidValue.split('.')]
        except ValueError:
            raise SNMPDeviceException('OIDs supplied is of invalid type/format')

        oid = pack('>B', 40*oidValueNumberList[0]+oidValueNumberList[1])
        for number in oidValueNumberList[2:]:
            if number < 128:
                oid += pack('>B', number)
            else:
                oid += self.__ConvertToMultipleBytes(number)
        return oid

    def __ConvertToMultipleBytes(self, number):

        binaryNumberSplit = re.findall('[0-1]{7}', bin(number)[2:].zfill(math.ceil(len(bin(number)[2:])/7)*7))
        return pack('>'+'B'*len(binaryNumberSplit), *[int(i, 2) if e == len(binaryNumberSplit)-1 else int(i, 2)+0x80 for e, i in enumerate(binaryNumberSplit)])

    def __RebuildOIDString(self, oidBytes):

        if oidBytes[0] == 43:
            oid = [1, 3]
        else:
            oid = [0, 0]
        highBitCheck = False
        oidbin = ''
        for byte in oidBytes[1:]:
            if byte < 127:
                if highBitCheck:
                    oidbin += bin(byte)[2:].zfill(7)
                    oid.append(int(oidbin, 2))
                    oidbin = ''
                    highBitCheck = False
                else:
                    oid.append(byte)
            else:
                oidbin += bin(byte-0x80)[2:].zfill(7)
                highBitCheck = True
        return '.'.join([str(i) for i in oid])