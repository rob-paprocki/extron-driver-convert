import base64
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AutoFocus': { 'Status': {}},
            'AutoPan': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = 'cgi-bin/camctrl?af=on'
        self.__SetHelper('AutoFocus', value, qualifier, AutoFocusCmdString)
    def SetAutoPan(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'cgi-bin/camctrl?atpan=on',
            'Off' : 'cgi-bin/camctrl?atpan=off'
        }

        AutoPanCmdString = ValueStateValues[value]
        self.__SetHelper('AutoPan', value, qualifier, AutoPanCmdString)
    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'      : 'cgi-bin/camctrl?bright=up',
            'Down'    : 'cgi-bin/camctrl?bright=down',
            'Default' : 'cgi-bin/camctrl?bright=1'
        }

        BrightnessCmdString = ValueStateValues[value]
        self.__SetHelper('Brightness', value, qualifier, BrightnessCmdString)
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near' : 'directctrl?focus=-{0}',
            'Far'  : 'directctrl?focus={0}',
            'Stop' : 'directctrl?focus=0'
        }

        speed = qualifier['Speed']
        if 1 <= int(speed) <= 4:
            FocusCmdString = ValueStateValues[value].format(speed)
            self.__SetHelper('Focus', value, qualifier, FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 'cgi-bin/directctrl?rpan=0&rtilt=-{0}',
            'Down'  : 'cgi-bin/directctrl?rpan=0&rtilt={0}',
            'Left'  : 'cgi-bin/directctrl?rpan=-{0}&rtilt=0',
            'Right' : 'cgi-bin/directctrl?rpan={0}&rtilt=0', 
            'Stop'  : 'cgi-bin/directctrl?pan=0&tilt=0'
        }

        panSpeed = qualifier['Pan Speed']
        tiltSpeed = qualifier['Tilt Speed']
        if 1 <= int(panSpeed) <= 256 and 1 <= int(tiltSpeed) <= 256:
            if value in ['Up', 'Down']: #For Tilt
                PanTiltCmdString = ValueStateValues[value].format(tiltSpeed)
            elif value in ['Left', 'Right']: #For Pan
                PanTiltCmdString = ValueStateValues[value].format(panSpeed)
            else: #For Stop
                PanTiltCmdString = ValueStateValues[value]
            self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')
    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Set'    : 'camposiset?presetset={0}',
            'Delete' : 'camposiset?presetdel={0}'
        }

        action = qualifier['Action']
        if 1 <= value <= 256 and action in ActionStates:
            PresetCmdString = ActionStates[action].format(value)
            self.__SetHelper('Preset', value, qualifier, PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 'cgi-bin/directctrl?zoom={0}',
            'Wide' : 'cgi-bin/directctrl?zoom=-{0}',
            'Stop' : 'cgi-bin/directctrl?zoom=0'
        }

        speed = qualifier['Speed']
        if 1 <= int(speed) <= 4:
            ZoomCmdString = ValueStateValues[value].format(speed)
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, value, qualifier, url, queryDelay=0):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {}
        myRequest = urllib.request.Request(url, data=None, headers=headers)

        try:
            res = self.Opener.open(myRequest, timeout = 10)  # open() returns a http.client.HTTPResponse object if successful
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