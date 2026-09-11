from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AirIntakeTemperature': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Parameters':['Sensor'],'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'InputPortConfiguration': {'Status': {}},
            'LampHours': {'Status': {}},
            'LensMove': {'Parameters':['Direction'],'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'SST\+TEMP!002 000 \"(-?\d{1,3}) .C\" \"Air Intake Temperature \(Temp 2\)\"'), self.__MatchAirIntakeTemperature, None)
            self.AddMatchString(compile(b'\(KEN\+(FRNT|REAR|WIRE|HDBT)!00([01])\)'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'\(FRZ!00([01])\)'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'\(SIN!(\d{3}).*\)'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\(HIS\+LMP1!0000 \".*\"\" \d{4} \d{4} \d{4} \d{4} (\d{4})\)'), self.__MatchLampHours, None)
            self.AddMatchString(compile(b'\(PWR!0([01]{2}).*\)'), self.__MatchPower, None)
            self.AddMatchString(compile(b'\(SHU!00([01])\)'), self.__MatchShutter, None)
            self.AddMatchString(compile(b'ERR(\d{5})'), self.__MatchError, None)

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def UpdateAirIntakeTemperature(self, value, qualifier):

        AirIntakeTemperatureCmdString = '(SST+TEMP?2)'
        self.__UpdateHelper('AirIntakeTemperature', AirIntakeTemperatureCmdString, value, qualifier)

    def __MatchAirIntakeTemperature(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('AirIntakeTemperature', value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Default': '0',
            'None': '1',
            'Full Size': '2',
            'Full Width': '3',
            'Full Height': '4',
        }

        AspectRatioCmdString = '(SZP {})'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(ASU)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        SensorStates = {
            'Front IR Keypad': '(KEN+FRNT {}',
            'Rear IR Keypad': '(KEN+REAR {}',
            'Wired Keypad': '(KEN+WIRE {}',
            'IR over HDBaseT': '(KEN+HDBT {}',
        }

        ValueStateValues = {
            'On': '1)',
            'Off': '0)',
        }

        sensor = qualifier['Sensor']
        if value in ValueStateValues and sensor in SensorStates:
            ExecutiveModeCmdString = SensorStates[sensor].format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        SensorStates = {
            'Front IR Keypad': '(KEN+FRNT?)',
            'Rear IR Keypad': '(KEN+REAR?)',
            'Wired Keypad': '(KEN+WIRE?)',
            'IR over HDBaseT': '(KEN+HDBT?)',
        }
        sensor = qualifier['Sensor']
        if sensor in SensorStates:
            ExecutiveModeCmdString = SensorStates[sensor]
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        SensorStates = {
            'FRNT': 'Front IR Keypad',
            'REAR': 'Rear IR Keypad',
            'WIRE': 'Wired Keypad',
            'HDBT': 'IR over HDBaseT',
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        qualifier = dict()
        qualifier['Sensor'] = SensorStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        FreezeCmdString = '(FRZ {})'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '(FRZ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateConstraints = {
            'Min': 1,
            'Max': 20,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueStateConstraints):
            InputCmdString = 'SIN {}'.format(ValueStateConstraints['Value'])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 20:
            value = '{}'.format(value)
            self.WriteStatus('Input', value, None)

    def SetInputPortConfiguration(self, value, qualifier):

        ValueStateValues = {
            'One-Port': '1',
            'Two-Port': '2',
            'Four-Port Columns': '3',
            'Four-Port Quadrants': '4',
        }

        InputPortConfigurationCmdString = '(SIN+PORT {})'.format(ValueStateValues[value])
        self.__SetHelper('InputPortConfiguration', InputPortConfigurationCmdString, value, qualifier)

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = '(HIS+LMP1?)'
        self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)

    def __MatchLampHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampHours', value, None)

    def SetLensMove(self, value, qualifier):

        DirectionStates = {
            'Horizontal': 'H',
            'Vertical': 'V',
        }

        ValueStateValues = {
            'Left / Down': '-1',
            'Stop': '0',
            'Right / Up': '1',
        }

        direction = qualifier['Direction']
        if value in ValueStateValues and direction in DirectionStates:
            LensMoveCmdString = '(LMV+{}RUN {})'.format(DirectionStates[direction], ValueStateValues[value])
            self.__SetHelper('LensMove', LensMoveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensMove')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        OnScreenDisplayCmdString = '(OSD {})'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = '(PWR {})'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
            '11': 'Warming Up',
            '10': 'Cooling Down',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open': '0',
            'Close': '1',
        }

        ShutterCmdString = '(SHU {})'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = '(SHU?)'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)
            
    def __MatchError(self, match, tag):

        Errors = {
            3:   'Invalid Parameter',
            4:   'Too Many Parameters',
            5:   'Too Few Parameters',
            6:   'Channel not found',
            7:   'Command not executed',
            8:   'Checksum error',
            9:   'Unknown request',
            10:  'Error receiving serial data',
            101: 'Control Not Found',
            102: 'Subcontrol Not Found',
            103: 'Wrong Control Type',
            104: 'Invalid Value',
        }
        value = int(match.group(1).decode())
        self.Error([Errors[value]])

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

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

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

