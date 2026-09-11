from extronlib.system import ProgramLog, Wait
import re
import base64
import urllib.error
import urllib.request
import binascii

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            cred = '{}:{}'.format(self.deviceUsername, self.devicePassword)
            self.authentication = binascii.b2a_base64(cred.encode()).decode().strip()
        else:
            print('Missing Authentication.')
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Models = {}

        self.Commands = {
            'AudioVolume': {'Status': {}},
            'StreamAudio': {'Status': {}},
            'StreamHost': {'Parameters': ['Address'], 'Status': {}},
            'StreamHostConnect': {'Parameters': ['Address', 'Videowall Enable'], 'Status': {}},
            'StreamVideo': {'Status': {}},
            'StreamVideoPriority': {'Status': {}},
        }

    def SetAudioVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&AUDIO.VOLUME={}&CMD=END'.format(value)
            self.__SetHelper('AudioVolume', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def SetStreamAudio(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 'HDMI',
            'DANTE': 'DANTE',
            'Analog': 'ANALOG',
            'Stream': 'STREAM',
        }

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.AUDIO={}&CMD=END'.format(ValueStateValues[value])
            self.__SetHelper('StreamAudio', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamAudio')

    def SetStreamHost(self, value, qualifier):

        ip_address = qualifier['Address']
        if ip_address:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.HOST={}&CMD=END'.format(ip_address)
            self.__SetHelper('StreamHost', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamHost')

    def SetStreamHostConnect(self, value, qualifier):

        VideowallEnableStates = ('True', 'False')

        vw_enable = qualifier['Videowall Enable']
        ip_address = qualifier['Address']
        if vw_enable in VideowallEnableStates and ip_address:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.HOST={}&VW.ACTIVE={}&STREAM.CONNECT=TRUE&CMD=END'.format(ip_address, vw_enable.upper())
            self.__SetHelper('StreamHostConnect', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamHostConnect')

    def SetStreamVideo(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'HDMI 1': 'HDMI1',
            'HDMI 2': 'HDMI2',
            'USB C': 'USB-C',
        }

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.VIDEO={}&CMD=END'.format(ValueStateValues[value])
            self.__SetHelper('StreamVideo', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamVideo')

    def SetStreamVideoPriority(self, value, qualifier):

        ValueStateValues = {
            'HDMI1 HDMI2 USB-C': '1',
            'HDMI1 USB-C HDMI2': '2',
            'HDMI2 HDMI1 USB-C': '3',
            'HDMI2 USB-C HDMI1': '4',
            'USB-C HDMI1 HDMI2': '5',
            'USB-C HDMI2 HDMI1': '6',
        }

        if value in ValueStateValues:
            url = 'cgi-bin/wapi.cgi?CMD=START&UNIT.ID=ALL&STREAM.VIDEO_PRIORITY={}&CMD=END'.format(ValueStateValues[value])
            self.__SetHelper('StreamVideoPriority', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetStreamVideoPriority')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode('iso-8859-1')

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  # self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Authorization': 'Basic {}'.format(self.authentication),
                   'Content-Type': 'application/x-www-form-urlencoded'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = urllib.request.urlopen(my_request, timeout=5)
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