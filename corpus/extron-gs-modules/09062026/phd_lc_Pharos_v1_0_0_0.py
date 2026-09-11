from extronlib.system import Wait, ProgramLog
import re
import base64
import urllib.error
import urllib.request
from json import loads, dumps

class DeviceClass:
    def __init__(self, ipAddress, port):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'MasterIntensity': {'Parameters':['Type'], 'Status': {}},
            'StartScene': { 'Status': {}},
        }

    def SetMasterIntensity(self, value, qualifier):

        TypeStates = {
            'Primary':   'primary',
            'Secondary': 'secondary',
            'Overlay 1': 'overlay_1',
            'Overlay 2': 'overlay_2'
            }
            
        ValueStateValues = {
            '0 %':   '0',
            '25 %':  '25',
            '50 %':  '50',
            '75 %':  '75',
            '100 %': '100'
            }

        if qualifier['Type'] in TypeStates and value in ValueStateValues:
            url = 'api/content_target'
            data = dumps({
                          "action": "master_intensity",
                          "level": "{}:100".format(ValueStateValues[value]),
                          "type": TypeStates[qualifier['Type']]
                        }) 
            self.__SetHelper('MasterIntensity', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetMasterIntensity')

    def SetStartScene(self, value, qualifier):

        if 1 <= value <= 99:
            url = 'api/scene'
            data = dumps({
                          "action": "start",
                          "num": value
                        })
            self.__SetHelper('StartScene', value, qualifier, url=url, data=data.encode('iso-8859-1'))

        else:
            self.Discard('Invalid Command for SetStartScene')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'application/json'}
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