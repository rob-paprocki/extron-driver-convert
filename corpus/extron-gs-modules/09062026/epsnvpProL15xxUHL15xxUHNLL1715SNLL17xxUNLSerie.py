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
            'Pro L1500UH': self.epsn_1_3757_SDI,
            'Pro L1500UHNL': self.epsn_1_3757_SDI,
            'Pro L1505UH': self.epsn_1_3757_SDI,
            'Pro L1505UHNL': self.epsn_1_3757_SDI,
            'Pro L1715SNL': self.epsn_1_3757_1715S,
            'Pro L1750UNL': self.epsn_1_3757_SDI,
            'Pro L1755UNL': self.epsn_1_3757_SDI,
            'Pro L1490U': self.epsn_1_3757_SDI,
            'Pro L1490UNL': self.epsn_1_3757_SDI,
            'Pro L1495U': self.epsn_1_3757_SDI,
            'Pro L1495UNL': self.epsn_1_3757_SDI,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetClear': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'SplitScreen': { 'Status': {}},
            'SplitScreenSize': { 'Status': {}},
            'SplitScreenSource': {'Parameters': ['Side'], 'Status': {}},
            'SplitScreenSwap': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=([023456A]0)( 30)?\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'ERR=(0[0-9A-F]|1[0-8])\r:'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=([13568AB][0-5])\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[0145])\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,5})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(0[0123459])\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r:'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)
            
            
    def SetOnConnectedString(self, value, qualifier):
    
        self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')        

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '00',
            '16:9'  : '20',
            'Auto'  : '30',
            'Full'  : '40',
            'H-Zoom': '50',
            'Native': '60',
            'V-Zoom': 'A0'
        }

        if value in ValueStateValues:
            self.__SetHelper('AspectRatio', 'ASPECT {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        self.__UpdateHelper('AspectRatio', 'ASPECT?\r', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '20': '16:9',
            '30': 'Auto',
            '40': 'Full',
            '50': 'H-Zoom',
            '60': 'Native',
            'A0': 'V-Zoom'
        }

        if match.group(2):
            value = 'Auto'
        else:
            value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'KEY 4A\r', value, qualifier)
    def SetAVMute(self, value, qualifier):


        ValueStateValues = {
            'On' : 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            self.__SetHelper('AVMute', 'MUTE {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        self.__UpdateHelper('AVMute', 'MUTE?\r', value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON' : 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        self.__UpdateHelper('DeviceStatus', 'ERR?\r', value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Fan Error',
            '03': 'Lamp Failure at Power On',
            '04': 'Internal Temperature is Abnormally High',
            '06': 'Lamp Error',
            '07': 'Lamp Cover Error',
            '08': 'Cinema Filter Error',
            '09': 'EDL Capacitor Disconnected',
            '0A': 'Auto Iris Error',
            '0B': 'Subsystem Error',
            '0C': 'Low Air Flow Error',
            '0D': 'Air Flow Error',
            '0E': 'Power Supply Error',
            '0F': 'Shutter Failure',
            '10': 'Cooling System Error',
            '11': 'Cooling System Error (Pump)',
            '12': 'Static Iris Error',
            '13': 'Power Supply Unit Error',
            '14': 'Exhaust Shutter Error',
            '15': 'Obstacle Detection Error',
            '16': 'IF Board Discernment Error',
            '17': 'Communication Error',
            '18': 'I2C Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            self.__SetHelper('Freeze', 'FREEZE {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        self.__UpdateHelper('Freeze', 'FREEZE?\r', value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON' : 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        if value in self.SetInputStateValues:
            self.__SetHelper('Input', 'SOURCE {0}\r'.format(self.SetInputStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', 'SOURCE?\r', value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.UpdateInputStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'  : '00',
            'Eco'     : '01',
            'Extended': '04',
            'Custom'  : '05'
        }

        if value in ValueStateValues:
            self.__SetHelper('LampMode', 'LUMINANCE {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        self.__UpdateHelper('LampMode', 'LUMINANCE?\r', value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Eco',
            '04': 'Extended',
            '05': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        self.__UpdateHelper('LampUsage', 'LAMP?\r', value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '03',
            'Escape': '05',
            'Enter' : '16',
            'Up'    : '35',
            'Down'  : '36',
            'Left'  : '37',
            'Right' : '38'
        }

        if value in ValueStateValues:
            self.__SetHelper('MenuNavigation', 'KEY {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'ON',
            'Off': 'OFF',
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', 'PWR {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'PWR?\r', value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
            '02': 'Warming Up',
            '03': 'Cooling Down',
            '04': 'Off', #Standby Mode (Network On)
            '05': 'Off', #Abnormality Standby
            '09': 'Off' #A/V Standby
        }

        if match.group(1).decode() == '05':
            self.Error(['Error: Abnormality Standby'])

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetClear(self, value, qualifier):

        if 1 <= int(value) <= 10:
            self.__SetHelper('PresetClear', 'ERASEMEM 02 {0:02X}\r'.format(int(value)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetClear')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 10:
            self.__SetHelper('PresetRecall', 'POPMEM 02 {0:02X}\r'.format(int(value)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):


        if 1 <= int(value) <= 10:
            self.__SetHelper('PresetSave', 'PUSHMEM 02 {0:02X}\r'.format(int(value)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On' : '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            self.__SetHelper('SplitScreen', 'SPS 01 {0}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSplitScreen')

    def SetSplitScreenSize(self, value, qualifier):

        ValueStateValues = {
            'Equal'       : '00',
            'Larger Left' : '01',
            'Larger Right': '02'
        }

        if value in ValueStateValues:
            self.__SetHelper('SplitScreenSize', 'SPS 02 {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSplitScreenSize')

    def SetSplitScreenSource(self, value, qualifier):

        SideStates = {
            'Left' : '03',
            'Right': '04'
        }

        if qualifier['Side'] in SideStates and value in self.SetInputStateValues:
            self.__SetHelper('SplitScreenSource', 'SPS {0} {1}\r'.format(SideStates[qualifier['Side']], self.SetInputStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSplitScreenSource')

    def SetSplitScreenSwap(self, value, qualifier):

        self.__SetHelper('SplitScreenSwap', 'SPS 05\r', value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeStateTable = {
            0 : 0,
            1 : 12,
            2 : 24,
            3 : 36,
            4 : 48,
            5 : 60,
            6 : 73,
            7 : 85,
            8 : 97,
            9 : 109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243
        }

        if 0 <= value <= 20:
            self.__SetHelper('Volume', 'VOL {0}\r'.format(VolumeStateTable[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'VOL?\r', value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(int(match.group(1)) / 12)
        self.WriteStatus('Volume', value, None)

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


        self.Error(['Command error.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


        if 'Serial' not in self.ConnectionType:
            self.SetOnConnectedString( None, None)
    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def epsn_1_3757_SDI(self):

        self.SetInputStateValues = {
            'D-SUB'         : '10',
            'RGB'           : '11',
            'Component'     : '14',
            'HDMI'          : '30',
            'LAN'           : '53',
            'SDI'           : '60',
            'HDBaseT'       : '80',
            'DVI-D'         : 'A0',
            'BNC'           : 'B0',
            'BNC (RGB)'     : 'B1',
            'BNC (Component)': 'B4'
        }

        self.UpdateInputStateValues = {
            '31' : 'D-RGB',
            '33' : 'RGB-Video',
            '34' : 'YCbCr',
            '35' : 'YPbPr',
            '64' : 'SDI (YCbCr)',
            '65' : 'SDI (YPbPr)',
            '81' : 'HDBaseT (Digital-RGB)',
            '83' : 'HDBaseT (RGB-Video)',
            '84' : 'HDBaseT (YCbCr)',
            '85' : 'HDBaseT (YPbPr)',
            'A1' : 'DVI-D (Digital-RGB)',
            'A3' : 'DVI-D (RGB-Video)',
            '10' : 'D-SUB',
            '11' : 'RGB',
            '14' : 'Component',
            '30' : 'HDMI',
            '53' : 'LAN',
            '60' : 'SDI',
            '80' : 'HDBaseT',
            'A0' : 'DVI-D',
            'B0' : 'BNC',
            'B1' : 'BNC (RGB)',
            'B4' : 'BNC (Component)'
        }



    def epsn_1_3757_1715S(self):

        self.SetInputStateValues = {
            'D-SUB'         : '10',
            'RGB'           : '11',
            'Component'     : '14',
            'HDMI'          : '30',
            'LAN'           : '53',
            'HDBaseT'       : '80',
            'DVI-D'         : 'A0',
            'BNC'           : 'B0',
            'BNC (RGB)'     : 'B1',
            'BNC (Component)': 'B4'
        }

        self.UpdateInputStateValues = {
            '31' : 'D-RGB',
            '33' : 'RGB-Video',
            '34' : 'YCbCr',
            '35' : 'YPbPr',
            '81' : 'HDBaseT (Digital-RGB)',
            '83' : 'HDBaseT (RGB-Video)',
            '84' : 'HDBaseT (YCbCr)',
            '85' : 'HDBaseT (YPbPr)',
            'A1' : 'DVI-D (Digital-RGB)',
            'A3' : 'DVI-D (RGB-Video)',
            '10' : 'D-SUB',
            '11' : 'RGB',
            '14' : 'Component',
            '30' : 'HDMI',
            '53' : 'LAN',
            '80' : 'HDBaseT',
            'A0' : 'DVI-D',
            'B0' : 'BNC',
            'B1' : 'BNC (RGB)',
            'B4' : 'BNC (Component)'
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
