from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
            'AudioMute': {'Parameters':['Reproducer'], 'Status': {}},
            'FileTransport': {'Parameters':['File','Reproducer'], 'Status': {}},
            'ReproducerStatus': {'Parameters':['Reproducer'], 'Status': {}},
            'SMPTE': { 'Status': {}},
            'SMPTEFrameRateMode': { 'Status': {}},
            'SMPTEMode': { 'Status': {}},
            'Transport': {'Parameters':['Reproducer'], 'Status': {}},
            'VideoMute': {'Parameters':['Reproducer'], 'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '0',
            'Off' : '1'
        }

        if qualifier['Reproducer'] == 'All':
            AudioMuteCmdString = '{0}*AD\r'.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Reproducer']) <= 8:
            AudioMuteCmdString = '{0}R{1}AD\r'.format(ValueStateValues[value], qualifier['Reproducer'])
        else:
            self.Discard('Invalid Command for SetAudioMute')

        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetFileTransport(self, value, qualifier):

        ValueStateValues = {
            'Search'                  : 'SE',
            'Play File'               : 'PL',
            'Loop File'               : 'LP',
            'Synchronously Play File' : 'SP',
            'Synchronously Loop File' : 'SL',
            'Play Next'               : 'PN',
            'Loop Next'               : 'LN'
        }

        if qualifier['Reproducer'] == 'All' and 0 <= int(qualifier['File']) <= 1023:
            FileTransportCmdString = '{0}*{1}\r'.format(qualifier['File'], ValueStateValues[value])
        elif 1 <= int(qualifier['Reproducer']) <= 8 and 0 <= int(qualifier['File']) <= 1023:
            FileTransportCmdString = '{0}R{1}{2}\r'.format(qualifier['File'],qualifier['Reproducer'], ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetFileTransport')

        self.__SetHelper('FileTransport', FileTransportCmdString, value, qualifier)
        
    def UpdateReproducerStatus(self, value, qualifier):

        ValueStateValues = {
            '4' : 'Playing',
            '1' : 'Stopped',
            '0' : 'Error',
            '5' : 'Stilled',
            '6' : 'Paused'
        }

        if 1 <= int(qualifier['Reproducer']) <= 8:
            ReproducerStatusCmdString = 'R{0}?P\r'.format(qualifier['Reproducer'])
            res = self.__UpdateHelper('ReproducerStatus', ReproducerStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('ReproducerStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Reproducer Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateReproducerStatus')

    def SetSMPTE(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'ES',
            'Disable' : 'DS',
            'Pause'   : 'PS',
            'Idle'    : 'IS'
        }

        SMPTECmdString = '{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SMPTE', SMPTECmdString, value, qualifier)

    def SetSMPTEFrameRateMode(self, value, qualifier):

        ValueStateValues = {
            '23.976' : '0',
            '24'     : '1',
            '25'     : '2',
            '29.97'  : '3',
            '30d'    : '4',
            '30'     : '5'
        }

        SMPTEFrameRateModeCmdString = '{0}FR\r'.format(ValueStateValues[value])
        self.__SetHelper('SMPTEFrameRateMode', SMPTEFrameRateModeCmdString, value, qualifier)

    def UpdateSMPTEFrameRateMode(self, value, qualifier):

        ValueStateValues = {
            '0' : '23.976',
            '1' : '24',
            '2' : '25',
            '3' : '29.97',
            '4' : '30d',
            '5' : '30'
        }

        SMPTEFrameRateModeCmdString = 'FR\r'
        res = self.__UpdateHelper('SMPTEFrameRateMode', SMPTEFrameRateModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('SMPTEFrameRateMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SMPTE Frame Rate Mode: Invalid/unexpected response'])

    def SetSMPTEMode(self, value, qualifier):

        ValueStateValues = {
            'Read'                 : '0',
            'Generate'             : '1',
            'Generate with V-Sync' : '2'
        }

        SMPTEModeCmdString = '{0}SO\r'.format(ValueStateValues[value])
        self.__SetHelper('SMPTEMode', SMPTEModeCmdString, value, qualifier)

    def UpdateSMPTEMode(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Read',
            '1' : 'Generate',
            '2' : 'Generate with V-Sync'
        }

        SMPTEModeCmdString = 'SO\r'
        res = self.__UpdateHelper('SMPTEMode', SMPTEModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('SMPTEMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SMPTE Mode: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop'  : 'RJ',
            'Loop'  : 'LP',
            'Still' : 'ST',
            'Pause' : 'PA',
            'Play'  : 'PL'
        }

        if qualifier['Reproducer'] == 'All':
            TransportCmdString = '*{0}\r'.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Reproducer']) <= 8:
            TransportCmdString = 'R{0}{1}\r'.format(qualifier['Reproducer'],ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetTransport')

        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '0',
            'Off' : '1'
        }

        if qualifier['Reproducer'] == 'All':
            VideoMuteCmdString = '{0}*VD\r'.format(ValueStateValues[value])
        elif 1 <= int(qualifier['Reproducer']) <= 8:
            VideoMuteCmdString = '{0}R{1}VD\r'.format(ValueStateValues[value], qualifier['Reproducer'])
        else:
            self.Discard('Invalid Command for SetVideoMute')

        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=2368, Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])