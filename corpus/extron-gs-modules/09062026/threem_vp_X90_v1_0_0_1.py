from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': {'Parameters':['Input'], 'Status': {}},
            'VolumeStatus': {'Parameters':['Input'], 'Status': {}},
            }

        self.Authentication = True
            
        self.regex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|[a-fA-F0-9]{8})')
        
        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)
            
    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            inStr = value.decode()
            outStr = inStr + self.devicePassword
            m = hashlib.md5(outStr.encode())
            cmdString = hexlify(m.digest())+b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
            self.Send(cmdString)
        else:
            self.Error(['Password is Missing'])

    def __MatchPassword(self, match, tag):
        self.Authentication = True
        self.SetPassword( match.group(1), None)
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'    : b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00', 
            '16:9'   : b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00', 
            '14:9'   : b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00', 
            'Small'  : b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00', 
            'Normal' : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00 : '4:3', 
            0x01 : '16:9', 
            0x09 : '14:9', 
            0x0A : 'Small', 
            0x10 : 'Normal'
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Normal', 
            0x01 : 'Cover Error', 
            0x02 : 'Fan Error', 
            0x03 : 'Lamp Error', 
            0x04 : 'Temp Error', 
            0x05 : 'Air Flow Error', 
            0x06 : 'Lamp Time Error', 
            0x07 : 'Cold Error', 
            0x08 : 'Filter Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = res[1]*256 + res[2]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1'      : b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00', 
            'RGB 2'      : b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00', 
            'Component'  : b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00', 
            'S-Video'    : b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00', 
            'Video'      : b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00', 
            'M1-Digital' : b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'RGB 1', 
            0x04 : 'RGB 2', 
            0x05 : 'Component', 
            0x02 : 'S-Video', 
            0x01 : 'Video', 
            0x03 : 'M1-Digital'
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00', 
            'Eco'    : b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Normal', 
            0x01 : 'Eco'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = res[1]*256 + res[2]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'       : b'\xBE\xEF\x03\x06\x00\x23\xF6\x01\x00\xBA\x30\x00\x00', 
            'Cinema'       : b'\xBE\xEF\x03\x06\x00\xB3\xF7\x01\x00\xBA\x30\x01\x00', 
            'Dynamic'      : b'\xBE\xEF\x03\x06\x00\xE3\xF4\x01\x00\xBA\x30\x04\x00', 
            'Board(Black)' : b'\xBE\xEF\x03\x06\x00\xE3\xEF\x01\x00\xBA\x30\x20\x00', 
            'Board(Green)' : b'\xBE\xEF\x03\x06\x00\x73\xEE\x01\x00\xBA\x30\x21\x00', 
            'Whiteboard'   : b'\xBE\xEF\x03\x06\x00\x83\xEE\x01\x00\xBA\x30\x22\x00' 
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Normal', 
            0x01 : 'Cinema', 
            0x04 : 'Dynamic', 
            0x20 : 'Board(Black)', 
            0x21 : 'Board(Green)', 
            0x22 : 'Whiteboard', 
            0x10 : 'Custom'
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  :  b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off', 
            0x02 : 'Cooling Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00', 
            'Off' : b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        InputStateIncrement = {
            'RGB 1'         : b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'RGB 2'         : b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Component'     : b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'S-Video'       : b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'M1-Digital'    : b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00'
            }

        InputStateDecrement = {
            'RGB 1'         : b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'RGB 2'         : b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00',
            'Component'     : b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00',
            'S-Video'       : b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00',
            'Video'         : b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
            'M1-Digital'    : b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
            }

        if value == 'Up':
            VolumeCmdString = InputStateIncrement[qualifier['Input']]
        elif value == 'Down':
            VolumeCmdString = InputStateDecrement[qualifier['Input']]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        
    def UpdateVolumeStatus(self, value, qualifier):

        InputValues = {
            'RGB 1'      : b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',   
            'RGB 2'      : b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',   
            'Component'  : b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'Video'      : b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',   
            'S-Video'    : b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',   
            'M1-Digital' : b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00'      
        }
        
        VolumeStatusCmdString = InputValues[qualifier['Input']]
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[1]
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
        b'\x15'   : 'Invalid Command Reply.',
        b'\x1C'   : 'Cannot Execute Command.',
        b'\x1F'   : 'Autentication Error.'          
        }   
        
        if response:
            if len(response) == 8:
                self.SetPassword( response, None)
                response = ''
            elif response[0:1] in DEVICE_ERROR_CODES:
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
                if response[0:1] == b'\x1F':
                    self.Authentication = False
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authentication == True or 'Serial' in self.ConnectionType:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.regex)
                return self.__CheckResponseForErrors(command, res)           

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authentication = False
                
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
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

