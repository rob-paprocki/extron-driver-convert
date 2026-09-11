# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from collections import OrderedDict

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
            'DTP3 CrossPoint 42' : self.extr_15_17578,
            'DTP3 CrossPoint 42 USB' : self.extr_15_17578_usb
        }

        self.inputs = ['1', '2', '3', '4']
        self.outputs = ['1', '2']
        self.outputs_a = ['1', '2', '3'] # include audio-only output 3

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'AutoImage': {'Parameters':['Output'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'Freeze': {'Parameters':['Output'], 'Status': {}},
            'GlobalUSBDevicePort': { 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'Logo': {'Parameters':['Output'], 'Status': {}},
            'MACAddress': { 'Status': {}},
            'MatrixIONameCommand': {'Parameters':['Type', 'Number', 'Name'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters':['Type','Number'], 'Status': {}},
            'MatrixIONumberSelect': { 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output','Tie Type'], 'Status': {}},
            'OutputResolution': {'Parameters':['Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Output','Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters':['Output','Tie Type'], 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'RefreshMatrixIONames': { 'Status': {}},
            'SerialNumber': { 'Status': {}},
            'USBDevicePort': {'Parameters':['Port'], 'Status': {}},
            'USBInput': { 'Status': {}},
            'USBInputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'USBOutputSignalStatus': {'Parameters':['Output'], 'Status': {}},
            'VideoMute': {'Parameters':['Output'], 'Status': {}},
            'Volume': { 'Status': {}}
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True

        self.matrix_tie_status = None
        self.matrix_io_names = {}
        self.matrix_io_names_received = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([1-3])\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Bld(\d.\d{2}.\d{4})\r\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(b'Frz([1-2])\*([0-1])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'HdcpE([1-4])\*([0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'In00 (00|01) (00|01) (00|01) (00|01) \r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'SigI(0|1)\r\n'), self.__MatchInputSignalStatus, 'Unsolicited')
            self.AddMatchString(re.compile(b'LogoE([1-2])\*(\d+)\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'Iph ([0-9A-Z-]{17})\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(re.compile(b'Nm([io])([1-9]),([ \S]{0,30})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(re.compile(b'Rate([0-2])\*(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'Psav([0-9])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(b'UsbcX([0-1])\r\n'), self.__MatchUSBDevicePort, None) # substring of "Query", adding first
            self.AddMatchString(re.compile(b'UsbcX([01 ]+)\r\n'), self.__MatchUSBDevicePort, "Query")
            self.AddMatchString(re.compile(b'UsbcX([1-4])\*(0|1)\r\n'), self.__MatchUSBDevicePort, "Set")
            self.AddMatchString(re.compile(b'UsbcI(0[0-1]) (0[0-1]) (0[0-1]) \r\n'), self.__MatchUSBInputSignalStatus, None)
            self.AddMatchString(re.compile(b'UsbcO0 ([0-1]) ([0-1]) ([0-1]) ([0-1]) \r\n'), self.__MatchUSBOutputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vol([-+]\d{1,3})\r\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'PrstR\d+\r\n'), self.__MatchQik, None)  # Response to a Set Preset Recall command
            self.AddMatchString(re.compile(b'Rpr\d+(?:\*\d+)?\r\n'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'Vgp00 Out01\*(0[0-4] 0[0-4] 0[0-4]) Vid\r\nVgp00 Out02\*(0[0-4] 0[0-4] 0[0-4] 0[0-4]) Aud\r\n'), self.__MatchAllMatrixTie, None)
            self.AddMatchString(re.compile(b'Vgp00 Out03\*0([0-3])[ \d]+Usb\r\n'), self.__MatchUSBInput, None)
            self.AddMatchString(re.compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'In0([0-3]) Usb\r\n'), self.__MatchUSBInput, None)
            self.AddMatchString(re.compile(b'Inf19\*(\w+)\r\n'), self.__MatchSerialNumber, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)             
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        
        self.OnConnected()
        self.VerboseDisabled = False
        
        self.UpdateAllMatrixTie(None, None)

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def __MatchQik(self, match, tag):

        self.UpdateAllMatrixTie(None, None)
        if self.ModelName == 'DTP3 CrossPoint 42 USB':
            self.UpdateUSBInput(None, None)

    def __MatchPreset(self, match, tag):

        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.matrix_tie_status = OrderedDict((input_, OrderedDict((output, 'Untied') for output in self.outputs_a)) for input_ in self.inputs)
        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

    def InputTieStatusHelper(self, tie, output=None):

        if tie == 'Individual':
            output_range = [str(output)]
        else:
            output_range = self.outputs_a
        for input_ in self.inputs:
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': input_, 'Output': output})

    def OutputTieStatusHelper(self, tie, output=None):

        seen = set()

        if tie == 'Individual':
            output_range = [output]
        else:
            output_range = self.outputs_a
        for input_ in self.inputs:
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': input_}) # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', input_, {'Output': output, 'Tie Type': tie_type})
                        if self.matrix_io_names_received: # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written (prevents debug log error)
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': output, 'Tie Type': tie_type})
                    seen.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': output, 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', input_, {'Output': output, 'Tie Type': 'Audio'})
                    if self.matrix_io_names_received:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': output, 'Tie Type': 'Audio'})
                    seen.add(output)
        for o in output_range:
            if o not in seen:
                self.WriteStatus('OutputTieStatus', '0', {'Output': o, 'Tie Type': 'Audio'})
                self.WriteStatus('OutputTieStatus', '0', {'Output': o, 'Tie Type': 'Audio/Video'})
                if self.matrix_io_names_received:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': o, 'Tie Type': 'Audio'})
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': o, 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        if not self.matrix_tie_status:
            return
        
        ties = {
            'Video': match.group(1).decode(),
            'Audio': match.group(2).decode()
        }

        for tag, match in ties.items():
            opposite_tag = 'Video' if tag == 'Audio' else 'Audio'
            for output, input_ in enumerate(match.strip().split()[1:], 1):
                input_ = str(int(input_))

                if input_ in ['0', '-1']:
                    continue
                if input_ not in self.inputs:
                    continue
                if str(output) not in self.outputs_a:
                    continue

                if self.matrix_tie_status[input_][str(output)] == opposite_tag:
                    self.matrix_tie_status[input_][str(output)] = 'Audio/Video'
                else:
                    self.matrix_tie_status[input_][str(output)] = tag

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        OutputValues = {
            '1': '1',
            '2': '2',
            '3': '3',
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if qualifier['Output'] in OutputValues and value in ValueStateValues:
            AudioMuteCmdString = '{}*{}Z'.format(OutputValues[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputValues = {
            '1': '1',
            '2': '2',
            '3': '3',
        }

        if qualifier['Output'] in OutputValues:
            AudioMuteCmdString = '{}Z'.format(OutputValues[qualifier['Output']])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {
            'Output': str(int(match.group(1).decode()))
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02',
            }

        ValueStateValues = {
            'Execute': '0',
            'Execute and Fill': '1',
            'Execute and Follow': '2'
            }

        if 1 <= int(qualifier['Output']) <= 2 and value in ValueStateValues:
            AutoImageCmdString = '{}*{}A'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = '*q'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)
        

    def __MatchFirmware(self, match, tag):
        
        self.WriteStatus('Firmware', match.group(1).decode(), None)

    def SetFreeze(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02',
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Output']) <= 2 and value in ValueStateValues:
            FreezeCmdString = '{}*{}F'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02',
            }

        if 1 <= int(qualifier['Output']) <= 2:
            FreezeCmdString = '{}F'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {
            'Output': str(int(match.group(1).decode()))
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, qualifier)

    def SetGlobalUSBDevicePort(self, value, qualifier):

        ValueStates = {
            'On': '1',
            'Off': '0'
            }

        if value in ValueStates:
            GlobalUSBDevicePortCmdString = 'wX{}USBC\r'.format(ValueStates[value])
            self.__SetHelper('GlobalUSBDevicePort', GlobalUSBDevicePortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalUSBDevicePort')

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video': '1',
            'Video & Sync': '2',
            'Off': '0'
            }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = '{}*B'.format(ValueStateValues[value])
            self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def SetHDCPInputAuthorization(self, value, qualifier):

        InputStates = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04'
            }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Input']) <= 4 and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{}*{}HDCP\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        InputStates = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04'
            }

        if 1 <= int(qualifier['Input']) <= 4:
            HDCPInputAuthorizationCmdString = 'wE{}HDCP\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        qualifier = {
            'Input': match.group(1).decode()
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        input_ = qualifier['Input']

        if 1 <= int(input_) <= 4:
            InputSignalStatusCmdString = '0LS'
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        InputStates = {
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4'
            }

        ValueStateValues = {
            '01': 'Active',
            '00': 'Not Active'
            }

        if tag == 'Unsolicited':
            self.UpdateInputSignalStatus(None, {'Input': '1'})
        else:
            for input_ in InputStates.values():
                value = ValueStateValues[match.group(int(input_)).decode()]
                self.WriteStatus('InputSignalStatus', value, {'Input': input_})

    def SetLogo(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02'
            }

        ValueStateValues = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            'Off': '0'
            }

        if 1 <= int(qualifier['Output']) <= 2 and value in ValueStateValues:
            LogoCmdString = 'wE{}*{}LOGO\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02'
            }

        if 1 <= int(qualifier['Output']) <= 2:
            LogoCmdString = 'wE{}LOGO\r'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogo')

    def __MatchLogo(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '0': 'Off'
            }

        qualifier = {
            'Output': str(int(match.group(1).decode()))
        }
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Logo', value, qualifier)

    def UpdateMACAddress(self, value, qualifier):

        MACAddressCmdString = 'wCH\r'
        self.__UpdateHelper('MACAddress', MACAddressCmdString, value, qualifier)

    def __MatchMACAddress(self, match, tag):
        
        self.WriteStatus('MACAddress', match.group(1).decode(), None)

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input':    'NI',
            'Output':   'NO'
        }
        type_ = qualifier['Type']

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 0 <= len(name) <= 30 and type_ in TypeStates:
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[type_])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
            if type_ == 'Input': #only write the name if it's for input
                for output in self.outputs:
                    audioVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Audio'}) # get audio input
                    if audioVal == number:
                        self.WriteStatus('OutputTieStatusName', name, {'Output': output, 'Tie Type': 'Audio'})

                    audioVideoVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Audio/Video'}) # get A/V input
                    if audioVideoVal == number: # if video input is the same as audio input
                        self.WriteStatus('OutputTieStatusName', name, {'Output': output, 'Tie Type': 'Audio/Video'}) # write AV name
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        
        number = match.group(2).decode()
        value = match.group(3).decode()
        if (type_ == 'Input' and number not in self.inputs) or (type_ == 'Output' and number not in self.outputs):
            return
        
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        self.matrix_io_names.setdefault(type_, {}).setdefault(number, value)
        if not self.matrix_io_names_received and \
            len(self.matrix_io_names.get('Input', {})) == len(self.inputs) and \
                len(self.matrix_io_names.get('Output', {})) == len(self.outputs):
            self.matrix_io_names_received = True
        if type_ == 'Input': # only write the name if type is input
            for output in self.outputs:
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Audio'}) # get audio input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': output, 'Tie Type': 'Audio'})
                
                audioVideoVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Audio/Video'}) # get A/V input
                if audioVideoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': output, 'Tie Type': 'Audio/Video'})

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        TieTypeStates = {
            'Audio':        '$', 
            'Audio/Video':  '!', 
        }
        tie_type = qualifier['Tie Type']
        
        if input_ in ['0'] + self.inputs and output in self.outputs_a + ['All'] and tie_type in TieTypeStates:
            if tie_type == 'Audio' and output in self.outputs:
                self.Discard('Invalid Command for SetMatrixTieCommand')
                return
            
            if output == 'All':
                MatrixTieCommandCmdString = '{}*{}'.format(input_,  TieTypeStates[tie_type])
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                MatrixTieCommandCmdString = '{}*{}{}'.format(input_, output, TieTypeStates[tie_type])
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetOutputResolution(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02',
            }

        ValueStateValues = {
            '640x480 (60Hz)': '10',
            '800x600 (60Hz)': '11',
            '1024x768 (60Hz)': '12',
            '1280x768 (60Hz)': '13',
            '1280x800 (60Hz)': '14',
            '1280x1024 (60Hz)': '15',
            '1360x768 (60Hz)': '16',
            '1366x768 (60Hz)': '17',
            '1440x900 (60Hz)': '18',
            '1400x1050 (60Hz)': '19',
            '1600x900 (60Hz)': '20',
            '1680x1050 (60Hz)': '21',
            '1600x1200 (60Hz)': '22',
            '1920x1200 (60Hz)': '23',
            '480p (59.94Hz)': '24',
            '480p (60Hz)': '25',
            '576p (50Hz)': '26',
            '720p (25Hz)': '29',
            '720p (29.97Hz)': '30',
            '720p (30Hz)': '31',
            '720p (50Hz)': '32',
            '720p (59.94Hz)': '33',
            '720p (60Hz)': '34',
            '1080i (50Hz)': '35',
            '1080i (59.94Hz)': '36',
            '1080i (60Hz)': '37',
            '1080p (23.98Hz)': '38',
            '1080p (24Hz)': '39',
            '1080p (25Hz)': '40',
            '1080p (29.97Hz)': '41',
            '1080p (30Hz)': '42',
            '1080p (50Hz)': '43',
            '1080p (59.94Hz)': '44',
            '1080p (60Hz)': '45',
            '2048x1080 (23.98Hz)': '46',
            '2048x1080 (24Hz)': '47',
            '2048x1080 (25Hz)': '48',
            '2048x1080 (29.97Hz)': '49',
            '2048x1080 (30Hz)': '50',
            '2048x1080 (50Hz)': '51',
            '2048x1080 (59.94Hz)': '52',
            '2048x1080 (60Hz)': '53',
            '2048x1200 (60Hz)': '54',
            '2048x1536 (60Hz)': '55',
            '2560x1080 (60Hz)': '56',
            '2560x1440 (60Hz)': '57',
            '2560x1600 (60Hz)': '58',
            '3840x2160 (23.98Hz)': '59',
            '3840x2160 (24Hz)': '60',
            '3840x2160 (25Hz)': '61',
            '3840x2160 (29.97Hz)': '62',
            '3840x2160 (30Hz)': '63',
            '3840x2160 (50Hz)': '64',
            '3840x2160 (59.94Hz)': '65',
            '3840x2160 (60Hz)': '66',
            '4096x2160 (23.98Hz)': '69',
            '4096x2160 (24Hz)': '70',
            '4096x2160 (25Hz)': '71',
            '4096x2160 (29.97Hz)': '72',
            '4096x2160 (30Hz)': '73',
            '4096x2160 (50Hz)': '74',
            '4096x2160 (59.94Hz)': '75',
            '4096x2160 (60Hz)': '76',
            'Custom 1': '201',
            'Custom 2': '202',
            'Custom 3': '203',
            'Custom 4': '204'
            }

        if 1 <= int(qualifier['Output']) <= 2 and value in ValueStateValues:
            OutputResolutionCmdString = 'w{}*{}RATE\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputStates = {
            '1': '01',
            '2': '02',
            }

        if 1 <= int(qualifier['Output']) <= 2:
            OutputResolutionCmdString = 'w{}RATE\r'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputResolution')

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10': '640x480 (60Hz)',
            '11': '800x600 (60Hz)',
            '12': '1024x768 (60Hz)',
            '13': '1280x768 (60Hz)',
            '14': '1280x800 (60Hz)',
            '15': '1280x1024 (60Hz)',
            '16': '1360x768 (60Hz)',
            '17': '1366x768 (60Hz)',
            '18': '1440x900 (60Hz)',
            '19': '1400x1050 (60Hz)',
            '20': '1600x900 (60Hz)',
            '21': '1680x1050 (60Hz)',
            '22': '1600x1200 (60Hz)',
            '23': '1920x1200 (60Hz)',
            '24': '480p (59.94Hz)',
            '25': '480p (60Hz)',
            '26': '576p (50Hz)',
            '29': '720p (25Hz)',
            '30': '720p (29.97Hz)',
            '31': '720p (30Hz)',
            '32': '720p (50Hz)',
            '33': '720p (59.94Hz)',
            '34': '720p (60Hz)',
            '35': '1080i (50Hz)',
            '36': '1080i (59.94Hz)',
            '37': '1080i (60Hz)',
            '38': '1080p (23.98Hz)',
            '39': '1080p (24Hz)',
            '40': '1080p (25Hz)',
            '41': '1080p (29.97Hz)',
            '42': '1080p (30Hz)',
            '43': '1080p (50Hz)',
            '44': '1080p (59.94Hz)',
            '45': '1080p (60Hz)',
            '46': '2048x1080 (23.98Hz)',
            '47': '2048x1080 (24Hz)',
            '48': '2048x1080 (25Hz)',
            '49': '2048x1080 (29.97Hz)',
            '50': '2048x1080 (30Hz)',
            '51': '2048x1080 (50Hz)',
            '52': '2048x1080 (59.94Hz)',
            '53': '2048x1080 (60Hz)',
            '54': '2048x1200 (60Hz)',
            '55': '2048x1536 (60Hz)',
            '56': '2560x1080 (60Hz)',
            '57': '2560x1440 (60Hz)',
            '58': '2560x1600 (60Hz)',
            '59': '3840x2160 (23.98Hz)',
            '60': '3840x2160 (24Hz)',
            '61': '3840x2160 (25Hz)',
            '62': '3840x2160 (29.97Hz)',
            '63': '3840x2160 (30Hz)',
            '64': '3840x2160 (50Hz)',
            '65': '3840x2160 (59.94Hz)',
            '66': '3840x2160 (60Hz)',
            '69': '4096x2160 (23.98Hz)',
            '70': '4096x2160 (24Hz)',
            '71': '4096x2160 (25Hz)',
            '72': '4096x2160 (29.97Hz)',
            '73': '4096x2160 (30Hz)',
            '74': '4096x2160 (50Hz)',
            '75': '4096x2160 (59.94Hz)',
            '76': '4096x2160 (60Hz)',
            '201': 'Custom 1',
            '202': 'Custom 2',
            '203': 'Custom 3',
            '204': 'Custom 4'
            }

        qualifier = {
            'Output': str(int(match.group(1).decode()))
        }
        value = ValueStateValues[str(int(match.group(2).decode()))]
        self.WriteStatus('OutputResolution', value, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):

        if not self.matrix_tie_status:
            return
        
        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, tag, *, audio_only_input=None):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video'
        }

        if audio_only_input is None:
            output = str(int(match.group(1).decode()))
            input_ = str(int(match.group(2).decode()))
            tietype = TieTypeStates[match.group(3).decode()]
        else:
            output = '3'
            input_ = audio_only_input
            tietype = 'Audio'
        if tietype == 'Audio' and output != '3':
            return
        if tietype in ['Video', 'Audio/Video'] and output not in self.outputs:
            return
        if tietype == 'Video':
            tietype = 'Audio/Video'

        for i in self.inputs:
            if i == input_:
                self.matrix_tie_status[i][output] = tietype
            elif input_ == '0' or i != input_:
                self.matrix_tie_status[i][output] = 'Untied'

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, tag):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video',
        }
        new_input = str(int(match.group(4).decode()))
        tietype = TieTypeStates[match.group(5).decode()]
        if tietype == 'Audio':
            self.__MatchIndividualTie(None, None, audio_only_input=new_input)
            return
        for output in self.outputs if tietype == 'Video' else self.outputs_a:
            for input_ in self.inputs:
                if input_ == new_input:
                    if output in self.outputs: # for regular outputs 1 - 2
                        self.matrix_tie_status[input_][output] = 'Audio/Video'
                    elif output in self.outputs_a: # for audio only output 3
                        self.matrix_tie_status[input_][output] = 'Audio'
                else:
                    self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2'
            }

        if value in ValueStateValues:
            PowerSaveModeCmdString = 'w{}PSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '9': 'Low Power (Over Temperature)'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = '{}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def SetRefreshMatrixIONames(self, value, qualifier):

        for input_ in self.inputs:
            self.Send('w{}NI\r'.format(input_))
        for output in self.outputs:
            self.Send('w{}NO\r'.format(output))

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = '19i'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier) 

    def __MatchSerialNumber(self, match, tag):
        
        self.WriteStatus('SerialNumber', match.group(1).decode(), None)

    def SetUSBDevicePort(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
            }

        if 1 <= int(qualifier['Port']) <= 4 and value in ValueStateValues:
            USBDevicePortCmdString = 'wX{}*{}USBC\r'.format(qualifier['Port'], ValueStateValues[value])
            self.__SetHelper('USBDevicePort', USBDevicePortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBDevicePort')

    def UpdateUSBDevicePort(self, value, qualifier):

        USBDevicePortCmdString = 'wXUSBC\r'
        self.__UpdateHelper('USBDevicePort', USBDevicePortCmdString, value, qualifier)

    def __MatchUSBDevicePort(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }
            
        if tag == "Set":
            port = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            qualifier = {
                'Port': port
            }
            self.WriteStatus('USBDevicePort', value, qualifier)
        else:
            if tag == "Query":
                values = match.group(1).decode().strip().split(' ')
                for port, value in enumerate(values[:5], 1):
                    value = ValueStateValues[value]
                    qualifier = {
                        'Port': str(port)
                    }
                    self.WriteStatus('USBDevicePort', value, qualifier)
            else:
                value = ValueStateValues[match.group(1).decode()]
                for port in ['1', '2', '3', '4', '5']:
                    qualifier = {
                        'Port': port
                    }
                    self.WriteStatus('USBDevicePort', value, qualifier)

    def SetUSBInput(self, value, qualifier):

        if 0 <= int(value) <= 3:
            USBInputCmdString = '{}*^'.format(int(value))
            self.__SetHelper('USBInput', USBInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBInput')

    def UpdateUSBInput(self, value, qualifier):

        USBInputCmdString = 'w0*1*3VC\r\n'
        self.__UpdateHelper('USBInput', USBInputCmdString, value, qualifier)

    def __MatchUSBInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('USBInput', value, None)

    def UpdateUSBInputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 3:
            USBInputSignalStatusCmdString = 'wIUSBC\r'
            self.__UpdateHelper('USBInputSignalStatus', USBInputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUSBInputSignalStatus')

    def __MatchUSBInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '01': 'Active',
            '00': 'Not Active'
            }

        for ports in ['1', '2', '3']:
            value = ValueStateValues[match.group(int(ports)).decode()]
            qualifier = {
                'Input': ports
            }
            self.WriteStatus('USBInputSignalStatus', value, qualifier)

    def UpdateUSBOutputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= 4:
            USBOutputSignalStatusCmdString = 'wOUSBC\r'
            self.__UpdateHelper('USBOutputSignalStatus', USBOutputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateUSBOutputSignalStatus')

    def __MatchUSBOutputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
            }

        for ports in ['1', '2', '3', '4']:
            value = ValueStateValues[match.group(int(ports)).decode()]
            qualifier = {
                'Output': ports
            }
            self.WriteStatus('USBOutputSignalStatus', value, qualifier)

    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
            }

        ValueStateValues = {
            'Video': '1',
            'Video & Sync': '2',
            'Off': '0'
            }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            VideoMuteCmdString = '{}*{}B'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def SetVolume(self, value, qualifier):

        if -100 <= value <= 0:
            VolumeCmdString = '{}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if -100 <= value <= 0:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System or command timed out',
            '22': 'Busy',
            '24': 'Privileges violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found',
            '33': 'Bad file type or size (for logo assignment)'
        }

        value = match.group(1).decode()
        self.Error(['An error occurred: ' + DEVICE_ERROR_CODES.get(value, value + ': Unknown error')])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.matrix_tie_status = None
        self.matrix_io_names = {}
        self.matrix_io_names_received = False

        self.EchoDisabled = True
        self.VerboseDisabled = True

    def extr_15_17578(self):
        
        self.ModelName = 'DTP3 CrossPoint 42'

    def extr_15_17578_usb(self):

        self.ModelName = 'DTP3 CrossPoint 42 USB'

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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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
