from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'Bass': {'Status': {}},
            'DigitalInput': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MainZone': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'OutputMute': {'Status': {}},
            'Power': {'Status': {}},
            'SDStatus': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Treble': {'Status': {}},
            'VideoSelectMode': {'Status': {}},
            'Zone2': {'Status': {}},
            'Zone2AudioMute': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PSBAS([0-9]{2})'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'DC(AUTO|PCM|DTS)'), self.__MatchDigitalInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)'), self.__MatchMainZone, None)
            self.AddMatchString(re.compile(b'MV([0-9]{2})'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'SD(AUTO|HDMI|DIGITAL|ANALOG)'), self.__MatchSDStatus, None)
            self.AddMatchString(re.compile(b'MS(MOVIE|MUSIC|GAME|DIRECT|PURE DIRECT|STEREO|STANDARD|DOLBY DIGITAL|DTS SURROUND|MCH STEREO|ROCK ARENA|JAZZ CLUB|CLASSIC CONCERT|MONO MOVIE|MATRIX|VIDEO GAME|VIRTUAL)'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'PSTRE([0-9]{2})'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)'), self.__MatchZone2, None)
            self.AddMatchString(re.compile(b'Z2(MUON|MUOFF)'), self.__MatchZone2AudioMute, None)
            self.AddMatchString(re.compile(b'Z2(CD|DVD|BD|SAT\/CBL|DOCK|V.AUX|IPOD|NET\/USB|SERVER|FAVORITES|USB\/IPOD)'), self.__MatchZone2Input, None)
            self.AddMatchString(re.compile(b'Z2([0-9]{2})'), self.__MatchZone2Volume, None)

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = str(value).zfill(2)
            BassCmdString = 'PSBAS' + volume + '\r'
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = 'PSBAS?\r'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Bass', value, None)

    def SetDigitalInput(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'DCAUTO\r',
            'PCM': 'DCPCM\r',
            'DTS': 'DCDTS\r'
        }

        DigitalInputCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalInput', DigitalInputCmdString, value, qualifier)

    def UpdateDigitalInput(self, value, qualifier):

        DigitalInputCmdString = 'DC?\r'
        self.__UpdateHelper('DigitalInput', DigitalInputCmdString, value, qualifier)

    def __MatchDigitalInput(self, match, tag):

        ValueStateValues = {
            'AUTO': 'Auto',
            'PCM': 'PCM',
            'DTS': 'DTS'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DigitalInput', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYREMOTE LOCK ON\r',
            'Off': 'SYREMOTE LOCK OFF\r'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'CD': 'SICD\r',
            'DVD': 'SIDVD\r',
            'BD': 'SIBD\r',
            'TV': 'SITV\r',
            'SAT': 'SISAT/CBL\r',
            'Game': 'SIGAME\r',
            'Game 2': 'SIGAME2\r',
            'Dock': 'SIDOCK\r',
            'V.AUX': 'SIV.AUX\r',
            'IPOD': 'SIIPOD\r',
            'Network/USB': 'SINET/USB\r',
            'Server': 'SISERVER\r',
            'Favorites': 'SIFAVORITES\r',
            'USB/IPOD': 'SIUSB/IPOD\r',
            'USB': 'SIUSB\r',
            'IPD': 'SIIPD\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            'CD': 'CD',
            'DVD': 'DVD',
            'BD': 'BD',
            'TV': 'TV',
            'SAT/CBL': 'SAT',
            'GAME': 'Game',
            'GAME2': 'Game 2',
            'DOCK': 'Dock',
            'V.AUX': 'V.AUX',
            'IPOD': 'IPOD',
            'NET/USB': 'Network/USB',
            'SERVER': 'Server',
            'FAVORITES': 'Favorites',
            'USB/IPOD': 'USB/IPOD',
            'USB': 'USB',
            'IPD': 'IPD'
        }

        InputCmdString = 'SI?\r'
        res = self.__UpdateHelperSYNC('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid/Unexpected response from device for Input status')

    def SetMainZone(self, value, qualifier):

        ValueStateValues = {
            'On': 'ZMON\r',
            'Off': 'ZMOFF\r'
        }

        MainZoneCmdString = ValueStateValues[value]
        self.__SetHelper('MainZone', MainZoneCmdString, value, qualifier)

    def UpdateMainZone(self, value, qualifier):

        MainZoneCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZone', MainZoneCmdString, value, qualifier)

    def __MatchMainZone(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZone', value, None)

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = str(value).zfill(2)
            MasterVolumeCmdString = 'MV' + volume + '\r'
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'MV?\r'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('MasterVolume', value, None)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUON\r',
            'Off': 'MUOFF\r'
        }

        OutputMuteCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        MuteState = {
            'ON': 'On',
            'OFF': 'Off'
        }

        OutputMuteCmdString = 'MU?\r'
        res = self.__UpdateHelperSYNC('OutputMute', OutputMuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteState[res[2:-1]]
                self.WriteStatus('OutputMute', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid/Unexpected response from device for OutputMute status')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputMute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PWON\r',
            'Off': 'PWSTANDBY\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PW?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'STANDBY': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSDStatus(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'SDAUTO\r',
            'HDMI': 'SDHDMI\r',
            'Digital': 'SDDIGITAL\r',
            'Analog': 'SDANALOG\r'
        }

        SDStatusCmdString = ValueStateValues[value]
        self.__SetHelper('SDStatus', SDStatusCmdString, value, qualifier)

    def UpdateSDStatus(self, value, qualifier):

        SDStatusCmdString = 'SD?\r'
        self.__UpdateHelper('SDStatus', SDStatusCmdString, value, qualifier)

    def __MatchSDStatus(self, match, tag):

        ValueStateValues = {
            'AUTO': 'Auto',
            'HDMI': 'HDMI',
            'DIGITAL': 'Digital',
            'ANALOG': 'Analog'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SDStatus', value, None)

    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Movie': 'MSMOVIE\r',
            'Musical': 'MSMUSIC\r',
            'GAME': 'MSGAME\r',
            'Direct': 'MSDIRECT\r',
            'Pure Direct': 'MSPURE DIRECT\r',
            'Stereo': 'MSSTEREO\r',
            'Standard': 'MSSTANDARD\r',
            'Dolby Digital': 'MSDOLBY DIGITAL\r',
            'DTS Surround': 'MSDTS SURROUND\r',
            'Mch Stereo': 'MSMCH STEREO\r',
            'Rock Arena': 'MSROCK ARENA\r',
            'Jazz Club': 'MSJAZZ CLUB\r',
            'Classic Concert': 'MSCLASSIC CONCERT\r',
            'Mono': 'MSMONO MOVIE\r',
            'Matrix': 'MSMATRIX\r',
            'Video Game': 'MSVIDEO GAME\r',
            'Virtual': 'MSVIRTUAL\r'
        }

        SurroundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'MOVIE': 'Movie',
            'MUSIC': 'Musical',
            'GAME': 'GAME',
            'DIRECT': 'Direct',
            'PURE DIRECT': 'Pure Direct',
            'STEREO': 'Stereo',
            'STANDARD': 'Standard',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DTS SURROUND': 'DTS Surround',
            'MCH STEREO': 'Mch Stereo',
            'ROCK ARENA': 'Rock Arena',
            'JAZZ CLUB': 'Jazz Club',
            'CLASSIC CONCERT': 'Classic Concert',
            'MONO MOVIE': 'Mono',
            'MATRIX': 'Matrix',
            'VIDEO GAME': 'Video Game',
            'VIRTUAL': 'Virtual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = str(value).zfill(2)
            TrebleCmdString = 'PSTRE' + volume + '\r'
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = 'PSTRE?\r'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Treble', value, None)

    def SetVideoSelectMode(self, value, qualifier):

        ValueStateValues = {
            'DVD': 'SVDVD\r',
            'BD': 'SVBD\r',
            'TV': 'SVTV\r',
            'SAT': 'SVSAT/CBL\r',
            'Game': 'SVGAME\r',
            'Game 2': 'SVGAME2\r',
            'Dock': 'SVDOCK\r',
            'V.AUX': 'SVV.AUX\r'
        }

        VideoSelectModeCmdString = ValueStateValues[value]
        self.__SetHelper('VideoSelectMode', VideoSelectModeCmdString, value, qualifier)

    def UpdateVideoSelectMode(self, value, qualifier):

        VidSelState = {
            'DVD': 'DVD',
            'BD': 'BD',
            'TV': 'TV',
            'SAT/CBL': 'SAT',
            'GAME': 'Game',
            'GAME2': 'Game 2',
            'DOCK': 'Dock',
            'V.AUX': 'V.AUX'
        }

        VideoSelectModeCmdString = 'SV?\r'
        res = self.__UpdateHelperSYNC('VideoSelectMode', VideoSelectModeCmdString, value, qualifier)
        if res:
            try:
                value = VidSelState[res[2:-1]]
                self.WriteStatus('VideoSelectMode', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid/Unexpected response from device for VideoSelectMode status')

    def SetZone2(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z2ON\r',
            'Off': 'Z2OFF\r'
        }

        Zone2CmdString = ValueStateValues[value]
        self.__SetHelper('Zone2', Zone2CmdString, value, qualifier)

    def UpdateZone2(self, value, qualifier):

        Zone2CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2', Zone2CmdString, value, qualifier)

    def __MatchZone2(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2', value, None)

    def SetZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Z2MUON\r',
            'Off': 'Z2MUOFF\r'
        }

        Zone2AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def UpdateZone2AudioMute(self, value, qualifier):

        Zone2AudioMuteCmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def __MatchZone2AudioMute(self, match, tag):

        ValueStateValues = {
            'MUON': 'On',
            'MUOFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2AudioMute', value, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'CD': 'Z2CD\r',
            'DVD': 'Z2DVD\r',
            'BD': 'Z2BD\r',
            'SAT': 'Z2SAT/CBL\r',
            'Dock': 'Z2DOCK\r',
            'V.AUX': 'Z2V.AUX\r',
            'IPOD': 'Z2IPOD\r',
            'Network/USB': 'Z2NET/USB\r',
            'Server': 'Z2SERVER\r',
            'Favorites': 'Z2FAVORITES\r',
            'USB/IPOD': 'Z2USB/IPOD\r'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        Zone2InputCmdString = 'Z2?'
        self.__UpdateHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def __MatchZone2Input(self, match, tag):

        ValueStateValues = {
            'CD': 'CD',
            'DVD': 'DVD',
            'BD': 'BD',
            'SAT/CBL': 'SAT',
            'DOCK': 'Dock',
            'V.AUX': 'V.AUX',
            'IPOD': 'IPOD',
            'NET/USB': 'Network/USB',
            'SERVER': 'Server',
            'FAVORITES': 'Favorites',
            'USB/IPOD': 'USB/IPOD'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Input', value, None)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = str(value).zfill(2)
            Zone2VolumeCmdString = 'Z2' + volume + '\r'
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = 'Z2?'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1).decode())
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

    def __UpdateHelperSYNC(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()


            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return res.decode()

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

