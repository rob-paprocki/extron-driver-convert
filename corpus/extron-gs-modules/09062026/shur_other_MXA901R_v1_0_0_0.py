# Copyright 2025, Extron. All rights reserved.

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
            'AudioGain': {'Parameters':['Channel'], 'Status': {}},
            'AudioLevelPeak': {'Parameters':['Channel'], 'Status': {}},
            'AudioLevelRMS': {'Parameters':['Channel'], 'Status': {}},
            'ChannelMute': {'Parameters':['Channel'], 'Status': {}},
            'DeviceMute': { 'Status': {}},
            'Identify': { 'Status': {}},
            'LEDBrightness': { 'Status': {}},
            'LEDStatus': {'Parameters':['State'], 'Status': {}},
            'MuteLEDStatus': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP (09|10) AUDIO_GAIN_HI_RES (\d{1,4}) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP (09|10) AUDIO_IN_PEAK_LVL (\d{1,3}) >'), self.__MatchAudioLevelPeak, None)
            self.AddMatchString(re.compile(b'< REP (09|10) AUDIO_IN_RMS_LVL (\d{1,3}) >'), self.__MatchAudioLevelRMS, None)
            self.AddMatchString(re.compile(b'< REP (09|10) AUDIO_MUTE (ON|OFF) >'), self.__MatchChannelMute, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_AUDIO_MUTE (ON|OFF) >'), self.__MatchDeviceMute, None)
            self.AddMatchString(re.compile(b'< REP FLASH (ON|OFF) >'), self.__MatchIdentify, None)
            self.AddMatchString(re.compile(b'< REP LED_BRIGHTNESS ([0-5]) >'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'< REP LED_STATE_(UNMUTED|MUTED) (ON|FLASHING|OFF) >'), self.__MatchLEDStatus, None)
            self.AddMatchString(re.compile(b'< REP DEV_MUTE_STATUS_LED_STATE (ON|OFF) >'), self.__MatchMuteLEDStatus, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, None)

    def SetAudioGain(self, value, qualifier):

        ChannelStates = {
            'Output' : '09',
            'AEC'    : '10'
        }

        if qualifier['Channel'] in ChannelStates and -110.0 <= value <= 30.0:
            AudioGainCmdString = '< SET {0} AUDIO_GAIN_HI_RES {1} >'.format(ChannelStates[qualifier['Channel']], int(value * 10) + 1100)
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):

        ChannelStates = {
            'Output' : '09',
            'AEC'    : '10'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioGainCmdString = '< GET {} AUDIO_GAIN_HI_RES >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGain')

    def __MatchAudioGain(self, match, tag):

        ChannelStates = {
            '09' : 'Output',
            '10' : 'AEC'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = (int(match.group(2)) - 1100) / 10
        if -110.0 <= value <= 30.0:
            self.WriteStatus('AudioGain', value, qualifier)

    def UpdateAudioLevelPeak(self, value, qualifier):

        ChannelStates = {
            'Output' : '09',
            'AEC'    : '10'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioLevelPeakCmdString = '< GET {} AUDIO_IN_PEAK_LVL >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioLevelPeak', AudioLevelPeakCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioLevelPeak')

    def __MatchAudioLevelPeak(self, match, tag):

        ChannelStates = {
            '09' : 'Output',
            '10' : 'AEC'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        if 0 <= value <= 60:
            self.WriteStatus('AudioLevelPeak', value, qualifier)

    def UpdateAudioLevelRMS(self, value, qualifier):

        ChannelStates = {
            'Output' : '09',
            'AEC'    : '10'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioLevelRMSCmdString = '< GET {} AUDIO_IN_RMS_LVL >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('AudioLevelRMS', AudioLevelRMSCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioLevelRMS')

    def __MatchAudioLevelRMS(self, match, tag):

        ChannelStates = {
            '09' : 'Output',
            '10' : 'AEC'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        if 0 <= value <= 60:
            self.WriteStatus('AudioLevelRMS', value, qualifier)

    def SetChannelMute(self, value, qualifier):

        ChannelStates = {
            'Output' : '09',
            'AEC'    : '10'
        }

        if qualifier['Channel'] in ChannelStates and value in ['On', 'Off']:
            ChannelMuteCmdString = '< SET {0} AUDIO_MUTE {1} >'.format(ChannelStates[qualifier['Channel']], value.upper())
            self.__SetHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelMute')

    def UpdateChannelMute(self, value, qualifier):

        ChannelStates = {
            'Output' : '09',
            'AEC'    : '10'
        }

        if qualifier['Channel'] in ChannelStates:
            ChannelMuteCmdString = '< GET {} AUDIO_MUTE >'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('ChannelMute', ChannelMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelMute')

    def __MatchChannelMute(self, match, tag):

        ChannelStates = {
            '09' : 'Output',
            '10' : 'AEC'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = match.group(2).decode().title()
        self.WriteStatus('ChannelMute', value, qualifier)

    def SetDeviceMute(self, value, qualifier):

        if value in ['On', 'Off']:
            DeviceMuteCmdString = '< SET DEVICE_AUDIO_MUTE {} >'.format(value.upper())
            self.__SetHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceMute')

    def UpdateDeviceMute(self, value, qualifier):

        DeviceMuteCmdString = '< GET DEVICE_AUDIO_MUTE >'
        self.__UpdateHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)

    def __MatchDeviceMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DeviceMute', value, None)

    def SetIdentify(self, value, qualifier):

        if value in ['On', 'Off']:
            IdentifyCmdString = '< SET FLASH {} >'.format(value.upper())
            self.__SetHelper('Identify', IdentifyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIdentify')

    def UpdateIdentify(self, value, qualifier):

        IdentifyCmdString = '< GET FLASH >'
        self.__UpdateHelper('Identify', IdentifyCmdString, value, qualifier)

    def __MatchIdentify(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Identify', value, None)

    def SetLEDBrightness(self, value, qualifier):

        ValueStateValues = {
            'Disabled'  : '0',
            '20%'       : '1',
            '40%'       : '2',
            '60%'       : '3',
            '80%'       : '4',
            '100%'      : '5'
        }

        if value in ValueStateValues:
            LEDBrightnessCmdString = '< SET LED_BRIGHTNESS {} >'.format(ValueStateValues[value])
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

    def SetLEDStatus(self, value, qualifier):

        ValueStateValues = {
            'On'       : 'ON',
            'Flashing' : 'FLASHING',
            'Off'      : 'OFF'
        }

        if qualifier['State'] in ['Muted', 'Unmuted'] and value in ValueStateValues:
            LEDStatusCmdString = '< SET LED_STATE_{0} {1} >'.format(qualifier['State'].upper(), ValueStateValues[value])
            self.__SetHelper('LEDStatus', LEDStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDStatus')

    def UpdateLEDStatus(self, value, qualifier):

        if qualifier['State'] in ['Muted', 'Unmuted']:
            LEDStatusCmdString = '< GET LED_STATE_{} >'.format(qualifier['State'].upper())
            self.__UpdateHelper('LEDStatus', LEDStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDStatus')

    def __MatchLEDStatus(self, match, tag):

        qualifier = {'State' : match.group(1).decode().title()}
        value = match.group(2).decode().title()
        self.WriteStatus('LEDStatus', value, qualifier)

    def UpdateMuteLEDStatus(self, value, qualifier):

        MuteLEDStatusCmdString = '< GET DEV_MUTE_STATUS_LED_STATE >'
        self.__UpdateHelper('MuteLEDStatus', MuteLEDStatusCmdString, value, qualifier)

    def __MatchMuteLEDStatus(self, match, tag):

        ValueStateValues = {
            'ON'  : 'Muted',
            'OFF' : 'Unmuted'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteLEDStatus', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 10:
            PresetRecallCmdString = '< SET PRESET {:02d} >'.format(int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
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

        self.Error(['An error occured.'])

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