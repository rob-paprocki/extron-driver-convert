from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'Power': { 'Status': {}},
            'Relay': {'Parameters':['Number'], 'Status': {}},
            'Socket': {'Parameters':['Number'], 'Status': {}},
        }
    
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'ons', 
            'Off' : 'offs'
        }

        PowerCmdString = '{0}.cgi?led=1111111111111111'.format(ValueStateValues[value])
        self.__SetHelper('Power', value, qualifier, PowerCmdString)

    def SetRelay(self, value, qualifier):

        NumberStates = {
            '1' : 128, 
            '2' : 64, 
            '3' : 32, 
            '4' : 16, 
            '5' : 8, 
            '6' : 4, 
            '7' : 2, 
            '8' : 1
        }

        ValueStateValues = {
            'On'  : 'ons', 
            'Off' : 'offs'
        }
        number= qualifier['Number']
        if number in NumberStates: 
            RelayCmdString = '{0}.chi?led={1}00000000'.format(ValueStateValues[value],bin(NumberStates[number])[2:].zfill(8))
            self.__SetHelper('Relay', value, qualifier, RelayCmdString)
        else:
            self.Discard('Invalid Command for SetRelay')

    def SetSocket(self, value, qualifier):

        NumberStates = {
            'A' : 128, 
            'B' : 64,  
            'C' : 32,  
            'D' : 16,  
            'E' : 8,  
            'F' : 4,  
            'G' : 2,  
            'H' : 1
        }

        ValueStateValues = {
            'On'  : 'ons', 
            'Off' : 'offs'
        }
        number= qualifier['Number']
        if number in NumberStates:
            SocketCmdString = '{0}.who?led={1}00000000'.format(ValueStateValues[value],bin(NumberStates[number])[2:].zfill(8))
            self.__SetHelper('Socket', value, qualifier, SocketCmdString)
        else:
            self.Discard('Invalid Command for SetSocket')

    def __CheckResponseForErrors(self, sourceCmdName, res):

        DEVICE_ERROR_CODES = {
            100: 'Continue',
            101: 'Switching Protocols',
            204: 'No Content',
            205: 'Reset Content',
            206: 'Partial Content',
            300: 'Multiple Choices',                 
            301: 'Moved Permanently',
            302: 'Found',
            303: 'See Other',
            304: 'Not Modified',                 
            305: 'Use Proxy',                 
            307: 'Temporary Redirect',
            400: 'Bad Request',                
            401: 'Unauthorized',               
            402: 'Payment Required',              
            403: 'Forbidden',                
            404: 'Not Found',
            405: 'Method Not Allowed',                 
            406: 'Not Acceptable',
            407: 'Proxy Authentication Required', 
            408: 'Request Timeout',
            409: 'Conflict', 
            410: 'Gone',                  
            411: 'Length Required', 
            412: 'Precondition Failed',
            413: 'Request Entity Too Large',
            414: 'Request-URI Too Long', 
            415: 'Unsupported Media Type',
            416: 'Requested Range Not Satisfiable',
            417: 'Expectation Failed',
            500: 'Internal Server Error',
            501: 'Not Implemented',                
            502: 'Bad Gateway',
            503: 'Service Unavailable',              
            504: 'Gateway Timeout',                 
            505: 'HTTP Version Not Supported'
        }
       
        if res:
            if res[0] == 200:
                res = res[1]
            else:
                if res[0] in DEVICE_ERROR_CODES:
                    errorString = '{0} {1} {2}'.format(sourceCmdName, res[0], DEVICE_ERROR_CODES[res[0]])
                    self.Error([errorString])
                    res = ''
                else:
                    self.Error(['Unknown Error'])
                    res = ''
        else:
            res = ''

        return res  

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        if self.authentication:
            headers = {
                'Authorization' : self.authentication
            }
        else:
            headers = {}

        url = '{}{}'.format(self.RootURL, url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, HTTPClass):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
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