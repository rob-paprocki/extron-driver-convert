from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:
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
            'PT-DZ780': self.pana_1_1421_780,
            'PT-DW750': self.pana_1_1421_D,
            'PT-DX820': self.pana_1_1421_D,
            }
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'Zoom': {'Status': {}},
            }
        self._DeviceId = '01'
        self.tempID = '1'

    @property
    def DeviceId(self):
        return self._DeviceId

    @DeviceId.setter
    def DeviceId(self, value):
        try:
            self.tempID = value
            if self.tempID == 'ALL':
                self._DeviceId = 'ZZ'
            elif 'A' <= self.tempID <= 'Z':
                self._DeviceId = self.tempID.zfill(2)
            elif 0 < int(self.tempID) < 65:
                self._DeviceId = self.tempID.zfill(2)
            else:
                self.Discard('Driver level parameter DeviceId set to an invalid value: {}'.format(value))
        except KeyError:
            self.Discard('Missing DeviceId Parameter.')
        except TypeError:
            self.Discard('DeviceId Parameter is the wrong type.')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto/Default': b';VSE:0',
            '4:3': b';VSE:1',
            '16:9': b';VSE:2',
            'Through': b';VSE:5',
            'HV Fit': b';VSE:6',
            'H Fit': b';VSE:9',
            'V Fit': b';VSE:10'
        }

        AspectRatioCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'0\x03': 'Auto/Default',
            b'1\x03': '4:3',
            b'2\x03': '16:9',
            b'5\x03': 'Through',
            b'6\x03': 'HV Fit',
            b'9\x03': 'H Fit',
            b'10': 'V Fit'
        }

        AspectRatioCmdString = b'\x02AD' + self._DeviceId.encode() + b';QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for AspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02AD' + self._DeviceId.encode() + b';OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
           'In': b'\x00',
            'Out': b'\x01'
        }
        tempDeviceId = None
        if(self.tempID == 'ALL'):
            tempDeviceId = b'\x00'
        elif('A' <= self.tempID <= 'Z'):
            tempDeviceId = pack('>B', self.tempID.encode()[0] + 63)
        elif(0 < int(self.tempID) < 65):
            tempDeviceId = pack('>B', int(self.tempID))

        FocusCmdString = b'\x02' + tempDeviceId + b'\xB1\x7C\x02\x01' + ValueStateValues[value] + b'\x03'
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b';OFZ:1',
            'Off': b';OFZ:0'
        }

        FreezeCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        FreezeCmdString = b'\x02AD' + self._DeviceId.encode() + b';QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for Freeze')

    def SetInput(self, value, qualifier):

        InputCmdString = b'\x02AD' + self._DeviceId.encode() + self.InputValues[value] + b'\x03'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x02AD' + self._DeviceId.encode() + b';QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 5:
                    value = self.ValueStateValues[res[1:4]]
                else:
                    value = self.DLValues[res[5:8]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for Input')

    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Dual': b';LPM:0',
            'Single': b';LPM:1',
            'Lamp 1': b';LPM:2',
            'Lamp 2': b';LPM:3'
        }

        LampSelectCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Dual',
            b'1': 'Single',
            b'2': 'Lamp 1',
            b'3': 'Lamp 2'
        }

        LampSelectCmdString = b'\x02AD' + self._DeviceId.encode() + b';QSL\x03'
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for LampSelect')

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if lamp in ['1', '2']:
            LampUsageCmdString = b'\x02AD' + self._DeviceId.encode() + b';Q$L:' + lamp.encode() + b'\x03'
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (KeyError, IndexError):
                    self.Discard('Invalid Response for LampUsage')
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetLensShift(self, value, qualifier):

        LensShiftStateValues = {
            'Right': b'\x00\x01\x00',
            'Left': b'\x00\x01\x01',
            'Up': b'\x01\x01\x00',
            'Down': b'\x01\x01\x01'
        }
        tempDeviceId = None
        if(self.tempID == 'ALL'):
            tempDeviceId = b'\x00'
        elif('A' <= self.tempID <= 'Z'):
            tempDeviceId = pack('>B', self.tempID.encode()[0] + 63)
        elif(0 < int(self.tempID) < 65):
            tempDeviceId = pack('>B', int(self.tempID))        

        LensShiftCmdString = b'\x02' + tempDeviceId + b'\xB1\x7C' + LensShiftStateValues[value] + b'\x03'
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b';OMN',
            'Up': b';OCU',
            'Down': b';OCD',
            'Left': b';OCL',
            'Right': b';OCR',
            'Enter': b';OEN'
        }

        MenuNavigationCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b';OOS:1',
            'Off': b';OOS:0'
        }

        OnScreenDisplayCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        OnScreenDisplayCmdString = b'\x02AD' + self._DeviceId.encode() + b';QOS\x03'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for LampUsage')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x02AD' + self._DeviceId.encode() + b';QST\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for OperationHours')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Natural': b';VPM:NAT',
            'Standard': b';VPM:STD',
            'Dynamic': b';VPM:DYN',
            'Cinema': b';VPM:CIN',
            'Graphic': b';VPM:GRA',
            'Easy DICOM': b';VPM:DIC',
            'Rec709': b';VPM:709'
        }

        PictureModeCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'NAT': 'Natural',
            b'STD': 'Standard',
            b'DYN': 'Dynamic',
            b'CIN': 'Cinema',
            b'GRA': 'Graphic',
            b'DIC': 'Easy DICOM',
            b'709': 'Rec709'
        }

        PictureModeCmdString = b'\x02AD' + self._DeviceId.encode() + b';QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:4]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for PictureMode')

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = b'\x02AD' + self._DeviceId.encode() + self.PIP[value] + b'\x03'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = b'\x02AD' + self._DeviceId.encode() + b';QIS\x03'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPValues[res[1:-1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for PIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'User 1': b';OPP:1',
            'Off': b';OPP:0',
            'User 2': b';OPP:2',
            'User 3': b';OPP:3'
        }

        PIPModeCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'1': 'User 1',
            b'0': 'Off',
            b'2': 'User 2',
            b'3': 'User 3'
        }

        PIPModeCmdString = b'\x02AD' + self._DeviceId.encode() + b';QPP\x03'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for PIPMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b';PON',
            'Off': b';POF',
        }

        PowerCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'2': 'On',
            b'0': 'Off',
            b'1': 'Warming Up',
            b'3': 'Cooling Down'
        }

        PowerCmdString = b'\x02AD' + self._DeviceId.encode() + b';Q$S\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for Power')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': b';OSH:1',
            'Off': b';OSH:0'
        }

        ShutterCmdString = b'\x02AD' + self._DeviceId.encode() + ValueStateValues[value] + b'\x03'
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        ShutterCmdString = b'\x02AD' + self._DeviceId.encode() + b';QSH\x03'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                self.Discard('Invalid Response for Shutter')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': b'\x30',
            'Out': b'\x31'
        }

        ZoomCmdString = b'\x02AD' + self._DeviceId.encode() + b';VXX:LNSI5=+0010' + ValueStateValues[value] + b'\x03'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02ER401\x03': "Invalid Command.",
            b'\x02ER402\x03': "Invalid Parameter"
            }
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self.tempID == 'ALL':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                return ''
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.tempID == 'ALL':
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

    def pana_1_1421_D(self):
        self.InputValues = {
            'RGB1'                     : b';IIS:RG1', 
            'RGB2'                     : b';IIS:RG2', 
            'Video'                    : b';IIS:VID', 
            'DVI'                      : b';IIS:DVI', 
            'HDMI'                     : b';IIS:HD1', 
            'Digital Link'             : b';IIS:DL1', 
            'Digital Link(HDMI 1)'     : b';IIS:DL1:HD1', 
            'Digital Link(HDMI 2)'     : b';IIS:DL1:HD2', 
            'Digital Link(Computer 1)' : b';IIS:DL1:PC1', 
            'Digital Link(Computer 2)' : b';IIS:DL1:PC2', 
            'Digital Link(S-Video)'    : b';IIS:DL1:SVD', 
            'Digital Link(Video)'      : b';IIS:DL1:VID'
            }
            
        self.ValueStateValues = {
            b'RG1' : 'RGB1', 
            b'RG2' : 'RGB2', 
            b'VID' : 'Video', 
            b'DVI' : 'DVI', 
            b'HD1' : 'HDMI', 
            b'DL1' : 'Digital Link', 
            }
            
        self.DLValues = {   
            b'HD1' : 'Digital Link(HDMI 1)', 
            b'HD2' : 'Digital Link(HDMI 2)', 
            b'PC1' : 'Digital Link(Computer 1)', 
            b'PC2' : 'Digital Link(Computer 2)', 
            b'SVD' : 'Digital Link(S-Video)', 
            b'VID' : 'Digital Link(Video)'
        }
        
        
        
        self.PIP = {
            'RGB1'         : b';SIS:RG1', 
            'RGB2'         : b';SIS:RG2', 
            'Digital Link' : b';SIS:DL1', 
            'DVI'          : b';SIS:DVI', 
            'HDMI'         : b';SIS:HD1'
            }
            
        self.PIPValues = {
            b'RG1' : 'RGB1', 
            b'RG2' : 'RGB2', 
            b'DL1' : 'Digital Link', 
            b'DVI' : 'DVI', 
            b'HD1' : 'HDMI'
        }
        
        
    def pana_1_1421_780(self):
        
        self.InputValues = {
            'RGB1'                     : b';IIS:RG1', 
            'RGB2'                     : b';IIS:RG2', 
            'Video'                    : b';IIS:VID', 
            'DVI'                      : b';IIS:DVI', 
            'HDMI'                     : b';IIS:HD1', 
            'SDI'                      : b';IIS:SD1', 
            'Digital Link'             : b';IIS:DL1', 
            'Digital Link(HDMI 1)'     : b';IIS:DL1:HD1', 
            'Digital Link(HDMI 2)'     : b';IIS:DL1:HD2', 
            'Digital Link(Computer 1)' : b';IIS:DL1:PC1', 
            'Digital Link(Computer 2)' : b';IIS:DL1:PC2', 
            'Digital Link(S-Video)'    : b';IIS:DL1:SVD', 
            'Digital Link(Video)'      : b';IIS:DL1:VID'
            }
            
        self.ValueStateValues = {
            b'RG1' : 'RGB1', 
            b'RG2' : 'RGB2', 
            b'VID' : 'Video', 
            b'DVI' : 'DVI', 
            b'HD1' : 'HDMI', 
            b'SD1' : 'SDI', 
            b'DL1' : 'Digital Link',
            }
            
        self.DLValues = {   
            b'HD1' : 'Digital Link(HDMI 1)', 
            b'HD2' : 'Digital Link(HDMI 2)', 
            b'PC1' : 'Digital Link(Computer 1)', 
            b'PC2' : 'Digital Link(Computer 2)', 
            b'SVD' : 'Digital Link(S-Video)', 
            b'VID' : 'Digital Link(Video)'
        }
        
        
        self.PIP = {
            'RGB1'         : b';SIS:RG1', 
            'RGB2'         : b';SIS:RG2', 
            'Digital Link' : b';SIS:DL1', 
            'SDI'          : b';SIS:SD1', 
            'DVI'          : b';SIS:DVI', 
            'HDMI'         : b';SIS:HD1'
            }
            
        self.PIPValues = {
            b'RG1' : 'RGB1', 
            b'RG2' : 'RGB2', 
            b'DL1' : 'Digital Link', 
            b'SD1' : 'SDI', 
            b'DVI' : 'DVI', 
            b'HD1' : 'HDMI'
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


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

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

