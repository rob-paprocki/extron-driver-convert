from extronlib.system import Wait, ProgramLog
import json
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ActivatePreset': {'Parameters': ['Target'], 'Status': {}},
            'ChangeContent': {'Parameters': ['Target', 'Layer', 'Preview Visible', 'Program Visible', 'Input'], 'Status': {}},
            'SavePreset': {'Parameters': ['Command'], 'Status': {}},
        }

    def SetActivatePreset(self, value, qualifier):

        TargetStates = {
            'Preview': 0,
            'Program': 1,
        }

        target = qualifier['Target']
        preset_name = value
        if target in TargetStates and preset_name:
            data = json.dumps({
                "params":
                    {
                        "type": TargetStates[target],
                        "presetName": "{}".format(preset_name)
                    },
                "method": "activatePreset",
                "id": "1234",
                "jsonrpc": "2.0"
            }).encode(encoding='iso-8859-1')
            self.__SetHelper('ActivatePreset', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetActivatePreset')

    def SetChangeContent(self, value, qualifier):

        TargetStates = {
            'PGM 1': 0,
            'PGM 2': 1,
        }

        LayerStates = {
            'Layout A': 0,
            'Layout B': 1,
        }

        PreviewVisibleStates = {
            'True':  1,
            'False': 0,
        }

        ProgramVisibleStates = {
            'True':  1,
            'False': 0,
        }

        InputStates = {
            'HDMI 1': 0,
            'HDMI 2': 1,
            'HDMI 3': 2,
            'HDMI 4': 3,
            'HDMI 5': 4,
            'HDMI 6': 5,
        }

        target = qualifier['Target']
        layer = qualifier['Layer']
        preview = qualifier['Preview Visible']
        program = qualifier['Program Visible']
        _input = qualifier['Input']
        if (target in TargetStates and layer in LayerStates and preview in PreviewVisibleStates and
                program in ProgramVisibleStates and _input in InputStates):
            data = json.dumps({
                "params": {
                    "id": TargetStates[target],
                    "Layers": [
                        {
                            "id": LayerStates[layer],
                            "LastSrcIdx": InputStates[_input],
                            "PvwMode": PreviewVisibleStates[preview],
                            "PgmMode": ProgramVisibleStates[program],
                            "Freeze": 0
                        }
                    ]
                },
                "method": "changeContent",
                "id": "1234",
                "jsonrpc": "2.0"
            }).encode(encoding='iso-8859-1')
            self.__SetHelper('ChangeContent', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetChangeContent')

    def SetSavePreset(self, value, qualifier):

        preset_name = value
        if preset_name:
            data = json.dumps({
                "params": {
                    "presetName": "{}".format(preset_name)
                },
                "method": "savePreset",
                "id": "1234",
                "jsonrpc": "2.0"
            }).encode(encoding='iso-8859-1')
            self.__SetHelper('SavePreset', value, qualifier, url='', data=data)
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = json.loads(response.read().decode())
        if not res["result"]["success"] == 0:
            self.Error(['An Error occurred.'])
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  # self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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