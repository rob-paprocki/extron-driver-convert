from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, match, escape, search
from struct import pack, unpack
from binascii import hexlify, unhexlify
import time
import copy

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
            'AutoAnswer': {'Parameters': ['HiQAddress'], 'Status': {}},
            'CallStatus': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'DTMF': {'Parameters': ['HiQAddress'], 'Status': {}},
            'Gain': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'Hook': {'Parameters': ['HiQAddress'], 'Status': {}},
            'LogicSource': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'LogicSourceSelect': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'LogicValue': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'Mute': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'Preset': {'Parameters': ['Type'], 'Status': {}},
            'Source': {'Parameters': ['HiQAddress', 'ID'], 'Status': {}},
            'VoIPAutoAnswer': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
            'VoIPCallerID': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
            'VoIPDTMF': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
            'VoIPHoldStatus': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
            'VoIPHook': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
            'VoIPHookStatus': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
            'VoIPRingingStatus': {'Parameters': ['HiQAddress', 'Line'], 'Status': {}},
        }

        self.TIRedialString = ''
        self.VoIPRedialString = {'1': '', '2': ''}
        self.HiQLookup = {}

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'Off': 0,
            '1 Ring': 1,
            '2 Rings': 2,
            '3 Rings': 3,
            '4 Rings': 4,
            '5 Rings': 5,
            '6 Rings': 6,
            '7 Rings': 7,
            '8 Rings': 8,
            '9 Rings': 9,
            '10 Rings': 10,
        }
        
        if qualifier['HiQAddress'] and value in ValueStateValues:
            key = 'AutoAnswer_{}'.format(qualifier['HiQAddress'].lower())
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']  # ex: {AutoAnswer_0x2f7203000002: 0x2F7203000002}

            HiQ = HiQMsg(qualifier['HiQAddress'], 124, 'Set')
            if HiQ:
                HiQ.setValue(ValueStateValues[value])
                self.__SetHelper('AutoAnswer', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetAutoAnswer')
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        if qualifier['HiQAddress']:
            key = 'AutoAnswer_{}'.format(qualifier['HiQAddress'].lower())
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], 124, 'Subscribe')
            if HiQ:
                self.__UpdateHelper('AutoAnswer', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateAutoAnswer')
        else:
            self.Discard('Invalid Command for UpdateAutoAnswer')

    def UpdateCallStatus(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'CallStatus_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('CallStatus', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateCallStatus')
        else:
            self.Discard('Invalid Command for UpdateCallStatus')

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': 104,
            '1': 105,
            '2': 106,
            '3': 107,
            '4': 108,
            '5': 109,
            '6': 110,
            '7': 111,
            '8': 112,
            '9': 113,
            '#': 114,
            '*': 115,
            ',': 116,
            '+': 117,
            'Clear': 118,
            'Delete': 119,
        }

        if qualifier['HiQAddress'] and value in ValueStateValues:
            HiQ = HiQMsg(qualifier['HiQAddress'], ValueStateValues[value], 'Set')
            if HiQ:
                HiQ.setValue(1)
                self.__SetHelper('DTMF', HiQ, value, qualifier)
                HiQ.setValue(0)
                self.__SetHelper('DTMF', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTMF')
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetGain(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535 and 0 <= value <= 100:
            key = 'Gain_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Set Percent')
            if HiQ:
                HiQ.setValue(value)
                self.__SetHelper('Gain', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetGain')
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'Gain_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe Percent')
            if HiQ:
                self.__UpdateHelper('Gain', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateGain')
        else:
            self.Discard('Invalid Command for UpdateGain')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'On': 0,
            'Off': 1,
            'Redial': 120,
            'Flash': 123
        }

        if qualifier['HiQAddress'] and (value in ValueStateValues or value == 'Clear Redial'):
            TIDialCmdString = ''
            key = 'Hook_{}'.format(qualifier['HiQAddress'].lower())
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            if value in ['Off', 'Redial']:
                if value == 'Redial':
                    TIDialCmdString = self.TIRedialString # get last number dialed
                else: # Off
                    try:
                        TIDialCmdString = qualifier['Number']
                        if TIDialCmdString: # if number exists
                            self.TIRedialString = TIDialCmdString # save it for redial
                    except KeyError:
                        pass # Hook Off qualifier is optional

                if TIDialCmdString: # if number exists
                    self.SetDTMF('Clear', qualifier) # clear device dial string
                    for i in TIDialCmdString: # send each digit in dial string to device 200 ms apart
                        # begin command pacing logic
                        refTime = time.monotonic() # define reference time
                        while True:
                            ctime = time.monotonic()
                            if ctime - refTime > 0.2: # if current time minus reference time is greater than 200 ms
                                break
                        self.SetDTMF(i, qualifier) # send digit to device
                    value = 'Off' # hardcode to Off after a redial

            # send command to device
            if value in ['On', 'Off']:
                HiQ = HiQMsg(qualifier['HiQAddress'], 127, 'Set')
                if HiQ:
                    HiQ.setValue(ValueStateValues[value])
                    self.__SetHelper('Hook', HiQ, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetHook')
            elif value in ['Flash', 'Redial']:
                HiQ = HiQMsg(qualifier['HiQAddress'], ValueStateValues[value], 'Set')
                if HiQ:
                    HiQ.setValue(1)
                    self.__SetHelper('Hook', HiQ, value, qualifier)
                    HiQ.setValue(0)
                    self.__SetHelper('Hook', HiQ, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetHook')
            else: # Clear Redial
                self.TIRedialString = '' # clear last number dialed
        else:
            self.Discard('Invalid Command for SetHook')

    def UpdateHook(self, value, qualifier):

        if qualifier['HiQAddress']:
            key = 'Hook_{}'.format(qualifier['HiQAddress'].lower())
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], 127, 'Subscribe')
            if HiQ:
                self.__UpdateHelper('Hook', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateHook')
        else:
            self.Discard('Invalid Command for UpdateHook')

    def SetLogicSource(self, value, qualifier):

        ValueStateValues = {
            '0': 0,
            '1': 1
        }

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535 and value in ValueStateValues:
            key = 'LogicSource_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Set')
            if HiQ:
                HiQ.setValue(ValueStateValues[value])
                self.__SetHelper('LogicSource', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLogicSource')
        else:
            self.Discard('Invalid Command for SetLogicSource')

    def UpdateLogicSource(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'LogicSource_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('LogicSource', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateLogicSource')
        else:
            self.Discard('Invalid Command for UpdateLogicSource')

    def SetLogicSourceSelect(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535 and 0 <= value <= 32:
            key = 'LogicSourceSelect_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Set')
            if HiQ:
                HiQ.setValue(value)
                self.__SetHelper('LogicSourceSelect', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLogicSourceSelect')
        else:
            self.Discard('Invalid Command for SetLogicSourceSelect')

    def UpdateLogicSourceSelect(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'LogicSourceSelect_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('LogicSourceSelect', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateLogicSourceSelect')
        else:
            self.Discard('Invalid Command for UpdateLogicSourceSelect')

    def SetLogicValue(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535 and value:
            key = 'LogicValue_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Set')
            if HiQ:
                HiQ.setValue(value)
                self.__SetHelper('LogicValue', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLogicValue')
        else:
            self.Discard('Invalid Command for SetLogicValue')

    def UpdateLogicValue(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'LogicValue_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('LogicValue', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateLogicValue')
        else:
            self.Discard('Invalid Command for UpdateLogicValue')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535 and value in ValueStateValues:
            key = 'Mute_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Set')
            if HiQ:
                HiQ.setValue(ValueStateValues[value])
                self.__SetHelper('Mute', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMute')
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'Mute_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('Mute', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateMute')
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Venue': 'Venue Preset Recall',
            'Param': 'Param Preset Recall'
        }

        if qualifier['Type'] in TypeStates and 0 <= value <= 65535:
            HiQ = HiQMsg(None, None, TypeStates[qualifier['Type']])
            if HiQ:
                HiQ.setValue(value)
                self.__SetHelper('Preset', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPreset')
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetSource(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535 and 0 <= value <= 128:
            key = 'Source_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Set')
            if HiQ:
                HiQ.setValue(value)
                self.__SetHelper('Source', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetSource')
        else:
            self.Discard('Invalid Command for SetSource')

    def UpdateSource(self, value, qualifier):

        if qualifier['HiQAddress'] and 0 <= qualifier['ID'] <= 65535:
            key = 'Source_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['ID'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], qualifier['ID'], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('Source', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateSource')
        else:
            self.Discard('Invalid Command for UpdateSource')

    def SetVoIPAutoAnswer(self, value, qualifier):

        LineStates = {
            '1': 0x155,
            '2': 0x1B9
        }

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates and value in ValueStateValues:
            key = 'VoIPAutoAnswer_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['Line'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']], 'Set')
            if HiQ:
                HiQ.setValue(ValueStateValues[value])
                self.__SetHelper('VoIPAutoAnswer', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVoIPAutoAnswer')
        else:
            self.Discard('Invalid Command for SetVoIPAutoAnswer')

    def UpdateVoIPAutoAnswer(self, value, qualifier):

        LineStates = {
            '1': 0x155,
            '2': 0x1B9
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates:
            key = 'VoIPAutoAnswer_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['Line'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('VoIPAutoAnswer', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateVoIPAutoAnswer')
        else:
            self.Discard('Invalid Command for UpdateVoIPAutoAnswer')

    def SetVoIPDTMF(self, value, qualifier):

        LineStates = {
            '1': 0,
            '2': 1
        }

        ValueStateValues = {
            '0': [0x172, 0x1D6],
            '1': [0x173, 0x1D7],
            '2': [0x174, 0x1D8],
            '3': [0x175, 0x1D9],
            '4': [0x176, 0x1DA],
            '5': [0x177, 0x1DB],
            '6': [0x178, 0x1DC],
            '7': [0x179, 0x1DD],
            '8': [0x17A, 0x1DE],
            '9': [0x17B, 0x1DF],
            '#': [0x17C, 0x1E0],
            '*': [0x17D, 0x1E1],
            ',': [0x17E, 0x1E2],
            'Clear': [0x180, 0x1E4],
            'Delete': [0x181, 0x1E5]
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates and value in ValueStateValues:
            HiQ = HiQMsg(qualifier['HiQAddress'], ValueStateValues[value][LineStates[qualifier['Line']]], 'Set')
            if HiQ:
                HiQ.setValue(1)
                self.__SetHelper('VoIPDTMF', HiQ, value, qualifier)
                HiQ.setValue(0)
                self.__SetHelper('VoIPDTMF', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVoIPDTMF')
        else:
            self.Discard('Invalid Command for SetVoIPDTMF')

    def UpdateVoIPHoldStatus(self, value, qualifier):

        LineStates = {
            '1': 0x189,
            '2': 0x1ED
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates:
            key = 'VoIPHoldStatus_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['Line'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('VoIPHoldStatus', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateVoIPHoldStatus')
        else:
            self.Discard('Invalid Command for UpdateVoIPHoldStatus')

    def SetVoIPHook(self, value, qualifier):

        LineStates = {
            '1': 0,
            '2': 1
        }

        ValueStateValues = {
            'Pick Up/Hang Up': [0x182, 0x1E6],
            'Dial':            [0x182, 0x1E6],  # same as Pick Up/Hang Up values
            'Redial':          [0x183, 0x1E7],
            'Hold':            [0x184, 0x1E8],
            'Reject':          [0x17F, 0x1E3]
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates and (value in ValueStateValues or value == 'Clear Redial'):
            if value in ['Dial', 'Redial']:
                if value == 'Redial':
                    VoIPDialCmdString = self.VoIPRedialString[qualifier['Line']] # get last number dialed
                else: # Dial
                    VoIPDialCmdString = qualifier['Number']
                    if VoIPDialCmdString: # if number exists
                        self.VoIPRedialString[qualifier['Line']] = VoIPDialCmdString # save it for redial
                        
                if VoIPDialCmdString:  # if number exists
                    VoIPDialCmdString = VoIPDialCmdString.replace('.','*')
                    self.SetVoIPDTMF('Clear', qualifier) # clear device dial string
                    for i in VoIPDialCmdString: # send each digit in dial string to device 200 ms apart
                        # begin command pacing logic
                        refTime = time.monotonic() # define reference time
                        while True:
                            ctime = time.monotonic()
                            if ctime - refTime > 0.2: # if current time minus reference time is greater than 200 ms
                                break
                        self.SetVoIPDTMF(i, qualifier) # send digit to device
                else:
                    self.Discard('Invalid Command for SetVoIPHook')
                    return # exit method w/o sending command to device

            # send command to device
            if value in ValueStateValues:
                HiQ = HiQMsg(qualifier['HiQAddress'], ValueStateValues[value][LineStates[qualifier['Line']]], 'Set')
                if HiQ:
                    HiQ.setValue(1)
                    self.__SetHelper('VoIPHook', HiQ, value, qualifier)
                    HiQ.setValue(0)
                    self.__SetHelper('VoIPHook', HiQ, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetVoIPHook')
            else: # Clear Redial
                self.VoIPRedialString[qualifier['Line']] = '' # clear last number dialed
        else:
            self.Discard('Invalid Command for SetVoIPHook')

    def UpdateVoIPHookStatus(self, value, qualifier):

        LineStates = {
            '1': 0x188,
            '2': 0x1EC
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates:
            key = 'VoIPHookStatus_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['Line'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('VoIPHookStatus', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateVoIPHookStatus')
        else:
            self.Discard('Invalid Command for UpdateVoIPHookStatus')

    def UpdateVoIPRingingStatus(self, value, qualifier):

        LineStates = {
            '1': 0x187,
            '2': 0x1EB
        }

        if qualifier['HiQAddress'] and qualifier['Line'] in LineStates:
            key = 'VoIPRingingStatus_{}_{}'.format(qualifier['HiQAddress'].lower(), qualifier['Line'])
            if key not in self.HiQLookup:
                self.HiQLookup[key] = qualifier['HiQAddress']

            HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']], 'Subscribe')
            if HiQ:
                self.__UpdateHelper('VoIPRingingStatus', HiQ, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateVoIPRingingStatus')
        else:
            self.Discard('Invalid Command for UpdateVoIPRingingStatus')
    
    def WriteAutoAnswer(self, value, qualifier):
        ValueStateValues = {
            0: 'Off',
            1: '1 Ring',
            2: '2 Rings',
            3: '3 Rings',
            4: '4 Rings',
            5: '5 Rings',
            6: '6 Rings',
            7: '7 Rings',
            8: '8 Rings',
            9: '9 Rings',
            10: '10 Rings',
        }

        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = ValueStateValues[value]
        self.WriteStatus('AutoAnswer', value, qualifier)

    def WriteCallStatus(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {1: 'Incoming Call', 0: 'Idle'}[value]
            self.WriteStatus('CallStatus', value, qualifier)

    def WriteGain(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        self.WriteStatus('Gain', value, qualifier)

    def WriteHook(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {1: 'On', 0: 'Off'}[value]
        self.WriteStatus('Hook', value, qualifier)

    def WriteLogicSource(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {0: '0', 1: '1'}[value]
        self.WriteStatus('LogicSource', value, qualifier)

    def WriteLogicSourceSelect(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        self.WriteStatus('LogicSourceSelect', value, qualifier)

    def WriteLogicValue(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        self.WriteStatus('LogicValue', value, qualifier)

    def WriteMute(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {1: 'On', 0: 'Off'}[value]
        self.WriteStatus('Mute', value, qualifier)

    def WriteSource(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        self.WriteStatus('Source', value, qualifier)

    def WriteVoIPAutoAnswer(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {1: 'On', 0: 'Off'}[value]
        self.WriteStatus('VoIPAutoAnswer', value, qualifier)

    def WriteVoIPHoldStatus(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {0: 'Not on Hold', 1: 'On Hold'}[value]
        self.WriteStatus('VoIPHoldStatus', value, qualifier)

    def WriteVoIPHookStatus(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {0: 'On', 1: 'Off'}[value]
        self.WriteStatus('VoIPHookStatus', value, qualifier)

    def WriteVoIPRingingStatus(self, value, qualifier):
        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        if isinstance(value, int):
            value = {1: 'Ringing', 0: 'Not Ringing'}[value]
        self.WriteStatus('VoIPRingingStatus', value, qualifier)

        if value == 'Ringing':
            LineStates = {
                '1': 0x18A,
                '2': 0x1EE
            }
            HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']],'Subscribe')
            if HiQ:
                self.__UpdateHelper('VoIPCallerID', HiQ, value, qualifier)

    def WriteVoIPCallerID(self, value, qualifier):
        LineStates = {
            '1': 0x18A,
            '2': 0x1EE
        }

        qualifier['HiQAddress'] = qualifier['HiQAddress'].lower()
        self.WriteStatus('VoIPCallerID', value, qualifier)
        HiQ = HiQMsg(qualifier['HiQAddress'], LineStates[qualifier['Line']], 'Unsubscribe')
        if HiQ:
            self.Send(HiQ.encodeMessage())
            
    def __MatchAll(self, match, tag):

        Statuses = {
            'AutoAnswer'       : self.WriteAutoAnswer,
            'CallStatus'       : self.WriteCallStatus,
            'Gain'             : self.WriteGain,
            'Hook'             : self.WriteHook,
            'LogicSource'      : self.WriteLogicSource,
            'LogicSourceSelect': self.WriteLogicSourceSelect,
            'LogicValue'       : self.WriteLogicValue,
            'Mute'             : self.WriteMute,
            'Source'           : self.WriteSource,
            'VoIPAutoAnswer'   : self.WriteVoIPAutoAnswer,
            'VoIPHoldStatus'   : self.WriteVoIPHoldStatus,
            'VoIPHookStatus'   : self.WriteVoIPHookStatus,
            'VoIPRingingStatus': self.WriteVoIPRingingStatus,
            'VoIPCallerID'     : self.WriteVoIPCallerID
        }

        if tag in Statuses:
            Status = Statuses[tag]
            HiQ = HiQMsg(Message=match.group(0))
            if tag in ['AutoAnswer', 'Hook']:
                qualifier = {'HiQAddress': HiQ.getAddress()}
            elif tag in ['VoIPAutoAnswer', 'VoIPHoldStatus', 'VoIPHookStatus', 'VoIPRingingStatus', 'VoIPCallerID']:
                line = '1' if HiQ.getSVID() in [0x155, 0x189, 0x188, 0x187, 0x18A] else '2'
                qualifier = {'HiQAddress': HiQ.getAddress(), 'Line': line}
            else:
                qualifier = {'HiQAddress': HiQ.getAddress(), 'ID': HiQ.getSVID()}

            if tag == 'LogicValue':
                Status(HiQ.getValue(fourByte=True), qualifier)
            else:
                Status(HiQ.getValue(), qualifier)
        
    def __SetHelper(self, command, HiQ, value, qualifier):
        self.Debug = True
        self.Send(HiQ.encodeMessage())
            
    def __UpdateHelper(self, command, HiQ, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if command == 'VoIPCallerID':
                ReturnType = 'Set String'
            else:
                ReturnType = 'Set Percent' if command == 'Gain' else 'Set'
            if command == 'VoIPCallerID':
                self.RemoveMatchString(compile(b'\x02' + \
                                                HiQ.Types[ReturnType] + \
                                                HiQ.getAddress('REGEX') + \
                                                HiQ.getSVID('REGEX') + \
                                                b'[^\x03]+\x03'))
            self.AddMatchString(compile(b'\x02' + \
                                        HiQ.Types[ReturnType] + \
                                        HiQ.getAddress('REGEX') + \
                                        HiQ.getSVID('REGEX') + \
                                        b'[^\x03]+\x03'), self.__MatchAll, command)
            self.Send(HiQ.encodeMessage())

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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        # check incoming data if it matched any expected data from device module
        tempList = copy.copy(self.__matchStringDict) # prevents RuntimeError due to RemoveMatchString
        for regexString, CurrentMatch in tempList.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
    
    def RemoveMatchString(self, regex_string):
        if regex_string in self.__matchStringDict:
            del self.__matchStringDict[regex_string]


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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


class HiQMsg(object):

    reAddress = compile(r'0x[0-9a-f]{12}')

    Types = {
        'Set'                : b'\x88',
        'Subscribe'          : b'\x89',
        'Unsubscribe'        : b'\x8A',
        'Venue Preset Recall': b'\x8B',
        'Param Preset Recall': b'\x8C', 
        'Set Percent'        : b'\x8D',
        'Subscribe Percent'  : b'\x8E',
        'Unsubscribe Percent': b'\x8F',
        'Bump Percent'       : b'\x90',
        'Set String'         : b'\x91' # VoIP Caller ID
        }

    def __init__(self, Address=None, SVID=None, Type=None, Message=None):
        if Address:
            Address = Address.lower()
            if self.reAddress.match(Address):
                self.__address = bytes.fromhex(Address[2:])
            else:
                raise ValueError('UserInput ' + Address)
                return None
        else:
            self.__address = None
        
        if SVID:
            if 0 <= SVID <= 65535:
                self.__svid = SVID
            else:
                raise ValueError('UserInput ' + str(SVID))
                return None
        else:
            self.__svid = 0

        if Type:
            if Type in self.Types:
                self.__type = self.Types[Type]
            else:
                return None
        else:
            self.__type = None

        self.setValue(0)

        if Message:
            self.decodeMessage(Message)

    def getAddress(self, Format='ASCII'):
        if Format == 'BINARY':
            return self.escape(self.__address)
        elif Format == 'ASCII':
            return '0x' + ''.join("%.2x"%(byte) for byte in self.__address)
        elif Format == 'REGEX':
            return escape(self.getAddress('BINARY'))
        else:
            return None

    def getSVID(self, Format=None):
        if Format == 'BINARY':
            return self.escape(self.__svid.to_bytes(2, byteorder='big'))
        elif Format == 'REGEX':
            return escape(self.getSVID('BINARY'))
        else:
            return self.__svid
    
    LogicValues = compile('0x[0-9a-fA-F]{8}')    
       
    def setValue(self, value):
        try:
            if 0 <= value <= 65535:
                if self.__type in [self.Types['Set Percent'], self.Types['Subscribe Percent']]:
                    self.__value = pack('>BBH', 0x00, value, 0x0000)
                elif self.__type in [self.Types['Set'], self.Types['Subscribe'], self.Types['Unsubscribe']]:
                    self.__value = pack('>HBB', 0x0000, 0x00, value)
                elif self.__type in [self.Types['Venue Preset Recall'], self.Types['Param Preset Recall']]:
                    self.__value = pack('>BBH', 0x00, 0x00, value)
            else:
                raise ValueError('Out of range: ' + str(value))
        except TypeError:
            if isinstance(value, str) and match(self.LogicValues, value):
                self.__value = unhexlify(value[2:])
            else:
                raise ValueError('Invalid input: ' + str(value))

    def getValue(self, fourByte=False):
        if fourByte:
            return '0x' + hexlify(self.__value).decode('iso-8859-1').upper()
        else:
            if self.__type == self.Types['Set Percent']:
                return unpack('>BBH', self.__value)[1]
            elif self.__type == self.Types['Set']:
                return unpack('>HBB', self.__value)[2]
            elif self.__type == self.Types['Set String']: # VoIP Caller ID
                if self.__value.decode('iso-8859-1')[1] == '\x00': # if no name exists
                    return 'Unknown'
                else:
                    return self.__value.decode('iso-8859-1')[2:-1]

    def escape(self, m):
        M = b''
        Escaped = {
            0x02: b'\x1B\x82', 
            0x03: b'\x1B\x83', 
            0x06: b'\x1B\x86', 
            0x15: b'\x1B\x95', 
            0x1b: b'\x1B\x9B'
            }
        for byte in m:
            if byte in Escaped:
                M += Escaped[byte]
            else:
                M += byte.to_bytes(1, byteorder='big')
        return M

    def unescape(self, m):
        M = b''
        Unescaped = {
            b'\x1B\x82': 0x02, 
            b'\x1B\x83': 0x03, 
            b'\x1B\x86': 0x06, 
            b'\x1B\x95': 0x15, 
            b'\x1B\x9B': 0x1b 
            }
        skip = False
        for byte in range(len(m)):
            if skip:
                skip = False
            else:
                if m[byte] == 0x1b:
                    M += Unescaped[m[byte:byte + 2]].to_bytes(1, byteorder='big')
                    skip = True
                else:
                    M += m[byte].to_bytes(1, byteorder='big')
        return M
        
    def encodeMessage(self):
        if self.__type in [self.Types['Venue Preset Recall'], self.Types['Param Preset Recall']]:
            m = pack('>1s4s',
                     self.__type,
                     self.__value
                     )
        else:
            m = pack('>1s6sH{0}s'.format(len(self.__value)),
                     self.__type,
                     self.__address,
                     self.__svid,
                     self.__value
                     )
        checksum = 0
        for byte in m:
            checksum ^= byte
        m += checksum.to_bytes(1, byteorder='big')
        return b'\x02' + self.escape(m) + b'\x03'

    def decodeMessage(self, m):
        M = self.unescape(m[1:-1])[:-1]
        self.__type, self.__address, self.__svid, self.__value = unpack('>1s6sH{0}s'.format(len(M[9:])), M)
