from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import re

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


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelDiscreteCommand': { 'Status': {}},
            'ChannelRemote': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'IREmulation': { 'Status': {}},
            'MajorChannelStatus': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MinorChannelStatus': { 'Status': {}},
            'Power': { 'Status': {}},
            'SignalQuality': { 'Status': {}},
            'Transport': { 'Status': {}},
        }
       
    def SetChannelDiscreteCommand(self, value, qualifier):
        MajorConstraints = {
            'Min' : 0,
            'Max' : 65535
            }

        MinorConstraints = {
            'Min' : 0,
            'Max' : 65535
            }
            
        ValueList = value.split('.')
        MajorValue = int(ValueList[0])
        MinorValue = int(ValueList[1])
        if MajorConstraints['Min'] <= MajorValue <= MajorConstraints['Max'] and MinorConstraints['Min'] <= MinorValue <= MinorConstraints['Max']:
            ChannelDiscreteCommandCmdString = b'\xFA\xA6' + pack('>HH', MajorValue, MinorValue)
            self.__SetHelper('ChannelDiscreteCommand', ChannelDiscreteCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDiscreteCommand')
           
    def SetChannelRemote(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\xD1', 
            'Down'      : b'\xD2', 
            'Previous'  : b'\xD6', 
            '0' : b'\xE0', 
            '1' : b'\xE1', 
            '2' : b'\xE2', 
            '3' : b'\xE3', 
            '4' : b'\xE4', 
            '5' : b'\xE5', 
            '6' : b'\xE6', 
            '7' : b'\xE7', 
            '8' : b'\xE8', 
            '9' : b'\xE9'
        }

        ChannelRemoteCmdString = b'\xFA\xA5\x00\x01' + ValueStateValues[value]
        self.__SetHelper('ChannelRemote', ChannelRemoteCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x94', 
            'Off' : b'\x93'
        }

        ExecutiveModeCmdString = b'\xFA' + ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetIREmulation(self, value, qualifier):

        ValueStateValues = {
            'Info'      : b'\xA1', 
            'Active'    : b'\xA2', 
            'List'      : b'\xA3', 
            '-'         : b'\xA5', 
            'Red'       : b'\xEA', 
            'Yellow'    : b'\xEB', 
            'Green'     : b'\xEC', 
            'Blue'      : b'\xED', 
            'Format'    : b'\xF8', 
            'Guide'     : b'\xD3'
        }

        IREmulationCmdString = b'\xFA\xA5\x00\x01' + ValueStateValues[value]
        self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)

    def UpdateMajorChannelStatus(self, value, qualifier):

        MajorChannelStatusCmdString = b'\xFA\x87'
        res = self.__UpdateHelper('MajorChannelStatus', MajorChannelStatusCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>HH', res[1:-1])
                self.WriteStatus('MajorChannelStatus', value[0], qualifier)
            except (ValueError, IndexError):
                self.Error(['Major Channel Status: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Back'  : b'\xA4', 
            'Select' : b'\xC3', 
            'Right' : b'\x9A', 
            'Left'  : b'\x9B', 
            'Up'    : b'\x9C', 
            'Down'  : b'\x9D', 
            'Menu'  : b'\xF7', 
            'Exit'  : b'\xD4'
        }

        MenuNavigationCmdString = b'\xFA\xA5\x00\x01' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateMinorChannelStatus(self, value, qualifier):

        MinorChannelStatusCmdString = b'\xFA\x87'
        res = self.__UpdateHelper('MinorChannelStatus', MinorChannelStatusCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>HH', res[1:-1])
                self.WriteStatus('MinorChannelStatus', value[1], qualifier)
            except (ValueError, IndexError):
                self.Error(['Minor Channel Status: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xC5', 
            'Off' : b'\xD0'
        }

        PowerCmdString = b'\xFA\xA5\x00\x01' + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdateSignalQuality(self, value, qualifier):

        SignalQualityCmdString = b'\xFA\x90'
        res = self.__UpdateHelper('SignalQuality', SignalQualityCmdString, value, qualifier)
        if res:
            try:
                value = res[1]
                self.WriteStatus('SignalQuality', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Signal Quality: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Pause'  : b'\xB0', 
            'Rewind' : b'\xB1', 
            'Play'   : b'\xB2', 
            'Stop'   : b'\xB3', 
            'FFWD'   : b'\xB4', 
            'Record' : b'\xB5', 
            'Replay' : b'\xB6', 
            'Advance': b'\xB7'
        }

        TransportCmdString = b'\xFA\xA5\x00\x01' + ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, typeVal, response):

        DEVICE_ERROR_CODES = {
                b'\xF1' : 'Command Unknown',
                b'\xF3' : 'Parser Timed Out',
                b'\xF5' : 'Service Command Unsuccessful',
                b'\xF7' : 'Busy',
                b'\xF9' : 'Command Parser In Use',
                b'\xFB' : 'Prefix Not Sent',
                b'\xFD' : 'Communication Data Error',
                b'\xFF' : 'Command Buffer Overflow'		
        }
        
        if response:
            if typeVal == 'Update':
                ErrorCode1 = DEVICE_ERROR_CODES.get(response[:1])
                ErrorCode2 = DEVICE_ERROR_CODES.get(response[-1:])
                if ErrorCode1:
                    self.Error([sourceCmdName + ' Error: ' + ErrorCode1])
                    response = ''
                if ErrorCode2:
                    self.Error([sourceCmdName + ' Error: ' + ErrorCode2])
                    response = ''
            elif typeVal == 'Set':
                if not (response == b'\xF0\xF2\xF4' or response == b'\xF0\xF4'):
                    for i in DEVICE_ERROR_CODES.items():
                        if i[0] in response:
                            self.Error([sourceCmdName + 'Error: ' + i[1]])
                    response = ''                            
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:            
            if command not in ['ExecutiveMode']: # ie. commands that have extra parameters as according to the protocol
                res1 = self.SendAndWait(commandstring[0:2], self.DefaultResponseTimeout, deliRex=re.compile(b'[\xF0-\xFF]'))
                res2 = self.SendAndWait(commandstring[2:], self.DefaultResponseTimeout, deliRex=re.compile(b'[\xF0-\xFF]{2}'))
                res = res1 + res2

            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=re.compile(b'[\xF0-\xFF]{2}'))

            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                self.__CheckResponseForErrors(command, 'Set', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):        
        UpdateRegex = {
            'MajorChannelStatus'  : re.compile(b'[\xF0-\xFF][\x00-\xFF]{4}[\xF0-\xFF]'),
            'MinorChannelStatus'  : re.compile(b'[\xF0-\xFF][\x00-\xFF]{4}[\xF0-\xFF]'),
            'SignalQuality'       : re.compile(b'[\xF0-\xFF][\x00-\x64][\xF0-\xFF]')
        }

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=UpdateRegex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, 'Update', res)            

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

