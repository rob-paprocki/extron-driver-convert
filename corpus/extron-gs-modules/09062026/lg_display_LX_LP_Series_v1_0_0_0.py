from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time

class DeviceClass():
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DeviceID = '1'

        #Do not change this the variables values below
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
            'AspectRatio'       : {'Status': {}},
            'AudioMute'         : {'Status': {}},
            'AutoImage'         : {'Status': {}},
            'ChannelStep'       : {'Status': {}},
            'ClosedCaption'     : {'Status': {}},
            'ExecutiveMode'     : {'Status': {}},
            'Freeze'            : {'Status': {}},
            'Input'             : {'Status': {}},
            'Keypad'            : {'Status': {}},
            'MenuNavigation'    : {'Status': {}},
            'OnScreenDisplay'   : {'Status': {}},
            'PIPInput'          : {'Status': {}},
            'PIPMode'           : {'Status': {}},
            'PIPPosition'       : {'Status': {}},
            'PIPSwap'           : {'Status': {}},
            'Power'             : {'Status': {}},
            'VideoMute'         : {'Status': {}},
            'Volume'            : {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK(01|02|03|04|05|06|10|11|12|13|14|15|16|17|18|19|1A|1B|1C|1D|1E|1F)x',re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK0([0-2])x',re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2} OK0(0|1)x',re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK(00|01|10|11|20|21|40|41|50|60|90)x',re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9a-f]{2} OK0(0|1)x',re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'y [0-9a-f]{2} OK(00|01|10|11|20|21)x',re.I), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'n [0-9a-f]{2} OK0(0|1|2|5)x',re.I), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'q [0-9a-f]{2} OK0([0-3])x',re.I), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK0(0|1)x',re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK0(0|1)x',re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-fA-F]{2})x',re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|m|b|l|y|n|q|a|d|f) [0-9a-f]{2} NG(.*)x',re.I), self.__MatchError, None)

    def SetDeviceID(self, DeviceID):
        if DeviceID == 'Broadcast':
            self.DeviceID = '00'
        else:
            self.DeviceID = '{0:02X}'.format(int(DeviceID))
    
    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Normal (4:3)'          : '01',
            'Widescreen (16:9)'     : '02',
            'Horizon'               : '03',
            'Zoom 1'                : '04',
            'Zoom 2'                : '05',
            'Auto (Set by Program)' : '06', 
            'Cinema Zoom 1'         : '10',
            'Cinema Zoom 2'         : '11',
            'Cinema Zoom 3'         : '12',
            'Cinema Zoom 4'         : '13',
            'Cinema Zoom 5'         : '14',
            'Cinema Zoom 6'         : '15',
            'Cinema Zoom 7'         : '16',
            'Cinema Zoom 8'         : '17',
            'Cinema Zoom 9'         : '18',
            'Cinema Zoom 10'        : '19',
            'Cinema Zoom 11'        : '1A',
            'Cinema Zoom 12'        : '1B',
            'Cinema Zoom 13'        : '1C',
            'Cinema Zoom 14'        : '1D',
            'Cinema Zoom 15'        : '1E',
            'Cinema Zoom 16'        : '1F'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = 'kc {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ValueStateValues = {
            '01' : 'Normal (4:3)', 
            '02' : 'Widescreen (16:9)', 
            '03' : 'Horizon', 
            '04' : 'Zoom 1', 
            '05' : 'Zoom 2', 
            '06' : 'Auto (Set by Program)', 
            '10' : 'Cinema Zoom 1', 
            '11' : 'Cinema Zoom 2', 
            '12' : 'Cinema Zoom 3', 
            '13' : 'Cinema Zoom 4', 
            '14' : 'Cinema Zoom 5', 
            '15' : 'Cinema Zoom 6', 
            '16' : 'Cinema Zoom 7', 
            '17' : 'Cinema Zoom 8', 
            '18' : 'Cinema Zoom 9', 
            '19' : 'Cinema Zoom 10', 
            '1A' : 'Cinema Zoom 11', 
            '1B' : 'Cinema Zoom 12', 
            '1C' : 'Cinema Zoom 13', 
            '1D' : 'Cinema Zoom 14', 
            '1E' : 'Cinema Zoom 15', 
            '1F' : 'Cinema Zoom 16'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On'              : '00',
            'Off'             : '01',
            'On (Caption On)' : '02'
        }

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        AudioMuteCmdString = 'ke {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        ValueStateValues = {
            '0' : 'On',
            '1' : 'Off',
            '2' : 'On (Caption On)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'ju {0} 01\r'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetChannelStep(self, value, qualifier):
        ValueStateValues = {
            'Up'   : '00',
            'Down' : '01'
        }

        ChannelStepCmdString = 'mc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier, 3)

    def SetClosedCaption(self, value, qualifier):
        ClosedCaptionCmdString = 'mc {0} 39\r'.format(self.DeviceID)
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01',
            'Off' : '00'
        }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ExecutiveModeCmdString = 'km {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):
        FreezeCmdString = 'mc {0} 65\r'.format(self.DeviceID)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'DTV (Antenna)'    : '00',
            'DTV (Cable)'      : '01',
            'Analog (Antenna)' : '10',
            'Analog (Cable)'   : '11',
            'Video 1'          : '20',
            'Video 2'          : '21',
            'Component 1'      : '40',
            'Component 2'      : '41',
            'RGB-DTV'          : '50',
            'RGB-PC'           : '60',
            'HDMI/DVI'         : '90'
        }

        InputCmdString = 'xb {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputCmdString = 'xb {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ValueStateValues = {
            '00' : 'DTV (Antenna)',
            '01' : 'DTV (Cable)',
            '10' : 'Analog (Antenna)',
            '11' : 'Analog (Cable)',
            '20' : 'Video 1',
            '21' : 'Video 2',
            '40' : 'Component 1',
            '41' : 'Component 2',
            '50' : 'RGB-DTV',
            '60' : 'RGB-PC',
            '90' : 'HDMI/DVI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):
        ValueStateValues = {
            '0' : '10', 
            '1' : '11', 
            '2' : '12', 
            '3' : '13', 
            '4' : '14', 
            '5' : '15', 
            '6' : '16', 
            '7' : '17', 
            '8' : '18', 
            '9' : '19'
        }

        KeypadCmdString = 'mc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier, 3)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up'    : '40',
            'Down'  : '41',
            'Left'  : '07',
            'Right' : '06', 
            'Enter' : '44', 
            'Menu'  : '43',
            'Exit'  : '5B'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01',
            'Off' : '00'
        }

        OnScreenDisplayCmdString = 'kl {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayCmdString = 'kl {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):
        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIPInput(self, value, qualifier):
        ValueStateValues = {
            'DTV (Antenna)'    : '00',
            'DTV (Cable)'      : '01',
            'Analog (Antenna)' : '10',
            'Analog (Cable)'   : '11',
            'Video 1'          : '20',
            'Video 2'          : '21'
        }

        PIPInputCmdString = 'xy {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier, 3)

    def UpdatePIPInput(self, value, qualifier):
        PIPInputCmdString = 'xy {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):
        ValueStateValues = {
            '00' : 'DTV (Antenna)',
            '01' : 'DTV (Cable)',
            '10' : 'Analog (Antenna)',
            '11' : 'Analog (Cable)',
            '20' : 'Video 1',
            '21' : 'Video 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):
        ValueStateValues = {
            'PIP Off'      : '00',
            'PIP'          : '01',
            'Twin Picture' : '02', 
            'POP'          : '05'
        }

        PIPModeCmdString = 'kn {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):
        PIPModeCmdString = 'kn {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):
        ValueStateValues = {
            '0' : 'PIP Off',
            '1' : 'PIP',
            '2' : 'Twin Picture',
            '5' : 'POP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):
        ValueStateValues = {
            'Bottom Right' : '00', 
            'Bottom Left'  : '01',
            'Top Right'    : '02',
            'Top Left'     : '03'
        }

        PIPPositionCmdString = 'kq {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):
        PIPPositionCmdString = 'kq {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):
        ValueStateValues = {
            '0' : 'Bottom Right',
            '1' : 'Bottom Left',
            '2' : 'Top Right',
            '3' : 'Top Left'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSwap(self, value, qualifier):
        PIPSwapCmdString = 'mc {0} 63\r'.format(self.DeviceID)
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01',
            'Off' : '00'
        }

        PowerCmdString = 'ka {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = 'ka {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01',
            'Off' : '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 3)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteCmdString = 'kd {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self.DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'kf {0} FF\r'.format(self.DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1), 16)
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True' or self.DeviceID == '00':
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
        State = {
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'm' : 'Executive Mode',
            'b' : 'Input',
            'l' : 'On Screen Display',
            'y' : 'PIP Input',
            'n' : 'PIP Mode',
            'q' : 'PIP Position',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume',
            }

        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1,temp2)
        print(value)

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