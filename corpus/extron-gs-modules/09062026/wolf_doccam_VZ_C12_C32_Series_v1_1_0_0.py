# How to use the Module in Main script
#
# import module by name of the py file
# import module
#
# Declare controller
# dvPro350 = ProcessorDevice('dvPro350')
#
# Specify communication settings if Serial
# SerialPort1 = module.SerialClass(dvPro350, 'COM1', Baud=19200, Model='SMX 200')
#
# Specify communication settings if Ethernet (for TCP)
# EthernetPort1 = module.EthernetClass('10.10.10.10', 23, Model='SMX 200')
#
# When using Ethernet Class:
# EthernetPort1.Connect() must be coded,
# Module does NOT connect to
# the device automatically.
#
# How to send a control command
# without qualifiers
# SerialPort1.Set('AudioMute', 'On')
#
# with qualifiers
# The 3rd argument (qualifier) must be specified as the example {'Input': 1}
# SerialPort1.Set('AudioMute', 'On',{'Input': 1})
#
# How  to send a control command with qualifier, but no value
# This example also show how to send multiple qualifier arguments
# SerialPort1.Set('MatrixTieCommand', None, {'Input': 1,'Ouput': 2,'TieType': 'Video'})
#
# How to send a update command
# Without qualifier
# SerialPort1.Update('AudioMute')
#
# How to send a update command
# With qualifier
# SerialPort1.Update('AudioMute',{'Input': 1})
#
# To avoid using delay after an Update command is called, it is recommended to use
# SubscribeStatus for commands that are query often, for logic or one time check
# use the example below
# How to subscribe to a command
# module.SubscribeStatus('Power',None, MethodToCall)
# any time we get status back for power from the device the Subscribed command
# 'Power' will call the Method defined 'MethodToCall'
# 'MethodToCall' must take 3 parameters (command, value, qualifier)
#
# def MethodToCall(command, value, qualifier)
#     if value == 'On':
#        Logic here
#     else:
#        Logic here
#
# All statuses of the Device will be store into a dictionary,
#
# Get Current Status of Audio Mute w/o qualifier.
# value will be equals to one of the states for the command requested
# value = SerialPort1.ReadStatus('AudioMute')
#
# Get Current Status of Audio Mute with qualifier
# value = SerialPort1.ReadStatus('AudioMute', {'Input': 1})
#
#####################################################################
# List of Models Supported by module
#####################################################################
# VZ-C12,VZ-C32,VZ-C12-3,VZ-C32-3,
#
#####################################################################
# REQUIRED VARIABLE SETTINGS
#####################################################################
# Unidirectional variable must be set to 'True' if status is not required
# Default value is 'False'
# Example: ModuleName.Unidirectional = 'True'

# ConnectionCounter variable must be set the number of queries that will be sent to the device
# before displaying 'Disconnected' if no response is received. Default value is 15.
# Example: ModuleName.ConnectionCounter = 5

from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time
from struct import pack
from struct import unpack


