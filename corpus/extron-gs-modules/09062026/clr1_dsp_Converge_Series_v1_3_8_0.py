from extronlib.interface import EthernetClientInterface, SerialInterface
from extronlib.system import ProgramLog
import time
from re import compile, match, search

class DeviceClass():

    def __init__(self, Model):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        
        self.Debug = False

        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.DeviceType = 'I'
        self.Inputs = (1, 12)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 12)
        self.AmplifierOutput = (1,4)
        self.ProcessingChannels = 'ABCDEFGH'
        self.PAVirtualReference = (1,4)
        self.Authenticated = False
        self.DeviceID = '0'
        
        self.Models = {
            'Converge Pro SR 1212': self.clr1_25_154_SR1212,
            'Converge Pro 840T': self.clr1_25_154_840T,
            'Converge Pro 880TA': self.clr1_25_154_880TA,
            'Converge Pro 880': self.clr1_25_154_880,
            'Converge Pro SR 1212A': self.clr1_25_154_SR1212A,
            'Converge Pro 880T': self.clr1_25_154_880T,
            'Converge Pro 8i': self.clr1_25_154_8i,
            'Converge Pro TH20': self.clr1_25_154_TH20,
            'Converge Pro VH20': self.clr1_25_154_VH20,
            'Beamforming Mic Array': self.clr1_25_154_Beam,
            }
        
        if Model not in self.Models: 
            print('Model mismatch')              
        else:
            self.Models[Model]()
            
        self.PasswdPromptCount = 0
        self.SerialEchoEnabled = False

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmplifierOutputGain': {'Parameters': ['Amplifier Output'], 'Status': {}},
            'AmplifierOutputMute': {'Parameters': ['Amplifier Output'], 'Status': {}},
            'AutoAnswer': {'Status': {}},
            'AutoAnswerVoIP': {'Status': {}},
            'BeamformingMicArrayGain': {'Status': {}},
            'BeamformingMicArrayMute': {'Status': {}},
            'CallerID': {'Status': {}},
            'ClearEffect': {'Status': {}},
            'DialString': {'Status': {}},
            'DTMF': {'Status': {}},
            'DTMFVoIP': {'Status': {}}, # kept for backward compatibility
            'FaderGain': {'Parameters': ['Fader'], 'Status': {}},
            'FaderMute': {'Parameters': ['Fader'], 'Status': {}},
            'GateStatus': {'Parameters':['Mic'], 'Status': {}},            
            'GPIOStatus': {'Parameters': ['Pin', 'Port'], 'Status': {}},
            'Hook': {'Status': {}},
            'HookVoIP': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'LineInputGain': {'Parameters': ['Line Input'], 'Status': {}},
            'LineInputMute': {'Parameters': ['Line Input'], 'Status': {}},
            'Macro': {'Status': {}},
            'Matrix': {'Parameters': ['Source', 'Source Group', 'Destination', 'Destination Group'], 'Status': {}},
            'MatrixLevel': {'Parameters': ['Source', 'Source Group', 'Destination', 'Destination Group'], 'Status': {}},
            'MicGain': {'Parameters': ['Mic'], 'Status': {}},
            'MicMute': {'Parameters': ['Mic'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'PhonebookAddEntryCommand': {'Parameters': ['Speed Dial'], 'Status': {}},
            'PhonebookAddEntryString': {'Status': {}},
            'PhonebookCount': {'Status': {}},
            'PhonebookDeleteEntryCommand': {'Status': {}},
            'PhonebookDeleteEntryString': {'Status': {}},
            'PhonebookEntry': {'Parameters': ['Index'], 'Status': {}},
            'PhonebookEntrySpeedDialValue': {'Parameters': ['Index'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Step'], 'Status': {}},
            'PhonebookRefresh': {'Status': {}},
            'PhonebookWritetoDialString': {'Parameters': ['Index'], 'Status': {}},
            'PhoneReceiveGain': {'Status': {}},
            'PhoneReceiveMute': {'Status': {}},
            'PhoneTransmitGain': {'Status': {}},
            'PhoneTransmitMute': {'Status': {}},
            'Preset': {'Parameters': ['Preset Number'], 'Status': {}},
            'ProcessingChannelGain': {'Parameters': ['Processing Channel'], 'Status': {}},
            'ProcessingChannelMute': {'Parameters': ['Processing Channel'], 'Status': {}},
            'RingerEnable': {'Status': {}},
            'RingerVoIPEnable': {'Status': {}},
            'SafetyMute': {'Status': {}},
            'SpeedDial': {'Status': {}},
            'SpeedDialVoip': {'Status': {}}, # kept for backward compatibility
            'StringExecution': {'Status': {}},
            'VoIPReceiveGain': {'Status': {}},
            'VoIPReceiveMute': {'Status': {}},
            'VoIPTransmitGain': {'Status': {}},
            'VoIPTransmitMute': {'Status': {}},
            }

        self.timeStamp = 0
        self.Matches = {}      
            
        self.deviceUsername = 'Clearone'
        self.devicePassword = 'Converge'
        
        self.Channels = compile('(1?\d|[A-Z])')

        self.MAX_PHONEBOOK_ENTRIES = 20
        self.PhonebookEntryCount = self.MAX_PHONEBOOK_ENTRIES

        self.PhonebookList = [{'name': '', 'number': '', 'speed': 'N/A'} for _ in range(0, self.MAX_PHONEBOOK_ENTRIES)]
        self.PhonebookStartIndex = 0

        self.PhonebookAddPattern = compile('[\#\*\d]{1,44} .{1,16}')
   
        if self.Unidirectional == 'False':
            self.AddMatchString(compile('#{0}{1} ERROR (.*)\r\n'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchError, None)
            self.AddMatchString(compile('#{0}{1} '.format(self.DeviceType, self._DeviceID).encode() + b'PHONEBOOKREAD (?P<index>1?[0-9]|20) (?P<speed>1?[0-9]|20) (?P<number>[\#\*\d]{1,44}) (?P<name>.{1,16})\r\n'), self.__MatchPhonebookRefresh, None)
            self.AddMatchString(compile(b'user:\s'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'pass:\s'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Invalid User/Pass.'), self.__MatchNonAuthenticated, None)
            self.AddMatchString(compile(b'Authenticated.'), self.__MatchAuthenticated, None)
            if self.DeviceType in ['H', 'D', '3', '2']:
                self.AddMatchString(compile('#{0}{1} '.format(self.DeviceType, self._DeviceID).encode() + b'CALLERID (?:[1-9]|10|11|12) (\d{7,11}) ([a-z A-Z]*)\r\nOK'), self.__MatchCallerID, None)
            
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) J ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchAmplifierOutputGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MUTE (\d{1,2}) J (1|0)').encode()), self.__MatchAmplifierOutputMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GATE ([0-9A-F]{1,2})').encode()), self.__MatchGateStatus, None)
            self.AddMatchString(compile('#{0}{1} AA 1 (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile('#{0}{1} XAA 1 Z (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchAutoAnswerVoIP, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) V ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchBeamformingMicArrayGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MUTE (\d{1,2}) V (1|0)').encode()), self.__MatchBeamformingMicArrayMute, None)
            self.AddMatchString(compile('#{0}{1} TE 1 (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchHook, 'TE'),
            self.AddMatchString(compile('#{0}{1} RING 1 (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchHook, 'RING')                                                    
            self.AddMatchString(compile('#{0}{1} XTE 1 Z (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchHookVoIP, 'TE'),
            self.AddMatchString(compile('#{0}{1} XRING 1 Z (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchHookVoIP, 'RING')                                                     
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'CLEAREFFECT \d{1,2} (0|1)').encode()), self.__MatchClearEffect, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) F ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchFaderGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MUTE (\d{1,2}) F (1|0)').encode()), self.__MatchFaderMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GPIOSTATUS (1[0-9]|2[0-4]|[1-9]) (1|2) (0|1)').encode()), self.__MatchGPIOStatus, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) I ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchInputGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MUTE (\d{1,2}) I (1|0)').encode()), self.__MatchInputMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) L ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchLineInputGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MUTE (\d{1,2}) L (1|0)').encode()), self.__MatchLineInputMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d) M ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchMicGain, None)
            self.AddMatchString(compile('#{0}{1} MUTE (\d) M (1|0)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchMicMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) O ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchOutputGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MUTE (\d{1,2}) O (1|0)').encode()), self.__MatchOutputMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'PHONEBOOKCNT (1?[0-9]|20)\r\n').encode()), self.__MatchPhonebookCount, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN ([A-H]) P ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchProcessingChannelGain, None)
            self.AddMatchString(compile('#{0}{1} MUTE ([A-H]) P (1|0)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchProcessingChannelMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MACRO (\d{1,3})').encode()), self.__MatchMacro, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MTRX (1?\d|[A-Z]) (I|M|P|E|L|F|R|K|Z|U|V) (1?\d|[A-Z]) (H|J|O|P|E|F|T|B|K|D) (0|1|2|3|4|5|6)').encode()), self.__MatchMatrix, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'MTRXLVL (?P<inChannel>1?\d|[A-Z]) (?P<inGroup>I|M|P|E|L|F|R|K|Z|U|V) (?P<outChannel>1?\d|[A-Z]) (?P<outGroup>H|J|O|P|E|F|T|B|K|D) (?P<value>-?[0-9]{1,2}\.[0-9]{2}) A\r\n').encode()), self.__MatchMatrixLevel, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'PRESET (\d{1,2}) (2|1|0)').encode()), self.__MatchPreset, None)
            self.AddMatchString(compile('#{0}{1} MUTE 1 R (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchPhoneReceiveMute, None)
            self.AddMatchString(compile('#{0}{1} MUTE 1 T (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchPhoneTransmitMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) T ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchPhoneTransmitGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) R ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchPhoneReceiveGain, None)
            self.AddMatchString(compile('#{0}{1} RINGEREN 1 (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchRingerEnable, None)
            self.AddMatchString(compile('#{0}{1} XRINGEREN 1 Z (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchRingerVoIPEnable, None)
            self.AddMatchString(compile('#{0}{1} SFTYMUTE (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchSafetyMute, None)
            self.AddMatchString(compile('#{0}{1} STRING ([0-7])'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchStringExecution, None)
            self.AddMatchString(compile('#{0}{1} MUTE 1 Z (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchVoIPReceiveMute, None)
            self.AddMatchString(compile('#{0}{1} MUTE 1 K (0|1)'.format(self.DeviceType, self._DeviceID).encode()), self.__MatchVoIPTransmitMute, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) K ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchVoIPTransmitGain, None)
            self.AddMatchString(compile('#{0}{1} {2}'.format(self.DeviceType, self._DeviceID, 'GAIN (\d{1,2}) Z ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchVoIPReceiveGain, None)

    @property
    def Username(self):
        return self.deviceUsername
    
    @Username.setter
    def Username(self, value):
        self.deviceUsername = value
        
    @property
    def Password(self):
        return self.devicePassword
    
    @Password.setter
    def Password(self, value):
        self.devicePassword = value
        
    @property
    def DeviceID(self):
        return self._DeviceID
    
    @DeviceID.setter
    def DeviceID(self, value):
        if value in '0123456789ABCDEF':
            self._DeviceID = value
        else:
            print('DeviceID Parameter should be one of 0-9 or A-F')

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')
        
    def __MatchUsername(self, match, qualifier):
        self.SetUsername(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')
        
    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def __MatchNonAuthenticated(self, match, qualifier):
        print('Invalid Username/Password')
        self.Authenticated = False
        
    def __MatchAuthenticated(self, match, qualifier):
        print('Authenticated')
        self.Authenticated = True
    
    def SetAmplifierOutputGain(self, value, qualifier):
        AmplifierOutput = qualifier['Amplifier Output']
        if -65.0 <= value <= 20.0 and self.AmplifierOutput[0] <= int(AmplifierOutput) <= self.AmplifierOutput[1]:
            CommandString = 'GAIN {0} J {1:0.1f} A'.format(AmplifierOutput, value)
            self.__SetHelper('AmplifierOutputGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for AmplifierOutputGain')

    def UpdateAmplifierOutputGain(self, value, qualifier):
        AmplifierOutput = qualifier['Amplifier Output']
        if self.AmplifierOutput[0] <= int(AmplifierOutput) <= self.AmplifierOutput[1]:
            CommandString = 'GAIN {0} J'.format(AmplifierOutput)
            self.__UpdateHelper('AmplifierOutputGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for AmplifierOutputGain')

    def __MatchAmplifierOutputGain(self, match, tag):
        qualifier = {'Amplifier Output': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('AmplifierOutputGain', value, qualifier)

    def SetAmplifierOutputMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }
        AmplifierOutput = qualifier['Amplifier Output']
        if self.AmplifierOutput[0] <= int(AmplifierOutput) <= self.AmplifierOutput[1]:
            CommandString = 'MUTE {0} J {1}'.format(AmplifierOutput, MuteValues[value])
            self.__SetHelper('AmplifierOutputMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for AmplifierOutputMute')

    def UpdateAmplifierOutputMute(self, value, qualifier):
        AmplifierOutput = qualifier['Amplifier Output']
        if self.AmplifierOutput[0] <= int(AmplifierOutput) <= self.AmplifierOutput[1]:
            CommandString = 'MUTE {0} J'.format(AmplifierOutput)
            self.__UpdateHelper('AmplifierOutputMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for AmplifierOutputMute')

    def __MatchAmplifierOutputMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }
        qualifier = {'Amplifier Output': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('AmplifierOutputMute', value, qualifier)

    def SetAutoAnswer(self, value, qualifier):
        if self.DeviceType == 'E':
            self.SetAutoAnswerVoIP(value, qualifier)
        else:
            AAValues = {
                        'On': '1',
                        'Off': '0',
                        'Toggle': '2'
                        }
            CommandString = 'AA 1 {0}'.format(AAValues[value])
            self.__SetHelper('AutoAnswer', CommandString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):
        if self.DeviceType == 'E':
            self.UpdateAutoAnswerVoIP(value, qualifier)
        else:
            self.__UpdateHelper('AutoAnswer', 'AA 1', value, qualifier)

    def __MatchAutoAnswer(self, match, tag):
        AAStates = {
                    b'1': 'On',
                    b'0': 'Off'
                    }
        value = AAStates[match.group(1)]
        self.WriteStatus('AutoAnswer', value, None)

    def SetAutoAnswerVoIP(self, value, qualifier):
        AAValues = {
                    'On': '1',
                    'Off': '0',
                    'Toggle': '2'
                    }
        CommandString = 'XAA 1 Z {0}'.format(AAValues[value])
        self.__SetHelper('AutoAnswer', CommandString, value, qualifier)

    def UpdateAutoAnswerVoIP(self, value, qualifier):
        self.__UpdateHelper('AutoAnswer', 'XAA 1 Z', value, qualifier)

    def __MatchAutoAnswerVoIP(self, match, tag):
        AAVoIPStates = {
                    b'1': 'On',
                    b'0': 'Off'
                    }
        value = AAVoIPStates[match.group(1)]
        self.WriteStatus('AutoAnswer', value, None)

    def SetBeamformingMicArrayGain(self, value, qualifier):

        if -65.0 <= value <= 20.0:
            CommandString = 'GAIN 1 V {0:0.1f} A'.format(value)
            self.__SetHelper('BeamformingMicArrayGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for BeamformingMicArrayGain')

    def UpdateBeamformingMicArrayGain(self, value, qualifier):

        CommandString = 'GAIN 1 V'
        self.__UpdateHelper('BeamformingMicArrayGain', CommandString, value, qualifier)

    def __MatchBeamformingMicArrayGain(self, match, tag):
        value = float(match.group(2))
        self.WriteStatus('BeamformingMicArrayGain', value, None)

    def SetBeamformingMicArrayMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }

        CommandString = 'MUTE 1 V {0}'.format(MuteValues[value])
        self.__SetHelper('BeamformingMicArrayMute', CommandString, value, qualifier)

    def UpdateBeamformingMicArrayMute(self, value, qualifier):

        CommandString = 'MUTE 1 V'
        self.__UpdateHelper('BeamformingMicArrayMute', CommandString, value, qualifier)

    def __MatchBeamformingMicArrayMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }

        value = MuteStates[match.group(2)]
        self.WriteStatus('BeamformingMicArrayMute', value, None)

    def __MatchCallerID(self, match, tag):
        value = match.group(2).decode() + ' - ' + match.group(1).decode()
        self.WriteStatus('CallerID', value, None)

    def SetClearEffect(self, value, qualifier):
        ClearEffectValues = {
                             'Off': '0',
                             'On': '1',
                             'Toggle': '2'
                             }

        CommandString = 'CLEAREFFECT 1 {0}'.format(ClearEffectValues[value])
        self.__SetHelper('ClearEffect', CommandString, value, qualifier)

    def UpdateClearEffect(self, value, qualifier):
        CommandString = 'CLEAREFFECT  1'
        self.__UpdateHelper('ClearEffect', CommandString, value, qualifier)

    def __MatchClearEffect(self, match, tag):
        ClearEffectStates = {
                             b'1': 'On',
                             b'0': 'Off'
                             }
        value = ClearEffectStates[match.group(1)]
        self.WriteStatus('ClearEffect', value, None)

    def SetDTMF(self, value, qualifier):
        if self.DeviceType == 'E':
            self.SetDTMFVoIP(value, qualifier)
        else:
            if value in '0123456789*#,':
                CommandString = 'DIAL 1 {0}'.format(value)
                self.__SetHelper('DTMF', CommandString, value, qualifier)
            else:
                print('Invalid Set Command for DTMF')

    def SetDTMFVoIP(self, value, qualifier):
        if value in '0123456789*#,':
            CommandString = 'XDIAL 1 Z {0}'.format(value)
            self.__SetHelper('DTMF', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for DTMF')

    def SetFaderGain(self, value, qualifier):
        Fader = qualifier['Fader']
        if -65.0 <= value <= 20.0 and self.Fader[0] <= int(Fader) <= self.Fader[1]:
            CommandString = 'GAIN {0} F {1:0.1f} A'.format(Fader, value)
            self.__SetHelper('FaderGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for FaderGain')

    def UpdateFaderGain(self, value, qualifier):
        Fader = qualifier['Fader']
        if self.Fader[0] <= int(Fader) <= self.Fader[1]:
            CommandString = 'GAIN {0} F'.format(Fader)
            self.__UpdateHelper('FaderGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for FaderGain')

    def __MatchFaderGain(self, match, tag):
        qualifier = {'Fader': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('FaderGain', round(value, 1), qualifier)

    def SetFaderMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }
        Fader = qualifier['Fader']
        if self.Fader[0] <= int(Fader) <= self.Fader[1]:
            CommandString = 'MUTE {0} F {1}'.format(Fader, MuteValues[value])
            self.__SetHelper('FaderMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for FaderMute')

    def UpdateFaderMute(self, value, qualifier):
        Fader = qualifier['Fader']
        if self.Fader[0] <= int(Fader) <= self.Fader[1]:
            CommandString = 'MUTE {0} F'.format(Fader)
            self.__UpdateHelper('FaderMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for FaderMute')

    def __MatchFaderMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }
        qualifier = {'Fader': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('FaderMute', value, qualifier)

    def UpdateGateStatus(self, value, qualifier):
        GateStatusCmdString = 'GATE'
        self.__UpdateHelper('GateStatus', GateStatusCmdString, value, qualifier)

    def __MatchGateStatus(self, match, tag):
        value = {'1' : 'On',
                 '0' : 'Off'
                 }

        res = bin(int(match.group(1).decode(),16)).split('b')[1]
        if self.Mics[1] != 4:
            res = res.zfill(8)  
        res = res[::-1]

        for i, j in enumerate(res):
            self.WriteStatus('GateStatus', value[j], {'Mic': str(i+1)})
    
    def SetGPIOStatus(self, value, qualifier):
        PortStates = {
            'A': '1',
            'B': '2'
        }

        ValueStateValues = {
            'High': '0',
            'Low': '1'
        }

        if (1 <= int(qualifier['Pin']) <= 16) and (int(qualifier['Pin']) % 2 == 0) and (PortStates[qualifier['Port']] == '1'):
            GPIOStatusCmdString = 'GPIOSTATUS {0} {1} {2}'.format(qualifier['Pin'], PortStates[qualifier['Port']], ValueStateValues[value])
            self.__SetHelper('GPIOStatus', GPIOStatusCmdString, value, qualifier)

        elif (int(qualifier['Pin']) == 22) and (PortStates[qualifier['Port']] == '2'):
            GPIOStatusCmdString = 'GPIOSTATUS {0} {1} {2}'.format(qualifier['Pin'], PortStates[qualifier['Port']], ValueStateValues[value])
            self.__SetHelper('GPIOStatus', GPIOStatusCmdString, value, qualifier)

    def UpdateGPIOStatus(self, value, qualifier):
        PortStates = {
            'A': '1',
            'B': '2'
        }

        if ((1 <= int(qualifier['Pin']) <= 16) and (int(qualifier['Pin']) % 2 == 0) and (PortStates[qualifier['Port']] == '1')) or (int(qualifier['Pin']) == 22):
            GPIOStatusCmdString = 'GPIOSTATUS {0} {1}'.format(qualifier['Pin'], PortStates[qualifier['Port']])
            self.__UpdateHelper('GPIOStatus', GPIOStatusCmdString, value, qualifier)

    def __MatchGPIOStatus(self, match, tag):
        PinStates = {
            '2': '2',
            '4': '4',
            '6': '6',
            '8': '8',
            '10': '10',
            '12': '12',
            '14': '14',
            '16': '16',
            '22': '22'
        }

        PortStates = {
            '1': 'A',
            '2': 'B'
        }

        ValueStateValues = {
            '0': 'High',
            '1': 'Low'
        }

        qualifier = {}
        qualifier['Pin'] = PinStates[match.group(1).decode()]
        qualifier['Port'] = PortStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('GPIOStatus', value, qualifier)

    def SetHook(self, value, qualifier):
        if self.DeviceType == 'E':
            self.SetHookVoIP(value, qualifier)
        else:
            TEValues = {
                'On': 'TE 1 0',
                'Off': 'TE 1 1',
                'Toggle': 'TE 1 2',
                'Flash': 'HOOK 1',
                'Redial': 'REDIAL 1'
                }
    
            if value in TEValues:
                self.__SetHelper('Hook', TEValues[value], value, qualifier)
            elif value == 'Dial':
                number = qualifier['Number']
                if number:
                    self.__SetHelper('Hook', 'DIAL 1 {0}'.format(number), value, qualifier)
            else:
                print('Invalid Set Command for Hook')

    def UpdateHook(self, value, qualifier):
        if self.DeviceType == 'E':
            self.UpdateHookVoIP(value, qualifier)
        else:
            self.__UpdateHelper('Hook', 'TE 1', value, qualifier)

    def __MatchHook(self, match, tag):
        if tag == 'TE':
            TEStates = {
                        b'0': 'On',
                        b'1': 'Off'
                        }
            value = TEStates[match.group(1)]
            if (value == 'On') & ((time.monotonic() - self.timeStamp) > 5):
                self.WriteStatus('CallerID', '', None)
        elif tag == 'RING':
            self.timeStamp = time.monotonic()
            RingStates = {
                          b'0': 'On',
                          b'1': 'Ringing'
                          }
            value = RingStates[match.group(1)]

        self.WriteStatus('Hook', value, None)

    def SetHookVoIP(self, value, qualifier):
        if value in ['On', 'Off', 'Toggle']:
            TEValues = {
                        'On': '0',
                        'Off': '1',
                        'Toggle': '2'
                        }
            CommandString = 'XTE 1 Z {0}'.format(TEValues[value])
        elif value == 'Flash':
            CommandString = 'XHOOK 1 Z'
        elif value == 'Redial':
            CommandString = 'XREDIAL 1 Z'
        elif value == 'Dial':
            number = qualifier['Number']
            if number:
                CommandString = 'XDIAL 1 Z {0}'.format(number)
            else:
                CommandString = ''
        else:
            print('Invalid Set Command for Hook')
            CommandString = ''
        if CommandString:
            self.__SetHelper('Hook', CommandString, value, qualifier)        

    def UpdateHookVoIP(self, value, qualifier):
        self.__UpdateHelper('Hook', 'XTE 1 Z', value, qualifier)

    def __MatchHookVoIP(self, match, tag):
        if tag == 'TE':
            TEStates = {
                        b'0': 'On',
                        b'1': 'Off'
                        }
            value = TEStates[match.group(1)]
        elif tag == 'RING':
            RingStates = {
                          b'0': 'On',
                          b'1': 'Ringing'
                          }
            value = RingStates[match.group(1)]
        self.WriteStatus('Hook', value, None)

    def SetInputGain(self, value, qualifier):
        Input = qualifier['Input']
        if -65.0 <= value <= 20.0 and self.Inputs[0] <= int(Input) <= self.Inputs[1]:
            CommandString = 'GAIN {0} I {1:0.1f} A'.format(Input, value)
            self.__SetHelper('InputGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for InputGain')

    def UpdateInputGain(self, value, qualifier):
        Input = qualifier['Input']
        if self.Inputs[0] <= int(Input) <= self.Inputs[1]:
            CommandString = 'GAIN {0} I'.format(Input)
            self.__UpdateHelper('InputGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for InputGain')

    def __MatchInputGain(self, match, tag):
        qualifier = {'Input': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('InputGain', round(value, 1), qualifier)
        

    def SetInputMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }
        Input = qualifier['Input']
        if self.Inputs[0] <= int(Input) <= self.Inputs[1]:
            CommandString = 'MUTE {0} I {1}'.format(Input, MuteValues[value])
            self.__SetHelper('InputMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for InputMute')

    def UpdateInputMute(self, value, qualifier):
        Input = qualifier['Input']
        if self.Inputs[0] <= int(Input) <= self.Inputs[1]:
            CommandString = 'MUTE {0} I'.format(Input)
            self.__UpdateHelper('InputMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for InputMute')

    def __MatchInputMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }
        qualifier = {'Input': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('InputMute', value, qualifier)

    def SetLineInputGain(self, value, qualifier):
        LineInput = qualifier['Line Input']
        if -65.0 <= value <= 20.0 and self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'GAIN {0} L {1:0.1f} A'.format(LineInput, value)
            self.__SetHelper('LineInputGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for LineInputGain')

    def UpdateLineInputGain(self, value, qualifier):
        LineInput = qualifier['Line Input']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'GAIN {0} L'.format(LineInput)
            self.__UpdateHelper('LineInputGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for LineInputGain')

    def __MatchLineInputGain(self, match, tag):
        qualifier = {'Line Input': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('LineInputGain', round(value, 1), qualifier)

    def SetLineInputMute(self, value, qualifier):
        MuteValues = {'Off': '0', 'On': '1', 'Toggle': '2'}
        LineInput = qualifier['Line Input']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'MUTE {0} L {1}'.format(LineInput, MuteValues[value])
            self.__SetHelper('LineInputMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for LineInputMute')

    def UpdateLineInputMute(self, value, qualifier):
        LineInput = qualifier['Line Input']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'MUTE {0} L'.format(LineInput)
            self.__UpdateHelper('LineInputMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for LineInputMute')

    def __MatchLineInputMute(self, match, tag):
        MuteStates = {b'1': 'On', b'0': 'Off'}
        qualifier = {'Line Input': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('LineInputMute', value, qualifier)

    def SetMacro(self, value, qualifier):
        if 1 <= value <= 255:
            CommandString = 'MACRO {0}'.format(value)
            self.__SetHelper('Macro', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for Macro')

    def UpdateMacro(self, value, qualifier):
        self.__UpdateHelper('Macro', 'MACRO', value, qualifier)

    def __MatchMacro(self, match, tag):
        value = int(match.group(1))
        self.WriteStatus('Macro', value, None)

    def SetMatrix(self, value, qualifier):
        SourceGroups = {
                        'Inputs': 'I',
                        'Mics': 'M',
                        'Processing': 'P',
                        'Expansion Bus': 'E',
                        'Line Inputs': 'L',
                        'Fader': 'F',
                        'Receive': 'R',
                        'VoIP Transmit': 'K',
                        'VoIP Receive': 'Z',
                        'USB Receive': 'U',
                        'Beamforming Mic Array': 'V'
                        }
        DestinationGroups = {
                            'PA Virtual Reference': 'H',
                            'Amplifier Ouput': 'J',
                            'Outputs': 'O',
                            'Processing': 'P',
                            'Expansion Bus': 'E',
                            'Fader': 'F',
                            'Transmit': 'T',
                            'Virtual Reference': 'B',
                            'VoIP Transmit': 'K',
                            'USB Transmit': 'D',
                             }
        MatrixValues = {
                        'Crosspoint off': '0',
                        'Crosspoint on': '1',
                        'Toggle': '2',
                        'Non-Gated': '3',
                        'Gated': '4',
                        'Pre-AEC': '5',
                        }

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        if not match(self.Channels, Source) or not match(self.Channels, Destination):
            print('Invalid Set Command for Matrix')
            return
        SourceGroup = SourceGroups[qualifier['Source Group']]
        DestinationGroup = DestinationGroups[qualifier['Destination Group']]
        CommandString = 'MTRX {0} {1} {2} {3} {4}'.format(Source, SourceGroup, Destination, DestinationGroup, MatrixValues[value])
        self.__SetHelper('Matrix', CommandString, value, qualifier)

    def UpdateMatrix(self, value, qualifier):
        SourceGroups = {
                        'Inputs': 'I',
                        'Mics': 'M',
                        'Processing': 'P',
                        'Expansion Bus': 'E',
                        'Line Inputs': 'L',
                        'Fader': 'F',
                        'Receive': 'R',
                        'VoIP Transmit': 'K',
                        'VoIP Receive': 'Z',
                        'USB Receive': 'U',
                        'Beamforming Mic Array': 'V'
                        }
        DestinationGroups = {
                            'PA Virtual Reference': 'H',
                            'Amplifier Ouput': 'J',
                            'Outputs': 'O',
                            'Processing': 'P',
                            'Expansion Bus': 'E',
                            'Fader': 'F',
                            'Transmit': 'T',
                            'Virtual Reference': 'B',
                            'VoIP Transmit': 'K',
                            'USB Transmit': 'D',
                             }
        Source = qualifier['Source']
        Destination = qualifier['Destination']
        if not match(self.Channels, Source) or not match(self.Channels, Destination):
            print('Invalid Update Command for Matrix')
            return
        SourceGroup = SourceGroups[qualifier['Source Group']]
        DestinationGroup = DestinationGroups[qualifier['Destination Group']]
        CommandString = 'MTRX {0} {1} {2} {3}'.format(Source, SourceGroup, Destination, DestinationGroup)
        self.__UpdateHelper('Matrix', CommandString, value, qualifier)

    def __MatchMatrix(self, match, tag):
        SourceGroups = {
                        b'I': 'Inputs',
                        b'M': 'Mics',
                        b'P': 'Processing',
                        b'E': 'Expansion Bus',
                        b'L': 'Line Inputs',
                        b'F': 'Fader',
                        b'R': 'Receive',
                        b'K': 'VoIP Transmit',
                        b'Z': 'VoIP Receive',
                        b'U': 'USB Receive',
                        b'V': 'Beamforming Mic Array'
                        }
        DestinationGroups = {
                            b'H': 'PA Virtual Reference',
                            b'J': 'Amplifier Ouput',
                            b'O': 'Outputs',
                            b'P': 'Processing',
                            b'E': 'Expansion Bus',
                            b'F': 'Fader',
                            b'T': 'Transmit',
                            b'B': 'Virtual Reference',
                            b'K': 'VoIP Transmit',
                            b'D': 'USB Transmit'
                            }
        MatrixStates = {
                        b'0': 'Crosspoint off',
                        b'1': 'Crosspoint on',
                        b'3': 'Non-Gated',
                        b'4': 'Gated',
                        b'5': 'Pre-AEC',
                        b'6': 'Routing Prohibited'
                        }
        Source = str(match.group(1).decode())
        SourceGroup = SourceGroups[match.group(2)]
        Destination = str(match.group(3).decode())
        DestinationGroup = DestinationGroups[match.group(4)]
        qualifier = {'Source': Source, 'Source Group': SourceGroup, 'Destination': Destination, 'Destination Group': DestinationGroup}
        value = MatrixStates[match.group(5)]
        self.WriteStatus('Matrix', value, qualifier)

    def SetMatrixLevel(self, value, qualifier):
        SourceGroups = {
                        'Inputs': 'I',
                        'Mics': 'M',
                        'Processing': 'P',
                        'Expansion Bus': 'E',
                        'Line Inputs': 'L',
                        'Fader': 'F',
                        'Receive': 'R',
                        'VoIP Transmit': 'K',
                        'VoIP Receive': 'Z',
                        'USB Receive': 'U',
                        'Beamforming Mic Array': 'V'
                        }
        DestinationGroups = {
                            'PA Virtual Reference': 'H',
                            'Amplifier Ouput': 'J',
                            'Outputs': 'O',
                            'Processing': 'P',
                            'Expansion Bus': 'E',
                            'Fader': 'F',
                            'Transmit': 'T',
                            'Virtual Reference': 'B',
                            'VoIP Transmit': 'K',
                            'USB Transmit': 'D',
                             }

        ValueConstraints = {
            'Min': -60,
            'Max': 12
            }

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        if not match(self.Channels, Source) or not match(self.Channels, Destination):
            print('Invalid Set Command for MatrixLevel')
            return
        SourceGroup = SourceGroups[qualifier['Source Group']]
        DestinationGroup = DestinationGroups[qualifier['Destination Group']]

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MatrixLevelCmdString = 'MTRXLVL {0} {1} {2} {3} {4:.2f} A'.format(Source, SourceGroup, Destination, DestinationGroup, value)
            self.__SetHelper('MatrixLevel', MatrixLevelCmdString, value, qualifier)
        else:
            print('Invalid Set Command for MatrixLevel')

    def UpdateMatrixLevel(self, value, qualifier):
        SourceGroups = {
                        'Inputs': 'I',
                        'Mics': 'M',
                        'Processing': 'P',
                        'Expansion Bus': 'E',
                        'Line Inputs': 'L',
                        'Fader': 'F',
                        'Receive': 'R',
                        'VoIP Transmit': 'K',
                        'VoIP Receive': 'Z',
                        'USB Receive': 'U',
                        'Beamforming Mic Array': 'V'
                        }
        DestinationGroups = {
                            'PA Virtual Reference': 'H',
                            'Amplifier Ouput': 'J',
                            'Outputs': 'O',
                            'Processing': 'P',
                            'Expansion Bus': 'E',
                            'Fader': 'F',
                            'Transmit': 'T',
                            'Virtual Reference': 'B',
                            'VoIP Transmit': 'K',
                            'USB Transmit': 'D',
                             }
        Source = qualifier['Source']
        Destination = qualifier['Destination']
        if not match(self.Channels, Source) or not match(self.Channels, Destination):
            print('Invalid Update Command for MatrixLevel')
            return
        SourceGroup = SourceGroups[qualifier['Source Group']]
        DestinationGroup = DestinationGroups[qualifier['Destination Group']]
        MatrixLevelCmdString = 'MTRXLVL {0} {1} {2} {3}'.format(Source, SourceGroup, Destination, DestinationGroup)
        self.__UpdateHelper('MatrixLevel', MatrixLevelCmdString, value, qualifier)

    def __MatchMatrixLevel(self, match, tag):
        SourceGroups = {
                        b'I': 'Inputs',
                        b'M': 'Mics',
                        b'P': 'Processing',
                        b'E': 'Expansion Bus',
                        b'L': 'Line Inputs',
                        b'F': 'Fader',
                        b'R': 'Receive',
                        b'K': 'VoIP Transmit',
                        b'Z': 'VoIP Receive',
                        b'U': 'USB Receive',
                        b'V': 'Beamforming Mic Array'
                        }
        DestinationGroups = {
                            b'H': 'PA Virtual Reference',
                            b'J': 'Amplifier Ouput',
                            b'O': 'Outputs',
                            b'P': 'Processing',
                            b'E': 'Expansion Bus',
                            b'F': 'Fader',
                            b'T': 'Transmit',
                            b'B': 'Virtual Reference',
                            b'K': 'VoIP Transmit',
                            b'D': 'USB Transmit'
                            }

        Source = match.group('inChannel').decode()
        SourceGroup = SourceGroups[match.group('inGroup')]
        Destination = match.group('outChannel').decode()
        DestinationGroup = DestinationGroups[match.group('outGroup')]
        qualifier = {'Source': Source, 'Source Group': SourceGroup, 'Destination': Destination, 'Destination Group': DestinationGroup}
        value = float(match.group('value').decode())
        self.WriteStatus('MatrixLevel', round(value, 1), qualifier)

    def SetMicGain(self, value, qualifier):
        Mic = qualifier['Mic']
        if -65.0 <= value <= 20.0 and self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'GAIN {0} M {1:0.1f} A'.format(Mic, value)
            self.__SetHelper('MicGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for MicGain')

    def UpdateMicGain(self, value, qualifier):
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'GAIN {0} M'.format(Mic)
            self.__UpdateHelper('MicGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for MicGain')

    def __MatchMicGain(self, match, tag):
        qualifier = {'Mic': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('MicGain', round(value, 1), qualifier)

    def SetMicMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'MUTE {0} M {1}'.format(Mic, MuteValues[value])
            self.__SetHelper('MicMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for MicMute')

    def UpdateMicMute(self, value, qualifier):
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'MUTE {0} M'.format(Mic)
            self.__UpdateHelper('MicMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for MicMute')

    def __MatchMicMute(self, match, tag):
        MuteStates = {b'1': 'On', b'0': 'Off'}
        qualifier = {'Mic': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('MicMute', value, qualifier)

    def SetOutputGain(self, value, qualifier):
        Output = qualifier['Output']
        if -65.0 <= value <= 20.0 and self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'GAIN {0} O {1:0.1f} A'.format(Output, value)
            self.__SetHelper('OutputGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for OutputGain')

    def UpdateOutputGain(self, value, qualifier):
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'GAIN {0} O'.format(Output)
            self.__UpdateHelper('OutputGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for OutputGain')

    def __MatchOutputGain(self, match, tag):
        qualifier = {'Output': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('OutputGain', round(value, 1), qualifier)

    def SetOutputMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'MUTE {0} O {1}'.format(Output, MuteValues[value])
            self.__SetHelper('OutputMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for OutputMute')

    def UpdateOutputMute(self, value, qualifier):
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'MUTE {0} O'.format(Output)
            self.__UpdateHelper('OutputMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for OutputMute')

    def __MatchOutputMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }
        qualifier = {'Output': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPhonebookAddEntryCommand(self, value, qualifier):
        SpeedDialStates = {
            'None': '0',
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
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20'
        }

        entryString = value
        speedDial = SpeedDialStates[qualifier['Speed Dial']]

        if entryString:
            matchCheck = match(self.PhonebookAddPattern, entryString)
            if matchCheck:
                PhonebookAddEntryCommandCmdString = 'PHONEBOOKADD {0} {1}'.format(speedDial, entryString)
                self.__SetHelper('PhonebookAddEntryCommand', PhonebookAddEntryCommandCmdString, value, qualifier)
            else:
                print('Invalid Set Command for PhonebookAddEntryCommand')
        else:
            print('Invalid Set Command for PhonebookAddEntryCommand')

    def UpdatePhonebookCount(self, value, qualifier):
        PhonebookCountCmdString = 'PHONEBOOKCNT'
        self.__UpdateHelper('PhonebookCount', PhonebookCountCmdString, value, qualifier)

    def __MatchPhonebookCount(self, match, tag):

        value = int(match.group(1).decode())
        self.PhonebookEntryCount = value
        self.WriteStatus('PhonebookCount', value, None)

    def SetPhonebookDeleteEntryCommand(self, value, qualifier):
        entryString = value
        if entryString:
            PhonebookDeleteEntryCommandCmdString = 'PHONEBOOKDEL {0}'.format(entryString)
            self.__SetHelper('PhonebookDeleteEntryCommand', PhonebookDeleteEntryCommandCmdString, value, qualifier)
        else:
            print('Invalid Set Command for PhonebookDeleteEntryCommand')

    def SetPhonebookNavigation(self, value, qualifier):
        StepStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        step = int(StepStates[qualifier['Step']])

        if value == 'Up':
            if self.PhonebookStartIndex - step >= 0:
                self.PhonebookStartIndex -= step
            else:
                self.PhonebookStartIndex = 0

        if value == 'Down':

            if self.PhonebookStartIndex + step <= self.PhonebookEntryCount - 1:
                self.PhonebookStartIndex += step
            else:
                self.PhonebookStartIndex = self.PhonebookEntryCount - 1

        writeIndex = 1
        for readIndex in range(self.PhonebookStartIndex, self.PhonebookEntryCount):
            entry = self.PhonebookList[readIndex]
            name = entry['name']
            number = entry['number']
            speed = entry['speed']
            if name and number and speed:
                label = '{0} : {1}'.format(name, number)
            else:
                label = ''
                speed = 'N/A'
            self.WriteStatus('PhonebookEntry', label, {'Index': str(writeIndex)})
            self.WriteStatus('PhonebookEntrySpeedDialValue', speed, {'Index': str(writeIndex)})
            writeIndex += 1
        else:
            while writeIndex <= self.MAX_PHONEBOOK_ENTRIES:
                self.WriteStatus('PhonebookEntry', '', {'Index': str(writeIndex)})
                self.WriteStatus('PhonebookEntrySpeedDialValue', 'N/A', {'Index': str(writeIndex)})
                writeIndex += 1

    def SetPhonebookRefresh(self, value, qualifier):
        count = self.PhonebookEntryCount

        if count == 0:
            for blankIndex in range(0, self.MAX_PHONEBOOK_ENTRIES):
                self.WriteStatus('PhonebookEntry', '', {'Index': str(blankIndex + 1)})
                self.WriteStatus('PhonebookEntrySpeedDialValue', 'N/A', {'Index': str(blankIndex + 1)})

                self.PhonebookList[blankIndex] = {'number': '', 'name': '', 'speed': 'N/A'}
        else:
            for index in range(0, count):
                PhonebookRefreshCmdString = 'PHONEBOOKREAD {0}'.format(index)
                self.__SetHelper('PhonebookRefresh', PhonebookRefreshCmdString, value, qualifier)
            else:
                index += 1
                while index < self.MAX_PHONEBOOK_ENTRIES:
                    self.WriteStatus('PhonebookEntry', '', {'Index': str(index + 1)})
                    self.WriteStatus('PhonebookEntrySpeedDialValue', 'N/A', {'Index': str(index + 1)})

                    self.PhonebookList[index] = {'number': '', 'name': '', 'speed': 'N/A'}
                    index += 1

    def __MatchPhonebookRefresh(self, match, tag):
        index = int(match.group('index').decode())        
        speed = match.group('speed').decode() 
        if speed == '0':
            speed = 'N/A'
        name = match.group('name').decode()
        number = match.group('number').decode()

        self.PhonebookList[index]['name'] = name
        self.PhonebookList[index]['number'] = number
        self.PhonebookList[index]['speed'] = speed
        self.PhonebookStartIndex = 0

        self.WriteStatus('PhonebookEntry', '{0} : {1}'.format(name, number), {'Index': str(index + 1)})

        self.WriteStatus('PhonebookEntrySpeedDialValue', speed, {'Index': str(index + 1)})

    def SetPhoneReceiveGain(self, value, qualifier):

        if -65.0 <= value <= 20.0:
            CommandString = 'GAIN 1 R {0:0.1f} A'.format(value)
            self.__SetHelper('PhoneReceiveGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for PhoneReceiveGain')

    def UpdatePhoneReceiveGain(self, value, qualifier):

        CommandString = 'GAIN 1 R'
        self.__UpdateHelper('PhoneReceiveGain', CommandString, value, qualifier)

    def __MatchPhoneReceiveGain(self, match, tag):
        value = float(match.group(2))
        self.WriteStatus('PhoneReceiveGain', round(value, 1), None)

    def SetPhoneReceiveMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }

        CommandString = 'MUTE 1 R {0}'.format(MuteValues[value])
        self.__SetHelper('PhoneReceiveMute', CommandString, value, qualifier)

    def UpdatePhoneReceiveMute(self, value, qualifier):

        CommandString = 'MUTE 1 R'
        self.__UpdateHelper('PhoneReceiveMute', CommandString, value, qualifier)

    def __MatchPhoneReceiveMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }

        value = MuteStates[match.group(1)]
        self.WriteStatus('PhoneReceiveMute', value, None)

    def SetPhoneTransmitGain(self, value, qualifier):
        if -65.0 <= value <= 20.0:
            CommandString = 'GAIN 1 T {0:0.1f} A'.format(value)
            self.__SetHelper('PhoneTransmitGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for PhoneTransmitGain')

    def UpdatePhoneTransmitGain(self, value, qualifier):

        CommandString = 'GAIN 1 T'
        self.__UpdateHelper('PhoneTransmitGain', CommandString, value, qualifier)

    def __MatchPhoneTransmitGain(self, match, tag):
        value = float(match.group(2))
        self.WriteStatus('PhoneTransmitGain', round(value, 1), None)

    def SetPhoneTransmitMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }

        CommandString = 'MUTE 1 T {0}'.format(MuteValues[value])
        self.__SetHelper('PhoneTransmitMute', CommandString, value, qualifier)

    def UpdatePhoneTransmitMute(self, value, qualifier):

        CommandString = 'MUTE 1 T'
        self.__UpdateHelper('PhoneTransmitMute', CommandString, value, qualifier)

    def __MatchPhoneTransmitMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }

        value = MuteStates[match.group(1)]
        self.WriteStatus('PhoneTransmitMute', value, None)

    def SetPreset(self, value, qualifier):
        PresetValues = {'Off': '0',
                        'Execute On': '1',
                        'Execute Off': '2'
                        }
        PresetNumber = qualifier['Preset Number']
        if 1 <= int(PresetNumber) <= 32:
            CommandString = 'PRESET {0} {1}'.format(PresetNumber, PresetValues[value])
            self.__SetHelper('Preset', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for Preset')

    def UpdatePreset(self, value, qualifier):
        PresetNumber = qualifier['Preset Number']
        if 1 <= int(PresetNumber) <= 32:
            CommandString = 'PRESET {0}'.format(PresetNumber)
            self.__UpdateHelper('Preset', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for Preset')

    def __MatchPreset(self, match, tag):

        PresetStates = {b'0': 'Off', b'1': 'Execute On', b'2': 'Execute Off'}
        qualifier = {'Preset Number': match.group(1).decode()}
        value = PresetStates[match.group(2)]
        self.WriteStatus('Preset', value, qualifier)

    def SetProcessingChannelGain(self, value, qualifier):
        ProcessingChannel = qualifier['Processing Channel']
        if -65.0 <= value <= 20.0 and ProcessingChannel in self.ProcessingChannels:
            CommandString = 'GAIN {0} P {1:0.1f} A'.format(ProcessingChannel, value)
            self.__SetHelper('ProcessingChannelGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for ProcessingChannelGain')

    def UpdateProcessingChannelGain(self, value, qualifier):
        ProcessingChannel = qualifier['Processing Channel']
        if ProcessingChannel in self.ProcessingChannels:
            CommandString = 'GAIN {0} P'.format(ProcessingChannel)
            self.__UpdateHelper('ProcessingChannelGain', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for ProcessingChannelGain')

    def __MatchProcessingChannelGain(self, match, tag):
        qualifier = {'Processing Channel': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('ProcessingChannelGain', round(value, 1), qualifier)

    def SetProcessingChannelMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }
        ProcessingChannel = qualifier['Processing Channel']
        if ProcessingChannel in self.ProcessingChannels:
            CommandString = 'MUTE {0} P {1}'.format(ProcessingChannel, MuteValues[value])
            self.__SetHelper('ProcessingChannelMute', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for ProcessingChannelMute')

    def UpdateProcessingChannelMute(self, value, qualifier):
        ProcessingChannel = qualifier['Processing Channel']
        if ProcessingChannel in self.ProcessingChannels:
            CommandString = 'MUTE {0} P'.format(ProcessingChannel)
            self.__UpdateHelper('ProcessingChannelMute', CommandString, value, qualifier)
        else:
            print('Invalid Update Command for ProcessingChannelMute')

    def __MatchProcessingChannelMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }
        qualifier = {'Processing Channel': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('ProcessingChannelMute', value, qualifier)

    def SetSafetyMute(self, value, qualifier):
        MuteValues = {'On': '1', 'Off': '0', 'Toggle': '2'}
        CommandString = 'SFTYMUTE {0}'.format(MuteValues[value])
        self.__SetHelper('SafetyMute', CommandString, value, qualifier)

    def UpdateSafetyMute(self, value, qualifier):
        self.__UpdateHelper('SafetyMute', 'SFTYMUTE', value, qualifier)

    def __MatchSafetyMute(self, match, tag):
        MuteStates = {b'1': 'On', b'0': 'Off'}
        value = MuteStates[match.group(1)]
        self.WriteStatus('SafetyMute', value, None)

    def SetSpeedDial(self, value, qualifier):
        if self.DeviceType == 'E':
            self.SetSpeedDialVoIP(value, qualifier)
        else:
            if 1 <= int(value) <= 20:
                CommandString = 'SPEEDDIAL 1 {0}'.format(value)
                self.__SetHelper('SpeedDial', CommandString, value, qualifier)
            else:
                print('Invalid Set Command for SpeedDial')

    def SetSpeedDialVoIP(self, value, qualifier):
        if 1 <= int(value) <= 20:
            CommandString = 'XSPEEDDIAL 1 Z {0}'.format(value)
            self.__SetHelper('SpeedDial', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for SpeedDial')

    def SetStringExecution(self, value, qualifier):
        if 0 <= int(value) <= 7:
            CommandString = 'STRING {0}'.format(value)
            self.__SetHelper('StringExecution', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for StringExecution')

    def UpdateStringExecution(self, value, qualifier):
        self.__UpdateHelper('StringExecution', 'STRING', value, qualifier)

    def __MatchStringExecution(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('StringExecution', value, None)

    def SetRingerEnable(self, value, qualifier):
        RingerEnableValues = {
                              'On': '1',
                              'Off': '0',
                              'Toggle': '2'
                              }
        CommandString = 'RINGEREN 1 {0}'.format(RingerEnableValues[value])
        self.__SetHelper('RingerEnable', CommandString, value, qualifier)

    def UpdateRingerEnable(self, value, qualifier):
        CommandString = 'RINGEREN 1'

        self.__UpdateHelper('RingerEnable', CommandString, value, qualifier)

    def __MatchRingerEnable(self, match, tag):
        RingerEnableStates = {b'1': 'On', b'0': 'Off'}
        value = RingerEnableStates[match.group(1)]
        self.WriteStatus('RingerEnable', value, None)

    def SetRingerVoIPEnable(self, value, qualifier):
        RingerVoIPEnableValues = {
                              'On': '1',
                              'Off': '0',
                              'Toggle': '2'
                              }
        CommandString = 'XRINGEREN 1 Z {0}'.format(RingerVoIPEnableValues[value])
        self.__SetHelper('RingerVoIPEnable', CommandString, value, qualifier)

    def UpdateRingerVoIPEnable(self, value, qualifier):
        CommandString = 'XRINGEREN 1 Z'

        self.__UpdateHelper('RingerVoIPEnable', CommandString, value, qualifier)

    def __MatchRingerVoIPEnable(self, match, tag):
        RingerVoIPEnableStates = {b'1': 'On', b'0': 'Off'}
        value = RingerVoIPEnableStates[match.group(1)]
        self.WriteStatus('RingerVoIPEnable', value, None)

    def SetVoIPReceiveGain(self, value, qualifier):

        if -65.0 <= value <= 20.0:
            CommandString = 'GAIN 1 Z {0:0.1f} A'.format(value)
            self.__SetHelper('VoIPReceiveGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for VoIPReceiveGain')

    def UpdateVoIPReceiveGain(self, value, qualifier):

        CommandString = 'GAIN 1 Z'
        self.__UpdateHelper('VoIPReceiveGain', CommandString, value, qualifier)

    def __MatchVoIPReceiveGain(self, match, tag):
        value = float(match.group(2))
        self.WriteStatus('VoIPReceiveGain', round(value, 1), None)

    def SetVoIPReceiveMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }

        CommandString = 'MUTE 1 Z {0}'.format(MuteValues[value])
        self.__SetHelper('VoIPReceiveMute', CommandString, value, qualifier)

    def UpdateVoIPReceiveMute(self, value, qualifier):

        CommandString = 'MUTE 1 Z'
        self.__UpdateHelper('VoIPReceiveMute', CommandString, value, qualifier)

    def __MatchVoIPReceiveMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }

        value = MuteStates[match.group(1)]
        self.WriteStatus('VoIPReceiveMute', value, None)

    def SetVoIPTransmitGain(self, value, qualifier):

        if -65.0 <= value <= 20.0:
            CommandString = 'GAIN 1 K {0:0.1f} A'.format(value)
            self.__SetHelper('VoIPTransmitGain', CommandString, value, qualifier)
        else:
            print('Invalid Set Command for VoIPTransmitGain')

    def UpdateVoIPTransmitGain(self, value, qualifier):

        CommandString = 'GAIN 1 K'
        self.__UpdateHelper('VoIPTransmitGain', CommandString, value, qualifier)

    def __MatchVoIPTransmitGain(self, match, tag):

        value = float(match.group(2))
        self.WriteStatus('VoIPTransmitGain', round(value, 1), None)

    def SetVoIPTransmitMute(self, value, qualifier):
        MuteValues = {
                      'Off': '0',
                      'On': '1',
                      'Toggle': '2'
                      }

        CommandString = 'MUTE 1 K {0}'.format(MuteValues[value])
        self.__SetHelper('VoIPTransmitMute', CommandString, value, qualifier)

    def UpdateVoIPTransmitMute(self, value, qualifier):

        CommandString = 'MUTE 1 K'
        self.__UpdateHelper('VoIPTransmitMute', CommandString, value, qualifier)

    def __MatchVoIPTransmitMute(self, match, tag):
        MuteStates = {
                      b'1': 'On',
                      b'0': 'Off'
                      }

        value = MuteStates[match.group(1)]
        self.WriteStatus('VoIPTransmitMute', value, None)

    def __MatchError(self, match, tag):

        print('ERROR: ' + match.group(1).decode())

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send('#{0}{1} {2}\r'.format(self.DeviceType, self._DeviceID, commandstring))
        
    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Authenticated:
            if self.Unidirectional == 'True':
                print('Inappropriate Command ', command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False
    
                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                    
                if self.SerialEchoEnabled:
                    self.Send('#{0}{1} SERECHO 1\r'.format(self.DeviceType, self._DeviceID))
                self.Send(('#{0}{1} {2}\r'.format(self.DeviceType, self._DeviceID, commandstring)).encode())                       

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SerialEchoEnabled = False

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.SerialEchoEnabled = True
        self.PhonebookEntryCount = self.MAX_PHONEBOOK_ENTRIES
        self.Authenticated = False

    def clr1_25_154_840T(self):

        self.DeviceType = '3'
        self.Inputs = (1, 8)
        self.Fader = (1, 4)
        self.LineInputs = (5, 8)
        self.Mics = (1, 4)
        self.Outputs = (1, 9)
        self.ProcessingChannels = 'ABCDEFGH'
        self.SpeakerOut = '9'     
 
    def clr1_25_154_880(self):

        self.DeviceType = '1'
        self.Inputs = (1, 12)
        self.Fader = (1, 4)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 12)
        self.ProcessingChannels = 'ABCDEFGH'

    def clr1_25_154_880T(self):

        self.DeviceType = 'D'
        self.Inputs = (1, 12)
        self.Fader = (1, 4)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 13)
        self.ProcessingChannels = 'ABCDEFGH'
        self.SpeakerOut = '13'

    def clr1_25_154_880TA(self):

        self.DeviceType = 'H'
        self.Inputs = (1, 12)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 8)
        self.AmplifierOutput = (1,4)
        self.ProcessingChannels = 'ABCDEFGH'

    def clr1_25_154_8i(self):

        self.DeviceType = 'A'
        self.Inputs = (1, 12)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 8)
        self.ProcessingChannels = 'ABCDEFGH'

    def clr1_25_154_SR1212(self):

        self.DeviceType = 'G'
        self.Inputs = (1, 12)
        self.Fader = (1, 4)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 12)
        self.ProcessingChannels = 'ABCDEFGH'

    def clr1_25_154_SR1212A(self):

        self.DeviceType = 'I'
        self.Inputs = (1, 12)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 12)
        self.AmplifierOutput = (1,4)
        self.ProcessingChannels = 'ABCDEFGH'
        self.PAVirtualReference = (1,4)

    def clr1_25_154_TH20(self):

        self.DeviceType = '2'
        self.Inputs = (1, 2)
        self.LineInputs = (1, 2)
        self.Outputs = (1, 2)

    def clr1_25_154_VH20(self):

        self.DeviceType = 'E'
        self.Inputs = (1, 2)
        self.LineInputs = (1, 2)
        self.Outputs = (1, 2)

    def clr1_25_154_Beam(self):

        self.DeviceType = 'N'


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

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg, command=None):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
        
        
    # Check incoming unsolicited data to see if it matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True      

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)                
        DeviceClass.__init__(self, Model)          
        self.Authenticated = True
        self.ConnectionType = 'Serial'
        
class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        DeviceClass.__init__(self, Model)
        self.ConnectionType = 'Ethernet' 
            
        
