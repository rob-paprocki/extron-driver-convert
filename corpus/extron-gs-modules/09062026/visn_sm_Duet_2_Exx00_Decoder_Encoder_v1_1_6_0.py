from extronlib.system import Wait, ProgramLog
import re
import urllib.error
import urllib.request
import binascii

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

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
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioVolume': { 'Status': {}},
            'CECCommand': { 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'StreamAudio': { 'Status': {}},
            'StreamHost': {'Parameters': ['Address'], 'Status': {}},
            'StreamHostConnect': {'Parameters': ['Address', 'Videowall Enable'], 'Status': {}},
            'StreamVideo': { 'Status': {}},
            'StreamVideoPriority': { 'Status': {}},
            'VideoOutput': { 'Status': {}}
        }

        self.input_signal_status_regex = re.compile('VIDEO\.TIMING=(Not Available|Timing Table)')
            
    def __GetBasicAuthHeader(self):

        cred = '{}:{}'.format(self.deviceUsername, self.devicePassword)
        return binascii.b2a_base64(cred.encode()).decode().strip()
    
    def SetAudioVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&AUDIO.VOLUME={}&CMD=END'.format(
                                        value)
            self.__SetHelper('AudioVolume', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def SetCECCommand(self, value, qualifier):

        string = value

        if string:
            CECCommandCmdString = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&VIDEO.SEND_CEC_GENERIC={}&CMD=END'.format(string)
            self.__SetHelper('CECCommand', value, qualifier, url=CECCommandCmdString)
        else:
            self.Discard('Invalid Command for SetCECCommand')

    def UpdateInputSignalStatus(self, value, qualifier):

        ValueStateValues = {
            'Timing Table':     'Active',
            'Not Available':    'Not Active'
        }
        
        InputSignalStatusCmdString = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&QUERY.VIDEO_TIMING=TRUE&CMD=END'
        res = self.__UpdateHelper('InputSignalStatus', value, qualifier, url=InputSignalStatusCmdString)
        if res:
            try:
                value = ValueStateValues[self.input_signal_status_regex.search(res).group(1)]
                self.WriteStatus('InputSignalStatus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input Signal Status: Invalid/unexpected response'])

    def SetStreamAudio(self, value, qualifier):

        ValueStateValues = {
            'HDMI':   'HDMI',
            'DANTE':  'DANTE',
            'Analog': 'ANALOG',
            'Stream': 'STREAM',
            }

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.AUDIO={}&CMD=END'.format(
                                        ValueStateValues[value])
            self.__SetHelper('StreamAudio', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamAudio')

    def SetStreamHost(self, value, qualifier):

        ip_address = qualifier['Address']
        if ip_address:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.HOST={}&CMD=END'.format(
                                            ip_address)
            self.__SetHelper('StreamHost', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamHost')

    def SetStreamHostConnect(self, value, qualifier):

        VideowallEnableStates = ('True', 'False')

        vw_enable = qualifier['Videowall Enable']
        ip_address = qualifier['Address']
        if vw_enable in VideowallEnableStates and ip_address:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.HOST={}&VW.ACTIVE={}&STREAM.CONNECT=TRUE&CMD=END'.format(
                                        ip_address, vw_enable.upper())
            self.__SetHelper('StreamHostConnect', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamHostConnect')

    def SetStreamVideo(self, value, qualifier):

        ValueStateValues = {
            'Auto':   'AUTO',
            'HDMI 1': 'HDMI1',
            'HDMI 2': 'HDMI2',
            'USB C':  'USB-C',
            }

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.VIDEO={}&CMD=END'.format(
                                        ValueStateValues[value])
            self.__SetHelper('StreamVideo', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamVideo')
            
    def SetStreamVideoPriority(self, value, qualifier):

        ValueStateValues = {
            'HDMI1 HDMI2 USB-C': '1',
            'HDMI1 USB-C HDMI2': '2',
            'HDMI2 HDMI1 USB-C': '3',
            'HDMI2 USB-C HDMI1': '4',
            'USB-C HDMI1 HDMI2': '5',
            'USB-C HDMI2 HDMI1': '6',
            }

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.VIDEO_PRIORITY={}&CMD=END'.format(
                                        ValueStateValues[value])
            self.__SetHelper('StreamVideoPriority', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamVideoPriority')

    def SetVideoOutput(self, value, qualifier):

        ValueStateValues = [
            'Normal',
            'Off',
            'Standby',
            'Logo'
        ]

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&VIDEO.OUTPUT={}&CMD=END'.format(value.upper())
            self.__SetHelper('VideoOutput', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetVideoOutput')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode('iso-8859-1')

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Authorization': 'Basic {}'.format(self.__GetBasicAuthHeader()),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = urllib.request.urlopen(my_request, timeout=5) 
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

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Authorization': 'Basic {}'.format(self.__GetBasicAuthHeader())}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=5)
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