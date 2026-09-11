from json import loads, dumps
import urllib.error
import urllib.request
import base64

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):

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
            'BassExtension': {'Parameters':['Zone'], 'Status': {}},
            'ClearPreset': { 'Status': {}},
            'Enhancer': {'Parameters':['Zone'], 'Status': {}},
            'Input': {'Parameters':['Zone'], 'Status': {}},
            'Mute': {'Parameters':['Zone'], 'Status': {}},
            'Playback': { 'Status': {}},
            'PlaybackInfo': {'Parameters':['Name'], 'Status': {}},
            'PlaybackTime': {'Parameters':['Time'], 'Status': {}},
            'Power': {'Parameters':['Zone'], 'Status': {}},
            'RecallPreset': {'Parameters':['Zone'], 'Status': {}},
            'PureDirect': {'Parameters':['Zone'], 'Status': {}},
            'Repeat': { 'Status': {}},
            'SavePreset': { 'Status': {}},
            'Shuffle': { 'Status': {}},
            'Sleep': {'Parameters':['Zone'], 'Status': {}},
            'SubwooferVolume': {'Parameters':['Zone'], 'Status': {}},
            'Volume': {'Parameters':['Zone'], 'Status': {}},
        }


        self.main_getStatusTimer = 0
        self.zone2_getStatusTimer = 0
        self.zone3_getStatusTimer = 0
        self.zone4_getStatusTimer = 0


    def SetBassExtension(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        state = {'On':True,'Off':False}[value]
        self.__SetHelper('BassExtension', value, qualifier, '{}/setBassExtension?enable={}'.format(zone, state))

    def UpdateBassExtension(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetEnhancer(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        state = {'On':True,'Off':False}[value]
        self.__SetHelper('Enhancer', value, qualifier, '{}/setEnhancer?enable={}'.format(zone, state))

    def UpdateEnhancer(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetInput(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        state = {
            'Audio'     : 'audio', 
            'Aux'       : 'aux', 
            'Digital'   : 'digital', 
            'Optical'   : 'optical', 
            'Coaxial'   : 'coaxial', 
            'Analog'    : 'analog', 
            'TV'        : 'tv', 
            'USB DAC'   : 'usb_dac', 
            'USB'       : 'usb', 
            'Bluetooth' : 'bluetooth', 
            'Server'    : 'server', 
            'Net Radio' : 'net_radio', 
            'Rhapsody'  : 'rhapsody', 
            'Napster'   : 'napster', 
            'Pandora'   : 'pandora', 
            'SiriusXM'  : 'siriusxm', 
            'Spotify'   : 'spotify', 
            'Juke'      : 'juke', 
            'Airplay'   : 'airplay', 
            'Radiko'    : 'radiko', 
            'Qobuz'     : 'qobuz', 
            'MC Link'   : 'mc_link', 
            'Main Sync' : 'main_sync'
        }[value]

        self.__SetHelper('Input', value, qualifier, '{}/setInput?input={}&mode=autoplay_disabled'.format(zone, state))

    def UpdateInput(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetMute(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        state = {'On':True,'Off':False}[value]
        self.__SetHelper('Mute', value, qualifier, '{}/setMute?enable={}'.format(zone, state))

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
                value = {'play':'Play','stop':'Stop','pause':'Pause','fast_reverse':'Fast Reverse','fast_forward':'Fast Forward'}[res['playback']]
                self.WriteStatus('Playback', value, qualifier)
            except (KeyError, KeyError, IndexError):
                self.Error(['Playback: Invalid/unexpected response'])
            try:
                for name in ['artist','album','track']:
                    self.WriteStatus('PlaybackInfo', res[name], {'Name':name.title()})
            except (TypeError, IndexError):
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


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        state = {'On':'on','Off':'standby'}[value]
        self.__SetHelper('Power', value, qualifier, '{}/setPower?power={}'.format(zone, state))

    def UpdatePower(self, value, qualifier):


        zone = qualifier['Zone']
        cmdString = ''

        if zone == 'Main':
            cmdString = 'main/getStatus'

        elif zone == '2':
            cmdString = 'zone2/getStatus'
                   
        elif zone == '3':
            cmdString = 'zone3/getStatus'
                                 
        elif zone == '4': 
            cmdString = 'zone4/getStatus'

        states = {True:'On', False:'Off'}
        power_states =  {'on':'On', 'standby':'Off'}
        input_states = {
            'audio'     : 'Audio', 
            'aux'       : 'Aux', 
            'digital'   : 'Digital', 
            'optical'   : 'Optical', 
            'coaxial'   : 'Coaxial', 
            'analog'    : 'Analog', 
            'tv'        : 'TV', 
            'usb_dac'   : 'USB DAC', 
            'usb'       : 'USB', 
            'bluetooth' : 'Bluetooth', 
            'server'    : 'Server', 
            'net_radio' : 'Net Radio', 
            'rhapsody'  : 'Rhapsody', 
            'napster'   : 'Napster', 
            'pandora'   : 'Pandora', 
            'siriusxm'  : 'SiriusXM', 
            'spotify'   : 'Spotify', 
            'juke'      : 'Juke', 
            'airplay'   : 'Airplay', 
            'radiko'    : 'Radiko', 
            'qobuz'     : 'Qobuz', 
            'mc_link'   : 'MC Link', 
            'main_sync' : 'Main Sync'
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
                    self.WriteStatus('Sleep', str(res['sleep']), qualifier)
                except (KeyError, TypeError, IndexError, KeyError):
                    self.Error(['Sleep: Invalid/unexpected response'])                
                try:
                    self.WriteStatus('BassExtension', states[res['bass_extension']], qualifier)
                except (KeyError, IndexError):
                    self.Error(['BassExtension: Invalid/unexpected response'])
                try:
                    self.WriteStatus('Enhancer', states[res['enhancer']], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Enhancer: Invalid/unexpected response'])
                try:
                    self.WriteStatus('PureDirect', states[res['pure_direct']], qualifier)
                except (KeyError, IndexError):
                    self.Error(['PureDirect: Invalid/unexpected response'])
                try:
                    self.WriteStatus('SubwooferVolume', res['subwoofer_volume'], qualifier)
                except (KeyError, IndexError):
                    self.Error(['SubwooferVolume: Invalid/unexpected response'])
                try:
                    self.WriteStatus('Volume', res['volume'], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        
        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        if 1 <= int(value) <= 10:
            self.__SetHelper('RecallPreset', value, qualifier, 'netusb/recallPreset?zone={}&num={}'.format(zone, value))
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        
        if 1 <= int(value) <= 10:
            self.__SetHelper('SavePreset', value, qualifier, 'netusb/storePreset?num={}'.format(value))
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def SetClearPreset(self, value, qualifier):

        
        if 1 <= int(value) <= 10:
            self.__SetHelper('ClearPreset', value, qualifier, 'netusb/clearPreset?num={}'.format(value))
        else:
            self.Discard('Invalid Command for SetClearPreset')
    def SetPureDirect(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        state = {'On':True,'Off':False}[value]
        self.__SetHelper('PureDirect', value, qualifier, '{}/setPureDirect?enable={}'.format(zone, state))

    def UpdatePureDirect(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetRepeat(self, value, qualifier):


        self.__SetHelper('Repeat', value, qualifier, 'netusb/toggleRepeat')

    def SetShuffle(self, value, qualifier):


        self.__SetHelper('Shuffle', value, qualifier, 'netusb/toggleShuffle')

    def SetSleep(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        if value in ['0', '30', '60', '90', '120']:
            self.__SetHelper('Sleep', value, qualifier, '{}/setSleep?sleep={}'.format(zone, value))
        else:
            self.Discard('Invalid Command for SetSleep')

    def UpdateSleep(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetSubwooferVolume(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        if 0 <= value <= 100:
            self.__SetHelper('SubwooferVolume', value, qualifier, '{}/setSubwooferVolume?volume={}'.format(zone, value))
        else:
            self.Discard('Invalid Command for SetSubwooferVolume')

    def UpdateSubwooferVolume(self, value, qualifier):


        self.UpdatePower(value, qualifier)

    def SetVolume(self, value, qualifier):


        zone = {'Main':'main','2':'zone2','3':'zone3','4':'zone4'}[qualifier['Zone']]
        if 0 <= value <= 100:
            self.__SetHelper('Volume', value, qualifier, '{}/setVolume?volume={}'.format(zone, value))
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
        myRequest = urllib.request.Request(url, data=data, headers=headers, method='GET')


        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()


        try:
            res = self.Opener.open(myRequest, timeout=1)
        except urllib.error.HTTPError as err:

            print('{0} {1} - {2}'.format(command, err.code, err.reason))

            res = ''

        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''

        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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

        
        self.main_getStatusTimer = 0
        self.zone2_getStatusTimer = 0
        self.zone3_getStatusTimer = 0
        self.zone4_getStatusTimer = 0

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
            print(command, 'does not exist in the module')

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