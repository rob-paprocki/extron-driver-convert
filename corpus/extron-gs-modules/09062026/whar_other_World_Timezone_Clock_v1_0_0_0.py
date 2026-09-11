import urllib.error
import urllib.request
import base64
import re

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}
        self.Commands = {
            'LocationSettingCommand': { 'Status': {}},
            'TimeZoneSettingCommand': { 'Status': {}},
            'UTCTimeSettingCommand': { 'Status': {}},
            'UTCTimeSettingString': { 'Status': {}},
            }
        
    def SetLocationSettingCommand(self, value, qualifier):
        if int(value) in range(8):
            cmdstring = qualifier['Location Legend']
            if cmdstring:
                LocationSettingCommandCmdString = 'legend?zone={}&text={}'.format(value,cmdstring.replace(' ','%20'))
                self.__SetHelper('LocationSettingCommand', value, qualifier, LocationSettingCommandCmdString)
        else:
            self.Discard('Invalid Command for SetLocationSettingCommand')

    def SetTimeZoneSettingCommand(self, value, qualifier):

        if int(value) in range(8):
            cmdstring = qualifier['UTC Offset']
            if cmdstring:
                TimeZoneSettingCommandCmdString = 'time?zone={}&offset={}'.format(value,cmdstring)
                self.__SetHelper('TimeZoneSettingCommand', value, qualifier, TimeZoneSettingCommandCmdString)
        else:
            self.Discard('Invalid Command for SetTimeZoneSettingCommand')

    def SetUTCTimeSettingCommand(self, value, qualifier):       
        good_time = re.match('^\d{4}\:((0[1-9])|(1[012]))\:((0[1-9])|([12]\d)|(3[01]))\:(([01][0-9])|(?:2[0123]))\:([0-5][0-9])\:([0-5][0-9])$', value)
        UTCTimeSettingCommandCmdString = 'utc?time={}'.format(value)
        if  good_time is not None:
            self.__SetHelper('UTCTimeSettingCommand', value, qualifier, UTCTimeSettingCommandCmdString)
        else:
            self.Discard('Invalid Command for SetUTCTimeSettingCommand')
    
    def __CheckResponseForErrors(self, sourceCmdName, response):
        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url, queryDelay=0):
        self.Debug = True
        if queryDelay > 0:
            self.queryDelay = queryDelay
        url = '{0}{1}'.format(self.RootURL, url)
        myRequest = urllib.request.Request(url)

        try:
            res = self.Opener.open(myRequest)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

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