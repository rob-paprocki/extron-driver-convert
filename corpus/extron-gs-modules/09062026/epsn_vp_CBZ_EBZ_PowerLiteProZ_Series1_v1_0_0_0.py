from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(20|20 30|40|50|60)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'CCAP=(00|1[1-2])\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'ERR=([0-1][0-9A-F])\r:'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(10|11|14|30|40|41|42|53|60|80|A0|B0|B1|B4)\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(00|01)\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,5}) ([0-9]{1,5})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(00|01|02|03|05)\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r'), self.__MatchVideoMute, None)

    def SetAspectRatio(self, value, qualifier):

        AspectStateValues = {
            '16:9': '20',
            'Auto': '30',
            'Full': '40',
            'Zoom': '50',
            'Native': '60'
        }
        AspectCmdString = 'ASPECT {0}\r'.format(AspectStateValues[value])

        self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectStateNames = {
            '20': '16:9',
            '20 30': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native'
        }
        value = AspectStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        CommandString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', CommandString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionControls = {
            'CC1': '11',
            'CC2': '12',
            'Off': '00'
        }

        CommandString = 'CCAP {0}\r'.format(ClosedCaptionControls[value])
        self.__SetHelper('ClosedCaption', CommandString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        CommandString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', CommandString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionNames = {
        '11': 'CC1',
        '12': 'CC2',
        '00': 'Off'
        }

        value = ClosedCaptionNames[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        if 'Serial' in self.ConnectionType:
            DeviceStatusCmdString = 'ERR?\r'
            self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateDeviceStatus')

    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusStateNames = {
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
            '16': 'IF board discernment error',
        }
        value = DeviceStatusStateNames[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': 'ON',
            'Off': 'OFF',
            }

        FreezeCmdString = 'FREEZE {0}\r'.format(FreezeStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):

        FreezeStateNames = {
            'ON': 'On',
            'OFF': 'Off',
            }
        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Input 1 D-Sub': '10',
            'Input 1 RGB Analog': '11',
            'Input 1 Component': '14',
            'Input 3 HDMI': '30',
            'Video': '40',
            'Video (RCA)': '41',
            'S-Video': '42',
            'LAN': '53',
            'SDI': '60',
            'HDBaseT': '80',
            'DVI': 'A0',
            'Input 4 (BNC)': 'B0',
            'Input 4 RGB Analog': 'B1',
            'Input 4 Component': 'B4'
        }
        InputCmdString = 'SOURCE {0}\r'.format(InputStateValues[value])

        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputStateNames = {
            '10': 'Input 1 D-Sub',
            '11': 'Input 1 RGB Analog',
            '14': 'Input 1 Component',
            '30': 'Input 3 HDMI',
            '40': 'Video',
            '41': 'Video (RCA)',
            '42': 'S-Video',
            '53': 'LAN',
            '60': 'SDI',
            '80': 'HDBaseT',
            'A0': 'DVI',
            'B0': 'Input 4 (BNC)',
            'B1': 'Input 4 RGB Analog',
            'B4': 'Input 4 Component'
        }
        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal': '00',
            'Eco': '01'
        }
        LampModeCmdString = 'LUMINANCE {0}\r'.format(LampModeStateValues[value])

        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeStateNames = {
            '00': 'Normal',
            '01': 'Eco'
        }
        value = LampModeStateNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, qualifier):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, {'Lamp': '1'})
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, {'Lamp': '2'})

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': '03',
            'Exit': '05',
            'Enter': '16',
            'Up': '35',
            'Down': '36',
            'Left': '37',
            'Right': '38',
        }
        MenuNavigationCmdString = 'KEY {0}\r'.format(MenuNavigationStateValues[value])

        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': 'ON',
            'Off': 'OFF',
        }
        PowerCmdString = 'PWR {0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '00': 'Off',
            '01': 'On',
            '02': 'Warming',
            '03': 'Cooling',
            '05': 'Abnormality Standby'
        }
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': 'ON',
            'Off': 'OFF',
            }
        VideoMuteCmdString = 'MUTE {0}\r'.format(VideoMuteStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteStateNames = {
            'ON': 'On',
            'OFF': 'Off',
            }
        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result
