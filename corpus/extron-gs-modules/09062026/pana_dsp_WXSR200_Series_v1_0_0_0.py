from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import hashlib
from struct import pack
from binascii import hexlify

from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

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
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Status': { 'Status': {}},
            'Mic': {'Parameters':['Mic'], 'Status': {}},
            'MicAudioLevel': {'Parameters':['Mic'], 'Status': {}},
            'MicBatteryLevel': {'Parameters':['Mic'], 'Status': {}},
            'MicConnectionAntenna': {'Parameters':['Mic'], 'Status': {}},
            'MicMute': {'Parameters':['Mic'], 'Status': {}},
            'MicRFLevel': {'Parameters':['Mic'], 'Status': {}},
            'MicVolume': {'Parameters':['Mic'], 'Status': {}},
            'OperationMode': { 'Status': {}},
            'WirelessAntenna': {'Parameters':['Antenna'], 'Status': {}},
            'WirelessReceiver': { 'Status': {}},
            'WirelessReceiverExtended': {'Parameters':['Receiver'], 'Status': {}},
        }

        self._authenticated = True
        self._mic_states = [False for _ in range(16)]
        self._mic_battery = [False for _ in range(16)]

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SR2\x00{2}\x14\x00\x01\xE0\x02\x00{6}\x00\x00\x00\x20\x00{24}([0-9A-Za-z]{8})'), self.__GenerateAuthentication, None)
            self.AddMatchString(re.compile(b'SR2\x00{2}\x14\x00\x02\xF0\x02'), self.__MatchAuthentication, None)

            self.AddMatchString(re.compile(b'SR2\x00{2}\x14\x00\x03\x00\x22\x00{9}\xB8\x00{32}([\x00\x01\x0F]{4})([\x00\x01])\x00{3}([\x00\x01\x0F\x80\x81\x8F]{8})(([\x00-\x63\xFF][\x00\x01\x0F][\x00\x01\x02][\x00-\x3F][\x00-\xFF]{2}[\x00-\x07][\x00-\xFF]){16})'), self.__MatchStatus, None)
            self.AddMatchString(re.compile(b'SR2\x00{2}\x14\x00[\x04\x05]\x01\x52\x00{9}\\x2A\x00{26}([\x00-\xFF]{16})'), self.__MatchMicVolume, None)
            self.AddMatchString(re.compile(b'SR2\x00{2}\x14\x00\x06\x01\x42\x00{9}\x1A\x00{24}([\x00\x01])'), self.__MatchOperationMode, None)

    def BuildCommand(self, trans_num, cmd_id, cmd_len, data=b''):

        header = b'SR2\x00\x00\x14'
        trans_num = pack('>H', trans_num)
        reserved = self.ReservedBytes(6)
        cmd_length = pack('>I', cmd_len)
        data_reserved = self.ReservedBytes(24)
        return b''.join([header, trans_num, cmd_id, reserved, cmd_length, data_reserved, data])

    def ReservedBytes(self, number):

        temp = b''
        for _ in range(number):
            temp = b''.join([temp, b'\x00'])
        return temp

    def VolumeSetting(self, value, mic):
        temp = self.ReservedBytes(16)
        return b''.join([temp[:mic], pack('B', value), temp[mic+1:]])

    def __ConnectionRequest(self):
        today= datetime.now()
        data = today.strftime('%Y%m%d%H%M%S').encode()

        self.Send(self.BuildCommand(0x01, b'\xE0\x01', 0x26, data))

    def __GenerateAuthentication(self, match, tag):
        if self.devicePassword is None:
            self.MissingCredentialsLog('Password')
        else:
            rand_num = match.group(1).decode
            data = '{}:{}'.format(self.devicePassword, rand_num)
            code_hash = hashlib.md5(data.encode())
            md5 = hexlify(code_hash.digest())
            self.Send(self.BuildCommand(0x02, b'\xF0\x01', 0x38, md5))

    def __MatchAuthentication(self, match, tag):
        self._authenticated = True

    def UpdateStatus(self, value, qualifier):
        self.__UpdateHelper('Status', self.BuildCommand(0x03, b'\x00\x21', 0x18), value, qualifier)

    def __MatchStatus(self, match, tag):


        state = {
            0x00: 'Power Off',
            0x80: 'Power Off',
            0x01: 'Connected',
            0x81: 'Connected',
            0x0F: 'Connection Error',
            0x8F: 'Connection Error'
        }

        mode = {
            0x00: 'Local',
            0x01: 'Remote'
        }

        battery_level = {
            0x00: 'Low',
            0x01: 'Mid',
            0x02: 'High'
        }

        mute = {
            0x80: 'On',
            0x00: 'Off'
        }


        wireless_rx = match.group(1)
        
        self.WriteStatus('WirelessReceiver', state[wireless_rx[0]], None)

        receiver = 1
        for value in wireless_rx[1:]:
            self.WriteStatus('WirelessReceiverExtended', state[value], {'Receiver': str(receiver)})
            receiver += 1

        operation_mode = match.group(2)[0]
        self.WriteStatus('OperationMode', mode[operation_mode], None)

        antenna = 1
        for value in match.group(3):
            self.WriteStatus('WirelessAntenna', state[value], {'Antenna': str(antenna)})
            antenna += 1

        mics = match.group(4)
        for mic in range(16):

            volume = mics[7 + (mic * 8)]
            self._mic_states[mic] = True if volume != 0xFF else False
            self._mic_battery[mic] = True if state[mics[1 + (mic * 8)]] == 'Connected' else False

            if self._mic_states[mic]:
                self.WriteStatus('Mic', state[mics[1 + (mic * 8)]], {'Mic': str(mic + 1)})
            else:
                self.WriteStatus('Mic', 'Unused', {'Mic': str(mic + 1)})

            if self._mic_battery[mic]:
                self.WriteStatus('MicBatteryLevel', battery_level[mics[2 + (mic * 8)]], {'Mic': str(mic + 1)})
            else:
                self.WriteStatus('MicBatteryLevel', 'Off', {'Mic': str(mic + 1)})

            self.WriteStatus('MicRFLevel', mics[3 + (mic * 8)] & 0x3F, {'Mic': str(mic + 1)})

            value = mics[4 + (mic * 8):6 + (mic * 8)]
            self.WriteStatus('MicAudioLevel', (256 * value[0]) + value[1], {'Mic': str(mic + 1)})

            self.WriteStatus('MicConnectionAntenna', str(mics[6 + (mic * 8)] + 1), {'Mic': str(mic + 1)})

            self.WriteStatus('MicMute', mute[volume & 0x80], {'Mic': str(mic + 1)})
            self.WriteStatus('MicVolume', volume & 0x3F, {'Mic': str(mic + 1)})

    def SetMicMute(self, value, qualifier):


        MicStates = {
            '1'  : 0x0001,
            '2'  : 0x0002,
            '3'  : 0x0004,
            '4'  : 0x0008,
            '5'  : 0x0010,
            '6'  : 0x0020,
            '7'  : 0x0040,
            '8'  : 0x0080,
            '9'  : 0x0100,
            '10' : 0x0200,
            '11' : 0x0400,
            '12' : 0x0800,
            '13' : 0x1000,
            '14' : 0x2000,
            '15' : 0x4000,
            '16' : 0x8000
        }



        ValueStateValues = {
            'On'  : 0x80,
            'Off' : 0x00
        }

        mic = qualifier['Mic']
        mode = self.ReadStatus('OperationMode', None)
        volume = self.ReadStatus('MicVolume', qualifier)
        temp = int(mic)
        volume_setting = self.VolumeSetting(volume + ValueStateValues[value], temp-1)
        data = b''.join([pack('>H', MicStates[mic]), volume_setting])

        if mode == 'Remote':
            self.__SetHelper('MicMute', self.BuildCommand(0x04, b'\x01\x50',0x2A, data), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def SetMicVolume(self, value, qualifier):


        MicStates = {
            '1'  : 0x0001,
            '2'  : 0x0002,
            '3'  : 0x0004,
            '4'  : 0x0008,
            '5'  : 0x0010,
            '6'  : 0x0020,
            '7'  : 0x0040,
            '8'  : 0x0080,
            '9'  : 0x0100,
            '10' : 0x0200,
            '11' : 0x0400,
            '12' : 0x0800,
            '13' : 0x1000,
            '14' : 0x2000,
            '15' : 0x4000,
            '16' : 0x8000
        }

        ValueStateValues = {
            'On'  : 0x80,
            'Off' : 0x00
        }

        mic = qualifier['Mic']
        mode = self.ReadStatus('OperationMode', None)
        mute = self.ReadStatus('MicMute', qualifier)
        temp = int(mic)
        volume_setting = self.VolumeSetting(ValueStateValues[mute] + value, temp-1)
        data = b''.join([pack('>H', MicStates[mic]), volume_setting])

        if 0 <= value <= 63 and mode == 'Remote':
            self.__SetHelper('MicVolume', self.BuildCommand(0x05, b'\x01\x50',0x2A, data), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicVolume')

    def __MatchMicVolume(self, match, tag):


        mute = {
            0x80: 'On',
            0x00: 'Off'
        }

        mic = 1
        for m in match.group(1):
            self.WriteStatus('MicMute', mute[m & 0x80], {'Mic': str(mic)})
            self.WriteStatus('MicVolume', m & 0x3F, {'Mic': str(mic)})
            mic += 1

    def SetOperationMode(self, value, qualifier):


        ValueStateValues = {
            'Local'  : b'\x00\x00',
            'Remote' : b'\x00\x01'
        }

        self.__SetHelper('OperationMode', self.BuildCommand(0x06, b'\x01\x40',0x1A, ValueStateValues[value]), value, qualifier)

    def __MatchOperationMode(self, match, tag):


        mode = {
            0x00: 'Local',
            0x01: 'Remote'
        }

        self.WriteStatus('OperationMode', mode[match.group(1)[0]], None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self._authenticated:
            self.Send(commandstring)
            #print(commandstring)
        else:
            self.Error(['Device not authenticated.'])

    def __UpdateHelper(self, command, commandstring, value, qualifier):


        if self._authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)
        else:
            self.Error(['Device not authenticated.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.__ConnectionRequest()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False


        self._authenticated = False
        self._mic_states = [False for _ in range(16)]
        self._mic_battery = [False for _ in range(16)]


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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

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

