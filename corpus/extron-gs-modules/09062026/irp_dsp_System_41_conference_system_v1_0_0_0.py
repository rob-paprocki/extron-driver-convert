from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self._compile_list = {}
        self.Subscription = {}
        self._ReceiveBuffer = b''
        self.ReceiveData = self.__ReceiveData
        self.connectionFlag = True

        self.Models = {
        }

        self.Commands = {
            'Microphone': {'Parameters': ['Microphone'], 'Status': {}},
            'Override': {'Status': {}},
        }

        self.AddMatchString(re.compile(b'([\x00-\x79])'), self.__MatchMicrophone, None)

    def SetMicrophone(self, value, qualifier):

        Value = {
            '1': ['\x39', '\x79'],
            '2': ['\x24', '\x64'],
            '3': ['\x03', '\x43'],
            '4': ['\x04', '\x44'],
            '5': ['\x05', '\x45'],
            '6': ['\x06', '\x46'],
            '7': ['\x22', '\x62'],
            '8': ['\x08', '\x48'],
            '9': ['\x09', '\x49'],
            '10': ['\x10', '\x50'],
            '11': ['\x11', '\x51'],
            '12': ['\x12', '\x52'],
            '13': ['\x13', '\x53'],
            '14': ['\x14', '\x54'],
            '15': ['\x15', '\x55'],
            '16': ['\x16', '\x56'],
            '17': ['\x17', '\x57'],
            '18': ['\x18', '\x58'],
            '19': ['\x19', '\x59'],
            '20': ['\x20', '\x60'],
            '21': ['\x36', '\x76'],
            '22': ['\x23', '\x63'],
            '23': ['\x07', '\x47'],
            '24': ['\x02', '\x42'],
            '25': ['\x25', '\x65'],
            '26': ['\x26', '\x66'],
            '27': ['\x27', '\x67'],
            '28': ['\x28', '\x68'],
            '29': ['\x29', '\x69'],
            '30': ['\x30', '\x70'],
            '31': ['\x31', '\x71'],
            '32': ['\x32', '\x72'],
            '33': ['\x33', '\x73'],
            '34': ['\x34', '\x74'],
        }

        Microphone = qualifier['Microphone']

        if value == 'On':
            MicrophoneCmdString = Value[Microphone][0]
        elif value == 'Off':
            MicrophoneCmdString = Value[Microphone][1]
        self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)

    def __MatchMicrophone(self, match, tag):

        Values = {
            0x39: ['1', 'On'],
            0x79: ['1', 'Off'],
            0x24: ['2', 'On'],
            0x64: ['2', 'Off'],
            0x03: ['3', 'On'],
            0x43: ['3', 'Off'],
            0x04: ['4', 'On'],
            0x44: ['4', 'Off'],
            0x05: ['5', 'On'],
            0x45: ['5', 'Off'],

            0x06: ['6', 'On'],
            0x46: ['6', 'Off'],
            0x22: ['7', 'On'],
            0x62: ['7', 'Off'],
            0x08: ['8', 'On'],
            0x48: ['8', 'Off'],
            0x09: ['9', 'On'],
            0x49: ['9', 'Off'],
            0x10: ['10', 'On'],
            0x50: ['10', 'Off'],

            0x11: ['11', 'On'],
            0x51: ['11', 'Off'],
            0x12: ['12', 'On'],
            0x52: ['12', 'Off'],
            0x13: ['13', 'On'],
            0x53: ['13', 'Off'],
            0x14: ['14', 'On'],
            0x54: ['14', 'Off'],
            0x15: ['15', 'On'],
            0x55: ['15', 'Off'],

            0x16: ['16', 'On'],
            0x56: ['16', 'Off'],
            0x17: ['17', 'On'],
            0x57: ['17', 'Off'],
            0x18: ['18', 'On'],
            0x58: ['18', 'Off'],
            0x19: ['19', 'On'],
            0x59: ['19', 'Off'],
            0x20: ['20', 'On'],
            0x60: ['20', 'Off'],

            0x36: ['21', 'On'],
            0x76: ['21', 'Off'],
            0x23: ['22', 'On'],
            0x63: ['22', 'Off'],
            0x07: ['23', 'On'],
            0x47: ['23', 'Off'],
            0x02: ['24', 'On'],
            0x42: ['24', 'Off'],
            0x25: ['25', 'On'],
            0x65: ['25', 'Off'],

            0x26: ['26', 'On'],
            0x66: ['26', 'Off'],
            0x27: ['27', 'On'],
            0x67: ['27', 'Off'],
            0x28: ['28', 'On'],
            0x68: ['28', 'Off'],
            0x29: ['29', 'On'],
            0x69: ['29', 'Off'],
            0x30: ['30', 'On'],
            0x70: ['30', 'Off'],

            0x31: ['31', 'On'],
            0x71: ['31', 'Off'],
            0x32: ['32', 'On'],
            0x72: ['32', 'Off'],
            0x33: ['33', 'On'],
            0x73: ['33', 'Off'],
            0x34: ['34', 'On'],
            0x74: ['34', 'Off'],

        }

        res = match.group(1)
        value = Values[res[0]][1]
        Microphone = Values[res[0]][0]
        self.WriteStatus('Microphone', value, {'Microphone': Microphone})

    def SetOverride(self, value, qualifier):
        OverrideCmdString = '\x56\x57\x58\x59\x60\x76\x63\x47\x02\x65\x66\x67\x68\x69\x70\x71\x72\x73\x74'
        self.__SetHelper('Override', OverrideCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it matched with device expectancy.
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

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

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


class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Model=None):
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