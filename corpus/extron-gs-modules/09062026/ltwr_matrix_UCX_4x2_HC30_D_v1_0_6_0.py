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
            'ActiveHDCPVersion': {'Parameters':['Input'], 'Status': {}},
            'AnalogAudioOutputVolume': { 'Status': {}},
            'AudioInput': { 'Status': {}},
            'AudioPort1Mute': {'Parameters':['Input'], 'Status': {}},
            'AudioPort2Mute': { 'Status': {}},
            'HDCPMode': {'Parameters':['Output'], 'Status': {}},
            'HDCPSetting': {'Parameters':['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'USBAutoselect': { 'Status': {}},
            'USBInput': { 'Status': {}},
            'VideoInputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'VideoMatrixRefresh': { 'Status': {}},
            'VideoMatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'VideoOutputTieStatus': {'Parameters':['Output'], 'Status': {}},
            'VideoPortMute': {'Parameters':['Input'], 'Status': {}},
        } 
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'/V1/MEDIA/VIDEO/XP/I([1-5])\.ActiveHdcpVersion=(N/A|None|HDCP 1.4|HDCP 2.2)\r\n'), self.__MatchActiveHDCPVersion, None)
            self.AddMatchString(re.compile(b'/V1/MEDIA/AUDIO/O3\.VolumePercent=(\d{1,3})\r\n'), self.__MatchAnalogAudioOutputVolume, None)
            self.AddMatchString(re.compile(b'/V1/MEDIA/AUDIO/XP/O3\.ConnectedSource=I([1-4])\r\n'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'/V1/MEDIA/VIDEO/I([1-5])\.SignalPresent=(true|false)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'/V1/MEDIA/USB/XP/H1\.ConnectedSource=U?([0-4])\r\n'), self.__MatchUSBInput, None)
            self.AddMatchString(re.compile(b'/V1/MEDIA/VIDEO/XP/O([1-2])\.ConnectedSource=I?([0-5])\r\n'), self.__MatchVideoTieStatus, None)
            self.AddMatchString(re.compile(b'[npm]E .+? %E(\d{3}:.*?)\r\n'), self.__MatchError, None)

    def __MatchActiveHDCPVersion(self, match, tag):

        ValueStateValues = {
            'N/A':      'Not Available', 
            'None':     'None', 
            'HDCP 1.4': 'HDCP 1.4', 
            'HDCP 2.2': 'HDCP 2.2'
        }
        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ActiveHDCPVersion', value, qualifier)
    
    def SetAnalogAudioOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AnalogAudioOutputVolumeCmdString = 'SET /V1/MEDIA/AUDIO/O3.VolumePercent={}\r\n'.format(value)
            self.__SetHelper('AnalogAudioOutputVolume', AnalogAudioOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogAudioOutputVolume')

    def __MatchAnalogAudioOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('AnalogAudioOutputVolume', value, None)
        
    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            '1':    'I1', 
            '2':    'I2', 
            '3':    'I3', 
            '4':    'I4', 
            'Break':'0'
        }

        if value in ValueStateValues:
            AudioInputCmdString = 'CALL /V1/MEDIA/AUDIO/XP:switch({}:O3)\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        AudioInputCmdString = 'GET /V1/MEDIA/AUDIO/XP/O3.ConnectedSource\r\n'
        self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def __MatchAudioInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('AudioInput', value, None)

    def SetAudioPort1Mute(self, value, qualifier):

        ValueStateValues = {
            'On':  'true', 
            'Off': 'false'
        }

        input_val = qualifier['Input']
        if value in ValueStateValues and 1 <= int(input_val) <= 4:
            AudioPort1MuteCmdString = 'SET /V1/MEDIA/AUDIO/XP/I{}.Mute={}\r\n'.format(input_val, ValueStateValues[value])
            self.__SetHelper('AudioPort1Mute', AudioPort1MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioPort1Mute')

    def SetAudioPort2Mute(self, value, qualifier):

        ValueStateValues = {
            'On':  'true', 
            'Off': 'false'
        }

        if value in ValueStateValues:
            AudioPort2MuteCmdString = 'SET /V1/MEDIA/AUDIO/O3.Mute={}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AudioPort2Mute', AudioPort2MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioPort2Mute')

    def SetHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'Auto':   'Auto', 
            'Always': 'Always'
        }

        output_val = qualifier['Output']
        if value in ValueStateValues and output_val in ('1', '2'):
            HDCPModeCmdString = 'SET /V1/MEDIA/VIDEO/O{}.HdcpMode={}\r\n'.format(output_val, ValueStateValues[value])
            self.__SetHelper('HDCPMode', HDCPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPMode')

    def SetHDCPSetting(self, value, qualifier):

        ValueStateValues = {
            'HDCP 1.4': 'HDCP 1.4', 
            'HDCP 2.2': 'HDCP 2.2', 
            'Off':      'Off'
        }

        input_val = qualifier['Input']
        if value in ValueStateValues and 1 <= int(input_val) <= 5:
            HDCPSettingCmdString = 'SET /V1/MEDIA/VIDEO/I{}/HDCP.AllowedHdcpVersion={}\r\n'.format(input_val, ValueStateValues[value])
            self.__SetHelper('HDCPSetting', HDCPSettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPSetting')

    def UpdateInputSignalStatus(self, value, qualifier):

        input_val = qualifier['Input']
        if 1 <= int(input_val) <= 5:
            InputSignalStatusCmdString = 'GET /V1/MEDIA/VIDEO/I{}.SignalPresent\r\n'.format(input_val)
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            'true':  'Present', 
            'false': 'Not Present'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetUSBAutoselect(self, value, qualifier):

        ValueStateValues = ('Follow Video', 'Off')

        if value in ValueStateValues:
            USBAutoselectCmdString = 'SET /V1/MEDIA/USB/AUTOSELECT/H1.Policy={}\r\n'.format(value)
            self.__SetHelper('USBAutoselect', USBAutoselectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBAutoselect')

    def SetUSBInput(self, value, qualifier):

        ValueStateValues = {
            '1':     'U1', 
            '2':     'U2', 
            '3':     'U3', 
            '4':     'U4', 
            'Break': '0'
        }

        if value in ValueStateValues:
            USBInputCmdString = 'CALL /V1/MEDIA/USB/XP:switch({}:H1)\r\n'.format(ValueStateValues[value])
            self.__SetHelper('USBInput', USBInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBInput')

    def UpdateUSBInput(self, value, qualifier):

        USBInputCmdString = 'GET /V1/MEDIA/USB/XP/H1.ConnectedSource\r\n'
        self.__UpdateHelper('USBInput', USBInputCmdString, value, qualifier)

    def __MatchUSBInput(self, match, tag):

        value = match.group(1).decode()
        if value == '0':
            value = 'No Source Detected'
        self.WriteStatus('USBInput', value, None)

    def SetVideoMatrixRefresh(self, value, qualifier):

        self.__SetHelper('VideoMatrixRefresh', 'GET /V1/MEDIA/VIDEO/XP/O1.ConnectedSource\r\n', value, qualifier)
        self.__SetHelper('VideoMatrixRefresh', 'GET /V1/MEDIA/VIDEO/XP/O2.ConnectedSource\r\n', value, qualifier)

    def __MatchVideoTieStatus(self, match, tag):

        InputStates = ['1', '2', '3', '4', '5']
        
        output_val = match.group(1).decode()
        input_val = match.group(2).decode()
        self.WriteStatus('VideoOutputTieStatus', input_val, {'Output' : output_val})
        for input_ in InputStates:
            if input_ == input_val:
                self.WriteStatus('VideoInputTieStatus', 'Tied', {'Input': input_, 'Output': output_val})
            else:
                self.WriteStatus('VideoInputTieStatus', 'Untied', {'Input': input_, 'Output': output_val})

    def SetVideoMatrixTieCommand(self, value, qualifier):

        InputStates = {
            '1':     'I1', 
            '2':     'I2', 
            '3':     'I3', 
            '4':     'I4', 
            '5':     'I5', 
            'Break': '0'
        }

        OutputStates = ('1', '2', 'All')
        
        input_val = qualifier['Input']
        output_val = qualifier['Output']
        if input_val in InputStates and output_val in OutputStates:
            if output_val == 'All':
                VideoMatrixTieCommandCmdString = 'CALL /V1/MEDIA/VIDEO/XP:switchAll({})\r\n'.format(InputStates[input_val])
            else:
                VideoMatrixTieCommandCmdString = 'CALL /V1/MEDIA/VIDEO/XP:switch({}:O{})\r\n'.format(InputStates[input_val],
                                                    output_val)
            self.__SetHelper('VideoMatrixTieCommand', VideoMatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMatrixTieCommand')

    def SetVideoPortMute(self, value, qualifier):

        ValueStateValues = {
            'On':  'true', 
            'Off': 'false'
        }

        input_val = qualifier['Input']
        if value in ValueStateValues and 1 <= int(input_val) <= 5:
            VideoPortMuteCmdString = 'SET /V1/MEDIA/VIDEO/XP/I{}.Mute={}\r\n'.format(input_val, ValueStateValues[value])
            self.__SetHelper('VideoPortMute', VideoPortMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoPortMute')

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

        self.Error(['An error occurred: {}'.format(match.group(1).decode())])

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