from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, I, search, findall
from extronlib.system import Wait, ProgramLog
import hashlib
from binascii import hexlify

class DeviceSerialClass:    
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampHours': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'VolumeStatus': { 'Status': {}},
            }
               
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*ASP=(4:3|16:9|16:10|AUTO|REAL)#', I), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'\*MUTE=(ON|OFF)#', I), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'\*FREEZE=(ON|OFF)#', I), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'\*SOUR=(RGB|RGB2|HDMI|VID|SVID|NETWORK)#', I), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*LTIM=(\d+)#', I), self.__MatchLampHours, None)
            self.AddMatchString(compile(b'\*LAMPM=(LNOR|ECO|SECO)#', I), self.__MatchLampMode, None)
            self.AddMatchString(compile(b'\*APPMOD=(PRESET|SRGB|DYNAMIC|CINE|USER1|USER2)#', I), self.__MatchPictureMode, None)
            self.AddMatchString(compile(b'\*POW=(ON|OFF)#', I), self.__MatchPower, None)
            self.AddMatchString(compile(b'\*BLANK=(ON|OFF)#', I), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'\*VOL=([0-9]{1,2})#', I), self.__MatchVolumeStatus, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = ['4:3', '16:9', '16:10', 'Auto', 'Real']
        if value in ValueStateValues:
            AspectRatioCmdString = '\r*asp={}#\r'.format(value.upper())
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10',
            'AUTO': 'Auto',
            'REAL': 'Real'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = ['On', 'Off']

        if value in ValueStateValues:
            AudioMuteCmdString = '\r*mute={}#\r'.format(value.lower())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\r*mute=?#\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = ['On', 'Off']

        if value in ValueStateValues:
            FreezeCmdString = '\r*freeze={}#\r'.format(value.lower())
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '\r*freeze=?#\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1': 'RGB',
            'Computer 2': 'RGB2',
            'S-Video': 'svid',
            'Video': 'vid',
            'HDMI': 'hdmi',
            'Network': 'network'
        }

        if value in ValueStateValues:
            InputCmdString = '\r*sour={}#\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'RGB': 'Computer 1',
            'RGB2': 'Computer 2',
            'SVID': 'S-Video',
            'VID': 'Video',
            'HDMI': 'HDMI',
            'NETWORK': 'Network'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Input', value, None)

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = '\r*ltim=?#\r'
        self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)

    def __MatchLampHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampHours', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'lnor',
            'Economic': 'eco',
            'SmartEco': 'seco'
        }

        if value in ValueStateValues:
            LampModeCmdString = '\r*lampm={}#\r'.format(ValueStateValues[value])
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            'LNOR': 'Normal',
            'ECO': 'Economic',
            'SECO': 'SmartEco'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('LampMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu On': 'menu=on',
            'Menu Off': 'menu=off',
            'Up': 'up',
            'Down': 'down',
            'Right': 'right',
            'Left': 'left',
            'Enter': 'enter'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = '\r*{}#\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': 'preset',
            'sRGB': 'srgb',
            'Dynamic': 'dynamic',
            'Cinema': 'cine',
            'User 1': 'user1',
            'User 2': 'user2',
        }

        if value in ValueStateValues:
            PictureModeCmdString = '\r*appmod={}#\r'.format(ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\r*appmod=?#\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'PRESET': 'Presentation',
            'SRGB': 'sRGB',
            'DYNAMIC': 'Dynamic',
            'CINE': 'Cinema',
            'USER1': 'User 1',
            'USER2': 'User 2',
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = ['On', 'Off']

        if value in ValueStateValues:
            PowerCmdString = '\r*pow={}#\r'.format(value.lower())
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off',
        }


        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = ['On', 'Off']

        if value in ValueStateValues:
            VideoMuteCmdString = '\r*blank={}#\r'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '+',
            'Down': '-'
        }

        if value in ValueStateValues:
            VolumeCmdString = '\r*vol={}#\r'.format(ValueStateValues[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = '\r*vol=?#\r'
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VolumeStatus', value, None)

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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class DeviceEthernetClass:    
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}        
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': { 'Status': {}},
            'ErrorStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampHours': { 'Status': {}},
            'Power': { 'Status': {}},
        }

        self.Authenticated = 'Not Needed'
        self.AVMuteMatchString = compile('%1AVMT=([1-3][0-1])\r')
        self.ErrorStatusMatchString = compile('%1ERST=([0-3]{6})\r')
        self.InputMatchString = compile('%1INPT=([0-9]{2})\r')
        self.LampHoursMatchString = compile('%1LAMP=([0-9]{1,5})\r')
        self.PowerMatchString = compile('%1POWR=([0-3])\r')
        self.ErrorMatchString = compile('ERR([1234A])')
        self.PasswordMatchString = compile('PJLINK 1 ([a-f0-9]{8})\r')

    def SetAVMute(self, value, qualifier):

        AVMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        AVMuteQualifierValues = {
            'Audio': '2',
            'Video': '1',
            'Audio/Video': '3'
        }
        AVMuteCmdString = '%1AVMT {0}{1}\r'.format(AVMuteQualifierValues[qualifier['Type']], AVMuteStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
    def UpdateAVMute(self, value, qualifier):

        AVMuteStateNames = {
            '11': {'Audio': 'Off', 'Video': 'On',  'Audio/Video': 'Off'},
            '21': {'Audio': 'On',  'Video': 'Off', 'Audio/Video': 'Off'},
            '31': {'Audio': 'On',  'Video': 'On',  'Audio/Video': 'On'},
            '30': {'Audio': 'Off', 'Video': 'Off', 'Audio/Video': 'Off'}
        }
        AVMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res != '':
            try:
                matchObject = search(self.AVMuteMatchString, res)
                if matchObject is not None:
                    AVMuteValues = AVMuteStateNames[matchObject.group(1)]
                    for Type in ['Audio', 'Video', 'Audio/Video']:
                        qualifier = {'Type': Type}
                        value = AVMuteValues[Type]
                        self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateErrorStatus(self, value, qualifier):

        ErrorWarningNames = {
            1: 'Fan',
            2: 'Lamp',
            3: 'Temp',
            4: 'Cover',
            5: 'Filter',
            6: 'Other'
        }
        ErrorStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('ErrorStatus', ErrorStatusCmdString, value, qualifier)
        if res != '':
            try:
                matchObject = search(self.ErrorStatusMatchString, res)
                if matchObject is not None:
                    ErrorStrings = matchObject.group(1)
                    if ErrorStrings.count('1') + ErrorStrings.count('2') == 0:
                        value = 'Normal'
                    if ErrorStrings.count('1') + ErrorStrings.count('2') > 2:
                        value = 'Multiple Errors/Warnings'
                    elif ErrorStrings.count('1') == 1:
                        index = ErrorStrings.index('1')
                        value = '{0} Warning'.format(ErrorWarningNames[index+1])
                    elif ErrorStrings.count('2') == 1:
                        index = ErrorStrings.index('2')
                        value = '{0} Error'.format(ErrorWarningNames[index+1])
                    self.WriteStatus('ErrorStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': '11',
            'VGA 2': '12',
            'S-Video': '21',
            'CVBS': '22',
            'HDMI': '31',
            'Card Reader': '51',
            'LAN Display': '52',
            'USB Display': '53'
        }

        InputCmdString = '%1INPT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11': 'VGA 1',
            '12': 'VGA 2',
            '21': 'S-Video',
            '22': 'CVBS',
            '31': 'HDMI',
            '51': 'Card Reader',
            '52': 'LAN Display',
            '53': 'USB Display'
        }
        InputCmdString = '%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = search(self.InputMatchString, res)
                if matchObject is not None:
                    value = ValueStateValues[matchObject.group(1)]
                    self.WriteStatus('Input', value, None)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = '%1LAMP ?\r'
        res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        if res != '':
            try:
                matchList = findall(self.LampHoursMatchString, res)
                if matchList != []:
                    for lamp in matchList:
                        value = int(lamp)
                        self.WriteStatus('LampHours', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '1',
            'Off': '0'
        }
        PowerCmdString = '%1POWR {0}\r'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '1': 'On',
            '2': 'Cooling Down',
            '3': 'Warming Up',
            '0': 'Off'
        }
        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res != '':
            try:
                matchObject = search(self.PowerMatchString, res)
                if matchObject is not None:
                    value = PowerStateNames[matchObject.group(1)]
                    self.WriteStatus('Power', value, None)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __MatchPassword(self, match):
        inStr = match.group(1)
        outStr = inStr + self.devicePassword
        m = hashlib.md5(outStr.encode())
        cmdString = hexlify(m.digest())+b'\x251POWR ?\r'
        self.Authenticated = 'Admin'
        self.__SetHelper('Password', cmdString.decode(), None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            MatchObject = search(self.ErrorMatchString, response)
            if MatchObject is not None:
                MatchNames = {
                    '1': 'Undefined Command',
                    '2': 'Out of Parameter',
                    '3': 'Unavailable Time',
                    '4': 'Projector Failure',
                    'A': 'Invalid Password'
                }
                self.Error(['Error = {0}; Command = {1}'.format(MatchNames[MatchObject.group(1)], sourceCmdName)])
                if 'ERRA' in response:
                    self.Authenticated = 'None'
                response = ''
        else:
            MatchObject = self.PasswordMatchString.search(response)
            if MatchObject is not None:
                response = ''
                self.__MatchPassword(MatchObject)
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)                
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if  res:
                    return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)                        

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'     

    
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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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