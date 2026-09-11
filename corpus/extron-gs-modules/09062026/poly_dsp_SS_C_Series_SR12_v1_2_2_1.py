from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog
import copy


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'DigitalGPIOState': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'DoNotDisturb': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'DTMF': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'Fader': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'Firmware': {'Status': {}},
            'Hook': {'Parameters': ['Number','Virtual Channel'], 'Status': {}},
            'MatrixGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MicGain': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'Mute': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'OutputGain': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'PresetRecallCommand': {'Status': {}},
            'RingStatus': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'VoIPCallAppearanceState': {'Parameters': ['Call Appearance Index', 'Virtual Channel'], 'Status': {}},
            'VoIPCallerID': {'Parameters': ['Call Appearance Index', 'Virtual Channel'], 'Status': {}},
            'VoIPDialMode': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'VoIPLineSelect': {'Parameters': ['Virtual Channel'], 'Status': {}},
            'VoIPLineStatus': {'Parameters': ['Line Number', 'Virtual Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'val dev_firmware_ver 1 \"(.*)\"\r'), self.__MatchFirmware, None)
            self.AddMatchString(compile(b'error \".*\"\r'), self.__MatchError, None)

    def SetAutoAnswer(self, value, qualifier):

        AutoAnswerCommand = {
            'On': '1',
            'Off': '0',
        }

        phone_name = qualifier['Virtual Channel']

        if phone_name not in self.Commands['AutoAnswer']['Status']:
            self.AddMatchString(compile('val phone_auto_answer_en \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchAutoAnswer, qualifier)

        cmdString = 'set phone_auto_answer_en \"{0}\" {1}\r'.format(phone_name, AutoAnswerCommand[value])
        self.__SetHelper('AutoAnswer', cmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        phone_name = qualifier['Virtual Channel']
        if phone_name not in self.Commands['AutoAnswer']['Status']:
            self.AddMatchString(compile('val phone_auto_answer_en \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchAutoAnswer, qualifier)

        self.__UpdateHelper('AutoAnswer', 'get phone_auto_answer_en \"{0}\"\r'.format(phone_name), qualifier)

    def __MatchAutoAnswer(self, match, qualifier):

        AutoAnswerValue = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('AutoAnswer', AutoAnswerValue[match.group(1)], qualifier)

    def UpdateDigitalGPIOState(self, value, qualifier):

        phone_name = qualifier['Virtual Channel']
        if phone_name not in self.Commands['DigitalGPIOState']['Status']:
            self.AddMatchString(compile('val digital_gpio_state \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchDigitalGPIOState, qualifier)

        self.__UpdateHelper('DigitalGPIOState', 'get digital_gpio_state \"{0}\"\r'.format(phone_name), qualifier)

    def __MatchDigitalGPIOState(self, match, qualifier):

        DigitalGPIOStateValue = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('DigitalGPIOState', DigitalGPIOStateValue[match.group(1)], qualifier)

    def SetDoNotDisturb(self, value, qualifier):

        DoNotDisturbCommand = {
            'On': '1',
            'Off': '0',
        }

        phone_name = qualifier['Virtual Channel']

        if phone_name not in self.Commands['DoNotDisturb']['Status']:
            self.AddMatchString(compile('val voip_dnd \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchDoNotDisturb, qualifier)

        cmdString = 'set voip_dnd \"{0}\" {1}\r'.format(phone_name, DoNotDisturbCommand[value])
        self.__SetHelper('DoNotDisturb', cmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        phone_name = qualifier['Virtual Channel']
        if phone_name not in self.Commands['DoNotDisturb']['Status']:
            self.AddMatchString(compile('val voip_dnd \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchDoNotDisturb, qualifier)

        self.__UpdateHelper('DoNotDisturb', 'get voip_dnd \"{0}\"\r'.format(phone_name), qualifier)

    def __MatchDoNotDisturb(self, match, qualifier):

        DoNotDisturbValue = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('DoNotDisturb', DoNotDisturbValue[match.group(1)], qualifier)

    def SetDTMF(self, value, qualifier):

        phone_name = qualifier['Virtual Channel']
        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            self.__SetHelper('DTMF', 'set phone_dial \"{0}\" \"{1}\"\r'.format(phone_name, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetFader(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if -100 <= value <= 20:
            if channel_name not in self.Commands['Fader']['Status']:
                self.AddMatchString(compile('val fader \"{0}\" (-*\d+.\d+)\r'.format(channel_name).encode()), self.__MatchFader, qualifier)
            self.__SetHelper('Fader', 'set fader \"{0}\" {1:.1f}\r'.format(channel_name, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFader')

    def UpdateFader(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['Fader']['Status']:
            self.AddMatchString(compile('val fader \"{0}\" (-*\d+.\d+)\r'.format(channel_name).encode()), self.__MatchFader, qualifier)
        self.__UpdateHelper('Fader', 'get fader \"{0}\"\r'.format(channel_name), qualifier)

    def __MatchFader(self, match, qualifier):

        self.WriteStatus('Fader', float(match.group(1)), qualifier)

    def UpdateFirmware(self, value, qualifier):

        self.__UpdateHelper('Firmware', 'get dev_firmware_ver 1\r', qualifier)

    def __MatchFirmware(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, qualifier)

    def SetHook(self, value, qualifier):

        HookCommand = {
            'On': 'phone_connect',
            'Off': 'phone_connect',
            'Flash': 'phone_flash',
            'Ignore': 'phone_ignore',
            'Redial': 'phone_redial',
            'Dial': 'phone_dial',
            'VoIP Send': 'voip_send',
            'VoIP Hold': 'voip_hold',
            'VoIP Transfer': 'voip_transfer',
            'VoIP Conference': 'voip_conference',
            'VoIP Answer': 'voip_answer',
            'VoIP Cancel': 'voip_cancel',
            'VoIP Join': 'voip_join',
            'VoIP Resume': 'voip_resume',
            'Reject': 'phone_reject',
            'VoIP Split': 'voip_split'		# Located on Page 596
        }

        HookState = {
            'On': 0,
            'Off': 1,
        }
        phone_name = qualifier['Virtual Channel']

        if phone_name not in self.Commands['Hook']['Status']:
            self.AddMatchString(compile('val phone_connect \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchHook, qualifier)

        if value in ['On', 'Off']:
            cmdString = 'set {0} \"{1}\" {2}\r'.format(HookCommand[value], phone_name, HookState[value])
            self.__SetHelper('Hook', cmdString, value, qualifier)
        else:
            number = qualifier['Number']
            if value == 'Dial' and number:
                number = '\"{0}\"'.format(number)
            cmdString = 'set {0} \"{1}\" {2}\r'.format(HookCommand[value], phone_name, number)
            self.__SetHelper('Hook', cmdString, value, qualifier)

    def UpdateHook(self, value, qualifier):

        phone_name = qualifier['Virtual Channel']
        if phone_name not in self.Commands['Hook']['Status']:
            self.AddMatchString(compile('val phone_connect \"{0}\" ([01])\r'.format(phone_name).encode()), self.__MatchHook, qualifier)

        self.__UpdateHelper('Hook', 'get phone_connect \"{0}\"\r'.format(phone_name), qualifier)

    def __MatchHook(self, match, qualifier):

        HookValue = {
            b'0': 'On',
            b'1': 'Off',
        }

        self.WriteStatus('Hook', HookValue[match.group(1)], qualifier)

    def SetMatrixGain(self, value, qualifier):

        inputVar = qualifier['Input']
        outputVar = qualifier['Output']
        if inputVar not in self.Commands['MatrixGain']['Status']:
            self.AddMatchString(compile('val matrix_gain \"{0}\" \"{1}\" (-*\d+.\d+)\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixGain, qualifier)
        elif outputVar not in self.Commands['MatrixGain']['Status'][inputVar]:
            self.AddMatchString(compile('val matrix_gain \"{0}\" \"{1}\" (-*\d+.\d+)\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixGain, qualifier)
        if -100 <= value <= 20:
            self.__SetHelper('MatrixGain', 'set matrix_gain \"{0}\" \"{1}\" {2:.1f}\r'.format(inputVar, outputVar, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixGain')

    def UpdateMatrixGain(self, value, qualifier):

        inputVar = qualifier['Input']
        outputVar = qualifier['Output']
        if inputVar not in self.Commands['MatrixGain']['Status']:
            self.AddMatchString(compile('val matrix_gain \"{0}\" \"{1}\" (-*\d+.\d+)\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixGain, qualifier)
        elif outputVar not in self.Commands['MatrixGain']['Status'][inputVar]:
            self.AddMatchString(compile('val matrix_gain \"{0}\" \"{1}\" (-*\d+.\d+)\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixGain, qualifier)
        self.__UpdateHelper('MatrixGain', 'get matrix_gain \"{0}\" \"{1}\"\r'.format(inputVar, outputVar), qualifier)

    def __MatchMatrixGain(self, match, qualifier):

        self.WriteStatus('MatrixGain', float(match.group(1)), qualifier)

    def SetMatrixMute(self, value, qualifier):

        MuteState = {
            'On': 1,
            'Off': 0,
        }
        inputVar = qualifier['Input']
        outputVar = qualifier['Output']
        state = MuteState[value]
        if inputVar not in self.Commands['MatrixMute']['Status']:
            self.AddMatchString(compile('val matrix_mute \"{0}\" \"{1}\" ([01])\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixMute, qualifier)
        elif outputVar not in self.Commands['MatrixMute']['Status'][inputVar]:
            self.AddMatchString(compile('val matrix_mute \"{0}\" \"{1}\" ([01])\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixMute, qualifier)
        self.__SetHelper('MatrixMute', 'set matrix_mute \"{0}\" \"{1}\" {2}\r'.format(inputVar, outputVar, state), value, qualifier)

    def UpdateMatrixMute(self, value, qualifier):

        inputVar = qualifier['Input']
        outputVar = qualifier['Output']
        if inputVar not in self.Commands['MatrixMute']['Status']:
            self.AddMatchString(compile('val matrix_mute \"{0}\" \"{1}\" ([01])\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixMute, qualifier)
        elif outputVar not in self.Commands['MatrixMute']['Status'][inputVar]:
            self.AddMatchString(compile('val matrix_mute \"{0}\" \"{1}\" ([01])\r'.format(inputVar, outputVar).encode()), self.__MatchMatrixMute, qualifier)

        self.__UpdateHelper('MatrixMute', 'get matrix_mute \"{0}\" \"{1}\"\r'.format(inputVar, outputVar), qualifier)

    def __MatchMatrixMute(self, match, qualifier):

        MuteValue = {
            b'1': 'On',
            b'0': 'Off',
        }
        self.WriteStatus('MatrixMute', MuteValue[match.group(1)], qualifier)

    def SetMicGain(self, value, qualifier):

        channel = qualifier['Virtual Channel']
        if -20 <= value <= 64:
            if channel not in self.Commands['MicGain']['Status']:
                self.AddMatchString(compile('val mic_in_gain \"{0}\" (-*[0-9]+.[0-9]+)\r'.format(channel).encode()), self.__MatchMicGain, qualifier)
            self.__SetHelper('MicGain', 'set mic_in_gain \"{0}\" {1:.1f}\r'.format(channel, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        channel = qualifier['Virtual Channel']
        if channel not in self.Commands['MicGain']['Status']:
            self.AddMatchString(compile('val mic_in_gain \"{0}\" (-*[0-9]+.[0-9]+)\r'.format(channel).encode()), self.__MatchMicGain, qualifier)
        self.__UpdateHelper('MicGain', 'get mic_in_gain \"{0}\"\r'.format(channel), qualifier)

    def __MatchMicGain(self, match, qualifier):

        self.WriteStatus('MicGain', float(match.group(1)), qualifier)

    def SetMute(self, value, qualifier):

        MuteState = {
            'On': 1,
            'Off': 0,
        }
        channel_name = qualifier['Virtual Channel']
        state = MuteState[value]
        if channel_name not in self.Commands['Mute']['Status']:
            self.AddMatchString(compile('val mute \"{0}\" ([01])\r'.format(channel_name).encode()), self.__MatchMute, qualifier)
        self.__SetHelper('Mute', 'set mute \"{0}\" {1}\r'.format(channel_name, state), value, qualifier)

    def UpdateMute(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['Mute']['Status']:
            self.AddMatchString(compile('val mute \"{0}\" ([01])\r'.format(channel_name).encode()), self.__MatchMute, qualifier)
        self.__UpdateHelper('Mute', 'get mute \"{0}\"\r'.format(channel_name), qualifier)

    def __MatchMute(self, match, qualifier):

        MuteValue = {
            b'1': 'On',
            b'0': 'Off',
        }
        self.WriteStatus('Mute', MuteValue[match.group(1)], qualifier)

    def SetOutputGain(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if -100 <= value <= 4:
            if channel_name not in self.Commands['OutputGain']['Status']:
                self.AddMatchString(compile('val line_out_gain \"{0}\" (-*\d+.\d+)\r'.format(channel_name).encode()), self.__MatchOutputGain, qualifier)
            self.__SetHelper('OutputGain', 'set line_out_gain \"{0}\" {1}\r'.format(channel_name, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['OutputGain']['Status']:
            self.AddMatchString(compile('val line_out_gain \"{0}\" (-*\d+.\d+)\r'.format(channel_name).encode()), self.__MatchOutputGain, qualifier)
        self.__UpdateHelper('OutputGain', 'get line_out_gain \"{0}\"\r'.format(channel_name), qualifier)

    def __MatchOutputGain(self, match, qualifier):

        self.WriteStatus('OutputGain', float(match.group(1)), qualifier)

    def SetPresetRecallCommand(self, value, qualifier):

        PresetRecallCommandCmdString = value
        if PresetRecallCommandCmdString:
            PresetRecallCommandCmdString = 'run \"' + PresetRecallCommandCmdString + '\"\r'
            PresetRecallCommandCmdString = PresetRecallCommandCmdString.encode(encoding='iso-8859-1')
            self.__SetHelper('PresetRecallCommand', PresetRecallCommandCmdString, value, qualifier)

    def UpdateRingStatus(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['RingStatus']['Status']:
            self.AddMatchString(compile('val phone_ring \"{0}\" (\d)\r'.format(channel_name).encode()), self.__MatchRingStatus, qualifier)
        self.__UpdateHelper('RingStatus', 'get phone_ring \"{0}\"\r'.format(channel_name), qualifier)

    def __MatchRingStatus(self, match, qualifier):

        value = {
            b'1': 'On',
            b'0': 'Off',
        }
        self.WriteStatus('RingStatus', value[match.group(1)], qualifier)

    def UpdateVoIPCallAppearanceState(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['VoIPCallAppearanceState']['Status']:
            self.AddMatchString(compile(('val voip_call_appearance_state \"({0})\"'.format(channel_name) + ' (\d{1,2}) (disconnected|free|dialtone|connected|proceeding|ringback)\r').encode()), self.__MatchVoIPCallAppearanceState, qualifier)

    def __MatchVoIPCallAppearanceState(self, match, qualifier):

        VoIPCallAppearanceStateValue = {
            b'dialtone': 'Dial Tone',
            b'disconnected': 'Disconnected',
            b'free': 'Free',
            b'ringback': 'Ringback',
            b'proceeding': 'Proceeding',
            b'connected': 'Connected'
        }
        qualifier = {}
        qualifier['Call Appearance Index'] = match.group(2).decode()
        qualifier['Virtual Channel'] = match.group(1).decode()
        self.WriteStatus('VoIPCallAppearanceState', VoIPCallAppearanceStateValue[match.group(3)], qualifier)

    def UpdateVoIPCallerID(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['VoIPCallerID']['Status']:
            self.AddMatchString(compile(('val voip_call_appearance_info \"({0})\"'.format(channel_name) + ' (\d{1,2}) \d \"(.{0,128})\"\r').encode()), self.__MatchVoIPCallerID, qualifier)

    def __MatchVoIPCallerID(self, match, qualifier):

        qualifier = {}
        qualifier['Call Appearance Index'] = match.group(2).decode()
        qualifier['Virtual Channel'] = match.group(1).decode()
        self.WriteStatus('VoIPCallerID', match.group(3).decode(), qualifier)

    def SetVoIPDialMode(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['VoIPDialMode']['Status']:
            self.AddMatchString(compile('val voip_dial_mode \"{0}\" (number|url)\r'.format(channel_name).encode()), self.__MatchVoIPDialMode, qualifier)
        self.__SetHelper('VoIPDialMode', 'set voip_dial_mode \"{0}\" {1}\r'.format(channel_name, value.lower()), value, qualifier)

    def UpdateVoIPDialMode(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['VoIPDialMode']['Status']:
            self.AddMatchString(compile('val voip_dial_mode \"{0}\" (number|url)\r'.format(channel_name).encode()), self.__MatchVoIPDialMode, qualifier)
        self.__UpdateHelper('VoIPDialMode', 'get voip_dial_mode \"{0}\"\r'.format(channel_name), qualifier)

    def __MatchVoIPDialMode(self, match, qualifier):

        VoIPDialModeValue = {
            b'url': 'URL',
            b'number': 'Number'
        }
        self.WriteStatus('VoIPDialMode', VoIPDialModeValue[match.group(1)], qualifier)

    def SetVoIPLineSelect(self, value, qualifier):

        if 1 <= int(value) <= 12:
            VoIPLineSelectCmdString = 'set voip_line \"{0}\" {1}\r'.format(qualifier['Virtual Channel'], value)
            self.__SetHelper('VoIPLineSelect', VoIPLineSelectCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetVoIPLineSelect')

    def UpdateVoIPLineStatus(self, value, qualifier):

        channel_name = qualifier['Virtual Channel']
        if channel_name not in self.Commands['VoIPLineStatus']['Status']:
            self.AddMatchString(compile(('val voip_line_state \"({0})\"'.format(channel_name) + ' (\d{1,2}) (messages|do_not_disturb|line_not_registered|line_registered|in_conference|call_active|call_on_hold|shared_line|speed_dial_indicator|forward_all_calls|acd_online|acd_offline|acd_not_logged_in|acd_available|remote_active|secure_rtp|remote_hold|hd_audio|offering|proceed|dial_tone|held|disconnect|feat_enabled|feat_disabled|cma_presence_available|cma_presence_busy|cma_presence_available_in_a_call|cma_presence_unavailable|cma_presence_away|cma_presence_offline|ocs_available|ocs_busy|ocs_do_not_disturb|ocs_away|ocs_no_info|ocs_offline|blf_busy|none)\r').encode()), self.__MatchVoIPLineStatus, qualifier)

    def __MatchVoIPLineStatus(self, match, tag):

        ValueStateValues = {
            'messages': 'Messages',
            'do_not_disturb': 'Do Not Disturb',
            'line_not_registered': 'Not Registered',
            'line_registered': 'Registered',
            'in_conference': 'In Conference',
            'call_active': 'Call Active',
            'call_on_hold': 'Call On Hold',
            'shared_line': 'Shared Line',
            'speed_dial_indicator': 'Speed Dial Indicator',
            'forward_all_calls': 'Forward All Calls',
            'acd_online': 'ACD Online',
            'acd_offline': 'ACD Offline',
            'acd_not_logged_in': 'ACD Not Logged In',
            'acd_available': 'ACD Available',
            'remote_active': 'Remote Active',
            'secure_rtp': 'Secure RTP',
            'remote_hold': 'Remote Hold',
            'hd_audio': 'HD Audio',
            'offering': 'Offering',
            'proceed': 'Proceed',
            'dial_tone': 'Dial Tone',
            'held': 'Held',
            'disconnect': 'Disconnect',
            'feat_enabled': 'Feat Enabled',
            'feat_disabled': 'Feat Disabled',
            'cma_presence_available': 'CMA Presence Available',
            'cma_presence_busy': 'CMA Presence Busy',
            'cma_presence_available_in_a_call': 'CMA Presence Available in a Call',
            'cma_presence_unavailable': 'CMA Presence Unavailable',
            'cma_presence_away': 'CMA Presence Away',
            'cma_presence_offline': 'CMA Presence Offline',
            'ocs_available': 'OCS Available',
            'ocs_away': 'OCS Away',
            'ocs_busy': 'OCS Busy',
            'ocs_do_not_disturb': 'OCS Do Not Disturb',
            'ocs_no_info': 'OCS No Info',
            'ocs_offline': 'OCS Offline',
            'blf_busy': 'BLF Busy',
            'none': 'Idle'
        }

        qualifier = {}
        if 1 <= int(match.group(2).decode()) <= 12:
            qualifier['Line Number'] = match.group(2).decode()
        qualifier['Virtual Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('VoIPLineStatus', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, qualifier):

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

        self.Error([match.group(0).decode()])

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
        tempCompileList = copy.copy(self._compile_list)
        for regexString in tempCompileList:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    tempCompileList[regexString]['callback'](result, tempCompileList[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
