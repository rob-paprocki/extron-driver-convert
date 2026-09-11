from extronlib.system import Wait, ProgramLog
import re
import urllib.error
import urllib.request

class DeviceHTTPClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            try:
                pwd = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                pwd.add_password(None, self.RootURL, deviceUsername, devicePassword)
                self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(pwd))
            except Exception as e:
                self.Error(['Error', str(e)])

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
            'AudioOutMode': { 'Status': {}},
            'AudioOutSoundSource': { 'Status': {}},
            'HDMIOutStreamAudioMode': { 'Status': {}},
            'HDMIOutStreamAudioSource': { 'Status': {}},
            'SourceConnect': { 'Status': {}},
            'VirtualUSBCamera': { 'Status': {}},
        }

        self.AudioOutModeRegex = re.compile('var AuxEnable=\"([01])\"')
        self.AudioOutSoundSourceRegex = re.compile('var AuxIn=\"([01])\"')
        self.HDMIOutStreamAudioModeRegex = re.compile('var StreamEnable=\"([01])\"')
        self.HDMIOutStreamAudioSourceRegex = re.compile('var StreamIn=\"([01])\"')

    def SetAudioOutMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            AudioOutModeCmdString = 'cgi/audio.cgi?AuxEnable={}'.format(ValueStateValues[value])
            self.__SetHelper('AudioOutMode', value, qualifier, url=AudioOutModeCmdString)
        else:
            self.Discard('Invalid Command for SetAudioOutMode')

    def UpdateAudioOutMode(self, value, qualifier):

        AudioOutModeCmdString = 'cgi/inquiry.cgi?inqjs=audio'
        res = self.__UpdateHelper('AudioOutMode', value, qualifier, url=AudioOutModeCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1' : 'On',
                    '0' : 'Off'
                }

                valueMatch = re.search(self.AudioOutModeRegex, res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AudioOutMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Out Mode: Invalid/unexpected response'])
            try:
                ValueStateValues = {
                    '0' : 'Follow Stream',
                    '1' : 'Follow Routing'
                }

                valueMatch = re.search(self.AudioOutSoundSourceRegex, res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AudioOutSoundSource', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Out Sound Source: Invalid/unexpected response'])
            try:
                ValueStateValues = {
                    '1' : 'On',
                    '0' : 'Off'
                }

                valueMatch = re.search(self.HDMIOutStreamAudioModeRegex, res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('HDMIOutStreamAudioMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['HDMI Out Stream Audio Mode: Invalid/unexpected response'])
            try:
                ValueStateValues = {
                    '0' : 'Follow Stream',
                    '1' : 'Follow Routing'
                }

                valueMatch = re.search(self.HDMIOutStreamAudioSourceRegex, res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('HDMIOutStreamAudioSource', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['HDMI Out Stream Audio Source: Invalid/unexpected response'])

    def SetAudioOutSoundSource(self, value, qualifier):

        ValueStateValues = {
            'Follow Stream': '0',
            'Follow Routing': '1'
        }

        if value in ValueStateValues:
            AudioOutSoundSourceCmdString = 'cgi/audio.cgi?AuxIn={}'.format(ValueStateValues[value])
            self.__SetHelper('AudioOutSoundSource', value, qualifier, url=AudioOutSoundSourceCmdString)
        else:
            self.Discard('Invalid Command for SetAudioOutSoundSource')

    def SetHDMIOutStreamAudioMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            HDMIOutStreamAudioModeCmdString = 'cgi/audio.cgi?StreamEnable={}'.format(ValueStateValues[value])
            self.__SetHelper('HDMIOutStreamAudioMode', value, qualifier, url=HDMIOutStreamAudioModeCmdString)
        else:
            self.Discard('Invalid Command for SetHDMIOutStreamAudioMode')

    def SetHDMIOutStreamAudioSource(self, value, qualifier):

        ValueStateValues = {
            'Follow Stream'  : '0',
            'Follow Routing' : '1'
        }

        if value in ValueStateValues:
            HDMIOutStreamAudioSourceCmdString = 'cgi/audio.cgi?StreamIn={}'.format(ValueStateValues[value])
            self.__SetHelper('HDMIOutStreamAudioSource', value, qualifier, url=HDMIOutStreamAudioSourceCmdString)
        else:
            self.Discard('Invalid Command for SetHDMIOutStreamAudioSource')

    def SetSourceConnect(self, value, qualifier):

        if 0 <= value <= 255:
            SourceConnectCmdString = 'cgi/source.cgi?SrcConn={}'.format(value)
            self.__SetHelper('SourceConnect', value, qualifier, url=SourceConnectCmdString)
        else:
            self.Discard('Invalid Command for SetSourceConnect')

    def SetVirtualUSBCamera(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            VirtualUSBCameraCmdString = 'cgi/video.cgi?UVCCamOnOff={}'.format(ValueStateValues[value])
            self.__SetHelper('VirtualUSBCamera', value, qualifier, url=VirtualUSBCameraCmdString)
        else:
            self.Discard('Invalid Command for SetVirtualUSBCamera')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
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

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername='admin', devicePassword='9999', Model=None):
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