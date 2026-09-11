from json import loads, dumps
import urllib.error
import urllib.request
import base64


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):

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
            'HDMIOutputEnable': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Zone'], 'Status': {}},
            'Mute': {'Parameters': ['Zone'], 'Status': {}},
            'Power': {'Parameters': ['Zone'], 'Status': {}},
            'Preset': {'Parameters': ['Action', 'Zone', 'Band'], 'Status': {}},
            'SoundProgram': {'Parameters': ['Zone'], 'Status': {}},
            'SpeakerEnable': {'Parameters': ['Speaker'], 'Status': {}},
            'Volume': {'Parameters': ['Zone'], 'Status': {}},
        }

    def UpdateAPIVersion(self, value, qualifier):

        res = self.__UpdateHelper('APIVersion', value, qualifier, 'system/getDeviceInfo')
        if res:
            try:
                self.WriteStatus('APIVersion', res['api_version'], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid Response for API Version.'])

    def SetHDMIOutputEnable(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        States = {
            'Enable': 'true',
            'Disable': 'false'
        }

        Output = OutputStates[qualifier['Output']]
        State = States[value]

        CmdString = 'system/setHdmiOut{}?enable={}'.format(Output, State)
        self.__SetHelper('HDMIOutputEnable', value, qualifier, CmdString)

    def UpdateHDMIOutputEnable(self, value, qualifier):

        States = {
            True: 'Enable',
            False: 'Disable'
        }

        res = self.__UpdateHelper('HDMIOutputEnable', value, qualifier, 'system/getFuncStatus')
        if res:

            try:
                self.WriteStatus('HDMIOutputEnable', States[res['hdmi_out_1']], {'Output': '1'})
                self.WriteStatus('HDMIOutputEnable', States[res['hdmi_out_2']], {'Output': '2'})
            except (KeyError, IndexError):
                self.Error(['Invalid Response for HDMI Output Enable.'])

            try:
                self.WriteStatus('SpeakerEnable', States[res['speaker_a']], {'Speaker': 'A'})
                self.WriteStatus('SpeakerEnable', States[res['speaker_b']], {'Speaker': 'B'})
            except (KeyError, IndexError):
                self.Error(['Invalid Response for Speaker Enable.'])

    def SetInput(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        Zone = ZoneStates[qualifier['Zone']]

        States = {
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
            'AV 1': 'av1',
            'AV 2': 'av2',
            'AV 3': 'av3',
            'AV 4': 'av4',
            'Audio 1': 'audio1',
            'Audio 2': 'audio2',
            'Audio 3': 'audio3',
            'Optical 1': 'optical1',
            'Optical 2': 'optical2',
            'Coaxial 1': 'coaxial1',
            'Coaxial 2': 'coaxial2',
            'Analog': 'analog',
            'TV': 'tv',
            'USB DAC': 'usb_dac',
            'USB': 'usb',
            'Bluetooth': 'bluetooth',
            'Server': 'server',
            'Net Radio': 'net_radio',
            'Rhapsody': 'rhapsody',
            'Napster': 'napster',
            'Pandora': 'pandora',
            'SiriusXM': 'siriusxm',
            'Spotify': 'spotify',
            'Juke': 'juke',
            'Airplay': 'airplay',
            'Radiko': 'radiko',
            'Qobuz': 'qobuz',
            'MC Link': 'mc_link',
            'Main Sync': 'main_sync'
        }

        State = States[value]

        CmdString = '{}/setInput?input={}&mode=autoplay_disabled'.format(Zone, State)
        self.__SetHelper('Input', value, qualifier, CmdString)

    def UpdateInput(self, value, qualifier):

        Zone = qualifier['Zone']
        CmdString = ''

        if Zone == 'Main':
            CmdString = 'main/getStatus'

        elif Zone == '2':
            CmdString = 'zone2/getStatus'

        elif Zone == '3':
            CmdString = 'zone3/getStatus'

        elif Zone == '4':
            CmdString = 'zone4/getStatus'

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
            'av1': 'AV 1',
            'av2': 'AV 2',
            'av3': 'AV 3',
            'av4': 'AV 4',
            'audio1': 'Audio 1',
            'audio2': 'Audio 2',
            'audio3': 'Audio 3',
            'optical1': 'Optical 1',
            'optical2': 'Optical 2',
            'coaxial1': 'Coaxial 1',
            'coaxial2': 'Coaxial 2',
            'analog': 'Analog',
            'tv': 'TV',
            'usb_dac': 'USB DAC',
            'usb': 'USB',
            'bluetooth': 'Bluetooth',
            'server': 'Server',
            'net_radio': 'Net Radio',
            'rhapsody': 'Rhapsody',
            'napster': 'Napster',
            'pandora': 'Pandora',
            'siriusxm': 'SiriusXM',
            'spotify': 'Spotify',
            'juke': 'Juke',
            'airplay': 'Airplay',
            'radiko': 'Radiko',
            'qobuz': 'Qobuz',
            'mc_link': 'MC Link',
            'main_sync': 'Main Sync'
        }

        PowerStates = {
            'on': 'On',
            'standby': 'Off'
        }

        MuteStates = {
            True: 'On',
            False: 'Off'
        }

        SoundProgramStates = {
            'munich_a': 'Munich A',
            'munich_b': 'Munich B',
            'munich': 'Munich',
            'frankfurt': 'Frankfurt',
            'stuttgart': 'Stuttgart',
            'vienna': 'Vienna',
            'amsterdam': 'Amsterdam',
            'usa_a': 'USA A',
            'usa_b': 'USA B',
            'tokyo': 'Tokyo',
            'freiburg': 'Freiburg',
            'royaumont': 'Royaumont',
            'chamber': 'Chamber',
            'concert': 'Concert',
            'village_gate': 'Village Gate',
            'village_vanguard': 'Village Vanguard',
            'warehouse_loft': 'Warehouse Loft',
            'cellar_club': 'Cellar Club',
            'jazz_club': 'Jazz Club',
            'roxy_theatre': 'Roxy Theatre',
            'bottom_line': 'Bottom Line',
            'arena': 'Arena',
            'sports': 'Sports',
            'action_game': 'Action Game',
            'roleplaying_game': 'Roleplaying Game',
            'game': 'Game',
            'music_video': 'Music Video',
            'music': 'Music',
            'recital_opera': 'Recital Opera',
            'pavilion': 'Pavilion',
            'disco': 'Disco',
            'standard': 'Standard',
            'spectacle': 'Spectacle',
            'sci-fi': 'Sci-Fi',
            'adventure': 'Adventure',
            'drama': 'Drama',
            'talk_show': 'Talk Show',
            'tv_program': 'TV Program',
            'mono_movie': 'Mono Movie',
            'movie': 'Movie',
            'enhanced': 'Enhanced',
            '2ch_stereo': '2 Channel Stereo',
            '5ch_stereo': '5 Channel Stereo',
            '7ch_stereo': '7 Channel Stereo',
            '9ch_stereo': '9 Channel Stereo',
            '11ch_stereo': '11 Channel Stereo',
            'stereo': 'Stereo',
            'surr_decoder': 'Surround Decoder',
            'my_surround': 'My Surround',
            'target': 'Target',
            'straight': 'Straight',
            'off': 'Off'
        }

        if CmdString:
            res = self.__UpdateHelper('HDMIOutputEnable', value, qualifier, CmdString)
            if res:
                try:
                    self.WriteStatus('Power', PowerStates[res['power']], {'Zone': Zone})
                except (KeyError, IndexError):
                    self.Error(['Invalid Response for Zone {}: Power.'.format(Zone)])

                try:
                    self.WriteStatus('Input', InputStates[res['input']], {'Zone': Zone})
                except (KeyError, IndexError):
                    sself.Error(['Invalid Response for Zone {}: Input.'.format(Zone)])

                try:
                    self.WriteStatus('Volume', res['volume'], {'Zone': Zone})
                except (ValueError, IndexError):
                    self.Error(['Invalid Response for Zone {}: Volume.'.format(Zone)])

                try:
                    self.WriteStatus('Mute', MuteStates[res['mute']], {'Zone': Zone})
                except (KeyError, IndexError):
                    self.Error(['Invalid Response for Zone {}: Mute.'.format(Zone)])

                try:
                    self.WriteStatus('SoundProgram', SoundProgramStates[res['sound_program']], {'Zone': Zone})
                except (KeyError, IndexError):
                    self.Error(['Invalid Response for Zone {}: Sound Program.'.format(Zone)])

    def SetMute(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        Zone = ZoneStates[qualifier['Zone']]

        States = {
            'On': 'true',
            'Off': 'false'
        }

        State = States[value]

        CmdString = '{}/setMute?enable={}'.format(Zone, State)
        self.__SetHelper('Mute', value, qualifier, CmdString)

    def UpdateMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetPower(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        Zone = ZoneStates[qualifier['Zone']]

        States = {
            'On': 'on',
            'Off': 'standby'
        }

        State = States[value]

        CmdString = '{}/setPower?power={}'.format(Zone, State)
        self.__SetHelper('Power', value, qualifier, CmdString)

    def UpdatePower(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetPreset(self, value, qualifier):

        Action = qualifier['Action']

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        Zone = ZoneStates[qualifier['Zone']]

        BandStates = {
            'Common': 'common',
            'AM': 'am',
            'FM': 'fm',
            'DAB': 'dab'
        }

        Band = BandStates[qualifier['Band']]

        States = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        State = States[value]

        CmdString = ''
        if Action == 'Recall':
            CmdString = 'tuner/recallPreset?zone={}&band={}&num={}'.format(Zone, Band, State)
        elif Action == 'Save':
            CmdString = 'tuner/storePreset?num={}'.format(State)
        elif Action == 'Clear':
            CmdString = 'tuner/clearPreset?band={}&num={}'.format(Band, State)

        if CmdString:
            self.__SetHelper('Preset', value, qualifier, CmdString)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetSoundProgram(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        Zone = ZoneStates[qualifier['Zone']]

        States = {
            'Munich A': 'munich_a',
            'Munich B': 'munich_b',
            'Munich': 'munich',
            'Frankfurt': 'frankfurt',
            'Stuttgart': 'stuttgart',
            'Vienna': 'vienna',
            'Amsterdam': 'amsterdam',
            'USA A': 'usa_a',
            'USA B': 'usa_b',
            'Tokyo': 'tokyo',
            'Freiburg': 'freiburg',
            'Royaumont': 'royaumont',
            'Chamber': 'chamber',
            'Concert': 'concert',
            'Village Gate': 'village_gate',
            'Village Vanguard': 'village_vanguard',
            'Warehouse Loft': 'warehouse_loft',
            'Cellar Club': 'cellar_club',
            'Jazz Club': 'jazz_club',
            'Roxy Theatre': 'roxy_theatre',
            'Bottom Line': 'bottom_line',
            'Arena': 'arena',
            'Sports': 'sports',
            'Action Game': 'action_game',
            'Roleplaying Game': 'roleplaying_game',
            'Game': 'game',
            'Music Video': 'music_video',
            'Music': 'music',
            'Recital Opera': 'recital_opera',
            'Pavilion': 'pavilion',
            'Disco': 'disco',
            'Standard': 'standard',
            'Spectacle': 'spectacle',
            'Sci-Fi': 'sci-fi',
            'Adventure': 'adventure',
            'Drama': 'drama',
            'Talk Show': 'talk_show',
            'TV Program': 'tv_program',
            'Mono Movie': 'mono_movie',
            'Movie': 'movie',
            'Enhanced': 'enhanced',
            '2 Channel Stereo': '2ch_stereo',
            '5 Channel Stereo': '5ch_stereo',
            '7 Channel Stereo': '7ch_stereo',
            '9 Channel Stereo': '9ch_stereo',
            '11 Channel Stereo': '11ch_stereo',
            'Stereo': 'stereo',
            'Surround Decoder': 'surr_decoder',
            'My Surround': 'my_surround',
            'Target': 'target',
            'Straight': 'straight',
            'Off': 'off'
        }

        State = States[value]

        CmdString = '{}/setSoundProgram?program={}'.format(Zone, State)
        self.__SetHelper('SoundProgram', value, qualifier, CmdString)

    def UpdateSoundProgram(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetSpeakerEnable(self, value, qualifier):

        SpeakerStates = {
            'A': 'A',
            'B': 'B'
        }

        Speaker = SpeakerStates[qualifier['Speaker']]

        States = {
            'Enable': 'true',
            'Disable': 'false'
        }

        State = States[value]

        CmdString = 'system/setSpeaker{}?enable={}'.format(Speaker, State)
        self.__SetHelper('SpeakerEnable', value, qualifier, CmdString)

    def UpdateSpeakerEnable(self, value, qualifier):
        self.UpdateHDMIOutputEnable(value, qualifier)

    def SetVolume(self, value, qualifier):

        ZoneStates = {
            'Main': 'main',
            '2': 'zone2',
            '3': 'zone3',
            '4': 'zone4'
        }

        Zone = ZoneStates[qualifier['Zone']]

        if 0 <= value <= 161:
            CmdString = '{}/setVolume?volume={}'.format(Zone, value)
            self.__SetHelper('Volume', value, qualifier, CmdString)
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
            112: 'Access Denied'
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

        url = '{}YamahaExtendedControl/v1/{}'.format(self.RootURL, resource)
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

        url = '{}YamahaExtendedControl/v1/{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

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
