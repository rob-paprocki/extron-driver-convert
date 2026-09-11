# Copyright 2026, Extron. All rights reserved.

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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Assign': {'Parameters':['Variable'], 'Status': {}},
            'ChannelLevel': {'Parameters':['Channel Number'], 'Status': {}},
            'Cue': {'Parameters':['Action'], 'Status': {}},
            'GlobalFadeTime': { 'Status': {}},
            'Go': { 'Status': {}},
            'GroupLevel': {'Parameters':['Group Number'], 'Status': {}}
        }

        self.set_regex = re.compile(b'[A-Za-z0-9]+')
        self.update_regex = re.compile(b'\d+')

    def SetAssign(self, value, qualifier):

        variable = qualifier['Variable']
        if 0 <= value <= 255:
            AssignCmdString = '"{}" = {}\r\n'.format(variable, value)
            self.__SetHelper('Assign', AssignCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAssign')

    def SetChannelLevel(self, value, qualifier):

        ChannelNo = qualifier['Channel Number']
        if 0 <= ChannelNo <= 16384 and 0 <= value <= 255:
            if ChannelNo == 0: # wildcard all channels
                ChannelLevelCmdString = 'Channel * At #{}\r\n'.format(value)
            else:
                ChannelLevelCmdString = 'Channel {} At #{}\r\n'.format(ChannelNo, value)

            self.__SetHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelLevel')
    
    def UpdateChannelLevel(self, value, qualifier):

        channel = qualifier['Channel Number']
        if 1 <= channel <= 16384:
            ChannelLevelCmdString = 'Channel {} At ?\r\n'.format(channel)
            res = self.__UpdateHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res) # 0-255
                    self.WriteStatus('ChannelLevel', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Channel Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateChannelLevel')

    def SetCue(self, value, qualifier):

        ActionStates = {
            'Recall': 'Cue',
            'Record': 'Record Cue',
            'Update': 'Update Cue'
        }

        CueAction = qualifier['Action']
        if CueAction in ActionStates and 0 <= value <= 99999:
            CueCmdString = '{} {}\r\n'.format(ActionStates[CueAction], value)
            self.__SetHelper('Cue', CueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCue')

    def SetGlobalFadeTime(self, value, qualifier):

        value = round(value, 2)

        if 0 <= value <= 3600:
            GlobalFadeTimeCmdString = 'Time {:.2f}\r\n'.format(value)
            self.__SetHelper('GlobalFadeTime', GlobalFadeTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalFadeTime')

    def SetGo(self, value, qualifier):

        GoCmdString = 'Go\r\n'
        self.__SetHelper('Go', GoCmdString, value, qualifier)

    def SetGroupLevel(self, value, qualifier):

        group = qualifier['Group Number']

        if 1 <= group <= 99999 and 0 <= value <= 255:
            GroupLevelCmdString = 'Group {} At #{}\r\n'.format(group, value)
            self.__SetHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLevel')
    
    def UpdateGroupLevel(self, value, qualifier):

        if 1 <= qualifier['Group Number'] <= 99999:
            GroupLevelCmdString = 'Group {} At ?\r\n'.format(qualifier['Group Number'])
            res = self.__UpdateHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res) # 0-255
                    self.WriteStatus('GroupLevel', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Group Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGroupLevel')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.update_regex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])