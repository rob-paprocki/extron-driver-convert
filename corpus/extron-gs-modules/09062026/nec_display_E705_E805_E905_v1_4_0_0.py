from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, Timer
import re
from struct import pack
from binascii import hexlify


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
        self._DeviceID = 0x41
        self.SixHundredSecs = None
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ImageFlip': {'Status': {}},
            'Input': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPAspectRatio': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'TVChannel': {'Status': {}},
            'TVChannelCommand': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        try:
            self.group_id_map = {
                'Broadcast': 0x2A,
                'Group A': 0x31,
                'Group B': 0x32,
                'Group C': 0x33,
                'Group D': 0x34,
                'Group E': 0x35,
                'Group F': 0x36,
                'Group G': 0x37,
                'Group H': 0x38,
                'Group I': 0x39,
                'Group J': 0x3A
            }
        except:
            print('Invalid DeviceID parameter, Range is from 1 - 100 or Broadcast or Group A to Group J')
            
        

        if self.Unidirectional == 'False' and 0x41 <= self._DeviceID <= 0xA4:
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x32\x37\x30\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x30-\x37])\x03[\x00-\xFF]\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x32\x32\x45\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x30-\x41])\x03[\x00-\xFF]\x0D'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x30\x38\x44\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x31\x32])\x03[\x00-\xFF]\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x32\x44\x37\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x30-\x34])\x03[\x00-\xFF]\x0D'), self.__MatchImageFlip, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x30\x36\x30\x30\x30[\x00-\xFF]{6}([\x30|\x31][\x30-\x46])\x03[\x00-\xFF]\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x32\x31\x41\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x30-\x39])\x03[\x00-\xFF]\x0D'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x31\x30\x38\x33\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x30-\x34])\x03[\x00-\xFF]\x0D'), self.__MatchPIPAspectRatio, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x32\x37\x33\x30\x30[\x00-\xFF]{4}\x30\x30([\x30-\x46]{2})\x03[\x00-\xFF]\x0D'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x32\x37\x32\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x30-\x36])\x03[\x00-\xFF]\x0D'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x42\x31\x32\x02\x30\x32\x30\x30\x44\x36\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x31-\x34])\x03[\x00-\xFF]\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x31\x30\x42\x36\x30\x30[\x00-\xFF]{4}\x30\x30\x30([\x31\x32])\x03[\x00-\xFF]\x0D'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4]\x44\x31\x32\x02\x30\x30\x30\x30\x36\x32\x30\x30[\x00-\xFF]{4}\x30\x30([\x30-\x46]{2})\x03[\x00-\xFF]\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x01\x30\x30[\x41-\xA4].*\x02\x30\x31'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        temp = value
        if temp in self.group_id_map:
            self._DeviceID = self.group_id_map[temp]
        elif 1 <= int(temp) <= 100:
            self._DeviceID = 0x40 + int(temp)
        else:
            print('Invalid DeviceID parameter, Range is from 1 - 100 or Broadcast or Group A to Group J')


    def To_keep_alive(self):
        command_string = pack('>BB10s', 0x30, self._DeviceID, b'0A06\x0201D6\x03')

        checksum = 0
        for i in command_string:
            checksum ^= i

        PowerCmdString = b'HELLOW\x01' + command_string + pack('>B', checksum) + b'\x0D'
        try:
            self.Send(PowerCmdString)
        except:
            #Ethernet in the case of module not being connected
            pass    
        self.SixHundredSecs.Restart()            
     

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x30\x03',
            'Normal': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x31\x03',
            'Full': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x32\x03',
            'Wide': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x33\x03',
            'Zoom': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x34\x03',
            'Dynamic': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x36\x03',
            '1:1': b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x37\x03'
        }
        AspectRatioCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in AspectRatioCmdStringTemp:
            checksum ^= i
        AspectRatioCmdString = b'\x01' + AspectRatioCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x30\x03')
        checksum = 0
        for i in AspectRatioCmdStringTemp:
            checksum ^= i
        AspectRatioCmdString = b'\x01' + AspectRatioCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x30': 'No Mean',
            b'\x31': 'Normal',
            b'\x32': 'Full',
            b'\x33': 'Wide',
            b'\x34': 'Zoom',
            b'\x36': 'Dynamic',
            b'\x37': '1:1'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x30\x03',
            'IN 1': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x31\x03',
            'IN 2': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x32\x03',
            'HDMI 1': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x34\x03',
            'Option': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x36\x03',
            'DisplayPort': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x37\x03',
            'HDMI 2': b'\x30\x45\x30\x41\x02\x30\x32\x32\x45\x30\x30\x30\x41\x03'
        }
        AudioInputCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in AudioInputCmdStringTemp:
            checksum ^= i
        AudioInputCmdString = b'\x01' + AudioInputCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        AudioInputCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x32\x32\x45\x03')
        checksum = 0
        for i in AudioInputCmdStringTemp:
            checksum ^= i
        AudioInputCmdString = b'\x01' + AudioInputCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def __MatchAudioInput(self, match, tag):

        ValueStateValues = {
            b'\x30': 'No Mean',
            b'\x31': 'IN 1',
            b'\x32': 'IN 2',
            b'\x34': 'HDMI 1',
            b'\x36': 'Option',
            b'\x37': 'DisplayPort',
            b'\x41': 'HDMI 2'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioInput', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x31\x03',
            'Off': b'\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x32\x03'
        }
        AudioMuteCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in AudioMuteCmdStringTemp:
            checksum ^= i
        AudioMuteCmdString = b'\x01' + AudioMuteCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x30\x38\x44\x03')

        checksum = 0
        for i in AudioMuteCmdStringTemp:
            checksum ^= i
        AudioMuteCmdString = b'\x01' + AudioMuteCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x32': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, b'\x30\x45\x30\x41\x02\x30\x30\x31\x45\x30\x30\x30\x31\x03')

        checksum = 0
        for i in AutoImageCmdStringTemp:
            checksum ^= i
        AutoImageCmdString = b'\x01' + AutoImageCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('AutoSetup', AutoImageCmdString, value, qualifier)  # required according to protocol

    def SetImageFlip(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x32\x44\x37\x30\x30\x30\x30\x03',
            'None': b'\x30\x45\x30\x41\x02\x30\x32\x44\x37\x30\x30\x30\x31\x03',
            'H Flip': b'\x30\x45\x30\x41\x02\x30\x32\x44\x37\x30\x30\x30\x32\x03',
            'V Flip': b'\x30\x45\x30\x41\x02\x30\x32\x44\x37\x30\x30\x30\x33\x03',
            '180 Rotate': b'\x30\x45\x30\x41\x02\x30\x32\x44\x37\x30\x30\x30\x34\x03'
        }
        ImageFlipCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in ImageFlipCmdStringTemp:
            checksum ^= i
        ImageFlipCmdString = b'\x01' + ImageFlipCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('ImageFlip', ImageFlipCmdString, value, qualifier)

    def UpdateImageFlip(self, value, qualifier):

        ImageFlipCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x32\x44\x37\x03')

        checksum = 0
        for i in ImageFlipCmdStringTemp:
            checksum ^= i
        ImageFlipCmdString = b'\x01' + ImageFlipCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('ImageFlip', ImageFlipCmdString, value, qualifier)

    def __MatchImageFlip(self, match, tag):

        ValueStateValues = {
            b'\x30': 'No Mean',
            b'\x31': 'None',
            b'\x32': 'H Flip',
            b'\x33': 'V Flip',
            b'\x34': '180 Rotate'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ImageFlip', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x30\x03',
            'VGA': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x31\x03',
            'DVI': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x33\x03',
            'Y/Pb/Pr': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x43\x03',
            'Option': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x44\x03',
            'DisplayPort': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x46\x03',
            'HDMI 1': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x31\x03',
            'HDMI 2': b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x32\x03'
        }
        InputCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in InputCmdStringTemp:
            checksum ^= i
        InputCmdString = b'\x01' + InputCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('Input', InputCmdString, value, qualifier)  # required according to protocol

    def UpdateInput(self, value, qualifier):

        InputCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x30\x36\x30\x03')

        checksum = 0
        for i in InputCmdStringTemp:
            checksum ^= i
        InputCmdString = b'\x01' + InputCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x30\x30': 'No Mean',
            b'\x30\x31': 'VGA',
            b'\x30\x33': 'DVI',
            b'\x30\x43': 'Y/Pb/Pr',
            b'\x30\x44': 'Option',
            b'\x30\x46': 'DisplayPort',
            b'\x31\x31': 'HDMI 1',
            b'\x31\x32': 'HDMI 2'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x30\x03',
            'sRGB': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x31\x03',
            'Highbright': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x33\x03',
            'Standard': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x34\x03',
            'Cinema': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x35\x03',
            'Custom 1': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x38\x03',
            'Custom 2': b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x39\x03'
        }
        PictureModeCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in PictureModeCmdStringTemp:
            checksum ^= i
        PictureModeCmdString = b'\x01' + PictureModeCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x32\x31\x41\x03')

        checksum = 0
        for i in PictureModeCmdStringTemp:
            checksum ^= i
        PictureModeCmdString = b'\x01' + PictureModeCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            b'\x30': 'No Mean',
            b'\x31': 'sRGB',
            b'\x33': 'Highbright',
            b'\x34': 'Standard',
            b'\x35': 'Cinema',
            b'\x38': 'Custom 1',
            b'\x39': 'Custom 2'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x31\x30\x38\x33\x30\x30\x30\x30\x03',
            'Normal': b'\x30\x45\x30\x41\x02\x31\x30\x38\x33\x30\x30\x30\x31\x03',
            'Full': b'\x30\x45\x30\x41\x02\x31\x30\x38\x33\x30\x30\x30\x32\x03',
            'Wide': b'\x30\x45\x30\x41\x02\x31\x30\x38\x33\x30\x30\x30\x33\x03',
            'Zoom': b'\x30\x45\x30\x41\x02\x31\x30\x38\x33\x30\x30\x30\x34\x03'
        }
        PIPAspectRatioCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in PIPAspectRatioCmdStringTemp:
            checksum ^= i
        PIPAspectRatioCmdString = b'\x01' + PIPAspectRatioCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('PIPAspectRatio', PIPAspectRatioCmdString, value, qualifier)

    def UpdatePIPAspectRatio(self, value, qualifier):

        PIPAspectRatioCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x31\x30\x38\x33\x03')

        checksum = 0
        for i in PIPAspectRatioCmdStringTemp:
            checksum ^= i
        PIPAspectRatioCmdString = b'\x01' + PIPAspectRatioCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('PIPAspectRatio', PIPAspectRatioCmdString, value, qualifier)

    def __MatchPIPAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x30': 'No Mean',
            b'\x31': 'Normal',
            b'\x32': 'Full',
            b'\x33': 'Wide',
            b'\x34': 'Zoom'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPAspectRatio', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x30\x30\x03',
            'VGA': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x30\x31\x03',
            'DVI': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x30\x33\x03',
            'Y/Pb/Pr': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x30\x43\x03',
            'Option': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x30\x44\x03',
            'DisplayPort': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x30\x46\x03',
            'HDMI 1': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x31\x31\x03',
            'HDMI 2': b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30\x31\x32\x03'
        }
        PIPInputCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in PIPInputCmdStringTemp:
            checksum ^= i
        PIPInputCmdString = b'\x01' + PIPInputCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)  # required according to protocol

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x33\x03')

        checksum = 0
        for i in PIPInputCmdStringTemp:
            checksum ^= i
        PIPInputCmdString = b'\x01' + PIPInputCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            b'\x30\x30': 'No Mean',
            b'\x30\x31': 'VGA',
            b'\x30\x33': 'DVI',
            b'\x30\x43': 'Y/Pb/Pr',
            b'\x30\x44': 'Option',
            b'\x30\x46': 'DisplayPort',
            b'\x31\x31': 'HDMI 1',
            b'\x31\x32': 'HDMI 2'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'No Mean': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x30\x03',
            'Off': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x31\x03',
            'PIP': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x32\x03',
            'POP': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x33\x03',
            'Still': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x34\x03',
            'Picture by Picture - Aspect': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x35\x03',
            'Picture by Picture - Full': b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30\x36\x03'
        }
        PIPModeCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in PIPModeCmdStringTemp:
            checksum ^= i
        PIPModeCmdString = b'\x01' + PIPModeCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x32\x03')

        checksum = 0
        for i in PIPModeCmdStringTemp:
            checksum ^= i
        PIPModeCmdString = b'\x01' + PIPModeCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            b'\x30': 'No Mean',
            b'\x31': 'Off',
            b'\x32': 'PIP',
            b'\x33': 'POP',
            b'\x34': 'Still',
            b'\x35': 'Picture by Picture - Aspect',
            b'\x36': 'Picture by Picture - Full'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x31\x03',
            'Off': b'\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x34\x03'
        }
        PowerCmdStringTemp = pack('>BB16s', 0x30, self._DeviceID, ValueStateValues[value])
        checksum = 0
        for i in PowerCmdStringTemp:
            checksum ^= i
        PowerCmdString = b'\x01' + PowerCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)  # required according to protocol

    def UpdatePower(self, value, qualifier):

        PowerCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x41\x30\x36\x02\x30\x31\x44\x36\x03')
        checksum = 0
        for i in PowerCmdStringTemp:
            checksum ^= i
        PowerCmdString = b'\x01' + PowerCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x34': 'Off',
            b'\x32': 'Standby (Power Save)',
            b'\x33': 'Suspend (Power Save)'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetTVChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x31\x03',
            'Down': b'\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x32\x03'
        }
        TVChannelCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in TVChannelCmdStringTemp:
            checksum ^= i
        TVChannelCmdString = b'\x01' + TVChannelCmdStringTemp + pack('>B', checksum) + b'\x0D'

        self.__SetHelper('TVChannel', TVChannelCmdString, value, qualifier)

    def SetTVChannelCommand(self, value, qualifier):

        if value:
            try:
                channel = value.split('.')
                if len(channel) == 2:  # If there's a successful split for the channel
                    upper_val = int(channel[0])
                    lower_val = int(channel[1])

                    if (0 <= upper_val <= 65535) and (0 <= lower_val <= 65535):
                        upperChannel = '{0:04X}'.format(int(channel[0])).encode()
                        lowerChannel = '{0:04X}'.format(int(channel[1])).encode()
                        channelByte = b''.join([b'\x30\x41\x31\x32\x02\x43\x32\x32\x44\x30\x30\x30\x30', upperChannel, lowerChannel, b'\x03'])

                        TVChannelCommandCmdStringTemp = pack('>BB22s', 0x30, self._DeviceID, channelByte)
                        checksum = 0
                        for i in TVChannelCommandCmdStringTemp:
                            checksum ^= i
                        TVChannelCommandCmdString = b'\x01' + TVChannelCommandCmdStringTemp + pack('>B', checksum) + b'\x0D'
                        self.__SetHelper('TVChannelCommand', TVChannelCommandCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetTVChannelCommand')
                else:
                    self.Discard('Invalid Command for SetTVChannelCommand')
            except ValueError:
                self.Discard('Invalid Command for SetTVChannelCommand')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x30\x45\x30\x41\x02\x31\x30\x42\x36\x30\x30\x30\x31\x03',
            'Off': b'\x30\x45\x30\x41\x02\x31\x30\x42\x36\x30\x30\x30\x32\x03'
        }
        VideoMuteCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, ValueStateValues[value])

        checksum = 0
        for i in VideoMuteCmdStringTemp:
            checksum ^= i
        VideoMuteCmdString = b'\x01' + VideoMuteCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x31\x30\x42\x36\x03')

        checksum = 0
        for i in VideoMuteCmdStringTemp:
            checksum ^= i
        VideoMuteCmdString = b'\x01' + VideoMuteCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x32': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeValue = b'\x30\x45\x30\x41\x02\x30\x30\x36\x32\x30\x30' + hexlify(value.to_bytes(1, 'big')).upper() + b'\x03'
            VolumeCmdStringTemp = pack('>BB14s', 0x30, self._DeviceID, VolumeValue)

            checksum = 0
            for i in VolumeCmdStringTemp:
                checksum ^= i
            VolumeCmdString = b'\x01' + VolumeCmdStringTemp + pack('>B', checksum) + b'\x0D'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdStringTemp = pack('>BB10s', 0x30, self._DeviceID, b'\x30\x43\x30\x36\x02\x30\x30\x36\x32\x03')

        checksum = 0
        for i in VolumeCmdStringTemp:
            checksum ^= i
        VolumeCmdString = b'\x01' + VolumeCmdStringTemp + pack('>B', checksum) + b'\x0D'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)  # ascii encoded hex to decimal
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0x2A or 0x31 <= self._DeviceID <= 0x3A:
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
        self.Error(['An error occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        if self.ConnectionType == 'Ethernet':
            self.SixHundredSecs.Restart()


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        if self.ConnectionType == 'Ethernet':
            self.SixHundredSecs.Cancel()   

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        index = 0    # Start of possible good data

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
        self.SixHundredSecs = Wait(600, self.To_keep_alive)
        self.SixHundredSecs.Cancel()
    
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
        self.SixHundredSecs = Wait(600, self.To_keep_alive)
        self.SixHundredSecs.Cancel()
    
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
        self.SixHundredSecs = Wait(600, self.To_keep_alive)
        self.SixHundredSecs.Cancel()
          
    
    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

