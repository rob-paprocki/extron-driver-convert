from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'BLU': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }            

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x14(\x01|\x00)\x8A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x12(\x01|\x00)\x8A'), self.__MatchBLU, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x15(\x04|\x05|\x06|\x07|\x08|\x09|\x0A|\x0C)\x8A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x11(\x01|\x00)\x8A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xA9\x41([\x00-\x80])\x13([\x00-\x64])\x8A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xA9\x4E[\x00-\x80]([\x11-\x16])([\x01-\xFF])\x8A'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 128:
            self._DeviceID = int(value)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        AudioMuteCmdString = pack('<5B', 0xA9, 0x14, self.DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = pack('<5B', 0xA9, 0x14, self.DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        if self.DeviceID == ord(match.group(1).decode()):
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, None)

    def SetBLU(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        BLUCmdString = pack('<5B', 0xA9, 0x12, self.DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('BLU', BLUCmdString, value, qualifier)

    def UpdateBLU(self, value, qualifier):

        BLUCmdString = pack('<5B', 0xA9, 0x12, self.DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('BLU', BLUCmdString, value, qualifier)

    def __MatchBLU(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        if self.DeviceID == ord(match.group(1).decode()):
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('BLU', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = pack('<5B', 0xA9, 0x16, self.DeviceID, 0xB8, 0x8A)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': 0x04,
            'HDMI 1 (2.0)': 0x0A,
            'HDMI 2 (MHL)': 0x05,
            'HDMI 3': 0x06,
            'EZ-BOX': 0x07,
            'DisplayPort': 0x08,
            'OPS': 0x09,
            'IFTD (Android)': 0x0C
        }

        InputCmdString = pack('<5B', 0xA9, 0x15, self.DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = pack('<5B', 0xA9, 0x15, self.DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x04': 'VGA',
            '\x0A': 'HDMI 1 (2.0)',
            '\x05': 'HDMI 2 (MHL)',
            '\x06': 'HDMI 3',
            '\x07': 'EZ-BOX',
            '\x08': 'DisplayPort',
            '\x09': 'OPS',
            '\x0C': 'IFTD (Android)'
        }

        if self.DeviceID == ord(match.group(1).decode()):
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('<5B', 0xA9, 0x11, self.DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = pack('<5B', 0xA9, 0x11, self.DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        if self.DeviceID == ord(match.group(1).decode()):

            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('<5B', 0xA9, 0x13, self.DeviceID, value, 0x8A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('<5B', 0xA9, 0x13, self.DeviceID, 0xAA, 0x8A)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        if self.DeviceID == ord(match.group(1).decode()):
            value = ord(match.group(2).decode())
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == 0:
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

        COMMAND_CODES = {
            '\x11': "Power",
            '\x12': "BLU",
            '\x13': "Volume",
            '\x14': "Audio Mute",
            '\x15': "Input",
            '\x16': "Remote Control Command"
            }
        ERROR_CODES = {
            '\x01': "Invalid Command",
            '\x02': "Invalid Data"
            }  
        if match.group(2).decode() in ERROR_CODES:
            value = "Error occured with command: {}, Error: {}.".format(COMMAND_CODES[match.group(1).decode()], ERROR_CODES[match.group(2).decode()])
        else:
            value = "Error occured with command: {}, Error: Unknown.".format(COMMAND_CODES[match.group(1).decode()])
        
        print('value for', command)

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
