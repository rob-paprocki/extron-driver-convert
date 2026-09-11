from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.cameraID = 0x81

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Status': {}},
            'FocusModeStatus': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'VideoSystemSet': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self.cameraID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self.cameraID = 0x80 + int(value)
        else:
            print('DeviceID must be between 1 and 7')

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x18, 0x01, 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': 0x02,
            'Far': 0x03,
            'Stop': 0x00
        }

        FocusCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF)
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def UpdateFocusModeStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'Auto',
            b'\x03': 'Manual'
        }

        FocusModeStatusCmdString = pack('>5B', self.cameraID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('FocusModeStatus', FocusModeStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('FocusModeStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFocusModeStatus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }
        IrisCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03]
        }

        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        if 1 <= PanSpd <= 24 and 1 <= TiltSpd <= 20:
            PanTiltCmdString = pack('>9B', self.cameraID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }
        PowerCmdString = pack('>6B', self.cameraID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }
        PowerCmdString = pack('>5B', self.cameraID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 9:
            cmdValue = int(value)
            PresetString = pack('>7B', self.cameraID, 0x01, 0x04, 0x3F, 0x02, cmdValue, 0xFF)
            self.__SetHelper('PresetRecall', PresetString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 9:
            cmdValue = int(value)
            PresetString = pack('>7B', self.cameraID, 0x01, 0x04, 0x3F, 0x01, cmdValue, 0xFF)
            self.__SetHelper('PresetSave', PresetString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetVideoSystemSet(self, value, qualifier):

        ValueStateValues = {
            '1080P59.94': 0,
            '1080P50': 1,
            '1080I59.94': 2,
            '1080I50': 3,
            '1080P29.97': 4,
            '1080P25': 5,
            '720P59.94': 6,
            '720P50': 7,
            '720P29.97': 8,
            '720P25': 9,
            '1280x768P30': 10,
            '800x600P30': 11,
            '1024x576P30': 12,
            '960x540P30': 13,
            '704x576P30': 14,
            '640x480P30': 15,
            '576x448P30': 16,
            '768x448P30': 17,
            '640x360P30': 18,
            '512x288P30': 19,
            '352x288P30': 20,
            '176x144P30': 21
        }

        VideoSystemSetCmdString = pack('>B4s2B', self.cameraID, b'\x01\x06\x35\x00', ValueStateValues[value], 0xFF)
        self.__SetHelper('VideoSystemSet', VideoSystemSetCmdString, value, qualifier)

    def UpdateVideoSystemSet(self, value, qualifier):

        ValueStateValues = {
            0: '1080P59.94',
            1: '1080P50',
            2: '1080I59.94',
            3: '1080I50',
            4: '1080P29.97',
            5: '1080P25',
            6: '720P59.94',
            7: '720P50',
            8: '720P29.97',
            9: '720P25',
            10: '1280x768P30',
            11: '800x600P30',
            12: '1024x576P30',
            13: '960x540P30',
            14: '704x576P30',
            15: '640x480P30',
            16: '576x448P30',
            17: '768x448P30',
            18: '640x360P30',
            19: '512x288P30',
            20: '352x288P30',
            21: '176x144P30'
        }

        VideoSystemSetCmdString = pack('>B4s', self.cameraID, b'\x09\x06\x23\xFF')
        res = self.__UpdateHelper('VideoSystemSet', VideoSystemSetCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('VideoSystemSet', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoSystemSet')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': 0,
            'Indoor': 1,
            'Outdoor': 2,
            'One Push': 3,
            'Manual': 5,
            'Outdoor Auto': 6,
            'Sodium Lamp Auto': 7,
            'Sodium Auto': 8
        }

        WhiteBalanceCmdString = pack('>B4s2B', self.cameraID, b'\x01\x04\x35', ValueStateValues[value], 0xFF)
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0: 'Auto',
            1: 'Indoor',
            2: 'Outdoor',
            3: 'One Push',
            4: 'ATW',
            5: 'Manual'
        }

        WhiteBalanceCmdString = pack('>B4s', self.cameraID, b'\x09\x04\x35\xFF')
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateWhiteBalance')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': 0x20,
            'Out': 0x30,
            'Stop': 0x00
        }
        if 0 <= int(qualifier['Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomString = pack('>6B', self.cameraID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)

                if (errorByte == 0x60) and (errorCode == 0x02):
                    print(sourceCmdName + ' Syntax Error')
                    response = ''
                elif (errorByte == 0x61) and (errorCode == 0x41):
                    self.Error([sourceCmdName + ' Command Not Executable'])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)


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
