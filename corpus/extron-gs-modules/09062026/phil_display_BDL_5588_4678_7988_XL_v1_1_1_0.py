from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
from re import compile, search

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
        self._GroupID = 0
        self.Models = {
            'BDL-5588XL': self.phil_10_1514_88XL,
            'BDL-4678XL': self.phil_10_1514_4678,
            'BDL-4988XL': self.phil_10_1514_88XL,
            'BDL-4988XC': self.phil_10_1514_88XL,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Monitor ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Monitor ID'], 'Status': {}},
            'Input': {'Parameters': ['Monitor ID'], 'Status': {}},
            'IRControl': {'Parameters': ['Monitor ID'], 'Status': {}},
            'KeypadControl': {'Parameters': ['Monitor ID'], 'Status': {}},
            'MasterPower': {'Status': {}},
            'OperationHours': {'Parameters': ['Monitor ID'], 'Status': {}},
            'PictureInPicture': {'Parameters': ['Monitor ID'], 'Status': {}},
            'PictureInPictureSourceSet': {'Parameters': ['Monitor ID', 'Quadrant 2', 'Quadrant 3', 'Quadrant 4'], 'Status': {}},
            'PictureInPictureSourceStatus': {'Parameters': ['Monitor ID', 'Quadrant'], 'Status': {}},
            'Power': {'Parameters': ['Monitor ID'], 'Status': {}},
            'TilingEnableStatus': {'Parameters': ['Monitor ID'], 'Status': {}},
            'TilingFrameCompStatus': {'Parameters': ['Monitor ID'], 'Status': {}},
            'TilingPositionStatus': {'Parameters': ['Monitor ID'], 'Status': {}},
            'TilingSet': {'Parameters': ['Monitor ID', 'Frame comp', 'Position', 'H Monitors', 'V Monitors'], 'Status': {}},
            'TilingVandHMonitorsStatus': {'Parameters': ['Monitor ID', 'Type'], 'Status': {}},
            'Volume': {'Parameters': ['Monitor ID', 'Type'], 'Status': {}},
            }



    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Use Monitor ID':
            self._GroupID = 0
        elif 1 <= int(value) <= 254:
            self._GroupID = int(value)
        else:
            print('ERROR: GroupID range is from 1 to 254 or Use Monitor ID')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0,
            'Custom': 1,
            'Real': 2,
            'Full': 3,
            '21:9': 4,
            'Dynamic': 5
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x3A ^ ValueStateValues[value]
            AspectRatioCmdString = pack('>6B', 6, MonitorID, self._GroupID, 0x3A, ValueStateValues[value], checksum)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x01: 'Custom',
            0x02: 'Real',
            0x03: 'Full',
            0x04: '21:9',
            0x05: 'Dynamic'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x3B
            AspectRatioCmdString = pack('>5B', 0x05, MonitorID, self._GroupID, 0x3B, checksum)
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x07 ^ MonitorID ^ self._GroupID ^ 0x70 ^ 0x40 ^ 0x00
            AutoImageCmdString = pack('>7B', 7, MonitorID, self._GroupID, 0x70, 0x40, 0x00, checksum)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetInput(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x09 ^ MonitorID ^ self._GroupID ^ 0xAC ^ self.InputValues[value] ^ 0 ^ 1 ^ 0  # Put Data[2] as 0 based on the legacy driver phil_10_7749
            InputCmdString = pack('>9B', 9, MonitorID, self._GroupID, 0xAC, self.InputValues[value], 0, 1, 0, checksum)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0xAD
            InputCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0xAD, checksum)
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = self.InputStates[res[-5]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetIRControl(self, value, qualifier):

        ValueStateValues = {
            'Lock All': 0x02,
            'Unlock All': 0x01,
            'Lock All But Power': 0x03,
            'Lock All But Volume': 0x04,
            'Primary': 0x05,
            'Secondary': 0x06,
            'Lock All But Power & Volume': 0x07
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x1C ^ ValueStateValues[value]
            IRControlCmdString = pack('>6B', 0x06, MonitorID, self._GroupID, 0x1C, ValueStateValues[value], checksum)
            self.__SetHelper('IRControl', IRControlCmdString, value, qualifier)
        else:
            self.Discard('IRControl: Invalid Monitor ID qualifier')

    def UpdateIRControl(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Lock All',
            0x01: 'Unlock All',
            0x03: 'Lock All But Power',
            0x04: 'Lock All But Volume',
            0x05: 'Primary',
            0x06: 'Secondary',
            0x07: 'Lock All But Power & Volume'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x1D
            IRControlCmdString = pack('>5B', 0x05, MonitorID, self._GroupID, 0x1D, checksum)
            res = self.__UpdateHelper('IRControl', IRControlCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('IRControl', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['IR Control: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateIRControl')

    def SetKeypadControl(self, value, qualifier):

        ValueStateValues = {
            'Lock All': 0x02,
            'Unlock All': 0x01,
            'Lock All But Power': 0x03,
            'Lock All But Volume': 0x04,
            'Lock All But Power & Volume': 0x07
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x1A ^ ValueStateValues[value]
            KeypadControlCmdString = pack('>6B', 0x06, MonitorID, self._GroupID, 0x1A, ValueStateValues[value], checksum)
            self.__SetHelper('KeypadControl', KeypadControlCmdString, value, qualifier)
        else:
            self.Discard('KeypadControl: Invalid Monitor ID qualifier')

    def UpdateKeypadControl(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Lock All',
            0x01: 'Unlock All',
            0x03: 'Lock All But Power',
            0x04: 'Lock All But Volume',
            0x07: 'Lock All But Power & Volume'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x1B
            KeypadControlCmdString = pack('>5B', 0x05, MonitorID, self._GroupID, 0x1B, checksum)
            res = self.__UpdateHelper('KeypadControl', KeypadControlCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('KeypadControl', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Keypad Control: Invalid/unexpected response'])
        else:
            self.Discard('KeypadControl: Invalid Monitor ID qualifier')

    def UpdateOperationHours(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x0F ^ 0x02
            OperationHoursCmdString = pack('>6B', 6, MonitorID, self._GroupID, 0x0F, 0x02, checksum)
            res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>H', res[4:-1])[0]
                    self.WriteStatus('OperationHours', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Operation Hours: Invalid/unexpected response'])
        else:
            self.Discard('OperationHours: Invalid Monitor ID qualifier')

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left': 0x00,
            'Top Left': 0x01,
            'Top Right': 0x02,
            'Bottom Right': 0x03
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            if value == 'Off':
                checksum = 0x09 ^ MonitorID ^ self._GroupID ^ 0x3C ^ 0 ^ 0 ^ 0 ^ 0
                PictureInPictureCmdString = pack('>9B', 9, MonitorID, self._GroupID, 0x3C, 0, 0, 0, 0, checksum)
            else:
                checksum = 0x09 ^ MonitorID ^ self._GroupID ^ 0x3C ^ 1 ^ ValueStateValues[value] ^ 0 ^ 0
                PictureInPictureCmdString = pack('>9B', 9, MonitorID, self._GroupID, 0x3C, 1, ValueStateValues[value], 0, 0, checksum)
            if PictureInPictureCmdString:
                self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        else:
            self.Discard('PictureInPicture: Invalid Monitor ID qualifier')

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPicturePositions = {
            0x00: 'Bottom Left',
            0x01: 'Top Left',
            0x02: 'Top Right',
            0x03: 'Bottom Right',
            0x04: 'Other'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x3D
            PictureInPictureCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0x3D, checksum)
            res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
            if res:
                try:
                    value = PictureInPicturePositions[res[-4] & 0x07]
                    self.WriteStatus('PictureInPicture', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture: Invalid/unexpected response'])
        else:
            self.Discard('PictureInPicture: Invalid Monitor ID qualifier')

    def SetPictureInPictureSourceSet(self, value, qualifier):

        quad2 = qualifier['Quadrant 2']
        quad3 = qualifier['Quadrant 3']
        quad4 = qualifier['Quadrant 4']
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255 and (quad2 in self.InputValues) and (quad3 in self.InputValues) and (quad4 in self.InputValues):
            checksum = 0x09 ^ MonitorID ^ self._GroupID ^ 0x84 ^ 0xFD ^ self.InputValues[quad2] ^ self.InputValues[quad3] ^ self.InputValues[quad4]
            PictureInPictureSourceCmdString = pack('>9B', 9, MonitorID, self._GroupID, 0x84, 0xFD, self.InputValues[quad2], self.InputValues[quad3], self.InputValues[quad4], checksum)
            self.__SetHelper('PictureInPictureSource', PictureInPictureSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPictureSourceSet')

    def UpdatePictureInPictureSourceStatus(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        quad = qualifier['Quadrant']
        if quad in ['2', '3', '4'] and 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x85
            PictureInPictureSourceStatusCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0x85, checksum)
            res = self.__UpdateHelper('PictureInPictureSourceStatus', PictureInPictureSourceStatusCmdString, value, qualifier)
            if res:
                try:
                    value = self.InputStates[res[-4]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Monitor ID': ID, 'Quadrant': '2'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])

                try:
                    value = self.InputStates[res[-3]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Monitor ID': ID, 'Quadrant': '3'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])

                try:
                    value = self.InputStates[res[-2]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Monitor ID': ID, 'Quadrant': '4'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])
        else:
            self.Discard('PictureInPictureSourceStatus: Invalid Monitor ID qualifier')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x01
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x18 ^ ValueStateValues[value]
            PowerCmdString = pack('>6B', 6, MonitorID, self._GroupID, 0x18, ValueStateValues[value], checksum)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Power: Invalid Monitor ID qualifier')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x19
            PowerCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0x19, checksum)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Power: Invalid Monitor ID qualifier')

    def UpdateMasterPower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }
        checksum = 0x05 ^ self.MonitorID ^ self._GroupID ^ 0x19
        MasterPowerCmdString = pack('>5B', 5, self.MonitorID, self._GroupID, 0x19, checksum)
        res = self.__UpdateHelper('MasterPower', MasterPowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                monitorID = unpack('B', res[2:3])[0]
                if 1 <= monitorID <= 255:
                    qualifier = {'Monitor ID': str(monitorID)}
                    self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Master Power: Invalid/unexpected response'])

    def UpdateTilingEnableStatus(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Yes',
            0x00: 'No'
        }

        PositionStates = {
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x07: '7',
            0x08: '8',
            0x09: '9',
            0x0A: '10',
            0x0B: '11',
            0x0C: '12',
            0x0D: '13',
            0x0E: '14',
            0x0F: '15',
            0x10: '16',
            0x11: '17',
            0x12: '18',
            0x13: '19',
            0x14: '20',
            0x15: '21',
            0x16: '22',
            0x17: '23',
            0x18: '24',
            0x19: '25'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x23
            TilingEnableStatusCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0x23, checksum)
            res = self.__UpdateHelper('TilingEnableStatus', TilingEnableStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-5]]
                    self.WriteStatus('TilingEnableStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tiling Enable Status: Invalid/unexpected response'])

                try:
                    value = ValueStateValues[res[-4]]
                    self.WriteStatus('TilingFrameCompStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tiling Enable Status: Invalid/unexpected response'])

                try:
                    value = PositionStates[res[-3]]
                    self.WriteStatus('TilingPositionStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tiling Enable Status: Invalid/unexpected response'])
        else:
            self.Discard('TilingEnableStatus: Invalid Monitor ID qualifier')

    def UpdateTilingFrameCompStatus(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            self.UpdateTilingEnableStatus(value, qualifier)
        else:
            self.Discard('TilingEnableStatus: Invalid Monitor ID qualifier')

    def UpdateTilingPositionStatus(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255:
            self.UpdateTilingEnableStatus(value, qualifier)
        else:
            self.Discard('TilingPositionStatus: Invalid Monitor ID qualifier')

    def UpdateTilingVandHMonitorsStatus(self, value, qualifier):

        HVMonitorsStates = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5'
        }
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        type = qualifier['Type']
        if 0 <= MonitorID <= 255 and type in ['H Monitors', 'V Monitors']:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x23
            TilingVandHMonitorsStatusCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0x23, checksum)
            res = self.__UpdateHelper('TilingVandHMonitorsStatus', TilingVandHMonitorsStatusCmdString, value, qualifier)
            if res:
                try:
                    VMonitor = (int(int(res[-2]) / 5)) + 1
                    if VMonitor == 6:
                        VMonitor = 5
                    self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[VMonitor], {'Monitor ID': ID, 'Type': 'V Monitors'})
                except (KeyError, IndexError):
                    self.Error(['Tiling Vand HMonitors Status: Invalid/unexpected response'])
                try:
                    HMonitor = int(res[-2]) % 5
                    if HMonitor == 0 and int(int(res[-2]) / 5) == 5:
                        HMonitor = 5
                    self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[HMonitor], {'Monitor ID': ID, 'Type': 'H Monitors'})
                except (KeyError, IndexError):
                    self.Error(['Tiling Vand HMonitors Status: Invalid/unexpected response'])
        else:
            self.Discard('TilingVandHMonitorsStatus: Invalid Monitor ID qualifier')

    def SetTilingSet(self, value, qualifier):

        FramecompStates = {
            'Yes': 0x01,
            'No': 0x00,
            'Keep Previous Value': 0x02
        }

        PositionStates = {
            'Keep Previous Value': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14,
            '21': 0x15,
            '22': 0x16,
            '23': 0x17,
            '24': 0x18,
            '25': 0x19
        }

        HMonitorsStates = {
            'Keep Previous Value': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5
        }

        VMonitorsStates = {
            'Keep Previous Value': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5
        }

        EnableStateValues = {
            'Yes': 0x01,
            'No': 0x00
        }

        FC = qualifier['Frame comp']
        POS = qualifier['Position']
        HM = qualifier['H Monitors']
        VM = qualifier['V Monitors']
        HVM = ((VMonitorsStates[VM] - 1) * 5) + HMonitorsStates[HM]
        if HVM == -5:
            HVM = 0x00
        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255 and FC in FramecompStates and POS in PositionStates and HM in HMonitorsStates and VM in VMonitorsStates:
            checksum = 0x09 ^ MonitorID ^ self._GroupID ^ 0x22 ^ EnableStateValues[value] ^ FramecompStates[FC] ^ PositionStates[POS] ^ HVM
            TilingSetCmdString = pack('>9B', 9, MonitorID, self._GroupID, 0x22, EnableStateValues[value], FramecompStates[FC], PositionStates[POS], HVM & 255, checksum & 255)
            self.__SetHelper('TilingSet', TilingSetCmdString, value, qualifier)
        else:
            self.Discard('TilingSet: Invalid Monitor ID qualifier')

    def SetVolume(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        if 0 <= MonitorID <= 255 and 0 <= value <= 100:
            voltype = qualifier['Type']
            if voltype == 'Speaker':
                checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x44 ^ 0xFF ^ value
                VolumeCmdString = pack('>7B', 6, MonitorID, self._GroupID, 0x44, value, 0xFF, checksum)
            elif voltype == 'Audio':
                checksum = 0x06 ^ MonitorID ^ self._GroupID ^ 0x44 ^ 0xFF ^ value
                VolumeCmdString = pack('>7B', 6, MonitorID, self._GroupID, 0x44, 0xFF, value, checksum)
            else:
                self.Discard('Invalid Command for SetVolume')
            if VolumeCmdString:
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Volume: Invalid Monitor ID qualifier')

    def UpdateVolume(self, value, qualifier):

        ID = qualifier['Monitor ID']
        if ID == 'Broadcast':
            ID = '0'
        MonitorID = int(ID)
        type = qualifier['Type']
        if 0 <= MonitorID <= 255 and type in ['Speaker', 'Audio']:
            checksum = 0x05 ^ MonitorID ^ self._GroupID ^ 0x45
            VolumeCmdString = pack('>5B', 5, MonitorID, self._GroupID, 0x45, checksum)
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[-3])
                    self.WriteStatus('Volume', value, {'Monitor ID': ID, 'Type': 'Speaker'})
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
                try:
                    value = int(res[-2])
                    self.WriteStatus('Volume', value, {'Monitor ID': ID, 'Type': 'Audio'})
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Volume: Invalid Monitor ID qualifier')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }
        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        LenDict = {
            'AspectRatio': 6,
            'Input': 9,
            'IRControl': 6,
            'KeypadControl': 6,
            'OperationHours': 7,
            'PictureInPicture': 9,
            'PictureInPictureSourceStatus': 9,
            'Power': 6,
            'MasterPower': 6,
            'TilingEnableStatus': 9,
            'TilingFrameCompStatus': 9,
            'TilingPositionStatus': 9,
            'TilingVandHMonitorsStatus': 9,
            'Volume': 7
        }

        if 'Monitor ID' in qualifier:
            if qualifier['Monitor ID'] == 'Broadcast':
                self.Discard('Invalid Update command for {}, Monitor ID qualifier is set to Broadcast'.format(command))
                return ''
                
        if self.Unidirectional == 'True':
            self.Discard('Invalid Update command for {}, GroupID parameter is set to  Use Monitor ID'.format(command))
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=LenDict[command])
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

    def phil_10_1514_88XL(self):

        self.InputValues = {
            'DVI-D'        : 0x0E, 
            'Composite'    : 0x02, 
            'Component'    : 0x03, 
            'HDMI 1'       : 0x0D, 
            'HDMI 2'       : 0x06, 
            'VGA'          : 0x05, 
            'Display Port' : 0x0A
        }

        self.InputStates  = {
            0x0E : 'DVI-D', 
            0x02 : 'Composite', 
            0x03 : 'Component', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x05 : 'VGA', 
            0x0A : 'Display Port'
        }

    def phil_10_1514_4678(self):

           
        self.InputValues = {
            'DVI-D'        : 0x0E, 
            'Composite'    : 0x02, 
            'Component'    : 0x03, 
            'HDMI 1'       : 0x0D, 
            'VGA'          : 0x05, 
            'Display Port' : 0x0A
        }

        self.InputStates  = {
            0x0E : 'DVI-D', 
            0x02 : 'Composite', 
            0x03 : 'Component', 
            0x0D : 'HDMI 1', 
            0x05 : 'VGA', 
            0x0A : 'Display Port'
        }

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._MonitorID = 1
        self._GroupID = 0
        self.Models = {
            'BDL-4678XL': self.phil_10_1514_4678,
            'BDL-4988XL': self.phil_10_1514_88XL,
            'BDL-5588XL': self.phil_10_1514_88XL,
            'BDL-4988XC': self.phil_10_1514_88XL,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'IRControl': {'Status': {}},
            'KeypadControl': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PictureInPictureSourceSet': {'Parameters': ['Quadrant 2', 'Quadrant 3', 'Quadrant 4'], 'Status': {}},
            'PictureInPictureSourceStatus': {'Parameters': ['Quadrant'], 'Status': {}},
            'Power': {'Status': {}},
            'TilingEnableStatus': {'Status': {}},
            'TilingFrameCompStatus': {'Status': {}},
            'TilingPositionStatus': {'Status': {}},
            'TilingSet': {'Parameters': ['Frame comp', 'Position', 'H Monitors', 'V Monitors'], 'Status': {}},
            'TilingVandHMonitorsStatus': {'Parameters': ['Type'], 'Status': {}},
            'Volume': {'Parameters': ['Type'], 'Status': {}},
            }

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Use Monitor ID':
            self._GroupID = 0
        elif 1 <= int(value) <= 254:
            self._GroupID = int(value)
        else:
            print('Invalid GroupID paramter. Range is from 1 to 254 or Use Monitor ID')

    @property
    def MonitorID(self):
        return self._MonitorID

    @MonitorID.setter
    def MonitorID(self, value):
        if value == 'Broadcast':
            self._MonitorID = 0
        elif 1 <= int(value) <= 255:
            self._MonitorID = int(value)
        else:
            print('Invalid MonitorID paramter. Range is from 1 to 254 or Broadcast')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0,
            'Custom': 1,
            'Real': 2,
            'Full': 3,
            '21:9': 4,
            'Dynamic': 5
        }

        checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x3A ^ ValueStateValues[value]
        AspectRatioCmdString = pack('>6B', 6, self._MonitorID, self._GroupID, 0x3A, ValueStateValues[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x01: 'Custom',
            0x02: 'Real',
            0x03: 'Full',
            0x04: '21:9',
            0x05: 'Dynamic'
        }
        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x3B
        AspectRatioCmdString = pack('>5B', 0x05, self._MonitorID, self._GroupID, 0x3B, checksum)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        checksum = 0x07 ^ self._MonitorID ^ self._GroupID ^ 0x70 ^ 0x40 ^ 0x00
        AutoImageCmdString = pack('>7B', 7, self._MonitorID, self._GroupID, 0x70, 0x40, 0x00, checksum)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        checksum = 0x09 ^ self._MonitorID ^ self._GroupID ^ 0xAC ^ self.InputValues[value] ^ 0 ^ 1 ^ 0  # Put Data[2] as 0 based on the legacy driver phil_10_7749
        InputCmdString = pack('>9B', 9, self._MonitorID, self._GroupID, 0xAC, self.InputValues[value], 0, 1, 0, checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0xAD
        InputCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0xAD, checksum)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStates[res[-5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIRControl(self, value, qualifier):

        ValueStateValues = {
            'Lock All': 0x02,
            'Unlock All': 0x01,
            'Lock All But Power': 0x03,
            'Lock All But Volume': 0x04,
            'Primary': 0x05,
            'Secondary': 0x06,
            'Lock All But Power & Volume': 0x07
        }

        checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x1C ^ ValueStateValues[value]
        IRControlCmdString = pack('>6B', 0x06, self._MonitorID, self._GroupID, 0x1C, ValueStateValues[value], checksum)
        self.__SetHelper('IRControl', IRControlCmdString, value, qualifier)

    def UpdateIRControl(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Lock All',
            0x01: 'Unlock All',
            0x03: 'Lock All But Power',
            0x04: 'Lock All But Volume',
            0x05: 'Primary',
            0x06: 'Secondary',
            0x07: 'Lock All But Power & Volume'
        }

        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x1D
        IRControlCmdString = pack('>5B', 0x05, self._MonitorID, self._GroupID, 0x1D, checksum)
        res = self.__UpdateHelper('IRControl', IRControlCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('IRControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Control: Invalid/unexpected response'])

    def SetKeypadControl(self, value, qualifier):

        ValueStateValues = {
            'Lock All': 0x02,
            'Unlock All': 0x01,
            'Lock All But Power': 0x03,
            'Lock All But Volume': 0x04,
            'Lock All But Power & Volume': 0x07
        }
        checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x1A ^ ValueStateValues[value]
        KeypadControlCmdString = pack('>6B', 0x06, self._MonitorID, self._GroupID, 0x1A, ValueStateValues[value], checksum)
        self.__SetHelper('KeypadControl', KeypadControlCmdString, value, qualifier)

    def UpdateKeypadControl(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Lock All',
            0x01: 'Unlock All',
            0x03: 'Lock All But Power',
            0x04: 'Lock All But Volume',
            0x07: 'Lock All But Power & Volume'
        }

        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x1B
        KeypadControlCmdString = pack('>5B', 0x05, self._MonitorID, self._GroupID, 0x1B, checksum)
        res = self.__UpdateHelper('KeypadControl', KeypadControlCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('KeypadControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keypad Control: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x0F ^ 0x02
        OperationHoursCmdString = pack('>6B', 6, self._MonitorID, self._GroupID, 0x0F, 0x02, checksum)
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>H', res[4:-1])[0]
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left': 0x00,
            'Top Left': 0x01,
            'Top Right': 0x02,
            'Bottom Right': 0x03
        }

        if value == 'Off':
            checksum = 0x09 ^ self._MonitorID ^ self._GroupID ^ 0x3C ^ 0 ^ 0 ^ 0 ^ 0
            PictureInPictureCmdString = pack('>9B', 9, self._MonitorID, self._GroupID, 0x3C, 0, 0, 0, 0, checksum)
        else:
            checksum = 0x09 ^ self._MonitorID ^ self._GroupID ^ 0x3C ^ 1 ^ ValueStateValues[value] ^ 0 ^ 0
            PictureInPictureCmdString = pack('>9B', 9, self._MonitorID, self._GroupID, 0x3C, 1, ValueStateValues[value], 0, 0, checksum)
        if PictureInPictureCmdString:
            self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPicture')

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPicturePositions = {
            0x00: 'Bottom Left',
            0x01: 'Top Left',
            0x02: 'Top Right',
            0x03: 'Bottom Right',
            0x04: 'Other'
        }

        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x3D
        PictureInPictureCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0x3D, checksum)
        res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        if res:
            try:
                value = PictureInPicturePositions[res[-4] & 0x07]
                self.WriteStatus('PictureInPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture in Picture: Invalid/unexpected response'])

    def SetPictureInPictureSourceSet(self, value, qualifier):

        quad2 = qualifier['Quadrant 2']
        quad3 = qualifier['Quadrant 3']
        quad4 = qualifier['Quadrant 4']

        if (quad2 in self.InputValues) and (quad3 in self.InputValues) and (quad4 in self.InputValues):
            checksum = 0x09 ^ self._MonitorID ^ self._GroupID ^ 0x84 ^ 0xFD ^ self.InputValues[quad2] ^ self.InputValues[quad3] ^ self.InputValues[quad4]
            PictureInPictureSourceCmdString = pack('>9B', 9, self._MonitorID, self._GroupID, 0x84, 0xFD, self.InputValues[quad2], self.InputValues[quad3], self.InputValues[quad4], checksum)
            self.__SetHelper('PictureInPictureSource', PictureInPictureSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPictureSourceSet')

    def UpdatePictureInPictureSourceStatus(self, value, qualifier):

        quad = qualifier['Quadrant']
        if quad in ['2', '3', '4']:
            checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x85
            PictureInPictureSourceStatusCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0x85, checksum)
            res = self.__UpdateHelper('PictureInPictureSourceStatus', PictureInPictureSourceStatusCmdString, value, qualifier)
            if res:
                try:
                    value = self.InputStates[res[-4]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Quadrant': '2'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])

                try:
                    value = self.InputStates[res[-3]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Quadrant': '3'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])

                try:
                    value = self.InputStates[res[-2]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Quadrant': '4'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureInPictureSourceStatus')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x01
        }
        checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x18 ^ ValueStateValues[value]
        PowerCmdString = pack('>6B', 6, self._MonitorID, self._GroupID, 0x18, ValueStateValues[value], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }

        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x19
        PowerCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0x19, checksum)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateTilingEnableStatus(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Yes',
            0x00: 'No'
        }

        PositionStates = {
            0x01: '1',
            0x02: '2',
            0x03: '3',
            0x04: '4',
            0x05: '5',
            0x06: '6',
            0x07: '7',
            0x08: '8',
            0x09: '9',
            0x0A: '10',
            0x0B: '11',
            0x0C: '12',
            0x0D: '13',
            0x0E: '14',
            0x0F: '15',
            0x10: '16',
            0x11: '17',
            0x12: '18',
            0x13: '19',
            0x14: '20',
            0x15: '21',
            0x16: '22',
            0x17: '23',
            0x18: '24',
            0x19: '25'
        }

        checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x23
        TilingEnableStatusCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0x23, checksum)
        res = self.__UpdateHelper('TilingEnableStatus', TilingEnableStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-5]]
                self.WriteStatus('TilingEnableStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tiling Enable Status: Invalid/unexpected response'])

            try:
                value = ValueStateValues[res[-4]]
                self.WriteStatus('TilingFrameCompStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tiling Enable Status: Invalid/unexpected response'])

            try:
                value = PositionStates[res[-3]]
                self.WriteStatus('TilingPositionStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tiling Enable Status: Invalid/unexpected response'])

    def UpdateTilingFrameCompStatus(self, value, qualifier):

        self.UpdateTilingEnableStatus(value, qualifier)

    def UpdateTilingPositionStatus(self, value, qualifier):

        self.UpdateTilingEnableStatus(value, qualifier)

    def UpdateTilingVandHMonitorsStatus(self, value, qualifier):

        HVMonitorsStates = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5'
        }

        type = qualifier['Type']
        if type in ['H Monitors', 'V Monitors']:
            checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x23
            TilingVandHMonitorsStatusCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0x23, checksum)
            res = self.__UpdateHelper('TilingVandHMonitorsStatus', TilingVandHMonitorsStatusCmdString, value, qualifier)
            if res:
                try:
                    VMonitor = (int(int(res[-2]) / 5)) + 1
                    if VMonitor == 6:
                        VMonitor = 5
                    self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[VMonitor], {'Type': 'V Monitors'})
                except (KeyError, IndexError):
                    self.Error(['Tiling Vand HMonitors Status: Invalid/unexpected response'])
                try:
                    HMonitor = int(res[-2]) % 5
                    if HMonitor == 0 and int(int(res[-2]) / 5) == 5:
                        HMonitor = 5
                    self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[HMonitor], {'Type': 'H Monitors'})
                except (KeyError, IndexError):
                    self.Error(['Tiling Vand HMonitors Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTilingVandHMonitorsStatus')

    def SetTilingSet(self, value, qualifier):

        FramecompStates = {
            'Yes': 0x01,
            'No': 0x00,
            'Keep Previous Value': 0x02
        }

        PositionStates = {
            'Keep Previous Value': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14,
            '21': 0x15,
            '22': 0x16,
            '23': 0x17,
            '24': 0x18,
            '25': 0x19
        }

        HMonitorsStates = {
            'Keep Previous Value': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5
        }

        VMonitorsStates = {
            'Keep Previous Value': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5
        }

        EnableStateValues = {
            'Yes': 0x01,
            'No': 0x00
        }

        FC = qualifier['Frame comp']
        POS = qualifier['Position']
        HM = qualifier['H Monitors']
        VM = qualifier['V Monitors']
        HVM = ((VMonitorsStates[VM] - 1) * 5) + HMonitorsStates[HM]
        if HVM == -5:
            HVM = 0x00

        if FC in FramecompStates and POS in PositionStates and HM in HMonitorsStates and VM in VMonitorsStates:
            checksum = 0x09 ^ self._MonitorID ^ self._GroupID ^ 0x22 ^ EnableStateValues[value] ^ FramecompStates[FC] ^ PositionStates[POS] ^ HVM
            TilingSetCmdString = pack('>9B', 9, self._MonitorID, self._GroupID, 0x22, EnableStateValues[value], FramecompStates[FC], PositionStates[POS], HVM & 255, checksum & 255)
            self.__SetHelper('TilingSet', TilingSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilingSet')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            voltype = qualifier['Type']
            if voltype == 'Speaker':
                checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x44 ^ 0xFF ^ value
                VolumeCmdString = pack('>7B', 6, self._MonitorID, self._GroupID, 0x44, value, 0xFF, checksum)
            elif voltype == 'Audio':
                checksum = 0x06 ^ self._MonitorID ^ self._GroupID ^ 0x44 ^ 0xFF ^ value
                VolumeCmdString = pack('>7B', 6, self._MonitorID, self._GroupID, 0x44, 0xFF, value, checksum)
            else:
                self.Discard('Invalid Command for SetVolume')
            if VolumeCmdString:
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        type = qualifier['Type']
        if type in ['Speaker', 'Audio']:
            checksum = 0x05 ^ self._MonitorID ^ self._GroupID ^ 0x45
            VolumeCmdString = pack('>5B', 5, self._MonitorID, self._GroupID, 0x45, checksum)
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[-3])
                    self.WriteStatus('Volume', value, {'Type': 'Speaker'})
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
                try:
                    value = int(res[-2])
                    self.WriteStatus('Volume', value, {'Type': 'Audio'})
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }
        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        LenDict = {
            'AspectRatio': 6,
            'Input': 9,
            'IRControl': 6,
            'KeypadControl': 6,
            'OperationHours': 7,
            'PictureInPicture': 9,
            'PictureInPictureSourceStatus': 9,
            'Power': 6,
            'TilingEnableStatus': 9,
            'TilingFrameCompStatus': 9,
            'TilingPositionStatus': 9,
            'TilingVandHMonitorsStatus': 9,
            'Volume': 7
        }

        if self.Unidirectional == 'True' or self._MonitorID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=LenDict[command])
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

    def phil_10_1514_88XL(self):

           
        self.InputValues = {
            'DVI-D'        : 0x0E, 
            'Composite'    : 0x02, 
            'Component'    : 0x03, 
            'HDMI 1'       : 0x0D, 
            'HDMI 2'       : 0x06, 
            'VGA'          : 0x05, 
            'Display Port' : 0x0A
        }

        self.InputStates  = {
            0x0E : 'DVI-D', 
            0x02 : 'Composite', 
            0x03 : 'Component', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x05 : 'VGA', 
            0x0A : 'Display Port'
        }

    def phil_10_1514_4678(self):

           
        self.InputValues = {
            'DVI-D'        : 0x0E, 
            'Composite'    : 0x02, 
            'Component'    : 0x03, 
            'HDMI 1'       : 0x0D, 
            'VGA'          : 0x05, 
            'Display Port' : 0x0A
        }

        self.InputStates  = {
            0x0E : 'DVI-D', 
            0x02 : 'Composite', 
            0x03 : 'Component', 
            0x0D : 'HDMI 1', 
            0x05 : 'VGA', 
            0x0A : 'Display Port'
        }

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
