# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import base64
import urllib.error
import urllib.request
import json
from datetime import datetime

class DeviceHTTPClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.base64Auth = base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode()).decode()
        else:
            self.Error(['Missing Username and Password.'])
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CreateAdHocEvent': {'Parameters':['Title','Folder ID','Duration'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'RecorderControl': {'Parameters':['Channel or Multitrack Recorder'], 'Status': {}},
            'ScheduleEventControl': { 'Status': {}},
            'ScheduleEventName': { 'Status': {}},
            'ScheduleEventStatus': { 'Status': {}}
        }

        self.eventID = ''

    def SetCreateAdHocEvent(self, value, qualifier):

        DurationStates = {
            '0h 15m' : 900,
            '0h 30m' : 1800,
            '0h 45m' : 2700,
            '1h 00m' : 3600,
            '1h 15m' : 4500,
            '1h 30m' : 5400,
            '1h 45m' : 6300,
            '2h 00m' : 7200,
            '2h 15m' : 8100,
            '2h 30m' : 9000,
            '2h 45m' : 9900,
            '3h 00m' : 10800
        }

        if qualifier['Title'] and qualifier['Folder ID'] and qualifier['Duration'] in DurationStates:
            CreateAdHocEventCmdString = 'api/v2.0/schedule/events'
            data = {
                "title": qualifier['Title'],
                "duration": DurationStates[qualifier['Duration']], 
                "folder" : qualifier['Folder ID']
            }
            self.__SetHelper('CreateAdHocEvent', value, qualifier, url=CreateAdHocEventCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetCreateAdHocEvent')
        
    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'api/v2.0/system/firmware'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res:
            try:
                value = res['result']['version']
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetRecorderControl(self, value, qualifier):

        if value in ['Start', 'Stop'] and qualifier['Channel or Multitrack Recorder']:
            RecorderControlCmdString = 'api/v2.0/recorders/{0}/control/{1}'.format(qualifier['Channel or Multitrack Recorder'], value.lower())
            self.__SetHelper('RecorderControl', value, qualifier, url=RecorderControlCmdString)
        else:
            self.Discard('Invalid Command for SetRecorderControl')

    def UpdateRecorderControl(self, value, qualifier):

        if qualifier['Channel or Multitrack Recorder']:
            RecorderControlCmdString = 'api/v2.0/recorders/{}/status'.format(qualifier['Channel or Multitrack Recorder'])
            res = self.__UpdateHelper('RecorderControl', value, qualifier, url=RecorderControlCmdString)
            if res:
                try:
                    ValueStateValues = {
                        'started': 'Start',
                        'stopped': 'Stop'
                    }

                    value = ValueStateValues[res['result']['state']]
                    self.WriteStatus('RecorderControl', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Recorder Control: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecorderControl')

    def SetScheduleEventControl(self, value, qualifier):

        if value in ['Start', 'Stop', 'Pause', 'Resume'] and self.eventID:
            ScheduleEventControlCmdString = 'api/v2.0/schedule/events/{0}/control/{1}'.format(self.eventID, value.lower())
            self.__SetHelper('ScheduleEventControl', value, qualifier, url=ScheduleEventControlCmdString)
        else:
            self.Discard('Invalid Command for SetScheduleEventControl')
            
    def UpdateScheduleEventName(self, value, qualifier):

        self.UpdateScheduleEventStatus(value, qualifier)

    def UpdateScheduleEventStatus(self, value, qualifier):
            
        tme = datetime.now()
        dateTime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}'.format(tme.year, tme.month, tme.day,
                                                                                tme.hour, tme.minute, tme.second)
        ScheduleEventStatusCmdString = 'api/v2.0/schedule/events?from={}&limit=1'.format(dateTime)
        res = self.__UpdateHelper('ScheduleEventStatus', value, qualifier, url=ScheduleEventStatusCmdString)
        if res:
            try:
                if res['result']:
                    if res['result'][0]['status'] in ['running', 'paused', 'scheduled']:
                        self.WriteStatus('ScheduleEventStatus', res['result'][0]['status'].title(), qualifier)
                        self.WriteStatus('ScheduleEventName', res['result'][0]['title'], qualifier)
                    else:
                        self.WriteStatus('ScheduleEventStatus', 'Finished', qualifier)
                        self.WriteStatus('ScheduleEventName', res['result'][0]['title'], qualifier)
                    self.eventID = res['result'][0]['id']
                else:
                    self.eventID = ''
                    self.WriteStatus('ScheduleEventStatus', 'Idle', qualifier)
                    self.WriteStatus('ScheduleEventName', 'None', qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Schedule Event Name: Invalid/unexpected response'])
                self.Error(['Schedule Event Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return json.loads(response.read().decode())

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {
            'Accept' : 'application/json',
            'Content-Type' : 'application/json',
            'Authorization' : 'Basic {}'.format(self.base64Auth)
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {
            'Accept' : 'application/json',
            'Authorization' : 'Basic {}'.format(self.base64Auth)
        }
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.eventID = ''

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

class DeviceSerialClass:
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
            'ChannelLayout': {'Parameters':['Channel or Recorder'], 'Status': {}},
            'FreeSpace': { 'Status': {}},
            'Record': {'Parameters':['Channel or Recorder'], 'Status': {}},
            'RecordingStatus': {'Parameters':['Channel or Recorder'], 'Status': {}},
            'RecordingTime': {'Parameters':['Channel or Recorder'], 'Status': {}},
            'SaveCFG': { 'Status': {}},
            'Snapshot': {'Parameters':['Channel or Recorder'], 'Status': {}},
            'Streaming': {'Parameters':['Channel', 'Logical Stream'], 'Status': {}}
        }
                    
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Freespace (\d+)\r\n\r\n'), self.__MatchFreeSpace, None)
            self.AddMatchString(re.compile(b'Status\.(\d{1,2}) (Running|Stopped|Uninitialized)\r\n\r\n'), self.__MatchRecordingStatus, None)
            self.AddMatchString(re.compile(b'Rectime\.(\d{1,2}) (\d+)\r\n\r\n'), self.__MatchRecordingTime, None)

    def SetChannelLayout(self, value, qualifier):

        channel = qualifier['Channel or Recorder']

        if 0 <= int(value) <= 255:
            if channel == 'All':
                ChannelLayoutCmdString = 'active_layout={0}\n'.format(value)
                self.__SetHelper('ChannelLayout', ChannelLayoutCmdString, value, qualifier)
            elif 1 <= int(channel) <= 16:
                    ChannelLayoutCmdString = 'SET.{0}.active_layout={1}\n'.format(channel, value)
                    self.__SetHelper('ChannelLayout', ChannelLayoutCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelLayout')
        else:
            self.Discard('Invalid Command for SetChannelLayout')

    def UpdateFreeSpace(self, value, qualifier):

        FreeSpaceCmdString = 'FREESPACE\n'
        self.__UpdateHelper('FreeSpace', FreeSpaceCmdString, value, qualifier)

    def __MatchFreeSpace(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FreeSpace', value, None)

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start' : 'START', 
            'Stop'  : 'STOP'
        }

        channel = qualifier['Channel or Recorder']
        if channel == 'All' and value in ValueStateValues:
            RecordCmdString = ValueStateValues[value] + '\n'
            self.__SetHelper('Record', RecordCmdString, value, qualifier)
        elif 1 <= int(channel) <= 16 and value in ValueStateValues:
            RecordCmdString = ValueStateValues[value] + '.{0}\n'.format(channel)
            self.__SetHelper('Record', RecordCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecord')

    def UpdateRecordingStatus(self, value, qualifier):

        channel = qualifier['Channel or Recorder']
        if 1 <= int(channel) <= 16:
            RecordingStatusCmdString = 'STATUS.{0}\n'.format(channel)
            self.__UpdateHelper('RecordingStatus', RecordingStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRecordingStatus')

    def __MatchRecordingStatus(self, match, tag):

        channel = match.group(1).decode()
        if 1 <= int(channel) <= 16:
            value = match.group(2).decode()
            self.WriteStatus('RecordingStatus', value, {'Channel or Recorder' : channel})

    def UpdateRecordingTime(self, value, qualifier):

        channel = qualifier['Channel or Recorder']
        if 1 <= int(channel) <= 16:
            RecordingTimeCmdString = 'RECTIME.{0}\n'.format(channel)
            self.__UpdateHelper('RecordingTime', RecordingTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRecordingTime')

    def __MatchRecordingTime(self, match, tag):

        channel = match.group(1).decode()
        if 1 <= int(channel) <= 16:
            value = match.group(2).decode()
            self.WriteStatus('RecordingTime', value, {'Channel or Recorder' : channel})

    def SetSaveCFG(self, value, qualifier):

        SaveCFGCmdString = 'SAVECFG\n'
        self.__SetHelper('SaveCFG', SaveCFGCmdString, value, qualifier)

    def SetSnapshot(self, value, qualifier):

        channel = qualifier['Channel or Recorder']
        if channel == 'All':
            SnapshotCmdString = 'SNAPSHOT\n'
            self.__SetHelper('Snapshot', SnapshotCmdString, value, qualifier)
        elif 1 <= int(channel) <= 16:
            SnapshotCmdString = 'SNAPSHOT.{0}\n'.format(channel)
            self.__SetHelper('Snapshot', SnapshotCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSnapshot')

    def SetStreaming(self, value, qualifier):

        ValueStateValues = {
            'On':  'on',
            'Off': ''
            }

        if 1 <= int(qualifier['Channel']) <= 16 and 1 <= qualifier['Logical Stream'] and value in ValueStateValues:
            StreamingCmdString = 'SET.{}:{}.publish_enabled={}\n'.format(qualifier['Channel'], 
                                    qualifier['Logical Stream'] -1, ValueStateValues[value])
            self.__SetHelper('Streaming', StreamingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreaming')

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])