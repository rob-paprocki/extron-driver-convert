from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            if 'Serial' in self.ConnectionType:
                self.AddMatchString(re.compile(b'\*ASP=(4:3|16:9|16:10|AUTO|REAL)#\r\n'), self.__MatchAspectRatio, None)
                self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#\r\n'), self.__MatchAudioMute, None)
                self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#\r\n'), self.__MatchFreeze, None)
                self.AddMatchString(re.compile(b'\*SOUR=(RGB|HDMI|HDMI2|VID|SVID)#\r\n'), self.__MatchInput, None)
                self.AddMatchString(re.compile(b'\*LAMPM=(ECO|LNOR|SECO)#\r\n'), self.__MatchLampMode, None)
                self.AddMatchString(re.compile(b'>\*ltim=\?#\r\r\n\*LTIM=([0-9]{1,5})#\r\n'), self.__MatchLampUsage, None)
                self.AddMatchString(re.compile(b'\*APPMOD=(PRESET|SRGB|BRIGHT|CINE|USER1|USER2)#\r\n'), self.__MatchPictureMode, None)
                self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#\r\n'), self.__MatchPower, None)
                self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#\r\n'), self.__MatchVideoMute, None)
                self.AddMatchString(re.compile(b'\*VOL=([0-9]{1,2})#\r\n'), self.__MatchVolumeStatus, None)
            else:
                self.AddMatchString(re.compile(b'\*ASP=(4:3|16:9|16:10|AUTO|REAL)#'), self.__MatchAspectRatio, None)
                self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#'), self.__MatchAudioMute, None)
                self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#'), self.__MatchFreeze, None)
                self.AddMatchString(re.compile(b'\*SOUR=(RGB|HDMI|HDMI2|VID|SVID)#'), self.__MatchInput, None)
                self.AddMatchString(re.compile(b'\*LAMPM=(ECO|LNOR|SECO)#'), self.__MatchLampMode, None)
                self.AddMatchString(re.compile(b'\*LTIM=([0-9]{1,5})#'), self.__MatchLampUsage, None)
                self.AddMatchString(re.compile(b'\*APPMOD=(PRESET|SRGB|BRIGHT|CINE|USER1|USER2)#', re.I), self.__MatchPictureMode, None)
                self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#'), self.__MatchPower, None)
                self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#'), self.__MatchVideoMute, None)
                self.AddMatchString(re.compile(b'\*VOL=([0-9]{1,2})#'), self.__MatchVolumeStatus, None)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': '\x0D*asp=4:3#\x0D',
            '16:9': '\x0D*asp=16:9#\x0D',
            '16:10': '\x0D*asp=16:10#\x0D',
            'Auto': '\x0D*asp=AUTO#\x0D',
            'Real': '\x0D*asp=REAL#\x0D',
        }

        self.__SetHelper('AspectRatio', States[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', '\x0D*asp=?#\x0D', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10',
            'AUTO': 'Auto',
            'REAL': 'Real',
        }

        self.WriteStatus('AspectRatio', States[match.group(1).decode()], None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '\x0D*mute=on#\x0D',
            'Off': '\x0D*mute=off#\x0D'
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '\x0D*mute=?#\x0D', value, qualifier)

    def __MatchAudioMute(self, match, tag):
        self.WriteStatus('AudioMute', match.group(1).decode().title(), None)

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', '\x0D*auto#\x0D', value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On': '\x0D*freeze=on#\x0D',
            'Off': '\x0D*freeze=off#\x0D'
        }

        self.__SetHelper('Freeze', States[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        self.__UpdateHelper('Freeze', '\x0D*freeze=?#\x0D', value, qualifier)

    def __MatchFreeze(self, match, tag):
        self.WriteStatus('Freeze', match.group(1).decode().title(), None)

    def SetInput(self, value, qualifier):

        States = {
            'PC/YPbPr': '\x0D*sour=RGB#\x0D',
            'HDMI1/MHL1': '\x0D*sour=hdmi#\x0D',
            'HDMI2/MHL2': '\x0D*sour=hdmi2#\x0D',
            'Composite': '\x0D*sour=vid#\x0D',
            'S-Video': '\x0D*sour=svid#\x0D',
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '\x0D*sour=?#\x0D', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'RGB': 'PC/YPbPr',
            'HDMI': 'HDMI1/MHL1',
            'HDMI2': 'HDMI2/MHL2',
            'VID': 'Composite',
            'SVID': 'S-Video',
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal': '\x0D*lampm=lnor#\x0D',
            'Eco': '\x0D*lampm=eco#\x0D',
            'Smart Eco (ImageCare)': '\x0D*lampm=seco#\x0D',
        }

        self.__SetHelper('LampMode', States[value], value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        self.__UpdateHelper('LampMode', '\x0D*lampm=?#\x0D', value, qualifier)

    def __MatchLampMode(self, match, tag):

        States = {
            'LNOR': 'Normal',
            'ECO': 'Eco',
            'SECO': 'Smart Eco (ImageCare)',
        }

        self.WriteStatus('LampMode', States[match.group(1).decode()], None)

    def UpdateLampUsage(self, value, qualifier):
        self.__UpdateHelper('LampUsage', '\x0D*ltim=?#\x0D', value, qualifier)

    def __MatchLampUsage(self, match, tag):
        self.WriteStatus('LampUsage', int(match.group(1).decode()), None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '\x0D*up#\x0D',
            'Down': '\x0D*down#\x0D',
            'Left': '\x0D*left#\x0D',
            'Right': '\x0D*right#\x0D',
            'Enter': '\x0D*enter#\x0D',
            'Menu': '\x0D*menu=on#\x0D',
            'Exit': '\x0D*menu=off#\x0D'
        }

        self.__SetHelper('MenuNavigation', States[value], value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Presentation': '\x0D*appmod=preset#\x0D',
            'sRGB': '\x0D*appmod=srgb#\x0D',
            'Bright': '\x0D*appmod=bright#\x0D',
            'Cinema': '\x0D*appmod=cine#\x0D',
            'User 1': '\x0D*appmod=user1#\x0D',
            'User 2': '\x0D*appmod=user2#\x0D',
        }

        self.__SetHelper('PictureMode', States[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        self.__UpdateHelper('PictureMode', '\x0D*appmod=?#\x0D', value, qualifier)

    def __MatchPictureMode(self, match, tag):

        States = {
            'PRESET': 'Presentation',
            'SRGB': 'sRGB',
            'BRIGHT': 'Bright',
            'CINE': 'Cinema',
            'USER1': 'User 1',
            'USER2': 'User 2',
        }

        self.WriteStatus('PictureMode', States[match.group(1).decode()], None)

    def SetPower(self, value, qualifier):

        States = {
            'On': '\x0D*pow=on#\x0D',
            'Off': '\x0D*pow=off#\x0D'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '\x0D*pow=?#\x0D', value, qualifier)

    def __MatchPower(self, match, tag):
        self.WriteStatus('Power', match.group(1).decode().title(), None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '\x0D*blank=on#\x0D',
            'Off': '\x0D*blank=off#\x0D'
        }

        self.__SetHelper('VideoMute', States[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', '\x0D*blank=?#\x0D', value, qualifier)

    def __MatchVideoMute(self, match, tag):
        self.WriteStatus('VideoMute', match.group(1).decode().title(), None)

    def SetVolume(self, value, qualifier):

        States = {
            'Up': '\x0D*vol=+#\x0D',
            'Down': '\x0D*vol=-#\x0D'
        }

        self.__SetHelper('Volume', States[value], value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):
        self.__UpdateHelper('VolumeStatus', '\x0D*vol=?#\x0D', value, qualifier)

    def __MatchVolumeStatus(self, match, tag):
        self.WriteStatus('VolumeStatus', int(match.group(1).decode()), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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

