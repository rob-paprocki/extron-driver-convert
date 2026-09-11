from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceSerialClass:
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
            'AspectRatio': {'Parameters':['Monitor'], 'Status': {}},
            'AudioMute': {'Parameters':['Monitor'], 'Status': {}},
            'FrameControl': {'Parameters':['Monitor'], 'Status': {}},
            'Input': {'Parameters':['Monitor'], 'Status': {}},
            'MultiDisplay': {'Parameters':['Monitor'], 'Status': {}},
            'MultiDisplaySetup' : {'Set': True,  'Update': False, 'Live': False, 'Emulated': False,
                                   'Parameters': ['Value', 'Horizontal Scale', 'Vertical Scale', 'Bezel H Adjustment',
                                                  'Bezel V Adjustment', 'Row', 'Column', 'Monitor'], 'Status': {}},
            'Power': {'Parameters':['Monitor'], 'Status': {}},
            'ReverseScan': {'Parameters':['Monitor'], 'Status': {}},
            'VideoMute': {'Parameters':['Monitor'], 'Status': {}},
            'Volume': {'Parameters':['Monitor'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAS:(ZOOM|FULL|NORM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAM:(1|0)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);MDC:FCT([012345])\x03'), self.__MatchFrameControl, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QMI:(HM1|HM2|DV1|PC1|VD1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QPW:(1|0)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);MDC:RVS(1|0)\x03'), self.__MatchReverseScan, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QVM:(1|0)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAV:([0-9]{1,3})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);ER401\x03'), self.__MatchError, None)

    def getMonitor (self, Monitor):
        if 1 <= int(Monitor) <= 100:
            return '\x02AD94;RAD:{0:03d};'.format (int(Monitor))

    def SetAspectRatio(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'Zoom 1': 'DAM:ZOOM\x03\r',
            '16:9'  : 'DAM:FULL\x03\r',
            '4:3'   : 'DAM:NORM\x03\r',
            'Zoom 2': 'DAM:ZOM2\x03\r'
        }

        CmdString = Head + States[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('AspectRatio', Head + 'QAS\x03\r', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            'ZOOM': 'Zoom 1',
            'FULL': '16:9',
            'NORM': '4:3',
            'ZOM2': 'Zoom 2'
        }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]

        self.WriteStatus('AspectRatio',  value, { 'Monitor' : Monitor })

    def SetAudioMute(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On' : 'AMT:1\x03\r',
            'Off': 'AMT:0\x03\r'
        }

        CmdString = Head + States[value]
        self.__SetHelper('AudioMute', CmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('AudioMute', Head + 'QAM\x03\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]

        self.WriteStatus('AudioMute',  value, { 'Monitor' : Monitor })

    def SetFrameControl(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            '0': 'MDC:FCT0\x03\r',
            '1': 'MDC:FCT1\x03\r',
            '2': 'MDC:FCT2\x03\r',
            '3': 'MDC:FCT3\x03\r',
            '4': 'MDC:FCT4\x03\r',
            '5': 'MDC:FCT5\x03\r'
        }

        CmdString = Head + States[value]
        self.__SetHelper('FrameControl', CmdString, value, qualifier)

    def UpdateFrameControl(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('FrameControl', Head + 'QDC:FCT\x03\r', value, qualifier)

    def __MatchFrameControl(self, match, tag):

        States = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]

        self.WriteStatus('FrameControl',  value, { 'Monitor' : Monitor })

    def SetInput(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'HDMI 1': 'IMS:HM1\x03\r',
            'HDMI 2': 'IMS:HM2\x03\r',
            'DVI-D' : 'IMS:DV1\x03\r',
            'PC'    : 'IMS:PC1\x03\r',
            'Video' : 'IMS:VD1\x03\r',
            'USB'   : 'IMS:UD1\x03\r'
        }

        CmdString = Head + States[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('Input', Head + 'QMI\x03\r', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DV1': 'DVI-D',
            'PC1': 'PC',
            'VD1': 'Video',
            'UD1': 'USB'
        }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]

        self.WriteStatus('Input',  value, { 'Monitor' : Monitor })

    def SetMultiDisplay(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On' : 'MDC:1\x03\r',
            'Off': 'MDC:0\x03\r'
        }

        CmdString = Head + States[value]
        self.__SetHelper('MultiDisplay', CmdString, value, qualifier)

    def SetMultiDisplaySetup(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        Value = {
            'On': '0',
            'Off': '1'
        }[qualifier['Value']]

        HScale = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'
        }[qualifier['Horizontal Scale']]

        VScale = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'
        }[qualifier['Vertical Scale']]

        BezelH = {
            '0': '000',
            '1': '010',
            '2': '020',
            '3': '030',
            '4': '040',
            '5': '050',
            '6': '060',
            '7': '070',
            '8': '080',
            '9': '090',
            '10': '100'
        }[qualifier['Bezel H Adjustment']]

        BezelV = {
            '0': '000',
            '1': '010',
            '2': '020',
            '3': '030',
            '4': '040',
            '5': '050',
            '6': '060',
            '7': '070',
            '8': '080',
            '9': '090',
            '10': '100'
        }[qualifier['Bezel V Adjustment']]

        Row = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            'I': '8',
            'J': '9'
        }[qualifier['Row']]

        Column = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'
        }[qualifier['Column']]

        Parameters = Value + HScale + VScale + BezelH + BezelV + Row + Column
        CmdString = Head + 'MDC:EXP{}\x03\r'.format(Parameters)
        self.__SetHelper('MultiDisplaySetup', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On' : 'PON\x03\r',
            'Off': 'POF\x03\r'
            }

        CmdString = Head + States[value]
        self.__SetHelper('Power', CmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('Power', Head + 'QPW\x03\r', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]
        self.WriteStatus('Power',  value, { 'Monitor' : Monitor })

    def SetReverseScan(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On' : 'MDC:RVS1\x03\r',
            'Off': 'MDC:RVS0\x03\r'
        }

        CmdString = Head + States[value]
        self.__SetHelper('ReverseScan', CmdString, value, qualifier)
    def UpdateReverseScan(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('ReverseScan', Head + 'QDC:RVS\x03\r', value, qualifier)

    def __MatchReverseScan(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]

        self.WriteStatus('ReverseScan',  value, { 'Monitor' : Monitor })

    def SetVideoMute(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On' : 'VMT:1\x03\r',
            'Off': 'VMT:0\x03\r'
            }

        CmdString = Head + States[value]
        self.__SetHelper('VideoMute', CmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('VideoMute', Head + 'QVM\x03\r', value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value   = States[match.group(2).decode()]

        self.WriteStatus('VideoMute',  value, { 'Monitor' : Monitor })

    def SetVolume(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        if 0 <= value <= 100:
            CmdString = Head + 'AVL:{0:03d}\x03\r'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('Volume', Head + 'QAV\x03\r', value, qualifier)

    def __MatchVolume(self, match, tag):
        Monitor = str(int(match.group(1).decode()))
        value   = int(match.group(2).decode())
        self.WriteStatus('Volume',  value, { 'Monitor' : Monitor })

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
        self.Error(['Incorrect Command'])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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

class DeviceEthernetClass:

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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'FrameControl': {'Status': {}},
            'Input': {'Status': {}},
            'MultiDisplay': {'Status': {}},
            'MultiDisplaySetup': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False,
                                   'Parameters': ['Value', 'Horizontal Scale', 'Vertical Scale', 'Bezel H Adjustment',
                                                  'Bezel V Adjustment', 'Row', 'Column'], 'Status': {}},
            'Power': {'Status': {}},
            'ReverseScan': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(ZOOM|FULL|NORM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(1|0)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02MDC:FCT([012345])\x03'), self.__MatchFrameControl, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|HM2|DV1|PC1|VD1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QPW:(1|0)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02MDC:RVS(1|0)\x03'), self.__MatchReverseScan, None)
            self.AddMatchString(re.compile(b'\x02QVM:(1|0)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-9]{1,3})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x02ER401\x03'), self.__MatchError, None)


    def SetAspectRatio(self, value, qualifier):

        Value = {
            'Zoom 1': '\x02DAM:ZOOM\x03\r',
            '16:9': '\x02DAM:FULL\x03\r',
            '4:3': '\x02DAM:NORM\x03\r',
            'Zoom 2': '\x02DAM:ZOM2\x03\r'
        }[value]

        self.__SetHelper('AspectRatio', Value, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', '\x02QAS\x03\r', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        Values = {
            'ZOOM': 'Zoom 1',
            'FULL': '16:9',
            'NORM': '4:3',
            'ZOM2': 'Zoom 2'
        }[match.group(1).decode()]
        self.WriteStatus('AspectRatio', Values, None)

    def SetAudioMute(self, value, qualifier):

        Value = {
            'On': '\x02AMT:1\x03\r',
            'Off': '\x02AMT:0\x03\r'
        }[value]

        self.__SetHelper('AudioMute', Value, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '\x02QAM\x03\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        Values = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]

        self.WriteStatus('AudioMute', Values, None)

    def SetFrameControl(self, value, qualifier):

        Value = {
            '0': '\x02MDC:FCT0\x03\r',
            '1': '\x02MDC:FCT1\x03\r',
            '2': '\x02MDC:FCT2\x03\r',
            '3': '\x02MDC:FCT3\x03\r',
            '4': '\x02MDC:FCT4\x03\r',
            '5': '\x02MDC:FCT5\x03\r'
        }[value]

        self.__SetHelper('FrameControl', Value, value, qualifier)

    def UpdateFrameControl(self, value, qualifier):
        self.__UpdateHelper('FrameControl', '\x02QDC:FCT\x03\r', value, qualifier)

    def __MatchFrameControl(self, match, tag):

        Values = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }[match.group(1).decode()]

        self.WriteStatus('FrameControl', Values, None)

    def SetInput(self, value, qualifier):

        Value = {
            'HDMI 1': '\x02IMS:HM1\x03\r',
            'HDMI 2': '\x02IMS:HM2\x03\r',
            'DVI-D': '\x02IMS:DV1\x03\r',
            'PC': '\x02IMS:PC1\x03\r',
            'Video': '\x02IMS:VD1\x03\r',
            'USB': '\x02IMS:UD1\x03\r'
        }[value]

        self.__SetHelper('Input', Value, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '\x02QMI\x03\r', value, qualifier)

    def __MatchInput(self, match, tag):

        Values = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DV1': 'DVI-D',
            'PC1': 'PC',
            'VD1': 'Video',
            'UD1': 'USB'
        }[match.group(1).decode()]

        self.WriteStatus('Input', Values, None)

    def SetMultiDisplay(self, value, qualifier):

        Value = {
            'On': '\x02MDC:1\x03\r',
            'Off': '\x02MDC:0\x03\r'
        }[value]

        self.__SetHelper('MultiDisplay', Value, value, qualifier)

    def SetMultiDisplaySetup(self, value, qualifier):

        Value = {
            'On': '0',
            'Off': '1'
        }[qualifier['Value']]

        HScale = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'
        }[qualifier['Horizontal Scale']]

        VScale = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'
        }[qualifier['Vertical Scale']]

        BezelH = {
            '0': '000',
            '1': '010',
            '2': '020',
            '3': '030',
            '4': '040',
            '5': '050',
            '6': '060',
            '7': '070',
            '8': '080',
            '9': '090',
            '10': '100'
        }[qualifier['Bezel H Adjustment']]

        BezelV = {
            '0': '000',
            '1': '010',
            '2': '020',
            '3': '030',
            '4': '040',
            '5': '050',
            '6': '060',
            '7': '070',
            '8': '080',
            '9': '090',
            '10': '100'
        }[qualifier['Bezel V Adjustment']]

        Row = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            'I': '8',
            'J': '9'
        }[qualifier['Row']]

        Column = {
            '1': '01',
            '2': '02',
            '3': '03',
            '4': '04',
            '5': '05',
            '6': '06',
            '7': '07',
            '8': '08',
            '9': '09',
            '10': '10'
        }[qualifier['Column']]

        Parameters = Value + HScale + VScale + BezelH + BezelV + Row + Column
        CmdString = '\x02MDC:EXP{}\x03\r'.format(Parameters)
        self.__SetHelper('MultiDisplaySetup', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        Value = {
            'On': '\x02PON\x03\r',
            'Off': '\x02POF\x03\r'
            }[value]

        self.__SetHelper('Power', Value, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', '\x02QPW\x03\r', value, qualifier)

    def __MatchPower(self, match, tag):

        Values = {
            '1': 'On',
            '0': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('Power', Values, None)

    def SetReverseScan(self, value, qualifier):

        Value = {
            'On': '\x02MDC:RVS1\x03\r',
            'Off': '\x02MDC:RVS0\x03\r'
        }[value]

        self.__SetHelper('ReverseScan', Value, value, qualifier)

    def UpdateReverseScan(self, value, qualifier):
        self.__UpdateHelper('ReverseScan', '\x02QDC:RVS\x03\r', value, qualifier)

    def __MatchReverseScan(self, match, tag):

        Values = {
            '1': 'On',
            '0': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('ReverseScan', Values, None)

    def SetVideoMute(self, value, qualifier):

        Value = {
            'On': '\x02VMT:1\x03\r',
            'Off': '\x02VMT:0\x03\r'
            }[value]

        self.__SetHelper('VideoMute', Value, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', '\x02QVM\x03\r', value, qualifier)

    def __MatchVideoMute(self, match, tag):

        Values = {
            '1': 'On',
            '0': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('VideoMute', Values, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            Value = '\x02AVL:{0:03d}\x03\r'.format(value)
            self.__SetHelper('Volume', Value, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '\x02QAV\x03\r', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode()), None)

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
        self.Error(['Incorrect Command'])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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
