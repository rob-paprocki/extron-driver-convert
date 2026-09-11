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
            'AutoImage': {'Status': {}},
            'Blank': {'Status': {}},
            'Freeze': {'Status': {}},
            'LampHours': {'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Source': {'Status': {}},
            'Volume': {'Status': {}}
            }        

        self.SetRegex = re.compile(b'OK|ERR')
        self.UpdateRegex1 = re.compile(b'[0-9]')
        self.UpdateRegex2 = re.compile(b'[0-9]{2}')
        self.UpdateRegex3 = re.compile(b'[0-9]{3}')
        self.UpdateRegex4 = re.compile(b'[0-9]{4}')

        self.UpdateRegex = {
            1: self.UpdateRegex1,
            2: self.UpdateRegex2,
            3: self.UpdateRegex3,
            4: self.UpdateRegex4
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': '0',
            '4:3': '1',
            '16:9': '2',
            'Letterbox': '3',
            'Native': '4',
            '2.35:1': '5'
        }

        AspectRatioCmdString = 'ASPC___{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Fill',
            '1': '4:3',
            '2': '16:9',
            '3': 'Letterbox',
            '4': 'Native',
            '5': '2.35:1'
        }

        AspectRatioCmdString = 'ASPC????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Update Aspect Ratio: Invalid/unexpected response')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ADJS___1\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBlank(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        BlankCmdString = 'PIMU___{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Blank', BlankCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'KYFR___1\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = 'PJRT????\r'
        res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        if res:
            try:
                value = res[0:]
                self.WriteStatus('LampHours', int(value), qualifier)
            except (ValueError, IndexError):
                print('Update Lamp Hours: Invalid/unexpected response')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': '0',
            'Normal': '1',
            'Dynamic Eco': '2'
        }

        LampModeCmdString = 'LMPM___{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Eco',
            '1': 'Normal',
            '2': 'Dynamic Eco'
        }

        LampModeCmdString = 'LMPM????\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Update Lamp Mode: Invalid/unexpected response')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'KYMN___1\r',
            'Enter': 'KYEN___1\r',
            'Up': 'KYUP___1\r',
            'Down': 'KYDO___1\r',
            'Left': 'KYLE___1\r',
            'Right': 'KYRI___1\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = 'POWR___{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
            '0': 'Reset',
            '3': 'Cooling'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Update Power: Invalid/unexpected response')

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': 'ISEL___1\r',
            'VGA 2': 'ISEL___2\r',
            'DVI': 'ISEL___3\r',
            'Video': 'ISEL___4\r',
            'S-Video': 'ISEL___5\r',
            'HDMI 1': 'ISEL___6\r',
            'BNC': 'ISEL___7\r',
            'Component': 'ISEL___8\r',
            'Display Port': 'ISEL___9\r',
            'HDMI 2': 'ISEL__10\r'
        }

        SourceCmdString = ValueStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            '1': 'VGA 1',
            '2': 'VGA 2',
            '3': 'DVI',
            '4': 'Video',
            '5': 'S-Video',
            '6': 'HDMI 1',
            '7': 'BNC',
            '8': 'Component',
            '9': 'Display Port',
            '10': 'HDMI 2'
        }

        SourceCmdString = 'ICHK????\r'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                print('Update Source: Invalid/unexpected response')

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '9999',
            'Down': '8888'
        }

        VolumeCmdString = 'KYVO{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            print('{0} : Invalid command reply'.format(sourceCmdName))
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                print('Set {0}: Invalid/Unexpected Response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier, length=1):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex[length])
            if not res:
                if length <= 1:
                    return ''
                else:
                    if length > 1:
                        return self.__UpdateHelper(command, commandstring, value, qualifier, length - 1)
            else:
                return self.__CheckResponseForErrors(command, res.decode())            

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
