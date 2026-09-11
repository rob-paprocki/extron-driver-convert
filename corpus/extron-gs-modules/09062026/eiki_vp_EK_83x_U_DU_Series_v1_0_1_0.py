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
            'AspectRatio': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'HSG': {'Status': {}},
            'Input': {'Status': {}},
            'LaserPower': {'Status': {}},
            'LoadLensMemory': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'ProjectionMode': {'Status': {}},
            'SignalPowerOn': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'#ASP=([0-3])\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'#SER=([EWO]{19})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(compile(b'#HSG=([01])\r'), self.__MatchHSG, None)
            self.AddMatchString(compile(b'#INQ=([0-68SE])\r'), self.__MatchInput, None)
            self.AddMatchString(compile(b'#LSR=([01])\r'), self.__MatchLaserPower, None)
            self.AddMatchString(compile(b'#LTT=(\d+)H\d+M\r'), self.__MatchOperationHours, None)
            self.AddMatchString(compile(b'#PIM=([0-4])\r'), self.__MatchPictureMode, None)
            self.AddMatchString(compile(b'#PPS=([01579])\r'), self.__MatchPower, None)
            self.AddMatchString(compile(b'#PRJ=([0-3])\r'), self.__MatchProjectionMode, None)
            self.AddMatchString(compile(b'#SPO=([01])\r'), self.__MatchSignalPowerOn, None)
            self.AddMatchString(compile(b'#MUT=([01])\r'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'#(?:(APS|SER|DER|HSG|INP|INQ|LSR|LTT|PIM|PPS|PRJ|SPO|MUT)=)?ER0\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            '4:3': '1',
            '16:9': '2',
            '16:10': '3'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = '*ASP={}\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '*ASP\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': '4:3',
            '2': '16:9',
            '3': '16:10'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '*DER\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        error_warning_values = (
            'Laser',
            'Temperature',
            'Color Wheel',
            'Phosphor Wheel 1',
            'Phosphor Wheel 2',
            'Liquid Pump 1',
            'Liquid Pump 2',
            'Fan 1',
            'Fan 2',
            'Fan 3',
            'Fan 4',
            'Fan 5',
            'Fan 6',
            'Fan 7',
            'Fan 8',
            'Fan 9',
            'Fan 10',
            'Fan 11',
            'Fan 12'
        )

        status_count = {}
        status_str = match.group(1).decode()
        for char in status_str:
            if char not in status_count.keys():
                status_count[char] = 0
            status_count[char] += 1

        if 'E' not in status_count and 'W' not in status_count:
            value = 'Normal'
        elif 'E' not in status_count and status_count['W'] > 1:
            value = 'Multiple Warnings'
        elif 'W' not in status_count and status_count['E'] > 1:
            value = 'Multiple Errors'
        elif 'E' in status_count and 'W' in status_count:
            value = 'Multiple Errors and Warnings'
        elif 'W' in status_count:
            pos = status_str.find('W')
            value = '{} Warning'.format(error_warning_values[pos])
        else:
            pos = status_str.find('E')
            value = '{} Error'.format(error_warning_values[pos])

        self.WriteStatus('DeviceStatus', value, None)

    def SetHSG(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            HSGCmdString = '*HSG={}\r'.format(ValueStateValues[value])
            self.__SetHelper('HSG', HSGCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHSG')

    def UpdateHSG(self, value, qualifier):

        HSGCmdString = '*HSG\r'
        self.__UpdateHelper('HSG', HSGCmdString, value, qualifier)

    def __MatchHSG(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HSG', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1': '0',
            'Computer 2 (BNC)': '1',
            'HDMI / MHL': '2',
            'DVI-D': '3',
            'Video': '4',
            'S-Video': '5',
            'HDBaseT': '6',
            '3G-SDI': '8'
        }

        if value in ValueStateValues:
            InputCmdString = '*INP={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*INQ\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'Computer 1',
            '1': 'Computer 2 (BNC)',
            '2': 'HDMI / MHL',
            '3': 'DVI-D',
            '4': 'Video',
            '5': 'S-Video',
            '6': 'HDBaseT',
            '8': '3G-SDI',
            'S': 'Searching',
            'E': 'Other'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLaserPower(self, value, qualifier):

        ValueStateValues = {
            'Low': '0',
            'Standard': '1'
        }

        if value in ValueStateValues:
            LaserPowerCmdString = '*LSR={}\r'.format(ValueStateValues[value])
            self.__SetHelper('LaserPower', LaserPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLaserPower')

    def UpdateLaserPower(self, value, qualifier):

        LaserPowerCmdString = '*LSR\r'
        self.__UpdateHelper('LaserPower', LaserPowerCmdString, value, qualifier)

    def __MatchLaserPower(self, match, tag):

        ValueStateValues = {
            '0': 'Low',
            '1': 'Standard'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LaserPower', value, None)

    def SetLoadLensMemory(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5'
        }

        if value in ValueStateValues:
            LoadLensMemoryCmdString = '*LEN={}\r'.format(ValueStateValues[value])
            self.__SetHelper('LoadLensMemory', LoadLensMemoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadLensMemory')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '*LTT\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Bright': '0',
            'Standard': '1',
            'Vivid': '2',
            'sRGB': '3',
            'DICOM SIM': '4'
        }

        if value in ValueStateValues:
            PictureModeCmdString = '*PIM={}\r'.format(ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '*PIM\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Bright',
            '1': 'Standard',
            '2': 'Vivid',
            '3': 'sRGB',
            '4': 'DICOM SIM',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '*PWO\r',
            'Off': '*PWF\r'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '*PPS\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '5': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '7': 'Cooling Down',
            '9': 'Shutdown by Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetProjectionMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'Rear': '1',
            'Ceiling': '2',
            'Rear Ceiling': '3'
        }

        if value in ValueStateValues:
            ProjectionModeCmdString = '*PRJ={}\r'.format(ValueStateValues[value])
            self.__SetHelper('ProjectionMode', ProjectionModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProjectionMode')

    def UpdateProjectionMode(self, value, qualifier):

        ProjectionModeCmdString = '*PRJ\r'
        self.__UpdateHelper('ProjectionMode', ProjectionModeCmdString, value, qualifier)

    def __MatchProjectionMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'Rear',
            '2': 'Ceiling',
            '3': 'Rear Ceiling'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ProjectionMode', value, None)

    def SetSignalPowerOn(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            SignalPowerOnCmdString = '*SPO={}\r'.format(ValueStateValues[value])
            self.__SetHelper('SignalPowerOn', SignalPowerOnCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSignalPowerOn')

    def UpdateSignalPowerOn(self, value, qualifier):

        SignalPowerOnCmdString = '*SPO\r'
        self.__UpdateHelper('SignalPowerOn', SignalPowerOnCmdString, value, qualifier)

    def __MatchSignalPowerOn(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SignalPowerOn', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = '*MUT={}\r'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '*MUT\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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

        cmd_names = {
            'APS': 'Aspect Ratio',
            'SER': 'Device Status',
            'DER': 'Device Status',
            'HSG': 'HSG',
            'INP': 'Input',
            'INQ': 'Input',
            'LSR': 'Laser Power',
            'LTT': 'Operation Hours',
            'PIM': 'Picture Mode',
            'PPS': 'Power',
            'PRJ': 'Projection Mode',
            'SPO': 'Signal Power On',
            'MUT': 'Video Mute'
        }

        if match.group(1) and match.group(1).decode() in cmd_names:
            error_msg = 'Execution Failure Response for command: {}'.format(cmd_names[match.group(1).decode()])
        else:
            error_msg = 'Invalid Command Response'
        self.Error([error_msg])

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

