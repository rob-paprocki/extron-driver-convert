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
            'Brightness': {'Parameters': ['Zone ID'], 'Status': {}},
            'CurrentScene': {'Parameters': ['Zone ID'], 'Status': {}},
            'LightLevel': {'Parameters': ['Zone ID'], 'Status': {}},
            'SceneRecall': {'Parameters': ['Zone ID'], 'Status': {}},
            'SceneSave': {'Parameters': ['Zone ID'], 'Status': {}},
            'Zone': {'Parameters': ['Zone ID'], 'Status': {}}
        }

        self.LightLevelRegex = re.compile(':OK (\d+)%?\r\n')
        self.CurrentSceneRegex = re.compile(':OK (\d+)( M)?\r\n')

    def SetBrightness(self, value, qualifier):

        zone_id = qualifier['Zone ID']

        if zone_id != '' and 0 <= value <= 100:
            BrightnessCmdString = ':SL {} {}\r\n'.format(zone_id, value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateCurrentScene(self, value, qualifier):

        zone_id = qualifier['Zone ID']
        if zone_id != '':
            CurrentSceneCmdString = ':QS {}\r\n'.format(zone_id)
            res = self.__UpdateHelper('CurrentScene', CurrentSceneCmdString, value, qualifier)
            if res:
                try:
                    value = self.CurrentSceneRegex.match(res).group(1)
                    self.WriteStatus('CurrentScene', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Current Scene: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCurrentScene')

    def UpdateLightLevel(self, value, qualifier):

        zone_id = qualifier['Zone ID']

        if zone_id != '':
            LightLevelCmdString = ':QB {}\r\n'.format(zone_id)
            res = self.__UpdateHelper('LightLevel', LightLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(self.LightLevelRegex.match(res).group(1))
                    self.WriteStatus('LightLevel', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Light Level: Invalid/unexpected response'])

    def SetSceneRecall(self, value, qualifier):

        zone_id = qualifier['Zone ID']

        if zone_id != '' and 0 <= int(value) <= 100:
            SceneRecallCmdString = ':RS {} {}\r\n'.format(zone_id, int(value))
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def SetSceneSave(self, value, qualifier):

        zone_id = qualifier['Zone ID']

        if zone_id != '' and 0 <= int(value) <= 100:
            SceneSaveCmdString = ':SS {} {}\r\n'.format(zone_id, int(value))
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSave')

    def SetZone(self, value, qualifier):

        zone_id = qualifier['Zone ID']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if zone_id != '' and value in ValueStateValues:
            ZoneCmdString = ':SZ {} {}\r\n'.format(zone_id, ValueStateValues[value])
            self.__SetHelper('Zone', ZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and 'ERROR' in response:
            self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, response.strip())])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()