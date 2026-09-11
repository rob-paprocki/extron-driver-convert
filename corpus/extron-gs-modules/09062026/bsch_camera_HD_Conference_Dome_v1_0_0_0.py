import urllib.error
import urllib.request
import base64

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
 
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
 
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Pan': {'Parameters': ['Speed'], 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'StopControl': {'Status': {}},
            'Tilt': {'Parameters': ['Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
        }

        self.header = '/rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload='

    def SetPan(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 15
        }

        ValueStateValues = {
            'Left': '0',
            'Right': '8'
        }

        speed = qualifier['Speed']
        if SpeedConstraints['Min'] <= speed <= SpeedConstraints['Max']:
            PanCmdString = '{}0x800006011085{}{}0000&res=1\r\n\r\n'.format(self.header, ValueStateValues[value], hex(speed)[2].upper())
            self.__SetHelper('Pan', value, qualifier, url=PanCmdString)
        else:
            print('Invalid Command for SetPan')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': '4',
            'Recall': '5'
        }

        action = qualifier['Action']
        if action in ActionStates and 1 <= int(value) <= 99:
            value = int(value)
            PresetCmdString = '{}0x80000201B080070{}{}&res=1\r\n\r\n'.format(self.header, ActionStates[action], hex(value)[2:].upper().zfill(2))
            self.__SetHelper('Preset', value, qualifier, url=PresetCmdString)
        else:
            print('Invalid Command for SetPreset')

    def SetStopControl(self, value, qualifier):

        StopControlCmdString = '{}0x800006011085000000&res=1\r\n\r\n'.format(self.header)
        self.__SetHelper('StopControl', value, qualifier, url=StopControlCmdString)

    def SetTilt(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 15
        }

        ValueStateValues = {
            'Up': '8',
            'Down': '0'
        }

        speed = qualifier['Speed']
        if SpeedConstraints['Min'] <= speed <= SpeedConstraints['Max']:
            TiltCmdString = '{}0x80000601108500{}{}00&res=1\r\n\r\n'.format(self.header, ValueStateValues[value], hex(speed)[2].upper())
            self.__SetHelper('Tilt', value, qualifier, url=TiltCmdString)
        else:
            print('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 1,
            'Max': 7
        }

        ValueStateValues = {
            'In': '8',
            'Out': '0'
        }

        speed = qualifier['Speed']
        if SpeedConstraints['Min'] <= speed <= SpeedConstraints['Max']:
            ZoomCmdString = '{}0x8000060110850000{}{}&res=1\r\n\r\n'.format(self.header, ValueStateValues[value], hex(speed)[2].upper())
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/xml'}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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
