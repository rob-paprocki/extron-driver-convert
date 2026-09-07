from Extron2.HTTPDriver import HTTPDriver
import time
import urllib.error
import urllib.request
import json
from Extron import Version

try:
    from Extron import Platform
    platform = Platform()
except ImportError:
    platform = 'Pro'

minimumVersion = (3,4,6)
version = tuple(int(i) for i in Version().split('.'))

class smsg_10_6738(HTTPDriver):
    """smsg_10_6738

    Created on 05/08/2024 11:10:12

    Supported Models:
        QN43LS03DAFXZA
        QN50LS03DAFXZA
        QN55LS03DAFXZA
        QN65LS03DAFXZA
        QN75LS03DAFXZA
        QN85LS03DAFXZA

    DRIVER STYLE
        Ethernet - HTTP Driver

    COMMAND STRUCTURE
        COMMAND DELIMITER:          JSON
        COMMAND EXAMPLE:            https://IP_ADDRESS:1516
            BODY (Refresh Token):   {
                                        "jsonrpc" : "2.0",
                                        "method" : "createAccessToken",
                                        "id" : "1"
                                    }
            HEADERS:                Content-Type: application/json
                                    Content-Length:
                                    Accept: application/json
        RESPONSE EXAMPLE:           {
                                        "id": "1",
                                        "jsonrpc": "2.0",
                                        "result": {
                                            "AccessToken": "1mvAkqTkkGoBLJtbP06A6Hli6VAvxntkYm65jhVlij0a2Sjk"
                                        }
                                    }

    COMMAND NOTES
        Reference TV_IPControl_Protocol_20231106_v.1.13.pdf

    REVISION HISTORY
    Version     Date            Notes
    1_0_0       6/4/2024        Extron Certified. Tested with QN43LS03DAFXZA. FW: 1066
                                Initial version. Internal DR.
    """

