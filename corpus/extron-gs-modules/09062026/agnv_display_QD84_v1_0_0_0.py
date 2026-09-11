from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack

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
            'AspectRatio': {'Parameters': ['Monitor ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Monitor ID'], 'Status': {}},
            'Input': {'Parameters': ['Monitor ID'], 'Status': {}},
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
            'Volume': {'Parameters': ['Monitor ID'], 'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0,
            'Custom': 1,
            'Real': 2,
            'Full': 3,
            '21:9': 4
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x3A ^ ValueStateValues[value]
            AspectRatioCmdString = pack('10B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x3A, ValueStateValues[value], checksum)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x01: 'Custom',
            0x02: 'Real',
            0x03: 'Full',
            0x04: '21:9'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x3B
            AspectRatioCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x3B, checksum)
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

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x05 ^ 0x01 ^ 0x70 ^ 0x40 ^ 0x00
            AutoImageCmdString = pack('11B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x05, 0x01, 0x70, 0x40, 0x00, checksum)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': 0x01,
            'Component': 0x03,
            'VGA': 0x05,
            'HDMI 1': 0x0D,
            'HDMI 2': 0x06,
            'HDMI 3': 0x0F,
            'DisplayPort': 0x0A,
            'Card OPS': 0x0B,
            'USB': 0x0C,
            'DVI-D': 0x0E
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0xAC ^ ValueStateValues[value] ^ 0x00 ^ 0x00 ^ 0x00
            InputCmdString = pack('13B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x07, 0x01, 0xAC, ValueStateValues[value], 0x00, 0x00, 0x00, checksum)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Video',
            0x03: 'Component',
            0x05: 'VGA',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0A: 'DisplayPort',
            0x0B: 'Card OPS',
            0x0C: 'USB',
            0x0E: 'DVI-D'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0xAD
            InputCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0xAD, checksum)
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-5]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def UpdateOperationHours(self, value, qualifier):

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x0F ^ 0x02
            OperationHoursCmdString = pack('10B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x0F, 0x02, checksum)
            res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
            if res:
                try:
                    value = unpack('>H', res[7:-1])[0]
                    self.WriteStatus('OperationHours', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Operation Hours: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOperationHours')

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left': 0x00,
            'Top Left': 0x01,
            'Top Right': 0x02,
            'Bottom Right': 0x03
        }

        PictureInPictureCmdString = ''
        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            if value == 'Off':
                checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0x3C ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x00
                PictureInPictureCmdString = pack('13B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x07, 0x01, 0x3C, 0x00, 0x00, 0x00, 0x00, checksum)
            else:
                checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0x3C ^ 0x01 ^ ValueStateValues[value] ^ 0x00 ^ 0x00
                PictureInPictureCmdString = pack('13B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x07, 0x01, 0x3C, 0x01, ValueStateValues[value], 0x00, 0x00, checksum)
            if PictureInPictureCmdString:
                self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPicture')

    def UpdatePictureInPicture(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Bottom Left',
            0x01: 'Top Left',
            0x02: 'Top Right',
            0x03: 'Bottom Right',
            0x04: 'Other'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x3D
            PictureInPictureCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x3D, checksum)
            res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
            if res:
                try:
                    if res[-5] & 0x01 == 0x00:
                        value = 'Off'
                    else:
                        value = ValueStateValues[res[-4] & 0x07]
                    self.WriteStatus('PictureInPicture', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Picture In Picture: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureInPicture')

    def SetPictureInPictureSourceSet(self, value, qualifier):

        QuadrantStates = {
            'Video': 0x01,
            'Component': 0x03,
            'VGA': 0x05,
            'HDMI 1': 0x0D,
            'HDMI 2': 0x06,
            'HDMI 3': 0x0F,
            'DisplayPort': 0x0A,
            'Card OPS': 0x0B,
            'USB': 0x0C,
            'DVI-D': 0x0E
        }

        quad2 = qualifier['Quadrant 2']
        quad3 = qualifier['Quadrant 3']
        quad4 = qualifier['Quadrant 4']
        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255 and quad2 in QuadrantStates and quad3 in QuadrantStates and quad4 in QuadrantStates:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0x84 ^ 0xFD ^ QuadrantStates[quad2] ^ QuadrantStates[quad3] ^ QuadrantStates[quad4]
            PictureInPictureSourceSetCmdString = pack('13B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x07, 0x01, 0x84, 0xFD, QuadrantStates[quad2], QuadrantStates[quad3], QuadrantStates[quad4], checksum)
            self.__SetHelper('PictureInPictureSourceSet', PictureInPictureSourceSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPictureSourceSet')

    def UpdatePictureInPictureSourceStatus(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Video',
            0x03: 'Component',
            0x05: 'VGA',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0A: 'DisplayPort',
            0x0B: 'Card OPS',
            0x0C: 'USB',
            0x0E: 'DVI-D'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x85
            PictureInPictureSourceStatusCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x85, checksum)
            res = self.__UpdateHelper('PictureInPictureSourceStatus', PictureInPictureSourceStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-4]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Monitor ID': str(MonitorID), 'Quadrant': '2'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])

                try:
                    value = ValueStateValues[res[-3]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Monitor ID': str(MonitorID), 'Quadrant': '3'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])

                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('PictureInPictureSourceStatus', value, {'Monitor ID': str(MonitorID), 'Quadrant': '4'})
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureInPictureSourceStatus')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x01
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x18 ^ ValueStateValues[value]
            PowerCmdString = pack('10B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x18, ValueStateValues[value], checksum)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x19
            PowerCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x19, checksum)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def UpdateTilingEnableStatus(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Yes',
            0x00: 'No'
        }
        HVMonitorsStates = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x23
            TilingEnableStatusCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x23, checksum)
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
                    self.Error(['Tiling Frame Comp Status: Invalid/unexpected response'])

                try:
                    value = unpack('B', res[-3:-2])[0]
                    self.WriteStatus('TilingPositionStatus', str(value), qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tiling Position Status: Invalid/unexpected response'])

                try:
                    VMonitor = (int(int(res[-2]) / 5)) + 1
                    if VMonitor == 6:
                        VMonitor = 5
                    self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[VMonitor], {'Monitor ID': str(MonitorID), 'Type': 'V Monitors'})
                except (KeyError, IndexError):
                    self.Error(['Tiling V Monitors Status: Invalid/unexpected response'])

                try:
                    HMonitor = int(res[-2]) % 5
                    if HMonitor == 0 and int(int(res[-2]) / 5) == 5:
                        HMonitor = 5
                    self.WriteStatus('TilingVandHMonitorsStatus', HVMonitorsStates[HMonitor], {'Monitor ID': str(MonitorID), 'Type': 'H Monitors'})
                except (KeyError, IndexError):
                    self.Error(['Tiling H Monitors Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTilingEnableStatus')

    def UpdateTilingFrameCompStatus(self, value, qualifier):

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            self.UpdateTilingEnableStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTilingFrameCompStatus')

    def UpdateTilingPositionStatus(self, value, qualifier):

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            self.UpdateTilingEnableStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTilingPositionStatus')

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

        ValueStateValues = {
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
        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255 and FC in FramecompStates and POS in PositionStates and HM in HMonitorsStates and VM in VMonitorsStates:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0x22 ^ ValueStateValues[value] ^ FramecompStates[FC] ^ PositionStates[POS] ^ HVM
            TilingSetCmdString = pack('13B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x07, 0x01, 0x22, ValueStateValues[value], FramecompStates[FC], PositionStates[POS], HVM & 255, checksum & 255)
            self.__SetHelper('TilingSet', TilingSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilingSet')

    def UpdateTilingVandHMonitorsStatus(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            self.UpdateTilingEnableStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTilingVandHMonitorsStatus')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x44 ^ value
                VolumeCmdString = pack('10B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x44, value, checksum)
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVolume')
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        MonitorID = int(qualifier['Monitor ID'])
        if 1 <= MonitorID <= 255:
            checksum = 0xA6 ^ MonitorID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x45
            VolumeCmdString = pack('9B', 0xA6, MonitorID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x45, checksum)
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[-2])
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: 'Limit Over.',
            0x02: 'Limit Over.',
            0x03: 'Command canceled.',
            0x04: 'Parse Error.',
        }
        if response[6] == 0x00 and response[7] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[7]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=9)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        LenDict = {
            'AspectRatio': 9,
            'Input': 12,
            'OperationHours': 10,
            'PictureInPicture': 12,
            'PictureInPictureSourceStatus': 12,
            'Power': 9,
            'MasterPower': 9,
            'TilingEnableStatus': 12,
            'TilingFrameCompStatus': 12,
            'TilingPositionStatus': 12,
            'TilingVandHMonitorsStatus': 12,
            'Volume': 9
        }

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

