from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
import time


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
        self._DeviceID = 1
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'BezelAdjust': {'Parameters': ['Bezel'], 'Status': {}},
            'BezelWidth': {'Parameters': ['Position'], 'Status': {}},
            'BlackLevel': {'Status': {}},
            'Brightness': {'Status': {}},
            'Colors': {'Status': {}},
            'Contrast': {'Status': {}},
            'Enlarge': {'Status': {}},
            'ImageLocation': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Tint': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.startPolling = False

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'OK'), self.__MatchSuccess, None)

    def __MatchUsername(self, match, tag):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchSuccess(self, match, tag):
        self.startPolling = True

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Normal': 2,
            'Wide': 1,
            'Dot by Dot': 3,
            'Zoom 1': 4,
            'Zoom 2': 5
        }

        CmdString = 'WIDE{0: 4}\r\n'.format(States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            2: 'Normal',
            1: 'Wide',
            3: 'Dot by Dot',
            4: 'Zoom 1',
            5: 'Zoom 2'
        }

        res = self.__UpdateHelper('AspectRatio', 'WIDE????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': 1,
            'Off': 0
        }

        CmdString = 'MUTE{0: 4}\r\n'.format(States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            1: 'On',
            0: 'Off'
        }

        res = self.__UpdateHelper('AudioMute', 'MUTE????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'AGIN0001\r\n', value, qualifier)

    def SetBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust': 'BZCO',
            'Top': 'BZCT',
            'Bottom': 'BZCB',
            'Right': 'BZCR',
            'Left': 'BZCL'
        }

        Value = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '{0}   {1}\r\n'.format(Bezel[qualifier['Bezel']], Value[value])
        self.__SetHelper('BezelAdjust', CmdString, value, qualifier)

    def UpdateBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust': 'BZCO????\r\n',
            'Top': 'BZCT????\r\n',
            'Bottom': 'BZCB????\r\n',
            'Right': 'BZCR????\r\n',
            'Left': 'BZCL????\r\n'
        }

        Value = {
            1: 'On',
            0: 'Off'
        }

        res = self.__UpdateHelper('BezelAdjust', Bezel[qualifier['Bezel']], value, qualifier)
        if res:
            try:
                self.WriteStatus('BezelAdjust', Value[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Bezel Adjust: Invalid/unexpected response'])

    def SetBezelWidth(self, value, qualifier):

        Position = {
            'Top': 'BZWT',
            'Bottom': 'BZWB',
            'Right': 'BZWR',
            'Left': 'BZWL'
        }

        if 0 <= value <= 100:
            CmdString = '{0}{1: 4}\r\n'.format(Position[qualifier['Position']], value)
            self.__SetHelper('BezelWidth', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBezelWidth')

    def UpdateBezelWidth(self, value, qualifier):

        Position = {
            'Top': 'BZWT????\r\n',
            'Bottom': 'BZWB????\r\n',
            'Right': 'BZWR????\r\n',
            'Left': 'BZWL????\r\n'
        }

        res = self.__UpdateHelper('BezelWidth', Position[qualifier['Position']], value, qualifier)
        if res:
            try:
                self.WriteStatus('BezelWidth', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Bezel Width: Invalid/unexpected response'])

    def SetBlackLevel(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'BLVL{0: 4}\r\n'.format(value)
            self.__SetHelper('BlackLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlackLevel')

    def UpdateBlackLevel(self, value, qualifier):

        res = self.__UpdateHelper('BlackLevel', 'BLVL????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('BlackLevel', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Black Level: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VLMP{0: 4}\r\n'.format(value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        res = self.__UpdateHelper('Brightness', 'VLMP????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Brightness', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'CONT{0: 4}\r\n'.format(value)
            self.__SetHelper('Contrast', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        res = self.__UpdateHelper('Contrast', 'CONT????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Contrast', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Contrast: Invalid/unexpected response'])

    def SetColors(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'COLR{0: 4}\r\n'.format(value)
            self.__SetHelper('Colors', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColors')

    def UpdateColors(self, value, qualifier):

        res = self.__UpdateHelper('Colors', 'COLR????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Colors', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Colors: Invalid/unexpected response'])

    def SetEnlarge(self, value, qualifier):

        States = {
            '2x2': 1,
            '3x3': 2,
            '4x4': 3,
            '5x5': 4,
        }

        CmdString = 'EMAG{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Enlarge', CmdString, value, qualifier)

    def UpdateEnlarge(self, value, qualifier):

        States = {
            1: '2x2',
            2: '3x3',
            3: '4x4',
            4: '5x5'
        }

        res = self.__UpdateHelper('Enlarge', 'EMAG????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Enlarge', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Enlarge: Invalid/unexpected response'])

    def SetImageLocation(self, value, qualifier):

        States = {
            '1x2': 12, '1x3': 13, '1x4': 14, '1x5': 15,
            '2x1': 21, '2x2': 22, '2x3': 23, '2x4': 24, '2x5': 25,
            '3x1': 31, '3x2': 32, '3x3': 33, '3x4': 34, '3x5': 35,
            '4x1': 41, '4x2': 42, '4x3': 43, '4x4': 44, '4x5': 45,
            '5x1': 51, '5x2': 52, '5x3': 53, '5x4': 54, '5x5': 55
        }

        CmdString = 'EPHV{0: 4}\r\n'.format(States[value])
        self.__SetHelper('ImageLocation', CmdString, value, qualifier)

    def UpdateImageLocation(self, value, qualifier):

        States = {
            12: '1x2', 13: '1x3', 14: '1x4', 15: '1x5',
            21: '2x1', 22: '2x2', 23: '2x3', 24: '2x4', 25: '2x5',
            31: '3x1', 32: '3x2', 33: '3x3', 34: '3x4', 35: '3x5',
            41: '4x1', 42: '4x2', 43: '4x3', 44: '4x4', 45: '4x5',
            51: '5x1', 52: '5x2', 53: '5x3', 54: '5x4', 55: '5x5'
        }

        res = self.__UpdateHelper('ImageLocation', 'EPHV????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('ImageLocation', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Enlarge Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        States = {
            'DVI-D': 1,
            'D-SUB RGB': 2,
            'D-SUB Component': 3,
            'HDMI 1': 10,
            'HDMI 2': 13,
            'DisplayPort': 14,
            'Option': 21
        }

        CmdString = 'INPS{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            1: 'DVI-D',
            2: 'D-SUB RGB',
            3: 'D-SUB Component',
            10: 'HDMI 1',
            13: 'HDMI 2',
            14: 'DisplayPort',
            21: 'Option'
        }

        res = self.__UpdateHelper('Input', 'INPS????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On 1': 0,
            'On 2': 2,
            'Off': 1
        }

        CmdString = 'LOSD{0: 4}\r\n'.format(States[value])
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        States = {
            0: 'On 1',
            1: 'Off',
            2: 'On 2'
        }

        res = self.__UpdateHelper('OnScreenDisplay', 'LOSD????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('OnScreenDisplay', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        States = {
            'PIP': 1,
            'PbyP 1': 2,
            'PbyP 2': 3,
            'Off': 0
        }

        CmdString = 'MWIN{0: 4}\r\n'.format(States[value])
        self.__SetHelper('PictureInPicture', CmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        States = {
            1: 'PIP',
            2: 'PbyP 1',
            3: 'PbyP 2',
            0: 'Off'
        }

        res = self.__UpdateHelper('PictureInPicture', 'MWIN????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureInPicture', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Picture In Picture: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        States = {
            'DVI-D': 1,
            'D-SUB RGB': 2,
            'D-SUB Component': 3,
            'HDMI 1': 10,
            'HDMI 2': 13,
            'DisplayPort': 14,
            'Option': 21
        }

        CmdString = 'MWIP{0: 4}\r\n'.format(States[value])
        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        States = {
            1: 'DVI-D',
            2: 'D-SUB RGB',
            3: 'D-SUB Component',
            10: 'HDMI 1',
            13: 'HDMI 2',
            14: 'DisplayPort',
            21: 'Option'
        }

        res = self.__UpdateHelper('PIPInput', 'MWIP????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('PIPInput', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        if 1 <= value <= 64:
            CmdString = 'MPSZ{0:>4}\r\n'.format(value)
            self.__SetHelper('PIPSize', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('PIPSize', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On': 1,
            'Off': 0
        }

        CmdString = 'POWR{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            1: 'On',
            0: 'Off',
            2: 'Input signal waiting mode'
        }

        res = self.__UpdateHelper('Power', 'POWR????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[int(res)], qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSharpness(self, value, qualifier):

        if 0 <= value <= 24:
            CmdString = 'SHRP{0: 4}\r\n'.format(value)
            self.__SetHelper('Sharpness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):

        res = self.__UpdateHelper('Sharpness', 'SHRP????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Sharpness', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Sharpness: Invalid/unexpected response'])

    def SetTint(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'TINT{0: 4}\r\n'.format(value)
            self.__SetHelper('Tint', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTint')

    def UpdateTint(self, value, qualifier):

        res = self.__UpdateHelper('Tint', 'TINT????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Tint', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Tint: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', 'VOLM????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                ErrorString = '{0}: Communication error or incorrect command'.format(sourceCmdName)
                self.Error([ErrorString])
                response = ''
            elif response[:2] == 'OK':
                self.startPolling = True
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.startPolling:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Invalid Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.startPolling:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.startPolling = False

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AssignID': {'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'BezelAdjust': {'Parameters': ['Device ID', 'Bezel'], 'Status': {}},
            'BezelWidth': {'Parameters': ['Device ID', 'Position'], 'Status': {}},
            'BlackLevel': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'Colors': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'Enlarge': {'Parameters': ['Device ID'], 'Status': {}},
            'IDCheck': {'Status': {}},
            'ImageLocation': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureInPicture': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'Sharpness': {'Parameters': ['Device ID'], 'Status': {}},
            'Tint': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self.IDSent = False
        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '0'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(WAIT\r\n)?OK (\d\d\d)\r\n'), self.__MatchDeviceOK, None)

        self.Regex = compile(b'\d{1,3} \d{3}\r\n|ERR\r\n|ERR \d\d\d\r\n')

    def DeviceIDHandler(self, Callback, value, qualifier):
        if qualifier and 'Device ID' in qualifier:
            if qualifier['Device ID'] == 'Broadcast' or qualifier['Device ID'] == '0':
                qualifier['Device ID'] = '0'
                if Callback.startswith('Update'):
                    self.Discard('Invalid Command')
                    return False
            elif not (1 <= int(qualifier['Device ID']) <= 255):
                self.Discard('Invalid Command')
                return False

            self.Callback = Callback
            self.valueCallback = value
            self.qualifierCallback = qualifier
            if self.SelectedID == qualifier['Device ID']:
                self.IDSent = False
                self.ExpiryTime = 0
                return True
            elif (self.ExpiryTime != 0) and (self.ExpiryTime <= time.monotonic()):
                self.IDSent = False
                self.ExpiryTime = 0
                self.Error(['Response timeout: Unable to set Device ID'])
            else:
                return self.IDLK_Callback()
        else:
            self.Discard('Invalid Command')

    def IDLK_Callback(self):
        if not self.IDSent:
            self.IDSent = True
            CmdString = 'IDLK{0:04d}\r\n'.format(int(self.qualifierCallback['Device ID']))
            self.SetIDLK(CmdString, None)
        else:
            method = getattr(self, self.Callback, None)
            if method is not None and callable(method):
                method(self.valueCallback, self.qualifierCallback)
            else:
                raise AttributeError(self.Callback + 'is not supported.')

    def SetIDLK(self, CmdString, qualifier):
        self.ExpiryTime = time.monotonic() + 5
        self.Send(CmdString)
        if self.qualifierCallback['Device ID'] == '0':
            self.SelectedID = '0'

        self.IDLK_Callback()

    def SetAssignID(self, value, qualifier):
        print('in here')
        self.__SetHelper('AssignID', 'IDST001+\r\n', value, qualifier)

    def SetIDCheck(self, value, qualifier):
        self.__SetHelper('IDCheck', 'IDCK0000\r\n', value, qualifier)

    def __MatchDeviceOK(self, match, tag):
        self.SelectedID = str(int(match.group(2).decode()))

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Normal': 2,
            'Wide': 1,
            'Dot by Dot': 3,
            'Zoom 1': 4,
            'Zoom 2': 5
        }
        if self.DeviceIDHandler('SetAspectRatio', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'WIDE{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'WIDE{0: 4}\r\n'.format(States[value])
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            2: 'Normal',
            1: 'Wide',
            3: 'Dot by Dot',
            4: 'Zoom 1',
            5: 'Zoom 2'
        }

        if self.DeviceIDHandler('UpdateAspectRatio', value, qualifier):
            res = self.__UpdateHelper('AspectRatio', 'WIDE????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('AspectRatio', States[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': 1,
            'Off': 0
        }
        if self.DeviceIDHandler('SetAudioMute', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'MUTE{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'MUTE{0: 4}\r\n'.format(States[value])
            self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            1: 'On',
            0: 'Off'
        }

        if self.DeviceIDHandler('UpdateAudioMute', value, qualifier):
            res = self.__UpdateHelper('AudioMute', 'MUTE????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('AudioMute', States[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        if self.DeviceIDHandler('SetAutoImage', value, qualifier):
            if qualifier['Device ID'] == '0':
                self.__SetHelper('AutoImage', 'AGIN001+\r\n', value, qualifier)
            else:
                self.__SetHelper('AutoImage', 'AGIN0001\r\n', value, qualifier)

    def SetBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust': 'BZCO',
            'Top': 'BZCT',
            'Bottom': 'BZCB',
            'Right': 'BZCR',
            'Left': 'BZCL'
        }

        Value = {
            'On': '1',
            'Off': '0'
        }

        if self.DeviceIDHandler('SetBezelAdjust', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = '{0}  {1}+\r\n'.format(Bezel[qualifier['Bezel']], Value[value])
            else:
                CmdString = '{0}   {1}\r\n'.format(Bezel[qualifier['Bezel']], Value[value])
            self.__SetHelper('BezelAdjust', CmdString, value, qualifier)

    def UpdateBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust': 'BZCO????\r\n',
            'Top': 'BZCT????\r\n',
            'Bottom': 'BZCB????\r\n',
            'Right': 'BZCR????\r\n',
            'Left': 'BZCL????\r\n'
        }

        Values = {
            1: 'On',
            0: 'Off'
        }

        if self.DeviceIDHandler('UpdateBezelAdjust', value, qualifier):
            res = self.__UpdateHelper('BezelAdjust', Bezel[qualifier['Bezel']], value, qualifier)
            if res:
                try:
                    self.WriteStatus('BezelAdjust', Values[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Bezel Adjust: Invalid/unexpected response'])

    def SetBezelWidth(self, value, qualifier):

        Position = {
            'Top': 'BZWT',
            'Bottom': 'BZWB',
            'Right': 'BZWR',
            'Left': 'BZWL'
        }

        if 0 <= value <= 100:
            if self.DeviceIDHandler('SetBezelWidth', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = '{0}{1:3}+\r\n'.format(Position[qualifier['Position']], value)
                else:
                    CmdString = '{0}{1:4}\r\n'.format(Position[qualifier['Position']], value)
                self.__SetHelper('BezelWidth', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBezelWidth')

    def UpdateBezelWidth(self, value, qualifier):

        Position = {
            'Top': 'BZWT????\r\n',
            'Bottom': 'BZWB????\r\n',
            'Right': 'BZWR????\r\n',
            'Left': 'BZWL????\r\n'
        }

        if self.DeviceIDHandler('UpdateBezelWidth', value, qualifier):
            res = self.__UpdateHelper('BezelWidth', Position[qualifier['Position']], value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 100:
                        self.WriteStatus('BezelWidth', value, qualifier)
                    else:
                        self.Error(['Bezel Width: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Bezel Width: Invalid/unexpected response'])

    def SetBlackLevel(self, value, qualifier):

        if 0 <= value <= 60:
            if self.DeviceIDHandler('SetBlackLevel', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'BLVL{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'BLVL{0: 4}\r\n'.format(value)
                self.__SetHelper('BlackLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlackLevel')

    def UpdateBlackLevel(self, value, qualifier):
        if self.DeviceIDHandler('UpdateBlackLevel', value, qualifier):
            res = self.__UpdateHelper('BlackLevel', 'BLVL????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('BlackLevel', value, qualifier)
                    else:
                        self.Error(['Black Level: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Black Level: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 31:
            if self.DeviceIDHandler('SetBrightness', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'VLMP{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'VLMP{0: 4}\r\n'.format(value)
                self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        if self.DeviceIDHandler('UpdateBrightness', value, qualifier):
            res = self.__UpdateHelper('Brightness', 'VLMP????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 31:
                        self.WriteStatus('Brightness', value, qualifier)
                    else:
                        self.Error(['Brightness: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Brightness: Invalid/unexpected response'])

    def SetColors(self, value, qualifier):

        if 0 <= value <= 60:
            if self.DeviceIDHandler('SetColors', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'COLR{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'COLR{0: 4}\r\n'.format(value)
                self.__SetHelper('Colors', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColors')

    def UpdateColors(self, value, qualifier):
        if self.DeviceIDHandler('UpdateColors', value, qualifier):
            res = self.__UpdateHelper('Tint', 'COLR????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('Colors', value, qualifier)
                    else:
                        self.Error(['Colors: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Colors: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 60:
            if self.DeviceIDHandler('SetContrast', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'CONT{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'CONT{0: 4}\r\n'.format(value)
                self.__SetHelper('Contrast', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):
        if self.DeviceIDHandler('UpdateContrast', value, qualifier):
            res = self.__UpdateHelper('Contrast', 'CONT????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('Contrast', value, qualifier)
                    else:
                        self.Error(['Contrast: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Contrast: Invalid/unexpected response'])

    def SetEnlarge(self, value, qualifier):

        States = {
            '2x2': 1,
            '3x3': 2,
            '4x4': 3,
            '5x5': 4
        }

        if self.DeviceIDHandler('SetEnlarge', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'EMAG{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'EMAG{0: 4}\r\n'.format(States[value])
            self.__SetHelper('Enlarge', CmdString, value, qualifier)

    def UpdateEnlarge(self, value, qualifier):

        States = {
            1: '2x2',
            2: '3x3',
            3: '4x4',
            4: '5x5',
        }

        if self.DeviceIDHandler('UpdateEnlarge', value, qualifier):
            res = self.__UpdateHelper('Enlarge', 'EMAG????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('Enlarge', States[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Enlarge: Invalid/unexpected response'])

    def SetImageLocation(self, value, qualifier):

        States = {
            '1x2': 12, '1x3': 13, '1x4': 14, '1x5': 15,
            '2x1': 21, '2x2': 22, '2x3': 23, '2x4': 24, '2x5': 25,
            '3x1': 31, '3x2': 32, '3x3': 33, '3x4': 34, '3x5': 35,
            '4x1': 41, '4x2': 42, '4x3': 43, '4x4': 44, '4x5': 45,
            '5x1': 51, '5x2': 52, '5x3': 53, '5x4': 54, '5x5': 55
        }

        if self.DeviceIDHandler('SetImageLocation', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'EPHV{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'EPHV{0: 4}\r\n'.format(States[value])
            self.__SetHelper('ImageLocation', CmdString, value, qualifier)

    def UpdateImageLocation(self, value, qualifier):
        States = {
            12: '1x2', 13: '1x3', 14: '1x4', 15: '1x5',
            21: '2x1', 22: '2x2', 23: '2x3', 24: '2x4', 25: '2x5',
            31: '3x1', 32: '3x2', 33: '3x3', 34: '3x4', 35: '3x5',
            41: '4x1', 42: '4x2', 43: '4x3', 44: '4x4', 45: '4x5',
            51: '5x1', 52: '5x2', 53: '5x3', 54: '5x4', 55: '5x5'
        }

        if self.DeviceIDHandler('UpdateImageLocation', value, qualifier):
            res = self.__UpdateHelper('ImageLocation', 'EPHV????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('ImageLocation', States[int(res[0:2])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Image Location: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        States = {
            'DVI-D': 1,
            'D-SUB RGB': 2,
            'D-SUB Component': 3,
            'HDMI 1': 10,
            'HDMI 2': 13,
            'DisplayPort': 14,
            'Option': 21
        }
        if self.DeviceIDHandler('SetInput', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'INPS{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'INPS{0: 4}\r\n'.format(States[value])
            self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            1: 'DVI-D',
            2: 'D-SUB RGB',
            3: 'D-SUB Component',
            10: 'HDMI 1',
            13: 'HDMI 2',
            14: 'DisplayPort',
            21: 'Option'
        }

        if self.DeviceIDHandler('UpdateInput', value, qualifier):
            res = self.__UpdateHelper('Input', 'INPS????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('Input', States[int(res[0:-6])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Input: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On 1': 0,
            'On 2': 2,
            'Off': 1
        }
        if self.DeviceIDHandler('SetOnScreenDisplay', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'LOSD{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'LOSD{0: 4}\r\n'.format(States[value])
            self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        States = {
            0: 'On 1',
            1: 'Off',
            2: 'On 2'
        }

        if self.DeviceIDHandler('UpdateOnScreenDisplay', value, qualifier):
            res = self.__UpdateHelper('OnScreenDisplay', 'LOSD????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('OnScreenDisplay', States[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPictureInPicture(self, value, qualifier):

        States = {
            'PIP': 1,
            'PbyP 1': 2,
            'PbyP 2': 3,
            'Off': 0,
        }
        if self.DeviceIDHandler('SetPictureInPicture', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'MWIN{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'MWIN{0: 4}\r\n'.format(States[value])
            self.__SetHelper('PictureInPicture', CmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        States = {
            1: 'PIP',
            2: 'PbyP 1',
            3: 'PbyP 2',
            0: 'Off'
        }

        if self.DeviceIDHandler('UpdatePictureInPicture', value, qualifier):
            res = self.__UpdateHelper('PictureInPicture', 'MWIN????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('PictureInPicture', States[int(res[0])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Picture In Picture: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        States = {
            'DVI-D': 1,
            'D-SUB RGB': 2,
            'D-SUB Component': 3,
            'HDMI 1': 10,
            'HDMI 2': 13,
            'DisplayPort': 14,
            'Option': 21
        }
        if self.DeviceIDHandler('SetPIPInput', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'MWIP{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'MWIP{0: 4}\r\n'.format(States[value])
            self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        States = {
            1: 'DVI-D',
            2: 'D-SUB RGB',
            3: 'D-SUB Component',
            10: 'HDMI 1',
            13: 'HDMI 2',
            14: 'DisplayPort',
            21: 'Option'
        }

        if self.DeviceIDHandler('UpdatePIPInput', value, qualifier):
            res = self.__UpdateHelper('PIPInput', 'MWIP????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('PIPInput', States[int(res[0:-6])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        if 1 <= value <= 64:
            if self.DeviceIDHandler('SetPIPSize', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'MPSZ{0:>3}+\r\n'.format(value)
                else:
                    CmdString = 'MPSZ{0:>4}\r\n'.format(value)
                self.__SetHelper('PIPSize', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        if self.DeviceIDHandler('UpdatePIPSize', value, qualifier):
            res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 1 <= value <= 64:
                        self.WriteStatus('PIPSize', value, qualifier)
                    else:
                        self.Error(['PIP Size: Invalid/unexpected response'])
                except (IndexError, ValueError):
                    self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On': 1,
            'Off': 0,
        }

        if self.DeviceIDHandler('SetPower', value, qualifier):
            if qualifier['Device ID'] == '0':
                CmdString = 'POWR{0: 3}+\r\n'.format(States[value])
            else:
                CmdString = 'POWR{0: 4}\r\n'.format(States[value])
            self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode',
        }

        if self.DeviceIDHandler('UpdatePower', value, qualifier):
            res = self.__UpdateHelper('Power', 'POWR????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('Power', States[res[0]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])

    def SetSharpness(self, value, qualifier):

        if 0 <= value <= 24:
            if self.DeviceIDHandler('SetSharpness', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'SHRP{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'SHRP{0: 4}\r\n'.format(value)
                self.__SetHelper('Sharpness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):
        if self.DeviceIDHandler('UpdateSharpness', value, qualifier):
            res = self.__UpdateHelper('Sharpness', 'SHRP????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 24:
                        self.WriteStatus('Sharpness', value, qualifier)
                    else:
                        self.Error(['Sharpness: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Sharpness: Invalid/unexpected response'])

    def SetTint(self, value, qualifier):

        if 0 <= value <= 60:
            if self.DeviceIDHandler('SetTint', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'TINT{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'TINT{0: 4}\r\n'.format(value)
                self.__SetHelper('Tint', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTint')

    def UpdateTint(self, value, qualifier):
        if self.DeviceIDHandler('UpdateTint', value, qualifier):
            res = self.__UpdateHelper('Tint', 'TINT????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    if 0 <= value <= 60:
                        self.WriteStatus('Tint', value, qualifier)
                    else:
                        self.Error(['Tint: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Tint: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            if self.DeviceIDHandler('SetVolume', value, qualifier):
                if qualifier['Device ID'] == '0':
                    CmdString = 'VOLM{0: 3}+\r\n'.format(value)
                else:
                    CmdString = 'VOLM{0: 4}\r\n'.format(value)
                self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if self.DeviceIDHandler('UpdateVolume', value, qualifier):
            res = self.__UpdateHelper('Volume', 'VOLM????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:2].strip(' '))
                    if 0 <= value <= 31:
                        self.WriteStatus('Volume', value, qualifier)
                    else:
                        self.Error(['Volume: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                ErrorString = '{0}: Communication error or incorrect command'.format(sourceCmdName)
                self.Error([ErrorString])
                response = ''
            if 'OK' in response:
                res = search('OK (\d\d\d)\r\n', response)
                self.SelectedID = str(int(res.group(1)))
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or (qualifier and qualifier['Device ID'] == '0'):
            self.Send(commandstring)
        else:
            if command == 'AssignID':
                print(commandstring)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.IDSent = False
        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '0'

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
