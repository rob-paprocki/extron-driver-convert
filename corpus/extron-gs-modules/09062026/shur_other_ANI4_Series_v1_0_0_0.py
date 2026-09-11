from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogAudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioGainLevel': {'Parameters': ['Channel'], 'Status': {}},
            'AudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'ChannelName': {'Parameters': ['Channel'], 'Status': {}},
            'DigitalAudioGain': {'Parameters': ['Channel'], 'Status': {}},
            'FlashLights': {'Status': {}},
            'LEDBrightness': {'Status': {}},
            'MicLogicLEDIn': {'Parameters': ['Channel'], 'Status': {}},
            'MicLogicSwitchOutStatus': {'Parameters': ['Channel'], 'Status': {}},
            'PhantomPower': {'Parameters': ['Channel'], 'Status': {}},
            'Preset': {'Status': {}},
            'SigClip': {'Parameters': ['Channel'], 'Status': {}},
            'UserDefinedString': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP ([1-4]) AUDIO_GAIN (\d\d) >'), self.__MatchAnalogAudioGain, None)
            self.AddMatchString(re.compile(b'< REP ([1-4]) AUDIO_OUT_LVL_SWITCH (LINE|AUX|MIC)_LVL >'), self.__MatchAudioGainLevel, None)
            self.AddMatchString(re.compile(b'< REP ([0-4]) AUDIO_MUTE (ON|OFF) >'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'< REP ([0-4]) CHAN_NAME \{(.{31})\} >'), self.__MatchChannelName, None)
            self.AddMatchString(re.compile(b'< REP ([1-4]) AUDIO_GAIN_HI_RES (\d{4}) >'), self.__MatchDigitalAudioGain, None)
            self.AddMatchString(re.compile(b'< REP LED_BRIGHTNESS ([012]) >'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'< REP ([0-4]) CHAN_LED_IN_STATE (ON|OFF) >'), self.__MatchMicLogicLEDIn, None)
            self.AddMatchString(re.compile(b'< REP ([0-4]) HW_GATING_LOGIC (ON|OFF) >'), self.__MatchMicLogicSwitchOutStatus, None)
            self.AddMatchString(re.compile(b'< REP ([1-4]) PHANTOM_PWR_ENABLE (ON|OFF) >'), self.__MatchPhantomPower, None)
            self.AddMatchString(re.compile(b'< REP PRESET (\d\d) >'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'< REP ([0-4]) LED_COLOR_SIG_CLIP (OFF|GREEN|AMBER|RED) >'), self.__MatchSigClip, None)

    def SetAnalogAudioGain(self, value, qualifier):
        Channel = qualifier['Channel']
        if (1 <= int(Channel) <= 4) and (0 <= value <= 51):
            CmdString = '< SET {0} AUDIO_GAIN {1:02d} >'.format(Channel, value)
            self.__SetHelper('AnalogAudioGain', CmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetAnalogAudioGain')

    def UpdateAnalogAudioGain(self, value, qualifier):
        Channel = qualifier['Channel']
        if 1 <= int(Channel) <= 4:
            CmdString = '< GET {} AUDIO_GAIN >'.format(Channel)
            self.__UpdateHelper('AnalogAudioGain', CmdString, value, qualifier)

    def __MatchAnalogAudioGain(self, match, tag):
        Channel = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('AnalogAudioGain', value, {'Channel': Channel})

    def SetAudioGain(self, value, qualifier):
        Channel = qualifier['Channel']
        if (1 <= int(Channel) <= 4) and (0 <= value <= 140):
            CmdString = '< SET {0} AUDIO_GAIN_HI_RES {1:04d} >'.format(Channel, int(value * 10))
            self.__SetHelper('AudioGain', CmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):
        Channel = qualifier['Channel']
        if 1 <= int(Channel) <= 4:
            CmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(Channel)
            self.__UpdateHelper('AudioGain', CmdString, value, qualifier)

    def __MatchAudioGain(self, match, tag):
        Channel = match.group(1).decode()
        value = int(match.group(2).decode()) / 10
        if 0 <= value <= 140:
            self.WriteStatus('AudioGain', value, {'Channel': Channel})

    def SetAudioGainLevel(self, value, qualifier):
        Channel = qualifier['Channel']

        Value = {
            'Line Level': 'LINE',
            'Aux Level': 'AUX',
            'Mic Level': 'MIC'
        }[value]

        if 1 <= int(Channel) <= 4:
            CmdString = '< SET {} AUDIO_OUT_LVL_SWITCH {}_LVL >'.format(Channel, Value)
            self.__SetHelper('AudioGainLevel', CmdString, value, qualifier)

    def UpdateAudioGainLevel(self, value, qualifier):
        Channel = qualifier['Channel']
        if 1 <= int(Channel) <= 4:
            CmdString = '< GET {} AUDIO_OUT_LVL_SWITCH >'.format(Channel)
            self.__UpdateHelper('AudioGainLevel', CmdString, value, qualifier)

    def __MatchAudioGainLevel(self, match, tag):

        Channel = match.group(1).decode()

        Level = {
            'LINE': 'Line Level',
            'AUX': 'Aux Level',
            'MIC': 'Mic Level'
        }[match.group(2).decode()]

        self.WriteStatus('AudioGainLevel', Level, {'Channel': Channel})

    def SetAudioMute(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'

        Value = {
            'On': 'ON',
            'Off': 'OFF'
        }[value]

        if 0 <= int(Channel) <= 4:
            CmdString = '< SET {} AUDIO_MUTE {} >'.format(Channel, Value)
            self.__SetHelper('AudioMute', CmdString, value, qualifier, 3)

    def UpdateAudioMute(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'
        if 0 <= int(Channel) <= 4:
            CmdString = '< GET {} AUDIO_MUTE >'.format(Channel)
            self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        Channel = match.group(1).decode()
        if Channel == '0':
            Channel = 'All'
        Values = match.group(2).decode().title()
        self.WriteStatus('AudioMute', Values, {'Channel': Channel})

    def UpdateChannelName(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'
        if 0 <= int(Channel) <= 4:
            CmdString = '< GET {} CHAN_NAME >'.format(Channel)
            self.__UpdateHelper('ChannelName', CmdString, value, qualifier)

    def __MatchChannelName(self, match, tag):
        Channel = match.group(1).decode()
        if Channel == '0':
            Channel = 'All'
        String = match.group(2).decode()
        self.WriteStatus('ChannelName', String, {'Channel': Channel})

    def SetDigitalAudioGain(self, value, qualifier):
        Channel = qualifier['Channel']
        if (1 <= int(Channel) <= 4) and (0 <= value <= 140):
            CmdString = '< SET {0} AUDIO_GAIN_HI_RES {1:04d} >'.format(Channel, int(value * 10))
            self.__SetHelper('DigitalAudioGain', CmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetDigitalAudioGain')

    def UpdateDigitalAudioGain(self, value, qualifier):
        Channel = qualifier['Channel']
        if 1 <= int(Channel) <= 4:
            CmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(Channel)
            self.__UpdateHelper('DigitalAudioGain', CmdString, value, qualifier)

    def __MatchDigitalAudioGain(self, match, tag):
        Channel = match.group(1).decode()
        value = int(match.group(2).decode()) / 10
        if 0 <= value <= 140:
            self.WriteStatus('DigitalAudioGain', value, {'Channel': Channel})

    def SetFlashLights(self, value, qualifier):
        Value = {
            'On': '< SET FLASH ON >',
            'Off': '< SET FLASH OFF >'
        }[value]

        self.__SetHelper('FlashLights', Value, value, qualifier)

    def SetLEDBrightness(self, value, qualifier):
        Value = {
            'Off': '< SET LED_BRIGHTNESS 0 >',
            'Low': '< SET LED_BRIGHTNESS 1 >',
            'High': '< SET LED_BRIGHTNESS 2 >'
        }[value]

        self.__SetHelper('LEDBrightness', Value, value, qualifier)

    def UpdateLEDBrightness(self, value, qualifier):
        self.__UpdateHelper('LEDBrightness', '< GET LED_BRIGHTNESS >', value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        Values = {
            '0': 'Off',
            '1': 'Low',
            '2': 'High'
        }[match.group(1).decode()]

        self.WriteStatus('LEDBrightness', Values, None)
        self.WriteStatus('DeviceResponseStatus', 'Good', None)

    def SetMicLogicLEDIn(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'

        Value = {
            'On': 'ON',
            'Off': 'OFF'
        }[value]

        if 0 <= int(Channel) <= 4:
            CmdString = '< SET {} CHAN_LED_IN_STATE {} >'.format(Channel, Value)
            self.__SetHelper('MicLogicLEDIn', CmdString, value, qualifier)

    def UpdateMicLogicLEDIn(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'
        if 0 <= int(Channel) <= 4:
            CmdString = '< GET {} CHAN_LED_IN_STATE >'.format(Channel)
            self.__UpdateHelper('MicLogicLEDIn', CmdString, value, qualifier)

    def __MatchMicLogicLEDIn(self, match, tag):
        Channel = match.group(1).decode()
        if Channel == '0':
            Channel = 'All'
        Values = match.group(2).decode().title()
        self.WriteStatus('MicLogicLEDIn', Values, {'Channel': Channel})

    def UpdateMicLogicSwitchOutStatus(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'
        if 0 <= int(Channel) <= 4:
            CmdString = '< GET {} HW_GATING_LOGIC >'.format(Channel)
            self.__UpdateHelper('MicLogicSwitchOutStatus', CmdString, value, qualifier)

    def __MatchMicLogicSwitchOutStatus(self, match, tag):
        Channel = match.group(1).decode()
        if Channel == '0':
            Channel = 'All'
        Values = match.group(2).decode().title()
        self.WriteStatus('MicLogicSwitchOutStatus', Values, {'Channel': Channel})

    def SetPhantomPower(self, value, qualifier):
        Channel = qualifier['Channel']

        Value = {
            'On': 'ON',
            'Off': 'OFF'
        }[value]

        if 1 <= int(Channel) <= 4:
            CmdString = '< SET {} PHANTOM_PWR_ENABLE {} >'.format(Channel, Value)
            self.__SetHelper('PhantomPower', CmdString, value, qualifier, 3)

    def UpdatePhantomPower(self, value, qualifier):
        Channel = qualifier['Channel']
        if 1 <= int(Channel) <= 4:
            CmdString = '< GET {} PHANTOM_PWR_ENABLE >'.format(Channel)
            self.__UpdateHelper('PhantomPower', CmdString, value, qualifier)

    def __MatchPhantomPower(self, match, tag):
        Channel = match.group(1).decode()
        Values = match.group(2).decode().title()
        self.WriteStatus('PhantomPower', Values, {'Channel': Channel})

    def SetPreset(self, value, qualifier):
        if 1 <= int(value) <= 10:
            CmdString = '< SET PRESET {0:02d} >'.format(int(value))
            self.__SetHelper('Preset', CmdString, value, qualifier, 3)

    def UpdatePreset(self, value, qualifier):
        self.__UpdateHelper('Preset', '< GET PRESET >', value, qualifier)

    def __MatchPreset(self, match, tag):
        self.WriteStatus('Preset', str(int(match.group(1).decode())), None)

    def UpdateSigClip(self, value, qualifier):
        Channel = qualifier['Channel']
        if Channel == 'All':
            Channel = '0'
        if 0 <= int(Channel) <= 4:
            CmdString = '< GET {} LED_COLOR_SIG_CLIP >'.format(Channel)
            self.__UpdateHelper('SigClip', CmdString, value, qualifier)

    def __MatchSigClip(self, match, tag):
        Channel = match.group(1).decode()
        if Channel == '0':
            Channel = 'All'
        Values = match.group(2).decode().title()
        self.WriteStatus('SigClip', Values, {'Channel': Channel})

    def __MatchError(self, match, tag):
        pass

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
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
        pass

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

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
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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
