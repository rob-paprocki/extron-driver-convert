from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.Models = {
            'MXWAPT4': self.shur_25_1187_4,
            'MXWAPT8': self.shur_25_1187_8,
            'MXWAPT2': self.shur_25_1187_2,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'APTFlash': { 'Status': {}},
            'AudioGain': {'Parameters':['Channel','Source'], 'Status': {}},
            'AudioInput': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryChargeStatus': {'Parameters':['Channel'], 'Status': {}},
            'BatteryHealth': {'Parameters':['Channel'], 'Status': {}},
            'BatteryRemainingTime': {'Parameters':['Channel'], 'Status': {}},
            'DeviceID': { 'Status': {}},
            'LinkMicrophoneOverNetwork': {'Parameters':['Type','Charging Slot Number','Channel','IP Address of APT'], 'Status': {}},
            'MicrophoneButtonStatus': {'Parameters':['Channel'], 'Status': {}},
            'MicrophoneFlash': {'Parameters':['Channel'], 'Status': {}},
            'MicrophoneGreenLED': {'Parameters':['Channel'], 'Status': {}},
            'MicrophoneRedLED': {'Parameters':['Channel'], 'Status': {}},
            'MicrophoneType': {'Parameters':['Channel'], 'Status': {}},
            'TransmitterStatus': {'Parameters':['Channel'], 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) (?P<source>INT_)?AUDIO_GAIN (?P<gain>0[0-4][0-9]) >'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) BP_MIC_MODE (?P<source>INT|EXT) >'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) BATT_CHARGE (?P<charge>[0-9]{3}) >'), self.__MatchBatteryChargeStatus, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) BATT_HEALTH (?P<health>[0-9]{3}) >'), self.__MatchBatteryHealth, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) BATT_RUN_TIME (?P<time>[0-9]{5}) >'), self.__MatchBatteryRemainingTime, None)
            self.AddMatchString(re.compile(b'< REP DEVICE_ID ([\s\S]+) >'), self.__MatchDeviceID, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) BUTTON_STS (?P<status>ON|OFF|UNKNOWN) >'), self.__MatchMicrophoneButtonStatus, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) LED_STATUS (?P<red>ON|OF|ST|FL|PU|NC) (?P<green>ON|OF|ST|FL|PU|NC) >'), self.__MatchMicrophoneRedAndGreenLED, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) LED_STATUS UNKNOWN >'), self.__MatchMicrophoneRedAndGreenLED, 'Unknown')
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) TX_TYPE (?P<type>MXW1|MXW2|MXW6|MXW8|UNKNOWN) >'), self.__MatchMicrophoneType, None)
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) TX_STATUS (?P<status>ACTIVE|MUTE|STANDBY|ON_CHARGER|UNKNOWN) >'), self.__MatchTransmitterStatus, None)
            self.AddMatchString(re.compile(b'< REP ERR >'), self.__MatchError, 'ERR')
            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) (?P<command>[A-Z_]{1,10}) (?P<code>252|253|254|255|65535|65534|65533|65532|ERR) >'), self.__MatchError, 'EXTRA')

            self.AddMatchString(re.compile(b'< REP (?P<channel>[1-8]) TX_AVAILABLE YES >'), self.__MatchTxAvailable, None)

            self.LastUpdateTime = {
                'AudioGain'             : 0,
                'AudioInput'            : 0,
                'BatteryChargeStatus'   : 0,
                'BatteryHealth'         : 0,
                'BatteryRemainingTime'  : 0,
                'MicrophoneButtonStatus': 0,
                'MicrophoneGreenLED'    : 0,
                'MicrophoneType'        : 0,
                'TransmitterStatus'     : 0
            }

    def __MatchTxAvailable(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = match.group('channel').decode()

        self.UpdateTransmitterStatus( None, qualifier)
        self.UpdateAudioGain( None, {'Channel': qualifier['Channel'], 'Source': 'Internal'})
        self.UpdateAudioInput( None, qualifier)
        self.UpdateBatteryRemainingTime( None, qualifier)
        self.UpdateBatteryChargeStatus( None, qualifier)
        self.UpdateBatteryHealth( None, qualifier)
        self.UpdateMicrophoneButtonStatus( None, qualifier)
        self.UpdateMicrophoneGreenLED( None, qualifier)
        self.UpdateMicrophoneType( None, qualifier)

    def SetAPTFlash(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON',
            'Off' : 'OFF'
        }
        
        if value in ValueStateValues:
            APTFlashCmdString = '< SET FLASH {0} >'.format(ValueStateValues[value])
            self.__SetHelper('APTFlash', APTFlashCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAPTFlash')

    def SetAudioGain(self, value, qualifier):

        if -25 <= value <= 15 and qualifier['Channel'] in self.SetChannelStates and qualifier['Source'] in  ['Internal', 'External']:
            if qualifier['Source'] == 'Internal':
                AudioGainCmdString = '< SET {0} INT_AUDIO_GAIN {1:03d} >'.format(self.SetChannelStates[qualifier['Channel']], value + 25)
            elif qualifier['Source'] == 'External':
                AudioGainCmdString = '< SET {0} AUDIO_GAIN {1:03d} >'.format(self.SetChannelStates[qualifier['Channel']], value + 25)
            else:
                self.Discard('Invalid Command for SetAudioGain')
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):
        
        if not qualifier['Channel'] == 'All' and qualifier['Channel'] in self.SetChannelStates and qualifier['Source'] in ['Internal', 'External']:
            AudioGainCmdString = '< GET 0 INT_AUDIO_GAIN >< GET 0 AUDIO_GAIN >'
            self.__UpdateHelper('AudioGain', AudioGainCmdString, value, qualifier)

    def __MatchAudioGain(self, match, tag):

        qualifier = {'Channel': match.group('channel').decode()}
        if match.group('source') == b'INT_':
            qualifier['Source'] = 'Internal'
        else:
            qualifier['Source'] = 'External'
        gainValue = int(match.group('gain').decode())
        self.WriteStatus('AudioGain', gainValue - 25, qualifier)

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Internal'  : 'INT',
            'External'  : 'EXT',
            'Auto'      : 'AUTO'
        }
        
        if value in ValueStateValues and qualifier['Channel'] in self.SetChannelStates:
            AudioInputCmdString = '< SET {0} BP_MIC_MODE {1} >'.format(self.SetChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):
      
        if qualifier['Channel'] in self.SetChannelStates:
            AudioInputCmdString = '< GET 0 BP_MIC_MODE >'
            self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateAudioInput')
            
    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            'INT': 'Internal',
            'EXT': 'External',
        }

        qualifier = {'Channel': match.group(1).decode()}
        value = ValueStateValues[match.group('source').decode()]
        self.WriteStatus('AudioInput', value, qualifier)

    def UpdateBatteryChargeStatus(self, value, qualifier):
        
        if qualifier['Channel'] in self.SetChannelStates:
            BatteryChargeStatusCmdString = '< GET 0 BATT_CHARGE >'
            self.__UpdateHelper('BatteryChargeStatus', BatteryChargeStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryChargeStatus')
            
    def __MatchBatteryChargeStatus(self, match, tag):

        qualifier = {'Channel': match.group('channel').decode()}

        chargeValue = int(match.group('charge').decode())
        if chargeValue != 255:
            self.WriteStatus('BatteryChargeStatus', chargeValue, qualifier)

    def UpdateBatteryHealth(self, value, qualifier):

        if qualifier['Channel'] in self.SetChannelStates:
            BatteryHealthCmdString = '< GET 0 BATT_HEALTH >'
            self.__UpdateHelper('BatteryHealth', BatteryHealthCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryHealth')
            
    def __MatchBatteryHealth(self, match, tag):

        qualifier = {'Channel': match.group('channel').decode()}
        value = int(match.group('health').decode())
        if value != 255:
            self.WriteStatus('BatteryHealth', value, qualifier)

    def UpdateBatteryRemainingTime(self, value, qualifier):

        if qualifier['Channel'] in self.SetChannelStates:
            BatteryRemainingTimeCmdString = '< GET 0 BATT_RUN_TIME >'
            self.__UpdateHelper('BatteryRemainingTime', BatteryRemainingTimeCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryRemainingTime')

    def __MatchBatteryRemainingTime(self, match, tag):

        qualifier = {'Channel': match.group('channel').decode()}
        value = int(match.group('time').decode())
        if not (65532 <= value <= 65535):
            hours = value // 60
            minutes = value % 60
            self.WriteStatus('BatteryRemainingTime', '{0}:{1:0>2}'.format(hours, minutes), qualifier)
        elif 65532 <= value <= 65535:
            self.WriteStatus('BatteryRemainingTime', '-', qualifier)

    def UpdateDeviceID(self, value, qualifier):

        DeviceIDCmdString = '< GET DEVICE_ID >'
        self.__UpdateHelper('DeviceID', DeviceIDCmdString, value, qualifier)

    def __MatchDeviceID(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceID', value, None)

    def SetLinkMicrophoneOverNetwork(self, value, qualifier):

        TypeStates = {
            'Primary'   : 'PRI', 
            'Secondary' : 'SEC'
        }

        type_val = qualifier['Type']
        chargingSlot = qualifier['Charging Slot Number']
        channelNo = qualifier['Channel']
        ip_address = qualifier['IP Address of APT']
        if type_val in TypeStates and 1 <= int(chargingSlot) <= self.channelNo and 1 <= int(channelNo) <= self.channelNo and ip_address:
            LinkMicrophoneOverNetworkCmdString = '< SET {0} {1} REMOTE_LINK {2} {{{3}}} >'.format(TypeStates[type_val], chargingSlot, channelNo, ip_address)
            self.__SetHelper('LinkMicrophoneOverNetwork', LinkMicrophoneOverNetworkCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLinkMicrophoneOverNetwork')

    def UpdateMicrophoneButtonStatus(self, value, qualifier):
        
        if qualifier['Channel'] in self.SetChannelStates:
            MicrophoneButtonStatusCmdString = '< GET 0 BUTTON_STS >'
            self.__UpdateHelper('MicrophoneButtonStatus', MicrophoneButtonStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateMicrophoneButtonStatus')
            
    def __MatchMicrophoneButtonStatus(self, match, tag):

        ValueStateValues = {
            'ON'        : 'On', 
            'OFF'       : 'Off',
            'UNKNOWN'   : 'Unknown'
        }

        qualifier = {'Channel': match.group('channel').decode()}
        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('MicrophoneButtonStatus', value, qualifier)

    def SetMicrophoneFlash(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON',
            'Off' : 'OFF'
        }
        
        if value in ValueStateValues and qualifier['Channel'] in self.SetChannelStates:
            MicrophoneFlashCmdString = '< SET {0} FLASH {1} >'.format(self.SetChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('MicrophoneFlash', MicrophoneFlashCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneFlash')

    def SetMicrophoneGreenLED(self, value, qualifier):

        ValueStateValues = {
            'On'        : 'ON', 
            'Off'       : 'OF', 
            'Strobe'    : 'ST', 
            'Flash'     : 'FL', 
            'Pulse'     : 'PU'
        }
        if value in ValueStateValues and qualifier['Channel'] in self.SetChannelStates:
            MicrophoneGreenLEDCmdString = '< SET {0} LED_STATUS NC {1} >'.format(self.SetChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('MicrophoneGreenLED', MicrophoneGreenLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneGreenLED')
            
    def UpdateMicrophoneGreenLED(self, value, qualifier):

        
        if not qualifier['Channel'] == 'All' and qualifier['Channel'] in self.SetChannelStates:
            MicrophoneGreenLEDCmdString = '< GET 0 LED_STATUS >'
            self.__UpdateHelper('MicrophoneGreenLED', MicrophoneGreenLEDCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateMicrophoneGreenLED')

    def __MatchMicrophoneRedAndGreenLED(self, match, tag):

        ValueStateValues = {
            'ON' : 'On', 
            'OF' : 'Off', 
            'ST' : 'Strobe', 
            'FL' : 'Flash', 
            'PU' : 'Pulse'
        }

        qualifier = {'Channel': match.group('channel').decode()}
        if tag == 'Unknown':
            self.WriteStatus('MicrophoneGreenLED', 'Unknown', qualifier)
            self.WriteStatus('MicrophoneRedLED', 'Unknown', qualifier)
        else:
            GreenLED = match.group('green').decode()
            RedLED = match.group('red').decode()

            if not GreenLED == 'NC':
                self.WriteStatus('MicrophoneGreenLED', ValueStateValues[GreenLED], qualifier)
            if not RedLED == 'NC':
                self.WriteStatus('MicrophoneRedLED', ValueStateValues[RedLED], qualifier)

    def SetMicrophoneRedLED(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'ON',
            'Off'   : 'OF',
            'Strobe' : 'ST', 
            'Flash' : 'FL', 
            'Pulse' : 'PU'
        }
        
        if value in ValueStateValues and qualifier['Channel'] in self.SetChannelStates:
            MicrophoneRedLEDCmdString = '< SET {0} LED_STATUS {1} NC >'.format(self.SetChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('MicrophoneRedLED', MicrophoneRedLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneRedLED')
            
    def UpdateMicrophoneRedLED(self, value, qualifier):

        self.UpdateMicrophoneGreenLED(value, qualifier)

    def UpdateMicrophoneType(self, value, qualifier):

        if qualifier['Channel'] in self.SetChannelStates:
            MicrophoneTypeCmdString = '< GET 0 TX_TYPE >'
            self.__UpdateHelper('MicrophoneType', MicrophoneTypeCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateMicrophoneType')

    def __MatchMicrophoneType(self, match, tag):

        ValueStateValues = {
            'MXW1'      : 'MXW1', 
            'MXW2'      : 'MXW2', 
            'MXW6'      : 'MXW6', 
            'MXW8'      : 'MXW8',
            'UNKNOWN'   : 'Unknown'
        }

        qualifier = {'Channel': match.group('channel').decode()}
        value = ValueStateValues[match.group('type').decode()]
        self.WriteStatus('MicrophoneType', value, qualifier)

    def SetTransmitterStatus(self, value, qualifier):

        ValueStateValues = {
            'Active'    : 'ACTIVE', 
            'Mute'      : 'MUTE', 
            'Standby'   : 'STANDBY', 
            'Off'       : 'OFF'
        }
        
        if value in ValueStateValues and qualifier['Channel'] in self.SetChannelStates:
            TransmitterStatusCmdString = '< SET {0} TX_STATUS {1} >'.format(self.SetChannelStates[qualifier['Channel']], ValueStateValues[value])
            self.__SetHelper('TransmitterStatus', TransmitterStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitterStatus')
            
    def UpdateTransmitterStatus(self, value, qualifier):

        if not qualifier['Channel'] == 'All' and qualifier['Channel'] in self.SetChannelStates:
            TransmitterStatusCmdString = '< GET 0 TX_STATUS >'
            self.__UpdateHelper('TransmitterStatus', TransmitterStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateTransmitterStatus')

    def __MatchTransmitterStatus(self, match, tag):

        ValueStateValues = {
            'ACTIVE'        : 'Active', 
            'MUTE'          : 'Mute', 
            'STANDBY'       : 'Standby', 
            'UNKNOWN'       : '-', 
            'ON_CHARGER'    : 'On Charger'
        }

        qualifier = {'Channel': match.group('channel').decode()}
        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('TransmitterStatus', value, qualifier)

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

        if tag == 'ERR':
            self.Error(['Command is not able to be implemented'])
        elif tag == 'EXTRA':
            self.Error(['Error Channel: {0} Command: {1} Code: {2}'.format(match.group('channel').decode(), match.group('command').decode(), match.group('code').decode())])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def shur_25_1187_2(self):

        self.SetChannelStates = {
            '1' : '1', 
            '2' : '2', 
            'All' : '0'
        }
        self.channelNo = 2

    def shur_25_1187_4(self):

        self.SetChannelStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4',
            'All' : '0'
        }
        self.channelNo = 4

    def shur_25_1187_8(self):

        self.SetChannelStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8',
            'All' : '0'
        }
        self.channelNo = 8

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

