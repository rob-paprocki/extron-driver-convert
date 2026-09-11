from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
from binascii import hexlify

class DeviceEthernetClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 0x41
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmbientBrightness': {'Parameters': ['Mode'], 'Status': {}},
            'AmbientCurrentIlluminance': {'Status': {}},
            'AmbientSensorRead': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Backlight': {'Status': {}},
            'Brightness': {'Status': {}},
            'ChannelNumber': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Contrast': {'Status': {}},
            'GammaCorrection': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Overscan': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'PowerSave': {'Status': {}},
            'TileHMonitor': {'Status': {}},
            'TileMatrix': {'Status': {}},
            'TileMatrixComp': {'Status': {}},
            'TilePosition': {'Status': {}},
            'TileVMonitor': {'Status': {}},
            'TVChannelStep': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 100:
            self.DeviceID = 0x40 + int(value)
        else:
            print('Invalid DeviceID parameter, range is from 1 to 100')


    def SetAmbientBrightness(self, value, qualifier):

        BrightnessStates = {
            'Low' : b'0E0A\x02103300', 
            'High' : b'0E0A\x02103400'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        if qualifier['Mode'] in BrightnessStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, self.DeviceID, BrightnessStates[qualifier['Mode']], result, b'\x03')


            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AmbientBrightnessCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AmbientBrightness', AmbientBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateAmbientBrightness(self, value, qualifier):

        BrightnessStates = {
            'Low' : b'0C06\x021033\x03', 
            'High' : b'0C06\x021034\x03'
        }

        if qualifier['Mode'] in BrightnessStates:
            buffer = pack('>BB10s', 0x30, self.DeviceID, BrightnessStates[qualifier['Mode']])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AmbientBrightnessCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('AmbientBrightness', AmbientBrightnessCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('AmbientBrightness', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Ambient Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def UpdateAmbientCurrentIlluminance(self, value, qualifier):

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x0202B4\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        AmbientCurrentIlluminanceCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AmbientCurrentIlluminance', AmbientCurrentIlluminanceCmdString, value, qualifier)

        if res:
            try:
                value = int(res[22:24],16)
                self.WriteStatus('AmbientCurrentIlluminance', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Ambient Current Illuminance: Invalid/unexpected response'])

    def UpdateAmbientSensorRead(self, value, qualifier):

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x0202B5\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        AmbientSensorReadCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AmbientSensorRead', AmbientSensorReadCmdString, value, qualifier)

        if res:
            try:
                value = int(res[22:24],16)
                self.WriteStatus('AmbientSensorRead', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Ambient Sensor Read: Invalid/unexpected response'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal'    		: b'0E0A\x0202700001\x03', 
            'Full'      		: b'0E0A\x0202700002\x03',
            'Wide'      		: b'0E0A\x0202700003\x03', 
            'Zoom'      		: b'0E0A\x0202700004\x03',
            'Dynamic'   		: b'0E0A\x0202700006\x03', 
            'Off (dot by dot)'	: b'0E0A\x0202700007\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AspectRatioCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
           b'1' : 'Normal', 
           b'2' : 'Full',
           b'3' : 'Wide',
           b'4' : 'Zoom',
           b'6' : 'Dynamic', 
           b'7' : 'Off (dot by dot)'
        }

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x020270\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        AspectRatioCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Audio 1(PC)'   : b'0E0A\x02022E0001\x03', 
            'Audio 2'       : b'0E0A\x02022E0002\x03', 
            'Audio 3'       : b'0E0A\x02022E0003\x03', 
            'HDMI'          : b'0E0A\x02022E0004\x03', 
            'TV/Option'     : b'0E0A\x02022E0006\x03',
            'DisplayPort'  : b'0E0A\x02022E0007\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AudioInputCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateAudioInput(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'Audio 1(PC)', 
            b'2' : 'Audio 2', 
            b'3' : 'Audio 3', 
            b'4' : 'HDMI', 
            b'6' : 'TV/Option',
            b'7' : 'DisplayPort' 
        }

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x02022E\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        AudioInputCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('AudioInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Input: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'   : b'0E0A\x02008D0001\x03', 
            'Off'  : b'0E0A\x02008D0000\x03'
        }

        if value in ValueStateValues:
            buffer = pack('>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AudioMuteCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'On', 
            b'2' : 'Off', 
            b'0' : 'Off' 
        }

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x02008D\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        AudioMuteCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetAutoImage(self, value, qualifier):

        buffer = pack('>BB14s', 0x30, self.DeviceID, b'0E0A\x02001E0001\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        AutoImageCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)


    def SetBacklight(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x02001000', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            BacklightCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateBacklight(self, value, qualifier):

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x020010\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

            
        BacklightCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)

        if res:
            try:
                value = int(res[22:24],16)
                self.WriteStatus('Backlight', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x02009200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            BrightnessCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateBrightness(self, value, qualifier):

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x020092\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        BrightnessCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

        if res:
            try:
                value = int(res[22:24],16)
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetChannelNumber(self, value, qualifier):

        ValueStateValues = {
            '1'         : b'0A0C\x02C210000801\x03', 
            '2'         : b'0A0C\x02C210000901\x03',
            '3'         : b'0A0C\x02C210000A01\x03',
            '4'         : b'0A0C\x02C210000B01\x03',
            '5'         : b'0A0C\x02C210000C01\x03',
            '6'         : b'0A0C\x02C210000D01\x03',
            '7'         : b'0A0C\x02C210000E01\x03',
            '8'         : b'0A0C\x02C210000F01\x03',
            '9'         : b'0A0C\x02C210001001\x03',
            '0'         : b'0A0C\x02C210001201\x03',
            '-'         : b'0A0C\x02C210004401\x03',
            'Enter'     : b'0A0C\x02C210004501\x03',
            'Exit'      : b'0A0C\x02C210001F01\x03',
            'Return'    : b'0A0C\x02C210002A01\x03'
        }

        if value in ValueStateValues:
            buffer = pack('>BB16s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ChannelNumberCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('ChannelNumber', ChannelNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1'  : b'0E0A\x0210840002\x03', 
            'CC2'  : b'0E0A\x0210840003\x03',
            'CC3'  : b'0E0A\x0210840004\x03',
            'CC4'  : b'0E0A\x0210840005\x03',
            'TT1'  : b'0E0A\x0210840006\x03',
            'TT2'  : b'0E0A\x0210840007\x03',
            'TT3'  : b'0E0A\x0210840008\x03',
            'TT4'  : b'0E0A\x0210840009\x03',
            'Off'  : b'0E0A\x0210840001\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ClosedCaptionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x02001200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ContrastCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateContrast(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020012\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        ContrastCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)

        if res:
            try:
                value = int(res[22:24],16)
                self.WriteStatus('Contrast', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Contrast: Invalid/unexpected response'])

    def SetGammaCorrection(self, value, qualifier):

        ValueStateValues = {
            'Native Gamma'  : b'0E0A\x0202680001\x03', 
            'Gamma=2.2'     : b'0E0A\x0202680004\x03', 
            'Gamma=2.4'     : b'0E0A\x0202680008\x03', 
            'S Gamma'       : b'0E0A\x0202680007\x03', 
            'DICOM SIM'     : b'0E0A\x0202680005\x03',
            'Programmable'  : b'0E0A\x0202680006\x03'
            }

        if value in ValueStateValues:
            buffer = pack('>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            GammaCorrectionCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('GammaCorrection', GammaCorrectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateGammaCorrection(self, value, qualifier):

        ValueStateValues = {
            b'01' : 'Native Gamma', 
            b'04' : 'Gamma=2.2', 
            b'08' : 'Gamma=2.4', 
            b'07' : 'S Gamma', 
            b'05' : 'DICOM SIM',
            b'06' : 'Programmable'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020268\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        GammaCorrectionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('GammaCorrection', GammaCorrectionCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[22:24]]
                self.WriteStatus('GammaCorrection', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Gamma Correction: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'           : b'0E0A\x0200600001\x03', 
            'RGB/HV'        : b'0E0A\x0200600002\x03',
            'DVI'           : b'0E0A\x0200600003\x03',
            'Video1'        : b'0E0A\x0200600005\x03',
            'Video2'        : b'0E0A\x0200600006\x03',
            'S-Video'       : b'0E0A\x0200600007\x03',
            'TV'            : b'0E0A\x020060000A\x03',
            'DVD/HD1'       : b'0E0A\x020060000C\x03',
            'Option'        : b'0E0A\x020060000D\x03',
            'DVD/HD2'       : b'0E0A\x020060000E\x03',
            'DisplayPort'  :  b'0E0A\x020060000F\x03',
            'HDMI'          : b'0E0A\x0200600004\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            InputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'01'  :'VGA',           
            b'02'  : 'RGB/HV',        
            b'03'  :'DVI',           
            b'05'  :'Video1',           
            b'06'  :'Video2',        
            b'07'  :'S-Video',       
            b'0A'  :'TV',
            b'0C'  :'DVD/HD1',       
            b'0D'  :'Option',        
            b'0E'  :'DVD/HD2',       
            b'0F'  :'DisplayPort',  
            b'11'  :'HDMI'  
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020060\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        InputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[22:24]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])


    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'0E0A\x0202EA0002\x03', 
            'Off' : b'0E0A\x0202EA0001\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            OnScreenDisplayCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            b'2' : 'On', 
            b'1' : 'Off' 
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0202EA\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        OnScreenDisplayCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetOverscan(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'0E0A\x0202E30002\x03',
            'Off' : b'0E0A\x0202E30001\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            OverscanCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Overscan', OverscanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateOverscan(self, value, qualifier):

        ValueStateValues = {
            b'2' : 'On', 
            b'1' : 'Off'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0202E3\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        OverscanCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Overscan', OverscanCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('Overscan', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Overscan: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'sRGB'      : b'0E0A\x02021A0001\x03', 
            'Hi-Bright' : b'0E0A\x02021A0003\x03',
            'Standard'  : b'0E0A\x02021A0004\x03',
            'Cinema'    : b'0E0A\x02021A0005\x03', 
            'ISF-Day'   : b'0E0A\x02021A0006\x03', 
            'ISF-Night' : b'0E0A\x02021A0007\x03',
            'Ambient-1' : b'0E0A\x02021A000B\x03', 
            'Ambient-2' : b'0E0A\x02021A000C\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            PictureModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'01' : 'sRGB', 
            b'03' : 'Hi-Bright', 
            b'04' : 'Standard', 
            b'05' : 'Cinema', 
            b'06' : 'ISF-Day', 
            b'07' : 'ISF-Night', 
            b'0B' : 'Ambient-1', 
            b'0C' : 'Ambient-2'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x02021A\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i

        PictureModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[22:24]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'           : b'0E0A\x0202730001\x03', 
            'RGB/HV'        : b'0E0A\x0202730002\x03',            
            'DVI'           : b'0E0A\x0202730003\x03', 
            'Video1'        : b'0E0A\x0202730005\x03',
            'Video2'        : b'0E0A\x0202730006\x03', 
            'S-Video'       : b'0E0A\x0202730007\x03',
            'DVD/HD1'       : b'0E0A\x020273000C\x03', 
            'Option'        : b'0E0A\x020273000D\x03',
            'DVD/HD2'       : b'0E0A\x020273000E\x03', 
            'DisplayPort'   : b'0E0A\x020273000F\x03',
            'HDMI'          : b'0E0A\x0202730004\x03', 
            'TV'            : b'0E0A\x020273000A\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            b'01'  :'VGA',           
            b'02'  :'RGB/HV',        
            b'03'  :'DVI',           
            b'05'  :'Video1',           
            b'06'  :'Video2',        
            b'07'  :'S-Video',       
            b'0A'  :'TV',
            b'0C'  :'DVD/HD1',       
            b'0D'  :'Option',        
            b'0E'  :'DVD/HD2',       
            b'0F'  :'DisplayPort',  
            b'11'  :'HDMI' 
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020273\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PIPInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[22:24]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP'                   : b'0E0A\x0202720002\x03', 
            'POP'                   : b'0E0A\x0202720003\x03',            
            'Still'                 : b'0E0A\x0202720004\x03', 
            'Side by side (Aspect)' : b'0E0A\x0202720005\x03',
            'Side by side (Full)'   : b'0E0A\x0202720006\x03', 
            'Off'                   : b'0E0A\x0202720001\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'Off',
            b'2'  :'PIP',           
            b'3'  :'POP',        
            b'4'  :'Still',           
            b'5'  :'Side by side (Aspect)',           
            b'6'  :'Side by side (Full)'     
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020272\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PIPModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small'     : b'0E0A\x0202710001\x03',
            'Middle'    : b'0E0A\x0202710002\x03',   
            'Large'     : b'0E0A\x0202710003\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPSizeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'Small',           
            b'2'  :'Middle',        
            b'3'  :'Large'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020271\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PIPSizeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'     : b'0A0C\x02C203D60001\x03', 
            'Off'    : b'0A0C\x02C203D60004\x03' 
        }

        if value in ValueStateValues:
            buffer = pack( '>BB16s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'On',           
            b'2'  :'Standby (Power Save)',
            b'3'  :'Suspend (Power Save)',
            b'4'  :'Off'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0A06\x0201D6\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPowerSave(self, value, qualifier):

        ValueStateValues = {
            'On':   b'0E0A\x0200E10001\x03',
            'Off':  b'0E0A\x0200E10000\x03'
        }

        if value in ValueStateValues:
            buffer = pack('>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PowerSaveCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PowerSave', PowerSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdatePowerSave(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        buffer = pack('>BB10s', 0x30, self.DeviceID, b'0C06\x0200E1\x03')
        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        PowerSaveCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('PowerSave', PowerSaveCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('PowerSave', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Save: Invalid/unexpected response'])

    def SetTileHMonitor(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 10:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x0202D000', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileHMonitorCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileHMonitor', TileHMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetTileMatrix(self, value, qualifier):

        ValueStateValues = {
            'On'            : b'0E0A\x0202D30002\x03', 
            'Off'           : b'0E0A\x0202D30003\x03',
            'Off W/ Frame'  : b'0E0A\x0202D30001\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileMatrixCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileMatrix', TileMatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateTileMatrix(self, value, qualifier):

        ValueStateValues = {
            b'2'  :'On',           
            b'1'  :'Off',
            b'3'  :'Off'
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0202D3\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        TileMatrixCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('TileMatrix', TileMatrixCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('TileMatrix', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Tile Matrix: Invalid/unexpected response'])
       
    def SetTileMatrixComp(self, value, qualifier):

        ValueStateValues = {
            'Enable'         : b'0E0A\x0202D50002\x03', 
            'Disable'        : b'0E0A\x0202D50001\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileMatrixCompCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileMatrixComp', TileMatrixCompCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetTilePosition(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 100:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x0202D200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TilePositionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetTileVMonitor(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 10:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x0202D100', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileVMonitorCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileVMonitor', TileVMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetTVChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'0E0A\x02008B0001\x03', 
            'Down'  : b'0E0A\x02008B0002\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TVChannelStepCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TVChannelStep', TVChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'   : b'0E0A\x0210B60001\x03', 
            'Off'  : b'0E0A\x0210B60002\x03'
        }

        if value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, self.DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            MuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('VideoMute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'On', 
            b'2' : 'Off', 
            b'0' : 'No Signal' 
        }

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x0210B6\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        MuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('VideoMute', MuteCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, self.DeviceID, b'0E0A\x02006200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        buffer = pack( '>BB10s', 0x30, self.DeviceID, b'0C06\x020062\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

        if res:
            try:
                value = int(res[22:24],16)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[8:10].decode() == '01':
                self.Error(['{0}: An Error Occurred'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
    
    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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

class DeviceSerialClass:


    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 0x41
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmbientBrightness': {'Parameters': ['Device ID', 'Mode'], 'Status': {}},
            'AmbientCurrentIlluminance': {'Parameters': ['Device ID'], 'Status': {}},
            'AmbientSensorRead': {'Parameters': ['Device ID'], 'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioInput': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Backlight': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'ChannelNumber': {'Parameters': ['Device ID'], 'Status': {}},
            'ClosedCaption': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'GammaCorrection': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'MasterPower': { 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'Overscan': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PowerSave': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrix': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixComp': {'Parameters': ['Device ID'], 'Status': {}},
            'TilePosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TVChannelStep': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 100:
            self.DeviceID = 0x40 + int(value)
        else:
            print('Invalid DeviceID parameter, range is from 1 to 100')

    def SetQualifierDeviceID(self, value):
        if value == 'Broadcast':
            return 0x2A
        elif 1 <= int(value) <= 100:
            return 0x40 + int(value)
        else:
            return 0

    def SetAmbientBrightness(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        BrightnessStates = {
            'Low' : b'0E0A\x02103300', 
            'High' : b'0E0A\x02103400'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        if DeviceID != 0 and qualifier['Mode'] in BrightnessStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, BrightnessStates[qualifier['Mode']], result, b'\x03')


            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AmbientBrightnessCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AmbientBrightness', AmbientBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateAmbientBrightness(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        BrightnessStates = {
            'Low' : b'0C06\x021033\x03', 
            'High' : b'0C06\x021034\x03'
        }

        if DeviceID != 0 and qualifier['Mode'] in BrightnessStates:
            buffer = pack('>BB10s', 0x30, DeviceID, BrightnessStates[qualifier['Mode']])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AmbientBrightnessCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('AmbientBrightness', AmbientBrightnessCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('AmbientBrightness', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Ambient Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def UpdateAmbientCurrentIlluminance(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202B4\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            AmbientCurrentIlluminanceCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('AmbientCurrentIlluminance', AmbientCurrentIlluminanceCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('AmbientCurrentIlluminance', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Ambient Current Illuminance: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def UpdateAmbientSensorRead(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202B5\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            AmbientSensorReadCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('AmbientSensorRead', AmbientSensorReadCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('AmbientSensorRead', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Ambient Sensor Read: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal'    		: b'0E0A\x0202700001\x03', 
            'Full'      		: b'0E0A\x0202700002\x03',
            'Wide'      		: b'0E0A\x0202700003\x03', 
            'Zoom'      		: b'0E0A\x0202700004\x03',
            'Dynamic'   		: b'0E0A\x0202700006\x03', 
            'Off (dot by dot)'	: b'0E0A\x0202700007\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AspectRatioCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r' 
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
           b'1' : 'Normal', 
           b'2' : 'Full',
           b'3' : 'Wide',
           b'4' : 'Zoom',
           b'6' : 'Dynamic', 
           b'7' : 'Off (dot by dot)'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020270\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AspectRatioCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'        
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Audio 1(PC)'   : b'0E0A\x02022E0001\x03', 
            'Audio 2'       : b'0E0A\x02022E0002\x03', 
            'Audio 3'       : b'0E0A\x02022E0003\x03', 
            'HDMI'          : b'0E0A\x02022E0004\x03', 
            'TV/Option'     : b'0E0A\x02022E0006\x03',
            'DisplayPort'   : b'0E0A\x02022E0007\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AudioInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateAudioInput(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'Audio 1(PC)', 
            b'2' : 'Audio 2', 
            b'3' : 'Audio 3', 
            b'4' : 'HDMI', 
            b'6' : 'TV/Option',
            b'7' : 'DisplayPort' 
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x02022E\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AudioInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AudioInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'   : b'0E0A\x02008D0001\x03', 
            'Off'  : b'0E0A\x02008D0000\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AudioMuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'On', 
            b'2' : 'Off', 
            b'0' : 'Off' 
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x02008D\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AudioMuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetAutoImage(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB14s', 0x30, DeviceID, b'0E0A\x02001E0001\x03')


            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            AutoImageCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetBacklight(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x02001000', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            BacklightCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateBacklight(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020010\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            
            BacklightCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('Backlight', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Backlight: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x02009200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            BrightnessCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateBrightness(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020092\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            BrightnessCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('Brightness', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetChannelNumber(self, value, qualifier):

        ValueStateValues = {
            '1'         : b'0A0C\x02C210000801\x03', 
            '2'         : b'0A0C\x02C210000901\x03',
            '3'         : b'0A0C\x02C210000A01\x03',
            '4'         : b'0A0C\x02C210000B01\x03',
            '5'         : b'0A0C\x02C210000C01\x03',
            '6'         : b'0A0C\x02C210000D01\x03',
            '7'         : b'0A0C\x02C210000E01\x03',
            '8'         : b'0A0C\x02C210000F01\x03',
            '9'         : b'0A0C\x02C210001001\x03',
            '0'         : b'0A0C\x02C210001201\x03',
            '-'         : b'0A0C\x02C210004401\x03',
            'Enter'     : b'0A0C\x02C210004501\x03',
            'Exit'      : b'0A0C\x02C210001F01\x03',
            'Return'    : b'0A0C\x02C210002A01\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB16s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ChannelNumberCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('ChannelNumber', ChannelNumberCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1'  : b'0E0A\x0210840002\x03', 
            'CC2'  : b'0E0A\x0210840003\x03',
            'CC3'  : b'0E0A\x0210840004\x03',
            'CC4'  : b'0E0A\x0210840005\x03',
            'TT1'  : b'0E0A\x0210840006\x03',
            'TT2'  : b'0E0A\x0210840007\x03',
            'TT3'  : b'0E0A\x0210840008\x03',
            'TT4'  : b'0E0A\x0210840009\x03',
            'Off'  : b'0E0A\x0210840001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ClosedCaptionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'Off', 
            b'2' : 'CC1', 
            b'3' : 'CC2',
            b'4' : 'CC3',
            b'5' : 'CC4',
            b'6' : 'TT1',
            b'7' : 'TT2',
            b'8' : 'TT3',
            b'9' : 'TT4' 
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x021084\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ClosedCaptionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('ClosedCaption', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Closed Caption: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x02001200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ContrastCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateContrast(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020012\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            ContrastCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('Contrast', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Contrast: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetGammaCorrection(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        ValueStateValues = {
            'Native Gamma'  : b'0E0A\x0202680001\x03', 
            'Gamma=2.2'     : b'0E0A\x0202680004\x03', 
            'Gamma=2.4'     : b'0E0A\x0202680008\x03', 
            'S Gamma'       : b'0E0A\x0202680007\x03', 
            'DICOM SIM'     : b'0E0A\x0202680005\x03',
            'Programmable'  : b'0E0A\x0202680006\x03'
        }

        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            GammaCorrectionCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('GammaCorrection', GammaCorrectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateGammaCorrection(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        ValueStateValues = {
            b'01' : 'Native Gamma', 
            b'04' : 'Gamma=2.2', 
            b'08' : 'Gamma=2.4', 
            b'07' : 'S Gamma', 
            b'05' : 'DICOM SIM',
            b'06' : 'Programmable'
        }

        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020268\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            GammaCorrectionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('GammaCorrection', GammaCorrectionCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('GammaCorrection', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Gamma Correction: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'           : b'0E0A\x0200600001\x03', 
            'RGB/HV'        : b'0E0A\x0200600002\x03',
            'DVI'           : b'0E0A\x0200600003\x03',
            'Video1'        : b'0E0A\x0200600005\x03',
            'Video2'        : b'0E0A\x0200600006\x03',
            'S-Video'       : b'0E0A\x0200600007\x03',
            'TV'            : b'0E0A\x020060000A\x03',
            'DVD/HD1'       : b'0E0A\x020060000C\x03',
            'Option'        : b'0E0A\x020060000D\x03',
            'DVD/HD2'       : b'0E0A\x020060000E\x03',
            'DisplayPort'   : b'0E0A\x020060000F\x03',
            'HDMI'          : b'0E0A\x0200600004\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            InputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'01'  :'VGA',           
            b'02'  : 'RGB/HV',        
            b'03'  :'DVI',           
            b'05'  :'Video1',           
            b'06'  :'Video2',        
            b'07'  :'S-Video',       
            b'0A'  :'TV',
            b'0C'  :'DVD/HD1',       
            b'0D'  :'Option',        
            b'0E'  :'DVD/HD2',       
            b'0F'  :'DisplayPort',  
            b'11'  :'HDMI'  
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020060\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            InputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def UpdateMasterPower(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'On',
            b'2'  :'Standby (Power Save)',
            b'3'  :'Suspend (Power Save)',
            b'4'  :'Off'
        }

        buffer = pack( '>BB10s', 0x30, self._DeviceID, b'0A06\x0201D6\x03')

        checksum = 0
        for i in buffer:
            checksum = checksum ^ i
        MasterPowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
        res = self.__UpdateHelper('MasterPower', MasterPowerCmdString, value, qualifier)

        if res:
            try:
                value = ValueStateValues[res[23:24]]
                self.WriteStatus('Power', value, {'Device ID': str(self.DeviceID - 0x40)})
            except (KeyError, IndexError):
                self.Error(['Master Power: Invalid/unexpected response'])


    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'0E0A\x0202EA0002\x03', 
            'Off' : b'0E0A\x0202EA0001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            OnScreenDisplayCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            b'2' : 'On', 
            b'1' : 'Off' 
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x0202EA\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            OnScreenDisplayCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('OnScreenDisplay', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['On Screen Display: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetOverscan(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'0E0A\x0202E30002\x03',
            'Off' : b'0E0A\x0202E30001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            OverscanCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Overscan', OverscanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateOverscan(self, value, qualifier):

        ValueStateValues = {
            b'2' : 'On', 
            b'1' : 'Off'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x0202E3\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            OverscanCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Overscan', OverscanCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('Overscan', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Overscan: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetPictureMode(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])

        ValueStateValues = {
            'sRGB'      : b'0E0A\x02021A0001\x03', 
            'Hi-Bright' : b'0E0A\x02021A0003\x03',
            'Standard'  : b'0E0A\x02021A0004\x03',
            'Cinema'    : b'0E0A\x02021A0005\x03', 
            'ISF-Day'   : b'0E0A\x02021A0006\x03', 
            'ISF-Night' : b'0E0A\x02021A0007\x03',
            'Ambient-1' : b'0E0A\x02021A000B\x03', 
            'Ambient-2' : b'0E0A\x02021A000C\x03'
        }

        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            PictureModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'01' : 'sRGB', 
            b'03' : 'Hi-Bright', 
            b'04' : 'Standard', 
            b'05' : 'Cinema', 
            b'06' : 'ISF-Day', 
            b'07' : 'ISF-Night', 
            b'0B' : 'Ambient-1', 
            b'0C' : 'Ambient-2'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x02021A\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i

            PictureModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('PictureMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'           : b'0E0A\x0202730001\x03', 
            'RGB/HV'        : b'0E0A\x0202730002\x03',            
            'DVI'           : b'0E0A\x0202730003\x03', 
            'Video1'        : b'0E0A\x0202730005\x03',
            'Video2'        : b'0E0A\x0202730006\x03', 
            'S-Video'       : b'0E0A\x0202730007\x03',
            'DVD/HD1'       : b'0E0A\x020273000C\x03', 
            'Option'        : b'0E0A\x020273000D\x03',
            'DVD/HD2'       : b'0E0A\x020273000E\x03', 
            'DisplayPort'   : b'0E0A\x020273000F\x03',
            'HDMI'          : b'0E0A\x0202730004\x03', 
            'TV'            : b'0E0A\x020273000A\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            b'01'  :'VGA',           
            b'02'  :'RGB/HV',        
            b'03'  :'DVI',           
            b'05'  :'Video1',           
            b'06'  :'Video2',        
            b'07'  :'S-Video',       
            b'0A'  :'TV',
            b'0C'  :'DVD/HD1',       
            b'0D'  :'Option',        
            b'0E'  :'DVD/HD2',       
            b'0F'  :'DisplayPort',  
            b'11'  :'HDMI' 
        }

        
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020273\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPInputCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP'                   : b'0E0A\x0202720002\x03', 
            'POP'                   : b'0E0A\x0202720003\x03',            
            'Still'                 : b'0E0A\x0202720004\x03', 
            'Side by side (Aspect)' : b'0E0A\x0202720005\x03',
            'Side by side (Full)'   : b'0E0A\x0202720006\x03', 
            'Off'                   : b'0E0A\x0202720001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'Off',
            b'2'  :'PIP',           
            b'3'  :'POP',        
            b'4'  :'Still',           
            b'5'  :'Side by side (Aspect)',           
            b'6'  :'Side by side (Full)'     
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020272\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPModeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('PIPMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small'     : b'0E0A\x0202710001\x03',
            'Middle'    : b'0E0A\x0202710002\x03',   
            'Large'     : b'0E0A\x0202710003\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPSizeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'Small',           
            b'2'  :'Middle',        
            b'3'  :'Large'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020271\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PIPSizeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('PIPSize', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Size: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'     : b'0A0C\x02C203D60001\x03', 
            'Off'    : b'0A0C\x02C203D60004\x03' 
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB16s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1'  :'On',
            b'2'  :'Standby (Power Save)',
            b'3'  :'Suspend (Power Save)',
            b'4'  :'Off'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0A06\x0201D6\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PowerCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetPowerSave(self, value, qualifier):

        ValueStateValues = {
            'On':   b'0E0A\x0200E10001\x03',
            'Off':  b'0E0A\x0200E10000\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PowerSaveCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('PowerSave', PowerSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdatePowerSave(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0200E1\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            PowerSaveCmdString = b'\x01' + buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('PowerSave', PowerSaveCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('PowerSave', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power Save: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetTileHMonitor(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        value = int(value)
        if DeviceID != 0 and 1 <= value <= 10:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D000', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileHMonitorCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileHMonitor', TileHMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def SetTileMatrix(self, value, qualifier):

        ValueStateValues = {
            'On'            : b'0E0A\x0202D30002\x03',
            'Off'           : b'0E0A\x0202D30003\x03',
            'Off W/ Frame'  : b'0E0A\x0202D30001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileMatrixCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileMatrix', TileMatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateTileMatrix(self, value, qualifier):

        ValueStateValues = {
            b'2'  :'On',           
            b'1'  :'Off',
            b'3'  :'Off'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x0202D3\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileMatrixCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('TileMatrix', TileMatrixCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('TileMatrix', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tile Matrix: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetTileMatrixComp(self, value, qualifier):

        ValueStateValues = {
            'Enable'         : b'0E0A\x0202D50002\x03', 
            'Disable'        : b'0E0A\x0202D50001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileMatrixCompCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileMatrixComp', TileMatrixCompCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetTilePosition(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        value = int(value)
        if DeviceID != 0 and 1 <= value <= 100:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TilePositionCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetTileVMonitor(self, value, qualifier):

        value = int(value)
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and 1 <= value <= 10:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D100', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TileVMonitorCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TileVMonitor', TileVMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def SetTVChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'0E0A\x02008B0001\x03', 
            'Down'  : b'0E0A\x02008B0002\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            TVChannelStepCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('TVChannelStep', TVChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'   : b'0E0A\x0210B60001\x03', 
            'Off'  : b'0E0A\x0210B60002\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and value in ValueStateValues:
            buffer = pack( '>BB14s', 0x30, DeviceID, ValueStateValues[value])

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            MuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('VideoMute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'1' : 'On', 
            b'2' : 'Off', 
            b'0' : 'No Signal' 
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x0210B6\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            MuteCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('VideoMute', MuteCmdString, value, qualifier)

            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('VideoMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack( '>BB11s2ss', 0x30, DeviceID, b'0E0A\x02006200', result, b'\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')


    def UpdateVolume(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack( '>BB10s', 0x30, DeviceID, b'0C06\x020062\x03')

            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

            if res:
                try:
                    value = int(res[22:24],16)
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[8:10].decode() == '01':
                self.Error(['{0}: An Error Occurred'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or 'Broadcast' in [qualifier['Device ID']]:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
    
    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or 'Broadcast' in qualifier['Device ID']:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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