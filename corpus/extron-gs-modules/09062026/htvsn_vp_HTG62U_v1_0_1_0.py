from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'AspectRatio': { 'Status': {}},
            'BlankScreen': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        self.__SetHelper('AspectRatio', b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x10\x00\xCF' , value, qualifier)

    def SetBlankScreen(self, value, qualifier):

        self.__SetHelper('BlankScreen', b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x15\xCF' , value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x03\xFF\x00\x0E\xCF'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int.from_bytes(res[10:12], byteorder='big')
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        States = {
            'VGA'       : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0D\xCF', 
            'Video'     : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x11\xCF', 
            'HDMI 1'    : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0A\xCF', 
            'HDMI 2'    : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0B\xCF', 
            'HDMI 3'    : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0E\xCF', 
            'HDBaseT'   : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x3B\xCF'
        }

        self.__SetHelper('Input', States[value] , value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            1  : 'VGA', 
            6  : 'Video', 
            8  : 'HDMI 1', 
            9  : 'HDMI 2', 
            10 : 'HDMI 3', 
            14 : 'HDBaseT',
            0  : 'No Signal'
        }

        InputCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x03\xFF\x00\x10\xCF'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = States[res[10]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x03\xFF\x00\x0D\xCF'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int.from_bytes(res[10:12], byteorder='big')
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On'        : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x00\xCF', 
            'Off'       : b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x01\xCF'
        }

        self.__SetHelper('Power', States[value] , value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            1 : 'On', 
            0 : 'Off'
        }

        PowerCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x03\xFF\x00\x0F\xCF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = States[res[10]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            if response[10] == 1:
                self.Error(['Command Failed : {}'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\xCF')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\xCF')
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

