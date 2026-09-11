from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
        self._MonitorID = b'\x01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PAPToggle': {'Status': {}},
            'PIPPAPInput': {'Status': {}},
            'PIPPAPSwap': {'Status': {}},
            'PIPToggle': {'Status': {}},
            'Power': {'Status': {}},
        }
                
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFC\x0A[\x01-\xFA]RGA\x00([\x00-\x07])[\x00-\xFF]\xFD'), self.__MatchGamma, None)
            self.AddMatchString(re.compile(b'\xFC\x0A[\x01-\xFA]RSO\x00([\x00-\x0D])[\x00-\xFF]\xFD'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xFC\x0B[\x01-\xFA]LTC\x00([\x00-\xFF]{2})[\x00-\xFF]\xFD'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\xFC\x0A[\x01-\xFA]PSS\x00([\x00-\x0D])[\x00-\xFF]\xFD'), self.__MatchPIPPAPInput, None)
            self.AddMatchString(re.compile(b'\xFC\x0A[\x01-\xFA]SMP\x00([\x00-\x01])[\x00-\xFF]\xFD'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xFC\x07[\x01-\xFA]\xF0\x0E[\x00-\xFF]\xFD'), self.__MatchError, None)

    @property
    def MonitorID(self):
        return self._MonitorID

    @MonitorID.setter
    def MonitorID(self, value):
        if 1 <= int(value) <= 250:
            self._MonitorID = bytes([int(value)])

    def BuildCommandString(self, commandstring):

        commandstring = b''.join([self._MonitorID, commandstring])
        length = len(commandstring) + 4
        checksum = 0
        for index in commandstring:
            checksum = checksum + index
        start = bytes([0xFC, length])
        stop = bytes([checksum & 0xFF, 0xFD])
        return b''.join([start, commandstring, stop])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1': b'SCA\x01\x00',
            'Fill': b'SCA\x01\x01',
            'Aspect': b'SCA\x01\x02'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'ADJ\x01'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            'Off': b'GOF\x01',
            '1.8': b'G18\x01',
            '2.0': b'G20\x01',
            '2.2': b'G22\x01',
            '2.4': b'G24\x01',
            '2.6': b'G26\x01',
            'DICOM': b'GDM\x01',
            'User': b'GAU\x01'
        }

        GammaCmdString = ValueStateValues[value]
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        GammaCmdString = b'RGA\x00'
        self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)

    def __MatchGamma(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': '1.8',
            b'\x02': '2.0',
            b'\x03': '2.2',
            b'\x04': '2.4',
            b'\x05': '2.6',
            b'\x06': 'DICOM',
            b'\x07': 'User'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Gamma', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVI': b'DVI\x01',
            'Composite': b'CVB\x01',
            'S-Video': b'SVO\x01',
            'Component': b'CPN\x01',
            'VGA': b'VGA\x01',
            'DVI-A': b'DVA\x01',
            'SDI': b'SDI\x01',
            'SDI-2': b'SD2\x01',
            'Display Port': b'DPT\x01',
            'HDMI 1': b'HD1\x01',
            'HDMI 2': b'HD2\x01',
            'YPbPr': b'RGB\x01',
            'RGB': b'SOG\x01',
            '3G-SDI': b'3GS\x01'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'RSO\x00'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'DVI',
            b'\x01': 'Composite',
            b'\x02': 'S-Video',
            b'\x03': 'Component',
            b'\x04': 'VGA',
            b'\x05': 'DVI-A',
            b'\x06': 'SDI',
            b'\x07': 'SDI-2',
            b'\x08': 'Display Port',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'YPbPr',
            b'\x0C': 'RGB',
            b'\x0D': '3G-SDI'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'LTC\x00'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        res = match.group(1)
        value = res[0] * 256 + res[1]
        self.WriteStatus('OperationHours', value, None)

    def SetPAPToggle(self, value, qualifier):

        PAPToggleCmdString = b'PAP\x01'
        self.__SetHelper('PAPToggle', PAPToggleCmdString, value, qualifier)

    def SetPIPPAPInput(self, value, qualifier):

        ValueStateValues = {
            'DVI': b'PSS\x01\x00',
            'Composite': b'PSS\x01\x01',
            'S-Video': b'PSS\x01\x02',
            'Component': b'PSS\x01\x03',
            'VGA': b'PSS\x01\x04',
            'DVI-A': b'PSS\x01\x05',
            'SDI': b'PSS\x01\x06',
            'SDI-2': b'PSS\x01\x07',
            'Display Port': b'PSS\x01\x08',
            'HDMI 1': b'PSS\x01\x09',
            'HDMI 2': b'PSS\x01\x0A',
            'YPbPr' : b'PSS\x01\x0B',
            'RGB': b'PSS\x01\x0C',
            '3G-SDI': b'PSS\x01\x0D'
        }

        PIPPAPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPAPInput', PIPPAPInputCmdString, value, qualifier)

    def UpdatePIPPAPInput(self, value, qualifier):

        PIPPAPInputCmdString = b'PSS\x00'
        self.__UpdateHelper('PIPPAPInput', PIPPAPInputCmdString, value, qualifier)

    def __MatchPIPPAPInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'DVI',
            b'\x01': 'Composite',
            b'\x02': 'S-Video',
            b'\x03': 'Component',
            b'\x04': 'VGA',
            b'\x05': 'DVI-A',
            b'\x06': 'SDI',
            b'\x07': 'SDI-2',
            b'\x08': 'Display Port',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'YPbPr',
            b'\x0C': 'RGB',
            b'\x0D': '3G-SDI'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPPAPInput', value, None)

    def SetPIPPAPSwap(self, value, qualifier):

        PIPPAPSwapCmdString = b'SWP\x01'
        self.__SetHelper('PIPPAPSwap', PIPPAPSwapCmdString, value, qualifier)

    def SetPIPToggle(self, value, qualifier):

        PIPToggleCmdString = b'PIT\x01'
        self.__SetHelper('PIPToggle', PIPToggleCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'PON\x01',
            'Off': b'POF\x01'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'SMP\x00'
        iself.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if command == 'UserDefinedCommand':
        	self.Send(commandstring)
        else:
        	self.Send(self.BuildCommandString(commandstring))

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(self.BuildCommandString(commandstring))            

    def __MatchError(self, match, tag):


        print('Error: NAK')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
