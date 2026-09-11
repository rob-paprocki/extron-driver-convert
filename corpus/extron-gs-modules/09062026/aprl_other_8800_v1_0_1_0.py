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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Alarm': {'Parameters': ['Node Address', 'Type'], 'Status': {}},
            'BuiltinHumidity': {'Parameters': ['Node Address'], 'Status': {}},
            'ControlMode': {'Parameters': ['Node Address'], 'Status': {}},
            'ErrorStatus': {'Parameters': ['Node Address', 'Error Type'], 'Status': {}},
            'FanMode': {'Parameters': ['Node Address'], 'Status': {}},
            'HumidifierType': {'Parameters': ['Node Address'], 'Status': {}},
            'HumidistatHumidityStatus': {'Parameters': ['Node Address'], 'Status': {}},
            'HumidityControlSetpoint': {'Parameters': ['Node Address', 'Type'], 'Status': {}},
            'NodeRemoteTemperatureStatus': {'Parameters': ['Node Address'], 'Status': {}},
            'OutdoorTemperatureStatus': {'Parameters': ['Node Address'], 'Status': {}},
            'PermanentHold': {'Parameters': ['Node Address'], 'Status': {}},
            'RemoteHumidityStatus': {'Parameters': ['Node Address'], 'Status': {}},
            'TemperatureScale': {'Parameters': ['Node Address'], 'Status': {}},
            'ThermostatRoomTemperatureControlStatus': {'Parameters': ['Node Address'], 'Status': {}},
            'ThermostatSetpoint': {'Parameters': ['Node Address', 'Type'], 'Status': {}},
        }

        self.c2enabled = False
        self.c3enabled = False
        self.c5enabled = False
        self.c7enabled = False
        self.c19enabled = False
        self.c14enabled = False
        self.c8enabled = False
        self.ErrorTime = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (FLT|WP|DEH|SYS)ALM=(ON|OFF)\r'), self.__MatchAlarm, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) BIHUM=(--%|\d{1,2}%)\r'), self.__MatchBuiltinHumidity, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (?:MODE|M)=(OFF|HEAT|COOL|EMHT|AUTO|HUMID|DEHUM)\r'), self.__MatchControlMode, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) ERROR=([012]{3}[01]{3})\r'), self.__MatchErrorStatus, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (?:F|FAN)=(ON|AUTO|CIRC|A)\r'), self.__MatchFanMode, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) HUMTYP=(0|1)\r'), self.__MatchHumidifierType, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) HUM=(--%|\d{1,2}%)\r'), self.__MatchHumidistatHumidityStatus, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (SHUM|SDEH)=(\d{1,2})%\r'), self.__MatchHumidityControlSetpoint, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) RTS=(\d{1,2}[CF])\r'), self.__MatchNodeRemoteTemperatureStatus, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (?:OT|R)=(--[FC]|-?\d{2,3}[FC])\r'), self.__MatchOutdoorTemperatureStatus, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) PERMHOLD=(ON|OFF)\r'), self.__MatchPermanentHold, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) OH=(--%|\d{1,2}%)\r'), self.__MatchRemoteHumidityStatus, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) SCALE=(F|C)\r'), self.__MatchTemperatureScale, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (?:T|TEMP)=(\d{1,2}[FC])\r'), self.__MatchThermostatRoomTemperatureControlStatus, None)
            self.AddMatchString(re.compile(b'SN(\d{1,2}) (SC|SH)=(\d{1,2})[FC]\r'), self.__MatchThermostatSetpoint, None)


    def SetAlarm(self, value, qualifier):

        TypeStates = {
            'Air Filter Alarm': 'FLTALM',
            'Humidifier Alarm': 'WPALM',
            'Dehumidifier Alarm': 'DEHALM',
            'HVAC System Alarm': 'SYSALM'
        }

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            AlarmCmdString = 'SN{0} {1}={2}\r'.format(qualifier['Node Address'], TypeStates[qualifier['Type']], ValueStateValues[value])
            self.__SetHelper('Alarm', AlarmCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAlarm')

    def UpdateAlarm(self, value, qualifier):

        TypeStates = {
            'Air Filter Alarm': 'FLTALM',
            'Humidifier Alarm': 'WPALM',
            'Dehumidifier Alarm': 'DEHALM',
            'HVAC System Alarm': 'SYSALM'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            AlarmCmdString = 'SN{0} {1}?\r'.format(qualifier['Node Address'], TypeStates[qualifier['Type']])
            self.__UpdateHelper('Alarm', AlarmCmdString, value, qualifier)
            if not self.c14enabled:
                self.__SetHelper('Alarm', 'SN{0} C14=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c14enabled = True
        else:
            self.Discard('Invalid Command for UpdateAlarm')

    def __MatchAlarm(self, match, tag):

        TypeStates = {
            'FLT': 'Air Filter Alarm',
            'WP': 'Humidifier Alarm',
            'DEH': 'Dehumidifier Alarm',
            'SYS': 'HVAC System Alarm'
        }

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            qualifier['Type'] = TypeStates[match.group(2).decode()]
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('Alarm', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateBuiltinHumidity(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            BuiltinHumidityCmdString = 'SN{0} BIHUM?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('BuiltinHumidity', BuiltinHumidityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBuiltinHumidity')

    def __MatchBuiltinHumidity(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = match.group(2).decode()
            if value == '--%':
                self.WriteStatus('BuiltinHumidity', 'Humidity Sensor Error', qualifier)
            else:
                self.WriteStatus('BuiltinHumidity', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetControlMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'OFF',
            'Heat': 'HEAT',
            'Cool': 'COOL',
            'Emergency Heat Mode (Heat Pump Only)': 'EMHT',
            'Auto': 'AUTO',
            'Humidification': 'HUMID',
            'Dehumidification': 'DEHUM'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            ControlModeCmdString = 'SN{0} MODE={1}\r'.format(qualifier['Node Address'], ValueStateValues[value])
            self.__SetHelper('ControlMode', ControlModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlMode')

    def UpdateControlMode(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            ControlModeCmdString = 'SN{0} MODE?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('ControlMode', ControlModeCmdString, value, qualifier)
            if not self.c7enabled:
                self.__SetHelper('ControlMode', 'SN{0} C7=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c7enabled = True
        else:
            self.Discard('Invalid Command for UpdateControlMode')

    def __MatchControlMode(self, match, tag):

        ValueStateValues = {
            'OFF': 'Off',
            'HEAT': 'Heat',
            'COOL': 'Cool',
            'EMHT': 'Emergency Heat Mode (Heat Pump Only)',
            'AUTO': 'Auto',
            'HUMID': 'Humidification',
            'DEHUM': 'Dehumidification'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('ControlMode', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateErrorStatus(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            ErrorStatusCmdString = 'SN{0} ERROR?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('ErrorStatus', ErrorStatusCmdString, value, qualifier)
            if not self.c19enabled:
                self.__SetHelper('ErrorStatus', 'SN{0} C19=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c19enabled = True
        else:
            self.Discard('Invalid Command for UpdateErrorStatus')

    def __MatchErrorStatus(self, match, tag):

        ErrorTypeStates = {
            0: 'Built-in Temperature Sensor Error',
            1: 'Remote Temperature Sensor 1 Error',
            2: 'Remote Temperature Sensor 2 Error',
            3: 'Built-in Humidity Sensor Error',
            4: 'Local Communication Error',
            5: 'EEPROM Error'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            value = match.group(2).decode()
            for i in range(0, 6):
                qualifier = {}
                qualifier['Node Address'] = match.group(1).decode()
                qualifier['Error Type'] = ErrorTypeStates[i]
                if value[i] == '0':
                    self.WriteStatus('ErrorStatus', 'No Error', qualifier)
                elif value[i] == '1':
                    if i < 3:
                        self.WriteStatus('ErrorStatus', 'Sensor is Open-Circuited', qualifier)
                    elif i == 3:
                        self.WriteStatus('ErrorStatus', 'RH Sensor Error', qualifier)
                    elif i == 4:
                        self.WriteStatus('ErrorStatus', 'Unresponsive Node Error', qualifier)
                    elif i == 5:
                        self.WriteStatus('ErrorStatus', 'EEPROM Error', qualifier)
                elif value[i] == '2':
                    self.WriteStatus('ErrorStatus', 'Sensor is Short-Circuited', qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetFanMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'On': 'ON',
            'Circulate': 'CIRC'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            FanModeCmdString = 'SN{0} F={1}\r'.format(qualifier['Node Address'], ValueStateValues[value])
            self.__SetHelper('FanMode', FanModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFanMode')

    def UpdateFanMode(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            FanModeCmdString = 'SN{0} F?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('FanMode', FanModeCmdString, value, qualifier)
            if not self.c8enabled:
                self.__SetHelper('Fan Mode', 'SN{0} C8=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c8enabled = True
        else:
            self.Discard('Invalid Command for UpdateFanMode')

    def __MatchFanMode(self, match, tag):

        ValueStateValues = {
            'AUTO': 'Auto',
            'A': 'Auto',
            'ON': 'On',
            'CIRC': 'Circulate'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('FanMode', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetHumidifierType(self, value, qualifier):

        ValueStateValues = {
            'Flow-Through Type': '0',
            'Drain-Less Type': '1'
        }
        if 1 <= int(qualifier['Node Address']) <= 64:
            HumidifierTypeCmdString = 'SN{0} HUMTYP={1}\r'.format(qualifier['Node Address'], ValueStateValues[value])
            self.__SetHelper('HumidifierType', HumidifierTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHumidifierType')

    def UpdateHumidifierType(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            HumidifierTypeCmdString = 'SN{0} HUMTYP?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('HumidifierType', HumidifierTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHumidifierType')

    def __MatchHumidifierType(self, match, tag):

        ValueStateValues = {
            '0': 'Flow-Through Type',
            '1': 'Drain-Less Type'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HumidifierType', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateHumidistatHumidityStatus(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            HumidistatHumidityStatusCmdString = 'SN{0} HUM?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('HumidistatHumidityStatus', HumidistatHumidityStatusCmdString, value, qualifier)
            if not self.c2enabled:
                self.__SetHelper('HumidistatHumidityStatus', 'SN{0} C2=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c2enabled = True
        else:
            self.Discard('Invalid Command for UpdateHumidistatHumidityStatus')

    def __MatchHumidistatHumidityStatus(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = match.group(2).decode()
            if value == '--%':
                self.WriteStatus('HumidistatHumidityStatus', 'Humidity Sensor Error', qualifier)
            else:
                self.WriteStatus('HumidistatHumidityStatus', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetHumidityControlSetpoint(self, value, qualifier):

        TypeStates = {
            'Humidification': 'SHUM',
            'Dehumidification': 'SDEH'
        }

        ValueConstraints = {
            'Min': 10,
            'Max': 90
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Node Address']) <= 64:
            HumidityControlSetpointCmdString = 'SN{0} {1}={2}%\r'.format(qualifier['Node Address'], TypeStates[qualifier['Type']], value)
            self.__SetHelper('HumidityControlSetpoint', HumidityControlSetpointCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHumidityControlSetpoint')

    def UpdateHumidityControlSetpoint(self, value, qualifier):

        TypeStates = {
            'Humidification': 'SHUM',
            'Dehumidification': 'SDEH'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            HumidityControlSetpointCmdString = 'SN{0} {1}?\r'.format(qualifier['Node Address'], TypeStates[qualifier['Type']])
            self.__UpdateHelper('HumidityControlSetpoint', HumidityControlSetpointCmdString, value, qualifier)
            if not self.c5enabled:
                self.__SetHelper('HumidityControlSetpoint', 'SN{0} C5=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c5enabled = True
        else:
            self.Discard('Invalid Command for UpdateHumidityControlSetpoint')

    def __MatchHumidityControlSetpoint(self, match, tag):

        TypeStates = {
            'SHUM': 'Humidification',
            'SDEH': 'Dehumidification'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            qualifier['Type'] = TypeStates[match.group(2).decode()]
            value = int(match.group(3).decode())
            self.WriteStatus('HumidityControlSetpoint', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateNodeRemoteTemperatureStatus(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            NodeRemoteTemperatureStatusCmdString = 'SN{0} RTS?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('NodeRemoteTemperatureStatus', NodeRemoteTemperatureStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateNodeRemoteTemperatureStatus')

    def __MatchNodeRemoteTemperatureStatus(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = match.group(2).decode()
            self.WriteStatus('NodeRemoteTemperatureStatus', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetPermanentHold(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            PermanentHoldCmdString = 'SN{0} PERMHOLD={1}\r'.format(qualifier['Node Address'], ValueStateValues[value])
            self.__SetHelper('PermanentHold', PermanentHoldCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPermanentHold')

    def UpdatePermanentHold(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            PermanentHoldCmdString = 'SN{0} PERMHOLD?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('PermanentHold', PermanentHoldCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePermanentHold')

    def __MatchPermanentHold(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('PermanentHold', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateOutdoorTemperatureStatus(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            OutdoorTemperatureStatusCmdString = 'SN{0} OT?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('OutdoorTemperatureStatus', OutdoorTemperatureStatusCmdString, value, qualifier)
            if not self.c3enabled:
                self.__SetHelper('OutdoorTemperatureStatus', 'SN{0} C3=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c3enabled = True
        else:
            self.Discard('Invalid Command for UpdateOutdoorTemperatureStatus')

    def __MatchOutdoorTemperatureStatus(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = match.group(2).decode()
            if value[:-1] == '--':
                self.WriteStatus('OutdoorTemperatureStatus', 'No Outdoor Temperature Sensor', qualifier)
            else:
                self.WriteStatus('OutdoorTemperatureStatus', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateRemoteHumidityStatus(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            RemoteHumidityStatusCmdString = 'SN{0} OH?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('RemoteHumidityStatus', RemoteHumidityStatusCmdString, value, qualifier)
            if not self.c3enabled:
                self.__SetHelper('RemoteHumidityStatus', 'SN{0} C3=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c3enabled = True
        else:
            self.Discard('Invalid Command for UpdateRemoteHumidityStatus')

    def __MatchRemoteHumidityStatus(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = match.group(2).decode()
            if value == '--%':
                self.WriteStatus('RemoteHumidityStatus', 'Sensor Not Connected or Temperature Only', qualifier)
            else:
                self.WriteStatus('RemoteHumidityStatus', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetTemperatureScale(self, value, qualifier):

        ValueStateValues = {
            'Fahrenheit': 'F',
            'Celsius': 'C'
        }
        if 1 <= int(qualifier['Node Address']) <= 64:
            TemperatureScaleCmdString = 'SN{0} SCALE={1}\r'.format(qualifier['Node Address'], ValueStateValues[value])
            self.__SetHelper('TemperatureScale', TemperatureScaleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemperatureScale')

    def UpdateTemperatureScale(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            TemperatureScaleCmdString = 'SN{0} SCALE?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('TemperatureScale', TemperatureScaleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperatureScale')

    def __MatchTemperatureScale(self, match, tag):

        ValueStateValues = {
            'F': 'Fahrenheit',
            'C': 'Celsius'
        }

  
        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('TemperatureScale', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def UpdateThermostatRoomTemperatureControlStatus(self, value, qualifier):

        if 1 <= int(qualifier['Node Address']) <= 64:
            ThermostatRoomTemperatureControlStatusCmdString = 'SN{0} T?\r'.format(qualifier['Node Address'])
            self.__UpdateHelper('ThermostatRoomTemperatureControlStatus', ThermostatRoomTemperatureControlStatusCmdString, value, qualifier)
            if not self.c2enabled:
                self.__SetHelper('ThermostatRoomTemperatureControlStatus', 'SN{0} C2=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c2enabled = True
        else:
            self.Discard('Invalid Command for UpdateThermostatRoomTemperatureControlStatus')

    def __MatchThermostatRoomTemperatureControlStatus(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            value = match.group(2).decode()
            self.WriteStatus('ThermostatRoomTemperatureControlStatus', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

    def SetThermostatSetpoint(self, value, qualifier):

        TemperatureScaleStates = {
            'Fahrenheit': 'F',
            'Celsius': 'C'
        }

        TypeStates = {
            'Heat': 'SH',
            'Cool': 'SC'
        }

        ValueConstraints = {
            'Min': 4,
            'Max': 99
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Node Address']) <= 64:
            ThermostatSetpointCmdString = 'SN{0} {1}={2}\r'.format(qualifier['Node Address'], TypeStates[qualifier['Type']], value)
            self.__SetHelper('ThermostatSetpoint', ThermostatSetpointCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetThermostatSetpoint')


    def UpdateThermostatSetpoint(self, value, qualifier):

        TypeStates = {
            'Heat': 'SH',
            'Cool': 'SC'
        }

        if 1 <= int(qualifier['Node Address']) <= 64:
            ThermostatSetpointCmdString = 'SN{0} {1}?\r'.format(qualifier['Node Address'], TypeStates[qualifier['Type']])
            self.__UpdateHelper('ThermostatSetpoint', ThermostatSetpointCmdString, value, qualifier)
            if not self.c5enabled:
                self.__SetHelper('ThermostatSetpoint', 'SN{0} C5=ON\r'.format(qualifier['Node Address']), value, qualifier)
                self.c5enabled = True
        else:
            self.Discard('Invalid Command for UpdateThermostatSetpoint')

    def __MatchThermostatSetpoint(self, match, tag):

        TypeStates = {
            'SH': 'Heat',
            'SC': 'Cool'
        }

        if 1 <= int(match.group(1).decode()) <= 64:
            qualifier = {}
            qualifier['Node Address'] = match.group(1).decode()
            qualifier['Type'] = TypeStates[match.group(2).decode()]
            value = int(match.group(3).decode())
            self.WriteStatus('ThermostatSetpoint', value, qualifier)
        else:
            self.Error(['Invalid/Unexpected Response'])

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

        self.c2enabled = False
        self.c3enabled = False
        self.c5enabled = False
        self.c7enabled = False
        self.c19enabled = False
        self.c14enabled = False
        self.c8enabled = False
        self.ErrorTime = 0

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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
