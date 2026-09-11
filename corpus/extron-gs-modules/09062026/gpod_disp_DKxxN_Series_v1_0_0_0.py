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
            'DK32N': self.gpod_10_5325_32N,
            'DK40N': self.gpod_10_5325_other,
            'DK43N': self.gpod_10_5325_other,
            'DK49N': self.gpod_10_5325_other,
            'DK55N': self.gpod_10_5325_other,
            'DK65N': self.gpod_10_5325_other,
            'DK75N': self.gpod_10_5325_other,
            'DK86N': self.gpod_10_5325_other,
            'DK98N': self.gpod_10_5325_other,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Dimming': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0F[01][0-9]{2}MUS#(-ON|OFF)#\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x0F[01][0-9]{2}DIS#(\d{3})#\x0D'), self.__MatchDimming, None)
            self.AddMatchString(re.compile(b'\x0F[01][0-9]{2}MIS#(HD[1-3]|DP[12])#\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x0F[01][0-9]{2}PWS#(-ON|OFF|DPM)#\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x0F[01][0-9]{2}VOS#(\d{3})#\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x0F[01][0-9]{2}(MU[TS]|DI[MS]|MI[NS]|RMT|PW[RS]|VO[LS])ERROR\x0D'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 100:
            self._DeviceID = int(value)
        else:
            self.Error(['Device ID should be a value between 1 to 100.'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '-ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '\x0F{0:03d}MUTW{1}0\x0D'.format(self._DeviceID, ValueStateValues[value]).encode()
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x0F{:03d}MUSR0000\x0D'.format(self._DeviceID).encode()
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '-ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetDimming(self, value, qualifier):

        if 0 <= value <= 100:
            DimmingCmdString = '\x0F{0:03d}DIMW{1:03d}0\x0D'.format(self._DeviceID, value).encode()
            self.__SetHelper('Dimming', DimmingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimming')

    def UpdateDimming(self, value, qualifier):

        DimmingCmdString = '\x0F{:03d}DISR0000\x0D'.format(self._DeviceID).encode()
        self.__UpdateHelper('Dimming', DimmingCmdString, value, qualifier)

    def __MatchDimming(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Dimming', value, None)

    def SetInput(self, value, qualifier):

        if value in self.SetInputValue:
            InputCmdString = '\x0F{0:03d}MINW{1}0\x0D'.format(self._DeviceID, self.SetInputValue[value]).encode()
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x0F{:03d}MISR0000\x0D'.format(self._DeviceID).encode()
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.MatchInputValue[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'MEN',
            'Up': '-UP',
            'Down': 'DOW',
            'Left': 'LEF',
            'Right': 'RIG',
            'Enter & PC Auto Adjust': 'ENT',
            'Exit': 'EXI'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = '\x0F{0:03d}RMTW{1}0\x0D'.format(self._DeviceID, ValueStateValues[value]).encode()
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '-ON',
            'Off': 'OFF',
        }

        PowerCmdString = '\x0F{0:03d}PWRW{1}0\x0D'.format(self._DeviceID, ValueStateValues[value]).encode()
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\x0F{:03d}PWSR0000\x0D'.format(self._DeviceID).encode()
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '-ON': 'On',
            'OFF': 'Off',
            'DPM': 'DPMS Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '\x0F{0:03d}VOLW{1:03d}0\x0D'.format(self._DeviceID, value).encode()
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x0F{0:03d}VOSR0000\x0D'.format(self._DeviceID).encode()
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
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

        DEVICE_ERROR_CODES = {
            'MUT' : 'Audio Mute Command',
            'MUS' : 'Audio Mute Status',
            'DIM' : 'Dimming Command',
            'DIS' : 'Dimming Status',
            'MIN' : 'Input Command',
            'MIS' : 'Input Status',
            'RMT' : 'Menu Navigation Command',
            'PWR' : 'Power Command',
            'PWS' : 'Power Status',
            'VOL' : 'Volume Command',
            'VOS' : 'Volume Status'
        }
        
        self.Error(['An error occured: {}'.format(DEVICE_ERROR_CODES[match.group(1).decode()])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def gpod_10_5325_32N(self):
        self.SetInputValue = {
            'HDMI 1'        : 'HD1',
            'HDMI 2'        : 'HD2',
            'DisplayPort 1' : 'DP1',
            'DisplayPort 2' : 'DP2'
        }

        self.MatchInputValue = {
            'HD1' : 'HDMI 1',
            'HD2' : 'HDMI 2',
            'DP1' : 'DisplayPort 1',
            'DP2' : 'DisplayPort 2'
        }

    def gpod_10_5325_other(self):
        self.SetInputValue = {
            'HDMI 1'        : 'HD1',
            'HDMI 2'        : 'HD2',
            'HDMI 3'        : 'HD3',
            'DisplayPort 1' : 'DP1',
            'DisplayPort 2' : 'DP2'
        }

        self.MatchInputValue = {
            'HD1' : 'HDMI 1',
            'HD2' : 'HDMI 2',
            'HD3' : 'HDMI 3',
            'DP1' : 'DisplayPort 1',
            'DP2' : 'DisplayPort 2'
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