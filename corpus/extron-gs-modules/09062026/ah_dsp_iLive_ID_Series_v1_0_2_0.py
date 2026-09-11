from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'iLive IDR16': self.ah_25_957_16,
            'iLive IDR64': self.ah_25_957_64,
            'iLive IDR32': self.ah_25_957_32,
            'iLive IDR48': self.ah_25_957_48,
            }


        self.Commands = {
            'FaderLevel': {'Parameters': ['MIDI Channel','Input'], 'Status': {}},
            'MuteControl': {'Parameters': ['MIDI Channel','Input'], 'Status': {}},
            'SceneRecall': {'Parameters': ['MIDI Channel'], 'Status': {}},
            }



        self.MidiChannelStates = {
            '1' : '0',
            '2' : '1',
            '3' : '2',
            '4' : '3',
            '5' : '4',
            '6' : '5',
            '7' : '6',
            '8' : '7',
            '9' : '8',
            '10' : '9',
            '11' : 'A',
            '12' : 'B',
            '13' : 'C',
            '14' : 'D',
            '15' : 'E',
            '16' : 'F'
            } 
        
    def SetFaderLevel(self, value, qualifier):

        FaderLevelConstraints = {
            'Min' : 0,
            'Max' : 127
            }

        midi = qualifier['MIDI Channel']
        input = qualifier['Input']
        if FaderLevelConstraints['Min'] <= value <= FaderLevelConstraints['Max'] and 1 <= int(midi) <= 16 and 1 <= int(input) <= self.InputSize:
            MidiConversion = int('B' + self.MidiChannelStates[midi], 16)
            FaderLevelCmdString = pack('BBBBBBB', MidiConversion, 0x63, self.InputStates[input], 0x62, 0x17, 0x06, value)
            self.__SetHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderLevel')

    def SetMuteControl(self, value, qualifier):

        MuteControlState = {
           'On'  : 0x7F,
           'Off' : 0x3F,
           }

        midi = qualifier['MIDI Channel']
        input = qualifier['Input']
        if 1 <= int(midi) <= 16 and 1<= int(input) <= self.InputSize:
            MidiConversion = int('9' + self.MidiChannelStates[midi], 16)
            MuteControlCmdString = pack('BBBBB', MidiConversion, self.InputStates[input], MuteControlState[value], self.InputStates[qualifier['Input']], 0x00)
            self.__SetHelper('MuteControl', MuteControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMuteControl')
    def SetSceneRecall(self, value, qualifier):

        SceneRecallConstraints1 = {
            'Min' : 1,
            'Max' : 128
            }
        SceneRecallConstraints2 = {
            'Min' : 129,
            'Max' : 250
            }

        midi = qualifier['MIDI Channel']
        if SceneRecallConstraints1['Min'] <= int(value) <= SceneRecallConstraints1['Max'] and 1 <= int(midi) <= 16:
            MidiConversion1 = int('B' + self.MidiChannelStates[midi], 16)
            MidiConversion2 = int('C' + self.MidiChannelStates[midi], 16)
            SceneRecallCmdString = pack('BBBBB', MidiConversion1, 0x00, 0x00, MidiConversion2, int(value)-1)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        elif SceneRecallConstraints2['Min'] <= int(value) <= SceneRecallConstraints2['Max'] and 1 <= int(midi) <= 16:
            MidiConversion1 = int('B' + self.MidiChannelStates[midi], 16)
            MidiConversion2 = int('C' + self.MidiChannelStates[midi], 16)
            SceneRecallCmdString = pack('BBBBB', MidiConversion1, 0x00, 0x01, MidiConversion2, int(value)-1)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        self.Send(commandstring)

    def ah_25_957_16(self):

        self.InputSize = 16
        self.InputStates = {
            '1' : 0x20,
            '2' : 0x21,
            '3' : 0x22,
            '4' : 0x23,
            '5' : 0x24,
            '6' : 0x25,
            '7' : 0x26,
            '8' : 0x27,
            '9' : 0x28,
            '10' : 0x29,
            '11' : 0x2A,
            '12' : 0x2B,
            '13' : 0x2C,
            '14' : 0x2D,
            '15' : 0x2E,
            '16' : 0x2F
            }


    def ah_25_957_32(self):

        self.InputSize = 32
        self.InputStates = {
            '1' : 0x20,
            '2' : 0x21,
            '3' : 0x22,
            '4' : 0x23,
            '5' : 0x24,
            '6' : 0x25,
            '7' : 0x26,
            '8' : 0x27,
            '9' : 0x28,
            '10' : 0x29,
            '11' : 0x2A,
            '12' : 0x2B,
            '13' : 0x2C,
            '14' : 0x2D,
            '15' : 0x2E,
            '16' : 0x2F,
            '17' : 0x30,
            '18' : 0x31,
            '19' : 0x32,
            '20' : 0x33,
            '21' : 0x34,
            '22' : 0x35,
            '23' : 0x36,
            '24' : 0x37,
            '25' : 0x38,
            '26' : 0x39,
            '27' : 0x3A,
            '28' : 0x3B,
            '29' : 0x3C,
            '30' : 0x3D,
            '31' : 0x3E,
            '32' : 0x3F
            }


    def ah_25_957_48(self):

        self.InputSize = 48
        self.InputStates = {
            '1' : 0x20,
            '2' : 0x21,
            '3' : 0x22,
            '4' : 0x23,
            '5' : 0x24,
            '6' : 0x25,
            '7' : 0x26,
            '8' : 0x27,
            '9' : 0x28,
            '10' : 0x29,
            '11' : 0x2A,
            '12' : 0x2B,
            '13' : 0x2C,
            '14' : 0x2D,
            '15' : 0x2E,
            '16' : 0x2F,
            '17' : 0x30,
            '18' : 0x31,
            '19' : 0x32,
            '20' : 0x33,
            '21' : 0x34,
            '22' : 0x35,
            '23' : 0x36,
            '24' : 0x37,
            '25' : 0x38,
            '26' : 0x39,
            '27' : 0x3A,
            '28' : 0x3B,
            '29' : 0x3C,
            '30' : 0x3D,
            '31' : 0x3E,
            '32' : 0x3F,
            '33' : 0x40,
            '34' : 0x41,
            '35' : 0x42,
            '36' : 0x43,
            '37' : 0x44,
            '38' : 0x45,
            '39' : 0x46,
            '40' : 0x47,
            '41' : 0x48,
            '42' : 0x49,
            '43' : 0x4A,
            '44' : 0x4B,
            '45' : 0x4C,
            '46' : 0x4D,
            '47' : 0x4E,
            '48' : 0x4F
            }


    def ah_25_957_64(self):

        
        self.InputSize = 64
        self.InputStates = {
            '1' : 0x20,
            '2' : 0x21,
            '3' : 0x22,
            '4' : 0x23,
            '5' : 0x24,
            '6' : 0x25,
            '7' : 0x26,
            '8' : 0x27,
            '9' : 0x28,
            '10' : 0x29,
            '11' : 0x2A,
            '12' : 0x2B,
            '13' : 0x2C,
            '14' : 0x2D,
            '15' : 0x2E,
            '16' : 0x2F,
            '17' : 0x30,
            '18' : 0x31,
            '19' : 0x32,
            '20' : 0x33,
            '21' : 0x34,
            '22' : 0x35,
            '23' : 0x36,
            '24' : 0x37,
            '25' : 0x38,
            '26' : 0x39,
            '27' : 0x3A,
            '28' : 0x3B,
            '29' : 0x3C,
            '30' : 0x3D,
            '31' : 0x3E,
            '32' : 0x3F,
            '33' : 0x40,
            '34' : 0x41,
            '35' : 0x42,
            '36' : 0x43,
            '37' : 0x44,
            '38' : 0x45,
            '39' : 0x46,
            '40' : 0x47,
            '41' : 0x48,
            '42' : 0x49,
            '43' : 0x4A,
            '44' : 0x4B,
            '45' : 0x4C,
            '46' : 0x4D,
            '47' : 0x4E,
            '48' : 0x4F,
            '49' : 0x50,
            '50' : 0x51,
            '51' : 0x52,
            '52' : 0x53,
            '53' : 0x54,
            '54' : 0x55,
            '55' : 0x56,
            '56' : 0x57,
            '57' : 0x58,
            '58' : 0x59,
            '59' : 0x5A,
            '60' : 0x5B,
            '61' : 0x5C,
            '62' : 0x5D,
            '63' : 0x5E,
            '64' : 0x5F
            }

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

