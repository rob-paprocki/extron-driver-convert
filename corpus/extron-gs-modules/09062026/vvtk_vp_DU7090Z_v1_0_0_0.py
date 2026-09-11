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
        self.DeviceID = '0'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'Resync': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        self.UpdateRegex = {
            'AspectRatio': re.compile(b'F|P[0-5]'),
            'EcoMode': re.compile(b'F|P[0-5]'),
            'Freeze': re.compile(b'F|P[01]'),
            'Input': re.compile(b'F|P(?:13|1|3|4|6|9|7)'),
            'Power': re.compile(b'F|P[0123]'),
            'VideoMute': re.compile(b'F|P[01]'),
        }

        self.SetRegex = re.compile(b'P|F')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 0 <= int(value) <= 98:
            self._DeviceID = '{}'.format(value.zfill(2))
        else:
            print('Invalid Device ID. range "0" to "98" or "Broadcast"')
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': '0',
            '4:3': '1',
            '16:9': '2',
            'Letter Box': '3',
            'Native': '4',
            '2.35:1': '5'
        }

        AspectRatioCmdString = 'V{0}S0301{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Fill',
            '1': '4:3',
            '2': '16:9',
            '3': 'Letter Box',
            '4': 'Native',
            '5': '2.35:1'
        }

        AspectRatioCmdString = 'V{0}G0301\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            'Eco': '1',
            'Eco Plus': '2',
            'Dimming': '3',
            'Extreme Dimming': '4',
            'Custom Light': '5'
        }

        EcoModeCmdString = 'V{0}S0319{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Eco',
            '2': 'Eco Plus',
            '3': 'Dimming',
            '4': 'Extreme Dimming',
            '5': 'Custom Light'
        }

        EcoModeCmdString = 'V{0}G0319\r'.format(self._DeviceID)
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateEcoMode')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = 'V{0}S0304{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = 'V{0}G0304\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB': '1',
            'DVI': '3',
            'Video': '4',
            'HDMI 1': '6',
            'HDMI 2': '9',
            'BNC': '7',
        }

        if value != 'HDBaseT':
            InputCmdString = 'V{0}S020{1}\r'.format(self._DeviceID, ValueStateValues[value])
        else:
            InputCmdString = 'V{0}S0213\r'.format(self._DeviceID)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'RGB',
            '3': 'DVI',
            '4': 'Video',
            '6': 'HDMI 1',
            '9': 'HDMI 2',
            '7': 'BNC',
            '13': 'HDBaseT'
        }

        InputCmdString = 'V{0}G0220\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'V{0}G0004\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '2',
        }

        PowerCmdString = 'V{0}S000{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
            '3': 'Cooling',
            '0': 'Reset'
        }

        PowerCmdString = 'V{0}G0007\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetResync(self, value, qualifier):

        ResyncCmdString = 'V{0}S0003\r'.format(self._DeviceID)
        self.__SetHelper('Resync', ResyncCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = 'V{0}S0302{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = 'V{0}G0302\r'.format(self._DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'V{0}S0305{1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V{0}G0305\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == 'F':
            response = ''
            print('Command Failed')
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '99':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex).decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '99':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if command == 'LampUsage' or command == 'Volume':
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            else:
                upRegex = self.UpdateRegex[command]
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=upRegex).decode()
            if not res:
                return ''
            else:
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
