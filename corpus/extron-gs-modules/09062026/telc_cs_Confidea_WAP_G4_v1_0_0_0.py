from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import re
import base64
import urllib.error
import urllib.request
from json import loads, dumps
from collections import defaultdict

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        if port == 9443:
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        else:
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._APIAccessKey = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveMicList': { 'Status': {}},
            'HeadphoneVolume': { 'Status': {}},
            'LoudspeakerVolume': { 'Status': {}},
            'MicrophoneControl': {'Parameters':['Number'], 'Status': {}},
            'MicrophoneRequestingToSpeak': {'Parameters':['Number'], 'Status': {}},
            'OpenMeetingStatus': {'Parameters':['Type'], 'Status': {}},
            'OpenMeetingStatusRefresh': { 'Status': {}},
            'PowerOffAllWirelessMics': { 'Status': {}},
            'RequesttoSpeakList': { 'Status': {}},
        }

    @property
    def APIAccessKey(self):
        return self._APIAccessKey

    @APIAccessKey.setter
    def APIAccessKey(self, value):
        self._APIAccessKey = value

    def UpdateActiveMicList(self, value, qualifier):

        url = 'api/discussion/speakers'
        res = self.__UpdateHelper('ActiveMicList', value, qualifier, url=url)
        if res:
            try:
                self.WriteStatus('ActiveMicList', res, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Active Mic List: Invalid/unexpected response'])
        else:
            self.WriteStatus('ActiveMicList', '[]', qualifier)

    def SetHeadphoneVolume(self, value, qualifier):

        ValueStateValues = {
            0:  -960,
            1:  -200,
            2:  -190,
            3:  -180,
            4:  -170,
            5:  -160,
            6:  -150,
            7:  -140,
            8:  -130,
            9:  -120,
            10: -110,
            11: -100,
            12: -90,
            13: -80,
            14: -70,
            15: -60,
            16: -50,
            17: -40,
            18: -30,
            19: -20,
            20: -10,
            21: 0,
            22: 10,
            23: 20,
            24: 30,
            25: 40,
            26: 50,
            27: 60,
            28: 70,
            29: 80,
            30: 90,
            31: 100,
            32: 110,
        }
            
        if value in ValueStateValues:
            url = 'api/audio/defaultchannelselectorvolume'
            data = dumps({"gain":ValueStateValues[value]}) 
            self.__SetHelper('HeadphoneVolume', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetHeadphoneVolume')

    def UpdateHeadphoneVolume(self, value, qualifier):

        url = 'api/audio/defaultchannelselectorvolume'
        res = self.__UpdateHelper('HeadphoneVolume', value, qualifier, url=url)
        if res:
            try:
                ValueStateValues = {
                    -1000:  0,
                    -960:   0,
                    -200:   1,
                    -190:   2,
                    -180:   3,
                    -170:   4,
                    -160:   5,
                    -150:   6,
                    -140:   7,
                    -130:   8,
                    -120:   9,
                    -110:   10,
                    -100:   11,
                    -90:    12,
                    -80:    13,
                    -70:    14,
                    -60:    15,
                    -50:    16,
                    -40:    17,
                    -30:    18,
                    -20:    19,
                    -10:    20,
                    0:      21,
                    10:     22,
                    20:     23,
                    30:     24,
                    40:     25,
                    50:     26,
                    60:     27,
                    70:     28,
                    80:     29,
                    90:     30,
                    100:    31,
                    110:    32,
                }
                value = ValueStateValues[res["gain"]]
                self.WriteStatus('HeadphoneVolume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Headphone Volume: Invalid/unexpected response'])

    def SetLoudspeakerVolume(self, value, qualifier):

        ValueStateValues = {
            0:  -960,
            1:  -240,
            2:  -220,
            3:  -200,
            4:  -180,
            5:  -160,
            6:  -140,
            7:  -120,
            8:  -100,
            9:  -80,
            10: -60,
            11: -40,
            12: -20,
            13: 0,
            14: 10,
            15: 20,
            16: 30,
            17: 40,
            18: 50,
            19: 60,
            20: 70,
            21: 80,
            22: 90,
            23: 100,
            24: 110,
            25: 120
        }
            
        if value in ValueStateValues:
            url = 'api/audio/loudspeakervolume'
            data = dumps({"gain":ValueStateValues[value]}) 
            self.__SetHelper('LoudspeakerVolume', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetLoudspeakerVolume')

    def UpdateLoudspeakerVolume(self, value, qualifier):

        url = 'api/audio/loudspeakervolume'
        res = self.__UpdateHelper('LoudspeakerVolume', value, qualifier, url=url)
        if res:
            try:
                ValueStateValues = {
                    -1000:  0,
                    -960:   0,
                    -240:   1,
                    -220:   2,
                    -200:   3,
                    -180:   4,
                    -160:   5,
                    -140:   6,
                    -120:   7,
                    -100:   8,
                    -80:    9,
                    -60:    10,
                    -40:    11,
                    -20:    12,
                    0:      13,
                    10:     14,
                    20:     15,
                    30:     16,
                    40:     17,
                    50:     18,
                    60:     19,
                    70:     20,
                    80:     21,
                    90:     22,
                    100:    23,
                    110:    24,
                    120:    25
                }

                value = ValueStateValues[res["gain"]]
                self.WriteStatus('LoudspeakerVolume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Loudspeaker Volume: Invalid/unexpected response'])

    def SetMicrophoneControl(self, value, qualifier):

        ValueStateValues = {
            'On':  True,
            'Off': False
        }

        if 1 <= qualifier['Number'] <= 2048 and value in ValueStateValues:
            speak_status = self.ReadStatus('MicrophoneRequestingToSpeak', {'Number': qualifier['Number']})
            if speak_status in ValueStateValues:
                url = 'api/discussion/seats/{}'.format(qualifier['Number'])
                data = dumps({
                              "microphoneOn": ValueStateValues[value],
                              "requestingToSpeak": ValueStateValues[speak_status]
                            }) 
                self.__SetHelper('MicrophoneControl', value, qualifier, url=url, data=data.encode('iso-8859-1'))
            else:
                self.Discard('Invalid Command for SetMicrophoneControl') 
        else:
            self.Discard('Invalid Command for SetMicrophoneControl')

    def UpdateMicrophoneControl(self, value, qualifier):

        if 1 <= qualifier['Number'] <= 2048:
            url = 'api/discussion/seats/{}'.format(qualifier['Number'])
            res = self.__UpdateHelper('MicrophoneControl', value, qualifier, url=url)
            if res:
                ValueStateValues = {
                    True:  'On',
                    False: 'Off'
                }

                try:
                    qualifier = {}
                    qualifier['Number'] = res["seatNumber"]
                    value = ValueStateValues[res["microphoneOn"]]
                    self.WriteStatus('MicrophoneControl', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Microphone Control: Invalid/unexpected response'])
                try:
                    qualifier = {}
                    qualifier['Number'] = res["seatNumber"]
                    value = ValueStateValues[res["requestingToSpeak"]]
                    self.WriteStatus('MicrophoneRequestingToSpeak', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Microphone Requesting To Speak: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMicrophoneControl')
            
    def UpdateMicrophoneRequestingToSpeak(self, value, qualifier):

        if 1 <= qualifier['Number'] <= 2048:
            self.UpdateMicrophoneControl(None, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneRequestingToSpeak')

    def SetOpenMeetingStatusRefresh(self, value, qualifier):

        url = 'api/meeting'
        res = self.__SetHelper('OpenMeetingStatusRefresh', value, qualifier, url=url)
        try:
            self.WriteStatus('OpenMeetingStatus', res["meetingId"], {'Type': 'Meeting ID'})
            self.WriteStatus('OpenMeetingStatus', res["title"], {'Type': 'Title'})
        except:
            self.Error(['Open Meeting Status: Invalid/unexpected response'])

    def SetPowerOffAllWirelessMics(self, value, qualifier):

        url = 'api/device/devices/actions'
        data = dumps({
            "action": "turnOff"
        }) 
        self.__SetHelper('PowerOffAllWirelessMics', value, qualifier, url=url, data=data.encode('iso-8859-1'))

    def UpdateRequesttoSpeakList(self, value, qualifier):

        url = 'api/discussion/requests'
        res = self.__UpdateHelper('RequesttoSpeakList', value, qualifier, url=url)
        if res:
            try:
                self.WriteStatus('RequesttoSpeakList', res, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.WriteStatus('RequesttoSpeakList', '[]', qualifier)
                self.Error(['Request to Speak List: Invalid/unexpected response'])
        else:
            self.WriteStatus('RequesttoSpeakList', '[]', qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = ''.join([self.RootURL, url])
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self._APIAccessKey)
        }

        if command == 'OpenMeetingStatusRefresh':
            method= 'GET' 
        elif command == 'PowerOffAllWirelessMics':
            method= 'POST'
        else:
            method= 'PUT'
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = urllib.request.urlopen(my_request, context=self._context, timeout=1)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202, 204):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = ''.join([self.RootURL, url])
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self._APIAccessKey)
        }

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = urllib.request.urlopen(my_request, context=self._context, timeout=1) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202, 204):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier    
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)  

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return  
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands.get(command, None)
        if Command:
            Status = Command['Status']
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Status = Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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