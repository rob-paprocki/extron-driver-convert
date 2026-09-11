from json import loads, dumps
import urllib.error
import urllib.request
import base64


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'APIVersion': {'Status': {}},
            'Input': {'Parameters': ['Zone'], 'Status': {}},
            'Mute': {'Parameters': ['Zone'], 'Status': {}},
            'Power': {'Parameters': ['Zone'], 'Status': {}},
            'Preset': {'Parameters': ['Action', 'Zone', 'Band'], 'Status': {}},
            'Volume': {'Parameters': ['Zone'], 'Status': {}},
        }

        self.ZoneStates = {
            'Main': ['main', 0],
            '2': ['zone2', 0],
            '3': ['zone3', 0],
            '4': ['zone4', 0]
        }

    def UpdateAPIVersion(self, value, qualifier):

        APIVersionCmdString = 'YamahaExtendedControl/v1/system/getDeviceInfo'
        res = self.__UpdateHelper('APIVersion', value, qualifier, APIVersionCmdString)
        if res:
            try:
                value = res['api_version']
                self.WriteStatus('APIVersion', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['API Version: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        ValueStateValues = {
            'CD': 'cd',
            'Tuner': 'tuner',
            'Multi Channel': 'multi_ch',
            'Phono': 'phono',
            'HDMI 1': 'hdmi1',
            'HDMI 2': 'hdmi2',
            'HDMI 3': 'hdmi3',
            'HDMI 4': 'hdmi4',
            'HDMI 5': 'hdmi5',
            'HDMI 6': 'hdmi6',
            'HDMI 7': 'hdmi7',
            'HDMI 8': 'hdmi8',
            'HDMI': 'hdmi',
            'V AUX': 'v_aux',
            'AUX 1': 'aux1',
            'AUX 2': 'aux2',
            'AUX': 'aux',
            'Audio 1': 'audio1',
            'Audio 2': 'audio2',
            'Audio 3': 'audio3',
            'Audio 4': 'audio4',
            'Audio 5': 'audio5',
            'Audio CD': 'audio_cd',
            'Audio': 'audio',
            'Optical 1': 'optical1',
            'Optical 2': 'optical2',
            'Optical': 'optical',
            'Coaxial 1': 'coaxial1',
            'Coaxial 2': 'coaxial2',
            'Coaxial': 'coaxial',
            'Digital 1': 'digital1',
            'Digital 2': 'digital2',
            'Digital': 'digital',
            'Line 1': 'line1',
            'Line 2': 'line2',
            'Line 3': 'line3',
            'Line CD': 'line_cd',
            'Analog': 'analog',
            'TV': 'tv',
            'BD DVD': 'bd_dvd',
            'USB DAC': 'usb_dac',
            'USB': 'usb',
            'Bluetooth': 'bluetooth',
            'Server': 'server',
            'Net Radio': 'net_radio',
            'Napster': 'napster',
            'Pandora': 'pandora',
            'SiriusXM': 'siriusxm',
            'Spotify': 'spotify',
            'Juke': 'juke',
            'Airplay': 'airplay',
            'Radiko': 'radiko',
            'Qobuz': 'qobuz',
            'Tidal': 'tidal',
            'Deezer': 'deezer',
            'MC Link': 'mc_link',
            'Main Sync': 'main_sync',
            'AV 1': 'av1',
            'AV 2': 'av2',
            'AV 3': 'av3',
            'AV 4': 'av4',
            'AV 5': 'av5',
            'AV 6': 'av6',
            'AV 7': 'av7',
            'None': 'none'
        }

        zone_val = qualifier['Zone']
        if zone_val in ZoneStates:
            InputCmdString = 'YamahaExtendedControl/v1/{}/setInput?input={}&mode=autoplay_disabled'.format(ZoneStates[zone_val], ValueStateValues[value])
            self.__SetHelper('Input', value, qualifier, InputCmdString)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputStates = {
            'cd': 'CD',
            'tuner': 'Tuner',
            'multi_ch': 'Multi Channel',
            'phono': 'Phono',
            'hdmi1': 'HDMI 1',
            'hdmi2': 'HDMI 2',
            'hdmi3': 'HDMI 3',
            'hdmi4': 'HDMI 4',
            'hdmi5': 'HDMI 5',
            'hdmi6': 'HDMI 6',
            'hdmi7': 'HDMI 7',
            'hdmi8': 'HDMI 8',
            'hdmi': 'HDMI',
            'v_aux': 'V AUX',
            'aux1': 'AUX 1',
            'aux2': 'AUX 2',
            'aux': 'AUX',
            'audio1': 'Audio 1',
            'audio2': 'Audio 2',
            'audio3': 'Audio 3',
            'audio4': 'Audio 4',
            'audio5': 'Audio 5',
            'audio_cd': 'Audio CD',
            'audio': 'Audio',
            'optical1': 'Optical 1',
            'optical2': 'Optical 2',
            'optical': 'Optical',
            'coaxial1': 'Coaxial 1',
            'coaxial2': 'Coaxial 2',
            'coaxial': 'Coaxial',
            'digital1': 'Digital 1',
            'digital2': 'Digital 2',
            'digital': 'Digital',
            'line1': 'Line 1',
            'line2': 'Line 2',
            'line3': 'Line 3',
            'line_cd': 'Line CD',
            'analog': 'Analog',
            'tv': 'TV',
            'bd_dvd': 'BD DVD',
            'usb_dac': 'USB DAC',
            'usb': 'USB',
            'bluetooth': 'Bluetooth',
            'server': 'Server',
            'net_radio': 'Net Radio',
            'napster': 'Napster',
            'pandora': 'Pandora',
            'siriusxm': 'SiriusXM',
            'spotify': 'Spotify',
            'juke': 'Juke',
            'airplay': 'Airplay',
            'radiko': 'Radiko',
            'qobuz': 'Qobuz',
            'tidal': 'Tidal',
            'deezer': 'Deezer',
            'mc_link': 'MC Link',
            'main_sync': 'Main Sync',
            'av1': 'AV 1',
            'av2': 'AV 2',
            'av3': 'AV 3',
            'av4': 'AV 4',
            'av5': 'AV 5',
            'av6': 'AV 6',
            'av7': 'AV 7',
            'none': 'None'
        }

        PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

        MuteStates = {
            True: 'On',
            False: 'Off'
        }

        zone_val = qualifier['Zone']

        if zone_val in self.ZoneStates:
            InputCmdString = 'YamahaExtendedControl/v1/{}/getStatus'.format(self.ZoneStates[zone_val][0])
            res = self.__UpdateHelper('Input', value, qualifier, InputCmdString)
            if res:
                try:
                    value = InputStates[res['input']]
                    self.WriteStatus('Input', value, {'Zone': zone_val})
                except (KeyError, IndexError):
                    self.Error(['Input for Zone {}: Invalid/unexpected response'.format(zone_val)])

                try:
                    value = MuteStates[res['mute']]
                    self.WriteStatus('Mute', value, {'Zone': zone_val})
                except (KeyError, IndexError):
                    self.Error(['Mute for Zone {}: Invalid/unexpected response'.format(zone_val)])

                try:
                    value = PowerStates[res['power']]
                    self.WriteStatus('Power', value, {'Zone': zone_val})
                except (KeyError, IndexError):
                    self.Error(['Power for Zone {}: Invalid/unexpected response'.format(zone_val)])

                try:
                    value = res['volume']
                    self.WriteStatus('Volume', value, {'Zone': zone_val})
                except (KeyError, IndexError):
                    self.Error(['Volume for Zone {}: Invalid/unexpected response'.format(zone_val)])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetMute(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        ValueStateValues = {
            'On': 'true',
            'Off': 'false'
        }

        zone_val = qualifier['Zone']
        if zone_val in ZoneStates:
            MuteCmdString = 'YamahaExtendedControl/v1/{}/setMute?enable={}'.format(ZoneStates[zone_val], ValueStateValues[value])
            self.__SetHelper('Mute', value, qualifier, MuteCmdString)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetPower(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'standby'
        }

        zone_val = qualifier['Zone']
        if zone_val in ZoneStates:
            PowerCmdString = 'YamahaExtendedControl/v1/{}/setPower?power={}'.format(ZoneStates[zone_val], ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetPreset(self, value, qualifier):

        ActionStates = ['Recall', 'Save', 'Clear']

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        BandStates = {
            'Common': 'common',
            'AM': 'am',
            'FM': 'fm',
            'DAB': 'dab'
        }

        PresetCmdString = ''
        action_val = qualifier['Action']
        zone_val = qualifier['Zone']
        band_val = qualifier['Band']
        if 0 <= int(value) <= 40 and action_val in ActionStates and zone_val in ZoneStates and band_val in BandStates:
            if action_val == 'Recall':
                PresetCmdString = 'YamahaExtendedControl/v1/tuner/recallPreset?zone={}&band={}&num={}'.format(ZoneStates[zone_val], BandStates[band_val], value)
            elif action_val == 'Save':
                PresetCmdString = 'YamahaExtendedControl/v1/tuner/storePreset?num={}'.format(value)
            elif action_val == 'Clear':
                PresetCmdString = 'YamahaExtendedControl/v1/tuner/clearPreset?band={}&num={}'.format(BandStates[band_val], value)
            if PresetCmdString:
                self.__SetHelper('Preset', value, qualifier, PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetVolume(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 194
        }

        zone_val = qualifier['Zone']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and zone_val in ZoneStates:
            VolumeCmdString = 'YamahaExtendedControl/v1/{}/setVolume?volume={}'.format(ZoneStates[zone_val], value)
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        RESPONSE_CODE = {
            1: 'Initializing',
            2: 'Internal Error',
            3: 'Invalid Request (A method did not exist, a method wasn\'t appropriate etc.)',
            4: 'Invalid Parameter (Out of range, invalid characters etc.)',
            5: 'Guarded (Unable to setup in current status etc.)',
            6: 'Time Out',
            99: 'Firmware Updating',
            100: 'Access Error',
            101: 'Other Errors',
            102: 'Wrong User Name',
            103: 'Wrong Password',
            104: 'Account Expired',
            105: 'Account Disconnected/Gone Off/Shut Down',
            106: 'Account Number Reached to the Limit',
            107: 'Server Maintenance',
            108: 'Invalid Account',
            109: 'License Error',
            110: 'Read Only Mode',
            111: 'Max Stations',
            112: 'Access Denied',
            113: 'There is a need to specify the additional destination Playlist',
            114: 'There is a need to create a new Playlist',
            115: 'Simultaneous logins has reached the upper limit',
            200: 'Linking in progress',
            201: 'Unlinking in progress'
        }

        try:
            res = loads(response.read().decode())
            if res['response_code'] in RESPONSE_CODE:
                err = RESPONSE_CODE[res['response_code']]
                self.Error(['Command {}, Error {}'.format(sourceCmdName, err)])
                return ''
            elif res['response_code'] == 0:
                return res
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True

        url = '{}{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
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

        self.ZoneStates = {
            'Main': ['main', 0],
            '2': ['zone2', 0],
            '3': ['zone3', 0],
            '4': ['zone4', 0]
        }

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
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
        Command = self.Commands[command]
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
