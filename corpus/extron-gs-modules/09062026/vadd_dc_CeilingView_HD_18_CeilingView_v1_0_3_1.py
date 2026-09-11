from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self._DeviceID = 0x81

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Brightness': {'Status': {}},
            'DigitalZoom': {'Parameters': ['Zoom Speed', ], 'Status': {}},
            'Effect': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed', ], 'Status': {}},
            'Freeze': {'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'LaserPointer': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed', ], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            self.Error(['DeviceID should be a number between 1 to 7.'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusStateCommand = {
            'On': 0x02,
            'Off': 0x03,
        }
        AutoFocusString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x38, AutoFocusStateCommand[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusString, value, qualifier)
        if len(res) != 0:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('AutoFocus', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('AutoFocus', 'Off', None)
                else:
                    self.Error(['Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetBacklightMode(self, value, qualifier):

        BacklightStateCommand = {
            'On': 0x02,
            'Off': 0x03,
        }
        BacklightString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x33, BacklightStateCommand[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        BacklightString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('BacklightMode', BacklightString, value, qualifier)
        if len(res) != 0:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('BacklightMode', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('BacklightMode', 'Off', None)
                else:
                    self.Error(['Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        BrightnessStateCommand = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }
        BrightnessString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x0D, BrightnessStateCommand[value], 0xFF)
        self.__SetHelper('Brightness', BrightnessString, value, qualifier)

    def SetDigitalZoom(self, value, qualifier):

        DigitalZoomStateCommand = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00,
        }
        if 0 <= int(qualifier['Zoom Speed']) <= 7:
            if value == 'Stop':
                digitalZoomSpeed = 0x00
            else:
                digitalZoomSpeed = int(qualifier['Zoom Speed']) + DigitalZoomStateCommand[value]
            DigitalZoomString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x06, digitalZoomSpeed, 0xFF)
            self.__SetHelper('DigitalZoom', DigitalZoomString, value, qualifier)
        else:
            self.Discard("Invalid Command")

    def SetEffect(self, value, qualifier):

        EffectStateCommand = {
            'B/W': 0x04,
            'Negative': 0x02,
            'Off': 0x00
        }
        EffectString = pack('>BBBBBB', self._DeviceID, 0x01, 0x4, 0x63, EffectStateCommand[value], 0xFF)
        self.__SetHelper('Effect', EffectString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusStateCommand = {
            'Far': 0x20,
            'Near': 0x30,
            'Stop': 0x00,
        }
        if 0 <= int(qualifier['Focus Speed']) <= 7:
            if value == 'Stop':
                focusSpeed = 0x00
            else:
                focusSpeed = int(qualifier['Focus Speed']) + FocusStateCommand[value]
            FocusString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x08, focusSpeed, 0xFF)
            self.__SetHelper('Focus', FocusString, value, qualifier)
        else:
            self.Discard("Invalid Command")

    def SetFreeze(self, value, qualifier):

        FreezeStateCommand = {
            'On': 0x02,
            'Off': 0x03,
        }
        FreezeString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x62, FreezeStateCommand[value], 0xFF)
        self.__SetHelper('Freeze', FreezeString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x62, 0xFF)
        res = self.__UpdateHelper('Freeze', FreezeString, value, qualifier)
        if len(res) != 0:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('Freeze', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('Freeze', 'Off', None)
                else:
                    self.Error(['Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        GainStateCommand = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00,
        }

        GainString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x0C, GainStateCommand[value], 0xFF)
        self.__SetHelper('Gain', GainString, value, qualifier)

    def SetIris(self, value, qualifier):

        IrisStateCommand = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00,
        }
        IrisString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x0B, IrisStateCommand[value], 0xFF)
        self.__SetHelper('Iris', IrisString, value, qualifier)

    def SetLaserPointer(self, value, qualifier):

        LaserPointerStateCommand = {
            'On': 0x02,
            'Off': 0x03,
            'Toggle': 0x01
        }
        LaserPointerString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x2F, LaserPointerStateCommand[value], 0xFF)
        self.__SetHelper('LaserPointer', LaserPointerString, value, qualifier)

    def UpdateLaserPointer(self, value, qualifier):

        LaserPointerString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x2F, 0xFF)
        res = self.__UpdateHelper('LaserPointer', LaserPointerString, value, qualifier)
        if not len(res) == 0:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('LaserPointer', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('LaserPointer', 'Off', None)
                else:
                    self.Error(['Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        MuteStateCommand = {
            'On': 0x02,
            'Off': 0x03,
        }
        MuteString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x75, MuteStateCommand[value], 0xFF)
        self.__SetHelper('Mute', MuteString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x75, 0xFF)
        res = self.__UpdateHelper('Mute', MuteString, value, qualifier)
        if not len(res) == 0:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('Mute', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('Mute', 'Off', None)
                else:
                    self.Error(['Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateCommand = {
            'On': 0x02,
            'Off': 0x03,
        }
        PowerString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x00, PowerStateCommand[value], 0xFF)
        self.__SetHelper('Power', PowerString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerString, value, qualifier)
        if not len(res) == 0:
            try:
                respID, queryByte, queryData, terminator = unpack('>BBBB', res)
                if (queryByte == 0x50) and (queryData == 0x02):
                    self.WriteStatus('Power', 'On', None)
                elif (queryByte == 0x50) and (queryData == 0x03):
                    self.WriteStatus('Power', 'Off', None)
                elif (queryByte == 0x50) and (queryData == 0x04):
                    self.Error(['Power: Internal Power Circuit Error'])
                else:
                    self.Error(['Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        if 0 <= int(value) <= 5:
            cmdValue = int(value)
            PresetString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, cmdValue, 0xFF)
            self.__SetHelper('RecallPreset', PresetString, value, qualifier)
        else:
            self.Discard("Invalid Command")

    def SetSavePreset(self, value, qualifier):

        if 0 <= int(value) <= 5:
            cmdValue = int(value)
            PresetString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, cmdValue, 0xFF)
            self.__SetHelper('SavePreset', PresetString, value, qualifier)
        else:
            self.Discard("Invalid Command")

    def SetZoom(self, value, qualifier):

        ZoomStateCommand = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00,
        }
        if 0 <= int(qualifier['Zoom Speed']) <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = int(qualifier['Zoom Speed']) + ZoomStateCommand[value]
            ZoomString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomString, value, qualifier)
        else:
            self.Discard("Invalid Command")

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)

                if (errorByte == 0x06) and (errorCode == 0x02):
                    self.Error([sourceCmdName + ' Syntax Error'])
                    response = ''
                elif (errorByte == 0x06) and (errorCode == 0x03):
                    self.Error([sourceCmdName + ' Command Buffer Full'])
                    response = ''
                elif (errorByte == 0x06) and (errorCode == 0x41):
                    self.Error([sourceCmdName + ' Command Not Executable'])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x51\xFF')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=4)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)

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
