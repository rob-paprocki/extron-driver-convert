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
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Keypad': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9a-f]{2}) OK(01|02|04|06|07|09|10|0B)x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9a-f]{2}) OK0([01])x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm ([0-9a-f]{2}) OK0([01])x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9a-f]{2}) OK(00|01|10|11|20|40|60|90|91|92)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l ([0-9a-f]{2}) OK0([01])x', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a ([0-9a-f]{2}) OK0([01])x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9a-f]{2}) OK(01|00|10)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9a-f]{2}) OK([0-9A-F]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'([abcdeflm]) [0-9A-F]{2} NG(.*)x', re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '14:9': '07',
            '16:9': '02',
            'Just Scan': '09',
            'Original': '06',
            'Full Wide': '0B',
            'Cinema Zoom 1': '10',
            'Zoom': '04'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            AspectRatioCmdString = 'kc {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            AspectRatioCmdString = 'kc {0} FF\r'.format(deviceID)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01': '4:3',
            '07': '14:9',
            '02': '16:9',
            '09': 'Just Scan',
            '06': 'Original',
            '0B': 'Full Wide',
            '10': 'Cinema Zoom 1',
            '04': 'Zoom'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Device ID': str(deviceID)})

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            AudioMuteCmdString = 'ke {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            AudioMuteCmdString = 'ke {0} FF\r'.format(deviceID)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, {'Device ID': str(deviceID)})

    def SetAutoImage(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            AutoImageCmdString = 'ju {0} 01\r'.format(deviceID)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            ExecutiveModeCmdString = 'km {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            ExecutiveModeCmdString = 'km {0} FF\r'.format(deviceID)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, {'Device ID': str(deviceID)})

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Cable DTV': '01',
            'Cable TV': '11',
            'AV': '20',
            'Component': '40',
            'RGB': '60',
            'HDMI 1': '90',
            'HDMI 2': '91',
            'HDMI 3': '92',
            'DTV': '00',
            'TV': '10'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            InputCmdString = 'xb {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            InputCmdString = 'xb {0} FF\r'.format(deviceID)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '01': 'Cable DTV',
            '11': 'Cable TV',
            '20': 'AV',
            '40': 'Component',
            '60': 'RGB',
            '90': 'HDMI 1',
            '91': 'HDMI 2',
            '92': 'HDMI 3',
            '00': 'DTV',
            '10': 'TV'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, {'Device ID': str(deviceID)})

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            KeypadCmdString = 'mc {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '43',
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            MenuNavigationCmdString = 'mc {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            OnScreenDisplayCmdString = 'kl {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            OnScreenDisplayCmdString = 'kl {0} FF\r'.format(deviceID)
            self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOnScreenDisplay')

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OnScreenDisplay', value, {'Device ID': str(deviceID)})

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            PowerCmdString = 'ka {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            PowerCmdString = 'ka {0} FF\r'.format(deviceID)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, {'Device ID': str(deviceID)})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On (Without OSD)': '01',
            'Off': '00',
            'On (With OSD)': '10'
        }

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            VideoMuteCmdString = 'kd {0} {1}\r'.format(deviceID, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            VideoMuteCmdString = 'kd {0} FF\r'.format(deviceID)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '01': 'On (Without OSD)',
            '00': 'Off',
            '10': 'On (With OSD)'
        }

        deviceID = int(match.group(1).decode().upper(), 16)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, {'Device ID': str(deviceID)})

    def SetVolume(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if 0 <= value <= 100 and deviceID:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(deviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        deviceID = ''
        id_ = qualifier['Device ID']
        if id_ == 'Broadcast':
            deviceID = '00'
        elif 1 <= int(id_) <= 99:
            deviceID = '{0:02X}'.format(int(id_))

        if deviceID:
            VolumeCmdString = 'kf {0} FF\r'.format(deviceID)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        deviceID = int(match.group(1).decode().upper(), 16)
        value = int(match.group(2).decode(), 16)
        self.WriteStatus('Volume', value, {'Device ID': str(deviceID)})

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        if 'OK' in response:
            return response
        elif 'NG' in response:
            err = 'Error in command: {0}'.format(sourceCmdName)
            self.Error([err])
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

        ERROR = {
            'a' : 'Power',
            'b' : 'Input',
            'c' : 'Aspect Ratio',
            'd' : 'Screen Mute',
            'e' : 'Volume Mute',
            'f' : 'Volume',
            'l' : 'On Screen Display',
            'm' : 'Executive Mode'
        }

        errorStr = 'Command: {0}. Error: {1}'.format(ERROR[match.group(1).decode()], match.group(2).decode())
        self.Error([errorStr])

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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