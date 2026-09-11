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
        self.Models = {
            'media:scape SP106-202': self.stcs_42,
            'media:scape SP106-201': self.stcs_84,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeselectAUXInput': { 'Status': {}},
            'InputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Output'], 'Status': {}},
            'PresetAUXInputs': {'Parameters':['Input'], 'Status': {}},
            'SelectAUXInput': {'Parameters':['Input','Output'], 'Status': {}},
            'WakeUpInput': { 'Status': {}},
            'ShutDown': { 'Status': {}},
            'ShutdownDelayTime': { 'Status': {}},
            'SoftReset': { 'Status': {}},
            'StandbyDelayTime': { 'Status': {}},
            'StandbyStatus': { 'Status': {}},
            'SwitchingControlType': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FanStatus': { 'Status': {}},
            'HeatAlarmStatus': { 'Status': {}},
            'WakeUp': { 'Status': {}},
            'WalkUpExperienceType': { 'Status': {}},
            'WalkUpMoviePlayTime': { 'Status': {}},
            }

        self.CurrentTies = []
        self.Unsolicited = 0
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\[\(([0-9]{1,2})[0-9,]{10,11}\)\(([0-9]{1,2})[0-9,]{10,11}\)\(([0-9]{1,2})[0-9,]{10,11}\)\(([0-9]{1,2})[0-9,]{10,11}\)\((1|2)\,[0-6,]{11}\)\(([0-9]{1,3})\,([0-9]{1,2})\,([0-4])\,0\)\(([0-3])\,[0-9]{1,3}\,\d+\,\d+\,\d+\,([0-9]{1,2})\)\([0-1,]{7}\)\([0-1]\)\([0|1|X|,]{7}\)\(([0-3])\,[0-1]\,[0-1]\)\((8x4|4x2)\)\]'), self.__MatchStandbyStatus, None)
            self.AddMatchString(re.compile(b'\[(P1|S1|S0)\]'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\[(F0|F1|F2)\]'), self.__MatchFanStatus, None)
            self.AddMatchString(re.compile(b'\[(H1|H0)\]'), self.__MatchHeatAlarmStatus, None)
            self.AddMatchString(re.compile(b'\[ER\]'), self.__MatchError, None)

    def SetDeselectAUXInput(self, value, qualifier):

        DeselectAUXInputCmdString = '[IPO{0}]'.format(self.DAUXStates[value])
        self.__SetHelper('DeselectAUXInput', DeselectAUXInputCmdString, value, qualifier)

    def UpdateStandbyStatus(self, value, qualifier):

        if self.Unsolicited == 0:
            self.Send('[UFA1]')
            self.Unsolicited = 1
        else:
            StandbyStatusCmdString = '[STP]'
            self.__UpdateHelper('StandbyStatus', StandbyStatusCmdString, value, qualifier)

    def __MatchStandbyStatus(self, match, tag):

        StandbyStates = {
            '0' : 'Awake', 
            '1' : 'Standby Countdown',
            '2' : 'Shutdown Countdown',
            '3' : 'Standby'
        }

        SwitchingControlStates = {
            '1' : 'Collaborative', 
            '2' : 'TCP/IP Control'
        }

        WalkUpExpType = {
            '0' : 'USB', 
            '1' : 'Video', 
            '2' : 'Still', 
            '3' : 'M:S'
        }

        counter = 1
        while 1 <= counter <= self.OutputSize:
            value = str(match.group(counter).decode())
            if 1 <= int(value) <= self.InputSize:
                qualifier = {'Output': str(counter)}
                self.WriteStatus('OutputTieStatus', self.ReturnInputStates[value], qualifier)
                oldInput = self.CurrentTies[int(counter)-1]
                if oldInput != value:
                    self.WriteStatus('InputTieStatus', 'Tied', {'Input' : self.ReturnInputStates[value], 'Output' : str(counter)})
                    if oldInput != 'Initialize':
                        self.WriteStatus('InputTieStatus', 'Untied', {'Input' : self.ReturnInputStates[str(oldInput)], 'Output' : str(counter)})
                    self.CurrentTies[int(counter)-1] = value
            counter = counter + 1

        SwitchingControlMode = SwitchingControlStates[match.group(5).decode()]
        self.WriteStatus('SwitchingControlType', SwitchingControlMode, None)

        StandbyDelayTime = int(match.group(6).decode())
        if 0 <= StandbyDelayTime <= 180:
            self.WriteStatus('StandbyDelayTime', StandbyDelayTime, None)
        else:
            self.Error(['Invalid/Unexpected Response'])

        ShutdownDelayTime = int(match.group(7).decode())
        if 0 <= ShutdownDelayTime <= 48:
            self.WriteStatus('ShutdownDelayTime', ShutdownDelayTime, None)
        else:
            self.Error(['Invalid/Unexpected Response'])

        StandbyStatus = StandbyStates[match.group(9).decode()]
        self.WriteStatus('StandbyStatus', StandbyStatus, None)

        WakeUpInput = self.ReturnWakeUpStates[match.group(8).decode()]      
        self.WriteStatus('WakeUpInput', WakeUpInput, None)

        WalkUpPlayTime = int(match.group(10).decode())
        if 1 <= WalkUpPlayTime <= 99:
            self.WriteStatus('WalkUpMoviePlayTime', WalkUpPlayTime, None)
        else:
            self.Error(['Invalid/Unexpected Response'])

        WalkUpExpType = WalkUpExpType[match.group(11).decode()]
        self.WriteStatus('WalkUpExperienceType', WalkUpExpType, None)

    def SetMatrixTieCommand(self, value, qualifier):

        MatrixTieCommandCmdString = '[I{0}O{1}]'.format(self.InputStates[qualifier['Input']], self.OutputStates[qualifier['Output']])
        self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)

    def SetPresetAUXInputs(self, value, qualifier):

        PresetAUXInputsCmdString = '[PI{0}O{1}]'.format(self.AUXStates[qualifier['Input']], self.PresetOutputStates[value])
        self.__SetHelper('PresetAUXInputs', PresetAUXInputsCmdString, value, qualifier)

    def SetSelectAUXInput(self, value, qualifier):

        SelectAUXInputCmdString = '[I{0}B{1}]'.format(self.AUXStates[qualifier['Input']], self.OutputStates[qualifier['Output']])
        self.__SetHelper('SelectAUXInput', SelectAUXInputCmdString, value, qualifier)

    def SetWakeUpInput(self, value, qualifier):

        WakeUpInputCmdString = '[SWU{0}]'.format(self.WakeUpStates[value])
        self.__SetHelper('SetWakeUpInput', WakeUpInputCmdString, value, qualifier)

    def SetShutDown(self, value, qualifier):

        ShutDownCmdString = '[STDWN]'
        self.__SetHelper('ShutDown', ShutDownCmdString, value, qualifier)

    def SetSoftReset(self, value, qualifier):

        SoftResetCmdString = '[SFT]'
        self.__SetHelper('SoftReset', SoftResetCmdString, value, qualifier)

    def SetStandbyDelayTime(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 180
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            StandbyDelayTimeCmdString = '[STBM{0}]'.format(value)
            self.__SetHelper('StandbyDelayTime', StandbyDelayTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandbyDelayTime')

    def SetShutdownDelayTime(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 48
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ShutdownDelayTimeCmdString = '[SSDM{0}]'.format(value)
            self.__SetHelper('ShutdownDelayTime', ShutdownDelayTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutdownDelayTime')

    def SetSwitchingControlType(self, value, qualifier):

        ValueStateValues = {
            'Collaborative'  : '1', 
            'TCP/IP Control' : '2'
        }

        SwitchingControlTypeCmdString = '[SMC{0}]'.format(ValueStateValues[value])
        self.__SetHelper('SwitchingControlType', SwitchingControlTypeCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        DeviceStates = {
        'P1' : 'Power Up Button was Pressed',
        'S1' : 'System Went to Sleep',
        'S0' : 'System Woke Up'
        }
        value = DeviceStates[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def __MatchFanStatus(self, match, tag):

        FanStates = {
        'F0' : 'Off',
        'F1' : 'Half Speed',
        'F2' : 'Full Speed'
        }
        value = FanStates[match.group(1).decode()]
        self.WriteStatus('FanStatus', value, None)

    def __MatchHeatAlarmStatus(self, match, tag):

        HeatAlarmStates = {
        'H0' : 'Alarm Back to Normal',
        'H1' : 'Alarm Activated'
        }
        value = HeatAlarmStates[match.group(1).decode()]
        self.WriteStatus('HeatAlarmStatus', value, None)

    def SetWakeUp(self, value, qualifier):

        WakeUpCmdString = '[WKP]'
        self.__SetHelper('WakeUp', WakeUpCmdString, value, qualifier)

    def SetWalkUpExperienceType(self, value, qualifier):

        ValueStateValues = {
            'USB'   : '0', 
            'Video' : '1', 
            'Still' : '2', 
            'M:S'   : '3'
        }

        WalkUpExperienceTypeCmdString = '[WLKUP{0}]'.format(ValueStateValues[value])
        self.__SetHelper('WalkUpExperienceType', WalkUpExperienceTypeCmdString, value, qualifier)

    def SetWalkUpMoviePlayTime(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            WalkUpMoviePlayTimeCmdString = '[WUPLAY{0}]'.format(value)
            self.__SetHelper('WalkUpMoviePlayTime', WalkUpMoviePlayTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWalkUpMoviePlayTime')

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

        self.Error(['Invalid/Unexpected Command'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.CurrentTies = [('Initialize') for i in range (0,self.OutputSize)]

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Unsolicited = 0


    def stcs_84(self):
        self.OutputSize = 4
        self.InputSize = 12

        self.InputStates = {
            '1'                  : '1',
            '2'                  : '2',
            '3'                  : '3',
            '4'                  : '4',
            '5'                  : '5',
            '6'                  : '6',
            '7'                  : '7',
            '8'                  : '8',
            'AUX 1'              : '9',
            'AUX 2'              : '10',
            'AUX 3'              : '11',
            'Walk Up Experience' : '12'  
            }

        self.ReturnInputStates = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            '5'  : '5',
            '6'  : '6',
            '7'  : '7',
            '8'  : '8',
            '9'  : 'AUX 1',
            '10' : 'AUX 2',
            '11' : 'AUX 3',
            '12' : 'Walk Up Experience',  
            }

        self.OutputStates = {
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
            }

        self.AUXStates = {
            'AUX 1' : '9',
            'AUX 2' : '10',
            'AUX 3' : '11'
            }

        self.DAUXStates = {
            'AUX 1' : '1',
            'AUX 2' : '2',
            'AUX 3' : '3'
            }

        self.PresetOutputStates = {
            '1'    : '1',
            '2'    : '2',
            '3'    : '3',
            '4'    : '4',
            'None' : '0'
            }

        self.WakeUpStates = {
            'AUX 1'   : '1', 
            'AUX 2'   : '2', 
            'AUX 3'   : '3', 
            'Any AUX' : '4', 
            'None'    : '0'
        }

        self.ReturnWakeUpStates = {
          '1' : 'AUX 1'   , 
          '2' : 'AUX 2'   , 
          '3' : 'AUX 3'   , 
          '4' : 'Any AUX' , 
          '0' : 'None'    
        }

    def stcs_42(self):
        self.OutputSize = 2
        self.InputSize = 7

        self.InputStates = {
            '1'                  : '1',
            '2'                  : '2',
            '3'                  : '3',
            '4'                  : '4',
            'AUX 1'              : '9',
            'AUX 2'              : '10',
            'Walk Up Experience' : '12',  
            }

        self.ReturnInputStates = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            '9'  : 'AUX 1',
            '10' : 'AUX 2',
            '12' : 'Walk Up Experience',  
            }

        self.OutputStates = {
            '1' : '1',
            '2' : '2',
            }

        self.AUXStates = {
            'AUX 1' : '9',
            'AUX 2' : '10'
            }

        self.DAUXStates = {
            'AUX 1' : '1',
            'AUX 2' : '2'
            }

        self.PresetOutputStates = {
            '1'    : '1',
            '2'    : '2',
            'None' : '0'
            }

        self.WakeUpStates = {
            'AUX 1'   : '1', 
            'AUX 2'   : '2',
            'Any AUX' : '4', 
            'None'    : '0'
        }

        self.ReturnWakeUpStates = {
          '1' : 'AUX 1'   , 
          '2' : 'AUX 2'   ,
          '4' : 'Any AUX' , 
          '0' : 'None'    
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