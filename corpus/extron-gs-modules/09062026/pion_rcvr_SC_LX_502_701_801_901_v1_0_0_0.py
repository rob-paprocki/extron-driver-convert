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


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'ChannelAudioMute': {'Parameters':['Channel'], 'Status': {}},
            'Input': { 'Status': {}},
            'ListeningMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zone2AudioMute': { 'Status': {}},
            'Zone2Input': { 'Status': {}},
            'Zone2Power': { 'Status': {}},
            'Zone2Preset': { 'Status': {}},
            'Zone2Volume': { 'Status': {}},
            }

        
        self.ChannelAudioMuteValues = None
        self.lastChannelAudioMuteUpdate = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x211AMT0(0|1)\x1A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x211CMT(0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1)0(0|1))\x1A'), self.__MatchChannelAudioMute, None)
            self.AddMatchString(re.compile(b'\x211SLI(01|02|03|10|11|12|22|23|24|25|26|29|2B|2E|55|56)\x1A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x211LMD(00|01|03|05|06|08|09|0A|0B|0C|0D|0E|0F|11|13|1F|40|80|82|FF)\x1A'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(b'\x211PWR0(0|1)\x1A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x211MVL([0-9A-F]{2})\x1A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x211ZMT0(0|1)\x1A'), self.__MatchZone2AudioMute, None)
            self.AddMatchString(re.compile(b'\x211SLZ(01|02|10|11|12|22|23|24|25|26|29|2B|2E)\x1A'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'\x211ZPW0(0|1)\x1A'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'\x211ZVL([0-9A-F]{2})\x1A'), self.__MatchZone2Volume, None)
            
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '!1AMT01\r\n', 
            'Off' : '!1AMT00\r\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '!1AMTQSTN\r\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannelAudioMute(self, value, qualifier):

        ChannelStates = {
            'Front Left'          : 1 , 
            'Front Right'         : 3 , 
            'Center'              : 5 , 
            'Surround Left'       : 7 , 
            'Surround Right'      : 9 , 
            'Surround Back Left'  : 11 , 
            'Surround Back Right' : 13 , 
            'Subwoofer 1'         : 15 , 
            'Height 1 Left'       : 17 , 
            'Height 1 Right'      : 19, 
            'Height 2 Left'       : 21, 
            'Height 2 Right'      : 23, 
            'Subwoofer 2'         : 25
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if self.ChannelAudioMuteValues:
            chan_val = qualifier['Channel']
            string_val = self.ChannelAudioMuteValues
            if chan_val in ChannelStates and string_val:
                slice_val = ChannelStates[chan_val]
                new_val = ''.join([string_val[:slice_val], ValueStateValues[value], string_val[slice_val+1:]])
                ChannelAudioMuteCmdString = '!1CMT{0}\r\n'.format(new_val)
                self.__SetHelper('ChannelAudioMute', ChannelAudioMuteCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelAudioMute')
        else:
            #Requires an update before the set commands can be sent
            self.UpdateChannelAudioMute(value, qualifier)
            self.SetChannelAudioMute(value, qualifier)
    def UpdateChannelAudioMute(self, value, qualifier):

        ChannelAudioMuteCmdString = '!1CMTQSTN\r\n'
        self.__UpdateHelper('ChannelAudioMute', ChannelAudioMuteCmdString, value, qualifier)


    def __MatchChannelAudioMute(self, match, tag):

        ChannelStates = {
            1  : 'Front Left', 
            2  : 'Front Right', 
            3  : 'Center', 
            4  : 'Surround Left', 
            5  : 'Surround Right', 
            6  : 'Surround Back Left', 
            7  : 'Surround Back Right', 
            8  : 'Subwoofer 1', 
            9  : 'Height 1 Left', 
            10 : 'Height 1 Right', 
            11 : 'Height 2 Left', 
            12 : 'Height 2 Right', 
            13 : 'Subwoofer 2'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        self.ChannelAudioMuteValues = match.group(1).decode()
        
        for i in range(2, 15):
            qualifier = {'Channel' : ChannelStates[i-1]}
            value = ValueStateValues[match.group(i).decode()]
            self.WriteStatus('ChannelAudioMute', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Cable/SAT'  : '!1SLI01\r\n', 
            'Game'       : '!1SLI02\r\n', 
            'Aux'        : '!1SLI03\r\n', 
            'BD/DVD'     : '!1SLI10\r\n', 
            'Strm Box'   : '!1SLI11\r\n', 
            'TV'         : '!1SLI12\r\n', 
            'Phono'      : '!1SLI22\r\n', 
            'CD'         : '!1SLI23\r\n', 
            'FM'         : '!1SLI24\r\n', 
            'AM'         : '!1SLI25\r\n', 
            'Tuner'      : '!1SLI26\r\n', 
            'USB Front'  : '!1SLI29\r\n', 
            'Network'    : '!1SLI2B\r\n', 
            'USB Toggle' : '!1SLI2C\r\n', 
            'Bluetooth'  : '!1SLI2E\r\n', 
            'HDMI 5'     : '!1SLI55\r\n', 
            'HDMI 6'     : '!1SLI56\r\n'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!1SLIQSTN\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '01' : 'Cable/SAT', 
            '02' : 'Game', 
            '03' : 'Aux', 
            '10' : 'BD/DVD', 
            '11' : 'Strm Box', 
            '12' : 'TV', 
            '22' : 'Phono', 
            '23' : 'CD', 
            '24' : 'FM', 
            '25' : 'AM', 
            '26' : 'Tuner', 
            '29' : 'USB Front', 
            '2B' : 'Network', 
            '2E' : 'Bluetooth', 
            '55' : 'HDMI 5', 
            '56' : 'HDMI 6'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        ValueStateValues = {
            'Stereo'                     : '!1LMD00\r\n', 
            'Direct'                     : '!1LMD01\r\n', 
            'Film'                       : '!1LMD03\r\n', 
            'Action'                     : '!1LMD05\r\n', 
            'Musical'                    : '!1LMD06\r\n', 
            'Orchestra'                  : '!1LMD08\r\n', 
            'Unplugged'                  : '!1LMD09\r\n', 
            'Studio-Mix'                 : '!1LMD0A\r\n', 
            'TV Logic'                   : '!1LMD0B\r\n', 
            'All Ch Stereo'              : '!1LMD0C\r\n', 
            'Theater-Dimensional'        : '!1LMD0D\r\n', 
            'Enhanced 7/Enhance'         : '!1LMD0E\r\n', 
            'Mono'                       : '!1LMD0F\r\n', 
            'Pure Audio'                 : '!1LMD11\r\n', 
            'Full Mono'                  : '!1LMD13\r\n', 
            'Whole House Mode'           : '!1LMD1F\r\n', 
            'Straight Decode'            : '!1LMD40\r\n', 
            'Dolby Atmos/Dolby Surround' : '!1LMD80\r\n', 
            'DTS:X/Neural:X'             : '!1LMD82\r\n', 
            'Auto Surround'              : '!1LMDFF\r\n'
        }

        ListeningModeCmdString = ValueStateValues[value]
        self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)
    def UpdateListeningMode(self, value, qualifier):

        ListeningModeCmdString = '!1LMDQSTN\r\n'
        self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)

    def __MatchListeningMode(self, match, tag):

        ValueStateValues = {
            '00' : 'Stereo', 
            '01' : 'Direct', 
            '03' : 'Film', 
            '05' : 'Action', 
            '06' : 'Musical', 
            '08' : 'Orchestra', 
            '09' : 'Unplugged', 
            '0A' : 'Studio-Mix', 
            '0B' : 'TV Logic', 
            '0C' : 'All Ch Stereo', 
            '0D' : 'Theater-Dimensional', 
            '0E' : 'Enhanced 7/Enhance', 
            '0F' : 'Mono', 
            '11' : 'Pure Audio', 
            '13' : 'Full Mono', 
            '1F' : 'Whole House Mode', 
            '40' : 'Straight Decode', 
            '80' : 'Dolby Atmos/Dolby Surround', 
            '82' : 'DTS:X/Neural:X', 
            'FF' : 'Auto Surround'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ListeningMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'          : '!1OSDUP\r\n', 
            'Down'        : '!1OSDDOWN\r\n', 
            'Right'       : '!1OSDRIGHT\r\n', 
            'Left'        : '!1OSDLEFT\r\n', 
            'Enter'       : '!1OSDENTER\r\n', 
            'Exit'        : '!1OSDEXIT\r\n', 
            'Home'        : '!1OSDHOME\r\n', 
            'Quick Setup' : '!1OSDQUICK\r\n'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '!1PWR01\r\n', 
            'Off' : '!1PWR00\r\n'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):


        PowerCmdString = '!1PWRQSTN\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)
        
    def SetPreset(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 40:
            PresetCmdString = '!1PRS{0:02X}\r\n'.format(preset)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '!1MVL{0:02X}\r\n'.format(int(value*2))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '!1MVLQSTN\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)/2
        self.WriteStatus('Volume', value, None)

    def SetZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '!1ZMT01\r\n', 
            'Off' : '!1ZMT00\r\n'
        }

        Zone2AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)
    def UpdateZone2AudioMute(self, value, qualifier):

        Zone2AudioMuteCmdString = '!1ZMTQSTN\r\n'
        self.__UpdateHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def __MatchZone2AudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2AudioMute', value, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'Cable/SAT'  : '!1SLZ01\r\n', 
            'Game'       : '!1SLZ02\r\n', 
            'BD/DVD'     : '!1SLZ10\r\n', 
            'Strm Box'   : '!1SLZ11\r\n', 
            'TV'         : '!1SLZ12\r\n', 
            'Phono'      : '!1SLZ22\r\n', 
            'CD'         : '!1SLZ23\r\n', 
            'FM'         : '!1SLZ24\r\n', 
            'AM'         : '!1SLZ25\r\n', 
            'Tuner'      : '!1SLZ26\r\n', 
            'USB Front'  : '!1SLZ29\r\n', 
            'Network'    : '!1SLZ2B\r\n', 
            'USB Toggle' : '!1SLZ2C\r\n', 
            'Bluetooth'  : '!1SLZ2E\r\n'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)
    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = '!1SLZQSTN\r\n'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            '01' : 'Cable/SAT', 
            '02' : 'Game', 
            '10' : 'BD/DVD', 
            '11' : 'Strm Box', 
            '12' : 'TV', 
            '22' : 'Phono', 
            '23' : 'CD', 
            '24' : 'FM', 
            '25' : 'AM', 
            '26' : 'Tuner', 
            '29' : 'USB Front', 
            '2B' : 'Network', 
            '2C' : 'USB Toggle', 
            '2E' : 'Bluetooth'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On'  : '!1ZPW01\r\n', 
            'Off' : '!1ZPW00\r\n'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)
    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = '!1ZPWQSTN\r\n'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Preset(self, value, qualifier):

        preset = int(value)
        if 1 <= preset <= 40:
            Zone2PresetCmdString = '!1PRZ{0:02X}\r\n'.format(preset)
            self.__SetHelper('Zone2Preset', Zone2PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Preset')
    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone2VolumeCmdString = '!1ZVL{0:02X}\r\n'.format(int(value*2))
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')
    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = '!1ZVLQSTN\r\n'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1).decode(), 16)/2
        self.WriteStatus('Zone2Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
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
      
        self.ChannelAudioMuteValues = None
        self.lastChannelAudioMuteUpdate = 0
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

