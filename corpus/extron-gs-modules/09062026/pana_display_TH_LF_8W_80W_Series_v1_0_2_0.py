from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import hashlib
from binascii import hexlify

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
        
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        
        self.Models = {
            'TH-55LF80W': self.pana_10_2701_A,
            'TH-49LF80': self.pana_10_2701_A,
            'TH-42LF80W': self.pana_10_2701_A,
            'TH-42LF8W': self.pana_10_2701_B,
            'TH-49LF8W': self.pana_10_2701_B,
            'TH-55LF8W': self.pana_10_2701_B,
            'TH-42LF80': self.pana_10_2701_A,
            'TH-42LF8': self.pana_10_2701_B,
            'TH-49LF80W': self.pana_10_2701_A,
            'TH-55LF80': self.pana_10_2701_A,
            'TH-55LF8': self.pana_10_2701_B,
            'TH-49LF8': self.pana_10_2701_B,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'DigitalLinkInput': { 'Status': {}},
            'Input': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'SoundOutput': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

            
        if 'Serial' not in self.ConnectionType:



            self.Delim = b'\x0D'
            self.md5hash = b''
            self.Authenticated = 'Not Needed'
            self.AddMatchString(re.compile(b'(NTCONTROL|PDPCONTROL) 1 ([a-z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'(?:PDPCONTROL )?ERRA\r'), self.__MatchFailedPassword, None)
            
        else:
            self.Delim = b''
            self.md5hash = b''
            self.Authenticated = 'Not Needed'
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(FULL|NORM|ZOOM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QMI:DL1(HD1|HD2|PC1|PC2|SVD|VID)\x03'), self.__MatchDigitalLinkInput, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|HM2|DL1|DV1|PC1|YP1|VD1|UD1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QSP:OSD(0|1)\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(VIV|NAT|STD|SUV|GRH|DCM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QAC:MEN(STD|DYN|CLR)\x03'), self.__MatchSoundMode, None)
            self.AddMatchString(re.compile(b'\x02QAC:OUT(SPO|LNO)\x03'), self.__MatchSoundOutput, None)
            self.AddMatchString(re.compile(b'\x02QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-9][0-9][0-9])\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(ER401|ERR[1-5])'), self.__MatchError, None)

        self.PasswdPromptCount = 0
    #######################################
    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(2).decode()
        if match.group(1).decode() == 'PDPCONTROL': #Protocol 1, PDPCONTROL
            full_str = rand_num + self.devicePassword
        else: #Protocol 2, NTCONTROl
            full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Authenticated = 'Admin'

    def __MatchFailedPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper User name and Password']) 
        self.Authenticated = 'None'
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full'   : b'\x02DAM:FULL\x03',          
            'Normal' : b'\x02DAM:NORM\x03', 
            'Zoom 1' : b'\x02DAM:ZOOM\x03', 
            'Zoom 2' : b'\x02DAM:ZOM2\x03'
        }

        AspectRatioCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b''.join([self.md5hash, b'\x02QAS\x03', self.Delim])
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FULL' : 'Full', 
            'NORM' : 'Normal', 
            'ZOOM' : 'Zoom 1', 
            'ZOM2' : 'Zoom 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02AMT:1\x03', 
            'Off' : b'\x02AMT:0\x03'
        }

        AudioMuteCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b''.join([self.md5hash, b'\x02QAM\x03', self.Delim])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetDigitalLinkInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'     : b'\x02IMS:DL1HD1\x03', 
            'HDMI 2'     : b'\x02IMS:DL1HD2\x03', 
            'Computer 1' : b'\x02IMS:DL1PC1\x03', 
            'Computer 2' : b'\x02IMS:DL1PC2\x03', 
            'S-Video'    : b'\x02IMS:DL1SVD\x03', 
            'Video'      : b'\x02IMS:DL1VID\x03', 
        }

        DigitalLinkInputCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('DigitalLinkInput', DigitalLinkInputCmdString, value, qualifier)
    def UpdateDigitalLinkInput(self, value, qualifier):

        DigitalLinkInputCmdString = b''.join([self.md5hash, b'\x02QMI:DL1\x03', self.Delim])
        self.__UpdateHelper('DigitalLinkInput', DigitalLinkInputCmdString, value, qualifier)

    def __MatchDigitalLinkInput(self, match, tag):

        ValueStateValues = {
            'HD1' : 'HDMI 1', 
            'HD2' : 'HDMI 2', 
            'PC1' : 'Computer 1', 
            'PC2' : 'Computer 2', 
            'SVD' : 'S-Video', 
            'VID' : 'Video', 
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DigitalLinkInput', value, None)

    def SetInput(self, value, qualifier):

       
        InputCmdString = b''.join([self.md5hash, self.InputValues[value], self.Delim])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = b''.join([self.md5hash, b'\x02QMI\x03', self.Delim])
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.UpdateInputStates[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02OSP:OSD1\x03', 
            'Off' : b'\x02OSP:OSD0\x03'
        }

        OnScreenDisplayCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = b''.join([self.md5hash, b'\x02QSP:OSD\x03', self.Delim])
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid Signage'   : b'\x02VPC:MENVIV\x03', 
            'Natural Signage' : b'\x02VPC:MENNAT\x03', 
            'Standard'        : b'\x02VPC:MENSTD\x03', 
            'Surveillance'    : b'\x02VPC:MENSUV\x03', 
            'Graphic'         : b'\x02VPC:MENGRH\x03', 
            'Dicom'           : b'\x02VPC:MENDCM\x03'
        }

        PictureModeCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b''.join([self.md5hash, b'\x02QPC:MEN\x03', self.Delim])
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'VIV' : 'Vivid Signage', 
            'NAT' : 'Natural Signage', 
            'STD' : 'Standard', 
            'SUV' : 'Surveillance', 
            'GRH' : 'Graphic', 
            'DCM' : 'Dicom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02PON\x03', 
            'Off' : b'\x02POF\x03'
        }

        PowerCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):


        PowerCmdString = b''.join([self.md5hash, b'\x02QPW\x03', self.Delim])
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)


    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard' : b'\x02AAC:MENSTD\x03', 
            'Dynamic'  : b'\x02AAC:MENDYN\x03', 
            'Clear'    : b'\x02AAC:MENCLR\x03'
        }

        SoundModeCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)
    def UpdateSoundMode(self, value, qualifier):

        SoundModeCmdString = b''.join([self.md5hash, b'\x02QAC:MEN\x03', self.Delim])
        self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def __MatchSoundMode(self, match, tag):

        ValueStateValues = {
            'STD' : 'Standard', 
            'DYN' : 'Dynamic', 
            'CLR' : 'Clear'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundMode', value, None)

    def SetSoundOutput(self, value, qualifier):

        ValueStateValues = {
            'Speaker Out' : b'\x02AAC:OUTSPO\x03', 
            'Line Out'    : b'\x02AAC:OUTLNO\x03'
        }

        SoundOutputCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('SoundOutput', SoundOutputCmdString, value, qualifier)
    def UpdateSoundOutput(self, value, qualifier):

        SoundOutputCmdString = b''.join([self.md5hash, b'\x02QAC:OUT\x03', self.Delim])
        self.__UpdateHelper('SoundOutput', SoundOutputCmdString, value, qualifier)

    def __MatchSoundOutput(self, match, tag):

        ValueStateValues = {
            'SPO' : 'Speaker Out', 
            'LNO' : 'Line Out'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SoundOutput', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02VMT:1\x03', 
            'Off' : b'\x02VMT:0\x03'
        }

        VideoMuteCmdString = b''.join([self.md5hash, ValueStateValues[value], self.Delim])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b''.join([self.md5hash, b'\x02QVM\x03', self.Delim])
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

    
        if 0 <= value <= 100:
            VolumeCmdString = '\x02AVL:{0}\x03'.format(str(value).zfill(3))
            VolumeCmdString = b''.join([self.md5hash, VolumeCmdString.encode(), self.Delim])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b''.join([self.md5hash, b'\x02QAV\x03', self.Delim])
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == True:
                self.Discard('Inappropriate Command ' + command)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
                'ERR1'              : 'Undefined Control Command.',
                'ERR2'              : 'Out of Parameter Range.',
                'ERR3'              : 'Busy State or Unavailable Period.',
                'ERR4'              : 'Timeout or Unavailable Period.',
                'ERR5'              : 'Invalid Data Length.',
                'PDPCONTROL ERRA'   : 'Password Mismatch.',
                'ER401'             : 'Command Processing Error.'
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

        self.PasswdPromptCount = 0
    def pana_10_2701_A(self):
        self.InputValues = {
			'HDMI 1'  		: b'\x02IMS:HM1\x03',
			'HDMI 2'  		: b'\x02IMS:HM2\x03',
			'Digital Link'  : b'\x02IMS:DL1\x03',
			'DVI-D' 		: b'\x02IMS:DV1\x03',
			'PC' 		    : b'\x02IMS:PC1\x03',
			'Component' 	: b'\x02IMS:YP1\x03',
			'Video' 		: b'\x02IMS:VD1\x03',
            'USB Display'   : b'\x02IMS:UD1\x03'

		}

        self.UpdateInputStates = {
            'HM1' : 'HDMI 1', 
            'HM2' : 'HDMI 2', 
            'DL1' : 'Digital Link', 
            'DV1' : 'DVI-D', 
            'PC1' : 'PC', 
            'YP1' : 'Component', 
            'VD1' : 'Video',
            'UD1' : 'USB Display'
        }



    def pana_10_2701_B(self):
        self.InputValues = {
			'HDMI 1'  		: b'\x02IMS:HM1\x03',
			'HDMI 2'  		: b'\x02IMS:HM2\x03',
			'DVI-D' 		: b'\x02IMS:DV1\x03',
			'PC' 		    : b'\x02IMS:PC1\x03',
			'Component' 	: b'\x02IMS:YP1\x03',
			'Video' 		: b'\x02IMS:VD1\x03',
            'USB Display'   : b'\x02IMS:UD1\x03'
		}

        self.UpdateInputStates = {
            'HM1' : 'HDMI 1', 
            'HM2' : 'HDMI 2', 
            'DV1' : 'DVI-D', 
            'PC1' : 'PC', 
            'YP1' : 'Component', 
            'VD1' : 'Video',
            'UD1' : 'USB Display'
        }


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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

