from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
from struct import pack
from functools import reduce
from operator import xor


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

        self.EnableIR = False

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\xAC(\x08\x86|\x09\x87|\x0A\x84|\x0C\x82|\x0B\x85|\x01\x8F|\x05\x8B|\x03\x8D)\xA5\xA5'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x18(\x00\x3A|\x01\x3B|\x02\x38|\x03\x39)\xA5\xA5'), self.__MatchPower, None)
            self.AddMatchString(compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x44([\x00-\x64])[\x02-\x79]\xA5\xA5'), self.__MatchVolumeStatus, None)
            self.AddMatchString(compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x16(\x01\x35|\x02\x36)\xA5\xA5'), self.__MatchError, None)

    def CmdString(self, Payload):
        Payload += reduce(xor, Payload).to_bytes(1, 'big')
        PayloadLen = len(Payload)
        return pack('>8B{}sH'.format(PayloadLen), 0x0E, PayloadLen + 10, 0, 0, 5, PayloadLen + 1, 0, 0x0C, Payload, 0xA5A5)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\x20\x3A\x00',
            'Zoom 14:9': b'\x20\x3A\x01',
            'Zoom 16:9m': b'\x20\x3A\x02',
            'Subtitle Zoom': b'\x20\x3A\x03',
            'Wide Screen': b'\x20\x3A\x04',
            'Super Zoom/Auto Zoom': b'\x20\x3A\x05',
            'Auto': b'\x20\x3A\x07',
            'Unscaled': b'\x20\x3A\x08',
            'Cinema 21:9': b'\x20\x3A\x09',
            'Cinema 21:9 Subtitle': b'\x20\x3A\x0A'
        }

        AspectRatioCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x20\x46\x01',
            'Off': b'\x20\x46\x00'
        }

        AudioMuteCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x20\x1B\xFF\xFF\xFF\x01\xFF',
            'Down': b'\x20\x1B\xFF\xFF\xFF\x02\xFF'
        }

        ChannelCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': b'\x20\xAC\x08',
            'HDMI 2': b'\x20\xAC\x09',
            'HDMI 3': b'\x20\xAC\x0A',
            'HDMI 4': b'\x20\xAC\x0C',
            'USB': b'\x20\xAC\x0B',
            'TV': b'\x20\xAC\x01',
            'YPbPr': b'\x20\xAC\x05',
            'SCART': b'\x20\xAC\x03'
        }

        InputCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.CmdString(b'\x21\xAC')
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x08\x86': 'HDMI 1',
            b'\x09\x87': 'HDMI 2',
            b'\x0A\x84': 'HDMI 3',
            b'\x0C\x82': 'HDMI 4',
            b'\x0B\x85': 'USB',
            b'\x01\x8F': 'TV',
            b'\x05\x8B': 'YPbPr',
            b'\x03\x8D': 'SCART'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x20\x18\x01',
            'Off': b'\x20\x18\x00',
        }

        PowerCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.CmdString(b'\x21\x18')
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01\x3B': 'On',
            b'\x00\x3A': 'Off',
            b'\x02\x38': 'Warming Up',
            b'\x03\x39': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x20\x34\x01',
            'Off': b'\x20\x34\x00'
        }

        VideoMuteCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x20\x45\x01',
            'Down': b'\x20\x45\x00'
        }

        VolumeCmdString = self.CmdString(ValueStateValues[value])
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = self.CmdString(b'\x21\x44')
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('VolumeStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if not self.EnableIR:
            self.EnableIR = True
            self.Send(b'\x0E\x0F\x00\x05\x06\x00\x0C\x20\xA3\x01\x00\x82\xA5\xA5')
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

            if not self.EnableIR:
                self.EnableIR = True
                self.Send(b'\x0E\x0F\x00\x05\x06\x00\x0C\x20\xA3\x01\x00\x82\xA5\xA5')
            self.Send(commandstring)


    def __MatchError(self, match, tag):

        Errors = {
            b'\x01\x35' : "This command's payload is malformed or has in invalid checksum.",
            b'\x02\x36' : "This command is not implemented for this TV set."
        }
        self.Error([Errors[match.group(1)]])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.EnableIR = False
    
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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
