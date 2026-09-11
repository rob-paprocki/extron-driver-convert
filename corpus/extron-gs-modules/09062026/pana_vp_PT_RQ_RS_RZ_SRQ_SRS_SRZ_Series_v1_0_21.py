from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.DeviceID = '1'
        self.Models = {
            'PT-RZ12K': self.pana_1_1954_SZ,
            'PT-RS11K': self.pana_1_1954_SZ,
            'PT-RQ13K': self.pana_1_1954_RQ,
            'PT-SRZ12KC': self.pana_1_1954_SZ,
            'PT-SRS11KC': self.pana_1_1954_SZ,
            'PT-SRQ13KC': self.pana_1_1954_RQ,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'LampStatus': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPFrameLock': { 'Status': {}},
            'PIPInput': {'Parameters':['PIP Type'], 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '\x02ADZZ;'
        else:
            temp = value.zfill(2)
            self._DeviceID = '\x02AD' + temp + ';'

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)'  : '1\x03', 
            'Wide (16:9)'   : '2\x03', 
            'Native'        : '5\x03', 
            'Full (HV Fit)' : '6\x03', 
            'H-Fit'         : '9\x03', 
            'V-Fit'         : '10\x03',
            'Default'       : '0\x03' 
        }

        AspectRatioCmdString = self._DeviceID + 'VSE:' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Normal (4:3)', 
            '2' : 'Wide (16:9)', 
            '5' : 'Native', 
            '6' : 'Full (HV Fit)', 
            '9' : 'H-Fit', 
            '10' : 'V-Fit',
            '0'  : 'Default'
        }

        AspectRatioCmdString = self._DeviceID + 'QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1\x03', 
            'Off' : '0\x03'
        }

        FreezeCmdString = self._DeviceID + 'OFZ:' + ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        FreezeCmdString = self._DeviceID + 'QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = self._DeviceID + 'IIS:' + self.InputStateValues[value] + '\x03'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):


        InputCmdString = self._DeviceID + 'QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : '0', 
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9'
        }

        KeypadCmdString = self._DeviceID + 'ONK:' + ValueStateValues[value] + '\x03'
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '0' : 'All Off', 
            '1' : 'Lamp 1 On', 
            '2' : 'Lamp 2 On', 
            '3' : 'All On'
        }

        LampStatusCmdString = self._DeviceID + 'QLS\x03'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if 1 <= int(lamp) <= 2:
            LampUsageCmdString = self._DeviceID + 'Q$L:{0}\x03'.format(lamp)
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:5])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 'OMN', 
            'Enter' : 'OEN', 
            'Up'    : 'OCU', 
            'Down'  : 'OCD', 
            'Left'  : 'OCL', 
            'Right' : 'OCR'
        }

        MenuNavigationCmdString = self._DeviceID + ValueStateValues[value] + '\x03'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic'   : 'DYN', 
            'Natural'   : 'NAT', 
            'Standard'  : 'STD', 
            'Cinema'    : 'CIN', 
            'Graphic'   : 'GRA', 
            'DICOM SIM' : 'DIC', 
            'User'      : 'USR'
        }

        PictureModeCmdString = self._DeviceID + 'VPM:' + ValueStateValues[value] + '\x03'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN' : 'Dynamic', 
            'NAT' : 'Natural', 
            'STD' : 'Standard', 
            'CIN' : 'Cinema', 
            'GRA' : 'Graphic', 
            'DIC' : 'DICOM SIM', 
            'USR' : 'User'
        }

        PictureModeCmdString = self._DeviceID + 'QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            'Main Window' : '0', 
            'Sub Window'  : '1'
        }

        PIPFrameLockCmdString = self._DeviceID + 'PFL:' + ValueStateValues[value] + '\x03'
        self.__SetHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)

    def UpdatePIPFrameLock(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Main Window', 
            '1' : 'Sub Window'
        }

        PIPFrameLockCmdString = self._DeviceID + 'QPF\x03'
        res = self.__UpdateHelper('PIPFrameLock', PIPFrameLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PIPFrameLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main' : 'MSI:', 
            'Sub'  : 'SIS:'
        }
        PIPInputType = qualifier['PIP Type']
        PIPInputType = PIPTypeStates[PIPInputType]
        ValueStateValues = {
            'RGB 1' : 'RG1', 
            'RGB 2' : 'RG2', 
            'DVI'   : 'DVI', 
            'HDMI'  : 'HD1', 
            'SDI 1' : 'SD1', 
            'SDI 2' : 'SD2'
        }
        if PIPInputType:
            PIPInputCmdString = self._DeviceID + PIPInputType + ValueStateValues[value]  + '\x03'
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPTypeStates = {
            'Main' : 'QIM', 
            'Sub'  : 'QIS'
        }
        PIPInputType = qualifier['PIP Type']
        PIPInputType = PIPTypeStates[PIPInputType]
        ValueStateValues = {
            'RG1' : 'RGB 1', 
            'RG2' : 'RGB 2', 
            'DVI' : 'DVI', 
            'HD1' : 'HDMI', 
            'SD1' : 'SDI 1', 
            'SD2' : 'SDI 2'
        }
        if PIPInputType:
            PIPInputCmdString = self._DeviceID + PIPInputType + '\x03'
            res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[1:-1]]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off'    : '0', 
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3'
        }

        PIPModeCmdString = self._DeviceID + 'OPP:' + ValueStateValues[value] + '\x03'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Off', 
            '1' : 'User 1', 
            '2' : 'User 2', 
            '3' : 'User 3'
        }

        PIPModeCmdString = self._DeviceID + 'QPP\x03'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PON', 
            'Off' : 'POF'
        }

        PowerCmdString = self._DeviceID + ValueStateValues[value] + '\x03'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = self._DeviceID + 'QPW\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '0', 
            'Off' : '1'
        }

        VideoMuteCmdString = self._DeviceID + 'OSH:' + ValueStateValues[value] + '\x03'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        VideoMuteCmdString = self._DeviceID + 'QSH\x03'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = { '\x02ER401\x03': 'Invalid Command.',
                               '\x02ER402\x03': 'Invalid Parameter' }   
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command , res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '\x02ADZZ;':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            return self.__CheckResponseForErrors(command , res.decode())

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_1_1954_SZ(self):
        

        self.InputStateValues = {
            'Computer 1'   : 'RG1', 
            'Computer 2'   : 'RG2', 
            'Video'        : 'VID', 
            'S- Video'     : 'SVD', 
            'DVI'          : 'DVI', 
            'HDMI'         : 'HD1', 
            'SDI 1'        : 'SD1', 
            'SDI 2'        : 'SD2', 
            'Digital Link' : 'DL1'
        }
        self.InputStateNames = {
            'RG1' : 'Computer 1', 
            'RG2' : 'Computer 2', 
            'VID' : 'Video', 
            'SVD' : 'S- Video', 
            'DVI' : 'DVI', 
            'HD1' : 'HDMI', 
            'SD1' : 'SDI 1', 
            'SD2' : 'SDI 2', 
            'DL1' : 'Digital Link'
        }

    def pana_1_1954_RQ(self):
    
        

        self.InputStateValues = {
            'SDI 1'                   : 'SD1', 
            'SDI 2'                   : 'SD2', 
            'SDI 3'                   : 'SD3', 
            'SDI 4'                   : 'SD4', 
            'Digital Link'            : 'DL1', 
            'Digital Link Computer 1' : 'DL1:PC1', 
            'Digital Link Computer 2' : 'DL1:PC2', 
            'Digital Link Video'      : 'DL1:VID', 
            'Digital Link HDMI 1'     : 'DL1:HD1', 
            'Digital Link HDMI 2'     : 'DL1:HD2', 
            'Digital Link S-Video'    : 'DL1:SVD'
        }
        self.InputStateNames = {
            'SD1' : 'SDI 1', 
            'SD2' : 'SDI 2', 
            'SD3' : 'SDI 3', 
            'SD4' : 'SDI 4', 
            'DL1' : 'Digital Link', 
            'DL1:PC1' : 'Digital Link Computer 1', 
            'DL1:PC2' : 'Digital Link Computer 2', 
            'DL1:VID' : 'Digital Link Video', 
            'DL1:HD1' : 'Digital Link HDMI 1', 
            'DL1:HD2' : 'Digital Link HDMI 2', 
            'DL1:SVD' : 'Digital Link S-Video'
        }            ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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


