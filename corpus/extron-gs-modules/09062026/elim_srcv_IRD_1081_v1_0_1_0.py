from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'ChannelTV': { 'Status': {}},
            'CurrentMode': { 'Status': {}},
            'DiscreteRadioChannel': { 'Status': {}},
            'DiscreteRadioChannelStatus': { 'Status': {}},
            'DiscreteTVChannel': { 'Status': {}},
            'DiscreteTVChannelStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'IRRemoteEmulation': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MovieBrowser': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'Power': { 'Status': {}},
            'Record': { 'Status': {}},
            'Transport': { 'Status': {}},
            'TunerFrequency': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
              
        if self.ConnectionType == 'Serial': 
            self.Power_UpdateRegex = re.compile(b'#RET: (On|Off)|#ERROR:.*?')
            self.CurrentMode_UpdateRegex = re.compile(b'#RET:\x20(TV|Radio)|#ERROR:.*?')
            self.Volume_UpdateRegex = re.compile(b'#RET: ([0-9]{1,3})|#ERROR:.*?')
            self.DiscreteTVChannelStatus_UpdateRegex = re.compile(b'#RET: ([0-9]{1,4})|#ERROR:.*?')
            self.DiscreteRadioChannelStatus_UpdateRegex = re.compile(b'#RET: ([0-9]{1,4})|#ERROR:.*?')
        else:
            self.Power_UpdateRegex = re.compile(b'\r\n#COMMAND: <GCS>\r\n#RET: (On|Off)\r\n#OK:\r\n|\r\n#COMMAND: <GCS>\r\n#ERROR: .*?')
            self.CurrentMode_UpdateRegex = re.compile(b'\r\n#COMMAND: <GCM>\r\n#RET: (TV|Radio)\r\n#OK:\r\n|\r\n#COMMAND: <GCM>\r\n#ERROR: .*?')
            self.Volume_UpdateRegex = re.compile(b'\r\n#COMMAND: <VOL \?>\r\n#RET: ([0-9]{1,3})\r\n#OK:\r\n|\r\n#COMMAND: <VOL \?>\r\n#ERROR: .*?')
            self.DiscreteTVChannelStatus_UpdateRegex = re.compile(b'\r\n#COMMAND: <GNT>\r\n#RET: ([0-9]{1,4})\r\n#OK:\r\n|\r\n#COMMAND: <GNT>\r\n#ERROR: .*?')
            self.DiscreteRadioChannelStatus_UpdateRegex = re.compile(b'\r\n#COMMAND: <GNR>\r\n#RET: ([0-9]{1,4})\r\n#OK:\r\n|\r\n#COMMAND: <GNR>\r\n#ERROR: .*?') 
            
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ON', 
            'Off' : 'OFF'
        }

        AudioMuteCmdString = '<VOL {0}>'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetChannelTV(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 'd', 
            'Down' : 'u'
        }

        ChannelTVCmdString = '<PRT {0}>'.format(ValueStateValues[value])
        self.__SetHelper('ChannelTV', ChannelTVCmdString, value, qualifier)
    def SetCurrentMode(self, value, qualifier):

        ValueStateValues = {
            'TV'    : 'T', 
            'Radio' : 'R'
        }

        CurrentModeCmdString = '<TT{0}>'.format(ValueStateValues[value])
        self.__SetHelper('CurrentMode', CurrentModeCmdString, value, qualifier)

    def UpdateCurrentMode(self, value, qualifier):

       
        CurrentModeCmdString = '<GCM>'
        res = self.__UpdateHelper('CurrentMode', CurrentModeCmdString, value, qualifier)
        if res:
            try:
                temp = re.findall(r'(TV|Radio)',res)
                value = temp[0]
                self.WriteStatus('CurrentMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetDiscreteRadioChannel(self, value, qualifier):
       
        if 1 <= int(value) <= 9999:
            DiscreteRadioChannelCommandCmdString = '<PRR {0:04d}>'.format(int(value))
            self.__SetHelper('DiscreteRadioChannelCommand', DiscreteRadioChannelCommandCmdString, value, qualifier)

    def UpdateDiscreteRadioChannelStatus(self, value, qualifier):

        DiscreteRadioChannelStatusCmdString = '<GNR>'
        res = self.__UpdateHelper('DiscreteRadioChannelStatus', DiscreteRadioChannelStatusCmdString, value, qualifier)
        if res:
            try:
                temp = re.findall(r'(\d+)',res)
                value = str(temp[0])
                self.WriteStatus('DiscreteRadioChannelStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])   

    def SetDiscreteTVChannel(self, value, qualifier):

       if 1 <= int(value) <= 9999:
            DiscreteTVChannelCommandCmdString = '<PRT {0:04d}>'.format(int(value))
            self.__SetHelper('DiscreteTVChannelCommand', DiscreteTVChannelCommandCmdString, value, qualifier)
        
    def UpdateDiscreteTVChannelStatus(self, value, qualifier):

        DiscreteTVChannelStatusCmdString = '<GNT>'
        res = self.__UpdateHelper('DiscreteTVChannelStatus', DiscreteTVChannelStatusCmdString, value, qualifier)
        if res:
            try:
                temp = re.findall(r'(\d+)',res)
                value = str(temp[0])
                self.WriteStatus('DiscreteTVChannelStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])
   
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Lock Front Panel'   : '<LCK 1>', 
            'Unlock Front Panel' : '<LCK 0>', 
            'Lock IR Remote'     : '<LCI 1>', 
            'Unlock IR Remote'    : '<LCI 0>'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        FreezeCmdString = '<FCP {0}>'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetIRRemoteEmulation(self, value, qualifier):

        ValueStateValues = {
            '0'                       : '0', 
            '1'                       : '1', 
            '2'                       : '2', 
            '3'                       : '3', 
            '4'                       : '4', 
            '5'                       : '5', 
            '6'                       : '6', 
            '7'                       : '7', 
            '8'                       : '8', 
            '9'                       : '9', 
            'OK'                      : 'i', 
            'Exit'                    : 'm', 
            'Menu'                    : 'b', 
            'Up'                      : 'u', 
            'Down'                    : 'j', 
            'Right'                   : 'k', 
            'Left'                    : 'h', 
            'Text'                    : 'e', 
            'EPG'                     : 'd', 
            'Record / Stop'           : 'f', 
            'Info'                    : 'g', 
            'Yellow (MP3/JPEG/Music)' : 'x', 
            'Red (DVR/PVR)'           : 'c', 
            'Radio/TV'                : 'v', 
            'Last'                    : 'n', 
            'On/Off'                  : 't', 
            'Mute'                    : 'a', 
            'PIP'                     : 'J', 
            'Freeze'                  : 'K', 
            'Zoom'                    : 'L', 
            'Audio Video'             : 'M', 
            'Mode'                    : 'A', 
            'Green'                   : 'B', 
            'Blue'                    : 'C', 
            'Rewind'                  : 'D', 
            'Play'                    : 'E', 
            'Forward'                 : 'F', 
            'Previous'                : 'G', 
            'Next'                    : 'H', 
            'Timer'                   : 'I'
        }

        IRRemoteEmulationCmdString = '<RMC {0}>'.format(ValueStateValues[value])
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'   : '<MNC>', 
            'Exit'   : '<EXT>', 
            'Select' : '<CNF>', 
            'Up'     : '<NAV U>', 
            'Down'   : '<NAV D>', 
            'Left'   : '<NAV L>', 
            'Right'  : '<NAV R>'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMovieBrowser(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        MovieBrowserCmdString = '<MPLAY {0}>'.format(ValueStateValues[value])
        self.__SetHelper('MovieBrowser', MovieBrowserCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'Info'    : '<INF>', 
            'Menu'    : '<TVL>', 
            'Up'      : '<PAG u>', 
            'Down'    : '<PAG d>'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '<ON>', 
            'Off' : '<OFF>'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '<GCS>'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                temp = re.findall(r'(Off|On)',res)
                value = temp[0]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start' : '1', 
            'Stop'  : '0'
        }

        RecordCmdString = '<REC {0}>'.format(ValueStateValues[value])
        self.__SetHelper('Record', RecordCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'         : '<MPPLAY>', 
            'Pause'        : '<MPPAUSE>', 
            'Fast Forward' : '<MPFF>', 
            'Rewind'       : '<MPRW>', 
            'Start'        : '<MPSTA>', 
            'Middle'       : '<MPMID>', 
            'End'          : '<MPEND>'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetTunerFrequency(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 'd', 
            'Down' : 'u'
        }

        TunerFrequencyCmdString = '<PRR {0}>'.format(ValueStateValues[value])
        self.__SetHelper('TunerFrequency', TunerFrequencyCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '<VOL {0}>'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '<VOL ?>'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                temp = re.findall(r'(\d+)',res)
                value = int(temp[0])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if self.ConnectionType == 'Serial': 
            DEVICE_ERROR_CODES = {'#ERROR': "Command Not Supported."}   
            if response[0:6] in DEVICE_ERROR_CODES:
                self.Error(['Error: {0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:6]])])
                return ''
            else:
                return response
        else:
            DEVICE_ERROR_CODES = {'#ERROR': "Command Not Supported."}   
            if (response[21:27]  in DEVICE_ERROR_CODES ) and (self.Commands == 'Volume'):
                self.Error(['Error: {0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[21:27]])])
                return ''
            elif (response[19:25]) in DEVICE_ERROR_CODES:
                self.Error(['Error: {0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[19:25]])])
                return ''
            else: 
                return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True       
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag = b'>')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        CommandDelimValues = {
            'Power'                       :    self.Power_UpdateRegex,
            'CurrentMode'                 :    self.CurrentMode_UpdateRegex,
            'Volume'                      :    self.Volume_UpdateRegex,
            'DiscreteTVChannelStatus'     :    self.DiscreteTVChannelStatus_UpdateRegex,
            'DiscreteRadioChannelStatus'  :    self.DiscreteRadioChannelStatus_UpdateRegex,
        }            
            
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()            

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())    

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

