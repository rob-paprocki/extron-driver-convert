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
            '3DInvert': {'Status': {}},
            '3DMode': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSubInput': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        InvertCmdString = 'CF 3D-INVERT {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('3DInvert', InvertCmdString, value, qualifier)

    def Update3DInvert(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        InvertCmdString = 'CR 3D-INVERT\r\n'
        res = self.__UpdateHelper('3DInvert', InvertCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('3DInvert', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Invert command: Invalid/Unexpected Response'])

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Auto': '1',
            'Frame Packing': '2',
            'Side by Side': '3',
            'Top and Bottom': '4',
            'Frame Sequential': '5'
        }

        ModeCmdString = 'CF 3D-MODE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)

    def Update3DMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Auto',
            '2': 'Frame Packing',
            '3': 'Side by Side',
            '4': 'Top and Bottom',
            '5': 'Frame Sequential'
        }

        ModeCmdString = 'CR 3D-Mode\r\n'
        res = self.__UpdateHelper('3DMode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('3DMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D Mode command: Invalid/Unexpected Response'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            '4:3': '2',
            '16:9': '3',
            '16:10': '4',
            'Native': '5'
        }

        AspectRatioCmdString = 'CF ASPECT {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Auto',
            '2': '4:3',
            '3': '16:9',
            '4': '16:10',
            '5': 'Native'
        }

        AspectRatioCmdString = 'CR ASPECT\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio command: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '1',
            'Video': '2',
            'Bright': '3',
            'REC709': '4',
            'DICOM SIM': '5',
            '2D High Speed': '6',
            '3D': '7',
            'Blending': '8',
            'User': '9'
        }

        DisplayModeCmdString = 'CF IMAGE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Presentation',
            '2': 'Video',
            '3': 'Bright',
            '4': 'REC709',
            '5': 'DICOM SIM',
            '6': '2D High Speed',
            '7': '3D',
            '8': 'Blending',
            '9': 'User'
        }

        DisplayModeCmdString = 'CR IMAGE\r\n'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Mode command: Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '3',
            'Off': '4'
        }

        FreezeCmdString = 'C4{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '05',
            'HDMI': '36',
            'DVI-D': '38',
            'HDBaseT': '52',
            'LAN': '08'
        }

        InputCmdString = 'C{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'VGA',
            '2': 'HDMI',
            '3': 'DVI-D',
            '4': 'HDBaseT',
            '5': 'LAN'
        }

        InputCmdString = 'CR1\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input command: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Constant Power': '2',
            'Constant Luminance': '3',
            'Eco Mode': '1'
        }

        LampModeCmdString = 'CF AUTOLAMPCONTROL {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '2': 'Constant Power',
            '3': 'Constant Luminance',
            '1': 'Eco Mode'
        }

        LampModeCmdString = 'CR AUTOLAMPCONTROL\r\n'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode command: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '3C',
            'Down': '3D',
            'Left': '3B',
            'Right': '3A',
            'Enter': '3F',
            'Exit': 'F KYEXIT',
            'Menu': '1C'
        }

        MenuNavigationCmdString = 'C{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PJTIME\r\n'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError):
                self.Error(['Operation Hours command: Invalid/Unexpected Response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PIPModeCmdString = 'CF PIPMODE {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PIPModeCmdString = 'CR PIPMODE\r\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode command: Invalid/Unexpected Response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'PBP, Main Left': '1',
            'PBP, Main Top': '2',
            'PBP, Main Right': '3',
            'PBP, Main Bottom': '4',
            'PIP-Bottom Right': '5',
            'PIP-Bottom Left': '6',
            'PIP-Top Left': '7',
            'PIP-Top Right': '8'
        }

        PIPPositionCmdString = 'CF PIPPOSITION {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            '1': 'PBP, Main Left',
            '2': 'PBP, Main Top',
            '3': 'PBP, Main Right',
            '4': 'PBP, Main Bottom',
            '5': 'PIP-Bottom Right',
            '6': 'PIP-Bottom Left',
            '7': 'PIP-Top Left',
            '8': 'PIP-Top Right'
        }

        PIPPositionCmdString = 'CR PIPPOSITION\r\n'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position command: Invalid/Unexpected Response'])

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '1',
            'Medium': '2',
            'Large': '3'
        }

        PIPSizeCmdString = 'CF PIPSIZESUB {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            '1': 'Small',
            '2': 'Medium',
            '3': 'Large'
        }

        PIPSizeCmdString = 'CR PIPSIZESUB\r\n'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Size command: Invalid/Unexpected Response'])

    def SetPIPSubInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '1',
            'HDMI': '2',
            'DVI-D': '3',
            'HDBaseT': '4',
            'LAN': '5'
        }

        PIPSubInputCmdString = 'CF PIPSUBINP {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)

    def UpdatePIPSubInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'VGA',
            '2': 'HDMI',
            '3': 'DVI-D',
            '4': 'HDBaseT',
            '5': 'LAN'
        }

        PIPSubInputCmdString = 'CR PIPSUBINP\r\n'
        res = self.__UpdateHelper('PIPSubInput', PIPSubInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('PIPSubInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Sub Input command: Invalid/Unexpected Response'])

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'CF PIPSWAP\r\n'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1',
        }

        PowerCmdString = 'C0{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'Off',
            '2': 'Warming Up',
            '4': 'On',
            '7': 'On',
            '12': 'Cooling Down'
        }

        PowerCmdString = 'CR0\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power command: Invalid/Unexpected Response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open': 'E',
            'Close': 'D'
        }

        ShutterCmdString = 'C0\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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
    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
