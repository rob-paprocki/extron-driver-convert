from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'KeyLock': {'Parameters': ['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPPosition': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSwap': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])ASP(\x00|\x01|\x02|\x03)\x08\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])MIN(\x00|\x01|\x09|\x0A|\x0D|\x0E)\x08\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])KLC(\x01|\x00)\x08\r'), self.__MatchKeyLock, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])PIN(\x00|\x01|\x09|\x0A|\x0D|\x0E)\x08\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])PPO(\x00|\x01|\x02|\x03)\x08\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])PSC(\x00|\x01|\x02|\x03|\x04)\x08\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])POW(\x01|\x00)\x08\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])VWS(\x01|\x00)\x08\r'), self.__MatchVideoWall, None)

    def SetDeviceID(self, ID):
        if ID == 'Broadcast':
            DeviceID = b'\x00'
        elif 1 <= int(ID) <= 25:
            DeviceID = pack('>B', int(ID))
        else:
            DeviceID = ''
        return DeviceID

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Native': b'\x00',
            'Fullscreen': b'\x01',
            '4:3': b'\x02',
            'Letterbox': b'\x03'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            AspectRatioCmdString = b'\x07' + DeviceID + b'\x02ASP' + AspectRatioState[value] + b'\x08\r'
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            AspectRatioCmdString = b'\x07' + DeviceID + b'\x01ASP\x08\r'
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '\x00': 'Native',
            '\x01': 'Fullscreen',
            '\x02': '4:3',
            '\x03': 'Letterbox'
        }

        deviceID = ord(match.group(1).decode())
        value = AspectRatioState[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Device ID': str(deviceID)})

    def SetAutoImage(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            AutoImageCmdString = b'\x07' + DeviceID + b'\x02ADJ\x00\x08\r'
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': b'\x00',
            'Digital DVI': b'\x01',
            'HDMI 1': b'\x09',
            'HDMI 2': b'\x0A',
            'DisplayPort': b'\x0D',
            'OPS': b'\x0E'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            InputCmdString = b'\x07' + DeviceID + b'\x02MIN' + InputState[value] + b'\x08\r'
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            InputCmdString = b'\x07' + DeviceID + b'\x01MIN\x08\r'
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        InputState = {
            '\x00': 'VGA',
            '\x01': 'Digital DVI',
            '\x09': 'HDMI 1',
            '\x0A': 'HDMI 2',
            '\x0D': 'DisplayPort',
            '\x0E': 'OPS'
        }
        deviceID = ord(match.group(1).decode())
        value = InputState[match.group(2).decode()]
        self.WriteStatus('Input', value, {'Device ID': str(deviceID)})

    def SetKeyLock(self, value, qualifier):

        KeyLockState = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            KeyLockCmdString = b'\x07' + DeviceID + b'\x02KLC' + KeyLockState[value] + b'\x08\r'
            self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeyLock')

    def UpdateKeyLock(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            KeyLockCmdString = b'\x07' + DeviceID + b'\x01KLC\x08\r'
            self.__UpdateHelper('KeyLock', KeyLockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateKeyLock')

    def __MatchKeyLock(self, match, tag):

        KeyLockState = {
            '\x01': 'On',
            '\x00': 'Off'
        }
        deviceID = ord(match.group(1).decode())
        value = KeyLockState[match.group(2).decode()]
        self.WriteStatus('KeyLock', value, {'Device ID': str(deviceID)})

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Left': b'\x04',
            'Right': b'\x05',
            'Enter': b'\x06',
            'Exit': b'\x07',
            'Menu': b'\x00'
        }

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            MenuNavigationCmdString = b'\x07' + DeviceID + b'\x02RCU' + MenuNavigationState[value] + b'\x08\r'
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
            'VGA': b'\x00',
            'Digital DVI': b'\x01',
            'HDMI 1': b'\x09',
            'HDMI 2': b'\x0A',
            'DisplayPort': b'\x0D',
            'OPS': b'\x0E'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPInputCmdString = b'\x07' + DeviceID + b'\x02PIN' + PIPInputState[value] + b'\x08\r'
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPInputCmdString = b'\x07' + DeviceID + b'\x01PIN\x08\r'
            self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPInput')

    def __MatchPIPInput(self, match, tag):

        PIPInputState = {
            '\x00': 'VGA',
            '\x01': 'Digital DVI',
            '\x09': 'HDMI 1',
            '\x0A': 'HDMI 2',
            '\x0D': 'DisplayPort',
            '\x0E': 'OPS'
        }
        deviceID = ord(match.group(1).decode())
        value = PIPInputState[match.group(2).decode()]
        self.WriteStatus('PIPInput', value, {'Device ID': str(deviceID)})

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Bottom Left': b'\x00',
            'Bottom Right': b'\x01',
            'Top Left': b'\x02',
            'Top Right': b'\x03'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPPositionCmdString = b'\x07' + DeviceID + b'\x02PPO' + PIPPositionState[value] + b'\x08\r'
            self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def UpdatePIPPosition(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPPositionCmdString = b'\x07' + DeviceID + b'\x01PPO\x08\r'
            self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPPosition')

    def __MatchPIPPosition(self, match, tag):

        PIPPositionState = {
            '\x00': 'Bottom Left',
            '\x01': 'Bottom Right',
            '\x02': 'Top Left',
            '\x03': 'Top Right'
        }
        deviceID = ord(match.group(1).decode())
        value = PIPPositionState[match.group(2).decode()]
        self.WriteStatus('PIPPosition', value, {'Device ID': str(deviceID)})

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
            'Off': b'\x00',
            'Small': b'\x01',
            'Medium': b'\x02',
            'Large': b'\x03',
            'Side by Side': b'\x04'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPSizeCmdString = b'\x07' + DeviceID + b'\x02PSC' + PIPSizeState[value] + b'\x08\r'
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPSizeCmdString = b'\x07' + DeviceID + b'\x01PSC\x08\r'
            self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPSize')

    def __MatchPIPSize(self, match, tag):

        PIPSizeState = {
            '\x00': 'Off',
            '\x01': 'Small',
            '\x02': 'Medium',
            '\x03': 'Large',
            '\x04': 'Side by Side'
        }
        deviceID = ord(match.group(1).decode())
        value = PIPSizeState[match.group(2).decode()]
        self.WriteStatus('PIPSize', value, {'Device ID': str(deviceID)})

    def SetPIPSwap(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PIPSwapCmdString = b'\x07' + DeviceID + b'\x02SWA\x00\x08\r'
            self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSwap')

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PowerCmdString = b'\x07' + DeviceID + b'\x02POW' + PowerState[value] + b'\x08\r'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            PowerCmdString = b'\x07' + DeviceID + b'\x01POW\x08\r'
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        PowerState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        deviceID = ord(match.group(1).decode())
        value = PowerState[match.group(2).decode()]

        if 1 <= int(deviceID) <= 25:
            self.WriteStatus('Power', value, {'Device ID': str(deviceID)})
        else:
            self.Error(['Invalid Response'])

    def SetVideoWall(self, value, qualifier):

        VideoWallState = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            VideoWallCmdString = b'\x07' + DeviceID + b'\x02VWS' + VideoWallState[value] + b'\x08\r'
            self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWall')

    def UpdateVideoWall(self, value, qualifier):

        ID = qualifier['Device ID']
        DeviceID = self.SetDeviceID(ID)
        if DeviceID:
            VideoWallCmdString = b'\x07' + DeviceID + b'\x01VWS\x08\r'
            self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWall')

    def __MatchVideoWall(self, match, tag):

        VideoWallState = {
            '\x01': 'On',
            '\x00': 'Off'
        }
        deviceID = ord(match.group(1).decode())
        value = VideoWallState[match.group(2).decode()]
        self.WriteStatus('VideoWall', value, {'Device ID': str(deviceID)})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}
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
        self._DeviceID = b'\x01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'KeyLock': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoWall': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]ASP(\x00|\x01|\x02|\x03)\x08\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]MIN(\x00|\x01|\x09|\x0A|\x0D|\x0E)\x08\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]KLC(\x01|\x00)\x08\r'), self.__MatchKeyLock, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]PIN(\x00|\x01|\x09|\x0A|\x0D|\x0E)\x08\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]PPO(\x00|\x01|\x02|\x03)\x08\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]PSC(\x00|\x01|\x02|\x03|\x04)\x08\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]POW(\x01|\x00)\x08\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]VWS(\x01|\x00)\x08\r'), self.__MatchVideoWall, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x00'
        elif 1 <= int(value) <= 25:
            self._DeviceID = pack('>B', int(value))
        else:
            self.Error(['Device ID should be between 1 to 25 or Broadcast'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Native': b'\x00',
            'Fullscreen': b'\x01',
            '4:3': b'\x02',
            'Letterbox': b'\x03'
        }

        AspectRatioCmdString = b'\x07' + self._DeviceID + b'\x02ASP' + AspectRatioState[value] + b'\x08\r'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x07' + self._DeviceID + b'\x01ASP\x08\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '\x00': 'Native',
            '\x01': 'Fullscreen',
            '\x02': '4:3',
            '\x03': 'Letterbox'
        }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x07' + self._DeviceID + b'\x02ADJ\x00\x08\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': b'\x00',
            'Digital DVI': b'\x01',
            'HDMI 1': b'\x09',
            'HDMI 2': b'\x0A',
            'DisplayPort': b'\x0D',
            'OPS': b'\x0E'
        }

        InputCmdString = b'\x07' + self._DeviceID + b'\x02MIN' + InputState[value] + b'\x08\r'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x07' + self._DeviceID + b'\x01MIN\x08\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputState = {
            '\x00': 'VGA',
            '\x01': 'Digital DVI',
            '\x09': 'HDMI 1',
            '\x0A': 'HDMI 2',
            '\x0D': 'DisplayPort',
            '\x0E': 'OPS'
        }

        value = InputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeyLock(self, value, qualifier):

        KeyLockState = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        KeyLockCmdString = b'\x07' + self._DeviceID + b'\x02KLC' + KeyLockState[value] + b'\x08\r'
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def UpdateKeyLock(self, value, qualifier):

        KeyLockCmdString = b'\x07' + self._DeviceID + b'\x01KLC\x08\r'
        self.__UpdateHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def __MatchKeyLock(self, match, tag):

        KeyLockState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = KeyLockState[match.group(1).decode()]
        self.WriteStatus('KeyLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x02',
            'Down': b'\x03',
            'Left': b'\x04',
            'Right': b'\x05',
            'Enter': b'\x06',
            'Exit': b'\x07',
            'Menu': b'\x00'
        }

        MenuNavigationCmdString = b'\x07' + self._DeviceID + b'\x02RCU' + MenuNavigationState[value] + b'\x08\r'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
            'VGA': b'\x00',
            'Digital DVI': b'\x01',
            'HDMI 1': b'\x09',
            'HDMI 2': b'\x0A',
            'DisplayPort': b'\x0D',
            'OPS': b'\x0E'
        }

        PIPInputCmdString = b'\x07' + self._DeviceID + b'\x02PIN' + PIPInputState[value] + b'\x08\r'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = b'\x07' + self._DeviceID + b'\x01PIN\x08\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        PIPInputState = {
            '\x00': 'VGA',
            '\x01': 'Digital DVI',
            '\x09': 'HDMI 1',
            '\x0A': 'HDMI 2',
            '\x0D': 'DisplayPort',
            '\x0E': 'OPS'
        }

        value = PIPInputState[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Bottom Left': b'\x00',
            'Bottom Right': b'\x01',
            'Top Left': b'\x02',
            'Top Right': b'\x03'
        }

        PIPPositionCmdString = b'\x07' + self._DeviceID + b'\x02PPO' + PIPPositionState[value] + b'\x08\r'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = b'\x07' + self._DeviceID + b'\x01PPO\x08\r'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        PIPPositionState = {
            '\x00': 'Bottom Left',
            '\x01': 'Bottom Right',
            '\x02': 'Top Left',
            '\x03': 'Top Right'
        }

        value = PIPPositionState[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
            'Off': b'\x00',
            'Small': b'\x01',
            'Medium': b'\x02',
            'Large': b'\x03',
            'Side by Side': b'\x04'
        }

        PIPSizeCmdString = b'\x07' + self._DeviceID + b'\x02PSC' + PIPSizeState[value] + b'\x08\r'
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = b'\x07' + self._DeviceID + b'\x01PSC\x08\r'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        PIPSizeState = {
            '\x00': 'Off',
            '\x01': 'Small',
            '\x02': 'Medium',
            '\x03': 'Large',
            '\x04': 'Side by Side'
        }

        value = PIPSizeState[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b'\x07' + self._DeviceID + b'\x02SWA\x00\x08\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b'\x07' + self._DeviceID + b'\x02POW' + PowerState[value] + b'\x08\r'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x07' + self._DeviceID + b'\x01POW\x08\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoWall(self, value, qualifier):

        VideoWallState = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoWallCmdString = b'\x07' + self._DeviceID + b'\x02VWS' + VideoWallState[value] + b'\x08\r'
        self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):

        VideoWallCmdString = b'\x07' + self._DeviceID + b'\x01VWS\x08\r'
        self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        VideoWallState = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = VideoWallState[match.group(1).decode()]
        self.WriteStatus('VideoWall', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\x00':
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}
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
    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
