from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {
            'WallVIEW HD-19': self.vadd_19_277_HD19,
            'WallVIEW HD-18': self.vadd_19_277_HD18_HD20,
            'WallVIEW HD-20': self.vadd_19_277_HD18_HD20,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Parameters': ['Device ID'], 'Status': {}},
            'Backlight': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID', 'Focus Speed'], 'Status': {}},
            'PanTilt': {'Parameters': ['Device ID', 'Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Device ID', 'Zoom Speed'], 'Status': {}},
        }

    def __DeviceIDCheck(self, deviceID):

        if deviceID == 'Broadcast':
            return 0x88
        elif 1 <= int(deviceID) <= 7:
            return 0x80 + int(deviceID)
        else:
            return None

    def SetAutoFocus(self, value, qualifier):
        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID:
            AutoFocusCmdString = bytes([DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID:
            AutoFocusCmdString = bytes([DeviceID, 0x09, 0x04, 0x38, 0xFF])
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('AutoFocus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Focus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAutoFocus')

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID:
            BacklightCmdString = bytes([DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF])
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID:
            BacklightCmdString = bytes([DeviceID, 0x09, 0x04, 0x33, 0xFF])
            res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Backlight', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Backlight: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBacklight')

    def SetFocus(self, value, qualifier):
        focusSpeed = int(qualifier['Focus Speed'])
        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])

        ValueStateValues = {
            'Far': 0x20 + focusSpeed,
            'Near': 0x30 + focusSpeed,
            'Stop': 0x00
        }

        if DeviceID and 0 <= focusSpeed <= 7:
            FocusCmdString = bytes([DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetPanTilt(self, value, qualifier):

        panSpeed = int(qualifier['Pan Speed'])
        tiltSpeed = int(qualifier['Tilt Speed'])
        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])

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

        if DeviceID and 1 <= panSpeed <= 24 and 1 <= tiltSpeed <= 20:
            PanTiltCmdString = bytes([DeviceID, 0x01, 0x06, 0x01, panSpeed, tiltSpeed, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID:
            PowerCmdString = bytes([DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID:
            PowerCmdString = bytes([DeviceID, 0x09, 0x04, 0x00, 0xFF])
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID and 1 <= int(value) <= self._PresetMax:
            PresetRecallCmdString = bytes([DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value) - 1, 0xFF])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])
        if DeviceID and 1 <= int(value) <= self._PresetMax:
            PresetSaveCmdString = bytes([DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value) - 1, 0xFF])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        zoomSpeed = int(qualifier['Zoom Speed'])
        DeviceID = self.__DeviceIDCheck(qualifier['Device ID'])

        ValueStateValues = {
            'Tele': 0x20 + zoomSpeed,
            'Wide': 0x30 + zoomSpeed,
            'Stop': 0x00
        }

        if DeviceID and 0 <= zoomSpeed <= 7:
            ZoomCmdString = bytes([DeviceID, 0x01, 0x04, 0x07, ValueStateValues[value], 0xFF])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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
        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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

    def vadd_19_277_HD19(self):
        self._PresetMax = 15

    def vadd_19_277_HD18_HD20(self):
        self._PresetMax = 16

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)


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
