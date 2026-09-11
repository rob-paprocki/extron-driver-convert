from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceSerialClass:

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
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'ButtonLock': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuLock': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'Mute': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PowerLock': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'80?([\w]+)rp00(0|1)\r'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'80?([\w]+)rj0(00|01|03|04|14|05|06|07|09)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'80?([\w]+)rq00(0|1)\r'), self.__MatchMenuLock, None)
            self.AddMatchString(re.compile(b'80?([\w]+)rg00(0|1)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'80?([\w]+)rl00(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'80?([\w]+)ro00(0|1)\r'), self.__MatchPowerLock, None)
            self.AddMatchString(re.compile(b'80?([\w]+)rf(\d{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'4[0-9]{2}-\r'), self.__MatchError, None)


    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return '00'
        elif 1 <= int(ID) <= 99:
            return '{0:02X}'.format(int(ID))
        else:
            self.Error(['Invalid Device ID provided'])

    # Aspect Ratio    
    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Full': '0',
            'Normal': '1',
            'Custom': '2',
            'Dynamic': '3',
            'Real': '4'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        AspectRatioCmdString = '8{0}s100{1}\r'.format(ID, AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    # Button Lock    
    def SetButtonLock(self, value, qualifier):

        ButtonLockState = {
            'On': '1',
            'Off': '0'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        ButtonLockCmdString = '8{0}s800{1}\r'.format(ID, ButtonLockState[value])
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        ButtonLockCmdString = '8{0}gp000\r'.format(ID)
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ButtonLockState = {
            '1': 'On',
            '0': 'Off'
            }

        value = ButtonLockState[match.group(2).decode()]
        self.WriteStatus('ButtonLock', value, {'Device ID': match.group(1).decode()})

    def SetInput(self, value, qualifier):

        InputState = {
            'TV': '00',
            'AV': '01',
            'YPbPr': '03',
            'HDMI 1': '04',
            'HDMI 2': '14',
            'DVI': '05',
            'VGA': '06',
            'OPS': '07',
            'DP': '09'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        InputCmdString = '8{0}s\x220{1}\r'.format(ID, InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        InputCmdString = '8{0}gj000\r'.format(ID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '00': 'TV',
            '01': 'AV',
            '03': 'YPbPr',
            '04': 'HDMI 1',
            '14': 'HDMI 2',
            '05': 'DVI',
            '06': 'VGA',
            '07': 'OPS',
            '09': 'DP'
            }

        value = InputState[match.group(2).decode()]
        self.WriteStatus('Input', value, {'Device ID': match.group(1).decode()})

    def SetMenuLock(self, value, qualifier):

        MenuLockState = {
            'On': '1',
            'Off': '0'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        MenuLockCmdString = '8{0}s\x3E00{1}\r'.format(ID, MenuLockState[value])
        self.__SetHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def UpdateMenuLock(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        MenuLockCmdString = '8{0}gq000\r'.format(ID)
        self.__UpdateHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def __MatchMenuLock(self, match, tag):

        MenuLockState = {
            '1': 'On',
            '0': 'Off'
            }

        value = MenuLockState[match.group(2).decode()]
        self.WriteStatus('MenuLock', value, {'Device ID': match.group(1).decode()})

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': '0',
            'Down': '1',
            'Left': '2',
            'Right': '3',
            'Enter': '4',
            'Input': '5',
            'Menu/Exit': '6'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        MenuNavigationCmdString = '8{0}sA00{1}\r'.format(ID, MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    # Mute    
    def SetMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        MuteCmdString = '8{0}s600{1}\r'.format(ID, MuteState[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        MuteCmdString = '8{0}gg000\r'.format(ID)
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        MuteState = {
            '1': 'On',
            '0': 'Off'
            }

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('Mute', value, {'Device ID': match.group(1).decode()})


    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '1',
            'Off': '0'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        PowerCmdString = '8{0}s\x2100{1}\r'.format(ID, PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        PowerCmdString = '8{0}gl000\r'.format(ID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '1': 'On',
            '0': 'Off'
            }

        ID = match.group(1).decode()
        value = PowerState[match.group(2).decode()]
        self.WriteStatus('Power', value, {'Device ID': str(ID)})

    def SetPowerLock(self, value, qualifier):

        PowerLockState = {
            'On': '1',
            'Off': '0'
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        PowerLockCmdString = '8{0}s400{1}\r'.format(ID, PowerLockState[value])
        self.__SetHelper('PowerLock', PowerLockCmdString, value, qualifier)

    def UpdatePowerLock(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        PowerLockCmdString = '8{0}go000\r'.format(ID)
        self.__UpdateHelper('PowerLock', PowerLockCmdString, value, qualifier)

    def __MatchPowerLock(self, match, tag):

        PowerLockState = {
            '1': 'On',
            '0': 'Off'
            }

        value = PowerLockState[match.group(2).decode()]
        self.WriteStatus('PowerLock', value, {'Device ID': match.group(1).decode()})

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        ID = self.GetDeviceID(qualifier['Device ID'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '8{0}s5{1:03d}\r'.format(ID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        VolumeCmdString = '8{0}gf000\r'.format(ID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, {'Device ID': match.group(1).decode()})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif 'Broadcast' in [qualifier['Device ID']]:
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
        self.Error(['Device responded with an error message.'])

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


class DeviceEthernetClass:
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
        self._DeviceID = '01'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'ButtonLock': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuLock': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerLock': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'8[0-9]{2}rp00(0|1)\r'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rj0(00|01|03|04|14|05|06|07|09)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rq00(0|1)\r'), self.__MatchMenuLock, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rg00(0|1)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rl00(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}ro00(0|1)\r'), self.__MatchPowerLock, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rf(\d{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'4[0-9]{2}-\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            return '{0:02X}'.format(int(value))
        else:
            self.Error(['Invalid Device ID provided, range is from 1 to 98 or Broadcast'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Full' : '0', 
            'Normal' : '1', 
            'Custom' : '2', 
            'Dynamic' : '3', 
            'Real' : '4'
            }

        AspectRatioCmdString = '8{0}s100{1}\r'.format(self._DeviceID, AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetButtonLock(self, value, qualifier):

        ButtonLockState = {
            'On' : '1', 
            'Off' : '0'
            }

        ButtonLockCmdString = '8{0}s800{1}\r'.format(self._DeviceID, ButtonLockState[value])
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        ButtonLockCmdString = '8{0}gp000\r'.format(self._DeviceID)
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ButtonLockState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = ButtonLockState[match.group(1).decode()]
        self.WriteStatus('ButtonLock', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            'TV'    : '00', 
            'AV'    : '01', 
            'YPbPr' : '03', 
            'HDMI 1': '04', 
            'HDMI 2': '14', 
            'DVI'   : '05', 
            'VGA'   : '06', 
            'OPS'   : '07', 
            'DP'    : '09'
            }

        InputCmdString = '8{0}s\x220{1}\r'.format(self._DeviceID, InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '8{0}gj000\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '00' : 'TV', 
            '01' : 'AV', 
            '03' : 'YPbPr', 
            '04' : 'HDMI 1', 
            '14' : 'HDMI 2', 
            '05' : 'DVI', 
            '06' : 'VGA', 
            '07' : 'OPS', 
            '09' : 'DP'
            }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuLock(self, value, qualifier):

        MenuLockState = {
            'On' : '1', 
            'Off' : '0'
            }

        MenuLockCmdString = '8{0}s\x3E00{1}\r'.format(self._DeviceID, MenuLockState[value])
        self.__SetHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def UpdateMenuLock(self, value, qualifier):

        MenuLockCmdString = '8{0}gq000\r'.format(self._DeviceID)
        self.__UpdateHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def __MatchMenuLock(self, match, tag):

        MenuLockState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = MenuLockState[match.group(1).decode()]
        self.WriteStatus('MenuLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up' : '0', 
            'Down' : '1', 
            'Left' : '2', 
            'Right' : '3', 
            'Enter' : '4', 
            'Input' : '5', 
            'Menu/Exit' : '6'
            }

        MenuNavigationCmdString = '8{0}sA00{1}\r'.format(self._DeviceID, MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetMute(self, value, qualifier):

        MuteState = {
            'On' : '1', 
            'Off' : '0'
            }

        MuteCmdString = '8{0}s600{1}\r'.format(self._DeviceID, MuteState[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '8{0}gg000\r'.format(self._DeviceID)
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        MuteState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = MuteState[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On' : '1', 
            'Off' : '0'
            }

        PowerCmdString = '8{0}s\x2100{1}\r'.format(self._DeviceID, PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '8{0}gl000\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '1' : 'On', 
            '0' : 'Off'
            }


        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPowerLock(self, value, qualifier):

        PowerLockState = {
            'On' : '1', 
            'Off' : '0'
            }

        PowerLockCmdString = '8{0}s400{1}\r'.format(self._DeviceID, PowerLockState[value])
        self.__SetHelper('PowerLock', PowerLockCmdString, value, qualifier)
        
    def UpdatePowerLock(self, value, qualifier):
        PowerLockCmdString = '8{0}go000\r'.format(self._DeviceID)
        self.__UpdateHelper('PowerLock', PowerLockCmdString, value, qualifier)

    def __MatchPowerLock(self, match, tag):

        PowerLockState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = PowerLockState[match.group(1).decode()]
        self.WriteStatus('PowerLock', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '8{0}s5{1:03d}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '8{0}gf000\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '99':
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
        self.Error(['Device responded with an error message.'])

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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
