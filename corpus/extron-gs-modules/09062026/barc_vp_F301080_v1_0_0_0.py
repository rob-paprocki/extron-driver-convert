from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait
import re

class DeviceClass:

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Iris': {'Parameters': ['Speed'], 'Status': {}},
            'LampMode': {'Status': {}},
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': {'Parameters': ['Speed'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMute': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            }
        self.CmdCounter = 0
        self.UpdateAllow = 0
        self.DelayUpdateCmds = Wait(5, self.DelayFlag)
        self.DelayUpdateCmds.Cancel()

    def DelayFlag(self):
        self.UpdateAllow = 0
        self.CmdCounter = 0

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1': b':SABS0\r',
            'Fill All': b':SABS1\r',
            'Fill Aspect Ratio': b':SABS2\r',
            'Fill 16:9': b':SABS3\r',
            'Fill 4:3': b':SABS4\r',
            'Letterbox 16:9': b':SABS9\r',
            'Letterbox St 16:9': b':SABS10\r',
            'Anamorphic Lens': b':SABS11\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'000000': '1:1',
            b'000001': 'Fill All',
            b'000002': 'Fill Aspect Ratio',
            b'000003': 'Fill 16:9',
            b'000004': 'Fill 4:3',
            b'000009': 'Letterbox 16:9',
            b'000010': 'Letterbox St 16:9',
            b'000011': 'Anamorphic Lens'
        }

        AspectRatioCmdString = b':SABS?\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b':AUTO\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'On': b':ECOM1\r',
            'Off': b':ECOM0\r'
        }

        EcoModeCmdString = ValueStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            b'000001': 'On',
            b'000000': 'Off'
        }

        EcoModeCmdString = b':ECOM?\r'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedStates = {
            'Slow': b'1',
            'Medium': b'2',
            'Fast': b'3'
        }

        ValueStateValues = {
            'In': b'OIN',
            'Out': b'OUT'
        }

        speed_val = qualifier['Speed']
        if speed_val in SpeedStates:
            FocusCmdString = b''.join([b':F', ValueStateValues[value], SpeedStates[speed_val], b'\r'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b':FRZE1\r',
            'Off': b':FRZE0\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'000001': 'On',
            b'000000': 'Off'
        }

        FreezeCmdString = b':FRZE?\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b':IABS0\r',
            'DVI': b':IABS2\r',
            'S-Video': b':IABS4\r',
            'Composite': b':IABS5\r',
            'Component': b':IABS6\r',
            'RGBs': b':IABS7\r',
            'HDMI': b':IABS8\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'000000': 'VGA',
            b'000002': 'DVI',
            b'000004': 'S-Video',
            b'000005': 'Composite',
            b'000006': 'Component',
            b'000007': 'RGBs',
            b'000008': 'HDMI'
        }

        InputCmdString = b':IABS?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        SpeedStates = {
            'Slow': b'1',
            'Medium': b'2',
            'Fast': b'3'
        }

        ValueStateValues = {
            'Open': b'ROP',
            'Close': b'RCL'
        }

        speed_val = qualifier['Speed']
        if speed_val in SpeedStates:
            IrisCmdString = b''.join([b':I', ValueStateValues[value], SpeedStates[speed_val], b'\r'])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Lamp 1': b':LMOD0\r',
            'Lamp 2': b':LMOD1\r',
            'Dual': b':LMOD2\r',
            'Auto': b':LMOD3\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'000000': 'Lamp 1',
            b'000001': 'Lamp 2',
            b'000002': 'Dual',
            b'000003': 'Auto'
        }

        LampModeCmdString = b':LMOD?\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            b'000000': 'Broken',
            b'000001': 'Warming Up',
            b'000002': 'On',
            b'000003': 'Off',
            b'000004': 'Cooling Down',
            b'000005': 'Not Present'
        }

        lamp_val = qualifier['Lamp']
        if lamp_val in ['1', '2']:
            LampStatusCmdString = b''.join([b':LST', lamp_val.encode(), b'?\r'])
            res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res.split()[2]]
                    self.WriteStatus('LampStatus', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Lamp Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampStatus')

    def UpdateLampUsage(self, value, qualifier):

        lamp_val = qualifier['Lamp']
        if lamp_val in ['1', '2']:
            LampUsageCmdString = b''.join([b':LTR', lamp_val.encode(), b'?\r'])
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res.split()[2])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetLensShift(self, value, qualifier):

        SpeedStates = {
            'Slow': b'1',
            'Medium': b'2',
            'Fast': b'3'
        }

        ValueStateValues = {
            'Up': b'SUP',
            'Down': b'SDW',
            'Left': b'SLF',
            'Right': b'SRH'
        }

        speed_val = qualifier['Speed']
        if speed_val in SpeedStates:
            LensShiftCmdString = b''.join([b':L', ValueStateValues[value], SpeedStates[speed_val], b'\r'])
            self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensShift')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': ':MENU\r',
            'Up': ':NVUP\r',
            'Down': ':NVDW\r',
            'Left': ':NVLF\r',
            'Right': ':NVRH\r',
            'OK': ':NVOK\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'Off': b':OSDC0\r',
            'Warnings Only': b':OSDC1\r',
            'On': b':OSDC2\r'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            b'000000': 'Off',
            b'000001': 'Warnings Only',
            b'000002': 'On'
        }

        OnScreenDisplayCmdString = b':OSDC?\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b':UTOT?\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res.split()[2])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureMute(self, value, qualifier):

        ValueStateValues = {
            'On': b':PMUT1\r',
            'Off': b':PMUT0\r'
        }

        PictureMuteCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMute', PictureMuteCmdString, value, qualifier)

    def UpdatePictureMute(self, value, qualifier):

        ValueStateValues = {
            b'000001': 'On',
            b'000000': 'Off'
        }

        PictureMuteCmdString = b':PMUT?\r'
        res = self.__UpdateHelper('PictureMute', PictureMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('PictureMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b':POWR1\r',
            'Off': b':POWR0\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'000003': 'On',
            b'000006': 'Off',
            b'000001': 'Off',
            b'000000': 'Off',
            b'000002': 'Warming Up',
            b'000004': 'Cooling Down',
            b'000005': 'Cooling Down'
        }

        PowerCmdString = b':POST?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.split()[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': b':SHUT1\r',
            'Off': b':SHUT0\r'
        }

        ShutterCmdString = ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        SpeedStates = {
            'Slow': b'1',
            'Medium': b'2',
            'Fast': b'3'
        }

        ValueStateValues = {
            'In': b'OIN',
            'Out': b'OUT'
        }

        speed_val = qualifier['Speed']
        if speed_val in SpeedStates:
            ZoomCmdString = b''.join([b':Z', ValueStateValues[value], SpeedStates[speed_val], b'\r'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'!00001': '{}: Access Denied.',
            b'!00002': '{}: Not Available.',
            b'!00003': '{}: Not Implemented.',
            b'!00004': '{}: Value Out of Range.',
        }
        error_val = response.split()[2]
        if error_val in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[error_val].format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.CmdCounter >= 20 and self.UpdateAllow == 0:
            self.UpdateAllow = 1
            self.DelayUpdateCmds.Restart()

        elif self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            self.CmdCounter += 1
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.CmdCounter >= 20 and self.UpdateAllow == 0:
            self.UpdateAllow = 1
            self.DelayUpdateCmds.Restart()
            print('20 commands received. Device is busy wait 5 seconds before sending an Update command')

        if self.Unidirectional == 'True' or self.UpdateAllow == 1:
            self.Discard('Inappropriate Command {}. Device is busy wait 5 seconds before sending an Update command'.format(command))
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.CmdCounter += 1
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.CmdCounter = 0
        self.UpdateAllow = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

