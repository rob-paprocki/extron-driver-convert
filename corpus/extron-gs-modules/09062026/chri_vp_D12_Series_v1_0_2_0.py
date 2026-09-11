from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp Number'], 'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'PresentationMode': {'Status': {}},
            'Shutter': {'Status': {}},
            'UserDefinedString': {'Status': {}}
            }

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(SZP!([0-8])\)'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\(FRZ!(0|1)\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN\+MAIN!((1|)([0-9]{1,2}))\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(LPM!([0-2])\)'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\(LOP!([1-3])\)'), self.__MatchLampSelect, None)
            self.AddMatchString(re.compile(b'\(LIF\+LP(1|2)H!(\d+)\)'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\(OSD!(0|1)\)'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\(LIF\+LPTH!(\d+)\)'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'\(PIP!(0|1)\)'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\(PWR!(0|1|10|11)\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(PST!([0-7])\)'), self.__MatchPresentationMode, None)
            self.AddMatchString(re.compile(b'\(SHU!(0|1)\)'), self.__MatchShutter, None)

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Auto': '(SZP0)',
            'Full Size': '(SZP4)',
            'Full Width': '(SZP5)',
            'Full Height': '(SZP6)',
            'Native': '(SZP1)',
            'Custom': '(SZP7)',
            '4:3': '(SZP2)',
            'Letterbox': '(SZP3)',
            '3D Mode': '(SZP8)'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = '(SZP?)'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ValueStateValues = {
            '0': 'Auto',
            '4': 'Full Size',
            '5': 'Full Width',
            '6': 'Full Height',
            '1': 'Native',
            '7': 'Custom',
            '2': '4:3',
            '3': 'Letterbox',
            '8': '3D Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = '(AIM 0)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On': '(FRZ1)',
            'Off': '(FRZ0)'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        FreezeCmdString = '(FRZ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'VGA'         : '(SIN+MAIN 1)', 
            'BNC'         : '(SIN+MAIN 2)', 
            'HDMI 1'      : '(SIN+MAIN 3)', 
            'HDMI 2'      : '(SIN+MAIN 4)', 
            'DVI-D'       : '(SIN+MAIN 5)', 
            'DisplayPort' : '(SIN+MAIN 6)', 
            '3G-SDI'      : '(SIN+MAIN 7)', 
            'HDBaseT'     : '(SIN+MAIN 8)', 
            'CVBS'        : '(SIN+MAIN 9)', 
            'Presenter'   : '(SIN+MAIN 10)', 
            'Card Reader' : '(SIN+MAIN 11)', 
            'Mini USB'    : '(SIN+MAIN 12)'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputCmdString = '(SIN+MAIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ValueStateValues = {
            '1': 'VGA',
            '2': 'BNC',
            '3': 'HDMI 1',
            '4': 'HDMI 2',
            '5': 'DVI-D',
            '6': 'DisplayPort',
            '7': '3G-SDI',
            '8': 'HDBaseT',
            '9': 'CVBS',
            '10': 'Presenter',
            '11': 'Card Reader',
            '12': 'Mini USB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):
        ValueStateValues = {
            'High': '(LPM1)',
            'Eco': '(LPM2)',
            'Power': '(LPM0)'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeCmdString = '(LPM?)'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):
        ValueStateValues = {
            '1': 'High',
            '2': 'Eco',
            '0': 'Power'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def SetLampSelect(self, value, qualifier):
        ValueStateValues = {
            'Lamp 1 Only': '(LOP1)',
            'Lamp 2 Only': '(LOP2)',
            'Lamp 1 and 2': '(LOP3)'
        }

        LampSelectCmdString = ValueStateValues[value]
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):
        LampSelectCmdString = '(LOP?)'
        self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def __MatchLampSelect(self, match, tag):
        ValueStateValues = {
            '1': 'Lamp 1 Only',
            '2': 'Lamp 2 Only',
            '3': 'Lamp 1 and 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampSelect', value, None)

    def UpdateLampUsage(self, value, qualifier):
        lamp = qualifier['Lamp Number']
        if lamp in ['1', '2']:
            LampUsageCmdString = '(LIF+LP{}H?)'.format(lamp)
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, tag):

        qualifier = {}
        qualifier['Lamp Number'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On': '(OSD1)',
            'Off': '(OSD0)'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayCmdString = '(OSD?)'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def UpdateOperationHours(self, value, qualifier):
        OperationHoursCmdString = '(LIF+LPTH?)'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPMode(self, value, qualifier):
        ValueStateValues = {
            'On': '(PIP1)',
            'Off': '(PIP0)'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier, 3)

    def UpdatePIPMode(self, value, qualifier):
        PIPModeCmdString = '(PIP?)'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': '(PWR1)',
            'Off': '(PWR0)',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 10)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '10': 'Cooling Down',
            '11': 'Warming Up'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresentationMode(self, value, qualifier):
        ValueStateValues = {
            'Presentation': '(PST0)',
            'Video': '(PST1)',
            'Bright': '(PST2)',
            'Real': '(PST3)',
            'DICOM SIM': '(PST4)',
            '2D High Speed': '(PST5)',
            'User': '(PST7)'
        }

        PresentationModeCmdString = ValueStateValues[value]
        self.__SetHelper('PresentationMode', PresentationModeCmdString, value, qualifier)

    def UpdatePresentationMode(self, value, qualifier):
        PresentationModeCmdString = '(PST?)'
        self.__UpdateHelper('PresentationMode', PresentationModeCmdString, value, qualifier)

    def __MatchPresentationMode(self, match, tag):
        ValueStateValues = {
            '0': 'Presentation',
            '1': 'Video',
            '2': 'Bright',
            '3': 'Real',
            '4': 'DICOM SIM',
            '5': '2D High Speed',
            '6': '3D',
            '7': 'User'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationMode', value, None)

    def SetShutter(self, value, qualifier):
        ValueStateValues = {
            'On': '(SHU1)',
            'Off': '(SHU0)'
        }

        ShutterCmdString = ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier, 3)

    def UpdateShutter(self, value, qualifier):
        ShutterCmdString = '(SHU?)'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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
