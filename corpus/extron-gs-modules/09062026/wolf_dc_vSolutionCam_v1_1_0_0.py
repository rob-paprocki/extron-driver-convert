from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re


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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'CaptureAreaShift': {'Status': {}},
            'ColorMode': {'Status': {}},
            'Detail': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Parameters': ['Speed'], 'Status': {}},
            'Keylock': {'Status': {}},
            'Light': {'Status': {}},
            'MainResolution': {'Status': {}},
            'MenuControl': {'Status': {}},
            'MenuOnOff': {'Status': {}},
            'PositiveNegative': {'Status': {}},
            'Power': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.UpdateRegex = re.compile(b'([\x00|\x08][\x00-\xFF][\x01|\x04][\x00-\x05][\x00-\x3E]{0,4})|(\x80[\x0A|\x31|\\x29|\x80|\x56|\xA0|\x98|\\x5D|\x1F|\x54|\x30|\x65|\x9E|\x6D|\x53|\x75][\x01-\x09])')
            self.SetRegex = re.compile(b'(\x01[\x31\x6D\x53\\x29\x21\x56\x80\xA0\x51\x97\x98\x99\x54\x30\x65\x20]\x00)|(\x81[\x31\x6D\x53\\x29\x21\x56\x80\xA0\x51\x97\x98\x99\x54\x30\x65\x20][\x01-\x09])')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x31\x01\x01',
            'Off': b'\x01\x31\x01\x00'
        }

        AutoFocusCmdString = ValueStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AutoFocusCmdString = b'\x00\x31\x00'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetCaptureAreaShift(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\xF2\x01\x01',
            'Off': b'\x01\xF2\x01\x00'
        }

        CaptureAreaShiftCmdString = ValueStateValues[value]
        self.__SetHelper('CaptureAreaShift', CaptureAreaShiftCmdString, value, qualifier)

    def UpdateCaptureAreaShift(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        CaptureAreaShiftCmdString = b'\x00\xF2\x00'
        res = self.__UpdateHelper('CaptureAreaShift', CaptureAreaShiftCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('CaptureAreaShift', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Capture Area Shift: Invalid/unexpected response'])

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'Black/White': b'\x01\x6D\x01\x00',
            'Presentation': b'\x01\x6D\x01\x01',
            'Natural': b'\x01\x6D\x01\x02',
            'Video Conference': b'\x01\x6D\x01\x03',
            'Manual': b'\x01\x6D\x01\x04'
        }

        ColorModeCmdString = ValueStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Black/White',
            1: 'Presentation',
            2: 'Natural',
            3: 'Video Conference',
            4: 'Manual'
        }

        ColorModeCmdString = b'\x00\x6D\x00'
        res = self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('ColorMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color Mode: Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x01\x53\x01\x00',
            'Medium': b'\x01\x53\x01\x02',
            'High': b'\x01\x53\x01\x03'
        }

        DetailCmdString = ValueStateValues[value]
        self.__SetHelper('Detail', DetailCmdString, value, qualifier)

    def UpdateDetail(self, value, qualifier):

        ValueStateValues = {
            0: 'Off',
            2: 'Medium',
            3: 'High'
        }

        DetailCmdString = b'\x00\x53\x00'
        res = self.__UpdateHelper('Detail', DetailCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Detail', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Detail: Invalid/unexpected response'])

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            '4x': b'\x01\x29\x01\x02',
            '10x': b'\x01\x29\x01\x03'
        }

        DigitalZoomCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            2: '4x',
            3: '10x'
        }

        DigitalZoomCmdString = b'\x00\x29\x00'
        res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('DigitalZoom', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Digital Zoom: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x01,
            'Near': 0x02
        }

        speed = int(qualifier['Speed'])
        if 1 <= speed <= 15:
            if value == 'Stop':
                FocusCmdString = b'\x01\x21\x03\x01\x00\x00'
            else:
                FocusCmdString = pack('>6B', 0x01, 0x21, 0x03, ValueStateValues[value], 0x00, speed)
            if FocusCmdString:
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x56\x01\x01',
            'Off': b'\x01\x56\x01\x00'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FreezeCmdString = b'\x00\x56\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        SpeedStates = {
            'Normal': 1,
            'Full': 2
        }

        ValueStateValues = {
            'Open': 0x01,
            'Close': 0x02
        }

        speed = qualifier['Speed']
        if speed in SpeedStates:
            if value == 'Stop':
                IrisCmdString = b'\x01\x22\x03\x01\x00\x00'
            else:
                IrisCmdString = pack('>6B', 0x01, 0x22, 0x03, ValueStateValues[value], 0x00, SpeedStates[speed])
            if IrisCmdString:
                self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetKeylock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x80\x01\x01',
            'Off': b'\x01\x80\x01\x00'
        }

        KeylockCmdString = ValueStateValues[value]
        self.__SetHelper('Keylock', KeylockCmdString, value, qualifier)

    def UpdateKeylock(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        KeylockCmdString = b'\x00\x80\x00'
        res = self.__UpdateHelper('Keylock', KeylockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Keylock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keylock: Invalid/unexpected response'])

    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\xA0\x01\x01',
            'Off': b'\x01\xA0\x01\x00'
        }

        LightCmdString = ValueStateValues[value]
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def UpdateLight(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        LightCmdString = b'\x00\xA0\x00'
        res = self.__UpdateHelper('Light', LightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Light', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Light: Invalid/unexpected response'])

    def SetMainResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x51\x04\x00\x00\x00\x00',
            '720p/60': b'\x01\x51\x04\x00\x00\x3C\x16',
            '1080p/30': b'\x01\x51\x04\x00\x00\x1E\x18',
            '1080p/60': b'\x01\x51\x04\x00\x00\x3C\x18'
        }

        MainResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('MainResolution', MainResolutionCmdString, value, qualifier)

    def UpdateMainResolution(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00': 'Auto',
            b'\x3C\x16': '720p/60',
            b'\x1E\x18': '1080p/30',
            b'\x3C\x18': '1080p/60'
        }

        MainResolutionCmdString = b'\x00\x51\x00'
        res = self.__UpdateHelper('MainResolution', MainResolutionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('MainResolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Main Resolution: Invalid/unexpected response'])

    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x99\x01\x02',
            'Down': b'\x01\x99\x01\x08',
            'Left': b'\x01\x99\x01\x04',
            'Right': b'\x01\x99\x01\x06',
            'Exit': b'\x01\x99\x01\x05',
            'Help': b'\x01\x99\x01\x10'
        }

        MenuControlCmdString = ValueStateValues[value]
        self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)

    def SetMenuOnOff(self, value, qualifier):

        ValueStateValues = {
            'Menu Off': b'\x01\x98\x01\x00',
            'Standard Menu On': b'\x01\x98\x01\x03',
            'Extra Menu On': b'\x01\x98\x01\x04'
        }

        MenuOnOffCmdString = ValueStateValues[value]
        self.__SetHelper('MenuOnOff', MenuOnOffCmdString, value, qualifier)

    def UpdateMenuOnOff(self, value, qualifier):

        ValueStateValues = {
            0: 'Menu Off',
            1: 'Standard Menu On',
            2: 'Extra Menu On'
        }

        MenuOnOffCmdString = b'\x00\x98\x00'
        res = self.__UpdateHelper('MenuOnOff', MenuOnOffCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('MenuOnOff', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Menu On Off: Invalid/unexpected response'])

    def SetPositiveNegative(self, value, qualifier):

        ValueStateValues = {
            'Positive': b'\x01\x54\x01\x00',
            'Negative': b'\x01\x54\x01\x01'
        }

        PositiveNegativeCmdString = ValueStateValues[value]
        self.__SetHelper('PositiveNegative', PositiveNegativeCmdString, value, qualifier)

    def UpdatePositiveNegative(self, value, qualifier):

        ValueStateValues = {
            0: 'Positive',
            1: 'Negative'
        }

        PositiveNegativeCmdString = b'\x00\x54\x00'
        res = self.__UpdateHelper('PositiveNegative', PositiveNegativeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('PositiveNegative', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Positive Negative: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x30\x01\x01',
            'Off': b'\x01\x30\x01\x00'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x00\x30\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x65\x01\x00',
            'Manual': b'\x01\x65\x01\x02',
            'Perform WB': b'\x01\x65\x01\x10'
        }

        WhiteBalanceCmdString = ValueStateValues[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0: 'Auto',
            2: 'Manual'
        }

        WhiteBalanceCmdString = b'\x00\x65\x00'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Wide': 0x01,
            'Tele': 0x02
        }

        speed = int(qualifier['Speed'])

        if 1 <= speed <= 15:
            if value == 'Stop':
                ZoomCmdString = b'\x01\x20\x03\x01\x00\x00'
            else:
                ZoomCmdString = pack('>6B', 0x01, 0x20, 0x03, ValueStateValues[value], 0x00, speed)
            if ZoomCmdString:
                self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        CommandAction = {
            b'\x80': 'Get',
            b'\x81': 'Set'
        }
        CommandList = {  # Commands zoom and focus does not support errors
            b'\x31': 'Auto Focus',
            b'\x6D': 'Color Mode',
            b'\x53': 'Detail',
            b'\x29': 'Digital Zoom',
            b'\x56': 'Freeze',
            b'\x80': 'Keylock',
            b'\xA0': 'Light',
            b'\x51': 'Main Resolution',
            b'\x99': 'Menu Control',
            b'\x98': 'Menu On Off',
            b'\x54': 'Positive Negative',
            b'\x30': 'Power',
            b'\x65': 'White Balance'

        }
        ErrorType = {
            b'\x01': 'Time Out',
            b'\x02': 'Invalid Cmd',
            b'\x03': 'Invalid Parameter',
            b'\x04': 'Invalid Length',
            b'\x05': 'FiFo Full',
            b'\x06': 'Firmware Update Error',
            b'\x07': 'Access Denied',
            b'\x08': 'AUTH Required',
            b'\x09': 'Busy'
        }
        if response:
            if response[0:1] in CommandAction and response[1:2] in CommandList and response[2:3] in ErrorType:
                self.Error(['{0} {1} Error: {2}'.format(CommandList[response[1:2]], CommandAction[response[0:1]], ErrorType[response[2:3]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                self.Error(['No response received'])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
