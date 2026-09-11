from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


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
            'HDMIOutput': {'Status': {}},
            'LoadCustomPreset': {'Status': {}},
            'MainInput': {'Status': {}},
            'MainVolume': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'SaveCustomPreset': {'Status': {}},
            'SpeakerSwitch': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Mute': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}},
            'Zone3Input': {'Status': {}},
            'Zone3Mute': {'Status': {}},
            'Zone3Power': {'Status': {}},
            'Zone3Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02\x07\xA8\x82\x00([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])[\x00-\xFF][\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02\x06\xA8\x92\x00\x01([\x00-\xFF])(\x00|\x80)[\x00-\xFF]'), self.__MatchMainVolume, None)
            self.AddMatchString(re.compile(b'\x02\x07\xA8\x82\x01([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])[\x00-\xFF][\x00-\xFF]'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'\x02\x06\xA8\x92\x01\x01([\x00-\xFF])(\x00|\x80)[\x00-\xFF]'), self.__MatchZone2Volume, None)
            self.AddMatchString(re.compile(b'\x02\x07\xA8\x82\x02([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])[\x00-\xFF][\x00-\xFF]'), self.__MatchZone3Power, None)
            self.AddMatchString(re.compile(b'\x02\x06\xA8\x92\x02\x01([\x00-\xFF])(\x00|\x80)[\x00-\xFF]'), self.__MatchZone3Volume, None)

    def CalChecksum(self, commandString):

        CheckSum = 0
        for i in commandString:
            CheckSum = CheckSum + i
        CheckSum = 4096 - CheckSum
        CheckSum &= 255
        return CheckSum

    def SetHDMIOutput(self, value, qualifier):

        HDMIOutputState = {
            'A': b'\x02\x03\xA0\x45\x00\x18',
            'B': b'\x02\x03\xA0\x45\x01\x17',
            'A+B': b'\x02\x03\xA0\x45\x02\x16',
            'Off': b'\x02\x03\xA0\x45\x03\x15'
            }

        HDMIOutputCmdString = HDMIOutputState[value]
        self.__SetHelper('HDMIOutput', HDMIOutputCmdString, value, qualifier)

    def SetLoadCustomPreset(self, value, qualifier):

        ValueStateValues = {
            'Scene 1': b'\x02\x03\xA0\x73\x01\xE9',
            'Scene 2': b'\x02\x03\xA0\x73\x02\xE8',
            'Scene 3': b'\x02\x03\xA0\x73\x03\xE7',
            'Scene 4': b'\x02\x03\xA0\x73\x04\xE6',
            'Off': b'\x02\x03\xA0\x73\x00\xEA'
        }

        LoadCustomPresetCmdString = ValueStateValues[value]
        self.__SetHelper('LoadCustomPreset', LoadCustomPresetCmdString, value, qualifier)

    def SetMainInput(self, value, qualifier):

        MainInputState = {
            'Video': b'\x02\x04\xA0\x42\x00\x10\x0A',
            'SA-CD/CD': b'\x02\x04\xA0\x42\x00\x02\x18',
            'BD/DVD': b'\x02\x04\xA0\x42\x00\x1B\xFF',
            'SAT/CATV': b'\x02\x04\xA0\x42\x00\x16\x04',
            'Game': b'\x02\x04\xA0\x42\x00\x1C\xFE',
            'Tuner': b'\x02\x04\xA0\x42\x00\x00\x1A',
            'FM': b'\x02\x04\xA0\x42\x00\x2E\xEC',
            'AM': b'\x02\x04\xA0\x42\x00\x2F\xEB',
            'STB': b'\x02\x04\xA0\x42\x00\x3F\xDB',
            'AUX': b'\x02\x04\xA0\x42\x00\x0A\x10',
            'TV': b'\x02\x04\xA0\x42\x00\x1A\x00'
            }

        MainInputCmdString = MainInputState[value]
        self.__SetHelper('MainInput', MainInputCmdString, value, qualifier)

    def SetMainVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -92,
            'Max': 23
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value < 0:
                NumValue = pack('B', 256 + value)
            else:
                NumValue = pack('B', value)
            VolString = b'\x06\xA0\x52\x00\x01' + NumValue + b'\x00'
            CheckSum = self.CalChecksum(VolString)
            MainVolumeCmdString = b'\x02' + VolString + pack('B', CheckSum)
            self.__SetHelper('MainVolume', MainVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainVolume')

    def UpdateMainInput(self, value, qualifier):
        UpdatePower(value, qualifier)
        
    def UpdateMute(self, value, qualifier):
        UpdatePower(value, qualifier)
        
    def UpdateMainVolume(self, value, qualifier):

        MainVolumeCmdString = b'\x02\x04\xA0\x92\x00\x01\xC9'
        self.__UpdateHelper('MainVolume', MainVolumeCmdString, value, qualifier)

    def __MatchMainVolume(self, match, tag):

        value = match.group(1)[0]
        if 164 <= value <= 255:
            value -= 256
        elif value == 128:
            value = -92
        self.WriteStatus('MainVolume', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x02\x02\xA0\x30\x2E',
            'Down': b'\x02\x02\xA0\x31\x2D',
            'Left': b'\x02\x02\xA0\x33\x2B',
            'Right': b'\x02\x02\xA0\x32\x2C',
            'Enter': b'\x02\x02\xA0\x22\x3C',
            'Menu': b'\x02\x02\xA0\x2B\x33',
            'Return': b'\x02\x02\xA0\x35\x29',
            'Option': b'\x02\x02\xA0\x36\x28'
            }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteState = {
            'On': b'\x02\x04\xA0\x53\x00\x01\x08',
            'Off': b'\x02\x04\xA0\x53\x00\x00\x09'
            }

        MuteCmdString = MuteState[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x02\x04\xA0\x60\x00\x01\xFB',
            'Off': b'\x02\x04\xA0\x60\x00\x00\xFC'
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x02\x03\xA0\x82\x00\xDB'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            1: 'On',
            0: 'Off'
            }

        MainInputState = {
            b'\x10': 'Video',
            b'\x02': 'SA-CD/CD',
            b'\x1B': 'BD/DVD',
            b'\x16': 'SAT/CATV',
            b'\x1C': 'Game',
            b'\x2E': 'FM',
            b'\x2F': 'AM',
            b'\x3F': 'STB',
            b'\x0A': 'AUX',
            b'\x1A': 'TV'
            }

        MuteState = {
            2: 'On',
            0: 'Off'
            }

        value2 = MainInputState[match.group(1)]
        value1 = PowerState[match.group(3)[0] & 1]
        value3 = MuteState[match.group(3)[0] & 2]

        self.WriteStatus('Power', value1, None)
        self.WriteStatus('MainInput', value2, None)
        self.WriteStatus('Mute', value3, None)

    def SetSaveCustomPreset(self, value, qualifier):

        ValueStateValues = {
            'Scene 1': b'\x02\x03\xA0\x74\x01\xE8',
            'Scene 2': b'\x02\x03\xA0\x74\x02\xE7',
            'Scene 3': b'\x02\x03\xA0\x74\x03\xE6',
            'Scene 4': b'\x02\x03\xA0\x74\x04\xE5'
        }

        SaveCustomPresetCmdString = ValueStateValues[value]
        self.__SetHelper('SaveCustomPreset', SaveCustomPresetCmdString, value, qualifier)

    def SetSpeakerSwitch(self, value, qualifier):

        SpeakerSwitchState = {
            'A': b'\x02\x03\xA0\x48\x02\x13',
            'B': b'\x02\x03\xA0\x48\x03\x12',
            'A+B': b'\x02\x03\xA0\x48\x04\x11',
            'Off': b'\x02\x03\xA0\x48\x01\x14'
            }

        SpeakerSwitchCmdString = SpeakerSwitchState[value]
        self.__SetHelper('SpeakerSwitch', SpeakerSwitchCmdString, value, qualifier)

    def SetZone2Input(self, value, qualifier):

        Zone2InputState = {
            'Video': b'\x02\x04\xA0\x42\x01\x10\x09',
            'SA-CD/CD': b'\x02\x04\xA0\x42\x01\x02\x17',
            'BD/DVD': b'\x02\x04\xA0\x42\x01\x1B\xFE',
            'SAT/CATV': b'\x02\x04\xA0\x42\x01\x16\x03',
            'Game': b'\x02\x04\xA0\x42\x01\x1C\xFD',
            'Tuner': b'\x02\x04\xA0\x42\x01\x00\x19',
            'FM': b'\x02\x04\xA0\x42\x01\x2E\xEB',
            'AM': b'\x02\x04\xA0\x42\x01\x2F\xEA',
            'Source': b'\x02\x04\xA0\x42\x01\x0F\x0A',
            'STB': b'\x02\x04\xA0\x42\x01\x3F\xDA',
            'AUX': b'\x02\x04\xA0\x42\x01\x0A\x0F',
            'TV': b'\x02\x04\xA0\x42\x01\x1A\xFF'
            }

        Zone2InputCmdString = Zone2InputState[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):
        self.UpdateZone2Power(value, qualifier)

    def SetZone2Mute(self, value, qualifier):

        Zone2MuteState = {
            'On': b'\x02\x04\xA0\x53\x01\x01\x07',
            'Off': b'\x02\x04\xA0\x53\x01\x00\x08'
            }

        Zone2MuteCmdString = Zone2MuteState[value]
        self.__SetHelper('Zone2Mute', Zone2MuteCmdString, value, qualifier)

    def UpdateZone2Mute(self, value, qualifier):
        self.UpdateZone2Power(value, qualifier)

    def SetZone2Power(self, value, qualifier):

        Zone2PowerState = {
            'On': b'\x02\x04\xA0\x60\x01\x01\xFA',
            'Off': b'\x02\x04\xA0\x60\x01\x00\xFB'
            }

        Zone2PowerCmdString = Zone2PowerState[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = b'\x02\x03\xA0\x82\x01\xDA'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        Zone2PowerState = {
            1: 'On',
            0: 'Off'
            }

        Zone2InputState = {
            b'\x10': 'Video',
            b'\x02': 'SA-CD/CD',
            b'\x1B': 'BD/DVD',
            b'\x16': 'SAT/CATV',
            b'\x1C': 'Game',
            b'\x2E': 'FM',
            b'\x2F': 'AM',
            b'\x0F': 'Source',
            b'\x3F': 'STB',
            b'\x0A': 'AUX',
            b'\x1A': 'TV'
            }

        Zone2MuteState = {
            2: 'On',
            0: 'Off'
            }

        value2 = Zone2InputState[match.group(1)]
        value1 = Zone2PowerState[match.group(3)[0] & 1]
        value3 = Zone2MuteState[match.group(3)[0] & 2]

        self.WriteStatus('Zone2Power', value1, None)
        self.WriteStatus('Zone2Input', value2, None)
        self.WriteStatus('Zone2Mute', value3, None)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -92,
            'Max': 23
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value < 0:
                NumValue = pack('B', 256 + value)
            else:
                NumValue = pack('B', value)
            VolString = b'\x06\xA0\x52\x01\x01' + NumValue + b'\x00'
            CheckSum = self.CalChecksum(VolString)
            Zone2VolumeCmdString = b'\x02' + VolString + pack('B', CheckSum)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):

        Zone2VolumeCmdString = b'\x02\x04\xA0\x92\x01\x01\xC8'
        self.__UpdateHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)

    def __MatchZone2Volume(self, match, tag):

        value = match.group(1)[0]
        if 164 <= value <= 255:
            value -= 256
        elif value == 128:
            value = -92
        self.WriteStatus('Zone2Volume', value, None)

    def SetZone3Input(self, value, qualifier):

        Zone3InputState = {
            'Video': b'\x02\x04\xA0\x42\x02\x10\x08',
            'SA-CD/CD': b'\x02\x04\xA0\x42\x02\x02\x16',
            'Tuner': b'\x02\x04\xA0\x42\x02\x00\x18',
            'FM': b'\x02\x04\xA0\x42\x02\x2E\xEA',
            'AM': b'\x02\x04\xA0\x42\x02\x2F\xE9',
            'Source': b'\x02\x04\xA0\x42\x02\x0F\x09',
            'AUX': b'\x02\x04\xA0\x42\x02\x0A\x0E',
            'TV': b'\x02\x04\xA0\x42\x02\x1A\xFE'
            }

        Zone3InputCmdString = Zone3InputState[value]
        self.__SetHelper('Zone3Input', Zone3InputCmdString, value, qualifier)

    def UpdateZone3Input(self, value, qualifier):
        self.UpdateZone3Power(value, qualifier)

    def SetZone3Mute(self, value, qualifier):

        Zone3MuteState = {
            'On': b'\x02\x04\xA0\x53\x02\x01\x06',
            'Off': b'\x02\x04\xA0\x53\x02\x00\x07'
            }

        Zone3MuteCmdString = Zone3MuteState[value]
        self.__SetHelper('Zone3Mute', Zone3MuteCmdString, value, qualifier)

    def UpdateZone3Mute(self, value, qualifier):
        self.UpdateZone3Power(value, qualifier)

    def SetZone3Power(self, value, qualifier):

        Zone3PowerState = {
            'On': b'\x02\x04\xA0\x60\x02\x01\xF9',
            'Off': b'\x02\x04\xA0\x60\x02\x00\xFA'
            }

        Zone3PowerCmdString = Zone3PowerState[value]
        self.__SetHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def UpdateZone3Power(self, value, qualifier):

        Zone3PowerCmdString = b'\x02\x03\xA0\x82\x02\xD9'
        self.__UpdateHelper('Zone3Power', Zone3PowerCmdString, value, qualifier)

    def __MatchZone3Power(self, match, tag):

        Zone3PowerState = {
            1: 'On',
            0: 'Off'
            }

        Zone3InputState = {
            b'\x10': 'Video',
            b'\x02': 'SA-CD/CD',
            b'\x2E': 'FM',
            b'\x2F': 'AM',
            b'\x0F': 'Source',
            b'\x0A': 'AUX',
            b'\x1A': 'TV'
            }

        Zone3MuteState = {
            2: 'On',
            0: 'Off'
            }

        value2 = Zone3InputState[match.group(1)]
        value1 = Zone3PowerState[match.group(3)[0] & 1]
        value3 = Zone3MuteState[match.group(3)[0] & 2]

        self.WriteStatus('Zone3Power', value1, None)
        self.WriteStatus('Zone3Input', value2, None)
        self.WriteStatus('Zone3Mute', value3, None)

    def SetZone3Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -92,
            'Max': 23
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value < 0:
                NumValue = pack('B', 256 + value)
            else:
                NumValue = pack('B', value)
            VolString = b'\x06\xA0\x52\x02\x01' + NumValue + b'\x00'
            CheckSum = self.CalChecksum(VolString)
            Zone3VolumeCmdString = b'\x02' + VolString + pack('B', CheckSum)
            self.__SetHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone3Volume')

    def UpdateZone3Volume(self, value, qualifier):

        Zone3VolumeCmdString = b'\x02\x04\xA0\x92\x02\x01\xC7'
        self.__UpdateHelper('Zone3Volume', Zone3VolumeCmdString, value, qualifier)

    def __MatchZone3Volume(self, match, tag):

        value = match.group(1)[0]
        if 164 <= value <= 255:
            value -= 256
        elif value == 128:
            value = -92
        self.WriteStatus('Zone3Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
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

