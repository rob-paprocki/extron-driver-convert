from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

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
            'AutoSwitch': { 'Status': {}},
            'ButtonLock': { 'Status': {}},
            'DeviceCurrent': {'Parameters': ['Device'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'GPINMode': { 'Status': {}},
            'HubPower': {'Parameters': ['Hub'], 'Status': {}},
            'Input': { 'Status': {}},
            'PCSwitchReason': { 'Status': {}},
            'PCVoltage': {'Parameters': ['PC'], 'Status': {}},
            'Reset': { 'Status': {}},
            'Save': { 'Status': {}},
        }

        self.regex_split = re.compile('\r\n|\n\r')

    def SetAutoSwitch(self, value, qualifier):

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        if value in ValueStateValues:
            AutoSwitchCmdString = 'SM {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSwitch', AutoSwitchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitch')

    def UpdateAutoSwitch(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        AutoSwitchCmdString = 'GM\r'
        res = self.__UpdateHelper('AutoSwitch', AutoSwitchCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.regex_split.split(res)[1]]
                self.WriteStatus('AutoSwitch', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Switch: Invalid/unexpected response'])

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        if value in ValueStateValues:
            ButtonLockCmdString = 'SLCK {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButtonLock')

    def UpdateButtonLock(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        ButtonLockCmdString = 'GLCK\r'
        res = self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.regex_split.split(res)[1]]
                self.WriteStatus('ButtonLock', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Button Lock: Invalid/unexpected response'])

    def UpdateDeviceCurrent(self, value, qualifier):

        device = qualifier['Device']

        if device in ['1', '2', '3']:
            DeviceCurrentCmdString = 'GDI {}\r'.format(device)
            res = self.__UpdateHelper('DeviceCurrent', DeviceCurrentCmdString, value, qualifier)
            if res:
                try:
                    value = float(self.regex_split.split(res)[1][:-1])
                    self.WriteStatus('DeviceCurrent', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Device Current: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDeviceCurrent')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'FW\r'
        res = self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)
        if res:
            try:
                value = self.regex_split.split(res)[1][7:]
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetGPINMode(self, value, qualifier):

        ValueStateValues = {
            'Pulse': '0',
            'Level': '1'
        }

        if value in ValueStateValues:
            GPINModeCmdString = 'SGMOD {}\r'.format(ValueStateValues[value])
            self.__SetHelper('GPINMode', GPINModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGPINMode')

    def UpdateGPINMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Pulse',
            '1': 'Level'
        }

        GPINModeCmdString = 'GGMOD\r'
        res = self.__UpdateHelper('GPINMode', GPINModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.regex_split.split(res)[1]]
                self.WriteStatus('GPINMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['GPIN Mode: Invalid/unexpected response'])

    def UpdateHubPower(self, value, qualifier):

        hub = qualifier['Hub']

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
            
        if hub in ['1', '2', '3']:
            HubPowerCmdString = 'GHPW {}\r'.format(hub)
            res = self.__UpdateHelper('HubPower', HubPowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[self.regex_split.split(res)[1]]
                    self.WriteStatus('HubPower', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Hub Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHubPower')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1':    '1',
            '2':    '2',
            'Off':  '0'
        }

        if value in ValueStateValues:
            InputCmdString = 'SH {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '0': 'Off'
        }

        InputCmdString = 'GH\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.regex_split.split(res)[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdatePCSwitchReason(self, value, qualifier):

        ValueStateValues = {
            'HOST_OFF': 'Host Off',
            'HOST_CHG': 'Host CHG',
            'BTN':      'Button',
            'CMD':      'Command'
        }

        PCSwitchReasonCmdString = 'GCAUSE\r'
        res = self.__UpdateHelper('PCSwitchReason', PCSwitchReasonCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.regex_split.split(res)[1]]
                self.WriteStatus('PCSwitchReason', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['PC Switch Reason: Invalid/unexpected response'])

    def UpdatePCVoltage(self, value, qualifier):

        pc = qualifier['PC']

        if pc in ['1', '2']:
            PCVoltageCmdString = 'GHV {}\r'.format(pc)
            res = self.__UpdateHelper('PCVoltage', PCVoltageCmdString, value, qualifier)
            if res:
                try:
                    value = float(self.regex_split.split(res)[1][:-1])
                    self.WriteStatus('PCVoltage', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['PC Voltage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePCVoltage')

    def SetReset(self, value, qualifier):

        ResetCmdString = 'RST\r'
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)

    def SetSave(self, value, qualifier):

        SaveCmdString = 'SAVE\r'
        self.__SetHelper('Save', SaveCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'NACK' in response:
            self.Error(['An error occurred: {}.'.format(sourceCmdName)])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()