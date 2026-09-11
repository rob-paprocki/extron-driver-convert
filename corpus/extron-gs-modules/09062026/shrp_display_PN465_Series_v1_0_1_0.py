from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re

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
            'AutoImage': {'Parameters': ['Input'], 'Status': {}},
            'EnlargeMode': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenSize': {'Parameters': ['Input'], 'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAutoImage(self, value, qualifier):
        tempValue = qualifier['Input']
        if tempValue:
            if 'PC2' == tempValue or 'PC3' == tempValue:
                AutoImageCmdString = 'AGIN   1\r'
            else:
                AutoImageCmdString = 'ASNC   1\r'
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAutoImage')

    def SetEnlargeMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '2x2': '1',
            '3x3': '2',
            '4x4': '3',
            '5x5': '4'
        }

        EnlargeModeCmdString = 'EMAG   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('EnlargeMode', EnlargeModeCmdString, value, qualifier)

    def UpdateEnlargeMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': '2x2',
            '2': '3x3',
            '3': '4x4',
            '4': '5x5'
        }

        EnlargeModeCmdString = 'EMAG????\r'
        res = self.__UpdateHelper('EnlargeMode', EnlargeModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('EnlargeMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateEnlargeMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'PC1 Digital': '1',
            'PC2 Analog': '2',
            'AV2 Component': '3',
            'AV3 Video': '4',
            'PC3 Analog': '6',
            'AV1 Digital': '7'
        }

        InputCmdString = 'INPS   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'PC1 Digital',
            '2': 'PC2 Analog',
            '3': 'AV2 Component',
            '4': 'AV3 Video',
            '6': 'PC3 Analog',
            '7': 'AV1 Digital'
        }

        InputCmdString = 'INPS????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MuteCmdString = 'MUTE   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'PC1 Digital': '1',
            'PC2 Analog': '2',
            'AV2 Component': '3',
            'AV3 Video': '4',
            'PC3 Analog': '6',
            'AV1 Digital': '7'
        }

        PIPInputCmdString = 'MWIP   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'PC1 Digital',
            '2': 'PC2 Analog',
            '3': 'AV2 Component',
            '4': 'AV3 Video',
            '6': 'PC3 Analog',
            '7': 'AV1 Digital'
        }

        PIPInputCmdString = 'MWIP????\r'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'PIP': '1',
            'PbyP': '2',
            'PbyP2': '3'
        }

        PIPModeCmdString = 'MWIN   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PbyP',
            '3': 'PbyP2'
        }

        PIPModeCmdString = 'MWIN????\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = 'POWR   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input Signal Waiting Mode'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetScreenSize(self, value, qualifier):

        ValueStateValuesPC = {
            'Wide': '1',
            'Normal': '2',
            'DotbyDot': '3',
            'Zoom1': '4',
            'Zoom2': '5'
        }

        ValueStateValuesAV = {
            'Wide': '1',
            'Normal': '4',
            'DotbyDot': '5',
            'Zoom1': '2',
            'Zoom2': '3'
        }

        tempValue = qualifier['Input']
        if tempValue:
            if 'AV' in tempValue:
                ScreenSizeCmdString = 'WIDE   {0}\r'.format(ValueStateValuesAV[value])
            elif 'PC' in tempValue:
                ScreenSizeCmdString = 'WIDE   {0}\r'.format(ValueStateValuesPC[value])

            self.__SetHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScreenSize')

    def UpdateScreenSize(self, value, qualifier):

        ValueStateValuesPC = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'DotbyDot',
            '4': 'Zoom1',
            '5': 'Zoom2'
        }

        ValueStateValuesAV = {
            '1': 'Wide',
            '4': 'Normal',
            '5': 'DotbyDot',
            '2': 'Zoom1',
            '3': 'Zoom2'
        }

        tempValue = qualifier['Input']
        ScreenSizeCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('ScreenSize', ScreenSizeCmdString, value, qualifier)
        if res and tempValue:
            try:
                if 'AV' in tempValue:
                    value = ValueStateValuesAV[res[0]]
                elif 'PC' in tempValue:
                    value = ValueStateValuesPC[res[0]]
                if value:
                    self.WriteStatus('ScreenSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateScreenSize')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
            }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:04}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'ERR\x0D' in response:
            ErrorString = sourceCmdName + ': Communcation error or incorrect command'
            print(ErrorString)
            response = ''
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
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
