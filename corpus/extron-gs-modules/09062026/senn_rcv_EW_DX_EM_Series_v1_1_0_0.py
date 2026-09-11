from extronlib.system import Wait, ProgramLog
from extronlib.system import GetUnverifiedContext
from collections import defaultdict
import base64
import json
import base64
import urllib.error
import urllib.request
import time

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='Off'):
        
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), 
                                                  urllib.request.HTTPSHandler(context=self._context))
        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = 'api'
        self.devicePassword = devicePassword
        self.Models = {
            'EW-DX EM 2': self.senn_27_5956_2,
            'EW-DX EM 2 Dante': self.senn_27_5956_2,
            'EW-DX EM 4 Dante': self.senn_27_5956_4,
        }

        self.base64Auth = 'Basic ' + base64.b64encode(b'api:' + self.devicePassword.encode()).decode()


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioLevel': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryLifetime': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryType': {'Parameters': ['Channel'], 'Status': {}},
            'BatteryVoltageLevel': {'Parameters': ['Channel'], 'Status': {}},
            'CarrierFrequency': {'Parameters': ['Channel'], 'Status': {}},
            'DeviceLocation': { 'Status': {}},
            'DeviceName': { 'Status': {}},
            'DeviceProduct': { 'Status': {}},
            'DeviceSerialNumber': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Identify': {'Parameters': ['Channel'], 'Status': {}},
            'LowCut': {'Parameters': ['Channel'], 'Status': {}},
            'Mute': {'Parameters': ['Channel'], 'Status': {}},
            'RFQuality': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterCapsule': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterMute': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterMuteMode': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterName': {'Parameters': ['Channel'], 'Status': {}},
            'TransmitterType': {'Parameters': ['Channel'], 'Status': {}}
        }

    def UpdateAudioLevel(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            AudioLevelCmdString = 'api/channel/{}/level'.format(ch - 1)
            res = self.__UpdateHelper('AudioLevel', value, qualifier, url=AudioLevelCmdString)
            if res not in [None, '']:
                try:
                    value = res['value']
                    if -138.5 <= value <= 0:
                        self.WriteStatus('AudioLevel', value, qualifier)
                except (ValueError, IndexError, AttributeError, KeyError):
                    self.Error(['Audio Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioLevel')

    def UpdateBatteryLifetime(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            BatteryLifetimeCmdString = 'api/transmitters/{}/battery'.format(ch - 1)
            res = self.__UpdateHelper('BatteryLifetime', value, qualifier, url=BatteryLifetimeCmdString)
            if res not in [None, '']:
                try:
                    value = res.get('lifetime', 'Not Found')

                    if value != 'Not Found':
                        value = time.strftime("%H:%M:%S", time.gmtime(int(value) * 60))

                    self.WriteStatus('BatteryLifetime', value, {'Channel': str(ch)})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Battery Lifetime: Invalid/unexpected response'])
                try:
                    ValueStateValues = {
                        'Battery':      'Battery',
                        'PrimaryCell':  'Primary Cell',
                        'NoBattery':    'No Battery'
                    }

                    value = ValueStateValues.get(res.get('type'), 'Not Found')
                    self.WriteStatus('BatteryType', value, {'Channel': str(ch)})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Battery Type: Invalid/unexpected response'])
                try:
                    value = res.get('gauge', 0)
                    if 0 <= value <= 100:
                        self.WriteStatus('BatteryVoltageLevel', value, {'Channel': str(ch)})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Battery Voltage Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBatteryLifetime')

    def UpdateBatteryType(self, value, qualifier):

        self.UpdateBatteryLifetime(value, qualifier)

    def UpdateBatteryVoltageLevel(self, value, qualifier):

        self.UpdateBatteryLifetime(value, qualifier)

    def SetCarrierFrequency(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size and 470.2 <= value <= 550.0:
            CarrierFrequencyCmdString = 'api/rf/channels/{}/frequency'.format(ch - 1)
            data = {
                'frequency': int(value * 1000)
            }

            self.__SetHelper('CarrierFrequency', value, qualifier, url=CarrierFrequencyCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetCarrierFrequency')

    def UpdateCarrierFrequency(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            CarrierFrequencyCmdString = 'api/rf/channels/{}'.format(ch - 1)
            res = self.__UpdateHelper('CarrierFrequency', value, qualifier, url=CarrierFrequencyCmdString)
            if res not in [None, '']:
                try:
                    value = res['frequency'] / 1000
                    if 470.2 <= value <= 550.0:
                        self.WriteStatus('CarrierFrequency', value, qualifier)
                except (ValueError, IndexError, AttributeError, KeyError):
                    self.Error(['Carrier Frequency: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCarrierFrequency')

    def UpdateDeviceLocation(self, value, qualifier):

        DeviceLocationCmdString = 'api/device/site'
        res = self.__UpdateHelper('DeviceLocation', value, qualifier, url=DeviceLocationCmdString)
        if res not in [None, '']:
            try:
                value = res['location']
                self.WriteStatus('DeviceLocation', value, None)
            except (ValueError, IndexError, AttributeError, KeyError):
                self.Error(['Device Location: Invalid/unexpected response'])
            try:
                value = res['deviceName']
                self.WriteStatus('DeviceName', value, None)
            except (ValueError, IndexError, AttributeError, KeyError):
                self.Error(['Device Name: Invalid/unexpected response'])

    def UpdateDeviceName(self, value, qualifier):

        self.UpdateDeviceLocation(value, qualifier)

    def UpdateDeviceProduct(self, value, qualifier):

        DeviceProductCmdString = 'api/device/identity'
        res = self.__UpdateHelper('DeviceProduct', value, qualifier, url=DeviceProductCmdString)
        if res not in [None, '']:
            try:
                value = res['product']
                self.WriteStatus('DeviceProduct', value, None)
            except (ValueError, IndexError, AttributeError, KeyError):
                self.Error(['Device Product: Invalid/unexpected response'])
            try:
                value = res['serial']
                self.WriteStatus('DeviceSerialNumber', value, None)
            except (ValueError, IndexError, AttributeError, KeyError):
                self.Error(['Device Serial Number: Invalid/unexpected response'])

    def UpdateDeviceSerialNumber(self, value, qualifier):

        self.UpdateDeviceProduct(value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'api/firmware/update/state'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res not in [None, '']:
            try:
                value = res['deviceVersion']
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, IndexError, AttributeError, KeyError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetIdentify(self, value, qualifier):

        ch = int(qualifier['Channel'])

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if 1 <= ch <= self.size and value in ValueStateValues:
            IdentifyCmdString = 'api/channel/{}/identify'.format(ch - 1)
            data = {
                'enabled': ValueStateValues[value]
            }

            self.__SetHelper('Identify', value, qualifier, url=IdentifyCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetIdentify')

    def UpdateIdentify(self, value, qualifier):

        ValueStateValues = {
            True:   'On',
            False:  'Off'
        }
        
        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            IdentifyCmdString = 'api/channel/{}/identify'.format(ch - 1)
            res = self.__UpdateHelper('Identify', value, qualifier, url=IdentifyCmdString)
            if res not in [None, '']:
                try:
                    value = ValueStateValues[res['enabled']]
                    self.WriteStatus('Identify', value, qualifier)
                except (KeyError, IndexError, AttributeError, KeyError):
                    self.Error(['Identify: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateIdentify')

    def UpdateLowCut(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            LowCutCmdString = 'api/syncSettings/{}'.format(ch - 1)
            res = self.__UpdateHelper('LowCut', value, qualifier, url=LowCutCmdString)
            if res not in [None, '']:
                try:
                    ValueStateValues = {
                        'Off': 'Off',
                        '30Hz': '30 Hz',
                        '60Hz': '60 Hz',
                        '80Hz': '80 Hz',
                        '100Hz': '100 Hz',
                        '120Hz': '120 Hz'
                    }

                    value = ValueStateValues[res['lowcut']]
                    self.WriteStatus('LowCut', value, {'Channel': str(ch)})
                except (KeyError, IndexError, AttributeError, KeyError):
                    self.Error(['Low Cut: Invalid/unexpected response'])
                try:
                    ValueStateValues = {
                        'Off':      'Off',
                        'RfMute':   'RF Mute',
                        'AfMute':   'AF Mute'
                    }

                    value = ValueStateValues[res['muteConfig']]
                    self.WriteStatus('TransmitterMuteMode', value, {'Channel': str(ch)})
                except (KeyError, IndexError, AttributeError, KeyError):
                    self.Error(['Transmitter Mute Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLowCut')

    def SetMute(self, value, qualifier):

        ch = int(qualifier['Channel'])

        ValueStateValues = {
            'On':   True,
            'Off':  False
        }

        if 1 <= ch <= self.size and value in ValueStateValues:
            MuteCmdString = 'api/channel/{}'.format(ch - 1)
            data = {
                'mute': ValueStateValues[value]
            }

            self.__SetHelper('Mute', value, qualifier, url=MuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            MuteCmdString = 'api/channel/{}'.format(ch - 1)
            res = self.__UpdateHelper('Mute', value, qualifier, url=MuteCmdString)
            if res not in [None, '']:
                try:
                    ValueStateValues = {
                        True:   'On',
                        False:  'Off'
                    }
                            
                    value = ValueStateValues[res['mute']]
                    self.WriteStatus('Mute', value, {'Channel': str(ch)})
                except (KeyError, IndexError, AttributeError, KeyError):
                    self.Error(['Mute: Invalid/unexpected response'])
                try:
                    value = res['name']
                    self.WriteStatus('TransmitterName', value, {'Channel': str(ch)})
                except (ValueError, IndexError, AttributeError, KeyError):
                    self.Error(['Transmitter Name: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def UpdateRFQuality(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            RFQualityCmdString = 'api/channel/{}/signalQualityIndicator'.format(ch - 1)
            res = self.__UpdateHelper('RFQuality', value, qualifier, url=RFQualityCmdString)
            if res not in [None, '']:
                try:
                    value = res['value']
                    if 0 <= value <= 100:
                        self.WriteStatus('RFQuality', value, qualifier)
                except (ValueError, IndexError, AttributeError, KeyError):
                    self.Error(['RF Quality: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRFQuality')

    def UpdateTransmitterCapsule(self, value, qualifier):

        ch = int(qualifier['Channel'])

        if 1 <= ch <= self.size:
            TransmitterCapsuleCmdString = 'api/transmitters/{}'.format(ch - 1)
            res = self.__UpdateHelper('TransmitterCapsule', value, qualifier, url=TransmitterCapsuleCmdString)
            if res not in [None, '']:
                try:
                    ValueStateValues = {
                        'KK_205':   'KK 205',
                        'KK_204':   'KK 204',
                        'ME_9002':  'ME 9002',
                        'ME_9004':  'ME 9004',
                        'ME_9005':  'ME 9005',
                        'MME_865':  'MME 865',
                        'MD_9235':  'MD 9235',
                        'MM_435':   'MM 435',
                        'MM_445':   'MM 445',
                        'MMD_945':  'MMD 945',
                        'MMD_935':  'MMD 935',
                        'MMD_845':  'MMD 845',
                        'MMD_835':  'MMD 835',
                        'MMD_815_1':'MMD 815-1',
                        'MMK_965':  'MMK 965',
                        'MMD_42_I': 'MMD 42-I',
                        'Unknown':  'Unknown',
                        'None':     'None'
                    }

                    value = ValueStateValues.get(res.get('capsule'), 'Not Found')
                    self.WriteStatus('TransmitterCapsule', value, {'Channel': str(ch)})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Capsule: Invalid/unexpected response'])
                try:
                    ValueStateValues = {
                        True:   'On',
                        False:  'Off'
                    }

                    value = ValueStateValues.get(res.get('mute'), 'Not Found')
                    self.WriteStatus('TransmitterMute', value, {'Channel': str(ch)})
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transmitter Mute: Invalid/unexpected response'])
                try:
                    value = res.get('type', 'Not Found')
                    self.WriteStatus('TransmitterType', value, {'Channel': str(ch)})
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Transmitter Type: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTransmitterCapsule')

    def UpdateTransmitterMute(self, value, qualifier):

        self.UpdateTransmitterCapsule(value, qualifier)

    def UpdateTransmitterMuteMode(self, value, qualifier):

        self.UpdateLowCut(value, qualifier)

    def UpdateTransmitterName(self, value, qualifier):

        self.UpdateMute(value, qualifier)

    def UpdateTransmitterType(self, value, qualifier):

        self.UpdateTransmitterCapsule(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except:
            self.Error(['{}: Invalid/unexpected response (JSON)'.format(sourceCmdName)])

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {
            'Authorization': self.base64Auth,
            'Content-Type': 'application/json'
        }

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
            'Authorization': self.base64Auth
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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

    def senn_27_5956_2(self):

        self.size = 2

    def senn_27_5956_4(self):

        self.size = 4

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
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='Off'):
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