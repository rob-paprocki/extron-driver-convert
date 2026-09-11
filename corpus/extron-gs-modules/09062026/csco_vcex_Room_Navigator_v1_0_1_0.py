from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, search
import copy

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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Button': {'Parameters':['Widget ID'], 'Status': {}},
            'ButtonEvent': {'Parameters':['Widget ID'], 'Status': {}},
            'GroupButton': {'Parameters':['Widget ID'], 'Status': {}},
            'GroupButtonEvent': {'Parameters':['Widget ID','Group ID'], 'Status': {}},
            'PageEvent': {'Parameters':['Page ID'], 'Status': {}},
            'PanelEvent': {'Parameters':['Panel ID'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'PresentationExternalSourceSelectCommand': { 'Status': {}},
            'PresentationExternalSourceSelected': { 'Status': {}},
            'PresentationExternalSourceStateSet': {'Parameters':['Source Identifier'], 'Status': {}},
            'Slider': {'Parameters':['Widget ID'], 'Status': {}},
            'Spinner': {'Parameters':['Widget ID'], 'Status': {}},
            'SpinnerEvent': {'Parameters':['Widget ID','Direction'], 'Status': {}},
            'Text': {'Parameters':['Widget ID'], 'Status': {}},
            'Toggle': {'Parameters':['Widget ID'], 'Status': {}},
            }

        self.tshellerror = False
        self.VerboseDisabled = False

        self.lastPresentationListSent = 0
        self.ExternalSourceFlag = False
        self.SourceIDRex = compile('Source (\d+) SourceIdentifier: "([\S\r\n\x00 ]+)"\r\n')
        self.SourceStateRex = compile('Source (\d+) State: (Ready|NotReady|Hidden|Error)\r\n')
        self.selectedSource = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'version="([\w.]+)" apiVersion'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\*e UserInterface Presentation ExternalSource Selected SourceIdentifier: "([\S\r\n\x00 ]+)"\r\n'), self.__MatchPresentationExternalSourceSelected, None)
            self.AddMatchString(compile(b'xCommand UserInterface Presentation ExternalSource State Set SourceIdentifier:([\S\r\n\x00 ]+) State:(\w+)\r\n'), self.__MatchPresentationExternalSourceStateSet, None)
            self.AddMatchString(compile(b'\*e UserInterface Extensions Event Page(Opened|Closed) PageId: "(.+)"\r'), self.__MatchPageEvent, None)
            self.AddMatchString(compile(b'\*e UserInterface Extensions Panel Clicked PanelId: "(.+)"\r'), self.__MatchPanelEvent, None)
            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'\*r Login successful\r\n'), self.__MatchPasswordSuccess, None)
            self.AddMatchString(compile(b'xfeedback register event/UserInterface/Extensions/Event'), self.__MatchVerbose, None)
            self.AddMatchString(compile(b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27'), self.__MatchAuthentication, None)

            if self.InterfaceType == 'SSHInterface':
                self.AddMatchString(compile(b'tshell: Failed to connect to system software\r\n'), self.__MatchTSHell, None)

    def __MatchTSHell(self, match, tag):
        self.tshellerror = True

    def __MatchAuthentication(self, match, tag):
        self.SetAuthentication( None, None)

    def SetAuthentication(self, value, qualifier):
        self.Send(b'\xFF\xFB\x18\xFF\xFB\x1F\xFF\xFC\x20\xFF\xFC\x23\xFF\xFB\x27\xFF\xFA\x1F\x00\x50\x00\x19\xFF\xF0\xFF\xFA\x27\x00\xFF\xF0\xFF\xFA\x18\x00\x41\x4E\x53\x49\xFF\xF0\xFF\xFD\x03\xFF\xFB\x01\xFF\xFE\x05\xFF\xFC\x21')

    def __MatchLogin(self, match, qualifier):
        self.SetLogin( None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername + '\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword( None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPasswordSuccess(self, match, tag):
        self.Send('xfeedback register event/UserInterface/Extensions/Event\r')
        self.Send('xfeedback register event/UserInterface/Extensions/Panel\r')
        self.Send('xfeedback register event/UserInterface/Presentation/ExternalSource\r')

    def __MatchVerbose(self, match, tag):
        self.VerboseDisabled = True

    def SetButton(self, value, qualifier):

        ValueStateValues = {
            'Active' : 'active',
            'Inactive' : 'inactive'
        }

        Widget_ID = qualifier['Widget ID']
        if 1 <= len(Widget_ID) <= 40 and value in ValueStateValues:
            if Widget_ID not in self.Commands['ButtonEvent']['Status']:
                self.AddMatchString(compile('Event (Pressed|Released) Signal: \"({0})\"\r'.format(Widget_ID).encode()), self.__MatchButtonEvent, qualifier)

            ButtonCmdString = 'xCommand UserInterface Extensions Widget SetValue WidgetId: "{0}" Value: "{1}"\r'.format(Widget_ID,ValueStateValues[value])
            self.__SetHelper('Button', ButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButton')

    def __MatchButtonEvent(self, match, qualifier):
        buttonEvent = match.group(1).decode()
        Widget_ID = match.group(2).decode()
        self.WriteStatus('ButtonEvent', buttonEvent, {'Widget ID':Widget_ID})

    def SetGroupButton(self, value, qualifier):

        Widget_ID = qualifier['Widget ID']
        if 1 <= len(Widget_ID) <= 40 and 1 <= int(value) <= 255:
            if Widget_ID not in self.Commands['GroupButtonEvent']['Status']:
                self.AddMatchString(compile('Event (Pressed|Released) Signal: \"({0}):([\d]+)\"\r'.format(Widget_ID).encode()), self.__MatchGroupButtonEvent, qualifier)

            GroupButtonCmdString = 'xCommand UserInterface Extensions Widget SetValue WidgetId: "{0}" Value: "{1}"\r'.format(Widget_ID,value)
            self.__SetHelper('GroupButton', GroupButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupButton')

    def __MatchGroupButtonEvent(self, match, qualifier):
        buttonEvent = match.group(1).decode()
        Widget_ID = match.group(2).decode()
        Group_ID = match.group(3).decode()
        self.WriteStatus('GroupButtonEvent', buttonEvent, {'Widget ID': Widget_ID,'Group ID': Group_ID})

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'xgetxml /status/standby\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):
        chkStatus = self.ReadStatus('FirmwareVersion', None)
        if chkStatus is None:
            self.WriteStatus('FirmwareVersion', '', None) # necessary for re-initialization monitor to trigger

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def __MatchPageEvent(self, match, tag):
        PageEvent = match.group(1).decode()
        Page_ID = match.group(2).decode()
        self.WriteStatus('PageEvent', PageEvent, {'Page ID': Page_ID})

    def __MatchPanelEvent(self, match, tag):
        Panel_ID = match.group(1).decode()
        self.WriteStatus('PanelEvent', 'Clicked', {'Panel ID': Panel_ID})

    def SetPresentationExternalSourceSelectCommand(self, value, qualifier):

        if value:
            commandString = 'xCommand UserInterface Presentation ExternalSource Select SourceIdentifier: "{}"\r'.format(value)
            self.__SetHelper('PresentationExternalSourceSelectCommand', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationExternalSourceSelectCommand')

    def __MatchPresentationExternalSourceSelected(self, match, qualifier):
        value = self.removeInvalidCharacters(match.group(1).decode())
        self.WriteStatus('PresentationExternalSourceSelected', value, qualifier)

    def clearSourceSelected(self):
        self.WriteStatus('PresentationExternalSourceSelected', '', None)

    def SetPresentationExternalSourceStateSet(self, value, qualifier):

        ValueStateValues = {
            'Hidden'    : 'Hidden',
            'Ready'     : 'Ready',
            'Not Ready' : 'NotReady',
            'Error'     : 'Error'
            }

        sourceID = qualifier['Source Identifier']
        if sourceID and value in ValueStateValues:
            cmdString = 'xCommand UserInterface Presentation ExternalSource State Set SourceIdentifier:{} State:{}\r'.format(sourceID,ValueStateValues[value])
            self.__SetHelper('PresentationExternalSourceStateSet', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationExternalSourceStateSet')

    def removeInvalidCharacters(self, cmdString):
        for character in '\r\n\x00':
            cmdString = cmdString.replace(character,'')
        return cmdString

    def UpdatePresentationExternalSourceStateSet(self, value, qualifier):
        ValueStateValues = {
            'Hidden'   : 'Hidden',
            'Ready'    : 'Ready',
            'NotReady' : 'Not Ready',
            'Error'    : 'Error'
            }

        IDValue = qualifier['Source Identifier']
        res = self.SendAndWait('xCommand UserInterface Presentation ExternalSource List\r', 2.0, deliTag=b'** end')
        if res:
            res = res.decode()
            sourceIdDict = dict(findall(self.SourceIDRex, res))
            sourceStateDict = dict(findall(self.SourceStateRex, res))
            if sourceIdDict:
                for index in sourceIdDict:
                    value = ValueStateValues[sourceStateDict[self.removeInvalidCharacters(index)]]
                    sourceID = sourceIdDict[self.removeInvalidCharacters(index)]
                    self.WriteStatus('PresentationExternalSourceStateSet', value, {'Source Identifier': sourceID})
            else:
                self.WriteStatus('PresentationExternalSourceStateSet', 'Source Identifier does not exist', {'Source Identifier': IDValue})
            self.ExternalSourceFlag = True

    def __MatchPresentationExternalSourceStateSet(self, match, qualifier):
        ValueStateValues = {
            'Hidden'  :   'Hidden',
            'Ready'   :   'Ready',
            'NotReady':   'Not Ready',
            'Error'   :   'Error',
            }

        SourceID = self.removeInvalidCharacters(match.group(1).decode())
        value = ValueStateValues[self.removeInvalidCharacters(match.group(2).decode())]
        self.WriteStatus('PresentationExternalSourceStateSet', value, {'Source Identifier':SourceID})

    def SetSlider(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        Widget_ID = qualifier['Widget ID']
        if 1 <= len(Widget_ID) <= 40 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if Widget_ID not in self.Commands['Slider']['Status']:
                self.AddMatchString(compile('Event Changed Signal: \"({0}):(\d+)\"\r'.format(Widget_ID).encode()), self.__MatchSlider, qualifier)

            SliderCmdString = 'xCommand UserInterface Extensions Widget SetValue WidgetId: "{0}" Value: "{1}"\r'.format(Widget_ID,value)
            self.__SetHelper('Slider', SliderCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSlider')

    def __MatchSlider(self, match, qualifier):
        Widget_ID = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('Slider', value, {'Widget ID': Widget_ID})

    def SetSpinner(self, value, qualifier):

        Widget_ID = qualifier['Widget ID']
        if 1 <= len(Widget_ID) <= 40 and value:
            if Widget_ID not in self.Commands['SpinnerEvent']['Status']:
                self.AddMatchString(compile('Event (Pressed|Released) Signal: "({0}):(increment|decrement)"\r'.format(Widget_ID).encode()), self.__MatchSpinnerEvent,qualifier)

            SpinnerCmdString = 'xCommand UserInterface Extensions Widget SetValue WidgetId: "{0}" Value: "{1}"\r'.format(Widget_ID,value)
            self.__SetHelper('Spinner', SpinnerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpinner')

    def __MatchSpinnerEvent(self, match, qualifier):
        buttonEvent = match.group(1).decode()
        Widget_ID = match.group(2).decode()
        Direction = match.group(3).decode().title()
        self.WriteStatus('SpinnerEvent', buttonEvent, {'Widget ID': Widget_ID, 'Direction': Direction})

    def SetText(self, value, qualifier):

        Widget_ID = qualifier['Widget ID']
        if 1 <= len(Widget_ID) <= 40 and value is not None:
            TextCmdString = 'xCommand UserInterface Extensions Widget SetValue WidgetId: "{0}" Value: "{1}"\r'.format(Widget_ID,value)
            self.__SetHelper('Text', TextCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetText')

    def SetToggle(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on',
            'Off' : 'off'
        }

        Widget_ID = qualifier['Widget ID']
        if 1 <= len(Widget_ID) <= 40 and value in ValueStateValues:
            if Widget_ID not in self.Commands['Toggle']['Status']:
                self.AddMatchString(compile('Changed Signal: "({0}):(on|off)"\r'.format(Widget_ID).encode()), self.__MatchToggle, qualifier)

            ToggleCmdString = 'xCommand UserInterface Extensions Widget SetValue WidgetId: "{0}" Value: "{1}"\r'.format(Widget_ID,ValueStateValues[value])
            self.__SetHelper('Toggle', ToggleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetToggle')

    def __MatchToggle(self, match, qualifier):
        Widget_ID = match.group(1).decode()
        value = match.group(2).decode().title()
        self.WriteStatus('Toggle', value, {'Widget ID': Widget_ID})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.tshellerror:
            self.Discard('Inappropriate Command')
        else:
            if self.VerboseDisabled is False: # needed for serial or no password
                self.Send('xfeedback register event/UserInterface/Extensions/Event\r')
                self.Send('xfeedback register event/UserInterface/Extensions/Panel\r')
                self.Send('xfeedback register event/UserInterface/Presentation/ExternalSource\r')
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.tshellerror:
            self.Discard('Inappropriate Command ' + command)
        elif self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.VerboseDisabled is False: # needed for serial or no password
                self.Send('xfeedback register event/UserInterface/Extensions/Event\r')
                self.Send('xfeedback register event/UserInterface/Extensions/Panel\r')
                self.Send('xfeedback register event/UserInterface/Presentation/ExternalSource\r')

            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        self.Error([match.group(0).decode().strip()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        if self.tshellerror:
            self.tshellerror = False

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = False
        self.lastPresentationListSent = 0
        self.ExternalSourceFlag = False

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
        # Create shadow copy of matchstrings to prevent matchstrings from being lost
        # This is necessary since some matchstrings are formed from button presses
        tempCompileList = copy.copy(self.__matchStringDict)
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in tempCompileList.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        self.InterfaceType = 'NotSSH'
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
        self.InterfaceType = 'NotSSH'
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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort=22, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        self.InterfaceType = 'SSHInterface'
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
