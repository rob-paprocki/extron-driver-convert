from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
import binascii

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
        self._DeviceID = '01'
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {
            'PT-RW630B': self.pana_1_889_RW,
            'PT-RZ670B': self.pana_1_889_RZ,
            'PT-RW630W': self.pana_1_889_RW,
            'PT-RW630LB': self.pana_1_889_RW,
            'PT-RW630LW': self.pana_1_889_RW,
            'PT-RZ670W': self.pana_1_889_RZ,
            'PT-RZ670LB': self.pana_1_889_RZ,
            'PT-RZ670LW': self.pana_1_889_RZ,
            'PT-RZ670WU': self.pana_1_889_RZ,
            'PT-RZ970BU': self.pana_1_889_RZ,
            'PT-RZ670BU': self.pana_1_889_RZ,
            }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampHours': {'Parameters':['Lamp Number'], 'Status': {}},
            'LampStatus': { 'Status': {}},
            'LensShiftHorizontal': {'Parameters':['Speed'], 'Status': {}},
            'LensShiftVertical': {'Parameters':['Speed'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureinPicture': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Temperature': {'Parameters':['Location'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

        self.md5hash = ''
        self.Security = False


        self.DeviceIDMatch = {
        'Broadcast' : 'ZZ',
        '01'        : '01',
        '02'        : '02',
        '03'        : '03',
        '04'        : '04',
        '05'        : '05',
        '06'        : '06',
        '07'        : '07',
        '08'        : '08',
        '09'        : '09',
        '10'        : '10',
        '11'        : '11',
        '12'        : '12',
        '13'        : '13',
        '14'        : '14',
        '15'        : '15',
        '16'        : '16',
        '17'        : '17',
        '18'        : '18',
        '19'        : '19',
        '20'        : '20',
        '21'        : '21',
        '22'        : '22',
        '23'        : '23',
        '24'        : '24',
        '25'        : '25',
        '26'        : '26',
        '27'        : '27',
        '28'        : '28',
        '29'        : '29',
        '30'        : '30',
        '31'        : '31',
        '32'        : '32',
        '33'        : '33',
        '34'        : '34',
        '35'        : '35',
        '36'        : '36',
        '37'        : '37',
        '38'        : '38',
        '39'        : '39',
        '40'        : '40',
        '41'        : '41',
        '42'        : '42',
        '43'        : '43',
        '44'        : '44',
        '45'        : '45',
        '46'        : '46',
        '47'        : '47',
        '48'        : '48',
        '49'        : '49',
        '50'        : '50',
        '51'        : '51',
        '52'        : '52',
        '53'        : '53',
        '54'        : '54',
        '55'        : '55',
        '56'        : '56',
        '57'        : '57',
        '58'        : '58',
        '59'        : '59',
        '60'        : '60',
        '61'        : '61',
        '62'        : '62',
        '63'        : '63',
        '64'        : '64',
        'Group A'   : '0A',
        'Group B'   : '0B',
        'Group C'   : '0C',
        'Group D'   : '0D',
        'Group E'   : '0E',
        'Group F'   : '0F',
        'Group G'   : '0G',
        'Group H'   : '0H',
        'Group I'   : '0I',
        'Group J'   : '0J',
        'Group K'   : '0K',
        'Group L'   : '0L',
        'Group M'   : '0M',
        'Group N'   : '0N',
        'Group O'   : '0O',
        'Group P'   : '0P',
        'Group Q'   : '0Q',
        'Group R'   : '0R',
        'Group S'   : '0S',
        'Group T'   : '0T',
        'Group U'   : '0U',
        'Group V'   : '0V',
        'Group W'   : '0W',
        'Group X'   : '0X',
        'Group Y'   : '0Y',
        'Group Z'   : '0Z',
        }

        self.LensDeviceIDMatch = {
        'Broadcast' : '00',
        '01'        : '01',
        '02'        : '02',
        '03'        : '03',
        '04'        : '04',
        '05'        : '05',
        '06'        : '06',
        '07'        : '07',
        '08'        : '08',
        '09'        : '09',
        '10'        : '0A',
        '11'        : '0B',
        '12'        : '0C',
        '13'        : '0D',
        '14'        : '0E',
        '15'        : '0F',
        '16'        : '10',
        '17'        : '11',
        '18'        : '12',
        '19'        : '13',
        '20'        : '14',
        '21'        : '15',
        '22'        : '16',
        '23'        : '17',
        '24'        : '18',
        '25'        : '19',
        '26'        : '1A',
        '27'        : '1B',
        '28'        : '1C',
        '29'        : '1D',
        '30'        : '1E',
        '31'        : '1F',
        '32'        : '20',
        '33'        : '21',
        '34'        : '22',
        '35'        : '23',
        '36'        : '24',
        '37'        : '25',
        '38'        : '26',
        '39'        : '27',
        '40'        : '28',
        '41'        : '29',
        '42'        : '2A',
        '43'        : '2B',
        '44'        : '2C',
        '45'        : '2D',
        '46'        : '2E',
        '47'        : '2F',
        '48'        : '30',
        '49'        : '31',
        '50'        : '32',
        '51'        : '33',
        '52'        : '34',
        '53'        : '35',
        '54'        : '36',
        '55'        : '37',
        '56'        : '38',
        '57'        : '39',
        '58'        : '3A',
        '59'        : '3B',
        '60'        : '3C',
        '61'        : '3D',
        '62'        : '3E',
        '63'        : '3F',
        '64'        : '40',
        'Group A'   : '80',
        'Group B'   : '81',
        'Group C'   : '82',
        'Group D'   : '83',
        'Group E'   : '84',
        'Group F'   : '85',
        'Group G'   : '86',
        'Group H'   : '87',
        'Group I'   : '88',
        'Group J'   : '89',
        'Group K'   : '8A',
        'Group L'   : '8B',
        'Group M'   : '8C',
        'Group N'   : '8D',
        'Group O'   : '8E',
        'Group P'   : '8F',
        'Group Q'   : '90',
        'Group R'   : '91',
        'Group S'   : '92',
        'Group T'   : '93',
        'Group U'   : '94',
        'Group V'   : '95',
        'Group W'   : '96',
        'Group X'   : '97',
        'Group Y'   : '98',
        'Group Z'   : '99',
        }
        self.StatusUnavailable = [b'ADZZ', b'AD0A', b'AD0B', b'AD0C', b'AD0D', b'AD0E', b'AD0F', b'AD0G', b'AD0H', b'AD0I',
                                  b'AD0J', b'AD0K', b'AD0L', b'AD0M', b'AD0N', b'AD0O', b'AD0P', b'AD0Q', b'AD0R', b'AD0S',
                                  b'AD0T', b'AD0U', b'AD0V', b'AD0W', b'AD0X', b'AD0Y', b'AD0Z', b'AD00', b'AD80', b'AD81',
                                  b'AD82', b'AD83', b'AD84', b'AD85', b'AD86', b'AD87', b'AD88', b'AD89', b'AD8A', b'AD8B', 
                                  b'AD8C', b'AD8D', b'AD8E', b'AD8F', b'AD90', b'AD91', b'AD92', b'AD93', b'AD94', b'AD95',
                                  b'AD96', b'AD97', b'AD98', b'AD99']  
                                  
        if 'Serial' not in self.ConnectionType:
            self.tag = b'\x0D'
            self.index = 2
            self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'NTCONTROL 0\r'), self.__MatchNoAuthentication, None)
        else:
            self.tag = b'\x03'
            self.index = 1

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):           
        self._DeviceID = value

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = ''.join([self.deviceUsername, ':', self.devicePassword, ':', rand_num])
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = binascii.hexlify(code_hash.digest())
        self.Security = True

    def __MatchNoAuthentication(self, match, tag):
        self.Security = False

    def CommandStringBuild(self, command, commandstring):
        if command in ['Focus', 'LensShiftHorizontal', 'LensShiftVertical', 'Zoom']: 
            IDTemp = b''.join([b'AD', self.DeviceIDMatch[self._DeviceID.zfill(2)].encode()])
        else:
            IDTemp = b''.join([b'AD', self.LensDeviceIDMatch[self._DeviceID.zfill(2)].encode()])    
        if 'Serial' not in self.ConnectionType:
            if self.Security:
                commandstring = b''.join([self.md5hash, b'00', IDTemp, b';', commandstring, b'\x0D'])
            else:
                commandstring = b''.join([b'00', IDTemp, b';', commandstring, b'\x0D'])
        else:
            commandstring = b''.join([b'\x02', IDTemp, b';', commandstring, b'\x03'])
        return commandstring
 
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

        AspectRatioCmdString = b''.join([b'VSE:', ValueStateValues[value].encode()])        
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0'  : 'Auto',
            '1'  : '4:3',
            '2'  : '16:9',
            '5'  : 'Through',
            '6'  : 'HV Fit',
            '9'  : 'H Fit',
            '10' : 'V Fit'
        }

        AspectRatioCmdString = b'QSE'        
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Aspect ratio has invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'OAS'    
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off'  : '0',
            'CC 1' : '1',
            'CC 2' : '2',
            'CC 3' : '3',
            'CC 4' : '4'
        }

        ClosedCaptionCmdString = b''.join([b'OCC:', ValueStateValues[value].encode()])        
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'CC 1', 
            '2' : 'CC 2', 
            '3' : 'CC 3', 
            '4' : 'CC 4'
        }

        ClosedCaptionCmdString = b'QCC'            
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Closed Caption has invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedStates = {
            'Slow'   : b'\x00',
            'Normal' : b'\x01',
            'Fast'   : b'\x02'
        }

        ValueStateValues = {
            'Forward'  : b'\x00',
            'Backward' : b'\x01'
        }

        FocusCmdString = b''.join([b'\xB1\x7C\x02', SpeedStates[qualifier['Speed']], ValueStateValues[value]])    
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        FreezeCmdString = b''.join([b'OFZ:', ValueStateValues[value].encode()])      
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        FreezeCmdString = b'QFZ'         
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Freeze has invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = b''.join([b'IIS:', self.SetInputValues[value].encode()])      
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'QIN'       
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInputValues[res[self.index:-1].decode()]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Input has invalid/unexpected response'])

    def UpdateLampHours(self, value, qualifier):

        if qualifier['Lamp Number'] in ['1','2']:
            LampHoursCmdString = 'Q$L:{0}'.format(qualifier['Lamp Number']).encode()
            res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[self.index:-1])
                    self.WriteStatus('LampHours', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Update Lamp Hours has invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampHours')

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '3' : 'Both On', 
            '0' : 'Both Off', 
            '1' : 'Only Lamp 1 On', 
            '2' : 'Only Lamp 2 On'
        }

        LampStatusCmdString = b'QLS'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Lamp Status has invalid/unexpected response'])

    def SetLensShiftHorizontal(self, value, qualifier):

        SpeedStates = {
            'Slow'   : b'\x00',
            'Normal' : b'\x01',
            'Fast'   : b'\x02',
            'Home'   : b'\x80'
        }

        ValueStateValues = {
            'Right'   : b'\x00',
            'Left'    : b'\x01'
        }

        LensShiftHorizontalCmdString = b''.join([b'\xB1\x7C\x00', SpeedStates[qualifier['Speed']], ValueStateValues[value]])        
        self.__SetHelper('LensShiftHorizontal', LensShiftHorizontalCmdString, value, qualifier)
    def SetLensShiftVertical(self, value, qualifier):

        SpeedStates = {
            'Slow'   : b'\x00',
            'Normal' : b'\x01',
            'Fast'   : b'\x02',
            'Home'   : b'\x80'
        }

        ValueStateValues = {
            'Up'   : b'\x00',
            'Down' : b'\x01'
        }

        LensShiftVerticalCmdString = b''.join([b'\xB1\x7C\x01', SpeedStates[qualifier['Speed']], ValueStateValues[value]])      
        self.__SetHelper('LensShiftVertical', LensShiftVerticalCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 'OMN',
            'Up'    : 'OCU',
            'Down'  : 'OCD',
            'Left'  : 'OCL',
            'Right' : 'OCR',
            'Enter' : 'OEN'
        }

        MenuNavigationCmdString = ValueStateValues[value].encode()     
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        OnScreenDisplayCmdString = b''.join([b'OOS:', ValueStateValues[value].encode()])         
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        OnScreenDisplayCmdString = b'QOS'        
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update On Screen Display has invalid/unexpected response'])

    def SetPictureinPicture(self, value, qualifier):

        ValueStateValues = {
            'Off'    : '0',
            'User 1' : '1',
            'User 2' : '2',
            'User 3' : '3'
        }

        PictureinPictureCmdString = b''.join([b'OPP:', ValueStateValues[value].encode()])       
        self.__SetHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)

    def UpdatePictureinPicture(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'User 1', 
            '2' : 'User 2', 
            '3' : 'User 3'
        }

        PictureinPictureCmdString = b'QPP'       
        res = self.__UpdateHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('PictureinPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Picture in Picure has invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Natural'    : 'NAT',
            'Standard'   : 'STD',
            'Dynamic'    : 'DYN',
            'Cinema'     : 'CIN',
            'Graphic'    : 'GRA',
            'DICOM SIM.' : 'DIC',
            'User'       : 'USR',
            'REC 709'    : '709'
        }

        PictureModeCmdString = b''.join([b'VPM:', ValueStateValues[value].encode()])        
        if value != 'User':
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier, 3.2)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'NAT' : 'Natural', 
            'STD' : 'Standard', 
            'DYN' : 'Dynamic', 
            'CIN' : 'Cinema', 
            'GRA' : 'Graphic', 
            'DIC' : 'DICOM SIM.',
            '709' : 'REC 709'
        }

        PictureModeCmdString = b'QPM'        
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Picture Mode has invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PON',
            'Off' : 'POF'
        }

        PowerCmdString = ValueStateValues[value].encode()       
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2' : 'On', 
            '0' : 'Off',
            '3' : 'Cooling Down',
            '1' : 'Warming Up'
        }

        PowerCmdString = b'Q$S'     
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Power has invalid/unexpected response'])

    def UpdateTemperature(self, value, qualifier):

        LocationStates = {
            'Intake Air'    : '0', 
            'Around Lamp'   : '1', 
            'Optics Module' : '2',
            'LD 1'          : '11',
            'LD 2'          : '12'
        }

        TemperatureCmdString = b''.join([b'QTM:', LocationStates[qualifier['Location']].encode()])       
        res = self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        if res:
            try:
                valuex = res[self.index:-1].decode().split('/')
                value = '{0} Degrees Fahrenheit'.format(int(valuex[1]))
                self.WriteStatus('Temperature', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Update Temperature has invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        VideoMuteCmdString = b''.join([b'OSH:', ValueStateValues[value].encode()])      
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        VideoMuteCmdString = b'QSH'      
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[self.index:-1].decode()]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Video Mute has invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        SpeedStates = {
            'Slow'   : b'\x00',
            'Normal' : b'\x01',
            'Fast'   : b'\x02'
        }

        ValueStateValues = {
            'In'  : b'\x00',
            'Out' : b'\x01'
        }

        ZoomCmdString = b''.join([b'\xB1\x7C\x03', SpeedStates[qualifier['Speed']], ValueStateValues[value]])       
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Serial' not in self.ConnectionType:
            DEVICE_ERROR_CODES = {
                b'00ERR1\x0D': 'Undefined Control Command.',
                b'00ERR2\x0D': 'Out of Parameter Range.',
                b'00ERR3\x0D': 'Busy State or No-acceptable Period.',
                b'00ERR4\x0D': 'Timeout or No-acceptable Period.',
                b'00ERR5\x0D': 'Wrong Data Length.',
                b'00ERRA\x0D': 'Password Mismatch.',
            }
        else:
            DEVICE_ERROR_CODES = {
                b'\x02ER402\x03' : 'Inappropriate Command.',
                b'\x02ER401\x03' : 'Invalid Command Reply.'
            }

        if response in DEVICE_ERROR_CODES.keys():
            self.Error(['{0} ERROR: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier,resptime=0.3):
        self.Debug = True
        commandstring = self.CommandStringBuild(command, commandstring)
        if self.Unidirectional == 'True' or self.DeviceID in self.StatusUnavailable:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, resptime, deliTag=self.tag)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = self.CommandStringBuild(command, commandstring)
        if self.Unidirectional == 'True' or self.DeviceID in self.StatusUnavailable:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=self.tag)
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

        if 'Serial' not in self.ConnectionType:
            self.md5hash = ''
            self.Security = False

    def pana_1_889_RZ(self):

        self.SetInputValues = {
            'RGB 1'        : 'RG1',
            'RGB 2'        : 'RG2',
            'Digital Link' : 'DL1',
            'DVI'          : 'DVI',
            'HDMI'         : 'HD1',
            'SDI'          : 'SD1'
        }

        self.UpdateInputValues = {
            'RG1' : 'RGB 1',        
            'RG2' : 'RGB 2',        
            'DL1' : 'Digital Link',
            'DVI' : 'DVI',         
            'HD1' : 'HDMI',        
            'SD1' : 'SDI'         
        }

    def pana_1_889_RW(self):

        self.SetInputValues = {
            'RGB 1'        : 'RG1',
            'RGB 2'        : 'RG2',
            'Digital Link' : 'DL1',
            'DVI'          : 'DVI',
            'HDMI'         : 'HD1'
        }

        self.UpdateInputValues = {
            'RG1' : 'RGB 1',        
            'RG2' : 'RGB 2',        
            'DL1' : 'Digital Link',
            'DVI' : 'DVI',         
            'HD1' : 'HDMI'    
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
        
        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

