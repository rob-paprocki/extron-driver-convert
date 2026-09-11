from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
import time

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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(SZP!([0-8])\)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\(FRZ!(0|1)\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN\+MAIN!([0-9]{1,2})\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(LPM!([0-4])\)'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\(LIF\+LSHS!(\d+)\)'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\(OSD!(0|1)\)'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\(LIF\+LPHS!(\d+)\)'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\(SIN\+PIP!([0-9]{1,2})\)'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\(PIP!(0|1)\)'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\(PPP!([0-7])\)'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\(PHS!(0|1|2)\)'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\(PWR!(0|1)\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!(0|1)\)'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\(\d+ \d+ (ERR\d+ \".+\")\)'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '(SZP 0)',
            'Native': '(SZP 1)',
            '4:3': '(SZP 2)',
            'Letterbox': '(SZP 3)',
            'Full Size': '(SZP 4)',
            'Full Width': '(SZP 5)',
            'Full Height': '(SZP 6)',
            'Custom': '(SZP 7)',
            '3D Mode': '(SZP 8)'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '(SZP?)'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Native',
            '2': '4:3',
            '3': 'Letterbox',
            '4': 'Full Size',
            '5': 'Full Width',
            '6': 'Full Height',
            '7': 'Custom',
            '8': '3D Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Normal': '(AIM 0)',
            'Wide': '(AIM 1)'
        }

        AutoImageCmdString = ValueStateValues[value]
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '(FRZ 1)',
            'Off': '(FRZ 0)'
        }

        FreezeCmdString = ValueStateValues[value]
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
            'VGA': '(SIN+MAIN 1)',
            'HDMI 1': '(SIN+MAIN 3)',
            'HDMI 2': '(SIN+MAIN 4)',
            'DVI-D': '(SIN+MAIN 5)',
            '3G-SDI': '(SIN+MAIN 7)',
            'HDBaseT': '(SIN+MAIN 8)',
            'Presenter': '(SIN+MAIN 10)',
            'Card Reader': '(SIN+MAIN 11)',
            'Mini USB': '(SIN+MAIN 12)'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN+MAIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            1: 'VGA',
            3: 'HDMI 1',
            4: 'HDMI 2',
            5: 'DVI-D',
            7: '3G-SDI',
            8: 'HDBaseT',
            10: 'Presenter',
            11: 'Card Reader',
            12: 'Mini USB'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '(KEY 36)',
            '1': '(KEY 26)',
            '2': '(KEY 27)',
            '3': '(KEY 28)',
            '4': '(KEY 29)',
            '5': '(KEY 30)',
            '6': '(KEY 31)',
            '7': '(KEY 32)',
            '8': '(KEY 33)',
            '9': '(KEY 34)'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Constant Power': '(LPM 0)',
            'Constant Intensity': '(LPM 1)',
            'ECO 1': '(LPM 2)',
            'ECO 2': '(LPM 3)',
            'Rental Mode': '(LPM 4)'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '(LPM?)'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '0': 'Constant Power',
            '1': 'Constant Intensity',
            '2': 'ECO 1',
            '3': 'ECO 2',
            '4': 'Rental Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '(LIF+LSHS?)'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '(KEY 38)',
            'Down': '(KEY 42)',
            'Left': '(KEY 39)',
            'Right': '(KEY 41)',
            'Enter': '(KEY 40)',
            'Exit': '(KEY 20)',
            'Menu': '(KEY 19)'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '(OSD 1)',
            'Off': '(OSD 0)'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
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

        OperationHoursCmdString = '(LIF+LPHS?)'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '(SIN+PIP 1)',
            'HDMI 1': '(SIN+PIP 3)',
            'HDMI 2': '(SIN+PIP 4)',
            'DVI-D': '(SIN+PIP 5)',
            '3G-SDI': '(SIN+PIP 7)',
            'HDBaseT': '(SIN+PIP 8)',
            'Presenter': '(SIN+PIP 10)',
            'Card Reader': '(SIN+PIP 11)',
            'Mini USB': '(SIN+PIP 12)'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '(SIN+PIP?)'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            1: 'VGA',
            3: 'HDMI 1',
            4: 'HDMI 2',
            5: 'DVI-D',
            7: '3G-SDI',
            8: 'HDBaseT',
            10: 'Presenter',
            11: 'Card Reader',
            12: 'Mini USB'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '(PIP 1)',
            'Off': '(PIP 0)'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '(PIP?)'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Left Vertical Center': '(PPP 0)',
            'Top Center': '(PPP 1)',
            'Right Vertical Center': '(PPP 2)',
            'Bottom Center': '(PPP 3)',
            'Bottom Right': '(PPP 4)',
            'Bottom Left': '(PPP 5)',
            'Top Left': '(PPP 6)',
            'Top Right': '(PPP 7)'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = '(PPP?)'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            '0': 'Left Vertical Center',
            '1': 'Top Center',
            '2': 'Right Vertical Center',
            '3': 'Bottom Center',
            '4': 'Bottom Right',
            '5': 'Bottom Left',
            '6': 'Top Left',
            '7': 'Top Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '(PHS 0)',
            'Medium': '(PHS 1)',
            'Large': '(PHS 2)'
        }

        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = '(PHS?)'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '(PPS)'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': '(PWR 0)',
            'On': '(PWR 1)'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            0: 'Off',
            1: 'On'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '(SHU 1)',
            'Off': '(SHU 0)'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '(SHU?)'
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
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        print('There was an error in the device response: ' + match.group(1).decode())


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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
