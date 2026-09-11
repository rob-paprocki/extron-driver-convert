from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {
            'XP-3060': self.xlca_25_630_3060,
            'XP-2040': self.xlca_25_630_2040,
            'XP-4080': self.xlca_25_630_4080,
            'XP-8080': self.xlca_25_630_8080,
            }

        self.Commands = {
            'InputGain': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputGain': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetStore': {'Status': {}},
        }

    def SetInputGain(self, value, qualifier):

        Vol_Sel = {
            'Up'   : 0x21,
            'Down' : 0x20,
        }
        
        ch_val = qualifier['Channel']

        ChkSum = 0x57 + 0x7F + 0x03 + 0x23 + 0x4C + 0x56 + 0x4C + 0x08 + 0x20 + 0x09 + 0x20 + 0x0A + self.Inp_Channel[ch_val] + 0x0C + Vol_Sel[value] + 0x10 + 0x24
        ChkSum = (ChkSum % 0x60) + 0x20
         
        CmdString = pack( '>21B', 0x01, 0x57, 0x7F, 0x03, 0x23, 0x4C, 0x56, 0x4C, \
                                  0x08, 0x20, 0x09, 0x20, 0x0A, self.Inp_Channel[ch_val], \
                                  0x0C, Vol_Sel[value], 0x10, 0x24, 0x1F, ChkSum, 0x02)

        self.__SetHelper('InputGain', CmdString, value, qualifier)


    def SetInputMute(self, value, qualifier):

        Mute_Val = {
            'On'   : 0x21,
            'Off'  : 0x20,
        }
        
        ch_val = qualifier['Channel']

        ChkSum = 0x57 + 0x7F + 0x03 + 0x4D + 0x55 + 0x54 + 0x30 + 0x08 + 0x20 + 0x09 + 0x20 + 0x0A + self.Inp_Channel[ch_val] + 0x10 + Mute_Val[value]
        ChkSum = (ChkSum % 0x60) + 0x20
         
        CmdString = pack( '>19B', 0x01, 0x57, 0x7F, 0x03, 0x4D, 0x55, 0x54, 0x30, \
                                  0x08, 0x20, 0x09, 0x20, 0x0A, self.Inp_Channel[ch_val], \
                                  0x10, Mute_Val[value], 0x1F, ChkSum, 0x02)

        self.__SetHelper('InputMute', CmdString, value, qualifier)


    def SetOutputGain(self, value, qualifier):

        Vol_Sel = {
            'Up'   : 0x21,
            'Down' : 0x20,
        }
        
        ch_val = qualifier['Channel']

        ChkSum = 0x57 + 0x7F + 0x03 + 0x23 + 0x4C + 0x56 + 0x4C + 0x08 + 0x20 + 0x09 + 0x21 + 0x0A + self.Out_Channel[ch_val] + 0x0C + Vol_Sel[value] + 0x10 + 0x24
        ChkSum = (ChkSum % 0x60) + 0x20

        CmdString = pack( '>21B', 0x01, 0x57, 0x7F, 0x03, 0x23, 0x4C, 0x56, 0x4C, \
                                  0x08, 0x20, 0x09, 0x21, 0x0A, self.Out_Channel[ch_val], \
                                  0x0C, Vol_Sel[value], 0x10, 0x24, 0x1F, ChkSum, 0x02)

        self.__SetHelper('OutputGain', CmdString, value, qualifier)


    def SetOutputMute(self, value, qualifier):

        Mute_Val = {
            'On'   : 0x21,
            'Off'  : 0x20,
        }
        
        ch_val = qualifier['Channel']

        ChkSum = 0x57 + 0x7F + 0x03 + 0x4D + 0x55 + 0x54 + 0x30 + 0x08 + 0x20 + 0x09 + 0x21 + 0x0A + self.Out_Channel[ch_val] + 0x10 + Mute_Val[value]
        ChkSum = (ChkSum % 0x60) + 0x20
         
        CmdString = pack( '>19B', 0x01, 0x57, 0x7F, 0x03, 0x4D, 0x55, 0x54, 0x30, \
                                  0x08, 0x20, 0x09, 0x21, 0x0A, self.Out_Channel[ch_val], \
                                  0x10, Mute_Val[value], 0x1F, ChkSum, 0x02)

        self.__SetHelper('OutputMute', CmdString, value, qualifier)


    def SetPresetRecall(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 30:
            prerecall_val = 0x20 + (value-1)
            ChkSum = 0x57 + 0x7F + 0x03 + 0x25 + 0x50 + 0x52 + 0x30 + 0x08 + 0x20 + 0x10 + prerecall_val
            ChkSum = (ChkSum % 0x60) + 0x20

            CmdString = pack( '>15B', 0x01, 0x57, 0x7F, 0x03, 0x25, 0x50, 0x52, 0x30, \
                                      0x08, 0x20, 0x10, prerecall_val, 0x1F, ChkSum, 0x02)
            self.__SetHelper('PresetRecall', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')


    def SetPresetStore(self, value, qualifier):

        value = int(value)
        if 1 <= value <= 30:
            prestore_val = 0x20 + (value-1)
            ChkSum = 0x57 + 0x7F + 0x03 + 0x25 + 0x50 + 0x53 + 0x30 + 0x08 + 0x20 + 0x10 + prestore_val
            ChkSum = (ChkSum % 0x60) + 0x20

            CmdString = pack( '>15B', 0x01, 0x57, 0x7F, 0x03, 0x25, 0x50, 0x53, 0x30, \
                                      0x08, 0x20, 0x10, prestore_val, 0x1F, ChkSum, 0x02)
            self.__SetHelper('PresetStore', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetStore')


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def xlca_25_630_2040(self):
        self.Inp_Channel = {
            '1'   : 0x20,
            '2'   : 0x21
        }

        self.Out_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22,
            '4'   : 0x23
        }

    def xlca_25_630_3060(self):
        self.Inp_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22
        }

        self.Out_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22,
            '4'   : 0x23,
            '5'   : 0x24,
            '6'   : 0x25
        }

    def xlca_25_630_4080(self):
        self.Inp_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22,
            '4'   : 0x23
        }

        self.Out_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22,
            '4'   : 0x23,
            '5'   : 0x24,
            '6'   : 0x25,
            '7'   : 0x26,
            '8'   : 0x27
        }

    def xlca_25_630_8080(self):
        self.Inp_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22,
            '4'   : 0x23,
            '5'   : 0x24,
            '6'   : 0x25,
            '7'   : 0x26,
            '8'   : 0x27
        }

        self.Out_Channel = {
            '1'   : 0x20,
            '2'   : 0x21,
            '3'   : 0x22,
            '4'   : 0x23,
            '5'   : 0x24,
            '6'   : 0x25,
            '7'   : 0x26,
            '8'   : 0x27
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=2, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
