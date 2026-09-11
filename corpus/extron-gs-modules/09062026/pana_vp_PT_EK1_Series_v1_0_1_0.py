from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.ProjectorID = '1'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            }
    @property
    def ProjectorID(self):
        return self._ProjectorID

    @ProjectorID.setter
    def ProjectorID(self, value):
        if value == 'Broadcast':
            self._ProjectorID = 'ZZ'
        elif 1 <= int(value) <= 64:
            self._ProjectorID = value.zfill(2)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            'Wide': '2',
            'Real': '5',
            'Full': '6',
            'Zoom': '40',
            'Custom': '50',
        }

        AspectRatioCmdString = '\x02AD' + self._ProjectorID + ';VSE:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '2': 'Wide',
            '5': 'Real',
            '6': 'Full',
            '40': 'Zoom',
            '50': 'Custom'
        }

        AspectRatioCmdString = '\x02AD' + self._ProjectorID + ';QSE\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02AD' + self._ProjectorID + ';OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '\x02AD' + self._ProjectorID + ';OSH:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AVMuteCmdString = '\x02AD' + self._ProjectorID + ';QSH\x03'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAVMute')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = '\x02AD' + self._ProjectorID + ';QFI:6\x03'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage', int(res[1:-1]), qualifier)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '\x02AD' + self._ProjectorID + ';OFZ:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '\x02AD' + self._ProjectorID + ';QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 'HD1',
            'RGB 1': 'RG1',
            'RGB 2': 'RG2',
            'DVI': 'DVI',
            'Scart': 'SCT',
            'Video': 'VID',
            'S-Video': 'SVD',
            'Computer 1': 'PC1',
            'Computer 2': 'PC2',

        }

        InputCmdString = '\x02AD' + self._ProjectorID + ';IIS:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'HD1': 'HDMI',
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'DVI': 'DVI',
            'SCT': 'Scart',
            'VID': 'Video',
            'SVD': 'S-Video',

        }

        InputCmdString = '\x02AD' + self._ProjectorID + ';QIN\x03'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            'Auto': '2',
            'Eco 1': '3',
            'Eco 2': '4'
        }

        LampModeCmdString = '\x02AD' + self._ProjectorID + ';OLP:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Auto',
            '3': 'Eco 1',
            '4': 'Eco 2'
        }

        LampModeCmdString = '\x02AD' + self._ProjectorID + ';QLP\x03'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampMode')

    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Quad': '0',
            'Lamp 1 and 4': '1',
            'Lamp 2 and 3': '2',
            'Dual': '3'
        }

        LampSelectCmdString = '\x02AD' + self._ProjectorID + ';LPM:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        ValueStateValues = {
            '0': 'Quad',
            '1': 'Lamp 1 and 4',
            '2': 'Lamp 2 and 3',
            '3': 'Dual'
        }

        LampSelectCmdString = '\x02AD' + self._ProjectorID + ';QSL\x03'
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampSelect')

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']

        LampUsageCmdString = '\x02AD' + self._ProjectorID + ';Q$L:{0}\x03'.format(lamp)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', int(res[1:-1]), qualifier)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'OMN',
            'Enter': 'OEN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR'
        }

        MenuNavigationCmdString = '\x02AD' + self._ProjectorID + ';{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '\x02AD' + self._ProjectorID + ';QST\x03'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('OperationHours', int(res[1:-1]), qualifier)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateOperationHours')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CIN',
            'Real': 'REA',
            'Image 1': 'IM1',
            'Image 2': 'IM2',
            'Image 3': 'IM3',
            'Image 4': 'IM4',
            'Image 5': 'IM5',
            'Image 6': 'IM6',
            'Image 7': 'IM7',
            'Image 8': 'IM8',
            'Image 9': 'IM9'
        }

        PictureModeCmdString = '\x02AD' + self._ProjectorID + ';VPM:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CIN': 'Cinema',
            'REA': 'Real',
            'IM1': 'Image 1',
            'IM2': 'Image 2',
            'IM3': 'Image 3',
            'IM4': 'Image 4',
            'IM5': 'Image 5',
            'IM6': 'Image 6',
            'IM7': 'Image 7',
            'IM8': 'Image 8',
            'IM9': 'Image 9'
        }

        PictureModeCmdString = '\x02AD' + self._ProjectorID + ';QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = '\x02AD' + self._ProjectorID + ';{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '001': 'On',
            '000': 'Off'
        }

        PowerCmdString = '\x02AD' + self._ProjectorID + ';QPW\x03'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': "Invalid Command.",
            '\x02ER402\x03': "Invalid Parameter"
        }
        if response in DEVICE_ERROR_CODES:
            print(sourceCmdName + ' ' + DEVICE_ERROR_CODES[response])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._ProjectorID == 'ZZ':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03').decode()
            if res:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)            

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
