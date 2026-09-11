from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x46(\x00\x64|\x01\x65)\xA5\xA5'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\xAC(\x08\x86|\x0C\x82|\x07\x89|\x03\x8D|\x05\x8B|\x0D\x83|\x0B\x85|\x01\x8F)\xA5\xA5'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x18(\x00\x3A|\x01\x3B|\x02\x38|\x03\x39)\xA5\xA5'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x44([\x00-\x64])[\x02-\x67]\xA5\xA5'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x16(\x01\x35|\x02\x36)\xA5\xA5'), self.__MatchError, None)

    def MakeCmdString(self, Payload):
        Payload += reduce(xor, Payload).to_bytes(1, 'big')
        Length = len(Payload)
        return pack('>8B{}sH'.format(Length), 0x0E, Length + 10, 0, 0, 5, Length + 1, 0, 0x0C, Payload, 0xA5A5)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\x20\x3A\x00',
            'Zoom 14:9': b'\x20\x3A\x01',
            'Zoom 16:9m': b'\x20\x3A\x02',
            'Subtitle Zoom': b'\x20\x3A\x03',
            'Wide Screen': b'\x20\x3A\x04',
            'Super Zoom / Auto Zoom': b'\x20\x3A\x05',
            'Auto': b'\x20\x3A\x07',
            'Unscaled': b'\x20\x3A\x08',
            'Cinema 21:9': b'\x20\x3A\x09',
            'Cinema 21:9 Subtitle': b'\x20\x3A\x0A'
        }
        AspectRatioCmdString = self.MakeCmdString(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x20\x46\x01',
            'Off': b'\x20\x46\x00'
        }
        AudioMuteCmdString = self.MakeCmdString(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.MakeCmdString(b'\x21\x46')
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01\x65': 'On',
            b'\x00\x64': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': b'\x20\xAC\x08',
            'HDMI (Side)': b'\x20\xAC\x0C',
            'VGA': b'\x20\xAC\x07',
            'SCART': b'\x20\xAC\x03',
            'YPbPr': b'\x20\xAC\x05',
            'Composite (Side)': b'\x20\xAC\x0D',
            'USB': b'\x20\xAC\x0B',
            'Main Tuner (TV)': b'\x20\xAC\x01'
        }
        InputCmdString = self.MakeCmdString(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.MakeCmdString(b'\x21\xAC')
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x08\x86': 'HDMI 1',
            b'\x0C\x82': 'HDMI (Side)',
            b'\x07\x89': 'VGA',
            b'\x03\x8D': 'SCART',
            b'\x05\x8B': 'YPbPr',
            b'\x0D\x83': 'Composite (Side)',
            b'\x0B\x85': 'USB',
            b'\x01\x8F': 'Main Tuner (TV)'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x20\x18\x01',
            'Off': b'\x20\x18\x00'
        }
        PowerCmdString = self.MakeCmdString(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.MakeCmdString(b'\x21\x18')
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
            'On': b'\x20\x37\x01',
            'Off': b'\x20\x37\x00'
        }
        VideoMuteCmdString = self.MakeCmdString(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = self.MakeCmdString(b'\x20\x44' + value.to_bytes(1, 'big'))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.MakeCmdString(b'\x21\x44')
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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

    def __MatchError(self, match, tag):

        Errors = {
            b'\x01\x35' : "This command's payload is malformed or has in invalid checksum.",
            b'\x02\x36' : "This command is not implemented for this TV set."
        }
        print(Errors[match.group(1)])

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
