from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPInput': {'Parameters': ['PIP Window'], 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'PIPPresetRecall': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }                    
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07\x01\x00\x41\x53\x50([\x00-\x03])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x4D\x55\x54([\x00-\x01])\x08'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x4D\x49\x4E([\x00\x0D\x10\x0E\x09\x0A\x0B\x0C])\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x53\x43\x4D([\x00-\x04])\x08'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x50\x49([\x4E-\x50])([\x00\x0D\x10\x0E\x09\x0A\x0B\x0C])\x08'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x50\x53\x43([\x00-\x04\x07])\x08'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x50\x50\x4F([\x00-\x03])\x08'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x50\x4F\x57([\x00-\x01])\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00\x56\x4F\x4C([\x00-\x64])\x08'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Native':      b'\x00',
            'Full Screen': b'\x01',
            '4:3':         b'\x02',
            'Letterbox':   b'\x03'
        }

        AspectRatioCmdString = b'\x07\x01\x02\x41\x53\x50' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x07\x01\x01\x41\x53\x50\x08'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Native',
            b'\x01': 'Full Screen',
            b'\x02': '4:3',
            b'\x03': 'Letterbox'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b'\x07\x01\x02\x4D\x55\x54' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x07\x01\x01\x4D\x55\x54\x08'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA':           b'\x00',
            'DisplayPort 1': b'\x0D',
            'DisplayPort 2': b'\x10',
            'OPS':           b'\x0E',
            'HDMI 1':        b'\x09',
            'HDMI 2':        b'\x0A',
            'HDMI 3':        b'\x0B',
            'HDMI 4':        b'\x0C'
        }

        InputCmdString = b'\x07\x01\x02\x4D\x49\x4E' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x07\x01\x01\x4D\x49\x4E\x08'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x0D': 'DisplayPort 1',
            b'\x10': 'DisplayPort 2',
            b'\x0E': 'OPS',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'HDMI 3',
            b'\x0C': 'HDMI 4'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':  b'\x0E',
            'Info':  b'\x04',
            'Up':    b'\x02',
            'Down':  b'\x19',
            'Left':  b'\x01',
            'Right': b'\x03',
            'Enter': b'\x12',
            'Exit':  b'\x05'
        }

        MenuNavigationCmdString = b'\x07\x01\x02\x52\x43\x55' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'User':   b'\x00',
            'Sport':  b'\x01',
            'Game':   b'\x02',
            'Cinema': b'\x03',
            'Vivid':  b'\x04'
        }

        PictureModeCmdString = b'\x07\x01\x02\x53\x43\x4D' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x07\x01\x01\x53\x43\x4D\x08'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'User',
            b'\x01': 'Sport',
            b'\x02': 'Game',
            b'\x03': 'Cinema',
            b'\x04': 'Vivid'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPWindowStates = {
            'Sub Window 1': b'\x4E',
            'Sub Window 2': b'\x4F',
            'Sub Window 3': b'\x50'
        }

        ValueStateValues = {
            'VGA':           b'\x00',
            'DisplayPort 1': b'\x0D',
            'DisplayPort 2': b'\x10',
            'OPS':           b'\x0E',
            'HDMI 1':        b'\x09',
            'HDMI 2':        b'\x0A',
            'HDMI 3':        b'\x0B',
            'HDMI 4':        b'\x0C'
        }

        if qualifier['PIP Window'] in PIPWindowStates:
            PIPInputCmdString = b'\x07\x01\x02\x50\x49' + PIPWindowStates[qualifier['PIP Window']] + ValueStateValues[value] + b'\x08'
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPWindowStates = {
            'Sub Window 1': b'\x4E',
            'Sub Window 2': b'\x4F',
            'Sub Window 3': b'\x50'
        }

        PIPInputCmdString = b'\x07\x01\x01\x50\x49' + PIPWindowStates[qualifier['PIP Window']] + b'\x08'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        PIPWindowStates = {
            b'\x4E': 'Sub Window 1',
            b'\x4F': 'Sub Window 2',
            b'\x50': 'Sub Window 3'
        }

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x0D': 'DisplayPort 1',
            b'\x10': 'DisplayPort 2',
            b'\x0E': 'OPS',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'HDMI 3',
            b'\x0C': 'HDMI 4'
        }

        qualifier = {'PIP Window': PIPWindowStates[match.group(1)]}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('PIPInput', value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off':          b'\x00',
            'Small':        b'\x01',
            'Medium':       b'\x02',
            'Large':        b'\x03',
            'Side by Side': b'\x04',
            'Quad View':    b'\x07'
        }

        PIPModeCmdString = b'\x07\x01\x02\x50\x53\x43' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = b'\x07\x01\x01\x50\x53\x43\x08'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'Small',
            b'\x02': 'Medium',
            b'\x03': 'Large',
            b'\x04': 'Side by Side',
            b'\x07': 'Quad View'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left':  b'\x00',
            'Bottom Right': b'\x01',
            'Top Left':     b'\x02',
            'Top Right':    b'\x03'
        }

        PIPPositionCmdString = b'\x07\x01\x02\x50\x50\x4F' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = b'\x07\x01\x01\x50\x50\x4F\x08'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Bottom Left',
            b'\x01': 'Bottom Right',
            b'\x02': 'Top Left',
            b'\x03': 'Top Right'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPPresetRecall(self, value, qualifier):

        ValueStateValues = {
            'Preset 1': b'\x00',
            'Preset 2': b'\x01',
            'Preset 3': b'\x02',
            'Preset 4': b'\x03'
        }

        PIPPresetRecallCmdString = b'\x07\x01\x02\x50\x52\x43' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('PIPPresetRecall', PIPPresetRecallCmdString, value, qualifier)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b'\x07\x01\x02\x53\x57\x41\x00\x08'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b'\x07\x01\x02\x50\x4F\x57' + ValueStateValues[value] + b'\x08'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = b'\x07\x01\x01\x50\x4F\x57\x08'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\x07\x01\x02\x56\x4F\x4C' + bytes([value]) + b'\x08'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x07\x01\x01\x56\x4F\x4C\x08'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = match.group(0)[6]
        self.WriteStatus('Volume', value, None)

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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