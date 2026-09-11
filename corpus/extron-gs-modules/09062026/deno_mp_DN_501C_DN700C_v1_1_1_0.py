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
            'AlbumName': { 'Status': {}},
            'ArtistName': { 'Status': {}},
            'CurrentMedia': { 'Status': {}},
            'CurrentTrackName': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'DiscStatus': { 'Status': {}},
            'FolderStatus': { 'Status': {}},
            'HotStartCueUp': { 'Status': {}},
            'HotStartPlay': { 'Status': {}},
            'PlayMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'TitleName': { 'Status': {}},
            'TotalTrackNumber': { 'Status': {}},
            'TrackElapseTime': { 'Status': {}},
            'TrackNumber': { 'Status': {}},
            'TrackRemainTime': { 'Status': {}},
            'Transport': { 'Status': {}},
            }

        
        self.regex = {
            'AlbumName'        : re.compile(b'\x15|@0al[\s\S]+\r'),
            'ArtistName'       : re.compile(b'\x15|@0at[\s\S]+\r'),
            'CurrentMedia'     : re.compile(b'\x15|@0MM[\s\S]+\r'),
            'CurrentTrackName' : re.compile(b'\x15|@0tn[\s\S]+\r'),
            'DeviceStatus'     : re.compile(b'\x15|@0ST[\s\S]+\r'),
            'DiscStatus'       : re.compile(b'\x15|@0CD[\s\S]+\r'),
            'FolderStatus'     : re.compile(b'\x15|@0SF[\s\S]+\r'),
            'HotStartPlay'     : re.compile(b'\x15|@0HP[\s\S]+\r'),
            'PlayMode'         : re.compile(b'\x15|@0PM[\s\S]+\r'),
            'Power'            : re.compile(b'\x15|@0PW[\s\S]+\r'),
            'TitleName'        : re.compile(b'\x15|@0ti[\s\S]+\r'),
            'TotalTrackNumber' : re.compile(b'\x15|@0Tt[\s\S]+\r'),
            'TrackElapseTime'  : re.compile(b'\x15|@0ET[\s\S]+\r'),
            'TrackNumber'      : re.compile(b'\x15|@0Tr[\s\S]+\r'),
            'TrackRemainTime'  : re.compile(b'\x15|@0RM[\s\S]+\r')
            }


    def UpdateAlbumName(self, value, qualifier):

        AlbumNameCmdString = '@0?al\r'
        res = self.__UpdateHelper('AlbumName', AlbumNameCmdString, value, qualifier)
        if res:
            try:
                value = res.split('@0al')[1][:-1]
                self.WriteStatus('AlbumName', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Album Name: Invalid/unexpected response'])
        else:
            self.WriteStatus('AlbumName', 'No Info', qualifier)

    def UpdateArtistName(self, value, qualifier):

        ArtistNameCmdString = '@0?at\r'
        res = self.__UpdateHelper('ArtistName', ArtistNameCmdString, value, qualifier)
        if res:
            try:
                value = res.split('@0at')[1][:-1]
                self.WriteStatus('ArtistName', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Artist Name: Invalid/unexpected response'])
        else:
            self.WriteStatus('ArtistName', 'No Info', qualifier)

    def SetCurrentMedia(self, value, qualifier):

        ValueStateValues = {
            'USB' : '@0MMUS\r', 
            'SD1' : '@0MMS1\r', 
            'SD2' : '@0MMS2\r', 
            'NET' : '@0MMNE\r', 
            'CD'  : '@0MMCD\r'
        }

        CurrentMediaCmdString = ValueStateValues[value]
        self.__SetHelper('CurrentMedia', CurrentMediaCmdString, value, qualifier)

    def UpdateCurrentMedia(self, value, qualifier):

        ValueStateValues = {
            'US' : 'USB', 
            'S1' : 'SD1', 
            'S2' : 'SD2', 
            'NE' : 'NET', 
            'CD' : 'CD'
        }

        CurrentMediaCmdString = '@0?MM\r'
        res = self.__UpdateHelper('CurrentMedia', CurrentMediaCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('CurrentMedia', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Current Media: Invalid/unexpected response'])

    def UpdateCurrentTrackName(self, value, qualifier):

        current_track = self.ReadStatus('TrackNumber', qualifier)
        if current_track:
            CurrentTrackNameCmdString = '@0?tn{:04}\r'.format(current_track)
            res = self.__UpdateHelper('CurrentTrackName', CurrentTrackNameCmdString, value, qualifier)
            if res:
                try:
                    value = (res.split('/')[-1]).split('.')[0]
                    self.WriteStatus('CurrentTrackName', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Current Track Name: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCurrentTrackName')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'ST' : 'Stop',
            'AC' : 'AutoCue',
            'PL' : 'Play',
            'PP' : 'Play Pause',
            'PR' : 'Repeat Play Pause',
            'FF' : 'Fast Forward',
            'RW' : 'Rewind',
            'AB' : 'A-B Repeat',
            'CE' : 'Cue Execute',
            'LD' : 'Loading',
            'BY' : 'Busy',
            'FL' : 'File List',
            'ED' : 'Track Edit/Preset',
            'ER' : 'Operation Error'
        }

        DeviceStatusCmdString = '@0?ST\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateDiscStatus(self, value, qualifier):

        ValueStateValues = {
            'NC' : 'No Disc', 
            'CI' : 'Disc In'
        }

        DiscStatusCmdString = '@0?CD \r'
        res = self.__UpdateHelper('DiscStatus', DiscStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('DiscStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Disc Status: Invalid/unexpected response'])

    def UpdateFolderStatus(self, value, qualifier):

        FolderStatusCmdString = '@0?SF\r'
        res = self.__UpdateHelper('FolderStatus', FolderStatusCmdString, value, qualifier)
        if res:
            try:
                value = res.split('@0SF')[1][1:-1]
                self.WriteStatus('FolderStatus', value, qualifier)
            except IndexError:
                self.Error(['Folder Status: Invalid/unexpected response'])

    def SetHotStartCueUp(self, value, qualifier):

        if 1 <= int(value) <= 20:
            HotStartCueUpCmdString = '@0HC{0:02}\r'.format(int(value))
            self.__SetHelper('HotStartCueUp', HotStartCueUpCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHotStartCueUp')
    def SetHotStartPlay(self, value, qualifier):

        if 1 <= int(value) <= 20:
            HotStartPlayCmdString = '@0HP{0:02}\r'.format(int(value))
            self.__SetHelper('HotStartPlay', HotStartPlayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHotStartPlay')

    def UpdateHotStartPlay(self, value, qualifier):

        HotStartPlayCmdString = '@0?HP\r'
        res = self.__UpdateHelper('HotStartPlay', HotStartPlayCmdString, value, qualifier)
        if res:
            try:
                value = res[-3:-1].lstrip('0')
                self.WriteStatus('HotStartPlay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Hot Start Play: Invalid/unexpected response'])

    def SetPlayMode(self, value, qualifier):

        ValueStateValues = {
            'Single'     : '@0PMSP\r', 
            'Continuous' : '@0PMCN\r'
        }

        PlayModeCmdString = ValueStateValues[value]
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def UpdatePlayMode(self, value, qualifier):

        ValueStateValues = {
            'SP' : 'Single', 
            'CN' : 'Continuous'
        }

        PlayModeCmdString = '@0?PM\r'
        res = self.__UpdateHelper('PlayMode', PlayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('PlayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'PW',
            'Off'   : '12'
        }

        PowerCmdString = '@023{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '00' : 'On',
            '01' : 'Off'
        }

        PowerCmdString = '@0?PW\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateTitleName(self, value, qualifier):

        TitleNameCmdString = '@0?ti\r'
        res = self.__UpdateHelper('TitleName', TitleNameCmdString, value, qualifier)
        if res:
            try:
                value = res.split('@0ti')[1][:-1]
                self.WriteStatus('TitleName', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Title Name: Invalid/unexpected response'])
        else:
            self.WriteStatus('TitleName', 'No Info', qualifier)

    def UpdateTotalTrackNumber(self, value, qualifier):

        TotalTrackNumberCmdString = '@0?Tt\r'
        res = self.__UpdateHelper('TotalTrackNumber', TotalTrackNumberCmdString, value, qualifier)
        if res:
            try:
                res = res.split('@0Tt')[1]
                self.WriteStatus('TotalTrackNumber', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Total Track Number: Invalid/unexpected response'])

    def UpdateTrackElapseTime(self, value, qualifier):

        TrackElapseTimeCmdString = '@0?ET\r'
        res = self.__UpdateHelper('TrackElapseTime', TrackElapseTimeCmdString, value, qualifier)
        if res:
            try:
                res = res.split('@0ET')[1]
                value = ''.join([res[0:3], ':', res[3:5], ':', res[5:7]])
                self.WriteStatus('TrackElapseTime', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Track Elapse Time: Invalid/unexpected response'])

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = '@0?Tr\r'
        res = self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-5:-1])
                self.WriteStatus('TrackNumber', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Track Number: Invalid/unexpected response'])

    def UpdateTrackRemainTime(self, value, qualifier):

        TrackRemainTimeCmdString = '@0?RM\r'
        res = self.__UpdateHelper('TrackRemainTime', TrackRemainTimeCmdString, value, qualifier)
        if res:
            try:
                res = res.split('@0RM')[1]
                value = ''.join([res[0:3], ':', res[3:5], ':', res[5:7]])
                self.WriteStatus('TrackRemainTime', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Track Remain Time: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play'         : '53',
            'Pause'        : '48',
            'Stop'         : '54',
            'Next'         : '32',
            'Previous'     : '33',
            'Skip Back'    : 'SB',
            'Fast Forward' : '52',
            'Rewind'       : '50',
        }

        TransportCmdString = '@023{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            response = response.decode()
            if response == '\x15':
                self.Error(['An error occured'])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = 1)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.regex[command])
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

