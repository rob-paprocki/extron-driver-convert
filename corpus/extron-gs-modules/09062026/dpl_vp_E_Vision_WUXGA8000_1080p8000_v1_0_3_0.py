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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Info': {'Status': {}},
            'Input': {'Status': {}},
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LampControl': {'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Model': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'SerialNumber': {'Status': {}},
            'SoftwareVersion': {'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT = ([0-8])\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'INPUT\.SEL = ([0-6])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LAMP([1-2]).STAT = ([01])\r'), self.__MatchLampStatus, None)
            self.AddMatchString(re.compile(b'LAMP([1-2]).HOURS = ([0-9]{1,5})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'LAMPS = ([0-1])\r'), self.__MatchLampControl, None)
            self.AddMatchString(re.compile(b'LAMP\.MODE = ([0-2])\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'MODEL = ([a-zA-Z0-9_ -.]+)\r'), self.__MatchModel, None)
            self.AddMatchString(re.compile(b'PROJ\.RUNTIME = ([0-9]{1,5})\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'PIP\.SEL = ([1-7])\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'PIP = ([01])\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'PIP\.POS = ([0-4])\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'STATUS = ([0-4])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'SER\.NO = ([a-zA-Z0-9_ -.]+)\r'), self.__MatchSerialNumber, None)
            self.AddMatchString(re.compile(b'SW\.VER = ([a-zA-Z0-9_ -.]+)\r'), self.__MatchSoftwareVersion, None)
            self.AddMatchString(re.compile(b'PICTURE\.MUTE = ([01])\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'ZOOM = ([0-2])\r'), self.__MatchZoom, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            '5:4': 'op aspect = 0\r',
            '4:3': 'op aspect = 1\r',
            '16:10': 'op aspect = 2\r',
            '16:9': 'op aspect = 3\r',
            '1.88': 'op aspect = 4\r',
            '2.35:1': 'op aspect = 5\r',
            'Letterbox': 'op aspect = 6\r',
            'Native': 'op aspect = 7\r',
            'Unscaled': 'op aspect = 8\r',
            }
        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'op aspect ?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, qualifier):

        AspectRatioStateNames = {
            '0': '5:4',
            '1': '4:3',
            '2': '16:10',
            '3': '16:9',
            '4': '1.88',
            '5': '2.35:1',
            '6': 'Letterbox',
            '7': 'Native',
            '8': 'Unscaled',
           }
        value = AspectRatioStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'op auto.img\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'ky freeze\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInfo(self, value, qualifier):

        InfoCmdString = 'ky info\r'
        self.__SetHelper('Info', InfoCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'HDMI': 'op input.sel = 0\r',
            'DVI': 'op input.sel = 1\r',
            'VGA': 'op input.sel = 2\r',
            'Component': 'op input.sel = 3\r',
            'Composite': 'op input.sel = 4\r',
            'S-Video': 'op input.sel = 5\r',
            '3G-SDI': 'op input.sel = 6\r',
            }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'op input.sel ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        InputStateNames = {
            '0': 'HDMI',
            '1': 'DVI',
            '2': 'VGA',
            '3': 'Component',
            '4': 'Composite',
            '5': 'S-Video',
            '6': '3G-SDI',
           }
        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampStatus(self, value, qualifier):

        lamp = int(qualifier['Lamp'])
        if lamp in [1, 2]:
            LampStatusCmdString = 'op lamp{0}.stat ?\r'.format(lamp)
            self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateLampStatus')

    def __MatchLampStatus(self, match, qualifier):

        LampStatusStateNames = {
            '1': 'On',
            '0': 'Off',
           }
        lamp = match.group(1).decode()
        value = LampStatusStateNames[match.group(2).decode()]
        self.WriteStatus('LampStatus', value, {'Lamp': lamp})

    def UpdateLampUsage(self, value, qualifier):

        lamp = int(qualifier['Lamp'])
        if lamp in [1, 2]:
            LampUsageCmdString = 'op lamp{0}.hours ?\r'.format(lamp)
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, tag):

        lamp = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, {'Lamp': lamp})

    def SetLampControl(self, value, qualifier):

        LampControlStateValues = {
            'Single': 'op lamps = 0\r',
            'Double': 'op lamps = 1\r',
            }
        LampControlCmdString = LampControlStateValues[value]
        self.__SetHelper('LampControl', LampControlCmdString, value, qualifier)

    def UpdateLampControl(self, value, qualifier):

        LampControlCmdString = 'op lamps ?\r'
        self.__UpdateHelper('LampControl', LampControlCmdString, value, qualifier)

    def __MatchLampControl(self, match, qualifier):

        LampControlStateNames = {
            '0': 'Single',
            '1': 'Double',
           }
        value = LampControlStateNames[match.group(1).decode()]
        self.WriteStatus('LampControl', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Standard': 'op lamp.mode = 1\r',
            'Dimming': 'op lamp.mode = 2\r',
            'Economy': 'op lamp.mode = 0\r',
            }
        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'op lamp.mode ?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, qualifier):

        LampModeStateNames = {
            '1': 'Standard',
            '2': 'Dimming',
            '0': 'Economy',
           }
        value = LampModeStateNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'ky menu\r',
            'Exit': 'ky exit\r',
            'Enter': 'ky enter\r',
            'Up': 'ky up\r',
            'Down': 'ky down\r',
            'Left': 'ky left\r',
            'Right': 'ky right\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateModel(self, value, qualifier):

        ModelCmdString = 'op model ?\r'
        self.__UpdateHelper('Model', ModelCmdString, value, qualifier)

    def __MatchModel(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Model', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'op proj.runtime ?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, qualifier):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputStateValues = {
            'HDMI': 'op pip.sel = 1\r',
            'DVI': 'op pip.sel = 2\r',
            'VGA': 'op pip.sel = 3\r',
            'Component': 'op pip.sel = 4\r',
            'Composite': 'op pip.sel = 5\r',
            'S-Video': 'op pip.sel = 6\r',
            '3G-SDI': 'op pip.sel = 7\r',
            }
        PIPInputCmdString = PIPInputStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = 'op pip.sel ?\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, qualifier):

        PIPInputStateNames = {
            '1': 'HDMI',
            '2': 'DVI',
            '3': 'VGA',
            '4': 'Component',
            '5': 'Composite',
            '6': 'S-Video',
            '7': '3G-SDI',
           }
        value = PIPInputStateNames[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPModeStateValues = {
            'On': 'op pip = 1\r',
            'Off': 'op pip = 0\r',
            }
        PIPModeCmdString = PIPModeStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = b'op pip ?\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, qualifier):

        PIPModeStateNames = {
            '1': 'On',
            '0': 'Off',
           }
        value = PIPModeStateNames[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionStateValues = {
            'Top Left': 'op pip.pos = 0\r',
            'Top Right': 'op pip.pos = 1\r',
            'Bottom Left': 'op pip.pos = 2\r',
            'Bottom Right': 'op pip.pos = 3\r',
            'Split L-R': 'op pip.pos = 4\r',
            }
        PIPPositionCmdString = PIPPositionStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = 'op pip.pos ?\r'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, qualifier):

        PIPPositionStateNames = {
            '0': 'Top Left',
            '1': 'Top Right',
            '2': 'Bottom Left',
            '3': 'Bottom Right',
            '4': 'Split L-R',
           }
        value = PIPPositionStateNames[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'op pip.swap\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': 'op power.off\r',
            'On': 'op power.on\r',
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'op status ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, qualifier):

        PowerStateNames = {
            '0': 'Off',
            '1': 'Warm Up',
            '2': 'On',
            '3': 'Cooling',
            '4': 'Warning',
           }
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = 'op ser.no ?\r'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)

    def __MatchSerialNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SerialNumber', value, None)

    def UpdateSoftwareVersion(self, value, qualifier):

        SoftwareVersionCmdString = 'op sw.ver ?\r'
        self.__UpdateHelper('SoftwareVersion', SoftwareVersionCmdString, value, qualifier)

    def __MatchSoftwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SoftwareVersion', value, None)

    def SetTestPattern(self, value, qualifier):

        TestPatternCmdString = 'ky testpattern\r'
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': 'op picture.mute = 1\r',
            'Off': 'op picture.mute = 0\r',
            }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'op picture.mute ?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteStateNames = {
            '1': 'On',
            '0': 'Off',
           }
        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'Zoom': 'op zoom = 2\r',
            'Crop': 'op zoom = 1\r',
            'Off': 'op zoom = 0\r',
            }
        ZoomCmdString = ZoomStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def UpdateZoom(self, value, qualifier):

        ZoomCmdString = 'op zoom ?\r'
        self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)

    def __MatchZoom(self, match, qualifier):

        ZoomStateNames = {
            '2': 'Zoom',
            '1': 'Crop',
            '0': 'Off',
           }
        value = ZoomStateNames[match.group(1).decode()]
        self.WriteStatus('Zoom', value, None)

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
