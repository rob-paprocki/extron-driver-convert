from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self._DeviceID = b'\x01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PAPEnable': {'Status': {}},
            'PAPSize': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value
        if 1 <= int(value) <= 98:
            self._DeviceID = value.zfill(2).encode()

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Full/Full 2': b'\x73\x31\x30\x30\x30\x0D',
            '4:3/Real': b'\x73\x31\x30\x30\x31\x0D',
            'Wide Zoom/Full 1': b'\x73\x31\x30\x30\x32\x0D',
            'Zoom': b'\x73\x31\x30\x30\x33\x0D'
        }

        AspectRatioCmdString = b'\x38' + self._DeviceID + AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            '0': 'Full/Full 2',
            '1': '4:3/Real',
            '2': 'Wide Zoom/Full 1',
            '3': 'Zoom'
        }

        AspectRatioCmdString = b'\x38' + self._DeviceID + b'\x67\x77\x30\x30\x30\x0D'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateValues[chr(res[-2])]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x38' + self._DeviceID + b'\x73\x8F\x30\x30\x30\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'VGA': b'\x73\x22\x30\x30\x30\x0D',
            'HDMI': b'\x73\x22\x30\x30\x31\x0D',
            'YPbPr': b'\x73\x22\x30\x30\x34\x0D',
            'DVI': b'\x73\x22\x30\x30\x36\x0D',
            'DisplayPort': b'\x73\x22\x30\x30\x37\x0D',
            'Multi-Media': b'\x73\x22\x30\x30\x39\x0D'
        }

        InputCmdString = b'\x38' + self._DeviceID + InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateValues = {
            '0': 'VGA',
            '1': 'HDMI',
            '4': 'YPbPr',
            '6': 'DVI',
            '7': 'DisplayPort',
            '9': 'Multi-Media'
        }

        InputCmdString = b'\x38' + self._DeviceID + b'\x67\x6A\x30\x30\x30\x0D'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateValues[chr(res[-2])]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMute(self, value, qualifier):

        MuteStateValues = {
            'On': b'\x73\x36\x30\x30\x31\x0D',
            'Off': b'\x73\x36\x30\x30\x30\x0D'
        }

        MuteCmdString = b'\x38' + self._DeviceID + MuteStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteCmdString = b'\x38' + self._DeviceID + b'\x67\x67\x30\x30\x30\x0D'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteStateValues[chr(res[-2])]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On': b'\x73\x5B\x30\x30\x31\x0D',
            'Off': b'\x73\x5B\x30\x30\x30\x0D'
        }

        OnScreenDisplayCmdString = b'\x38' + self._DeviceID + OnScreenDisplayStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = b'\x38' + self._DeviceID + b'\x67\x5D\x30\x30\x30\x0D'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateValues[chr(res[-2])]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPAPEnable(self, value, qualifier):

        PAPEnableStateValues = {
            'Off': b'\x73\x8A\x30\x30\x30\x0D',
            'PIP': b'\x73\x8A\x30\x30\x31\x0D',
            'PBP': b'\x73\x8A\x30\x30\x32\x0D'
        }

        PAPEnableCmdString = b'\x38' + self._DeviceID + PAPEnableStateValues[value]
        self.__SetHelper('PAPEnable', PAPEnableCmdString, value, qualifier)

    def UpdatePAPEnable(self, value, qualifier):

        PAPEnableStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PBP'
        }

        PAPEnableCmdString = b'\x38' + self._DeviceID + b'\x67\xBA\x30\x30\x30\x0D'
        res = self.__UpdateHelper('PAPEnable', PAPEnableCmdString, value, qualifier)
        if res:
            try:
                value = PAPEnableStateValues[chr(res[-2])]
                self.WriteStatus('PAPEnable', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePAPEnable')

    def SetPAPSize(self, value, qualifier):

        PIPSizeStateValues = {
            'Small': b'\x73\x8D\x30\x30\x30\x0D',
            'Large': b'\x73\x8D\x30\x30\x31\x0D',
        }

        PBPSizeStateValues = {
            '0': b'\x73\x8D\x30\x30\x30\x0D',
            '1': b'\x73\x8D\x30\x30\x31\x0D',
            '2': b'\x73\x8D\x30\x30\x32\x0D',
            '3': b'\x73\x8D\x30\x30\x33\x0D',
            '4': b'\x73\x8D\x30\x30\x34\x0D',
            '5': b'\x73\x8D\x30\x30\x35\x0D',
            '6': b'\x73\x8D\x30\x30\x36\x0D',
            '7': b'\x73\x8D\x30\x30\x37\x0D',
            '8': b'\x73\x8D\x30\x30\x38\x0D',
            '9': b'\x73\x8D\x30\x30\x39\x0D',
            '10': b'\x73\x8D\x30\x31\x30\x0D',
            '11': b'\x73\x8D\x30\x31\x31\x0D',
            '12': b'\x73\x8D\x30\x31\x32\x0D',
            '13': b'\x73\x8D\x30\x31\x33\x0D',
            '14': b'\x73\x8D\x30\x31\x34\x0D'
        }

        PAPEnabled = self.ReadStatus('PAPEnable', None)
        if PAPEnabled == 'PIP' and value in ['Small', 'Large']:
            PAPSizeCmdString = b'\x38' + self._DeviceID + PIPSizeStateValues[value]
            self.__SetHelper('PAPSize', PAPSizeCmdString, value, qualifier)
        elif PAPEnabled == 'PBP'and 0 <= int(value) <= 14:
            PAPSizeCmdString = b'\x38' + self._DeviceID + PBPSizeStateValues[value]        
            self.__SetHelper('PAPSize', PAPSizeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdatePAPSize(self, value, qualifier):

        PIPSizeStateValues = {
            b'00': 'Small',
            b'01': 'Large',
        }

        PBPSizeStateValues = {
            b'00': '0',
            b'01': '1',
            b'02': '2',
            b'03': '3',
            b'04': '4',
            b'05': '5',
            b'06': '6',
            b'07': '7',
            b'08': '8',
            b'09': '9',
            b'10': '10',
            b'11': '11',
            b'12': '12',
            b'13': '13',
            b'14': '14'
        }

        PAPEnableCmdString = b'\x38' + self._DeviceID + b'\x67\xBA\x30\x30\x30\x0D'
        PAPSizeCmdString = b'\x38' + self._DeviceID + b'\x67\xBD\x30\x30\x30\x0D'
        res = self.__UpdateHelper('PAPSize', PAPSizeCmdString, value, qualifier)
        if res:
            try:
                PAP = self.__UpdateHelper('PAPEnable', PAPEnableCmdString, value, qualifier)
                if chr(PAP[-2]) == '1':
                    value = PIPSizeStateValues[res[6:-1]]
                elif chr(PAP[-2]) == '2':
                    value = PBPSizeStateValues[res[6:-1]]
                if value:
                    self.WriteStatus('PAPSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePAPSize')

    def SetPIPPosition(self, value, qualifier):

        PIPPositionStateValues = {
            'Upper Left': b'\x73\x8E\x30\x30\x30\x0D',
            'Upper Right': b'\x73\x8E\x30\x30\x31\x0D',
            'Lower Left': b'\x73\x8E\x30\x30\x32\x0D',
            'Lower Right': b'\x73\x8E\x30\x30\x33\x0D'
        }

        PIPPositionCmdString = b'\x38' + self._DeviceID + PIPPositionStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionStateValues = {
            '0': 'Upper Left',
            '1': 'Upper Right',
            '2': 'Lower Left',
            '3': 'Lower Right'
        }

        PIPPositionCmdString = b'\x38' + self._DeviceID + b'\x67\xBF\x30\x30\x30\x0D'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = PIPPositionStateValues[chr(res[-2])]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPPosition')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': b'\x73\x21\x30\x30\x30\x0D',
            'On': b'\x73\x21\x30\x30\x31\x0D'
        }

        PowerCmdString = b'\x38' + self._DeviceID + PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        PowerCmdString = b'\x38' + self._DeviceID + b'\x67\x6C\x30\x30\x30\x0D'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateValues[chr(res[-2])]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = b'\x38' + self._DeviceID + b'\x73\x35' + (str(value)).zfill(3).encode() + b'\x0D'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x38' + self._DeviceID + b'\x67\x66\x30\x30\x30\x0D'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:-1].decode())
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if chr(response[3]) == b'-':
            print('The Command is Not Valid')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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
