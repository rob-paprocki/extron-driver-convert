from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}}
            }

        initError = []

        if self.Unidirectional == 'False':  # include echo
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#\r\n', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*asp=(4:3|anam|real|lbox|wide)#\r\n', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#\r\n', re.I), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#\r\n', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#\r\n', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|YPBR|HDMI|VID|RGB2|NETWORK|USBDISPLAY|USBREADER|HDMI2)#\r\n', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*LTI(M|M2)=([0-9]{1,5})#\r\n', re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(ECO|LNOR|DUALBR|DUALRE|SINGLE|SINGLEECO|SECO)#\r\n', re.I), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*VOL=([0-9]{1,2})#\r\n', re.I), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'Illegal format\r\n', re.I), self.__MatchError, None)  # command not accepted when in power off state
            self.AddMatchString(re.compile(b'Block item\r\n', re.I), self.__MatchError, None)  # command not accepted when powering On or powering off

    def SetAspectRatio(self, value, qualifier):
        AspectStateValues = {
            '4:3': '*asp=4:3#',
            'Anamorphic': '*asp=ANAM#',
            'Letterbox': '*asp=LBOX#',
            'Wide': '*asp=WIDE#',
            'Real': '*asp=REAL#',
            }
        AspectCmdString = AspectStateValues[value]
        self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectCmdString = '*asp=?#'
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        AspectStateNames = {
           '4:3': '4:3',
           'anam': 'Anamorphic',
           'lbox': 'Letterbox',
           'real': 'Real',
           'wide': 'Wide'
           }
        value = AspectStateNames[match.group(1).decode().lower()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):
        AudioMuteStateValues = {
            'On': '*mute=on#',
            'Off': '*mute=off#',
            }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '*mute=?#'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        AudioMuteStateNames = {
           'on': 'On',
           'off': 'Off',
           }
        value = AudioMuteStateNames[match.group(1).decode().lower()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = '*auto#'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetFreeze(self, value, qualifier):
        FreezeStateValues = {
            'On': '*freeze=on#',
            'Off': '*freeze=off#'
            }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '*freeze=?#'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):
        FreezeStateNames = {
           'on': 'On',
           'off': 'Off',
           }
        value = FreezeStateNames[match.group(1).decode().lower()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'Component': 'ypbr',
            'Composite': 'vid',
            'Network': 'network',
            'USB Reader': 'usbreader',
            'USB Display': 'usbdisplay',
            'Computer 1': 'RGB',
            'Computer 2': 'RGB2',
            'HDMI 1': 'hdmi',
            'HDMI 2': 'hdmi2'
        }

        InputCmdString = '*sour={0}#'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*sour=?#'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'hdmi': 'HDMI 1',
            'ypbr': 'Component',
            'vid': 'Composite',
            'network': 'Network',
            'usbreader': 'USB Reader',
            'usbdisplay': 'USB Display',
            'rgb': 'Computer 1',
            'rgb2': 'Computer 2',
            'hdmi2': 'HDMI 2'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'lnor',
            'Eco': 'eco',
            'Smart Eco': 'seco',
            'Dual Brightest': 'dualbr',
            'Dual Reliable': 'dualre',
            'Single Alternative': 'single',
            'Single Alternative Eco': 'singleeco'
        }

        LampModeCmdString = '*lampm={0}#'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '*lampm=?#'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):
        ValueStateValues = {
            'lnor': 'Normal',
            'eco': 'Eco',
            'seco': 'Smart Eco',
            'dualbr': 'Dual Brightest',
            'dualre': 'Dual Reliable',
            'single': 'Single Alternative',
            'singleeco': 'Single Alternative Eco'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if lamp == '1':
             LampUsageCmdString = '*ltim=?#'
        elif lamp == '2':
            LampUsageCmdString = '*ltim2=?#'
        else:
            print('Invalid Command for UpdateLampUsage')
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(2).decode())
        lamp = match.group(1).decode().lower()
        if lamp == 'm':
            qualifier = {'Lamp': '1'}
            self.WriteStatus('LampUsage', value, qualifier)
        elif lamp == 'm2':
            qualifier = {'Lamp': '2'}
            self.WriteStatus('LampUsage', value, qualifier)

    def SetMenuNavigation(self, value, qualifier):
        MenuNavigationStateValues = {
            'Up': '*up#',
            'Down': '*down#',
            'Left': '*left#',
            'Right': '*right#',
            'Enter': '*enter#',
            'Menu On': '*menu=on#',
            'Menu Off': '*menu=off#',
            }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetPower(self, value, qualifier):
        PowerStateValues = {
            'On': '*pow=on#',
            'Off': '*pow=off#',
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 20)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '*pow=?#'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        PowerStateNames = {
            'on': 'On',
            'off': 'Off',
            }
        value = PowerStateNames[match.group(1).decode().lower()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):
        VideoMuteStateValues = {
            'On': '*blank=on#',
            'Off': '*blank=off#'
            }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 2)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '*blank=?#'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        VideoMuteStateNames = {
           'on': 'On',
           'off': 'Off',
           }
        value = VideoMuteStateNames[match.group(1).decode().lower()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeStateValues = {
            'Up': '*vol=+#',
            'Down': '*vol=-#',
            }
        VolumeCmdString = VolumeStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = '*vol=?#'
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('VolumeStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send('\r' + commandstring + '\r')

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
            self.Send('\r' + commandstring + '\r')

    def __MatchError(self, match, tag):
        value = match.group(0).decode()
        print(value)

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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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
