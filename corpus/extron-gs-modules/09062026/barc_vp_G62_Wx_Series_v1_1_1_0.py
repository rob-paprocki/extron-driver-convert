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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': { 'Status': {}},
            '3DInvert': { 'Status': {}},
            '3DMode': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'LensControl': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\[ASPR!0?([0-5])]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\[PMUT!0?([01])]'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'\[DPMO!0?(\d|10)]'), self.__MatchDisplayMode, None)
            self.AddMatchString(re.compile(b'\[MSRC!0([0-4])]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\[LSAT!(\d+?)]'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\[LPTH!(\d+?)]'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\[SSRC!0?([0-4])]'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\[POWR!0([01])]'), self.__MatchPower, None)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto'               : '0',
            'Frame Packing'      : '1',
            'Side by Side (Half)': '2',
            'Top and Bottom'     : '3',
            'Frame Sequential'   : '4'
            }

        if value in ValueStateValues:
            _3DFormatCmdString = '[TDEN{}]'.format(ValueStateValues[value])
            self.__SetHelper('3DFormat', _3DFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3DFormat')
            
    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            _3DInvertCmdString = '[TDIV{}]'.format(ValueStateValues[value])
            self.__SetHelper('3DInvert', _3DInvertCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3DInvert')

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On' : '1'
            }

        if value in ValueStateValues:
            _3DModeCmdString = '[TDNG{}]'.format(ValueStateValues[value])
            self.__SetHelper('3DMode', _3DModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for Set3DMode')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'         : '0',
            '4:3'          : '1',
            '16:9'         : '2',
            '16:10'        : '3',
            'Letter Boxing': '4',
            'Native'       : '5'
            }

        if value in ValueStateValues:
            AspectRatioCmdString = '[ASPR{}]'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '[ASPR?]'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': '4:3',
            '2': '16:9',
            '3': '16:10',
            '4': 'Letter Boxing',
            '5': 'Native'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0',
            }

        if value in ValueStateValues:
            AVMuteCmdString = '[PMUT{}]'.format(ValueStateValues[value])
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = '[PMUT?]'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation' : '0',
            'Bright'       : '1',
            'Super Bright' : '2',
            'Cinema'       : '3',
            'HDR'          : '4',
            'sRGB'         : '5',
            'DICOM SIM'    : '6',
            'Blending'     : '7',
            '3D'           : '8',
            '2D High Speed': '9',
            'User'         : '10'
            }

        if value in ValueStateValues:
            DisplayModeCmdString = '[DPMO{}]'.format(ValueStateValues[value])
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):

        DisplayModeCmdString = '[DPMO?]'
        self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def __MatchDisplayMode(self, match, tag):

        ValueStateValues = {
            '0': 'Presentation',
            '1': 'Bright',
            '2': 'Super Bright',
            '3': 'Cinema',
            '4': 'HDR',
            '5': 'sRGB',
            '6': 'DICOM SIM',
            '7': 'Blending',
            '8': '3D',
            '9': '2D High Speed',
            '10': 'User'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DisplayMode', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'In':  'I',
            'Out': 'O'
            }

        if value in ValueStateValues:
            FocusCmdString = '[FCS{}1]'.format(ValueStateValues[value])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            FreezeCmdString = '[FRZE{}]'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')
            
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'      : '0',
            'HDMI 2'      : '1',
            'DVI-D'       : '2',
            '3G-SDI'      : '3',
            'HDBaseT'     : '4'
            }

        if value in ValueStateValues:
            InputCmdString = '[MSRC{}]'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '[MSRC?]'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'DVI-D',
            '3': '3G-SDI',
            '4': 'HDBaseT'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '[LSAT?]'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetLensControl(self, value, qualifier):

        ValueStateValues = {
            'Up':   'U',
            'Down': 'D'
            }

        if value in ValueStateValues:
            LensControlCmdString = '[LSV{}1]'.format(ValueStateValues[value])
            self.__SetHelper('LensControl', LensControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensControl')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '[LPTH?]'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'      : '0',
            'HDMI 2'      : '1',
            'DVI-D'       : '2',
            '3G-SDI'      : '3',
            'HDBaseT'     : '4'
            }

        if value in ValueStateValues:
            PIPInputCmdString = '[SSRC{}]'.format(ValueStateValues[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '[SSRC?]'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'DVI-D',
            '3': '3G-SDI',
            '4': 'HDBaseT'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'PIP': '1',
            'PBP': '2'
            }

        if value in ValueStateValues:
            PIPModeCmdString = '[PIBP{}]'.format(ValueStateValues[value])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Right': '4',
            'Bottom Left' : '5',
            'Top Left'    : '6',
            'Top Right'   : '7'
            }

        if value in ValueStateValues:
            PIPPositionCmdString = '[PILO{}]'.format(ValueStateValues[value])
            self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small' : '0',
            'Medium': '1',
            'Large' : '2'
            }

        if value in ValueStateValues:
            PIPSizeCmdString = '[PHSG{}]'.format(ValueStateValues[value])
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '[PISW1]'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            PowerCmdString = '[POWR{}]'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
    
    def UpdatePower(self, value, qualifier):

        PowerCmdString = '[POWR?]'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In':  'I',
            'Out': 'O'
            }

        if value in ValueStateValues:
            ZoomCmdString = '[ZOM{}1]'.format(ValueStateValues[value])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()