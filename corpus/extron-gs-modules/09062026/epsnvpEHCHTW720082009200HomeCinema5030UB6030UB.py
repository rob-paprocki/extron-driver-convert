from extronlib.interface import EthernetClientInterface, SerialInterface, IRInterface, RelayInterface
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
        self.Models = {
            'EH-TW9200': self.epsn_1_2464_other,
            'EH-TW7200': self.epsn_1_2464_other,
            'EH-TW8200': self.epsn_1_2464_other,
            'EH-TW8200W': self.epsn_1_2464_other,
            'EH-TW9200W': self.epsn_1_2464_other,
            'CH-TW7200': self.epsn_1_2464_other,
            'CH-TW8200': self.epsn_1_2464_other,
            'CH-TW8200W': self.epsn_1_2464_other,
            'CH-TW9200': self.epsn_1_2464_other,
            'CH-TW9200W': self.epsn_1_2464_other,
            'PL-HomeCinema 5030UB': self.epsn_1_2464_other,
            'PL-HomeCinema 5030UBe': self.epsn_1_2464_other,
            'PL-ProCinema 6030UB': self.epsn_1_2464_6030,
            'PL-ProCinema 4030': self.epsn_1_2464_other,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AVMute': {'Status': {}},
            'ColorMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(00|30|40|50|80|90)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CMODE=(06|07|0C|13|15|17|18|19|20)\r'), self.__MatchColorMode, None)
            self.AddMatchString(re.compile(b'ERR=([0-9A-F]{2})\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'SOURCE=([0-9A-F]{2})\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(00|01)\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,5})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(00|01|02|03|05|07)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ERR\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AspectValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        value = self.AspectNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'MUTE ON\r',
            'Off': 'MUTE OFF\r'
        }

        AVMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 'CMODE 06\r',
            'Natural': 'CMODE 07\r',
            'Living': 'CMODE 0C\r',
            'THX': 'CMODE 13\r',
            'Cinema': 'CMODE 15\r',
            '3D Cinema': 'CMODE 17\r',
            '3D Dynamic': 'CMODE 18\r',
            '3D THX': 'CMODE 19\r',
            'B&W Cinema': 'CMODE 20\r'
        }

        ColorModeCmdString = ValueStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        ColorModeCmdString = 'CMODE?\r'
        self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def __MatchColorMode(self, match, tag):

        ValueStateValues = {
            '06': 'Dynamic',
            '07': 'Natural',
            '0C': 'Living',
            '13': 'THX',
            '15': 'Cinema',
            '17': '3D Cinema',
            '18': '3D Dynamic',
            '19': '3D THX',
            '20': 'B&W Cinema'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ColorMode', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Fan error',
            '03': 'Lamp failure at power on',
            '04': 'High internal temperature error',
            '06': 'Lamp error',
            '07': 'Open lamp cover door error',
            '08': 'Cinema filter error',
            '09': 'Electric dual-layered capacitor is disconnected',
            '0A': 'Auto iris error',
            '0B': 'Subsystem error',
            '0C': 'Low air flow error',
            '0D': 'Air filter air flow sensor error',
            '0E': 'Power supply unit error (Ballast)',
            '0F': 'Shutter error',
            '10': 'Cooling system error (peltiert element)',
            '11': 'Cooling system error (pump)',
            '12': 'Static iris error',
            '13': 'Power supply unit error (disagreement of Ballast)',
            '14': 'Exhaust shutter error',
            '15': 'Obstacle detection error',
            '16': 'IF board discernment error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Component': 'SOURCE 10\r',
            'YCbCr 1': 'SOURCE 14\r',
            'YPbPr 1': 'SOURCE 15\r',
            'Auto': 'SOURCE 1F\r',
            'D-sub 15': 'SOURCE 20\r',
            'RGB': 'SOURCE 21\r',
            'HDMI 1': 'SOURCE 30\r',
            'Digital-RGB 1': 'SOURCE 31\r',
            'RGB-Video 1': 'SOURCE 33\r',
            'YCbCr 2': 'SOURCE 34\r',
            'YPbPr 2': 'SOURCE 35\r',
            'Video': 'SOURCE 40\r',
            'Video-RCA': 'SOURCE 41\r',
            'HDMI 2': 'SOURCE A0\r',
            'Digital-RGB 2': 'SOURCE A1\r',
            'RGB-Video 2': 'SOURCE A3\r',
            'YCbCr 3': 'SOURCE A4\r',
            'YPbPr 3': 'SOURCE A5\r',
            'Wireless HD': 'SOURCE D0\r',
            'Digital-RGB 3': 'SOURCE D1\r',
            'RGB-Video 3': 'SOURCE D3\r',
            'YCbCr 4': 'SOURCE D4\r',
            'YPbPr 4': 'SOURCE D5\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '10': 'Component',
            '14': 'YCbCr 1',
            '15': 'YPbPr 1',
            '1F': 'Auto',
            '20': 'D-sub 15',
            '21': 'RGB',
            '30': 'HDMI 1',
            '31': 'Digital-RGB 1',
            '33': 'RGB-Video 1',
            '34': 'YCbCr 2',
            '35': 'YPbPr 2',
            '40': 'Video',
            '41': 'Video-RCA',
            'A0': 'HDMI 2',
            'A1': 'Digital-RGB 2',
            'A3': 'RGB-Video 2',
            'A4': 'YCbCr 3',
            'A5': 'YPbPr 3',
            'D0': 'Wireless HD',
            'D1': 'Digital-RGB 3',
            'D3': 'RGB-Video 3',
            'D4': 'YCbCr 4',
            'D5': 'YPbPr 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'LUMINANCE 00\r',
            'Eco': 'LUMINANCE 01\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Eco'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'KEY 03\r',
            'Esc': 'KEY 05\r',
            'Enter': 'KEY 16\r',
            'Up': 'KEY 35\r',
            'Down': 'KEY 36\r',
            'Left': 'KEY 37\r',
            'Right': 'KEY 38\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PWR ON\r',
            'Off': 'PWR OFF\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
            '02': 'Warming Up',
            '03': 'Cooling Down',
            '05': 'Abnormality Standby',
            '07': 'Wireless HD Standby'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 'KEY 56\r',
            'Down': 'KEY 57\r'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

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

    def __MatchError(self, match, tag):
        print('An error occurred')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0        

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False        

    def epsn_1_2464_6030(self):       
        self.AspectValues = {
            'Normal'     : 'ASPECT 00\r', 
            'Auto'       : 'ASPECT 30\r', 
            'Full'       : 'ASPECT 40\r', 
            'Zoom'       : 'ASPECT 50\r', 
            'Anamorphic' : 'ASPECT 80\r', 
            'H Squeeze'  : 'ASPECT 90\r'
        }
        self.AspectNames = {
            '00' : 'Normal', 
            '30' : 'Auto', 
            '40' : 'Full', 
            '50' : 'Zoom', 
            '80' : 'Anamorphic', 
            '90' : 'H Squeeze'
        }
        
    def epsn_1_2464_other(self):
        self.AspectValues = {
            'Normal' : 'ASPECT 00\r', 
            'Auto'   : 'ASPECT 30\r', 
            'Full'   : 'ASPECT 40\r', 
            'Zoom'   : 'ASPECT 50\r'
        }
        self.AspectNames = {
            '00' : 'Normal', 
            '30' : 'Auto', 
            '40' : 'Full', 
            '50' : 'Zoom'
        }

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
