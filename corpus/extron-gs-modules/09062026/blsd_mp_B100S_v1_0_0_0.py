import urllib.error
import urllib.request
import re
from extronlib.system import Wait, ProgramLog
import base64
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
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
            'AlbumName': { 'Status': {}},
            'ArtistName': { 'Status': {}},
            'CurrentTrackLength': { 'Status': {}},
            'CurrentTrackTime': { 'Status': {}},
            'CurrentTrackTitle': {'Parameters':['Number'], 'Status': {}},
            'Mute': { 'Status': {}},
            'Playback': { 'Status': {}},
            'Preset': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'Shuffle': { 'Status': {}},
            'Volume': { 'Status': {}},
            }   
        
        self.albumRegex = re.compile('<album>([\s\S]+?)</album>')
        self.artistRegex = re.compile('<artist>([\s\S]+?)</artist>')
        self.titleRegex = re.compile('<title([1-3])>([\s\S]+?)</title[1-3]>')
        self.totlenRegex = re.compile('<totlen>(\d+?)</totlen>')
        self.secsRegex = re.compile('<secs>(\d+?)</secs>')
        self.stateRegex = re.compile('<state>([\s\S]+?)</state>')
        self.muteRegex = re.compile('<mute>(0|1)</mute>')
        self.volumeRegex = re.compile('<volume>(-?\d+?)</volume>')
        self.repeatRegex = re.compile('<repeat>([0-2])</repeat>')
        self.shuffleRegex = re.compile('<shuffle>(0|1)</shuffle>')

    def UpdateAlbumName(self, value, qualifier):

        StateValues = {
            '1': 'On', 
            '0': 'Off'
        }
        RepeatValues = {
            '0': 'Current Queue', 
            '1': 'Current Track', 
            '2': 'Off'
        }
        PlaybackValues = {
            'play'       : 'Play', 
            'pause'      : 'Pause', 
            'stop'       : 'Stop', 
            'stream'     : 'Streaming', 
            'Connecting' : 'Connecting', 
        }
        AlbumNameCmdString = 'Status'
        res = self.__UpdateHelper('AlbumName', value, qualifier, AlbumNameCmdString)
        if res:
            try:
                value = re.findall(self.albumRegex, res)[0]
                self.WriteStatus('AlbumName', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Album Name: Invalid/unexpected response'])
            try:
                value = re.findall(self.artistRegex, res)[0]
                self.WriteStatus('ArtistName', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Artist Name: Invalid/unexpected response'])  
            try:
                value = re.findall(self.totlenRegex, res)[0]
                formatTime = time.strftime('%M:%S', time.localtime(int(value)))
                self.WriteStatus('CurrentTrackLength', formatTime, qualifier)
            except (ValueError, IndexError):
                self.Error(['Current Track Length: Invalid/unexpected response']) 
            try:
                value = re.findall(self.secsRegex, res)[0]
                formatTime = time.strftime('%M:%S', time.localtime(int(value)))
                self.WriteStatus('CurrentTrackTime', formatTime, qualifier)
            except (ValueError, IndexError):
                self.Error(['Current Track Time: Invalid/unexpected response']) 
            try:
                value = re.findall(self.titleRegex, res)
                self.WriteStatus('CurrentTrackTitle', value[0][1], {'Number' : value[0][0]})
                self.WriteStatus('CurrentTrackTitle', value[1][1], {'Number' : value[1][0]})
                self.WriteStatus('CurrentTrackTitle', value[2][1], {'Number' : value[2][0]})
            except (ValueError, IndexError):
                self.Error(['Current Track Title: Invalid/unexpected response']) 
            try:
                value = StateValues[re.findall(self.muteRegex, res)[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response']) 
            try:
                value = re.findall(self.stateRegex, res)[0]
                if value in PlaybackValues:
                    self.WriteStatus('Playback', PlaybackValues[value], qualifier)
                else:
                    self.WriteStatus('Playback', 'Other', qualifier)
            except (KeyError, IndexError):
                self.Error(['Playback: Invalid/unexpected response'])  
            try:
                value = RepeatValues[re.findall(self.repeatRegex, res)[0]]
                self.WriteStatus('Repeat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Repeat: Invalid/unexpected response']) 
            try:
                value = StateValues[re.findall(self.shuffleRegex, res)[0]]
                self.WriteStatus('Shuffle', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Shuffle: Invalid/unexpected response'])
            try:
                value = int(re.findall(self.volumeRegex, res)[0])
                if value != -1: # Means Player volume Fixed
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])  

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        MuteCmdString = 'Volume?mute={0}'.format(ValueStateValues[value])
        self.__SetHelper('Mute', value, qualifier, MuteCmdString)
    
    def UpdateMute(self, value, qualifier):
        self.UpdateAlbumName(value, qualifier)

    def SetPlayback(self, value, qualifier):

        ValueStateValues = {
            'Play'  : 'Play', 
            'Pause' : 'Pause', 
            'Stop'  : 'Stop', 
            'Skip'  : 'Skip', 
            'Back'  : 'Back', 
        }

        PlaybackCmdString = ValueStateValues[value]
        if value not in ['Skip', 'Back']:
            self.__SetHelper('Playback', value, qualifier, PlaybackCmdString)

    def UpdatePlayback(self, value, qualifier):
        self.UpdateAlbumName(value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PresetCmdString = 'Preset?id={0}'.format(value)
            self.__SetHelper('Preset', value, qualifier, PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Current Queue' : '0', 
            'Current Track' : '1', 
            'Off'           : '2'
        }

        RepeatCmdString = 'Repeat?state={0}'.format(ValueStateValues[value])
        self.__SetHelper('Repeat', value, qualifier, RepeatCmdString)
    
    def UpdateRepeat(self, value, qualifier):
        self.UpdateAlbumName(value, qualifier)

    def SetShuffle(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        ShuffleCmdString = 'Shuffle?state={0}'.format(ValueStateValues[value])
        self.__SetHelper('Shuffle', value, qualifier, ShuffleCmdString)
    
    def UpdateShuffle(self, value, qualifier):
        self.UpdateAlbumName(value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'Volume?level={0}'.format(value)
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString)
        else:
            self.Discard('Invalid Command for SetVolume')
    
    def UpdateVolume(self, value, qualifier):
        self.UpdateAlbumName(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier,url, data=None):
        self.Debug = True
        headers = {'Content-Type': 'application/xml'}
        url = ''.join([self.RootURL,url])
        
        my_request = urllib.request.Request(url, data, headers=headers)
        try:
            res = self.Opener.open(my_request, timeout=5)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

    def __UpdateHelper(self, command, value, qualifier, url, data=None):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        headers = {'Content-Type': 'application/xml'}
        url = ''.join([self.RootURL,url])
        my_request = urllib.request.Request(url, data=None, headers=headers)
        
        try:
            res = self.Opener.open(my_request, timeout=5) # open() returns a http.client.HTTPResponse object if successful
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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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