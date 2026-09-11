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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Blank': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PiPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'SourceLayoutInput': {'Parameters': ['Window'], 'Status': {}},
            'SourceLayoutMode': {'Status': {}},
        }
       
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1': b'\x30',
            'Fill Screen': b'\x31',
            '4:3': b'\x39',
            '16:9': b'\x41',
            '5:4': b'\x46'
        }

        AspectRatioCmdString = b''.join([b'\x8C', ValueStateValues[value]])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x30': '1:1',
            b'\x31': 'Fill Screen',
            b'\x39': '4:3',
            b'\x41': '16:9',
            b'\x46': '5:4'
        }

        AspectRatioCmdString = b'\x8C\x3F'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier, 3)
        if res:
            try:
                value = ValueStateValues[res[-1:]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetBlank(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x30',
            'Off': b'\x31'
        }

        BlankCmdString = b''.join([b'\xE1', ValueStateValues[value]])
        self.__SetHelper('Blank', BlankCmdString, value, qualifier)

    def UpdateBlank(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'On',
            b'\x31': 'Off'
        }

        BlankCmdString = b'\xE1\x3F'
        res = self.__UpdateHelper('Blank', BlankCmdString, value, qualifier, 3)
        if res:
            try:
                value = ValueStateValues[res[-1:]]
                self.WriteStatus('Blank', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateBlank')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x41\x31',
            'DisplayPort': b'\x50\x31',
            'HDMI 1': b'\x48\x31',
            'HDMI 2': b'\x48\x32',
            'HDMI 3': b'\x48\x33',
            'DVI': b'\x46\x31'
        }

        InputCmdString = b''.join([b'\x98', ValueStateValues[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x41\x31': 'VGA',
            b'\x50\x31': 'DisplayPort',
            b'\x48\x31': 'HDMI 1',
            b'\x48\x32': 'HDMI 2',
            b'\x48\x33': 'HDMI 3',
            b'\x46\x31': 'DVI'
        }

        InputCmdString = b'\x98\x3F'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier, 4)
        if res:
            try:
                value = ValueStateValues[res[-2:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xF7',
            'Up': b'\xFB',
            'Down': b'\xFA',
            'Right': b'\xFC',
            'Left': b'\xFD'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPiPSwap(self, value, qualifier):

        PiPSwapCmdString = b'\xE3'
        self.__SetHelper('PiPSwap', PiPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30'
        }

        PowerCmdString = b''.join([b'\xC8', ValueStateValues[value]])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x30': 'Off'
        }

        PowerCmdString = b'\xC8\x3F'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier, 3)
        if res:
            try:
                value = ValueStateValues[res[-1:]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetSourceLayoutInput(self, value, qualifier):

        WindowStates = {
            '2P': b'',
            '3P': b'\x63',
            '4P': b'\x64'
        }

        ValueStateValues = {
            'VGA': b'\x41\x31',
            'DisplayPort': b'\x50\x31',
            'HDMI 1': b'\x48\x31',
            'HDMI 2': b'\x48\x32',
            'HDMI 3': b'\x48\x33',
            'DVI': b'\x46\x31'
        }

        SourceLayoutInputCmdString = b''.join([b'\xA7', WindowStates[qualifier['Window']], ValueStateValues[value]])
        self.__SetHelper('SourceLayoutInput', SourceLayoutInputCmdString, value, qualifier)

    def UpdateSourceLayoutInput(self, value, qualifier):

        WindowStates = {
            '2P': b'',
            '3P': b'\x63',
            '4P': b'\x64'
        }

        ValueStateValues = {
            b'\x41\x31': 'VGA',
            b'\x50\x31': 'DisplayPort',
            b'\x48\x31': 'HDMI 1',
            b'\x48\x32': 'HDMI 2',
            b'\x48\x33': 'HDMI 3',
            b'\x46\x31': 'DVI'
        }

        SourceLayoutInputCmdString = b''.join([b'\xA7', WindowStates[qualifier['Window']], b'\x3F'])

        if qualifier['Window'] == '2P':
            resLen = 4
        else:
            resLen = 5

        res = self.__UpdateHelper('SourceLayoutInput', SourceLayoutInputCmdString, value, qualifier, resLen)
        if res:
            try:
                value = ValueStateValues[res[-2:]]
                self.WriteStatus('SourceLayoutInput', value, qualifier)
            except (KeyError, IndexError, TypeError):
                print('Invalid/unexpected response for UpdateSourceLayoutInput')

    def SetSourceLayoutMode(self, value, qualifier):

        ValueStateValues = {
            'Single': b'\x30',
            'PiP': b'\x31',
            'PbP (Left Right)': b'\x32',
            'PbP (Top Bottom)': b'\x33',
            '4 PiP': b'\x34'
        }

        SourceLayoutModeCmdString = b''.join([b'\x9A', ValueStateValues[value]])
        self.__SetHelper('SourceLayoutMode', SourceLayoutModeCmdString, value, qualifier)

    def UpdateSourceLayoutMode(self, value, qualifier):

        ValueStateValues = {
            b'\x30': 'Single',
            b'\x31': 'PiP',
            b'\x32': 'PbP (Left Right)',
            b'\x33': 'PbP (Top Bottom)',
            b'\x34': '4 PiP'
        }

        SourceLayoutModeCmdString = b'\x9A\x3F'
        res = self.__UpdateHelper('SourceLayoutMode', SourceLayoutModeCmdString, value, qualifier, 3)
        if res:
            try:
                value = ValueStateValues[res[-1:]]
                self.WriteStatus('SourceLayoutMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateSourceLayoutMode')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier, length):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=length)
            if res:
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
