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
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ControlLock': {'Parameters': ['Device ID', 'Type'], 'Status': {}},
            'DisplaySequence': {'Parameters': ['Device ID'], 'Status': {}},
            'HorizontalSetCount': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'MasterPower': {'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'VerticalSetCount': {'Parameters': ['Device ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Horizontal', 'Vertical', 'Value'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0F([01][0-9]{2})PWS#(-ON|OFF)#\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x0F([01][0-9]{2})(AUT|RML|KPL|SDS|HSC|MIN|RMT|PW[RS]|VSC|ZOM)ERROR\x0D'), self.__MatchError, None)

    def SetAutoImage(self, value, qualifier):

        if 1 <= int(qualifier['Device ID']) <= 100:
            AutoImageCmdString = '\x0F{:03d}AUTW-PC0\x0D'.format(int(qualifier['Device ID'])).encode()
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetControlLock(self, value, qualifier):

        TypeStates = {
            'Remote': 'RML',
            'Keypad': 'KPL'
        }

        ValueStateValues = {
            'On': '-ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Device ID']) <= 100 and qualifier['Type'] in TypeStates:
            ControlLockCmdString = '\x0F{0:03d}{1}W{2}0\x0D'.format(int(qualifier['Device ID']), TypeStates[qualifier['Type']], ValueStateValues[value]).encode()
            self.__SetHelper('ControlLock', ControlLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlLock')

    def SetDisplaySequence(self, value, qualifier):

        if 1 <= int(value) <= 100 and 1 <= int(qualifier['Device ID']) <= 100:
            DisplaySequenceCmdString = '\x0F{0:03d}SDSW{1:03d}0\x0D'.format(int(qualifier['Device ID']), int(value)).encode()
            self.__SetHelper('DisplaySequence', DisplaySequenceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplaySequence')

    def SetHorizontalSetCount(self, value, qualifier):

        if 1 <= int(value) <= 10 and 1 <= int(qualifier['Device ID']) <= 10:
            HorizontalSetCountCmdString = '\x0F{0:03d}HSCW{1:03d}0\x0D'.format(int(qualifier['Device ID']), int(value)).encode()
            self.__SetHelper('HorizontalSetCount', HorizontalSetCountCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalSetCount')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVI': 'DVI',
            'HDMI': 'HDM',
            'VGA': '-PC',
            'DisplayPort': '-DP'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Device ID']) <= 100:
            InputCmdString = '\x0F{0:03d}MINW{1}0\x0D'.format(int(qualifier['Device ID']), ValueStateValues[value]).encode()
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'MEN',
            'Left': 'LEF',
            'Right': 'RIG',
            'Enter': 'ENT',
            'Up': '-UP',
            'Down': 'DOW',
            'Exit': 'EXI'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Device ID']) <= 100:
            MenuNavigationCmdString = '\x0F{0:03d}RMTW{1}0\x0D'.format(int(qualifier['Device ID']), ValueStateValues[value]).encode()
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '-ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Device ID']) <= 100:
            PowerCmdString = '\x0F{0:03d}PWRW{1}0\x0D'.format(int(qualifier['Device ID']), ValueStateValues[value]).encode()
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        if 1 <= int(qualifier['Device ID']) <= 100:
            PowerCmdString = '\x0F{:03d}PWSR0000\x0D'.format(int(qualifier['Device ID'])).encode()
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '-ON': 'On',
            'OFF': 'Off'
        }

        deviceID = int(match.group(1))

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, {'Device ID': str(deviceID)})

    def SetVerticalSetCount(self, value, qualifier):

        if 1 <= int(value) <= 10 and 1 <= int(qualifier['Device ID']) <= 100:
            VerticalSetCountCmdString = '\x0F{0:03d}VSCW{1:03d}0\x0D'.format(int(qualifier['Device ID']), int(value)).encode()
            self.__SetHelper('VerticalSetCount', VerticalSetCountCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalSetCount')

    def SetZoom(self, value, qualifier):

        ValueStates = {
            'In': 'I',
            'Out': 'O'
        }

        if value in ValueStates and 1 <= int(qualifier['Horizontal']) <= 9 and 1 <= int(qualifier['Vertical']) <= 9:
            ZoomCmdString = '\x0F000ZOMW{0}{1}{2}0\x0D'.format(qualifier['Horizontal'], qualifier['Vertical'], ValueStates[value]).encode()
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

        DEVICE_ERROR_CODES = {
            'AUT' : 'Auto Image Command',
            'RML' : 'Remote Control Lock Command',
            'KPL' : 'Keypad Control Lock Command',
            'SDS' : 'Display Sequence Command',
            'HSC' : 'Horizontal Set Command',
            'MIN' : 'Input Command',
            'RMT' : 'Menu Navigation Command',
            'PWR' : 'Power Command',
            'PWS' : 'Power Status',
            'VSC' : 'Vertical Set Command',
            'ZOM' : 'Zoom Command'
        }

        self.Error(['An error occured: Device ID {0}, {1}'.format(str(int(match.group(1))), DEVICE_ERROR_CODES[match.group(2).decode()])])

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
        
        # check incoming data if it matched any expected data from device module
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