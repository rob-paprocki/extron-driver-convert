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
            'AspectRatio': { 'Status': {}},
            'AutoImage': {'Parameters':['Mode'], 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(SZP!([0-6])\)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\(CLC!(0|1|2)\)'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'\(FRZ!(0|1)\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN\+MAIN!([0-9]{1,2})\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(LPM!(0|1|3)\)'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\(OSD!(0|1)\)'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\(SIN\+PIP!([0-9]{1,2})\)'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\(PIP!(0|1)\)'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\(PPP!([0-7])\)'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\(PHS!(0|1|2)\)'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\(PWR!(0|1)\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!(0|1)\)'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\(.*ERR.*\)'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'        : '(SZP 0)', 
            'Native'      : '(SZP 1)', 
            '4:3'         : '(SZP 2)', 
            'LetterBox'   : '(SZP 3)', 
            'Full Size'   : '(SZP 4)', 
            'Full Width'  : '(SZP 5)', 
            'Full Height' : '(SZP 6)'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '(SZP ?)'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : 'Native', 
            '2' : '4:3', 
            '3' : 'LetterBox', 
            '4' : 'Full Size', 
            '5' : 'Full Width', 
            '6' : 'Full Height'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        ModeStates = {
            'Normal' : '(AIM 0)', 
            'Wide'   : '(AIM 1)'
        }
        mode = qualifier['Mode']
        if mode in ModeStates:
            AutoImageCmdString = ModeStates[mode]
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off'  : '(CLC 0)',
            'CC1'  : '(CLC 1)',
            'CC2'  : '(CLC 2)'
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = '(CLC ?)'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'CC1', 
            '2' : 'CC2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(FRZ 1)', 
            'Off' : '(FRZ 0)'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '(FRZ ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'         : '(SIN+MAIN 1)', 
            'HDMI'        : '(SIN+MAIN 4)', 
            'DVI-D'       : '(SIN+MAIN 5)', 
            'DisplayPort' : '(SIN+MAIN 6)', 
            'Component'   : '(SIN+MAIN 7)', 
            'S-Video'     : '(SIN+MAIN 8)', 
            'Composite'   : '(SIN+MAIN 9)', 
            'Mini USB'    : '(SIN+MAIN 12)'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN+MAIN ?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '1' : 'VGA', 
            '4' : 'HDMI', 
            '5' : 'DVI-D', 
            '6' : 'DisplayPort', 
            '7' : 'Component', 
            '8' : 'S-Video', 
            '9' : 'Composite', 
            '12' : 'Mini USB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : '(KEY 36)', 
            '1' : '(KEY 26)', 
            '2' : '(KEY 27)', 
            '3' : '(KEY 28)', 
            '4' : '(KEY 29)', 
            '5' : '(KEY 30)', 
            '6' : '(KEY 31)', 
            '7' : '(KEY 32)', 
            '8' : '(KEY 33)', 
            '9' : '(KEY 34)'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Constant Power (Default)' : '(LPM 0)', 
            'Constant Intensity'       : '(LPM 1)', 
            'Eco'                      : '(LPM 3)'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '(LPM ?)'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Constant Power (Default)', 
            '1' : 'Constant Intensity', 
            '3' : 'Eco'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '(KEY 19)', 
            'Up'    : '(KEY 38)', 
            'Down'  : '(KEY 42)', 
            'Right' : '(KEY 41)', 
            'Left'  : '(KEY 39)', 
            'Exit'  : '(KEY 20)', 
            'Enter' : '(KEY 40)'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(OSD 1)', 
            'Off' : '(OSD 0)'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '(OSD ?)'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'          : '(SIN+PIP 1)', 
            'HDMI'         : '(SIN+PIP 4)', 
            'DVI-D'        : '(SIN+PIP 5)', 
            'DisplayPort'  : '(SIN+PIP 6)', 
            'Component'    : '(SIN+PIP 7)', 
            'S-Video'      : '(SIN+PIP 8)', 
            'Composite'    : '(SIN+PIP 9)', 
            'Mini USB'     : '(SIN+PIP 12)'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '(SIN+PIP ?)'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            '1' : 'VGA', 
            '4' : 'HDMI', 
            '5' : 'DVI-D', 
            '6' : 'DisplayPort', 
            '7' : 'Component', 
            '8' : 'S-Video', 
            '9' : 'Composite', 
            '12' : 'Mini USB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(PIP 1)', 
            'Off' : '(PIP 0)'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '(PIP ?)'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Left Vertical Center'   : '(PPP 0)', 
            'Top Center'             : '(PPP 1)', 
            'Right Vertical Center'  : '(PPP 2)', 
            'Bottom Center'          : '(PPP 3)', 
            'Bottom Right'           : '(PPP 4)', 
            'Bottom Left'            : '(PPP 5)', 
            'Top Left'               : '(PPP 6)', 
            'Top Right'              : '(PPP 7)'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = '(PPP ?)'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            '0' : 'Left Vertical Center', 
            '1' : 'Top Center', 
            '2' : 'Right Vertical Center', 
            '3' : 'Bottom Center', 
            '4' : 'Bottom Right', 
            '5' : 'Bottom Left', 
            '6' : 'Top Left', 
            '7' : 'Top Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small'  : '(PHS 0)', 
            'Medium' : '(PHS 1)', 
            'Large'  : '(PHS 2)'
        }

        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = '(PHS ?)'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '0' : 'Small', 
            '1' : 'Medium', 
            '2' : 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '(PPS)'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(PWR 1)', 
            'Off' : '(PWR 0)'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        
        PowerCmdString = '(PWR ?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '(SHU 1)', 
            'Off' : '(SHU 0)'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '(SHU ?)'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
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

        self.Error(['Error Occurred!!!'])

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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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