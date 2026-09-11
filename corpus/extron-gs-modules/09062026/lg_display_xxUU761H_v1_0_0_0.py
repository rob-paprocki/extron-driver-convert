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
        self.DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'EnergySaving': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OSD': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            partialRegex = ' {} '.format(self._DeviceID).encode() + b'OK([0-9A-F]{2})x'

            self.AddMatchString(re.compile(b'c'+ partialRegex,re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e'+ partialRegex,re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'q'+ partialRegex,re.I), self.__MatchEnergySaving, None)
            self.AddMatchString(re.compile(b'm'+ partialRegex,re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b'+ partialRegex,re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l'+ partialRegex,re.I), self.__MatchOSD, None)
            self.AddMatchString(re.compile(b'a'+ partialRegex,re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd'+ partialRegex,re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f'+ partialRegex,re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|q|m|b|l|a|d|f) ([0-9A-F]{2,3}) NG(.*?)x',re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9a-fA-F]{2}x')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 99:
            self._DeviceID = '{0:02X}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3'       : '01', 
            '16:9'      : '02', 
            'Original'  : '06', 
            'Just Scan' : '09'
        }

        self.__SetHelper('AspectRatio', 'kc {0} {1}\r'.format(self._DeviceID,States[value]) , value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', 'kc {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '01' : '4:3', 
            '02' : '16:9', 
            '06' : 'Original', 
            '09' : 'Just Scan'
        }     
        self.WriteStatus('AspectRatio',  States[match.group(1).decode()] , None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : '00', 
            'Off' : '01'
        }

        CmdString = 'ke {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'ke {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '00' : 'On', 
            '01' : 'Off'
        }

        self.WriteStatus('AudioMute',  States[match.group(1).decode()] , None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(self._DeviceID) , value, qualifier)

    def SetEnergySaving(self, value, qualifier):


        States = {
            'Off'           : '00', 
            'Minimum'       : '01', 
            'Medium'        : '02', 
            'Maximum'       : '03', 
            'Automatic'     : '04', 
            'Screen Off'    : '05'
        }

        CmdString = 'jq {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('EnergySaving', CmdString, value, qualifier)

    def UpdateEnergySaving(self, value, qualifier):
        self.__UpdateHelper('EnergySaving', 'jq {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchEnergySaving(self, match, tag):

        States = {
            '00' : 'Off', 
            '01' : 'Minimum', 
            '02' : 'Medium', 
            '03' : 'Maximum', 
            '04' : 'Automatic', 
            '05' : 'Screen Off'
        }

        self.WriteStatus('EnergySaving',  States[match.group(1).decode()] , None)

    def SetExecutiveMode(self, value, qualifier):


        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        CmdString = 'km {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'km {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        States = {
            '01' : 'On', 
            '00' : 'Off'
        }

        self.WriteStatus('ExecutiveMode',  States[match.group(1).decode()] , None)

    def SetInput(self, value, qualifier):

        States = {
            'DTV'       : '00', 
            'Analogue'  : '10', 
            'AV'        : '20', 
            'Component' : '40', 
            'RGB'       : '60', 
            'HDMI 1'    : '90', 
            'HDMI 2'    : '91', 
            'HDMI 3'    : '92', 
            'HDMI 4'    : '93'
        }

        CmdString = 'xb {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'xb {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '00' : 'DTV', 
            '10' : 'Analogue', 
            '20' : 'AV', 
            '40' : 'Component', 
            '60' : 'RGB', 
            '90' : 'HDMI 1', 
            '91' : 'HDMI 2', 
            '92' : 'HDMI 3', 
            '93' : 'HDMI 4'
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

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):


        States = {
            'Up'        : '40', 
            'Down'      : '41', 
            'Left'      : '07', 
            'Right'     : '06', 
            'Enter'     : '44', 
            'Return'    : '28', 
            'Exit'      : '5B', 
            'S.Menu'    : '3F',
            'Settings'  : '43'
        }

        CmdString = 'mc {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetOSD(self, value, qualifier):


        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        CmdString = 'kl {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateOSD(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'kl {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchOSD(self, match, tag):

        States = {
            '01' : 'On', 
            '00' : 'Off'
        }

        self.WriteStatus('OSD',  States[match.group(1).decode()] , None)

    def SetPower(self, value, qualifier):


        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        CmdString = 'ka {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', 'ka {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '01' : 'On', 
            '00' : 'Off'
        }

        self.WriteStatus('Power',  States[match.group(1).decode()] , None)

    def SetVideoMute(self, value, qualifier):


        States = {
            'Off'              : '00', 
            'On (Without OSD)' : '10', 
            'On (With OSD)'    : '01'
        }

        CmdString = 'kd {0} {1}\r'.format(self._DeviceID,States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'kd {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchVideoMute(self, match, tag):
 
        States = {
            '00' : 'Off', 
            '10' : 'On (Without OSD)', 
            '01' : 'On (With OSD)'
        }

        self.WriteStatus('VideoMute',  States[match.group(1).decode()] , None)

    def SetVolume(self, value, qualifier):


        if 0 <= value <= 100:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'kf {0} FF\r'.format(self._DeviceID) , value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume',  int(match.group(1), 16) , None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if 'OK' in response:
            return response
        elif 'NG' in response:
            self.Error(['Error occured in {}'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{} : Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

        State = {
            'c' : 'Aspect Ratio, Menu Navigation or Keypad',
            'e' : 'Audio Mute',
            'q' : 'Energy Saving',
            'm' : 'Executive Mode',
            'b' : 'Input',
            'l' : 'OSD',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume',
        }
        
        temp1 = State[match.group(1).decode().lower()]
        temp2 = match.group(1).decode().upper()
        temp3 = match.group(3).decode()
        value = '{0} Error, Device ID {1}: {2}'.format(temp1,temp2,temp3)
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

