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
        self._DeviceID = '01'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

                
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2} OK(01|02|04|06|07|09|10|11|12|13|14|15|16|17|18|19|1A|1B|1C|1D|1E|1F)x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2} OK0(1|0)x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2} OK0(1|0)x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2} OK(00|01|10|11|20|21|40|41|60|90|91|92|93)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9a-f]{2} OK0(1|0)x'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2} OK0(1|0)x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2} OK0(1|0)x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2} OK([0-9a-fA-F]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(j|c|e|m|b|l|a|d|f) [0-9a-f]{2} NG(.*)x'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            print('Broadcast')
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            print('Notcast')
            self._DeviceID ='{0:02X}'.format(int(value))
        else:
            self.Error(['Device ID Out of Range'])
    def SetAspectRatio(self, value, qualifier):


        States = {
            'Normal'             : '01', 
            'Wide'               : '02',
            'Zoom'               : '04',
            'Original'           : '06', 
            '14:9'               : '07', 
            'Just Scan'          : '09', 
            'Cinema Zoom 1'      : '10', 
            'Cinema Zoom 2'      : '11', 
            'Cinema Zoom 3'      : '12', 
            'Cinema Zoom 4'      : '13', 
            'Cinema Zoom 5'      : '14', 
            'Cinema Zoom 6'      : '15', 
            'Cinema Zoom 7'      : '16', 
            'Cinema Zoom 8'      : '17', 
            'Cinema Zoom 9'      : '18', 
            'Cinema Zoom 10'     : '19', 
            'Cinema Zoom 11'     : '1A', 
            'Cinema Zoom 12'     : '1B', 
            'Cinema Zoom 13'     : '1C', 
            'Cinema Zoom 14'     : '1D', 
            'Cinema Zoom 15'     : '1E', 
            'Cinema Zoom 16'     : '1F', 
        }

        self.__SetHelper('AspectRatio', 'kc {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', 'kc {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '01' : 'Normal',
            '02' : 'Wide', 
            '04' : 'Zoom', 
            '06' : 'Original', 
            '07' : '14:9', 
            '09' : 'Just Scan',
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
            '1F' : 'Cinema Zoom 16', 
        }

        self.WriteStatus('AspectRatio',  States[match.group(1).decode()] , None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : '00', 
            'Off' : '01'
        }

        self.__SetHelper('AudioMute', 'ke {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', 'ke {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '0' : 'On', 
            '1' : 'Off'
        }

        self.WriteStatus('AudioMute',  States[match.group(1).decode()] , None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(self.DeviceID) , value, qualifier)

    def SetChannelStep(self, value, qualifier):

        States = {
            'Up'   : '00', 
            'Down' : '01'
        }

        self.__SetHelper('ChannelStep', 'mc {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        self.__SetHelper('ClosedCaption', 'mc {0} 39\r'.format(self.DeviceID) , value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        self.__SetHelper('ExecutiveMode', 'km {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdateExecutiveMode(self, value, qualifier):
        self.__UpdateHelper('ExecutiveMode', 'km {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        self.WriteStatus('ExecutiveMode',  States[match.group(1).decode()] , None)

    def SetInput(self, value, qualifier):

        States = {
            'DTV'         : '00', 
            'CADTV'       : '01', 
            'ATV'         : '10', 
            'CATV'        : '11', 
            'AV 1'        : '20', 
            'AV 2'        : '21', 
            'Component 1' : '40', 
            'Component 2' : '41', 
            'RGB'         : '60', 
            'HDMI 1'      : '90', 
            'HDMI 2'      : '91', 
            'HDMI 3'      : '92', 
            'HDMI 4'      : '93',
        }

        self.__SetHelper('Input', 'xb {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'xb {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '00' : 'DTV', 
            '01' : 'CADTV', 
            '10' : 'ATV', 
            '11' : 'CATV', 
            '20' : 'AV 1', 
            '21' : 'AV 2', 
            '40' : 'Component 1',
            '41' : 'Component 2', 
            '60' : 'RGB', 
            '90' : 'HDMI 1', 
            '91' : 'HDMI 2', 
            '92' : 'HDMI 3', 
            '93' : 'HDMI 4', 
        }

        self.WriteStatus('Input',  States[match.group(1).decode()] , None)

    def SetKeypad(self, value, qualifier):

        States = {
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

        self.__SetHelper('Keypad', 'mc {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu'  : '43',
            'Up'    : '40', 
            'Down'  : '41', 
            'Left'  : '07', 
            'Right' : '06', 
            'Enter' : '44',
            'Exit'  : '5B'
        }

        self.__SetHelper('MenuNavigation', 'mc {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        self.__SetHelper('OnScreenDisplay', 'kl {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdateOnScreenDisplay(self, value, qualifier):
        self.__UpdateHelper('OnScreenDisplay', 'kl {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        self.WriteStatus('OnScreenDisplay',  States[match.group(1).decode()] , None)

    def SetPower(self, value, qualifier):

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        self.__SetHelper('Power', 'ka {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdatePower(self, value, qualifier):


        self.__UpdateHelper('Power', 'ka {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        self.WriteStatus('Power',  States[match.group(1).decode()] , None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        self.__SetHelper('VideoMute', 'kd {0} {1}\r'.format(self.DeviceID, States[value]) , value, qualifier)
    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'kd {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        self.WriteStatus('VideoMute',  States[match.group(1).decode()] , None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'kf {0} {1:02X}\r'.format(self.DeviceID, value) , value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'kf {0} FF\r'.format(self.DeviceID) , value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume',  int(match.group(1), 16) , None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True


        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
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

        State = {
            'j' : 'Auto Image',
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'm' : 'Executive Mode',
            'b' : 'Input',
            'l' : 'On Screen Display',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume'
            }
            
        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1,temp2)
        self.Error([value])


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

