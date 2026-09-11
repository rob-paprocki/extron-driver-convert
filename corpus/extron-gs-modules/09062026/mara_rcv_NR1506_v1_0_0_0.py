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
            'ChannelVolume': {'Parameters': ['Channel'], 'Status': {}},
            'Input': {'Status': {}},
            'MainZonePower': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'MenuControl': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OutputMute': {'Status': {}},
            'PanelLock': {'Status': {}},
            'Power': {'Status': {}},
            'RDSStationName': {'Status': {}},
            'RemoteLock': {'Status': {}},
            'SurroundMode': {'Status': {}},
            'TunerPreset': {'Status': {}},
            }

        self.__LastChannelUpdate = 0        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'CV(FL|FR|C|SW|SL|SR|SBL|SBR|SB) ([0-9]{2})\r'), self.__MatchChannelVolume, None)
            self.AddMatchString(re.compile(b'SI(CD|BD|TV|SAT/CBL|MPLAY|GAME|TUNER|SPOTIFY|SIRIUS|PANDORA|IRADIO|SERVER|FAVORITES|AUX1|NET|BT|USB/IPOD|USB|IPD|IRP|FVP)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ZM(ON|OFF)\r'), self.__MatchMainZonePower, None)
            self.AddMatchString(re.compile(b'MV([0-9]{2})\r'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'MNMEN (ON|OFF)\r'), self.__MatchMenuControl, None)
            self.AddMatchString(re.compile(b'MU(ON|OFF)\r'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'PW(ON|STANDBY)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'TFANNAME([\s\S]+)\r'), self.__MatchRDSStationName, None)
            self.AddMatchString(re.compile(b'MS([\s\S]+)\r'), self.__MatchSurroundMode, None)
            self.AddMatchString(re.compile(b'TPANMEM([0-9]{2})\r'), self.__MatchTunerPreset, None)  # unsolicited response

    def SetChannelVolume(self, value, qualifier):

        ChannelStates = {
            'Front Left': 'CVFL',
            'Front Right': 'CVFR',
            'Center': 'CVC',
            'Subwoofer': 'CVSW',
            'Surround Left': 'CVSL',
            'Surround Right': 'CVSR',
            'Surround Back Left': 'CVSBL',
            'Surround Back Right': 'CVSBR',
            'Surround Back': 'CVSB'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
            }

        channel = qualifier['Channel']

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel in ChannelStates:
            ChannelVolumeCmdString = '{0} {1:02}\r'.format(ChannelStates[channel], value + 50)
            self.__SetHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelVolume')

    def UpdateChannelVolume(self, value, qualifier):
        
        ChannelVolumeCmdString = 'CV?\r'
        self.__UpdateHelper('ChannelVolume', ChannelVolumeCmdString, value, qualifier)        

    def __MatchChannelVolume(self, match, tag):

        ChannelStates = {
            'FL': 'Front Left',
            'FR': 'Front Right',
            'C': 'Center',
            'SW': 'Subwoofer',
            'SL': 'Surround Left',
            'SR': 'Surround Right',
            'SBL': 'Surround Back Left',
            'SBR': 'Surround Back Right',
            'SB': 'Surround Back'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = int(match.group(2).decode()) - 50
        self.WriteStatus('ChannelVolume', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'CD': 'SICD\r',
            'BD': 'SIBD\r',
            'TV': 'SITV\r',
            'SAT/CBL': 'SISAT/CBL\r',
            'Media Player': 'SIMPLAY\r',
            'Game': 'SIGAME\r',
            'Tuner': 'SITUNER\r',
            'Spotify': 'SISPOTIFY\r',
            'Sirius XM': 'SISIRIUS\r',
            'Pandora': 'SIPANDORA\r',
            'Internet Radio': 'SIIRADIO\r',
            'Server': 'SISERVER\r',
            'Favorites': 'SIFAVORITES\r',
            'AUX 1': 'SIAUX1\r',
            'NET': 'SINET\r',
            'Bluetooth': 'SIBT\r',
            'USB/iPod': 'SIUSB/IPOD\r',
            'USB': 'SIUSB\r',
            'IPD': 'SIIPD\r',
            'IRP': 'SIIRP\r',
            'FVP': 'SIFVP\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SI?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'CD': 'CD',
            'BD': 'BD',
            'TV': 'TV',
            'SAT/CBL': 'SAT/CBL',
            'MPLAY': 'Media Player',
            'GAME': 'Game',
            'TUNER': 'Tuner',
            'SPOTIFY': 'Spotify',
            'SIRIUS': 'Sirius XM',
            'PANDORA': 'Pandora',
            'IRADIO': 'Internet Radio',
            'SERVER': 'Server',
            'FAVORITES': 'Favorites',
            'AUX1': 'AUX 1',
            'NET': 'NET',
            'BT': 'Bluetooth',
            'USB/IPOD': 'USB/iPod',
            'USB': 'USB',
            'IPD': 'IPD',
            'IRP': 'IRP',
            'FVP': 'FVP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMainZonePower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ZMON\r',
            'Off': 'ZMOFF\r'
        }

        MainZonePowerCmdString = ValueStateValues[value]
        self.__SetHelper('MainZonePower', MainZonePowerCmdString, value, qualifier)

    def UpdateMainZonePower(self, value, qualifier):

        MainZonePowerCmdString = 'ZM?\r'
        self.__UpdateHelper('MainZonePower', MainZonePowerCmdString, value, qualifier)

    def __MatchMainZonePower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MainZonePower', value, None)

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 18
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = 'MV{0:02}\r'.format(value + 80)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'MV?\r'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = int(match.group(1).decode()) - 80
        self.WriteStatus('MasterVolume', value, None)

    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'On': 'MNMEN ON\r',
            'Off': 'MNMEN OFF\r'
        }

        MenuControlCmdString = ValueStateValues[value]
        self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)

    def UpdateMenuControl(self, value, qualifier):

        MenuControlCmdString = 'MNMEN?\r'
        self.__UpdateHelper('MenuControl', MenuControlCmdString, value, qualifier)

    def __MatchMenuControl(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MenuControl', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'MNCUP\r',
            'Down': 'MNCDN\r',
            'Left': 'MNCLT\r',
            'Right': 'MNCRT\r',
            'Enter': 'MNENT\r',
            'Return': 'MNRTN\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUON\r',
            'Off': 'MUOFF\r'
        }

        OutputMuteCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        OutputMuteCmdString = 'MU?\r'
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputMute', value, None)

    def SetPanelLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYPANEL LOCK ON\r',
            'Off': 'SYPANEL LOCK OFF\r',
            'On except Master Volume': 'SYPANEL+V LOCK ON\r'
        }

        PanelLockCmdString = ValueStateValues[value]
        self.__SetHelper('PanelLock', PanelLockCmdString, value, qualifier)

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

    def UpdateRDSStationName(self, value, qualifier):

        RDSStationNameCmdString = 'ANNAME?\r'
        self.__UpdateHelper('RDSStationName', RDSStationNameCmdString, value, qualifier)

    def __MatchRDSStationName(self, match, tag):

        value = match.group(1).decode()
        if value == ' ':
            self.WriteStatus('RDSStationName', 'Null', None)
        else:
            self.WriteStatus('RDSStationName', value, None)

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'SYREMOTE LOCK ON\r',
            'Off': 'SYREMOTE LOCK OFF\r'
        }

        RemoteLockCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def SetSurroundMode(self, value, qualifier):

        ValueStateValues = {
            'Movie': 'MSMOVIE\r',
            'Music': 'MSMUSIC\r',
            'Game': 'MSGAME\r',
            'Direct': 'MSDIRECT\r',
            'Pure Direct': 'MSPURE DIRECT\r',
            'Stereo': 'MSSTEREO\r',
            'Auto': 'MSAUTO\r',
            'Dolby PL2 C': 'MSDOLBY PL2 C\r',
            'Dolby PL2 M': 'MSDOLBY PL2 M\r',
            'Dolby PL2 G': 'MSDOLBY PL2 G\r',
            'Dolby Digital': 'MSDOLBY DIGITAL\r',
            'Dolby D+': 'MSDOLBY D+\r',
            'Dolby HD': 'MSDOLBY HD\r',
            'DTS NEO:6 C': 'MSDTS NEO:6 C\r',
            'DTS NEO:6 M': 'MSDTS NEO:6 C\r',
            'DTS Surround': 'MSDTS SURROUND\r',
            'DTS 96/24': 'MSDTS96/24\r',
            'DTS HD': 'MSDTS HD\r',
            'DTS HD MSTR': 'MSDTS HD MSTR\r',
            'DTS Express': 'MSDTS EXPRESS\r',
            'Multi CH IN': 'MSMULTI CH IN\r',
            'Multi CH Stereo': 'MSMCH STEREO\r',
            'Virtual': 'MSVIRTUAL\r',
        }

        SurroundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def UpdateSurroundMode(self, value, qualifier):

        SurroundModeCmdString = 'MS?\r'
        self.__UpdateHelper('SurroundMode', SurroundModeCmdString, value, qualifier)

    def __MatchSurroundMode(self, match, tag):

        ValueStateValues = {
            'MOVIE': 'Movie',
            'MUSIC': 'Music',
            'GAME': 'Game',
            'DIRECT': 'Direct',
            'PURE DIRECT': 'Pure Direct',
            'STEREO': 'Stereo',
            'AUTO': 'Auto',
            'DOLBY PL2 C': 'Dolby PL2 C',
            'DOLBY PL2 M': 'Dolby PL2 M',
            'DOLBY PL2 G': 'Dolby PL2 G',
            'DOLBY DIGITAL': 'Dolby Digital',
            'DOLBY D+': 'Dolby D+',
            'DOLBY HD': 'Dolby HD',
            'DTS NEO:6 C': 'DTS NEO:6 C',
            'DTS NEO:6 M': 'DTS NEO:6 M',
            'DTS SURROUND': 'DTS Surround',
            'DTS96/24': 'DTS 96/24',
            'DTS HD': 'DTS HD',
            'DTS HD MSTR': 'DTS HD MSTR',
            'DTS EXPRESS': 'DTS Express',
            'MULTI CH IN': 'Multi CH IN',
            'MCH STEREO': 'Multi CH Stereo',
            'VIRTUAL': 'Virtual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SurroundMode', value, None)

    def SetTunerPreset(self, value, qualifier):

        if 1 <= int(value) <= 56:
            TunerPresetCmdString = 'TPANMEM{}\r'.format(value.zfill(2))
            self.__SetHelper('TunerPreset', TunerPresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTunerPreset')

    def __MatchTunerPreset(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 56:
            self.WriteStatus('TunerPreset', str(value), None)

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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.__LastChannelUpdate = 0       

    
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
