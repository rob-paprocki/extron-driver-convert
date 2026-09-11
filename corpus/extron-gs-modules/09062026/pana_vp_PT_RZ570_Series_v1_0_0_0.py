from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import time
import re
import hashlib
from binascii import hexlify


class DeviceSeriakClass():

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
        self.deviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationMode': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def SetDisplayID(DisplayID):    
        if DisplayID == 'Broadcast':
            self.DeviceID = '\x02ADZZ;'
        else:
            self.DeviceID = '\x02AD' + DisplayID.zfill(2) + ';'            

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Auto': '0',
            'Normal (4:3)': '1',
            'Wide (16:9)': '2',
            'Native (Through)': '5',
            'Full (HV Fit)': '6',
            'H-Fit': '9',
            'V-Fit': '10'
        }

        AspectRatioCmdString = '{0}VSE:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '0': 'Auto',
            '1': 'Normal (4:3)',
            '2': 'Wide (16:9)',
            '5': 'Native (Through)',
            '6': 'Full (HV Fit)',
            '9': 'H-Fit',
            '10': 'V-Fit'
        }

        AspectRatioCmdString = '{0}QSE\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = '{0}OAS\x03'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetClosedCaption(self, value, qualifier):
        ValueStateValues = {
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4',
            'Off': '0'
        }

        ClosedCaptionCmdString = '{0}OCC:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        ValueStateValues = {
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
            '0': 'Off'
        }

        ClosedCaptionCmdString = '{0}QCC\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')

    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '{0}OFZ:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '{0}QFZ\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'Video': 'VID',
            'DVI': 'DVI',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2',
            'Digital Link': 'DL1',
            'Digital Link Computer 1': 'DL1:PC1',
            'Digital Link Computer 2': 'DL1:PC2',
            'Digital Link Video': 'DL1:VID',
            'Digital Link HDMI 1': 'DL1:HD1',
            'Digital Link HDMI 2': 'DL1:HD2'
        }

        InputCmdString = '{0}IIS:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        ValueStateValues = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'DVI': 'DVI',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'DL1': 'Digital Link',
            'DL1:PC1': 'Digital Link Computer 1',
            'DL1:PC2': 'Digital Link Computer 2',
            'DL1:VID': 'Digital Link Video',
            'DL1:HD1': 'Digital Link HDMI 1',
            'DL1:HD2': 'Digital Link HDMI 2'
        }

        InputCmdString = '{0}QIN\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = '{0}Q$L:1\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Menu': 'OMN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
            'Enter': 'OEN',
            'Return': 'OBK'
        }

        MenuNavigationCmdString = '{0}{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = '{0}OOS:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = '{0}QOS\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetOperationMode(self, value, qualifier):
        ValueStateValues = {
            'Normal': '000',
            'Eco': '001',
            'Silent': '002',
            'User': '101'
        }

        OperationModeCmdString = '{0}VXX:OPEI1=+00{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('OperationMode', OperationModeCmdString, value, qualifier)

    def UpdateOperationMode(self, value, qualifier):
        ValueStateValues = {
            '000': 'Normal',
            '001': 'Eco',
            '002': 'Silent',
            '101': 'User'
        }

        OperationModeCmdString = '{0}QVX:OPEI1\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('OperationMode', OperationModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10:-1]]
                self.WriteStatus('OperationMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOperationMode')

    def SetPictureMode(self, value, qualifier):
        ValueStateValues = {
            'Dynamic': 'DYN',
            'Natural': 'NAT',
            'Standard': 'STD',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM SIM': 'DIC',
            'REC709': '709'
        }

        PictureModeCmdString = '{0}VPM:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'DICOM SIM',
            '709': 'REC709'
        }

        PictureModeCmdString = '{0}QPM\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPIPMode(self, value, qualifier):
        ValueStateValues = {
            'Off': '0',
            'User 1': '1',
            'User 2': '2',
            'User 3': '3'
        }

        PIPModeCmdString = '{0}OPP:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):
        ValueStateValues = {
            '0': 'Off',
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3'
        }

        PIPModeCmdString = '{0}QPP\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = '{0}{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 10)

    def UpdatePower(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '{0}QPW\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetShutter(self, value, qualifier):
        ValueStateValues = {
            'Open': '0',
            'Close': '1'
        }

        ShutterCmdString = '{0}OSH:{1}\x03'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):
        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        ShutterCmdString = '{0}QSH\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateShutter')

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 63
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}AVL:{1}\x03'.format(self.DeviceID, str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = '{0}QAV\x03'.format(self.DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {'\x02ER401\x03': 'Invalid Command.',
                               '\x02ER402\x03': 'Invalid Parameter'}
        if response in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True' or self.DeviceID == '\x02ADZZ;':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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
                result = search(regexString, self._ReceiveBuffer)                
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

