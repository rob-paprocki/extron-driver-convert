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
            'AutoImage': {'Status': {}},
            'Channel': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PictureInPicturePosition': {'Status': {}},
            'PictureInPictureSwap': {'Status': {}},
            'Power': {'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(CHA!0(\d\d)\)'), self.__MatchChannel, None)
            self.AddMatchString(re.compile(b'\(FRZ!00([01])\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN!00([1-8])\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(LPM!00([012])\)'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\(LPH!(\d+)\)'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\(OSD!00([01])\)'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\(PJH!(\d+)\)'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\(PIP!00([01])\)'), self.__MatchPictureInPicture, None)
            self.AddMatchString(re.compile(b'\(PPP!00([0-4])\)'), self.__MatchPictureInPicturePosition, None)
            self.AddMatchString(re.compile(b'\(PWR!0([01][0-3])\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(ITP!0([01][0-8])\)'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'\(PMT!00([01])\)'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\(\d{5} \d{5}ERR 0[01][0-9] "(.*)"\)'), self.__MatchError, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(ASU)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Min': 1,
            'Max': 50
        }

        if ValueStateValues['Min'] <= int(value) <= ValueStateValues['Max']:
            ChannelCmdString = '(CHA {0})'.format(value)
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = '(CHA?)'
        self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)

    def __MatchChannel(self, match, tag):

        value = match.group(1).decode().lstrip('0')
        self.WriteStatus('Channel', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '(FRZ {0})'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '(FRZ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'BNC': '1',
            'DVI-I': '2',
            'Composite': '3',
            'S-Video': '4',
            'Slot 1 (Input 1)': '5',
            'Slot 1 (Input 2)': '7',
            'Slot 2 (Input 1)': '6',
            'Slot 2 (Input 2)': '8'
        }

        InputCmdString = '(SIN {0})'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '1': 'BNC',
            '2': 'DVI-I',
            '3': 'Composite',
            '4': 'S-Video',
            '5': 'Slot 1 (Input 1)',
            '7': 'Slot 1 (Input 2)',
            '6': 'Slot 2 (Input 1)',
            '8': 'Slot 2 (Input 2)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadDepressCmdString = '(KEY {0})'.format(value)
            KeypadReleaseCmdString = '(KEY {0})'.format(int(value) + 128)   # released command

            self.__SetHelper('Keypad', KeypadDepressCmdString, value, qualifier)
            self.__SetHelper('Keypad', KeypadReleaseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Maximum Brightness': '0',
            'Maintain Intensity': '1',
            'Maintain Power': '2'
        }

        LampModeCmdString = '(LPM {0})'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '(LPM?)'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '0': 'Maximum Brightness',
            '1': 'Maintain Intensity',
            '2': 'Maintain Power'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '(LPH?)'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '58',
            'Down': '59',
            'Left': '60',
            'Right': '62',
            'Enter': '13',
            'Menu': '44',
            'Exit': '27'
        }

        MenuNavigationDepressString = '(KEY {0})'.format(ValueStateValues[value])
        MenuNavigationReleaseString = '(KEY {0})'.format(int(ValueStateValues[value]) + 128)
        self.__SetHelper('MenuNavigation', MenuNavigationDepressString, value, qualifier)
        self.__SetHelper('MenuNavigation', MenuNavigationReleaseString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = '(OSD {0})'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '(OSD?)'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '(PJH?)'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PictureInPictureCmdString = '(PIP {0})'.format(ValueStateValues[value])
        self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPictureCmdString = '(PIP?)'
        self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def __MatchPictureInPicture(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureInPicture', value, None)

    def SetPictureInPicturePosition(self, value, qualifier):

        ValueStateValues = {
            'Top Right': '0',
            'Top Left': '1',
            'Bottom Left': '2',
            'Bottom Right': '3'
        }

        PictureInPicturePositionCmdString = '(PPP {0})'.format(ValueStateValues[value])
        self.__SetHelper('PictureInPicturePosition', PictureInPicturePositionCmdString, value, qualifier)

    def UpdatePictureInPicturePosition(self, value, qualifier):

        PictureInPicturePositionCmdString = '(PIP?)'
        self.__UpdateHelper('PictureInPicturePosition', PictureInPicturePositionCmdString, value, qualifier)

    def __MatchPictureInPicturePosition(self, match, tag):

        ValueStateValues = {
            '0': 'Top Right',
            '1': 'Top Left',
            '2': 'Bottom Left',
            '3': 'Bottom Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureInPicturePosition', value, None)

    def SetPictureInPictureSwap(self, value, qualifier):

        PictureInPictureSwapCmdString = '(PPS)'
        self.__SetHelper('PictureInPictureSwap', PictureInPictureSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'Boot Mode': '2',
            'No Lamp': '3',
            'Warming Up': '11'
        }

        PowerCmdString = '(PWR {0})'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)'

        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
            '02': 'Boot Mode',
            '03': 'No Lamp',
            '11': 'Warming Up'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Grid': '1',
            'Grey Scale': '2',
            'White': '3',
            'Flat Grey': '4',
            'Black': '5',
            'Checker': '6',
            '13 Point': '7',
            'Color Bars': '8',
            'Edge Blend': '11',
            'Aspect Ratio': '12'
        }

        TestPatternCmdString = '(ITP {0})'.format(ValueStateValues[value])
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = '(ITP?)'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '01': 'Grid',
            '02': 'Grey Scale',
            '03': 'White',
            '04': 'Flat Grey',
            '05': 'Black',
            '06': 'Checker',
            '07': '13 Point',
            '08': 'Color Bars',
            '11': 'Edge Blend',
            '12': 'Aspect Ratio'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '(PMT {0})'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '(PMT?)'
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
        self.Error(['An error occurred: ' + match.group(1).decode()])

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