################################################################
# INITIALIZATION
################################################################

    def __init__(self, configs):
        """Driver Constructor
        Read/set information passed in via configuration data.

        """
        initError = []

        try:
            self.SSLVerifyMode = configs['DriverParams']['SSL Verify Mode']
            if self.SSLVerifyMode not in ['On', 'Off']:
                initError.append('Missing SSL Verify Mode Parameter.')
            if self.SSLVerifyMode == 'Off':
                if platform == 'Pro'and version < minimumVersion:
                    initError.append('Minimum API version not met. Needs to be >= 3.4.6')
                else:
                    configs['HTTPParams'].append('ssl_verify_off')
        except TypeError:
            initError.append('SSL Verify Mode Parameter is the wrong type.')

        super().__init__(configs)

        self.Commands = {
            'AspectRatio':      {'Set': True, 'Update': True,  'Live': True,  'Emulated': True,  'Status': {}},
            'AudioMute':        {'Set': True, 'Update': True,  'Live': True,  'Emulated': True,  'Status': {}},
            'ChannelStep':      {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
            'Input':            {'Set': True, 'Update': True,  'Live': True,  'Emulated': True,  'Status': {}},
            'Keypad':           {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
            'MenuNavigation':   {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
            'MultiviewCommand': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
            'MultiviewString':  {'Set': True, 'Update': False, 'Live': False, 'Emulated': True,  'Status': {}},
            'Power':            {'Set': True, 'Update': True,  'Live': True,  'Emulated': True,  'Status': {}},
            'RefreshToken':     {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
            'Volume':           {'Set': True, 'Update': True,  'Live': True,  'Emulated': True,  'Status': {}},
            }

        self.AccessToken = None
        self.authenticated = False

        try:
            self.Unidirectional = configs['Unidirectional']
            if self.Unidirectional not in ['True', 'False']:
                initError.append('Unidirectional set to an invalid value: {0}'.format(configs['Unidirectional']))
        except KeyError:
            initError.append('Missing Unidirectional Parameter.')

        try:
            self.CommandPacing = configs['CommandPacing']
            if not 0 <= self.CommandPacing <= 30:
                initError.append('CommandPacing must be greater than or equal to 0 and less than or equal to 30')
        except KeyError:
            initError.append('Missing CommandPacing Parameter.')
        except TypeError:
            initError.append('CommandPacing Parameter is the wrong type.')

        try:
            self.DefaultResponseTimeout = configs['ResponseTimeout']
            if self.DefaultResponseTimeout <= 0:
                initError.append('ResponseTimeout must be greater than 0.')
        except KeyError:
            initError.append('Missing ResponseTimeout Parameter.')
        except TypeError:
            initError.append('ResponseTimeout Parameter is the wrong type.')

        if initError:
            self.Error(initError)
            self.Disable()

################################################################
### BEGIN AUTO GENERATION OF COMMAND DEF
################################################################

    # pg.19/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin AspectRatio
    def _cmd_SetAspectRatio(self, value, qualifier):
        """Set Aspect Ratio
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            '4:3'  : '4:3',
            '16:9' : '16:9'
        }

        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc' : '2.0',
                'method' : 'pictureSizeControl',
                'params' : {
                    'AccessToken' : self.AccessToken,
                    'pictureSize' : ValueStateValues[value]
                },
                'id' : 1
            }

            if self.__SafeToSet('AspectRatio'):
                self.WriteAspectRatio(value, qualifier, 'Emulated')
                self.__SetHelper('AspectRatio', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateAspectRatio(self, value, qualifier):
        """Update Aspect Ratio
        value: Enum
        qualifier: None

        """
        data = {
                'jsonrpc' : '2.0',
                'method' : 'pictureSizeControl',
                'params' : {
                    'AccessToken' : self.AccessToken
                },
                'id' : 1
            }
        res = self.__UpdateHelper('AspectRatio', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {
                    '4:3': '4:3',
                    '16:9': '16:9'
                    }
                # Res: {"jsonrpc":"2.0","id":"1","result":{"pictureSize":"16:9"}}
                value = ValueStateValues[str(res['result']['pictureSize'])]
                self.WriteAspectRatio(value, qualifier, 'Live')
            except (KeyError, IndexError, AttributeError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def WriteAspectRatio(self, value, qualifier, context):
        """Write Aspect Ratio
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('AspectRatio', value, qualifier, context)

    def ReadAspectRatio(self, qualifier, context):
        """Read Aspect Ratio
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('AspectRatio', qualifier, context)

    # pg.12/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Audio Mute
    def _cmd_SetAudioMute(self, value, qualifier):
        """Set Audio Mute
        value: Enum
        qualifier: None

        """
        ValueStateValues = {
            'On'  : 'muteOn',
            'Off' : 'muteOff'
        }

        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'muteControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'mute': ValueStateValues[value]
                },
                'id': 1
            }

            if self.__SafeToSet('AudioMute'):
                self.WriteAudioMute(value, qualifier, 'Emulated')
                self.__SetHelper('AudioMute', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateAudioMute(self, value, qualifier):
        """Update Audio Mute
        value: Enum
        qualifier: None

        """
        data = {
                'jsonrpc': '2.0',
                'method': 'muteControl',
                'params': {
                    'AccessToken': self.AccessToken
                },
                'id': 1
            }
        res = self.__UpdateHelper('AudioMute', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {
                    'muteOn': 'On',
                    'muteOff': 'Off'
                    }
                # Res: {"jsonrpc":"2.0","id":"1","result":{"mute":"muteOff"}}
                value = ValueStateValues[str(res['result']['mute'])]
                self.WriteAudioMute(value, qualifier, 'Live')
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def WriteAudioMute(self, value, qualifier, context):
        """Write Audio Mute
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('AudioMute', value, qualifier, context)

    def ReadAudioMute(self, qualifier, context):
        """Read Audio Mute
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('AudioMute', qualifier, context)

    # pg.13/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Channel Step
    def _cmd_SetChannelStep(self, value, qualifier):
        """Set Channel Step
        value: Enum
        qualifier: None

        """
        ValueStateValues = {
            'Up'    : 'channelUp',
            'Down'  : 'channelDn'
        }

        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'channelUpDnControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'control': ValueStateValues[value]
                },
                'id': 1
            }

            if self.__SafeToSet('ChannelStep'):
                self.__SetHelper('ChannelStep', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    # pg.13/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Input
    def _cmd_SetInput(self, value, qualifier):
        """Set Input
        value: Enum
        qualifier: None

        """
        ValueStateValues = {
            'TV'     : 'TV',
            'HDMI 1' : 'HDMI1', 
            'HDMI 2' : 'HDMI2',
            'HDMI 3' : 'HDMI3',
            'HDMI 4' : 'HDMI4'
        }

        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'inputSourceControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'inputSource': ValueStateValues[value]
                },
                'id': 1
            }

            if self.__SafeToSet('Input'):
                self.WriteInput(value, qualifier, 'Emulated')
                self.__SetHelper('Input', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateInput(self, value, qualifier):
        """Update Input
        value: Enum
        qualifier: None

        """
        data = {
                'jsonrpc': '2.0',
                'method': 'inputSourceControl',
                'params': {
                    'AccessToken': self.AccessToken
                },
                'id': 1
            }
        res = self.__UpdateHelper('Input', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {
                    'TV': 'TV',
                    'HDMI1': 'HDMI 1',
                    'HDMI2': 'HDMI 2',
                    'HDMI3': 'HDMI 3',
                    'HDMI4': 'HDMI 4'
                    }
                # Res: {"jsonrpc":"2.0","id":"1","result":{"inputSource":"TV"}}
                value = ValueStateValues[str(res['result']['inputSource'])]
                self.WriteInput(value, qualifier, 'Live')
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def WriteInput(self, value, qualifier, context):
        """Write Input
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('Input', value, qualifier, context)

    def ReadInput(self, qualifier, context):
        """Read Input
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('Input', qualifier, context)

    # pg.37/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Keypad
    def _cmd_SetKeypad(self, value, qualifier):
        """Set Keypad
        value: Enum
        qualifier: None

        """
        ValueStateValues = {
            '0' : 'number0', 
            '1' : 'number1', 
            '2' : 'number2', 
            '3' : 'number3', 
            '4' : 'number4', 
            '5' : 'number5', 
            '6' : 'number6', 
            '7' : 'number7', 
            '8' : 'number8', 
            '9' : 'number9'
        }

        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': ValueStateValues[value]
                },
                'id': 1
            }

            if self.__SafeToSet('Keypad'):
                self.__SetHelper('Keypad', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    # pg.19/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Menu Navigation
    def _cmd_SetMenuNavigation(self, value, qualifier):
        """Set Menu Navigation
        value: Enum
        qualifier: None

        """
        ValueStateValues = {
            'Up'     : 'cursorUp',
            'Down'   : 'cursorDn',
            'Left'   : 'cursorLeft',
            'Right'  : 'cursorRight',
            'Menu'   : 'menu',
            'Enter'  : 'enter',
            'Return' : 'return',
            'Exit'   : 'exit',
            'Home'   : 'firstScreen' 
        }
        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': ValueStateValues[value]
                },
                'id': 1
            }

            if self.__SafeToSet('MenuNavigation'):
                self.__SetHelper('MenuNavigation', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    # pg.40/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Multiview Command
    def _cmd_SetMultiviewCommand(self, value, qualifier):
        """Set Multiview Command
        value: None
        qualifier: None

        """
        mode = self.ReadMultiviewString(qualifier, 'Emulated')
        data = {
                'jsonrpc': '2.0',
                'method': 'multiviewControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'multiviewMode': mode
                },
                'id': 1
            }
        if self.__SafeToSet('MultiviewCommand'):
            self.__SetHelper('MultiviewCommand', value, qualifier, data)

    # Begin Multiview String
    def _cmd_SetMultiviewString(self, value, qualifier):
        """Set Multiview String
        value: String
        qualifier: None

        """
        if self.__SafeToSet('MultiviewString'):
            self.WriteMultiviewString(value, qualifier, 'Emulated')

    def WriteMultiviewString(self, value, qualifier, context):
        """Write Multiview String
        value: String
        qualifier: None

        """
        self.WriteStatusHelper('MultiviewString', value, qualifier, context)

    def ReadMultiviewString(self, qualifier, context):
        """Read Multiview String
        value: String
        qualifier: None

        """
        return self.ReadStatusHelper('MultiviewString', qualifier, context)

    # pg.10/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Power
    def _cmd_SetPower(self, value, qualifier):
        """Set Power
        value: Enum
        qualifier: None

        """
        ValueStateValues = {
            'On':  'powerOn',
            'Off': 'powerOff'
            }

        if value in ValueStateValues and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'powerControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'power': ValueStateValues[value]
                },
                'id': 1
            }
            if self.__SafeToSet('Power'):
                self.WritePower(value, qualifier, 'Emulated')
                self.__SetHelper('Power', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdatePower(self, value, qualifier):
        """Update Power
        value: Enum
        qualifier: None

        """
        data = {
                'jsonrpc': '2.0',
                'method': 'powerControl',
                'params': {
                    'AccessToken': self.AccessToken,
                },
                'id': 1
            }
        res = self.__UpdateHelper('Power', value, qualifier, data)
        if res:
            try:
                ValueStateValues = {
                    'powerOn':  'On',
                    'powerOff': 'Off'
                    }
                # Res: {"jsonrpc":"2.0","id":"1","result":{"power":"powerOn"}}
                value = ValueStateValues[str(res['result']['power'])]
                self.WritePower(value, qualifier, 'Live')
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def WritePower(self, value, qualifier, context):
        """Write Power
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('Power', value, qualifier, context)

    def ReadPower(self, qualifier, context):
        """Read Power
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('Power', qualifier, context)

    # pg.3/5 [Extron]TV_IPControl_Protocol_Client_Authentication_20221004_v.1.0.pdf
    # Begin Refresh Token
    def _cmd_SetRefreshToken(self, value, qualifier):
        """Set Refresh Token
        value: None
        qualifier: None

        """
        data = {
            'jsonrpc' : '2.0',
            'method' : 'createAccessToken',
            'id' : 1
        }

        if self.__SafeToSet('RefreshToken'):
            res = self.__SetHelper('RefreshToken', value, qualifier, data)
            if res:
                try:
                    self.AccessToken = res['result']['AccessToken']
                    self.authenticated = True
                except KeyError:
                    self.Error(['Refresh Token: Invalid/unexpected response'])

    # pg.11/45 TV_IPControl_Protocol_20231106_v.1.13.pdf
    # Begin Volume
    def _cmd_SetVolume(self, value, qualifier):
        """Set Volume
        value: Decimal
        qualifier: None

        """
        if 0 <= value <= 100 and self.AccessToken:
            data = {
                'jsonrpc': '2.0',
                'method': 'directVolumeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'volume': value
                },
                'id': 1
            }
            if self.__SafeToSet('Volume'):
                self.WriteVolume(value, qualifier, 'Emulated')
                self.__SetHelper('Volume', value, qualifier, data)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateVolume(self, value, qualifier):
        """Update Volume
        value: Decimal
        qualifier: None

        """
        
        data = {
            'jsonrpc': '2.0',
            'method': 'directVolumeControl',
            'params': {
                'AccessToken': self.AccessToken,
            },
            'id': 1
        }
        res = self.__UpdateHelper('Volume', value, qualifier, data)
        if res:
            try:
                # Res: {"jsonrpc":"2.0","id":"1","result":{"volume":4}}
                
                value = int(res['result']['volume'])
                self.WriteVolume(value, qualifier, 'Live')
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def WriteVolume(self, value, qualifier, context):
        """Write Volume
        value: Decimal
        qualifier: None

        """
        self.WriteStatusHelper('Volume', value, qualifier, context)

    def ReadVolume(self, qualifier, context):
        """Read Volume
        value: Decimal
        qualifier: None

        """
        return self.ReadStatusHelper('Volume', qualifier, context)

################################################################
### END AUTO GENERATION OF COMMAND DEF
################################################################

    def __CheckResponseForErrors(self, sourceCmdName, response):
        """Check Response For Errors
        Called by all SendAndWait calls to the device.
        Device will always have a response...confirmation, errors or answer to queries

        """
        try:
            res = json.loads(response.read().decode())
            if 'error' in res:
                self.Error(['{0}: {1}'.format(sourceCmdName, res['error']['message'])])
                return ''
            return res
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])


    def __SafeToSet(self, command):
        powerstatus = self.ReadPower(None, 'Live')
        if powerstatus in ['Off'] and command not in ['Power', 'RefreshToken']:
            self.Discard('Inappropriate Command')
            return False
        else:
            return True

    def __SetHelper(self, command, value, qualifier, data=None):
        """Set Helper
        This function is used to determine how to send.

        """

        # Controller needs to wait for the user to hit 'Approve' when the prompt comes up to allow IP Control
        if command == 'RefreshToken':
            responseTimeout = 30
        else:
            responseTimeout = 1

        # Create Request parameters
        url = self.RootURL.replace('http', 'https')
        #url = self.RootURL # Uncomment for Emulator testing
        data = json.dumps(data).encode()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Create Request object
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=responseTimeout) # open() returns a http.client.HTTPResponse object if successful
            # Some devices need customized headers that self.Opener.open() doesn't support for these cases use urlopen()
            # res = urllib.request.urlopen(my_request)
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

    def __UpdateHelper(self, command, value, qualifier, data=None):
        """Update Helper
        This function is used to determine how to send.

        """
        # Create Request parameters
        url = self.RootURL.replace('http', 'https')
        #url = self.RootURL # Uncomment for Emulator testing
        data = json.dumps(data).encode()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.authenticated:
            # Create Request object
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
                # Some devices need customized headers that self.Opener.open() doesn't support for these cases use urlopen()
                # res = urllib.request.urlopen(my_request)
            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                self.WriteDeviceResponseStatus('Good', None, 'Live')
                res = ''
            except urllib.error.URLError as err: # received if can't reach the server (times out)
                self.Error(['{0} {1}'.format(command, err.reason)])
                if command == 'Power':
                    self.WriteDeviceResponseStatus('Bad', None, 'Live')
                res = ''
            except Exception as err: # includes HTTP status code 100 and any invalid status code
                if command == 'Power':
                    self.WriteDeviceResponseStatus('Bad', None, 'Live')
                res = ''
            else:
                self.WriteDeviceResponseStatus('Good', None, 'Live')
                if res.status not in (200, 202):
                    self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                    res = ''
                else:
                    res = self.__CheckResponseForErrors(command, res)
            self.WriteStatusHelper(command, value, qualifier, 'UpdateTime')
            return res
        else:
            self.Discard('Inappropriate Command')


    def OnConnected(self):
        """
        On Connected
        This callback will be set by the firmware when a device has connected or
        reconnected to the device.  It's called after a successful response (sync)
        or matchstring (async) via the self.DriverResponseStatus property

        """
        pass

    def OnDisconnected(self):
        """
        On Disconnected
        This callback will be set by the firmware when a device has not responded
        or malformed responed for <n> seconds as indicated in the driver
        descriptor.  Behavior is to set all status to their uninitialized state.

        """
        self.__ResetLiveStatus()

################################################################
### HELPER METHODS SECTION
################################################################

    def WriteStatusHelper(self, command, value, qualifier, context):
        """
        Write Status Helper
        Wrapper method to manage setting/posting Live and Emulated status

        """
        Command = self.Commands[command]
        if Command['Live'] or Command['Emulated']:
            Status = Command['Status']
            with self.Mutex():
                if 'Parameters' in Command:
                    for Parameter in Command['Parameters']:
                        try:
                            Status = Status[qualifier[Parameter]]
                        except KeyError:
                            if Parameter in qualifier:
                                Status[qualifier[Parameter]] = {}
                                Status = Status[qualifier[Parameter]]
                            else:
                                self.Error(['Invalid parameter(s): {0}'.format(qualifier)])
                                return
                try:
                    if context in ['Live', 'Emulated']:
                        Status['TimeStamps'][context] = ExtronTime(time.monotonic())
                        if Status[context] != value:
                            Status[context] = value
                            self.PostNewStatusEx(command, value, qualifier, context)
                    elif context == 'UpdateTime':
                        try:
                            Status['TimeStamps']['Update'] = ExtronTime(time.monotonic())
                        except KeyError:
                            Status['TimeStamps'] = {'Update': ExtronTime(time.monotonic())}
                    elif context == 'Meta':
                        Status['Meta'] = value

                except:
                    Status['Emulated'] = value
                    if 'TimeStamps' not in Status:
                        Status['TimeStamps'] = {}
                    Status['TimeStamps']['Emulated'] = ExtronTime(time.monotonic())
                    self.PostNewStatusEx(command, value, qualifier, 'Emulated')
                    if context == 'Live':
                        Status['Live'] = value
                        Status['TimeStamps']['Live'] = ExtronTime(time.monotonic())
                        self.PostNewStatusEx(command, value, qualifier, 'Live')
                    else:
                        Status['Live'] = None
                        Status['TimeStamps']['Live'] = None
        else:
            self.Error(['Command, {0}, does not have status.'.format(command)])
            return

    def ReadStatusHelper(self, command, qualifier, context):
        """
        Read Status Helper
        Wrapper method to return current status Live or Emulated

        """
        Command = self.Commands[command]
        if Command['Live'] or Command['Emulated']:
            Status = Command['Status']
            with self.Mutex():
                if 'Parameters' in Command:
                    for Parameter in Command['Parameters']:
                        try:
                            Status = Status[qualifier[Parameter]]
                        except KeyError:
                            return None
                try:
                    return Status[context]
                except:
                    return None
        else:
            self.Error(['Command, {0}, does not have status.'.format(command)])
            return

    def __StatusItems(self, dictionary):
        """Iterator Function to 'yield' all of the Live/Emulated pairs

        """
        for k, v in dictionary.items():
            if k == 'Live' and not isinstance(dictionary['Live'], dict) and not isinstance(dictionary['Live'], ExtronTime):
                yield [], dictionary
            elif isinstance(v, dict):
                for subkey, result in self.__StatusItems(v):
                    yield [k]+subkey, result

    def _cmd_SetSyncEmulatedStatus(self, value, qualifier):
        """
        Synchronize All Emulated Status
        This command is issued by the automation script to cause a driver to sync
        all Emulated Feedback status to the authoritative Live feedback information.
        For each Emulated Feedback field that is out of date, change notification
        should be generated.
        value:  None
        qualifier:  None

        """
        with self.Mutex():
            if value in self.Commands:
                Command = self.Commands[value]
                if Command['Live'] and Command['Emulated']:
                    Status = Command['Status']
                    if 'Parameters' in Command:
                        for Parameter in Command['Parameters']:
                            try:
                                Status = Status[qualifier[Parameter]]
                            except KeyError:
                                if Parameter not in qualifier:
                                    self.Error(['Invalid parameter(s): {0}'.format(qualifier)])
                                    return
                    try:
                        if Status['Live'] is not None and Status['Live'] != Status['Emulated'] and Status['TimeStamps']['Live'] > Status['TimeStamps']['Emulated']:
                            Status['Emulated'] = Status['Live']
                            self.PostNewStatusEx(value, Status['Live'], qualifier, 'Emulated')
                    except:
                        pass
            else:
                self.Error(['Invalid Command: {0}'.format(value)])

    def StatusRefresh(self):
        """
        Status Refresh
        This command is called by the automation script when it needs a driver to
        to generate a Refresh of status for soft clients.

        """
        self.PostNewStatusEx('RefreshBegin', None, None, 'Live')
        with self.Mutex():
            for command in self.Commands:
                Command = self.Commands[command]
                for Parameters, Status in self.__StatusItems(Command['Status']):
                    qualifier = {}
                    for Parameter in range(len(Parameters)):
                        qualifier[Command['Parameters'][Parameter]] = Parameters[Parameter]
                    self.PostNewStatusEx(command, Status['Live'], qualifier, 'LiveRefresh')
                    self.PostNewStatusEx(command, Status['Emulated'], qualifier, 'EmulatedRefresh')
        super().StatusRefresh()
        self.PostNewStatusEx('RefreshComplete', None, None, 'Live')

    def __ResetLiveStatus(self):
        """
        Reset Status to Uninitialized
        This function is call when OnDisconnected is call to reset all the Live status.

        """
        with self.Mutex():
            for command in self.Commands:
                Command = self.Commands[command]
                if Command['Live']:
                    for _, Status in self.__StatusItems(Command['Status']):
                        Status['Live'] = None

    #Parent Class overloads
    def SendAndWait(self, data, timeout, **kwds):
        """Send and Wait
        Overload to handle bytes translation. If the data is a string then the data returned
        from the device will be a string. If the data sent is a byte string, then
        the data returned from the device will be a byte string.

        """
        if isinstance(data, str):
            data = data.encode(encoding = 'iso-8859-1')
            IsString = True
        else:
            IsString = False
        try:
            kwds['deliTag'] = kwds['deliTag'].encode(encoding = 'iso-8859-1')
        except:
            pass
        if IsString:
            check = super().SendAndWait(data, timeout, **kwds)
            if check:
                return check.decode()
            else:
                return ''
        else:
            return super().SendAndWait(data, timeout, **kwds)

    def Send(self, data, **kwds):
        """Send
        Overload to handle bytes translation.

        """
        if isinstance(data, str):
            data = data.encode(encoding = 'iso-8859-1')
        super().Send(data, **kwds)


class ExtronTime(float):
    pass

