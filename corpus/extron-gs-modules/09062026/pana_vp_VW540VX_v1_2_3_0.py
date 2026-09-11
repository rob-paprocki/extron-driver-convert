from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify

class DeviceEthernetClass:
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
        self.deviceUsername = None
        self.devicePassword = 'panasonic'
        self.Models = {
            'PT-VZ580': self.pana_1_3112_0,
            'PT-VW540': self.pana_1_3112_0,
            'PT-VX610': self.pana_1_3112_0,
            'PT-VZ585N': self.pana_1_3112_N,
            'PT-VX615N': self.pana_1_3112_N,
            'PT-VW545N': self.pana_1_3112_N,
            'PT-VW545NE': self.pana_1_3112_N,
            'PT-VZ585NU': self.pana_1_3112_N,
            'PT-VZ580D': self.pana_1_3112_0,
            'PT-VW540D': self.pana_1_3112_0,
            'PT-VX610D': self.pana_1_3112_0,
            'PT-VZ580T': self.pana_1_3112_0,
            'PT-VW540T': self.pana_1_3112_0,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
        }

        self.Authenticated = 'Not Needed'
        self.StartQuery = False
        self.md5hash = ''

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)

    def __MatchPassword(self, match, tag):

        inStr = match.group(1).decode()
        outStr = inStr + self.devicePassword
        encrypted = hashlib.md5(outStr.encode()) 
        self.md5hash = hexlify(encrypted.digest())
        self.Authenticated = 'Admin'
        self.StartQuery = True

    def __MatchNoAuthentication(self, match, tag):

        self.Authenticated = 'Not Needed'
        self.StartQuery = True

    def md5HashBuilder(self, commandstring):

        if self.Authenticated == 'Admin':
            commandstring = self.md5hash + commandstring.encode()
        return commandstring

    def SetAVMute(self, value, qualifier):

        States = {
            'On'  : '%1AVMT 31\r', 
            'Off' : '%1AVMT 30\r'
        }

        self.__SetHelper('AVMute', self.md5HashBuilder(States[value]) , value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        States = {
            '31' : 'On', 
            '30' : 'Off'
        }

        res = self.__UpdateHelper('AVMute', self.md5HashBuilder('%1AVMT ?\r') , value, qualifier)
        if res:
            try:
                self.WriteStatus('AVMute',  States[res[7:-1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/Unexpected Response'])

    def UpdateDeviceStatus(self, value, qualifier):

        States = {
            0 : 'Fan', 
            1 : 'Lamp', 
            2 : 'Temperature', 
            4 : 'Filter',
            5 : 'Other'
        }

        res = self.__UpdateHelper('DeviceStatus', self.md5HashBuilder('%1ERST ?\r') , value, qualifier)
        if res:
            try:
                status = res[7:-1]
                if status.count('0') == 6:
                    value = 'Normal'
                elif status.count('1') + status.count('2') > 2:
                    value = 'Multiple Warnings / Errors'
                elif status.count('1') == 1:
                    index = status.index('1')
                    value = '{0} Warning'.format(States[index])
                elif status.count('2') == 1:
                    index = status.index('2')
                    value = '{0} Error'.format(States[index])
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        self.__SetHelper('Input', self.md5HashBuilder(self.Inputs[value]) , value, qualifier)

    def UpdateInput(self, value, qualifier):

        res = self.__UpdateHelper('Input', self.md5HashBuilder('%1INPT ?\r') , value, qualifier)
        if res:
            try:
                self.WriteStatus('Input',  self.InputStates[res[7:-1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', self.md5HashBuilder('%1LAMP ?\r') , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage',  int(res[7:-3]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        States = {
            'On'  : '%1POWR 1\r', 
            'Off' : '%1POWR 0\r', 
        }

        self.__SetHelper('Power', self.md5HashBuilder(States[value]) , value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off', 
            '2' : 'Cooling Down', 
            '3' : 'Warming Up'
        }

        res = self.__UpdateHelper('Power', self.md5HashBuilder('%1POWR ?\r') , value, qualifier)
        if res:
            try:
                self.WriteStatus('Power',  States[res[-2]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'ERR1' : "Undefined command.",
            'ERR2' : "Out of parameter.",
            'ERR3' : "Unavailable time.",
            'ERR4' : "Projector failure.",
            'ERRA' : "Invalid password."
        }

        if isinstance(response, bytes):
            response = response.decode()
        if 'ERR' in response:
            self.Error([sourceCmdName + ' ' + DEVICE_ERROR_CODES[response[7:-1]]])
            if 'ERRA' in response:
                self.StartQuery = False
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.StartQuery:
            if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                if isinstance(res, bytes):
                    res = res.decode()
                if not res:
                    self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command')
            return ''

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.StartQuery:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)
            return''

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Required'
        self.StartQuery = False
        self.md5hash = ''

    def pana_1_3112_N(self):

        self.Inputs = {
            'Computer 1'            : '%1INPT 11\r', 
            'Computer 2'            : '%1INPT 12\r', 
            'Video'                 : '%1INPT 21\r', 
            'HDMI 1'                : '%1INPT 31\r', 
            'HDMI 2'                : '%1INPT 32\r',
            'Digital Link'          : '%1INPT 33\r',
            'Memory Viewer'         : '%1INPT 41\r', 
            'Panasonic Application' : '%1INPT 51\r', 
            'Miracast'              : '%1INPT 52\r',           
        }

        self.InputStates = {
            '11' : 'Computer 1',
            '12' : 'Computer 2',
            '21' : 'Video',
            '31' : 'HDMI 1',
            '32' : 'HDMI 2',
            '33' : 'Digital Link',
            '41' : 'Memory Viewer',
            '51' : 'Panasonic Application',
            '52' : 'Miracast',
        }

    def pana_1_3112_0(self):

        self.Inputs = {
            'Computer 1'            : '%1INPT 11\r', 
            'Computer 2'            : '%1INPT 12\r', 
            'Video'                 : '%1INPT 21\r', 
            'HDMI 1'                : '%1INPT 31\r', 
            'HDMI 2'                : '%1INPT 32\r',        
        }

        self.InputStates = {
            '11' : 'Computer 1',
            '12' : 'Computer 2',
            '21' : 'Video',
            '31' : 'HDMI 1',
            '32' : 'HDMI 2',
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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


class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'PT-VZ580': self.pana_1_3112_0,
            'PT-VW540': self.pana_1_3112_0,
            'PT-VX610': self.pana_1_3112_0,
            'PT-VZ585N': self.pana_1_3112_N,
            'PT-VX615N': self.pana_1_3112_N,
            'PT-VW545N': self.pana_1_3112_N,
            'PT-VW545NE': self.pana_1_3112_N,
            'PT-VZ585NU': self.pana_1_3112_N,
            'PT-VZ580D': self.pana_1_3112_0,
            'PT-VW540D': self.pana_1_3112_0,
            'PT-VX610D': self.pana_1_3112_0,
            'PT-VZ580T': self.pana_1_3112_0,
            'PT-VW540T': self.pana_1_3112_0,
            'PT-VX610T': self.pana_1_3112_0,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Auto'   : '\x02VSE:00\x03', 
            'Normal' : '\x02VSE:01\x03', 
            'Wide'   : '\x02VSE:02\x03', 
            'Native' : '\x02VSE:05\x03', 
            'Full'   : '\x02VSE:06\x03', 
            'H-Fit'  : '\x02VSE:09\x03', 
            'V-Fit'  : '\x02VSE:10\x03'
        }

        self.__SetHelper('AspectRatio', States[value] , value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            '0' : 'Auto', 
            '1' : 'Normal', 
            '2' : 'Wide', 
            '5' : 'Native', 
            '6' : 'Full', 
            '9' : 'H-Fit', 
            '10': 'V-Fit'
        }  

        res = self.__UpdateHelper('AspectRatio', '\x02QS1\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio',  States[res[1:-1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : '\x02AMT:1\x03', 
            'Off' : '\x02AMT:0\x03'
        }

        self.__SetHelper('AudioMute', States[value] , value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }       

        res = self.__UpdateHelper('AudioMute', '\x02QMT\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '\x02OAS\x03' , value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        States = {
            'Off' : '\x02OCC:0\x03', 
            'CC1' : '\x02OCC:1\x03', 
            'CC2' : '\x02OCC:2\x03', 
            'CC3' : '\x02OCC:3\x03', 
            'CC4' : '\x02OCC:4\x03'
        }

        self.__SetHelper('ClosedCaption', States[value] , value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        States = {
            '0' : 'Off', 
            '1' : 'CC1', 
            '2' : 'CC2', 
            '3' : 'CC3', 
            '4' : 'CC4'
        }

        res = self.__UpdateHelper('ClosedCaption', '\x02QCC\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaption',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption : Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', '\x02QFI:0\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage',  int(res[1:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage : Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        States = {
            'On'  : '\x02OFZ:1\x03', 
            'Off' : '\x02OFZ:0\x03'
        }

        self.__SetHelper('Freeze', States[value] , value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }   

        res = self.__UpdateHelper('Freeze', '\x02QFZ\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        self.__SetHelper('Input', self.Inputs[value] , value, qualifier)

    def UpdateInput(self, value, qualifier):
            
        res = self.__UpdateHelper('Input', '\x02QIN\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Input',  self.InputStates[res[1:4]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal' : '\x02OLP:1\x03', 
            'Eco 1'  : '\x02OLP:3\x03',
            'Eco 2'  : '\x02OLP:4\x03'
        }

        self.__SetHelper('LampMode', States[value] , value, qualifier)

    def UpdateLampMode(self, value, qualifier):
            
        States = {
            '1' : 'Normal', 
            '3' : 'Eco 1',
            '4' : 'Eco 2',
        }

        res = self.__UpdateHelper('LampMode', '\x02QLP\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode : Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', '\x02Q$L\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage',  int(res[1:5]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage : Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu'  : '\x02OMN\x03', 
            'Enter' : '\x02OEN\x03', 
            'Up'    : '\x02OCU\x03', 
            'Down'  : '\x02OCD\x03', 
            'Left'  : '\x02OCL\x03', 
            'Right' : '\x02OCR\x03',
            'Return': '\x02OBK\x03'
        }

        self.__SetHelper('MenuNavigation', States[value] , value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', '\x02QVX:RTMI0\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('OperationHours',  int(res[8:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours : Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        States = {
            'Dynamic'    : '\x02VPM:DYN\x03', 
            'Natural'    : '\x02VPM:NAT\x03', 
            'Standard'   : '\x02VPM:STD\x03', 
            'Blackboard' : '\x02VPM:BBD\x03', 
            'Cinema'     : '\x02VPM:CIN\x03', 
            'Whiteboard' : '\x02VPM:WBD\x03'
        }

        self.__SetHelper('PictureMode', States[value] , value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        
        States = {
            'DYN' : 'Dynamic', 
            'NAT' : 'Natural', 
            'STD' : 'Standard', 
            'BBD' : 'Blackboard', 
            'CIN' : 'Cinema', 
            'WBD' : 'Whiteboard'
        }

        res = self.__UpdateHelper('PictureMode', '\x02QPM\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureMode',  States[res[1:4]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode : Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On'  : '\x02PON\x03', 
            'Off' : '\x02POF\x03', 
        }

        self.__SetHelper('Power', States[value] , value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            '2' : 'On', 
            '0' : 'Off', 
            '1' : 'Warming Up', 
            '3' : 'Cooling Down'
        }

        res = self.__UpdateHelper('Power', '\x02Q$S\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Power',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/unexpected response'])   

    def SetVideoMute(self, value, qualifier):

        States = {
            'On' : '\x02OSH:1\x03', 
            'Off' : '\x02OSH:0\x03'
        }

        self.__SetHelper('VideoMute', States[value] , value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        res = self.__UpdateHelper('VideoMute', '\x02QSH\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            self.__SetHelper('Volume', '\x02AVL:{0:03d}\x03'.format(value) , value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        
        res = self.__UpdateHelper('Volume', '\x02QAV\x03' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume',  int(res[1:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': "Invalid Command Reply.",
            '\x02ER402\x03': "Invalid Parameter."
        }

        response = response.decode()                                
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
            return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_1_3112_N(self):

        self.Inputs = {
            'Computer 1'            : '\x02IIS:RG1\x03', 
            'Computer 2'            : '\x02IIS:RG2\x03', 
            'Video'                 : '\x02IIS:VID\x03', 
            'HDMI 1'                : '\x02IIS:HD1\x03', 
            'HDMI 2'                : '\x02IIS:HD2\x03',
            'Network/USB'           : '\x02IIS:NWP\x03', 
            'Panasonic Application' : '\x02IIS:PA1\x03', 
            'Miracast'              : '\x02IIS:MC1\x03', 
            'Memory Viewer'         : '\x02IIS:MV1\x03', 
            'Digital Link'          : '\x02IIS:DL1\x03'
            
        }

        self.InputStates = {
            'RG1' : 'Computer 1', 
            'RG2' : 'Computer 2', 
            'VID' : 'Video', 
            'HD1' : 'HDMI 1', 
            'HD2' : 'HDMI 2',
            'NWP' : 'Network/USB', 
            'PA1' : 'Panasonic Application', 
            'MC1' : 'Miracast', 
            'MV1' : 'Memory Viewer', 
            'DL1' : 'Digital Link'
            
        }

    def pana_1_3112_0(self):

        self.Inputs = {
            'Computer 1' : '\x02IIS:RG1\x03', 
            'Computer 2' : '\x02IIS:RG2\x03', 
            'Video'      : '\x02IIS:VID\x03', 
            'HDMI 1'     : '\x02IIS:HD1\x03', 
            'HDMI 2'     : '\x02IIS:HD2\x03'
        }
        self.InputStates = {
            'RG1' : 'Computer 1', 
            'RG2' : 'Computer 2', 
            'VID' : 'Video', 
            'HD1' : 'HDMI 1', 
            'HD2' : 'HDMI 2'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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