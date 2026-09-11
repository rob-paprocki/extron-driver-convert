from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from itertools import cycle

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
            '3DFormat': { 'Status': {}},
            '3DInvert': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'VolumeStatus': { 'Status': {}},
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*ASP=(4:3|16:9|16:10|AUTO|REAL)#'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|HDMI|HDMI2|VID|SVID)#'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(LNOR|ECO|SECO)#'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*LTIM=(\d+)#'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*APPMOD=(PRESET|SRGB|BRIGHT|DICOM|VIVID|USER1|USER2|THREED)#'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*VOL=([0-9]{1,2})#'), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'(Illegal format|Block item|Unsupported item)'), self.__MatchError, None)

    def Set3DFormat(self, value, qualifier):

        States = {
            'Off'              : 'off', 
            'Top Bottom'       : 'tb', 
            'Frame Sequential' : 'fs', 
            'Side by Side'     : 'sbs'
        }

        CmdString = '\r*3d={0}#\r'.format(States[value])
        self.__SetHelper('3DFormat', CmdString, value, qualifier)

    def Set3DInvert(self, value, qualifier):

        States = {
            'On'  : 'iv', 
            'Off' : 'da'
        }

        CmdString = '\r*3d={0}#\r'.format(States[value])
        self.__SetHelper('3DInvert', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3'   : '4:3', 
            '16:9'  : '16:9', 
            '16:10' : '16:10', 
            'Auto'  : 'AUTO', 
            'Real'  : 'REAL'
        }

        CmdString = '\r*asp={0}#\r'.format(States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        CmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)


    def __MatchAspectRatio(self, match, tag):
        self.WriteStatus('AspectRatio',  match.group(1).decode().title() , None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        CmdString = '\r*mute={0}#\r'.format(States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        CmdString = '\r*mute=?#\r'
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)


    def __MatchAudioMute(self, match, tag):
        self.WriteStatus('AudioMute',  match.group(1).decode().title() , None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '\r*auto#\r' , value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        CmdString = '\r*freeze={0}#\r'.format(States[value])
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        CmdString = '\r*freeze=?#\r'
        self.__UpdateHelper('Freeze', CmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):
        self.WriteStatus('Freeze',  match.group(1).decode().title() , None)

    def SetInput(self, value, qualifier):

        States = {
            'Computer/YPbPr' : 'RGB', 
            'HDMI 1'         : 'hdmi', 
            'HDMI 2/MHL'     : 'hdmi2', 
            'Video'          : 'vid', 
            'S-Video'        : 'svid', 
        }

        CmdString = '\r*sour={0}#\r'.format(States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        CmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'RGB'     : 'Computer/YPbPr', 
            'HDMI'    : 'HDMI 1', 
            'HDMI2'   : 'HDMI 2/MHL', 
            'VID'     : 'Video', 
            'SVID'    : 'S-Video', 
        }

        self.WriteStatus('Input',  States[match.group(1).decode()] , None)

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal'  : 'lnor', 
            'Eco'     : 'eco', 
            'SmartEco' : 'seco',
        }

        CmdString = '\r*lampm={0}#\r'.format(States[value])
        self.__SetHelper('LampMode', CmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        CmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', CmdString, value, qualifier)


    def __MatchLampMode(self, match, tag):

        States = {
            'LNOR'    : 'Normal', 
            'ECO'     : 'Eco', 
            'SECO'    : 'SmartEco',
        }

        self.WriteStatus('LampMode',  States[match.group(1).decode()] , None)

    def UpdateLampUsage(self, value, qualifier):
        CmdString = '\r*ltim=?#\r'
        self.__UpdateHelper('LampUsage', CmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):
        self.WriteStatus('LampUsage',  int(match.group(1).decode()) , None)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu On'  : 'menu=on', 
            'Menu Off' : 'menu=off', 
            'Up'       : 'up', 
            'Down'     : 'down', 
            'Right'    : 'right', 
            'Left'     : 'left', 
            'Enter'    : 'enter'
        }

        CmdString = '\r*{0}#\r'.format(States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Presentation' : 'preset', 
            'sRGB'         : 'srgb', 
            'Bright'       : 'bright', 
            'DICOM'        : 'dicom', 
            'Vivid'        : 'vivid', 
            'User 1'       : 'user1', 
            'User 2'       : 'user2'
        }

        CmdString = '\r*appmod={0}#\r'.format(States[value])
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        CmdString = '\r*appmod=?#\r'
        self.__UpdateHelper('PictureMode', CmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        States = {
            'PRESET' : 'Presentation', 
            'SRGB'   : 'sRGB', 
            'BRIGHT' : 'Bright', 
            'DICOM'  : 'DICOM', 
            'VIVID'  : 'Vivid', 
            'USER1'  : 'User 1', 
            'USER2'  : 'User 2', 
            'THREED' : '3D'
        }

        self.WriteStatus('PictureMode',  States[match.group(1).decode()] , None)

    def SetPower(self, value, qualifier):

        States = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        CmdString = '\r*pow={0}#\r'.format(States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        CmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        self.WriteStatus('Power',  match.group(1).decode().title() , None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        CmdString = '\r*blank={0}#\r'.format(States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        CmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):
        self.WriteStatus('VideoMute',  match.group(1).decode().title() , None)

    def SetVolume(self, value, qualifier):

        States = {
            'Up'   : '+', 
            'Down' : '-'
        }

        CmdString = '\r*vol={0}#\r'.format(States[value])
        self.__SetHelper('Volume', CmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):
        CmdString = '\r*vol=?#\r'
        self.__UpdateHelper('VolumeStatus', CmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):
        self.WriteStatus('VolumeStatus',  int(match.group(1).decode()) , None)

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
        self.Error([match.group(0).decode()])

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

