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
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*SAAMUT000000000000000(0|1)\x0A'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SACHHN([0-9]{8})\.0000000\x0A'), self.__MatchChannel, None)
            self.AddMatchString(re.compile(b'\*SAINPT0000000(0|1|3|4)0000000(0|1|2|3)\x0A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*SAPOWR000000000000000(0|1)\x0A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*SAPMUT000000000000000(0|1)\x0A'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*SAVOLU0000000000000([0-9]{3})\x0A'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\*SA([A-Z]{4})(FFFFFFFFFFFFFFFF|NNNNNNNNNNNNNNNN)\x0A'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCAMUT0000000000000001\x0A',
            'Off': '*SCAMUT0000000000000000\x0A'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '*SEAMUT################\x0A'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99999999
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ChannelCmdString = '*SCCHHN{0:08d}.0000000\x0A'.format(value)
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = '*SECHHN################\x0A'
        self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)

    def __MatchChannel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Channel', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': '*SCINPT0000000000000000\x0A',
            'HDMI 1': '*SCINPT0000000100000001\x0A',
            'HDMI 2': '*SCINPT0000000100000002\x0A',
            'HDMI 3': '*SCINPT0000000100000003\x0A',
            'Composite': '*SCINPT0000000300000001\x0A',
            'Component': '*SCINPT0000000400000001\x0A'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*SEINPT################\x0A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        if match.group(1).decode() == '1':
            value = 'HDMI ' + match.group(2).decode()
        else:
            value = {'0': 'TV', '3': 'Composite', '4': 'Component'}.get(match.group(1).decode())

        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '*SCIRCC0000000000000018\x0A',
            '2': '*SCIRCC0000000000000019\x0A',
            '3': '*SCIRCC0000000000000020\x0A',
            '4': '*SCIRCC0000000000000021\x0A',
            '5': '*SCIRCC0000000000000022\x0A',
            '6': '*SCIRCC0000000000000023\x0A',
            '7': '*SCIRCC0000000000000024\x0A',
            '8': '*SCIRCC0000000000000025\x0A',
            '9': '*SCIRCC0000000000000026\x0A',
            '0': '*SCIRCC0000000000000027\x0A',
            '11': '*SCIRCC0000000000000028\x0A',
            '12': '*SCIRCC0000000000000029\x0A'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '*SCIRCC0000000000000009\x0A',
            'Down': '*SCIRCC0000000000000010\x0A',
            'Right': '*SCIRCC0000000000000011\x0A',
            'Left': '*SCIRCC0000000000000012\x0A',
            'Confirm': '*SCIRCC0000000000000013\x0A',
            'Exit': '*SCIRCC0000000000000041\x0A',
            'Top Menu': '*SCIRCC0000000000000088\x0A',
            'Popup Menu': '*SCIRCC0000000000000089\x0A',
            'Enter': '*SCIRCC0000000000000037\x0A',
            'Home': '*SCIRCC0000000000000006\x0A'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPOWR0000000000000001\x0A',
            'Off': '*SCPOWR0000000000000000\x0A'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '*SEPOWR################\x0A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '*SCPMUT0000000000000001\x0A',
            'Off': '*SCPMUT0000000000000000\x0A'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '*SEPMUT################\x0A'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '*SCVOLU0000000000000{0:03d}\x0A'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '*SEVOLU################\x0A'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)
        else:
            print('Invalid response from Volume.')

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

        ErrorValues = {
            'FFFFFFFFFFFFFFFF': 'Error while executing command {0}',
            'NNNNNNNNNNNNNNNN': 'Channel not found: {0}'
        }

        value = match.group(1).decode()
        print('ErrorValues[match.group(2).decode()]'.format(value), command)

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
