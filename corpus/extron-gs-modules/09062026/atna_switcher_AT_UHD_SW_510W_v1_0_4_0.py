from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from json import loads

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
        self._NumberOfModeratorSearch = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'AudioSource': { 'Status': {}},
            'FactoryReset': { 'Status': {}},
            'Input': { 'Status': {}},
            'MatrixMode': { 'Status': {}},
            'MatrixRoute': {'Parameters':['Output'], 'Status': {}},
            'ModeratorName': {'Parameters':['Button'], 'Status': {}},
            'ModeratorNavigation': { 'Status': {}},
            'ModeratorSearch': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'OutputDisplay': { 'Status': {}},
            'OutputVolume': { 'Status': {}},
            'Restart': { 'Status': {}},
            'Shutdown': { 'Status': {}},
        }
        
        self.ModeratorStartingEntry = 0
        self.Advance = True
        self.json_list = []
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"result": ?{"outputmute": ?{"analog": ?(true|false),"hdmi": ?(true|false)}},"methodreturn": ?"Audio:Mute:Get"}\n#\n', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'{"result": ?{"input": ?([0-4]|"?unknown"?)(?:,"type": ?".+?")?},"methodreturn": ?"display:input:get","jsonrpc": ?"2.0"}\n#\n', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'{"result": ?{"mode": ?(true|false)(?:,"subtype": ?".+?")?},"methodreturn": ?"display:matrix:mode:get","jsonrpc": ?"2.0"}\n#\n', re.I), self.__MatchMatrixMode, None)
            self.AddMatchString(re.compile(b'{"result": ?{"input": ?([0-4])},"methodreturn": ?"display:matrix:get ?(0|1)","jsonrpc": ?"2.0"}\n#\n', re.I), self.__MatchMatrixRoute, None)
            self.AddMatchString(re.compile(b'{"result": ?{"state": ?(true|false)},"methodreturn": ?"osd:state:get"}\n#\n', re.I), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'{"result": ?{"volume": ?{"units": ?"dB","value": ?(-80|-[1-7][0-9]|-[0-9]|0)}},"methodreturn": ?"audio:volume:get"}\n#\n', re.I), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'(on|off)\s*?\n#\n'), self.__MatchOutputDisplay, None)
            self.AddMatchString(re.compile(b'"?Unknown command"?.\n#\n', re.I), self.__MatchError, None)

    @property
    def NumberOfModeratorSearch(self):
        return self._NumberOfModeratorSearch

    @NumberOfModeratorSearch.setter
    def NumberOfModeratorSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfModeratorSearch = value
        else:
            self.Error(['Invalid Number of Moderator Search Parameter.'])

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Analog' : 'analog', 
            'HDMI'   : 'hdmi'
        }

        ValueStateValues = {
            'On'  : 'true', 
            'Off' : 'false'
        }

        output_val = qualifier['Output']
        if output_val in OutputStates:
            AudioMuteCmdString = 'Audio:Mute:Set {0} {1}\r'.format(OutputStates[output_val], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Audio:Mute:Get\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'true'  : 'On', 
            'false' : 'Off'
        }

        self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode().lower()], {'Output' : 'Analog'})
        self.WriteStatus('AudioMute', ValueStateValues[match.group(2).decode().lower()], {'Output' : 'HDMI'})

    def SetAudioSource(self, value, qualifier):

        ValueStateValues = {
            'Analog'  : 'Audio:SetSource analog\r', 
            'Digital' : 'Audio:SetSource digital\r'
        }

        AudioSourceCmdString = ValueStateValues[value]
        self.__SetHelper('AudioSource', AudioSourceCmdString, value, qualifier)

    def SetFactoryReset(self, value, qualifier):

        FactoryResetCmdString = 'Platform:Reset all\r'
        self.__SetHelper('FactoryReset', FactoryResetCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'USB-C'       : 'Display:Input:Set 0\r', 
            'DisplayPort' : 'Display:Input:Set 1\r', 
            'HDMI 3'      : 'Display:Input:Set 2\r', 
            'HDMI 4'      : 'Display:Input:Set 3\r', 
            'BYOD'        : 'Display:Input:Set 4\r', 
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'Display:Input:Get\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0'        : 'USB-C', 
            '1'        : 'DisplayPort', 
            '2'        : 'HDMI 3', 
            '3'        : 'HDMI 4', 
            '4'        : 'BYOD', 
            'unknown'  : 'No Input'
        }
        
        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Input', value, None)

    def SetMatrixMode(self, value, qualifier):

        ValueStateValues = {
            'On'                    : 'Display:Matrix:Mode:Set 1\r', 
            'On with Static Route'  : 'Display:Matrix:Mode:Set 2\r', 
            'Off'                   : 'Display:Matrix:Mode:Set 0\r'
        }

        MatrixModeCmdString = ValueStateValues[value]
        self.__SetHelper('MatrixMode', MatrixModeCmdString, value, qualifier)

    def UpdateMatrixMode(self, value, qualifier):

        MatrixModeCmdString = 'Display:Matrix:Mode:Get\r'
        self.__UpdateHelper('MatrixMode', MatrixModeCmdString, value, qualifier)

    def __MatchMatrixMode(self, match, tag):

        ValueStateValues = {
            'true'  : 'On', 
            'false' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('MatrixMode', value, None)

    def SetMatrixRoute(self, value, qualifier):

        OutputStates = {
            'HDBaseT' : '0', 
            'HDMI'    : '1'
        }

        ValueStateValues = {
            'USB-C'       : '0', 
            'DisplayPort' : '1', 
            'HDMI 3'      : '2', 
            'HDMI 4'      : '3', 
            'BYOD'        : '4'
        }

        output_val = qualifier['Output']
        if output_val in OutputStates and value in ValueStateValues:
            MatrixRouteCmdString = 'Display:Matrix:Set {0} {1}\r'.format(ValueStateValues[value], OutputStates[output_val])
            self.__SetHelper('MatrixRoute', MatrixRouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixRoute')

    def UpdateMatrixRoute(self, value, qualifier):

        OutputStates = {
            'HDBaseT' : '0', 
            'HDMI'    : '1'
        }
        output_val = qualifier['Output']
        if output_val in OutputStates:
            output_val = qualifier['Output']
            MatrixRouteCmdString = 'Display:Matrix:Get {0}\r'.format(OutputStates[output_val])
            self.__UpdateHelper('MatrixRoute', MatrixRouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixRoute')

    def __MatchMatrixRoute(self, match, tag):

        OutputStates = {
            '0' : 'HDBaseT', 
            '1' :'HDMI'
        }
        ValueStateValues = {
            '0' : 'USB-C', 
            '1' : 'DisplayPort', 
            '2' : 'HDMI 3', 
            '3' : 'HDMI 4', 
            '4' : 'BYOD'
        }
        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(2).decode()]
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MatrixRoute', value, qualifier)

    def SetModeratorNavigation(self, value, qualifier):
        
        if 'Page Up' == value:
            self.ModeratorStartingEntry -= self._NumberOfModeratorSearch
        elif 'Page Down' == value and self.Advance:
            self.ModeratorStartingEntry += self._NumberOfModeratorSearch

        if self.ModeratorStartingEntry >= len(self.json_list):
            self.ModeratorStartingEntry = len(self.json_list) - 1

        if self.ModeratorStartingEntry < 0:
            self.ModeratorStartingEntry = 0

        self.Advance = True
        Button = 1
        for a in self.json_list[self.ModeratorStartingEntry:]:
            self.WriteStatus('ModeratorName', a["name"], {'Button' : Button})
            Button += 1
            if Button == self._NumberOfModeratorSearch + 1: break
        for a in range(Button, self._NumberOfModeratorSearch + 1):
            self.Advance = False
            self.WriteStatus('ModeratorName', '<empty>', {'Button' : a})

    def SetModeratorSearch(self, value, qualifier):

        ModeratorSearchCmdString = 'Moderator:Status:Get\r'
        res = self.SendAndWait(ModeratorSearchCmdString, self.DefaultResponseTimeout, deliTag = '\n').decode()
        if res:
            try:
                if isinstance(res, str):
                    res = loads(res)
                self.json_list = res["moderator"]["streams"]
                self.Advance = True
                self.SetModeratorNavigation( None, None)
            except (KeyError, IndexError):
                self.Error(['Moderator Search: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'OSD:State:Set 1\r', 
            'Off' : 'OSD:State:Set 0\r'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = 'OSD:State:Get\r'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            'true'  : 'On', 
            'false' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetOutputDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Display:Minimal:Set 1\r', 
            'Off' : 'Display:Minimal:Set 0\r'
        }

        OutputDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OutputDisplay', OutputDisplayCmdString, value, qualifier)

    def UpdateOutputDisplay(self, value, qualifier):

        OutputDisplayCmdString = 'Display:Minimal:Get\r'
        self.__UpdateHelper('OutputDisplay', OutputDisplayCmdString, value, qualifier)

    def __MatchOutputDisplay(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('OutputDisplay', value, None)

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -80,
            'Max' : 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = 'Audio:Volume:Set {0}\r'.format(value)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputVolumeCmdString = 'Audio:Volume:Get\r'
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputVolume', value, None)

    def SetRestart(self, value, qualifier):

        RestartCmdString = 'Platform:Restart\r'
        self.__SetHelper('Restart', RestartCmdString, value, qualifier)

    def SetShutdown(self, value, qualifier):

        ShutdownCmdString = 'Platform:Shutdown\r'
        self.__SetHelper('Shutdown', ShutdownCmdString, value, qualifier)

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

        self.Error(['Unknown Command.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetModeratorSearch(None, None)
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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
        
        #check incoming data if it matched any expected data from device module
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