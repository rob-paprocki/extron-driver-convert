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
        self.Models = {}

        self.Commands = {
            'ActuatorSwitching': {'Parameters': ['Actuator ID'], 'Status': {}},
        }


    def SetActuatorSwitching(self, value, qualifier):
        print('IM here')
        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        actorID = qualifier['Actuator ID']
        if 1 <= int(actorID) <= 6:
            ActuatorSwitchingCmdString = 'id={0}&action={1}'.format(actorID, ValueStateValues[value])
            self.__SetHelper('ActuatorSwitching', value, qualifier, ActuatorSwitchingCmdString)
        else:
            self.Discard('Invalid Command for SetActuatorSwitching')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/xml?mode=actor&type=switch&{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/xml'}

        my_request = urllib.request.Request(url, data=None, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request)
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
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
