# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from json import dumps, loads

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveMicrophones': { 'Status': {}},
            'HeadphoneVolume': { 'Status': {}},
            'LoudspeakerVolume': { 'Status': {}},
            'Microphone': {'Parameters':['UID'], 'Status': {}},
            'OpenConnection': { 'Status': {}},
            'Recording': { 'Status': {}}
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0202:rep[0-9A-Z]{28}:\s*?{\s*?"rep":\s*?{([\s\S]*?)}\s*?}\x03'), self.__MatchOpenConnection, None)
            self.AddMatchString(re.compile(b'\x0202:(?:rep|evt)[0-9A-Z]{28}:{[\s\S]*?"nam":\s*?"mam",\s*?"mam":\s*?"?([0-8])"?[\s\S]*?}\x03'), self.__MatchActiveMicrophones, None)
            self.AddMatchString(re.compile(b'\x0202:(?:rep|evt)[0-9A-Z]{28}:{[\s\S]*?"nam":\s*?"hpvol",\s*?"vol":\s*?"?(\d+)"?\s*?}\x03'), self.__MatchHeadphoneVolume, None)
            self.AddMatchString(re.compile(b'\x0202:(?:rep|evt)[0-9A-Z]{28}:{[\s\S]*?"nam":\s*?"lsvol",\s*?"vol":\s*?"?(\d+)"?\s*?}\x03'), self.__MatchLoudspeakerVolume, None)
            self.AddMatchString(re.compile(b'\x0202:(?:rep|evt)[0-9A-Z]{28}:{[\s\S]*?"nam":\s*?"micstat",\s*?"uid":\s*?"(\S+)",\s*?"stat":\s*?"?(0|1|2)"?[\s\S]*?}\x03'), self.__MatchMicrophone, None)
            self.AddMatchString(re.compile(b'\x0202:(?:rep|evt)[0-9A-Z]{28}:{[\s\S]*?"nam":\s*?"recstat",\s*?"stat":\s*?"?([1-5])"?\s*?}\x03'), self.__MatchRecording, None)

    def SetConnection(self, value, qualifier):

        data = dumps({"typ":"Application","nam":"DU","ver":"1.01","inf":"","svr":0,"tim":""})
        CommandString = b''.join([b'\x0202:con0001020O00000C00000000000000:',
                                    data.encode(), b'\x03'])
        self.__SetHelper('Connection', CommandString, value, qualifier)

    def SetActiveMicrophones(self, value, qualifier):

        if 0 <= int(value) <= 8:
            data = dumps({"nam":"smam", "mam":value})
            ActiveMicrophonesCmdString = b''.join([b'\x0202:set0000020O00000C00000000000000:',
                                                    data.encode(), b'\x03'])
            self.__SetHelper('ActiveMicrophones', ActiveMicrophonesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveMicrophones')

    def UpdateActiveMicrophones(self, value, qualifier):

        ActiveMicrophonesCmdString = b'\x0202:get0000020C00000O00000000000000:{"nam": "gmam"}\x03'
        self.__UpdateHelper('ActiveMicrophones', ActiveMicrophonesCmdString, value, qualifier)

    def __MatchActiveMicrophones(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ActiveMicrophones', value, None)

    def SetHeadphoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = dumps({"nam":"shpvol", "vol":value})
            HeadphoneVolumeCmdString = b''.join([b'\x0202:set0000020O00000C00000000000000:',
                                                data.encode(),  b'\x03'])
            self.__SetHelper('HeadphoneVolume', HeadphoneVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHeadphoneVolume')

    def UpdateHeadphoneVolume(self, value, qualifier):

        HeadphoneVolumeCmdString = b'\x0202:get0000020O00000C00000000000000:{"nam": "ghpvol"}\x03'
        self.__UpdateHelper('HeadphoneVolume', HeadphoneVolumeCmdString, value, qualifier)

    def __MatchHeadphoneVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 24:
            self.WriteStatus('HeadphoneVolume', value, None)

    def SetLoudspeakerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = dumps({"nam":"slsvol", "vol":value})
            LoudspeakerVolumeCmdString = b''.join([b'\x0202:set0000020O00000C00000000000000:',
                                                    data.encode(),  b'\x03'])
            self.__SetHelper('LoudspeakerVolume', LoudspeakerVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoudspeakerVolume')

    def UpdateLoudspeakerVolume(self, value, qualifier):

        LoudspeakerVolumeCmdString = b'\x0202:get0000020O00000C00000000000000:{"nam": "glsvol"}\x03'
        self.__UpdateHelper('LoudspeakerVolume', LoudspeakerVolumeCmdString, value, qualifier)

    def __MatchLoudspeakerVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 24:
            self.WriteStatus('LoudspeakerVolume', value, None)

    def SetMicrophone(self, value, qualifier):

        ValueStateValues = {
            'On':       '1', 
            'Off':      '0', 
            'Request':  '2'
        }

        uid_val = qualifier['UID']
        if uid_val and value in ValueStateValues:
            data = dumps({"nam":"smicstat", "uid":uid_val, "stat":ValueStateValues[value]})
            MicrophoneCmdString = b''.join([b'\x0202:set0000029O00000C00000000000000:',
                                            data.encode(), b'\x03'])
            self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophone')

    def UpdateMicrophone(self, value, qualifier):

        uid_val = qualifier['UID']
        if uid_val:
            data = dumps({"nam":"gmicstat", "uid":uid_val})
            MicrophoneCmdString = b''.join([b'\x0202:get0000029O00000C00000000000000:',
                                            data.encode(), b'\x03'])
            self.__UpdateHelper('Microphone', MicrophoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophone')

    def __MatchMicrophone(self, match, tag):

        ValueStateValues = {
            '1': 'On', 
            '0': 'Off', 
            '2': 'Request'
        }

        qualifier = {}
        qualifier['UID'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Microphone', value, qualifier)

    def UpdateOpenConnection(self, value, qualifier):

        OpenConnectionCmdString = b'\x0202:lfc0001020O00000C00000000000000:\x03'
        self.__UpdateHelper('OpenConnection', OpenConnectionCmdString, value, qualifier)

    def __MatchOpenConnection(self, match, tag):

        if 'still alive' not in match.group(1).decode().lower():
            self.SetConnection(None, None)

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Stopped': '1', 
            'Record':  '2', 
            'Paused':  '3', 
        }

        if value in ValueStateValues:
            data = dumps({"nam":"srecstat", "stat": ValueStateValues[value]})
            RecordingCmdString = b''.join([b'\x0202:set0000029O00000C00000000000000:',
                                            data.encode(), b'\x03'])
            self.__SetHelper('Recording', RecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecording')

    def UpdateRecording(self, value, qualifier):

        RecordingCmdString = b'\x0202:get0000029C00000O00000000000000:{"nam": "grecstat"}\x03'
        self.__UpdateHelper('Recording', RecordingCmdString, value, qualifier)

    def __MatchRecording(self, match, tag):

        ValueStateValues = {
            '1': 'Stopped', 
            '2': 'Record', 
            '3': 'Paused', 
            '4': 'Playing', 
            '5': 'Playing paused'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Recording', value, None)

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

        self.SetConnection( None, None)
    
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