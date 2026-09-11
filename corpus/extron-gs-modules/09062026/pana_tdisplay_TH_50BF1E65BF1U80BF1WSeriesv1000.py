from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import re
import hashlib
import binascii

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
        
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QAS:(ZOOM|FULL|JUST|NORM|ZOM2|ZOM3|SJST|SNOM|SFUL|14:9)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QMI:(HM1|HM2|SL1|S1A|S1B|VD1|YP1|DV1|PC1|DL1|MG1|NW1|MV1|WB1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QPC:MEN(STD|DYN|CNM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QDW:(PIP\r?([0-3])|OFF)\x03'), self.__MatchPIP, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QSI:(HM1|HM2|SL1|S1A|S1B|VD1|YP1|DV1|PC1|DL1|NW1)\x03'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QDW:MOD(PIP|PIW)\x03'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QDW:SIZ([1-4])\x03'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD:\d\d\d;QAV:([0-9]{2})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(ER401)'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        ID = value
        if ID == 'Broadcast':
            self.Header = '\x02AD94;RAD:000;'
            self._DeviceID = value
        elif 1 <= int(ID) <= 100:
            self.Header = '\x02AD94;RAD:{0:03d};'.format(int(ID))
            self._DeviceID = value
        else:
            print('Device ID must be between 1 and 100 or Broadcast')        

    def CommandStringBuild(self, command, commandstring):
        return self.Header + commandstring

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Zoom 1': 'ZOOM',
            '16:9': 'FULL',
            'Just': 'JUST',
            '4:3': 'NORM',
            'Zoom 2': 'ZOM2',
            'Zoom 3': 'ZOM3',
            'Side Cut Just': 'SJST',
            '4:3 Side Cut': 'SNOM',
            '4:3 Full': 'SFUL',
            '14:9': '14:9'
        }

        AspectRatioCmdString = 'DAM:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'QAS\x03'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'ZOOM': 'Zoom 1',
            'FULL': '16:9',
            'JUST': 'Just',
            'NORM': '4:3',
            'ZOM2': 'Zoom 2',
            'ZOM3': 'Zoom 3',
            'SJST': 'Side Cut Just',
            'SNOM': '4:3 Side Cut',
            'SFUL': '4:3 Full',
            '14:9': '14:9'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = 'AMT:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'QAM\x03'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'DGE:ASU1\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'IMS:HM1',
            'HDMI 2': 'IMS:HM2',
            'Slot': 'IMS:SL1',
            'Slot A': 'IMS:S1A',
            'Slot B': 'IMS:S1B',
            'Video': 'IMS:VD1',
            'Component': 'IMS:YP1',
            'PC': 'IMS:PC1',
            'DVI': 'IMS:DV1',
            'Digital Link': 'IMS:DL1',
            'Miracast': 'IMS:MG1',
            'Panasonic Application': 'IMS:NW1',
            'Memory Viewer': 'IMS:MV1',
            'Whiteboard': 'IMS:WB1'
        }

        InputCmdString = '{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'QMI\x03'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'SL1': 'Slot',
            'S1A': 'Slot A',
            'S1B': 'Slot B',
            'VD1': 'Video',
            'YP1': 'Component',
            'PC1': 'PC',
            'DV1': 'DVI',
            'DL1': 'Digital Link',
            'MG1': 'Miracast',
            'NW1': 'Panasonic Application',
            'MV1': 'Memory Viewer',
            'WB1': 'Whiteboard'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': 'OSP:OSD1\x03',
            'Off': 'VDO\x03'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CNM'
        }

        PictureModeCmdString = 'VPC:MEN{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = 'QPC:MEN\x03'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'STD': 'Normal',
            'DYN': 'Dynamic',
            'CNM': 'Cinema'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Off': 'DWA:OFF\x03',
            'Picture In Picture': 'DWA:PIP\x03'
        }

        PIPCmdString = ValueStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        PIPCmdString = 'QDW\x03'
        self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)

    def __MatchPIP(self, match, tag):

        PIPPositionStateValues = {
            '0': 'Lower Right',
            '3': 'Upper Right',
            '1': 'Lower Left',
            '2': 'Upper Left'
        }

        if match.group(1).decode() == 'OFF':
            self.WriteStatus('PIP', 'Off', None)
        elif 'PIP' in match.group(1).decode():
            PIPPosition = PIPPositionStateValues[match.group(2).decode()]
            self.WriteStatus('PIP', 'Picture In Picture', None)
            self.WriteStatus('PIPPosition', PIPPosition, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'ISS:HM1',
            'HDMI 2': 'ISS:HM2',
            'Slot': 'ISS:SL1',
            'Slot A': 'ISS:S1A',
            'Slot B': 'ISS:S1B',
            'Video': 'ISS:VD1',
            'Component': 'ISS:YP1',
            'PC': 'ISS:PC1',
            'DVI': 'ISS:DV1',
            'Digital Link': 'ISS:DL1',
            'Panasonic Application': 'ISS:NW1',
        }

        PIPInputCmdString = '{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = 'QSI\x03'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'SL1': 'Slot',
            'S1A': 'Slot A',
            'S1B': 'Slot B',
            'VD1': 'Video',
            'YP1': 'Component',
            'PC1': 'PC',
            'DV1': 'DVI',
            'DL1': 'Digital Link',
            'NW1': 'Panasonic Application',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Picture In Picture': 'DWA:MODPIP\x03',
            'Picture In Whiteboard': 'DWA:MODPIW\x03'
        }
        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = 'QDW:MOD\x03'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            'PIP': 'Picture In Picture',
            'PIW': 'Picture In Whiteboard'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Lower Right': 'DWA:PIN0\x03',
            'Upper Right': 'DWA:PIN3\x03',
            'Lower Left': 'DWA:PIN1\x03',
            'Upper Left': 'DWA:PIN2\x03'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        self.UpdatePIP(value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            '1': 'DWA:SIZ1\x03',
            '2': 'DWA:SIZ2\x03',
            '3': 'DWA:SIZ3\x03',
            '4': 'DWA:SIZ4\x03'
        }

        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'QDW:SIZ\x03'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'DWA:SWP\x03'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON\x03',
            'Off': 'POF\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'QPW\x03'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = 'VMT:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'QVM\x03'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'AVL:{0:02d}\x03'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'QAV\x03'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = self.CommandStringBuild(command, commandstring)
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        commandstring = self.CommandStringBuild(command, commandstring)
        self.Send(commandstring)


    def __MatchError(self, match, tag):
        print('Invalid Command Reply.')

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.md5hash = ''
        self.Security = False
        
        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(ZOOM|FULL|JUST|NORM|ZOM2|ZOM3|SJST|SNOM|SFUL|14:9)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|HM2|SL1|S1A|S1B|VD1|YP1|DV1|PC1|DL1|MG1|NW1|MV1|WB1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(STD|DYN|CNM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QDW:(PIP\r?([0-3])|OFF)\x03'), self.__MatchPIP, None)
            self.AddMatchString(re.compile(b'\x02QSI:(HM1|HM2|SL1|S1A|S1B|VD1|YP1|DV1|PC1|DL1|NW1)\x03'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x02QDW:MOD(PIP|PIW)\x03'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\x02QDW:SIZ([1-4])\x03'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\x02QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-9]{2})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(ERR[1-5]|ER401|PDPCONTROL ERRA)'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        
        if self.devicePassword is None:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.md5(full_str.encode())
            self.md5hash = binascii.hexlify(code_hash.digest()).decode()
            self.Security = True
        else:
            self.MissingCredentialsLog('Password')

    def __MatchNoAuthentication(self, match, tag):

        self.Security = False

    def CommandStringBuild(self, command, commandstring):
        if self.Security:
            commandstring = self.md5hash + commandstring + '\r'
        else:
            commandstring = commandstring + '\r'
        return commandstring

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Zoom 1': 'ZOOM',
            '16:9': 'FULL',
            'Just': 'JUST',
            '4:3': 'NORM',
            'Zoom 2': 'ZOM2',
            'Zoom 3': 'ZOM3',
            'Side Cut Just': 'SJST',
            '4:3 Side Cut': 'SNOM',
            '4:3 Full': 'SFUL',
            '14:9': '14:9'
        }

        AspectRatioCmdString = '\x02DAM:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x02QAS\x03'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'ZOOM': 'Zoom 1',
            'FULL': '16:9',
            'JUST': 'Just',
            'NORM': '4:3',
            'ZOM2': 'Zoom 2',
            'ZOM3': 'Zoom 3',
            'SJST': 'Side Cut Just',
            'SNOM': '4:3 Side Cut',
            'SFUL': '4:3 Full',
            '14:9': '14:9'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '\x02AMT:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x02QAM\x03'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02DGE:ASU1\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'IMS:HM1',
            'HDMI 2': 'IMS:HM2',
            'Slot': 'IMS:SL1',
            'Slot A': 'IMS:S1A',
            'Slot B': 'IMS:S1B',
            'Video': 'IMS:VD1',
            'Component': 'IMS:YP1',
            'PC': 'IMS:PC1',
            'DVI': 'IMS:DV1',
            'Digital Link': 'IMS:DL1',
            'Miracast': 'IMS:MG1',
            'Panasonic Application': 'IMS:NW1',
            'Memory Viewer': 'IMS:MV1',
            'Whiteboard': 'IMS:WB1'
        }

        InputCmdString = '\x02{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x02QMI\x03'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'SL1': 'Slot',
            'S1A': 'Slot A',
            'S1B': 'Slot B',
            'VD1': 'Video',
            'YP1': 'Component',
            'PC1': 'PC',
            'DV1': 'DVI',
            'DL1': 'Digital Link',
            'MG1': 'Miracast',
            'NW1': 'Panasonic Application',
            'MV1': 'Memory Viewer',
            'WB1': 'Whiteboard'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02OSP:OSD1\x03',
            'Off': '\x02VDO\x03'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CNM'
        }

        PictureModeCmdString = '\x02VPC:MEN{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\x02QPC:MEN\x03'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'STD': 'Normal',
            'DYN': 'Dynamic',
            'CNM': 'Cinema'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Off': '\x02DWA:OFF\x03',
            'Picture In Picture': '\x02DWA:PIP\x03'
        }

        PIPCmdString = ValueStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        PIPCmdString = '\x02QDW\x03'
        self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)

    def __MatchPIP(self, match, tag):

        PIPPositionStateValues = {
            '0': 'Lower Right',
            '3': 'Upper Right',
            '1': 'Lower Left',
            '2': 'Upper Left'
        }

        if match.group(1).decode() == 'OFF':
            self.WriteStatus('PIP', 'Off', None)
        elif 'PIP' in match.group(1).decode():
            PIPPosition = PIPPositionStateValues[match.group(2).decode()]
            self.WriteStatus('PIP', 'Picture In Picture', None)
            self.WriteStatus('PIPPosition', PIPPosition, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'ISS:HM1',
            'HDMI 2': 'ISS:HM2',
            'Slot': 'ISS:SL1',
            'Slot A': 'ISS:S1A',
            'Slot B': 'ISS:S1B',
            'Video': 'ISS:VD1',
            'Component': 'ISS:YP1',
            'PC': 'ISS:PC1',
            'DVI': 'ISS:DV1',
            'Digital Link': 'ISS:DL1',
            'Panasonic Application': 'ISS:NW1',
        }

        PIPInputCmdString = '\x02{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '\x02QSI\x03'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'SL1': 'Slot',
            'S1A': 'Slot A',
            'S1B': 'Slot B',
            'VD1': 'Video',
            'YP1': 'Component',
            'PC1': 'PC',
            'DV1': 'DVI',
            'DL1': 'Digital Link',
            'NW1': 'Panasonic Application',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Picture In Picture': '\x02DWA:MODPIP\x03',
            'Picture In Whiteboard': '\x02DWA:MODPIW\x03'
        }
        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '\x02QDW:MOD\x03'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            'PIP': 'Picture In Picture',
            'PIW': 'Picture In Whiteboard'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Lower Right': '\x02DWA:PIN0\x03',
            'Upper Right': '\x02DWA:PIN3\x03',
            'Lower Left': '\x02DWA:PIN1\x03',
            'Upper Left': '\x02DWA:PIN2\x03'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        self.UpdatePIP(value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            '1': '\x02DWA:SIZ1\x03',
            '2': '\x02DWA:SIZ2\x03',
            '3': '\x02DWA:SIZ3\x03',
            '4': '\x02DWA:SIZ4\x03'
        }

        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = '\x02QDW:SIZ\x03'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '\x02DWA:SWP\x03'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02PON\x03',
            'Off': '\x02POF\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\x02QPW\x03'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '\x02VMT:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\x02QVM\x03'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x02AVL:{0:02d}\x03'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x02QAV\x03'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = self.CommandStringBuild(command, commandstring)
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        commandstring = self.CommandStringBuild(command, commandstring)

        self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            'ERR1': 'Undefined Control Command.',
            'ERR2': 'Out of Parameter Range.',
            'ERR3': 'Busy State or No-acceptable Period.',
            'ERR4': 'Timeout or No-acceptable Period.',
            'ERR5': 'Wrong Data Length.',
            'PDPCONTROL ERRA': 'Password Mismatch.',
            'ER401': 'Invalid Command Reply.'
        }

        if match.group(1).decode() in DEVICE_ERROR_CODES.keys():
            print(DEVICE_ERROR_CODES[match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.md5hash = ''
        self.Security = False

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
