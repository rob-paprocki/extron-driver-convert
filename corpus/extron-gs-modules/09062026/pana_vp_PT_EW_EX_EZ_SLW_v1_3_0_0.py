from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import re
import hashlib
from binascii import hexlify


class DeviceSerialClass:
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
            'PT-EZ770Z': self.pana_1_326_A,
            'PT-EW540L': self.pana_1_326_D,
            'PT-SLX80CL': self.pana_1_326_A,
            'PT-SLX75C': self.pana_1_326_B,
            'PT-SLX75CL': self.pana_1_326_B,
            'PT-SLW65C': self.pana_1_326_D,
            'PT-SLW65CL': self.pana_1_326_D,
            'PT-SLX62C': self.pana_1_326_D,
            'PT-SLX62CL': self.pana_1_326_D,
            'PT-EW730Z': self.pana_1_326_A,
            'PT-EW730ZL': self.pana_1_326_A,
            'PT-EX800ZL': self.pana_1_326_A,
            'PT-EZ580L': self.pana_1_326_C,
            'PT-EW640': self.pana_1_326_C,
            'PT-EW640L': self.pana_1_326_C,
            'PT-EW540': self.pana_1_326_D,
            'PT-EX610': self.pana_1_326_C,
            'PT-EX610L': self.pana_1_326_C,
            'PT-EX510': self.pana_1_326_D,
            'PT-EX510L': self.pana_1_326_D,
            'PT-SLZ77C': self.pana_1_326_A,
            'PT-SLZ77CL': self.pana_1_326_A,
            'PT-SLW83C': self.pana_1_326_A,
            'PT-SLW83CL': self.pana_1_326_A,
            'PT-SLX80C': self.pana_1_326_A,
            'PT-EZ580': self.pana_1_326_C,
            'PT-EZ770ZL': self.pana_1_326_A,
            'PT-EX800Z': self.pana_1_326_A,
            'PT-EW540E': self.pana_1_326_D,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPFrameLock': {'Status': {}},
            'PIPHandVMagnification': {'Parameters': ['PIP Type'], 'Status': {}},
            'PIPInput': {'Parameters': ['PIP Type'], 'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self._DeviceID = '\x02AD01;'

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '\x02ADZZ;'
        elif 1 <= int(value) <= 64:
            self._DeviceID = '\x02AD' + value.zfill(2) + ';'

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Normal': '0\x03',
            '4:3': '1\x03',
            'Wide': '2\x03',
            'Native': '5\x03',
            'Full': '6\x03',
            'H Fit': '9\x03',
            'V Fit': '10\x03'
        }
        AspectRatioCmdString = self._DeviceID + 'VSE:' + AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNames = {
            b'0\x03': 'Normal',
            b'1\x03': '4:3',
            b'2\x03': 'Wide',
            b'5\x03': 'Native',
            b'6\x03': 'Full',
            b'9\x03': 'H Fit',
            b'10\x03': 'V Fit'
        }
        AspectRatioCmdString = self._DeviceID.encode() + b'QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[1:]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Aspect Ratio'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self._DeviceID + 'OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'CC1': '1\x03',
            'CC2': '2\x03',
            'CC3': '3\x03',
            'CC4': '4\x03',
            'Off': '0\x03'
        }
        ClosedCaptionCmdString = self._DeviceID + 'OCC:' + ClosedCaptionStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionStateNames = {
            b'1\x03': 'CC1',
            b'2\x03': 'CC2',
            b'3\x03': 'CC3',
            b'4\x03': 'CC4',
            b'0\x03': 'Off'
        }
        ClosedCaptionCmdString = self._DeviceID.encode() + b'QCC\x03'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateNames[res[1:]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Closed Caption'])

    def UpdateDeviceStatus(self, value, qualifier):

        ErrorString = ''
        Errors = 0

        States = {
            '0': 'Intake Air Temperature Warning',
            '2': 'Exhaust Temperature Warning',
            '4': 'Intake Air Temperature Error',
            '6': 'Exhaust Temperature Error',
            '8': 'Lamp Warning',
            '12': 'Lamp Runtime Error (Shut Down)',
            '16': 'Lamp Error',
            '20': 'Lamp Ignition Error',
            '24': 'Lamp Mounting Error',
            '29': 'Lamp Cover Error',
            '32': 'Disconnect Intake Fan Temperature Sensor',
            '34': 'Disconnect Exhaust Fan Temperature Sensor',
            '35': 'Disconnect Clogged Sensor Cable',
            '36': 'Air Filter Clogged',
            '37': 'Clock Battery Low',
            '38': 'Angle Sensor Error',
            '40': 'No Air Filter Installed',
            '42': 'Fan 1 Error',
            '43': 'Fan 2 Error',
            '44': 'Fan 3 Error',
            '45': 'Fan 4 Error',
            '46': 'Fan 5 Error',
            '47': 'Fan 6 Error',
            '48': 'Fan 7 Error',
            '49': 'Fan 8 Error',
            '66': 'Shutter Error',
            '67': 'Iris Error',
            '72': 'Lamp Not Initialized',
            '80': 'FPGA1 Configure Error',
            '86': 'Lens Mounter Operation Error',
            '87': 'Ballast Communication Error',
            '91': 'Optical Output Limitation',
            '92': 'Gamma Data Not Saved',
            '93': 'Color Shading Correction Data Not Saved',
            '94': 'Pressure Sensor Error',
            '95': 'Portrait Warning',
            '97': 'Network CPU Communication Error',
            '98': 'Sub CPU Communication Error',
            '99': 'Internal Communication Error',
            '100': 'Internal Communication Error',
            '101': 'Internal Communication Error',
            '105': 'Internal Communication Error',
            '106': 'Internal Communication Error',
            '107': 'Internal Communication Error',
            '108': 'Internal Communication Error',
            '109': 'Internal Communication Error',
            '110': 'Internal Communication Error',
            '111': 'Internal Communication Error',
            '112': 'Internal Communication Error',
            '113': 'Internal Communication Error',
            '114': 'Internal Communication Error',
            '115': 'A-PRINT Not Initialized',
            '127': 'Internal Error',
        }

        res = self.__UpdateHelper('DeviceStatus', b'\x02\x00\xFE\x03', value, qualifier)
        if res:

            try:
                res = int.from_bytes(res[4:19], byteorder='big')

                for i in range(0, 128):
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

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '1\x03',
            'Off': '0\x03'
        }
        FreezeCmdString = self._DeviceID + 'OFZ:' + FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            b'0\x03': 'Off',
            b'1\x03': 'On'
        }
        FreezeCmdString = self._DeviceID.encode() + b'QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[1:]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Freeze'])

    def SetInput(self, value, qualifier):

        InputCmdString = self._DeviceID + 'IIS:' + self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)  # query delay of 10 implemented same as legacy

    def UpdateInput(self, value, qualifier):
        InputCmdString = self._DeviceID.encode() + b'QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res[1:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Input'])

    def SetLampPower(self, value, qualifier):

        LampPowerCmdString = self._DeviceID + 'VXX:LPWI1=+000' + self.LampPowerStateValues[value]
        self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)  ##query delay of 10 implemented same as legacy

    def UpdateLampPower(self, value, qualifier):
        
        LampPowerCmdString = self._DeviceID.encode() + b'QVX:LPWI1\x03'
        res = self.__UpdateHelper('LampPower', LampPowerCmdString, value, qualifier)
        if res:
            try:
                value = self.LampPowerStateNames[res[15:]]
                self.WriteStatus('LampPower', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Lamp Power'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = self._DeviceID.encode() + b'Q$L:1\x03'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:5])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Lamp Usage'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up': b'OCU\x03',
            'Down': b'OCD\x03',
            'Left': b'OCL\x03',
            'Right': b'OCR\x03',
            'Enter': b'OEN\x03',
            'Menu': b'OMN\x03'
        }
        MenuNavigationCmdString = self._DeviceID.encode() + MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = self._DeviceID.encode() + b'QST\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:6])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Operation Hours'])

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural': 'NAT\x03',
            'Standard': 'STD\x03',
            'Dynamic': 'DYN\x03',
            'Cinema': 'CIN\x03',
            'Dicom Sim': 'DIC\x03'
        }
        PictureModeCmdString = self._DeviceID + 'VPM:' + PictureModeStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeStateNames = {
            b'NA': 'Natural',
            b'ST': 'Standard',
            b'DY': 'Dynamic',
            b'CI': 'Cinema',
            b'DI': 'Dicom Sim',
        }
        PictureModeCmdString = self._DeviceID.encode() + b'QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[1:3]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Picture Mode'])

    def SetPIPFrameLock(self, value, qualifier):

        PIPFrameLockStateValues = {
            'Main Window': '0\x03',
            'Sub Window': '1\x03'
        }
        PIPFrameLockCmdString = self._DeviceID + 'PFL:' + PIPFrameLockStateValues[value]
        self.__SetHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)

    def UpdatePIPFrameLock(self, value, qualifier):

        PIPFrameLockStateNames = {
            b'0\x03': 'Main Window',
            b'1\x03': 'Sub Window'
        }
        PIPFrameLockCmdString = self._DeviceID.encode() + b'QPF\x03'
        res = self.__UpdateHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)
        if res:
            try:
                value = PIPFrameLockStateNames[res[1:]]
                self.WriteStatus('PIPFrameLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Frame Lock'])

    def SetPIPHandVMagnification(self, value, qualifier):

        PipTypeValues = {
            'Main': b'MSZ:',
            'Sub': b'SSZ:'
        }

        PipType = qualifier['PIP Type']
        PipType = PipTypeValues[PipType]

        PIPHandVMagnificationStateValues = {
            '10': b'010\x03',
            '20': b'020\x03',
            '30': b'030\x03',
            '40': b'040\x03',
            '50': b'050\x03',
            '60': b'060\x03',
            '70': b'070\x03',
            '80': b'080\x03',
            '90': b'090\x03',
            '100': b'100\x03'
        }
        PIPHandVMagnificationCmdString = self._DeviceID.encode() + PipType + PIPHandVMagnificationStateValues[value]
        self.__SetHelper('PIPHandVMagnification', PIPHandVMagnificationCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        PIPInputTypeValues = {
            'Main': 'MSI:',
            'Sub': 'SIS:'
        }

        PIPInputType = qualifier['PIP Type']
        PIPInputType = PIPInputTypeValues[PIPInputType]

        PIPInputCmdString = self._DeviceID + PIPInputType + self.PIPInputStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputTypeValues = {
            'Main': b'QIM',
            'Sub': b'QIS'
        }

        PIPInputType = qualifier['PIP Type']
        PIPInputType = PIPInputTypeValues[PIPInputType]
        PIPInputCmdString = self._DeviceID.encode() + PIPInputType + b'\x03'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPInputStateNames[res[1:]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for PIP Input'])

    def SetPIPMode(self, value, qualifier):

        PIPModeStateValues = {
            'User 1': '1\x03',
            'User 2': '2\x03',
            'User 3': '3\x03',
            'Off': '0\x03'
        }
        PIPModeCmdString = self._DeviceID + 'OPP:' + PIPModeStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeStateNames = {
            b'1': 'User 1',
            b'2': 'User 2',
            b'3': 'User 3',
            b'0': 'Off'
        }
        PIPModeCmdString = self._DeviceID.encode() + b'QPP\x03'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeStateNames[res[1:2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for PIP Mode'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': 'PON\x03',
            'Off': 'POF\x03'
        }
        PowerCmdString = self._DeviceID + PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'2': 'On',
            b'1': 'Warming Up',
            b'3': 'Cooling Down',
            b'0': 'Off'
        }
        PowerCmdString = self._DeviceID.encode() + b'Q$S\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

        if res:
            try:
                value = PowerStateNames[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Power'])

    def SetShutter(self, value, qualifier):

        ShutterStateValues = {
            'On': '1\x03',
            'Off': '0\x03'
        }
        ShutterCmdString = self._DeviceID + 'OSH:' + ShutterStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)  ##query delay of 3 implemented same as legacy

    def UpdateShutter(self, value, qualifier):

        ShutterStateNames = {
            b'1\x03': 'On',
            b'0\x03': 'Off'
        }
        ShutterCmdString = self._DeviceID.encode() + b'QSH\x03'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ShutterStateNames[res[1:]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Shutter'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            VolumeCmdString = self._DeviceID.encode() + b'AVL:' + str(value).zfill(3).encode() + b'\x03'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self._DeviceID.encode() + b'QAV\x03'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Volume'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {b'\x02ER401\x03': 'Invalid Command.',
                              b'\x02ER402\x03': 'Invalid Parameter'}
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or self._DeviceID == '\x02ADZZ;':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['Invalid/unexpected response for {}'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '\x02ADZZ;':
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

    def pana_1_326_A(self):

        self.InputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03',
            'DisplayPort': 'DP1\x03',
            'Digital Link': 'DL1\x03'
        }

        self.InputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
            b'DP1\x03': 'DisplayPort',
            b'DL1\x03': 'Digital Link'
        }

        self.PIPInputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03',
            'DisplayPort': 'DP1\x03',
            'Digital Link': 'DL1\x03'
        }

        self.PIPInputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
            b'DP1\x03': 'DisplayPort',
            b'DL1\x03': 'Digital Link'
        }

        self.LampPowerStateValues = {
            'Eco 1': '20\x03',
            'Eco 2': '21\x03',
            'Normal': '01\x03',
            'Auto': '30\x03'
        }

        self.LampPowerStateNames = {
            b'20\x03': 'Eco 1',
            b'21\x03': 'Eco 2',
            b'01\x03': 'Normal',
            b'30\x03': 'Auto'
        }

    def pana_1_326_B(self):

        self.InputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03'
        }

        self.InputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI'
        }

        self.PIPInputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03'
        }

        self.PIPInputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
        }

        self.LampPowerStateValues = {
            'Eco 1': '20\x03',
            'Eco 2': '21\x03',
            'Normal': '01\x03',
            'Auto': '30\x03'
        }

        self.LampPowerStateNames = {
            b'20\x03': 'Eco 1',
            b'21\x03': 'Eco 2',
            b'01\x03': 'Normal',
            b'30\x03': 'Auto'
        }

    def pana_1_326_C(self):

        self.InputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03',
            'DisplayPort': 'DP1\x03',
            'Digital Link': 'DL1\x03'
        }

        self.InputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
            b'DP1\x03': 'DisplayPort',
            b'DL1\x03': 'Digital Link'
        }

        self.PIPInputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03',
            'DisplayPort': 'DP1\x03',
            'Digital Link': 'DL1\x03'
        }

        self.PIPInputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
            b'DP1\x03': 'DisplayPort',
            b'DL1\x03': 'Digital Link'
        }

        self.LampPowerStateValues = {
            'Eco': '00\x03',
            'Normal': '01\x03',
            'Auto': '30\x03'
        }

        self.LampPowerStateNames = {
            b'00\x03': 'Eco',
            b'01\x03': 'Normal',
            b'30\x03': 'Auto'
        }

    def pana_1_326_D(self):

        self.InputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03',
        }

        self.InputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
        }

        self.PIPInputStateValues = {
            'RGB 1': 'RG1\x03',
            'RGB 2': 'RG2\x03',
            'Video': 'VID\x03',
            'DVI': 'DVI\x03',
            'HDMI': 'HD1\x03',
        }

        self.PIPInputStateNames = {
            b'RG1\x03': 'RGB 1',
            b'RG2\x03': 'RGB 2',
            b'VID\x03': 'Video',
            b'DVI\x03': 'DVI',
            b'HD1\x03': 'HDMI',
        }

        self.LampPowerStateValues = {
            'Eco': '00\x03',
            'Normal': '01\x03',
            'Auto': '30\x03'
        }

        self.LampPowerStateNames = {
            b'00\x03': 'Eco',
            b'01\x03': 'Normal',
            b'30\x03': 'Auto'
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


class DeviceEthernetClass:
    def __init__(self):

        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {
            'PT-EZ770ZL': self.pana_1_326_A,
            'PT-EX800Z': self.pana_1_326_A,
            'PT-EZ580': self.pana_1_326_C,
            'PT-EW540': self.pana_1_326_D,
            'PT-EW640': self.pana_1_326_C,
            'PT-EW730Z': self.pana_1_326_A,
            'PT-EW730ZL': self.pana_1_326_A,
            'PT-EX510': self.pana_1_326_D,
            'PT-EX610': self.pana_1_326_C,
            'PT-EX800ZL': self.pana_1_326_A,
            'PT-EZ770Z': self.pana_1_326_A,
            'PT-EZ770ZE': self.pana_1_326_A,
            'PT-EW540E': self.pana_1_326_D,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Input': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

        self.md5hash = ''
        self.Security = False

        self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
        self.AddMatchString(re.compile(b'ERR([1-5A])\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            '4:3': '1',
            'Wide': '2',
            'Native': '5',
            'Full': '6',
            'H Fit': '9',
            'V Fit': '10'
        }

        AspectRatioCmdString = '00VSE:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        InputCmdString = '00IIS:{0}\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'User 1': '1',
            'User 2': '2',
            'User 3': '3',
            'Off': '0'
        }

        PIPModeCmdString = '00OPP:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShutterCmdString = '00OSH:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Security:
            self.Send(self.md5hash + commandstring.encode())
        else:
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorValue = {
            '1': 'Undefined control command',
            '2': 'Out of parameter range',
            '3': 'Busy state or no-acceptable period',
            '4': 'Timeout or no-acceptable period',
            '5': 'Wrong data length',
            'A': 'Password mismatch',
        }

        value = match.group(1).decode()
        self.Error([ErrorValue[value]])

    def pana_1_326_A(self):

        self.InputStateValues = {
            'Video': 'VID',
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'Digital Link': 'DL1',
            'DisplayPort': 'DP1'
        }

    def pana_1_326_B(self):

        self.InputStateValues = {
            'Video': 'VID',
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'DVI': 'DVI',
            'HDMI': 'HD1',
        }

    def pana_1_326_C(self):

        self.InputStateValues = {
            'Video': 'VID',
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'DVI': 'DVI',
            'HDMI': 'HD1',
            'Digital Link': 'DL1',
            'DisplayPort': 'DP1'
        }

    def pana_1_326_D(self):

        self.InputStateValues = {
            'Video': 'VID',
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'DVI': 'DVI',
            'HDMI': 'HD1',
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
