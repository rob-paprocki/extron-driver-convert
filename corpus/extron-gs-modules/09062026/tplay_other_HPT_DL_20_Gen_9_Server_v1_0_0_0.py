import base64
import urllib.error
import urllib.request


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
        urllib.request.install_opener(self.Opener)

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'HTTPSEventRequest': {'Parameters': ['Event ID', 'Authentication Key', 'Activate/Deactivate Event'], 'Status': {}},
            }

    def SetHTTPSEventRequest(self, value, qualifier):

        EventID = qualifier['Event ID']
        AuthKey = qualifier['Authentication Key']

        States = {
            'Activate Event'    : '1', 
            'Deactivate Event'  : '0'
        }

        State = States[qualifier['Activate/Deactivate Event']]
        if 1 <= int(EventID) <= 99:
            url = '/triplecare/eventHttpRequest.php?id={}&key={}&status={}'.format(EventID,AuthKey,State)
            self.__SetHelper('HTTPSEventRequest', value, qualifier, url)
        else:
            self.Discard('Invalid Command for SetHTTPSEventRequest')
            
    def __CheckResponseForErrors(self, sourceCmdName, res):
        return res.read().decode()

    def __SetHelper(self, command, value, qualifier, url=''):
        self.Debug = True
        url = '{}{}'.format(self.RootURL.rstrip('/'), url)
        my_request = urllib.request.Request(url, method='POST')
        try:
            res = self.Opener.open(my_request)  # open() returns a http.client.HTTPResponse object if successful
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
