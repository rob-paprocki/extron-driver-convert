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
        self._DeviceID = 1

        self.Models = {
            '32LD325': self.lg_10_90_Default,
            '26LD325': self.lg_10_90_Default,
            '26LD325N': self.lg_10_90_Default,
            '26LD328': self.lg_10_90_Default,
            '32LD328': self.lg_10_90_Default,
            '26LD335': self.lg_10_90_Default,
            '32LD335': self.lg_10_90_Default,
            '26LD336': self.lg_10_90_Default,
            '32LD336': self.lg_10_90_Default,
            '32LD452C': self.lg_10_90_Default,
            '37LD452C': self.lg_10_90_Default,
            '42LD452C': self.lg_10_90_Default,
            '47LD452C': self.lg_10_90_Default,
            '32LD420': self.lg_10_90_Default,
            '42LD420': self.lg_10_90_Default,
            '47LD420': self.lg_10_90_Default,
            '32LD420C': self.lg_10_90_Default,
            '37LD420C': self.lg_10_90_Default,
            '42LD420C': self.lg_10_90_Default,
            '47LD420C': self.lg_10_90_Default,
            '32LD420N': self.lg_10_90_Default,
            '37LD420N': self.lg_10_90_Default,
            '42LD420N': self.lg_10_90_Default,
            '47LD420N': self.lg_10_90_Default,
            '32LD421': self.lg_10_90_Default,
            '37LD421': self.lg_10_90_Default,
            '42LD421': self.lg_10_90_Default,
            '47LD421': self.lg_10_90_Default,
            '32LD421N': self.lg_10_90_Default,
            '37LD421N': self.lg_10_90_Default,
            '42LD421N': self.lg_10_90_Default,
            '47LD421N': self.lg_10_90_Default,
            '32LD425': self.lg_10_90_Default,
            '37LD425': self.lg_10_90_Default,
            '42LD425': self.lg_10_90_Default,
            '47LD425': self.lg_10_90_Default,
            '32LD426': self.lg_10_90_Default,
            '37LD426': self.lg_10_90_Default,
            '42LD426': self.lg_10_90_Default,
            '47LD426': self.lg_10_90_Default,
            '32LD428': self.lg_10_90_Default,
            '42LD428': self.lg_10_90_Default,
            '32LD450': self.lg_10_90_Default,
            '37LD428': self.lg_10_90_Default,
            '47LD428': self.lg_10_90_Default,
            '32LD455': self.lg_10_90_Default,
            '37LD455': self.lg_10_90_Default,
            '42LD455': self.lg_10_90_Default,
            '47LD455': self.lg_10_90_Default,
            '32LD458': self.lg_10_90_Default,
            '37LD458': self.lg_10_90_Default,
            '42LD458': self.lg_10_90_Default,
            '47LD458': self.lg_10_90_Default,
            '32LD465': self.lg_10_90_Default,
            '37LD465': self.lg_10_90_Default,
            '42LD465': self.lg_10_90_Default,
            '47LD465': self.lg_10_90_Default,
            '32LD465N': self.lg_10_90_Default,
            '37LD465N': self.lg_10_90_Default,
            '42LD465N': self.lg_10_90_Default,
            '47LD465N': self.lg_10_90_Default,
            '32LD468': self.lg_10_90_Default,
            '37LD468': self.lg_10_90_Default,
            '42LD468': self.lg_10_90_Default,
            '47LD468': self.lg_10_90_Default,
            '32LD450C': self.lg_10_90_Default,
            '37LD450C': self.lg_10_90_Default,
            '42LD450C': self.lg_10_90_Default,
            '47LD450C': self.lg_10_90_Default,
            '32LD450N': self.lg_10_90_Default,
            '37LD450N': self.lg_10_90_Default,
            '42LD450N': self.lg_10_90_Default,
            '47LD450N': self.lg_10_90_Default,
            '32LD452B': self.lg_10_90_Default,
            '37LD452B': self.lg_10_90_Default,
            '42LD452B': self.lg_10_90_Default,
            '47LD452B': self.lg_10_90_Default,
            '32LD340H': self.lg_10_90_Default,
            '32LD325N': self.lg_10_90_Default,
            '55LD520': self.lg_10_90_55,
            '55LD630': self.lg_10_90_55,
            '55LD520C': self.lg_10_90_55,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ChannelTV': {'Status': {}},
            'ChannelTVStep': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9]{1,2} OK(01|02|04|06|09|1[0-9]|1A|1B|1C|1D|1E|1F)x', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9]{1,2} OK(00|01)x', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'm [0-9]{1,2} OK(00|01)x', re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9]{1,2} OK(00|01|10|11|20|21|40|60|90|91|92)x', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9]{1,2} OK(00|01)x', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'a [0-9]{1,2} OK(00|01)x', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9]{1,2} OK(00|01)x', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9]{1,2} OK([0-9A-F]{2})x', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(a|c|d|e|f|l|m) ([0-9A-F]{1,2}) NG(.*)x', re.I), self.__MatchError, None)

    @property
    def DisplayId(self):
        return self._DeviceID

    @DisplayId.setter
    def DisplayId(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 99:
            self._DeviceID = int(value)
        else:
            self.Error(['Display Id should be a value between 1 to 99 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Auto': '06',
            'JUST-SCAN': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1A',
            'Cinema Zoom 12': '1B',
            'Cinema Zoom 13': '1C',
            'Cinema Zoom 14': '1D',
            'Cinema Zoom 15': '1E',
            'Cinema Zoom 16': '1F'
        }
        AspectRatioCmdString = 'kc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = 'kc {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Auto',
            '09': 'JUST-SCAN',
            '10': 'Cinema Zoom 1',
            '11': 'Cinema Zoom 2',
            '12': 'Cinema Zoom 3',
            '13': 'Cinema Zoom 4',
            '14': 'Cinema Zoom 5',
            '15': 'Cinema Zoom 6',
            '16': 'Cinema Zoom 7',
            '17': 'Cinema Zoom 8',
            '18': 'Cinema Zoom 9',
            '19': 'Cinema Zoom 10',
            '1A': 'Cinema Zoom 11',
            '1B': 'Cinema Zoom 12',
            '1C': 'Cinema Zoom 13',
            '1D': 'Cinema Zoom 14',
            '1E': 'Cinema Zoom 15',
            '1F': 'Cinema Zoom 16'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01',
        }
        AudioMuteCmdString = 'ke {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '00': 'On',
            '01': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ju {0:02X} 01\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannelTVStep(self, value, qualifier):

        ValueStateValues = {
            'Up': '00',
            'Down': '01',
        }
        ChannelStepCmdString = 'mc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ChannelTVStep', ChannelStepCmdString, value, qualifier)

    def SetChannelTV(self, value, qualifier):

        ValueStateValues = {
            '0': '10\r',
            '1': '11\r',
            '2': '12\r',
            '3': '13\r',
            '4': '14\r',
            '5': '15\r',
            '6': '16\r',
            '7': '17\r',
            '8': '18\r',
            '9': '19\r',
            '-': '4C\r',
        }

        SetChannelTVCmdString = 'mc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ChannelTV', SetChannelTVCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00',
        }

        ExecutiveModeCmdString = 'km {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'km {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = 'xb {0:02X} {1}\r'.format(self._DeviceID, self.SetInputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.GetInputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '43',
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Enter': '44',
            'Exit': '5B',
        }

        MenuNavigationCmdString = 'mc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00',
        }

        OnScreenDisplayCmdString = 'kl {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = 'kl {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00',
        }

        PowerCmdString = 'ka {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {0:02X} FF\r'.format(self._DeviceID)

        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00',
            }

        VideoMuteCmdString = 'kd {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0:02X} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            'c': 'Aspect Ratio',
            'e': 'Audio Mute',
            'm': 'Executive Mode',
            'b': 'Input',
            'l': 'On Screen Display',
            'a': 'Power',
            'f': 'Volume',
            'd': 'Video Mute'
        }

        errorstring = 'DeviceID: {0}, Command: {1}, State: {2}'.format(match.group(2).decode(), DEVICE_ERROR_CODES[match.group(1).decode()], match.group(3).decode())
        self.Error([errorstring])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
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

        
    def lg_10_90_Default(self):
        self.SetInputState = {
            'Analog-Antenna' :'10',
            'Analog-Cable'   :'11',
            'AV1'            :'20',
            'AV2'            :'21',          
            'Component1'     :'40',
            'RGB'            :'60',
            'HDMI1'          :'90',
            'HDMI2'          :'91',
            'DTV-Antenna'    :'00',
            'DTV-Cable'      :'01',
        }

        self.GetInputState = {
            '10': 'Analog-Antenna',
            '11': 'Analog-Cable',
            '00': 'DTV-Antenna',
            '01': 'DTV-Cable',
            '20': 'AV1',
            '21': 'AV2',
            '40': 'Component1',
            '60': 'RGB',
            '90': 'HDMI1',
            '91': 'HDMI2',
        }



    def lg_10_90_55(self):
        self.SetInputState = {
            'Analog-Antenna' :'10',
            'Analog-Cable'   :'11',
            'AV1'            :'20',
            'AV2'            :'21',          
            'Component1'     :'40',
            'RGB'            :'60',
            'HDMI1'          :'90',
            'HDMI2'          :'91',
            'DTV-Antenna'    :'00',
            'DTV-Cable'      :'01',
            'HDMI3'          :'92'
        }

        self.GetInputState = {
            '10': 'Analog-Antenna',
            '11': 'Analog-Cable',
            '00': 'DTV-Antenna',
            '01': 'DTV-Cable',
            '20': 'AV1',
            '21': 'AV2',
            '40': 'Component1',
            '60': 'RGB',
            '90': 'HDMI1',
            '91': 'HDMI2',
            '92': 'HDMI3'
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
        
        # check incoming data if it matched any expected data from device module
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