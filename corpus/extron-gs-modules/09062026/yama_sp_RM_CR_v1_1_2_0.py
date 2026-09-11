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
            'BluetoothPairing': { 'Status': {}},
            'BluetoothPairingStatus': { 'Status': {}},
            'CallControl': {'Parameters': ['Line', 'Number'], 'Status': {}},
            'CallStatus': {'Parameters': ['Line'], 'Status': {}},
            'DanteInputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'DanteInputMute': {'Parameters': ['Channel'], 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'DTMF': {'Parameters': ['Line', 'Character'], 'Status': {}},
            'FarEndInputFaderLevel': {'Parameters': ['Channel'], 'Status': {}},
            'FarEndInputFaderMute': {'Parameters': ['Channel'], 'Status': {}},
            'FarEndOutputFaderLevel': {'Parameters': ['Channel'], 'Status': {}},
            'FarEndOutputFaderMute': {'Parameters': ['Channel'], 'Status': {}},
            'MicInputFaderLevel': {'Parameters': ['Channel'], 'Status': {}},
            'MicInputFaderMute': {'Parameters': ['Channel'], 'Status': {}},
            'MixingBusLevel': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'NearEndOutputFaderLevel': {'Parameters': ['Channel'], 'Status': {}},
            'NearEndOutputFaderMute': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.RunModeDisabled = True
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) event rm: ?(?:get)?bluetoothstatus "(disable|idle|connected|pairing)".*\n', re.I), self.__MatchBluetoothPairingStatus, None)
            self.AddMatchString(re.compile(b'OK event rm:getcallstatus "sip1=(.+?),sip2=(.+?),usb=(.+?),bt=(.+?),aux=(.+?),.+?"\n'), self.__MatchCallStatus, 'Solicited')
            self.AddMatchString(re.compile(b'NOTIFY event rm:changedcallstatus "(sip[12]|usb|bt|aux)=(.+?)"\n'), self.__MatchCallStatus, 'Unsolicited')
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:NeIn_Fader/Ch/Level (\d|1[0-5]) 0 (-?[0-9]{1,5}).*?\n'), self.__MatchDanteInputLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:NeIn_Fader/Ch/On (\d|1[0-5]) 0 ([01]).*?\n'), self.__MatchDanteInputMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus error "(none|flt|err|wrn).*"\n'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:FeIn_Fader/Ch/Level ([0-7]) 0 (-?[0-9]{1,5}).*?\n'), self.__MatchFarEndInputFaderLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:FeIn_Fader/Ch/On ([0-7]) 0 ([01]).*?\n'), self.__MatchFarEndInputFaderMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:FeOut_Fader/Ch/Level ([0-7]) 0 (-?[0-9]{1,5}).*?\n'), self.__MatchFarEndOutputFaderLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:FeOut_Fader/Ch/On ([0-7]) 0 ([01]).*?\n'), self.__MatchFarEndOutputFaderMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:ExtMic_Fader/Ch/Level ([01]) 0 (-?[0-9]{1,5}).*?\n'), self.__MatchMicInputFaderLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:ExtMic_Fader/Ch/On ([01]) 0 ([01]).*?\n'), self.__MatchMicInputFaderMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:MixBus/Input/Output/Level (\d|10) (\d) (-?[0-9]{1,5}).*?\n'), self.__MatchMixingBusLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:NeOut_Fader/Ch/Level ([0-3]) 0 (-?[0-9]{1,5}).*?\n'), self.__MatchNearEndOutputFaderLevel, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) [sg]et RM:NeOut_Fader/Ch/On ([0-3]) 0 ([01]).*?\n'), self.__MatchNearEndOutputFaderMute, None)
            self.AddMatchString(re.compile(b'(?:NOTIFY|OK) devstatus runmode "normal"\n'), self.__MatchRunMode, None)
        
    def __MatchRunMode(self, match, tag):

        self.RunModeDisabled = False

        self.Send('scpmode encoding ascii\n')

        self.Send('scpmode valuetype raw\n')

    def SetBluetoothPairing(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start',
            'Stop':  'stop'
            }

        if value in ValueStateValues:
            BluetoothPairingCmdString = 'event rm:bluetoothpairing "{}"\n'.format(ValueStateValues[value])
            self.__SetHelper('BluetoothPairing', BluetoothPairingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBluetoothPairing')

    def UpdateBluetoothPairingStatus(self, value, qualifier):

        BluetoothPairingStatusCmdString = 'event rm: getbluetoothstatus\n'
        self.__UpdateHelper('BluetoothPairingStatus', BluetoothPairingStatusCmdString, value, qualifier)

    def __MatchBluetoothPairingStatus(self, match, tag):

        ValueStateValues = {
            'disable':   'Disable',
            'idle':      'Idle',
            'connected': 'Connected',
            'pairing':   'Pairing'
            }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('BluetoothPairingStatus', value, None)

    def SetCallControl(self, value, qualifier):

        LineStates = {
            'SIP 1':        'sip1',
            'SIP 2':        'sip2',
            'USB':          'usb',
            'Bluetooth':    'bt',
            'Aux':          'aux'
        }
        line = qualifier['Line']
        
        ValueStateValues = {
            'Initiate Call': 'dial',
            'Answer Call':   'offhook',
            'Hold':          'holdorresume',
            'Resume':        'holdorresume',
            'Disconnect':    'hangup'
        }

        CallControlCmdString = ''
        if line in LineStates and value in ValueStateValues:
            if value == 'Initiate Call':
                dial_str = qualifier['Number']
                if dial_str:
                    CallControlCmdString = 'event rm:callaction "dial={}:{}"\n'.format(LineStates[line], dial_str)
            else:
                CallControlCmdString = 'event rm:callaction "{}={}"\n'.format(ValueStateValues[value], LineStates[line])
            if CallControlCmdString:
                self.__SetHelper('CallControl', CallControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallControl')

    def UpdateCallStatus(self, value, qualifier):

        LineStates = [
            'SIP 1',
            'SIP 2',
            'USB',
            'Bluetooth',
            'Aux'
        ]
        line = qualifier['Line']

        if line in LineStates:
            CallStatusCmdString = 'event rm:getcallstatus ""\n'
            self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCallStatus')

    def __MatchCallStatus(self, match, tag):

        LineStates = {
            'sip1': 'SIP 1',
            'sip2': 'SIP 2',
            'usb': 'USB',
            'bt': 'Bluetooth',
            'aux': 'Aux'
        }

        ValueStateValues = {
            'idle': 'Idle',
            'calling': 'Calling',
            'calling/mute': 'Calling Mute',
            'failed': 'Failed',
            'active': 'Active',
            'active/mute': 'Active Mute',
            'incoming': 'Incoming',
            'incoming/mute': 'Incoming Mute',
            'onhold': 'On Hold',
            'onhold/mute': 'On Hold Mute',
            'music': 'Music',
            'music/mute': 'Music Mute',
            'inconference_calling': 'In Conference Calling',
            'inconference_calling/mute': 'In Conference Calling Mute',
            'inconference_active': 'In Conference Active',
            'inconference_active/mute': 'In Conference Active Mute',
            'inconference_incoming': 'In Conference Incoming',
            'inconference_incoming/mute': 'In Conference Incoming Mute',
            'inconference_onhold': 'In Conference On Hold',
            'inconference_onhold/mute': 'In Conference On Hold Mute',
            'inconference_music': 'In Conference Music',
            'inconference_music/mute': 'In Conference Music Mute'
        }

        if tag == 'Solicited':
            self.WriteStatus('CallStatus', ValueStateValues[match.group(1).decode()], {'Line': 'SIP 1'})
            self.WriteStatus('CallStatus', ValueStateValues[match.group(2).decode()], {'Line': 'SIP 2'})
            self.WriteStatus('CallStatus', ValueStateValues[match.group(3).decode()], {'Line': 'USB'})
            self.WriteStatus('CallStatus', ValueStateValues[match.group(4).decode()], {'Line': 'Bluetooth'})
            self.WriteStatus('CallStatus', ValueStateValues[match.group(5).decode()], {'Line': 'Aux'})
        else:
            self.WriteStatus('CallStatus', ValueStateValues[match.group(2).decode()], {'Line': LineStates[match.group(1).decode()]})

    def SetDanteInputLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 16 and -138.01 <= value <= 10:
            temp_value = -327.68 if value == -138.01 else value
            DanteInputLevelCmdString = 'set RM:NeIn_Fader/Ch/Level {} 0 {}\n'.format(channel - 1, int(temp_value * 100))  
            self.__SetHelper('DanteInputLevel', DanteInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDanteInputLevel')

    def UpdateDanteInputLevel(self, value, qualifier):

        channel = int(qualifier['Channel']) 

        if 1 <= channel <= 16:
            DanteInputLevelCmdString = 'get RM:NeIn_Fader/Ch/Level {} 0\n'.format(channel - 1)
            self.__UpdateHelper('DanteInputLevel', DanteInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDanteInputLevel')

    def __MatchDanteInputLevel(self, match, tag):

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }

        if int(match.group(2).decode()) == -32768:
            value = -138.01
        else: 
            value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('DanteInputLevel', value, qualifier)
        else:
            self.Error(['Dante Input Level: Invalid/unexpected response'])

    def SetDanteInputMute(self, value, qualifier):

        channel = int(qualifier['Channel'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= channel <= 16 and value in ValueStateValues:
            DanteInputMuteCmdString = 'set RM:NeIn_Fader/Ch/On {} 0 {}\n'.format(channel - 1, ValueStateValues[value])
            self.__SetHelper('DanteInputMute', DanteInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDanteInputMute')

    def UpdateDanteInputMute(self, value, qualifier):

        channel = int(qualifier['Channel']) 

        if 1 <= channel <= 16:
            DanteInputMuteCmdString = 'get RM:NeIn_Fader/Ch/On {} 0\n'.format(channel - 1)
            self.__UpdateHelper('DanteInputMute', DanteInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDanteInputMute')

    def __MatchDanteInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel': str(int(match.group(1).decode()) + 1)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DanteInputMute', value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'devstatus error\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'none': 'Normal',
            'err':  'Error',
            'flt':  'Fault',
            'wrn':  'Warning'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetDTMF(self, value, qualifier):

        LineStates = {
            'SIP 1': 'sip1',
            'SIP 2': 'sip2'
        }
        line = qualifier['Line']

        character = qualifier['Character']

        if line in LineStates and 1 <= len(character) <= 1:
            DTMFCmdString = 'event rm:callaction "dtmf={}:{}"\n'.format(LineStates[line], character)
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetFarEndInputFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
        }

        ValueConstraints = {
            'Min' : -138.01,
            'Max' : 10
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            temp_value = -327.68 if value == -138.01 else value
            FarEndInputFaderLevelCmdString = 'set RM:FeIn_Fader/Ch/Level {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], int(temp_value * 100))  
            self.__SetHelper('FarEndInputFaderLevel', FarEndInputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndInputFaderLevel')

    def UpdateFarEndInputFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
        }
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            FarEndInputFaderLevelCmdString = 'get RM:FeIn_Fader/Ch/Level {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FarEndInputFaderLevel', FarEndInputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFarEndInputFaderLevel')

    def __MatchFarEndInputFaderLevel(self, match, tag):

        ChannelStates = {
            '0': 'Bluetooth L', 
            '1': 'Bluetooth R', 
            '2': 'AUX 1', 
            '3': 'AUX 2', 
            '4': 'SIP (VoIP) 1', 
            '5': 'SIP (VoIP) 2', 
            '6': 'USB L', 
            '7': 'USB R' 
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        if int(match.group(2).decode()) == -32768:
            value = -138.01
        else: 
            value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('FarEndInputFaderLevel', value, qualifier)
        else:
            self.Error(['Far End Input Fader Level: Invalid/unexpected response'])

    def SetFarEndInputFaderMute(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
        }

        ValueStateValues = {
            'On':  '1', 
            'Off': '0'
        }

        channel_val = qualifier['Channel']
        if value in ValueStateValues and channel_val in ChannelStates:
            FarEndInputFaderMuteCmdString = 'set RM:FeIn_Fader/Ch/On {} 0 {}\n'.format(
                                            ChannelStates[channel_val], ValueStateValues[value])  
            self.__SetHelper('FarEndInputFaderMute', FarEndInputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndInputFaderMute')

    def UpdateFarEndInputFaderMute(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
        }
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            FarEndInputFaderMuteCmdString = 'get RM:FeIn_Fader/Ch/On {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FarEndInputFaderMute', FarEndInputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFarEndInputFaderMute')

    def __MatchFarEndInputFaderMute(self, match, tag):

        ChannelStates = {
            '0': 'Bluetooth L', 
            '1': 'Bluetooth R', 
            '2': 'AUX 1', 
            '3': 'AUX 2', 
            '4': 'SIP (VoIP) 1', 
            '5': 'SIP (VoIP) 2', 
            '6': 'USB L', 
            '7': 'USB R'       
        }

        ValueStateValues = {
            '1': 'On', 
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FarEndInputFaderMute', value, qualifier)

    def SetFarEndOutputFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
            }

        ValueConstraints = {
            'Min' : -138.01,
            'Max' : 10
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            temp_value = -327.68 if value == -138.01 else value
            FarEndOutputFaderLevelCmdString = 'set RM:FeOut_Fader/Ch/Level {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], int(temp_value * 100))  
            self.__SetHelper('FarEndOutputFaderLevel', FarEndOutputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndOutputFaderLevel')

    def UpdateFarEndOutputFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            FarEndOutputFaderLevelCmdString = 'get RM:FeOut_Fader/Ch/Level {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FarEndOutputFaderLevel', FarEndOutputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFarEndOutputFaderLevel')

    def __MatchFarEndOutputFaderLevel(self, match, tag):

        ChannelStates = {
            '0': 'Bluetooth L', 
            '1': 'Bluetooth R', 
            '2': 'AUX 1', 
            '3': 'AUX 2', 
            '4': 'SIP (VoIP) 1', 
            '5': 'SIP (VoIP) 2', 
            '6': 'USB L', 
            '7': 'USB R' 
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        if int(match.group(2).decode()) == -32768:
            value = -138.01
        else: 
            value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('FarEndOutputFaderLevel', value, qualifier)
        else:
            self.Error(['Far End Output Fader Level: Invalid/unexpected response'])

    def SetFarEndOutputFaderMute(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
            }

        ValueStateValues = {
            'On':  '1', 
            'Off': '0'
        }

        channel_val = qualifier['Channel']
        if value in ValueStateValues and channel_val in ChannelStates:
            FarEndOutputFaderMuteCmdString = 'set RM:FeOut_Fader/Ch/On {} 0 {}\n'.format(
                                            ChannelStates[channel_val], ValueStateValues[value])  
            self.__SetHelper('FarEndOutputFaderMute', FarEndOutputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndOutputFaderMute')

    def UpdateFarEndOutputFaderMute(self, value, qualifier):

        ChannelStates = {
            'Bluetooth L':  '0', 
            'Bluetooth R':  '1', 
            'AUX 1':        '2', 
            'AUX 2':        '3', 
            'SIP (VoIP) 1': '4', 
            'SIP (VoIP) 2': '5', 
            'USB L':        '6', 
            'USB R':        '7'
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            FarEndOutputFaderMuteCmdString = 'get RM:FeOut_Fader/Ch/On {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FarEndOutputFaderMute', FarEndOutputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFarEndOutputFaderMute')

    def __MatchFarEndOutputFaderMute(self, match, tag):

        ChannelStates = {
            '0': 'Bluetooth L', 
            '1': 'Bluetooth R', 
            '2': 'AUX 1', 
            '3': 'AUX 2', 
            '4': 'SIP (VoIP) 1', 
            '5': 'SIP (VoIP) 2', 
            '6': 'USB L', 
            '7': 'USB R' 
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FarEndOutputFaderMute', value, qualifier)

    def SetMicInputFaderLevel(self, value, qualifier):

        ChannelStates = {
            '1': '0', 
            '2': '1'
        }

        ValueConstraints = {
            'Min' : -138.01,
            'Max' : 10
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            temp_value = -327.68 if value == -138.01 else value
            MicInputFaderLevelCmdString = 'set RM:ExtMic_Fader/Ch/Level {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], int(temp_value * 100))  
            self.__SetHelper('MicInputFaderLevel', MicInputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicInputFaderLevel')

    def UpdateMicInputFaderLevel(self, value, qualifier):

        ChannelStates = {
            '1': '0', 
            '2': '1'
        }
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            MicInputFaderLevelCmdString = 'get RM:ExtMic_Fader/Ch/Level {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('MicInputFaderLevel', MicInputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicInputFaderLevel')

    def __MatchMicInputFaderLevel(self, match, tag):

        ChannelStates = {
            '0': '1', 
            '1': '2'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        if int(match.group(2).decode()) == -32768:
            value = -138.01
        else: 
            value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('MicInputFaderLevel', value, qualifier)
        else:
            self.Error(['Mic Input Fader Level: Invalid/unexpected response'])

    def SetMicInputFaderMute(self, value, qualifier):

        ChannelStates = {
            '1': '0', 
            '2': '1'
        }

        ValueStateValues = {
            'On':  '1', 
            'Off': '0'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues: 
            MicInputFaderMuteCmdString = 'set RM:ExtMic_Fader/Ch/On {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('MicInputFaderMute', MicInputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicInputFaderMute')

    def UpdateMicInputFaderMute(self, value, qualifier):

        ChannelStates = {
            '1': '0', 
            '2': '1'
        }
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            MicInputFaderMuteCmdString = 'get RM:ExtMic_Fader/Ch/On {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('MicInputFaderMute', MicInputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicInputFaderMute')

    def __MatchMicInputFaderMute(self, match, tag):

        ChannelStates = {
            '0': '1', 
            '1': '2'
        }

        ValueStateValues = {
            '1': 'On', 
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicInputFaderMute', value, qualifier)

    def SetMixingBusLevel(self, value, qualifier):

        InputStates = {
            'Bluetooth L':  '0',
            'Bluetooth R':  '1',
            'AUX 1':        '2',
            'AUX 2':        '3',
            'SIP (VoIP) 1': '4',
            'SIP (VoIP) 2': '5',
            'USB L':        '6',
            'USB R':        '7',
            'Mic 1':        '8',
            'Mic 2':        '9',
            'Dante':        '10'
        }
        input_ = qualifier['Input']

        OutputStates = {
            'Bluetooth L':  '0',
            'Bluetooth R':  '1',
            'AUX 1':        '2',
            'AUX 2':        '3',
            'SIP (VoIP) 1': '4',
            'SIP (VoIP) 2': '5',
            'USB L':        '6',
            'USB R':        '7',
            'Speaker L':    '8',
            'Speaker R':    '9'
        }
        output = qualifier['Output']

        if input_ in InputStates and output in OutputStates and -138.01 <= value <= 0:
            temp_value = -327.68 if value == -138.01 else value
            MixingBusLevelCmdString = 'set RM:MixBus/Input/Output/Level {} {} {}\n'.format(InputStates[input_], OutputStates[output], int(temp_value * 100))
            self.__SetHelper('MixingBusLevel', MixingBusLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixingBusLevel')

    def UpdateMixingBusLevel(self, value, qualifier):

        InputStates = {
            'Bluetooth L':  '0',
            'Bluetooth R':  '1',
            'AUX 1':        '2',
            'AUX 2':        '3',
            'SIP (VoIP) 1': '4',
            'SIP (VoIP) 2': '5',
            'USB L':        '6',
            'USB R':        '7',
            'Mic 1':        '8',
            'Mic 2':        '9',
            'Dante':        '10'
        }
        input_ = qualifier['Input']

        OutputStates = {
            'Bluetooth L':  '0',
            'Bluetooth R':  '1',
            'AUX 1':        '2',
            'AUX 2':        '3',
            'SIP (VoIP) 1': '4',
            'SIP (VoIP) 2': '5',
            'USB L':        '6',
            'USB R':        '7',
            'Speaker L':    '8',
            'Speaker R':    '9'
        }
        output = qualifier['Output']

        if input_ in InputStates and output in OutputStates:
            MixingBusLevelCmdString = 'get RM:MixBus/Input/Output/Level {} {}\n'.format(InputStates[input_], OutputStates[output])
            self.__UpdateHelper('MixingBusLevel', MixingBusLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixingBusLevel')

    def __MatchMixingBusLevel(self, match, tag):

        InputStates = {
            '0': 'Bluetooth L',
            '1': 'Bluetooth R',
            '2': 'AUX 1',
            '3': 'AUX 2',
            '4': 'SIP (VoIP) 1',
            '5': 'SIP (VoIP) 2',
            '6': 'USB L',
            '7': 'USB R',
            '8': 'Mic 1',
            '9': 'Mic 2',
            '10': 'Dante'
        }

        OutputStates = {
            '0': 'Bluetooth L',
            '1': 'Bluetooth R',
            '2': 'AUX 1',
            '3': 'AUX 2',
            '4': 'SIP (VoIP) 1',
            '5': 'SIP (VoIP) 2',
            '6': 'USB L',
            '7': 'USB R',
            '8': 'Speaker L',
            '9': 'Speaker R'
        }

        qualifier = {
            'Input': InputStates[match.group(1).decode()],
            'Output': OutputStates[match.group(2).decode()],
        }

        if int(match.group(3).decode()) == -32768:
            value = -138.01
        else: 
            value = int(match.group(3).decode()) / 100
        if -138.01 <= value <= 0:
            self.WriteStatus('MixingBusLevel', value, qualifier)

    def SetNearEndOutputFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Analog Speaker 1': '0',
            'Analog Speaker 2': '1',
            'Dante Speaker 1':  '2',
            'Dante Speaker 2':  '3'
            }

        ValueConstraints = {
            'Min' : -138.01,
            'Max' : 10
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            temp_value = -327.68 if value == -138.01 else value
            NearEndOutputFaderLevelCmdString = 'set RM:NeOut_Fader/Ch/Level {} 0 {}\n'.format(
                                                  ChannelStates[channel_val], int(temp_value * 100))  
            self.__SetHelper('NearEndOutputFaderLevel', NearEndOutputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndOutputFaderLevel')

    def UpdateNearEndOutputFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Analog Speaker 1': '0',
            'Analog Speaker 2': '1',
            'Dante Speaker 1':  '2',
            'Dante Speaker 2':  '3'
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            NearEndOutputFaderLevelCmdString = 'get RM:NeOut_Fader/Ch/Level {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('NearEndOutputFaderLevel', NearEndOutputFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateNearEndOutputFaderLevel')

    def __MatchNearEndOutputFaderLevel(self, match, tag):

        ChannelStates = {
            '0': 'Analog Speaker 1',
            '1': 'Analog Speaker 2',
            '2': 'Dante Speaker 1',
            '3': 'Dante Speaker 2'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        if int(match.group(2).decode()) == -32768:
            value = -138.01
        else: 
            value = int(match.group(2).decode()) / 100
        if -138.01 <= value <= 10:
            self.WriteStatus('NearEndOutputFaderLevel', value, qualifier)
        else:
            self.Error(['Near End Output Fader Level: Invalid/unexpected response'])

    def SetNearEndOutputFaderMute(self, value, qualifier):

        ChannelStates = {
            'Analog Speaker 1': '0',
            'Analog Speaker 2': '1',
            'Dante Speaker 1':  '2',
            'Dante Speaker 2':  '3'
            }

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        channel_val = qualifier['Channel']
        if value in ValueStateValues and channel_val in ChannelStates:
            NearEndOutputFaderMuteCmdString = 'set RM:NeOut_Fader/Ch/On {} 0 {}\n'.format(
                                            ChannelStates[channel_val], ValueStateValues[value])  
            self.__SetHelper('NearEndOutputFaderMute', NearEndOutputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNearEndOutputFaderMute')

    def UpdateNearEndOutputFaderMute(self, value, qualifier):

        ChannelStates = {
            'Analog Speaker 1': '0',
            'Analog Speaker 2': '1',
            'Dante Speaker 1':  '2',
            'Dante Speaker 2':  '3'
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            NearEndOutputFaderMuteCmdString = 'get RM:NeOut_Fader/Ch/On {} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('NearEndOutputFaderMute', NearEndOutputFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateNearEndOutputFaderMute')

    def __MatchNearEndOutputFaderMute(self, match, tag):

        ChannelStates = {
            '0': 'Analog Speaker 1',
            '1': 'Analog Speaker 2',
            '2': 'Dante Speaker 1',
            '3': 'Dante Speaker 2'
            }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {}
        qualifier['Channel'] = ChannelStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('NearEndOutputFaderMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.RunModeDisabled:
            self.Send('devstatus runmode\n')

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.RunModeDisabled:
                self.Send('devstatus runmode\n')

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

        self.RunModeDisabled = True

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