from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'ChannelMute': { 'Status': {}},
            'DefaultToggleFunction': { 'Status': {}},
            'DeviceLEDInState': { 'Status': {}},
            'DeviceSwitchOutState': { 'Status': {}},
            'Flash': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDColor': {'Parameters':['State'], 'Status': {}},
            'LEDState': {'Parameters':['State'], 'Status': {}},
            'MuteButtonStatus': { 'Status': {}},
            'MuteControlFunction': { 'Status': {}},
            'MuteControlMode': { 'Status': {}},
            'MuteLEDState': { 'Status': {}},
            'Preset': { 'Status': {}}
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP AUDIO_MUTE (ON|OFF) >', re.I), self.__MatchChannelMute, None)
            self.AddMatchString(re.compile(b'< REP DEFAULT_TOGGLE_STATE (Muted|Unmuted) >', re.I), self.__MatchDefaultToggleFunction, None)
            self.AddMatchString(re.compile(b'< REP DEV_LED_IN_STATE (ON|OFF) >'), self.__MatchDeviceLEDInState, None)
            self.AddMatchString(re.compile(b'< REP EXT_SWITCH_OUT_STATE (On|Off) >', re.I), self.__MatchDeviceSwitchOutState, None)
            self.AddMatchString(re.compile(b'< REP FLASH (ON|OFF) >'), self.__MatchFlash, None)
            self.AddMatchString(re.compile(b'< REP LED_BRIGHTNESS ([0-5]) >'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'< REP LED_COLOR_(UNMUTED|MUTED) (RED|ORANGE|GOLD|YELLOW|YELLOWGREEN|GREEN|TURQUOISE|POWDERBLUE|CYAN|SKYBLUE|BLUE|PURPLE|LIGHTPURPLE|VIOLET|ORCHID|PINK|WHITE) >'), self.__MatchLEDColor, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_(UNMUTED|MUTED) (ON|FLASHING|OFF) >'), self.__MatchLEDState, None)
            self.AddMatchString(re.compile(b'< REP MUTE_BUTTON_STATUS (ON|OFF|UNKNOWN) >'), self.__MatchMuteButtonStatus, None)
            self.AddMatchString(re.compile(b'< REP MUTE_CONTROL_FUNC (ENABLED|DISABLED) >'), self.__MatchMuteControlFunction, None)
            self.AddMatchString(re.compile(b'< REP MUTE_CONTROL_MODE (TOG|PTT|PTM) >'), self.__MatchMuteControlMode, None)
            self.AddMatchString(re.compile(b'< REP DEV_MUTE_STATUS_LED_STATE (ON|OFF) >'), self.__MatchMuteLEDState, None)
            self.AddMatchString(re.compile(b'< REP PRESET (\d{1,2}) >'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)

    def SetChannelMute(self, value, qualifier):

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF'
            }

        if value in ValueStateValues:
            ChannelMuteCmdString = '< SET AUDIO_MUTE {} >'.format(ValueStateValues[value])
            self.__SetHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMute')

    def UpdateChannelMute(self, value, qualifier):

        ChannelMuteCmdString = '< GET AUDIO_MUTE >'
        self.__UpdateHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)

    def __MatchChannelMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('ChannelMute', value, None)

    def SetDefaultToggleFunction(self, value, qualifier):

        ValueStateValues = {
            'Muted'   : '< SET DEFAULT_TOGGLE_STATE Muted >', 
            'Unmuted' : '< SET DEFAULT_TOGGLE_STATE Unmuted >'
        }

        if value in ValueStateValues:
            DefaultToggleFunctionCmdString = ValueStateValues[value]
            self.__SetHelper('DefaultToggleFunction', DefaultToggleFunctionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDefaultToggleFunction')

    def UpdateDefaultToggleFunction(self, value, qualifier):

        DefaultToggleFunctionCmdString = '< GET DEFAULT_TOGGLE_STATE >'
        self.__UpdateHelper('DefaultToggleFunction', DefaultToggleFunctionCmdString, value, qualifier)

    def __MatchDefaultToggleFunction(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DefaultToggleFunction', value, None)

    def SetDeviceLEDInState(self, value, qualifier):

        ValueStateValues = ['On', 'Off']

        if value in ValueStateValues:
            DeviceLEDInStateCmdString = '< SET DEV_LED_IN_STATE {} >'.format(value.upper())
            self.__SetHelper('DeviceLEDInState', DeviceLEDInStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceLEDInState')

    def UpdateDeviceLEDInState(self, value, qualifier):

        DeviceLEDInStateCmdString = '< GET DEV_LED_IN_STATE >'
        self.__UpdateHelper('DeviceLEDInState', DeviceLEDInStateCmdString, value, qualifier)

    def __MatchDeviceLEDInState(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DeviceLEDInState', value, None)

    def UpdateDeviceSwitchOutState(self, value, qualifier):

        DeviceSwitchOutStateCmdString = '< GET EXT_SWITCH_OUT_STATE >'
        self.__UpdateHelper('DeviceSwitchOutState', DeviceSwitchOutStateCmdString, value, qualifier)

    def __MatchDeviceSwitchOutState(self, match, tag):

        ValueStateValues = {
            'off' : 'Mute',
            'on'  : 'Unmute'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('DeviceSwitchOutState', value, None)

    def SetFlash(self, value, qualifier):

        ValueStateValues = {
            'On'  : '< SET FLASH ON >',
            'Off' : '< SET FLASH OFF >'
        }

        if value in ValueStateValues:
            FlashCmdString = ValueStateValues[value]
            self.__SetHelper('Flash', FlashCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlash')

    def UpdateFlash(self, value, qualifier):

        FlashCmdString = '< GET FLASH >'
        self.__UpdateHelper('Flash', FlashCmdString, value, qualifier)

    def __MatchFlash(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Flash', value, None)

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'Disabled'  : '< SET LED_BRIGHTNESS 0 >',
            '20%'       : '< SET LED_BRIGHTNESS 1 >',
            '40%'       : '< SET LED_BRIGHTNESS 2 >',
            '60%'       : '< SET LED_BRIGHTNESS 3 >',
            '80%'       : '< SET LED_BRIGHTNESS 4 >',
            '100%'      : '< SET LED_BRIGHTNESS 5 >'
        }

        if value in ValueStateValues:
            LEDBrightnessCmdString = ValueStateValues[value]
            self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):

        LEDBrightnessCmdString = '< GET LED_BRIGHTNESS >'
        self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)

    def __MatchLEDBrightness(self, match, tag):

        ValueStateValues = {
            '0' : 'Disabled', 
            '1' : '20%', 
            '2' : '40%', 
            '3' : '60%', 
            '4' : '80%', 
            '5' : '100%'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LEDBrightness', value, None)

    def SetLEDColor(self, value, qualifier):

        StateStates = {
            'Unmuted' : 'UNMUTED',
            'Muted'   : 'MUTED'
        }

        ValueStateValues = {
            'Red'           : 'RED',
            'Orange'        : 'ORANGE',
            'Gold'          : 'GOLD',
            'Yellow'        : 'YELLOW',
            'Yellow Green'  : 'YELLOWGREEN',
            'Green'         : 'GREEN',
            'Turquoise'     : 'TURQUOISE',
            'Powder Blue'   : 'POWDERBLUE',
            'Cyan'          : 'CYAN',
            'Sky Blue'      : 'SKYBLUE',
            'Blue'          : 'BLUE',
            'Purple'        : 'PURPLE',
            'Light Purple'  : 'LIGHTPURPLE',
            'Violet'        : 'VIOLET',
            'Orchid'        : 'ORCHID',
            'Pink'          : 'PINK',
            'White'         : 'WHITE'
        }

        if value in ValueStateValues and qualifier['State'] in StateStates:
            LEDColorCmdString = '< SET LED_COLOR_{0} {1} >'.format(StateStates[qualifier['State']], ValueStateValues[value])
            self.__SetHelper('LEDColor', LEDColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDColor')

    def UpdateLEDColor(self, value, qualifier):

        StateStates = {
            'Unmuted' : 'UNMUTED',
            'Muted'   : 'MUTED'
        }

        if qualifier['State'] in StateStates:
            LEDColorCmdString = '< GET LED_COLOR_{} >'.format(StateStates[qualifier['State']])
            self.__UpdateHelper('LEDColor', LEDColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDColor')

    def __MatchLEDColor(self, match, tag):

        ValueStateValues = {
            'RED'           : 'Red',
            'ORANGE'        : 'Orange',
            'GOLD'          : 'Gold',
            'YELLOW'        : 'Yellow',
            'YELLOWGREEN'   : 'Yellow Green',
            'GREEN'         : 'Green',
            'TURQUOISE'     : 'Turquoise',
            'POWDERBLUE'    : 'Powder Blue',
            'CYAN'          : 'Cyan',
            'SKYBLUE'       : 'Sky Blue',
            'BLUE'          : 'Blue',
            'PURPLE'        : 'Purple',
            'LIGHTPURPLE'   : 'Light Purple',
            'VIOLET'        : 'Violet',
            'ORCHID'        : 'Orchid',
            'PINK'          : 'Pink',
            'WHITE'         : 'White'
        }

        qualifier = {'State' : match.group(1).decode().title()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LEDColor', value, qualifier)

    def SetLEDState(self, value, qualifier):

        StateStates = {
            'Unmuted'  : 'UNMUTED',
            'Muted'    : 'MUTED'
        }

        ValueStateValues = {
            'On'        : 'ON',
            'Flashing'  : 'FLASHING',
            'Off'       : 'OFF'
        }

        if value in ValueStateValues and qualifier['State'] in StateStates:
            LEDStateCmdString = '< SET LED_STATE_{0} {1} >'.format(StateStates[qualifier['State']], ValueStateValues[value])
            self.__SetHelper('LEDState', LEDStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDState')

    def UpdateLEDState(self, value, qualifier):

        StateStates = {
            'Unmuted'  : 'UNMUTED',
            'Muted'    : 'MUTED'
        }

        if qualifier['State'] in StateStates:
            LEDStateCmdString = '< GET LED_STATE_{} >'.format(StateStates[qualifier['State']])
            self.__UpdateHelper('LEDState', LEDStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDState')

    def __MatchLEDState(self, match, tag):

        qualifier = {'State' : match.group(1).decode().title()}
        value = match.group(2).decode().title()
        self.WriteStatus('LEDState', value, qualifier)

    def UpdateMuteButtonStatus(self, value, qualifier):

        MuteButtonStatusCmdString = '< GET MUTE_BUTTON_STATUS >'
        self.__UpdateHelper('MuteButtonStatus', MuteButtonStatusCmdString, value, qualifier)

    def __MatchMuteButtonStatus(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('MuteButtonStatus', value, None)

    def SetMuteControlFunction(self, value, qualifier):

        ValueStateValues = {
            'Enabled'  : '< SET MUTE_CONTROL_FUNC ENABLED >',
            'Disabled' : '< SET MUTE_CONTROL_FUNC DISABLED >'
        }

        if value in ValueStateValues:
            MuteControlFunctionCmdString = ValueStateValues[value]
            self.__SetHelper('MuteControlFunction', MuteControlFunctionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMuteControlFunction')

    def UpdateMuteControlFunction(self, value, qualifier):

        MuteControlFunctionCmdString = '< GET MUTE_CONTROL_FUNC >'
        self.__UpdateHelper('MuteControlFunction', MuteControlFunctionCmdString, value, qualifier)

    def __MatchMuteControlFunction(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('MuteControlFunction', value, None)

    def SetMuteControlMode(self, value, qualifier):

        ValueStateValues = {
            'Toggle'        : '< SET MUTE_CONTROL_MODE TOG >',
            'Push To Talk'  : '< SET MUTE_CONTROL_MODE PTT >',
            'Push To Mute'  : '< SET MUTE_CONTROL_MODE PTM >'
        }

        if value in ValueStateValues:
            MuteControlModeCmdString = ValueStateValues[value]
            self.__SetHelper('MuteControlMode', MuteControlModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMuteControlMode')

    def UpdateMuteControlMode(self, value, qualifier):

        MuteControlModeCmdString = '< GET MUTE_CONTROL_MODE >'
        self.__UpdateHelper('MuteControlMode', MuteControlModeCmdString, value, qualifier)

    def __MatchMuteControlMode(self, match, tag):

        ValueStateValues = {
            'TOG' : 'Toggle', 
            'PTT' : 'Push To Talk', 
            'PTM' : 'Push To Mute'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteControlMode', value, None)

    def UpdateMuteLEDState(self, value, qualifier):

        MuteLEDStateCmdString = '< GET DEV_MUTE_STATUS_LED_STATE >'
        self.__UpdateHelper('MuteLEDState', MuteLEDStateCmdString, value, qualifier)

    def __MatchMuteLEDState(self, match, tag):

        ValueStateValues = {
            'ON'  : 'Muted',
            'OFF' : 'Unmuted'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteLEDState', value, None)

    def SetPreset(self, value, qualifier):

        if 1 <= int(value) <= 10:
            PresetCmdString = '< SET PRESET {:02d} >'.format(int(value))
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '< GET PRESET >'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        value = int(match.group(1))
        if 0 <= value <= 10:
            self.WriteStatus('Preset', str(value), None)

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

    def __MatchError(self, match, tag):

        self.counter = 0

        self.Error(['An error occurred.'])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()