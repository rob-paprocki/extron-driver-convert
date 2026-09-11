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
            'DimmingControl': {'Parameters': ['Address'], 'Status': {}},
            'RelayControl': {'Parameters': ['Address'], 'Status': {}},
        }

    def SetDimmingControl(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        temp = qualifier['Address']
        if (1 <= temp <= 500) and (ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            DimmingControlCmdString = '>D0{0:03d}={1}\r'.format(temp, value)
            self.__SetHelper('DimmingControl', DimmingControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDimmingControl')

    def UpdateDimmingControl(self, value, qualifier):

        temp = qualifier['Address']
        if (1 <= temp <= 500):
            DimmingControlCmdString = '>D0{0:03d}?\r'.format(temp)
            res = self.__UpdateHelper('DimmingControl', DimmingControlCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(res[7:-1]))
                    self.WriteStatus('DimmingControl', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateDimmingControl')
        else:
            print('Invalid Command')

    def SetRelayControl(self, value, qualifier):

        AddressConstraints = {
            'Min': 1,
            'Max': 500
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        temp = qualifier['Address']
        if (1 <= temp <= 500):
            RelayControlCmdString = '>D0{0:03d}={1}\r'.format(temp, ValueStateValues[value])
            self.__SetHelper('RelayControl', RelayControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRelayControl')

    def UpdateRelayControl(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        temp = qualifier['Address']
        if (1 <= temp <= 500):
            RelayControlCmdString = '>D0{0:03d}?\r'.format(temp)
            res = self.__UpdateHelper('RelayControl', RelayControlCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[7:8]]
                    self.WriteStatus('RelayControl', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateRelayControl')
        else:
            print('Invalid Command')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '>E01\r': "Address is not configured.",
            '>E02\r': "Address does not accept any value to be written."
        }
        if response in DEVICE_ERROR_CODES:
            print('{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
