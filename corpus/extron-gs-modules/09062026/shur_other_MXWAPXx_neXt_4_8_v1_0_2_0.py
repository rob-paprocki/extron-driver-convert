# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
        self.Models = {
            'MXWAPX4': self.shur_31_17299_4,
            'neXt 4': self.shur_31_17299_4,
            'MXWAPX8': self.shur_31_17299_8,
            'neXt 8': self.shur_31_17299_8
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BatteryCharge': {'Parameters': ['Port'], 'Status': {}},
            'BatteryHealth': {'Parameters': ['Port'], 'Status': {}},
            'BatteryRunTime': {'Parameters': ['Port'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'MicrophoneButtonStatus': {'Parameters': ['Port'], 'Status': {}},
            'MicrophoneLED': {'Parameters': ['Port', 'Color'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'TransmitterStatus': {'Parameters': ['Port'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP ([1-8]) BATT_CHARGE ([01][0-9][0-9]) >'), self.__MatchBatteryCharge, None)
            self.AddMatchString(re.compile(b'< REP ([1-8]) BATT_HEALTH ([01][0-9][0-9]) >'), self.__MatchBatteryHealth, None)
            self.AddMatchString(re.compile(b'< REP ([1-8]) BATT_RUN_TIME (\d+) >'), self.__MatchBatteryRunTime, None)
            self.AddMatchString(re.compile(b'< REP FW_VER \{(\d+\.\d+\.\d+\.\d+\*?) } >'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'< REP (\d+) INPUT_CH_GAIN (\d+) >'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'< REP (\d+) INPUT_CH_MUTE (MUTED|ACTIVE) >'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'< REP ([1-8]) BUTTON_STS (ON|OFF) >'), self.__MatchMicrophoneButtonStatus, None)
            self.AddMatchString(re.compile(b'< REP ([1-8]) LED_STATUS (ON|OF|ST|FL|PU) (ON|OF|ST|FL|PU) >'), self.__MatchMicrophoneLED, None)
            self.AddMatchString(re.compile(b'< REP (\d+) OUTPUT_CH_GAIN (\d+) >'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'< REP (\d+) OUTPUT_CH_MUTE (MUTED|ACTIVE) >'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'< REP CH ([1-8]) TX_STATUS (ACTIVE|MUTED|ON_CHARGER|UNKNOWN) >'), self.__MatchTransmitterStatus, None)

            self.AddMatchString(re.compile(b'< REP ([1-8]) (BATT_HEALTH|BATT_CHARGE) (253|255) >'), self.__MatchError, None)

    def UpdateBatteryCharge(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            BatteryChargeCmdString = '< GET {} BATT_CHARGE >'.format(qualifier['Port'])
            self.__UpdateHelper('BatteryCharge', BatteryChargeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryCharge')

    def __MatchBatteryCharge(self, match, tag):

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BatteryCharge', value, qualifier)

    def UpdateBatteryHealth(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            BatteryHealthCmdString = '< GET {} BATT_HEALTH >'.format(qualifier['Port'])
            self.__UpdateHelper('BatteryHealth', BatteryHealthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryHealth')

    def __MatchBatteryHealth(self, match, tag):

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BatteryHealth', value, qualifier)

    def UpdateBatteryRunTime(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            BatteryRunTimeCmdString = '< GET {} BATT_RUN_TIME >'.format(qualifier['Port'])
            self.__UpdateHelper('BatteryRunTime', BatteryRunTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryRunTime')

    def __MatchBatteryRunTime(self, match, tag):

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 65531:
            self.WriteStatus('BatteryRunTime', value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '< GET FW_VER >'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetInputGain(self, value, qualifier):

        InputStates = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Dante 10': '10',
            'Dante 11': '11',
            'Dante 12': '12',
            'Dante 13': '13',
            'Dante 14': '14',
            'Dante 15': '15',
            'Dante 16': '16',
            'Dante 17': '17',
            'Dante 18': '18',
            'Dante 19': '19',
            'Mic 1': '21',
            'Mic 2': '22',
            'Mic 3': '23',
            'Mic 4': '24',
            'Mic 5': '25',
            'Mic 6': '26',
            'Mic 7': '27',
            'Mic 8': '28',
            'Mic 9': '29',
            'Mic 10': '30',
            'Mic 11': '31',
            'Mic 12': '32',
            'Mic 13': '33',
            'Mic 14': '34',
            'Mic 15': '35',
            'Mic 16': '36',
            'Mic 17': '37',
            'Mic 18': '38',
            'Mic 19': '39',
            'USB': '51'
            }

        if qualifier['Input'] in InputStates and -110 <= value <= 30:
            gain = value * 10 + 1100
            InputGainCmdString = '< SET {} INPUT_CH_GAIN {} >'.format(InputStates[qualifier['Input']], int(gain))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputStates = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Dante 10': '10',
            'Dante 11': '11',
            'Dante 12': '12',
            'Dante 13': '13',
            'Dante 14': '14',
            'Dante 15': '15',
            'Dante 16': '16',
            'Dante 17': '17',
            'Dante 18': '18',
            'Dante 19': '19',
            'Mic 1': '21',
            'Mic 2': '22',
            'Mic 3': '23',
            'Mic 4': '24',
            'Mic 5': '25',
            'Mic 6': '26',
            'Mic 7': '27',
            'Mic 8': '28',
            'Mic 9': '29',
            'Mic 10': '30',
            'Mic 11': '31',
            'Mic 12': '32',
            'Mic 13': '33',
            'Mic 14': '34',
            'Mic 15': '35',
            'Mic 16': '36',
            'Mic 17': '37',
            'Mic 18': '38',
            'Mic 19': '39',
            'USB': '51'
            }

        if qualifier['Input'] in InputStates:
            InputGainCmdString = '< GET {} INPUT_CH_GAIN >'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        InputStates = {
            '1': 'Dante 1',
            '2': 'Dante 2',
            '3': 'Dante 3',
            '4': 'Dante 4',
            '5': 'Dante 5',
            '6': 'Dante 6',
            '7': 'Dante 7',
            '8': 'Dante 8',
            '9': 'Dante 9',
            '10': 'Dante 10',
            '11': 'Dante 11',
            '12': 'Dante 12',
            '13': 'Dante 13',
            '14': 'Dante 14',
            '15': 'Dante 15',
            '16': 'Dante 16',
            '17': 'Dante 17',
            '18': 'Dante 18',
            '19': 'Dante 19',
            '21': 'Mic 1',
            '22': 'Mic 2',
            '23': 'Mic 3',
            '24': 'Mic 4',
            '25': 'Mic 5',
            '26': 'Mic 6',
            '27': 'Mic 7',
            '28': 'Mic 8',
            '29': 'Mic 9',
            '30': 'Mic 10',
            '31': 'Mic 11',
            '32': 'Mic 12',
            '33': 'Mic 13',
            '34': 'Mic 14',
            '35': 'Mic 15',
            '36': 'Mic 16',
            '37': 'Mic 17',
            '38': 'Mic 18',
            '39': 'Mic 19',
            '51': 'USB'
            }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode()) - 1100
        value = value / 10
        if -110 <= value <= 30:
            self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        InputStates = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Dante 10': '10',
            'Dante 11': '11',
            'Dante 12': '12',
            'Dante 13': '13',
            'Dante 14': '14',
            'Dante 15': '15',
            'Dante 16': '16',
            'Dante 17': '17',
            'Dante 18': '18',
            'Dante 19': '19',
            'Mic 1': '21',
            'Mic 2': '22',
            'Mic 3': '23',
            'Mic 4': '24',
            'Mic 5': '25',
            'Mic 6': '26',
            'Mic 7': '27',
            'Mic 8': '28',
            'Mic 9': '29',
            'Mic 10': '30',
            'Mic 11': '31',
            'Mic 12': '32',
            'Mic 13': '33',
            'Mic 14': '34',
            'Mic 15': '35',
            'Mic 16': '36',
            'Mic 17': '37',
            'Mic 18': '38',
            'Mic 19': '39',
            'USB': '51'
            }

        ValueStateValues = {
            'On': 'MUTED',
            'Off': 'ACTIVE'
            }

        if qualifier['Input'] in InputStates and value in ValueStateValues:
            InputMuteCmdString = '< SET {} INPUT_CH_MUTE {} >'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        InputStates = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Dante 10': '10',
            'Dante 11': '11',
            'Dante 12': '12',
            'Dante 13': '13',
            'Dante 14': '14',
            'Dante 15': '15',
            'Dante 16': '16',
            'Dante 17': '17',
            'Dante 18': '18',
            'Dante 19': '19',
            'Mic 1': '21',
            'Mic 2': '22',
            'Mic 3': '23',
            'Mic 4': '24',
            'Mic 5': '25',
            'Mic 6': '26',
            'Mic 7': '27',
            'Mic 8': '28',
            'Mic 9': '29',
            'Mic 10': '30',
            'Mic 11': '31',
            'Mic 12': '32',
            'Mic 13': '33',
            'Mic 14': '34',
            'Mic 15': '35',
            'Mic 16': '36',
            'Mic 17': '37',
            'Mic 18': '38',
            'Mic 19': '39',
            'USB': '51'
            }

        if qualifier['Input'] in InputStates:
            InputMuteCmdString = '< GET {} INPUT_CH_MUTE >'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        InputStates = {
            '1': 'Dante 1',
            '2': 'Dante 2',
            '3': 'Dante 3',
            '4': 'Dante 4',
            '5': 'Dante 5',
            '6': 'Dante 6',
            '7': 'Dante 7',
            '8': 'Dante 8',
            '9': 'Dante 9',
            '10': 'Dante 10',
            '11': 'Dante 11',
            '12': 'Dante 12',
            '13': 'Dante 13',
            '14': 'Dante 14',
            '15': 'Dante 15',
            '16': 'Dante 16',
            '17': 'Dante 17',
            '18': 'Dante 18',
            '19': 'Dante 19',
            '21': 'Mic 1',
            '22': 'Mic 2',
            '23': 'Mic 3',
            '24': 'Mic 4',
            '25': 'Mic 5',
            '26': 'Mic 6',
            '27': 'Mic 7',
            '28': 'Mic 8',
            '29': 'Mic 9',
            '30': 'Mic 10',
            '31': 'Mic 11',
            '32': 'Mic 12',
            '33': 'Mic 13',
            '34': 'Mic 14',
            '35': 'Mic 15',
            '36': 'Mic 16',
            '37': 'Mic 17',
            '38': 'Mic 18',
            '39': 'Mic 19',
            '51': 'USB'
            }

        ValueStateValues = {
            'MUTED': 'On',
            'ACTIVE': 'Off'
            }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def UpdateMicrophoneButtonStatus(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            MicrophoneButtonStatusCmdString = '< GET {} BUTTON_STS >'.format(qualifier['Port'])
            self.__UpdateHelper('MicrophoneButtonStatus', MicrophoneButtonStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneButtonStatus')

    def __MatchMicrophoneButtonStatus(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
            }

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicrophoneButtonStatus', value, qualifier)

    def SetMicrophoneLED(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OF',
            'Strobe': 'ST',
            'Flash': 'FL',
            'Pulse': 'PU'
            }

        if 1 <= int(qualifier['Port']) <= self.ports and qualifier['Color'] in ['Red', 'Green'] and value in ValueStateValues:
            if qualifier['Color'] == 'Red':
                MicrophoneLEDCmdString = '< SET {} LED_STATUS {} NC >'.format(qualifier['Port'], ValueStateValues[value])
            else:
                MicrophoneLEDCmdString = '< SET {} LED_STATUS NC {} >'.format(qualifier['Port'], ValueStateValues[value])
            self.__SetHelper('MicrophoneLED', MicrophoneLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneLED')

    def UpdateMicrophoneLED(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports and qualifier['Color'] in ['Red', 'Green']:
            MicrophoneLEDCmdString = '< GET {} LED_STATUS >'.format(qualifier['Port'])
            self.__UpdateHelper('MicrophoneLED', MicrophoneLEDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneLED')

    def __MatchMicrophoneLED(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OF': 'Off',
            'ST': 'Strobe',
            'FL': 'Flash',
            'PU': 'Pulse'
            }

        port = match.group(1).decode()
        redValue = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicrophoneLED', redValue, {'Port': port, 'Color': 'Red'})

        greenValue = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MicrophoneLED', greenValue, {'Port': port, 'Color': 'Green'})

    def SetOutputGain(self, value, qualifier):

        if qualifier['Output'] in self.OutputStatesOut and -110 <= value <= 30:
            gain = value * 10 + 1100
            OutputGainCmdString = '< SET {} OUTPUT_CH_GAIN {} >'.format(self.OutputStatesOut[qualifier['Output']], int(gain))
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        if qualifier['Output'] in self.OutputStatesOut:
            OutputGainCmdString = '< GET {} OUTPUT_CH_GAIN >'.format(self.OutputStatesOut[qualifier['Output']])
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {}
        qualifier['Output'] = self.OutputStatesIn[match.group(1).decode()]
        value = int(match.group(2).decode()) - 1100
        value = value / 10
        if -110 <= value <= 30:
            self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTED',
            'Off': 'ACTIVE'
            }

        if qualifier['Output'] in self.OutputStatesOut and value in ValueStateValues:
            OutputMuteCmdString = '< SET {} OUTPUT_CH_MUTE {} >'.format(self.OutputStatesOut[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        if qualifier['Output'] in self.OutputStatesOut:
            OutputMuteCmdString = '< GET {} OUTPUT_CH_MUTE >'.format(self.OutputStatesOut[qualifier['Output']])
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            'MUTED': 'On',
            'ACTIVE': 'Off'
            }

        qualifier = {}
        qualifier['Output'] = self.OutputStatesIn[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetTransmitterStatus(self, value, qualifier):

        ValueStateValues = {
            'Undocked & Unmuted':   'ACTIVE',
            'Undocked & Muted':     'MUTED',
            'Off':                  'OFF'
        }

        if 1 <= int(qualifier['Port']) <= self.ports and value in ValueStateValues:
            TransmitterStatusCmdString = '< SET CH {} TX_STATUS {} >'.format(qualifier['Port'], ValueStateValues[value])
            self.__SetHelper('TransmitterStatus', TransmitterStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitterStatus')

    def UpdateTransmitterStatus(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            TransmitterStatusCmdString = '< GET CH {} TX_STATUS >'.format(qualifier['Port'])
            self.__UpdateHelper('TransmitterStatus', TransmitterStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterStatus')

    def __MatchTransmitterStatus(self, match, tag):

        ValueStateValues = {
            'ACTIVE': 'Undocked & Unmuted',
            'MUTED': 'Undocked & Muted',
            'ON_CHARGER': 'Docked',
            'UNKNOWN': 'Offline/Unlinked'
            }

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterStatus', value, qualifier)

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

        CommandStateValues = {
            'BATT_HEALTH': 'Battery Health',
            'BATT_CHARGE': 'Battery Charge',
        }

        ErrorStateValues = {
            '253': 'Error',
            '255': 'Unknown Exception',
        }

        port = match.group(1).decode()
        command = CommandStateValues[match.group(2).decode()]
        error = ErrorStateValues[match.group(3).decode()]
        self.Error(['Error: An {} has occurred for command {} on port {}.'.format(error, command, port)])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def shur_31_17299_4(self):

        self.ports = 4

        self.OutputStatesOut = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Analog': '42',
            'USB': '51',
            'Back-channel Audio': '61'
            }

        self.OutputStatesIn = {
            '1': 'Dante 1',
            '2': 'Dante 2',
            '3': 'Dante 3',
            '4': 'Dante 4',
            '5': 'Dante 5',
            '42': 'Analog',
            '51': 'USB',
            '61': 'Back-channel Audio'
            }

    def shur_31_17299_8(self):

        self.ports = 8

        self.OutputStatesOut = {
            'Dante 1': '1',
            'Dante 2': '2',
            'Dante 3': '3',
            'Dante 4': '4',
            'Dante 5': '5',
            'Dante 6': '6',
            'Dante 7': '7',
            'Dante 8': '8',
            'Dante 9': '9',
            'Analog': '42',
            'USB': '51',
            'Back-channel Audio': '61'
            }

        self.OutputStatesIn = {
            '1': 'Dante 1',
            '2': 'Dante 2',
            '3': 'Dante 3',
            '4': 'Dante 4',
            '5': 'Dante 5',
            '6': 'Dante 6',
            '7': 'Dante 7',
            '8': 'Dante 8',
            '9': 'Dante 9',
            '42': 'Analog',
            '51': 'USB',
            '61': 'Back-channel Audio'
            }

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()