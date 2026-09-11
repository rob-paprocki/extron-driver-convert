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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FanSpeed': {'Parameters':['Line','Indoor Unit'], 'Status': {}},
            'LockMode': {'Parameters':['Line','Indoor Unit'], 'Status': {}},
            'OperationMode': {'Parameters':['Line','Indoor Unit'], 'Status': {}},
            'Power': {'Parameters':['Line','Indoor Unit'], 'Status': {}},
            'Temperature': {'Parameters':['Line','Indoor Unit'], 'Status': {}},
            }
        
    def SetFanSpeed(self, value, qualifier):

        LineStates = {
            'L1' : 'L1',
            'L2' : 'L2',
            'L3' : 'L3',
            'L4' : 'L4',
            'L5' : 'L5',
            'L6' : 'L6',
            'L7' : 'L7',
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        ValueStateValues = {
            'Low'    : 'l',
            'Medium' : 'm',
            'High'   : 'h',
            'Top'    : 't',
            'Auto'   : 'a'
        }

        if IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
            FanSpeedCmdString = 'fspeed {0}.{1:0>3} {2}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'], ValueStateValues[value])
            self.__SetHelper('FanSpeed', FanSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFanSpeed')

    def UpdateFanSpeed(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetLockMode(self, value, qualifier):

        LineStates = {
            'L1' : 'L1', 
            'L2' : 'L2', 
            'L3' : 'L3', 
            'L4' : 'L4', 
            'L5' : 'L5', 
            'L6' : 'L6', 
            'L7' : 'L7', 
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        ValueStateValues = {
            'Lock Power, Lock Operation Mode, Lock Temperature'       : '+',
            'Unlock Power, Unlock Operation Mode, Unlock Temperature' : '-',
            'Lock Power'                                              : '+o',
            'Unlock Power'                                            : '-o',
            'Lock Operation Mode'                                     : '+m',
            'Unlock Operation Mode'                                   : '-m',
            'Lock Temperature'                                        : '+t',
            'Unlock Temperature'                                      : '-t'
        }

        if IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
            LockModeCmdString = 'lock {0}.{1:0>3} {2}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'], ValueStateValues[value])
            self.__SetHelper('LockMode', LockModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLockMode')

    def UpdateLockMode(self, value, qualifier):

        LineStates = {
            'L1' : 'L1',
            'L2' : 'L2',
            'L3' : 'L3',
            'L4' : 'L4',
            'L5' : 'L5',
            'L6' : 'L6',
            'L7' : 'L7',
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        ValueStateValues = {
            '+o +m +t' : 'Lock Power, Lock Operation Mode, Lock Temperature',
            '-o -m -t' : 'Unlock Power, Unlock Operation Mode, Unlock Temperature',
            '+o -m -t' : 'Lock Power, Unlock Operation Mode, Unlock Temperature',
            '+o -m +t' : 'Lock Power, Unlock Operation Mode, Lock Temperature',
            '+o +m -t' : 'Lock Power, Lock Operation Mode, Unlock Temperature',
            '-o -m +t' : 'Unlock Power, Unlock Operation Mode, Lock Temperature',
            '-o +m -t' : 'Unlock Power, Lock Operation Mode, Unlock Temperature',
            '-o +m +t' : 'Unlock Power, Lock Operation Mode, Lock Temperature'
        }

        if IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
            LockModeCmdString = 'lock {0}.{1:0>3}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'])
            res = self.__UpdateHelper('LockMode', LockModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0:-2]]
                    self.WriteStatus('LockMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateLockMode')

    def SetOperationMode(self, value, qualifier):

        LineStates = {
            'L1' : 'L1', 
            'L2' : 'L2', 
            'L3' : 'L3', 
            'L4' : 'L4', 
            'L5' : 'L5', 
            'L6' : 'L6', 
            'L7' : 'L7', 
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        ValueStateValues = {
            'Cool' : 'cool', 
            'Heat' : 'heat', 
            'Fan' : 'fan', 
            'Dry' : 'dry', 
            'Auto' : 'auto'
        }

        if IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
            OperationModeCmdString = '{2} {0}.{1:0>3}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'], ValueStateValues[value])
            self.__SetHelper('OperationMode', OperationModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOperationMode')

    def UpdateOperationMode(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):

        LineStates = {
            'L1' : 'L1', 
            'L2' : 'L2', 
            'L3' : 'L3', 
            'L4' : 'L4', 
            'L5' : 'L5', 
            'L6' : 'L6', 
            'L7' : 'L7', 
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        ValueStateValues = {
            'On'  : 'on',
            'Off' : 'off'
        }

        if IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
            PowerCmdString = '{2} {0}.{1:0>3}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'], ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        LineStates = {
            'L1' : 'L1',
            'L2' : 'L2',
            'L3' : 'L3',
            'L4' : 'L4',
            'L5' : 'L5',
            'L6' : 'L6',
            'L7' : 'L7',
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        PowerStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        FanSpeedStateValues = {
            'Low'  : 'Low',
            'Med'  : 'Medium',
            'High' : 'High',
            'Top'  : 'Top',
            'Auto' : 'Auto'
        }

        OperationModeStateValues = {
            'Cool' : 'Cool',
            'Heat' : 'Heat',
            'Fan'  : 'Fan',
            'Dry'  : 'Dry',
            'Auto' : 'Auto'
        }

        qualifierKey = '{0} {1}'.format(qualifier['Line'], qualifier['Indoor Unit'])
        ctime = time.monotonic()
        if qualifierKey not in self.lastStatusQuery or ctime - self.lastStatusQuery[qualifierKey] > 1:
            self.lastStatusQuery[qualifierKey] = ctime
            if IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
                PowerCmdString = 'ls {0}.{1:0>3}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'])
                res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
                if res:
                    try:
                        responseList = res.split()
                        line = LineStates[responseList[0].split('.')[0]]
                        indoorUnit = int(responseList[0].split('.')[1])
                        value = PowerStateValues[responseList[1]] #Power
                        self.WriteStatus('Power', value, {'Line': line, 'Indoor Unit': indoorUnit})
                        value = int(responseList[2].replace('C','')) #Temperature
                        self.WriteStatus('Temperature', value, {'Line': line, 'Indoor Unit': indoorUnit})
                        value = FanSpeedStateValues[responseList[4]] #Fan Speed
                        self.WriteStatus('FanSpeed', value, {'Line': line, 'Indoor Unit': indoorUnit})
                        value = OperationModeStateValues[responseList[5]] #Operation Mode
                        self.WriteStatus('OperationMode', value, {'Line': line, 'Indoor Unit': indoorUnit})
                    except (KeyError, IndexError):
                        self.Error(['Invalid/Unexpected Response'])
            else:
                self.Discard('Invalid Command for UpdatePower')
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetTemperature(self, value, qualifier):

        LineStates = {
            'L1' : 'L1', 
            'L2' : 'L2', 
            'L3' : 'L3', 
            'L4' : 'L4', 
            'L5' : 'L5', 
            'L6' : 'L6', 
            'L7' : 'L7', 
            'L8' : 'L8'
        }

        IndoorUnitConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and IndoorUnitConstraints['Min'] <= qualifier['Indoor Unit'] <= IndoorUnitConstraints['Max']:
            TemperatureCmdString = 'temp {0}.{1:0>3} {2:.1F}\r\n'.format(LineStates[qualifier['Line']], qualifier['Indoor Unit'], value)
            self.__SetHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemperature')

    def UpdateTemperature(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '1'  : 'UID not found',
            '2'  : 'UID must be precise',
            '3'  : 'Command format is wrong',
            '4'  : 'Command execution failed',
            '5'  : 'Line is unused',
            '6'  : 'Command is unknown',
            '7'  : 'Line number is wrong',
            '8'  : 'Wrong function',
            '9'  : 'Command parameter is wrong',
            '10' : 'Command execution will be effective after reboot'
        }
        if response[0:3] == 'ERR':
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES.get(response[6:-2], 'Unknown error code'))])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Send('set verbose 0\r\n') #added this to obtain more error codes from the device (see pg. 13 of protocol)
        self.Send('set echo 0\r\n') #added to prevent status issues

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

