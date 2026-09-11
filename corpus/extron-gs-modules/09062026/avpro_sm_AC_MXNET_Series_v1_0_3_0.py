from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import json

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
            'Blackout': {'Parameters': ['Receiver'], 'Status': {}},
            'HotPlugDetect': {'Parameters': ['Device'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Transmitter', 'Receiver', 'Tie Type'], 'Status': {}},
            'RS232Command': {'Parameters': ['Device'], 'Status': {}},
            'Version': { 'Status': {}},
        }

    def SetBlackout(self, value, qualifier):

        rx = qualifier['Receiver']

        if rx and value in ['On', 'Off']:
            BlackoutCommandCmdString = 'config set device blackout {} {}\r\n'.format(value.lower(), rx)
            self.__SetHelper('Blackout', BlackoutCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlackout')

    def UpdateHotPlugDetect(self, value, qualifier):

        device = qualifier['Device']

        if device:
            HotPlugDetectCmdString = 'config get device status {}\r\n'.format(device)
            res = self.__UpdateHelper('HotPlugDetect', HotPlugDetectCmdString, value, qualifier)
            if res:
                try:
                    value = res['info'][device]['hpd']
                    if value == 'HPD1':
                        value = 'Active'
                    else:
                        value = 'Not Active'
                    self.WriteStatus('HotPlugDetect', value, qualifier)
                except (KeyError, TypeError, AttributeError):
                    self.Error(['Hot Plug Detect: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHotPlugDetect')

    def SetMatrixTieCommand(self, value, qualifier):

        tx = qualifier['Transmitter']
        rx = qualifier['Receiver']

        TieTypeStates = {
            'Video':    'v',
            'Audio':    'a',
            'USB':      'u',
            'Infrared': 'r',
            'Serial':   's',
            'All':      'z'
        }

        tie_type = qualifier['Tie Type']

        if tx and rx and tie_type in TieTypeStates:
            MatrixTieCommandCmdString = 'matrix aset :{} {} {}\r\n'.format(TieTypeStates[tie_type], tx, rx)
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetRS232Command(self, value, qualifier):

        cmdstring = value
        device = qualifier['Device']

        if cmdstring and device:
            cmdstring = ' '.join('{:02X}'.format(b) for b in cmdstring.replace('\r', '\\\r').replace('\n', '\\\n').encode(encoding='iso-8859-1'))

            RS232CommandCmdString = 'config set device rs232 2 {} {}\r\n'.format(cmdstring, device)
            self.__SetHelper('RS232Command', RS232CommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRS232Command')

    def UpdateVersion(self, value, qualifier):

        VersionCmdString = 'config get version\r\n'
        res = self.__UpdateHelper('Version', VersionCmdString, value, qualifier)
        if res:
            try:
                value = res['info']
                self.WriteStatus('Version', value, qualifier)
            except KeyError:
                self.Error(['Version: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response)
        except json.decoder.JSONDecodeError:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            return {}

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            res = res.decode()
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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
            res = res.decode()
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()