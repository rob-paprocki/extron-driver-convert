from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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

        self.Models = {
            'PowerLite Pro G6170': self.epsn_1_1311_A,
            'PowerLite Pro G6270W': self.epsn_1_1311_A,
            'PowerLite Pro G6470WU': self.epsn_1_1311_A,
            'PowerLite Pro G6070W': self.epsn_1_1311_B,
            'PowerLite Pro G6570WU': self.epsn_1_1311_B,
            'PowerLite Pro G6770WU': self.epsn_1_1311_B,
            'PowerLite Pro G6870': self.epsn_1_1311_B,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(00|20|40|50|60)( 30)?\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CCAP=(11|12|00)\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'ERR=(00|01|04|03|07|06|08|09|0A|0B|0C|0D|0E|0F|10|11|12|13|14|15|16)\r:'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(11|14|30|41|42|B1|B4|53|70|80)\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(00|01|A0)\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,5})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(00|01|02|03|04|05|09)\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r:'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '16:9': 'ASPECT 20\r',
            'Auto': 'ASPECT 30\r',
            'Full': 'ASPECT 40\r',
            'Zoom': 'ASPECT 50\r',
            'Native': 'ASPECT 60\r'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '20': '16:9',
            '00': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native'
            }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        AVMuteState = {
            'On': 'MUTE ON\r',
            'Off': 'MUTE OFF\r'
            }

        AVMuteCmdString = AVMuteState[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        AVMuteState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        value = AVMuteState[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'CC1': 'CCAP 11\r',
            'CC2': 'CCAP 12\r',
            'Off': 'CCAP 00\r'
            }

        ClosedCaptionCmdString = ClosedCaptionState[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionState = {
            '11': 'CC1',
            '12': 'CC2',
            '00': 'Off'
            }

        value = ClosedCaptionState[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusState = {
            '00': 'Normal',
            '01': 'Fan Error',
            '04': 'Internal Temperature is Abnormally High',
            '03': 'Lamp Burnt-out',
            '07': 'Lamp Cover Error',
            '06': 'Lamp Error',
            '08': 'Filter Error',
            '09': 'EDL Capacitor Disconnected',
            '0A': 'Auto Iris Error',
            '0B': 'Subsystem Error',
            '0C': 'Low Air Flow Error',
            '0D': 'Air Flow Error',
            '0E': 'Power Supply Error',
            '0F': 'Shutter Failure',
            '10': 'Cooling System Error',
            '11': 'Cooling System Error (Pump)',
            '12': 'Static Iris Error',
            '13': 'Power Supply Unit Error (Disagreement of Ballast)',
            '14': 'Exhaust Shutter Error',
            '15': 'Obstacle Detection Error',
            '16': 'IF Board Discernment Error'
            }

        value = DeviceStatusState[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': 'FREEZE ON\r',
            'Off': 'FREEZE OFF\r'
            }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        value = FreezeState[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = self.SetInputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.GetInputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal': 'LUMINANCE 00\r',
            'Eco': 'LUMINANCE 01\r',
            'Temperature sensitive': 'LUMINANCE A0\r'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeState = {
            '00': 'Normal',
            '01': 'Eco',
            'A0': 'Temperature sensitive'
            }

        value = LampModeState[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetPower(self, value, qualifier):

        if value == 'On':
            self.__SetHelper('Power', 'PWR ON\r', value, qualifier)
        elif value == 'Off':
            self.__SetHelper('Power', 'PWR OFF\r', value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '01': 'On',
            '00': 'Off',
            '04': 'Off',
            '05': 'Off',
            '09': 'Off',
            '02': 'Warming Up',
            '03': 'Cooling Down'
            }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 20
            }
        VolumeStateTable = {
            0: 0,
            1: 12,
            2: 24,
            3: 36,
            4: 48,
            5: 60,
            6: 73,
            7: 85,
            8: 97,
            9: 109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOL {0}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) // 12
        if value > 20:
            value = 20
        self.WriteStatus('Volume', value, None)

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
        print('Error Occurred')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False



    def epsn_1_1311_A(self):
        self.SetInputState = {
            'Computer 1 RGB' : 'SOURCE 11\r', 
            'Computer 1 YPbPr' : 'SOURCE 14\r', 
            'HDMI' : 'SOURCE 30\r', 
            'Video' : 'SOURCE 41\r', 
            'S-Video' : 'SOURCE 42\r', 
            'BNC (RGB)' : 'SOURCE B1\r', 
            'BNC (Component)' : 'SOURCE B4\r',
            'LAN' : 'SOURCE 53\r', 
            'Display Port' : 'SOURCE 70\r'
            }

        self.GetInputState = {
            '11' : 'Computer 1 RGB', 
            '14' : 'Computer 1 YPbPr', 
            '30' : 'HDMI', 
            '41' : 'Video', 
            '42' : 'S-Video', 
            'B1' : 'BNC (RGB)', 
            'B4' : 'BNC (Component)',
            '53' : 'LAN', 
            '70' : 'Display Port'
            }


    def epsn_1_1311_B(self):
        self.SetInputState = {
            'Computer 1 RGB' : 'SOURCE 11\r', 
            'Computer 1 YPbPr' : 'SOURCE 14\r', 
            'HDMI' : 'SOURCE 30\r', 
            'Video' : 'SOURCE 41\r', 
            'S-Video' : 'SOURCE 42\r', 
            'BNC (RGB)' : 'SOURCE B1\r', 
            'BNC (Component)' : 'SOURCE B4\r',
            'LAN' : 'SOURCE 53\r', 
            'Display Port' : 'SOURCE 70\r',
            'HDBaseT' : 'SOURCE 80\r'
            }

        self.GetInputState = {
            '11' : 'Computer 1 RGB', 
            '14' : 'Computer 1 YPbPr', 
            '30' : 'HDMI', 
            '41' : 'Video', 
            '42' : 'S-Video', 
            'B1' : 'BNC (RGB)', 
            'B4' : 'BNC (Component)',
            '53' : 'LAN', 
            '70' : 'Display Port',
            '80' : 'HDBaseT'
            }
        
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

class DeviceEthernetClass:

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

        self.Models = {
            'PowerLite Pro G6170': self.epsn_1_1311_A,
            'PowerLite Pro G6270W': self.epsn_1_1311_A,
            'PowerLite Pro G6470WU': self.epsn_1_1311_A,
            'PowerLite Pro G6070W': self.epsn_1_1311_B,
            'PowerLite Pro G6570WU': self.epsn_1_1311_B,
            'PowerLite Pro G6770WU': self.epsn_1_1311_B,
            'PowerLite Pro G6870': self.epsn_1_1311_B,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(00|20|40|50|60)( 30)?\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CCAP=(11|12|00)\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(11|14|30|41|42|B1|B4|53|70|80)\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(00|01|A0)\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,5})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(00|01|02|03|04|05|09)\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r:'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)
            

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '16:9': 'ASPECT 20\r',
            'Auto': 'ASPECT 30\r',
            'Full': 'ASPECT 40\r',
            'Zoom': 'ASPECT 50\r',
            'Native': 'ASPECT 60\r'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioState = {
            '20': '16:9',
            '00': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native'
            }

        value = AspectRatioState[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        AVMuteState = {
            'On': 'MUTE ON\r',
            'Off': 'MUTE OFF\r'
            }

        AVMuteCmdString = AVMuteState[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        AVMuteState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        value = AVMuteState[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'CC1': 'CCAP 11\r',
            'CC2': 'CCAP 12\r',
            'Off': 'CCAP 00\r'
            }

        ClosedCaptionCmdString = ClosedCaptionState[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionState = {
            '11': 'CC1',
            '12': 'CC2',
            '00': 'Off'
            }

        value = ClosedCaptionState[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': 'FREEZE ON\r',
            'Off': 'FREEZE OFF\r'
            }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeState = {
            'ON': 'On',
            'OFF': 'Off'
            }

        value = FreezeState[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = self.SetInputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.GetInputState[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal': 'LUMINANCE 00\r',
            'Eco': 'LUMINANCE 01\r',
            'Temperature sensitive': 'LUMINANCE A0\r'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeState = {
            '00': 'Normal',
            '01': 'Eco',
            'A0': 'Temperature sensitive'
            }

        value = LampModeState[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetPower(self, value, qualifier):

        if value == 'On':
            self.__SetHelper('Power', 'PWR ON\r', value, qualifier)
        elif value == 'Off':
            self.__SetHelper('Power', 'PWR OFF\r', value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerState = {
            '01': 'On',
            '00': 'Off',
            '04': 'Off',
            '05': 'Off',
            '09': 'Off',
            '02': 'Warming Up',
            '03': 'Cooling Down'
            }

        value = PowerState[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 20
            }
        VolumeStateTable = {
            0: 0,
            1: 12,
            2: 24,
            3: 36,
            4: 48,
            5: 60,
            6: 73,
            7: 85,
            8: 97,
            9: 109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOL {0}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) // 12
        if value > 20:
            value = 20
        self.WriteStatus('Volume', value, None)

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
                self.OnDisconnected
            self.Send(commandstring)

    def __MatchError(self, match, tag):
        print('Error Occurred')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def epsn_1_1311_A(self):
        self.SetInputState = {
            'Computer 1 RGB' : 'SOURCE 11\r', 
            'Computer 1 YPbPr' : 'SOURCE 14\r', 
            'HDMI' : 'SOURCE 30\r', 
            'Video' : 'SOURCE 41\r', 
            'S-Video' : 'SOURCE 42\r', 
            'BNC (RGB)' : 'SOURCE B1\r', 
            'BNC (Component)' : 'SOURCE B4\r',
            'LAN' : 'SOURCE 53\r', 
            'Display Port' : 'SOURCE 70\r'
            }

        self.GetInputState = {
            '11' : 'Computer 1 RGB', 
            '14' : 'Computer 1 YPbPr', 
            '30' : 'HDMI', 
            '41' : 'Video', 
            '42' : 'S-Video', 
            'B1' : 'BNC (RGB)', 
            'B4' : 'BNC (Component)',
            '53' : 'LAN', 
            '70' : 'Display Port'
            }


    def epsn_1_1311_B(self):
        self.SetInputState = {
            'Computer 1 RGB' : 'SOURCE 11\r', 
            'Computer 1 YPbPr' : 'SOURCE 14\r', 
            'HDMI' : 'SOURCE 30\r', 
            'Video' : 'SOURCE 41\r', 
            'S-Video' : 'SOURCE 42\r', 
            'BNC (RGB)' : 'SOURCE B1\r', 
            'BNC (Component)' : 'SOURCE B4\r',
            'LAN' : 'SOURCE 53\r', 
            'Display Port' : 'SOURCE 70\r',
            'HDBaseT' : 'SOURCE 80\r'
            }

        self.GetInputState = {
            '11' : 'Computer 1 RGB', 
            '14' : 'Computer 1 YPbPr', 
            '30' : 'HDMI', 
            '41' : 'Video', 
            '42' : 'S-Video', 
            'B1' : 'BNC (RGB)', 
            'B4' : 'BNC (Component)',
            '53' : 'LAN', 
            '70' : 'Display Port',
            '80' : 'HDBaseT'
            }

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result
