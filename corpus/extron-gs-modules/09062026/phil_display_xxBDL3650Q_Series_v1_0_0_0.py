from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
from struct import pack, unpack

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': {'Parameters':['Type'], 'Status': {}},
        }

        self.LenDict = {
            'AspectRatio':  6,
            'AudioMute':    6,
            'AVMute':       6,
            'Channel':      7,
            'Freeze':       6,
            'Input':        9,
            'Power':        6,
            'Volume':       7
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value)
        else:
            self.Error(['Device ID Parameter is set to wrong value.'])

    def calChkSum(self, command_string):
        ChkSum = 0
        for i in range(0, len(command_string)):
            ChkSum = ChkSum ^ command_string[i]
        return ChkSum.to_bytes(1, 'big')
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':      0x00,
            'Custom':   0x01,
            '1:1':      0x02,
            'Full':     0x03,
            '21:9':     0x04,
            'Dynamic':  0x05,
            '16:9':     0x06
            }

        if value in ValueStateValues:
            AspectRatioCmdString = pack('5B', 0x06, self._DeviceID, 0x00, 0x3A, ValueStateValues[value])
            ChkSum = self.calChkSum(AspectRatioCmdString)
            AspectRatioCmdString = b''.join([AspectRatioCmdString, ChkSum])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0x3B)
        ChkSum = self.calChkSum(AspectRatioCmdString)
        AspectRatioCmdString = b''.join([AspectRatioCmdString, ChkSum])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x00: '4:3',
                    0x01: 'Custom',
                    0x02: '1:1',
                    0x03: 'Full',
                    0x04: '21:9',
                    0x05: 'Dynamic',
                    0x06: '16:9'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
            }

        if value in ValueStateValues:
            AudioMuteCmdString = pack('5B', 0x06, self._DeviceID, 0x00, 0x47, ValueStateValues[value])
            ChkSum = self.calChkSum(AudioMuteCmdString)
            AudioMuteCmdString = b''.join([AudioMuteCmdString, ChkSum])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0x46)
        ChkSum = self.calChkSum(AudioMuteCmdString)
        AudioMuteCmdString = b''.join([AudioMuteCmdString, ChkSum])
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'On',
                    0x00: 'Off'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
            }

        if value in ValueStateValues:
            AVMuteCmdString = pack('5B', 0x06, self._DeviceID, 0x00, 0x7B, ValueStateValues[value])
            ChkSum = self.calChkSum(AVMuteCmdString)
            AVMuteCmdString = b''.join([AVMuteCmdString, ChkSum])
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0x7A)
        ChkSum = self.calChkSum(AVMuteCmdString)
        AVMuteCmdString = b''.join([AVMuteCmdString, ChkSum])
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'On',
                    0x00: 'Off'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetChannel(self, value, qualifier):

        if 0 <= value <= 9999:
            high, low = divmod(value, 0x100)
            ChannelCmdString = pack('6B', 0x07, self._DeviceID, 0x00, 0xC2, high, low)
            ChkSum = self.calChkSum(ChannelCmdString)
            ChannelCmdString = b''.join([ChannelCmdString, ChkSum])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0xC1)
        ChkSum = self.calChkSum(ChannelCmdString)
        ChannelCmdString = b''.join([ChannelCmdString, ChkSum])
        res = self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)
        if res:
            try:
                value = int.from_bytes(res[4:6], "big")
                self.WriteStatus('Channel', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Channel: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
            }

        if value in ValueStateValues:
            FreezeCmdString = pack('5B', 0x06, self._DeviceID, 0x00, 0x77, ValueStateValues[value])
            ChkSum = self.calChkSum(FreezeCmdString)
            FreezeCmdString = b''.join([FreezeCmdString, ChkSum])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0x76)
        ChkSum = self.calChkSum(FreezeCmdString)
        FreezeCmdString = b''.join([FreezeCmdString, ChkSum])
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x01: 'On',
                    0x00: 'Off'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'USB 1':    0x0C,
            'USB 2':    0x08,
            'DVI-I':    0x0E,
            'HDMI 1':   0x0D,
            'HDMI 2':   0x06
            }

        if value in ValueStateValues:
            InputCmdString = pack('8B', 0x09, self._DeviceID, 0x00, 0xAC, ValueStateValues[value], 0x09, 0x01, 0x00)
            ChkSum = self.calChkSum(InputCmdString)
            InputCmdString = b''.join([InputCmdString, ChkSum])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0xAD)
        ChkSum = self.calChkSum(InputCmdString)
        InputCmdString = b''.join([InputCmdString, ChkSum])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x0C: 'USB 1',
                    0x08: 'USB 2',
                    0x0E: 'DVI-I',
                    0x0D: 'HDMI 1',
                    0x06: 'HDMI 2'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x01
            }

        if value in ValueStateValues:
            PowerCmdString = pack('5B', 0x06, self._DeviceID, 0x00, 0x18, ValueStateValues[value])
            ChkSum = self.calChkSum(PowerCmdString)
            PowerCmdString = b''.join([PowerCmdString, ChkSum])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0x19)
        ChkSum = self.calChkSum(PowerCmdString)
        PowerCmdString = b''.join([PowerCmdString, ChkSum])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02: 'On',
                    0x01: 'Off'
                    }

                value = ValueStateValues[res[4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        TypeStates = {
            'Audio Out':    1,
            'Speaker':      2
            }

        if qualifier['Type'] in TypeStates and 0 <= value <= 100:
            if TypeStates[qualifier['Type']] == 1:
                VolumeCmdString = pack('6B', 0x07, self._DeviceID, 0x00, 0x44, 0xFF, value)
                ChkSum = self.calChkSum(VolumeCmdString)
                VolumeCmdString = b''.join([VolumeCmdString, ChkSum])
            elif TypeStates[qualifier['Type']] == 2:
                VolumeCmdString = pack('6B', 0x07, self._DeviceID, 0x00, 0x44, value, 0xFF)
                ChkSum = self.calChkSum(VolumeCmdString)
                VolumeCmdString = b''.join([VolumeCmdString, ChkSum])
            else:
                self.Discard('Invalid Command for SetVolume')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        TypeStates = {
            'Audio Out':    1,
            'Speaker':      2
            }

        if qualifier['Type'] in TypeStates:
            VolumeCmdString = pack('4B', 0x05, self._DeviceID, 0x00, 0x45)
            ChkSum = self.calChkSum(VolumeCmdString)
            VolumeCmdString = b''.join([VolumeCmdString, ChkSum])
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    if 0 <= int(res[5]) <= 100:
                        value = int(res[5])
                        self.WriteStatus('Volume', value, {'Type': 'Audio Out'})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Volume Audio Out: Invalid/unexpected response'])
                try:
                    if 0 <= int(res[4]) <= 100:
                        value = int(res[4])
                        self.WriteStatus('Volume', value, {'Type': 'Speaker'})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Volume Speaker: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledged',
            b'\x18': 'Not Available',
        }

        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=self.LenDict[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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