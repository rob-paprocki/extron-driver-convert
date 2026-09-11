from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from struct import pack
from binascii import hexlify

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AnalogClosedCaption': { 'Status': {}},
            'AspectRatio': { 'Status': {}},       
            'AudioMute': { 'Status': {}}, 
            'DigitalClosedCaption': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'InformationOSD': { 'Status': {}},
            'Input': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'TVChannel': { 'Status': {}},
            'VolumeDiscrete': { 'Status': {}},
            'VolumeStep': { 'Status': {}},
            }


    def SetAnalogClosedCaption(self, value, qualifier):

        AnalogClosedCaptionStateValues = {
            'Off' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x31\x03\x08\x0D',
            'CC1' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x32\x03\x0B\x0D',
            'CC2' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x33\x03\x0A\x0D',
            'CC3' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x34\x03\x0D\x0D',
            'CC4' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x35\x03\x0C\x0D',
            'TT1' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x36\x03\x0F\x0D',
            'TT2' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x37\x03\x0E\x0D',
            'TT3' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x38\x03\x01\x0D',
            'TT4' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x39\x03\x00\x0D',
            }

        AnalogClosedCaptionCmdString = AnalogClosedCaptionStateValues[value]
        self.__SetHelper('AnalogClosedCaption', AnalogClosedCaptionCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
           '4:3' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x31\x03\x70\x0D',
           'Auto' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x32\x03\x73\x0D',
           '16:9' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x33\x03\x72\x0D',
           'Zoom' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x34\x03\x75\x0D',
           'Cinema' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x42\x03\x03\x0D'
            }

        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)


    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'Off' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x32\x03\x0A\x0D',
            'On' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x31\x03\x09\x0D',
            }

        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)


    def SetDigitalClosedCaption(self, value, qualifier):

        DigitalClosedCaptionStateValues = {
            'Off' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x31\x03\x74\x0D',
            'Srv1' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x32\x03\x77\x0D',
            'Srv2' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x33\x03\x76\x0D',
            'Srv3' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x34\x03\x71\x0D',
            'Srv4' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x35\x03\x70\x0D',
            'Srv5' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x36\x03\x73\x0D',
            'Srv6' : b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x37\x03\x72\x0D'
            }

        DigitalClosedCaptionCmdString = DigitalClosedCaptionStateValues[value]
        self.__SetHelper('DigitalClosedCaption', DigitalClosedCaptionCmdString, value, qualifier)


    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'All Buttons' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x32\x03\x72\x0D',
            'Control Buttons' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x31\x03\x71\x0D',
            'Unlock' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x30\x03\x70\x0D'
            }

        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)


    def SetInformationOSD(self, value, qualifier):

        InformationOSDStateValues = {
            'On' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x45\x41\x30\x30\x30\x32\x03\x70\x0D',
            'Off': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x45\x41\x30\x30\x30\x31\x03\x73\x0D'
            }

        InformationOSDCmdString = InformationOSDStateValues[value]
        self.__SetHelper('InformationOSD', InformationOSDCmdString, value, qualifier)


    def SetInput(self, value, qualifier):

        InputStateValues = {
            'VGA':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x31\x03\x73\x0D',
            'HDMI1':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x31\x03\x72\x0D',
            'HDMI2':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x32\x03\x71\x0D',
            'HDMI3':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x33\x03\x70\x0D',
            'Composite':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x35\x03\x77\x0D',
            'Component':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x43\x03\x01\x0D',
            'USB':b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x34\x03\x77\x0D',
            'TV' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x41\x03\x03\x0D', 
            }

        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)


    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Standard' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x34\x03\x02\x0D',
            'Theater' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x35\x03\x03\x0D',
            'Dynamic' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x44\x03\x72\x0D',
            'Energy Saving' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x45\x03\x73\x0D',
            'Custom' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30\x46\x03\x70\x0D',
            'Game' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x31\x30\x03\x07\x0D'
            }

        PictureModeCmdString = PictureModeStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off' : b'\x01\x30\x41\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x34\x03\x76\x0D',
            'On' : b'\x01\x30\x41\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x31\x03\x73\x0D',
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)


    def SetSoundMode(self, value, qualifier):

        SoundModeStateValues = {
            'Standard':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x42\x32\x30\x30\x30\x31\x03\x04\x0D',
            'Movie':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x42\x32\x30\x30\x30\x32\x03\x07\x0D',
            'Music':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x42\x32\x30\x30\x30\x33\x03\x06\x0D',
            'News':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x42\x32\x30\x30\x30\x34\x03\x01\x0D',
            'Custom':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x42\x32\x30\x30\x30\x35\x03\x00\x0D',
            'Equalizer':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x42\x32\x30\x30\x30\x36\x03\x03\x0D'
            }

        SoundModeCmdString = SoundModeStateValues[value]
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)


    def SetTVChannel(self, value, qualifier):

        TVChannelStateValues = {
            'Up' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x31\x03\x0F\x0D',
            'Down' : b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x32\x03\x0C\x0D'
            }
        TVChannelCmdString = TVChannelStateValues[value]
        self.__SetHelper('TVChannel', TVChannelCmdString, value, qualifier)


    def SetVolumeDiscrete(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1,'big')).upper()
            buffer = pack('>B12s2sB', 0x30,b'A0E0A\x02006200', result, 0x03)
            checksum = 0
            for i in buffer:
                checksum = checksum ^ i
            VolumeCmdString = b'\x01'+ buffer + pack('>B', checksum) + b'\r'           
            self.__SetHelper('VolumeDiscrete', VolumeCmdString, value, qualifier)

    def SetVolumeStep(self, value, qualifier):

        VolumeStateValues = {
            'Up':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x44\x30\x30\x30\x31\x03\x71\x0D',
            'Down':b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x44\x30\x30\x30\x32\x03\x72\x0D'
            }
        VolumeCmdString = VolumeStateValues[value]
        self.__SetHelper('VolumeStep', VolumeCmdString, value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):
   
        pass

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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

