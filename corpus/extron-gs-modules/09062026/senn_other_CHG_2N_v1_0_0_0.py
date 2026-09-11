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
            'ActiveBays': {'Parameters':['Bay'], 'Status': {}},
            'BatteryBars': {'Parameters':['Bay'], 'Status': {}},
            'BatteryTimetoFull': {'Parameters':['Bay'], 'Status': {}},
            'ChargingStatus': {'Parameters':['Bay'], 'Status': {}},
            'DeviceIdentity': { 'Status': {}},
            'DeviceLocation': { 'Status': {}},
            'DeviceName': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"bays":{"active":\[(true|false),(true|false)]}}\x00'), self.__MatchActiveBays, None)
            self.AddMatchString(re.compile(b'{"bays":{"bat_bars":\[([0-6]),([0-6])]}}\x00'), self.__MatchBatteryBars, None)
            self.AddMatchString(re.compile(b'{"bays":{"bat_timetofull":\[(\d+),(\d+)]}}\x00'), self.__MatchBatteryTimetoFull, None)
            self.AddMatchString(re.compile(b'{"bays":{"charging":\[(true|false),(true|false)]}}\x00'), self.__MatchChargingStatus, None)
            self.AddMatchString(re.compile(b'{"device":{"identity":{"product":"([\s\S]+?)"}}}\x00'), self.__MatchDeviceIdentity, None)
            self.AddMatchString(re.compile(b'{"device":{"location":"([\s\S]+?)"}}\x00'), self.__MatchDeviceLocation, None)
            self.AddMatchString(re.compile(b'{"device":{"name":"([\s\S]+?)"}}\x00'), self.__MatchDeviceName, None)
            self.AddMatchString(re.compile(b'{"device":{"identity":{"version":"(\d+\.\d+\.\d+)"}}}\x00'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'{"osc":{"error":.*?\[(\d{3})].*?}}\x00'), self.__MatchError, None)

    def UpdateActiveBays(self, value, qualifier):

        if qualifier['Bay'] in ['1', '2']:
            ActiveBaysCmdString = '{"bays":{"active":null}}\r'
            self.__UpdateHelper('ActiveBays', ActiveBaysCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateActiveBays')

    def __MatchActiveBays(self, match, tag):

        ValueStateValues = {
            'true':  'Active',
            'false': 'Not Active',
            }

        self.WriteStatus('ActiveBays', ValueStateValues[match.group(1).decode()], {'Bay' : '1'})
        self.WriteStatus('ActiveBays', ValueStateValues[match.group(2).decode()], {'Bay' : '2'})

    def UpdateBatteryBars(self, value, qualifier):

        if qualifier['Bay'] in ['1', '2']:
            BatteryBarsCmdString = '{"bays":{"bat_bars":null}}\r'
            self.__UpdateHelper('BatteryBars', BatteryBarsCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateBatteryBars')
            
    def __MatchBatteryBars(self, match, tag):

        self.WriteStatus('BatteryBars', int(match.group(1).decode()), {'Bay' : '1'})
        self.WriteStatus('BatteryBars', int(match.group(2).decode()), {'Bay' : '2'})

    def UpdateBatteryTimetoFull(self, value, qualifier):
            
        if qualifier['Bay'] in ['1', '2']:
            BatteryTimetoFullCmdString = '{"bays":{"bat_timetofull":null}}\r'
            self.__UpdateHelper('BatteryTimetoFull', BatteryTimetoFullCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryTimetoFull')

    def __MatchBatteryTimetoFull(self, match, tag):

        self.WriteStatus('BatteryTimetoFull', int(match.group(1).decode()), {'Bay' : '1'})
        self.WriteStatus('BatteryTimetoFull', int(match.group(2).decode()), {'Bay' : '2'})

    def UpdateChargingStatus(self, value, qualifier):

        if qualifier['Bay'] in ['1', '2']:
            ChargingStatusCmdString = '{"bays":{"charging":null}}\r'
            self.__UpdateHelper('ChargingStatus', ChargingStatusCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command for UpdateChargingStatus')

    def __MatchChargingStatus(self, match, tag):

        ValueStateValues = {
            'true':  'Charging', 
            'false': 'Not Charging'
        }

        self.WriteStatus('ChargingStatus', ValueStateValues[match.group(1).decode()], {'Bay' : '1'})
        self.WriteStatus('ChargingStatus', ValueStateValues[match.group(2).decode()], {'Bay' : '2'})

    def UpdateDeviceIdentity(self, value, qualifier):

        DeviceIdentityCmdString = '{"device":{"identity":{"product":null}}}\r'
        self.__UpdateHelper('DeviceIdentity', DeviceIdentityCmdString, value, qualifier)

    def __MatchDeviceIdentity(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceIdentity', value, None)

    def UpdateDeviceLocation(self, value, qualifier):

        DeviceLocationCmdString = '{"device":{"location":null}}\r'
        self.__UpdateHelper('DeviceLocation', DeviceLocationCmdString, value, qualifier)

    def __MatchDeviceLocation(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceLocation', value, None)

    def UpdateDeviceName(self, value, qualifier):

        DeviceNameCmdString = '{"device":{"name":null}}\r'
        self.__UpdateHelper('DeviceName', DeviceNameCmdString, value, qualifier)

    def __MatchDeviceName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceName', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '{"device":{"identity":{"version":null}}}\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):
        
        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

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

        ErrorStates = {
            '310': 'Error 310: Subscription Terminates',
            '400': 'Error 400: Bad Request',
            '401': 'Error 401: Unauthorized',
            '403': 'Error 403: Forbidden',
            '404': 'Error 404: Not Found',
            '406': 'Error 406: Not Acceptable',
            '408': 'Error 408: Request Timeout',
            '409': 'Error 409: Conflict',
            '410': 'Error 410: Gone',
            '413': 'Error 413: Request Entity Too Large',
            '414': 'Error 414: Request Too Complex',
            '422': 'Error 422: Unprocessable Entity',
            '423': 'Error 423: Locked',
            '424': 'Error 424: Failed Dependency',
            '450': 'Error 450: Answer Too Long',
            '454': 'Error 454: Parameter Address Not Found',
            '500': 'Error 500: Internal Server Error',
            '501': 'Error 501: Not Implemented',
            '503': 'Error 503: Service Unavailable'
        }
        value = match.group(1).decode()
        if value in ErrorStates:
            self.Error([ErrorStates[value]])

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
class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])