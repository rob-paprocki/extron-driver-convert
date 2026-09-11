from Extron2.HTTPDriver import HTTPDriver
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

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Enhancer': {'Parameters':['Zone'], 'Status': {}},
            'Input': {'Parameters':['Zone'], 'Status': {}},
            'Mute': {'Parameters':['Zone'], 'Status': {}},
            'Playback': { 'Status': {}},
            'PlaybackInfo': {'Parameters':['Name'], 'Status': {}},
            'PlaybackTime': {'Parameters':['Time'], 'Status': {}},
            'Power': {'Parameters':['Zone'], 'Status': {}},
            'PresetClear': { 'Status': {}},
            'PresetRecall': {'Parameters':['Zone'], 'Status': {}},
            'PresetSave': { 'Status': {}},
            'PureDirect': {'Parameters':['Zone'], 'Status': {}},
            'Repeat': { 'Status': {}},
            'Shuffle': { 'Status': {}},
            'Sleep': {'Parameters':['Zone'], 'Status': {}},
            'SpeakerPattern': { 'Status': {}},
            'Volume': {'Parameters':['Zone'], 'Status': {}},
        }

    def SetEnhancer(self, value, qualifier):

        state = {'On' : 'true', 'Off': 'false'}[value]
        if qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            self.__SetHelper('Enhancer', value, qualifier, '{}/setEnhancer?enable={}'.format(zone, state))
        else:
            self.Discard('Invalid Command for SetEnhancer')

    def UpdateEnhancer(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetInput(self, value, qualifier):

        state = {
            'AV 1'           : 'av1', 
            'AV 2'           : 'av2', 
            'AV 3'           : 'av3', 
            'AV 4'           : 'av4', 
            'AV 5'           : 'av5', 
            'AV 6'           : 'av6', 
            'AV 7'           : 'av7', 
            'AUX'            : 'aux', 
            'USB'            : 'usb', 
            'Bluetooth'      : 'bluetooth', 
            'Server'         : 'server', 
            'Net Radio'      : 'net_radio', 
            'Audio 1'        : 'audio1', 
            'Audio 2'        : 'audio2', 
            'Audio 3'        : 'audio3', 
            'Phono'          : 'phono', 
            'Airplay'        : 'airplay', 
            'MusicCast Link' : 'mc_link'
        }[value]

        if qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            self.__SetHelper('Input', value, qualifier, '{}/setInput?input={}&mode=autoplay_disabled'.format(zone, state))
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        self.UpdatePower(value, qualifier)        

    def SetMute(self, value, qualifier):

        state = {'On' : 'true', 'Off' : 'false'}[value]
        if qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            self.__SetHelper('Mute', value, qualifier, '{}/setMute?enable={}'.format(zone, state))
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetPlayback(self, value, qualifier):

        state = {
            'Play'               : 'play', 
            'Stop'               : 'stop', 
            'Pause'              : 'pause', 
            'Play/Pause'         : 'play_pause', 
            'Previous'           : 'previous', 
            'Next'               : 'next', 
            'Fast Reverse Start' : 'fast_reverse_start', 
            'Fast Reverse Stop'  : 'fast_reverse_end', 
            'Fast Forward Start' : 'fast_forward_start', 
            'Fast Forward Stop'  : 'fast_forward_stop', 
        }[value]

        if value in ['Play', 'Stop', 'Pause']:
            self.__SetHelper('Playback', value, qualifier, 'netusb/setPlayback?playback={}'.format(state))

    def UpdatePlayback(self, value, qualifier):

        res = self.__UpdateHelper('Playback', value, qualifier, 'netusb/getPlayInfo')
        if res:
            try:
                value = {
                    'play'          : 'Play',
                    'stop'          :'Stop',
                    'pause'         :'Pause',
                    'fast_reverse'  :'Fast Reverse',
                    'fast_forward'  :'Fast Forward'
                }[res['playback']]

                self.WriteStatus('Playback', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Playback: Invalid/unexpected response'])
            try:
                for name in ['artist','album','track']:
                    self.WriteStatus('PlaybackInfo', res[name], {'Name':name.title()})
            except (KeyError, TypeError, IndexError):
                self.Error(['PlaybackInfo: Invalid/unexpected response'])
            try:
                current_time = res['play_time']
                if current_time > -60000:
                    self.WriteStatus('PlaybackTime', str(current_time), {'Time':'Current'})
                else:
                    self.WriteStatus('PlaybackTime', 'Not Available', {'Time':'Current'})
                
                total_time = res['total_time']
                if total_time > 0:
                    self.WriteStatus('PlaybackTime', str(total_time), {'Time':'Total'})
                else:
                    self.WriteStatus('PlaybackTime', 'Not Available', {'Time':'Total'})
            except (KeyError, TypeError, IndexError):
                self.Error(['PlaybackTime: Invalid/unexpected response'])   
            try:
                self.WriteStatus('Repeat', res['repeat'].title(), qualifier)
            except (KeyError, TypeError, IndexError):
                self.Error(['Repeat: Invalid/unexpected response'])
            try:
                self.WriteStatus('Shuffle', res['shuffle'].title(), qualifier)
            except (KeyError, TypeError, IndexError):
                self.Error(['Shuffle: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        state = {'On': 'on', 'Off': 'standby'}[value]
        if qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            self.__SetHelper('Power', value, qualifier, '{}/setPower?power={}'.format(zone, state))
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        zone = qualifier['Zone']
        cmdString = ''

        if zone in ['Main', '2']:
            if zone == 'Main':                
                cmdString = 'main/getStatus'
            elif zone == '2':                
                cmdString = 'zone2/getStatus'

            states = {True : 'On', False : 'Off'}
            power_states =  {'on':'On', 'standby':'Off'}
            input_states = {
                'av1'       : 'AV 1',
                'av2'       : 'AV 2',
                'av3'       : 'AV 3',
                'av4'       : 'AV 4',
                'av5'       : 'AV 5',
                'av6'       : 'AV 6',
                'av7'       : 'AV 7',
                'aux'       : 'AUX',
                'usb'       : 'USB',
                'bluetooth' : 'Bluetooth',
                'server'    : 'Server',
                'net_radio' : 'Net Radio',
                'audio1'    : 'Audio 1',
                'audio2'    : 'Audio 2',
                'audio3'    : 'Audio 3',
                'phono'     : 'Phono',
                'airplay'   : 'Airplay',
                'mc_link'   : 'MusicCast Link'
            }
            sleep_states = {
                0   : 'Off',
                30  : '30 Minutes',
                60  : '60 Minutes',
                90  : '90 Minutes',
                120 : '120 Minutes'
            }
            if cmdString:
                res = self.__UpdateHelper('Power', value, qualifier, cmdString)
                if res:
                    try:
                        self.WriteStatus('Power', power_states[res['power']], qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Power: Invalid/unexpected response'])
                    try:
                        self.WriteStatus('Input', input_states[res['input']], qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Input: Invalid/unexpected response'])
                    try:
                        self.WriteStatus('Mute', states[res['mute']], qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Mute: Invalid/unexpected response'])
                    try:
                        self.WriteStatus('Sleep', sleep_states[res['sleep']], qualifier)
                    except (KeyError, TypeError, IndexError):
                        self.Error(['Sleep: Invalid/unexpected response'])
                    try:
                        self.WriteStatus('Enhancer', states[res['enhancer']], qualifier)
                    except (KeyError, IndexError):
                        self.Error(['Enhancer: Invalid/unexpected response'])
                    try:
                        self.WriteStatus('PureDirect', states[res['pure_direct']], qualifier)
                    except (KeyError, IndexError):
                        self.Error(['PureDirect: Invalid/unexpected response'])
                    try:
                        self.WriteStatus('Volume', res['volume'], qualifier)
                    except (KeyError, ValueError, IndexError):
                        self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Device Is Busy for UpdatePower')

    def SetPresetClear(self, value, qualifier):

        if 1 <= int(value) <= 40:
            self.__SetHelper('PresetClear', value, qualifier, 'netusb/clearPreset?num={}'.format(value))
        else:
            self.Discard('Invalid Command for SetPresetClear')
    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 40 and qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            self.__SetHelper('PresetRecall', value, qualifier, 'netusb/recallPreset?zone={}&num={}'.format(zone, value))
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 40:
            self.__SetHelper('PresetSave', value, qualifier, 'netusb/storePreset?num={}'.format(value))
        else:
            self.Discard('Invalid Command for SetPresetSave')
    def SetPureDirect(self, value, qualifier):

        state = {'On' : 'true', 'Off' : 'false'}[value]
        if qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            self.__SetHelper('PureDirect', value, qualifier, '{}/setPureDirect?enable={}'.format(zone, state))
        else:
            self.Discard('Invalid Command for SetPureDirect')

    def UpdatePureDirect(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetRepeat(self, value, qualifier):

        state = {
            'Off' : 'off"', 
            'One' : 'one"', 
            'All' : 'all"'
        }[value]

        self.__SetHelper('Repeat', value, qualifier, 'netusb/setRepeat?mode={}'.format(state))

    def SetShuffle(self, value, qualifier):

        state = {
            'Off'    : 'off', 
            'On'     : 'on', 
            'Songs'  : 'songs', 
            'Albums' : 'albums'
        }[value]

        self.__SetHelper('Shuffle', value, qualifier, 'netusb/setShuffle?mode={}'.format(state))

    def SetSpeakerPattern(self, value, qualifier):

        state = {
            '1' : '1', 
            '2' : '2'
        }[value]

        self.__SetHelper('SpeakerPattern', value, qualifier, 'system/setSpeakerPattern?num={}'.format(state))

    def UpdateSpeakerPattern(self, value, qualifier):

        state = {
            1 : '1', 
            2 : '2'
        }

        res = self.__UpdateHelper('SpeakerPattern', value, qualifier, 'system/getFuncStatus')
        if res:
            try:
                value = state[res['speaker_pattern']]
                self.WriteStatus('SpeakerPattern', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Speaker Pattern: Invalid/unexpected response'])

    def SetSleep(self, value, qualifier):

        state = {
            'Off'         : '0', 
            '30 Minutes'  : '30', 
            '60 Minutes'  : '60', 
            '90 Minutes'  : '90', 
            '120 Minutes' : '120'
        }[value]

        if qualifier['Zone'] in ['Main', '2']:
            zone = {'Main' : 'main', '2' : 'zone2'}[qualifier['Zone']]
            self.__SetHelper('Sleep', value, qualifier, '{}/setSleep?sleep={}'.format(zone, state))
        else:
            self.Discard('Invalid Command for SetSleep')

    def UpdateSleep(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 161 and qualifier['Zone'] in ['Main', '2']:
            zone = {'Main': 'main', '2': 'zone2'}[qualifier['Zone']]
            CmdString = '{}/setVolume?volume={}'.format(zone,value)
            self.__SetHelper('Volume', value, qualifier, CmdString)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        RESPONSE_CODE = {
            1   : 'Initializing',
            2   : 'Internal Error',
            3   : 'Invalid Request (A method did not exist, a method wasn\'t appropriate etc.)',
            4   : 'Invalid Parameter (Out of range, invalid characters etc.)',
            5   : 'Guarded (Unable to setup in current status etc.)',
            6   : 'Time Out',
            99  : 'Firmware Updating',
            100 : 'Access Error',
            101 : 'Other Errors',
            102 : 'Wrong User Name',
            103 : 'Wrong Password',
            104 : 'Account Expired',
            105 : 'Account Disconnected/Gone Off/Shut Down',
            106 : 'Account Number Reached to the Limit',
            107 : 'Server Maintenance',
            108 : 'Invalid Account',
            109 : 'License Error',
            110 : 'Read Only Mode',
            111 : 'Max Stations',
            112 : 'Access Denied'
        }

        try:
            res = loads(response.read().decode())
            if res['response_code'] in RESPONSE_CODE:
                err = RESPONSE_CODE[res['response_code']]
                self.Error(['Command {}, Error {}'.format(sourceCmdName,err)])
                return ''
            elif res['response_code'] == 0:
                return res
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True
        url = '{}YamahaExtendedControl/v1/{}'.format(self.RootURL ,resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')
        
        try:
            res = self.Opener.open(my_request, timeout=10)           
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

        url = '{}YamahaExtendedControl/v1/{}'.format(self.RootURL, resource)
        headers = {'Content-Type': 'application/json'}    
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)         
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