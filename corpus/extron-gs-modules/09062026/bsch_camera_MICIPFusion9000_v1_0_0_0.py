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
            'DigitalZoom': { 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Stop': { 'Status': {}},
            'Tour': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            1  : '4001',
            2  : '6000',
            3  : '6A80',
            4  : '7000',
            5  : '7300',
            6  : '7540',
            7  : '76C0',
            8  : '7800',
            9  : '78C0',
            10 : '7980',
            11 : '7A00',
            12 : '7AC0'
        }

        if 1 <= value <= 12:
            DigitalZoomCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x810006012003' + ValueStateValues[value]
            self.__SetHelper('DigitalZoom', value, qualifier, DigitalZoomCmdString)
        else:
            self.Discard('Invalid Command for SetDigitalZoom')

    def SetPanTilt(self, value, qualifier):

        if 1 <= int(qualifier['Speed']) <= 15:
            speedValue = '{:X}'.format(int(qualifier['Speed']))

            ValueStateValues = {
                'Up'    : '008{}00'.format(speedValue),
                'Down'  : '000{}00'.format(speedValue),
                'Left'  : '0{}0000'.format(speedValue),
                'Right' : '8{}0000'.format(speedValue)
            }

            PanTiltCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x800006011085' + ValueStateValues[value]
            self.__SetHelper('PanTilt', value, qualifier, PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 99:
            PresetRecallCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x80000201B0800705' + '{:02X}'.format(int(value))
            self.__SetHelper('PresetRecall', value, qualifier, PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 99:
            PresetSaveCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x80000201B0800704' + '{:02X}'.format(int(value))
            self.__SetHelper('PresetSave', value, qualifier, PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetStop(self, value, qualifier):

        StopCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x800006011085000000'
        self.__SetHelper('Stop', value, qualifier, StopCmdString)

    def SetTour(self, value, qualifier):

        ValueStateValues = {
            'Record'            : '00002',
            'Stop Recording'    : '30000',
            'Replay Loop'       : '10001',
            'Replay Once'       : '20001',
            'Stop Replay'       : '30000'
        }

        TourCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x80000601608' + ValueStateValues[value]
        self.__SetHelper('Tour', value, qualifier, TourCmdString)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : '8',
            'Wide' : '0'
        }

        if 1 <= int(qualifier['Speed']) <= 7:
            ZoomCmdString = 'rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x8000060110850000' + ValueStateValues[value] + qualifier['Speed']
            self.__SetHelper('Zoom', value, qualifier, ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, value, qualifier, url='', data=None):        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

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