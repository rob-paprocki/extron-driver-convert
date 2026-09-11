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
            '3DSync': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*3d=\?#\r\r\n\*3d=(off|tb|fs)#\r\n'), self.__Match3DSync, None)
            self.AddMatchString(re.compile(b'\*3d=\?#\r\r\n\*3D=(OFF|TB|FS)#\r\n'), self.__Match3DSync, None)
            self.AddMatchString(re.compile(b'\*pow=\?#\r\r\n\*POW=(ON|OFF)#\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*pow=\?#\r\r\n\*pow=(on|off)#\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*asp=\?#\r\r\n\*ASP=(4:3|16:9|16:10|AUTO|REAL|auto|real)#\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*asp=\?#\r\r\n\*asp=(4:3|16:9|16:10|auto|real|AUTO|REAL)#\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*freeze=\?#\r\r\n\*FREEZE=(ON|OFF)#\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*freeze=\?#\r\r\n\*freeze=(on|off)#\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*blank=\?#\r\r\n\*BLANK=(ON|OFF)#\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*blank=\?#\r\r\n\*blank=(on|off)#\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*mute=\?#\r\r\n\*MUTE=(ON|OFF)#\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*mute=\?#\r\r\n\*mute=(on|off)#\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*sour=\?#\r\r\n\*SOUR=(RGB|RGB2|HDMI|VID|SVID|NETWORK|USBDISPLAY|USBREADER)#\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*sour=\?#\r\r\n\*sour=(rgb|rgb2|hdmi|vid|svid|network|usbdisplay|usbreader)#\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*ltim=\?#\r\r\n\*LTIM=([0-9]{1,5})#\r\n'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*ltim=\?#\r\r\n\*ltim=([0-9]{1,5})#\r\n'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*lampm=\?#\r\r\n\*LAMPM=(ECO|SECO|LNOR)#\r\n'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*lampm=\?#\r\r\n\*lampm=(eco|seco|lnor)#\r\n'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*vol=\?#\r\r\n\*VOL=([0-9]{1,2})#\r\n'), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'\*vol=\?#\r\r\n\*vol=([0-9]{1,2})#\r\n'), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'Illegal format\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Block item\r\n'), self.__MatchError, None)

    def Set3DSync(self, value, qualifier):

        ThreeDSyncStateValues = {
            'Off': '\r*3d=off#\r',
            'Top Bottom': '\r*3d=tb#\r',
            'Frame Sequential': '\r*3d=fs#\r'
            }
        ThreeDSyncCmdString = ThreeDSyncStateValues[value]
        self.__SetHelper('3DSync', ThreeDSyncCmdString, value, qualifier)

    def Update3DSync(self, value, qualifier):

        ThreeDSyncCmdString = '\r*3d=?#\r'
        self.__UpdateHelper('3DSync', ThreeDSyncCmdString, value, qualifier)

    def __Match3DSync(self, match, tag):

        ThreeDSyncStateNames = {
           'OFF': 'Off',
           'TB': 'Top Bottom',
           'FS': 'Frame Sequential',
           'off': 'Off',
           'tb': 'Top Bottom',
           'fs': 'Frame Sequential'
           }

        value = ThreeDSyncStateNames[match.group(1).decode()]
        self.WriteStatus('3DSync', value, None)

    def SetAspectRatio(self, value, qualifier):

        AspectStateValues = {
            '4:3': '\r*asp=4:3#\r',
            '16:9': '\r*asp=16:9#\r',
            '16:10': '\r*asp=16:10#\r',
            'Auto': '\r*asp=AUTO#\r',
            'Real': '\r*asp=REAL#\r',
            }
        AspectCmdString = AspectStateValues[value]
        self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectStateNames = {
           '4:3': '4:3',
           '16:9': '16:9',
           '16:10': '16:10',
           'AUTO': 'Auto',
           'REAL': 'Real',
           'auto': 'Auto',
           'real': 'Real',
           }

        value = AspectStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': '\r*mute=on#\r',
            'Off': '\r*mute=off\r',
            }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\r*mute=?#\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
           'ON': 'On',
           'OFF': 'Off',
           'on': 'On',
           'off': 'Off',
           }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '\r*freeze=on#\r',
            'Off': '\r*freeze=off#\r'
            }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '\r*freeze=?#\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeStateNames = {
           'ON': 'On',
           'OFF': 'Off',
           'on': 'On',
           'off': 'Off',
           }

        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Composite': '\r*sour=vid#\r',
            'Computer 1': '\r*sour=RGB#\r',
            'Computer 2': '\r*sour=RGB2#\r',
            'HDMI': '\r*sour=hdmi#\r',
            'Network': '\r*sour=network#\r',
            'S-Video': '\r*sour=svid#\r',
            'USB Display': '\r*sour=usbdisplay#\r',
            'USB Reader': '\r*sour=usbreader#\r',
            }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputStateNames = {
           'VID': 'Composite',
           'RGB': 'Computer 1',
           'RGB2': 'Computer 2',
           'HDMI': 'HDMI',
           'NETWORK': 'Network',
           'SVID': 'S-Video',
           'USBDISPLAY': 'USB Display',
           'USBREADER': 'USB Reader',
           'vid': 'Composite',
           'rgb': 'Computer 1',
           'rgb2': 'Computer 2',
           'hdmi': 'HDMI',
           'network': 'Network',
           'svid': 'S-Video',
           'usbdisplay': 'USB Display',
           'usbreader': 'USB Reader'
           }

        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal': '\r*lampm=lnor#\r',
            'Eco': '\r*lampm=eco#\r',
            'Smart Eco': '\r*lampm=seco#\r',
            }
        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeStateNames = {
           'LNOR': 'Normal',
           'ECO': 'Eco',
           'SECO': 'Smart Eco',
           'lnor': 'Normal',
           'eco': 'Eco',
           'seco': 'Smart Eco',
           }

        value = LampModeStateNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '\r*ltim=?#\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up': '\r*up#\r',
            'Down': '\r*down#\r',
            'Left': '\r*left#\r',
            'Right': '\r*right#\r',
            'Enter': '\r*enter#\r',
            'Menu On': '\r*menu=on#\r',
            'Menu Off': '\r*menu=off#\r',
            }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '\r*pow=on#\r',
            'Off': '\r*pow=off#\r',
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '\r*pow=?#\r', value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            'ON': 'On',
            'OFF': 'Off',
            'on': 'On',
            'off': 'Off',
            }

        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': '\r*blank=on#\r',
            'Off': '\r*blank=off#\r'
            }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
           'ON': 'On',
           'OFF': 'Off',
           'on': 'On',
           'off': 'Off',
           }

        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeStateValues = {
            'Up': '\r*vol=+#\r',
            'Down': '\r*vol=-#\r',
            }
        VolumeCmdString = VolumeStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

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
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        value = match.group(0).decode()
        print(value)

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
