from extronlib.interface import SerialInterface, EthernetClientInterface

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1': '0',
            '16:9': '3',
            '4:3': '4',
            'Fill All': '1',
            'Fill Aspect Ratio': '2',
            'Fill 2.35:1': '5',
            'Anamorphic Lens': '11'
        }

        AspectRatioCmdString = ':SABS{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '00': '1:1',
            '03': '16:9',
            '04': '4:3',
            '01': 'Fill All',
            '02': 'Fill Aspect Ratio',
            '05': 'Fill 2.35:1',
            '11': 'Anamorphic Lens'
        }

        AspectRatioCmdString = ':SABS?\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[14:16]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = ':AUTO\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = ':FRZE{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = ':FRZE?\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:16]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': '0',
            'VGA 2': '1',
            'HDMI 1': '8',
            'HDMI 2': '11',
            'DVI 1': '2',
            'DVI 2': '10',
            'DVI Dual': '12',
            'HDMI Dual': '13',
            'Component': '7'
        }

        InputCmdString = ':IABS{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '00': 'VGA 1',
            '01': 'VGA 2',
            '07': 'Component',
            '08': 'HDMI 1',
            '11': 'HDMI 2',
            '02': 'DVI 1',
            '10': 'DVI 2',
            '12': 'DVI Dual',
            '13': 'HDMI Dual'
        }

        InputCmdString = ':IABS?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[14:16]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': ':ECOM1\r',
            'Normal': ':ECOM0\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Eco',
            '0': 'Normal'
        }

        LampModeCmdString = ':ECOM?\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:16]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Lamp 1': '0',
            'Lamp 2': '1',
            'Dual Lamp': '2',
            'Auto': '3'
        }

        LampSelectCmdString = ':LMOD{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        ValueStateValues = {
            '0': 'Lamp 1',
            '1': 'Lamp 2',
            '2': 'Dual Lamp',
            '3': 'Auto'
        }

        LampSelectCmdString = ':LMOD?\r'
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:16]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampSelect')

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Defect',
            '1': 'Warming Up',
            '2': 'On',
            '3': 'Off',
            '4': 'Cooling Down',
            '5': 'Not Present'
        }

        if 1 <= int(qualifier['Lamp']) <= 2:
            LampStatusCmdString = ':LST{}?\r'.format(qualifier['Lamp'])
            res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[15:16]]
                    self.WriteStatus('LampStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateLampStatus')
        else:
            print('Invalid Command for UpdateLampStatus')

    def UpdateLampUsage(self, value, qualifier):

        if 1 <= int(qualifier['Lamp']) <= 2:
            LampUsageCmdString = ':LTR{}?\r'.format(qualifier['Lamp'])
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[12:16])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateLampUsage')
        else:
            print('Invalid Command for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': ':MENU\r',
            'Up': ':NVUP\r',
            'Down': ':NVDW\r',
            'Left': ':NVLF\r',
            'Right': ':NVRH\r',
            'Ok': ':NVOK\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': ':OSDC2\r',
            'Show Only Warnings': ':OSDC1\r',
            'Off': ':OSDC0\r'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Show Only Warnings',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = ':OSDC?\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:16]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = ':UTOT?\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10:16])
                self.WriteStatus('OperationHours', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': ':POWR1\r',
            'Off': ':POWR0\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Off',
            '2': 'Warming Up',
            '3': 'On',
            '4': 'Cooling Down',
            '5': 'Cooling Down',
            '6': 'Off',
            '7': 'On',
            '8': 'Cooling Down'
        }

        PowerCmdString = ':POST?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:16]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': ':PMUT1\r',
            'Off': ':PMUT0\r'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = ':PMUT?\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[15:16]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '!00001': 'Access Denied',
            '!00002': 'Not Available',
            '!00003': 'Not Implemented',
            '!00004': 'Value Out of Range',
            }
        if response[10:16] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[10:16]]))
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
