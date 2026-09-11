from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self.Models = {
            'LINUS14D': self.coda_25_4941_14D14,
            'LINUS10-C': self.coda_25_4941_5C10C,
            'LINUS5-C': self.coda_25_4941_5C10C,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Delay': {'Parameters':['Channel'], 'Status': {}},
            'DeviceInformation': { 'Status': {}},
            'Fallback': { 'Status': {}},
            'Gain': {'Parameters':['Channel'], 'Status': {}},
            'Mute': {'Parameters':['Channel'], 'Status': {}},
            'Power': { 'Status': {}},
            'Snapshot': { 'Status': {}},
            }
   
        if self.Unidirectional == 'False':
            self.DelayRegex             = re.compile(b'\*DELAY=[0-4],0,\d{1,5}')
            self.DeviceInformationRegex = re.compile(b'\*DEVINFO_[\s\S]+_[0-9A-Fa-f]{12}')
            self.FallbackRegex          = re.compile(b'\*FALLBACK=[01]')
            self.GainRegex              = re.compile(b'\*GAIN=[0-4],0,-?\d{1,3}')
            self.MuteRegex              = re.compile(b'\*MUTE=[01]')
            self.SnapshotRegex          = re.compile(b'\*ACT_SNAPSHOT ?= ?\d{1,2},[\s\S]{1,16}')

            self.updateRegex = {
                'Delay'             : self.DelayRegex,
                'DeviceInformation' : self.DeviceInformationRegex,
                'Fallback'          : self.FallbackRegex,
                'Gain'              : self.GainRegex,
                'Mute'              : self.MuteRegex,
                'Snapshot'          : self.SnapshotRegex
            }
    
    def SetDelay(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4')
        channel_val = qualifier['Channel']
        if (self.DelayConstraints['Min'] <= value <= self.DelayConstraints['Max']
                and channel_val in ChannelStates):
            DelayCmdString = '*SET_DELAY={0},0,{1}'.format(channel_val, int(round(value * 96, 1)))
            self.__SetHelper('Delay', DelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelay')

    def UpdateDelay(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4')
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            DelayCmdString = '*GET_DELAY={0},0'.format(int(channel_val)-1)
            res = self.__UpdateHelper('Delay', DelayCmdString, value, qualifier)
            if res:
                try:
                    value = round(int(res.split(',')[-1])/96, 2)
                    self.WriteStatus('Delay', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Delay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDelay')

    def UpdateDeviceInformation(self, value, qualifier):

        DeviceInformationCmdString = '*GETDEVINFO'
        res = self.__UpdateHelper('DeviceInformation', DeviceInformationCmdString, value, qualifier)
        if res:
            try:
                value = res.split('_')
                string_val = ''.join(['Amplifier Model: ', value[1], '\r\n', 'MAC Address: ', ':'.join(value[2][i:i+2] for i in range(0,12,2))])
                self.WriteStatus('DeviceInformation', string_val, qualifier)
            except (ValueError, IndexError):
                self.Error(['Device Information: Invalid/unexpected response'])

    def SetFallback(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues:
            FallbackCmdString = '*SET_FALLBACK={0}'.format(ValueStateValues[value])
            self.__SetHelper('Fallback', FallbackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFallback')

    def UpdateFallback(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        FallbackCmdString = '*GET_FALLBACK'
        res = self.__UpdateHelper('Fallback', FallbackCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-1]]
                self.WriteStatus('Fallback', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Fallback: Invalid/unexpected response'])

    def SetGain(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4')

        ValueConstraints = {
            'Min' : -99,
            'Max' : 15
            }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ChannelStates:
            GainCmdString = '*SET_GAIN={0},0,{1}'.format(channel_val, int(value*10))
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4')
        
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            GainCmdString = '*GET_GAIN={0},0'.format(int(channel_val)-1)
            res = self.__UpdateHelper('Gain', GainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res.split(',')[-1])/10
                    self.WriteStatus('Gain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGain')

    def SetMute(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4')

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        channel_val = qualifier['Channel']
        if value in ValueStateValues and channel_val in ChannelStates:
            MuteCmdString = '*SET_MUTE={0},{1}'.format(channel_val, ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ChannelStates = ('1', '2', '3', '4')

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            MuteCmdString = '*GET_MUTE={0}'.format(channel_val)
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[-1]]
                    self.WriteStatus('Mute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : ('1', '5'), # Power On Delay fixed to 5
            'Off' : ('0', '0')
        }

        if value in ValueStateValues:
            PowerCmdString = '*SET_POWER={0},{1}'.format(ValueStateValues[value][0], ValueStateValues[value][1])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetSnapshot(self, value, qualifier):

        if 0 <= int(value) <= 20:
            SnapshotCmdString = '*LOADSNAPSHOT={0}'.format(value)
            self.__SetHelper('Snapshot', SnapshotCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSnapshot')

    def UpdateSnapshot(self, value, qualifier):

        SnapshotCmdString = '*GET_ACT_SNAPSHOT'
        res = self.__UpdateHelper('Snapshot', SnapshotCmdString, value, qualifier)
        if res:
            try:
                value = str(int(res.split(',')[0].split('=')[-1]))
                self.WriteStatus('Snapshot', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Snapshot: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.updateRegex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def coda_25_4941_5C10C(self):
        self.DelayConstraints = {
            'Min' : 0,
            'Max' : 200
            }

    def coda_25_4941_14D14(self):
        self.DelayConstraints = {
            'Min' : 0,
            'Max' : 1000
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