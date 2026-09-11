from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re


class DeviceClass:

    def __init__(self):

        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}
        self._Checksum = 'Enabled'

        self.Commands = {
            'DimLevel': {'Parameters': ['Lighting Application Address', 'Group Address', 'Dimming Rate'], 'Status': {}},
            'SwitchLight': {'Parameters': ['Lighting Application Address', 'Group Address'], 'Status': {}},
        }

        self.AddMatchString(re.compile(b'05[0-9A-F]{2}([0-9A-F]{2})(00|0100)(02|0A|12|1A|22|2A|32|3A|42|4A|52|5A|62|6A|72|7A)([0-9A-F]{2})([0-9A-F]{2})[0-9A-F]{2}'), self.__MatchDimLevel, None)
        self.AddMatchString(re.compile(b'05[0-9A-F]{2}([0-9A-F]{2})(00|0100)(79|01)([0-9A-F]{2})[0-9A-F]{2}'), self.__MatchSwitchLight, None)

    @property
    def Checksum(self):
        return self._Checksum

    @Checksum.setter
    def Checksum(self, value):
        if value in ['Enabled','Disabled']:
            self._Checksum = value
        else:
            print('Invalid value for Checksum. Available options are: Enabled, Disabled')

    def SetDeviceInitialize(self, value, qualifier):
        self.SendAndWait('~~~\r', 1, deliTag=b'\r') 
        self.SendAndWait('A3300051\r', 1, deliTag=b'\r')
        self.Debug = True
        

    def SetDimLevel(self, value, qualifier):

        DimmingRateStates = {
            'Instantaneous': '\x02',
            '4 seconds': '\x0A',
            '8 seconds': '\x12',
            '12 seconds': '\x1A',
            '20 seconds': '\x22',
            '30 seconds': '\x2A',
            '40 seconds': '\x32',
            '1 minute': '\x3A',
            '1.5 minutes': '\x42',
            '2 minutes': '\x4A',
            '3 minutes': '\x52',
            '5 minutes': '\x5A',
            '7 minutes': '\x62',
            '10 minutes': '\x6A',
            '15 minutes': '\x72',
            '17 minutes': '\x7A'
        }

        DimmingLevelConstraints = {
            'Min': 0,
            'Max': 255
        }

        LightingApplicationAddressConstraints = {
            'Min': 48,
            'Max': 255
        }

        GroupAddressConstraints = {
            'Min': 0,
            'Max': 255
        }

        LightingApplicationAddress = int(qualifier['Lighting Application Address'])
        GroupAddress = int(qualifier['Group Address'])
        DimmingRate = ord(DimmingRateStates[qualifier['Dimming Rate']])
        DimmingLevel = value

        if (DimmingLevelConstraints['Min'] <= DimmingLevel <= DimmingLevelConstraints['Max'] and
                LightingApplicationAddressConstraints['Min'] <= LightingApplicationAddress <= LightingApplicationAddressConstraints['Max'] and
                GroupAddressConstraints['Min'] <= GroupAddress <= GroupAddressConstraints['Max']
                ):
            if self._Checksum == 'Enabled':
                CKS = (~((0x05 + LightingApplicationAddress + 0x00 + DimmingRate + GroupAddress + DimmingLevel) % 0x100) + 1) & 0xFF
                DimLevelCmdString = '\\05{:02X}00{:02X}{:02X}{:02X}{:02X}\r'.format(LightingApplicationAddress, DimmingRate, GroupAddress, DimmingLevel, CKS)
            else:
                DimLevelCmdString = '\\05{:02X}00{:02X}{:02X}{:02X}\r'.format(LightingApplicationAddress, DimmingRate, GroupAddress, DimmingLevel)

            self.__SetHelper('DimLevel', DimLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimLevel')

    def __MatchDimLevel(self, match, tag):

        DimmingRateStates = {
            '02': 'Instantaneous',
            '0A': '4 seconds',
            '12': '8 seconds',
            '1A': '12 seconds',
            '22': '20 seconds',
            '2A': '30 seconds',
            '32': '40 seconds',
            '3A': '1 minute',
            '42': '1.5 minutes',
            '4A': '2 minutes',
            '52': '3 minutes',
            '5A': '5 minutes',
            '62': '7 minutes',
            '6A': '10 minutes',
            '72': '15 minutes',
            '7A': '17 minutes'
        }

        qualifier = {}
        qualifier['Lighting Application Address'] = str(int(match.group(1).decode(), 16))
        qualifier['Dimming Rate'] = DimmingRateStates[match.group(3).decode()]
        qualifier['Group Address'] = str(int(match.group(4).decode(), 16))
        value = int(match.group(5).decode(), 16)
        self.WriteStatus('DimLevel', value, qualifier)

    def SetSwitchLight(self, value, qualifier):

        SwitchLightStateValues = {
            'On': '\x79',
            'Off': '\x01'
        }

        LightingApplicationAddressConstraints = {
            'Min': 48,
            'Max': 255
        }

        GroupAddressConstraints = {
            'Min': 0,
            'Max': 255
        }

        LightingApplicationAddress = int(qualifier['Lighting Application Address'])
        GroupAddress = int(qualifier['Group Address'])
        SwitchLightState = ord(SwitchLightStateValues[value])

        if (
            LightingApplicationAddressConstraints['Min'] <= LightingApplicationAddress <= LightingApplicationAddressConstraints['Max'] and
            GroupAddressConstraints['Min'] <= GroupAddress <= GroupAddressConstraints['Max']
        ):
            if self._Checksum == 'Enabled':
                CKS = (~((0x05 + LightingApplicationAddress + int(SwitchLightState) + GroupAddress) % 0x100) + 1) & 0xFF
                SwitchLightCmdString = '\\05{:02X}00{:02X}{:02X}{:02X}\r'.format(LightingApplicationAddress, SwitchLightState, GroupAddress, CKS)
            else:
                SwitchLightCmdString = '\\05{:02X}00{:02X}{:02X}\r'.format(LightingApplicationAddress, SwitchLightState, GroupAddress)

            self.__SetHelper('SwitchLight', SwitchLightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchLight')

    def __MatchSwitchLight(self, match, tag):

        ValueStateValues = {
            '79': 'On',
            '01': 'Off',
        }
        qualifier = {}
        qualifier['Lighting Application Address'] = str(int(match.group(1).decode(), 16))
        qualifier['Group Address'] = str(int(match.group(4).decode(), 16))
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('SwitchLight', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}
            
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
