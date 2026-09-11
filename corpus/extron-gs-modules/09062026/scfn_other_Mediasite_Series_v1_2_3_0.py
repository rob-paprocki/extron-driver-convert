from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from collections import defaultdict

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
            'AudioInputLevel': { 'Status': {}},
            'AudioRecordLevel': { 'Status': {}},
            'AudioStatus': { 'Status': {}},
            'CurrentPresentationTemplateID': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'EncoderVideoInput': {'Parameters': ['Stream Type'], 'Status': {}},
            'ErrorStatus': { 'Status': {}},
            'FileLoad': { 'Status': {}},
            'FreeSpace': { 'Status': {}},
            'ImageAdvance': { 'Status': {}},
            'ImageCount': { 'Status': {}},
            'ImagePreset': { 'Status': {}},
            'PresentationInfo': {'Parameters': ['Type'], 'Status': {}},
            'PresentationTitle': { 'Status': {}},
            'Profile': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'RecallPresentationTemplate': {'Parameters': ['ID'], 'Status': {}},
            'RecordTime': { 'Status': {}},
            'ScheduleType': { 'Status': {}},
            'ServerConnectionInfo': {'Parameters': ['Index', 'Type'], 'Status': {}},
            'ServerConnectionNameCommand': { 'Status': {}},
            'ServerConnectionNameStatus': { 'Status': {}},
            'Shutdown': { 'Status': {}},
            'Transport': { 'Status': {}},
            'WakePreview': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\* AUDIOLEVEL ([0-9]{1,3}) \r'), self.__MatchAudioInputLevel, None)
            self.AddMatchString(re.compile(b'\* AUDIORECORDLEVEL ([0-9]{1,3}\.\d) \r'), self.__MatchAudioRecordLevel, None)
            self.AddMatchString(re.compile(b'\* AUDIOSTATUS ([012]) \r'), self.__MatchAudioStatus, None)
            self.AddMatchString(re.compile(b'\* PRESENTATIONTEMPLATEID ([\w\W]+) \r'), self.__MatchCurrentPresentationTemplateID, None)
            self.AddMatchString(re.compile(b'\* STATUS (IDLE|RECBUSY|RECORD|PAUSED|PUBLISH) \r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\* ETEXT ([\w\W]+) \r'), self.__MatchErrorStatus, None)
            self.AddMatchString(re.compile(b'\* ENCODERVIDEOINPUT ([012]) (Video\s?1|Video\s?2|Video\s?3|Image) \r'), self.__MatchEncoderVideoInput, None)
            self.AddMatchString(re.compile(b'\* FREESPACE ([0-9]{1,5}) \r'), self.__MatchFreeSpace, None)
            self.AddMatchString(re.compile(b'\* IMAGECOUNT ([0-9]{1,3}) \r'), self.__MatchImageCount, None)
            self.AddMatchString(re.compile(b'\* PRESETINDEX ([0-9]{1,2}) \r'), self.__MatchImagePreset, None)
            self.AddMatchString(re.compile(b'\* PRESENTATIONINFO ([\w\W]+) ([\w\W]+) ([\w\W]+) \r'), self.__MatchPresentationInfo, None)
            self.AddMatchString(re.compile(b'\* PRESENTATIONTITLE ([\w\W]+) \r'), self.__MatchPresentationTitle, None)
            self.AddMatchString(re.compile(b'\* PROFILEINDEX ([0-9]{1,2}) \r'), self.__MatchProfile, None)
            self.AddMatchString(re.compile(b'\* TIME ([0-9]{2}:[0-9]{2}:[0-9]{2}) \r'), self.__MatchRecordTime, None)
            self.AddMatchString(re.compile(b'\* SCHEDULETYPE (Create|CreateAndLoad|CreateLoadAndStart|CreateLoadStartAndStop|None) \r'), self.__MatchScheduleType, None)
            self.AddMatchString(re.compile(b'\* SERVERCONNECTIONINFO (\d+) ("[\w\W]+") ([\w\W]+) \r'), self.__MatchServerConnectionInfo, None)
            self.AddMatchString(re.compile(b'\* SERVERCONNECTIONNAME ([\w\W]+) \r'), self.__MatchServerConnectionNameStatus, None)
            self.AddMatchString(re.compile(b'\* ERROR TRUE \r'), self.__MatchError, None)
                    
    def UpdateAudioInputLevel(self, value, qualifier):

        AudioInputLevelCmdString = '* AUDIOLEVEL ? \r'
        self.__UpdateHelper('AudioInputLevel', AudioInputLevelCmdString, value, qualifier)

    def __MatchAudioInputLevel(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('AudioInputLevel', value, None)

    def SetAudioRecordLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioRecordLevelCmdString = '* AUDIORECORDLEVEL {0:.1f} \r'.format(value)
            self.__SetHelper('AudioRecordLevel', AudioRecordLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioRecordLevel')

    def UpdateAudioRecordLevel(self, value, qualifier):

        AudioRecordLevelCmdString = '* AUDIORECORDLEVEL ? \r'
        self.__UpdateHelper('AudioRecordLevel', AudioRecordLevelCmdString, value, qualifier)

    def __MatchAudioRecordLevel(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('AudioRecordLevel', value, None)

    def UpdateAudioStatus(self, value, qualifier):

        AudioStatusCmdString = '* AUDIOSTATUS ? \r'
        self.__UpdateHelper('AudioStatus', AudioStatusCmdString, value, qualifier)

    def __MatchAudioStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Low Audio Levels',
            '2': 'Low Audio Warning'
        }
              
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioStatus', value, None)

    def UpdateCurrentPresentationTemplateID(self, value, qualifier):

        CurrentPresentationTemplateIDCmdString = '* PRESENTATIONTEMPLATEID ? \r'
        self.__UpdateHelper('CurrentPresentationTemplateID', CurrentPresentationTemplateIDCmdString, value, qualifier)

    def __MatchCurrentPresentationTemplateID(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CurrentPresentationTemplateID', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '* STATUS ? \r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        
    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            'IDLE': 'Idle',
            'RECBUSY': 'Busy',
            'RECORD': 'Record',
            'PAUSED': 'Paused',
            'PUBLISH': 'Publish'
        }
       
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetEncoderVideoInput(self, value, qualifier):

        StreamTypeStates = {
            'Video 1' : 'Video1', 
            'Video 2' : 'Video2', 
            'Video 3' : 'Video3', 
            'Image' : 'Image'
        }

        ValueStateValues = {
            'Video': '0',
            'Image': '1',
            'PIP': '2'
        }

        EncoderVideoInputCmdString = '* ENCODERVIDEOINPUT {0} {1} \r'.format(ValueStateValues[value], StreamTypeStates[qualifier['Stream Type']])
        self.__SetHelper('EncoderVideoInput', EncoderVideoInputCmdString, value, qualifier)

    def UpdateEncoderVideoInput(self, value, qualifier):

        EncoderVideoInputCmdString = '* ENCODERVIDEOINPUT ? \r'
        self.__UpdateHelper('EncoderVideoInput', EncoderVideoInputCmdString, value, qualifier)

    def __MatchEncoderVideoInput(self, match, tag):

        StreamTypeStates = {
            'Video1' : 'Video 1', 
            'Video2' : 'Video 2', 
            'Video3' : 'Video 3', 
            'Image' : 'Image'
        }

        ValueStateValues = {
            '0': 'Video',
            '1': 'Image',
            '2': 'PIP'
        }
        qualifier = {}
        qualifier['Stream Type'] = StreamTypeStates[match.group(2).decode().replace(" ", "")]
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EncoderVideoInput', value, qualifier)

    def UpdateErrorStatus(self, value, qualifier):

        ErrorStatusCmdString = '* ETEXT ? \r'
        self.__UpdateHelper('ErrorStatus', ErrorStatusCmdString, value, qualifier)

    def __MatchErrorStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ErrorStatus', value, None)

    def UpdateFileLoad(self, value, qualifier):
               
        FileLoadCmdString = '* PRESENTATIONTITLE ? \r'
        self.__UpdateHelper('FileLoad', FileLoadCmdString, value, qualifier)
        
    def UpdateFreeSpace(self, value, qualifier):

        FreeSpaceCmdString = '* FREESPACE ? \r'
        self.__UpdateHelper('FreeSpace', FreeSpaceCmdString, value, qualifier)

    def __MatchFreeSpace(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('FreeSpace', value, None)

    def SetImageAdvance(self, value, qualifier):

        if value in ['True', 'False']:
            ImageAdvanceCmdString = '* IMAGEADVANCE {0} \r'.format(value.upper())
            self.__SetHelper('ImageAdvance', ImageAdvanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageAdvance')

    def UpdateImageCount(self, value, qualifier):
    
        ImageCountCmdString = '* IMAGECOUNT ? \r'
        self.__UpdateHelper('ImageCount', ImageCountCmdString, value, qualifier)

    def __MatchImageCount(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('ImageCount', value, None)

    def SetImagePreset(self, value, qualifier):

        if 0 <= int(value) <= 29:
            ImagePresetCmdString = '* PRESETINDEX {0} \r'.format(value)
            self.__SetHelper('ImagePreset', ImagePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImagePreset')

    def UpdateImagePreset(self, value, qualifier):

        ImagePresetCmdString = '* PRESETINDEX ? \r'
        self.__UpdateHelper('ImagePreset', ImagePresetCmdString, value, qualifier)

    def __MatchImagePreset(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ImagePreset', value, None)

    def UpdatePresentationInfo(self, value, qualifier):
               
        PresentationInfoCmdString = '* PRESENTATIONINFO ? \r'
        self.__UpdateHelper('PresentationInfo', PresentationInfoCmdString, value, qualifier)
        
    def __MatchPresentationInfo(self, match, tag):

        date = match.group(1).decode()
        _time = match.group(2).decode()
        duration = match.group(3).decode()

        self.WriteStatus('PresentationInfo', date, {'Type': 'Date'})
        self.WriteStatus('PresentationInfo', _time, {'Type': 'Time'})
        self.WriteStatus('PresentationInfo', duration, {'Type': 'Duration'})

    def UpdatePresentationTitle(self, value, qualifier):

        PresentationTitleCmdString = '* PRESENTATIONTITLE ? \r'
        self.__UpdateHelper('PresentationTitle', PresentationTitleCmdString, value, qualifier)

    def __MatchPresentationTitle(self, match, tag):

        if 'Untitled' in match.group(1).decode():
            FileLoadValue = 'Not Schedule'
        else:
            FileLoadValue = 'Schedule'
        self.WriteStatus('FileLoad', FileLoadValue, None)

        PresentationTitleValue = match.group(1).decode()
        self.WriteStatus('PresentationTitle', PresentationTitleValue, None)

    def SetProfile(self, value, qualifier):

        if 0 <= int(value) <= 29:
            ProfileCmdString = '* PROFILEINDEX {0} \r'.format(value)
            self.__SetHelper('Profile', ProfileCmdString, value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def UpdateProfile(self, value, qualifier):

        ProfileCmdString = '* PROFILEINDEX ? \r'
        self.__UpdateHelper('Profile', ProfileCmdString, value, qualifier)

    def __MatchProfile(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Profile', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = '* REBOOT \r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetRecallPresentationTemplate(self, value, qualifier):

        if qualifier['ID']:
            RecallCmdString = '* PRESENTATIONTEMPLATEID {0} \r'.format(qualifier['ID'])
            self.__SetHelper('RecallPresentationTemplate', RecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPresentationTemplate')

    def UpdateRecordTime(self, value, qualifier):

        RecordTimeCmdString = '* TIME ? \r'
        self.__UpdateHelper('RecordTime', RecordTimeCmdString, value, qualifier)

    def __MatchRecordTime(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('RecordTime', value, None)

    def UpdateScheduleType(self, value, qualifier):

        ScheduleTypeCmdString = '* SCHEDULETYPE ? \r'
        self.__UpdateHelper('ScheduleType', ScheduleTypeCmdString, value, qualifier)

    def __MatchScheduleType(self, match, tag):

        ValueStateValues = {
            'Create' : 'Create', 
            'CreateAndLoad' : 'Create And Load', 
            'CreateLoadAndStart' : 'Create Load And Start', 
            'CreateLoadStartAndStop' : 'Create Load Start And Stop', 
            'None' : 'None'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScheduleType', value, None)

    def UpdateServerConnectionInfo(self, value, qualifier):

        index = qualifier['Index']
        if 0 <= int(index) <= 9:
            ServerConnectionInfoCmdString = '* SERVERCONNECTIONINFO {} ? \r'.format(index)
            self.__UpdateHelper('ServerConnectionInfo', ServerConnectionInfoCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateServerConnectionInfo')

    def __MatchServerConnectionInfo(self, match, tag):

        index = match.group(1).decode()

        if 0 <= int(index) <= 9:
            name = match.group(2).decode().strip('"')
            url = match.group(3).decode()

            self.WriteStatus('ServerConnectionInfo', name, {'Index': index, 'Type': 'Name'})
            self.WriteStatus('ServerConnectionInfo', url, {'Index': index, 'Type': 'URL'})

    def SetServerConnectionNameCommand(self, value, qualifier):

        name = value
        if name:
            ServerConnectionNameCommandCmdString = '* SERVERCONNECTIONNAME {} \r'.format(name)
            self.__SetHelper('ServerConnectionNameCommand', ServerConnectionNameCommandCmdString, None, qualifier)
        else:
            self.Discard('Invalid Command for SetServerConnectionNameCommand')

    def UpdateServerConnectionNameStatus(self, value, qualifier):

        ServerConnectionNameStatusCmdString = '* SERVERCONNECTIONNAME ? \r'
        self.__UpdateHelper('ServerConnectionNameStatus', ServerConnectionNameStatusCmdString, value, qualifier)

    def __MatchServerConnectionNameStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ServerConnectionNameStatus', value, None)

    def SetShutdown(self, value, qualifier):

        ShutdownCmdString = '* SHUTDOWN \r'
        self.__SetHelper('Shutdown', ShutdownCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Publish': 'PUBLISH CD',
            'Pause': 'PAUSE',
            'Stop': 'STOP',
            'Record': 'RECORD',
                    'Add Chapter': 'ADDCHAPTER'
        }

        TransportCmdString = '* {0} \r'.format(ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetWakePreview(self, value, qualifier):

        WakePreviewCmdString = '* WAKEPREVIEW \r'
        self.__SetHelper('WakePreview', WakePreviewCmdString, value, qualifier)

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
       
        self.Error(['An Error has occurred.'])

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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

