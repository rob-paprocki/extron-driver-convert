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

        self.Models = {
            }

        self.Commands = {
            'ConnectionStatus'      : {'Status': {}},
            'ControlButtonEmulation': {'Parameters':['Device Number'], 'Status': {}},
            'DoButton'              : {'Parameters':['Device Number'], 'Status': {}},
            'DoLogic'               : {'Parameters':['Device Number','Logic Output Number'], 'Status': {}},
            'DoMacro'               : {'Parameters':['Device Number'], 'Status': {}},
            'DoMatrixAction'        : {'Parameters':['Device Number','Assignment Switch'], 'Status': {}},
            'LogicInputContacts'    : {'Parameters':['Input Contact Number'], 'Status': {}},
            'LogicStatus'           : {'Parameters':['Device Number','Logic Output Number'], 'Status': {}},
            'InputTieStatus'        : {'Parameters':['Device Number','Input'], 'Status': {}},
            'PowerUpResetEvent'     : {'Status': {}},
            'RemotePort'            : {'Parameters':['Port'], 'Status': {}},
            }

        self.c_time_tie_status = {
            '01' : 0,
            '02' : 0,
            '03' : 0,
            '04' : 0,
            '05' : 0,
            '06' : 0,
            '07' : 0,
            '08' : 0
        }

        self.c_time_logic_status = {
            '01' : 0,
            '02' : 0,
            '03' : 0,
            '04' : 0,
            '05' : 0,
            '06' : 0,
            '07' : 0,
            '08' : 0
        }

    def SetControlButtonEmulation(self, value, qualifier):

        DeviceSelectStates = {
            '1'             : 0x6C, 
            '2'             : 0x6D, 
            '3'             : 0x6F, 
            '4'             : 0x73, 
            '1 & 2'         : 0x6E, 
            '1 & 3'         : 0x70, 
            '2 & 3'         : 0x71, 
            '1 & 2 & 3'     : 0x72, 
            '1 & 4'         : 0x74, 
            '2 & 4'         : 0x75, 
            '3 % 4'         : 0x77, 
            '1 & 2 & 4'     : 0x76, 
            '1 & 3 & 4'     : 0x78, 
            '2 & 3 & 4'     : 0x79, 
            '1 & 2 & 3 & 4' : 0x7A
        }

        ValueStateValues = {
            '1'  : 0x42, 
            '2'  : 0x43, 
            '3'  : 0x44, 
            '4'  : 0x45, 
            '5'  : 0x46, 
            '6'  : 0x47, 
            '7'  : 0x48, 
            '8'  : 0x49, 
            '9'  : 0x4A, 
            '10' : 0x4B, 
            '11' : 0x4C, 
            '12' : 0x4D, 
            '13' : 0x4E, 
            '14' : 0x4F, 
            '15' : 0x50, 
            '16' : 0x51, 
            '17' : 0x52, 
            '18' : 0x53, 
            '19' : 0x54, 
            '20' : 0x55, 
            '21' : 0x56, 
            '22' : 0x57, 
            '23' : 0x58, 
            '24' : 0x59, 
            '25' : 0x5A, 
            '26' : 0x5B, 
            '27' : 0x5C, 
            '28' : 0x5D, 
            '29' : 0x5E, 
            '30' : 0x5F, 
            '31' : 0x60, 
            '32' : 0x62, 
            '33' : 0x63, 
            '34' : 0x64, 
            '35' : 0x65, 
            '36' : 0x66, 
            '37' : 0x67, 
            '38' : 0x68, 
            '39' : 0x69, 
            '40' : 0x6A
        }

        if qualifier['Device Number'] == 'Broadcast':
            ControlButtonEmulationCmdString = pack('B', ValueStateValues[value])
        else:
            ControlButtonEmulationCmdString = pack('>2B',DeviceSelectStates[qualifier['Device Number']],ValueStateValues[value])
        self.__SetHelper('ControlButtonEmulation', ControlButtonEmulationCmdString, value, qualifier)

    def SetDoButton(self, value, qualifier):

        DeviceNumberStates = {
            '1' : '01', 
            '2' : '02', 
            '3' : '04', 
            '4' : '08', 
            '5' : '10', 
            '6' : '20', 
            '7' : '40', 
            '8' : '80'
        }

        if 0 <= int(value) <= 199:
            DoButtonCmdString = '{0:02X}?>08{1}#'.format(int(value), DeviceNumberStates[qualifier['Device Number']])
            self.__SetHelper('DoButton', DoButtonCmdString, value, qualifier)
        else:
            print('Inappropriate Command for SetDoButton')

    def SetDoLogic(self, value, qualifier):

        DeviceNumberStates = {
            '1' : '01', 
            '2' : '02', 
            '3' : '04', 
            '4' : '08', 
            '5' : '10', 
            '6' : '20', 
            '7' : '40', 
            '8' : '80'
        }

        LogicOutputNumberStates = {
            '1' : '00', 
            '2' : '01', 
            '3' : '02', 
            '4' : '03', 
            '5' : '04', 
            '6' : '05', 
            '7' : '06', 
            '8' : '07', 
            '9' : '08', 
            '10' : '09', 
            '11' : '0:', 
            '12' : '0;', 
            '13' : '0<', 
            '14' : '0=', 
            '15' : '0>', 
            '16' : '0?'
        }

        ValueStateValues = {
            'NOP' : '00', 
            'Turn Off' : '01', 
            'Turn On' : '02', 
        }

        DoLogicCmdString = '{0}{1}08{2}*'.format(ValueStateValues[value], LogicOutputNumberStates[qualifier['Logic Output Number']], DeviceNumberStates[qualifier['Device Number']])
        self.__SetHelper('DoLogic', DoLogicCmdString, value, qualifier)

    def SetDoMacro(self, value, qualifier):

        DeviceNumberStates = {
            '1' : '01', 
            '2' : '02', 
            '3' : '04', 
            '4' : '08', 
            '5' : '10', 
            '6' : '20', 
            '7' : '40', 
            '8' : '80'
        }

        
        if 0 <= int(value) <= 49:
            temp_value = int(value) + 128
            DoMacroCmdString = '{0:02X}08{1}!'.format(temp_value, DeviceNumberStates[qualifier['Device Number']])
            self.__SetHelper('DoMacro', DoMacroCmdString, value, qualifier)
        else:
            print('Inappropriate Command for SetDoMacro')

    def SetDoMatrixAction(self, value, qualifier):

        DeviceNumberStates = {
            '1' : '01', 
            '2' : '02', 
            '3' : '03', 
            '4' : '04', 
            '5' : '05', 
            '6' : '06', 
            '7' : '07', 
            '8' : '08'
        }

        AssignmentSwitchStates = {
            'In 1 - Out 1' : '00', 
            'In 1 - Out 2' : '01', 
            'In 1 - Out 3' : '02', 
            'In 1 - Out 4' : '03', 
            'In 2 - Out 1' : '04', 
            'In 2 - Out 2' : '05', 
            'In 2 - Out 3' : '06', 
            'In 2 - Out 4' : '07', 
            'In 3 - Out 1' : '08', 
            'In 3 - Out 2' : '09', 
            'In 3 - Out 3' : '0:', 
            'In 3 - Out 4' : '0;', 
            'In 4 - Out 1' : '0<', 
            'In 4 - Out 2' : '0=', 
            'In 4 - Out 3' : '0>', 
            'In 4 - Out 4' : '0?', 
            'In 5 - Out 1' : '10', 
            'In 5 - Out 2' : '11', 
            'In 5 - Out 3' : '12', 
            'In 5 - Out 4' : '13', 
            'In 6 - Out 1' : '14', 
            'In 6 - Out 2' : '15', 
            'In 6 - Out 3' : '16', 
            'In 6 - Out 4' : '17', 
            'In 7 - Out 1' : '18', 
            'In 7 - Out 2' : '19', 
            'In 7 - Out 3' : '1:', 
            'In 7 - Out 4' : '1;', 
            'In 8 - Out 1' : '1<', 
            'In 8 - Out 2' : '1=', 
            'In 8 - Out 3' : '1>', 
            'In 8 - Out 4' : '1?'
        }

        ValueStateValues = {
            'NOP' : '00', 
            'Turn Off' : '01', 
            'Turn On' : '02', 
        }

        DoMatrixActionCmdString = '{0}{1}08{2}\''.format(ValueStateValues[value], AssignmentSwitchStates[qualifier['Assignment Switch']], DeviceNumberStates[qualifier['Device Number']])
        self.__SetHelper('DoMatrixAction', DoMatrixActionCmdString, value, qualifier)

    def SetLogicInputContacts(self, value, qualifier):

        InputContactNumberStates = {
            '1'  : 0xA0, 
            '2'  : 0xA1, 
            '3'  : 0xA2, 
            '4'  : 0xA3, 
            '5'  : 0xA8, 
            '6'  : 0xA9, 
            '7'  : 0xAA, 
            '8'  : 0xAB, 
            '9'  : 0xB0, 
            '10' : 0xB1, 
            '11' : 0xB2, 
            '12' : 0xB3, 
            '13' : 0xB8, 
            '14' : 0xB9, 
            '15' : 0xBA, 
            '16' : 0xBB
        }

        ValueStateValues = {
            'Open' : 0x04, 
            'Close' : 0x00
        }

        cmdState = InputContactNumberStates[qualifier['Input Contact Number']] + ValueStateValues[value]
        LogicInputContactsCmdString = pack('B', cmdState)
        self.__SetHelper('LogicInputContacts', LogicInputContactsCmdString, value, qualifier)

    def UpdateLogicStatus(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        DeviceNumberStates = {
            '1' : '01', 
            '2' : '02', 
            '3' : '03', 
            '4' : '04', 
            '5' : '05', 
            '6' : '06', 
            '7' : '07', 
            '8' : '08'
        }
        
        d_num = DeviceNumberStates[qualifier['Device Number']]
        LogicStatusCmdString = '08{0}('.format(d_num)
        res = self.__UpdateHelper('LogicStatus', LogicStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[0:-1]
                temp_value = ''
                for num in value:
                    temp_value = temp_value + '{0:04b}'.format(int(num))

                for enum, val in enumerate(temp_value):
                    qualifier = {}
                    qualifier['Device Number'] = d_num.strip('0')
                    qualifier['Logic Output Number'] = str(16 - enum)
                    value = ValueStateValues[val]
                    self.WriteStatus('LogicStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLogicStatus')

    def UpdateInputTieStatus(self, value, qualifier):

        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '4' : '3', 
            '8' : '4'
        }

        DeviceNumberStates = {
            '1' : '01', 
            '2' : '02', 
            '3' : '03', 
            '4' : '04', 
            '5' : '05', 
            '6' : '06', 
            '7' : '07', 
            '8' : '08'
        }

        d_num = DeviceNumberStates[qualifier['Device Number']]
        InputTieStatusCmdString = '08{0}%'.format(d_num)
        res = self.__UpdateHelper('InputTieStatus', InputTieStatusCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = res[:-1][::-1]
                for enum, val in enumerate(value):
                    qualifier = {}
                    qualifier['Input'] = str(enum + 1)
                    qualifier['Device Number'] = d_num.strip('0')
                    self.WriteStatus('InputTieStatus', ValueStateValues[val], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInputTieStatus')

    def SetPowerUpResetEvent(self, value, qualifier):

        PowerUpResetEventCmdString = b'\xC7'
        self.__SetHelper('PowerUpResetEvent', PowerUpResetEventCmdString, value, qualifier)

    def SetRemotePort(self, value, qualifier):

        PortStates = {
            '1' : 0x00, 
            '2' : 0x28, 
            '3' : 0x50, 
            '4' : 0x78
        }

        if 1 <= int(value) <= 40:
            cmdState = PortStates[qualifier['Port']] + (int(value)-1)
            RemotePortCmdString = pack('B', cmdState)
            self.__SetHelper('RemotePort', RemotePortCmdString, value, qualifier)
        else:
            print('Inappropriate Command for SetRemotePort')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
                return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

