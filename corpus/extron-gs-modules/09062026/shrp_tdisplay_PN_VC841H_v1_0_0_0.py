from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

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
            'AudioMute': {'Status': {}},
            'AutoAdjust': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'Screen': {'Status': {}},
            'Volume': {'Status': {}}
            }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off': b'\x46\xD3\x01\x00\x02\x20\x00\x00'
        }

        AudioMuteCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoAdjust(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x32\xD4\x01\x00\x19\x20\x01\x00',
            'Off': b'\xA2\xD5\x01\x00\x19\x20\x00\x00'
        }

        AutoAdjustCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x93\x97\x01\x00\x11\x24\x01\x00',
            'Off': b'\x03\x96\x01\x00\x11\x24\x00\x00'
        }

        ExecutiveModeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        ExecutiveModeCmdString = b'\xBE\xEF\x03\x06\x00\x30\x96\x02\x00\x11\x24\x00\x00'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': b'\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'VGA': b'\x6E\xD2\x01\x00\x00\x20\x01\x00',
            'PC': b'\xFE\xD2\x01\x00\x00\x20\x00\x00'
        }

        InputCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'HDMI',
            b'\x03': 'VGA',
            b'\x01': 'PC'
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xFA\x62\x01\x00\x00\x37\x00\x00'
        }

        OnScreenDisplayCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\x2A\xD3\x01\x00\x00\x60\x00\x00'
        }

        PCPowerCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('PCPower', PCPowerCmdString, value, qualifier)

    def UpdatePCPower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PCPowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('PCPower', PCPowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('PCPower', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePCPower')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x19\xD3\x02\x00\x00\x60\x02\x00',
            'Off': b'\x19\xD3\x02\x00\x00\x60\x01\x00'
        }

        PowerCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD8\x03\x00\x00\x60\x07\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetScreen(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off': b'\xFB\xD8\x01\x00\x20\x30\x00\x00'
        }

        ScreenCmdString = b''.join([b'\xBE\xEF\x03\x06\x00', ValueStateValues[value]])
        self.__SetHelper('Screen', ScreenCmdString, value, qualifier)

    def UpdateScreen(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        ScreenCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('Screen', ScreenCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Screen', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateScreen')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 29
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volume = pack('>B', value)
            VolumeCmdString = b''.join([b'\xBE\xEF\x03\x06\x00\x31\xD3\x03\x00\x01\x20\x01', volume])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xBE\xEF\x03\x06\x00\x31\xD3\x02\x00\x01\x20\x00\x00'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
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
