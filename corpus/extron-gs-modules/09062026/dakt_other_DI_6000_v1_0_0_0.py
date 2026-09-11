import base64
import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Brightness': { 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            BrightnessCmdString = 'daktronics/syscontrol/2.0/dimming/managers/0/dynamic'
            data = json.dumps(round(value / 100, 2)).encode()

            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   False,
            'Off':  True
        }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = 'daktronics/syscontrol/2.0/active'
            data = json.dumps(ValueStateValues[value]).encode()

            self.__SetHelper('GlobalVideoMute', value, qualifier, url=GlobalVideoMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }
        output = qualifier['Output']

        if 0 <= output and value in ValueStateValues:
            VideoMuteCmdString = 'daktronics/syscontrol/2.0/outputs/{}/blank'.format(output)
            data = json.dumps(ValueStateValues[value]).encode()

            self.__SetHelper('VideoMute', value, qualifier, url=VideoMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Content-Type': 'application/json'
        }

        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=10)
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