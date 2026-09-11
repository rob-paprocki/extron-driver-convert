from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
            'AlarmMode': { 'Status': {}},
            'AlarmMute': { 'Status': {}},
            'BatteryCharge': { 'Status': {}},
            'BatteryHealth': { 'Status': {}},
            'BatteryLoad': { 'Status': {}},
            'BatteryRuntime': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'OutletAmperage': {'Parameters':['Outlet'], 'Status': {}},
            'OutletControl': {'Parameters':['Outlet','Delay'], 'Status': {}},
            'OutletName': {'Parameters':['Outlet'], 'Status': {}},
            'OutletStatus': {'Parameters':['Outlet'], 'Status': {}},
            'OutletVoltage': {'Parameters':['Outlet'], 'Status': {}},
            'OutletWattage': {'Parameters':['Outlet'], 'Status': {}},
            'PowerLost': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\?UPSStatus=(\d+),(\d+),(Good|Bad),(True|False),(\d+),(True|False),(True|False)\r\n'), self.__MatchBatteryCharge, None)
            self.AddMatchString(re.compile(b'\?Firmware=([\d\.]+)\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'\?OutletPowerStatus=(\d{1,2}),(\d+.\d+),(\d+.\d+),(\d+.\d+)\r\n'), self.__MatchOutletAmperage, None)
            self.AddMatchString(re.compile(b'\?OutletName={([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)},{([\S ]+)}\r\n'), self.__MatchOutletName, None)
            self.AddMatchString(re.compile(b'\?OutletStatus=([01]),([01]),([01]),([01]),([01]),([01]),([01]),([01]),([01]),([01]),([01]),([01])\r\n'), self.__MatchOutletStatus, None)
            self.AddMatchString(re.compile(b'#Error\r\n'), self.__MatchError, None)

    def UpdateAlarmMode(self, value, qualifier):

        self.UpdateBatteryCharge(value, qualifier)

    def UpdateAlarmMute(self, value, qualifier):

        self.UpdateBatteryCharge(value, qualifier)

    def UpdateBatteryCharge(self, value, qualifier):

        BatteryChargeCmdString = '?UPSStatus\n'
        self.__UpdateHelper('BatteryCharge', BatteryChargeCmdString, value, qualifier)

    def __MatchBatteryCharge(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BatteryCharge', value, None)
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BatteryLoad', value, None)
        value = match.group(3).decode()
        self.WriteStatus('BatteryHealth', value, None)
        value = match.group(4).decode()
        self.WriteStatus('PowerLost', value, None)
        value = int(match.group(5))
        self.WriteStatus('BatteryRuntime', value, None)
        ValueStateValues = {
            'True'  : 'Enabled',
            'False' : 'Disabled'
        }

        value = ValueStateValues[match.group(6).decode()]
        self.WriteStatus('AlarmMode', value, None)
        ValueStateValues = {
            'True'  : 'On',
            'False' : 'Off'
        }

        value = ValueStateValues[match.group(7).decode()]
        self.WriteStatus('AlarmMute', value, None)

    def UpdateBatteryHealth(self, value, qualifier):

        self.UpdateBatteryCharge(value, qualifier)

    def UpdateBatteryLoad(self, value, qualifier):

        self.UpdateBatteryCharge(value, qualifier)

    def UpdateBatteryRuntime(self, value, qualifier):

        self.UpdateBatteryCharge(value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '?Firmware\n'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def UpdateOutletAmperage(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= 12:
            OutletAmperageCmdString = '?OutletPowerStatus={}\n'.format(qualifier['Outlet'])
            self.__UpdateHelper('OutletAmperage', OutletAmperageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletAmperage')

    def __MatchOutletAmperage(self, match, tag):

        outlet = match.group(1).decode()
        if 1 <= int(outlet) <= 12:
            qualifier = {'Outlet' : outlet}
            value = float(match.group(2).decode())
            self.WriteStatus('OutletAmperage', value, qualifier)
            value = float(match.group(3).decode())
            self.WriteStatus('OutletWattage', value, qualifier)
            value = float(match.group(4).decode())
            self.WriteStatus('OutletVoltage', value, qualifier)

    def SetOutletControl(self, value, qualifier):

        ValueStateValues = {
            'On'     : 'ON',
            'Off'    : 'OFF',
            'Toggle' : 'TOGGLE',
            'Reset'  : 'RESET'
        }

        if 1 <= int(qualifier['Outlet']) <= 12 and 1 <= qualifier['Delay'] <= 600 and value in ValueStateValues:
            if value == 'Reset': # Per API, Delay can only be used for 'Reset'
                OutletControlCmdString = '!OutletSet={},{},{}\n'.format(qualifier['Outlet'], ValueStateValues[value], qualifier['Delay'])
            else:
                OutletControlCmdString = '!OutletSet={},{}\n'.format(qualifier['Outlet'], ValueStateValues[value])
            self.__SetHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletControl')
            
    def UpdateOutletName(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= 12:
            OutletNameCmdString = '?OutletName\n'
            self.__UpdateHelper('OutletName', OutletNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletName')

    def __MatchOutletName(self, match, tag):

        for i in range(1, 13):
            value = match.group(i).decode()
            self.WriteStatus('OutletName', value, {'Outlet' : str(i)})

    def UpdateOutletStatus(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= 12:
            OutletStatusCmdString = '?OutletStatus\n'
            self.__UpdateHelper('OutletStatus', OutletStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletStatus')

    def __MatchOutletStatus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        for i in range(1, 13):
            value = ValueStateValues[match.group(i).decode()]
            self.WriteStatus('OutletStatus', value, {'Outlet' : str(i)})

    def UpdateOutletVoltage(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= 12:
            self.UpdateOutletAmperage(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletVoltage')

    def UpdateOutletWattage(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= 12:
            self.UpdateOutletAmperage(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletWattage')

    def UpdatePowerLost(self, value, qualifier):

        self.UpdateBatteryCharge(value, qualifier)

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

        self.Error(['An error has occured. Please see the device log page for further detailed error messages.'])

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()