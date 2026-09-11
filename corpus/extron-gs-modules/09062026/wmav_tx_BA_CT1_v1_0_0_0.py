# Copyright 2026, Extron. All rights reserved.

from extronlib.system import ProgramLog, Wait, GetUnverifiedContext
import json
import base64
import urllib.error
import urllib.request
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
        
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._APIKey = ''
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioSource': {'Parameters': ['Channel'], 'Status': {}},
            'DigitalGain': {'Parameters': ['Channel'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'TransmitterEnable': {'Parameters': ['MAC Address', 'Channel'], 'Status': {}},
            'TransmitterName': {'Parameters': ['MAC Address', 'Channel'], 'Status': {}},
            'TransmitterStatus': {'Parameters': ['MAC Address', 'Channel'], 'Status': {}}
        }

        self.audioSourceStatus = {}

        self.digitalGainStatus = {}

        self.executiveModeStatus = {}

        self.transmitterEnableStatus = {}

    @property
    def APIKey(self):
        return self._APIKey

    @APIKey.setter
    def APIKey(self, value):
        if value:
            self._APIKey = value
        else:
            self.Error(['Missing API Key Parameter.'])

    def SetAudioSource(self, value, qualifier):

        channel = int(qualifier['Channel'])

        ValueStateValues = {
            'Disabled':                 'Disabled',
            'Terminal Block':           'Terminal Block',
            'XLR / 1/4" (Combo Jack)':  'XLR / 1/4" (Combo Jack)',
            'Dante':                    'Dante',
            'Test Tone':                'Test Tone'
        }

        if 1 <= channel <= 2 and channel in self.audioSourceStatus and value in ValueStateValues:
            AudioSourceCmdString = 'api/controller/channel{}/audio-source'.format(channel)

            self.audioSourceStatus[channel]['audio_source'] = ValueStateValues[value]
            data = self.audioSourceStatus[channel]

            self.__SetHelper('AudioSource', value, qualifier, url=AudioSourceCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAudioSource')

    def UpdateAudioSource(self, value, qualifier):

        ValueStateValues = {
            'Disabled':                 'Disabled',
            'Terminal Block':           'Terminal Block',
            'XLR / 1/4" (Combo Jack)':  'XLR / 1/4" (Combo Jack)',
            'Dante':                    'Dante',
            'Test Tone':                'Test Tone'
        }
        
        channel = int(qualifier['Channel'])

        if 1 <= channel <= 2:

            AudioSourceCmdString = 'api/controller/channel{}/audio-source'.format(channel)
            res = self.__UpdateHelper('AudioSource', value, qualifier, url=AudioSourceCmdString)
            if res:
                try:
                    value = ValueStateValues[res['audio_source']]
                    self.WriteStatus('AudioSource', value, qualifier)

                    self.audioSourceStatus[channel] = res
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Audio Source: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioSource')

    def SetDigitalGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 2 and channel in self.digitalGainStatus and -60 <= value <= 24:
            DigitalGainCmdString = 'api/controller/channel{}/audio-settings'.format(channel)

            self.digitalGainStatus[channel]['digital_gain'] = int(value)
            data = self.digitalGainStatus[channel]

            self.__SetHelper('DigitalGain', value, qualifier, url=DigitalGainCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetDigitalGain')

    def UpdateDigitalGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        if 1 <= channel <= 2:
            DigitalGainCmdString = 'api/controller/channel{}/audio-settings'.format(channel)
            res = self.__UpdateHelper('DigitalGain', value, qualifier, url=DigitalGainCmdString)
            if res:
                try:
                    value = int(res['digital_gain'])
                    if -60 <= value <= 24:
                        self.WriteStatus('DigitalGain', value, qualifier)

                        if 'channel_enable' in res:
                            del res['channel_enable']

                        self.digitalGainStatus[channel] = res
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Digital Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDigitalGain')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if self.executiveModeStatus and value in ValueStateValues:
            ExecutiveModeCmdString = 'api/controller/front-panel'

            self.executiveModeStatus['lock_status'] = ValueStateValues[value]

            self.__SetHelper('ExecutiveMode', value, qualifier, url=ExecutiveModeCmdString, data=self.executiveModeStatus)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }
        
        ExecutiveModeCmdString = 'api/controller/front-panel'
        res = self.__UpdateHelper('ExecutiveMode', value, qualifier, url=ExecutiveModeCmdString)
        if res:
            try:
                value = ValueStateValues[res['lock_status']]
                self.WriteStatus('ExecutiveMode', value, qualifier)

                self.executiveModeStatus = res
            except (KeyError, IndexError, AttributeError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetTransmitterEnable(self, value, qualifier):

        mac = qualifier['MAC Address']
        channel = int(qualifier['Channel'])

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if mac and 1 <= channel <= 2 and self.transmitterEnableStatus and value in ValueStateValues:
            TransmitterEnableCmdString = 'api/transmitter/{}/audio'.format(mac)
            self.transmitterEnableStatus['channel{}_enable'.format(channel)] = ValueStateValues[value]

            self.__SetHelper('TransmitterEnable', value, qualifier, url=TransmitterEnableCmdString, data=self.transmitterEnableStatus)
        else:
            self.Discard('Invalid Command for SetTransmitterEnable')

    def UpdateTransmitterEnable(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }
        
        mac = qualifier['MAC Address']
        channel = int(qualifier['Channel'])

        if mac and 1 <= channel <= 2:
            TransmitterEnableCmdString = 'api/transmitter/{}/audio'.format(mac)
            res = self.__UpdateHelper('TransmitterEnable', value, qualifier, url=TransmitterEnableCmdString)

            if res:
                try:
                    value = ValueStateValues[res['channel1_enable']]
                    self.WriteStatus('TransmitterEnable', value, {'MAC Address': mac, 'Channel': '1'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Enable (1): Invalid/unexpected response'])
                try:
                    value = ValueStateValues[res['channel2_enable']]
                    self.WriteStatus('TransmitterEnable', value, {'MAC Address': mac, 'Channel': '2'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Enable (2): Invalid/unexpected response'])
                try:
                    value = res['channel1_name']
                    self.WriteStatus('TransmitterName', value, {'MAC Address': mac, 'Channel': '1'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Name (1): Invalid/unexpected response'])
                try:
                    value = res['channel2_name']
                    self.WriteStatus('TransmitterName', value, {'MAC Address': mac, 'Channel': '2'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Name (2): Invalid/unexpected response'])
                
                self.transmitterEnableStatus = res
        else:
            self.Discard('Invalid Command for UpdateTransmitterEnable')

    def UpdateTransmitterName(self, value, qualifier):

        self.UpdateTransmitterEnable(value, qualifier)

    def UpdateTransmitterStatus(self, value, qualifier):

        ValueStateValues = {
            True:   'Streaming',
            False:  'Paused'
        }

        mac = qualifier['MAC Address']
        channel = int(qualifier['Channel'])

        if mac and 1 <= channel <= 2:
            TransmitterStatusCmdString = 'api/transmitter/{}/status'.format(mac)
            res = self.__UpdateHelper('TransmitterStatus', value, qualifier, url=TransmitterStatusCmdString)
            if res:
                try:
                    value = ValueStateValues[res['channel1_stream_state']]
                    self.WriteStatus('TransmitterStatus', value, {'MAC Address': mac, 'Channel': '1'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Status (1): Invalid/unexpected response'])
                try:
                    value = ValueStateValues[res['channel2_stream_state']]
                    self.WriteStatus('TransmitterStatus', value, {'MAC Address': mac, 'Channel': '2'})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Status (2): Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTransmitterStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except json.decoder.JSONDecodeError:
            self.Error(['{}: Invalid/unexpected response (JSON)'.format(sourceCmdName)])

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization': self.APIKey
        }

        if data:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=1)
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization': self.APIKey
        }
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1)
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

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.audioSourceStatus = {}

        self.digitalGainStatus = {}

        self.executiveModeStatus = {}

        self.transmitterEnableStatus = {}

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