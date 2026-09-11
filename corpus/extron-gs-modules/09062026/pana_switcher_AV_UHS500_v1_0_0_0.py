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
            'AutoTransitionTime': {'Parameters':['Source'], 'Status': {}},
            'AuxTransition': {'Parameters':['Source','Effect'], 'Status': {}},
            'BusSelection': {'Parameters':['Bus'], 'Status': {}},
            'BusTransitionTime': {'Parameters':['Bus','Mode'], 'Status': {}},
            'CutTransition': {'Parameters':['Source'], 'Status': {}},
            'KeySignalCoupling': { 'Status': {}},
            'TransitionPattern': {'Parameters':['Type'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02ATIM:(0[014-8]):(\d{1,3})\x03'), self.__MatchAutoTransitionTime, None)
            self.AddMatchString(re.compile(b'\x02ABSC:(\d{1,3}):(\d{1,3})\x03'), self.__MatchBusSelection, None)
            self.AddMatchString(re.compile(b'\x02ABTI:(0[12]):(0[12]):(\d{1,3})\x03'), self.__MatchBusTransitionTime, None)
            self.AddMatchString(re.compile(b'\x02AKRS:(0[01])\x03'), self.__MatchKeySignalCoupling, None)
            self.AddMatchString(re.compile(b'\x02APAT:(0[12]):(\d{1,2})\x03'), self.__MatchTransitionPattern, None)
            self.AddMatchString(re.compile(b'\x02EROR:(0[12])\x03'), self.__MatchError, None)

    def SetAutoTransitionTime(self, value, qualifier):

        SourceStates = {
            'BKGD'  : '00',
            'KEY1'  : '01',
            'KEY2'  : '04',
            'KEY3'  : '05',
            'FTB'   : '06',
            'DSK1'  : '07',
            'DSK2'  : '08'
        }

        if qualifier['Source'] in SourceStates and 0 <= value <= 999:
            AutoTransitionTimeCmdString = '\x02STIM:{0}:{1:03d}\x03'.format(SourceStates[qualifier['Source']], value)
            self.__SetHelper('AutoTransitionTime', AutoTransitionTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTransitionTime')

    def UpdateAutoTransitionTime(self, value, qualifier):

        SourceStates = {
            'BKGD': '00',
            'KEY1': '01',
            'KEY2': '04',
            'KEY3': '05',
            'FTB': '06',
            'DSK1': '07',
            'DSK2': '08'
        }

        if qualifier['Source'] in SourceStates:
            AutoTransitionTimeCmdString = '\x02QTIM:{}\x03'.format(SourceStates[qualifier['Source']])
            self.__UpdateHelper('AutoTransitionTime', AutoTransitionTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoTransitionTime')

    def __MatchAutoTransitionTime(self, match, tag):

        SourceStates = {
            '00': 'BKGD',
            '01': 'KEY1',
            '04': 'KEY2',
            '05': 'KEY3',
            '06': 'FTB',
            '07': 'DSK1',
            '08': 'DSK2'
        }

        qualifier = {'Source' : SourceStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        if 0 <= value <= 999:
            self.WriteStatus('AutoTransitionTime', value, qualifier)

    def SetAuxTransition(self, value, qualifier):

        SourceStates = {
            'BKGD': '00',
            'KEY1': '01',
            'KEY2': '04',
            'KEY3': '05',
            'FTB': '06',
            'DSK1': '07',
            'DSK2': '08'
        }

        EffectStates = {
            'Mix': '0',
            'Wipe': '1'
        }

        ValueStateValues = {
            'Trigger On': '0',
            'On Take': '1',
            'Off Take': '2'
        }

        if qualifier['Source'] in SourceStates and qualifier['Effect'] in EffectStates and value in ValueStateValues:
            AuxTransitionCmdString = '\x02SAUT:{0}:{1}:{2}\x03'.format(SourceStates[qualifier['Source']], EffectStates[qualifier['Effect']], ValueStateValues[value])
            self.__SetHelper('AuxTransition', AuxTransitionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxTransition')

    def SetBusSelection(self, value, qualifier):

        BusStates = {
            'ME1PGM': '01',
            'ME1PVM': '02',
            'ME1KEY1-F': '03',
            'ME1KEY1-S': '04',
            'ME1KEY2-F': '05',
            'ME1KEY2-S': '06',
            'ME1KEY3-F': '07',
            'ME1KEY3-S': '08',
            'DSK1-F': '97',
            'DSK1-S': '98',
            'DSK2-F': '99',
            'DSK2-S': '100',
            'AUX1': '113',
            'AUX2': '114',
            'AUX3': '115',
            'AUX4': '116',
            'DISP': '141',
            'VMEM-V': '150',
            'VMEM-K': '151',
            'MV1-1': '153',
            'MV1-2': '154',
            'MV1-3': '155',
            'MV1-4': '156',
            'MV1-5': '157',
            'MV1-6': '158',
            'MV1-7': '159',
            'MV1-8': '160',
            'MV1-9': '161',
            'MV1-10': '162',
            'MV1-11': '163',
            'MV1-12': '164',
            'MV1-13': '165',
            'MV1-14': '166',
            'MV1-15': '167',
            'MV1-16': '168',
            'MV2-1': '169',
            'MV2-2': '170',
            'MV2-3': '171',
            'MV2-4': '172',
            'MV2-5': '173',
            'MV2-6': '174',
            'MV2-7': '175',
            'MV2-8': '176',
            'MV2-9': '177',
            'MV2-10': '178',
            'MV2-11': '179',
            'MV2-12': '180',
            'MV2-13': '181',
            'MV2-14': '182',
            'MV2-15': '183',
            'MV2-16': '184'
        }

        ValueStateValues = {
            'IN1': '01',
            'IN2': '02',
            'SDI IN3': '03',
            'SDI IN4': '04',
            'SDI IN5': '05',
            'SDI IN6': '06',
            'SDI IN7': '07',
            'SDI IN8': '08',
            'OPA IN1': '09',
            'OPA IN2': '10',
            'OPA IN3': '11',
            'OPA IN4': '12',
            'OPB IN1': '13',
            'OPB IN2': '14',
            'OPB IN3': '15',
            'OPB IN4': '16',
            'CBGD1': '145',
            'CBGD2': '146',
            'CBAR': '147',
            'BLACK': '148',
            'STILL1V': '149',
            'STILL1K': '150',
            'STILL2V': '151',
            'STILL2K': '152',
            'CLIP1V': '157',
            'CLIP1K': '158',
            'CLIP2V': '159',
            'CLIP2K': '160',
            'MV1': '165',
            'MV2': '166',
            'Key Out': '171',
            'CLN': '172',
            'PGM': '201',
            'PVW': '203',
            'ME PGM': '209',
            'AUX1': '227',
            'AUX2': '228',
            'AUX3': '229',
            'AUX4': '230',
            'CLOCK': '251'
        }

        if qualifier['Bus'] in BusStates and value in ValueStateValues:
            BusSelectionCmdString = '\x02SBUS:{0}:{1}\x03'.format(BusStates[qualifier['Bus']], ValueStateValues[value])
            self.__SetHelper('BusSelection', BusSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusSelection')

    def UpdateBusSelection(self, value, qualifier):

        BusStates = {
            'ME1PGM': '01',
            'ME1PVM': '02',
            'ME1KEY1-F': '03',
            'ME1KEY1-S': '04',
            'ME1KEY2-F': '05',
            'ME1KEY2-S': '06',
            'ME1KEY3-F': '07',
            'ME1KEY3-S': '08',
            'DSK1-F': '97',
            'DSK1-S': '98',
            'DSK2-F': '99',
            'DSK2-S': '100',
            'AUX1': '113',
            'AUX2': '114',
            'AUX3': '115',
            'AUX4': '116',
            'DISP': '141',
            'VMEM-V': '150',
            'VMEM-K': '151',
            'MV1-1': '153',
            'MV1-2': '154',
            'MV1-3': '155',
            'MV1-4': '156',
            'MV1-5': '157',
            'MV1-6': '158',
            'MV1-7': '159',
            'MV1-8': '160',
            'MV1-9': '161',
            'MV1-10': '162',
            'MV1-11': '163',
            'MV1-12': '164',
            'MV1-13': '165',
            'MV1-14': '166',
            'MV1-15': '167',
            'MV1-16': '168',
            'MV2-1': '169',
            'MV2-2': '170',
            'MV2-3': '171',
            'MV2-4': '172',
            'MV2-5': '173',
            'MV2-6': '174',
            'MV2-7': '175',
            'MV2-8': '176',
            'MV2-9': '177',
            'MV2-10': '178',
            'MV2-11': '179',
            'MV2-12': '180',
            'MV2-13': '181',
            'MV2-14': '182',
            'MV2-15': '183',
            'MV2-16': '184'
        }

        if qualifier['Bus'] in BusStates:
            BusSelectionCmdString = '\x02QBSC:{}\x03'.format(BusStates[qualifier['Bus']])
            self.__UpdateHelper('BusSelection', BusSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusSelection')

    def __MatchBusSelection(self, match, tag):

        BusStates = {
            '01': 'ME1PGM',
            '02': 'ME1PVM',
            '03': 'ME1KEY1-F',
            '04': 'ME1KEY1-S',
            '05': 'ME1KEY2-F',
            '06': 'ME1KEY2-S',
            '07': 'ME1KEY3-F',
            '08': 'ME1KEY3-S',
            '97': 'DSK1-F',
            '98': 'DSK1-S',
            '99': 'DSK2-F',
            '100': 'DSK2-S',
            '113': 'AUX1',
            '114': 'AUX2',
            '115': 'AUX3',
            '116': 'AUX4',
            '141': 'DISP',
            '150': 'VMEM-V',
            '151': 'VMEM-K',
            '153': 'MV1-1',
            '154': 'MV1-2',
            '155': 'MV1-3',
            '156': 'MV1-4',
            '157': 'MV1-5',
            '158': 'MV1-6',
            '159': 'MV1-7',
            '160': 'MV1-8',
            '161': 'MV1-9',
            '162': 'MV1-10',
            '163': 'MV1-11',
            '164': 'MV1-12',
            '165': 'MV1-13',
            '166': 'MV1-14',
            '167': 'MV1-15',
            '168': 'MV1-16',
            '169': 'MV2-1',
            '170': 'MV2-2',
            '171': 'MV2-3',
            '172': 'MV2-4',
            '173': 'MV2-5',
            '174': 'MV2-6',
            '175': 'MV2-7',
            '176': 'MV2-8',
            '177': 'MV2-9',
            '178': 'MV2-10',
            '179': 'MV2-11',
            '180': 'MV2-12',
            '181': 'MV2-13',
            '182': 'MV2-14',
            '183': 'MV2-15',
            '184': 'MV2-16'
        }

        ValueStateValues = {
            '01': 'IN1',
            '02': 'IN2',
            '03': 'SDI IN3',
            '04': 'SDI IN4',
            '05': 'SDI IN5',
            '06': 'SDI IN6',
            '07': 'SDI IN7',
            '08': 'SDI IN8',
            '09': 'OPA IN1',
            '10': 'OPA IN2',
            '11': 'OPA IN3',
            '12': 'OPA IN4',
            '13': 'OPB IN1',
            '14': 'OPB IN2',
            '15': 'OPB IN3',
            '16': 'OPB IN4',
            '145': 'CBGD1',
            '146': 'CBGD2',
            '147': 'CBAR',
            '148': 'BLACK',
            '149': 'STILL1V',
            '150': 'STILL1K',
            '151': 'STILL2V',
            '152': 'STILL2K',
            '157': 'CLIP1V',
            '158': 'CLIP1K',
            '159': 'CLIP2V',
            '160': 'CLIP2K',
            '165': 'MV1',
            '166': 'MV2',
            '171': 'Key Out',
            '172': 'CLN',
            '201': 'PGM',
            '203': 'PVW',
            '209': 'ME PGM',
            '227': 'AUX1',
            '228': 'AUX2',
            '229': 'AUX3',
            '230': 'AUX4',
            '251': 'CLOCK'
        }

        qualifier = {'Bus' : BusStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BusSelection', value, qualifier)

    def SetBusTransitionTime(self, value, qualifier):

        BusStates = {
            'AUX1': '01',
            'AUX2': '02'
        }

        ModeStates = {
            'Enable': '01',
            'Disable': '02'
        }

        if qualifier['Bus'] in BusStates and qualifier['Mode'] in ModeStates and 0 <= value <= 999:
            BusTransitionTimeCmdString = '\x02SBTI:{0}:{1}:{2:03d}\x03'.format(BusStates[qualifier['Bus']], ModeStates[qualifier['Mode']], value)
            self.__SetHelper('BusTransitionTime', BusTransitionTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusTransitionTime')

    def UpdateBusTransitionTime(self, value, qualifier):

        BusStates = {
            'AUX1': '01',
            'AUX2': '02'
        }

        ModeStates = {
            'Enable': '01',
            'Disable': '02'
        }

        if qualifier['Bus'] in BusStates and qualifier['Mode'] in ModeStates:
            BusTransitionTimeCmdString = '\x02QBTI:{}\x03'.format(BusStates[qualifier['Bus']])
            self.__UpdateHelper('BusTransitionTime', BusTransitionTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusTransitionTime')

    def __MatchBusTransitionTime(self, match, tag):

        BusStates = {
            '01': 'AUX1',
            '02': 'AUX2'
        }

        ModeStates = {
            '01': 'Enable',
            '02': 'Disable'
        }

        qualifier = {
            'Bus' : BusStates[match.group(1).decode()],
            'Mode' : ModeStates[match.group(2).decode()]
        }

        value = int(match.group(3).decode())
        if 0 <= value <= 999:
            self.WriteStatus('BusTransitionTime', value, qualifier)

    def SetCutTransition(self, value, qualifier):

        SourceStates = {
            'BKGD': '00',
            'KEY1': '01',
            'KEY2': '04',
            'KEY3': '05',
            'FTB': '06',
            'DSK1': '07',
            'DSK2': '08'
        }

        if qualifier['Source'] in SourceStates:
            CutTransitionCmdString = '\x02SCUT:{}\x03'.format(SourceStates[qualifier['Source']])
            self.__SetHelper('CutTransition', CutTransitionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCutTransition')

    def SetKeySignalCoupling(self, value, qualifier):

        ValueStateValues = {
            'Fill to Source': '00',
            'Source to Fill': '01'
        }

        if value in ValueStateValues:
            KeySignalCouplingCmdString = '\x02SKRS:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('KeySignalCoupling', KeySignalCouplingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeySignalCoupling')

    def UpdateKeySignalCoupling(self, value, qualifier):

        KeySignalCouplingCmdString = '\x02QKRS\x03'
        self.__UpdateHelper('KeySignalCoupling', KeySignalCouplingCmdString, value, qualifier)

    def __MatchKeySignalCoupling(self, match, tag):

        ValueStateValues = {
            '00': 'Fill to Source',
            '01': 'Source to Fill'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('KeySignalCoupling', value, None)

    def SetTransitionPattern(self, value, qualifier):

        TypeStates = {
            'BKGD': '01',
            'KEY1': '02'
        }

        if qualifier['Type'] in TypeStates and 1 <= int(value) <= 69:
            TransitionPatternCmdString = '\x02SPAT:{0}:{1:02d}\x03'.format(TypeStates[qualifier['Type']], int(value))
            self.__SetHelper('TransitionPattern', TransitionPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransitionPattern')

    def UpdateTransitionPattern(self, value, qualifier):

        TypeStates = {
            'BKGD': '01',
            'KEY1': '02'
        }

        if qualifier['Type'] in TypeStates:
            TransitionPatternCmdString = '\x02QPAT:{}\x03'.format(TypeStates[qualifier['Type']])
            self.__UpdateHelper('TransitionPattern', TransitionPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransitionPattern')

    def __MatchTransitionPattern(self, match, tag):

        TypeStates = {
            '01': 'BKGD',
            '02': 'KEY1'
        }

        qualifier = {'Type' : TypeStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        if 1 <= value <= 69:
            self.WriteStatus('TransitionPattern', str(value), qualifier)

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

        DEVICE_ERROR_CODES = {
            '01' : 'Out of the parameter range.',
            '02' : 'Syntax error.'
        }

        value = DEVICE_ERROR_CODES[match.group(0).decode()]
        self.Error(['Error: {}'.format(value)])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
