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
        self.tempID = '1'
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SideBySide': {'Status': {}},
            'VideoMute': {'Status': {}}
        }


    @property
    def DeviceID(self):
        return self._DeviceId

    @DeviceID.setter
    def DeviceID(self, value):
        self.tempID = value
        if value == 'ALL':
            self._DeviceID = 'ZZ'
        elif 'A' <= value <= 'Z':
            self._DeviceID = value.zfill(2)
        elif 0 < int(value) < 65:
            self._DeviceID = value.zfill(2)
        else:
            print("DeviceID raise is from '1' to '64', and 'A' to 'Z', and 'All'")
            self.tempID = None

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Auto': '0',
            '4:3': '1',
            '16:9': '2',
            'Through': '5',
            'HV Fit': '6',
            'H Fit': '9',
            'V Fit': '10',
            'S1 Auto': '20',
            'Video Auto': '30'
        }
        AspectRatioCmdString = b'\x02AD' + self._DeviceID.encode() + b';VSE:' + AspectRatioStateValues[value].encode() + b'\x03'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioStateNames = {
            b'0\x03': 'Auto',
            b'1\x03': '4:3',
            b'2\x03': '16:9',
            b'5\x03': 'Through',
            b'6\x03': 'HV Fit',
            b'9\x03': 'H Fit',
            b'10': 'V Fit',
            b'20': 'S1 Auto',
            b'30': 'Video Auto',
        }

        AspectRatioCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioStateNames[res[1:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02AD' + self._DeviceID.encode() + b';OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x02AD' + self._DeviceID.encode() + b';QFI:0\x03'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'In': b'\x00',
            'Out': b'\x01'
        }

        if(self.tempID == 'ALL'):
            tempDeviceId = b'\x00'
        elif('A' < self.tempID < 'Z'):
            tempDeviceId = pack('>B', self.tempID.encode()[0] + 63)
        elif(0 < int(self.tempID) < 65):
            tempDeviceId = pack('>B', int(self.tempID))

        FocusCmdString = b'\x02' + tempDeviceId + b'\xB1\x7C\x02\x01' + FocusStateValues[value] + b'\x03'
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '1',
            'Off': '0'
        }
        FreezeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OFZ:' + FreezeStateValues[value].encode() + b'\x03'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }

        FreezeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[1:2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'SDI': 'SDI',
        }
        InputCmdString = b'\x02AD' + self._DeviceID.encode() + b';IIS:' + InputStateValues[value].encode() + b'\x03'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            b'RG1': 'RGB 1',
            b'RG2': 'RGB 2',
            b'VID': 'Video',
            b'SVD': 'S-Video',
            b'DVI': 'DVI',
            b'SDI': 'SDI'
        }

        InputCmdString = b'\x02AD' + self._DeviceID.encode() + b';QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[res[1:4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'High': '0',
            'Low': '1'
        }
        LampModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';OLP:' + LampModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeStateNames = {
            b'0': 'High',
            b'1': 'Low'
        }

        LampModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QLP\x03'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[1:2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if 0 < int(lamp) < 3:
            LampUsageCmdString = b'\x02AD' + self._DeviceID.encode() + b';Q$L:' + lamp.encode() + b'\x03'
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateLampUsage')
        else:
            print('Invalid Command for UpdateLampUsage')

    def SetLampSelect(self, value, qualifier):

        LampSelectStateValues = {
            'Dual': '0',
            'Single': '1',
            'Lamp 1': '2',
            'Lamp 2': '3'
        }
        LampSelectCmdString = b'\x02AD' + self._DeviceID.encode() + b';LPM:' + LampSelectStateValues[value].encode() + b'\x03'
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        LampSelectStateNames = {
            b'0': 'Dual',
            b'1': 'Single',
            b'2': 'Lamp 1',
            b'3': 'Lamp 2'
        }
        LampSelectCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSL\x03'
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = LampSelectStateNames[res[1:2]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampSelect')

    def SetLensShift(self, value, qualifier):

        LensShiftStateValues = {
            'Right': b'\x00\x01\x00',
            'Left': b'\x00\x01\x01',
            'Up': b'\x01\x01\x00',
            'Down': b'\x01\x01\x01'
        }

        if(self.tempID == 'ALL'):
            tempDeviceId = b'\x00'
        elif('A' < self.tempID < 'Z'):
            tempDeviceId = pack('>B', self.tempID.encode()[0] + 63)
        elif(0 < int(self.tempID) < 65):
            tempDeviceId = pack('>B', int(self.tempID))

        LensShiftCmdString = b'\x02' + tempDeviceId + b'\xB1\x7C' + LensShiftStateValues[value] + b'\x03'
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Menu': b'OMN',
            'Up': b'OCU',
            'Down': b'OCD',
            'Left': b'OCL',
            'Right': b'OCR',
            'Enter': b'OEN'
        }
        MenuNavigationCmdString = b'\x02AD' + self._DeviceID.encode() + b';' + MenuNavigationStateValues[value] + b'\x03'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateValues = {
            'On': '1',
            'Off': '0'
        }
        OnScreenDisplayCmdString = b'\x02AD' + self._DeviceID.encode() + b';OOS:' + OnScreenDisplayStateValues[value].encode() + b'\x03'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }
        OnScreenDisplayCmdString = b'\x02AD' + self._DeviceID.encode() + b';QOS\x03'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = OnScreenDisplayStateNames[res[1:2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\x02AD' + self._DeviceID.encode() + b';QST\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Natural': 'NAT',
            'Standard': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CIN',
            'Graphic': 'GRA'
        }
        PictureModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';VPM:' + PictureModeStateValues[value].encode() + b'\x03'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeStateNames = {
            b'NA': 'Natural',
            b'ST': 'Standard',
            b'DY': 'Dynamic',
            b'CI': 'Cinema',
            b'GR': 'Graphic'
        }

        PictureModeCmdString = b'\x02AD' + self._DeviceID.encode() + b';QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[1:3]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = b'\x02AD' + self._DeviceID.encode() + b';' + PowerStateValues[value].encode() + b'\x03'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'2': 'On',
            b'1': 'Warming Up',
            b'3': 'Cooling Down',
            b'0': 'Off'
        }

        PowerCmdString = b'\x02AD' + self._DeviceID.encode() + b';Q$S\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetSideBySide(self, value, qualifier):

        SideBySideCmdString = b'\x02AD' + self._DeviceID.encode() + b';ODW\x03'
        self.__SetHelper('SideBySide', SideBySideCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        VideoMuteCmdString = b'\x02AD' + self._DeviceID.encode() + b';OSH:' + VideoMuteStateValues[value].encode() + b'\x03'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteStateNames = {
            b'0': 'Off',
            b'1': 'On'
        }

        VideoMuteCmdString = b'\x02AD' + self._DeviceID.encode() + b';QSH\x03'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteStateNames[res[1:2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02ER401\x03': "Invalid Command.",
            b'\x02ER402\x03': "Invalid Parameter"
        }
        if response in DEVICE_ERROR_CODES:
            print(sourceCmdName + ' ' + DEVICE_ERROR_CODES[response])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self.tempID == 'ALL':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + str(commandstring), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.tempID == 'ALL':
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
                return self.__CheckResponseForErrors(command + ':' + str(commandstring), res)

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
