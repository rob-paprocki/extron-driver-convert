from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'BatteryBars': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryCapacityCurrent': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryCapacityCurrentMax': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryCapacityMax': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryCharge': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryChargingCycles': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryDetected': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryErrorStatus': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryHealth': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryState': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryTemperatureCelsius': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryTemperatureFahrenheit': {'Parameters': ['Bay Number'], 'Status': {}},
            'BatteryTimeToFull': {'Parameters': ['Bay Number'], 'Status': {}},
            'DeviceID': { 'Status': {}},
            'DeviceIDStatus': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Flash': { 'Status': {}},
            'Model': { 'Status': {}},
            'StorageMode': { 'Status': {}},
        }                    

        self.bay_number_range = tuple(str(x) for x in range(1, 9))
        self.cap_range = br'[0-5]\d{4}|6(?:[0-4]\d{3}|5(?:[0-4]\d{2}|5(?:[0-2]\d|3[0-3])))'
        self.state_range = br'FULL|CALCULATING|NORMAL|WARM|WARM_FULL|HOT|COLD|PRECHARGE|READY_TO_STORE|' \
                           br'DISCHARGE_CALC|DISCHARGING|DISCHARGING_WARM|DISCHARGING_COLD|ERROR|NO_BATT'
        self.bat_full_range = br'[0-5]\d{4}|6(?:[0-4]\d{3}|5(?:[0-4]\d{2}|5(?:[0-2]\d|33)))'
        
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_BARS (00[0-5]|255) >'), self.__MatchBatteryBars, None)
            self.AddMatchString(compile(br''.join([br'< REP ([1-8]) BATT_CURRENT_CAPACITY (', self.cap_range, br') >'])), self.__MatchBatteryCapacityCurrent, None)
            self.AddMatchString(compile(br''.join([br'< REP ([1-8]) BATT_CURRENT_CAPACITY_MAX (', self.cap_range, br') >'])), self.__MatchBatteryCapacityCurrentMax, None)
            self.AddMatchString(compile(br''.join([br'< REP ([1-8]) BATT_CAPACITY_MAX (', self.cap_range, br') >'])), self.__MatchBatteryCapacityMax, None)
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_CHARGE (0\d{2}|100|255) >'), self.__MatchBatteryCharge, None)
            self.AddMatchString(compile(br''.join([br'< REP ([1-8]) BATT_CYCLE (', self.cap_range, br') >'])), self.__MatchBatteryChargingCycles, None)
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_DETECTED (YES|NO) >'), self.__MatchBatteryDetected, None)
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_ERROR (00[0-7]|255) >'), self.__MatchBatteryErrorStatus, None)
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_HEALTH (0\d{2}|100|255) >'), self.__MatchBatteryHealth, None)
            self.AddMatchString(compile(br''.join([br'< REP ([1-8]) BATT_STATE (', self.state_range, br') >'])), self.__MatchBatteryState, None)
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_TEMP_C ([01]\d{2}|2[0-4]\d|25[0-3]|255) >'), self.__MatchBatteryTemperatureCelsius, None)
            self.AddMatchString(compile(br'< REP ([1-8]) BATT_TEMP_F ([01]\d{2}|2[0-4]\d|25[0-3]|255) >'), self.__MatchBatteryTemperatureFahrenheit, None)
            self.AddMatchString(compile(br''.join([br'< REP ([1-8]) BATT_TIME_TO_FULL (', self.bat_full_range, br') >'])), self.__MatchBatteryTimeToFull, None)
            self.AddMatchString(compile(br'< REP DEVICE_ID {([\S ]{31})} >'), self.__MatchDeviceIDStatus, None)
            self.AddMatchString(compile(br'< REP FW_VER {([\S ]{24})} >'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(br'< REP MODEL {([\S ]{32})} >'), self.__MatchModel, None)
            self.AddMatchString(compile(br'< REP STORAGE_MODE (ON|OFF) >'), self.__MatchStorageMode, None)
            self.AddMatchString(compile(br'< REP(?: [1-8])? (\S*) (254|65534|65535) >'), self.__MatchError, None)

    def UpdateBatteryBars(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryBarsCmdString = '< GET 0 BATT_BARS >'
            self.__UpdateHelper('BatteryBars', BatteryBarsCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryBars')
       
    def __MatchBatteryBars(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        result = int(match.group(2).decode())
        value = 0 if result == 255 else result
        self.WriteStatus('BatteryBars', value, qualifier)

    def UpdateBatteryCapacityCurrent(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:           
            BatteryCapacityCurrentCmdString = '< GET 0 BATT_CURRENT_CAPACITY >'
            self.__UpdateHelper('BatteryCapacityCurrent', BatteryCapacityCurrentCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryCapacityCurrent')        

    def __MatchBatteryCapacityCurrent(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('BatteryCapacityCurrent', value, qualifier)

    def UpdateBatteryCapacityCurrentMax(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryCapacityCurrentMaxCmdString = '< GET 0 BATT_CURRENT_CAPACITY_MAX >'
            self.__UpdateHelper('BatteryCapacityCurrentMax', BatteryCapacityCurrentMaxCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryCapacityCurrentMax')        

    def __MatchBatteryCapacityCurrentMax(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('BatteryCapacityCurrentMax', value, qualifier)

    def UpdateBatteryCapacityMax(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryCapacityMaxCmdString = '< GET 0 BATT_CAPACITY_MAX >'
            self.__UpdateHelper('BatteryCapacityMax', BatteryCapacityMaxCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryCapacityMax')

    def __MatchBatteryCapacityMax(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('BatteryCapacityMax', value, qualifier)

    def UpdateBatteryCharge(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:   
            BatteryChargeCmdString = '< GET 0 BATT_CHARGE >'
            self.__UpdateHelper('BatteryCharge', BatteryChargeCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryCharge')
       
    def __MatchBatteryCharge(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        result = int(match.group(2).decode())
        value = 0 if result == 255 else result
        self.WriteStatus('BatteryCharge', value, qualifier)

    def UpdateBatteryChargingCycles(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryChargingCyclesCmdString = '< GET 0 BATT_CYCLE >'
            self.__UpdateHelper('BatteryChargingCycles', BatteryChargingCyclesCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryChargingCycles')
     
    def __MatchBatteryChargingCycles(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('BatteryChargingCycles', value, qualifier)

    def UpdateBatteryDetected(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryDetectedCmdString = '< GET 0 BATT_DETECTED >'
            self.__UpdateHelper('BatteryDetected', BatteryDetectedCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryDetected')        

    def __MatchBatteryDetected(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        value = match.group(2).decode().title()
        self.WriteStatus('BatteryDetected', value, qualifier)

    def UpdateBatteryErrorStatus(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryErrorStatusCmdString = '< GET 0 BATT_ERROR >'
            self.__UpdateHelper('BatteryErrorStatus', BatteryErrorStatusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryErrorStatus')
      
    def __MatchBatteryErrorStatus(self, match, tag):

        ValueStateValues = {
            '000': 'No Active Error',
            '001': 'Unknown Module',
            '002': 'Unrecognized Battery',
            '003': 'Deep Discharge Recovery Failed',
            '004': 'Charge Failed',
            '005': 'Check Battery',
            '006': 'Check Charger',
            '007': 'Communication Failure',
            '255': 'No Battery Present',
        }

        qualifier = {'Bay Number': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BatteryErrorStatus', value, qualifier)

    def UpdateBatteryHealth(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryHealthCmdString = '< GET 0 BATT_HEALTH >'
            self.__UpdateHelper('BatteryHealth', BatteryHealthCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryHealth')    

    def __MatchBatteryHealth(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        result = int(match.group(2).decode())
        value = 0 if result == 255 else result
        self.WriteStatus('BatteryHealth', value, qualifier)

    def UpdateBatteryState(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryStateCmdString = '< GET 0 BATT_STATE >'
            self.__UpdateHelper('BatteryState', BatteryStateCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryState')
      
    def __MatchBatteryState(self, match, tag):

        ValueStateValues = {
            'FULL':             'Full',
            'CALCULATING':      'Calculating',
            'NORMAL':           'Normal',
            'WARM':             'Warm',
            'WARM_FULL':        'Warm Full',
            'HOT':              'Hot',
            'COLD':             'Cold',
            'PRECHARGE':        'Precharge',
            'READY_TO_STORE':   'Ready To Store',
            'DISCHARGE_CALC':   'Discharge Calc',
            'DISCHARGING':      'Discharging',
            'DISCHARGING_WARM': 'Discharging Warm',
            'DISCHARGING_COLD': 'Discharging Cold',
            'ERROR':            'Error',
            'NO_BATT':          'No Battery',
        }

        qualifier = {'Bay Number': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BatteryState', value, qualifier)

    def UpdateBatteryTemperatureCelsius(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryTemperatureCelsiusCmdString = '< GET 0 BATT_TEMP_C >'
            self.__UpdateHelper('BatteryTemperatureCelsius', BatteryTemperatureCelsiusCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryTemperatureCelsius')
      
    def __MatchBatteryTemperatureCelsius(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        result = int(match.group(2).decode()) - 40
        value = -40 if result == 215 else result
        self.WriteStatus('BatteryTemperatureCelsius', value, qualifier)

    def UpdateBatteryTemperatureFahrenheit(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:           
            BatteryTemperatureFahrenheitCmdString = '< GET 0 BATT_TEMP_F >'
            self.__UpdateHelper('BatteryTemperatureFahrenheit', BatteryTemperatureFahrenheitCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryTemperatureFahrenheit')
       
    def __MatchBatteryTemperatureFahrenheit(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        result = int(match.group(2).decode()) - 40
        value = -40 if result == 215 else result
        self.WriteStatus('BatteryTemperatureFahrenheit', value, qualifier)

    def UpdateBatteryTimeToFull(self, value, qualifier):

        bay_number = qualifier['Bay Number']
        if bay_number in self.bay_number_range:            
            BatteryTimeToFullCmdString = '< GET 0 BATT_TIME_TO_FULL >'
            self.__UpdateHelper('BatteryTimeToFull', BatteryTimeToFullCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateBatteryTimeToFull')
     
    def __MatchBatteryTimeToFull(self, match, tag):

        qualifier = {'Bay Number': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('BatteryTimeToFull', value, qualifier)

    def SetDeviceID(self, value, qualifier):

        device_id = self.ReadStatus('DeviceIDStatus', None)
        if device_id and 1 <= len(device_id) <= 8:
            DeviceIDCommandCmdString = ''.join(['< SET DEVICE_ID {', device_id, '} >'])
            self.__SetHelper('DeviceID', DeviceIDCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceIDCommand')

    def UpdateDeviceIDStatus(self, value, qualifier):

        DeviceIDStatusCmdString = '< GET DEVICE_ID >'
        self.__UpdateHelper('DeviceIDStatus', DeviceIDStatusCmdString, value, qualifier)

    def __MatchDeviceIDStatus(self, match, tag):

        value = match.group(1).decode().rstrip()
        self.WriteStatus('DeviceIDStatus', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '< GET FW_VER >'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode().rstrip()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetFlash(self, value, qualifier):

        FlashCmdString = '< SET FLASH ON >'
        self.__SetHelper('Flash', FlashCmdString, value, qualifier)
    def UpdateModel(self, value, qualifier):

        ModelCmdString = '< GET MODEL >'
        self.__UpdateHelper('Model', ModelCmdString, value, qualifier)

    def __MatchModel(self, match, tag):

        value = match.group(1).decode().rstrip()
        self.WriteStatus('Model', value, None)

    def SetStorageMode(self, value, qualifier):

        StorageModeCmdString = '< SET STORAGE_MODE TOGGLE >'
        self.__SetHelper('StorageMode', StorageModeCmdString, value, qualifier)

    def UpdateStorageMode(self, value, qualifier):

        StorageModeCmdString = '< GET STORAGE_MODE >'
        self.__UpdateHelper('StorageMode', StorageModeCmdString, value, qualifier)

    def __MatchStorageMode(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('StorageMode', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
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

        cmd_names_values = {
            'BATT_BARS':                 ('Battery Bars', 0),
            'BATT_CURRENT_CAPACITY':     ('Battery Capacity Current', 0),
            'BATT_CURRENT_CAPACITY_MAX': ('Battery Capacity Current Max', 0),
            'BATT_CAPACITY_MAX':         ('Battery Capacity Max', 0),
            'BATT_CHARGE':               ('Battery Charge', 0),
            'BATT_CYCLE':                ('Battery Charging Cycles', 1),
            'BATT_HEALTH':               ('Battery Health', 0),
            'BATT_TEMP_C':               ('Battery Temperature Celsius', 0),
            'BATT_TEMP_F':               ('Battery Temperature Fahrenheit', 0),
            'BATT_TIME_TO_FULL':         ('Battery Time To Full', 1)
        }

        error_values = {
            '254':   ('An error has occurred, the value is not applicable at this time', ),
            '65534': ('An error has occurred, the value is not applicable at this time', 'Error has occurred'),
            '65535': ('No battery or not applicable', 'Unknown or not applicable'),
        }

        cmd = match.group(1).decode()
        error_num = match.group(2).decode()

        if cmd in cmd_names_values:
            msg = "Error executing command: '{}', message: '{}'".format(
                cmd_names_values[cmd][0],
                error_values[error_num][cmd_names_values[cmd][1]]
            )
        else:
            msg = "Unknown error occurred"

        self.Error([msg])

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
                result = search(regexString, self.__receiveBuffer)
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

