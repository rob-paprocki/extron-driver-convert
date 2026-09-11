import base64
import urllib.error
import urllib.request
import re

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
            'GlobalGroup': { 'Status': {}},
            'Group': {'Parameters': ['Group'], 'Status': {}},
            'LiveMode': { 'Status': {}},
            'LiveModeLayout': { 'Status': {}},
            'Profile': { 'Status': {}},
            'USBOutput': { 'Status': {}},
        }

        self.LiveModeLayoutRegex = re.compile('/request=getLiveLayout live layout=([0-5])')
        self.USBOutputRegex = re.compile('TrkBox_Usb_output_switch=([012])')

    def SetGlobalGroup(self, value, qualifier):

        ValueStateValues = {
            'Enable':   'enableAll',
            'Disable':  'disableAll',
            'Pause':    'pause',
            'Resume':   'resume'
        }

        if value in ValueStateValues:
            GlobalGroupCmdString = 'request={}'.format(ValueStateValues[value])
            self.__SetHelper('GlobalGroup', value, qualifier, GlobalGroupCmdString)
        else:
            self.Discard('Invalid Command for SetGlobalGroup')

    def SetGroup(self, value, qualifier):

        group = qualifier['Group']

        ValueStateValues = [
            'Enable',
            'Disable'
        ]

        if 1 <= group <= 25 and value in ValueStateValues:
            GroupCmdString = 'request={}&group={}'.format(value.lower(), group)
            self.__SetHelper('Group', value, qualifier, GroupCmdString)
        else:
            self.Discard('Invalid Command for SetGroup')

    def SetLiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':   'enable',
            'Off':  'disable'
        }

        if value in ValueStateValues:
            LiveModeCmdString = 'request={}LiveMode'.format(ValueStateValues[value])
            self.__SetHelper('LiveMode', value, qualifier, LiveModeCmdString)
        else:
            self.Discard('Invalid Command for SetLiveMode')

    def SetLiveModeLayout(self, value, qualifier):

        ValueStateValues = {
            'PIP':              '0',
            'Single':           '1',
            'Side-By-Side':     '2',
            'Main Speaker 1':   '3',
            'Main Speaker 2':   '4',
            'Quad View':        '5'
        }

        if value in ValueStateValues:
            LiveModeLayoutCmdString = 'request=setLiveLayout&liveLayout={}'.format(ValueStateValues[value])
            self.__SetHelper('LiveModeLayout', value, qualifier, LiveModeLayoutCmdString)
        else:
            self.Discard('Invalid Command for SetLiveModeLayout')

    def UpdateLiveModeLayout(self, value, qualifier):

        ValueStateValues = {
            '0': 'PIP',
            '1': 'Single',
            '2': 'Side-By-Side',
            '3': 'Main Speaker 1',
            '4': 'Main Speaker 2',
            '5': 'Quad View'
        }
        
        LiveModeLayoutCmdString = 'request=getLiveLayout'
        res = self.__UpdateHelper('LiveModeLayout', value, qualifier, LiveModeLayoutCmdString)
        if res:
            try:
                value = ValueStateValues[self.LiveModeLayoutRegex.match(res).group(1)]
                self.WriteStatus('LiveModeLayout', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Live Mode Layout: Invalid/unexpected response'])

    def SetProfile(self, value, qualifier):

        if 1 <= value:
            ProfileCmdString = 'request=setProfile&profile={}'.format(value)
            self.__SetHelper('Profile', value, qualifier, ProfileCmdString)
        else:
            self.Discard('Invalid Command for SetProfile')

    def SetUSBOutput(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            '1':    '1',
            '2':    '2'
        }

        if value in ValueStateValues:
            USBOutputCmdString = 'cgi-bin?Set=TrkBox_Usb_output_switch,3,{}'.format(ValueStateValues[value])
            self.__SetHelper('USBOutput', value, qualifier, USBOutputCmdString)
        else:
            self.Discard('Invalid Command for SetUSBOutput')

    def UpdateUSBOutput(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': '1',
            '2': '2'
        }
        
        USBOutputCmdString = 'cgi-bin?Get=TrkBox_Usb_output_switch'
        res = self.__UpdateHelper('USBOutput', value, qualifier, USBOutputCmdString)
        if res:
            try:
                value = ValueStateValues[self.USBOutputRegex.match(res).group(1)]
                self.WriteStatus('USBOutput', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['USB Output: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()
        
    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {'Authorization' : self.authentication}

        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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

        url = '{}{}'.format(self.RootURL, url)
        headers = {'Authorization' : self.authentication}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)
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