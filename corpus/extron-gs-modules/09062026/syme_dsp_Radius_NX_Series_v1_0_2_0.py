from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallerID': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'CallStatus': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'DialedNumber': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'HookStatus': {'Parameters':['Controller Number'], 'Status': {}},
            'HookToggle': {'Parameters':['Controller Number'], 'Status': {}},
            'Mute': {'Parameters':['Controller Number'], 'Status': {}},
            'NumbertoDialCommand': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'NumbertoDialStatus': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'Preset': { 'Status': {}},
            'SpeedDialNameCommand': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'SpeedDialNameStatus': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'SpeedDialNumberCommand': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'SpeedDialNumberStatus': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'TimeinCall': {'Parameters':['Channel','Card','Enum','Unit'], 'Status': {}},
            'Volume': {'Parameters':['Controller Number'], 'Status': {}},
        }

        self.UpdateRegex = re.compile(b'[\S ]+?( succeeded)?\r')

    def UpdateCallStatus(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            CallStatusCmdString = 'GSYSS {0}.1005.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                        CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('CallStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Caller ID: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCallStatus')

    def UpdateCallerID(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            CallerIDCmdString = 'GSYSS {0}.1003.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                      CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('CallerID', CallerIDCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('CallerID', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Call Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCallerID')

    def UpdateDialedNumber(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            DialedNumberCmdString = 'GSYSS {0}.1002.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                          CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('DialedNumber', DialedNumberCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('DialedNumber', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Dialed Number: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDialedNumber')

    def UpdateHookStatus(self, value, qualifier):

        ValueStateValues = {
            0     : 'On',
            65535 : 'Off'
        }

        if 1 <= qualifier['Controller Number'] <= 10000:
            HookStatusCmdString = 'GS {0}\r'.format(qualifier['Controller Number'])
            res = self.__UpdateHelper('HookStatus', HookStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[int(res)]
                    self.WriteStatus('HookStatus', value, qualifier)
                except (ValueError, KeyError, IndexError):
                    self.Error(['Hook Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHookStatus')

    def SetHookToggle(self, value, qualifier):

        if 1 <= qualifier['Controller Number'] <= 10000:
            HookToggleCmdString = 'CS {0} 65535\r'.format(qualifier['Controller Number'])
            self.__SetHelper('HookToggle', HookToggleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHookToggle')
    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '65535', 
            'Off' : '0'
        }

        if value in ValueStateValues and 1 <= qualifier['Controller Number'] <= 10000:
            MuteCmdString = 'CS {0} {1}\r'.format(qualifier['Controller Number'], ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')
    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            65535   : 'On',
            0       : 'Off'
        }

        if 1 <= qualifier['Controller Number'] <= 10000:
            MuteCmdString = 'GS {0}\r'.format(qualifier['Controller Number'])
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
            
                try:
                    value = ValueStateValues[int(res)]
                    self.WriteStatus('Mute', value, qualifier)
                except (ValueError, KeyError, TypeError):
                    self.Error(['Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetNumbertoDialCommand(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            DialStr = value
            if DialStr:
                NumbertoDialCommandCmdString = 'SSYSS {0}.1004.{1}.{2}.{3}={4}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                                    CardStates[qualifier['Card']], qualifier['Channel'], DialStr)
                NumbertoDialCommandCmdString = NumbertoDialCommandCmdString.encode(encoding='iso-8859-1')
                self.__SetHelper('NumbertoDialCommand', NumbertoDialCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNumbertoDialCommand')
    def UpdateNumbertoDialStatus(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            NumbertoDialStatusCmdString = 'GSYSS {0}.1004.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                                CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('NumbertoDialStatus', NumbertoDialStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('NumbertoDialStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Number to Dial Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateNumbertoDialStatus')

    def SetPreset(self, value, qualifier):

        if 1 <= value <= 1000:
            PresetCmdString = 'LP {0}\r'.format(value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = 'GPR\r'   
        res = self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                if 1 <= value <= 1000:
                    self.WriteStatus('Preset', value, qualifier)
            except (ValueError, TypeError):
                self.Error(['Preset: Invalid/unexpected response'])

    def SetSpeedDialNameCommand(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            NameStr = value
            if NameStr:
                SpeedDialNameCommandCmdString = 'SSYSS {0}.1001.{1}.{2}.{3}={4}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                                          CardStates[qualifier['Card']], qualifier['Channel'], NameStr)
                SpeedDialNameCommandCmdString = SpeedDialNameCommandCmdString.encode(encoding='iso-8859-1')
                self.__SetHelper('SpeedDialNameCommand', SpeedDialNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeedDialNameCommand')
    def UpdateSpeedDialNameStatus(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            SpeedDialNameStatusCmdString = 'GSYSS {0}.1001.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                                 CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('SpeedDialNameStatus', SpeedDialNameStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('SpeedDialNameStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speed Dial Name Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeedDialNameStatus')

    def SetSpeedDialNumberCommand(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            DialNum = value
            if DialNum:
                SpeedDialNumberCommandCmdString = 'SSYSS {0}.1000.{1}.{2}.{3}={4}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']],qualifier['Channel'], DialNum)
                SpeedDialNumberCommandCmdString = SpeedDialNumberCommandCmdString.encode(encoding='iso-8859-1')
                self.__SetHelper('SpeedDialNumberCommand', SpeedDialNumberCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeedDialNumberCommand')
    def UpdateSpeedDialNumberStatus(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            SpeedDialNumberStatusCmdString = 'GSYSS {0}.1000.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                                   CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('SpeedDialNumberStatus', SpeedDialNumberStatusCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('SpeedDialNumberStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Speed Dial Number Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpeedDialNumberStatus')

    def UpdateTimeinCall(self, value, qualifier):

        CardStates = {
            'A' : '0',
            'B' : '1',
            'C' : '2',
            'D' : '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and qualifier['Card'] in CardStates and 0 <= int(qualifier['Enum']) <= 19 \
                and 1 <= int(qualifier['Unit']) <= 9:
            TimeinCallCmdString = 'GSYSS {0}.1006.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'],
                                                                        CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('TimeinCall', TimeinCallCmdString, value, qualifier)
            if res:
                try:
                    value = res
                    self.WriteStatus('TimeinCall', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Time in Call: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTimeinCall')

    def SetVolume(self, value, qualifier):

        if -72 <= value <= 12 and 1 <= qualifier['Controller Number'] <= 10000:
            position = int(((value+72)/84)*65535) 
            VolumeCmdString = 'CS {0} {1:05d}\r'.format(qualifier['Controller Number'], position)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if 1 <= qualifier['Controller Number'] <= 10000:
            VolumeCmdString = 'GS {0}\r'.format(qualifier['Controller Number'])
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(round(-72 + 84*(int(res)/65535), 0))
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, TypeError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume') 

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'NAK\r': "Invalid Command Reply."}   
        if response:
            response = response.decode()
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])]) ##str was added for the case of volume
            response = ''
        #if ' succeeded\r' in response:
            #response = response.replace(' succeeded\r', '')
            #response = response[response.find(' is ')+4:]

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
            print(commandstring)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
            return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)           

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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