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
        self.Models = {
            'dVision 30 Series': self.dpl_1_2004_D30,
            'iVision 20 Series': self.dpl_1_2004_I20,
            'iVision 30 Series': self.dpl_1_2004_I30,
            'dVision 30-1080p XB': self.dpl_1_2004_D30,
            'dVision 30-1080p XC': self.dpl_1_2004_D30,
            'dVision 30-1080p XL': self.dpl_1_2004_D30,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'Lamp1Status': {'Status': {}},
            'Lamp1Usage': {'Status': {}},
            'Lamp2Status': {'Status': {}},
            'Lamp2Usage': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampStatus': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\%001 SABS 0000(00|01|02|03|04|09|10)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\%001 FRZE 00000(0|1)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\%001 GABS 00000(0|1|2|3|7|8)\r'), self.__MatchGamma, None)
            self.AddMatchString(re.compile(b'\%001 IABS 00000(0|1|2|4|5|6|7|8)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\%001 LST1 00000(0|1|2|3|4|5)\r'), self.__MatchLampStatus, None)
            self.AddMatchString(re.compile(b'\%001 LTR1 ([0-9]{6})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\%001 LST2 00000(0|1|2|3|4|5)\r'), self.__MatchLamp2Status, None)
            self.AddMatchString(re.compile(b'\%001 LTR2 ([0-9]{6})\r'), self.__MatchLamp2Usage, None)
            self.AddMatchString(re.compile(b'\%001 ECOM 00000(0|1)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\%001 LMOD 00000(0|1|2|3)\r'), self.__MatchLampSelect, None)
            self.AddMatchString(re.compile(b'\%001 OSDC 00000(0|1|2)\r'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\%001 UTOT ([0-9]{6})\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\%001 POST 00000(0|1|2|3|4|5|6)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\%001 ISTS 00000(0|1)\r'), self.__MatchSignalStatus, None)
            self.AddMatchString(re.compile(b'\%001 PMUT 00000(0|1)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\!0000[1-4]|e00001'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1' 						: '0',
            'Fill All' 					: '1',
            'Fill Aspect Ratio' 		: '2',
            'Fill 16:9' 				: '3',
            'Fill 4:3' 					: '4',
            'Fill Letterbox to 16:9' 	: '9',
            'Fill Letterbox st to 16:9': '10'
        }

        AspectRatioCmdString = ':SABS{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = ':SABS?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '00': '1:1',
            '01': 'Fill All',
            '02': 'Fill Aspect Ratio',
            '03': 'Fill 16:9',
            '04': 'Fill 4:3',
            '09': 'Fill Letterbox to 16:9',
            '10': 'Fill Letterbox st to 16:9'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = ':AUTO\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):
        cmdString = ':POST?\r'
        self.__UpdateHelper('DeviceStatus', cmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = ':FRZE{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = ':FRZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            'Film 1': '0',
            'Film 2': '1',
            'Video 1': '2',
            'Video 2': '3',
            'Computer 1': '7',
            'Computer 2': '8'
        }

        GammaCmdString = ':GABS{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        GammaCmdString = ':GABS?\r'
        self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)

    def __MatchGamma(self, match, tag):

        ValueStateValues = {
            '0': 'Film 1',
            '1': 'Film 2',
            '2': 'Video 1',
            '3': 'Video 2',
            '7': 'Computer 1',
            '8': 'Computer 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Gamma', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = ':IABS{0}\r'.format(self.SetInputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = ':IABS?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.UpdateInputStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLamp1Status(self, value, qualifier):

        Lamp1StatusCmdString = ':LST1?\r'
        self.__UpdateHelper('Lamp1Status', Lamp1StatusCmdString, value, qualifier)

    def UpdateLamp1Usage(self, value, qualifier):

        Lamp1UsageCmdString = ':LTR1?\r'
        self.__UpdateHelper('Lamp1Usage', Lamp1UsageCmdString, value, qualifier)

    def UpdateLamp2Status(self, value, qualifier):

        Lamp2StatusCmdString = ':LST2?\r'
        self.__UpdateHelper('Lamp2Status', Lamp2StatusCmdString, value, qualifier)

    def __MatchLamp2Status(self, match, tag):

        ValueStateValues = {
            '0': 'Broken',
            '1': 'Warming Up',
            '2': 'On',
            '3': 'Off',
            '4': 'Cooling Down',
            '5': 'Not Present'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Lamp2Status', value, None)

    def UpdateLamp2Usage(self, value, qualifier):

        Lamp2UsageCmdString = ':LTR2?\r'
        self.__UpdateHelper('Lamp2Usage', Lamp2UsageCmdString, value, qualifier)

    def __MatchLamp2Usage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Lamp2Usage', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': '1',
            'Normal': '0'
        }

        LampModeCmdString = ':ECOM{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = ':ECOM?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '1': 'Eco',
            '0': 'Normal'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Single 1': '0',
            'Single 2': '1',
            'Dual': '2',
            'Auto': '3'
        }

        LampSelectCmdString = ':LMOD{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        LampSelectCmdString = ':LMOD?\r'
        self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def __MatchLampSelect(self, match, tag):

        ValueStateValues = {
            '0': 'Single 1',
            '1': 'Single 2',
            '2': 'Dual',
            '3': 'Auto'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampSelect', value, None)

    def UpdateLampStatus(self, value, qualifier):

        LampStatusCmdString = ':LST1?\r'
        self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)

    def __MatchLampStatus(self, match, tag):

        value = self.LampStatusValues[match.group(1).decode()]
        if self.numberLamps > 1:
            self.WriteStatus('Lamp1Status', value, None)
        else:
            self.WriteStatus('LampStatus', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = ':LTR1?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)
        if self.numberLamps > 1:
            self.WriteStatus('Lamp1Usage', value, None)
        else:
            self.WriteStatus('LampUsage', value, None)


    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu' 	: 'MENU',
            'Up' 	: 'NVUP',
            'Down' 	: 'NVDW',
            'Left' 	: 'NVLF',
            'Right': 'NVRH',
            'Ok' 	: 'NVOK'
        }

        MenuNavigationCmdString = ':{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '0',
            'Show Only Warnings': '1'
        }

        OnScreenDisplayCmdString = ':OSDC{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = ':OSDC?\r'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '0': 'Off',
            '1': 'Show Only Warnings'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = ':UTOT?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = ':POWR{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = ':POST?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Off',
            '2': 'Warming Up',
            '3': 'On',
            '4': 'Cooling Down',
            '5': 'Cooling Down',
            '6': 'Off'
        }

        DeviceStatusValues = {
            '0': 'Deep Sleep',
            '1': 'Normal',
            '2': 'Normal',
            '3': 'Normal',
            '4': 'Normal',
            '5': 'Critical Powering Down',
            '6': 'Critical Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

        status = DeviceStatusValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', status, None)

    def UpdateSignalStatus(self, value, qualifier):

        SignalStatusCmdString = ':ISTS?\r'
        self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)

    def __MatchSignalStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Searching',
            '1': 'Locked to Source'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SignalStatus', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = ':PMUT{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = ':PMUT?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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


        ErrorStringValues = {
        	'1' : 'Access Denied',
        	'2' : 'Not Available',
        	'3' : 'Not Implemented',
        	'4' : 'Value out of Range'
        }

        value = match.group(0).decode()

        if value[0] == 'e':
        	errorstring = 'Extended Info'
        else:
        	errorstring = ErrorStringValues[value[-1]]

        self.Error([errorstring])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def dpl_1_2004_I20(self):	
        self.numberLamps = 1
        self.SetInputStateValues = {
            'VGA' 		: '0', 
            'DVI' 		: '2', 
            'S-Video' 	: '4', 
            'Composite' : '5', 
            'Component' : '6', 
            'RGBs' 		: '7', 
            'HDMI' 		: '8'
        }

        self.UpdateInputStateValues = {
            '0' : 'VGA',  
            '2' : 'DVI', 
            '4' : 'S-Video', 
            '5' : 'Composite', 
            '6' : 'Component', 
            '7' : 'RGBs', 
            '8' : 'HDMI'
        }

        self.LampStatusValues = {
            '0' : 'Broken', 
            '1' : 'Warming Up', 
            '2' : 'On', 
            '3' : 'Off', 
            '4' : 'Cooling Down'
        }
        

    def dpl_1_2004_I30(self):
    
        self.numberLamps = 1
        self.SetInputStateValues = {
            'VGA 1' 	: '0', 
            'VGA 2' 	: '1', 
            'DVI' 		: '2', 
            'S-Video' 	: '4', 
            'Composite' : '5', 
            'Component' : '6', 
            'RGBs' 		: '7', 
            'HDMI' 		: '8'
        }

        self.UpdateInputStateValues = {
            '0' : 'VGA 1', 
            '1' : 'VGA 2', 
            '2' : 'DVI', 
            '4' : 'S-Video', 
            '5' : 'Composite', 
            '6' : 'Component', 
            '7' : 'RGBs', 
            '8' : 'HDMI'
        }

        self.LampStatusValues = {
            '0' : 'Broken', 
            '1' : 'Warming Up', 
            '2' : 'On', 
            '3' : 'Off', 
            '4' : 'Cooling Down'
        }
        
    def dpl_1_2004_D30(self):
    
        self.numberLamps = 2
        self.SetInputStateValues = {
            'VGA' 		: '0', 
            'BNC' 		: '1', 
            'DVI' 		: '2', 
            'S-Video' 	: '4', 
            'Composite' : '5', 
            'Component' : '6', 
            'RGBs' 		: '7', 
            'HDMI' 		: '8'
        }

        self.UpdateInputStateValues = {
            '0' : 'VGA', 
            '1' : 'BNC', 
            '2' : 'DVI', 
            '4' : 'S-Video', 
            '5' : 'Composite', 
            '6' : 'Component', 
            '7' : 'RGBs', 
            '8' : 'HDMI'
        }

        self.LampStatusValues = {
            '0' : 'Broken', 
            '1' : 'Warming Up', 
            '2' : 'On', 
            '3' : 'Off', 
            '4' : 'Cooling Down',
            '5' : 'Not Present'
        }
        
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

