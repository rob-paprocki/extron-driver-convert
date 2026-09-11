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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'NumberKey': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
              
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9a-fA-F]{2}) OK0(1|2|4|5|6|7|9)x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e ([0-9a-fA-F]{2}) OK0(1|0)x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm ([0-9a-fA-F]{2}) OK0(1|0)x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b ([0-9a-fA-F]{2}) OK(00|10|20|21|22|40|60|90|91|92)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l ([0-9a-fA-F]{2}) OK0(1|0)x'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a ([0-9a-fA-F]{2}) OK0(1|0)x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9a-fA-F]{2}) OK0(1|0)x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f ([0-9a-fA-F]{2}) OK([0-9a-fA-F]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|m|b|l|a|d|f) ([0-9a-fA-F]{1,2}) NG(.*)x'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 0 < int(value) < 100:
            self._DeviceID = '{0:02x}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '4:3'       : '01', 
            '16:9'      : '02', 
            'Zoom1'     : '04', 
            'Zoom2'     : '05', 
            'Original'  : '06', 
            '14:9'      : '07', 
            'Just Scan' : '09'
        }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = 'kc {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        ValueStateValues = {
            '1' : '4:3', 
            '2' : '16:9', 
            '4' : 'Zoom1', 
            '5' : 'Zoom2', 
            '6' : 'Original', 
            '7' : '14:9', 
            '9' : 'Just Scan'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On'  : '00', 
            'Off' : '01'
        }

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        AudioMuteCmdString = 'ke {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'ju {0} 01\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ExecutiveModeCmdString = 'km {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):       
        ValueStateValues = {
            'DTV-Antenna'     : '00', 
            'Analogue-Antenna': '10', 
            'AV1'             : '20',
            'AV2'             : '21',
            'AV3'             : '22',
            'Component'       : '40', 
            'RGB'             : '60', 
            'HDMI1'           : '90',
            'HDMI2'           : '91',
            'HDMI3'           : '92',
        }
        InputCmdString = 'xb {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
   
    def UpdateInput(self, value, qualifier):
        InputCmdString = 'xb {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        ValueStateValues = {
            '00' : 'DTV-Antenna', 
            '10' : 'Analogue-Antenna', 
            '20' : 'AV1', 
            '21' : 'AV2',
            '22' : 'AV3',
            '40' : 'Component', 
            '60' : 'RGB', 
            '90' : 'HDMI1',
            '91' : 'HDMI2',
            '92' : 'HDMI3'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up'     : '40', 
            'Down'   : '41', 
            'Left'   : '07', 
            'Right'  : '06', 
            'Enter'  : '44', 
            'Return' : '28', 
            'Menu'   : '43'
        }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetNumberKey(self, value, qualifier):
        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19'
        }

        NumberKeyCmdString = 'mc {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('NumberKey', NumberKeyCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        OnScreenDisplayCmdString = 'kl {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayCmdString = 'kl {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('OnScreenDisplay', value, None)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        PowerCmdString = 'ka {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = 'ka {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteCmdString = 'kd {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        if self._DeviceID == match.group(1).decode().lower():
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02x}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'kf {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        if self._DeviceID == match.group(1).decode().lower():
            value = int(match.group(2), 16)
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True' or self._DeviceID == '00':
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
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'm' : 'Executive',
            'b' : 'Input',
            'l' : 'OSD',
            'a' : 'Power',
            'd' : 'Video Mute',
            'f' : 'Volume'
            }
            
        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode().lower()
        temp3 = match.group(3).decode()
        value = '{0} Error, DeviceID {1}: {2}'.format(temp1,temp2,temp3)
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

