from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentPlug': {'Parameters': ['Device', 'Input'], 'Status': {}},
            'Firmware': {'Status': {}},
            'GPIMode': {'Parameters': ['Device'], 'Status': {}},
            'GPIOTakeScreen': {'Parameters': ['Device'], 'Status': {}},
            'GPOMode': {'Parameters': ['Device', 'Output'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Device', 'Input', 'Input Type'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Device', 'Output'], 'Status': {}},
            'InputAutoSet': {'Parameters': ['Device', 'Input'], 'Status': {}},
            'InputFreeze': {'Parameters': ['Device', 'Input'], 'Status': {}},
            'LayerInput': {'Parameters': ['Screen', 'Preset Mode', 'Layer'], 'Status': {}},
            'MasterPresetMode': {'Status': {}},
            'MasterPresetOriginMemoryNumber': {'Status': {}},
            'MasterPresetRecall': {'Parameters': ['Screen'], 'Status': {}},
            'MasterPresetReset': {'Status': {}},
            'MasterPresetSave': {'Parameters': ['Save Mode'], 'Status': {}},
            'MonitoringFullscreen': {'Parameters': ['Device'], 'Status': {}},
            'NativeBackground': {'Parameters': ['Preset Mode', 'Screen'], 'Status': {}},
            'PresetFilterCategory': {'Parameters': ['Type'], 'Status': {}},
            'PresetLoad': {'Status': {}},
            'PresetLoadandTake': {'Status': {}},
            'PresetMode': {'Status': {}},
            'PresetOriginMemoryNumber': {'Status': {}},
            'PresetRecallScale': {'Status': {}},
            'PresetRecallScreen': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Reboot': {'Parameters': ['Device'], 'Status': {}},
            'Shutdown': {'Parameters': ['Device'], 'Status': {}},
        }

        self.cur_state = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'VEupd0,(\d{1,10})\r\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'IShdc(\d|1\d|2[0-3]),([0-5]),([01])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'OUihc([0-7]),([01])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'PSprf([01])\r\n'), self.__MatchMasterPresetMode, None)
            self.AddMatchString(re.compile(b'PSmet(\d|[1-9]\d|1[0-3]\d|14[0-3])\r\n'), self.__MatchMasterPresetOriginMemoryNumber, None)
            self.AddMatchString(re.compile(b'PMcat(\d|[1-9]\d|[1-9]\d\d|[1-3]\d\d\d|40(?:[1-8]\d|9[0-5]))\r\n'), self.__MatchPresetFilterCategory, None)
            self.AddMatchString(re.compile(b'PMprf([01])\r\n'), self.__MatchPresetMode, None)
            self.AddMatchString(re.compile(b'PMmet(\d|[1-9]\d|1[0-3]\d|14[0-3])\r\n'), self.__MatchPresetOriginMemoryNumber, None)
            self.AddMatchString(re.compile(b'PMlse([01])\r\n'), self.__MatchPresetRecallScale, None)
            self.AddMatchString(re.compile(b'PMscf([0-7])\r\n'), self.__MatchPresetRecallScreen, None)
            self.AddMatchString(re.compile(b'(E1[0-3])\r\n'), self.__MatchError, None)

    def SetCurrentPlug(self, value, qualifier):

        DeviceStates = {
            'Master': 0,
            'Slave': 12
        }

        ValueStateValues = {
            'Analog HD15': '0',
            'Analog DVI': '1',
            'DVI': '2',
            'SDI': '3',
            'HDMI': '4',
            'Display Port': '5'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates and 1 <= int(qualifier['Input']) <= 12:
            self.__SetHelper('CurrentPlug', '{},{}INplg\n'.format(int(qualifier['Input']) - 1 + DeviceStates[qualifier['Device']], ValueStateValues[value]),
                             value, qualifier)
        else:
            self.Discard('Invalid Command for SetCurrentPlug')

    def UpdateFirmware(self, value, qualifier):

        self.__UpdateHelper('Firmware', '0,VEupd\n', value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = int(match.group(1).decode()) if match.group(1).decode().isdigit() else -1
        if 0 <= value <= 0xFFFFFFFF:
            build = value & 0xFFFF
            minor = (value & 0xFF0000) >> 16
            major = (value & 0x7F000000) >> 24
            description = 'BETA' if (value & 0x80000000) == 0x80000000 else 'Released'

            string_value = 'v{0}.{1:02}.{2:02} {3}'.format(major, minor, build, description)

            self.WriteStatus('Firmware', string_value, None)

    def SetGPIMode(self, value, qualifier):

        DeviceStates = {
            'Master': '0',
            'Slave': '1'
        }

        ValueStateValues = {
            'Normal': '0',
            'Take': '1'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates:
            self.__SetHelper('GPIMode', '{},{}GPimo\n'.format(DeviceStates[qualifier['Device']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGPIMode')

    def SetGPIOTakeScreen(self, value, qualifier):

        DeviceStates = {
            'Master': '0',
            'Slave': '1'
        }

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates:
            self.__SetHelper('GPIOTakeScreen', '{},{}GPits\n'.format(DeviceStates[qualifier['Device']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGPIOTakeScreen')

    def SetGPOMode(self, value, qualifier):

        DeviceStates = {
            'Master': 0,
            'Slave': 5
        }

        ValueStateValues = {
            'Free': '0',
            'Tally before transition': '1',
            'Tally after transition': '2'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates and 1 <= int(qualifier['Output']) <= 5:
            self.__SetHelper('GPOMode', '{},{}GPomo\n'.format(int(qualifier['Output']) - 1 + DeviceStates[qualifier['Device']], ValueStateValues[value]), value,
                             qualifier)
        else:
            self.Discard('Invalid Command for SetGPOMode')

    def UpdateHDCPInputStatus(self, value, qualifier):

        DeviceStates = {
            'Master': 0,
            'Slave': 12
        }

        InputTypeStates = {
            'Analog': '0',
            'DVI-A': '1',
            'DVI-D': '2',
            'SDI': '3',
            'HDMI': '4',
            'DisplayPort': '5'
        }

        if qualifier['Device'] in DeviceStates and 1 <= int(qualifier['Input']) <= 12 and qualifier['Input Type'] in InputTypeStates:
            self.__UpdateHelper('HDCPInputStatus', '{},{},IShdc\n'.format(int(qualifier['Input']) - 1 + DeviceStates[qualifier['Device']],
                                                                          InputTypeStates[qualifier['Input Type']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        InputTypeStates = {
            '0': 'Analog',
            '1': 'DVI-A',
            '2': 'DVI-D',
            '3': 'SDI',
            '4': 'HDMI',
            '5': 'DisplayPort'
        }

        ValueStateValues = {
            '1': 'Enabled',
            '0': 'Disabled'
        }

        qualifier = dict()
        input_value = int(match.group(1).decode()) + 1

        if input_value <= 12:
            qualifier['Device'] = 'Master'
            qualifier['Input'] = str(input_value)
        else:
            qualifier['Device'] = 'Slave'
            qualifier['Input'] = str(input_value - 12)
        qualifier['Input Type'] = InputTypeStates[match.group(2).decode()]

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        DeviceStates = {
            'Master': 0,
            'Slave': 4
        }

        if qualifier['Device'] in DeviceStates and 1 <= int(qualifier['Output']) <= 4:
            self.__UpdateHelper('HDCPOutputStatus', '{},OUihc\n'.format(int(qualifier['Output']) - 1 + DeviceStates[qualifier['Device']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Enabled',
            '0': 'Disabled'
        }

        qualifier = dict()
        output_value = int(match.group(1).decode()) + 1
        if output_value <= 4:
            qualifier['Device'] = 'Master'
            qualifier['Output'] = str(output_value)
        else:
            qualifier['Device'] = 'Slave'
            qualifier['Output'] = str(output_value - 4)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetInputAutoSet(self, value, qualifier):

        DeviceStates = {
            'Master': 0,
            'Slave': 12
        }

        if qualifier['Device'] in DeviceStates and 1 <= int(qualifier['Input']) <= 12:
            self.__SetHelper('InputAutoSet', '{}INasi\n'.format(int(qualifier['Input']) - 1 + DeviceStates[qualifier['Device']]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAutoSet')

    def SetInputFreeze(self, value, qualifier):

        DeviceStates = {
            'Master': 0,
            'Slave': 12
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates and 1 <= int(qualifier['Input']) <= 12:
            self.__SetHelper('InputFreeze', '{},{}INfrz\n'.format(int(qualifier['Input']) - 1 + DeviceStates[qualifier['Device']], ValueStateValues[value]),
                             value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputFreeze')

    def SetLayerInput(self, value, qualifier):

        PresetModeStates = {
            'Main': '0',
            'Preview': '1'
        }

        ValueStateValues = {
            'No Input': '0',
            'Input 1 of Master Device': '1',
            'Input 2 of Master Device': '2',
            'Input 3 of Master Device': '3',
            'Input 4 of Master Device': '4',
            'Input 5 of Master Device': '5',
            'Input 6 of Master Device': '6',
            'Input 7 of Master Device': '7',
            'Input 8 of Master Device': '8',
            'Input 9 of Master Device': '9',
            'Input 10 of Master Device': '10',
            'Input 11 of Master Device': '11',
            'Input 12 of Master Device': '12',
            'Input 1 of Slave Device': '13',
            'Input 2 of Slave Device': '14',
            'Input 3 of Slave Device': '15',
            'Input 4 of Slave Device': '16',
            'Input 5 of Slave Device': '17',
            'Input 6 of Slave Device': '18',
            'Input 7 of Slave Device': '19',
            'Input 8 of Slave Device': '20',
            'Input 9 of Slave Device': '21',
            'Input 10 of Slave Device': '22',
            'Input 11 of Slave Device': '23',
            'Input 12 of Slave Device': '24',
            'Frame 1 of Master Device': '25',
            'Frame 2 of Master Device': '26',
            'Frame 3 of Master Device': '27',
            'Frame 4 of Master Device': '28',
            'Frame 1 of Slave Device': '29',
            'Frame 2 of Slave Device': '30',
            'Frame 3 of Slave Device': '31',
            'Frame 4 of Slave Device': '32',
            'Logo 1 of Master Device': '33',
            'Logo 2 of Master Device': '34',
            'Logo 3 of Master Device': '35',
            'Logo 4 of Master Device': '36',
            'Logo 1 of Slave Device': '37',
            'Logo 2 of Slave Device': '38',
            'Logo 3 of Slave Device': '39',
            'Logo 4 of Slave Device': '40',
            'Color (or Black) fill of PiP': '41'
        }

        if value in ValueStateValues and 1 <= int(qualifier['Screen']) <= 8 and qualifier['Preset Mode'] in PresetModeStates and 1 <= int(
                qualifier['Layer']) <= 24:
            self.__SetHelper('LayerInput',
                             '{},{},{},{}SPPEi\n'.format(int(qualifier['Screen']) - 1, PresetModeStates[qualifier['Preset Mode']], int(qualifier['Layer']) - 1,
                                                         ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayerInput')

    def SetMasterPresetMode(self, value, qualifier):

        ValueStateValues = {
            'Program': '0',
            'Preview': '1'
        }

        if value in ValueStateValues:
            self.__SetHelper('MasterPresetMode', '{}PSprf\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterPresetMode')

    def UpdateMasterPresetMode(self, value, qualifier):

        self.__UpdateHelper('MasterPresetMode', 'PSprf\n', value, qualifier)

    def __MatchMasterPresetMode(self, match, tag):

        ValueStateValues = {
            '0': 'Program',
            '1': 'Preview'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MasterPresetMode', value, None)

    def SetMasterPresetOriginMemoryNumber(self, value, qualifier):

        if 1 <= int(value) <= 144:
            self.__SetHelper('MasterPresetOriginMemoryNumber', '{}PSmet\n'.format(int(value) - 1), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterPresetOriginMemoryNumber')

    def UpdateMasterPresetOriginMemoryNumber(self, value, qualifier):

        self.__UpdateHelper('MasterPresetOriginMemoryNumber', 'PSmet\n', value, qualifier)

    def __MatchMasterPresetOriginMemoryNumber(self, match, tag):

        self.WriteStatus('MasterPresetOriginMemoryNumber', str(int(match.group(1).decode()) + 1), None)

    def SetMasterPresetRecall(self, value, qualifier):

        if 1 <= int(qualifier['Screen']) <= 8:
            self.__SetHelper('MasterPresetRecall', '{},1PSose\n'.format(int(qualifier['Screen']) - 1), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterPresetRecall')

    def SetMasterPresetReset(self, value, qualifier):

        self.__SetHelper('MasterPresetReset', '1PSres\n', value, qualifier)

    def SetMasterPresetSave(self, value, qualifier):

        SaveModeStates = {
            'No Save Operation': '0',
            'Selected by User': '1',
            'Auto Allocated by Device': '2'
        }

        if qualifier['Save Mode'] in SaveModeStates:
            self.__SetHelper('MasterPresetSave', '{}PSsav\n'.format(SaveModeStates[qualifier['Save Mode']]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterPresetSave')

    def SetMonitoringFullscreen(self, value, qualifier):

        DeviceStates = {
            'Master': '0',
            'Slave': '1'
        }

        ValueStateValues = {
            'Mosaic': '0',
            'Fullscreen': '1'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates:
            self.__SetHelper('MonitoringFullscreen', '{},{}MLfen\n'.format(DeviceStates[qualifier['Device']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMonitoringFullscreen')

    def SetNativeBackground(self, value, qualifier):

        PresetModeStates = {
            'Program': '0',
            'Preview': '1'
        }

        ScreenStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        ValueStateValues = {
            'None': '1',
            '1': '2',
            '2': '3',
            '3': '4',
            '4': '5',
            '5': '6',
            '6': '7',
            '7': '8',
            '8': '9'
        }

        if value in ValueStateValues and qualifier['Preset Mode'] in PresetModeStates and qualifier['Screen'] in ScreenStates:
            self.__SetHelper('NativeBackground',
                             '{},{},{}SPPNi\n'.format(ScreenStates[qualifier['Screen']], PresetModeStates[qualifier['Preset Mode']], ValueStateValues[value]),
                             value, qualifier)
        else:
            self.Discard('Invalid Command for SetNativeBackground')

    def SetPresetFilterCategory(self, value, qualifier):

        TypeStates = {
            'Source': 0b000000000001,
            'Position': 0b000000000010,
            'Transparency': 0b000000000100,
            'Crop': 0b000000001000,
            'Border': 0b000000010000,
            'Transitions': 0b000000100000,
            'Effects': 0b000001000000,
            'Timing': 0b000010000000,
            'Speed': 0b000100000000,
            'Flying Curve': 0b001000000000,
            'Native Background': 0b010000000000,
            'Mask': 0b100000000000,
            'All': 0b111111111111
        }

        type_state = qualifier['Type']
        ValueStateValues = ['Include', 'Exclude']
        if type_state in TypeStates and value in ValueStateValues:
            if type_state == 'All':
                if value == 'Include':
                    PresetFilterCategoryCmdString = '{}PMcat\n'.format(TypeStates[type_state])
                else:
                    PresetFilterCategoryCmdString = '{}PMcat\n'.format(0x000)
                self.__SetHelper('PresetFilterCategory', PresetFilterCategoryCmdString, value, qualifier)
            else:
                if self.cur_state:
                    cur_value = int(self.cur_state, base=2)
                    new_value = None
                    if value == 'Include' and cur_value & TypeStates[type_state] != TypeStates[type_state]:
                        new_value = cur_value + TypeStates[type_state]
                    elif value == 'Exclude' and cur_value & TypeStates[type_state] == TypeStates[type_state]:
                        new_value = cur_value - TypeStates[type_state]
                    if new_value:
                        PresetFilterCategoryCmdString = '{}PMcat\n'.format(new_value)
                        self.__SetHelper('PresetFilterCategory', PresetFilterCategoryCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetPresetFilterCategory')
        else:
            self.Discard('Invalid Command for SetPresetFilterCategory')

    def UpdatePresetFilterCategory(self, value, qualifier):

        self.__UpdateHelper('PresetFilterCategory', 'PMcat\n', value, qualifier)

    def __MatchPresetFilterCategory(self, match, tag):

        TypeStates = ['Source', 'Position', 'Transparency', 'Crop', 'Border', 'Transitions',
                      'Effects', 'Timing', 'Speed', 'Flying Curve', 'Native Background', 'Mask']

        ValueStateValues = {
            '1': 'Include',
            '0': 'Exclude'
        }

        self.cur_state = '{:012b}'.format(int(match.group(1).decode()))
        for cnt in range(12):
            qualifier = dict()
            qualifier['Type'] = TypeStates[11 - cnt]
            value = ValueStateValues[self.cur_state[cnt]]
            self.WriteStatus('PresetFilterCategory', value, qualifier)

    def SetPresetLoad(self, value, qualifier):

        self.__SetHelper('PresetLoad', '1PMloa\n', value, qualifier)

    def SetPresetLoadandTake(self, value, qualifier):

        self.__SetHelper('PresetLoadandTake', '1PMlot\n', value, qualifier)

    def SetPresetMode(self, value, qualifier):

        ValueStateValues = {
            'Program': '0',
            'Preview': '1'
        }

        if value in ValueStateValues:
            self.__SetHelper('PresetMode', '{}PMprf\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetMode')

    def UpdatePresetMode(self, value, qualifier):

        self.__UpdateHelper('PresetMode', 'PMprf\n', value, qualifier)

    def __MatchPresetMode(self, match, tag):

        ValueStateValues = {
            '0': 'Program',
            '1': 'Preview'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresetMode', value, None)

    def SetPresetOriginMemoryNumber(self, value, qualifier):

        if 1 <= int(value) <= 144:
            self.__SetHelper('PresetOriginMemoryNumber', '{}PMmet\n'.format(int(value) - 1), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetOriginMemoryNumber')

    def UpdatePresetOriginMemoryNumber(self, value, qualifier):

        self.__UpdateHelper('PresetOriginMemoryNumber', 'PMmet\n', value, qualifier)

    def __MatchPresetOriginMemoryNumber(self, match, tag):

        self.WriteStatus('PresetOriginMemoryNumber', str(int(match.group(1).decode()) + 1), None)

    def SetPresetRecallScale(self, value, qualifier):

        ValueStateValues = {
            'Enable automatic resizing': '1',
            'Disable automatic resizing': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('PresetRecallScale', '{}PMlse\n'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallScale')

    def UpdatePresetRecallScale(self, value, qualifier):

        self.__UpdateHelper('PresetRecallScale', 'PMlse\n', value, qualifier)

    def __MatchPresetRecallScale(self, match, tag):

        ValueStateValues = {
            '1': 'Enable automatic resizing',
            '0': 'Disable automatic resizing'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresetRecallScale', value, None)

    def SetPresetRecallScreen(self, value, qualifier):

        if 1 <= int(value) <= 8:
            self.__SetHelper('PresetRecallScreen', '{}PMscf\n'.format(int(value) - 1), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallScreen')

    def UpdatePresetRecallScreen(self, value, qualifier):

        self.__UpdateHelper('PresetRecallScreen', 'PMscf\n', value, qualifier)

    def __MatchPresetRecallScreen(self, match, tag):

        self.WriteStatus('PresetRecallScreen', str(int(match.group(1).decode()) + 1), None)

    def SetPresetReset(self, value, qualifier):

        self.__SetHelper('PresetReset', '1PMres\n', value, qualifier)

    def SetPresetSave(self, value, qualifier):

        self.__SetHelper('PresetSave', '1PMsav\n', value, qualifier)

    def SetReboot(self, value, qualifier):

        DeviceStates = {
            'Master': '0',
            'Slave': '1'
        }

        if qualifier['Device'] in DeviceStates:
            self.__SetHelper('Reboot', '{},1PCreb\n'.format(DeviceStates[qualifier['Device']]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetReboot')

    def SetShutdown(self, value, qualifier):

        DeviceStates = {
            'Master': '0',
            'Slave': '1'
        }

        ValueStateValues = {
            'Idle': '0',
            'Shutdown of device': '1',
            'Shutdown of device and Enable Wake On Lan': '2'
        }

        if value in ValueStateValues and qualifier['Device'] in DeviceStates:
            self.__SetHelper('Shutdown', '{},{}PCsht\n'.format(DeviceStates[qualifier['Device']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutdown')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrorStates = {
            'E10': 'Invalid Command',
            'E11': 'Index Value Error(index value out of range)',
            'E12': 'Index Number Error (too or few indexes)',
            'E13': 'Value Out Of Range Error',
        }

        value = match.group(1).decode()
        self.Error([ErrorStates[value]])

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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
