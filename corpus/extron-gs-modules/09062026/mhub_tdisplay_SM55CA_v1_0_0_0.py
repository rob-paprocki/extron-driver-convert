from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
from json import loads, dumps
import hashlib
import time


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMuteStatus': {'Status': {}},
            'VideoMuteToggle': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x01(\x00|\x01)[\x83-\x84]\xDD\xEE\xFF'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x81(\x03|\x06|\x07|\x02|\x08|\x0A|\x0E|\x11)\x00[\x83-\x92]\xDD\xEE\xFF'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x83([\x00-\x03])\x00[\x83-\x86]\xDD\xEE\xFF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x80(\x00|\x01)\x00[\x80-\x81]\xDD\xEE\xFF'), self.__MatchVideoMuteStatus, None)
            self.AddMatchString(re.compile(b'\xAA\xBB\xCC\x82\x00([\x00-\x64])[\x82-\xE6]\xDD\xEE\xFF'), self.__MatchVolume, None)

    

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x03\x01\x00\x04\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x03\x01\x01\x05\xDD\xEE\xFF'
        }
        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xAA\xBB\xCC\x03\x03\x00\x06\xDD\xEE\xFF'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            0: 'On',
            1: 'Off'
        }

        value = ValueStateValues[match.group(1)[0]]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\xAA\xBB\xCC\x02\x03\x00\x05\xDD\xEE\xFF',
            'HDMI 1': b'\xAA\xBB\xCC\x02\x06\x00\x08\xDD\xEE\xFF',
            'HDMI 2': b'\xAA\xBB\xCC\x02\x07\x00\x09\xDD\xEE\xFF',
            'PC': b'\xAA\xBB\xCC\x02\x08\x00\x0A\xDD\xEE\xFF',
            'Android': b'\xAA\xBB\xCC\x02\x0A\x00\x0C\xDD\xEE\xFF'
        }
        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xAA\xBB\xCC\x02\x00\x00\x02\xDD\xEE\xFF'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            0x03: 'VGA',
            0x06: 'HDMI 1',
            0x07: 'HDMI 2',
            0x08: 'PC',
            0x0A: 'Android'
        }

        value = ValueStateValues[match.group(1)[0]]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xAA\xBB\xCC\x07\x1B\x00\x22\xDD\xEE\xFF',
            '1': b'\xAA\xBB\xCC\x07\x00\x00\x07\xDD\xEE\xFF',
            '2': b'\xAA\xBB\xCC\x07\x10\x00\x17\xDD\xEE\xFF',
            '3': b'\xAA\xBB\xCC\x07\x11\x00\x18\xDD\xEE\xFF',
            '4': b'\xAA\xBB\xCC\x07\x13\x00\x1A\xDD\xEE\xFF',
            '5': b'\xAA\xBB\xCC\x07\x14\x00\x1B\xDD\xEE\xFF',
            '6': b'\xAA\xBB\xCC\x07\x15\x00\x1C\xDD\xEE\xFF',
            '7': b'\xAA\xBB\xCC\x07\x17\x00\x1E\xDD\xEE\xFF',
            '8': b'\xAA\xBB\xCC\x07\x18\x00\x1F\xDD\xEE\xFF',
            '9': b'\xAA\xBB\xCC\x07\x19\x00\x20\xDD\xEE\xFF'
        }
        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home': b'\xAA\xBB\xCC\x07\x48\x00\x4F\xDD\xEE\xFF',
            'Up': b'\xAA\xBB\xCC\x07\x47\x00\x4E\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x4D\x00\x54\xDD\xEE\xFF',
            'Left': b'\xAA\xBB\xCC\x07\x49\x00\x50\xDD\xEE\xFF',
            'Right': b'\xAA\xBB\xCC\x07\x4B\x00\x52\xDD\xEE\xFF',
            'Enter': b'\xAA\xBB\xCC\x07\x4A\x00\x51\xDD\xEE\xFF',
            'Back': b'\xAA\xBB\xCC\x07\x0A\x00\x11\xDD\xEE\xFF',
            'Page Up': b'\xAA\xBB\xCC\x07\x42\x00\x49\xDD\xEE\xFF',
            'Page Down': b'\xAA\xBB\xCC\x07\x0F\x00\x16\xDD\xEE\xFF',
            'Backspace': b'\xAA\xBB\xCC\x07\x40\x00\x47\xDD\xEE\xFF'
        }
        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x01\x00\x00\x01\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x01\x01\x00\x02\xDD\xEE\xFF'
        }
        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xAA\xBB\xCC\x09\x02\x00\x0B\xDD\xEE\xFF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            0: 'On',
            1: 'Off',
            2: 'Sleep',
            3: 'Hibernate'
        }

        value = ValueStateValues[match.group(1)[0]]
        self.WriteStatus('Power', value, None)

    def UpdateVideoMuteStatus(self, value, qualifier):

        VideoMuteStatusCmdString = b'\xAA\xBB\xCC\x01\x02\x00\x03\xDD\xEE\xFF'
        self.__UpdateHelper('VideoMuteStatus', VideoMuteStatusCmdString, value, qualifier)

    def __MatchVideoMuteStatus(self, match, tag):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        value = ValueStateValues[match.group(1)[0]]
        self.WriteStatus('VideoMuteStatus', value, None)

    def SetVideoMuteToggle(self, value, qualifier):

        VideoMuteToggleCmdString = b'\xAA\xBB\xCC\x07\x4E\x00\x55\xDD\xEE\xFF'
        self.__SetHelper('VideoMuteToggle', VideoMuteToggleCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = b'\xAA\xBB\xCC\x03\x00' + bytes([value, value + 3]) + b'\xDD\xEE\xFF'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xAA\xBB\xCC\x03\x02\x00\x05\xDD\xEE\xFF'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1)[0])
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:               
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}



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

