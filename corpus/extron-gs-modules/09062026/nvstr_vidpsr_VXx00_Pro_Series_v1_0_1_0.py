# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
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
        self.Models = {
            'VX2000 Pro': self.nvstr_29_17274_2000,
            'VX1000 Pro': self.nvstr_29_17274_other,
            'VX600 Pro': self.nvstr_29_17274_other,
            'VX400 Pro': self.nvstr_29_17274_other
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'BrightnessStatus': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Heartbeat': { 'Status': {}},
            'Input': {'Parameters':['Layer'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'ScreenBrightness': { 'Status': {}},
            'VideoMute': { 'Status': {}}
        }

        if self.ConnectionType == 'Ethernet':
            reply_str = b'\xAA\x55\x01\x00\x00\xFE\x00{6}\x02\x00{3}\x02[\x00-\xFF]{3}'
        else:
            reply_str = b'\xAA\x55\x01\x00{17}[\x00-\xFF]{2}'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(reply_str), self.__MatchHeartbeat, None)
            self.AddMatchString(re.compile(b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x02\x02\x00([\x00-\x64])[\x00-\xFF]{3}'), self.__MatchBrightnessStatus, None)
            self.AddMatchString(re.compile(b'\xAA\x55\x00\x00\x00\xFE\x00\x00\x00\x00\x00\x00\x05\x00\x00\x01\x01\x00([\x00-\x02])[\x00-\xFF]{2}'), self.__MatchDeviceStatus, None)
            
    def __calculate_checksum(self, cmd_string):

        chk_sum = 0
        for cnt in range(0, len(cmd_string)):
            chk_sum += cmd_string[cnt]
        chk_sum += 0x5555
        chk_sum_high = chk_sum >> 8
        chk_sum_low = chk_sum & 0xFF
        return pack('B', chk_sum_high), pack('B', chk_sum_low)
    
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x55\xAA\x00\x00\xFE\xFF\x00\x00\x00\x00\x01\x00\x86\x00\x00\x02\x01\x00\x58\x34\x58',
            'Off':  b'\x55\xAA\x00\x00\xFE\xFF\x00\x00\x00\x00\x01\x00\x86\x00\x00\x02\x01\x00\x00\xDC\x57'
            }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateBrightnessStatus(self, value, qualifier):
    
        BrightnessStatusCmdString = b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x02\x02\x00\x66\x56'
        self.__UpdateHelper('BrightnessStatus', BrightnessStatusCmdString, value, qualifier)

    def __MatchBrightnessStatus(self, match, tag):

        value = ord(match.group(1))
        if 0 <= value <= 100:
            self.WriteStatus('BrightnessStatus', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x01\x01\x00\x5A\x56'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Independent Mode',
            b'\x01': 'Primary Device',
            b'\x02': 'Backup Device'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x55\xAA\x00\x00\xFE\xFF\x00\x00\x00\x00\x01\x00\x50\x00\x20\x02\x01\x00\x02\xC8\x57',
            'Off': b'\x55\xAA\x00\x00\xFE\xFF\x00\x00\x00\x00\x01\x00\x50\x00\x20\x02\x01\x00\x00\xC6\x57'
            }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateHeartbeat(self, value, qualifier):

        if self.ConnectionType == 'Ethernet':
            HeartbeatCommandCmdString = b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x02\x00\x57\x56'
        else:
            HeartbeatCommandCmdString = b'\x55\xAA\x00\x14\xFE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x02\x02\x00\x6D\x56'
        self.__UpdateHelper('Heartbeat', HeartbeatCommandCmdString, value, qualifier)

    def __MatchHeartbeat(self, match, tag):

        self.WriteStatus('Heartbeat', 'Connected', None)

    def SetInput(self, value, qualifier):
    
        layer = qualifier['Layer']

        if 1 <= int(layer) <= self.layers and value in self.InputStateValues:
            payload = b''.join([b'\x00\x3E\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x00\x02\x13\x02\x00',  self.LayerStates[layer], self.InputStateValues[value]])
            checksum_high, checksum_low = self.__calculate_checksum(payload)
            InputCmdString = b''.join([b'\x55\xAA', payload, checksum_low, checksum_high])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x00\xBA\x56',
            '2':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x01\xBB\x56',
            '3':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x02\xBC\x56',
            '4':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x03\xBD\x56',
            '5':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x04\xBE\x56',
            '6':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x05\xBF\x56',
            '7':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x06\xC0\x56',
            '8':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x07\xC1\x56',
            '9':  b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x08\xC2\x56',
            '10': b'\x55\xAA\x00\x00\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x01\x51\x13\x01\x00\x09\xC3\x56'
            }

        if 1 <= int(value) <= 10:
            PresetRecallCmdString = ValueStateValues[value]
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetScreenBrightness(self, value, qualifier):

        if 0 <= value <= 255:
            payload = b''.join([b'\x00\x00\xFE\xFF\x01\xFF\xFF\xFF\x01\x00\x01\x00\x00\x02\x01\x00',
                                pack('B', value)])
            checksum_high, checksum_low = self.__calculate_checksum(payload)
            ScreenBrightnessCmdString = b''.join([b'\x55\xAA', payload, checksum_low, checksum_high])
            self.__SetHelper('ScreenBrightness', ScreenBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenBrightness')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x55\xAA\x00\x00\xFE\xFF\x00\x00\x00\x00\x01\x00\x50\x00\x20\x02\x01\x00\x01\xC7\x57',
            'Off': b'\x55\xAA\x00\x00\xFE\xFF\x00\x00\x00\x00\x01\x00\x50\x00\x20\x02\x01\x00\x00\xC6\x57'
            }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

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

    def nvstr_29_17274_2000(self):

        self.layers = 12
        self.LayerStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C'
            }

        self.InputStateValues = {
            'HDMI 1': b'\x01',
            'HDMI 2': b'\x02',
            'HDMI 3': b'\x03',
            'HDMI 4': b'\x04',
            'HDMI 5': b'\x05',
            'HDMI 6': b'\x06',
            'DisplayPort': b'\x08',
            'SDI': b'\x09',
            'USB': b'\x0B',
            'OPT 1': b'\x0D',
            'OPT 2': b'\x0E'
            }

    def nvstr_29_17274_other(self):

        self.layers = 6
        self.LayerStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06'
            }

        self.InputStateValues = {
            'HDMI 1': b'\x01',
            'HDMI 2': b'\x02',
            'HDMI 3': b'\x03',
            'SDI': b'\x09',
            'USB': b'\x0B',
            'OPT': b'\x0D'
            }
        
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()