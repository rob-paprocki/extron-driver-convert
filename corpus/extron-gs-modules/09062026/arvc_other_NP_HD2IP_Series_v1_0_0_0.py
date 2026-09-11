from json import loads, dumps
import urllib.error
import urllib.request
import base64
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
            'Channel': { 'Status': {}},
            'ChannelUpDownButton': { 'Status': {}},
            'EDID': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'HDCPMode': { 'Status': {}},
            'HDMIOut': { 'Status': {}},
            'USBOverIP': { 'Status': {}},
            'USBOverIPStatus': { 'Status': {}},
            'VideoWall': {'Parameters':['X1','Y1','X2','Y2','Rotation'], 'Status': {}},
            }

    def SetChannel(self, value, qualifier):

        ChannelCmdString = '/cgi-bin/query.cgi?cmd=set_channel+{}'.format(value)
        self.__SetHelper('Channel', value, qualifier, ChannelCmdString)

    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = '/cgi-bin/query.cgi?cmd=get_channel'
        res = self.__UpdateHelper('Channel', value, qualifier, ChannelCmdString)
        if res:
            try:
                value = str(int(res))
                self.WriteStatus('Channel', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Channel: Invalid/unexpected response'])

    def SetChannelUpDownButton(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'on', 
            'Disable' : 'off'
        }

        ChannelUpDownButtonCmdString = '/cgi-bin/query.cgi?cmd=set_ud_buttons+{}'.format(ValueStateValues[value])
        self.__SetHelper('ChannelUpDownButton', value, qualifier, ChannelUpDownButtonCmdString)

    def UpdateChannelUpDownButton(self, value, qualifier):

        ValueStateValues = {
            'on'  : 'Enable', 
            'off' : 'Disable'
        }

        ChannelUpDownButtonCmdString = '/cgi-bin/query.cgi?cmd=get_ud_buttons'
        res = self.__UpdateHelper('ChannelUpDownButton', value, qualifier, ChannelUpDownButtonCmdString)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ChannelUpDownButton', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Channel Up/Down Button: Invalid/unexpected response'])

    def SetEDID(self, value, qualifier):

        ValueStateValues = {
            'DVI 1200' : 'dvi1200', 
            'DVI 1080' : 'dvi1080', 
            'HDMI 4K'  : 'hdmi4k', 
            'HDMI HD'  : 'hdmihd', 
            'HDMI 720' : 'hdmi720', 
            'User'     : 'usr'
        }

        EDIDCmdString = '/cgi-bin/query.cgi?cmd=set_edid+{}'.format(ValueStateValues[value])
        self.__SetHelper('EDID', value, qualifier, EDIDCmdString)
    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '/cgi-bin/query.cgi?cmd=get_version'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, FirmwareVersionCmdString)
        if res:
            try:
                value = str(res)
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        HDCPModeCmdString = '/cgi-bin/query.cgi?cmd=set_hdcp+{}'.format(ValueStateValues[value])
        self.__SetHelper('HDCPMode', value, qualifier, HDCPModeCmdString)

    def UpdateHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        HDCPModeCmdString = '/cgi-bin/query.cgi?cmd=get_hdcp'
        res = self.__UpdateHelper('HDCPMode', value, qualifier, HDCPModeCmdString)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('HDCPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HDCP Mode: Invalid/unexpected response'])

    def SetHDMIOut(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        HDMIOutCmdString = '/cgi-bin/query.cgi?cmd=set_hdmiout+{}'.format(ValueStateValues[value])
        self.__SetHelper('HDMIOut', value, qualifier, HDMIOutCmdString)

    def UpdateHDMIOut(self, value, qualifier):

        ValueStateValues = {
            'on' : 'On', 
            'off' : 'Off'
        }

        HDMIOutCmdString = '/cgi-bin/query.cgi?cmd=get_hdmiout'
        res = self.__UpdateHelper('HDMIOut', value, qualifier, HDMIOutCmdString)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('HDMIOut', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HDMI Out: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        string = qualifier['String']
        if string:
            OnScreenDisplayCmdString = '/cgi-bin/query.cgi?cmd=set_osd+{}'.format(string)
        else:
            OnScreenDisplayCmdString = '/cgi-bin/query.cgi?cmd=set_osd'
        self.__SetHelper('OnScreenDisplay', value, qualifier, OnScreenDisplayCmdString)

    def SetUSBOverIP(self, value, qualifier):

        USBOverIPCmdString = '/cgi-bin/query.cgi?cmd=request_usb'
        self.__SetHelper('USBOverIP', value, qualifier, USBOverIPCmdString)
    def UpdateUSBOverIPStatus(self, value, qualifier):

        ValueStateValues = {
            's_srv_on'     : 'Connection', 
            's_srv_search' : 'Cutting'
        }

        USBOverIPStatusCmdString = '/cgi-bin/query.cgi?cmd=get_usb_status'
        res = self.__UpdateHelper('USBOverIPStatus', value, qualifier, USBOverIPStatusCmdString)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('USBOverIPStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['USB Over IP Status: Invalid/unexpected response'])

    def SetVideoWall(self, value, qualifier):

        RotationStates = {
            'No Rotation' : '0', 
            '180 Degrees' : '3', 
            '90 Degrees'  : '6'
        }

        x1 = qualifier['X1']
        y1 = qualifier['Y1']
        x2 = qualifier['X2']
        y2 = qualifier['Y2']
        rotate = qualifier['Rotation']
        if x1 and y1 and x2 and y2 and rotate in RotationStates:
            VideoWallCmdString = '/cgi-bin/query.cgi?cmd=setup_vw2+{}+{}+{}+{}+{}'.format(x1, y1, x2, y2, RotationStates[rotate])
            self.__SetHelper('VideoWall', value, qualifier, VideoWallCmdString)
        else:
            self.Discard('Invalid Command for SetVideoWall')

        res = response.read().decode()
        return res

    def __CheckResponseForErrors(self, sourceCmdName, response):
        
        res = response.read().decode()
        return res
        
    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True
        ipadd = re.search('http://(\S+):[0-9]+/',self.RootURL)
        IPAddress = ipadd.group(1)
        url = 'http://{0}{1}'.format(IPAddress, url)
        headers = {'Content-Type': 'text/xml'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        try:
            res = self.Opener.open(my_request, timeout=10)             
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        ipadd = re.search('http://(\S+):[0-9]+/',self.RootURL)
        IPAddress = ipadd.group(1)
        url = 'http://{0}{1}'.format(IPAddress, url)
        headers = {'Content-Type': 'text/xml'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful            
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