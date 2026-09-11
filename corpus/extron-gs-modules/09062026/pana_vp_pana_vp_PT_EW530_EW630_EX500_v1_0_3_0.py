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
        self.Models = {
            'PT-EW630': self.pana_1_248_EZ570,
            'PT-EX500EL': self.pana_1_248_EX600,
            'PT-EX600UL': self.pana_1_248_EX600,
            'PT-EZ570': self.pana_1_248_EZ570,
            'PT-EZ570E': self.pana_1_248_EZ570,
            'PT-EZ570EL': self.pana_1_248_EZ570,
            'PT-EZ570U': self.pana_1_248_EZ570,
            'PT-EZ570UL': self.pana_1_248_EZ570,
            'PT-EW530E': self.pana_1_248_EZ570,
            'PT-EW530EL': self.pana_1_248_EZ570,
            'PT-EW530UL': self.pana_1_248_EZ570,
            'PT-EW530U': self.pana_1_248_EZ570,
            'PT-EW630E': self.pana_1_248_EZ570,
            'PT-EW630EL': self.pana_1_248_EZ570,
            'PT-EW630UL': self.pana_1_248_EZ570,
            'PT-EW630U': self.pana_1_248_EZ570,
            'PT-EX500': self.pana_1_248_EX600,
            'PT-EX500E': self.pana_1_248_EX600,
            'PT-EX500U': self.pana_1_248_EX600,
            'PT-EX500UL': self.pana_1_248_EX600,
            'PT-EX600': self.pana_1_248_EX600,
            'PT-EX600E': self.pana_1_248_EX600,
            'PT-EX600EL': self.pana_1_248_EX600,
            'PT-EW530': self.pana_1_248_EZ570,
            'PT-EX600U': self.pana_1_248_EX600,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PipFrameLock': {'Status': {}},
            'PipHandVMagnification': {'Parameters': ['PIP Type'], 'Status': {}},
            'PipInput': {'Parameters': ['PIP Type'], 'Status': {}},
            'PipMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):
        self.__SetHelper('AspectRatio', self.SetAspectRatioStateValues[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        res = self.__UpdateHelper('AspectRatio', b'\x02QSE\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', self.UpdateAspectRatioStateValues[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Aspect Ratio'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', b'\x02OAS\x03', value, qualifier)

    def SetAVMute(self, value, qualifier):

        States = {
            'On': b'\x02OSH:1\x03',
            'Off': b'\x02OSH:0\x03'
        }

        self.__SetHelper('AVMute', States[value], value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        States = {
            b'1\x03': 'On',
            b'0\x03': 'Off'
        }

        res = self.__UpdateHelper('AVMute', b'\x02QSH\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('AVMute', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for AV Mute'])

    def SetClosedCaption(self, value, qualifier):

        States = {
            'CC1': b'\x02CC:1\x03',
            'CC2': b'\x02CC:2\x03',
            'CC3': b'\x02CC:3\x03',
            'CC4': b'\x02CC:4\x03',
            'Off': b'\x02CC:0\x03'
        }

        self.__SetHelper('ClosedCaption', States[value], value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        States = {
            b'1\x03': 'CC1',
            b'2\x03': 'CC2',
            b'3\x03': 'CC3',
            b'4\x03': 'CC4',
            b'0\x03': 'Off'
        }

        res = self.__UpdateHelper('ClosedCaption', b'\x02QCC\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaption', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Closed Caption'])

    def UpdateDeviceStatus(self, value, qualifier):

        ErrorString = ''
        Errors = 0

        States = {
            '2': 'Lamp 1 Failure After Turning On',
            '4': 'Lamp 1 Failure When Turning On',
            '6': 'Fan 1 Error',
            '7': 'Fan 2 Error',
            '8': 'Fan 3 Error',
            '9': 'Fan 4 Error',
            '10': 'Fan 5 Error',
            '11': 'Fan 6 Error',
            '12': 'Fan 7 Error',
            '13': 'Fan 8 Error',
            '14': 'Fan 9 Error',
            '15': 'Fan 10 Error',
            '24': 'Ballast 1 Error',
            '28': 'Exhaust Fan 1 Error',
            '30': 'Network Error',
            '31': 'FPGA Error',
            '33': 'Lamp Cover Error',
            '37': 'Filter Error',
            '44': 'High Temp Lamp Warning',
            '45': 'Intake Temp Warning',
            '46': 'LCD Panel Temp Warning',
            '52': 'Shutter Error',
            '53': 'Iris Error',
            '54': 'Lamp 1 Error',
            '56': 'Lamp 1 Time Error',
            '58': 'ACF Missing',
            '59': 'High Temp Around Lamp Warning',
            '60': 'Intake Temp Error',
            '61': 'LCD Temp Error',
            '62': 'Internal Error',
            '63': 'Fan Error',
        }

        res = self.__UpdateHelper('DeviceStatus', b'\x02\x00\xFE\x03', value, qualifier)
        if res:
            try:
                res = int.from_bytes(res[2:10], byteorder='big')
                for i in range(2, 64):
                    if (str(i) in States) and (res >> i & 1):
                        Errors += 1
                        ErrorString = States[str(i)]
                if Errors == 0:
                    self.WriteStatus('DeviceStatus', 'No Errors', qualifier)
                elif Errors == 1:
                    self.WriteStatus('DeviceStatus', ErrorString, qualifier)
                else:
                    self.WriteStatus('DeviceStatus', 'Multiple Errors', qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Device Status'])

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', b'\x02QFI:0\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage', int(res[1:-1]), qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Filter Usage'])

    def SetFocus(self, value, qualifier):

        States = {
            'In': b'\x02\xB1\x7C\x02\x01\x00\x03',
            'Out': b'\x02\xB1\x7C\x02\x01\x01\x03'
        }

        self.__SetHelper('Focus', States[value], value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On': b'\x02OFZ:1\x03',
            'Off': b'\x02OFZ:0\x03'
        }

        self.__SetHelper('Freeze', States[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            b'0\x03': 'Off',
            b'1\x03': 'On'
        }

        res = self.__UpdateHelper('Freeze', b'\x02QFZ\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Freeze'])

    def SetInput(self, value, qualifier):

        States = {
            'PC1': b'\x02IIS:PC1\x03',
            'PC2': b'\x02IIS:PC2\x03',
            'RGB 1': b'\x02IIS:RG1\x03',
            'RGB 2': b'\x02IIS:RG2\x03',
            'Input 2: Y/Pb/Pr': b'\x02IIS:CP1\x03',
            'Input 3: Y/Pb/Pr': b'\x02IIS:CP2\x03',
            'Input 2 Video': b'\x02IIS:VD1\x03',
            'Input 3 Video': b'\x02IIS:VD2\x03',
            'S-Video': b'\x02IIS:SVD\x03',
            'DVI': b'\x02IIS:DVI\x03',
            'HDMI': b'\x02IIS:HD1\x03',
            'Scart': b'\x02IIS:SCT\x03'
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            b'PC1\x03': 'PC1',
            b'PC2\x03': 'PC2',
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'CP1\x03': 'Input 2: Y/Pb/Pr',
            b'CP2\x03': 'Input 3: Y/Pb/Pr',
            b'VD1\x03': 'Input 2 Video',
            b'VD2\x03': 'Input 3 Video',
            b'SVD\x03': 'S-Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
            b'SCT\x03': 'Scart'
        }

        res = self.__UpdateHelper('Input', b'\x02QIN\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Input'])

    def SetLampPower(self, value, qualifier):

        States = {
            'Normal': b'\x02OLP:0\x03',
            'Auto': b'\x02OLP:2\x03',
            'Eco 1': b'\x02OLP:3\x03',
            'Eco 2': b'\x02OLP:4\x03'
        }

        self.__SetHelper('LampPower', States[value], value, qualifier)

    def UpdateLampPower(self, value, qualifier):

        States = {
            b'0\x03': 'Normal',
            b'2\x03': 'Auto',
            b'3\x03': 'Eco 1',
            b'4\x03': 'Eco 2'
        }

        res = self.__UpdateHelper('LampPower', b'\x02QLP\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampPower', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Lamp Power'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', b'\x02Q$L:1\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', int(res[1:-1]), qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Lamp Usage'])

    def SetLensShift(self, value, qualifier):

        States = {
            'Right': b'\x02\xB1\x7C\x00\x01\x00\x03',
            'Left': b'\x02\xB1\x7C\x00\x01\x01\x03',
            'Up': b'\x02\xB1\x7C\x01\x01\x00\x03',
            'Down': b'\x02\xB1\x7C\x01\x01\x01\x03'
        }

        self.__SetHelper('LensShift', States[value], value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': b'\x02OMN\x03',
            'Up': b'\x02OCU\x03',
            'Down': b'\x02OCD\x03',
            'Left': b'\x02OCL\x03',
            'Right': b'\x02OCR\x03',
            'Enter': b'\x02OEN\x03'
        }

        self.__SetHelper('MenuNavigation', States[value], value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', b'\x02QST\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('OperationHours', int(res[1:-1]), qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Operation Hours'])

    def SetPictureMode(self, value, qualifier):

        States = {
            'Standard': b'\x02VPM:STD\x03',
            'Dynamic': b'\x02VPM:DYN\x03',
            'Cinema': b'\x02VPM:CIN\x03',
            'Real': b'\x02VPM:REA\x03',
            'Natural': b'\x02VPM:NAT\x03'
        }

        self.__SetHelper('PictureMode', States[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        States = {
            b'ST': 'Standard',
            b'DY': 'Dynamic',
            b'CI': 'Cinema',
            b'RE': 'Real',
            b'NA': 'Natural'
        }

        res = self.__UpdateHelper('PictureMode', b'\x02QPM\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureMode', States[res[1:3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Picture Mode'])

    def SetPipFrameLock(self, value, qualifier):

        States = {
            'Main': b'\x02PFL:0\x03',
            'Sub Window': b'\x02PFL:1\x03'
        }

        self.__SetHelper('PipFrameLock', States[value], value, qualifier)

    def UpdatePipFrameLock(self, value, qualifier):

        States = {
            b'0\x03': 'Main',
            b'1\x03': 'Sub Window'
        }

        res = self.__UpdateHelper('PipFrameLock', b'\x02QPF\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('PipFrameLock', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for PIP Frame Lock'])

    def SetPipHandVMagnification(self, value, qualifier):

        PipTypeValues = {
            'Main': b'MSZ',
            'Sub': b'SSZ'
        }

        PipType = qualifier['PIP Type']
        PipType = PipTypeValues[PipType]

        States = {
            '10': b'\x02' + PipType + b':010\x03',
            '20': b'\x02' + PipType + b':020\x03',
            '30': b'\x02' + PipType + b':030\x03',
            '40': b'\x02' + PipType + b':040\x03',
            '50': b'\x02' + PipType + b':050\x03',
            '60': b'\x02' + PipType + b':060\x03',
            '70': b'\x02' + PipType + b':070\x03',
            '80': b'\x02' + PipType + b':080\x03',
            '90': b'\x02' + PipType + b':090\x03',
            '100': b'\x02' + PipType + b':100\x03'
        }

        self.__SetHelper('PipHandVMagnification', States[value], value, qualifier)

    def SetPipInput(self, value, qualifier):

        PipInputType = {
            'Main': b'MSZ',
            'Sub': b'SIS'
        }[qualifier['PIP Type']]

        States = {
            'PC1': b'\x02' + PipInputType + b':PC1\x03',
            'PC2': b'\x02' + PipInputType + b':PC2\x03',
            'RGB 1': b'\x02' + PipInputType + b':RG1\x03',
            'RGB 2': b'\x02' + PipInputType + b':RG2\x03',
            'Input 2: Y/Pb/Pr': b'\x02' + PipInputType + b':CP1\x03',
            'Input 3: Y/Pb/Pr': b'\x02' + PipInputType + b':CP2\x03',
            'Input 2 Video': b'\x02' + PipInputType + b':VD1\x03',
            'Input 3 Video': b'\x02' + PipInputType + b':VD2\x03',
            'S-Video': b'\x02' + PipInputType + b':SVD\x03',
            'DVI': b'\x02' + PipInputType + b':DVI\x03',
            'HDMI': b'\x02' + PipInputType + b':HD1\x03',
            'Scart': b'\x02' + PipInputType + b':SCT\x03'
        }

        self.__SetHelper('PipInput', States[value], value, qualifier)

    def UpdatePipInput(self, value, qualifier):

        CmdString = {
            'Main': b'\x02QIM\x03',
            'Sub': b'\x02QIS\x03'
        }[qualifier['PIP Type']]

        States = {
            b'PC1\x03': 'PC1',
            b'PC2\x03': 'PC2',
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'CP1\x03': 'Input 2: Y/Pb/Pr',
            b'CP2\x03': 'Input 3: Y/Pb/Pr',
            b'VD1\x03': 'Input 2 Video',
            b'VD2\x03': 'Input 3 Video',
            b'SVD\x03': 'S-Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
            b'SCT\x03': 'Scart'
        }

        res = self.__UpdateHelper('PipInput', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('PipInput', States[res[1:]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response fof PIP Input'])

    def SetPipMode(self, value, qualifier):

        States = {
            'User 1': b'\x02OPP:1\x03',
            'User 2': b'\x02OPP:2\x03',
            'User 3': b'\x02OPP:3\x03',
            'User 4': b'\x02OPP:4\x03',
            'User 5': b'\x02OPP:5\x03',
            'Off': b'\x02OPP:0\x03'
        }

        self.__SetHelper('PipMode', States[value], value, qualifier)

    def UpdatePipMode(self, value, qualifier):

        States = {
            b'1': 'User 1',
            b'2': 'User 2',
            b'3': 'User 3',
            b'4': 'User 4',
            b'5': 'User 5',
            b'0': 'Off'
        }

        res = self.__UpdateHelper('PipMode', b'\x02QPP\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('PipMode', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for PIP Mode'])

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\x02ADZZ;PON\x03',
            'Off': b'\x02ADZZ;POF\x03'
        }
        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            b'2': 'On',
            b'1': 'Warming Up',
            b'3': 'Cooling Down',
            b'0': 'Off'
        }

        res = self.__UpdateHelper('Power', b'\x02Q$S\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Power'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            CmdString = b'\x02AVL:' + str(value).zfill(3).encode() + b'\x03'
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', b'\x02QAV\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res[1:4]), qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Volume'])

    def SetZoom(self, value, qualifier):

        States = {
            'In': b'\x02\xB1\x7C\x03\x01\x00\x03',
            'Out': b'\x02\xB1\x7C\x03\x01\x01\x03'
        }

        self.__SetHelper('Zoom', States[value], value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {b'\x02ER401\x03': 'Invalid Command.',
                              b'\x02ER402\x03': 'Invalid Parameter'}
        if response:
            for key, value in DEVICE_ERROR_CODES.items():
                if key == response:
                    self.Error([sourceCmdName + ' ' + value])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['Invalid/Unexpected Response for {}'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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

    def pana_1_248_EZ570(self):

        self.SetAspectRatioStateValues = {
            'Normal': b'\x02VSE:0\x03',
            'Full': b'\x02VSE:6\x03',
            'Wide': b'\x02VSE:2\x03',
            'Zoom': b'\x02VSE:40\x03',
            'Real': b'\x02VSE:5\x03',
            'Custom': b'\x02VSE:50\x03',
            'Natural': b'\x02VSE:60\x03'
        }

        self.UpdateAspectRatioStateValues = {
            b'0\x03': 'Normal',
            b'6\x03': 'Full',
            b'2\x03': 'Wide',
            b'40\x03': 'Zoom',
            b'5\x03': 'Real',
            b'50\x03': 'Custom',
            b'60\x03': 'Natural'
        }

    def pana_1_248_EX600(self):

        self.SetAspectRatioStateValues = {
            'Normal': b'\x02VSE:0\x03',
            'Full': b'\x02VSE:6\x03',
            'Wide': b'\x02VSE:2\x03',
            'Zoom': b'\x02VSE:40\x03',
            'Real': b'\x02VSE:5\x03',
            'Custom': b'\x02VSE:50\x03',
        }

        self.UpdateAspectRatioStateValues = {
            b'0\x03': 'Normal',
            b'6\x03': 'Full',
            b'2\x03': 'Wide',
            b'40\x03': 'Zoom',
            b'5\x03': 'Real',
            b'50\x03': 'Custom',
        }

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
