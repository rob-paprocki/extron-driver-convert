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
            'AcceptMeeting': { 'Status': {}},
            'AcceptPresenter': { 'Status': {}},
            'AddressBook': { 'Status': {}},
            'AudioMuteStatus': {'Parameters':['Source'], 'Status': {}},
            'DuplicatePrimary': { 'Status': {}},
            'Meeting': {'Parameters':['Site Names'], 'Status': {}},
            'MoveDVI': { 'Status': {}},
            'MoveSource': {'Parameters':['Source'], 'Status': {}},
            'PrimaryOutput': { 'Status': {}},
            'Restart': { 'Status': {}},
            'SecuritySession': {'Parameters':['Minutes','Password'], 'Status': {}},
            'Shutdown': { 'Status': {}},
            'SourceConnection': {'Parameters':['Source'], 'Status': {}},
            'SourceName': {'Parameters':['Source'], 'Status': {}},
            'SourceType': {'Parameters':['Source'], 'Status': {}},
            'StartPresenting': { 'Status': {}},
            'ToggleAudio': {'Parameters':['Source'], 'Status': {}},
            'ToggleAutoShow': { 'Status': {}},
            'ToggleSourceVisibility': {'Parameters':['Source'], 'Status': {}},
            'TotalSources': { 'Status': {}},
            'VideoMuteStatus': {'Parameters':['Source'], 'Status': {}},
            'Whiteboard': { 'Status': {}},
            }

    def SetAcceptMeeting(self, value, qualifier):

        AcceptMeetingStateValues = {
            'Accept'   : 'true',
            'Decline'  : 'false'
            }

        AcceptMeetingCmdString = 'AcceptMeeting {0}\r'.format(AcceptMeetingStateValues[value])
        self.__SetHelper('AcceptMeeting', AcceptMeetingCmdString, value, qualifier)

    def SetAcceptPresenter(self, value, qualifier):

        AcceptPresenterStateValues = {
            'Accept'   : 'true',
            'Decline'  : 'false'
            }

        AcceptPresenterCmdString = 'AcceptPresenter {0}\r'.format(AcceptPresenterStateValues[value])
        self.__SetHelper('AcceptPresenter', AcceptPresenterCmdString, value, qualifier)

    def UpdateAddressBook(self, value, qualifier):

        AddressBookCmdString = 'GetAddressBook\r'
        res = self.__UpdateHelper('AddressBook', AddressBookCmdString, value, qualifier)
        if res:
            try:
                RepIndex = res.find(' ', 8, len(res))
                NumberOfNames = int(res[8:RepIndex])
                SiteNames = res[RepIndex+1:-1]
                SiteNames = SiteNames.split()
                OldString = ''
                digit = 1

                for i in range(0, NumberOfNames):
                    newStatus = SiteNames[i]
                    digit = 1 + i
                    DigitString = ' {0}: '.format(digit)
                    Sequence = ('Name', newStatus)
                    NewString = DigitString.join(Sequence)
                    if OldString == '':
                        AddressBookString = NewString
                    else:
                        AddressBookString = OldString + ' ' + NewString

                    OldString = AddressBookString

                self.WriteStatus('AddressBook', AddressBookString, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampPower')

    def UpdateAudioMuteStatus(self, value, qualifier):

        AVStateValues = {
            'True'  : 'On', 
            'False' : 'Off'
            }

        SourceConnectionStateValues = {
            'True'  : 'Connected',
            'False' : 'Disconnected'
            }
        
        SourceConstraints = {
            'Min' : 0 
            }

        Source = qualifier['Source']

        if SourceConstraints['Min'] <= Source:
            AudioMuteStatusCmdString = 'GetSourceStatus {0}\r'.format(Source)
            res = self.__UpdateHelper('AudioMuteStatus', AudioMuteStatusCmdString, value, qualifier)
            if res:
                try:
                    firstIndex = 0
                    for i in range(0,5):
                        firstIndex = res.find(' ', firstIndex+i, len(res))     #7  , 16 , 20 , 26 , 31 , 36 , 38 , 43
                        secondIndex = res.find(' ' , firstIndex+1, len(res))   #16 , 20 , 26 , 31 , 36 , 38 , 43 , 49
                        if i == 0:
                            SourceName = res[firstIndex+1:secondIndex]
                            self.WriteStatus('SourceName', SourceName, qualifier)
                        elif i == 1:
                            SourceType = res[firstIndex+1:secondIndex]
                            self.WriteStatus('SourceType', SourceType, qualifier)
                        elif i == 2: 
                            AudioMute = AVStateValues[res[firstIndex+1:secondIndex]]
                            self.WriteStatus('AudioMuteStatus', AudioMute, qualifier)
                        elif i == 3:
                            SourceConnection = SourceConnectionStateValues[res[firstIndex+1:secondIndex]]
                            self.WriteStatus('SourceConnection', SourceConnection, qualifier)
                        elif i == 4:
                            VideoMute = AVStateValues[res[firstIndex+1:secondIndex]]
                            self.WriteStatus('VideoMuteStatus', VideoMute, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateLampPower')
        else:
            self.Discard('Invalid Command for UpdateAudioMuteStatus')

    def SetDuplicatePrimary(self, value, qualifier):

        DuplicatePrimaryStateValues = {
            'On'   : 'true',
            'Off'  : 'false'
        }

        DuplicatePrimaryCmdString = 'SetDuplicatePrimary {0}\r'.format(DuplicatePrimaryStateValues[value])
        self.__SetHelper('DuplicatePrimary', DuplicatePrimaryCmdString, value, qualifier)

    def SetMeeting(self, value, qualifier):

        SiteNameString = qualifier['Site Names'] 

        if value == 'Start':
            MeetingCmdString = 'StartMeeting {0}\r'.format(SiteNameString)
            self.__SetHelper('Meeting', MeetingCmdString, value, qualifier)
        elif value == 'End':
            MeetingCmdString = 'EndMeeting\r'
            self.__SetHelper('Meeting', MeetingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMeeting')

    def SetMoveDVI(self, value, qualifier):
     
        MoveDVICmdString = 'MoveDviToPositionOne {0}\r'.format(value)
        self.__SetHelper('MoveDVI', MoveDVICmdString, value, qualifier)

    def SetMoveSource(self, value, qualifier):

        SourceConstraints = {
            'Min' : 0 
            }

        Source = qualifier['Source']

        if SourceConstraints['Min'] <= Source:
            MoveSourceCmdString = 'MoveSourceToPositionOne {0}\r'.format(Source)
            self.__SetHelper('MoveSource', MoveSourceCmdString, value, qualifier)

        else:
            self.Discard('Invalid Command for SetMoveSource')

    def SetPrimaryOutput(self, value, qualifier):

        PrimaryOutputCmdString = 'SetPrimaryOutput {0}\r'.format(value)
        self.__SetHelper('PrimaryOutput', PrimaryOutputCmdString, value, qualifier)

    def SetRestart(self, value, qualifier):

        RestartCmdString = 'Restart\r'
        self.__SetHelper('Restart', RestartCmdString, value, qualifier)

    def SetSecuritySession(self, value, qualifier):

        MinutesConstraints = {
            'Min' : 0,
        }

        MinutesString = qualifier['Minutes']
        
        Password = qualifier['Password']
         
        if MinutesConstraints['Min'] <= MinutesString:
            if value == 'Start':
                SecuritySessionCmdString = '{0}Security {1} {2}\r'.format(value, Password, MinutesString)
            elif value == 'End':
                SecuritySessionCmdString = '{0}Security\r'.format(value)
            self.__SetHelper('SecuritySession', SecuritySessionCmdString, value, qualifier)

        else:
            self.Discard('Invalid Command for SetSecuritySession')

    def SetShutdown(self, value, qualifier):

        ShutdownCmdString = 'Shutdown\r'
        self.__SetHelper('Shutdown', ShutdownCmdString, value, qualifier)

    def UpdateSourceConnection(self, value, qualifier):

        self.UpdateAudioMuteStatus(value, qualifier)

    def UpdateSourceName(self, value, qualifier):

        self.UpdateAudioMuteStatus(value, qualifier)

    def UpdateSourceType(self, value, qualifier):

        self.UpdateAudioMuteStatus(value, qualifier)

    def SetStartPresenting(self, value, qualifier):

        StartPresentingCmdString = 'StartPresenting\r'
        self.__SetHelper('StartPresenting', StartPresentingCmdString, value, qualifier)

    def SetToggleAudio(self, value, qualifier):

        SourceConstraints = {
            'Min' : 0,
            }

        Source = qualifier['Source']

        if SourceConstraints['Min'] <= Source:
            ToggleAudioCmdString = 'ToggleAudio {0}\r'.format(Source)
            self.__SetHelper('ToggleAudio', ToggleAudioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetToggleAudio')

    def SetToggleAutoShow(self, value, qualifier):

        ToggleAutoShowCmdString = 'ToggleAutoShow\r'
        self.__SetHelper('ToggleAutoShow', ToggleAutoShowCmdString, value, qualifier)

    def SetToggleSourceVisibility(self, value, qualifier):

        SourceConstraints = {
            'Min' : 0,
            }

        Source = qualifier['Source']

        if SourceConstraints['Min'] <= Source:
            ToggleSourceVisibilityCmdString = 'ToggleSourceVisibility {0}\r'.format(Source)
            self.__SetHelper('ToggleSourceVisibility', ToggleSourceVisibilityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetToggleSourceVisibility')

    def UpdateTotalSources(self, value, qualifier):

        TotalSourcesCmdString = 'GetSources\r'
        res = self.__UpdateHelper('TotalSources', TotalSourcesCmdString, value, qualifier)
        if res:
            RepIndex = res.find(' ', 8, len(res))
            NumberOfSources = int(res[8:RepIndex])
            self.WriteStatus('TotalSources', NumberOfSources, qualifier)

    def UpdateVideoMuteStatus(self, value, qualifier):

        self.UpdateAudioMuteStatus(value, qualifier)

    def SetWhiteboard(self, value, qualifier):

        WhiteboardCmdString = '{0}Whiteboard\r'.format(value)
        self.__SetHelper('Whiteboard', WhiteboardCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {'Empty>'           : 'Data requested is not available.',
                       'InvalidCommand>'  : 'Invalid command specified.',
                       'InvalidArgCount>' : 'Missing required minimum number of arguments.',
                       'InvalidArgValue>' : 'One or more arguments were invalid.',
                       'Execution>'       : 'An execution error occurred while processing the command.',
                       }   
        if response in ErrorStates:
            self.Error([ErrorStates[response]])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
            res = res.decode()
            if not res:
                print('Invalid/unexpected response')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
            res = res.decode()
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

