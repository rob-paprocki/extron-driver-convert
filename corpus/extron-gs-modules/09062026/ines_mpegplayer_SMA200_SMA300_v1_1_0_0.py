import base64
import urllib.error
import urllib.request


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername and devicePassword:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'PlayerControl': {'Parameters': ['Variable State 1', 'Variable State 2', 'Variable State 3', 'Variable State 4', 'Variable State 5',
                                             'Variable Name 1', 'Variable Name 2', 'Variable Name 3', 'Variable Name 4', 'Variable Name 5'], 'Status': {}},
        }

    def SetPlayerControl(self, value, qualifier):

        States = {'True', 'False'}
        State1 = qualifier['Variable State 1']
        State2 = qualifier['Variable State 2']
        State3 = qualifier['Variable State 3']
        State4 = qualifier['Variable State 4']
        State5 = qualifier['Variable State 5']
        Name1 = qualifier['Variable Name 1']
        Name2 = qualifier['Variable Name 2']
        Name3 = qualifier['Variable Name 3']
        Name4 = qualifier['Variable Name 4']
        Name5 = qualifier['Variable Name 5']
        if (Name1 and Name2 and Name3 and Name4 and Name5 and
                State1 in States and State2 in States and State3 in States and State4 in States and State5 in States):
            URL = '.playout/variables.xml'
            XMLData = ('<?xml version="1.0" encoding="UTF-8"?>'
                       '<variables xmlns="ns.innes.xpf.3" xmlns:xpf="ns.innes.xpf.3">'
                       '<variable name="{}" type="xsd:boolean">{}</variable>'
                       '<variable name="{}" type="xsd:boolean">{}</variable>'
                       '<variable name="{}" type="xsd:boolean">{}</variable>'
                       '<variable name="{}" type="xsd:boolean">{}</variable>'
                       '<variable name="{}" type="xsd:boolean">{}</variable>'
                       '</variables>').format(Name1, State1.lower(), Name2, State2.lower(), Name3, State3.lower(),
                                              Name4, State4.lower(), Name5, State5.lower()).encode(encoding='iso-8859-1')
            self.__SetHelper('PlayerControl', value, qualifier, URL, XMLData)
        else:
            print('Invalid Command for SetPlayerControl')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        headers = {'Content-Type': 'text/html'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(self.RootURL + url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = b''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
                res = b''
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
