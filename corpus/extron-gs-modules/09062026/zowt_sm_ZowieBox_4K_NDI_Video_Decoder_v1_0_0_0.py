from extronlib.system import ProgramLog, Wait
import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DecoderState': { 'Status': {}},
            'DisableNDIDecoding': { 'Status': {}},
            'EnableNDIDecoding': {'Parameters':['NDI Name'], 'Status': {}},
        }

    def UpdateDecoderState(self, value, qualifier):

        DecoderStateCmdString = 'streamplay?option=getinfo&login_check_flag=1'
        data = {
            'group' : 'streamplay',
            'opt' : 'get_decoder_state'
        }

        res = self.__UpdateHelper('DecoderState', value, qualifier, url=DecoderStateCmdString, data=json.dumps(data).encode())
        if res:
            try:
                ValueStateValues = {
                    1 : 'Streaming Enabled',
                    0 : 'Streaming Disabled'
                }

                value = ValueStateValues[res['data']['decoder_state']]
                self.WriteStatus('DecoderState', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Decoder State: Invalid/unexpected response'])

    def SetDisableNDIDecoding(self, value, qualifier):

        DisableNDIDecodingCmdString = 'streamplay?option=setinfo&login_check_flag=1'
        data = {
            'group' : 'streamplay_ndi',
            'opt' : 'ndi_close'
        }

        self.__SetHelper('DisableNDIDecoding', value, qualifier, url=DisableNDIDecodingCmdString, data=json.dumps(data).encode())

    def SetEnableNDIDecoding(self, value, qualifier):

        if qualifier['NDI Name']:
            EnableNDIDecodingCmdString = 'streamplay?option=setinfo&login_check_flag=1'
            data = {
                'group' : 'streamplay_ndi',
                'opt' : 'ndi_recv',
                'data' : {
                    'ndi_name' : qualifier['NDI Name']
                }
            }

            self.__SetHelper('EnableNDIDecoding', value, qualifier, url=EnableNDIDecodingCmdString, data=json.dumps(data).encode())
        else:
            self.Discard('Invalid Command for SetEnableNDIDecoding')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = json.loads(response.read().decode())
        if res['status'] != '00000':
            DEVICE_ERROR_CODES = {
                '00002' : 'Program is not ready',
                '00003' : 'Missing required parameters',
                '00004' : 'Product not supported',
                '00005' : 'Switch opening failed',
                '00006' : 'Switch not open',
                '00007' : 'Enable not open',
                '00008' : 'Verification code error',
                '00009' : 'The operation is too fast, please wait',
                '00010' : 'Restarting, please wait',
                '50001' : 'NDI activation failed',
                '50002' : 'NDI has been activated and does not need to be activated again',
                '60001' : 'Stream URL already exists',
                '60002' : 'Failed to start streaming',
                '60003' : 'Failed to close streaming',
                '60004' : 'Invalid URL',
                '60005' : 'Stream protocol is not supported',
                '60006' : 'Protocol mismatch',
                '60007' : 'The stream is open and needs to be closed before operation',
                '60008' : 'Invalid IP',
                '60009' : 'Invalid port',
                '60010' : 'Protocol selectId mismatch',
                '60011' : 'The number of streams reaches the maximum value',
                '60012' : 'Push type is not supported',
                '60013' : 'Invalid index',
                '70001' : 'Failed to connect to WiFi',
                '70002' : 'Wrong IP address',
                '70003' : 'IP address is occupied',
                '70004' : 'The data is the same and no modification is required',
                '70005' : 'Password length must be more than eight characters',
                '70006' : 'Account cannot be empty',
                '70007' : 'HTTP port is occupied',
                '70008' : 'RTMP port is occupied',
                '70009' : 'RTSP port is occupied',
                '70010' : 'VISCA TCP port is occupied',
                '70011' : 'VISCA UDP port is occupied',
                '70012' : 'WebSocket port is occupied',
                '70013' : 'RTP port is occupied',
                '70014' : 'Onvif port is occupied',
                '70015' : 'Onvif soap port is occupied',
                '70016' : 'No WiFi module',
                '80001' : 'User not found',
                '80002' : 'User already exists',
                '80003' : 'User is not logged in',
                '80004' : 'Non-admin account',
                '80005' : 'Wrong password',
                '80006' : 'File format error',
                '80007' : 'Upgrading firmware is illegal',
                '80008' : 'Log saving was not turned off before clearing the logs',
                '80009' : 'Log reading failed',
                '90001' : 'Please plug in the signal source before modifying the audio configuration',
                '100001' : 'Disk full',
                '100002' : 'Invalid storage medium',
                '100003' : 'Photo format is wrong',
                '100004' : 'Photo format is wrong',
                '100005' : 'Photo format is wrong',
                '100006' : 'Uninstall failed',
                '100007' : 'Disk not mounted',
                '100008' : 'Mount failed',
                '100009' : 'NAS service is busy',
                '100010' : 'Disk information has reached the maximum limit',
                '100011' : 'There is an open NAS device, please close it first',
                '100012' : 'Modification is not allowed when open',
                '100013' : 'NAS is not open',
                '100014' : 'Format failed',
                '100015' : 'Storage device is occupied',
                '110001' : 'The task has been started and cannot be modified',
                '110002' : 'Invalid index',
                '110003' : 'Task name already exists',
                '110004' : 'The mission has started. cannot be deleted',
                '110005' : 'Task startup failed',
                '110006' : 'Task exceeds maximum limit',
                '110007' : 'Recording in progress and cannot be modified',
                '110008' : 'Operating too fast',
                '120001' : 'Maximum value reached',
                '120003' : 'Startup failed',
                '120004' : 'Close failed',
                '120005' : 'The video module is not started and the layout cannot be started',
                '130001' : 'No signal source',
                '130002' : 'Not allowed to change output resolution',
                '130003' : 'Quality out of range',
                '130004' : 'Output loopout switching mode failed',
                '140001' : 'Decoded URL already exists',
                '140002' : 'Decoding address is full',
                '140003' : 'Invalid decoding index',
                '140004' : 'Decoding type is not supported',
                '140005' : 'Please close it before operating',
                '140006' : 'Decoding startup failed'
            }

            self.Error(['Error: {}.'.format(DEVICE_ERROR_CODES[res['status']])])
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
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
        headers = {}
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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port)
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