from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'ColorBW': {'Status': {}},
            'Detail': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Parameters': ['Speed'], 'Status': {}},
            'Light': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'OutputSource': {'Status': {}},
            'PosNeg': {'Status': {}},
            'Power': {'Status': {}},
            'TextEnhancer': {'Status': {}},
            'VideoMute': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'WhiteBalanceMode': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x00\x31\x01([\x00\x01])'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'\x00\x32\x01([\x00\x01])'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'\x00\x6D\x01([\x00\x01\x02\x03\x04])'), self.__MatchColorBW, None)
            self.AddMatchString(re.compile(b'\x00\x53\x01([\x00\x02\x03])'), self.__MatchDetail, None)
            self.AddMatchString(re.compile(b'\x00\x80\x01([\x00\x01])'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x00\x56\x01([\x00\x01])'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\x00\xA0\x01([\x00\x01])'), self.__MatchLight, None)
            self.AddMatchString(re.compile(b'\x00\x51(\x01[\x00\x04\x08\x16\x1E\xFF])'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'\x00\x57\x01([\x00\x01])'), self.__MatchOutputSource, None)
            self.AddMatchString(re.compile(b'\x00\x54\x01([\x00\x01\x02])'), self.__MatchPosNeg, None)
            self.AddMatchString(re.compile(b'\x00\x30\x01([\x00\x01])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x00\x85\x01([\x00\x01])'), self.__MatchTextEnhancer, None)
            self.AddMatchString(re.compile(b'\x00\x86\x01([\x00\x01])'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x00\x65\x01([\x00\x01\x02])'), self.__MatchWhiteBalanceMode, None)
            self.AddMatchString(re.compile(b'([\x80\x81])[\x00-\xFF]([\x02\x03])'), self.__MatchError, None)

    def SetAutoFocus(self, value, qualifier):

        AF_Values = {
            'Off': 0x00,
            'On': 0x01
        }

        AFCmdString = pack('>BBBB', 0x01, 0x31, 0x01, AF_Values[value])
        self.__SetHelper('AutoFocus', AFCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        AF_Status = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = AF_Status[match.group(1).decode()]
        self.WriteStatus('AutoFocus', value, None)

    def UpdateAutoFocus(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x31, 0x00)
        self.__UpdateHelper('AutoFocus', CmdString, value, qualifier)

    def SetAutoIris(self, value, qualifier):

        AI_Values = {
            'Off': 0x00,
            'On': 0x01
        }

        AICmdString = pack('>BBBB', 0x01, 0x32, 0x01, AI_Values[value])
        self.__SetHelper('AutoIris', AICmdString, value, qualifier)

    def __MatchAutoIris(self, match, tag):

        AI_Status = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = AI_Status[match.group(1).decode()]
        self.WriteStatus('AutoIris', value, None)

    def UpdateAutoIris(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x32, 0x00)
        self.__UpdateHelper('AutoIris', CmdString, value, qualifier)

    def SetColorBW(self, value, qualifier):

        CBW_Values = {
            'BW': 0x00,
            'Presentation': 0x01,
            'Natural': 0x02,
            'Video Conference': 0x03,
            'Manual': 0x04
        }

        CBWCmdString = pack('>BBBB', 0x01, 0x6D, 0x01, CBW_Values[value])
        self.__SetHelper('ColorBW', CBWCmdString, value, qualifier)

    def __MatchColorBW(self, match, tag):

        CBW_Status = {
            '\x00': 'BW',
            '\x01': 'Presentation',
            '\x02': 'Natural',
            '\x03': 'Video Conference',
            '\x04': 'Manual'
        }

        value = CBW_Status[match.group(1).decode()]
        self.WriteStatus('ColorBW', value, None)

    def UpdateColorBW(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x6D, 0x00)
        self.__UpdateHelper('ColorBW', CmdString, value, qualifier)

    def SetDetail(self, value, qualifier):

        DTL_Values = {
            'Medium': 0x02,
            'High': 0x03,
            'Off': 0x00
        }

        DTLCmdString = pack('>BBBB', 0x01, 0x53, 0x01, DTL_Values[value])
        self.__SetHelper('Detail', DTLCmdString, value, qualifier)

    def __MatchDetail(self, match, tag):

        DTL_Status = {
            '\x02': 'Medium',
            '\x03': 'High',
            '\x00': 'Off'
        }

        value = DTL_Status[match.group(1).decode()]
        self.WriteStatus('Detail', value, None)

    def UpdateDetail(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x53, 0x00)
        self.__UpdateHelper('Detail', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        EM_Values = {
            'Off': 0x00,
            'On': 0x01
        }

        EMCmdString = pack('>BBBB', 0x01, 0x80, 0x01, EM_Values[value])
        self.__SetHelper('ExecutiveMode', EMCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        EM_Status = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = EM_Status[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateExecutiveMode(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x80, 0x00)
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        Focus_Values = {
            'Far': 0x01,
            'Near': 0x02,
            'Stop': 0x00
        }

        range = int(qualifier['Speed'])
        if 1 <= range <= 15:
            if value is 'Stop':
                FocusCmdString = pack('>6B', 0x01, 0x21, 0x03, 0x00, 0x00, 0x00)
            else:
                FocusCmdString = pack('>6B', 0x01, 0x21, 0x03, Focus_Values[value], 0x00, range)

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        Frz_Values = {
            'Off': 0x00,
            'On': 0x01
        }

        FrzCmdString = pack('>BBBB', 0x01, 0x56, 0x01, Frz_Values[value])
        self.__SetHelper('Freeze', FrzCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        Frz_Status = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = Frz_Status[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def UpdateFreeze(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x56, 0x00)
        self.__UpdateHelper('Freeze', CmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        Iris_Values = {
            'Open': 0x01,
            'Close': 0x02,
            'Stop': 0x00
        }

        range = int(qualifier['Speed'])
        if 1 <= range <= 15:
            if value is 'Stop':
                IrisCmdString = pack('>6B', 0x01, 0x22, 0x03, 0x00, 0x00, 0x00)
            else:
                IrisCmdString = pack('>6B', 0x01, 0x22, 0x03, Iris_Values[value], 0x00, range)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetIris')

    def SetLight(self, value, qualifier):

        Light_Values = {
            'Off': 0x00,
            'On': 0x01
        }

        LightCmdString = pack('>BBBB', 0x01, 0xA0, 0x01, Light_Values[value])
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def __MatchLight(self, match, tag):

        Light_Status = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = Light_Status[match.group(1).decode()]
        self.WriteStatus('Light', value, None)

    def UpdateLight(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0xA0, 0x00)
        self.__UpdateHelper('Light', CmdString, value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        OR_Values = {
            'Off': 0xFF,
            'Auto': 0x00,
            'XGA 60Hz': 0x04,
            'SXGA 60Hz': 0x08,
            '720p 60Hz': 0x16,
            'WXGA 60Hz': 0x1E,
        }

        ORCmdString = pack('>BBBB', 0x01, 0x51, 0x01, OR_Values[value])
        self.__SetHelper('OutputResolution', ORCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        OR_Status = {
            b'\x01\xFF': 'Off',
            b'\x01\x00': 'Auto',
            b'\x01\x04': 'XGA 60Hz',
            b'\x01\x08': 'SXGA 60Hz',
            b'\x01\x16': '720p 60Hz',
            b'\x01\x1E': 'WXGA 60Hz'
        }

        or_value = match.group(1)
        value = OR_Status[or_value]
        self.WriteStatus('OutputResolution', value, None)

    def UpdateOutputResolution(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x51, 0x00)
        self.__UpdateHelper('OutputResolution', CmdString, value, qualifier)

    def SetOutputSource(self, value, qualifier):

        OS_Values = {
            'External': 0x01,
            'Internal': 0x00,
        }

        OSCmdString = pack('>BBBB', 0x01, 0x57, 0x01, OS_Values[value])
        self.__SetHelper('OutputSource', OSCmdString, value, qualifier)

    def __MatchOutputSource(self, match, tag):

        OS_Status = {
            '\x00': 'Internal',
            '\x01': 'External'
        }

        value = OS_Status[match.group(1).decode()]
        self.WriteStatus('OutputSource', value, None)

    def UpdateOutputSource(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x57, 0x00)
        self.__UpdateHelper('OutputSource', CmdString, value, qualifier)

    def SetPosNeg(self, value, qualifier):

        PN_Values = {
            'Positive': 0x00,
            'Negative': 0x01,
            'Blue': 0x02
        }

        PNCmdString = pack('>BBBB', 0x01, 0x54, 0x01, PN_Values[value])
        self.__SetHelper('PosNeg', PNCmdString, value, qualifier)

    def __MatchPosNeg(self, match, tag):

        PN_Status = {
            '\x00': 'Positive',
            '\x01': 'Negative',
            '\x02': 'Blue'
        }

        value = PN_Status[match.group(1).decode()]
        self.WriteStatus('PosNeg', value, None)

    def UpdatePosNeg(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x54, 0x00)
        self.__UpdateHelper('PosNeg', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PW_Values = {
            'Off': 0x00,
            'On': 0x01
        }

        PwdCmdString = pack('>BBBB', 0x01, 0x30, 0x01, PW_Values[value])
        self.__SetHelper('Power', PwdCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PW_Status = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = PW_Status[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def UpdatePower(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x30, 0x00)
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def SetTextEnhancer(self, value, qualifier):

        TN_Values = {
            'Off': 0x00,
            'On': 0x01,
        }

        TNCmdString = pack('>BBBB', 0x01, 0x85, 0x01, TN_Values[value])
        self.__SetHelper('TextEnhancer', TNCmdString, value, qualifier)

    def __MatchTextEnhancer(self, match, tag):

        TN_Status = {
            '\x00': 'Off',
            '\x01': 'On',
        }

        value = TN_Status[match.group(1).decode()]
        self.WriteStatus('TextEnhancer', value, None)

    def UpdateTextEnhancer(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x85, 0x00)
        self.__UpdateHelper('TextEnhancer', CmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VM_Values = {
            'Off': 0x00,
            'On': 0x01,
        }

        VMCmdString = pack('>BBBB', 0x01, 0x86, 0x01, VM_Values[value])
        self.__SetHelper('VideoMute', VMCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VM_Status = {
            '\x00': 'Off',
            '\x01': 'On',
        }

        value = VM_Status[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def UpdateVideoMute(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x86, 0x00)
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        VMCmdString = pack('>BBBB', 0x01, 0x65, 0x01, 0x10)
        self.__SetHelper('WhiteBalance', VMCmdString, value, qualifier)

    def SetWhiteBalanceMode(self, value, qualifier):

        WBM_Values = {
            'Auto': 0x00,
            'One-Push': 0x01,
            'Manual': 0x02
        }

        WBMCmdString = pack('>BBBB', 0x01, 0x65, 0x01, WBM_Values[value])
        self.__SetHelper('WhiteBalanceMode', WBMCmdString, value, qualifier)

    def __MatchWhiteBalanceMode(self, match, tag):

        WBM_Status = {
            '\x00': 'Auto',
            '\x01': 'One-Push',
            '\x02': 'Manual'
        }

        value = WBM_Status[match.group(1).decode()]
        self.WriteStatus('WhiteBalanceMode', value, None)

    def UpdateWhiteBalanceMode(self, value, qualifier):

        CmdString = pack('>BBB', 0x00, 0x65, 0x00)
        self.__UpdateHelper('WhiteBalanceMode', CmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        Zoom_Values = {
            'Tele': 0x02,
            'Wide': 0x01,
            'Stop': 0x00
        }

        range = int(qualifier['Speed'])
        if 1 <= range <= 15:
            if value is 'Stop':
                ZoomCmdString = pack('>6B', 0x01, 0x20, 0x03, 0x00, 0x00, 0x00)
            else:
                ZoomCmdString = pack('>6B', 0x01, 0x20, 0x03, Zoom_Values[value], 0x00, range)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetZoom')

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '\x03': 'Invalid Parameter',
            '\x02': 'Invalid Command'
        }

        value = DEVICE_ERROR_CODES[match.group(2).decode()]
        self.Error([value])

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
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
