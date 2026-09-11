from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'VX4S': self.nvstr_29_3603_C,
            'VX2U': self.nvstr_29_3603_A,
            'VX4U': self.nvstr_29_3603_A,
            'VX4': self.nvstr_29_3603_B,
            }


        self.Commands = {
            'Brightness': { 'Status': {}},
            'Contrast': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPLayout': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPTransparency': { 'Status': {}},
            'RecallPreset': { 'Status': {}},
            'ResetPreset': { 'Status': {}},
            'SavePreset': { 'Status': {}},
            'ScreenLockMode': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }


    def calcChkSum(self, cmdstring):
        ChkSum = 0
        for i in range(0,len(cmdstring)):
            ChkSum = ChkSum + cmdstring[i]
        ChkSum = ChkSum + 0x5555
        Chksum_H = ChkSum >> 8
        Chksum_L = ChkSum & 0xFF
        return Chksum_H.to_bytes(1, 'big'),Chksum_L.to_bytes(1, 'big')
    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 255:
            CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x01,0xFF,0xFF,0xFF,0x01,0x00,0x01,0x00,0x00,0x02,0x01,0x00,value)
            ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
            BrightnessCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 200:
            CmdString = pack('>17B',0x00,0x00,0xFE,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x02,0x00,0x05,0x13,0x01,0x00,value)
            ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
            ContrastCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : 0x00, 
            'Freeze' : 0x01, 
            'Black'  : 0x02
        }

        CmdString = pack('>17B',0x00,0x00,0xFE,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x50,0x00,0x20,0x02,0x01,0x00,ValueStateValues[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        DisplayModeCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        CmdString = pack('>17B',0x00,0x00,0xFE,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x2D,0x00,0x20,0x02,0x01,0x00,self.Inputs[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        InputCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetPIPInput(self, value, qualifier):

        CmdString = pack('>17B',0x00,0x00,0xFE,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x31,0x00,0x20,0x02,0x01,0x00,self.Inputs[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        PIPInputCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def SetPIPLayout(self, value, qualifier):

        ValueStateValues = {
            'Top Left'     : 0x01, 
            'Bottom Left'  : 0x02, 
            'Top Right'    : 0x03, 
            'Bottom Right' : 0x04, 
            'Center'       : 0x05
        }

        CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x44,0x00,0x20,0x02,0x01,0x00,ValueStateValues[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        PIPLayoutCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x30,0x00,0x20,0x02,0x01,0x00,ValueStateValues[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        PIPModeCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPIPTransparency(self, value, qualifier):

        if 0 <= value <= 15:
            CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x32,0x00,0x20,0x02,0x01,0x00,value)
            ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
            PIPTransparencyCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
            self.__SetHelper('PIPTransparency', PIPTransparencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPTransparency')

    def SetRecallPreset(self, value, qualifier):

        CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x70,0x00,0x20,0x02,0x01,0x00,int(value))
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        RecallPresetCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
    def SetResetPreset(self, value, qualifier):

        CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x72,0x00,0x20,0x02,0x01,0x00,int(value))
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        ResetPresetCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('ResetPreset', ResetPresetCmdString, value, qualifier)
    def SetSavePreset(self, value, qualifier):

        CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x71,0x00,0x20,0x02,0x01,0x00,int(value))
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        SavePresetCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)

    def SetScreenLockMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        CmdString = pack('>17B',0x00,0x00,0xFE,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0xF7,0x00,0x20,0x02,0x01,0x00,ValueStateValues[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        ScreenLockModeCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('ScreenLockMode', ScreenLockModeCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Off'         : 0x00, 
            'Custom'      : 0x01, 
            'Full Screen' : 0x02
        }

        CmdString = pack('>17B',0x00,0x00,0xFE,0xFF,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x20,0x02,0x01,0x00,ValueStateValues[value])
        ChkSum_H, ChkSum_L = self.calcChkSum(CmdString)
        ZoomCmdString = b'\x55\xAA' + CmdString + ChkSum_L + ChkSum_H
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
        self.Send(commandstring)

    def nvstr_29_3603_C(self):
        self.Inputs = {
                'DVI'         : 0x10, 
                'HDMI'        : 0xA0, 
                'VGA 1'       : 0x01, 
                'VGA 2'       : 0x02, 
                'CVBS 1'      : 0x71, 
                'CVBS 2'      : 0x72, 
                'SDI'         : 0x40, 
                'DisplayPort' : 0x90
            }

    def nvstr_29_3603_A(self):
        self.Inputs = {
                'DVI'         : 0x10, 
                'HDMI'        : 0xA0, 
                'VGA 1'       : 0x01, 
                'VGA 2'       : 0x02, 
                'CVBS 1'      : 0x71, 
                'CVBS 2'      : 0x72, 
                'DisplayPort' : 0x90
            }        

    def nvstr_29_3603_B(self):   
        self.Inputs = {
                'DVI'         : 0x10, 
                'HDMI'        : 0xA0, 
                'VGA 1'       : 0x01, 
                'VGA 2'       : 0x02, 
                'VGA 3'       : 0x03, 
                'CVBS 1'      : 0x71, 
                'CVBS 2'      : 0x72, 
                'CVBS 3'      : 0x73, 
                'DisplayPort' : 0x90
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

