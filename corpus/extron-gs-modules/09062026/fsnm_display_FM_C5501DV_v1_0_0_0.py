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
            'AspectRatio': {'Status': {}},
            'Backlight': {'Status': {}},
            'Brightness': {'Status': {}},
            'ColorSpace': {'Status': {}},
            'ColorTemperature': {'Status': {}},
            'Contrast': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'PIPLayout': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Reset': {'Status': {}},
            'Rotate': {'Status': {}},
            'Saturation': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Vividness': {'Status': {}},
            'WindowSelect': {'Status': {}},
        }

        self.set_regex = re.compile(b'(ACK|NACK)')
        self.get_regex = re.compile(b'(ACK[\x30-\x35]{2}|NACK)')

    def CalCRC(self, Data):
        CRC = 0
        for i in range(0, len(Data)):
            CRC = CRC + Data[i]
        return CRC & 0xFF

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': 0x30,
            'Auto': 0x31,
            'Fill-H': 0x32
        }

        Data = [0x31, 0x32, 0x30, 0x0C, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        AspectRatioCmdString = pack('11B', 0x31, 0x32, 0x30, 0x0C, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Full',
            b'\x31': 'Auto',
            b'\x32': 'Fill-H'
        }

        Data = [0x31, 0x32, 0x30, 0x0C, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        AspectRatioCmdString = pack('11B', 0x31, 0x32, 0x30, 0x0C, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            val = str(value).zfill(3)
            Data = [0x31, 0x32, 0x30, 0x00, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48]
            crc = self.CalCRC(Data)
            BacklightCmdString = pack('11B', 0x31, 0x32, 0x30, 0x00, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48, crc, 0x33, 0x34)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x00, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        BacklightCmdString = pack('11B', 0x31, 0x32, 0x30, 0x00, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Backlight', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            val = str(value).zfill(3)
            Data = [0x31, 0x32, 0x30, 0x01, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48]
            crc = self.CalCRC(Data)
            BrightnessCmdString = pack('11B', 0x31, 0x32, 0x30, 0x01, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48, crc, 0x33, 0x34)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x01, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        BrightnessCmdString = pack('11B', 0x31, 0x32, 0x30, 0x01, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetColorSpace(self, value, qualifier):

        ValueStateValues = {
            'Native': 0x30,
            'sRGB': 0x31
        }

        Data = [0x31, 0x32, 0x30, 0x06, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        ColorSpaceCmdString = pack('11B', 0x31, 0x32, 0x30, 0x06, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('ColorSpace', ColorSpaceCmdString, value, qualifier)

    def UpdateColorSpace(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Native',
            b'\x31': 'sRGB'
        }

        Data = [0x31, 0x32, 0x30, 0x06, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        ColorSpaceCmdString = pack('11B', 0x31, 0x32, 0x30, 0x06, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('ColorSpace', ColorSpaceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('ColorSpace', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color Space: Invalid/unexpected response'])

    def SetColorTemperature(self, value, qualifier):

        ValueStateValues = {
            'C1': 0x30,
            'C2': 0x31,
            'C3': 0x32,
            'User': 0x33
        }

        Data = [0x31, 0x32, 0x30, 0x08, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        ColorTemperatureCmdString = pack('11B', 0x31, 0x32, 0x30, 0x08, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)

    def UpdateColorTemperature(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'C1',
            b'\x31': 'C2',
            b'\x32': 'C3',
            b'\x33': 'User'
        }

        Data = [0x31, 0x32, 0x30, 0x08, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        ColorTemperatureCmdString = pack('11B', 0x31, 0x32, 0x30, 0x08, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('ColorTemperature', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color Temperature: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            val = str(value).zfill(3)
            Data = [0x31, 0x32, 0x30, 0x02, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48]
            crc = self.CalCRC(Data)
            ContrastCmdString = pack('11B', 0x31, 0x32, 0x30, 0x02, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48, crc, 0x33, 0x34)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x02, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        ContrastCmdString = pack('11B', 0x31, 0x32, 0x30, 0x02, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Contrast', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Contrast: Invalid/unexpected response'])

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            'Bypass': 0x30,
            '1.8': 0x31,
            '2.0': 0x32,
            '2.2': 0x33,
            '2.4': 0x34,
            '2.6': 0x35,
            'DICOM': 0x36
        }

        Data = [0x31, 0x32, 0x30, 0x05, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        GammaCmdString = pack('11B', 0x31, 0x32, 0x30, 0x05, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Bypass',
            b'\x31': '1.8',
            b'\x32': '2.0',
            b'\x33': '2.2',
            b'\x34': '2.4',
            b'\x35': '2.6',
            b'\x36': 'DICOM'
        }

        Data = [0x31, 0x32, 0x30, 0x05, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        GammaCmdString = pack('11B', 0x31, 0x32, 0x30, 0x05, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Gamma: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1 SST': (0x30, 0x31),
            'DisplayPort 2 SST': (0x30, 0x32),
            'HDMI': (0x30, 0x33),
            'Dual DVI 1': (0x31, 0x34),
            'Dual DVI 2': (0x32, 0x34),
            'Dual DVI-Dual': (0x35, 0x34),
            'DVI': (0x30, 0x35)
        }

        Data = [0x31, 0x32, 0x30, 0x0E, 0x30, 0x30, ValueStateValues[value][0], ValueStateValues[value][1]]
        crc = self.CalCRC(Data)
        InputCmdString = pack('11B', 0x31, 0x32, 0x30, 0x0E, 0x30, 0x30, ValueStateValues[value][0], ValueStateValues[value][1], crc, 0x33, 0x34)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x30\x31': 'DisplayPort 1 SST',
            b'\x30\x32': 'DisplayPort 2 SST',
            b'\x30\x33': 'HDMI',
            b'\x31\x34': 'Dual DVI 1',
            b'\x32\x34': 'Dual DVI 2',
            b'\x35\x34': 'Dual DVI-Dual',
            b'\x30\x35': 'DVI'
        }

        Data = [0x31, 0x32, 0x30, 0x0E, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        InputCmdString = pack('11B', 0x31, 0x32, 0x30, 0x0E, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPIPLayout(self, value, qualifier):

        ValueStateValues = {
            'Single': 0x30,
            'PBP': 0x31,
            'PIP': 0x33
        }

        Data = [0x31, 0x32, 0x30, 0x0F, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        PIPLayoutCmdString = pack('11B', 0x31, 0x32, 0x30, 0x0F, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)

    def UpdatePIPLayout(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Single',
            b'\x31': 'PBP',
            b'\x33': 'PIP'
        }

        Data = [0x31, 0x32, 0x30, 0x0F, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        PIPLayoutCmdString = pack('11B', 0x31, 0x32, 0x30, 0x0F, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PIPLayout', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Layout: Invalid/unexpected response'])

    def SetPIPSwap(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x11, 0x30, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        PIPSwapCmdString = pack('11B', 0x31, 0x32, 0x30, 0x11, 0x30, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetReset(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x12, 0x30, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        ResetCmdString = pack('11B', 0x31, 0x32, 0x30, 0x12, 0x30, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)

    def SetRotate(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0x30,
            '180 Degree': 0x31,
            'H-Mirror': 0x32,
            'V-Mirror': 0x33
        }

        Data = [0x31, 0x32, 0x30, 0x14, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        RotateCmdString = pack('11B', 0x31, 0x32, 0x30, 0x14, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('Rotate', RotateCmdString, value, qualifier)

    def UpdateRotate(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Normal',
            b'\x31': '180 Degree',
            b'\x32': 'H-Mirror',
            b'\x33': 'V-Mirror'
        }

        Data = [0x31, 0x32, 0x30, 0x14, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        RotateCmdString = pack('11B', 0x31, 0x32, 0x30, 0x14, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Rotate', RotateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Rotate', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Rotate: Invalid/unexpected response'])

    def SetSaturation(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            val = str(value).zfill(3)
            Data = [0x31, 0x32, 0x30, 0x03, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48]
            crc = self.CalCRC(Data)
            SaturationCmdString = pack('11B', 0x31, 0x32, 0x30, 0x03, 0x30, int(val[0]) + 48, int(val[1]) + 48, int(val[2]) + 48, crc, 0x33, 0x34)
            self.__SetHelper('Saturation', SaturationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaturation')

    def UpdateSaturation(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x03, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        SaturationCmdString = pack('11B', 0x31, 0x32, 0x30, 0x03, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Saturation', SaturationCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Saturation', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Saturation: Invalid/unexpected response'])

    def SetSharpness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 4
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Data = [0x31, 0x32, 0x30, 0x04, 0x30, 0x30, 0x30, value + 48]
            crc = self.CalCRC(Data)
            SharpnessCmdString = pack('11B', 0x31, 0x32, 0x30, 0x04, 0x30, 0x30, 0x30, value + 48, crc, 0x33, 0x34)
            self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):

        Data = [0x31, 0x32, 0x30, 0x04, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        SharpnessCmdString = pack('11B', 0x31, 0x32, 0x30, 0x04, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Sharpness', SharpnessCmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                self.WriteStatus('Sharpness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Sharpness: Invalid/unexpected response'])

    def SetVividness(self, value, qualifier):

        ValueStateValues = {
            'Off': 0x30,
            'Low': 0x31,
            'Mid': 0x32,
            'High': 0x33
        }

        Data = [0x31, 0x32, 0x30, 0x07, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        VividnessCmdString = pack('11B', 0x31, 0x32, 0x30, 0x07, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('Vividness', VividnessCmdString, value, qualifier)

    def UpdateVividness(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Off',
            b'\x31': 'Low',
            b'\x32': 'Mid',
            b'\x33': 'High'
        }

        Data = [0x31, 0x32, 0x30, 0x07, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        VividnessCmdString = pack('11B', 0x31, 0x32, 0x30, 0x07, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('Vividness', VividnessCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Vividness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Vividness: Invalid/unexpected response'])

    def SetWindowSelect(self, value, qualifier):

        ValueStateValues = {
            'Left or Main': 0x30,
            'Right or Sub': 0x31
        }

        Data = [0x31, 0x32, 0x30, 0x10, 0x30, 0x30, 0x30, ValueStateValues[value]]
        crc = self.CalCRC(Data)
        WindowSelectCmdString = pack('11B', 0x31, 0x32, 0x30, 0x10, 0x30, 0x30, 0x30, ValueStateValues[value], crc, 0x33, 0x34)
        self.__SetHelper('WindowSelect', WindowSelectCmdString, value, qualifier)

    def UpdateWindowSelect(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Left or Main',
            b'\x31': 'Right or Sub'
        }

        Data = [0x31, 0x32, 0x30, 0x10, 0x31, 0x30, 0x30, 0x30]
        crc = self.CalCRC(Data)
        WindowSelectCmdString = pack('11B', 0x31, 0x32, 0x30, 0x10, 0x31, 0x30, 0x30, 0x30, crc, 0x33, 0x34)
        res = self.__UpdateHelper('WindowSelect', WindowSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('WindowSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Window Select: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0:1] == b'N':
            self.Error(['{}: Command Failed.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
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

            if command == 'Input':
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.get_regex)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=4)

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
