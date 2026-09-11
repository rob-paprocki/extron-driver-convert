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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ThreeDDarkTime': {'Status': {}},
            'ThreeDDLPLink': {'Status': {}},
            'ThreeDEyeSwap': {'Status': {}},
            'ThreeDFormat': {'Status': {}},
            'ThreeDSyncDelay': {'Status': {}},
            'ThreeDSyncReference': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ColorSpace': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Input': {'Status': {}},
            'LaserHours': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Overscan': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.regexRes = {
                'ThreeDDarkTime': re.compile(b'OP 3D\.DARKTIME = (0|1|2)'),
                'ThreeDDLPLink': re.compile(b'OP 3D\.DLPLINK = (0|1)'),
                'ThreeDEyeSwap': re.compile(b'OP 3D\.SWAP = (0|1)'),
                'ThreeDFormat': re.compile(b'OP 3D\.FORMAT = ([0-4])'),
                'ThreeDSyncDelay': re.compile(b'OP 3D\.SYNCDELAY = (\d+)'),
                'ThreeDSyncReference': re.compile(b'OP 3D\.SYNCREF = ([0-2])'),
                'AspectRatio': re.compile(b'OP ASPECT = ([0-8])'),
                'ColorSpace': re.compile(b'OP COLOR\.SPACE = ([0-4])'),
                'EcoMode': re.compile(b'OP LASER\.MODE = ([0-2])'),
                'Input': re.compile(b'OP INPUT\.SEL = ([0-6])'),
                'LaserHours': re.compile(b'OP LASER\.HOURS = (\d+)'),
                'Overscan': re.compile(b'OP ZOOM = ([0-2])'),
                'PictureMode': re.compile(b'OP PIC\.MODE = ([0-2])'),
                'PIP': re.compile(b'OP PIP\.MODE = (0|1)'),
                'PIPInput': re.compile(b'OP PIP\.INPUT = ([0-6])'),
                'PIPPosition': re.compile(b'OP PIP\.POSITION = ([0-4])'),
                'Power': re.compile(b'OP STATUS = ([0-4])')
            }

    def SetThreeDDarkTime(self, value, qualifier):

        ValueStateValues = {
            '0.65 ms': 'op 3d.darktime = 0\r',
            '1.3 ms': 'op 3d.darktime = 1\r',
            '1.95 ms': 'op 3d.darktime = 2\r'
        }

        ThreeDDarkTimeCmdString = ValueStateValues[value]
        self.__SetHelper('ThreeDDarkTime', ThreeDDarkTimeCmdString, value, qualifier)

    def UpdateThreeDDarkTime(self, value, qualifier):

        ValueStateValues = {
            '0': '0.65 ms',
            '1': '1.3 ms',
            '2': '1.95 ms'
        }

        ThreeDDarkTimeCmdString = 'op 3d.darktime ?\r'
        res = self.__UpdateHelper('ThreeDDarkTime', ThreeDDarkTimeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[17]]
                self.WriteStatus('ThreeDDarkTime', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ThreeDDarkTime: Invalid/unexpected response'])

    def SetThreeDDLPLink(self, value, qualifier):

        ValueStateValues = {
            'Off': 'op 3d.dlplink = 0\r',
            'On': 'op 3d.dlplink = 1\r'
        }

        ThreeDDLPLinkCmdString = ValueStateValues[value]
        self.__SetHelper('ThreeDDLPLink', ThreeDDLPLinkCmdString, value, qualifier)

    def UpdateThreeDDLPLink(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        ThreeDDLPLinkCmdString = 'op 3d.dlplink ?\r'
        res = self.__UpdateHelper('ThreeDDLPLink', ThreeDDLPLinkCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[16]]
                self.WriteStatus('ThreeDDLPLink', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ThreeDDLPLink: Invalid/unexpected response'])

    def SetThreeDEyeSwap(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'op 3d.swap = 0\r',
            'Reverse': 'op 3d.swap = 1\r'
        }

        ThreeDEyeSwapCmdString = ValueStateValues[value]
        self.__SetHelper('ThreeDEyeSwap', ThreeDEyeSwapCmdString, value, qualifier)

    def UpdateThreeDEyeSwap(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Reverse'
        }

        ThreeDEyeSwapCmdString = 'op 3d.swap ?\r'
        res = self.__UpdateHelper('ThreeDEyeSwap', ThreeDEyeSwapCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[13]]
                self.WriteStatus('ThreeDEyeSwap', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ThreeDEyeSwap: Invalid/unexpected response'])

    def SetThreeDFormat(self, value, qualifier):

        ValueStateValues = {
            'Off': 'op 3d.format = 0\r',
            'Auto': 'op 3d.format = 1\r',
            'Side by Side': 'op 3d.format = 2\r',
            'Top and Bottom': 'op 3d.format = 3\r',
            'Frame Sequential': 'op 3d.format = 4\r'
        }

        ThreeDFormatCmdString = ValueStateValues[value]
        self.__SetHelper('ThreeDFormat', ThreeDFormatCmdString, value, qualifier)

    def UpdateThreeDFormat(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Auto',
            '2': 'Side by Side',
            '3': 'Top and Bottom',
            '4': 'Frame Sequential'
        }

        ThreeDFormatCmdString = 'op 3d.format ?\r'
        res = self.__UpdateHelper('ThreeDFormat', ThreeDFormatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15]]
                self.WriteStatus('ThreeDFormat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ThreeDFormat: Invalid/unexpected response'])

    def SetThreeDSyncDelay(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 60
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ThreeDSyncDelayCmdString = 'op 3d.syncdelay = {0}\r'.format(value)
            self.__SetHelper('ThreeDSyncDelay', ThreeDSyncDelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetThreeDSyncDelay')

    def UpdateThreeDSyncDelay(self, value, qualifier):

        ThreeDSyncDelayCmdString = 'op 3d.syncdelay ?\r'
        res = self.__UpdateHelper('ThreeDSyncDelay', ThreeDSyncDelayCmdString, value, qualifier)
        if res:
            try:
                value = int(res[18:])
                self.WriteStatus('ThreeDSyncDelay', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['ThreeDSyncDelay: Invalid/unexpected response'])

    def SetThreeDSyncReference(self, value, qualifier):

        ValueStateValues = {
            'External': 'op 3d.syncref = 0\r',
            'Internal': 'op 3d.syncref = 1\r',
            'Auto': 'op 3d.syncref = 2\r'
        }

        ThreeDSyncReferenceCmdString = ValueStateValues[value]
        self.__SetHelper('ThreeDSyncReference', ThreeDSyncReferenceCmdString, value, qualifier)

    def UpdateThreeDSyncReference(self, value, qualifier):

        ValueStateValues = {
            '0': 'External',
            '1': 'Internal',
            '2': 'Auto'
        }

        ThreeDSyncReferenceCmdString = 'op 3d.syncref ?\r'
        res = self.__UpdateHelper('ThreeDSyncReference', ThreeDSyncReferenceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[16]]
                self.WriteStatus('ThreeDSyncReference', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ThreeDSyncReference: Invalid/unexpected response'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '5:4': 'op aspect = 0\r',
            '4:3': 'op aspect = 1\r',
            '16:10': 'op aspect = 2\r',
            '16:9': 'op aspect = 3\r',
            '1.88': 'op aspect = 4\r',
            '2.35': 'op aspect = 5\r',
            'LetterBox': 'op aspect = 6\r',
            'Source': 'op aspect = 7\r',
            'Native': 'op aspect = 8\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': '5:4',
            '1': '4:3',
            '2': '16:10',
            '3': '16:9',
            '4': '1.88',
            '5': '2.35',
            '6': 'LetterBox',
            '7': 'Source',
            '8': 'Native'
        }

        AspectRatioCmdString = 'op aspect ?\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AspectRatio: Invalid/unexpected response'])

    def SetColorSpace(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'op color.space = 0\r',
            'YPbPr': 'op color.space = 1\r',
            'YcbCr': 'op color.space = 2\r',
            'RGB-PC': 'op color.space = 3\r',
            'RGB-Video': 'op color.space = 4\r'
        }

        ColorSpaceCmdString = ValueStateValues[value]
        self.__SetHelper('ColorSpace', ColorSpaceCmdString, value, qualifier)

    def UpdateColorSpace(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'YPbPr',
            '2': 'YcbCr',
            '3': 'RGB-PC',
            '4': 'RGB-Video'
        }

        ColorSpaceCmdString = 'op color.space ?\r'
        res = self.__UpdateHelper('ColorSpace', ColorSpaceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[17]]
                self.WriteStatus('ColorSpace', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ColorSpace: Invalid/unexpected response'])

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Eco Mode': 'op laser.mode = 0\r',
            'Normal Mode': 'op laser.mode = 1\r',
            'Custom Power Mode': 'op laser.mode = 2\r'
        }

        EcoModeCmdString = ValueStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Eco Mode',
            '1': 'Normal Mode',
            '2': 'Custom Power Mode'
        }

        EcoModeCmdString = 'op laser.mode ?\r'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[16]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['EcoMode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'op input.sel = 0\r',
            'HDMI 2': 'op input.sel = 1\r',
            'VGA': 'op input.sel = 2\r',
            'Component (BNC)': 'op input.sel = 3\r',
            'DVI': 'op input.sel = 4\r',
            '3G-SDI': 'op input.sel = 5\r',
            'HDBaseT': 'op input.sel = 6\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'VGA',
            '3': 'Component (BNC)',
            '4': 'DVI',
            '5': '3G-SDI',
            '6': 'HDBaseT'
        }

        InputCmdString = 'op input.sel ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLaserHours(self, value, qualifier):

        LaserHoursCmdString = 'op laser.hours ?\r'
        res = self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[17:])
                self.WriteStatus('LaserHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['LaserHours: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Exit': 'ky exit\r',
            'Menu': 'ky menu\r',
            'Enter': 'ky enter\r',
            'Up': 'ky up\r',
            'Down': 'ky down\r',
            'Left': 'ky left\r',
            'Right': 'ky right\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOverscan(self, value, qualifier):

        ValueStateValues = {
            'Off': 'op zoom = 0\r',
            'Crop': 'op zoom = 1\r',
            'Zoom': 'op zoom = 2\r'
        }

        OverscanCmdString = ValueStateValues[value]
        self.__SetHelper('Overscan', OverscanCmdString, value, qualifier)

    def UpdateOverscan(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Crop',
            '2': 'Zoom'
        }

        OverscanCmdString = 'op zoom ?\r'
        res = self.__UpdateHelper('Overscan', OverscanCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10]]
                self.WriteStatus('Overscan', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Overscan: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'High Bright': 'op pic.mode = 0\r',
            'Presentation': 'op pic.mode = 1\r',
            'Video': 'op pic.mode = 2\r'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'High Bright',
            '1': 'Presentation',
            '2': 'Video'
        }

        PictureModeCmdString = 'op pic.mode ?\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[14]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PictureMode: Invalid/unexpected response'])

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'On': 'op pip.mode = 1\r',
            'Off': 'op pip.mode = 0\r'
        }

        PIPCmdString = ValueStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PIPCmdString = 'op pip.mode ?\r'
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[14]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'op pip.input = 0\r',
            'HDMI 2': 'op pip.input = 1\r',
            'VGA': 'op pip.input = 2\r',
            'Component (BNC)': 'op pip.input = 3\r',
            'DVI': 'op pip.input = 4\r',
            '3G-SDI': 'op pip.input = 5\r',
            'HDBaseT': 'op pip.input = 6\r'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'VGA',
            '3': 'Component (BNC)',
            '4': 'DVI',
            '5': '3G-SDI',
            '6': 'HDBaseT'
        }

        PIPInputCmdString = 'op pip.input ?\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIPInput: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': 'op pip.position = 0\r',
            'Top Right': 'op pip.position = 1\r',
            'Bottom Left': 'op pip.position = 2\r',
            'Bottom Right': 'op pip.position = 3\r',
            'PBP': 'op pip.position = 4\r'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            '0': 'Top Left',
            '1': 'Top Right',
            '2': 'Bottom Left',
            '3': 'Bottom Right',
            '4': 'PBP'
        }

        PIPPositionCmdString = 'op pip.position ?\r'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[18]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIPPosition: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ky power.on\r',
            'Off': 'ky power.off\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Warming Up',
            '2': 'On',
            '3': 'Cooling Down',
            '4': 'Error'
        }

        PowerCmdString = 'op status ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == 'NA':
            self.Error(['{0}: Failed to execute command'.format(sourceCmdName)])
            response = b''
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or command == 'MenuNavigation':
            self.Send(commandstring)
        else:
            delimReg = self.regexRes[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=delimReg)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            if command == 'ThreeDSyncDelay' or command == 'LaserHours':
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            else:
                delimReg = self.regexRes[command]
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=delimReg)
            if not res:
                if command == 'Power':
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

