from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog
import hashlib
from binascii import hexlify

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
        
        self.Models = {
            'PT-DS12K': self.pana_1_407_2lamps,
            'PT-DS12KE': self.pana_1_407_2lamps,
            'PT-DS12KU': self.pana_1_407_2lamps,
            'PT-DS20K': self.pana_1_407_4lamps,
            'PT-DW11K': self.pana_1_407_2lamps,
            'PT-DW11KE': self.pana_1_407_2lamps,
            'PT-DW11KU': self.pana_1_407_2lamps,
            'PT-DW17K': self.pana_1_407_4lamps,
            'PT-DZ10K': self.pana_1_407_2lamps,
            'PT-DZ10KE': self.pana_1_407_2lamps,
            'PT-DZ10KU': self.pana_1_407_2lamps,
            'PT-DZ13K': self.pana_1_407_2lamps,
            'PT-DZ13KE': self.pana_1_407_2lamps,
            'PT-DZ13KU': self.pana_1_407_2lamps,
            'PT-DZ16K': self.pana_1_407_4lamps,
            'PT-DZ21K': self.pana_1_407_4lamps,
            'SDS20KC': self.pana_1_407_4lamps,
            'SDW17KC': self.pana_1_407_4lamps,
            'SDZ18KC': self.pana_1_407_4lamps,
            'SDZ21KC': self.pana_1_407_4lamps,
         }
        
        self.Commands = {
            'AspectRatio': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampStatus': {'Status': {}},
            'LampUsage': {'Status': {}, 'Parameters': ['LampNumber']},
            'LensMemoryDelete': {'Status': {}},
            'LensMemoryLoad': {'Status': {}},
            'LensMemorySave': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }
        
        self.DeviceID = '1'

    @property
    def DeviceID(self):
        return self._DeviceID
    
    @DeviceID.setter
    def DeviceID(self, value):
        temp = str(value)
        if temp.isnumeric():
            temp = int(temp)
            if temp < 1 or temp > 64:
                print('Invalid DeviceID given, should be between 1 and 64, or between A and Z, or ZZ for broadcast.')
            else:
                self._DeviceID = '{0:02}'.format(temp)
        elif len(temp) == 1 and temp.isalpha():
            self._DeviceID = '0' + temp
        elif temp == 'ZZ':
            self._DeviceID = 'ZZ'
        else:
            print('Invalid DeviceID given, should be between 1 and 64, or between A and Z, or ZZ for broadcast.')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Auto' :    '0',
            '4:3' :     '1',
            '16:9' :    '2',
            'Through' : '5',
            'HV Fit' :  '6',
            'H Fit' :   '9',
            'V Fit' :   '10',
            }
        AspectRatioCmdString = '\x02AD{0};VSE:{1}\x03'.format(self._DeviceID,AspectRatioStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier): 

        AspectRatioStateNames = {
             '0' : 'Auto',
             '1' : '4:3',
             '2' : '16:9',
             '5' : 'Through',
             '6' : 'HV Fit',
             '9' : 'H Fit',
            '10' : 'V Fit',
            }

        matchString = re.compile('\x02([0-9]{1,2})\x03')
        AspectRatioCmdString = '\x02AD{0};QSE\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(matchString, res)
                if matchObject:
                    value = matchObject.group(1)
                    self.WriteStatus('AspectRatio', AspectRatioStateNames[value], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusNames = {
            0x00000000000000000000000000000000 : 'No errors',
            0x00000000000000000000000000000001 : 'Intake air temperature warning',
            0x00000000000000000000000000000002 : 'Optical module high temperature warning',
            0x00000000000000000000000000000004 : 'Exhaust air high temperature warning',
            0x00000000000000000000000000000008 : 'Optical module low temperature warning',
            0x00000000000000000000000000000010 : 'Intake air temperature error',
            0x00000000000000000000000000000020 : 'Optical module high temperature error',
            0x00000000000000000000000000000040 : 'Exhaust air high temperature error',
            0x00000000000000000000000000000080 : 'Optical module low temperature error',
            0x00000000000000000000000000000100 : 'LAMP1 runtime warning',
            0x00000000000000000000000000000200 : 'LAMP2 runtime warning',
            0x00000000000000000000000000000400 : 'LAMP3 runtime warning',
            0x00000000000000000000000000000800 : 'LAMP4 runtime warning',
            0x00000000000000000000000000001000 : 'Lamp1 runtime is over',
            0x00000000000000000000000000002000 : 'Lamp2 runtime is over',
            0x00000000000000000000000000004000 : 'Lamp3 runtime is over',
            0x00000000000000000000000000008000 : 'Lamp4 runtime is over',
            0x00000000000000000000000000010000 : 'Unexpected Lamp1 OFF',
            0x00000000000000000000000000020000 : 'Unexpected Lamp2 OFF',
            0x00000000000000000000000000040000 : 'Unexpected Lamp3 OFF',
            0x00000000000000000000000000080000 : 'Unexpected Lamp4 OFF',
            0x00000000000000000000000000100000 : 'Lamp1 failed to light',
            0x00000000000000000000000000200000 : 'Lamp2 failed to light',
            0x00000000000000000000000000400000 : 'Lamp3 failed to light',
            0x00000000000000000000000000800000 : 'Lamp4 failed to light',
            0x00000000000000000000000001000000 : 'Lamp1 not installed',
            0x00000000000000000000000002000000 : 'Lamp2 not installed',
            0x00000000000000000000000004000000 : 'Lamp3 not installed',
            0x00000000000000000000000008000000 : 'Lamp4 not installed',
            0x00000000000000000000000010000000 : 'Low AC voltage warning',
            0x00000000000000000000000020000000 : 'Cover open error',
            0x00000000000000000000000040000000 : 'Special filter setting',
            0x00000000000000000000000080000000 : 'Luminance sensor error',
            0x00000000000000000000000100000000 : 'Intake air temperature sensor disconnected',
            0x00000000000000000000000200000000 : 'Optical module temperature sensor disconnected',
            0x00000000000000000000000400000000 : 'Exhaust air temperature sensor disconnected',
            0x00000000000000000000000800000000 : 'Airflow sensor disconnected',
            0x00000000000000000000001000000000 : 'Filter clogged warning',
            0x00000000000000000000002000000000 : 'Battery replacement for the internal clock',
            0x00000000000000000000004000000000 : 'Angle sensor error',
            0x00000000000000000000008000000000 : 'Portrait installation warning',
            0x00000000000000000000010000000000 : 'Air filter unit warning',
            0x00000000000000000000020000000000 : 'Filter clogged error',
            0x00000000000000000000040000000000 : 'FAN1 (Exhaust-R) error/warning',
            0x00000000000000000000080000000000 : 'FAN2 (Exhaust-C) error/warning',
            0x00000000000000000000100000000000 : 'FAN3 (Exhaust-L) error/warning',
            0x00000000000000000000200000000000 : 'FAN4 (Intake1) error/warning',
            0x00000000000000000000400000000000 : 'FAN5 (Intake2) error/warning',
            0x00000000000000000000800000000000 : 'FAN6 (Lamp1) error/warning',
            0x00000000000000000001000000000000 : 'FAN7 (Lamp2) error/warning',
            0x00000000000000000002000000000000 : 'FAN8 (Power) error/warning',
            0x00000000000000000004000000000000 : 'FAN9 (Ballast) error/warning',
            0x00000000000000000008000000000000 : 'FAN10 (Composition Mirror) error/warning',
            0x00000000000000000010000000000000 : 'FAN11 (DMD Exhaust) error/warning',
            0x00000000000000000020000000000000 : 'FAN12 (Color prism) error/warning',
            0x00000000000000000040000000000000 : 'FAN13 (DMD1) error/warning',
            0x00000000000000000080000000000000 : 'FAN14 (DMD2) error/warning',
            0x00000000000000000100000000000000 : 'FAN15 error/warning',
            0x00000000000000000200000000000000 : 'FAN16 error/warning',
            0x00000000000000000400000000000000 : 'FAN17 error/warning',
            0x00000000000000000800000000000000 : 'FAN18 error/warning',
            0x00000000000000001000000000000000 : 'FAN19 error/warning',
            0x00000000000000002000000000000000 : 'PUMP1 error/warning',
            0x00000000000000004000000000000000 : 'PUMP2 error/warning',
            0x00000000000000008000000000000000 : 'PUMP3 error/warning',
            0x00000000000000010000000000000000 : 'Portrait lamp warning',
            0x00000000000000020000000000000000 : 'Unsupported lamp warning',
            0x00000000000000040000000000000000 : 'Shutter error',
            0x00000000000000080000000000000000 : 'Dynamic iris error',
            0x00000000000000100000000000000000 : 'Lamp drive mode changeover error',
            0x00000000000001000000000000000000 : 'Lamp 1 memory error',
            0x00000000000002000000000000000000 : 'Lamp 2 memory error',
            0x00000000000004000000000000000000 : 'Lamp 3 memory error',
            0x00000000000008000000000000000000 : 'Lamp 4 memory error',
            0x00000000000100000000000000000000 : 'FPGA 1/2 configuration error',
            0x00000000000200000000000000000000 : 'FPGA 3 configuration error',
            0x00000000004000000000000000000000 : 'Lens mount error',
            0x00000000008000000000000000000000 : 'Ballast1 communication error',
            0x00000000010000000000000000000000 : 'Ballast2 communication error',
            0x00000000020000000000000000000000 : 'Ballast3 communication error',
            0x00000000040000000000000000000000 : 'Ballast4 communication error',
            0x00000000800000000000000000000000 : 'Installation angle warning',
            0x00000002000000000000000000000000 : 'Network microcomputer communication error',
            0x00000004000000000000000000000000 : 'Sub microcomputer (R8) communication error',
            0x00000008000000000000000000000000 : 'IIC communication error 1(RTC)',
            0x00000010000000000000000000000000 : 'IIC communication error 2(EEPROM)',
            0x00000020000000000000000000000000 : 'IIC communication error 3(LAMP1 EEPROM)',
            0x00000040000000000000000000000000 : 'IIC communication error 4(LAMP2 EEPROM)',
            0x00000080000000000000000000000000 : 'IIC communication error 5(LAMP3 EEPROM)',
            0x00000100000000000000000000000000 : 'IIC communication error 6(LAMP4 EEPROM)',
            0x00000200000000000000000000000000 : 'IIC communication error 7(EDID DIGITAL)',
            0x00000400000000000000000000000000 : 'IIC communication error 8(EDID ANALOG)',
            0x00000800000000000000000000000000 : 'IIC communication error 9(ADC1)',
            0x00001000000000000000000000000000 : 'IIC communication error 10(ADC2)',
            0x00002000000000000000000000000000 : 'IIC communication error 11(ACCELERATION SENSOR)',
            0x00004000000000000000000000000000 : 'IC communication error 12(OPTICAL SENSOR)',
            0x04000000000000000000000000000000 : 'FM-P.C.B communication error',
            0x08000000000000000000000000000000 : 'WF-P.C.B(GEOMERTY) communication error',
            0x20000000000000000000000000000000 : 'Lamp type is mixed warning',
            0x80000000000000000000000000000000 : 'Internal error',
        }

        matchString = re.compile(b'\x02AD' + bytes(self._DeviceID,'ascii') + b'\xFE(.*)\x03')
        DeviceStatusCmdString = b'\x02AD' + bytes(self._DeviceID,'ascii') + b'\xFE\xFE\x03'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(matchString, res.encode(encoding='iso-8859-1'))
                if matchObject:
                    value = int(matchObject.group(1).decode(encoding='iso-8859-1'),16)
                    self.WriteStatus('DeviceStatus', DeviceStatusNames.get(value,'Multiple errors'), qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On' :  '1',
            'Off' : '0',
            }
        FreezeCmdString = '\x02AD{0};OFZ:{1}\x03'.format(self._DeviceID,FreezeStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier): 

        FreezeStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        matchString = re.compile('\x02([0|1])\x03')
        FreezeCmdString = '\x02AD{0};QFZ\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(matchString, res)
                if matchObject:
                    value = matchObject.group(1)
                    self.WriteStatus('Freeze', FreezeStateNames[value], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'RGB1' :  'RG1',
            'RGB2' :  'RG2',
            'Video' : 'VID',
            'DVI' :   'DVI',
            'HDMI' :  'HD1',
            'SDI1' :  'SD1',
            'SDI2' :  'SD2',
            }
        InputCmdString = '\x02AD{0};IIS:{1}\x03'.format(self._DeviceID,InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier): 

        InputStateNames = {
            'RG1': 'RGB1',
            'RG2': 'RGB2',
            'VID': 'Video',
            'DVI': 'DVI',
            'HD1': 'HDMI',
            'SD1': 'SDI1',
            'SD2': 'SDI2',
        }
        matchString = re.compile('\x02(RG1|RG2|VID|DVI|HD1|SD1|SD2)\x03')
        InputCmdString = '\x02AD{0};QIN\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)

        if res:
            try:
                matchObject = re.search(matchString, res)
                if matchObject:
                    value = matchObject.group(1)
                    self.WriteStatus('Input', InputStateNames[value], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampSelect(self, value, qualifier):

        LampSelectCmdString = '\x02AD{0};LPM:{1}\x03'.format(self._DeviceID,self.LampSelectStateValues[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)
    def UpdateLampSelect(self, value, qualifier):

        LampSelectCmdString = '\x02AD{0};QSL\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try: 
                matchObject = re.search(self.matchString, res)
                if matchObject:
                    value = matchObject.group(1)
                    self.WriteStatus('LampSelect', self.LampSelectStateNames[value], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampSelect')

    def UpdateLampStatus(self, value, qualifier):


        LampStatusCmdString = '\x02AD{0};QLS\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = self.LampStatusStateNames[res[1:-1]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampStatus')

    def UpdateLampUsage(self, value, qualifier): 

        
        LampNumber = qualifier['LampNumber']
        if self.LampNumberConstraints['Min'] <= int(LampNumber) <= self.LampNumberConstraints['Max']:
            matchString = '\x02([0-9]{4})\x03'
            LampUsageCmdString = '\x02AD{0};Q$L:{1}\x03'.format(self._DeviceID, LampNumber)
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    matchObject = re.search(matchString, res)
                    if matchObject:
                        value = int(matchObject.group(1))
                        self.WriteStatus('LampUsage', value, {'LampNumber': LampNumber })
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateLampUsage')
        else:
            print('Invalid Command for UpdateLampUsage')        

    def SetLensMemoryDelete(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 3
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            LensMemoryDeleteCmdString = '\x02AD{0};VXX:LNMI3=+{1:05}\x03'.format(self._DeviceID, int(value)-1)
            self.__SetHelper('LensMemoryDelete', LensMemoryDeleteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLensMemoryDelete')

    def SetLensMemoryLoad(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 3
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            LensMemoryLoadCmdString = '\x02AD{0};VXX:LNMI1=+{1:05}\x03'.format(self._DeviceID, int(value)-1)
            self.__SetHelper('LensMemoryLoad', LensMemoryLoadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLensMemoryLoad')

    def SetLensMemorySave(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 3
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            LensMemorySaveCmdString = '\x02AD{0};VXX:LNMI2=+{1:05}\x03'.format(self._DeviceID, int(value)-1)
            self.__SetHelper('LensMemorySave', LensMemorySaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLensMemorySave')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu' :  'OMN',
            'Enter' : 'OEN',
            'Up' :    'OCU',
            'Down' :  'OCD',
            'Left' :  'OCL',
            'Right' : 'OCR',
            }
        MenuNavigationCmdString = '\x02AD{0};{1}\x03'.format(self._DeviceID, MenuNavigationStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        OnScreenDisplayCmdString = '\x02AD{0};OOS:{1}\x03'.format(self._DeviceID,ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        
    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        OnScreenDisplayCmdString = '\x02AD{0};QOS\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural' :   'NAT',
            'Standard' :  'STD',
            'Dynamic' :   'DYN',
            'Cinema' :    'CIN',
            'Graphic' :   'GRA',
            'Dicom Sim' : 'DIC',
            'User' :      'USR',
            }
        PictureModeCmdString = '\x02AD{0};VPM:{1}\x03'.format(self._DeviceID, PictureModeStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def UpdatePictureMode(self, value, qualifier): 

        PictureModeStateNames = {
            'NAT' : 'Natural',
            'STD' : 'Standard',
            'DYN' : 'Dynamic',
            'CIN' : 'Cinema',
            'GRA' : 'Graphic',
            'DIC' : 'Dicom Sim',
            'USR' : 'User'
           }
        matchString = '\x02(NAT|STD|DYN|CIN|GRA|DIC|USR)\x03'
        PictureModeCmdString = '\x02AD{0};QPM\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(matchString, res)
                if matchObject:
                    value = matchObject.group(1)
                    self.WriteStatus('PictureMode', PictureModeStateNames[value], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On' :  'PON',
            'Off' : 'POF',
            }
        PowerCmdString = '\x02AD{0};{1}\x03'.format(self._DeviceID, PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier): 

        PowerStateNames = {
            '1' : 'On',
            '0' : 'Off',
           }
        matchString = '\x0200(0|1)\x03'
        PowerCmdString = '\x02AD{0};QPW\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(matchString, res)
                if matchObject:
                    value = matchObject.group(1)
                    self.WriteStatus('Power', PowerStateNames[value], None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')


    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0', 
            'On' : '1'
        }

        VideoMuteCmdString = '\x02AD{0};OSH:{1}\x03'.format(self._DeviceID,ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'On'
        }

        VideoMuteCmdString = '\x02AD{0};QSH\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03').decode(encoding='iso-8859-1')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ':
            print('Inappropriate Command ', command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03').decode(encoding='iso-8859-1')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response
        if 'ER40' in res:
            if '401' in res:
                print('Commands can not currently be recieved by the device.')
            elif '402' in res:
                print('Device responded with a Parameter Error.')
            else:
                print('Device responded with an error.')
            response = ''
        return response
    

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def pana_1_407_2lamps(self):
        self.LampSelectStateValues = {
            'Dual' :   '0',
            'Single' : '1',
            'Lamp 1' : '2',
            'Lamp 2' : '3',
            }

        self.LampSelectStateNames = {
            '0': 'Dual',
            '1': 'Single',
            '2': 'Lamp 1',
            '3': 'Lamp 2'
        }

        self.LampStatusStateNames = {
            '0' : 'No lamps are on', 
            '1' : 'Lamp 1 is on', 
            '2' : 'Lamp 2 is on', 
            '3' : 'All lamps are on'
        }

        self.LampNumberConstraints = {
           'Min' : 1,
           'Max' : 2
        }

        self.matchString = '\x02(0|1|2|3)\x03'
        
    def pana_1_407_4lamps(self):
        self.LampSelectStateValues = {
            'Quad':       '00',
            'Lamp 1/4':   '01',
            'Lamp 2/3':   '02',
            'Dual':       '03',
            'Lamp 1/2/3': '04',
            'Lamp 1/2/4': '05',
            'Lamp 1/3/4': '06',
            'Lamp 2/3/4': '07',
            'Triple':     '08',
            'Lamp 1':     '09',
            'Lamp 2':     '10',
            'Lamp 3':     '11',
            'Lamp 4':     '12',
            'Single':     '13'
        }

        self.LampSelectStateNames = {
            '0' : 'Quad',
            '1' : 'Lamp 1/4',
            '2' : 'Lamp 2/3',
            '3' : 'Dual',
            '4' : 'Lamp 1/2/3',
            '5' : 'Lamp 1/2/4',
            '6' : 'Lamp 1/3/4',
            '7' : 'Lamp 2/3/4',
            '8' : 'Triple',
            '9' : 'Lamp 1',
            '10' : 'Lamp 2',
            '11' : 'Lamp 3',
            '12' : 'Lamp 4',
            '13' : 'Single'
        }

        self.LampStatusStateNames = {
            '0' : 'No lamps are on', 
            '1' : 'All lamps are on', 
            '2' : 'Lamp 1 and Lamp 4 are on', 
            '3' : 'Lamp 2 and Lamp 3 are on', 
            '4' : 'Lamp 1, 2 and 3 are on', 
            '5' : 'Lamp 1, 2 and 4 are on', 
            '6' : 'Lamp 1, 3 and 4 are on', 
            '7' : 'Lamp 2, 3 and 4 are on', 
            '8' : 'Lamp 1 is on', 
            '9' : 'Lamp 2 is on', 
            '10' : 'Lamp 3 is on', 
            '11' : 'Lamp 4 is on'
        }

        self.LampNumberConstraints = {
           'Min' : 1,
           'Max' : 4
        }

        self.matchString = '\x02(0|1|2|3|4|5|6|7|8|9|10|11|12|13)\x03'
        
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
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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

class DeviceEthernetClass:
    
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
        
        self.Models = {
            'PT-DS12K': self.pana_1_407_tcp_1213,
            'PT-DS12KE': self.pana_1_407_tcp_1213,
            'PT-DS12KU': self.pana_1_407_tcp_1213,
            'PT-DW11K': self.pana_1_407_tcp_11,
            'PT-DW11KE': self.pana_1_407_tcp_11,
            'PT-DW11KU': self.pana_1_407_tcp_11,
            'PT-DZ10K': self.pana_1_407_tcp_10,
            'PT-DZ10KE': self.pana_1_407_tcp_10,
            'PT-DZ10KU': self.pana_1_407_tcp_10,
            'PT-DZ13K': self.pana_1_407_tcp_1213,
            'PT-DZ13KE': self.pana_1_407_tcp_1213,
            'PT-DZ13KU': self.pana_1_407_tcp_1213,
         }        
        
        self.Commands = {
            'AspectRatio': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

        self.md5hash = ''
        self.Security = False
        self.deviceUsername = None
        self.devicePassword = None
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'00VSE:(0|1|2|5|6|9|10)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'00LPM:(0|1|2|3)\r'), self.__MatchLampSelect, None)
            self.AddMatchString(re.compile(b'00Q\$L([0-9]{4})([0-9]{4})\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'00OPP:(0|1|2|3)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'0000(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'00OSH:(0|1)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'ERR(1|2|3|4|5|A)\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        if self.deviceUsername is not None:
            if self.devicePassword is not None:
                rand_num = match.group(1).decode()
                full_str = ''.join([self.deviceUsername, ':', self.devicePassword, ':', rand_num])
                code_hash = hashlib.md5(full_str.encode())
                self.md5hash = hexlify(code_hash.digest())
                self.Security = True
            else:
                self.MissingCredentialsLog('Password')
        else:
            self.MissiongCredentialsLog('Username')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'    : '0', 
            '4:3'     : '1', 
            '16:9'    : '2', 
            'Through' : '5', 
            'HV Fit'  : '6', 
            'H Fit'   : '9', 
            'V Fit'   : '10'
        }

        AspectRatioCmdString =  '00VSE:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '00QSE\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : '4:3', 
            '2' : '16:9', 
            '5' : 'Through', 
            '6' : 'HV Fit', 
            '9' : 'H Fit', 
            '10' : 'V Fit'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = '00IIS:{0}\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        LampModeCmdString = '00OLP:{0}\r'.format(self.LampModeValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)


    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Dual'   : '0',
            'Single' : '1', 
            'Lamp 1' : '2', 
            'Lamp 2' : '3'
        }

        LampSelectCmdString = '00LPM:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)
        
    def UpdateLampSelect(self, value, qualifier):

        LampSelectCmdString = '00QSL\r'
        self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def __MatchLampSelect(self, match, tag):

        ValueStateValues = {
            '0' : 'Dual',
            '1' : 'Single', 
            '2' : 'Lamp 1', 
            '3' : 'Lamp 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampSelect', value, None)

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if lamp in ['1', '2']:
            LampUsageCmdString = '00Q$L\r'
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, tag):

        self.WriteStatus('LampUsage', int(match.group(1).decode()), {'Lamp' : '1'})
        self.WriteStatus('LampUsage', int(match.group(2).decode()), {'Lamp' : '2'})

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'Off'    : '0'
        }

        PIPModeCmdString = '00OPP:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        
    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '00QPP\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '1' : 'User 1', 
            '2' : 'User 2', 
            '3' : 'User 3', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PON', 
            'Off' : 'POF'
        }

        PowerCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):
        PowerCmdString = '00QPW\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            
    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0', 
            'On'  : '1'
        }

        VideoMuteCmdString = '00OSH:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '00QSH\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Security:
            self.Send(self.md5hash + commandstring.encode())
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.Security:
                self.Send(self.md5hash + commandstring.encode())
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorValue = {
            '1' : 'Undefined control command',
            '2' : 'Out of parameter range',
            '3' : 'Busy state or no-acceptable period',
            '4' : 'Timeout or no-acceptable period',
            '5' : 'Wrong data length',
            'A' : 'Password mismatch',

        }
        print(ErrorValue[match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Security = False
        
    def pana_1_407_tcp_1213(self):
        self.InputStateValues = {
            'RGB1'  : 'RG1', 
            'RGB2'  : 'RG2', 
            'Video' : 'VID', 
            'DVI-D' : 'DVI', 
            'HDMI'  : 'HD1', 
            'SDI1'  : 'SD1', 
            'SDI2'  : 'SD2'
            }
            
        self.LampModeValues = {
            'High'   : '0', 
            'Middle' : '1', 
            'Eco'    : '8'
        }
        
    def pana_1_407_tcp_11(self):
        self.InputStateValues = {
            'RGB1'  : 'RG1', 
            'RGB2'  : 'RG2', 
            'Video' : 'VID', 
            'DVI-D' : 'DVI', 
            'HDMI'  : 'HD1' 
            }
            
        self.LampModeValues = {
            'High'   : '0', 
            'Middle' : '1', 
            'Eco'    : '8'
        }
        
    def pana_1_407_tcp_10(self):
        self.InputStateValues = {
            'RGB1'  : 'RG1', 
            'RGB2'  : 'RG2', 
            'Video' : 'VID', 
            'DVI-D' : 'DVI', 
            'HDMI'  : 'HD1',
            'SDI1'  : 'SD1'
            }
            
        self.LampModeValues = {
            'Normal' : '0', 
            'Eco'    : '8'
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
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 
            
    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
