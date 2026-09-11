from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
import time

class DeviceEthernetClass:
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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'ExecutiveModeTarget': { 'Status': {}},
            'Input': { 'Status': {}},
            'InputSignal': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'Power': { 'Status': {}},
            'ResolutionLongestDirection': { 'Status': {}},
            'ResolutionShortestDirection': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.startPolling = False

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'OK'), self.__MatchSuccess, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername( None, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword( None, None)

    def __MatchSuccess(self, match, tag):
        self.startPolling = True

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide':       '1',
            'Normal':     '2',
            'Dot by Dot': '3',
            'Zoom':       '4',
        }

        AspectRatioCmdString = 'WIDE{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'Dot by Dot',
            '4': 'Zoom',
        }

        AspectRatioCmdString = 'WIDE????\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        AudioMuteCmdString = 'MUTE{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        AudioMuteCmdString = 'MUTE????\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ASNC   1\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':  '0',
            'On 1': '1',
            'On 2': '2',
        }

        ExecutiveModeCmdString = 'ALCK{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On 1',
            '2': 'On 2',
        }

        ExecutiveModeCmdString = 'ALCK????\r\n'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetExecutiveModeTarget(self, value, qualifier):

        ValueStateValues = {
            'Remote Control':  '0',
            'Monitor Buttons': '1',
            'Both':            '2',
        }

        ExecutiveModeTargetCmdString = 'ALTG{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveModeTarget', ExecutiveModeTargetCmdString, value, qualifier)

    def UpdateExecutiveModeTarget(self, value, qualifier):

        ValueStateValues = {
            '0': 'Remote Control',
            '1': 'Monitor Buttons',
            '2': 'Both',
        }

        ExecutiveModeTargetCmdString = 'ALTG????\r\n'
        res = self.__UpdateHelper('ExecutiveModeTarget', ExecutiveModeTargetCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('ExecutiveModeTarget', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode Target: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Toggle':      '0',
            'D-SUB':       '2',
            'HDMI 1':      '10',
            'HDMI 2':      '13',
            'DisplayPort': '14',
            'Option':      '21',
            'Application': '24',
        }

        InputCmdString = 'INPS{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '2':  'D-SUB',
            '10': 'HDMI 1',
            '13': 'HDMI 2',
            '14': 'DisplayPort',
            '21': 'Option',
            '24': 'Application',
        }

        InputCmdString = 'INPS????\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetInputSignal(self, value, qualifier):

        ValueStateValues = {
            '768) 1360 x 768':   '1',
            '768) 1280 x 768':   '2',
            '768) 1024 x 768':   '3',
            '480) 848 x 480':    '5',
            '480) 640 x 480':    '6',
            '1050) 1680 x 1050': '7',
            '1050) 1400 x 1050': '8',
            '768) Auto':         '9',
            '480) Auto':         '10',
        }

        InputSignalCmdString = 'PXSL{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('InputSignal', InputSignalCmdString, value, qualifier)

    def UpdateInputSignal(self, value, qualifier):

        ValueStateValues = {
            '1':  '768) 1360 x 768',
            '2':  '768) 1280 x 768',
            '3':  '768) 1024 x 768',
            '5':  '480) 848 x 480',
            '6':  '480) 640 x 480',
            '7':  '1050) 1680 x 1050',
            '8':  '1050) 1400 x 1050',
            '9':  '768) Auto',
            '10': '480) Auto',
        }

        InputSignalCmdString = 'PXSL????\r\n'
        res = self.__UpdateHelper('InputSignal', InputSignalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('InputSignal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input Signal: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'D-SUB':       '2',
            'HDMI 1':      '10',
            'HDMI 2':      '13',
            'DisplayPort': '14',
            'Option':      '21',
            'Application': '24',
        }

        PIPInputCmdString = 'MWIP{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '2':  'D-SUB',
            '10': 'HDMI 1',
            '13': 'HDMI 2',
            '14': 'DisplayPort',
            '21': 'Option',
            '24': 'Application',
        }

        PIPInputCmdString = 'MWIP????\r\n'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off':                  '0',
            'PIP':                  '1',
            'Picture by Picture 1': '2',
            'Picture by Picture 2': '3',
        }

        PIPModeCmdString = 'MWIN{0:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'Picture by Picture 1',
            '3': 'Picture by Picture 2',
        }

        PIPModeCmdString = 'MWIN????\r\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 64,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PIPSizeCmdString = 'MPSZ{:>4}\r\n'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 64,
        }

        PIPSizeCmdString = 'MPSZ????\r\n'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[:-2])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('PIPSize', value, qualifier)
                else:
                    self.Error(['PIP Size: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }

        PowerCmdString = 'POWR{:>4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode',
        }

        PowerCmdString = 'POWR????\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetResolutionLongestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1920,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ResolutionLongestDirectionCmdString = 'HRES{:>4}\r\n'.format(value)
            self.__SetHelper('ResolutionLongestDirection', ResolutionLongestDirectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResolutionLongestDirection')

    def UpdateResolutionLongestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1920,
        }

        ResolutionLongestDirectionCmdString = 'HRES????\r\n'
        res = self.__UpdateHelper('ResolutionLongestDirection', ResolutionLongestDirectionCmdString, value, qualifier)
        if res:
            try:
                value = int(res[:-2])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('ResolutionLongestDirection', value, qualifier)
                else:
                    self.Error(['Resolution Longest Direction: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Resolution Longest Direction: Invalid/unexpected response'])

    def SetResolutionShortestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1200,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ResolutionShortestDirectionCmdString = 'VRES{:>4}\r\n'.format(value)
            self.__SetHelper('ResolutionShortestDirection', ResolutionShortestDirectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResolutionShortestDirection')

    def UpdateResolutionShortestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1200,
        }

        ResolutionShortestDirectionCmdString = 'VRES????\r\n'
        res = self.__UpdateHelper('ResolutionShortestDirection', ResolutionShortestDirectionCmdString, value, qualifier)
        if res:
            try:
                value = int(res[:-2])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('ResolutionShortestDirection', value, qualifier)
                else:
                    self.Error(['Resolution Shortest Direction: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Resolution Shortest Direction: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{:>4}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31,
        }

        VolumeCmdString = 'VOLM????\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[:-2])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    self.Error(['Volume: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if isinstance(response, bytes):
                response = response.decode()

            if 'ERR' in response:
                error_string = '{0}: Communication error or incorrect command.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
            elif 'OK' in response:
                self.startPolling = True
            elif 'WAIT' in response:
                error_string = '{0}: Waiting for response.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
            elif 'LOCKED' in response:
                error_string = '{}: Control via RS-232 is locked.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
            elif 'UNSELECTED' in response:
                error_string = '{}: Monitor Control Select is set to LAN or Application.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            if self.startPolling:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)
            else:
                self.Discard('Invalid Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.startPolling:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.startPolling = False
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

class DeviceSerialClass:
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
            'AspectRatio': {'Parameters':['Device ID'], 'Status': {}},
            'AssignID': { 'Status': {}},
            'AudioMute': {'Parameters':['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters':['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters':['Device ID'], 'Status': {}},
            'ExecutiveModeTarget': {'Parameters':['Device ID'], 'Status': {}},
            'IDCheck': { 'Status': {}},
            'Input': {'Parameters':['Device ID'], 'Status': {}},
            'InputSignal': {'Parameters':['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters':['Device ID'],  'Status': {}},
            'PIPMode': {'Parameters':['Device ID'],  'Status': {}},
            'PIPSize': {'Parameters':['Device ID'],  'Status': {}},
            'Power': {'Parameters':['Device ID'],  'Status': {}},
            'ResolutionLongestDirection': {'Parameters':['Device ID'], 'Status': {}},
            'ResolutionShortestDirection': {'Parameters':['Device ID'], 'Status': {}},
            'Volume': {'Parameters':['Device ID'], 'Status': {}},
        }

        self.IDSent = False
        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '0'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(br'(WAIT\r\n)?OK (\d\d\d)\r\n'), self.__MatchDeviceOK, None)

        self.Regex = compile(br'\d{1,4} \d{3}\r\n|ERR\r\n|ERR \d\d\d\r\n|WAIT\r\n|LOCKED\r\n|UNSELECTED\r\n')
        self.DeviceIDRegex = compile(r'OK (\d\d\d)\r\n')


    def DeviceIDHandler(self, Callback, value, qualifier, CallBackType='Set'):
        if qualifier and 'Device ID' in qualifier:
            if qualifier['Device ID'] == 'Broadcast' or qualifier['Device ID'] == '0':
                qualifier['Device ID'] = '0'
                if CallBackType == 'Update':
                    self.Discard('Invalid Command')
                    return False
            elif not (1 <= int(qualifier['Device ID']) <= 255):
                self.Discard('Invalid Command')
                return False
            self.Callback = Callback
            self.valueCallback = value
            self.qualifierCallback = qualifier
            
            if self.SelectedID == qualifier['Device ID']:
                self.IDSent = False
                self.ExpiryTime = 0
                return True
            elif (self.ExpiryTime != 0) and (self.ExpiryTime <= time.monotonic()):
                self.IDSent = False
                self.ExpiryTime = 0
                self.Error(['Response timeout: Unable to set Device ID'])
            else:
                return self.IDLK_Callback()
        else:
            self.Discard('Invalid Command')
            
    def IDLK_Callback(self):
        if not self.IDSent:
            self.IDSent = True
            CmdString = 'IDLK{0:04d}\r\n'.format(int(self.qualifierCallback['Device ID']))
            self.SetIDLK( CmdString, None)
        else:
            self.Callback(self.valueCallback, self.qualifierCallback)            
            
    def SetIDLK(self, cmd_string, qualifier):
        self.ExpiryTime = time.monotonic() + 5  # 5s timeout
        self.Send(cmd_string)
        if self.qualifierCallback['Device ID'] == '0':
            self.SelectedID = '0'
        self.IDLK_Callback()

    def __MatchDeviceOK(self, match, tag):
        self.SelectedID = str(int(match.group(2).decode()))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide':       '1',
            'Normal':     '2',
            'Dot by Dot': '3',
            'Zoom':       '4',
        }
        if self.DeviceIDHandler(self.SetAspectRatio, value, qualifier):
            if qualifier['Device ID'] == '0':   # 0 is Broadcast, changed in DeviceIDHandler
                AspectRatioCmdString = 'WIDE{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                AspectRatioCmdString = 'WIDE{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'Dot by Dot',
            '4': 'Zoom',
        }

        if self.DeviceIDHandler(self.UpdateAspectRatio, value, qualifier, 'Update'):
            AspectRatioCmdString = 'WIDE????\r\n'
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAssignID(self, value, qualifier):

        AssignIDCmdString = 'IDST001+\r\n'
        self.__SetHelper('AssignID', AssignIDCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }
        if self.DeviceIDHandler(self.SetAudioMute, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                AudioMuteCmdString = 'MUTE{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                AudioMuteCmdString = 'MUTE{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        if self.DeviceIDHandler(self.UpdateAudioMute, value, qualifier, 'Update'):
            AudioMuteCmdString = 'MUTE????\r\n'
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):
        if self.DeviceIDHandler(self.SetAutoImage, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                AutoImageCmdString = 'ASNC  1+\r\n'
            else:
                AutoImageCmdString = 'ASNC   1\r\n'
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':  '0',
            'On 1': '1',
            'On 2': '2',
        }
        if self.DeviceIDHandler(self.SetExecutiveMode, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                ExecutiveModeCmdString = 'ALCK{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                ExecutiveModeCmdString = 'ALCK{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On 1',
            '2': 'On 2',
        }

        if self.DeviceIDHandler(self.UpdateExecutiveMode, value, qualifier, 'Update'):
            ExecutiveModeCmdString = 'ALCK????\r\n'
            res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('ExecutiveMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetExecutiveModeTarget(self, value, qualifier):

        ValueStateValues = {
            'Remote Control':  '0',
            'Monitor Buttons': '1',
            'Both':            '2',
        }
        if self.DeviceIDHandler(self.SetExecutiveModeTarget, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                ExecutiveModeTargetCmdString = 'ALTG{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                ExecutiveModeTargetCmdString = 'ALTG{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveModeTarget', ExecutiveModeTargetCmdString, value, qualifier)

    def UpdateExecutiveModeTarget(self, value, qualifier):

        ValueStateValues = {
            '0': 'Remote Control',
            '1': 'Monitor Buttons',
            '2': 'Both',
        }

        if self.DeviceIDHandler(self.UpdateExecutiveModeTarget, value, qualifier, 'Update'):
            ExecutiveModeTargetCmdString = 'ALTG????\r\n'
            res = self.__UpdateHelper('ExecutiveModeTarget', ExecutiveModeTargetCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('ExecutiveModeTarget', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Executive Mode Target: Invalid/unexpected response'])

    def SetIDCheck(self, value, qualifier):
        IDCheckCmdString = 'IDCK0000\r\n'
        self.__SetHelper('IDCheck', IDCheckCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Toggle':      '0',
            'D-SUB':       '2',
            'HDMI 1':      '10',
            'HDMI 2':      '13',
            'DisplayPort': '14',
            'Option':      '21',
            'Application': '24',
        }
        if self.DeviceIDHandler(self.SetInput, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                InputCmdString = 'INPS{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                InputCmdString = 'INPS{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '2':  'D-SUB',
            '10': 'HDMI 1',
            '13': 'HDMI 2',
            '14': 'DisplayPort',
            '21': 'Option',
            '24': 'Application',
        }

        if self.DeviceIDHandler(self.UpdateInput, value, qualifier, 'Update'):
            InputCmdString = 'INPS????\r\n'
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0:-6]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])

    def SetInputSignal(self, value, qualifier):

        ValueStateValues = {
            '768) 1360 x 768':   '1',
            '768) 1280 x 768':   '2',
            '768) 1024 x 768':   '3',
            '480) 848 x 480':    '5',
            '480) 640 x 480':    '6',
            '1050) 1680 x 1050': '7',
            '1050) 1400 x 1050': '8',
            '768) Auto':         '9',
            '480) Auto':         '10',
        }
        if self.DeviceIDHandler(self.SetInputSignal, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                InputSignalCmdString = 'PXSL{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                InputSignalCmdString = 'PXSL{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('InputSignal', InputSignalCmdString, value, qualifier)

    def UpdateInputSignal(self, value, qualifier):

        ValueStateValues = {
            '1':  '768) 1360 x 768',
            '2':  '768) 1280 x 768',
            '3':  '768) 1024 x 768',
            '5':  '480) 848 x 480',
            '6':  '480) 640 x 480',
            '7':  '1050) 1680 x 1050',
            '8':  '1050) 1400 x 1050',
            '9':  '768) Auto',
            '10': '480) Auto',
        }

        if self.DeviceIDHandler(self.UpdateInputSignal, value, qualifier, 'Update'):
            InputSignalCmdString = 'PXSL????\r\n'
            res = self.__UpdateHelper('InputSignal', InputSignalCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0:-6]]
                    self.WriteStatus('InputSignal', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Signal: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'D-SUB':       '2',
            'HDMI 1':      '10',
            'HDMI 2':      '13',
            'DisplayPort': '14',
            'Option':      '21',
            'Application': '24',
        }
        if self.DeviceIDHandler(self.SetPIPInput, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                PIPInputCmdString = 'MWIP{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                PIPInputCmdString = 'MWIP{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '2':  'D-SUB',
            '10': 'HDMI 1',
            '13': 'HDMI 2',
            '14': 'DisplayPort',
            '21': 'Option',
            '24': 'Application',
        }

        if self.DeviceIDHandler(self.UpdatePIPInput, value, qualifier, 'Update'):
            PIPInputCmdString = 'MWIP????\r\n'
            res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[:-6]]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off':                  '0',
            'PIP':                  '1',
            'Picture by Picture 1': '2',
            'Picture by Picture 2': '3',
        }
        if self.DeviceIDHandler(self.SetPIPMode, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                PIPModeCmdString = 'MWIN{0:>3}+\r\n'.format(ValueStateValues[value])
            else:
                PIPModeCmdString = 'MWIN{0:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'Picture by Picture 1',
            '3': 'Picture by Picture 2',
        }

        if self.DeviceIDHandler(self.UpdatePIPMode, value, qualifier, 'Update'):
            PIPModeCmdString = 'MWIN????\r\n'
            res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('PIPMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 64,
        }
        if self.DeviceIDHandler(self.SetPIPSize, value, qualifier):
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                    PIPSizeCmdString = 'MPSZ{:>3}+\r\n'.format(value)
                else:
                    PIPSizeCmdString = 'MPSZ{:>4}\r\n'.format(value)
                self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 64,
        }

        if self.DeviceIDHandler(self.UpdatePIPSize, value, qualifier, 'Update'):
            PIPSizeCmdString = 'MPSZ????\r\n'
            res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[:-6])
                    if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                        self.WriteStatus('PIPSize', value, qualifier)
                    else:
                        self.Error(['PIP Size: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
        }
        if self.DeviceIDHandler(self.SetPower, value, qualifier):
            if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                PowerCmdString = 'POWR{:>3}+\r\n'.format(ValueStateValues[value])
            else:
                PowerCmdString = 'POWR{:>4}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode',
        }

        if self.DeviceIDHandler(self.UpdatePower, value, qualifier, 'Update'):
            PowerCmdString = 'POWR????\r\n'
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])

    def SetResolutionLongestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1920,
        }
        if self.DeviceIDHandler(self.SetResolutionLongestDirection, value, qualifier):
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                if self.DeviceIDHandler('SetResolutionLongestDirection', value, qualifier):
                    if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                        ResolutionLongestDirectionCmdString = 'HRES{:>3}+\r\n'.format(value)
                    else:
                        ResolutionLongestDirectionCmdString = 'HRES{:>4}\r\n'.format(value)
                    self.__SetHelper('ResolutionLongestDirection', ResolutionLongestDirectionCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetResolutionLongestDirection')

    def UpdateResolutionLongestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1920,
        }

        if self.DeviceIDHandler(self.UpdateResolutionLongestDirection, value, qualifier, 'Update'):
            ResolutionLongestDirectionCmdString = 'HRES????\r\n'
            res = self.__UpdateHelper('ResolutionLongestDirection', ResolutionLongestDirectionCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[:-6])
                    if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                        self.WriteStatus('ResolutionLongestDirection', value, qualifier)
                    else:
                        self.Error(['Resolution Longest Direction: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Resolution Longest Direction: Invalid/unexpected response'])

    def SetResolutionShortestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1200,
        }
        if self.DeviceIDHandler(self.SetResolutionShortestDirection, value, qualifier):
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                if self.DeviceIDHandler('SetResolutionShortestDirection', value, qualifier):
                    if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                        ResolutionShortestDirectionCmdString = 'VRES{:>3}+\r\n'.format(value)
                    else:
                        ResolutionShortestDirectionCmdString = 'VRES{:>4}\r\n'.format(value)
                    self.__SetHelper('ResolutionShortestDirection', ResolutionShortestDirectionCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetResolutionShortestDirection')

    def UpdateResolutionShortestDirection(self, value, qualifier):

        ValueConstraints = {
            'Min': 300,
            'Max': 1200,
        }

        if self.DeviceIDHandler(self.UpdateResolutionShortestDirection, value, qualifier, 'Update'):
            ResolutionShortestDirectionCmdString = 'VRES????\r\n'
            res = self.__UpdateHelper('ResolutionShortestDirection', ResolutionShortestDirectionCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[:-6])
                    if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                        self.WriteStatus('ResolutionShortestDirection', value, qualifier)
                    else:
                        self.Error(['Resolution Shortest Direction: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Resolution Shortest Direction: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31,
        }
        if self.DeviceIDHandler(self.SetVolume, value, qualifier):
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                if qualifier['Device ID'] == '0':  # 0 is Broadcast, changed in DeviceIDHandler
                    VolumeCmdString = 'VOLM{:>3}+\r\n'.format(value)
                else:
                    VolumeCmdString = 'VOLM{:>4}\r\n'.format(value)
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31,
        }

        if self.DeviceIDHandler(self.UpdateVolume, value, qualifier, 'Update'):
            VolumeCmdString = 'VOLM????\r\n'
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[:-6])
                    if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                        self.WriteStatus('Volume', value, qualifier)
                    else:
                        self.Error(['Volume: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if isinstance(response, bytes):
                response = response.decode()

            if 'ERR' in response:
                error_string = '{}: Communication error or incorrect command.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
            elif 'OK' in response:
                res = search(self.DeviceIDRegex, response)
                self.SelectedID = str(int(res.group(1)))
            elif 'WAIT' in response:
                error_string = '{}: Waiting for response.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
            elif 'LOCKED' in response:
                error_string = '{}: Control via RS-232 is locked.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
            elif 'UNSELECTED' in response:
                error_string = '{}: Monitor Control Select is set to LAN or Application.'.format(sourceCmdName)
                self.Error([error_string])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or (qualifier and qualifier['Device ID'] == '0'):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)



    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.IDSent = False
        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self. SelectedID = '0'
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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