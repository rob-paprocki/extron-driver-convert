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
            'Lamp2Usage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*3D=(OFF|TB|FS)#\r\n', re.I), self.__Match3DSync, None)
            self.AddMatchString(re.compile(b'\*ASP=(AUTO|REAL|4:3|16:9|16:10)#\r\n', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*MUTE=(ON|OFF)#\r\n', re.I), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#\r\n', re.I), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|RGB2|HDMI|VID|SVID|NETWORK|USBDISPLAY|USBREADER)#\r\n', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(LNOR|ECO|SECO|SECO2|SECO3)#\r\n', re.I), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*LTIM=([0-9]{1,5})#\r\n', re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*LTIM2=([0-9]{1,5})#\r\n', re.I), self.__MatchLamp2Usage, None)
            self.AddMatchString(re.compile(b'\*APPMOD=(DYNAMIC|PRESET|SRGB|CINE|USER1|USER2)#\r\n', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#\r\n', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#\r\n', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*VOL=([0-9]{1,2})#\r\n', re.I), self.__MatchVolumeStatus, None)
            self.AddMatchString(re.compile(b'(Illegal format|Block item)\r\n', re.I), self.__MatchError, None)

    def Set3DSync(self, value, qualifier):

        ValueStateValues = {
            'Sync Off': 'off',
            'Top Bottom': 'tb',
            'Frame Sequential': 'fs'
        }

        CmdString = '\r*3d={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('3DSync', CmdString, value, qualifier)

    def Update3DSync(self, value, qualifier):

        CmdString = '\r*3d=?#\r'
        self.__UpdateHelper('3DSync', CmdString, value, qualifier)

    def __Match3DSync(self, match, tag):

        ValueStateValues = {
            'OFF': 'Sync Off',
            'TB': 'Top Bottom',
            'FS': 'Frame Sequential'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('3DSync', value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'AUTO',
            'Real': 'REAL',
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10'
        }

        AspectRatioCmdString = '\r*asp={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'AUTO': 'Auto',
            'REAL': 'Real',
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        AudioMuteCmdString = '\r*mute={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

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

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        FreezeCmdString = '\r*freeze={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

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
            'Computer/YPbPr': 'RGB',
            'Computer 2/YPbPr 2': 'RGB2',
            'HDMI': 'hdmi',
            'Composite': 'vid',
            'S-Video': 'svid',
            'Network': 'network',
            'USB Display': 'usbdisplay',
            'USB Reader': 'usbreader'
        }

        InputCmdString = '\r*sour={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'RGB': 'Computer/YPbPr',
            'RGB2': 'Computer 2/YPbPr 2',
            'HDMI': 'HDMI',
            'VID': 'Composite',
            'SVID': 'S-Video',
            'NETWORK': 'Network',
            'USBDISPLAY': 'USB Display',
            'USBREADER': 'USB Reader'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'lnor',
            'Eco': 'eco',
            'Smart Eco': 'seco',
            'Smart Eco 2': 'seco2',
            'Smart Eco 3': 'seco3'
        }

        LampModeCmdString = '\r*lampm={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):
        ValueStateValues = {
            'LNOR': 'Normal',
            'ECO': 'Eco',
            'SECO': 'Smart Eco',
            'SECO2': 'Smart Eco 2',
            'SECO3': 'Smart Eco 3'
        }
        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = '\r*ltim=?#\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def UpdateLamp2Usage(self, value, qualifier):
        Lamp2UsageCmdString = '\r*ltim2=?#\r'
        self.__UpdateHelper('Lamp2Usage', Lamp2UsageCmdString, value, qualifier)

    def __MatchLamp2Usage(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('Lamp2Usage', value, None)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Enter': 'enter',
            'Menu On': 'menu=on',
            'Menu Off': 'menu=off'
        }

        MenuNavigationCmdString = '\r*{0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):
        ValueStateValues = {
            'Dynamic': 'dynamic',
            'Presentation': 'preset',
            'sRGB': 'srgb',
            'Cinema': 'cine',
            'User 1': 'user1',
            'User 2': 'user2'
        }

        PictureModeCmdString = '\r*appmod={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\r*appmod=?#\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'DYNAMIC': 'Dynamic',
            'PRESET': 'Presentation',
            'SRGB': 'sRGB',
            'CINE': 'Cinema',
            'USER1': 'User 1',
            'USER2': 'User 2'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        PowerCmdString = '\r*pow={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        VideoMuteCmdString = '\r*blank={0}#\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

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

        VolumeCmdString = '\r*vol={0}#\r'.format(ValueStateValues[value])
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
