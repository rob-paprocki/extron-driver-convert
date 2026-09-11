from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Bass': {'Status': {}},
            'Input': {'Status': {}},
            'MainZonePower': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OutputMute': {'Status': {}},
            'PanelLock': {'Status': {}},
            'Power': {'Status': {}},
            'RecSelectMode': {'Status': {}},
            'Remote': {'Status': {}},
            'Resolution': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'Treble': {'Status': {}},
            'VideoSelectMode': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2Mode': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'VSASP(NRM|FUL)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'PSBAS ([0-9]{2})\r'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'SI(PHONO|CD|TUNER|DVD|TV/CBL|VCR|DVR|V.AUX|XM|IPOD|AUX)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
            self.AddMatchString(re.compile(b'(MU|Z2MU)(ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'SR(PHONO|CD|TUNER|DVD|TV/CBL|VCR|DVR|V.AUX|XM|IPOD|AUX)\r'), self.__MatchRecSelectMode, None)
            self.AddMatchString(re.compile(b'VSSC(48P|10I|72P|10P|AUTO)\r'), self.__MatchResolution, None)
            self.AddMatchString(re.compile(b'MS(.*)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'PSTRE ([0-9]{2})\r'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'SV(DVD|TV/CBL|VCR|DVR|V.AUX|SOURCE)\r'), self.__MatchVideoSelectMode, None)
            self.AddMatchString(re.compile(b'MV([0-9]{2})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Z2(PHONO|CD|TUNER|DVD|TV/CBL|VCR|DVR|V.AUX|XM|IPOD|AUX)\r'), self.__MatchZone2Mode, None)
            self.AddMatchString(re.compile(b'Z2(ON|OFF)\r'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'Z2([0-9]{2})\r'), self.__MatchZone2Volume, None)

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Normal': 'VSASPNRM\r',
            'Full': 'VSASPFUL\r',
            }
        CmdString = States[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CmdString = 'VSASP?\r'
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        Status = {
            'NRM': 'Normal',
            'FUL': 'Full',
           }
        value = Status[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetBass(self, value, qualifier):

        if -6 <= int(value) <= 6:
            temp = value + 50
            CmdString = 'PSBAS {0}\r'.format(temp)
            self.__SetHelper('Bass', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        CmdString = 'PSBAS ?\r'
        self.__UpdateHelper('Bass', CmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = int(match.group(1).decode())
        if 44 <= value <= 56:
            value = value - 50
            self.WriteStatus('Bass', value, None)

    def SetInput(self, value, qualifier):

        States = {
            'Phono': 'SIPHONO\r',
            'CD': 'SICD\r',
            'Tuner': 'SITUNER\r',
            'DVD': 'SIDVD\r',
            'TV/CBL': 'SITV/CBL\r',
            'VCR': 'SIVCR\r',
            'DVR': 'SIDVR\r',
            'V Aux': 'SIV.AUX\r',
            'XM': 'SIXM\r',
            'IPOD': 'SIIPOD\r',
            'Aux': 'SIAUX\r',
            }
        CmdString = States[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CmdString = 'SI?\r'
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        Status = {
            'PHONO': 'Phono',
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'TV/CBL': 'TV/CBL',
            'VCR': 'VCR',
            'DVR': 'DVR',
            'V.AUX': 'V Aux',
            'XM': 'XM',
            'IPOD': 'IPOD',
            'AUX': 'Aux',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZonePower(self, value, qualifier):

        States = {
            'On': 'ZMON\r',
            'Off': 'ZMOFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('MainZonePower', CmdString, value, qualifier)

    def UpdateMainZonePower(self, value, qualifier):

        CmdString = 'ZM?\r'
        self.__UpdateHelper('MainZonePower', CmdString, value, qualifier)

    def __MatchMainZonePower(self, match, tag):

        Status = {
            'ON': 'On',
            'OFF': 'Off',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('MainZonePower', value, None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': 'MNCUP\r',
            'Down': 'MNCDN\r',
            'Left': 'MNCLT\r',
            'Right': 'MNCRT\r',
            'Enter': 'MNENT\r',
            'Return': 'MNRTN\r',
            'Menu On': 'MNMEN ON\r',
            'Menu Off': 'MNMEN OFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetOutputMute(self, value, qualifier):

        States = {
            'On': 'MUON\r',
            'Off': 'MUOFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('OutputMute', CmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        CmdString = 'MU?\r'
        self.__UpdateHelper('OutputMute', CmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        Status = {
            'ON': 'On',
            'OFF': 'Off',
           }

        if match.group(1).decode() == 'MU':
            value = Status[match.group(2).decode()]
            self.WriteStatus('OutputMute', value, None)

        elif match.group(1).decode() == 'Z2MU':
            value = Status[match.group(2).decode()]
            self.WriteStatus('Zone2Mute', value, None)

    def SetPanelLock(self, value, qualifier):

        States = {
            'Mode 1': 'SYPANEL LOCK ON\r',
            'Mode 2': 'SYPANEL+V LOCK ON\r',
            'Off': 'SYPANEL LOCK OFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('PanelLock', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': 'PWON\r',
            'Standby': 'PWSTANDBY\r',
            }
        CmdString = States[value]
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = 'PW?\r'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        Status = {
            'ON': 'On',
            'STANDBY': 'Standby',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRecSelectMode(self, value, qualifier):

        States = {
            'Phono': 'SRPHONO\r',
            'CD': 'SRCD\r',
            'Tuner': 'SRTUNER\r',
            'DVD': 'SRDVD\r',
            'TV/CBL': 'SRTV/CBL\r',
            'VCR': 'SRVCR\r',
            'DVR': 'SRDVR\r',
            'V Aux': 'SRV.AUX\r',
            'XM': 'SRXM\r',
            'IPOD': 'SRIPOD\r',
            'Aux': 'SRAUX\r',
            'Cancel': 'SRSOURCE\r',
            }
        CmdString = States[value]
        if value not in ['Cancel']:
            self.__SetHelper('RecSelectMode', CmdString, value, qualifier)

    def UpdateRecSelectMode(self, value, qualifier):

        CmdString = 'SR?\r'
        self.__UpdateHelper('RecSelectMode', CmdString, value, qualifier)

    def __MatchRecSelectMode(self, match, tag):

        Status = {
            'PHONO': 'Phono',
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'TV/CBL': 'TV/CBL',
            'VCR': 'VCR',
            'DVR': 'DVR',
            'V.AUX': 'V Aux',
            'XM': 'XM',
            'IPOD': 'IPOD',
            'AUX': 'Aux',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('RecSelectMode', value, None)

    def SetRemote(self, value, qualifier):

        States = {
            'Lock': 'SYREMOTE LOCK ON\r',
            'Unlock': 'SYREMOTE LOCK OFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('Remote', CmdString, value, qualifier)

    def SetResolution(self, value, qualifier):

        States = {
            '480p/576p': 'VSSC48P\r',
            '1080i': 'VSSC10I\r',
            '720p': 'VSSC72P\r',
            '1080p': 'VSSC10P\r',
            'Auto': 'VSSCAUTO\r',
            }
        CmdString = States[value]
        self.__SetHelper('Resolution', CmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):

        CmdString = 'VSSC?\r'
        self.__UpdateHelper('Resolution', CmdString, value, qualifier)

    def __MatchResolution(self, match, tag):

        Status = {
            '48P': '480p/576p',
            '10I': '1080i',
            '72P': '720p',
            '10P': '1080p',
            'AUTO': 'Auto',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('Resolution', value, None)

    def SetSurroundMode(self, value, qualifier):

        States = {
            'Direct': 'MSDIRECT\r',
            'Pure Direct': 'MSPURE DIRECT\r',
            'Stereo': 'MSSTEREO\r',
            'Standard': 'MSSTANDARD\r',
            'Dolby Digital': 'MSDOLBY DIGITAL\r',
            'DTS Surround': 'MSDTS SURROUND\r',
            'Neural': 'MSNEURAL\r',
            '7ch Stereo': 'MS7CH STEREO\r',
            'Rock Arena': 'MSROCK ARENA\r',
            'Jazz Club': 'MSJAZZ CLUB\r',
            'Mono Movie': 'MSMONO MOVIE\r',
            'Matrix': 'MSMATRIX\r',
            'Video Game': 'MSVIDEO GAME\r',
            'Virtual': 'MSVIRTUAL\r',
            }
        CmdString = States[value]
        self.__SetHelper('SurroundMode', CmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        CmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', CmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        Status = {
            'DIRECT': 'Direct',
            'PURE DIRECT': 'Pure Direct',
            'STEREO': 'Stereo',
            'STANDARD': 'Standard',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DTS SURROUND': 'DTS Surround',
            'NEURAL': 'Neural',
            '7CH STEREO': '7ch Stereo',
            'ROCK ARENA': 'Rock Arena',
            'JAZZ CLUB': 'Jazz Club',
            'MONO MOVIE': 'Mono Movie',
            'VIDEO GAME': 'Video Game',
            'MATRIX': 'Matrix',
            'VIRTUAL': 'Virtual',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetTreble(self, value, qualifier):

        if -6 <= int(value) <= 6:
            temp = value + 50
            CmdString = 'PSTRE {0}\r'.format(temp)
            self.__SetHelper('Treble', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        CmdString = 'PSTRE ?\r'
        self.__UpdateHelper('Treble', CmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = int(match.group(1).decode())
        if 44 <= value <= 56:
            value = value - 50
            self.WriteStatus('Treble', value, None)

    def SetVideoSelectMode(self, value, qualifier):

        States = {
            'DVD': 'SVDVD\r',
            'TV/CBL': 'SVTV/CBL\r',
            'VCR': 'SVVCR\r',
            'DVR': 'SVDVR\r',
            'V Aux': 'SVV.AUX\r',
            'Cancel': 'SVSOURCE\r',
            }
        CmdString = States[value]
        if value != 'Cancel':
            self.__SetHelper('VideoSelectMode', CmdString, value, qualifier)

    def UpdateVideoSelectMode(self, value, qualifier):

        CmdString = 'SV?\r'
        self.__UpdateHelper('VideoSelectMode', CmdString, value, qualifier)

    def __MatchVideoSelectMode(self, match, tag):

        Status = {
             'DVD': 'DVD',
             'TV/CBL': 'TV/CBL',
             'VCR': 'VCR',
             'DVR': 'DVR',
             'V.AUX': 'V Aux',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('VideoSelectMode', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= int(value) < 99:
            temp = str(value).zfill(2)
            CmdString = 'MV{0}\r'.format(temp)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CmdString = 'MV?\r'
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('Volume', value, None)

    def SetZone2Mode(self, value, qualifier):

        States = {
            'Phono': 'Z2PHONO\r',
            'CD': 'Z2CD\r',
            'Tuner': 'Z2TUNER\r',
            'DVD': 'Z2DVD\r',
            'TV/CBL': 'Z2TV/CBL\r',
            'VCR': 'Z2VCR\r',
            'DVR': 'Z2DVR\r',
            'V Aux': 'Z2V.AUX\r',
            'XM': 'Z2XM\r',
            'IPOD': 'Z2IPOD\r',
            'Aux': 'Z2AUX\r',
            'Cancel': 'Z2SOURCE\r',
            }
        CmdString = States[value]
        if value != 'Cancel':
            self.__SetHelper('Zone2Mode', CmdString, value, qualifier)

    def UpdateZone2Mode(self, value, qualifier):

        CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Mode', CmdString, value, qualifier)

    def __MatchZone2Mode(self, match, tag):

        Status = {
            'PHONO': 'Phono',
            'CD': 'CD',
            'TUNER': 'Tuner',
            'DVD': 'DVD',
            'TV/CBL': 'TV/CBL',
            'VCR': 'VCR',
            'DVR': 'DVR',
            'V.AUX': 'V Aux',
            'XM': 'XM',
            'IPOD': 'IPOD',
            'AUX': 'Aux',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('Zone2Mode', value, None)

    def SetZone2Mute(self, value, qualifier):

        States = {
            'On': 'Z2MUON\r',
            'Off': 'Z2MUOFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('Zone2Mute', CmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):

        CmdString = 'Z2MU?\r'
        self.__UpdateHelper('Zone2Mute', CmdString, value, qualifier)

    def SetZone2Power(self, value, qualifier):

        States = {
            'On': 'Z2ON\r',
            'Off': 'Z2OFF\r',
            }
        CmdString = States[value]
        self.__SetHelper('Zone2Power', CmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Power', CmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        Status = {
            'ON': 'On',
            'OFF': 'Off',
           }

        value = Status[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):

        if 10 <= int(value) < 99:
            CmdString = 'Z2{0}\r'.format(value)
            self.__SetHelper('Zone2Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        CmdString = 'Z2?\r'
        self.__UpdateHelper('Zone2Volume', CmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = int(match.group(1))
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

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
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
