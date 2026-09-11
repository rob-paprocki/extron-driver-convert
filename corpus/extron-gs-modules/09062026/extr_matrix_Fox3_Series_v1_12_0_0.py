# Copyright 2026, Extron. All rights reserved.

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
        self.NumOfInputs = 8
        self.NumOfOutputs = 8
        self.Models = {
            'FOX3 Matrix 160x': self.extr_15_4803_160x,
            'FOX3 Matrix 24x': self.extr_15_4803_24x,
            'FOX3 Matrix 320x': self.extr_15_4803_320x,
            'FOX3 Matrix 40x': self.extr_15_4803_40x,
            'FOX3 Matrix 560x': self.extr_15_4803_560x,
            'FOX3 Matrix 80x': self.extr_15_4803_80x,
            'FOX3 Matrix 840x': self.extr_15_4803_840x
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'FanSpeed': {'Parameters': ['Fan'], 'Status': {}},
            'GlobalAudioMute': { 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'Laser': {'Parameters': ['Output'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters': ['Type'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'MatrixIONumberSelect': { 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PartNumber': { 'Status': {}},
            'PowerSupplyStatus': {'Parameters': ['Power Supply'], 'Status': {}},
            'PowerSupplyVoltage': {'Parameters': ['Power Supply'], 'Status': {}},
            'PresetNameCommand': {'Parameters': ['Preset'], 'Status': {}},
            'PresetNameStatus': {'Parameters': ['Preset'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'RefreshMatrixIONames': { 'Status': {}},
            'RoomPresetRecall': {'Parameters': ['Room'], 'Status': {}},
            'RoomPresetSave': {'Parameters': ['Room'], 'Status': {}},
            'Temperature': {'Parameters': ['Scale'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}}
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{1,3})([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{1,3})([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{1,3})([0-9 -]*)Dmp\r\n'), self.__MatchAllMatrixTie, 'DMP')
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{1,3})([0-9 -]*)Dte\r\n'), self.__MatchAllMatrixTie, 'Dante')
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{1,3})([0-9 -]*)Ana\r\n'), self.__MatchAllMatrixTie, 'Analog')
            self.AddMatchString(re.compile(b'Amt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, 'AudioUnsolicited')
            self.AddMatchString(re.compile(b'Amt([0-1])\r\n'), self.__MatchVideoMute, 'AudioGlobal')
            self.AddMatchString(re.compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(re.compile(b'In00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Nm([io])([0-9]{2,3}),([ \S]{1,16})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(re.compile(b'(60-15(53|76|77|78)-[01]2|60-1716-(\d{2})|60-1978-(\d{2})|60-1882-(\d{2}))\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(re.compile(b'Nmg([0-9]{1,2}),([ \S]{1,32})\r\n'), self.__MatchPresetNameStatus, None)
            self.AddMatchString(re.compile(b'Sts00\*(\d+\.\d+) (\d+\.\d+) (\d+\.\d+)F (\d+\.\d+)C  ((?:\d+RPM )+) ([012]) ([012])\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'Mut00\*([0-2 ]+)\r\n'), self.__MatchVideoMute, 'Query')
            self.AddMatchString(re.compile(b'Vmt(\d+)\*([0-2])\r\n'), self.__MatchVideoMute, 'VideoUnsolicited')
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, 'VideoGlobal')
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            
            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'Rpr(\d+)\r\n'), self.__MatchQik, None)

            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    @property
    def NumberofInputs(self):
        return self.NumOfInputs

    @NumberofInputs.setter
    def NumberofInputs(self, value):
        if 1 <= int(value) <= 840:
            self.NumOfInputs = int(value)

    @property
    def NumberofOutputs(self):
        return self.NumOfOutputs

    @NumberofOutputs.setter
    def NumberofOutputs(self, value):
        if 1 <= int(value) <= 840:
            self.NumOfOutputs = int(value)

    def __MatchEchoMode(self, match, tag):
        self.EchoDisabled = False

    def __MatchVerboseMode(self, match, tag):
        self.OnConnected()

        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchQik(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.matrix_tie_status_dmp = [['Untied' for _ in range(self.OutputSize)] for _ in range(8)]
        self.matrix_tie_status_analog = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.NumOfAnalogAudio)]
        self.matrix_tie_status_dante = [['Untied' for _ in range(self.OutputSize)] for _ in range(32)]

        for query in self.refresh_matrix_strings:
            self.Send(query)

    def OutputTieStatusHelper(self, tie, output=None):
        
        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSize)

        matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self.NumOfOutputs)}) # used to check if 'Matrix IO Name Status' exists or not
        for input_ in range(self.InputSize):
            inputCalc = str(input_ + 1)
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': inputCalc}) # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                outputCalc = str(output + 1)
                zeroCalc = '0'
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', inputCalc, {'Output': outputCalc, 'Tie Type': tie_type})
                        if matrixIONameStatus: # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': outputCalc, 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', zeroCalc, {'Output': outputCalc, 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', inputCalc, {'Output': outputCalc, 'Tie Type': 'Audio'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': outputCalc, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': outputCalc, 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', zeroCalc, {'Output': outputCalc, 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', inputCalc, {'Output': outputCalc, 'Tie Type': 'Video'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': outputCalc, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': outputCalc, 'Tie Type': 'Video'})
                    VideoList.add(output)
        for input_ in range(8):
            for output in output_range:
                tietype = self.matrix_tie_status_dmp[input_][output]
                if tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', 'DMP Exp Input ' + str(input_+1), {'Output': str(output+1), 'Tie Type': 'Audio'})
                    AudioList.add(output)

        for input_ in range(32):
            for output in output_range:
                tietype = self.matrix_tie_status_dante[input_][output]
                if tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', 'Dante Input ' + str(input_+1), {'Output': str(output+1), 'Tie Type': 'Audio'})
                    AudioList.add(output)

        for input_ in range(self.NumOfAnalogAudio):
            for output in output_range:
                tietype = self.matrix_tie_status_analog[input_][output]
                if tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', 'Analog Audio Input ' + str(input_+1), {'Output': str(output+1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
        
        for o in output_range:
            outputCalc = str(o + 1)
            zeroCalc = '0'
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', zeroCalc, {'Output': outputCalc, 'Tie Type': 'Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': outputCalc, 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', zeroCalc, {'Output': outputCalc, 'Tie Type': 'Audio'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': outputCalc, 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', zeroCalc, {'Output': outputCalc, 'Tie Type': 'Audio/Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': outputCalc, 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        if tag == 'Audio' or tag == 'Video':
            av_counter_max = self.OutputSize
            opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

            for i in input_list:
                if i != '---' and (30001 <= int(i) <= 30008 or 40001 <= int(i) <= 40032 or 50001 <= int(i) <= 50000+self.NumOfAnalogAudio):
                    if 30001 <= int(i) <= 30008:
                        prefix = 'DMP Exp Input '
                        input_ = int(i) - 30000
                        self.matrix_tie_status_dmp[input_ - 1][int(current_output - 1)] = 'Audio'
                    elif 40001 <= int(i) <= 40032:
                        prefix = 'Dante Input '
                        input_ = int(i) - 40000
                        self.matrix_tie_status_dante[input_ - 1][int(current_output - 1)] = 'Audio'
                    elif 50001 <= int(i) <= 50000+self.NumOfAnalogAudio:
                        prefix = 'Analog Audio Input '
                        input_ = int(i) - 50000
                        self.matrix_tie_status_analog[input_ - 1][int(current_output - 1)] = 'Audio'
                    self.audio_status_counter += 1
                    current_output += 1
                else:
                    if i != '---':
                        if tag == 'Audio':
                            self.audio_status_counter += 1
                        elif tag == 'Video':
                            self.video_status_counter += 1
                        if i != '000':
                            if tag in ['Video', 'Audio']:
                                if opposite_tag == self.matrix_tie_status[int(i) - 1][int(current_output - 1)]:
                                    self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                                else:
                                    self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                        current_output += 1
            if self.audio_status_counter == av_counter_max and self.video_status_counter == av_counter_max:
                self.OutputTieStatusHelper('All')
        else:
            taglookup = {
                'DMP': 'DMP Exp Output ',
                'Dante': 'Dante Output ',
                'Analog': 'Analog Audio Output ',
            }
            
            for index, input_ in enumerate(input_list):
                if input_ == '---':
                    continue
                elif input_ != '000':
                    prefix = ''
                    inputCalc = None
                    if 30001 <= int(input_) <= 30008:
                        prefix = 'DMP Exp Input '
                        input_ = int(input_) - 30000
                    elif 40001 <= int(input_) <= 40032:
                        prefix = 'Dante Input '
                        input_ = int(input_) - 40000
                    elif 50001 <= int(input_) <= 50000+self.NumOfAnalogAudio:
                        prefix = 'Analog Audio Input '
                        input_ = int(input_) - 50000
                    inputCalc = prefix + str(int(input_))
                    outputcalc = taglookup[tag]  + str(index+1)
                    zeroCalc = '0'
                    self.WriteStatus('OutputTieStatus', inputCalc, {'Output': outputcalc, 'Tie Type': 'Audio'})
                else:
                    outputcalc = taglookup[tag]  + str(index+1)
                    zeroCalc = '0'
                    self.WriteStatus('OutputTieStatus', zeroCalc, {'Output': outputcalc, 'Tie Type': 'Audio'})

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Output']) <= self.OutputSize and value in ValueStateValues:
            AudioMuteCmdString = '{0}*{1}Z'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateVideoMute( None, qualifier)

    def UpdateFanSpeed(self, value, qualifier):

        fan = int(qualifier['Fan'])

        if 1 <= fan <= self.NumOfFans:
            self.UpdateTemperature(None, {'Scale': 'Celsius'})
        else:
            self.Discard('Invalid Command for UpdateFanSpeed')

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = '{0}*Z'.format(ValueStateValues[value])
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = '{0}*B'.format(ValueStateValues[value])
            self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def UpdateInputSignalStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputSize:
            InputSignalStatusCmdString = 'w0LS\r'
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        for input_, value in enumerate(match.group(1).decode()):
            self.WriteStatus('InputSignalStatus', ValueStateValues[value], {'Input': str(input_+1)})
        input_+=1
        while input_ < self.InputSize:
            self.WriteStatus('InputSignalStatus', 'Not Active', {'Input': str(input_+1)})
            input_ += 1

    def SetLaser(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if (qualifier['Output'] == 'All' or 1 <= int(qualifier['Output']) <= self.OutputSize) and value in ValueStateValues:
            if qualifier['Output'] == 'All':
                LaserCmdString = 'w{}*FIBR\r'.format(ValueStateValues[value])
            else:
                LaserCmdString = 'w{}*{}FIBR\r'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('Laser', LaserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLaser')

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 1 <= len(name) <= 16 and qualifier['Type'] in TypeStates:
            if name == ' ': # if name is a space
                name = '{} #{}'.format(qualifier['Type'], number) # reset to default name
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = str(int(match.group(2).decode()))
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})

        matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self.NumOfOutputs)})
        if matrixIONameStatus and type_ == 'Input': # only write the name if 'Matrix IO Name Status' has been written and type is input
            for output in range(1, self.OutputSize + 1):
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(output), 'Tie Type': 'Audio'}) # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(output), 'Tie Type': 'Video'}) # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(output), 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(output), 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(output), 'Tie Type': 'Audio/Video'})

    def SetRefreshMatrixIONames(self, value, qualifier):

        self.Debug = True
        self.UpdateMatrixIONames( None, None)

    def UpdateMatrixIONames(self, value, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number',
            '13': 'Invalid parameter',
            '14': 'Invalid command for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System or command timed out',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privileges violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
        }
        for input_ in range(1, self.NumOfInputs+1):
            if input_ <= self.InputSize:
                res = self.SendAndWait('w{0}NI\r'.format(input_), 0.2, deliTag='\n')
                if res:
                    res = res.decode()
                    if res[0] == 'N':
                        num = int(res[3:5])
                        value = res[6:-2]
                        self.WriteStatus('MatrixIONameStatus', value, {'Type': 'Input', 'Number': str(num)})
                    else:
                        if res[1:3] in DEVICE_ERROR_CODES:
                            self.Error(['Matrix Input {0} Name: {1}'.format(input_, DEVICE_ERROR_CODES[res[1:3]])])
                        else:
                            self.Error(['Matrix Input {0} Name: Unrecognized error code: {1}'.format(input_, res[0:3])])
                else:
                    self.Error(['Matrix Input {0} Name: Invalid/unexpected response'.format(input_)])
            else:
                self.Discard('Invalid Command for UpdateMatrixIONames')
        for output in range(1, self.NumOfOutputs+1):
            if output <= self.OutputSize:
                res = self.SendAndWait('w{0}NO\r'.format(output), 0.2, deliTag='\n')
                if res:
                    res = res.decode()
                    if res[0] == 'N':
                        num = int(res[3:5])
                        value = res[6:-2]
                        self.WriteStatus('MatrixIONameStatus', value, {'Type': 'Output', 'Number': str(num)})
                    else:
                        if res[1:3] in DEVICE_ERROR_CODES:
                            self.Error(['Matrix Output {0} Name: {1}'.format(output, DEVICE_ERROR_CODES[res[1:3]])])
                        else:
                            self.Error(['Matrix Output {0} Name: Unrecognized error code: {1}'.format(output, res[0:3])])
                else:
                    self.Error(['Matrix Output {0} Name: Invalid/unexpected response'.format(output)])
            else:
                self.Discard('Invalid Command for UpdateMatrixIONames')

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        TieTypeStates = {
            'Audio':        '$',  
            'Video':        '%', 
            'Audio/Video':  '!'
        }

        if 'DMP Exp Input' in qualifier['Input'] or 'Dante Input' in qualifier['Input'] or 'Analog Audio Input' in qualifier['Input']:
            InputStates = {
                'DMP Exp Input 1': '30001',
                'DMP Exp Input 2': '30002',
                'DMP Exp Input 3': '30003',
                'DMP Exp Input 4': '30004',
                'DMP Exp Input 5': '30005',
                'DMP Exp Input 6': '30006',
                'DMP Exp Input 7': '30007',
                'DMP Exp Input 8': '30008',
                'Dante Input 1': '40001',
                'Dante Input 2': '40002',
                'Dante Input 3': '40003',
                'Dante Input 4': '40004',
                'Dante Input 5': '40005',
                'Dante Input 6': '40006',
                'Dante Input 7': '40007',
                'Dante Input 8': '40008',
                'Dante Input 9': '40009',
                'Dante Input 10': '40010',
                'Dante Input 11': '40011',
                'Dante Input 12': '40012',
                'Dante Input 13': '40013',
                'Dante Input 14': '40014',
                'Dante Input 15': '40015',
                'Dante Input 16': '40016',
                'Dante Input 17': '40017',
                'Dante Input 18': '40018',
                'Dante Input 19': '40019',
                'Dante Input 20': '40020',
                'Dante Input 21': '40021',
                'Dante Input 22': '40022',
                'Dante Input 23': '40023',
                'Dante Input 24': '40024',
                'Dante Input 25': '40025',
                'Dante Input 26': '40026',
                'Dante Input 27': '40027',
                'Dante Input 28': '40028',
                'Dante Input 29': '40029',
                'Dante Input 30': '40030',
                'Dante Input 31': '40031',
                'Dante Input 32': '40032',
                'Analog Audio Input 1': '50001',
                'Analog Audio Input 2': '50002',
                'Analog Audio Input 3': '50003',
                'Analog Audio Input 4': '50004',
            }
            input_ = InputStates[qualifier['Input']]

        if 'DMP Exp Output' in qualifier['Output'] or 'Dante Output' in qualifier['Output'] or 'Analog Audio Output' in qualifier['Output']:
            OutputStates = {
                'DMP Exp Output 1': '30001',
                'DMP Exp Output 2': '30002',
                'DMP Exp Output 3': '30003',
                'DMP Exp Output 4': '30004',
                'DMP Exp Output 5': '30005',
                'DMP Exp Output 6': '30006',
                'DMP Exp Output 7': '30007',
                'DMP Exp Output 8': '30008',
                'Dante Output 1': '40001',
                'Dante Output 2': '40002',
                'Dante Output 3': '40003',
                'Dante Output 4': '40004',
                'Dante Output 5': '40005',
                'Dante Output 6': '40006',
                'Dante Output 7': '40007',
                'Dante Output 8': '40008',
                'Dante Output 9': '40009',
                'Dante Output 10': '40010',
                'Dante Output 11': '40011',
                'Dante Output 12': '40012',
                'Dante Output 13': '40013',
                'Dante Output 14': '40014',
                'Dante Output 15': '40015',
                'Dante Output 16': '40016',
                'Dante Output 17': '40017',
                'Dante Output 18': '40018',
                'Dante Output 19': '40019',
                'Dante Output 20': '40020',
                'Dante Output 21': '40021',
                'Dante Output 22': '40022',
                'Dante Output 23': '40023',
                'Dante Output 24': '40024',
                'Dante Output 25': '40025',
                'Dante Output 26': '40026',
                'Dante Output 27': '40027',
                'Dante Output 28': '40028',
                'Dante Output 29': '40029',
                'Dante Output 30': '40030',
                'Dante Output 31': '40031',
                'Dante Output 32': '40032',
                'Analog Audio Output 1': '50001',
                'Analog Audio Output 2': '50002',
                'Analog Audio Output 3': '50003',
                'Analog Audio Output 4': '50004',
            }
            output = OutputStates[qualifier['Output']]
        
        if (0 <= int(input_) <= self.InputSize or qualifier['Input'] in InputStates) and qualifier['Tie Type'] in TieTypeStates:
            if output == 'All':
                MatrixTieCommandCmdString = '{0}*{1}'.format(input_, TieTypeStates[qualifier['Tie Type']])
            elif 1 <= int(output) <= self.OutputSize or qualifier['Output'] in OutputStates:
                MatrixTieCommandCmdString = '{0}*{1}{2}'.format(input_, output, TieTypeStates[qualifier['Tie Type']])

            if MatrixTieCommandCmdString:
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')  

    def __MatchOutputTieStatus(self, match, tag):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, tag):
        
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video'
        }
        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]
        if tietype == 'Audio/Video' and \
            ((30001 <= int(input_) <= 30008 or 40001 <= int(input_) <= 40032 or 50001 <= int(input_) <= 50000+self.NumOfAnalogAudio) or \
             (30001 <= int(output) <= 30008 or 40001 <= int(output) <= 40032 or 50001 <= int(output) <= 50000+self.NumOfAnalogAudio)):
            tietype = 'Audio'

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output-1]
                if i != input_-1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output-1] = 'Untied'
                elif i == input_-1:
                    self.matrix_tie_status[i][output-1] = 'Audio/Video'
            for i in range(8):
                current_tie = self.matrix_tie_status_dmp[i][output-1]
                if current_tie == 'Audio':
                    self.matrix_tie_status_dmp[i][output-1] = 'Untied'
            for i in range(32):
                current_tie = self.matrix_tie_status_dante[i][output-1]
                if current_tie == 'Audio':
                    self.matrix_tie_status_dante[i][output-1] = 'Untied'
            for i in range(self.NumOfAnalogAudio):
                current_tie = self.matrix_tie_status_analog[i][output-1]
                if current_tie == 'Audio':
                    self.matrix_tie_status_analog[i][output-1] = 'Untied'

            self.OutputTieStatusHelper('Individual', output)

        elif tietype in ['Video', 'Audio']:
            if tietype == 'Audio' and (30001 <= int(output) <= 30008 or 40001 <= int(output) <= 40032 or 50001 <= int(output) <= 50000+self.NumOfAnalogAudio):
                prefix = ''
                outprefix = ''
                if 30001 <= int(input_) <= 30008:
                    prefix = 'DMP Exp Input '
                    input_ = prefix + str(int(input_) - 30000)
                elif 40001 <= int(input_) <= 40032:
                    prefix = 'Dante Input '
                    input_ = prefix + str(int(input_) - 40000)
                elif 50001 <= int(input_) <= 50000+self.NumOfAnalogAudio:
                    prefix = 'Analog Audio Input '
                    input_ = prefix + str(int(input_) - 50000)
                if 30001 <= int(output) <= 30008:
                    outprefix = 'DMP Exp Output '
                    output = outprefix + str(int(output) - 30000)
                elif 40001 <= int(output) <= 40032:
                    outprefix = 'Dante Output '
                    output = outprefix + str(int(output) - 40000)
                elif 50001 <= int(output) <= 50000+self.NumOfAnalogAudio:
                    outprefix = 'Analog Audio Output '
                    output = outprefix + str(int(output) - 50000)
                input_ = str(input_)
                self.WriteStatus('OutputTieStatus', input_, {'Output': output, 'Tie Type': 'Audio'})

            elif tietype == 'Audio' and (1 <= int(output) <= self.OutputSize) and (30001 <= int(input_) <= 30008 or 40001 <= int(input_) <= 40032 or 50001 <= int(input_) <= 50000+self.NumOfAnalogAudio):
                if 30001 <= int(input_) <= 30008:
                    prefix = 'DMP Exp Input '
                    input_ = str(int(input_) - 30000)
                    for i in range(self.NumOfAnalogAudio):
                        current_tie = self.matrix_tie_status_analog[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_analog[i][output-1] = 'Untied'
                    for i in range(8):
                        current_tie = self.matrix_tie_status_dmp[i][output-1]
                        if i != int(input_)-1 and current_tie == 'Audio':
                            self.matrix_tie_status_dmp[i][output-1] = 'Untied'
                        elif i == int(input_)-1:
                            self.matrix_tie_status_dmp[i][output-1] = 'Audio'
                    for i in range(32):
                        current_tie = self.matrix_tie_status_dante[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_dante[i][output-1] = 'Untied'
                    for i in range(self.InputSize):
                        current_tie = self.matrix_tie_status[i][output-1]
                        if current_tie == 'Audio/Video' or current_tie == 'Video':
                            self.matrix_tie_status[i][output-1] = 'Video'
                        else:
                            self.matrix_tie_status[i][output-1] = 'Untied'

                elif 40001 <= int(input_) <= 40032:
                    prefix = 'Dante Input '
                    input_ = str(int(input_) - 40000)
                    for i in range(self.NumOfAnalogAudio):
                        current_tie = self.matrix_tie_status_analog[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_analog[i][output-1] = 'Untied'
                    for i in range(8):
                        current_tie = self.matrix_tie_status_dmp[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_dmp[i][output-1] = 'Untied'
                    for i in range(32):
                        current_tie = self.matrix_tie_status_dante[i][output-1]
                        if i != int(input_)-1 and current_tie == 'Audio':
                            self.matrix_tie_status_dante[i][output-1] = 'Untied'
                        elif i == int(input_)-1:
                            self.matrix_tie_status_dante[i][output-1] = 'Audio'
                    for i in range(self.InputSize):
                        current_tie = self.matrix_tie_status[i][output-1]
                        if current_tie == 'Audio/Video' or current_tie == 'Video':
                            self.matrix_tie_status[i][output-1] = 'Video'
                        else:
                            self.matrix_tie_status[i][output-1] = 'Untied'

                elif 50001 <= int(input_) <= 50000+self.NumOfAnalogAudio:
                    prefix = 'Analog Audio Input '
                    input_ = str(int(input_) - 50000)
                    for i in range(self.NumOfAnalogAudio):
                        current_tie = self.matrix_tie_status_analog[i][output-1]
                        if i != int(input_)-1 and current_tie == 'Audio':
                            self.matrix_tie_status_analog[i][output-1] = 'Untied'
                        elif i == int(input_)-1:
                            self.matrix_tie_status_analog[i][output-1] = 'Audio'
                    for i in range(8):
                        current_tie = self.matrix_tie_status_dmp[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_dmp[i][output-1] = 'Untied'
                    for i in range(32):
                        current_tie = self.matrix_tie_status_dante[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_dante[i][output-1] = 'Untied'
                    for i in range(self.InputSize):
                        current_tie = self.matrix_tie_status[i][output-1]
                        if current_tie == 'Audio/Video' or current_tie == 'Video':
                            self.matrix_tie_status[i][output-1] = 'Video'
                        else:
                            self.matrix_tie_status[i][output-1] = 'Untied'
                            
                self.OutputTieStatusHelper('Individual', output)

            else:
                for i in range(self.InputSize):
                    current_tie = self.matrix_tie_status[i][output-1]
                    opTag = 'Audio' if tietype == 'Video' else 'Video'
                    if i == input_-1:
                        if current_tie == opTag or current_tie == 'Audio/Video':
                            self.matrix_tie_status[i][output-1] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[i][output-1] = tietype
                    elif input_ == 0 or i != input_-1:
                        if current_tie == tietype:
                            self.matrix_tie_status[i][output-1] = 'Untied'
                        elif current_tie == 'Audio/Video':
                            self.matrix_tie_status[i][output-1] = opTag

                if tietype == 'Audio':
                    for i in range (8):
                        current_tie = self.matrix_tie_status_dmp[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_dmp[i][output-1] = 'Untied'
                    for i in range(32):
                        current_tie = self.matrix_tie_status_dante[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_dante[i][output-1] = 'Untied'
                    for i in range(self.NumOfAnalogAudio):
                        current_tie = self.matrix_tie_status_analog[i][output-1]
                        if current_tie == 'Audio':
                            self.matrix_tie_status_analog[i][output-1] = 'Untied'

                self.OutputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, tag):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video'
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if (30001 <= int(new_input) <= 30008 or 40001 <= int(new_input) <= 40032 or 50001 <= int(new_input) <= 50000+self.NumOfAnalogAudio):
            if 30001 <= int(new_input) <= 30008:
                prefix = 'DMP Exp Input '
                input_ = str(int(new_input) - 30000)
                input_ = int(input_)
                for output in range(self.OutputSize):
                    for i in range(self.NumOfAnalogAudio):
                        self.matrix_tie_status_analog[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(8):
                        if i == input_-1:
                            self.matrix_tie_status_dmp[i][output] = 'Audio'
                        else:
                            self.matrix_tie_status_dmp[i][output] = 'Untied'
                for i in range(32):
                    for output in range(self.OutputSize):
                        for i in range(32):
                            self.matrix_tie_status_dante[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(self.InputSize):
                        current_tie = self.matrix_tie_status[i][output]
                        if current_tie == 'Audio/Video' or current_tie == 'Video':
                            self.matrix_tie_status[i][output] = 'Video'
                        else:
                            self.matrix_tie_status[i][output] = 'Untied'

            elif 40001 <= int(new_input) <= 40032:
                prefix = 'Dante Input '
                input_ = str(int(new_input) - 40000)
                input_ = int(input_)
                for output in range(self.OutputSize):
                    for i in range(self.NumOfAnalogAudio):
                        self.matrix_tie_status_analog[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(8):
                        self.matrix_tie_status_dmp[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(32):
                        if i == input_ - 1:
                            self.matrix_tie_status_dante[i][output] = 'Audio'
                        else:
                            self.matrix_tie_status_dante[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(self.InputSize):
                        current_tie = self.matrix_tie_status[i][output]
                        if current_tie == 'Audio/Video' or current_tie == 'Video':
                            self.matrix_tie_status[i][output] = 'Video'
                        else:
                            self.matrix_tie_status[i][output] = 'Untied'

            elif 50001 <= int(new_input) <= 50000+self.NumOfAnalogAudio:
                prefix = 'Analog Audio Input '
                input_ = str(int(new_input) - 50000)
                input_ = int(input_)
                for output in range(self.OutputSize):
                    for i in range(self.NumOfAnalogAudio):
                        if i == input_ - 1:
                            self.matrix_tie_status_analog[i][output] = 'Audio'
                        else:
                            self.matrix_tie_status_analog[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(8):
                        self.matrix_tie_status_dmp[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(32):
                        self.matrix_tie_status_dante[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(self.InputSize):
                        current_tie = self.matrix_tie_status[i][output]
                        if current_tie == 'Audio/Video' or current_tie == 'Video':
                            self.matrix_tie_status[i][output] = 'Video'
                        else:
                            self.matrix_tie_status[i][output] = 'Untied'

            for output in range(8):
                self.WriteStatus('OutputTieStatus', prefix + str(input_), {'Output': 'DMP Exp Output ' + str(output + 1), 'Tie Type': 'Audio'}) 
            for output in range(32):
                self.WriteStatus('OutputTieStatus', prefix + str(input_), {'Output': 'Dante Output ' + str(output + 1), 'Tie Type': 'Audio'}) 
            for output in range(self.NumOfAnalogAudio):
                self.WriteStatus('OutputTieStatus', prefix + str(input_), {'Output': 'Analog Audio Output ' + str(output + 1), 'Tie Type': 'Audio'})

            self.OutputTieStatusHelper('All')

        else:
            if tietype in ['Audio', 'Video']:
                op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
                for output in range(self.OutputSize):
                    for input_ in range(self.InputSize):
                        if input_ == new_input-1:
                            if op_tie_type in self.matrix_tie_status[input_][output]:
                                self.matrix_tie_status[input_][output] = 'Audio/Video'
                            elif self.matrix_tie_status[input_][output] == 'Audio/Video':
                                pass
                            else:
                                self.matrix_tie_status[input_][output] = tietype
                        else:
                            if 'Audio/Video' in self.matrix_tie_status[input_][output]:
                                self.matrix_tie_status[input_][output] = op_tie_type
                            elif op_tie_type not in self.matrix_tie_status[input_][output]:
                                self.matrix_tie_status[input_][output] = 'Untied'

                if tietype == 'Audio':
                    for output in range(self.OutputSize):
                        for i in range(self.NumOfAnalogAudio):
                            self.matrix_tie_status_analog[i][output] = 'Untied'
                    for output in range(self.OutputSize):
                        for i in range(8):
                            self.matrix_tie_status_dmp[i][output] = 'Untied'
                    for output in range(self.OutputSize):
                        for i in range(32):
                            self.matrix_tie_status_dante[i][output] = 'Untied'
                    for output in range(8):
                        self.WriteStatus('OutputTieStatus', str(new_input), {'Output': 'DMP Exp Output ' + str(output + 1), 'Tie Type': 'Audio'}) 
                    for output in range(32):
                        self.WriteStatus('OutputTieStatus', str(new_input), {'Output': 'Dante Output ' + str(output + 1), 'Tie Type': 'Audio'}) 
                    for output in range(self.NumOfAnalogAudio):
                        self.WriteStatus('OutputTieStatus', str(new_input), {'Output': 'Analog Audio Output ' + str(output + 1), 'Tie Type': 'Audio'}) 

            elif tietype == 'Audio/Video':
                for output in range(self.OutputSize):
                    for input_ in range(self.InputSize):
                        if input_ == new_input-1:
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(self.NumOfAnalogAudio):
                        self.matrix_tie_status_analog[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(8):
                        self.matrix_tie_status_dmp[i][output] = 'Untied'
                for output in range(self.OutputSize):
                    for i in range(32):
                        self.matrix_tie_status_dante[i][output] = 'Untied'
                for output in range(8):
                    self.WriteStatus('OutputTieStatus', str(new_input), {'Output': 'DMP Exp Output ' + str(output + 1), 'Tie Type': 'Audio'}) 
                for output in range(32):
                    self.WriteStatus('OutputTieStatus', str(new_input), {'Output': 'Dante Output ' + str(output + 1), 'Tie Type': 'Audio'}) 
                for output in range(self.NumOfAnalogAudio):
                    self.WriteStatus('OutputTieStatus', str(new_input), {'Output': 'Analog Audio Output ' + str(output + 1), 'Tie Type': 'Audio'})

            self.OutputTieStatusHelper('All')

    def UpdatePartNumber(self, value, qualifier):

        PartNumberCmdString = 'n'
        self.__UpdateHelper('PartNumber', PartNumberCmdString, value, qualifier)

    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def UpdatePowerSupplyStatus(self, value, qualifier):

        PowerSupplyStates = [
            'Primary',
            'Redundant'
        ]
        power_supply = qualifier['Power Supply']

        if power_supply in PowerSupplyStates:
            self.UpdateTemperature(None, {'Scale': 'Celsius'})
        else:
            self.Discard('Invalid Command for UpdatePowerSupplyStatus')

    def UpdatePowerSupplyVoltage(self, value, qualifier):

        PowerSupplyStates = [
            'Primary',
            'Redundant'
        ]
        power_supply = qualifier['Power Supply']

        if power_supply in PowerSupplyStates:
            self.UpdateTemperature(None, {'Scale': 'Celsius'})
        else:
            self.Discard('Invalid Command for UpdatePowerSupplyVoltage')

    def SetPresetNameCommand(self, value, qualifier):

        name = value
        if 1 <= int(qualifier['Preset']) <= 16 and name:
            PresetNameCommandCmdString = 'w{},{}NG\r'.format(qualifier['Preset'], name)
            self.__SetHelper('PresetNameCommand', PresetNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetNameCommand')

    def UpdatePresetNameStatus(self, value, qualifier):

        if 1 <= int(qualifier['Preset']) <= 16:
            PresetNameStatusCmdString = 'w{}NG\r'.format(qualifier['Preset'])
            self.__UpdateHelper('PresetNameStatus', PresetNameStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresetNameStatus')

    def __MatchPresetNameStatus(self, match, tag):

        qualifier = {'Preset': match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('PresetNameStatus', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = '{}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = '{},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        self.Debug = True
        self.UpdateAllMatrixTie(None, None)

    def SetRoomPresetRecall(self, value, qualifier):

        if 1 <= int(qualifier['Room']) <= 80 and 1 <= int(value) <= 10:
            RoomPresetRecallCmdString = '{}*{}.'.format(qualifier['Room'], value)
            self.__SetHelper('RoomPresetRecall', RoomPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomPresetRecall')

    def SetRoomPresetSave(self, value, qualifier):

        if 1 <= int(qualifier['Room']) <= 80 and 1 <= int(value) <= 10:
            RoomPresetSaveCmdString = '{}*{},'.format(qualifier['Room'], value)
            self.__SetHelper('RoomPresetSave', RoomPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomPresetSave')

    def UpdateTemperature(self, value, qualifier):

        ScaleStates = [
            'Celsius',
            'Fahrenheit'
        ]
        scale = qualifier['Scale']

        if scale in ScaleStates:
            TemperatureCmdString = 'S'
            self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperature')

    def __MatchTemperature(self, match, tag):

        self.WriteStatus('PowerSupplyVoltage', float(match.group(1).decode()), {'Power Supply': 'Primary'})
        self.WriteStatus('PowerSupplyVoltage', float(match.group(2).decode()), {'Power Supply': 'Redundant'})

        self.WriteStatus('Temperature', float(match.group(3).decode()), {'Scale': 'Fahrenheit'})
        self.WriteStatus('Temperature', float(match.group(4).decode()), {'Scale': 'Celsius'})

        for fan, rpm in enumerate(match.group(5).decode().split(), 1):
            self.WriteStatus('FanSpeed', int(rpm[:-3]), {'Fan': str(fan)}) # -3 to remove the trailing RPM, example: 2075RPM
            if fan >= self.NumOfFans:
                break

        PowerSupplyStatus_ValueStateValues = {
            '0': 'Inactive/Not Installed',
            '1': 'Active/Installed',
            '2': 'Failed/Installed'
        }
        self.WriteStatus('PowerSupplyStatus', PowerSupplyStatus_ValueStateValues[match.group(6).decode()], {'Power Supply': 'Primary'})
        self.WriteStatus('PowerSupplyStatus', PowerSupplyStatus_ValueStateValues[match.group(7).decode()], {'Power Supply': 'Redundant'})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Output']) <= self.OutputSize and value in ValueStateValues:
            VideoMuteCmdString = '{0}*{1}B'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            VideoMuteCmdString = 'wVM\r'
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'

        }

        if tag == 'Query':
            vidaudmute = match.group(1).decode().split(' ')
            for output, value in enumerate(vidaudmute[0]):
                if value == '0':
                    self.WriteStatus('VideoMute', 'Off', {'Output': str(output+1)})
                    self.WriteStatus('AudioMute', 'Off', {'Output': str(output+1)})
                elif value == '1':
                    self.WriteStatus('VideoMute', 'On', {'Output': str(output+1)})
                    self.WriteStatus('AudioMute', 'Off', {'Output': str(output+1)})
                elif value == '2':
                    self.WriteStatus('VideoMute', 'Off', {'Output': str(output+1)})
                    self.WriteStatus('AudioMute', 'On', {'Output': str(output+1)})
                elif value == '3':
                    self.WriteStatus('VideoMute', 'On', {'Output': str(output+1)})
                    self.WriteStatus('AudioMute', 'On', {'Output': str(output+1)})

        elif tag == 'VideoUnsolicited':
            self.WriteStatus('VideoMute', ValueStateValues[match.group(2).decode()], {'Output': str(int(match.group(1).decode()))})
        elif tag == 'AudioUnsolicited':
            self.WriteStatus('AudioMute', ValueStateValues[match.group(2).decode()], {'Output': str(int(match.group(1).decode()))})
        elif tag == 'VideoGlobal':
            for output in range(self.OutputSize):
                self.WriteStatus('VideoMute', ValueStateValues[match.group(1).decode()], {'Output': str(output+1)})
        elif tag == 'AudioGlobal':
            for output in range(self.OutputSize):
                self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output': str(output+1)})

    def SetVolume(self, value, qualifier):

        output = int(qualifier['Output'].replace('Analog Audio Output ', ''))
        if 1 <= output <= self.NumOfAnalogAudio and 0 <= value <= 100:
            VolumeCmdString = '{0}*{1}V'.format(50000+output, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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
        else:
            if self.EchoDisabled and 'Serial' not in self.ConnectionType:
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
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number',
            '13': 'Invalid parameter',
            '14': 'Invalid command for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System or command timed out',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privileges violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E'+ match.group(1).decode()])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True

    def extr_15_4803_24x(self):

        self.InputSize = 24
        self.OutputSize = 24
        self.NumOfAnalogAudio = 2
        self.NumOfFans = 3

        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs

    def extr_15_4803_40x(self):

        self.InputSize = 40
        self.OutputSize = 40
        self.NumOfAnalogAudio = 4
        self.NumOfFans = 4

        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs

    def extr_15_4803_80x(self):

        self.InputSize = 80
        self.OutputSize = 80
        self.NumOfAnalogAudio = 4
        self.NumOfFans = 3
        
        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs

    def extr_15_4803_160x(self):

        self.InputSize = 160
        self.OutputSize = 160
        self.NumOfAnalogAudio = 4
        self.NumOfFans = 6

        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs

    def extr_15_4803_320x(self):

        self.InputSize = 320
        self.OutputSize = 320
        self.NumOfAnalogAudio = 4
        self.NumOfFans = 9

        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs
        
    def extr_15_4803_560x(self):

        self.InputSize = 560
        self.OutputSize = 560
        self.NumOfAnalogAudio = 4
        self.NumOfFans = 15

        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs
        
    def extr_15_4803_840x(self):

        self.InputSize = 840
        self.OutputSize = 840
        self.NumOfAnalogAudio = 4
        self.NumOfFans = 24

        self.refresh_matrix_strings = []

        output = 1
        while output <= self.OutputSize:
            self.refresh_matrix_strings.append('w0*{}*1VC\r'.format(output)) # A/V
            self.refresh_matrix_strings.append('w0*{}*2VC\r'.format(output))
            output += 16
        self.refresh_matrix_strings.append('w0*1*6VC\r') # DMP outputs
        self.refresh_matrix_strings.append('w0*1*7VC\r') # Dante outputs
        self.refresh_matrix_strings.append('w0*1*8VC\r') # Analog outputs

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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