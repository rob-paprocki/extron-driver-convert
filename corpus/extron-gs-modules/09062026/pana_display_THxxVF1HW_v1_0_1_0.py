from extronlib.interface import SerialInterface, EthernetClientInterface
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Monitor'], 'Status': {}},
            'AudioMute': {'Parameters': ['Monitor'], 'Status': {}},
            'AutoImage': {'Parameters': ['Monitor'], 'Status': {}},
            'Input': {'Parameters': ['Monitor'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Monitor'], 'Status': {}},
            'PictureMode': {'Parameters': ['Monitor'], 'Status': {}},
            'Power': {'Parameters': ['Monitor'], 'Status': {}},
            'SoundMode': {'Parameters': ['Monitor'], 'Status': {}},
            'SoundOutput': {'Parameters': ['Monitor'], 'Status': {}},
            'VideoMute': {'Parameters': ['Monitor'], 'Status': {}},
            'Volume': {'Parameters': ['Monitor'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAS:(FULL|NORM|ZOOM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QMI:(HM1|DP1|DL1|DV1|DV2|PC1|YP1|VD1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QSP:OSD(0|1)\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QPC:MEN(VIV|NAT|STD|SUV|GRH|DCM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAC:MEN(STD|DYN|CLR)\x03'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAC:OUT(SPO|LNO)\x03'), self.__MatchSoundOutput, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02AD94;RAD(\d\d\d);QAV:([0-9][0-9][0-9])\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'AD94;RAD(\d\d\d);(ERR[1-5]|ER401|PDPCONTROL ERRA)\x03'), self.__MatchError, None)

    def getMonitor(self, Monitor):
        if 1 <= int(Monitor) <= 100:
            return '\x02AD94;RAD:{0:03d};'.format(int(Monitor))

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Full': 'DAM:FULL\x03',
            'Normal': 'DAM:NORM\x03',
            'Zoom 1': 'DAM:ZOOM\x03',
            'Zoom 2': 'DAM:ZOM2\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QAS\x03'
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'ZOOM': 'Zoom 1',
            'ZOM2': 'Zoom 2'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Monitor': Monitor})

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': 'AMT:1\x03',
            'Off': 'AMT:0\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QAM\x03'
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, {'Monitor': Monitor})

    def SetAutoImage(self, value, qualifier):

        CmdString = self.getMonitor(qualifier['Monitor']) + 'DGE:ASU1\x03'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'HDMI': 'IMS:HM1\x03',
            'DisplayPort': 'IMS:DP1\x03',
            'Digital Link': 'IMS:DL1\x03',
            'DVI-D1': 'IMS:DV1\x03',
            'DVI-D2': 'IMS:DV2\x03',
            'PC': 'IMS:PC1\x03',
            'Component(RGB)': 'IMS:YP1\x03',
            'Video': 'IMS:VD1\x03',
            'USB Display': 'IMS:UD1\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QMI\x03'
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'HM1': 'HDMI',
            'DP1': 'DisplayPort',
            'DL1': 'Digital Link',
            'DV1': 'DVI-D1',
            'DV2': 'DVI-D2',
            'PC1': 'PC',
            'YP1': 'Component(RGB)',
            'VD1': 'Video',
            'UD1': 'USB Display'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('Input', value, {'Monitor': Monitor})

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On': 'OSP:OSD1\x03',
            'Off': 'OSP:OSD0\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QSP:OSD\x03'
        self.__UpdateHelper('OnScreenDisplay', CmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('OnScreenDisplay', value, {'Monitor': Monitor})

    def SetPictureMode(self, value, qualifier):

        States = {
            'Vivid Signage': 'VPC:MENVIV\x03',
            'Natural Signage': 'VPC:MENNAT\x03',
            'Standard': 'VPC:MENSTD\x03',
            'Surveillance': 'VPC:MENSUV\x03',
            'Graphic': 'VPC:MENGRH\x03',
            'Dicom': 'VPC:MENDCM\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QPC:MEN\x03'
        self.__UpdateHelper('PictureMode', CmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        States = {
            'VIV': 'Vivid Signage',
            'NAT': 'Natural Signage',
            'STD': 'Standard',
            'SUV': 'Surveillance',
            'GRH': 'Graphic',
            'DCM': 'Dicom'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('PictureMode', value, {'Monitor': Monitor})

    def SetPower(self, value, qualifier):

        States = {
            'On': 'PON\x03',
            'Off': 'POF\x03'
            }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QPW\x03'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('Power', value, {'Monitor': Monitor})


    def SetSoundMode(self, value, qualifier):

        States = {
            'Standard': 'AAC:MENSTD\x03',
            'Dynamic': 'AAC:MENDYN\x03',
            'Clear': 'AAC:MENCLR\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('SoundMode', CmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QAC:MEN\x03'
        self.__UpdateHelper('SoundMode', CmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        States = {
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CLR': 'Clear'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('SoundMode', value, {'Monitor': Monitor})

    def SetSoundOutput(self, value, qualifier):

        States = {
            'Line Out': 'AAC:OUTLNO\x03',
            'Speaker Out': 'AAC:OUTSPO\x03'
        }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('SoundOutput', CmdString, value, qualifier)

    def UpdateSoundOutput(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QAC:OUT\x03'
        self.__UpdateHelper('SoundOutput', CmdString, value, qualifier)

    def __MatchSoundOutput(self, match, tag):

        States = {
            'LNO': 'Line Out',
            'SPO': 'Speaker Out'
        }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('SoundOutput', value, {'Monitor': Monitor})

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': 'VMT:1\x03',
            'Off': 'VMT:0\x03'
            }

        CmdString = self.getMonitor(qualifier['Monitor']) + States[value]
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QVM\x03'
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
            }

        Monitor = str(int(match.group(1).decode()))
        value = States[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, {'Monitor': Monitor})

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = self.getMonitor(qualifier['Monitor']) + 'AVL:{0:03d}\x03'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        CmdString = self.getMonitor(qualifier['Monitor']) + 'QAV\x03'
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        Monitor = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, {'Monitor': Monitor})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = commandstring + '\r'
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = commandstring + '\r'
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

        DEVICE_ERROR_CODES = {
                'ERR1'              : 'Undefined Control Command.',
                'ERR2'              : 'Out of Parameter Range.',
                'ERR3'              : 'Busy State or No-acceptable Period.',
                'ERR4'              : 'Timeout or No-acceptable Period.',
                'ERR5'              : 'Wrong Data Length.',
                'PDPCONTROL ERRA'   : 'Password Mismatch.',
                'ER401'             : 'Invalid Command Reply.'
            }
            
        if match.group(1).decode() in DEVICE_ERROR_CODES.keys():
            self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

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
        self.devicePassword = 'panasonic'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SoundMode': {'Status': {}},
            'SoundOutput': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.md5hash = ''
        self.Security = False
        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(FULL|NORM|ZOOM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|DP1|DL1|DV1|DV2|PC1|YP1|VD1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QSP:OSD(0|1)\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(VIV|NAT|STD|SUV|GRH|DCM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QAC:MEN(STD|DYN|CLR)\x03'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'\x02QAC:OUT(SPO|LNO)\x03'), self.__MatchSoundOutput, None)
            self.AddMatchString(re.compile(b'\x02QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-9][0-9][0-9])\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(ERR[1-5]|ER401|PDPCONTROL ERRA)'), self.__MatchError, None)

        self.AddMatchString(re.compile(b'PDPCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
        self.AddMatchString(re.compile(b'PDPCONTROL 0\r'), self.__MatchNoAuthentication, None)


    def __MatchAuthentication(self, match, tag):

        EncodeString = (self.devicePassword + match.group(1).decode()).encode()
        code_hash = hashlib.md5(EncodeString)
        self.md5hash = binascii.hexlify(code_hash.digest()).decode()
        self.Security = True
        self.Authenticated = True

    def __MatchNoAuthentication(self, match, tag):

        self.Security = False
        self.Authenticated = True

    def CommandStringBuild(self, command, commandstring):
        if self.Security == True:
            commandstring = self.md5hash + commandstring + '\r'
        else:
            commandstring = commandstring + '\r'
        return commandstring

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': '\x02DAM:FULL\x03',
            'Normal': '\x02DAM:NORM\x03',
            'Zoom 1': '\x02DAM:ZOOM\x03',
            'Zoom 2': '\x02DAM:ZOM2\x03'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x02QAS\x03'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'ZOOM': 'Zoom 1',
            'ZOM2': 'Zoom 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AMT:1\x03',
            'Off': '\x02AMT:0\x03'
        }

        AudioMuteCmdString = ValueStateValues[value]
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
            'HDMI': '\x02IMS:HM1\x03',
            'DisplayPort': '\x02IMS:DP1\x03',
            'Digital Link': '\x02IMS:DL1\x03',
            'DVI-D1': '\x02IMS:DV1\x03',
            'DVI-D2': '\x02IMS:DV2\x03',
            'PC': '\x02IMS:PC1\x03',
            'Component(RGB)': '\x02IMS:YP1\x03',
            'Video': '\x02IMS:VD1\x03',
            'USB Display': '\x02IMS:UD1\x03'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x02QMI\x03'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI',
            'DP1': 'DisplayPort',
            'DL1': 'Digital Link',
            'DV1': 'DVI-D1',
            'DV2': 'DVI-D2',
            'PC1': 'PC',
            'YP1': 'Component(RGB)',
            'VD1': 'Video',
            'UD1': 'USB Display'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02OSP:OSD1\x03',
            'Off': '\x02OSP:OSD0\x03'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '\x02QSP:OSD\x03'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid Signage': '\x02VPC:MENVIV\x03',
            'Natural Signage': '\x02VPC:MENNAT\x03',
            'Standard': '\x02VPC:MENSTD\x03',
            'Surveillance': '\x02VPC:MENSUV\x03',
            'Graphic': '\x02VPC:MENGRH\x03',
            'Dicom': '\x02VPC:MENDCM\x03'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\x02QPC:MEN\x03'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'VIV': 'Vivid Signage',
            'NAT': 'Natural Signage',
            'STD': 'Standard',
            'SUV': 'Surveillance',
            'GRH': 'Graphic',
            'DCM': 'Dicom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

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

    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '\x02AAC:MENSTD\x03',
            'Dynamic': '\x02AAC:MENDYN\x03',
            'Clear': '\x02AAC:MENCLR\x03'
        }

        SoundModeCmdString = ValueStateValues[value]
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = '\x02QAC:MEN\x03'
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CLR': 'Clear'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetSoundOutput(self, value, qualifier):

        ValueStateValues = {
            'Line Out': '\x02AAC:OUTLNO\x03',
            'Speaker Out': '\x02AAC:OUTSPO\x03'
        }

        SoundOutputCmdString = ValueStateValues[value]
        self.__SetHelper('SoundOutput', SoundOutputCmdString, value, qualifier)

    def UpdateSoundOutput(self, value, qualifier):

        SoundOutputCmdString = '\x02QAC:OUT\x03'
        self.__UpdateHelper('SoundOutput', SoundOutputCmdString, value, qualifier)

    def __MatchSoundOutput(self, match, tag):

        ValueStateValues = {
            'LNO': 'Line Out',
            'SPO': 'Speaker Out'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundOutput', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02VMT:1\x03',
            'Off': '\x02VMT:0\x03'
        }

        VideoMuteCmdString = ValueStateValues[value]
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
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x02AVL:{0}\x03'.format(str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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

        commandstring = self.CommandStringBuild(command, commandstring)
        if self.Unidirectional == 'True' or self.Authenticated == False:
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

        DEVICE_ERROR_CODES = {
                'ERR1'              : 'Undefined Control Command.',
                'ERR2'              : 'Out of Parameter Range.',
                'ERR3'              : 'Busy State or No-acceptable Period.',
                'ERR4'              : 'Timeout or No-acceptable Period.',
                'ERR5'              : 'Wrong Data Length.',
                'PDPCONTROL ERRA'   : 'Password Mismatch.',
                'ER401'             : 'Invalid Command Reply.'
            }
           
        State = match.group(1).decode()
         
        if State in DEVICE_ERROR_CODES.keys():
            self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])
        if State == 'PDPCONTROL ERRA':
            self.Authenticated = False
        
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.md5hash = ''
        self.Security = False
        self.Authenticated = False
        

    
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
