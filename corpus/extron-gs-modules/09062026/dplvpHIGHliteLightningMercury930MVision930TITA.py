from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'HIGHlite 660 2D': self.dpl_1_1032_dual_2D,
            'HIGHlite 660 3D': self.dpl_1_1032_H660_3D,
            'HIGHlite 740 2D': self.dpl_1_1032_dual_2D,
            'Mercury 930 3D': self.dpl_1_1032_dual_3D,
            'TITAN 930 2D': self.dpl_1_1032_dual_2D,
            'TITAN 930 3D': self.dpl_1_1032_dual_3D,
            'TITAN LED 3D': self.dpl_1_1032_dual_3D,
            'TITAN Quad 2000 2D': self.dpl_1_1032_quad_2D,
            'TITAN Quad 2000 3D': self.dpl_1_1032_quad_3D,
            'TITAN Quad 2D': self.dpl_1_1032_quad_2D,
            'TITAN Quad 3D': self.dpl_1_1032_quad_3D,
            'TITAN Super Quad 2000': self.dpl_1_1032_quad_3D,
            'TITAN Super Quad 2D': self.dpl_1_1032_quad_2D,
            'TITAN Super Quad 3D': self.dpl_1_1032_quad_3D,
            'Lightning 2D': self.dpl_1_1032_dual_2D,
            'Lightning 3D': self.dpl_1_1032_dual_3D,
            'HIGHlite 8000': self.dpl_1_1032_8000,
            'HIGHlite Laser 3D': self.dpl_1_1032_laser,
            'M-Vision 930 3D': self.dpl_1_1032_vision_3D,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DDarkTime': {'Status': {}},
            '3DDominance': {'Status': {}},
            '3DEnable': {'Status': {}},
            '3DFrameMultiplier': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DSyncPolarity': {'Status': {}},
            'Input': {'Status': {}},
            'LampHours': {'Parameters': ['Lamp'], 'Status': {}},
            'LampMode': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LaserHours': {'Status': {}},
            'LaserMode': {'Status': {}},
            'LaserPower': {'Status': {}},
            'LaserStatus': {'Status': {}},
            'PIPHorizontalPosition': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPVerticalPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:ack|ACK) 3d\.darktime = (0|1|2|3)\r'), self.__Match3DDarkTime, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) 3d\.dominance = (left|right)\r'), self.__Match3DDominance, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) 3d\.enable = (on|off)\r'), self.__Match3DEnable, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) 3d\.frmultiplier = (1|2|3)\r'), self.__Match3DFrameMultiplier, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) 3d\.format = (auto|seq|fpack|tab|sbs)\r'), self.__Match3DFormat, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) 3d\.syncpolarity = (pos|neg)\r'), self.__Match3DSyncPolarity, None)

            self.AddMatchString(re.compile(b'(?:ack|ACK) input = (\d+)\r'), self.__MatchInput, None)

            self.AddMatchString(re.compile(b'(?:ack|ACK) lamp([1234])\.hours = (\d+):(\d+)\r'), self.__MatchLampHours, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) lamp\.mode = (\d+)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) lamp\.power = (\d{1,3})\r'), self.__MatchLampPower, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) lamp([1234])\.status = (\d+)\r'), self.__MatchLampStatus, None)

            self.AddMatchString(re.compile(b'(?:ack|ACK) laser\.hours = (\d+)(?::\d+)\r'), self.__MatchLaserHours, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) laser\.mode = (0|1|2|3)\r'), self.__MatchLaserMode, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) laser\.power = (\d+)\r'), self.__MatchLaserPower, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) laser\.status = (0|1)\r'), self.__MatchLaserStatus, None)

            self.AddMatchString(re.compile(b'(?:ack|ACK) pip\.hpos = (\d+)\r'), self.__MatchPIPHorizontalPosition, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) pip\.input = (0|1|2|3|4|5|6|7)\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) pip\.mode = (0|1|2|3)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) pip\.position = (0|1|2|3|4)\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) pip\.size = (0|1|2)\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) pip\.vpos = (\d+)\r'), self.__MatchPIPVerticalPosition, None)

            self.AddMatchString(re.compile(b'(?:ack|ACK) power = (on|standby|1|0)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'(?:ack|ACK) shutter = (on|off)\r'), self.__MatchShutter, None)
            self.AddMatchString(re.compile(b'(?:nack|NAK) (.*)\r'), self.__MatchError, None)

    def Set3DDarkTime(self, value, qualifier):

        Values = {
            '0 us': '*3d.darktime = 0\r',
            '650 us': '*3d.darktime = 1\r',
            '1300 us': '*3d.darktime = 2\r',
            '7500 us': '*3d.darktime = 3\r'
        }

        self.__SetHelper('3DDarkTime', Values[value], value, qualifier)

    def Update3DDarkTime(self, value, qualifier):
        self.__UpdateHelper('3DDarkTime', '*3d.darktime ?\r', value, qualifier)

    def __Match3DDarkTime(self, match, tag):

        Values = {
            '0': '0 us',
            '1': '650 us',
            '2': '1300 us',
            '3': '7500 us'
        }

        self.WriteStatus('3DDarkTime', Values[match.group(1).decode()], None)

    def Set3DDominance(self, value, qualifier):

        Values = {
            'Left': '*3d.dominance = left\r',
            'Right': '*3d.dominance = right\r'
        }

        self.__SetHelper('3DDominance', Values[value], value, qualifier)

    def Update3DDominance(self, value, qualifier):
        self.__UpdateHelper('3DDominance', '*3d.dominance ?\r', value, qualifier)

    def __Match3DDominance(self, match, tag):

        Values = {
            'left': 'Left',
            'right': 'Right'
        }

        self.WriteStatus('3DDominance', Values[match.group(1).decode()], None)

    def Set3DEnable(self, value, qualifier):

        Values = {
            'On': '*3d.enable = on\r',
            'Off': '*3d.enable = off\r'
        }

        self.__SetHelper('3DEnable', Values[value], value, qualifier)

    def Update3DEnable(self, value, qualifier):
        self.__UpdateHelper('3DEnable', '*3d.enable ?\r', value, qualifier)

    def __Match3DEnable(self, match, tag):

        Values = {
            'on': 'On',
            'off': 'Off'
        }

        self.WriteStatus('3DEnable', Values[match.group(1).decode()], None)

    def Set3DFrameMultiplier(self, value, qualifier):

        Values = {
            '1X': '*3d.frmultiplier = 1\r',
            '2X': '*3d.frmultiplier = 2\r',
            '3X': '*3d.frmultiplier = 3\r'
        }

        self.__SetHelper('3DFrameMultiplier', Values[value], value, qualifier)

    def Update3DFrameMultiplier(self, value, qualifier):
        self.__UpdateHelper('3DFrameMultiplier', '*3d.frmultiplier ?\r', value, qualifier)

    def __Match3DFrameMultiplier(self, match, tag):

        Values = {
            '1': '1X',
            '2': '2X',
            '3': '3X'
        }

        self.WriteStatus('3DFrameMultiplier', Values[match.group(1).decode()], None)

    def Set3DFormat(self, value, qualifier):

        Values = {
            'Auto': '*3d.format = auto\r',
            'Sequential': '*3d.format = seq\r',
            'F Pack': '*3d.format = fpack\r',
            'Tab': '*3d.format = tab\r',
            'SBS': '*3d.format = sbs\r'
        }

        self.__SetHelper('3DFormat', Values[value], value, qualifier)

    def Update3DFormat(self, value, qualifier):
        self.__UpdateHelper('3DFormat', '*3d.format ?\r', value, qualifier)

    def __Match3DFormat(self, match, tag):

        Values = {
            'auto': 'Auto',
            'seq': 'Sequential',
            'fpack': 'F Pack',
            'tab': 'Tab',
            'sbs': 'SBS'
        }

        self.WriteStatus('3DFormat', Values[match.group(1).decode()], None)

    def Set3DSyncPolarity(self, value, qualifier):

        Values = {
            'Positive': '*3d.syncpolarity = pos\r',
            'Negative': '*3d.syncpolarity = neg\r'
        }

        self.__SetHelper('3DSyncPolarity', Values[value], value, qualifier)

    def Update3DSyncPolarity(self, value, qualifier):
        self.__UpdateHelper('3DSyncPolarity', '*3d.syncpolarity ?\r', value, qualifier)

    def __Match3DSyncPolarity(self, match, tag):

        Values = {
            'pos': 'Positive',
            'neg': 'Negative'
        }

        self.WriteStatus('3DSyncPolarity', Values[match.group(1).decode()], None)

    def SetInput(self, value, qualifier):

        CmdString = '*input = {0}\r'.format(self.Inputs[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '*input ?\r', value, qualifier)

    def __MatchInput(self, match, tag):

        if match.group(1).decode() in self.InputStates:
            self.WriteStatus('Input', self.InputStates[match.group(1).decode()], None)
        else:
            self.Error(['Input has provided an unexpected response'])

    def UpdateLampHours(self, value, qualifier):
        CmdString = '*lamp{0}.hours ?\r'.format(qualifier['Lamp'])
        self.__UpdateHelper('LampHours', CmdString, value, qualifier)

    def __MatchLampHours(self, match, tag):

        if match.group(1).decode() in self.LampStates:
            Lamp = self.LampStates[match.group(1).decode()]
            Hours = int(match.group(2).decode())
            self.WriteStatus('LampHours', Hours, {'Lamp': Lamp})
        else:
            self.Error(['Lamp Hours has provided an unexpected response'])

    def SetLampMode(self, value, qualifier):

        CmdString = '*lamp.mode = {0}\r'.format(self.LampModes[value])
        self.__SetHelper('LampMode', CmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        self.__UpdateHelper('LampMode', '*lamp.mode ?\r', value, qualifier)

    def __MatchLampMode(self, match, tag):

        if match.group(1).decode() in self.LampModeStates:
            self.WriteStatus('LampMode', self.LampModeStates[match.group(1).decode()], None)
        else:
            self.Error(['Lamp Mode has provided an unexpected response'])

    def SetLampPower(self, value, qualifier):

        if 1 <= value <= 100:
            CmdString = '*lamp.power = {0}\r'.format(value)
            self.__SetHelper('LampPower', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampPower')

    def UpdateLampPower(self, value, qualifier):
        self.__UpdateHelper('LampPower', '*lamp.power ?\r', value, qualifier)

    def __MatchLampPower(self, match, tag):

        self.WriteStatus('LampPower', int(match.group(1).decode()), None)

    def UpdateLampStatus(self, value, qualifier):

        CmdString = '*lamp{0}.status ?\r'.format(qualifier['Lamp'])
        self.__UpdateHelper('LampStatus', CmdString, value, qualifier)

    def __MatchLampStatus(self, match, tag):

        Values = {
            '0': 'Off',
            '1': 'Pre-Cooling',
            '2': 'Ignition',
            '3': 'Ignition Confirm',
            '4': 'Enable Communication',
            '5': 'Delay Cooling',
            '6': 'Warm-up Eco Mode',
            '7': 'Warm-up',
            '8': 'Cool Down No Restrike',
            '9': 'Cool Down OK Restrike',
            '10': 'Normal',
            '11': 'Error',
            '12': 'Ignition Retry',
            '13': 'Re-strike Delay',
            '14': 'Enable CSI',
            '15': 'Deferred Shutdown',
            '16': 'Shutdown Confirm',
            '17': 'Error Shutdown',
            '18': 'Lamp Warmup Stage 1',
            '19': 'Lamp Warmup Stage 2'
        }

        if (match.group(1).decode() in self.LampStates) and (match.group(2).decode() in Values):
            Lamp = self.LampStates[match.group(1).decode()]
            Status = Values[match.group(2).decode()]
            self.WriteStatus('LampStatus', Status, {'Lamp': Lamp})
        else:
            self.Erroe(['Lamp Status has provided an unexpected response'])

    def UpdateLaserHours(self, value, qualifier):

        LaserHoursCmdString = '*laser.hours ?\r'
        self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)

    def __MatchLaserHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LaserHours', value, None)

    def SetLaserMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': '0',
            'Normal': '1',
            'Custom': '2',
            'Quiet': '3'
        }

        LaserModeCmdString = '*laser.mode = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def UpdateLaserMode(self, value, qualifier):

        LaserModeCmdString = '*laser.mode ?\r'
        self.__UpdateHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def __MatchLaserMode(self, match, tag):

        ValueStateValues = {
            '0': 'Eco',
            '1': 'Normal',
            '2': 'Custom',
            '3': 'Quiet'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LaserMode', value, None)

    def SetLaserPower(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 28
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LaserPowerCmdString = '*laser.power = {0}\r'.format(value)
            self.__SetHelper('LaserPower', LaserPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLaserPower')

    def UpdateLaserPower(self, value, qualifier):

        LaserPowerCmdString = '*laser.power ?\r'
        self.__UpdateHelper('LaserPower', LaserPowerCmdString, value, qualifier)

    def __MatchLaserPower(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LaserPower', value, None)

    def UpdateLaserStatus(self, value, qualifier):

        LaserStatusCmdString = '*laser.status ?\r'
        self.__UpdateHelper('LaserStatus', LaserStatusCmdString, value, qualifier)

    def __MatchLaserStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LaserStatus', value, None)

    def SetPIPInput(self, value, qualifier):

        Values = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6',
            'HDMI': '7'
        }

        CmdString = '*pip.input = {0}\r'.format(Values[value])
        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):
        self.__UpdateHelper('PIPInput', '*pip.input ?\r', value, qualifier)

    def __MatchPIPInput(self, match, tag):

        Values = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI',
            '7': 'HDMI'
        }

        self.WriteStatus('PIPInput', Values[match.group(1).decode()], None)

    def SetPIPMode(self, value, qualifier):

        Values = {
            'Off': '*pip.input = 0\r',
            'PIP': '*pip.input = 1\r',
            'PAP': '*pip.input = 2\r',
            'POP': '*pip.input = 3\r'
        }

        self.__SetHelper('PIPMode', Values[value], value, qualifier)

    def UpdatePIPMode(self, value, qualifier):
        self.__UpdateHelper('PIPMode', '*pip.mode ?\r', value, qualifier)

    def __MatchPIPMode(self, match, tag):

        Values = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PAP',
            '3': 'POP'
        }

        self.WriteStatus('PIPMode', Values[match.group(1).decode()], None)

    def SetPIPPosition(self, value, qualifier):

        Values = {
            'Top Left': '*pip.position = 0\r',
            'Top Right': '*pip.position = 1\r',
            'Bottom Left': '*pip.position = 2\r',
            'Bottom Right': '*pip.position = 3\r',
            'Custom': '*pip.position = 4\r'
        }

        self.__SetHelper('PIPPosition', Values[value], value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):
        self.__UpdateHelper('PIPPosition', '*pip.position ?\r', value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        Values = {
            '0': 'Top Left',
            '1': 'Top Right',
            '2': 'Bottom Left',
            '3': 'Bottom Right',
            '4': 'Custom'
        }

        self.WriteStatus('PIPPosition', Values[match.group(1).decode()], None)

    def SetPIPSize(self, value, qualifier):

        Values = {
            'Small': '*pip.size = 0\r',
            'Medium': '*pip.size = 1\r',
            'Large': '*pip.size = 2\r'
        }

        self.__SetHelper('PIPSize', Values[value], value, qualifier)

    def UpdatePIPSize(self, value, qualifier):
        self.__UpdateHelper('PIPSize', '*pip.size ?\r', value, qualifier)

    def __MatchPIPSize(self, match, tag):

        Values = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large'
        }

        self.WriteStatus('PIPSize', Values[match.group(1).decode()], None)

    def SetPIPHorizontalPosition(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '*pip.hpos = {0}\r'.format(value)
            self.__SetHelper('PIPHorizontalPosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPHorizontalPosition')

    def UpdatePIPHorizontalPosition(self, value, qualifier):
        self.__UpdateHelper('PIPHorizontalPosition', '*pip.hpos ?\r', value, qualifier)

    def __MatchPIPHorizontalPosition(self, match, tag):

        self.WriteStatus('PIPHorizontalPosition', int(match.group(1).decode()), None)

    def SetPIPVerticalPosition(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '*pip.vpos = {0}\r'.format(value)
            self.__SetHelper('PIPVerticalPosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPVerticalPosition')

    def UpdatePIPVerticalPosition(self, value, qualifier):
        self.__UpdateHelper('PIPVerticalPosition', '*pip.vpos ?\r', value, qualifier)

    def __MatchPIPVerticalPosition(self, match, tag):

        self.WriteStatus('PIPVerticalPosition', int(match.group(1).decode()), None)

    def SetPower(self, value, qualifier):

        self.__SetHelper('Power', self.PowerSet[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '*power ?\r', value, qualifier)

    def __MatchPower(self, match, tag):

        self.WriteStatus('Power', self.PowerStates[match.group(1).decode()], None)

    def SetShutter(self, value, qualifier):

        Values = {
            'Open': '*shutter = off\r',
            'Close': '*shutter = on\r'
        }

        self.__SetHelper('Shutter', Values[value], value, qualifier)

    def UpdateShutter(self, value, qualifier):
        self.__UpdateHelper('Shutter', '*shutter ?\r', value, qualifier)

    def __MatchShutter(self, match, tag):

        Values = {
            'off': 'Open',
            'on': 'Close'
        }

        self.WriteStatus('Shutter', Values[match.group(1).decode()], None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        self.Error([match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def dpl_1_1032_dual_2D(self):
        self.LampStates = {
            '1': '1',
            '2': '2'
        }

        self.LampModes = {
            'Both': '0',
            '1': '1',
            '2': '2',
            'Auto 1': '3'
        }

        self.LampModeStates = {
            '0': 'Both',
            '1': '1',
            '2': '2',
            '3': 'Auto 1'
        }

        self.Inputs = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6',
            'HDMI': '7',
            'Test Pattern': '8'
        }

        self.InputStates = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI',
            '7': 'HDMI',
            '8': 'Test Pattern'
        }

        self.PowerSet = {
            'On': '*power = on\r',
            'Off': '*power = off\r'
        }

        self.PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

    def dpl_1_1032_dual_3D(self):
        self.LampStates = {
            '1': '1',
            '2': '2'
        }

        self.LampModes = {
            'Both': '0',
            '1': '1',
            '2': '2',
            'Auto 1': '3'
        }

        self.LampModeStates = {
            '0': 'Both',
            '1': '1',
            '2': '2',
            '3': 'Auto 1'
        }

        self.Inputs = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6',
            'HDMI': '7',
            'Test Pattern': '8',
            'Main/DVI': '9',
            'Sub/HDMI': '10',
            'Dual Pipe': '11'
        }

        self.InputStates = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI',
            '7': 'HDMI',
            '8': 'Test Pattern',
            '9': 'Main/DVI',
            '10': 'Sub/HDMI',
            '11': 'Dual Pipe'
        }

        self.PowerSet = {
            'On': '*power = on\r',
            'Off': '*power = off\r'
        }

        self.PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

    def dpl_1_1032_quad_2D(self):
        self.LampStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        self.LampModes = {
            'All': '0',
            'Auto 3': '1',
            'Auto 2': '2',
            'Auto 1': '3',
            '1,2,3': '4',
            '1,2,4': '5',
            '1,3,4': '6',
            '2,3,4': '7',
            '1,2': '8',
            '1,3': '9',
            '1,4': '10',
            '2,3': '11',
            '2,4': '12',
            '3,4': '13',
            '1': '14',
            '2': '15',
            '3': '16',
            '4': '17'
        }

        self.LampModeStates = {
            '0': 'All',
            '1': 'Auto 3',
            '2': 'Auto 2',
            '3': 'Auto 1',
            '4': '1,2,3',
            '5': '1,2,4',
            '6': '1,3,4',
            '7': '2,3,4',
            '8': '1,2',
            '9': '1,3',
            '10': '1,4',
            '11': '2,3',
            '12': '2,4',
            '13': '3,4',
            '14': '1',
            '15': '2',
            '16': '3',
            '17': '4'
        }

        self.Inputs = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6',
            'HDMI': '7',
            'Test Pattern': '8'
        }

        self.InputStates = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI',
            '7': 'HDMI',
            '8': 'Test Pattern'
        }

        self.PowerSet = {
            'On': '*power = on\r',
            'Off': '*power = off\r'
        }

        self.PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

    def dpl_1_1032_quad_3D(self):

        self.LampStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        self.LampModes = {
            'All': '0',
            'Auto 3': '1',
            'Auto 2': '2',
            'Auto 1': '3',
            '1,2,3': '4',
            '1,2,4': '5',
            '1,3,4': '6',
            '2,3,4': '7',
            '1,2': '8',
            '1,3': '9',
            '1,4': '10',
            '2,3': '11',
            '2,4': '12',
            '3,4': '13',
            '1': '14',
            '2': '15',
            '3': '16',
            '4': '17'
        }

        self.LampModeStates = {
            '0': 'All',
            '1': 'Auto 3',
            '2': 'Auto 2',
            '3': 'Auto 1',
            '4': '1,2,3',
            '5': '1,2,4',
            '6': '1,3,4',
            '7': '2,3,4',
            '8': '1,2',
            '9': '1,3',
            '10': '1,4',
            '11': '2,3',
            '12': '2,4',
            '13': '3,4',
            '14': '1',
            '15': '2',
            '16': '3',
            '17': '4'
        }

        self.Inputs = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6',
            'HDMI': '7',
            'Test Pattern': '8',
            'Main/DVI': '9',
            'Sub/HDMI': '10',
            'Dual Pipe': '11'
        }

        self.InputStates = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI',
            '7': 'HDMI',
            '8': 'Test Pattern',
            '9': 'Main/DVI',
            '10': 'Sub/HDMI',
            '11': 'Dual Pipe'
        }

        self.PowerSet = {
            'On': '*power = on\r',
            'Off': '*power = off\r'
        }

        self.PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

    def dpl_1_1032_H660_3D(self):
        self.LampStates = {
            '1': '1',
            '2': '2'
        }

        self.LampModes = {
            'Both': '0',
            '1': '1',
            '2': '2',
            'Auto 1': '3'
        }

        self.LampModeStates = {
            '0': 'Both',
            '1': '1',
            '2': '2',
            '3': 'Auto 1'
        }

        self.Inputs = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6',
            'HDMI': '7',
            'Test Pattern': '8',
            'HDBaseT': '9',
            'DVI 2': '10',
            'HDMI 2': '11',
            'HDMI 3': '12',
            'Dual Pipe': '13'
        }

        self.InputStates = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI',
            '7': 'HDMI',
            '8': 'Test Pattern',
            '9': 'HDBaseT',
            '10': 'DVI 2',
            '11': 'HDMI 2',
            '12': 'HDMI 3',
            '13': 'Dual Pipe',
        }

        self.PowerSet = {
            'On': '*power = on\r',
            'Off': '*power = off\r'
        }

        self.PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

    def dpl_1_1032_8000(self):
        self.LampStates = {
            '1': '1',
            '2': '2'
        }

        self.LampModes = {
            'Both': '0',
            '1': '1',
            '2': '2',
            'Auto 1': '3'
        }

        self.LampModeStates = {
            '0': 'Both',
            '1': '1',
            '2': '2',
            '3': 'Auto 1'
        }

        self.Inputs = {
            'CVBS 1': '0',
            'CVBS 2': '1',
            'S-Video': '2',
            'Component': '3',
            'VGA': '4',
            '3G-SDI': '5',
            'DVI': '6'
        }

        self.InputStates = {
            '0': 'CVBS 1',
            '1': 'CVBS 2',
            '2': 'S-Video',
            '3': 'Component',
            '4': 'VGA',
            '5': '3G-SDI',
            '6': 'DVI'
        }

        self.PowerSet = {
            'On': '*power = on\r',
            'Off': '*power = off\r'
        }

        self.PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

    def dpl_1_1032_laser(self):
        self.LaserStates = {
            '1': '1',
            '2': '2'
        }

        self.LaserModes = {
            'Both': '0',
            '1': '1',
            '2': '2',
            'Auto 1': '3'
        }

        self.LaserModeStates = {
            '0': 'Both',
            '1': '1',
            '2': '2',
            '3': 'Auto 1'
        }

        self.Inputs = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'VGA': '2',
            'Component 1': '3',
            'Component 2': '4',
            'DVI': '5',
            'HDBaseT': '6',
            '3G-SDI': '7'
        }

        self.InputStates = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'VGA',
            '3': 'Component 1',
            '4': 'Component 2',
            '5': 'DVI',
            '6': 'HDBaseT',
            '7': '3G-SDI'
        }

        self.PowerSet = {
            'On': '*power = 1\r',
            'Off': '*power = 0\r'
        }

        self.PowerStates = {
            '1': 'On',
            '0': 'Off'
        }

    def dpl_1_1032_vision_3D(self):
        self.LampStates = {
            '1': '1',
            '2': '2'
        }

        self.LampModes = {
            'Both': '0',
            '1': '1',
            '2': '2',
            'Auto 1': '3'
        }

        self.LampModeStates = {
            '0': 'Both',
            '1': '1',
            '2': '2',
            '3': 'Auto 1'
        }

        self.Inputs = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'VGA': '2',
            'Component 1': '3',
            'Component 2': '4',
            'DVI': '5',
            'HDBaseT': '6'
        }

        self.InputStates = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'VGA',
            '3': 'Component 1',
            '4': 'Component 2',
            '5': 'DVI',
            '6': 'HDBaseT'
        }

        self.PowerSet = {
            'On': '*power = 1\r',
            'Off': '*power = 0\r'
        }

        self.PowerStates = {
            '1': 'On',
            '0': 'Off'
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
