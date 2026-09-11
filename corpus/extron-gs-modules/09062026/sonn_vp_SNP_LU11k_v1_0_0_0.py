from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from itertools import cycle


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
            '3DFormat': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AVMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPBP': {'Status': {}},
            'Power': {'Status': {}},
            'Swap': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\[TDEN!0(0|1|2|3|4|5)\]'), self.__Match3DFormat, None)
            self.AddMatchString(re.compile(b'\[ASPR!0(0|1|2|3|4)\]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\[PMUT!0(0|1)\]'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'\[DPMO!0(0|1|2|3|4|5|6|7|8)\]'), self.__MatchDisplayMode, None)
            self.AddMatchString(re.compile(b'\[FRZE!0(0|1)\]'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\[MSRC!(0|1|2|3|4|5)\]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\[LPTH!([0-9]{5})\]'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\[SSRC!(0|1|2|3|4|5)\]'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\[PIBP!0(0|1)\]'), self.__MatchPIPPBP, None)
            self.AddMatchString(re.compile(b'\[POWR!(0|1|10|11)\]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\[ERR \"(TDEN|ASPR|PMUT|DPMO|FRZE|MSRC|LPTH|SSRC|PIBP|POWR): Request Fail\"\]'), self.__MatchError, None)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '[TDEN0]',
            'Frame Packing': '[TDEN1]',
            'Side by Side': '[TDEN2]',
            'Top and Bottom': '[TDEN3]',
            'Frame Sequential': '[TDEN4]',
            'Off': '[TDEN5]'
        }

        FormatCmdString = ValueStateValues[value]
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier):

        self.__UpdateHelper('3DFormat', '[TDEN?]', value, qualifier)

    def __Match3DFormat(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Frame Packing',
            '2': 'Side by Side',
            '3': 'Top and Bottom',
            '4': 'Frame Sequential',
            '5': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('3DFormat', value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '[ASPR0]',
            '4:3': '[ASPR1]',
            '16:9': '[ASPR2]',
            '16:10': '[ASPR3]',
            'Native': '[ASPR4]'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        self.__UpdateHelper('AspectRatio', '[ASPR?]', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': '4:3',
            '2': '16:9',
            '3': '16:10',
            '4': 'Native'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '[PMUT1]',
            'Off': '[PMUT0]'
        }

        AVMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        self.__UpdateHelper('AVMute', '[PMUT?]', value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '[DPMO0]',
            'Video': '[DPMO1]',
            'Standard': '[DPMO2]',
            'REC709': '[DPMO3]',
            'DICOM SIM.': '[DPMO4]',
            '2D High Speed': '[DPMO5]',
            '3D': '[DPMO6]',
            'Blending': '[DPMO7]',
            'User': '[DPMO8]'
        }

        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        self.__UpdateHelper('DisplayMode', '[DPMO?]', value, qualifier)

    def __MatchDisplayMode(self, match, tag):

        ValueStateValues = {
            '0': 'Presentation',
            '1': 'Video',
            '2': 'Standard',
            '3': 'REC709',
            '4': 'DICOM SIM.',
            '5': '2D High Speed',
            '6': '3D',
            '7': 'Blending',
            '8': 'User'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DisplayMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '[FRZE1]',
            'Off': '[FRZE0]'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        self.__UpdateHelper('Freeze', '[FRZE?]', value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '[MSRC0]',
            'HDMI': '[MSRC1]',
            'DVI-D': '[MSRC2]',
            'HDBaseT': '[MSRC3]',
            'LAN': '[MSRC4]',
            '3G-SDI': '[MSRC5]'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', '[MSRC?]', value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'VGA',
            '1': 'HDMI',
            '2': 'DVI-D',
            '3': 'HDBaseT',
            '4': 'LAN',
            '5': '3G-SDI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '[KEYG64]',
            'Down': '[KEYG65]',
            'Left': '[KEYG66]',
            'Right': '[KEYG67]',
            'Enter': '[KEYG19]',
            'Menu': '[KEYG27]',
            'Exit': '[KEYG29]'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        self.__UpdateHelper('OperationHours', '[LPTH?]', value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '[SSRC0]',
            'HDMI': '[SSRC1]',
            'DVI-D': '[SSRC2]',
            'HDBaseT': '[SSRC3]',
            'LAN': '[SSRC4]',
            '3G-SDI': '[SSRC5]'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        self.__UpdateHelper('PIPInput', '[SSRC?]', value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            '0': 'VGA',
            '1': 'HDMI',
            '2': 'DVI-D',
            '3': 'HDBaseT',
            '4': 'LAN',
            '5': '3G-SDI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPBP(self, value, qualifier):

        ValueStateValues = {
            'On': '[PIBP1]',
            'Off': '[PIBP0]'
        }

        PIPPBPCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPBP', PIPPBPCmdString, value, qualifier)

    def UpdatePIPPBP(self, value, qualifier):

        self.__UpdateHelper('PIPPBP', '[PIBP?]', value, qualifier)

    def __MatchPIPPBP(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPBP', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '[POWR1]',
            'Off': '[POWR0]'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', '[POWR?]', value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '11': 'Warming Up',
            '10': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSwap(self, value, qualifier):

        SwapCmdString = '[PISW1]'
        self.__SetHelper('Swap', SwapCmdString, value, qualifier)

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

        Commands = {
            'TDEN' : '3DFormat',
            'ASPR' : 'Aspect Ratio',
            'PMUT' : 'AV Mute',
            'DPMO' : 'Display Mode',
            'FRZE' : 'Freeze',
            'MSRC' : 'Input',
            'LPTH' : 'Operation Hours',
            'SSRC' : 'PIP Input',
            'PIBP' : 'PIP PBP',
            'POWR' : 'Power'
        }
        self.Error(['{0}: Request Fail'.format(Commands[match.group(1).decode()])])

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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