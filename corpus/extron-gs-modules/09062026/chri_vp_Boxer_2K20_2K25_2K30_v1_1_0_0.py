from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': { 'Status': {}},
            'ExecutiveMode': {'Parameters':['Sensor'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'InputPortConfiguration': { 'Status': {}},
            'LampHours': {'Parameters':['Number'], 'Status': {}},
            'LampSelection': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            }

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(KEN\+(FRNT|REAR|WIRE|HDBT)!00(0|1)\)'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\(FRZ!00(0|1)\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN!([0-9]{3}).*?\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(HIS\+LMP([1-6])!0000 \".*?\"\" [\d]{4} [\d]{4} [\d]{4} [\d]{4} ([\d]{4})\)'), self.__MatchLampHours, None)
            
            self.AddMatchString(re.compile(b'\(LOP!00([1-6]).*?\)'), self.__MatchLampSelection, None)
            self.AddMatchString(re.compile(b'\(PWR!(000|001|010|011).*?\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!(0|1) \"(Open|Closed)\"\)'), self.__MatchShutter, None)
            self.AddMatchString(re.compile(b'ERR(\d{5})'), self.__MatchError, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(ASU)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):


        SensorStates = {
            'Front IR Keypad'   : 'FRNT',
            'Rear IR Keypad'    : 'REAR',
            'Wired Keypad'      : 'WIRE',
            'IR over HDBaseT'   : 'HDBT'
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        sensor_val = qualifier['Sensor']
        if sensor_val in SensorStates:
            ExecutiveModeCmdString = '(KEN+{0} {1})'.format(SensorStates[sensor_val], ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        SensorStates = {
            'Front IR Keypad'   : '(KEN+FRNT?)',
            'Rear IR Keypad'    : '(KEN+REAR?)',
            'Wired Keypad'      : '(KEN+WIRE?)',
            'IR over HDBaseT'   : '(KEN+HDBT?)'
        }

        sensor_val = qualifier['Sensor']
        if sensor_val in SensorStates:
            ExecutiveModeCmdString = SensorStates[sensor_val]
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        SensorStates = {
            'FRNT' : 'Front IR Keypad',
            'REAR' : 'Rear IR Keypad',
            'WIRE' : 'Wired Keypad',
            'HDBT' : 'IR over HDBaseT'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Sensor'] = SensorStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(FRZ 1)', 
            'Off' : '(FRZ 0)'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '(FRZ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):


        if 1 <= int(value) <= 43:               # Enumeration of 20 arbitary values, subject to change based on available inputs/ configured input cards.
            InputCmdString = '(SIN {0})'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = str(int(match.group(1).decode()))
        self.WriteStatus('Input', value, None)

    def SetInputPortConfiguration(self, value, qualifier):

        ValueStateValues = {
            'One-Port'              : '(SIN+PORT 1)', 
            'Two-Port'              : '(SIN+PORT 2)', 
            'Four-Port Columns'     : '(SIN+PORT 3)', 
            'Four-Port Quadrants'   : '(SIN+PORT 4)'
        }

        InputPortConfigurationCmdString = ValueStateValues[value]
        self.__SetHelper('InputPortConfiguration', InputPortConfigurationCmdString, value, qualifier)
    def UpdateLampHours(self, value, qualifier):

        lamp_val = qualifier['Number']
        if 1 <= int(lamp_val) <= 6:
            LampHoursCmdString = '(HIS+LMP{0}?)'.format(lamp_val)
            self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLampHours')

    def __MatchLampHours(self, match, tag):

        lamp_val  = match.group(1).decode()
        hours_val = int(match.group(2).decode())
        self.WriteStatus('LampHours', hours_val, {'Number' : lamp_val})

    def SetLampSelection(self, value, qualifier):

        ValueStateValues = {
            'A1' : '(LOP 1)', 
            'A2' : '(LOP 2)', 
            'A3' : '(LOP 3)', 
            'B1' : '(LOP 4)', 
            'B2' : '(LOP 5)', 
            'B3' : '(LOP 6)'
        }

        LampSelectionCmdString = ValueStateValues[value]
        self.__SetHelper('LampSelection', LampSelectionCmdString, value, qualifier)

    def UpdateLampSelection(self, value, qualifier):

        LampSelectionCmdString = '(LOP?)'
        self.__UpdateHelper('LampSelection', LampSelectionCmdString, value, qualifier)

    def __MatchLampSelection(self, match, tag):

        ValueStateValues = {
            '1' : 'A1', 
            '2' : 'A2', 
            '3' : 'A3', 
            '4' : 'B1', 
            '5' : 'B2', 
            '6' : 'B3'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampSelection', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(OSD 1)', 
            'Off' : '(OSD 0)'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(PWR 1)', 
            'Off' : '(PWR 0)'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '001' : 'On', 
            '000' : 'Off',              #<Standby> in protocol 
            '011' : 'Warming Up', 
            '010' : 'Cooling Down'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open'  : '(SHU 0)', 
            'Close' : '(SHU 1)'
        }

        ShutterCmdString = ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = '(SHU?)'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            '0' : 'Open', 
            '1' : 'Close'
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
        self.counter = 0

        value = int(match.group(1).decode())
        Errors = {
                  3 : 'Invalid Parameter.',
                  4 : 'Too Many Parameters.',
                  5 : 'Too Few Parameters.',
                  6 : 'Channel not found.',
                  7 : 'Command not executed.',
                  8 : 'Checksum error.',
                  9 : 'Unknown request.',
                  10 : 'Error receiving serial data.',
                  101 : 'Control Not Found.',
                  102 : 'Subcontrol Not Found.',
                  103 : 'Wrong Control Type.',
                  104 : 'Invalid Value.',
                  105 : 'Disabled Control.',
                  106 : 'Invalid Language.',
                  107 : 'Exceeded List Size.',
                  110 : 'Communication Timeout.',
                  111 : 'Communications Failure.',
                  112 : 'Failed to set Hardware.',
                  113 : 'Bad File.',
                  114 : 'Memory Failure.',
                  115 : 'Not Implemented.',
                  116 : 'Invalid Security Token.',
                  117 : 'Invalid Access Group.',
                  118 : 'System Busy - Try Again Later.',
                  }
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
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

