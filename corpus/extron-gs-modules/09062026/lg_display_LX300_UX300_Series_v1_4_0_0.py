from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface
import re
from extronlib.system import Wait

class DeviceClass:

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
        self.Debug = False
        self.Models = {}
        self._displayID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DMode': {'Parameters': ['Option', 'Direction', '3D Effect'], 'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ChannelKeypad': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK(01|02|04|06|09|10|11|12|13|14|15|16|17|18|19|1a|1b|1c|1d|1e|1f)x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK(00|01|10|11|20|40|60|90|91)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK0(1|0)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-fA-F]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(j|c|e|m|b|l|a|d|f|t) [0-9a-f]{2} NG(.*)x', re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')

    @property
    def DisplayID(self):
        return self._displayID

    @DisplayID.setter
    def DisplayID(self, value):
        if 1 <= int(value) <= 99:
            self._displayID = '{0:02X}'.format(int(value))
        else:
            print('Invalid DeviceID number, range is from 1 to 99')
       

    def Set3DMode(self, value, qualifier):

        OptionStates = {
            'Top and Bottom': '00',
            'Side by Side': '01',
            'Check Board': '02',
            'Frame Sequential': '03',
            'Column Interleaving': '04',
            'Row Interleaving': '05'
        }

        DirectionStates = {
            'Right to Left': '00',
            'Left to Right': '01'
        }

        ValueStateValues = {
            '3D On': '00',
            '3D Off': '01',
            '3D to 2D': '02',
            '2D to 3D': '03'
        }

        if 0 <= qualifier['3D Effect'] <= 20:
            effect = qualifier['3D Effect']
            ModeCmdString = 'xt {0} {1} {2} {3} {4:02X}\r'.format(self._displayID, ValueStateValues[value], OptionStates[qualifier['Option']], DirectionStates[qualifier['Direction']], effect)
            self.__SetHelper('3DMode', ModeCmdString, value, qualifier)
        else:
            print('Invalid Command for Set3DMode')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Set by Program': '06',
            'Just Scan': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1A',
            'Cinema Zoom 12': '1B',
            'Cinema Zoom 13': '1C',
            'Cinema Zoom 14': '1D',
            'Cinema Zoom 15': '1E',
            'Cinema Zoom 16': '1F'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = 'kc {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ValueStateValues = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Set by Program',
            '09': 'Just Scan',
            '10': 'Cinema Zoom 1',
            '11': 'Cinema Zoom 2',
            '12': 'Cinema Zoom 3',
            '13': 'Cinema Zoom 4',
            '14': 'Cinema Zoom 5',
            '15': 'Cinema Zoom 6',
            '16': 'Cinema Zoom 7',
            '17': 'Cinema Zoom 8',
            '18': 'Cinema Zoom 9',
            '19': 'Cinema Zoom 10',
            '1a': 'Cinema Zoom 11',
            '1b': 'Cinema Zoom 12',
            '1c': 'Cinema Zoom 13',
            '1d': 'Cinema Zoom 14',
            '1e': 'Cinema Zoom 15',
            '1f': 'Cinema Zoom 16'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        AudioMuteCmdString = 'ke {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'ju {0} 01\r'.format(int(self._displayID))
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannelKeypad(self, value, qualifier):
        ValueStateValues = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10',
            '-': '4C'
        }

        ChannelKeypadCmdString = 'mc {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('ChannelKeypad', ChannelKeypadCmdString, value, qualifier)

    def SetChannelStep(self, value, qualifier):
        ValueStateValues = {
            'Up': '00',
            'Down': '01'
        }

        ChannelStepCmdString = 'mc {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):
        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ExecutiveModeCmdString = 'km {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'Cable DTV': '01',
            'Cable TV': '11',
            'AV': '20',
            'Component': '40',
            'RGB': '60',
            'HDMI 1': '90',
            'HDMI 2': '91',
            'DTV': '00',
            'TV': '10'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        InputCmdString = 'xb {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ValueStateValues = {
            '01': 'Cable DTV',
            '11': 'Cable TV',
            '20': 'AV',
            '40': 'Component',
            '60': 'RGB',
            '90': 'HDMI 1',
            '91': 'HDMI 2',
            '00': 'DTV',
            '10': 'TV'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Menu': '43',
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'OK': '44',
            'Back': '28',
            'Exit': '5B'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        OnScreenDisplayCmdString = 'kl {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayCmdString = 'kl {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        PowerCmdString = 'ka {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self._displayID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteCmdString = 'kd {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02x}\r'.format(self._displayID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'kf {0} FF\r'.format(self._displayID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1), 16)
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'OK' in response:
            return response
        elif 'NG' in response:
            err = 'Error in command: {0}'.format(sourceCmdName)
            print(err)
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, 0.3, deliRex=self.regexSet)
            if not res:
                print('No resposne or Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        State = {
            't': '3D Mode',
            'j': 'Auto Image',
            'c': 'Aspect Ratio',
            'e': 'Audio Mute',
            'm': 'Executive Mode',
            'b': 'Input',
            'l': 'On Screen Display',
            'a': 'Power',
            'd': 'Video Mute',
            'f': 'Volume'
            }

        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1, temp2)
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