class DeviceClass(): 
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'ColorMode': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Gain': {'Status': {}},
            'Image': {'Status': {}},
            'ImageTurn': {'Status': {}},
            'Iris': {'Parameters': ['Speed'], 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp Select'], 'Status': {}},
            'Light': {'Status': {}},
            'MemoryRecall': {'Status': {}},
            'MemoryStore': {'Status': {}},
            'Menu': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OutputResolution': {'Parameters': ['Output Select'], 'Status': {}},
            'PerformWB': {'Status': {}},
            'PIP': {'Status': {}},
            'PosandNeg': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'ShowAll': {'Status': {}},
            'Source': {'Status': {}},
            'TextEnhancer': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\x00][\x32][\x01]([\x00-\x01])'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'[\x00][\x6D][\x01]([\x00-\x04])'), self.__MatchColorMode, None)
            self.AddMatchString(re.compile(b'[\x00][\x29][\x01]([\x00-\x02])'), self.__MatchDigitalZoom, None)
            self.AddMatchString(re.compile(b'[\x00][\x56][\x01]([\x00-\x01])'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'[\x00][\x60][\x01]([\x00-\x18])'), self.__MatchGain, None)
            self.AddMatchString(re.compile(b'[\x00][\x86][\x01]([\x00-\x01])'), self.__MatchImage, None)
            self.AddMatchString(re.compile(b'[\x00][\x83][\x01]([\x00-\x03])'), self.__MatchImageTurn, None)
            self.AddMatchString(re.compile(b'[\x00][\x80][\x01]([\x00-\x01])'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'[\x00]([\xA3-\xA4])[\x01]([\x00-\xFF]{2})'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'[\x00][\xA0][\x01]([\x00-\x01])'), self.__MatchLight, None)
            self.AddMatchString(re.compile(b'[\x00][\x98][\x01]([\x00-\x03])'), self.__MatchMenu, None)
            self.AddMatchString(re.compile(b'[\x00]([\x50-\x51])[\x01]([\x00-\xFF])'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'[\x00][\x5D][\x01]([\x00-\x01])'), self.__MatchPIP, None)
            self.AddMatchString(re.compile(b'[\x00][\x54][\x01]([\x00-\x02])'), self.__MatchPosandNeg, None)
            self.AddMatchString(re.compile(b'[\x00][\x30][\x01]([\x00-\x01])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'[\x00][\x93][\x01]([\x00-\x01])'), self.__MatchShowAll, None)
            self.AddMatchString(re.compile(b'[\x00][\x9E][\x01]([\x00-\x03])'), self.__MatchSource, None)
            self.AddMatchString(re.compile(b'[\x00][\x85][\x01]([\x00-\x01])'), self.__MatchTextEnhancer, None)
            self.AddMatchString(re.compile(b'([\x80-\x81])([\x0A]|[\x31]|[\x29]|[\x56]|[\xA0]|[\x98]|[\x5D]|[\x30])([\x01-\x09])'), self.__MatchError, None)


    def SetAutoFocus(self, value, qualifier):
        AutoFocusCmdString = b'\x01\x31\x01\x10'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            
    def SetAutoIris(self, value, qualifier):
        AutoIrisStateValues = {
            'On'  : b'\x01\x32\x01\x01',
            'Off' : b'\x01\x32\x01\x00',
            }
        AutoIrisCmdString = AutoIrisStateValues[value]
        self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def UpdateAutoIris(self, value, qualifier): 
        AutoIrisCmdString = b'\x00\x32\x00'
        self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def __MatchAutoIris(self, match, qualifier):
        AutoIrisStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = AutoIrisStateNames[match.group(1).decode()]
        self.WriteStatus('AutoIris', value, None)

    def SetColorMode(self, value, qualifier):
        ColorModeStateValues = {
            'Black/White'       :   b'\x01\x6D\x01\x00',
            'Presentation'      :   b'\x01\x6D\x01\x01',
            'Natural'           :   b'\x01\x6D\x01\x02',
            'Video Conference'  :   b'\x01\x6D\x01\x03',
            'Manual'            :   b'\x01\x6D\x01\x04',
            }
        ColorModeCmdString = ColorModeStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier, 1)

    def UpdateColorMode(self, value, qualifier): 
        ColorModeCmdString = b'\x00\x6D\x00'
        self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def __MatchColorMode(self, match, qualifier):
        ColorModeStateNames = {
            '\x00'  :   'Black/White',
            '\x01'  :   'Presentation',
            '\x02'  :   'Natural',
            '\x03'  :   'Video Conference',
            '\x04'  :   'Manual',
           }
        value = ColorModeStateNames[match.group(1).decode()]
        self.WriteStatus('ColorMode', value, None)

    def SetDigitalZoom(self, value, qualifier):
        DigitalZoomStateValues = {
            '2x'  : b'\x01\x29\x01\x01',
            '4x'  : b'\x01\x29\x01\x02',
            'Off' : b'\x01\x29\x01\x00',
            }
        DigitalZoomCmdString = DigitalZoomStateValues[value]
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier, 3)

    def UpdateDigitalZoom(self, value, qualifier): 
        DigitalZoomCmdString = b'\x00\x29\x00'
        self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def __MatchDigitalZoom(self, match, qualifier):
        DigitalZoomStateNames = {
            '\x01' : '2x',
            '\x02' : '4x',
            '\x00' : 'Off',
           }
        value = DigitalZoomStateNames[match.group(1).decode()]
        self.WriteStatus('DigitalZoom', value, None)

    def SetExecutiveMode(self, value, qualifier):
        ExecutiveModeStateValues = {
            'On'  : b'\x01\x80\x01\x01',
            'Off' : b'\x01\x80\x01\x00',
            }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier, 4)

    def UpdateExecutiveMode(self, value, qualifier): 
        ExecutiveModeCmdString = b'\x00\x80\x00'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):
        ExecutiveModeStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFocus(self, value, qualifier):
        FocusStateName = {
                'Far'  : 0x01,
                'Near' : 0x02,
            }

        qRange = int(qualifier['Speed'])
        if 1 <= qRange <= 15:
            if value == 'Stop':
                FocusCmdString = pack('>BBBBBB',0x01,0x21,0x03,0x00,0x00,0x00)
            else:
                FocusCmdString = pack('>BBBBBB',0x01,0x21,0x03,FocusStateName[value],0x00,qRange)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)
        else:
            print('Inappropriate Command for SetFocus')

    def SetFreeze(self, value, qualifier):
        FreezeStateValues = {
            'On'  : b'\x01\x56\x01\x01',
            'Off' : b'\x01\x56\x01\x00',
            }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier, 3)

    def UpdateFreeze(self, value, qualifier): 
        FreezeCmdString = b'\x00\x56\x00'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):
        FreezeStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGain(self, value, qualifier):
        GainConstraints = {
            'Min' : 0,
            'Max' : 24
        }

        if GainConstraints['Min'] <= value <= GainConstraints['Max']:
            GainCmdString = pack('>BBBB',0x01,0x60,0x01,int(value))
            self.__SetHelper('Gain', GainCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier): 
        GainCmdString = b'\x00\x60\x00'
        self.__UpdateHelper('Gain', GainCmdString, value, qualifier)

    def __MatchGain(self, match, qualifier):
        value = match.group(1)
        value = int(value[0])
        self.WriteStatus('Gain', value, None)

    def SetImage(self, value, qualifier):
        ImageStateValues = {
            'On'  : b'\x01\x86\x01\x01',
            'Off' : b'\x01\x86\x01\x00',
            }
        ImageCmdString = ImageStateValues[value]
        self.__SetHelper('Image', ImageCmdString, value, qualifier, 3)

    def UpdateImage(self, value, qualifier): 
        ImageCmdString = b'\x00\x86\x00'
        self.__UpdateHelper('Image', ImageCmdString, value, qualifier)

    def __MatchImage(self, match, qualifier):
        ImageStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = ImageStateNames[match.group(1).decode()]
        self.WriteStatus('Image', value, None)

    def SetImageTurn(self, value, qualifier):
        ImageTurnStateValues = {
            'Toggle': b'\x01\x83\x01\x02',
            'Off'   : b'\x01\x83\x01\x00',
            }
        ImageTurnCmdString = ImageTurnStateValues[value]
        self.__SetHelper('ImageTurn', ImageTurnCmdString, value, qualifier, 3)

    def UpdateImageTurn(self, value, qualifier): 
        ImageTurnCmdString = b'\x00\x83\x00'
        self.__UpdateHelper('ImageTurn', ImageTurnCmdString, value, qualifier)

    def __MatchImageTurn(self, match, qualifier):
        ImageTurnStateNames = {
            '\x00' : '0 Degrees',
            '\x01' : '-90 Degrees',
            '\x02' : '180 Degrees',
            '\x03' : '90 Degrees',
           }
        value = ImageTurnStateNames[match.group(1).decode()]
        self.WriteStatus('ImageTurn', value, None)

    def SetIris(self, value, qualifier):
        IrisStateValues = {
            'Open' : 0x01,
            'Close': 0x02,
            }
            
        SpeedStateValues = {
            'Normal' : 0x01,
            'Fast'   : 0x02
        }
        Irisspeed = qualifier['Speed']       
        if Irisspeed in SpeedStateValues:
            if value == 'Stop':
                IrisCmdString = pack('>BBBB',0x01,0x2F,0x01, 0x00)
            else:
                IrisCmdString = pack('>BBBBBB', 0x01,0x22,0x03,IrisStateValues[value],0x00,SpeedStateValues[Irisspeed])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier,3)
        else:
            print('Invalid Command for SetIris')

    def SetLight(self, value, qualifier):
        LightStateValues = {
            'On'  : b'\x01\xA0\x01\x01',
            'Off' : b'\x01\xA0\x01\x00',
            }
        LightCmdString = LightStateValues[value]
        self.__SetHelper('Light', LightCmdString, value, qualifier, 3)

    def UpdateLight(self, value, qualifier): 
        LightCmdString = b'\x00\xA0\x00'
        self.__UpdateHelper('Light', LightCmdString, value, qualifier)

    def __MatchLight(self, match, qualifier):
        LightStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = LightStateNames[match.group(1).decode()]
        self.WriteStatus('Light', value, None)

    def UpdateLampUsage(self, value, qualifier): 
        a = qualifier['Lamp Select']

        lampSelect = {
            '1' :   0xA3,
            '2' :   0xA4,
        }
        if a in ['1','2']:
            LampUsageCmdString = pack('>BBB',0x00,lampSelect[a],0x00)
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, qualifier):
        
        lampSelect = {
            0xA3 : '1',
            0xA4 : '2',
        }

        a = match.group(1)[0]
        value = unpack('>H', match.group(2))[0]
        self.WriteStatus('LampUsage', value, {'Lamp Select': lampSelect[a]})

    def SetMemoryRecall(self, value, qualifier):
        if 1 <= int(value) <= 9:
            MemoryRecallCmdString = pack('>BBBB',0x01,0x91,0x01,int(value))
            self.__SetHelper('MemoryRecall', MemoryRecallCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetMemoryRecall')

    def SetMemoryStore(self, value, qualifier):

        if 'Snapshot' in value:
            MemoryStoreCmdString = b'\x01\x92\x01\x10'
        elif 'Erase' in value:
            MemoryStoreCmdString = b'\x01\x92\x01\x20'
        elif 1 <= int(value) <= 9:
            MemoryStoreCmdString =  pack('>BBBB',0x01,0x92,0x01,int(value))
        

        if MemoryStoreCmdString and self.__SafeToSet('MemoryStore'):
            self.__SetHelper('MemoryStore', MemoryStoreCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetMemoryStore')

    def SetMenu(self, value, qualifier):
        MenuStateValues = {
            'On'  : b'\x01\x98\x01\x01',
            'Off' : b'\x01\x98\x01\x00',
            }
        MenuCmdString = MenuStateValues[value]
        self.__SetHelper('Menu', MenuCmdString, value, qualifier)

    def UpdateMenu(self, value, qualifier): 
        MenuCmdString = b'\x00\x98\x00'
        self.__UpdateHelper('Menu', MenuCmdString, value, qualifier)

    def __MatchMenu(self, match, qualifier):
        MenuStateNames = {
            '\x01' : 'On',
            '\x02' : 'On',
            '\x03' : 'On',
            '\x00' : 'Off',
           }
        value = MenuStateNames[match.group(1).decode()]
        self.WriteStatus('Menu', value, None)

    def SetMenuNavigation(self, value, qualifier):
        MenuNavigationStateValues = {
            'Up'    : 0x02,
            'Down'  : 0x08,
            'Left'  : 0x04,
            'Right' : 0x06,
            'Enter' : 0x05,
            }
        MenuNavigationCmdString = pack('>BBBB',0x01,0x99,0x01,MenuNavigationStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetOutputResolution(self, value, qualifier):
        a = qualifier['Output Select']

        Output = {
            'DVI'  :   0x51,
            'RGB'  :   0x50,
            }

        OutputResolutionStateValues = {
            'Off'                   :   0xFF,
            'Auto'                  :   0x00,
            'SVGA/60 (800x600)'     :   0x01,
            'XGA/60 (1024x768)'     :   0x04,
            'SXGA-/60 (1280x960)'   :   0x08,
            'SXGA/60 (1280x1024)'   :   0x0A,
            'UXGA/60 (1600x1200)'   :   0x0D,
            'SXGA+/60 (1400x1050)'  :   0x12,
            'VGA/60 (640x480)'      :   0x14,
            '720p/50 (1280x720)'    :   0x15,
            '720p/60'               :   0x16,
            '1080p/50 (1920x1080)'  :   0x17,
            '1080p/60'              :   0x18,
            'WSXGA/60 (1680x1050)'  :   0x1A,
            'WXGA/60 (1366x768)'    :   0x1B,
            'WUXGA/60 (1920x1200)'  :   0x1C,
            'WXGA+/60 (1440x900)'   :   0x1D,
            'WXGA*/60 (1280x800)'   :   0x1E,
            '1080p/30'              :   0x20,
            }
        if a in Output:
            OutputResolutionCmdString = pack('>BBBB',0x01,Output[a],0x01,OutputResolutionStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier): 
        a = qualifier['Output Select']
        Output = {
            'DVI'  :   0x51,
            'RGB'  :   0x50,
            }        
        OutputResolutionCmdString = pack('>BBB',0x00,Output[a],0x00)

        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        
    def __MatchOutputResolution(self, match, qualifier):
        Output = {
        '\x51'  :   'DVI',
        '\x50'  :   'RGB',
        }

        OutputResolutionStateNames = {
            b'\xFF'  :   'Off',
            b'\x00'  :   'Auto',
            b'\x01'  :   'SVGA/60 (800x600)',
            b'\x04'  :   'XGA/60 (1024x768)',
            b'\x08'  :   'SXGA-/60 (1280x960)',
            b'\x0A'  :   'SXGA/60 (1280x1024)',
            b'\x0D'  :   'UXGA/60 (1600x1200)',
            b'\x12'  :   'SXGA+/60 (1400x1050)',
            b'\x14'  :   'VGA/60 (640x480)',
            b'\x15'  :   '720p/50 (1280x720)',
            b'\x16'  :   '720p/60',
            b'\x17'  :   '1080p/50 (1920x1080)',
            b'\x18'  :   '1080p/60',
            b'\x1A'  :   'WSXGA/60 (1680x1050)',
            b'\x1B'  :   'WXGA/60 (1366x768)',
            b'\x1C'  :   'WUXGA/60 (1920x1200)',
            b'\x1D'  :   'WXGA+/60 (1440x900)',
            b'\x1E'  :   'WXGA*/60 (1280x800)',
            b'\x20'  :   '1080p/30',
            }
        a = match.group(1).decode()
        value = OutputResolutionStateNames[match.group(2)]
        self.WriteStatus('OutputResolution', value, {'Output Select': Output[a]})

    def SetPerformWB(self, value, qualifier):
        PerformWBCmdString = b'\x01\x65\x01\x10'
        self.__SetHelper('PerformWB', PerformWBCmdString, value, qualifier,2)

    def SetPIP(self, value, qualifier):
        PIPStateValues = {
            'On'  : b'\x01\x5D\x01\x01',
            'Off' : b'\x01\x5D\x01\x00',
            }
        PIPCmdString = PIPStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier, 3)

    def UpdatePIP(self, value, qualifier): 
        PIPCmdString = b'\x00\x5D\x00'
        self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)

    def __MatchPIP(self, match, qualifier):
        PIPStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = PIPStateNames[match.group(1).decode()]
        self.WriteStatus('PIP', value, None)

    def SetPosandNeg(self, value, qualifier):
        PosandNegStateValues = {
            'Positive'  : b'\x01\x54\x01\x00',
            'Negative'  : b'\x01\x54\x01\x01',
            'Blue'      : b'\x01\x54\x01\x02',
            }
        PosandNegCmdString = PosandNegStateValues[value]
        self.__SetHelper('PosandNeg', PosandNegCmdString, value, qualifier, 1)

    def UpdatePosandNeg(self, value, qualifier): 
        PosandNegCmdString = b'\x00\x54\x00'
        self.__UpdateHelper('PosandNeg', PosandNegCmdString, value, qualifier)

    def __MatchPosandNeg(self, match, qualifier):
        PosandNegStateNames = {
            '\x00' : 'Positive',
            '\x01' : 'Negative',
            '\x02' : 'Blue',
           }
        value = PosandNegStateNames[match.group(1).decode()]
        self.WriteStatus('PosandNeg', value, None)

    def SetPower(self, value, qualifier):
        PowerStateValues = {
            'On'  : b'\x01\x30\x01\x01',
            'Off' : b'\x01\x30\x01\x00',
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        PowerCmdString = b'\x00\x30\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, qualifier):
        PowerStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
           
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):
        PresetRecallStateValues = {
            '1' : b'\x01\x40\x01\x01',
            '2' : b'\x01\x40\x01\x02',
            '3' : b'\x01\x40\x01\x03',
            }
        PresetRecallCmdString = PresetRecallStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier, 3)
            
    def SetPresetSave(self, value, qualifier):
        PresetSaveStateValues = {
            '1' : b'\x01\x41\x01\x01',
            '2' : b'\x01\x41\x01\x02',
            '3' : b'\x01\x41\x01\x03',
            }
        PresetSaveCmdString = PresetSaveStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier, 3)
    
    def SetShowAll(self, value, qualifier):
        ShowAllStateValues = {
            'On'  : b'\x01\x93\x01\x01',
            'Off' : b'\x01\x93\x01\x00',
            }
        ShowAllCmdString = ShowAllStateValues[value]
        self.__SetHelper('ShowAll', ShowAllCmdString, value, qualifier, 3)

    def UpdateShowAll(self, value, qualifier):
        ShowAllCmdString = b'\x00\x93\x00'
        self.__UpdateHelper('ShowAll', ShowAllCmdString, value, qualifier)

    def __MatchShowAll(self, match, qualifier):
        ShowAllStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = ShowAllStateNames[match.group(1).decode()]
        self.WriteStatus('ShowAll', value, None)

    def SetSource(self, value, qualifier):
        SourceStateValues = {
            'Live'   : b'\x01\x9E\x01\x00',
            'Mem'    : b'\x01\x9E\x01\x01',
            'USB'    : b'\x01\x9E\x01\x02',
            'Extern' : b'\x01\x9E\x01\x03',
            }
        SourceCmdString = SourceStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier, 4)

    def UpdateSource(self, value, qualifier): 
        SourceCmdString = b'\x00\x9E\x00'
        self.__UpdateHelper('Source', SourceCmdString, value, qualifier)

    def __MatchSource(self, match, qualifier):
        SourceStateNames = {
            '\x00' : 'Live',
            '\x01' : 'Mem',
            '\x02' : 'USB',
            '\x03' : 'Extern',
           }
        value = SourceStateNames[match.group(1).decode()]
        self.WriteStatus('Source', value, None)

    def SetTextEnhancer(self, value, qualifier):
        TextEnhancerStateValues = {
            'On'   : b'\x01\x85\x01\x01',
            'Off'  : b'\x01\x85\x01\x00',
            }
        TextEnhancerCmdString = TextEnhancerStateValues[value]
        self.__SetHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier, 2)

    def UpdateTextEnhancer(self, value, qualifier): 
        TextEnhancerCmdString = b'\x00\x85\x00'
        self.__UpdateHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)

    def __MatchTextEnhancer(self, match, qualifier):
        TextEnhancerStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off',
           }
        value = TextEnhancerStateNames[match.group(1).decode()]
        self.WriteStatus('TextEnhancer', value, None)

    def SetZoom(self, value, qualifier):
        ZoomStateValues = {
            'Wide' : 0x01,
            'Tele' : 0x02,
            }
        qRange = int(qualifier['Speed'])
        if 1 <= qRange <= 15:
            if value == 'Stop':
                ZoomCmdString = pack('>BBBBBB',0x01,0x20,0x03,0x00,0x00,0x00)
            else:
                ZoomCmdString = pack('>BBBBBB',0x01,0x20,0x03,ZoomStateValues[value],0x00,qRange)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier, 3)
        else:
            print('Inappropriate Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)
        
    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):
        CommandAction = {
            b'\x80' : 'Get',
            b'\x81' : 'Set'
            }
        CommandList = {
            b'\x0A' : 'Aspect Ratio',
            b'\x31' : 'Auto Focus',
            b'\x29' : 'Digital Zoom',
            b'\x56' : 'Freeze',
            b'\xA0' : 'Light',
            b'\x98' : 'Menu Call',
            b'\x5D' : 'PIP',
            b'\x30' : 'Power',
            }
        ErrorType = {
            b'\x01' : 'Time Out',
            b'\x02' : 'Invalid Cmd',
            b'\x03' : 'Invalid Parameter',
            b'\x04' : 'Invalid Length',
            b'\x05' : 'FiFo Full',
            b'\x06' : 'Firmware Update Error',
            b'\x07' : 'Access Denied',
            b'\x08' : 'AUTH Required',
            b'\x09' : 'Busy'
            }
        CmdType = CommandAction[match.group(1)]
        CmdName = CommandList[match.group(2)]
        errorString = '{0} {1} Error: {2}'.format(CmdName, CmdType, ErrorType[match.group(3)])
        print(errorString)
   
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        pass

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
