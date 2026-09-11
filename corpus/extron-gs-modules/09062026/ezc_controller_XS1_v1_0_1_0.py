import urllib.error
import urllib.request
from json import loads


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.ipAddress = ipAddress
        self.port = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.RootURL = 'http://{0}:{1}/'.format(self.ipAddress, self.port)

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
            'Blinds': {'Parameters': ['Actuator Number'], 'Status': {}},
            'Dimmer': {'Parameters': ['Actuator Number'], 'Status': {}},
            'PresetActuators': {'Parameters': ['Actuator Number'], 'Status': {}},
            'Switch': {'Parameters': ['Actuator Number'], 'Status': {}},
            'Temperature': {'Parameters': ['Sensor Number'], 'Status': {}},
            }

        ##HTTP opener
        self.opener = urllib.request.build_opener()
        urllib.request.install_opener(self.opener)

        ##Basic Password authentication
        self.authentication = None

    def SetBlinds(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        Actuator = qualifier['Actuator Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and \
                1 <= int(Actuator) <= 64:
            BlindsCmdString = 'cmd=set_state_actuator&number={0}&value={1}'.format(Actuator, value)
            self.__SetHelper('Blinds', BlindsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBlinds')

    def UpdateBlinds(self, value, qualifier):

        Actuator = qualifier['Actuator Number']
        BlindsCmdString = 'cmd=get_state_actuator&number={0}'.format(Actuator)
        res = self.__UpdateHelper('Blinds', BlindsCmdString, value, qualifier)
        if res:
            temp = res.split('(')[1]
            temp = temp.split(')')[0]
            while (temp.count('.}') > 0) or (temp.count('."') > 0):
                temp = temp.replace('.}', '}')
                temp = temp.replace('."', '"')
            jsonRes = loads(temp)
            if jsonRes['actuator']['type'] == 'blind':
                value = int(jsonRes['actuator']['value'])
                qualifier = {'Actuator Number': str(jsonRes['actuator']['number'])}
                self.WriteStatus('Blinds', value, qualifier)
            else:
                print('Invalid actuator type for UpdateBlinds')
        else:
            print('Invalid command for UpdateBlinds')

    def SetDimmer(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }
        Actuator = qualifier['Actuator Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and \
                1 <= int(Actuator) <= 64:
            DimmerCmdString = 'cmd=set_state_actuator&number={0}&value={1}'.format(Actuator, value)
            self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDimmer')

    def UpdateDimmer(self, value, qualifier):

        Actuator = qualifier['Actuator Number']
        if 1 <= int(Actuator) <= 64:
            DimmerCmdString = 'cmd=get_state_actuator&number={0}'.format(Actuator)
            res = self.__UpdateHelper('Dimmer', DimmerCmdString, value, qualifier)
            if res:
                temp = res.split('(')[1]
                temp = temp.split(')')[0]
                while (temp.count('.}') > 0) or (temp.count('."') > 0):
                    temp = temp.replace('.}', '}')
                    temp = temp.replace('."', '"')
                jsonRes = loads(temp)
                if jsonRes['actuator']['type'] == 'dimmer':
                    value = int(jsonRes['actuator']['value'])
                    qualifier = {'Actuator Number': str(jsonRes['actuator']['number'])}
                    self.WriteStatus('Dimmer', value, qualifier)
                else:
                    print('Invalid actuator type for UpdateDimmer')
        else:
            print('Invalid Command for UpdateDimmer')

    def SetPresetActuators(self, value, qualifier):

        Actuator = qualifier['Actuator Number']
        if 1 <= int(Actuator) <= 64 and 1 <= int(value) <= 4:
            PresetActuatorsCmdString = 'cmd=set_state_actuator&number={0}&function={1}'.format(Actuator, value)
            self.__SetHelper('PresetActuators', PresetActuatorsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetActuators')

    def SetSwitch(self, value, qualifier):

        Actuator = qualifier['Actuator Number']
        if 1 <= int(Actuator) <= 64:
            switchCmdString = 'cmd=set_state_actuator&number={0}&function=1'.format(Actuator)
            self.__SetHelper('Switch', switchCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSwitch')

    def UpdateSwitch(self, value, qualifier):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off',
            0: 'Off',
            100: 'On'
        }

        Actuator = qualifier['Actuator Number']
        if 1 <= int(Actuator) <= 64:
            switchCmdString = 'cmd=get_state_actuator&number={0}'.format(Actuator)
            res = self.__UpdateHelper('Switch', switchCmdString, value, qualifier)
            if res:
                temp = res.split('(')[1]
                temp = temp.split(')')[0]
                while (temp.count('.}') > 0) or (temp.count('."') > 0):
                    temp = temp.replace('.}', '}')
                    temp = temp.replace('."', '"')
                jsonRes = loads(temp)
                if jsonRes['actuator']['type'] == 'switch':
                    valueType = jsonRes['actuator']['value']
                    qualifier = {'Actuator Number': str(jsonRes['actuator']['number'])}
                    if type(valueType) == float or type(valueType) == int:
                        value = ValueStateValues[valueType]
                    else:
                        value = ValueStateValues[valueType.upper()]
                    self.WriteStatus('Switch', value, qualifier)
                else:
                    print('Invalid actuator type for UpdateSwitch') 
        else:
            print('Invalid Command for UpdateSwitch')

    def UpdateTemperature(self, value, qualifier):

        Sensor = qualifier['Sensor Number']
        if 1 <= int(Sensor) <= 64:
            TemperatureCmdString = 'cmd=get_state_sensor&number={0}'.format(Sensor)
            res = self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
            if res:
                temp = res.split('(')[1]
                temp = temp.split(')')[0]
                while (temp.count('.}') > 0) or (temp.count('."') > 0):
                    temp = temp.replace('.}', '}')
                    temp = temp.replace('."', '"')
                jsonRes = loads(temp)
                if jsonRes['sensor']['type'] == 'temperature':
                    value = float(jsonRes['sensor']['value'])
                    qualifier = {'Sensor Number': str(jsonRes['sensor']['number'])}
                    self.WriteStatus('Temperature', value, qualifier)
                else:
                    print('Invalid actuator type for UpdateTemperature')
        else:
            print('Invalid Command for UpdateTemperature')

    def __CheckResponseForErrors(self, sourceCmdName, res):
        ErrorMessages = {
                    '01': 'invalid command',
                    '02': 'type cmd missing',
                    '03': 'number / name not found',
                    '04': 'duplicate name',
                    '05': 'invalid system',
                    '06': 'invalid function',
                    '07': 'invalid date / time',
                    '08': 'object not found',
                    '09': 'type not virtual',
                    '10': 'syntax error',
                    '11': 'error time range',
                    '12': 'protocol version mismatch'
                 }
       
        if res:
            restemp = res.read().decode()
            if 'error' in restemp:
                check = loads(restemp.split('(')[1][:-1])
                print(ErrorMessages[check['error']])
                res = ''
            else:
                res = restemp
        else:
            res = ''

        return res

    def __SetHelper(self, command, data, value, qualifier):
        self.Debug = True

        url = 'control?callback=cname&{}'.format(data)
        req = urllib.request.Request('{0}{1}'.format(self.RootURL, url), method='GET')
        try:
            res = self.opener.open(req, timeout=1)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = b''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, data, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter += 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        url = 'control?callback=cname&{0}'.format(data)
        req = urllib.request.Request('{0}{1}'.format(self.RootURL, url), method='GET')
        try:
            res = self.opener.open(req, timeout=1)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = b''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

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


class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
