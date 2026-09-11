from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:


    
    def __init__(self):

        self.Debug = False
        self.Models = {
            'UN32J6300': self.smsg_10_1432_Other,
            'UN40J6300': self.smsg_10_1432_Other,
            'UN48J6300': self.smsg_10_1432_Other,
            'UN50J6300': self.smsg_10_1432_Other,
            'UN55F7050': self.smsg_10_1432_Other,
            'UN55J6300': self.smsg_10_1432_Other,
            'UN60F7050': self.smsg_10_1432_Other,
            'UN60J6300': self.smsg_10_1432_Other,
            'UN65F7050': self.smsg_10_1432_Other,
            'UN65J6300': self.smsg_10_1432_Other,
            'UN75F7050': self.smsg_10_1432_Other,
            'UN75J6300': self.smsg_10_1432_Other,
            'UN40J6200': self.smsg_10_1432_J6200,
            'UN48J6200': self.smsg_10_1432_J6200,
            'UN50J6200': self.smsg_10_1432_J6200,
            'UN55J6200': self.smsg_10_1432_J6200,
            'UN60J6200': self.smsg_10_1432_J6200,
            'UN65J6200': self.smsg_10_1432_J6200,
            }


        self.Commands = {
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ChannelCommand': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9'       : b'\x00\xC0',
            'Zoom 1'     : b'\x01\xBF',
            'Zoom 2'     : b'\x02\xBE',
            'Wide Fit'   : b'\x03\xBD',
            '4:3'        : b'\x04\xBC',
            'Screen Fit' : b'\x05\xBB'
        }

        AspectRatioCmdString = b'\x08\x22\x0B\x0A\x01' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)



    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x08\x22\x02\x00\x00\x00\xD4'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)



    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up'   : b'\x08\x22\x03\x00\x01\x00\xD2',
            'Down' : b'\x08\x22\x03\x00\x02\x00\xD1'
            }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)







    def SetChannelCommand(self, value, qualifier):

        cmdstring = value
        if cmdstring:
            if '-' in cmdstring:
                if 0 <= int(cmdstring.split('-')[1]) <= 999:
                    minorChannel = int(cmdstring.split('-')[1]) & 0xFF
                else:
                    self.Discard('Invalid Command for SetChannelCommand')

                majorChannel = int(cmdstring.split('-')[0])



                if 0 <= majorChannel <= 63:
                    byte4 = 0x80
                    offset = 0
                elif 64 <= majorChannel <= 127:
                    byte4 = 0x81
                    offset = 0
                elif 128 <= majorChannel <= 191:
                    byte4 = 0x82
                    offset = 0
                elif 192 <= majorChannel <= 255:
                    byte4 = 0x83
                    offset = 0
                elif 256 <= majorChannel <= 319:
                    byte4 = 0x84
                    offset = 1
                elif 320 <= majorChannel <= 383:
                    byte4 = 0x85
                    offset = 1
                elif 384 <= majorChannel <= 447:
                    byte4 = 0x86
                    offset = 1
                elif 448 <= majorChannel <= 511:
                    byte4 = 0x87
                    offset = 1
                elif 512 <= majorChannel <= 575:
                    byte4 = 0x88
                    offset = 2
                elif 576 <= majorChannel <= 639:
                    byte4 = 0x89
                    offset = 2
                elif 640 <= majorChannel <= 703:
                    byte4 = 0x8A
                    offset = 2
                elif 704 <= majorChannel <= 767:
                    byte4 = 0x8B
                    offset = 2
                elif 768 <= majorChannel <= 831:
                    byte4 = 0x8C
                    offset = 3
                elif 832 <= majorChannel <= 895:
                    byte4 = 0x8D
                    offset = 3
                elif 896 <= majorChannel <= 959:
                    byte4 = 0x8E
                    offset = 3
                elif 960 <= majorChannel <= 999:
                    byte4 = 0x8F
                    offset = 3
                else:
                    self.Discard('Invalid Command for SetChannelCommand')

                majorChannel = ((majorChannel * 4) + offset) & 255
                checksum = (256 - (46 + byte4 + majorChannel + minorChannel)) & 255
                ChannelCommandCmdString = b'\x08\x22\x04' + byte4.to_bytes(1, 'big') + majorChannel.to_bytes(1, 'big') + minorChannel.to_bytes(1, 'big') + checksum.to_bytes(1, 'big')
            else:
                try:
                    if 0 <= int(cmdstring) <= 16383:
                        majorChannel = divmod(int(cmdstring), 256)
                        checksum = (256 - (46 + majorChannel[0] + majorChannel[1])) & 255
                        ChannelCommandCmdString = b'\x08\x22\x04\x00' + majorChannel[0].to_bytes(1, 'big') + majorChannel[1].to_bytes(1, 'big') + checksum.to_bytes(1, 'big')
                    else:
                        self.Discard('Invalid Command for SetChannelCommand')
                except ValueError:
                    self.Discard('Invalid Command for SetChannelCommand')

            if ChannelCommandCmdString:
                self.__SetHelper('ChannelCommand', ChannelCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelCommand')
        else:
            self.Discard('Invalid Command for SetChannelCommand')



    def SetInput(self, value, qualifier):

        InputCmdString = b'\x08\x22\x0A\x00' + self.InputStates[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)



    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x60\x69',
            'Down'  : b'\x61\x68',
            'Left'  : b'\x65\x64',
            'Right' : b'\x62\x67',
            'Menu'  : b'\x1A\xAF',
            'Enter' : b'\x68\x61',
            'Exit'  : b'\x2D\x9C'
        }

        MenuNavigationCmdString = b'\x08\x22\x0D\x00\x00' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)



    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\xD4',
            'Off' : b'\x01\xD5'
        }

        PowerCmdString = b'\x08\x22\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)





    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            cks = 213 - value
            VolumeCmdString = b'\x08\x22\x01\x00\x00' + value.to_bytes(1,'big') + cks.to_bytes(1,'big')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True


        self.Send(commandstring)

    def smsg_10_1432_J6200(self):
        self.InputStates = {
            'TV'        : b'\x00\x00\xCC',
            'AV'        : b'\x01\x00\xCB',
            'Component' : b'\x03\x00\xC9',
            'HDMI 1'    : b'\x05\x00\xC7',
            'HDMI 2'    : b'\x05\x01\xC6'
            }
    
    def smsg_10_1432_Other(self):
        self.InputStates = {
            'TV'        : b'\x00\x00\xCC',
            'AV'        : b'\x01\x00\xCB',
            'Component' : b'\x03\x00\xC9',
            'HDMI 1'    : b'\x05\x00\xC7',
            'HDMI 2'    : b'\x05\x01\xC6',
            'HDMI 3'    : b'\x05\x02\xC5',
            'HDMI 4'    : b'\x05\x03\xC4'
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

