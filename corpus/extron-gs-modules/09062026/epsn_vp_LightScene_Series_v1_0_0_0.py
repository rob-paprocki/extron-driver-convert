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
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LaserMode': { 'Status': {}},
            'LaserUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }                   
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=([02-6]0)( 30)?\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'ERR=([01][\d\w])\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'SOURCE=(30|52|53|57|58)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[0145])\r'), self.__MatchLaserMode, None)
            self.AddMatchString(re.compile(b'LAMP=([\d]+)\r'), self.__MatchLaserUsage, None)
            self.AddMatchString(re.compile(b'PWR=(0[0-5])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal'    : '00',
            '16:9'      : '20',
            'Auto'      : '30',
            'Full'      : '40',
            'Zoom'      : '50',
            'Native'    : '60'
        }

        AspectRatioCmdString = 'ASPECT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '00' : 'Normal', 
            '20' : '16:9', 
            '30' : 'Auto', 
            '40' : 'Full', 
            '50' : 'Zoom', 
            '60' : 'Native'
        }
        if match.group(2):
            value = 'Auto'
        else:
            value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE ON\r'
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Fan Error',
            '03': 'Lamp Failure at Power On',
            '04': 'High Internal Temperature Error',
            '06': 'Lamp Error',
            '07': 'Open Lamp Cover Door Error',
            '08': 'Cinema Filter Error',
            '09': 'Electric Dual-Layered Capacitor is Disconnected',
            '0A': 'Auto Iris Error',
            '0B': 'Subsystem Error',
            '0C': 'Low Air Flow Error',
            '0D': 'Air Filter Air Flow Sensor Error',
            '0E': 'Power Supply Unit Error (Ballast)',
            '0F': 'Shutter Error',
            '10': 'Cooling System Error (Peltiert Element)',
            '11': 'Cooling System Error (Pump)',
            '12': 'Static Iris Error',
            '13': 'Power Supply Unit Error (Disagreement of Ballast)',
            '14': 'Exhaust Shutter Error',
            '15': 'Obstacle Detection Error',
            '16': 'IF Board Discernment Error',
            '17': 'Communication Error of "Stack Projection Function"',
            '18': 'I2C Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Increment' : 'KEY 2A\r',
            'Decrement' : 'KEY 2B\r'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI'      : '30',
            'LAN'       : '53',
            'SD Player' : '57', 
            'Spotlight' : '58'
        }

        InputCmdString = 'SOURCE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '30' : 'HDMI', 
            '53' : 'LAN', 
            '57' : 'SD Player', 
            '58' : 'Spotlight'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLaserMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'    : '00',
            'Eco'       : '01',
            'Extended'  : '04',
            'Custom'    : '05'
        }

        LaserModeCmdString = 'LUMINANCE {}\r'.format(ValueStateValues[value])
        self.__SetHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def UpdateLaserMode(self, value, qualifier):

        LaserModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def __MatchLaserMode(self, match, tag):

        ValueStateValues = {
            '00' : 'Normal', 
            '01' : 'Eco', 
            '04' : 'Extended', 
            '05' : 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LaserMode', value, None)

    def UpdateLaserUsage(self, value, qualifier):

        LaserUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LaserUsage', LaserUsageCmdString, value, qualifier)

    def __MatchLaserUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LaserUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'      : '3C',
            'Escape'    : '3D',
            'Enter'     : '49',
            'Up'        : '58',
            'Down'      : '59',
            'Left'      : '5A',
            'Right'     : '5B'
        }

        MenuNavigationCmdString = 'KEY {}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PWR ON\r',
            'Off' : 'PWR OFF\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01' : 'On',
            '00' : 'Off',
            '02' : 'Warming Up', 
            '03' : 'Cooling Down',
            '04' : 'Off',   # Standby Mode (Network ON)
            '05' : 'Off'    # Abnormality Standby
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        VolumeValues = {
            0   : '0',
            1   : '12',
            2   : '24',
            3   : '36',
            4   : '48',
            5   : '60',
            6   : '73',
            7   : '85',
            8   : '97',
            9   : '109',
            10  : '121',
            11  : '134',
            12  : '146',
            13  : '158',
            14  : '170',
            15  : '182',
            16  : '195',
            17  : '207',
            18  : '219',
            19  : '231',
            20  : '243'
        }

        if value in VolumeValues:
            VolumeCmdString = 'VOL {}\r'.format(VolumeValues[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) // 12
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Increment' : 'KEY 2E\r',
            'Decrement' : 'KEY 2F\r'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
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

        self.Error(['Error occurred.'])

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
