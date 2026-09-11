from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.deviceUsername = 'netmax'
        self.devicePassword = 'netmax'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DigitalInputGain': {'Parameters':['Slot','Input'], 'Status': {}},
            'DigitalInputMute': {'Parameters':['Slot','Input'], 'Status': {}},
            'DigitalOutputGain': {'Parameters':['Slot','Output'], 'Status': {}},
            'DigitalOutputMute': {'Parameters':['Slot','Output'], 'Status': {}},
            'Echo': { 'Status': {}},
            'GPO': {'Parameters':['Input'], 'Status': {}},
            'InputGain': {'Parameters':['Slot','Input'], 'Status': {}},
            'InputMute': {'Parameters':['Slot','Input'], 'Status': {}},
            'MatrixMixerConnectCrosspoint': {'Parameters':['Matrix','Crosspoint'], 'Status': {}},
            'MatrixMixerGainCrosspoint': {'Parameters':['Matrix','Crosspoint'], 'Status': {}},
            'MatrixMixerGainIn': {'Parameters':['Matrix','Input'], 'Status': {}},
            'MatrixMixerGainOut': {'Parameters':['Matrix','Output'], 'Status': {}},
            'MatrixMixerMuteIn': {'Parameters':['Matrix','Input'], 'Status': {}},
            'MatrixMixerMuteOut': {'Parameters':['Matrix','Output'], 'Status': {}},
            'MatrixRouterGainIn': {'Parameters':['Matrix','Input'], 'Status': {}},
            'MatrixRouterGainOut': {'Parameters':['Matrix','Output'], 'Status': {}},
            'MatrixRouterMuteIn': {'Parameters':['Matrix','Input'], 'Status': {}},
            'MatrixRouterMuteOut': {'Parameters':['Matrix','Output'], 'Status': {}},
            'MicGain': {'Parameters':['Slot','Mic'], 'Status': {}},
            'MicMute': {'Parameters':['Slot','Mic'], 'Status': {}},
            'MixerGainIn': {'Parameters':['Mixer','Input'], 'Status': {}},
            'MixerGainOut': {'Parameters':['Mixer','Output'], 'Status': {}},
            'MixerMuteIn': {'Parameters':['Mixer','Input'], 'Status': {}},
            'MixerMuteOut': {'Parameters':['Mixer','Output'], 'Status': {}},
            'OutputGain': {'Parameters':['Slot','Output'], 'Status': {}},
            'OutputMute': {'Parameters':['Slot','Output'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': {'Parameters':['Compression','Mute'], 'Status': {}},
            }

        self.lastDigitalInputGain = {'1': 0, '2':0, '3':0, '4':0}
        self.lastDigitalInputMute = {'1': 0, '2':0, '3':0, '4':0}
        self.lastDigitalOutputGain = {'1': 0, '2':0, '3':0, '4':0}
        self.lastDigitalOutputMute = {'1': 0, '2':0, '3':0, '4':0}
        self.lastInputGain = {'1': 0, '2':0, '3':0, '4':0}
        self.lastInputMute = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixMixerConnectCrosspoint = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixMixerGainCrosspoint = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixMixerGainIn = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixMixerGainOut = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixMixerMuteIn = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixMixerMuteOut = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixRouterGainIn = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixRouterGainOut = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixRouterMuteIn = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMatrixRouterMuteOut = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMicMute = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMicGain = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMixerGainIn = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMixerGainOut = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMixerMuteIn = {'1': 0, '2':0, '3':0, '4':0}
        self.lastMixerMuteOut = {'1': 0, '2':0, '3':0, '4':0}
        self.lastOutputMute = {'1': 0, '2':0, '3':0, '4':0}
        self.lastOutputGain = {'1': 0, '2':0, '3':0, '4':0}
        self.lastGPO = 0
        self.echo = 'On'
        self.Authenticated = 'Not Authenticated' if 'Serial' not in self.ConnectionType else 'Not Needed'
        if self.Unidirectional == 'False':
            self.MatchDigitalInputGain = re.compile('/PARAM/DSP/DIGITALIN_([1-8])/GAIN/ALL([\-., 0-9]+)\r')
            self.MatchDigitalInputMute = re.compile('/PARAM/DSP/DIGITALIN_([1-8])/MUTE/ALL([ ,01]+)\r')
            self.MatchDigitalOutputGain = re.compile('/PARAM/DSP/DIGITALOUT_([1-8])/GAIN/ALL([\-., 0-9]+)\r')
            self.MatchDigitalOutputMute = re.compile('/PARAM/DSP/DIGITALOUT_([1-8])/MUTE/ALL([ ,01]+)\r')
            self.MatchEcho = re.compile('/COMM/ECHO (ON|OFF)\r')
            self.MatchGPO = re.compile('/PARAM/LOCAL/GPO/ALL([ ,01]+)\r')
            self.MatchInputGain = re.compile('/PARAM/DSP/ANALOGIN_([1-8])/GAIN/ALL([\-., 0-9]+)\r')
            self.MatchInputMute = re.compile('/PARAM/DSP/ANALOGIN_([1-8])/MUTE/ALL([ ,01]+)\r')
            self.MatchMatrixMixerConnectCrosspoint = re.compile('/PARAM/DSP/MATRIX_([1-4])/CONNECTCROSSPOINT/ALL([ ,01]+)\r')
            self.MatchMatrixMixerGainCrosspoint = re.compile('/PARAM/DSP/MATRIX_([1-4])/GAINCROSSPOINT/ALL([\-, 0-9]+)\r')
            self.MatchMatrixMixerGainIn = re.compile('/PARAM/DSP/MATRIX_([1-4])/GAININ/ALL([\-., 0-9]+)\r')
            self.MatchMatrixMixerGainOut = re.compile('/PARAM/DSP/MATRIX_([1-4])/GAINOUT/ALL([\-, 0-9]+)\r')
            self.MatchMatrixMixerMuteIn = re.compile('/PARAM/DSP/MATRIX_([1-4])/MUTEIN/ALL([ ,01]+)\r')
            self.MatchMatrixMixerMuteOut = re.compile('/PARAM/DSP/MATRIX_([1-4])/MUTEOUT/ALL([ ,01]+)\r')
            self.MatchMatrixRouterGainIn = re.compile('/PARAM/DSP/MATRIXROUTER_([1-4])/GAININ/ALL([\-., 0-9]+)\r')
            self.MatchMatrixRouterGainOut = re.compile('/PARAM/DSP/MATRIXROUTER_([1-4])/GAINOUT/ALL([\-, 0-9]+)\r')
            self.MatchMatrixRouterMuteIn = re.compile('/PARAM/DSP/MATRIXROUTER_([1-4])/MUTEIN/ALL([ ,01]+)\r')
            self.MatchMatrixRouterMuteOut = re.compile('/PARAM/DSP/MATRIXROUTER_([1-4])/MUTEOUT/ALL([ ,01]+)\r')
            self.MatchMicGain = re.compile('/PARAM/DSP/ANALOGMICIN_([1-8])/GAIN/ALL([\-., 0-9]+)\r')
            self.MatchMicMute = re.compile('/PARAM/DSP/ANALOGMICIN_([1-8])/MUTE/ALL([ ,01]+)\r')
            self.MatchMixerGainIn = re.compile('/PARAM/DSP/MIXER_([1-4])/GAININ/ALL([\-, 0-9]+)\r')
            self.MatchMixerGainOut = re.compile('/PARAM/DSP/MIXER_([1-4])/GAINOUT/ALL([\-., 0-9]+)\r')
            self.MatchMixerMuteIn = re.compile('/PARAM/DSP/MIXER_([1-4])/MUTEIN/ALL([ ,01]+)\r')
            self.MatchMixerMuteOut = re.compile('/PARAM/DSP/MIXER_([1-4])/MUTEOUT/ALL([ ,01]+)\r')
            self.MatchOutputGain = re.compile('/PARAM/DSP/ANALOGOUT_([1-8])/GAIN/ALL([\-., 0-9]+)\r')
            self.MatchOutputMute = re.compile('/PARAM/DSP/ANALOGOUT_([1-8])/MUTE/ALL([ ,01]+)\r')
            self.MatchError = re.compile('error|not found|\?')

            self.AddMatchString(re.compile(b'/COMM ECHO OFF\r|/COMM/ECHO>'), self.__MatchEchoSet, None)
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27'), self.__MatchFirstHandshake, None)
                self.AddMatchString(re.compile(b'\xFF\xFB\x03\xFF\xFD\x01\xFF\xFD\x1F\xFF\xFB\x05\xFF\xFD\x21'), self.__MatchSecondHandshake, None)
                self.AddMatchString(re.compile(b'login:'), self.__MatchUsername, None)
                self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Built-in shell \(msh\)'), self.__MatchAuthSuccess, None)
                self.AddMatchString(re.compile(b'N8000 command mode entered'), self.__MatchWelcome, None)

    def __MatchFirstHandshake(self, match, tag):
        self.SetFirstHandshake( None, None)

    def SetFirstHandshake(self, value, qualifier):
        self.Send(b'\xFF\xFC\x18\xFF\xFC\x20\xFF\xFC\x23\xFF\xFC\x27')

    def __MatchSecondHandshake(self, match, tag):
        self.SetSecondHandshake( None, None)

    def SetSecondHandshake(self, value, qualifier):
        self.Send(b'\xFF\xFE\x03\xFF\xFC\x01\xFF\xFC\x1F\xFF\xFE\x05\xFF\xFC\x21')

    def __MatchUsername(self, match, tag):
        self.SetUsername( None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        self.SetPassword( None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchAuthSuccess(self, match, tag):
        self.SetParser( None, None)

    def SetParser(self, value, qualifier):
        self.Send('parser -f\r')

    def __MatchWelcome(self, match, tag):
        self.Authenticated = 'Authenticated'
        self.SetEcho( None, None)

    def SetEcho(self, value, qualifier):
        self.Send('/COMM ECHO OFF\r')

    def __MatchEchoSet(self, match, tag):
        self.echo = 'Off'

    def SetDigitalInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18  # device software doesn't allow over 18
            }

        slot = qualifier['Slot']
        input_ = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and input_ in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            DigitalInputGainCmdString = '/PARAM DSP DIGITALIN_{0} GAIN IDX{1} {2}\r'.format(slot, input_, value)
            self.__SetHelper('DigitalInputGain', DigitalInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalInputGain')

    def UpdateDigitalInputGain(self, value, qualifier):

        slot = qualifier['Slot']
        DigitalInputGainCmdString = '/PARAM DSP DIGITALIN_{0} GAIN ALL ?\r'.format(slot)
        res = self.__UpdateHelper('DigitalInputGain', DigitalInputGainCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchDigitalInputGain, res)
                slot = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('DigitalInputGain', float(value), {'Slot':slot, 'Input':str(input_)})
                    input_ += 1
            except (ValueError, IndexError, AttributeError):
                    self.Error(['Digital Input Gain: Invalid/unexpected response'])

    def SetDigitalInputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }
        slot = qualifier['Slot']
        input_ = qualifier['Input']
        if input_ in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            DigitalInputMuteCmdString = '/PARAM DSP DIGITALIN_{0} MUTE IDX{1} {2}\r'.format(slot, input_, ValueStateValues[value])
            self.__SetHelper('DigitalInputMute', DigitalInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalInputMute')

    def UpdateDigitalInputMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        slot = qualifier['Slot']
       
        DigitalInputMuteCmdString = '/PARAM DSP DIGITALIN_{0} MUTE ALL ?\r'.format(slot)
        res = self.__UpdateHelper('DigitalInputMute', DigitalInputMuteCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchDigitalInputMute, res)
                slot = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('DigitalInputMute', ValueStateValues[value], {'Slot':slot, 'Input':str(input_)})
                    input_ += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Digital Input Mute: Invalid/unexpected response'])

    def SetDigitalOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18
            }

        slot = qualifier['Slot']
        Output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Output in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            DigitalOutputGainCmdString = '/PARAM DSP DIGITALOUT_{0} GAIN IDX{1} {2}\r'.format(slot, Output, value)
            self.__SetHelper('DigitalOutputGain', DigitalOutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalOutputGain')

    def UpdateDigitalOutputGain(self, value, qualifier):

        slot = qualifier['Slot']
        DigitalOutputGainCmdString = '/PARAM DSP DIGITALOUT_{0} GAIN ALL ?\r'.format(slot)
        res = self.__UpdateHelper('DigitalOutputGain', DigitalOutputGainCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchDigitalOutputGain, res)
                slot = allValues.group(1)
                Output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('DigitalOutputGain', float(value), {'Slot':slot, 'Output':str(Output)})
                    Output += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Digital Output Gain: Invalid/unexpected response'])

    def SetDigitalOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }
        slot = qualifier['Slot']
        Output = qualifier['Output']
        if Output in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            DigitalOutputMuteCmdString = '/PARAM DSP DIGITALOUT_{0} MUTE IDX{1} {2}\r'.format(slot, Output, ValueStateValues[value])
            self.__SetHelper('DigitalOutputMute', DigitalOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalOutputMute')

    def UpdateDigitalOutputMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        slot = qualifier['Slot']
        DigitalOutputMuteCmdString = '/PARAM DSP DIGITALOUT_{0} MUTE ALL ?\r'.format(slot)
        res = self.__UpdateHelper('DigitalOutputMute', DigitalOutputMuteCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchDigitalOutputMute, res)
                slot = allValues.group(1)
                Output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('DigitalOutputMute', ValueStateValues[value], {'Slot':slot, 'Output':str(Output)})
                    Output += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Digital Output Mute: Invalid/unexpected response'])

    def UpdateEcho(self, value, qualifier):

        ValueStateValues = {
            'ON'  : 'On',
            'OFF' : 'Off'
        }

        EchoCmdString = '/COMM ECHO ?\r'
        res = self.__UpdateHelper('Echo', EchoCmdString, value, qualifier)
        if res:
            try:
                value = re.search(self.MatchEcho, res)
                value = ValueStateValues[value.group(1)]
                if value == 'On':
                    self.SetEcho( None, None)
                self.WriteStatus('Echo', value, None)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Echo: Invalid/unexpected response'])

    def SetGPO(self, value, qualifier):

        ValueConstraints = {
            'Open' : '0',
            'Closed' : '1',
            }

        input_ = qualifier['Input']
        if input_ in ['1', '2', '3']:
            GPOCmdString = '/PARAM LOCAL GPO IDX{0} {1}\r'.format(input_, ValueConstraints[value])
            self.__SetHelper('GPO', GPOCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGPO')

    def UpdateGPO(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Closed',
            '0' : 'Open'
        }

        GPOCmdString = '/PARAM LOCAL GPO ALL ?\r'
        res = self.__UpdateHelper('GPO', GPOCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchGPO, res)
                input_ = 1
                for value in allValues.group(1).replace(' ', '').split(','):
                    self.WriteStatus('GPO', ValueStateValues[value], {'Input': str(input_)})
                    input_ += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['GPO: Invalid/unexpected response'])

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18  # device software doesn't allow over 18
            }
        slot = qualifier['Slot']
        input_ = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and input_ in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            InputGainCmdString = '/PARAM DSP ANALOGIN_{0} GAIN IDX{1} {2}\r'.format(slot, input_, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        slot = qualifier['Slot']
        InputGainCmdString = '/PARAM DSP ANALOGIN_{0} GAIN ALL ?\r'.format(slot)
        res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchInputGain, res)
                slot = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('InputGain', float(value), {'Slot':slot, 'Input':str(input_)})
                    input_ += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Input Gain: Invalid/unexpected response'])

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        slot = qualifier['Slot']
        input_ = qualifier['Input']
        if input_ in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            InputMuteCmdString = '/PARAM DSP ANALOGIN_{0} MUTE IDX{1} {2}\r'.format(slot, input_, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        slot = qualifier['Slot']
        InputMuteCmdString = '/PARAM DSP ANALOGIN_{0} MUTE ALL ?\r'.format(slot)
        res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchInputMute, res)
                slot = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('InputMute', ValueStateValues[value], {'Slot':slot, 'Input':str(input_)})
                    input_ += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input Mute: Invalid/unexpected response'])

    def SetMatrixMixerConnectCrosspoint(self, value, qualifier):

        ValueStateValues = {
            'Connected' : '1', 
            'Not Connected' : '0'
        }
        matrix = qualifier['Matrix']
        crosspoint = qualifier['Crosspoint']
        if 1 <= crosspoint <= 1024 and 1 <= crosspoint <= 1024 and matrix in ['1', '2', '3', '4']:
            MatrixMixerConnectCrosspointCmdString = '/PARAM DSP MATRIX_{0} CONNECTCROSSPOINT IDX{1} {2}\r'.format(matrix, crosspoint, ValueStateValues[value])
            self.__SetHelper('MatrixMixerConnectCrosspoint', MatrixMixerConnectCrosspointCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerConnectCrosspoint')

    def UpdateMatrixMixerConnectCrosspoint(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Connected',
            '0' : 'Not Connected'
        }

        matrix = qualifier['Matrix']
        MatrixMixerConnectCrosspointCmdString = '/PARAM DSP MATRIX_{0} CONNECTCROSSPOINT ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixMixerConnectCrosspoint', MatrixMixerConnectCrosspointCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixMixerConnectCrosspoint, res)
                matrix = allValues.group(1)
                crosspoint = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixMixerConnectCrosspoint', ValueStateValues[value], {'Matrix':matrix, 'Crosspoint':crosspoint})
                    crosspoint += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Matrix Mixer Connect Crosspoint: Invalid/unexpected response'])

    def SetMatrixMixerGainCrosspoint(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 0
            }

        matrix = qualifier['Matrix']
        crosspoint = qualifier['Crosspoint']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= crosspoint <= 1024 and matrix in ['1', '2', '3', '4']:
            MatrixMixerGainCrosspointCmdString = '/PARAM DSP MATRIX_{0} GAINCROSSPOINT IDX{1} {2}\r'.format(matrix, crosspoint, value)
            self.__SetHelper('MatrixMixerGainCrosspoint', MatrixMixerGainCrosspointCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerGainCrosspoint')

    def UpdateMatrixMixerGainCrosspoint(self, value, qualifier):

        matrix = qualifier['Matrix']        
        MatrixMixerGainCrosspointCmdString = '/PARAM DSP MATRIX_{0} GAINCROSSPOINT ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixMixerGainCrosspoint', MatrixMixerGainCrosspointCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixMixerGainCrosspoint, res)
                matrix = allValues.group(1)
                crosspoint = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixMixerGainCrosspoint', int(value), {'Matrix':matrix, 'Crosspoint':crosspoint})
                    crosspoint += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Matrix Mixer Gain Crosspoint: Invalid/unexpected response'])

    def SetMatrixMixerGainIn(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 0
            }

        matrix = qualifier['Matrix']
        input_ = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(input_) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixMixerGainInCmdString = '/PARAM DSP MATRIX_{0} GAININ IDX{1} {2}\r'.format(matrix, input_, value)
            self.__SetHelper('MatrixMixerGainIn', MatrixMixerGainInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerGainIn')

    def UpdateMatrixMixerGainIn(self, value, qualifier):

        matrix = qualifier['Matrix']
        MatrixMixerGainInCmdString = '/PARAM DSP MATRIX_{0} GAININ ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixMixerGainIn', MatrixMixerGainInCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixMixerGainIn, res)
                matrix = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixMixerGainIn', float(value), {'Matrix': matrix, 'Input': str(input_)})
                    input_ += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Matrix Mixer Gain In: Invalid/unexpected response'])

    def SetMatrixMixerGainOut(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 0
            }

        matrix = qualifier['Matrix']
        output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(output) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixMixerGainOutCmdString = '/PARAM DSP MATRIX_{0} GAINOUT IDX{1} {2}\r'.format(matrix, output, value)
            self.__SetHelper('MatrixMixerGainOut', MatrixMixerGainOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerGainOut')

    def UpdateMatrixMixerGainOut(self, value, qualifier):

        matrix = qualifier['Matrix']
        MatrixMixerGainOutCmdString = '/PARAM DSP MATRIX_{0} GAINOUT ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixMixerGainOut', MatrixMixerGainOutCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixMixerGainOut, res)
                matrix = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixMixerGainOut', int(value), {'Matrix': matrix, 'Output': str(output)})
                    output += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Matrix Mixer Gain Out: Invalid/unexpected response'])

    def SetMatrixMixerMuteIn(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        matrix = qualifier['Matrix']
        input_ = qualifier['Input']
        if 1 <= int(input_) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixMixerMuteInCmdString = '/PARAM DSP MATRIX_{0} MUTEIN IDX{1} {2}\r'.format(matrix, input_, ValueStateValues[value])
            self.__SetHelper('MatrixMixerMuteIn', MatrixMixerMuteInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerMuteIn')

    def UpdateMatrixMixerMuteIn(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }
        matrix = qualifier['Matrix']
        MatrixMixerMuteInCmdString = '/PARAM DSP MATRIX_{0} MUTEIN ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixMixerMuteIn', MatrixMixerMuteInCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixMixerMuteIn, res)
                matrix = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixMixerMuteIn', ValueStateValues[value], {'Matrix': matrix, 'Input': str(input_)})
                    input_ += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Matrix Mixer Mute In: Invalid/unexpected response'])

    def SetMatrixMixerMuteOut(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        matrix = qualifier['Matrix']
        output = qualifier['Output']
        if 1 <= int(output) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixMixerMuteOutCmdString = '/PARAM DSP MATRIX_{0} MUTEOUT IDX{1} {2}\r'.format(matrix, output, ValueStateValues[value])
            self.__SetHelper('MatrixMixerMuteOut', MatrixMixerMuteOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerMuteOut')

    def UpdateMatrixMixerMuteOut(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }
        matrix = qualifier['Matrix']
        MatrixMixerMuteOutCmdString = '/PARAM DSP MATRIX_{0} MUTEOUT ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixMixerMuteOut', MatrixMixerMuteOutCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixMixerMuteOut, res)
                matrix = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixMixerMuteOut', ValueStateValues[value], {'Matrix': matrix, 'Output': str(output)})
                    output += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Matrix Mixer Mute Out: Invalid/unexpected response'])

    def SetMatrixRouterGainIn(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 0
            }

        matrix = qualifier['Matrix']
        input_ = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(input_) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixRouterGainInCmdString = '/PARAM DSP MATRIXROUTER_{0} GAININ IDX{1} {2}\r'.format(matrix, input_, value)
            self.__SetHelper('MatrixRouterGainIn', MatrixRouterGainInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixRouterGainIn')

    def UpdateMatrixRouterGainIn(self, value, qualifier):
    
        matrix = qualifier['Matrix']
        MatrixRouterGainInCmdString = '/PARAM DSP MATRIXROUTER_{0} GAININ ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixRouterGainIn', MatrixRouterGainInCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixRouterGainIn, res)
                matrix = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixRouterGainIn', float(value), {'Matrix': matrix, 'Input': str(input_)})
                    input_ += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Matrix Router Gain In: Invalid/unexpected response'])

    def SetMatrixRouterGainOut(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 0
            }

        matrix = qualifier['Matrix']
        output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(output) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixRouterGainOutCmdString = '/PARAM DSP MATRIXROUTER_{0} GAINOUT IDX{1} {2}\r'.format(matrix, output, value)
            self.__SetHelper('MatrixRouterGainOut', MatrixRouterGainOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixRouterGainOut')

    def UpdateMatrixRouterGainOut(self, value, qualifier):
    
        matrix = qualifier['Matrix']
        MatrixRouterGainOutCmdString = '/PARAM DSP MATRIXROUTER_{0} GAINOUT ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixRouterGainOut', MatrixRouterGainOutCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixRouterGainOut, res)
                matrix = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixRouterGainOut', int(value), {'Matrix': matrix, 'Output': str(output)})
                    output += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Matrix Router Gain Out: Invalid/unexpected response'])

    def SetMatrixRouterMuteIn(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        matrix = qualifier['Matrix']
        input_ = qualifier['Input']
        if 1 <= int(input_) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixRouterMuteInCmdString = '/PARAM DSP MATRIXROUTER_{0} MUTEIN IDX{1} {2}\r'.format(matrix, input_, ValueStateValues[value])
            self.__SetHelper('MatrixRouterMuteIn', MatrixRouterMuteInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixRouterMuteIn')

    def UpdateMatrixRouterMuteIn(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }
        matrix = qualifier['Matrix']
        MatrixRouterMuteInCmdString = '/PARAM DSP MATRIXROUTER_{0} MUTEIN ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixRouterMuteIn', MatrixRouterMuteInCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixRouterMuteIn, res)
                matrix = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixRouterMuteIn', ValueStateValues[value], {'Matrix': matrix, 'Input': str(input_)})
                    input_ += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Matrix Router Mute In: Invalid/unexpected response'])

    def SetMatrixRouterMuteOut(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        matrix = qualifier['Matrix']
        output = qualifier['Output']
        if 1 <= int(output) <= 32 and matrix in ['1', '2', '3', '4']:
            MatrixRouterMuteOutCmdString = '/PARAM DSP MATRIXROUTER_{0} MUTEOUT IDX{1} {2}\r'.format(matrix, output, ValueStateValues[value])
            self.__SetHelper('MatrixRouterMuteOut', MatrixRouterMuteOutCmdString, value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def UpdateMatrixRouterMuteOut(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        matrix = qualifier['Matrix']        
        MatrixRouterMuteOutCmdString = '/PARAM DSP MATRIXROUTER_{0} MUTEOUT ALL ?\r'.format(matrix)
        res = self.__UpdateHelper('MatrixRouterMuteOut', MatrixRouterMuteOutCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMatrixRouterMuteOut, res)
                matrix = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MatrixRouterMuteOut', ValueStateValues[value], {'Matrix': matrix, 'Output': str(output)})
                    output += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Matrix Router Mute Out: Invalid/unexpected response'])

    def SetMicGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18
            }

        slot = qualifier['Slot']
        mic = qualifier['Mic']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and mic in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            MicGainCmdString = '/PARAM DSP ANALOGMICIN_{0} GAIN IDX{1} {2}\r'.format(slot, mic, value)
            self.__SetHelper('MicGain', MicGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        slot = qualifier['Slot']
        MicGainCmdString = '/PARAM DSP ANALOGMICIN_{0} GAIN ALL ?\r'.format(slot)
        res = self.__UpdateHelper('MicGain', MicGainCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMicGain, res)
                slot = allValues.group(1)
                mic = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MicGain', float(value), {'Slot': slot, 'Mic': str(mic)})
                    mic += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Mic Gain: Invalid/unexpected response'])

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        slot = qualifier['Slot']
        mic = qualifier['Mic']
        if mic in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            MicMuteCmdString = '/PARAM DSP ANALOGMICIN_{0} MUTE IDX{1} {2}\r'.format(slot, mic, ValueStateValues[value])
            self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        slot = qualifier['Slot']
        MicMuteCmdString = '/PARAM DSP ANALOGMICIN_{0} MUTE ALL ?\r'.format(slot)
        res = self.__UpdateHelper('MicMute', MicMuteCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMicMute, res)
                slot = allValues.group(1)
                mic = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MicMute', ValueStateValues[value], {'Slot': slot, 'Mic': str(mic)})
                    mic += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Mic Mute: Invalid/unexpected response'])

    def SetMixerGainIn(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }

        mixer = qualifier['Mixer']
        input_ = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(input_) <= 32 and mixer in ['1', '2','3', '4']:
            MixerGainInCmdString = '/PARAM DSP MIXER_{0} GAININ IDX{1} {2}\r'.format(mixer, input_, value)
            self.__SetHelper('MixerGainIn', MixerGainInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerGainIn')

    def UpdateMixerGainIn(self, value, qualifier):

        mixer = qualifier['Mixer']
        MixerGainInCmdString = '/PARAM DSP MIXER_{0} GAININ ALL ?\r'.format(mixer)
        res = self.__UpdateHelper('MixerGainIn', MixerGainInCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMixerGainIn, res)
                mixer = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MixerGainIn', int(value), {'Mixer': mixer, 'Input': str(input_)})
                    input_ += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Mixer Gain In: Invalid/unexpected response'])

    def SetMixerGainOut(self, value, qualifier):

        OutputStates = {
            'Left' : '1',
            'Right': '2'
        }

        ValueConstraints = {
            'Min': -80,
            'Max': 18
        }

        mixer = qualifier['Mixer']
        output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and mixer in ['1', '2', '3', '4']:
            MixerGainOutCmdString = '/PARAM DSP MIXER_{0} GAINOUT IDX{1} {2}\r'.format(mixer, OutputStates[output], value)
            self.__SetHelper('MixerGainOut', MixerGainOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerGainOut')

    def UpdateMixerGainOut(self, value, qualifier):

        OutputStates = {
            '1' : 'Left',
            '2' : 'Right'
        }

        mixer = qualifier['Mixer']
        MixerGainOutCmdString = '/PARAM DSP MIXER_{0} GAINOUT ALL ?\r'.format(mixer)
        res = self.__UpdateHelper('MixerGainOut', MixerGainOutCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMixerGainOut, res)
                mixer = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MixerGainOut', float(value), {'Mixer': mixer, 'Output': OutputStates[str(output)]})
                    output += 1
            except (KeyError, ValueError, IndexError, AttributeError):
                self.Error(['Mixer Gain Out: Invalid/unexpected response'])

    def SetMixerMuteIn(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        mixer = qualifier['Mixer']
        input_ = qualifier['Input']
        if 1 <= int(input_) <= 32 and mixer in ['1', '2', '3', '4']:
            MixerMuteInCmdString = '/PARAM DSP MIXER_{0} MUTEIN IDX{1} {2}\r'.format(mixer, input_, ValueStateValues[value])
            self.__SetHelper('MixerMuteIn', MixerMuteInCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerMuteIn')

    def UpdateMixerMuteIn(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        mixer = qualifier['Mixer']
        MixerMuteInCmdString = '/PARAM DSP MIXER_{0} MUTEIN ALL ?\r'.format(mixer)
        res = self.__UpdateHelper('MixerMuteIn', MixerMuteInCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMixerMuteIn, res)
                mixer = allValues.group(1)
                input_ = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MixerMuteIn', ValueStateValues[value], {'Mixer': mixer, 'Input': str(input_)})
                    input_ += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Mixer Mute In: Invalid/unexpected response'])

    def SetMixerMuteOut(self, value, qualifier):

        OutputStates = {
            'Left' : '1',
            'Right': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        mixer = qualifier['Mixer']
        output = qualifier['Output']
        if mixer in ['1', '2', '3', '4']:
            MixerMuteOutCmdString = '/PARAM DSP MIXER_{0} MUTEOUT IDX{1} {2}\r'.format(mixer, OutputStates[output], ValueStateValues[value])
            self.__SetHelper('MixerMuteOut', MixerMuteOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerMuteOut')

    def UpdateMixerMuteOut(self, value, qualifier):

        OutputStates = {
            '1': 'Left',
            '2': 'Right'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        mixer = qualifier['Mixer']
        MixerMuteOutCmdString = '/PARAM DSP MIXER_{0} MUTEOUT ALL ?\r'.format(mixer)
        res = self.__UpdateHelper('MixerMuteOut', MixerMuteOutCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchMixerMuteOut, res)
                mixer = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('MixerMuteOut', ValueStateValues[value], {'Mixer': mixer, 'Output': OutputStates[str(output)]})
                    output += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Mixer Mute Out: Invalid/unexpected response'])

    def SetOutputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 18
            }

        slot = qualifier['Slot']
        output = qualifier['Output']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and output in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            OutputGainCmdString = '/PARAM DSP ANALOGOUT_{0} GAIN IDX{1} {2}\r'.format(slot, output, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        slot = qualifier['Slot']
        OutputGainCmdString = '/PARAM DSP ANALOGOUT_{0} GAIN ALL ?\r'.format(slot)
        res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchOutputGain, res)
                slot = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('OutputGain', float(value), {'Slot': slot, 'Output': str(output)})
                    output += 1
            except (ValueError, IndexError, AttributeError):
                self.Error(['Output Gain: Invalid/unexpected response'])

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }
        slot = qualifier['Slot']
        output = qualifier['Output']
        if output in ['1', '2', '3', '4', '5', '6', '7', '8'] and slot in ['1', '2', '3', '4']:
            OutputMuteCmdString = '/PARAM DSP ANALOGOUT_{0} MUTE IDX{1} {2}\r'.format(slot, output, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        slot = qualifier['Slot']
        OutputMuteCmdString = '/PARAM DSP ANALOGOUT_{0} MUTE ALL ?\r'.format(slot)
        res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        if res:
            try:
                allValues = re.search(self.MatchOutputMute, res)
                slot = allValues.group(1)
                output = 1
                for value in allValues.group(2).replace(' ', '').split(','):
                    self.WriteStatus('OutputMute', ValueStateValues[value], {'Slot': slot, 'Output': str(output)})
                    output += 1
            except (KeyError, IndexError, AttributeError):
                self.Error(['Output Mute: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 60:
            PresetRecallCmdString = '/PARAM DSP FUNCTIONS LOAD_PRESET {0}\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        CompressionStates = {
            'With Compression' : 'WITHCOMP',
            'No Compression'   : 'NOCOMP'
        }

        MuteStates = {
            'On'  : 'MUTE',
            'Off' : 'NOMUTE'
        }

        if 1 <= int(value) <= 60:
            PresetSaveCmdString = '/PARAM DSP FUNCTIONS SAVE_PRESET {0} {1} {2}\r'.format(value, CompressionStates[qualifier['Compression']], MuteStates[qualifier['Mute']])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetPresetSave')
            
    def __CheckResponseForErrors(self, sourceCmdName, response):

        error = re.search(self.MatchError, response)
        if error: # obtained via testing w/ device
            self.Error(['{0} command error occurred'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command , res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Authenticated', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.echo != 'Off':
                    self.Send('/COMM ECHO OFF\r')
                else:
                    if self.initializationChk:
                        self.OnConnected()
                        self.initializationChk = False

                    self.counter = self.counter + 1
                    if self.counter > self.connectionCounter and self.connectionFlag:
                        self.OnDisconnected()

                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                    if not res:
                        return ''
                    else:
                        return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Authenticated'
        self.echo = 'On'
        
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='SW', CharDelay=0, Mode='RS232', Model =None):
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

