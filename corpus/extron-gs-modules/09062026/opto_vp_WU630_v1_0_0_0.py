from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DInvert': {'Status': {}},
            '3DMode': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02d}'.format(int(value))

    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        ThreeDCmdString = '~{0}231 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DInvert', ThreeDCmdString, value, qualifier)

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '~{0}230 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DMode', CmdString, value, qualifier)

    def Update3DMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        CmdString = '~{0}503 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('3DMode', CmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('3DMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for Update3DMode')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '1',
            '16:10': '3',
            'Native': '6',
            'Auto': '7'
        }

        AspectRatioCmdString = '~{0}60 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': '4:3',
            '3': '16:10',
            '6': 'Native',
            '7': 'Auto'
        }

        AspectRatioCmdString = '~{0}127 1\r'.format(self._DeviceID);
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ExecutiveModeCmdString = '~{0}103 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': '1',
            'DVI': '2',
            'Computer': '5',
            'BNC': '4',
            'Video': '10'
        }

        InputCmdString = '~{0}39 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '7': 'HDMI',
            '1': 'DVI',
            '2': 'Computer',
            '6': 'BNC',
            '5': 'Video'
        }

        InputCmdString = '~{0}121 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '1',
            'ECO': '2',
            'Advanced': '5'
        }

        LampModeCmdString = '~{0}110 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def SetLampPower(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 9
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LampPowerCmdString = '~{0}326 {1}\r'.format(self._DeviceID, value);
            self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLampPower')

    def UpdateLampPower(self, value, qualifier):

        LampPowerCmdString = '~{0}358 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampPower', LampPowerCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('LampPower', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampPower')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '~{0}108 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '~{0}00 {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '~{0}124 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == 'F\r':
            self.__CheckResponseForErrors(['{0} Command Failed'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
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