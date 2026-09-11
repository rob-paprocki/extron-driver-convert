import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AudioMute': { 'Status': {}},
            'ChannelCommand': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'DisplayPower': {'Parameters':['Type'], 'Status': {}},
            'Reboot': { 'Status': {}},
            'StaticImage': { 'Status': {}},
            'VolumeStep': { 'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'mute',
            'Off' : 'unmute'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', value, qualifier, url=AudioMuteCmdString)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetChannelCommand(self, value, qualifier):

        channel = value
        if channel:
            ChannelCommandCmdString = 'channel={}'.format(channel)
            self.__SetHelper('ChannelCommand', value, qualifier, url=ChannelCommandCmdString)
        else:
            self.Discard('Invalid Command for SetChannelCommand')

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 'channelup',
            'Down'  : 'channeldown'
        }

        if value in ValueStateValues:
            ChannelStepCmdString = ValueStateValues[value]
            self.__SetHelper('ChannelStep', value, qualifier, url=ChannelStepCmdString)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetDisplayPower(self, value, qualifier):

        TypeStates = {
            'Samsung'  : 'samsung',
            'HDMI CEC' : ''
        }

        ValueStateValues = {
            'On'  : 'poweron',
            'Off' : 'poweroff'
        }

        if qualifier['Type'] in TypeStates and value in ValueStateValues:
            DisplayPowerCmdString = '{}{}'.format(ValueStateValues[value], TypeStates[qualifier['Type']])
            self.__SetHelper('DisplayPower', value, qualifier, url=DisplayPowerCmdString)
        else:
            self.Discard('Invalid Command for SetDisplayPower')

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'reboot'
        self.__SetHelper('Reboot', value, qualifier, url=RebootCmdString)

    def SetStaticImage(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'imageon',
            'Off' : 'imageoff'
        }

        if value in ValueStateValues:
            StaticImageCmdString = ValueStateValues[value]
            self.__SetHelper('StaticImage', value, qualifier, url=StaticImageCmdString)
        else:
            self.Discard('Invalid Command for SetStaticImage')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 'volumeup',
            'Down'  : 'volumedown'
        }

        if value in ValueStateValues:
            VolumeStepCmdString = ValueStateValues[value]
            self.__SetHelper('VolumeStep', value, qualifier, url=VolumeStepCmdString)
        else:
            self.Discard('Invalid Command for SetVolumeStep')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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