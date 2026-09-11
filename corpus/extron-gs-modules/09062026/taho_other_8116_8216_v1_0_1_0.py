from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'Power': {'Parameters':['Outlet'], 'Status': {}},
            }

        self.OutletList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.onOutlet = []
        self.offOutlet = []

    def SetPower(self, value, qualifier):

        OutletValues = {
            '1'  : '1', 
            '2'  : '2', 
            '3'  : '3', 
            '4'  : '4', 
            '5'  : '5', 
            '6'  : '6', 
            '7'  : '7', 
            '8'  : '8', 
            '9'  : '9', 
            '10' : '10',
            'All' : '*'
        }
        ValueStateValues = {
            'On' : 'power on {}\r', 
            'Off' : 'power off {}\r'
        }
        Outlet = qualifier['Outlet']
        if Outlet in OutletValues:
            PowerCmdString = ValueStateValues[value].format(OutletValues[Outlet])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        ValueStatesValue = {
            'N': 'On',
            'F': 'Off'
        }

        RequiredCommandCmdString = 'power status\r'
        res = self.__UpdateHelper('Power', RequiredCommandCmdString, value, qualifier)
        if res:
            try:
                self.onOutlet = []
                self.offOutlet = []
                self.MaxOutletNumber = 0
                self.OutletList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                avaibleOutlets = res.splitlines()
                for Outlet in avaibleOutlets:
                    OutletNumber = int(Outlet[-2])
                    if OutletNumber == 0:
                        OutletNumber = 10
                    if OutletNumber in self.OutletList:
                        self.OutletList.remove(OutletNumber)
                    if 'ON' in Outlet:
                        value = 'On'
                        self.onOutlet.append(OutletNumber)
                    elif 'OFF' in Outlet:
                        value = 'Off'
                        self.offOutlet.append(OutletNumber)
                    self.WriteStatus('Power', value, {'Outlet': str(OutletNumber)})

                # Write Not Avaible on all other non supported outlets
                for noOutlet in self.OutletList:
                    self.WriteStatus('Power', 'Not Available', {'Outlet': str(noOutlet)})
            except (KeyError, IndexError):
                print('Power has provided an invalid/unexpected response')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout).decode()
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(commandstring, res)

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
