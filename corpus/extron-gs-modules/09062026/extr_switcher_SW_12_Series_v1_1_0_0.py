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
        self.Models = {
            'SW 12AV': self.extr_2_115_12av,
            'SW 12A': self.extr_2_115_12a,
            'SW 12A RCA': self.extr_2_115_12a,
            'SW 12AV RCA': self.extr_2_115_12av,
            'SW 12SVA': self.extr_2_115_12av,
            'SW 12SVA RCA': self.extr_2_115_12av,
            'SW 12SV': self.extr_2_115_12v,
            'SW 12V': self.extr_2_115_12v,
            'SW 4AV': self.extr_2_115_4av,
            'SW 4AV RCA': self.extr_2_115_4av,
            'SW 4SVA': self.extr_2_115_4av,
            'SW 4SVA RCA': self.extr_2_115_4av,
            'SW 6A': self.extr_2_115_6a,
            'SW 6A RCA': self.extr_2_115_6a,
            'SW 6AV': self.extr_2_115_6av,
            'SW 6AV RCA': self.extr_2_115_6av,
            'SW 6SV': self.extr_2_115_6v,
            'SW 6SVA': self.extr_2_115_6av,
            'SW 6SVA RCA': self.extr_2_115_6av,
            'SW 6V': self.extr_2_115_6v,
            'SW 8A': self.extr_2_115_8a,
            'SW 8A RCA': self.extr_2_115_8a,
            'SW 8AV': self.extr_2_115_8av,
            'SW 8AV RCA': self.extr_2_115_8av,
            'SW 8SV': self.extr_2_115_8v,
            'SW 8SVA': self.extr_2_115_8av,
            'SW 8SVA RCA': self.extr_2_115_8av,
            'SW 8V': self.extr_2_115_8v,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'In(\d{2,3}) Aud=([+-]\d{2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'F\*?([12])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'In([0-9]{2,3}) (Aud|Vid|All)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'V\*?(\d{2,3}|x) A\*?(\d{2,3}|x) F\*?([12x]) ?Vmt([01x]) Amt([01x])\r\n'), self.__MatchHeartbeat, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Sig([ 01]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        ValueConstraints = {
            'Min': -18,
            'Max': 24
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Input']) <= self.InputSize:
            type_ = 'G' if value >= 0 else 'g'
            AudioGainAttenuationCmdString = '{0}*{1}{2}'.format(int(qualifier['Input']), abs(value), type_)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputSize:
            AudioGainAttenuationCmdString = 'V{0}G'.format(qualifier['Input'])
            res = self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('AudioGainAttenuation', value, qualifier)
                except ValueError:
                    self.Error(['Audio Gain Attenuation: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def __MatchAudioGainAttenuation(self, match, tag):

        input_ = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        self.WriteStatus('AudioGainAttenuation', value, {'Input': input_})

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1Z',
            'Off': '0Z'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1X',
            'Off': '0X'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        ExecutiveModeCmdString = 'X'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('ExecutiveMode', value, None)
            except(KeyError, ValueError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'I', value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', 'I', value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'I', value, qualifier)

    def UpdateSwitchingMode(self, value, qualifier):
        self.__UpdateHelper('SwitchingMode', 'I', value, qualifier)


    def __MatchHeartbeat(self, match, tag):

        MuteStates = {
            '1': 'On',
            '0': 'Off'
        }

        AutoSwitchStates = {
            '2': 'On',
            '1': 'Off',
        }

        if self.Model == 'Video':
            self.WriteStatus('Input', str(int(match.group(1).decode())), None)
            self.WriteStatus('VideoMute', MuteStates[match.group(4).decode()], None)

        elif self.Model == 'Audio':
            self.WriteStatus('Input', str(int(match.group(2).decode())), None)
            self.WriteStatus('AudioMute', MuteStates[match.group(5).decode()], None)

        else:
            self.WriteStatus('Input', str(int(match.group(1).decode())), {'Type': 'Video'})
            self.WriteStatus('VideoMute', MuteStates[match.group(4).decode()], None)
            self.WriteStatus('Input', str(int(match.group(2).decode())), {'Type': 'Audio'})
            self.WriteStatus('AudioMute', MuteStates[match.group(5).decode()], None)
            if match.group(1).decode() == match.group(2).decode():
                self.WriteStatus('Input', str(int(match.group(1).decode())), {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})

        if match.group(3).decode() != 'x':
            self.WriteStatus('AutoSwitchMode', AutoSwitchStates[match.group(3).decode()], None)

    def SetInput(self, value, qualifier):

        TypeStates = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }
        if self.Model == 'AV':
            if 0 <= int(value) <= self.InputSize:
                CmdString = '{0}{1}'.format(value, TypeStates[qualifier['Type']])
                self.__SetHelper('Input', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')
        elif self.Model == 'Audio':
            if 0 <= int(value) <= self.InputSize:
                CmdString = '{0}$'.format(value)
                self.__SetHelper('Input', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')
        elif self.Model == 'Video':
            if 0 <= int(value) <= self.InputSize:
                CmdString = '{0}&'.format(value)
                self.__SetHelper('Input', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput_Video')

    def __MatchInput(self, match, tag):

        TypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video'
        }

        value = str(int(match.group(1).decode()))
        type_ = TypeStates[match.group(2).decode()]
        if self.Model in ['Video','Audio']:
            self.WriteStatus('Input', value, None)
        else:
            self.WriteStatus('Input', value, {'Type': type_})
            if type_ == 'Audio/Video':
                self.WriteStatus('Input', value, {'Type': 'Audio'})
                self.WriteStatus('Input', value, {'Type': 'Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})


    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0S'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        valueList = match.group(1).decode().split()
        index = 1
        for value in valueList:
            self.WriteStatus('InputSignalStatus', ValueStateValues[value], {'Input': str(index)})
            index += 1

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1'
        }

        AutoSwitchModeCmdString = '{0}#'.format(ValueStateValues[value])
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number (out of range)',
            'E10': 'Invalid command',
            'E13': 'Invalid value (out of range)',
            'E14': 'Illegal command for this configuration'
            }

        if response[0:3] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:3]])])
            return ''
        elif response[0].isdigit() or response[0] in ['+', '-']:
            return response
        else:
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command {}'.format(command))
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if command in ['AudioGainAttenuation', 'ExecutiveMode']: # sync
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
            else: # async
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '13': 'Invalid value (out of range)',
            '14': 'Illegal command for this configuration'
            }

        self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
      

    def extr_2_115_4a(self):
        self.InputSize = 4
        self.Model = 'Audio'

    def extr_2_115_4v(self):
        self.InputSize = 4
        self.Model = 'Video'

    def extr_2_115_4av(self):
        self.InputSize = 4
        self.Model = 'AV'

    def extr_2_115_6a(self):
        self.InputSize = 6
        self.Model = 'Audio'

    def extr_2_115_6v(self):
        self.InputSize = 6
        self.Model = 'Video'

    def extr_2_115_6av(self):
        self.InputSize = 6
        self.Model = 'AV'

    def extr_2_115_8a(self):
        self.InputSize = 8
        self.Model = 'Audio'

    def extr_2_115_8v(self):
        self.InputSize = 8
        self.Model = 'Video'

    def extr_2_115_8av(self):
        self.InputSize = 8
        self.Model = 'AV'

    def extr_2_115_12a(self):
        self.InputSize = 12
        self.Model = 'Audio'

    def extr_2_115_12v(self):
        self.InputSize = 12
        self.Model = 'Video'

    def extr_2_115_12av(self):
        self.InputSize = 12
        self.Model = 'AV'

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

