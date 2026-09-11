from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def cmdStringBuild(self, data):
        chkSum = 0
        for i in range(0, 3):
            chkSum = chkSum + data[i]
        cmdString = b'\xAA\xBB\xCC' + data + chkSum.to_bytes(1, 'big') + b'\xDD\xEE\xFF'
        return cmdString

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': 0x00,
            '4:3': 0x01,
            'Point to Point': 0x07
        }

        data = pack('>3B', 0x08, ValueStateValues[value], 0x00)
        AspectRatioCmdString = self.cmdStringBuild(data)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01
        }

        data = pack('>3B', 0x03, 0x01, ValueStateValues[value])
        AudioMuteCmdString = self.cmdStringBuild(data)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        data = pack('>3B', 0x03, 0x03, 0x00)
        AudioMuteCmdString = self.cmdStringBuild(data)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Audio Mute: Invalid/unexpected response')

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x09
        }

        data = pack('>3B', 0x07, ValueStateValues[value], 0x00)
        ChannelCmdString = self.cmdStringBuild(data)
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': 0x02,
            'VGA 1': 0x03,
            'VGA 2': 0x04,
            'VGA 3': 0x0B,
            'HDMI 1': 0x06,
            'HDMI 2': 0x07,
            'HDMI 3': 0x05,
            'PC': 0x08,
            'DTEN': 0x0A
        }

        data = pack('>3B', 0x02, ValueStateValues[value], 0x00)
        InputCmdString = self.cmdStringBuild(data)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x02: 'AV',
            0x03: 'VGA 1',
            0x04: 'VGA 2',
            0x0B: 'VGA 3',
            0x06: 'HDMI 1',
            0x07: 'HDMI 2',
            0x05: 'HDMI 3',
            0x08: 'PC',
            0x0A: 'DTEN'
        }

        data = pack('>3B', 0x02, 0x00, 0x00)
        InputCmdString = self.cmdStringBuild(data)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Input: Invalid/unexpected response')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': 0x1B,
            '1': 0x00,
            '2': 0x10,
            '3': 0x11,
            '4': 0x13,
            '5': 0x14,
            '6': 0x15,
            '7': 0x17,
            '8': 0x18,
            '9': 0x19,
            'Delete': 0x40
        }

        data = pack('>3B', 0x07, ValueStateValues[value], 0x00)
        KeypadCmdString = self.cmdStringBuild(data)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x47,
            'Down': 0x4D,
            'Left': 0x49,
            'Right': 0x4B,
            'Enter': 0x4A,
            'Back': 0x0A,
            'Menu': 0x0D,
            'Home': 0x48
        }

        data = pack('>3B', 0x07, ValueStateValues[value], 0x00)
        MenuNavigationCmdString = self.cmdStringBuild(data)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        data = pack('>3B', 0x09, ValueStateValues[value], 0x00)
        PCPowerCmdString = self.cmdStringBuild(data)
        self.__SetHelper('PCPower', PCPowerCmdString, value, qualifier)

    def UpdatePCPower(self, value, qualifier):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off',
            0x02: 'Sleep',
            0x03: 'Hibernate'
        }

        data = pack('>3B', 0x09, 0x02, 0x00)
        PCPowerCmdString = self.cmdStringBuild(data)
        res = self.__UpdateHelper('PCPower', PCPowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('PCPower', value, qualifier)
            except (KeyError, IndexError):
                print('PC Power: Invalid/unexpected response')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01
        }

        data = pack('>3B', 0x01, ValueStateValues[value], 0x00)
        PowerCmdString = self.cmdStringBuild(data)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        data = pack('>3B', 0x01, 0x02, 0x00)
        PowerCmdString = self.cmdStringBuild(data)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = pack('>3B', 0x03, 0x00, value)
            VolumeCmdString = self.cmdStringBuild(data)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        data = pack('>3B', 0x03, 0x02, 0x00)
        VolumeCmdString = self.cmdStringBuild(data)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Volume: Invalid/unexpected response')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Unidirectional is enable, Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return ''
            else:
                return res

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
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