class DeviceEthernetClass():

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
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationMode': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'Volume': {'Status': {}}
            }

        self.md5hash = ''
        self.Security = False

        if self.Unidirectional == 'False':
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
            'Auto': '0',
            'Normal (4:3)': '1',
            'Wide (16:9)': '2',
            'Native (Through)': '5',
            'Full (HV Fit)': '6',
            'H-Fit': '9',
            'V-Fit': '10'
        }

        AspectRatioCmdString = '00VSE:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '0': 'Auto',
            '1': 'Normal (4:3)',
            '2': 'Wide (16:9)',
            '5': 'Native (Through)',
            '6': 'Full (HV Fit)',
            '9': 'H-Fit',
            '10': 'V-Fit'
        }

        AspectRatioCmdString = '00QSE\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = '00OAS\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetClosedCaption(self, value, qualifier):
        ValueStateValues = {
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4',
            'Off': '0'
        }

        ClosedCaptionCmdString = '00OCC:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):
        ValueStateValues = {
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
            '0': 'Off'
        }

        ClosedCaptionCmdString = '00QCC\r'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaption')

    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '00OFZ:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '00QFZ\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'Computer 1': 'RG1',
            'Computer 2': 'RG2',
            'Video': 'VID',
            'DVI': 'DVI',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2',
            'Digital Link': 'DL1',
            'Digital Link Computer 1': 'DL1:PC1',
            'Digital Link Computer 2': 'DL1:PC2',
            'Digital Link Video': 'DL1:VID',
            'Digital Link HDMI 1': 'DL1:HD1',
            'Digital Link HDMI 2': 'DL1:HD2'
        }

        InputCmdString = '00IIS:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        ValueStateValues = {
            'RG1': 'Computer 1',
            'RG2': 'Computer 2',
            'VID': 'Video',
            'DVI': 'DVI',
            'HD1': 'HDMI 1',
            'HD2': 'HDMI 2',
            'DL1': 'Digital Link',
            'DL1:PC1': 'Digital Link Computer 1',
            'DL1:PC2': 'Digital Link Computer 2',
            'DL1:VID': 'Digital Link Video',
            'DL1:HD1': 'Digital Link HDMI 1',
            'DL1:HD2': 'Digital Link HDMI 2'
        }

        InputCmdString = '00QIN\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = '00Q$L:1\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Menu': 'OMN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR',
            'Enter': 'OEN',
            'Return': 'OBK'
        }

        MenuNavigationCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)

    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = '00OOS:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = '00QOS\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetOperationMode(self, value, qualifier):
        ValueStateValues = {
            'Normal': '000',
            'Eco': '001',
            'Silent': '002',
            'User': '101'
        }

        OperationModeCmdString = '00VXX:OPEI1=+00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('OperationMode', OperationModeCmdString, value, qualifier)

    def UpdateOperationMode(self, value, qualifier):
        ValueStateValues = {
            '000': 'Normal',
            '001': 'Eco',
            '002': 'Silent',
            '101': 'User'
        }

        OperationModeCmdString = '00QVX:OPEI1\r'
        res = self.__UpdateHelper('OperationMode', OperationModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[11:-1]]
                self.WriteStatus('OperationMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOperationMode')

    def SetPictureMode(self, value, qualifier):
        ValueStateValues = {
            'Dynamic': 'DYN',
            'Natural': 'NAT',
            'Standard': 'STD',
            'Cinema': 'CIN',
            'Graphic': 'GRA',
            'DICOM SIM': 'DIC',
            'REC709': '709'
        }

        PictureModeCmdString = '00VPM:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        ValueStateValues = {
            'DYN': 'Dynamic',
            'NAT': 'Natural',
            'STD': 'Standard',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'DICOM SIM',
            '709': 'REC709'
        }

        PictureModeCmdString = '00QPM\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPIPMode(self, value, qualifier):
        ValueStateValues = {
            'Off': '0',
            'User 1': '1',
            'User 2': '2',
            'User 3': '3'
        }

        PIPModeCmdString = '00OPP:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):
        ValueStateValues = {
            '0': 'Off',
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3'
        }

        PIPModeCmdString = '00QPP\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = '00{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 10)

    def UpdatePower(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '00QPW\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetShutter(self, value, qualifier):
        ValueStateValues = {
            'Open': '0',
            'Close': '1'
        }

        ShutterCmdString = '00OSH:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):
        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        ShutterCmdString = '00QSH\r'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateShutter')

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 63
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '00AVL:{0}\r'.format(str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = '00QAV\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {'00ER401\r': 'Invalid Command.',
                               '00ER402\r': 'Invalid Parameter'}
        if response in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Security:
            if command == 'UserDefinedCommand':
                commandstring = self.md5hash + commandstring
            else:
                commandstring = self.md5hash + commandstring.encode()

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.Security:
                commandstring = self.md5hash + commandstring.encode()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def __MatchError(self, match, tag):
        ErrorValue = {
            '1': 'Undefined control command',
            '2': 'Out of parameter range',
            '3': 'Busy state or no-acceptable period',
            '4': 'Timeout or no-acceptable period',
            '5': 'Wrong data length',
            'A': 'Password mismatch',

        }
        value = match.group(1).decode()
        print(ErrorValue[value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Security = False


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