class DeviceHTTPClass:
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

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._MagicCode = 'd342530a6304cfd7'
        self._SerialNumber = ''
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': { 'Status': {}},
            'Home': { 'Status': {}},
            'Input': { 'Status': {}},
            'ModelName': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.CurrentTimeStamp = 0
        self.Token = None

    @property
    def MagicCode(self):
        return self._MagicCode

    @MagicCode.setter
    def MagicCode(self, value):
        self._MagicCode= value

    @property
    def SerialNumber(self):
        return self._SerialNumber

    @SerialNumber.setter
    def SerialNumber(self, value):
        self._SerialNumber= value

    def generateToken(self):
        self.CurrentTimeStamp = str(int(time.monotonic()))
        tokenString = self.SerialNumber + self.CurrentTimeStamp + self.MagicCode
        self.Token = hashlib.md5(tokenString.encode('utf-8')).hexdigest()

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            BrightnessCmdString = '/brightness'
            jsonData = dumps(
                        {'brightness':value/100}
                        )
            self.__SetHelper('Brightness', value, qualifier, BrightnessCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = '/brightness?token={}&ts={}'.format(self.Token, self.CurrentTimeStamp)
        res = self.__UpdateHelper('Brightness', value, qualifier, BrightnessCmdString)
        if res:
            try:
                value = float(res['brightness'])*100
                self.WriteStatus('Brightness', int(value), qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetHome(self, value, qualifier):


        HomeCmdString = '/input'
        jsonData = dumps(
                    {'input_id':0}
                    )
        self.__SetHelper('Home', value, qualifier, HomeCmdString, jsonData.encode())
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'        : 2, 
            'HDMI 2'        : 3, 
            'PC'            : 4,
            'Android'       : 5,
            'VGA'           : 6
        }
        if value in ValueStateValues:
            InputCmdString = '/input'
            jsonData = dumps(
                        {'input_id':ValueStateValues[value]}
                        )
            self.__SetHelper('Input', value, qualifier, InputCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            2 : 'HDMI 1',
            3 : 'HDMI 2',
            4 : 'PC',
            5 : 'Android',
            6 : 'VGA'
        }

        InputCmdString = '/input?token={}&ts={}'.format(self.Token, self.CurrentTimeStamp)
        res = self.__UpdateHelper('Input', value, qualifier, InputCmdString)
        if res:
            try:
                value = ValueStateValues[int(res['current_input_id'])]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateModelName(self, value, qualifier):

        ModelNameCmdString = '/infomations?token={}&ts={}'.format(self.Token, self.CurrentTimeStamp)
        res = self.__UpdateHelper('ModelName', value, qualifier, ModelNameCmdString)
        if res:
            try:
                value = res['model']
                self.WriteStatus('ModelName', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Model Name: Invalid/unexpected response'])
            
    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '/shutdown'
        self.__SetHelper('PowerOff', value, qualifier, PowerOffCmdString)
    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'false', 
            'Off' : 'true'
        }
        if value in ValueStateValues:
            VideoMuteCmdString = '/screen'
            jsonData = dumps(
                        {'state':ValueStateValues[value]}
                        )
            self.__SetHelper('VideoMute', value, qualifier, VideoMuteCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            False   : 'On', 
            True    : 'Off'
        }

        VideoMuteCmdString = '/screen?token={}&ts={}'.format(self.Token, self.CurrentTimeStamp)
        res = self.__UpdateHelper('VideoMute', value, qualifier, VideoMuteCmdString)
        if res:
            try:
                value = ValueStateValues[res['state']]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Screen Mute: Invalid/unexpected response'])
            
    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:        
            VolumeCmdString = '/volume'
            jsonData = dumps(
                        {'volume':value/100}
                        )
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString, jsonData.encode())
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '/volume?token={}&ts={}'.format(self.Token, self.CurrentTimeStamp)
        res = self.__UpdateHelper('Volume', value, qualifier, VolumeCmdString)
        if res:
            try:
                value = float(res['volume'])*100
                self.WriteStatus('Volume', int(value), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])
            
    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = loads(response.read().decode())
        except:
            self.Error(['Invalid Response'])
            response = ''
        return response
 
    def __SetHelper(self, command, value, qualifier, resource, data=None):

        self.Debug = True
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {
                    'Content-Type': 'application/json',
                    'token': self.Token,
                    'ts': self.CurrentTimeStamp
                  }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, headers=headers) #method defaults to GET when data is None

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.generateToken()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.CurrentTimeStamp = 0
        self.Token = None

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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
