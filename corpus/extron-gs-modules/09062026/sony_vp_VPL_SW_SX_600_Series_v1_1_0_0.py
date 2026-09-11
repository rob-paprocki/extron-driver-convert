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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\["no_err"\]\r\n'), self.__MatchDeviceStatus, 'No Error')
            self.AddMatchString(re.compile(b'\[("err_(power|power2|system2|cover|light_src|lens_cover|shock|nolens|attitude|temp|fan|wheel|light_over|assy|lens_shift)",?){2,12}\]\r\n'), self.__MatchDeviceStatus, 'Multiple Errors')
            self.AddMatchString(re.compile(b'\["err_(power|power2|system2|cover|light_src|lens_cover|shock|nolens|attitude|temp|fan|wheel|light_over|assy|lens_shift)"\]\r\n'), self.__MatchDeviceStatus, 'Error')
            self.AddMatchString(re.compile(b'("standby"|"startup"|"on"|"cooling1"|"cooling2"|"saving_cooling1"|"saving_cooling2"|"saving_standby")\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\[\{"operation"\:([0-9]{1,4})\},\{"light_src"\:([0-9]{1,4})\},\{"prev_light_src"\:[0-9]{1,4}\}\]\r\n'), self.__MatchTimer, None)
            self.AddMatchString(re.compile(b'err_(cmd|option|inactive|val|auth|internal1|internal2)\r\n'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': '"4_3"',
            '16:9': '"16_9"',
            'Full 1': '"full1"',
            'Full 2': '"full2"',
            'Full 3': '"full3"',
            'Normal': '"normal"',
            'Full': '"full"',
            'Zoom': '"zoom"'
        }

        CmdString = 'aspect {0}\r\n'.format(States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'Off': '"off"',
            'On': '"on"'
        }

        CmdString = 'muting {0}\r\n'.format(States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', 'apa_exec\r\n', value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        States = {
            'Off': '"off"',
            'CC1': '"cc1"',
            'CC2': '"cc2"',
            'CC3': '"cc3"',
            'CC4': '"cc4"',
            'Text1': '"text1"',
            'Text2': '"text2"',
            'Text3': '"text3"',
            'Text4': '"text4"'
        }

        CmdString = 'cc_display {0}\r\n'.format(States[value])
        self.__SetHelper('ClosedCaption', CmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):
        self.__UpdateHelper('DeviceStatus', 'error ?\r\n', value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        States = {
            'power' 		: 'Power Supply Error',
            'power2' 		: 'Power Supply (D5V) Error',
            'system2': 'System Error 2',
            'cover' 		: 'Cover Error',
            'light_src' 	: 'Light-source Error',
            'shock' 		: 'Shock Error',
            'attitude': 'Installation Angle Error',
            'temp': 'Temperature Error',
            'fan': 'Fan Error',
            'wheel' 		: 'Wheel Rotation Error',
            'light_over': 'Luminance Error',
            'assy': 'Assembling Error',
        }

        if tag == 'No Error':
            self.WriteStatus('DeviceStatus', 'No Error', None)
        elif tag == 'Multiple Errors':
            self.WriteStatus('DeviceStatus', 'Multiple Errors', None)
        elif tag == 'Error':
            self.WriteStatus('DeviceStatus', States[match.group(1).decode()], None)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'Off': '"off"',
            'On': '"on"'
        }

        CmdString = 'controlkey_lock {0}\r\n'.format(States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'Off': '"off"',
            'On': '"on"'
        }

        CmdString = 'freeze {0}\r\n'.format(States[value])
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'Video': '"video1"',
            'S-Video': '"svideo1"',
            'RGB 1': '"rgb1"',
            'RGB 2': '"rgb2"',
            'HDMI': '"hdmi1"',
            'Network': '"network"',
            'USB A': '"usb_a"',
            'USB B': '"usb_b"'
        }

        CmdString = 'input {0}\r\n'.format(States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        States = {
            'High': '"high"',
            'Mid': '"mid"',
            'Low': '"low"',
            'Auto': '"auto"'
        }

        CmdString = 'light_output_mode {0}\r\n'.format(States[value])
        self.__SetHelper('LampMode', CmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        self.__UpdateHelper('LampUsage', 'timer ?\r\n', value, qualifier)

    def UpdateOperationHours(self, value, qualifier):
        self.__UpdateHelper('OperationHours', 'timer ?\r\n', value, qualifier)

    def __MatchTimer(self, match, tag):
        self.WriteStatus('OperationHours', int(match.group(1).decode()), None)
        self.WriteStatus('LampUsage', int(match.group(2).decode()), None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': '"menu"',
            'Up': '"up"',
            'Down': '"down"',
            'Right': '"right"',
            'Left': '"left"',
            'Enter': '"enter"',
            'Return': '"return"'
        }

        CmdString = 'key {0}\r\n'.format(States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Dynamic': '"dynamic"',
            'Standard': '"standard"',
            'Presentation': '"presentation"',
            'Blackboard': '"blackboard"',
            'Whiteboard': '"whiteboard"',
            'Cinema': '"cinema"'
        }

        CmdString = 'picture_mode {0}\r\n'.format(States[value])
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'Off': '"off"',
            'On': '"on"'
        }

        CmdString = 'power {0}\r\n'.format(States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'power_status ?\r\n', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '"standby"' 	 	: 'Off',
            '"on"'  	 		: 'On',
            '"startup"'  		: 'Startup',
            '"cooling1"' 		: 'Cooling 1',
            '"cooling2"' 		: 'Cooling 2',
            '"saving_cooling1"': 'Power Saving Cooling 1',
            '"saving_cooling2"': 'Power Saving Cooling 2',
            '"saving_standby"': 'Power Saving Standby'
        }

        value = States[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'Off': '"off"',
            'On': '"on"'
        }

        CmdString = 'blank {0}\r\n'.format(States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'volume {0}\r\n'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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

        error = match.group(1).decode()

        Errors = {
            'cmd'       : 'Unrecognized Command.',
            'inactive'  : 'Inactive Command',
            'option'    : 'Command Option Error', 
            'val'       : 'Value Error.',         
            'auth'      : 'Authentication Error', 
            'internal1' : 'Internal Error 1 : Projector is busy',
            'internal2' : 'Internal Error 2',     
            }

        self.Error([Errors[error]])

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
