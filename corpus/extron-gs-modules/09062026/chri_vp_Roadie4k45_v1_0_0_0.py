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
        self._ReceiveBuffer = b''
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
            'LampMode': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(CHA!L001 001 000(01|02|03|11|12|21|22|23|24) '), self.__MatchChannel, None)
            self.AddMatchString(re.compile(b'\(HIS!0000(0|1|2) ".*?" ".*?" ".*?" [0-9]{5} [0-9]{5} [0-9]{5} [0-9]{5} ([0-9]{5})\)'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\(PWR!0(00|01|10|11) '), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!0000(0|1) '), self.__MatchVideoMute, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(ASU)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Four-Port (slot 1,2)': '(CHA 1)',
            'Four-Port (slot 3,4)': '(CHA 2)',
            'Four-Port (slot 1,2,3,4)': '(CHA 3)',
            'Two-Port (slot 1,2)': '(CHA 11)',
            'Two-Port (slot 3,4)': '(CHA 12)',
            'One-Port (slot 1)': '(CHA 21)',
            'One-Port (slot 2)': '(CHA 22)',
            'One-Port (slot 3)': '(CHA 23)',
            'One-Port (slot 4)': '(CHA 24)'
            }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = '(CHA?L)'
        self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)

    def __MatchChannel(self, match, tag):

        ChannelState = {
            '01': 'Four-Port (slot 1,2)',
            '02': 'Four-Port (slot 3,4)',
            '03': 'Four-Port (slot 1,2,3,4)',
            '11': 'Two-Port (slot 1,2)',
            '12': 'Two-Port (slot 3,4)',
            '21': 'One-Port (slot 1)',
            '22': 'One-Port (slot 2)',
            '23': 'One-Port (slot 3)',
            '24': 'One-Port (slot 4)'
            }

        value = ChannelState[match.group(1).decode()]
        self.WriteStatus('Channel', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': '(FRZ 1)',
            'Off': '(FRZ 0)'
            }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Constant Power': '(LPM 0)',
            'Constant Intensity': '(LPM 1)'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '(HIS?)'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        LampState = {
            '0': '1',
            '1': '2',
            '2': '3'
            }

        LampValue = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, {'Lamp': LampState[LampValue]})

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '(PWR 1)',
            'Off': '(PWR 0)',
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '01': 'On',
            '00': 'Off',
            '11': 'Warming Up',
            '10': 'Cooling Down'
            }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '(SHU 1)',
            'Off': '(SHU 0)'
            }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '(SHU?)'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            '1': 'On',
            '0': 'Off'
            }

        value = VideoMuteState[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
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