class DeviceEthernetClass:
    def __init__(self):

        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        self.Models = {
            'PT-RQ13K': self.pana_1_1954_RQ,
            'PT-RS11K': self.pana_1_1954_SZ,
            'PT-RZ12K': self.pana_1_1954_SZ,
            'PT-SRQ13KC': self.pana_1_1954_RQ,
            'PT-SRS11KC': self.pana_1_1954_SZ,
            'PT-SRZ12KC': self.pana_1_1954_SZ,
            }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }
        self.md5hash = ''
        self.Security = False

        self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
        self.AddMatchString(re.compile(b'ERR([1-5A])\r'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)'  : '1', 
            'Wide (16:9)'   : '2', 
            'Native'        : '5', 
            'Full (HV Fit)' : '6', 
            'H-Fit'         : '9', 
            'V-Fit'         : '10', 
            'Default'       : '0'
        }

        AspectRatioCmdString = '00VSE:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

      
        InputCmdString = '00IIS:{0}\r'.format(self.InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'PON', 
            'Off' : 'POF'
        }

        PowerCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        VideoMuteCmdString = '00OSH:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Security is True:
            if command == 'UserDefinedCommand':
                self.Send(self.md5hash + commandstring)
            else:
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
        value = match.group(1).decode()
        self.Error([ErrorValue[value]])
    
    def pana_1_1954_SZ(self):
        

        self.InputStateValues = {
            'Computer 1'   : 'RG1', 
            'Computer 2'   : 'RG2', 
            'DVI'          : 'DVI', 
            'HDMI'         : 'HD1', 
            'SDI 1'        : 'SD1', 
            'SDI 2'        : 'SD2', 
            'Digital Link' : 'DL1'
        }
      
    def pana_1_1954_RQ(self):
    
        

        self.InputStateValues = {
            'SDI 1'                   : 'SD1', 
            'SDI 2'                   : 'SD2', 
            'SDI 3'                   : 'SD3', 
            'SDI 4'                   : 'SD4', 
            'Digital Link'            : 'DL1', 
            'SDI 1 (Slot 1)'          : 'AU1,SD1', 
            'SDI 2 (Slot 1)'          : 'AU1,SD2', 
            'SDI 3 (Slot 2)'          : 'AU2,SD3', 
            'SDI 4 (Slot 2)'          : 'AU2,SD4', 
            'HDMI 1 (Slot 1)'         : 'AU1,HD1', 
            'HDMI 2 (Slot 1)'         : 'AU1,HD2', 
            'HDMI 3 (Slot 2)'         : 'AU2,HD3', 
            'HDMI 4 (Slot 2)'         : 'AU2,HD4', 
            'DVI-D1 (Slot 1)'         : 'AU1,DV1', 
            'DVI-D2 (Slot 1)'         : 'AU1,DV2', 
            'DVI-D3 (Slot 2)'         : 'AU2,DV3', 
            'DVI-D4 (Slot 2)'         : 'AU2,DV4'
        }
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