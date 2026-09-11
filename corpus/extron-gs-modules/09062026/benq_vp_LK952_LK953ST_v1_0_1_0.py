from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuCall': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'>\*asp=\?#\r\r\n\*ASP=(AUTO|REAL|4:3|16:9|16:10)#\r\n', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'>\*mute=\?#\r\r\n\*MUTE=(ON|OFF)#\r\n', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'>\*sour=\?#\r\r\n\*SOUR=(RGB|HDMI|HDMI2|HDMI3|HDBASET)#\r\n', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'>\*lampm=\?#\r\r\n\*LAMPM=(LNOR|ECO|DIMMING|CUSTOM)#\r\n', re.I), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'>\*ltim=\?#\r\r\n\*LTIM=(\d+)#\r\n', re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'>\*appmod=\?#\r\r\n\*APPMOD=(PRESET|SRGB|BRIGHT|DICOM|VIVID|USER1|USER2)#\r\n', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'>\*pow=\?#\r\r\n\*POW=(ON|OFF)#\r\n', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'>\*blank=\?#\r\r\n\*BLANK=(ON|OFF)#\r\n', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'>\*vol=\?#\r\r\n\*VOL=(\d+)#\r\n', re.I), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(Illegal format|Block item|Unsupported item)\r', re.I), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Auto': '\r*asp=AUTO#\r',
            'Real': '\r*asp=REAL#\r',
            '4:3': '\r*asp=4:3#\r',
            '16:9': '\r*asp=16:9#\r',
            '16:10': '\r*asp=16:10#\r'
        }

        self.__SetHelper('AspectRatio', States[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', '\r*asp=?#\r', value, qualifier)

    def __MatchAspectRatio(self, match, tag):
        self.WriteStatus('AspectRatio', match.group(1).decode().title(), None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '\r*mute=on#\r',
            'Off': '\r*mute=off#\r'
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '\r*mute=?#\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):
        self.WriteStatus('AudioMute', match.group(1).decode().title(), None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '\r*auto#\r', value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'Computer': '\r*sour=RGB#\r',
            'HDMI 1': '\r*sour=hdmi#\r',
            'HDMI 2': '\r*sour=hdmi2#\r',
            'HDMI 3': '\r*sour=hdmi3#\r',
            'HDBaseT': '\r*sour=hdbaset#\r'
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '\r*sour=?#\r', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'RGB': 'Computer',
            'HDMI': 'HDMI 1',
            'HDMI2': 'HDMI 2',
            'HDMI3': 'HDMI 3',
            'HDBASET': 'HDBaseT'
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal': '\r*lampm=lnor#\r',
            'Eco': '\r*lampm=eco#\r',
            'Dimming': '\r*lampm=dimming#\r',
            'Custom': '\r*lampm=custom#\r'
        }

        self.__SetHelper('LampMode', States[value], value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        self.__UpdateHelper('LampMode', '\r*lampm=?#\r', value, qualifier)

    def __MatchLampMode(self, match, tag):

        States = {
            'LNOR': 'Normal',
            'ECO': 'Eco',
            'DIMMING': 'Dimming',
            'CUSTOM': 'Custom'
        }

        self.WriteStatus('LampMode', States[match.group(1).decode()], None)

    def UpdateLampUsage(self, value, qualifier):

        self.__UpdateHelper('LampUsage', '\r*ltim=?#\r', value, qualifier)

    def __MatchLampUsage(self, match, tag):
        self.WriteStatus('LampUsage', int(match.group(1).decode()), None)

    def SetMenuCall(self, value, qualifier):

        States = {
            'On': '\r*menu=on#\r',
            'Off': '\r*menu=off#\r'
        }

        self.__SetHelper('MenuCall', States[value], value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '\r*up#\r',
            'Down': '\r*down#\r',
            'Left': '\r*left#\r',
            'Right': '\r*right#\r',
            'Enter': '\r*enter#\r'
        }

        self.__SetHelper('MenuNavigation', States[value], value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Presentation': '\r*appmod=preset#\r',
            'sRGB': '\r*appmod=srgb#\r',
            'Bright': '\r*appmod=bright#\r',
            'DICOM': '\r*appmod=dicom#\r',
            'Vivid': '\r*appmod=vivid#\r',
            'User 1': '\r*appmod=user1#\r',
            'User 2': '\r*appmod=user2#\r'
        }

        self.__SetHelper('PictureMode', States[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        self.__UpdateHelper('PictureMode', '\r*appmod=?#\r', value, qualifier)

    def __MatchPictureMode(self, match, tag):
        States = {
            'PRESET': 'Presentation',
            'SRGB': 'sRGB',
            'BRIGHT': 'Bright',
            'DICOM': 'DICOM',
            'VIVID': 'Vivid',
            'USER1': 'User 1',
            'USER2': 'User 2'
        }

        self.WriteStatus('PictureMode', States[match.group(1).decode()], None)

    def SetPower(self, value, qualifier):

        States = {
            'On': '\r*pow=on#\r',
            'Off': '\r*pow=off#\r'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '\r*pow=?#\r', value, qualifier)

    def __MatchPower(self, match, tag):
        self.WriteStatus('Power', match.group(1).decode().title(), None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '\r*blank=on#\r',
            'Off': '\r*blank=off#\r'
        }

        self.__SetHelper('VideoMute', States[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', '\r*blank=?#\r', value, qualifier)

    def __MatchVideoMute(self, match, tag):
        self.WriteStatus('VideoMute', match.group(1).decode().title(), None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 10:
            self.__SetHelper('Volume', '\r*vol={}#\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '\r*vol=?#\r', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode()), None)

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

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['An error occurred: {}.'.format(match.group(0).decode().strip().title())])

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
