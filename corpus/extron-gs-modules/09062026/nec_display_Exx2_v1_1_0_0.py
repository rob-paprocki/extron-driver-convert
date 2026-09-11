from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from binascii import hexlify

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AnalogClosedCaption': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Channel': { 'Status': {}},
            'DigitalClosedCaption': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }


    def __calculate_checksum(self, command_string):

        checksum = 0
        for byte in command_string[1:]:
            checksum ^= byte
        return bytes([checksum])

    def __build_setstring(self, op_code_page, op_code, value):

        header = b'\x010A0E0A'
        message = b'\x02' + op_code_page + op_code + b'00' + value + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter
    def SetAnalogClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x31\x03\x78\x0D',
            'CC1': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x32\x03\x7B\x0D',
            'CC2': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x33\x03\x7A\x0D',
            'CC3': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x34\x03\x7D\x0D',
            'CC4': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x35\x03\x7C\x0D',
            'TT1': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x36\x03\x7F\x0D',
            'TT2': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x37\x03\x7E\x0D',
            'TT3': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x38\x03\x71\x0D',
            'TT4': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x39\x03\x70\x0D'
        }

        AnalogClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogClosedCaption', AnalogClosedCaptionCmdString, value, qualifier)
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x31\x03\x09\x0D',
            'Off':  b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x32\x03\x0A\x0D'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x31\x45\x30\x30\x30\x31\x03\x01\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up':   b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x31\x03\x0F\x0D',
            'Down': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x32\x03\x0C\x0D'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
    def SetDigitalClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off':  b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x31\x03\x04\x0D',
            'Srv1': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x32\x03\x07\x0D',
            'Srv2': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x33\x03\x06\x0D',
            'Srv3': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x34\x03\x01\x0D',
            'Srv4': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x35\x03\x00\x0D',
            'Srv5': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x36\x03\x03\x0D',
            'Srv6': b'\x01\x30\x41\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x37\x03\x02\x0D'
        }

        DigitalClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalClosedCaption', DigitalClosedCaptionCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'All Buttons':          b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x32\x03\x72\x0D',
            'Control Buttons Only': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x31\x03\x71\x0D',
            'Unlock':               b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x30\x03\x70\x0D'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA':          b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x31\x03\x73\x0D',
            'HDMI 1':       b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x31\x03\x72\x0D',
            'HDMI 2':       b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x32\x03\x71\x0D',
            'HDMI 3':       b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x33\x03\x70\x0D',
            'Composite':    b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x35\x03\x77\x0D',
            'TV':           b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x41\x03\x03\x0D',
            'Component':    b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x43\x03\x01\x0D'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01\x30\x41\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x31\x03\x73\x0D',
            'Off':  b'\x01\x30\x41\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x34\x03\x76\x0D'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = self.__build_setstring(b'00', b'62', hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

        ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


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

