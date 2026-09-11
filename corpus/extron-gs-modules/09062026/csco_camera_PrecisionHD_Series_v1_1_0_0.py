from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import time
from re import search
from math import pow


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self._Device_ID = 1

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
        self._Camera_Address = 0x80 + self._Device_ID

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightComp': {'Status': {}},
            'Focus'	: {'Status': {}},
            'FocuswithSpeed': {'Parameters': ['Focus Speed'], 'Status': {}},
            'IRReceiver': {'Status': {}},
            'PanPosition': {'Status': {}},
            'PanTilt': {'Status': {}},
            'PanTiltwithSpeed': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PanTiltDirect': {'Parameters': ['Pan Position', 'Tilt Position'], 'Status': {}},
            'Power': {'Status': {}},
            'ResetPanTilt': {'Status': {}},
            'TiltPosition': {'Status': {}},
            'Zoom': {'Status': {}},
            'ZoomwithSpeed': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._Device_ID

    @DeviceID.setter
    def DeviceID(self, newID):
        if 1 <= int(newID) <= 7:
            self._Device_ID = int(newID)
            self._Camera_Address = 0x80 + self._Device_ID
        else:
            print('Invalid Device_ID, ID must be within range of 1 to 7')

    def SetAutoFocus(self, value, qualifier):
        states = {
            'Auto': 0x02,
            'Manual': 0x03
        }

        AutoFocusCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x38, states[value], 0xff])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):
        ValueStateValues = {
            0x02: 'Auto',
            0x03: 'Manual'
        }

        AutoFocusCmdString = bytes([self._Camera_Address, 0x09, 0x04, 0x38, 0xff])
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAutoFocus')

    def SetBacklightComp(self, value, qualifier):
        states = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightCompCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x33, states[value], 0xff])
        self.__SetHelper('BacklightComp', BacklightCompCmdString, value, qualifier)

    def UpdateBacklightComp(self, value, qualifier):
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        BacklightCompCmdString = bytes([self._Camera_Address, 0x09, 0x04, 0x33, 0xff])
        res = self.__UpdateHelper('BacklightComp', BacklightCompCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('BacklightComp', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateBacklightComp')

    def SetFocus(self, value, qualifier):
        states = {
            'Near': 0x30,
            'Far': 0x20,
            'Stop': 0x00
        }

        FocusCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x08, states[value], 0xff])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)

    def SetFocuswithSpeed(self, value, qualifier):
        speed = int(qualifier['Focus Speed'])

        states = {
            'Near': 0x30,
            'Far': 0x20,
        }

        if value == 'Stop':
            FocusCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x08, 0x00, 0xff])
            self.__SetHelper('FocuswithSpeed', FocusCmdString, value, qualifier, 3)
        elif 0 <= speed <= 7:
            FocusCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x08, states[value] + speed, 0xff])
            self.__SetHelper('FocuswithSpeed', FocusCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetFocuswithSpeed')

    def SetIRReceiver(self, value, qualifier):
        states = {
            'On': 0x02,
            'Off': 0x03
        }

        IRReceiverCmdString = bytes([self._Camera_Address, 0x01, 0x06, 0x09, states[value], 0xff])
        self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)

    def UpdatePanPosition(self, value, qualifier):

        PanPositionCmdString = bytes([self._Camera_Address, 0x09, 0x06, 0x12, 0xff])
        res = self.__UpdateHelper('PanPosition', PanPositionCmdString, value, qualifier)
        if res:
            try:
                value = round(((res[3] * pow(16, 2) + res[4] * pow(16, 1) + res[5]) - 408) * (15 / 68))
                if -90 <= value <= 90:
                    self.WriteStatus('PanPosition', value, qualifier)
                else:
                    print('Invalid/unexpected response for UpdatePanPosition')
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePanPosition')

    def SetPanTilt(self, value, qualifier):
        states = {
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

        PanTiltCmdString = bytes([self._Camera_Address, 0x01, 0x06, 0x01, 0x03, 0x03, states[value][0], states[value][1], 0xff])
        self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier, 3)

    def SetPanTiltwithSpeed(self, value, qualifier):
        speed_limits = {
            'min': 1,
            'max': 10
        }

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']

        states = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
        }

        if value == 'Stop':
            PanTiltCmdString = bytes([self._Camera_Address, 0x01, 0x06, 0x01, 0x03, 0x03, 0x03, 0x03, 0xff])
            self.__SetHelper('PanTiltwithSpeed', PanTiltCmdString, value, qualifier, 3)
        elif speed_limits['min'] <= pan_speed <= speed_limits['max'] and speed_limits['min'] <= tilt_speed <= speed_limits['max']:
            PanTiltCmdString = bytes([self._Camera_Address, 0x01, 0x06, 0x01, pan_speed, tilt_speed, states[value][0], states[value][1], 0xff])
            self.__SetHelper('PanTiltwithSpeed', PanTiltCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetPanTiltwithSpeed')

    def SetPanTiltDirect(self, value, qualifier):
        PanPositionConstraints = {
            'Min': -90,
            'Max': 90
        }

        pan_pos = qualifier['Pan Position']
        if PanPositionConstraints['Min'] <= pan_pos <= PanPositionConstraints['Max']:
            pan_valid = True

        TiltPositionConstraints = {
            'Min': -25,
            'Max': 15
        }

        tilt_pos = qualifier['Tilt Position']
        if TiltPositionConstraints['Min'] <= tilt_pos <= TiltPositionConstraints['Max']:
            tilt_valid = True

        if pan_valid and tilt_valid:
            temp_pan = hex(int((68 / 15) * pan_pos + 408))
            pan = temp_pan[2:].zfill(3)
            temp_tilt = hex(int((41 / 8) * tilt_pos + 135))
            tilt = temp_tilt[2:].zfill(3)
            PanTiltDirectCmdString = bytes([self._Camera_Address, 0x01, 0x06, 0x02, 0x0A, 0x0A, 0x00, int(pan[0], 16), int(pan[1], 16), int(pan[2], 16), 0x00, int(tilt[0], 16), int(tilt[1], 16), int(tilt[2], 16), 0xff])
            self.__SetHelper('PanTiltDirect', PanTiltDirectCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTiltDirect')

    def SetPower(self, value, qualifier):
        states = {
            'On': 0x02,
            'Off': 0x03,
        }

        PowerCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x00, states[value], 0xff])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = bytes([self._Camera_Address, 0x09, 0x04, 0x00, 0xff])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetResetPanTilt(self, value, qualifier):
        ResetPanTiltCmdString = bytes([self._Camera_Address, 0x01, 0x06, 0x05, 0xff])
        self.__SetHelper('ResetPanTilt', ResetPanTiltCmdString, value, qualifier)

    def UpdateTiltPosition(self, value, qualifier):
        TiltPositionCmdString = bytes([self._Camera_Address, 0x09, 0x06, 0x12, 0xff])
        res = self.__UpdateHelper('TiltPosition', TiltPositionCmdString, value, qualifier)
        if res:
            try:
                value = round(((res[7] * pow(16, 2) + res[8] * pow(16, 1) + res[9]) - 135) * (8 / 41))
                if -25 <= value <= 15:
                    self.WriteStatus('TiltPosition', value, qualifier)
                else:
                    print('Invalid/unexpected response for UpdateTiltPosition')
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTiltPosition')

    def SetZoom(self, value, qualifier):
        states = {
            'Wide': 0x30,
            'Tele': 0x20,
            'Stop': 0x00
        }

        ZoomCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x07, states[value], 0xff])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier, 3)

    def SetZoomwithSpeed(self, value, qualifier):
        ZoomSpeedConstraints = {
            'Min': 0,
            'Max': 7
        }

        speed = qualifier['Zoom Speed']

        states = {
            'Wide': 0x30,
            'Tele': 0x20
        }

        if value == 'Stop':
            ZoomCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x07, 0x00, 0xff])
            self.__SetHelper('ZoomwithSpeed', ZoomCmdString, value, qualifier, 3)
        elif ZoomSpeedConstraints['Min'] <= speed <= ZoomSpeedConstraints['Max']:
            ZoomCmdString = bytes([self._Camera_Address, 0x01, 0x04, 0x07, states[value] + speed, 0xff])
            self.__SetHelper('ZoomwithSpeed', ZoomCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetZoomwithSpeed')

    def __CheckResponseForErrors(self, sourceCmdName, res):
        DEVICE_ERROR_CODES = {
            0x00: 'Unknown Error',
            0x01: 'Message too long',
            0x02: 'Syntax Error',
            0x03: 'Command buffer full',
            0x04: 'Command cancelled',
            0x05: 'No socket',
            0x41: 'Command not executable',
        }

        if len(res) >= 3:
            if res[1] & 0xf0 == 0x50:
                response = res
            else:
                if res[1] & 0xf0 == 0x60:
                    errorstring = DEVICE_ERROR_CODES[res[1] & 0x0f]
                    print(errorstring)
                    response = ''
                else:
                    print('Invalid/unexpected response ', sourceCmdName)
                    response = ''
        else:
            print('Invalid/unexpected response ', sourceCmdName)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('Invalid/unexpected response', command)
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
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
