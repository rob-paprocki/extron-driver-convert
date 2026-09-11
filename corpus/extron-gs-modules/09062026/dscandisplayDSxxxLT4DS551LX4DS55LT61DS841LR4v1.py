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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self._DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'InputSignal': {'Status': {}},
            'LandscapeMode': {'Status': {}},
            'Power': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 255
        elif 0 <= int(value) <= 254:
            self._DeviceID = int(value)
        else:
            print('Device ID is set to an Invalid value.')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x40, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2])
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for Brightness')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ContrastCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x46, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            print('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x46, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2])
                self.WriteStatus('Contrast', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for Contrast')

    def SetLandscapeMode(self, value, qualifier):

        ValueStateValues = {
            'Landscape': 0x80,
            'Portrait': 0x00
        }

        LandscapeModeCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x5C, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
        self.__SetHelper('LandscapeMode', LandscapeModeCmdString, value, qualifier)

    def UpdateLandscapeMode(self, value, qualifier):

        ValueStateValues = {
            0x80: 'Landscape',
            0x00: 'Portrait'
        }

        LandscapeModeCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x5C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('LandscapeMode', LandscapeModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('LandscapeMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for LandscapeMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0xFF,
            'Off': 0x7F
        }

        PowerCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x54, ValueStateValues[value], 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0xAA)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x80: 'On',
            0xA0: 'On',
            0x00: 'Off',
            0x20: 'Off'
        }

        PowerCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x4E, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xAA)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                if res[5] == 0x80 or res[5] == 0x00:
                    self.WriteStatus('InputSignal', 'Present', qualifier)
                else:
                    self.WriteStatus('InputSignal', 'No Input', qualifier)
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for Power')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 255:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
            if not res:
                print('Invalid/Unexpected Response for', command)
            else:
                return self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 255:
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
