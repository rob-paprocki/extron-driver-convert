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
            'AudioMute': {'Parameters': ['Monitor'], 'Status': {}},
            'Input': {'Parameters': ['Monitor'], 'Status': {}},
            'Power': {'Parameters': ['Monitor'], 'Status': {}},
            'VideoMute': {'Parameters': ['Monitor'], 'Status': {}},
            'Volume': {'Parameters': ['Monitor'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02AD94;RAD:(\d{3});QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:(\d{3});QMI:(HM1|HM2|DP1|DV1|PC1|YP1|VD1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:(\d{3});QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:(\d{3});QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:(\d{3});QAV:(\d{3})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ER401'), self.__MatchError, None)

    def getMonitor(self, Monitor):
        if Monitor == 'Broadcast':
            return '\x02AD94;RAD:000;'
        elif 1 <= int(Monitor) <= 100:
            return '\x02AD94;RAD:{0:03d};'.format(int(Monitor))

    def SetAudioMute(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On': 'AMT:1\x03',
            'Off': 'AMT:0\x03'
        }

        self.__SetHelper('AudioMute', Head + States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('AudioMute', Head + 'QAM\x03', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]

        self.WriteStatus('AudioMute', value, {'Monitor': Monitor})

    def SetInput(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'HDMI 1': 'IMS:HM1\x03',
            'HDMI 2': 'IMS:HM2\x03',
            'DisplayPort': 'IMS:DP1\x03',
            'DVI-D': 'IMS:DV1\x03',
            'PC': 'IMS:PC1\x03',
            'Component': 'IMS:YP1\x03',
            'Video': 'IMS:VD1\x03',
            'USB': 'IMS:UD1\x03'
        }

        self.__SetHelper('Input', Head + States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('Input', Head + 'QMI\x03', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'DP1': 'DisplayPort',
            'DV1': 'DVI-D',
            'PC1': 'PC',
            'YP1': 'Component',
            'VD1': 'Video',
            'UD1': 'USB'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]

        self.WriteStatus('Input', value, {'Monitor': Monitor})

    def SetPower(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On': 'PON\x03',
            'Off': 'POF\x03'
            }

        self.__SetHelper('Power', Head + States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('Power', Head + 'QPW\x03', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('Power', value, {'Monitor': Monitor})

    def SetVideoMute(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        States = {
            'On': 'VMT:1\x03',
            'Off': 'VMT:0\x03'
            }

        self.__SetHelper('VideoMute', Head + States[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('VideoMute', Head + 'QVM\x03', value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]

        self.WriteStatus('VideoMute', value, {'Monitor': Monitor})

    def SetVolume(self, value, qualifier):

        Head = self.getMonitor(qualifier['Monitor'])

        if 0 <= value <= 100:
            CmdString = Head + 'AVL:{0:03d}\x03'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        Head = self.getMonitor(qualifier['Monitor'])
        self.__UpdateHelper('Volume', Head + 'QAV\x03', value, qualifier)

    def __MatchVolume(self, match, tag):
        Monitor = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, {'Monitor': Monitor})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Broadcast = False
        if 'Monitor' in qualifier:
            if qualifier['Monitor'] == 'Broadcast':
                Broadcast = True

        if self.Unidirectional == 'True' and not Broadcast:
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
        self.Error(['Incorrect Command'])

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

