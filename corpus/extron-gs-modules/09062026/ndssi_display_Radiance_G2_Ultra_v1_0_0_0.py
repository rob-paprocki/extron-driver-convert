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
            'Radiance': self.ndssi_10_4002_G2,
            'Radiance G2': self.ndssi_10_4002_G2,
            'Radiance Ultra': self.ndssi_10_4002_Ultra,
            'Radiance Ultra 4K': self.ndssi_10_4002_4K,
        }
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveWindow': {'Status': {}},
            'AutoSource': {'Status': {}},
            'DiscState': {'Status': {}},
            'DisplayStatus': {'Status': {}},
            'FlipOrRotate': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'Mirroring': {'Status': {}},
            'Overscan': {'Status': {}},
            'PIP': {'Status': {}},
            'PortNameCommand': {'Parameters': ['Input'], 'Status': {}},
            'PortNameStatus': {'Parameters': ['Input'], 'Status': {}},
            'Scaling': {'Status': {}},
            'SwapPrimaryAndSecondary': {'Status': {}},
        }

    def CalCRC(self, Data):
        Crc = 0
        for i in range(0, len(Data)):
            Crc = Crc + Data[i]
            Crc_hig = hex(int(((Crc % 256) & 0xF0) / 16))[2:].upper()
            Crc_low = hex((Crc % 256) & 0x0F)[2:].upper()
        return (Crc_hig, Crc_low)

    def SetActiveWindow(self, value, qualifier):

        ValueStateValues = {
            'Primary': b'01140000',
            'Secondary': b'01140001'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        ActiveWindowCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('ActiveWindow', ActiveWindowCmdString, value, qualifier)

    def UpdateActiveWindow(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Primary',
            b'1': 'Secondary'
        }

        crc_high, crc_low = self.CalCRC(b'01150000')
        ActiveWindowCmdString = b''.join([b':', b'01150000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('ActiveWindow', ActiveWindowCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('ActiveWindow', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Active Window: Invalid/unexpected response'])

    def SetAutoSource(self, value, qualifier):

        crc_high, crc_low = self.CalCRC(self.AutoSourceValues[value])
        AutoSourceCmdString = b''.join([b':', self.AutoSourceValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('AutoSource', AutoSourceCmdString, value, qualifier)

    def UpdateAutoSource(self, value, qualifier):

        crc_high, crc_low = self.CalCRC(b'01100000')
        AutoSourceCmdString = b''.join([b':', b'01100000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('AutoSource', AutoSourceCmdString, value, qualifier)
        if res:
            try:
                value = self.AutoSourceNames[res[8:9]]
                self.WriteStatus('AutoSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Source: Invalid/unexpected response'])

    def SetDiscState(self, value, qualifier):

        ValueStateValues = {
            'Green': b'01060001',
            'White': b'01060002',
            'Red': b'01060003',
            'Off': b'01060000'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        DiscStateCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('DiscState', DiscStateCmdString, value, qualifier)

    def UpdateDiscState(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Green',
            b'2': 'White',
            b'3': 'Red',
            b'0': 'Off'
        }

        crc_high, crc_low = self.CalCRC(b'01110000')
        DiscStateCmdString = b''.join([b':', b'01110000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('DiscState', DiscStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('DiscState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Disc State: Invalid/unexpected response'])

    def UpdateDisplayStatus(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Operating',
            b'0': 'Not Operating'
        }

        crc_high, crc_low = self.CalCRC(b'01160000')
        DisplayStatusCmdString = b''.join([b':', b'01160000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('DisplayStatus', DisplayStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('DisplayStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Status: Invalid/unexpected response'])

    def SetFlipOrRotate(self, value, qualifier):

        ValueStateValues = {
            'Off': b'013E0000',
            'Horizontal Flip On': b'013E0001',
            'Vertical Flip On': b'013E0002',
            '90 Degree Rotate': b'013E0003',
            '180 Degree Rotate': b'013E0004',
            '270 Degree Rotate': b'013E0005'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        FlipOrRotateCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('FlipOrRotate', FlipOrRotateCmdString, value, qualifier)

    def UpdateFlipOrRotate(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Off',
            b'1': 'Horizontal Flip On',
            b'2': 'Vertical Flip On',
            b'3': '90 Degree Rotate',
            b'4': '180 Degree Rotate',
            b'5': '270 Degree Rotate'
        }

        crc_high, crc_low = self.CalCRC(b'013F0000')
        FlipOrRotateCmdString = b''.join([b':', b'013F0000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('FlipOrRotate', FlipOrRotateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('FlipOrRotate', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Flip Or Rotate: Invalid/unexpected response'])

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            '1.8': b'012B0001',
            '2.0': b'012B0002',
            '2.2': b'012B0003',
            '2.4': b'012B0004',
            '2.6': b'012B0005',
            'Video': b'012B0006',
            'PACS': b'012B0007'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        GammaCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        ValueStateValues = {
            b'1': '1.8',
            b'2': '2.0',
            b'3': '2.2',
            b'4': '2.4',
            b'5': '2.6',
            b'6': 'Video',
            b'7': 'PACS'
        }

        crc_high, crc_low = self.CalCRC(b'012C0000')
        GammaCmdString = b''.join([b':', b'012C0000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Gamma: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        FormatStates = {
            'DVI': b'0000',
            'SDI': b'0001',
            'RGBS': b'0002',
            'YPbPr': b'0003',
            'VGA': b'0004',
            'SOG': b'0005',
            'S-Video': b'0006',
            'Composite': b'0007'
        }

        if qualifier and 'Format' in qualifier:
            frmt_val = qualifier['Format']
            if frmt_val in FormatStates:
                crc_high, crc_low = self.CalCRC(self.InputStates[value][2] + FormatStates[frmt_val])
                InputCmdString = b''.join([b':', self.InputStates[value][2], FormatStates[frmt_val], crc_high.encode(), crc_low.encode(), b'\r'])
                self.__SetHelper('Input', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')
        else:
            crc_high, crc_low = self.CalCRC(self.InputStates[value][2])
            InputCmdString = b''.join([b':', self.InputStates[value][2], crc_high.encode(), crc_low.encode(), b'\r'])
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        FormatStates = {
            b'0': 'DVI',
            b'1': 'SDI',
            b'2': 'RGBS',
            b'3': 'YPbPr',
            b'4': 'VGA',
            b'5': 'SOG',
            b'6': 'S-Video',
            b'7': 'Composite'
        }

        crc_high, crc_low = self.CalCRC(self.InputQuery)
        InputCmdString = b''.join([b':', self.InputQuery, crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 12:  # No format field in response
                    value = self.InputNames[res[7:9]]
                    self.WriteStatus('Input', value, qualifier)
                else:
                    value = self.InputNames[res[7:9]]
                    self.WriteStatus('Input', value, {'Format': FormatStates[res[12:13]]})
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMirroring(self, value, qualifier):

        ValueStateValues = {
            'On': b'013E0001',
            'Off': b'013E0000'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        MirroringCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('Mirroring', MirroringCmdString, value, qualifier)

    def UpdateMirroring(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Off',
            b'1': 'On'
        }

        crc_high, crc_low = self.CalCRC(b'013F0000')
        MirroringCmdString = b''.join([b':', b'013F0000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('Mirroring', MirroringCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('Mirroring', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mirroring: Invalid/unexpected response'])

    def SetOverscan(self, value, qualifier):

        ValueStateValues = {
            'Off': b'01320000',
            'Step 1': b'01320001',
            'Step 2': b'01320002',
            'Step 3': b'01320003',
            'Step 4': b'01320004',
            'Step 5': b'01320005',
            'Step 6': b'01320006'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        OverscanCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('Overscan', OverscanCmdString, value, qualifier)

    def UpdateOverscan(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Off',
            b'1': 'Step 1',
            b'2': 'Step 2',
            b'3': 'Step 3',
            b'4': 'Step 4',
            b'5': 'Step 5',
            b'6': 'Step 6'
        }

        crc_high, crc_low = self.CalCRC(b'01330000')
        OverscanCmdString = b''.join([b':', b'01330000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('Overscan', OverscanCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('Overscan', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Overscan: Invalid/unexpected response'])

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Primary Only': b'01170000',
            'Small Secondary Size': b'01170001',
            'Medium Secondary Size': b'01170002',
            'Half (Side-by-side) Size': b'01170003',
            'Oversized (Side-by-side) Size': b'01170004'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        PIPCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Primary Only',
            b'1': 'Small Secondary Size',
            b'2': 'Medium Secondary Size',
            b'3': 'Half (Side-by-side) Size',
            b'4': 'Oversized (Side-by-side) Size'
        }

        crc_high, crc_low = self.CalCRC(b'01190000')
        PIPCmdString = b''.join([b':', b'01190000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP: Invalid/unexpected response'])

    def SetPortNameCommand(self, value, qualifier):

        portName = value
        if value:
            input_val = qualifier['Input']
            if portName and len(portName) <= 20 and input_val in self.InputStates:
                cmd_val = self.InputStates[input_val][0] + portName.encode()
                crc_high, crc_low = self.CalCRC(cmd_val)
                PortNameCommandCmdString = b''.join([b':', cmd_val, crc_high.encode(), crc_low.encode(), b'\r'])
                self.__SetHelper('PortNameCommand', PortNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPortNameCommand, missing String for value')

    def UpdatePortNameStatus(self, value, qualifier):

        input_val = qualifier['Input']
        if input_val in self.InputStates:
            crc_high, crc_low = self.CalCRC(self.InputStates[input_val][1])
            PortNameStatusCmdString = b''.join([b':', self.InputStates[input_val][1], crc_high.encode(), crc_low.encode(), b'\r'])
            res = self.__UpdateHelper('PortNameStatus', PortNameStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res[5:-3].decode()
                    self.WriteStatus('PortNameStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Port Name Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePortNameStatus')

    def SetScaling(self, value, qualifier):

        ValueStateValues = {
            'Fill': b'01300000',
            'Aspect': b'01300001',
            '1:1': b'01300002'
        }

        crc_high, crc_low = self.CalCRC(ValueStateValues[value])
        ScalingCmdString = b''.join([b':', ValueStateValues[value], crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('Scaling', ScalingCmdString, value, qualifier)

    def UpdateScaling(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Fill',
            b'1': 'Aspect',
            b'2': '1:1'
        }

        crc_high, crc_low = self.CalCRC(b'01310000')
        ScalingCmdString = b''.join([b':', b'01310000', crc_high.encode(), crc_low.encode(), b'\r'])
        res = self.__UpdateHelper('Scaling', ScalingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8:9]]
                self.WriteStatus('Scaling', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Scaling: Invalid/unexpected response'])

    def SetSwapPrimaryAndSecondary(self, value, qualifier):

        crc_high, crc_low = self.CalCRC(b'01180000')
        SwapPrimaryAndSecondaryCmdString = b''.join([b':', b'01180000', crc_high.encode(), crc_low.encode(), b'\r'])
        self.__SetHelper('SwapPrimaryAndSecondary', SwapPrimaryAndSecondaryCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'1': "Unrecognized Command.",
            b'2': "Invalid Command Checksum.",
            b'3': "Invalid Command Start Character.",
            b'4': "Invalid Command Data Field."
        }
        if response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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

    def ndssi_10_4002_4K(self):
        self.Commands['Input'] = {'Parameters': ['Format'], 'Status': {}}
        self.AutoSourceValues = {
            'On': b'01040001',
            'Off': b'01040000',
            'Priority': b'01040002'
        }
        self.AutoSourceNames = {
            b'1': 'On',
            b'0': 'Off',
            b'2': 'Off'
        }

        self.InputQuery = b'010C0001'

        self.InputStates = {
            '4x3G-SDI / 12G-SDI': [b'01380000', b'01390000', b'01000000'],
            '3G-SDI-5': [b'01380008', b'01390008', b'01000008'],
            'DVI 1': [b'01380005', b'01390005', b'01000005'],
            'DVI 2': [b'01380009', b'01390009', b'01000009'],
            'DisplayPort': [b'0138000C', b'0139000C', b'0100000C'],
            'HDMI 1': [b'0138000D', b'0139000D', b'0100000D'],
            'HDMI 2': [b'01380012', b'01390012', b'01000012']
        }
        self.InputNames = {
            b'00': '4x3G-SDI / 12G-SDI',
            b'08': '3G-SDI-5',
            b'05': 'DVI 1',
            b'09': 'DVI 2',
            b'0C': 'DisplayPort',
            b'0D': 'HDMI 1',
            b'12': 'HDMI 2'
        }

    def ndssi_10_4002_Ultra(self):
        self.Commands['Input'] = {'Parameters': ['Format'], 'Status': {}}
        self.AutoSourceValues = {
            'On': b'01040001',
            'Off': b'01040000',
            'Priority': b'01040002'
        }
        self.AutoSourceNames = {
            b'1': 'On',
            b'0': 'Off',
            b'2': 'Off'
        }

        self.InputQuery = b'010C0001'

        self.InputStates = {
            'SDI 1': [b'01380000', b'01390000', b'01000000'],
            'SDI 2': [b'01380008', b'01390008', b'01000008'],
            'VGA 1': [b'01380001', b'01390001', b'01000001'],
            'VGA 2': [b'0138000E', b'0139000E', b'0100000E'],
            'RGBS 1': [b'01380002', b'01390002', b'01000002'],
            'RGBS 2': [b'0138000F', b'0139000F', b'0100000F'],
            'DVI 1': [b'01380005', b'01390005', b'01000005'],
            'DVI 2': [b'01380009', b'01390009', b'01000009'],
            'DVI Fiber': [b'0138000A', b'0139000A', b'0100000A'],
            'S-Video': [b'01380004', b'01390004', b'01000004'],
            'YPbPr 1': [b'01380003', b'01390003', b'01000003'],
            'YPbPr 2': [b'01380011', b'01390011', b'01000011'],
            'Composite': [b'01380006', b'01390006', b'01000006'],
            'HDMI': [b'0138000D', b'0139000D', b'0100000D'],
            'DisplayPort': [b'0138000C', b'0139000C', b'0100000C'],
            'ZeroWire': [b'01380010', b'01390010', b'01000010'],
            'SOG 1': [b'01380007', b'01390007', b'01000007'],
            'SOG 2': [b'0138000B', b'0139000B', b'0100000B']
        }
        self.InputNames = {
            b'00': 'SDI 1',
            b'08': 'SDI 2',
            b'01': 'VGA 1',
            b'0E': 'VGA 2',
            b'02': 'RGBS 1',
            b'0F': 'RGBS 2',
            b'05': 'DVI 1',
            b'09': 'DVI 2',
            b'0A': 'DVI Fiber',
            b'04': 'S-Video',
            b'03': 'YPbPr 1',
            b'11': 'YPbPr 2',
            b'06': 'Composite',
            b'0D': 'HDMI',
            b'0C': 'DisplayPort',
            b'10': 'ZeroWire',
            b'07': 'SOG 1',
            b'0B': 'SOG 2'
        }

    def ndssi_10_4002_G2(self):

        self.AutoSourceValues = {
            'On': b'01040001',
            'Off': b'01040000'
        }
        self.AutoSourceNames = {
            b'1': 'On',
            b'0': 'Off'
        }

        self.InputQuery = b'010C0000'

        self.InputStates = {
            'SDI 1': [b'01380000', b'01390000', b'01000000'],
            'SDI 2': [b'01380008', b'01390008', b'01000008'],
            'VGA': [b'01380001', b'01390001', b'01000001'],
            'RGBS': [b'01380002', b'01390002', b'01000002'],
            'YPbPr': [b'01380003', b'01390003', b'01000003'],
            'S-Video': [b'01380004', b'01390004', b'01000004'],
            'DVI 1': [b'01380005', b'01390005', b'01000005'],
            'DVI 2': [b'01380009', b'01390009', b'01000009'],
            'Composite': [b'01380006', b'01390006', b'01000006'],
            'SOG 1': [b'01380007', b'01390007', b'01000007'],
            'SOG 2': [b'0138000B', b'0139000B', b'0100000B'],
            'DVI Fiber': [b'0138000A', b'0139000A', b'0100000A'],
            'ZeroWire': [b'01380010', b'01390010', b'01000010']
        }
        self.InputNames = {
            b'00': 'SDI 1',
            b'08': 'SDI 2',
            b'01': 'VGA',
            b'02': 'RGBS',
            b'03': 'YPbPr',
            b'04': 'S-Video',
            b'05': 'DVI 1',
            b'09': 'DVI 2',
            b'06': 'Composite',
            b'07': 'SOG 1',
            b'0B': 'SOG 2',
            b'0A': 'DVI Fiber',
            b'10': 'ZeroWire'
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
