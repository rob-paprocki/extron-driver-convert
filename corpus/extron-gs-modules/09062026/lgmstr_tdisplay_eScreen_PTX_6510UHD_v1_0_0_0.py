from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
            'Power': { 'Status': {}},
            'SchemeSelection': { 'Status': {}},
            'Volume': { 'Status': {}},
            }





        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07\x01\x00ASP([\x00-\x04])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00MUT(\x00|\x01)\x08'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00KLC(\x00|\x01)\x08'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00MIN(\x00|\x0D|\x09|\x0A|\x0B|\x0C|\x0F)\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00POW(\x00|\x01)\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00SCM([\x00-\x04])\x08'), self.__MatchSchemeSelection, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00VOL([\x00-\x64])\x08'), self.__MatchVolume, None)
            
            
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'FullScreen' : '\x07\x01\x02ASP\x01\x08', 
            'Pillar Box' : '\x07\x01\x02ASP\x02\x08', 
            'Auto'       : '\x07\x01\x02ASP\x04\x08', 
            'Native'     : '\x07\x01\x02ASP\x00\x08', 
            'Letterbox'  : '\x07\x01\x02ASP\x03\x08'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x07\x01\x01ASP\x08'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x01' : 'FullScreen', 
            '\x02' : 'Pillar Box', 
            '\x04' : 'Auto', 
            '\x00' : 'Native', 
            '\x03' : 'Letterbox'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x07\x01\x02MUT\x01\x08', 
            'Off' : '\x07\x01\x02MUT\x00\x08'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x07\x01\x01MUT\x08'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x07\x01\x02ADJ\x00\x08'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x07\x01\x02KLC\x01\x08', 
            'Off' : '\x07\x01\x02KLC\x00\x08'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '\x07\x01\x01KLC\x08'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'         : '\x07\x01\x02MIN\x00\x08', 
            'HDMI 1'      : '\x07\x01\x02MIN\x09\x08', 
            'HDMI 2'      : '\x07\x01\x02MIN\x0A\x08', 
            'HDMI 3'      : '\x07\x01\x02MIN\x0B\x08', 
            'HDMI 4'      : '\x07\x01\x02MIN\x0C\x08', 
            'DisplayPort' : '\x07\x01\x02MIN\x0D\x08', 
            'OPS'         : '\x07\x01\x02MIN\x0F\x08'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x07\x01\x01MIN\x08'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x00' : 'VGA', 
            '\x09' : 'HDMI 1', 
            '\x0A' : 'HDMI 2', 
            '\x0B' : 'HDMI 3', 
            '\x0C' : 'HDMI 4', 
            '\x0D' : 'DisplayPort', 
            '\x0F' : 'OPS'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '\x07\x01\x02RCU\x00\x08', 
            'Info'  : '\x07\x01\x02RCU\x01\x08', 
            'Up'    : '\x07\x01\x02RCU\x02\x08', 
            'Down'  : '\x07\x01\x02RCU\x03\x08', 
            'Left'  : '\x07\x01\x02RCU\x04\x08', 
            'Right' : '\x07\x01\x02RCU\x05\x08', 
            'Enter' : '\x07\x01\x02RCU\x06\x08', 
            'Exit'  : '\x07\x01\x02RCU\x07\x08'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x07\x01\x02POW\x01\x08', 
            'Off' : '\x07\x01\x02POW\x00\x08'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

            
        PowerCmdString = '\x07\x01\x01POW\x08'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }
        
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSchemeSelection(self, value, qualifier):

        ValueStateValues = {
            'User'   : '\x07\x01\x02SCM\x00\x08', 
            'Sport'  : '\x07\x01\x02SCM\x01\x08', 
            'Game'   : '\x07\x01\x02SCM\x02\x08', 
            'Cinema' : '\x07\x01\x02SCM\x03\x08', 
            'Vivid'  : '\x07\x01\x02SCM\x04\x08'
        }

        SchemeSelectionCmdString = ValueStateValues[value]
        self.__SetHelper('SchemeSelection', SchemeSelectionCmdString, value, qualifier)
    def UpdateSchemeSelection(self, value, qualifier):

        SchemeSelectionCmdString = '\x07\x01\x01SCM\x08'
        self.__UpdateHelper('SchemeSelection', SchemeSelectionCmdString, value, qualifier)

    def __MatchSchemeSelection(self, match, tag):

        ValueStateValues = {
            '\x00' : 'User', 
            '\x01' : 'Sport', 
            '\x02' : 'Game', 
            '\x03' : 'Cinema', 
            '\x04' : 'Vivid'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SchemeSelection', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('8B', 0x07, 0x01, 0x02, 0x56, 0x4F, 0x4C, value, 0x08)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x07\x01\x01\x56\x4F\x4C\x08'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = unpack('B',match.group(1))[0]
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

