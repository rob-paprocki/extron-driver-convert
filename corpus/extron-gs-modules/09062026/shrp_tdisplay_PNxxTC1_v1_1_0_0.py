from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.deviceUsername = None
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'InitCommand': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
         self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
         self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide':         'WIDE0001\r',
            'Dot by Dot':   'WIDE0003\r',
            'Normal':       'WIDE0006\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Wide',
            '3': 'Dot by Dot',
            '6': 'Normal'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'No detectable error has occurred',
            '1': 'Standby mode by Power Button',
            '2': 'Main power off by the main power switch',
            '3': 'Standby mode by RS-232C or LAN',
            '4': 'Input signal waiting mode by No Signal',
            '6': 'Standby mode by abnormal temperature',
            '20': 'Standby mode by OFF IF NO OPERATION setting'
        }

        DeviceStatusCmdString = 'STCA????\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Remote Control':   'ALTG0000\r',
            'Monitor Buttons':  'ALTG0001\r',
            'All On':           'ALTG0002\r',
            'All Off':          'ALTG0003\r'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Remote Control',
            '1': 'Monitor Buttons',
            '2': 'All On',
            '3': 'All Off'
        }

        ExecutiveModeCmdString = 'ALTG????\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'D-SUB':        'INPS0002\r',
            'HDMI 1':       'INPS0010\r',
            'HDMI 2':       'INPS0013\r',
            'DisplayPort':  'INPS0014\r',
            'Option':       'INPS0021\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetInitCommand(self, value, qualifier):
        self.Debug = True
        self.Send(b'CTLS0000\r')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '2': 'D-SUB',
            '10': 'HDMI 1',
            '13': 'HDMI 2',
            '14': 'DisplayPort',
            '21': 'Option'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE0001\r',
            'Off': 'MUTE0000\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'PC':               'BMOD0000\r',
            'High Illuminance': 'BMOD0004\r',
            'AV':               'BMOD0009\r',
            'User':             'BMOD0010\r'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'PC',
            '4': 'High Illuminance',
            '9': 'AV',
            '10': 'User'
        }

        PictureModeCmdString = 'BMOD????\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'D-SUB':        'MWIP0002\r',
            'HDMI 1':       'MWIP0010\r',
            'HDMI 2':       'MWIP0013\r',
            'DisplayPort':  'MWIP0014\r',
            'Option':       'MWIP0021\r'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '2': 'D-SUB',
            '10': 'HDMI 1',
            '13': 'HDMI 2',
            '14': 'DisplayPort',
            '21': 'Option'
        }

        PIPInputCmdString = 'MWIP????\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP': 'MWIN0001\r',
            'PbyP': 'MWIN0002\r',
            'Off': 'MWIN0000\r'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'PIP',
            '2': 'PbyP',
            '0': 'Off'
        }

        PIPModeCmdString = 'MWIN????\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Right':  'MWPS0000\r',
            'Upper Left':   'MWPS0001\r',
            'Lower Right':  'MWPS0002\r',
            'Lower Left':   'MWPS0003\r'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            '0': 'Upper Right',
            '1': 'Upper Left',
            '2': 'Lower Right',
            '3': 'Lower Left'
        }

        PIPPositionCmdString = 'MWPS????\r'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small':    'MPSZ0000\r',
            'Medium':   'MPSZ0001\r',
            'Large':    'MPSZ0002\r'
        }

        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large'
        }

        PIPSizeCmdString = 'MPSZ????\r'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'POWR0001\r',
            'Off':  'POWR0000\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            VolumeCmdString = 'VOLM{0:4d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and 'ERR' in response:
            self.Error(['{0} Communication error or incorrect command'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'CTLS0001\r')
        return result

