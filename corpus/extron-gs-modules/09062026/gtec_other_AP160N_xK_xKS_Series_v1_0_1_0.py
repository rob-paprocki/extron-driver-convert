from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'BatteryLevel': { 'Status': {}},
            'BatteryTemperature': { 'Status': {}},
            'BatteryVoltage': { 'Status': {}},
            'EstimatedRuntime': { 'Status': {}},
            'HighDetectFrequencyOnBypass': { 'Status': {}},
            'HighVoltageRangeOnBypass': { 'Status': {}},
            'InputFaultVoltage': { 'Status': {}},
            'InputFrequencyStatus': { 'Status': {}},
            'InputMaximumVoltage': { 'Status': {}},
            'InputMinimumVoltage': { 'Status': {}},
            'InputVoltage': { 'Status': {}},
            'LowDetectFrequencyOnBypass': { 'Status': {}},
            'LowVoltageRangeOnBypass': { 'Status': {}},
            'NegativeBUSVoltage': { 'Status': {}},
            'OutputCurrentPercent': { 'Status': {}},
            'OutputLoadPercentage': { 'Status': {}},
            'OutputVoltage': { 'Status': {}},
            'PositiveBUSVoltage': { 'Status': {}},
            'SystemMode': { 'Status': {}},
            'TemperatureStatus': { 'Status': {}},
            'UPSStatus': { 'Status': {}},
            'UPSStatus2': {'Parameters':['Type'], 'Status': {}},
            }

        
        self.lastFrequencyOnBypassUpdate = 0
        self.lastEstimatedRuntime = 0
        self.lastUPSStatus2Update = 0   

                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(([0-9]{0,3}\.[0-9])\r'), self.__MatchBatteryTemperature, None)
            self.AddMatchString(re.compile(b'\((?:[0-9]{0,3}\.[0-9] ){8}(?:[0-9]{0,3} ){3}(?:[0-9]{0,3}\.[0-9] ){3}([0-9]{0,5}) [0-9]{0,3} ([0-9])[0-7] [0-9]{8} [01]{8} [01][01]\r'), self.__MatchEstimatedRuntime, None)
            self.AddMatchString(re.compile(b'\(([0-9]{0,2}\.[0-9]) ([0-9]{0,2}\.[0-9]) ([0-9]{1,3}) ([0-9]{1,3}) E[a-z]+D[a-z]+\r'), self.__MatchHighDetectFrequencyOnBypass, None)
            self.AddMatchString(re.compile(b'\(([0-9]{0,3}\.[0-9]) ([0-9]{0,3}\.[0-9]) ([0-9]{0,3}\.[0-9]) ([0-9]{0,3}\.[0-9]) ([0-9]{0,3}\.[0-9]) ([0-9]{1,3}) ([0-9]{1,3}) ([0-9]{0,2}\.[0-9]) ([0-9]{1,3}) ([0-9]{1,3}) ([0-9]{0,3}\.[0-9]) ([0-9]{0,2}\.[0-9]) ([A-N]+)\r'), self.__MatchUPSStatus, None)
            self.AddMatchString(re.compile(b'\((?:[0-9]{0,3}\.[0-9] ){3}[0-9]{0,3} (?:[0-9]{0,2}\.[0-9]{0,2} ){3}([01]{8})\r'), self.__MatchUPSStatus2, None)
            self.AddMatchString(re.compile(b'^(\d{3})\r'), self.__MatchBatteryLevel, None)

    def UpdateBatteryLevel(self, value, qualifier):

        BatteryLevelCmdString = 'BL?\r'
        self.__UpdateHelper('BatteryLevel', BatteryLevelCmdString, value, qualifier)

    def __MatchBatteryLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryLevel', value, None)

    def UpdateBatteryTemperature(self, value, qualifier):

        BatteryTemperatureCmdString = 'TC?\r'
        self.__UpdateHelper('BatteryTemperature', BatteryTemperatureCmdString, value, qualifier)

    def __MatchBatteryTemperature(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('BatteryTemperature', value, None)

    def UpdateEstimatedRuntime(self, value, qualifier):

        EstimatedRuntimeCmdString = 'Q6\r'
        self.__UpdateHelper('EstimatedRuntime', EstimatedRuntimeCmdString, value, qualifier)

    def __MatchEstimatedRuntime(self, match, tag):

        ValueStateValues = {
            '0' : 'Power On', 
            '1' : 'Standby', 
            '2' : 'Bypass', 
            '3' : 'Line', 
            '4' : 'Battery', 
            '5' : 'Battery Test', 
            '6' : 'Fault', 
            '7' : 'Converter', 
            '8' : 'Eco', 
            '9' : 'ShutDown'
        }
        
        value = int(match.group(1).decode())
        self.WriteStatus('EstimatedRuntime', value, None)
        
        SystemModeValue = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SystemMode', SystemModeValue, None)

    def UpdateHighDetectFrequencyOnBypass(self, value, qualifier):

        HighDetectFrequencyOnBypassCmdString = 'QP\r'
        self.__UpdateHelper('HighDetectFrequencyOnBypass', HighDetectFrequencyOnBypassCmdString, value, qualifier)

    def __MatchHighDetectFrequencyOnBypass(self, match, tag):

        self.WriteStatus('LowDetectFrequencyOnBypass', float(match.group(1)), None)
        
        self.WriteStatus('HighDetectFrequencyOnBypass', float(match.group(2)), None)
        
        self.WriteStatus('LowVoltageRangeOnBypass', int(match.group(3)), None)
        
        self.WriteStatus('HighVoltageRangeOnBypass', int(match.group(4)), None)

    def UpdateHighVoltageRangeOnBypass(self, value, qualifier):

        self.UpdateHighDetectFrequencyOnBypass(None, qualifier)

    def UpdateLowDetectFrequencyOnBypass(self, value, qualifier):

        self.UpdateHighDetectFrequencyOnBypass(None, qualifier)

    def UpdateLowVoltageRangeOnBypass(self, value, qualifier):

        self.UpdateHighDetectFrequencyOnBypass(None, qualifier)

    def UpdateSystemMode(self, value, qualifier):

        self.UpdateEstimatedRuntime(None, qualifier)

    def UpdateUPSStatus(self, value, qualifier):


        UPSStatusCmdString = 'Q4\r'
        self.__UpdateHelper('UPSStatus', UPSStatusCmdString, value, qualifier)

    def __MatchUPSStatus(self, match, tag):

        UPSStates = {
            'A' : 'Utility Fail', 
            'B' : 'Battery Low', 
            'C' : 'Bypass/Boost Active', 
            'D' : 'UPS Failed', 
            'E' : 'Test in Progress', 
            'F' : 'Shutdown Active', 
            'G' : 'SITE fault', 
            'H' : 'EPROM fail', 
            'I' : 'Test passed - Result: OK', 
            'J' : 'Test passed - Result: Failed', 
            'K' : 'Test not Possible or Inhibited', 
            'L' : 'Test Status Unknown', 
            'M' : 'UPS normal mode', 
            'N' : 'UPS 110% overload'
        }
        
        
        self.WriteStatus('InputVoltage', float(match.group(1)), None)
        
        self.WriteStatus('InputMaximumVoltage', float(match.group(2)), None)
        
        self.WriteStatus('InputMinimumVoltage', float(match.group(3)), None)
        
        self.WriteStatus('InputFaultVoltage', float(match.group(4)), None)
        
        self.WriteStatus('OutputVoltage', float(match.group(5)), None)
        
        self.WriteStatus('OutputCurrentPercent', int(match.group(6)), None)
        
        self.WriteStatus('OutputLoadPercentage', int(match.group(7)), None)
        
        self.WriteStatus('InputFrequencyStatus', float(match.group(8)), None)
        
        self.WriteStatus('PositiveBUSVoltage', int(match.group(9)), None)
        
        self.WriteStatus('NegativeBUSVoltage', int(match.group(10)), None)
        
        self.WriteStatus('BatteryVoltage', float(match.group(11)), None)
        
        self.WriteStatus('TemperatureStatus', float(match.group(12)), None)
        
        ups_status_val = ''
        for val in match.group(13).decode():
            ups_status_val =  ', '.join([ups_status_val, UPSStates[val]])
        self.WriteStatus('UPSStatus', ups_status_val[2:], None)

    def UpdateUPSStatus2(self, value, qualifier):

        UPSStatus2CmdString = 'Q1\r'
        self.__UpdateHelper('UPSStatus2', UPSStatus2CmdString, value, qualifier)

    def __MatchUPSStatus2(self, match, tag):

        ValueStateValues = {
            '1' : 'True', 
            '0' : 'False'
        }
        ValueStateValues2 = {
            '0' : 'True', 
            '1' : 'False'
        }

        val = match.group(1).decode()
        
        self.WriteStatus('UPSStatus2', ValueStateValues[val[0]], {'Type' :'Utility Fail'})
        self.WriteStatus('UPSStatus2', ValueStateValues[val[1]], {'Type' :'Battery Low'})
        self.WriteStatus('UPSStatus2', ValueStateValues[val[2]], {'Type' :'Bypass/Boost Active'})
        self.WriteStatus('UPSStatus2', ValueStateValues[val[3]], {'Type' :'UPS Failed'})
        self.WriteStatus('UPSStatus2', ValueStateValues[val[4]], {'Type' :'UPS Type is Standby'})
        self.WriteStatus('UPSStatus2', ValueStateValues[val[5]], {'Type' :'Test in Progress'})
        self.WriteStatus('UPSStatus2', ValueStateValues[val[6]], {'Type' :'Shutdown Active'})
        self.WriteStatus('UPSStatus2', ValueStateValues2[val[7]], {'Type' :'Battery Silence'})

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

    def __init__(self, Host, Port, Baud=2400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

