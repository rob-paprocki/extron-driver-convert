from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search, findall

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
            'CurrentStatus': {'Parameters':['Outlet'], 'Status': {}},
            'OutletPower': {'Parameters':['Outlet'], 'Status': {}},
            'VoltageStatus': {'Parameters':['Outlet'], 'Status': {}},
            }


    def UpdateCurrentStatus(self, value, qualifier):

        OutletNum = int(qualifier['Outlet'])
        Currentpattern = compile('[\s\S]+Reading: (\d+)[\s\S]+')
        CurrentStatusCmdString = '#show sensor outlet {0} current'.format(OutletNum)
        res = self.__UpdateHelper('CurrentStatus', CurrentStatusCmdString, value, qualifier)
        if res:
            try:
                response = findall(Currentpattern, res)
                value = int(response[0])
                self.WriteStatus('CurrentStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Current Status: Invalid/unexpected response'])

    def SetOutletPower(self, value, qualifier):

        OutletStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            'All' : 'All'
        }

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off'
        }

        OutletNum = OutletStates[qualifier['Outlet']]
        OutletPowerCmdString = '#power outlets {0} {1} \/y'.format(OutletNum, ValueStateValues[value])
        self.__SetHelper('OutletPower', OutletPowerCmdString, value, qualifier)

    def UpdateOutletPower(self, value, qualifier):


        OutletStates = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10' : '10', 
            '11' : '11', 
            '12' : '12', 
            '13' : '13', 
            '14' : '14', 
            '15' : '15', 
            'All' : 'All'
        }

        ValueStateValues = {
            'on' : 'On', 
            'off' : 'Off'
        }

        OutletNum = OutletStates[qualifier['Outlet']]

        Outletpattern = compile('[\s\S]+State: (on|off)[\s\S]+')

        OutletPowerCmdString = '#show outlets {0}'.format(OutletNum)
        res = self.__UpdateHelper('OutletPower', OutletPowerCmdString, value, qualifier)
        if res:
            try:
                response = findall(Outletpattern, res)
                value = ValueStateValues[response[0]]
                self.WriteStatus('OutletPower', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Outlet Power: Invalid/unexpected response'])

    def UpdateVoltageStatus(self, value, qualifier):

        OutletNum = int(qualifier['Outlet'])
        Voltagepattern = compile('[\s\S]+Reading: (\d+)[\s\S]+')
        VoltageStatusCmdString = '#show sensor outlet {0} voltage'.format(OutletNum)
        res = self.__UpdateHelper('VoltageStatus', VoltageStatusCmdString, value, qualifier)
        if res:
            try:
                response = findall(Voltagepattern, res)
                value = int(response[0])
                self.WriteStatus('VoltageStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Voltage Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            response = response.decode()
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
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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
            return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)
     
            

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        
class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None),
                 Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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

