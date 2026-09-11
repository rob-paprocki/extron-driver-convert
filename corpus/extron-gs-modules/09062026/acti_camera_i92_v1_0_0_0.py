from json import loads, dumps
import urllib.error
import urllib.request
import base64

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'ExposureMode': {'Status': {}},
            'Flip': {'Status': {}},
            'Focus': {'Status': {}},
            'Home': {'Status': {}},
            'IrisMode': {'Status': {}},
            'Mirror': {'Status': {}},
            'MotionDetection': {'Status': {}},
            'PanandTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PowerLED': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'ShutterMode': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

    def SetBrightness(self, value, qualifier):

        if 1 <= value <= 100:
            BrightnessCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_BRIGHTNESS={2}'.format(self.deviceUsername, self.devicePassword, value)
            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetContrast(self, value, qualifier):

        if 1 <= value <= 100:
            ContrastCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_CONTRAST={2}'.format(self.deviceUsername, self.devicePassword, value)
            self.__SetHelper('Contrast', value, qualifier, url=ContrastCmdString)
        else:
            self.Discard('Invalid Command for SetContrast')

    def SetExposureMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Manual': 'MANUAL',
            'Iris Priority': 'IRIS_PRIORITY',
            'Shutter Priority': 'SHUTTER_PRIORITY'
        }

        ExposureModeCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_EXPOSURE_MODE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('ExposureMode', value, qualifier, url=ExposureModeCmdString)

    def SetFlip(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        FlipCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_FLIP_MODE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('Flip', value, qualifier, url=FlipCmdString)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 'FAR',
            'Near': 'NEAR',
            'Stop': 'STOP',
            'Auto': 'AUTO',
            'Manual': 'MANUAL',
            'Zoom_AF': 'ZOOM_AF',
            'Refocus': 'REFOCUS'
        }

        FocusCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&FOCUS={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('Focus', value, qualifier, url=FocusCmdString)

    def SetHome(self, value, qualifier):

        HomeCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&MOVE=HOME'.format(self.deviceUsername, self.devicePassword)
        self.__SetHelper('Home', value, qualifier, url=HomeCmdString)

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Manual': 'MANUAL'
        }

        IrisModeCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_IRIS_MODE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('IrisMode', value, qualifier, url=IrisModeCmdString)

    def SetMirror(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        MirrorCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_MIRROR_MODE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('Mirror', value, qualifier, url=MirrorCmdString)

    def SetMotionDetection(self, value, qualifier):

        ValueStateValues = {
            'On': '0x01',
            'Off': '0x00'
        }

        MotionDetectionCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&MOTION_ENABLED={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('MotionDetection', value, qualifier, url=MotionDetectionCmdString)

    def SetPanandTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'Up Left': 'UPLEFT',
            'Up Right': 'UPRIGHT',
            'Down Left': 'DOWNLEFT',
            'Down Right': 'DOWNRIGHT',
            'Stop': 'STOP'
        }

        panspeed = qualifier['Pan Speed']
        tiltspeed = qualifier['Tilt Speed']
        if 1 <= int(panspeed) <= 5 and 1 <= int(tiltspeed) <= 5:
            if value == 'Up' or value == 'Down':
                PanandTiltCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&MOVE={2},{3}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value], tiltspeed)
            elif value == 'Left' or value == 'Right':
                PanandTiltCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&MOVE={2},{3}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value], panspeed)
            elif value == 'Stop':
                PanandTiltCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&MOVE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
            else:
                PanandTiltCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&MOVE={2},{3},{4}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value], panspeed, tiltspeed)
            self.__SetHelper('PanandTilt', value, qualifier, url=PanandTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanandTilt')

    def SetPowerLED(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        PowerLEDCmdString = 'cgi-bin/system?USER={0}&PWD={1}&POWER_LED={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('PowerLED', value, qualifier, url=PowerLEDCmdString)

    def SetRecallPreset(self, value, qualifier):

        RecallPresetCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&PTZ_PRESET_GO={2}'.format(self.deviceUsername, self.devicePassword, value)
        self.__SetHelper('RecallPreset', value, qualifier, url=RecallPresetCmdString)

    def SetShutterMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Manual': 'MANUAL'
        }

        ShutterModeCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_SHUTTER_MODE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('ShutterMode', value, qualifier, url=ShutterModeCmdString)

    def SetWhiteBalanceMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Indoor 1': 'INDOOR1',
            'Indoor 2': 'INDOOR2',
            'Outdoor 1': 'OUTDOOR1',
            'Outdoor 2': 'OUTDOOR2',
            'Hold': 'HOLD',
            'Manual': 'MANUAL'
        }

        WhiteBalanceModeCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&VIDEO_WB_MODE={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
        self.__SetHelper('WhiteBalanceMode', value, qualifier, url=WhiteBalanceModeCmdString)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 'TELE',
            'Wide': 'WIDE',
            'Stop': 'STOP'
        }

        zmspeed = qualifier['Speed']
        if 2 <= int(zmspeed) <= 7:
            if value == 'Stop':
                ZoomCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&ZOOM={2}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value])
            else:
                ZoomCmdString = 'cgi-bin/encoder?USER={0}&PWD={1}&ZOOM={2},{3}'.format(self.deviceUsername, self.devicePassword, ValueStateValues[value], zmspeed)
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = loads(response.read().decode())
        return res

    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
        try:
            res = self.Opener.open(req)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
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
