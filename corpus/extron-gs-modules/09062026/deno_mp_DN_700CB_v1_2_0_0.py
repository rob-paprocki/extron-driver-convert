from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'AlbumName': {'Status': {}},
            'ArtistName': {'Status': {}},
            'CurrentTrackTime': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'MediaStatus': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'RemainingTime': {'Status': {}},
            'Search': {'Status': {}},
            'Source': {'Status': {}},
            'TracklistSize': {'Status': {}},
            'TrackName': {'Status': {}},
            'TrackNumber': {'Status': {}},
            'Transport': {'Status': {}},
        }

        self.deli_tag = '\x06' if 'Serial' in self.ConnectionType else '\x15'

        def CheckQueryDelay():
            self.DeviceNotBusy = True
            
        self.DeviceNotBusy = True
        self.QueryDelayWait = Wait(2, CheckQueryDelay)

    def UpdateAlbumName(self, value, qualifier):

        AlbumNameCmdString = '@0?al\r'
        res = self.__UpdateHelper('AlbumName', AlbumNameCmdString, value, qualifier)
        if res:
            try:
                if res[0] == '\x15':
                    value = 'None'
                else:
                    value = res[10:-2]
                self.WriteStatus('AlbumName', value, qualifier)
            except IndexError:
                self.Error(['Album Name: Invalid/unexpected response'])

    def UpdateArtistName(self, value, qualifier):

        ArtistNameCmdString = '@0?at\r'
        res = self.__UpdateHelper('ArtistName', ArtistNameCmdString, value, qualifier)
        if res:
            try:
                if res[0] == '\x15':
                    value = 'None'
                else:
                    value = res[11:-2]
                self.WriteStatus('ArtistName', value, qualifier)
            except IndexError:
                self.Error(['Artist Name: Invalid/unexpected response'])

    def UpdateCurrentTrackTime(self, value, qualifier):

        CurrentTrackTimeCmdString = '@0?tl\r'
        res = self.__UpdateHelper('CurrentTrackTime', CurrentTrackTimeCmdString, value, qualifier)
        if res:
            try:
                hoursMinutes = divmod(int(res[4:7]), 60)  # format: (hh, mm)
                value = '{}:{}:{}'.format(str(hoursMinutes[0]).zfill(2), str(hoursMinutes[1]).zfill(2), res[7:9])  # format: hh:mm:ss
                self.WriteStatus('CurrentTrackTime', value, None)
            except (ValueError, IndexError):
                self.Error(['Current Track Time: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'PL\r\x06': 'Playing',
            'PP\r\x06': 'Paused',
            'ST\r\x06': 'Stopped',
            'PL\r\x15': 'Playing',
            'PP\r\x15': 'Paused',
            'ST\r\x15': 'Stopped',
            'DVFR': 'Fast Reverse',     # protocol has typo
            'DVFF': 'Fast Forward',     # protocol has typo
        }

        DeviceStatusCmdString = '@0?ST\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:8]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = '@0?ET\r'
        res = self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{}:{}:{}'.format(res[4:7], res[7:9], res[9:11])    # format: hhh:mm:ss
                self.WriteStatus('ElapsedTime', value, qualifier)
            except IndexError:
                self.Error(['Elapsed Time: Invalid/unexpected response'])

    def UpdateMediaStatus(self, value, qualifier):

        ValueStateValues = {
            'NC': 'No Disc',
            'CI': 'Disc In',
        }

        MediaStatusCmdString = '@0?CD\r'
        res = self.__UpdateHelper('MediaStatus', MediaStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:6]]
                self.WriteStatus('MediaStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Media Status: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '@0mt01\r',
            'Off': '@0mt00\r',
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        MuteCmdString = '@0?mt\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '@0PW00\r',    # query delays based on testing
            'Off': '@0PW01\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off',
        }

        PowerCmdString = '@0?PW\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateRemainingTime(self, value, qualifier):

        RemainingTimeCmdString = '@0?RM\r'
        res = self.__UpdateHelper('RemainingTime', RemainingTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{}:{}:{}'.format(res[4:7], res[7:9], res[9:11])    # format: hhh:mm:ss
                self.WriteStatus('RemainingTime', value, qualifier)
            except IndexError:
                self.Error(['Remaining Time: Invalid/unexpected response'])

    def SetSearch(self, value, qualifier):

        ValueStateValues = {
            'Fast Reverse': '@0PCSLSR\r',
            'Fast Forward': '@0PCSLSF\r',
        }

        SearchCmdString = ValueStateValues[value]
        self.__SetHelper('Search', SearchCmdString, value, qualifier)

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'CD': 'CD',
            'Bluetooth': 'BT',
            'USB Drive': 'US',
            'Network Drive': 'NE',
            'Line or AUX Input': 'LN',
        }

        SourceCmdString = '@0SS{}\r'.format(ValueStateValues[value])
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            'CD': 'CD',
            'BT': 'Bluetooth',
            'US': 'USB Drive',
            'NE': 'Network Drive',
            'LN': 'Line or AUX Input',
        }

        SourceCmdString = '@0?SS\r'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4:-2]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source: Invalid/unexpected response'])

    def UpdateTracklistSize(self, value, qualifier):

        TracklistSizeCmdString = '@0?Tt\r'
        res = self.__UpdateHelper('TracklistSize', TracklistSizeCmdString, value, qualifier)
        if res:
            try:
                if res[4:8] == 'UNKN':
                    value = 0
                else:
                    value = int(res[4:8])
                self.WriteStatus('TracklistSize', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Tracklist Size: Invalid/unexpected response'])

    def UpdateTrackName(self, value, qualifier):

        TrackNameCmdString = '@0?ti\r'
        res = self.__UpdateHelper('TrackName', TrackNameCmdString, value, qualifier)
        if res:
            try:
                if res[0] == '\x15':
                    value = 'None'
                else:
                    value = res[10:-2]
                self.WriteStatus('TrackName', value, qualifier)
            except IndexError:
                self.Error(['Track Name: Invalid/unexpected response'])

    def SetTrackNumber(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 2000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrackNumberCmdString = '@0Tr{0:04}\r'.format(value)
            self.__SetHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackNumber')

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = '@0?Tr\r'
        res = self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)
        if res:
            try:
                if res[4:8] == 'UNKN':
                    value = 0
                else:
                    value = int(res[4:8])
                self.WriteStatus('TrackNumber', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Track Number: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '@02353\r',
            'Pause': '@02348\r',
            'Stop': '@02354\r',
            'Next': '@02332\r',
            'Previous': '@02333\r',
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if '@0BDERBUSY' in response:
            self.Error(['Device is busy'])
            response = ''

            self.DeviceNotBusy = False
            self.QueryDelayWait.Restart()

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if self.DeviceNotBusy:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.deli_tag)
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.DeviceNotBusy:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.deli_tag)
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