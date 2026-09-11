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
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VolumeStatus': {'Status': {}},
            'VolumeStep': {'Status': {}}
            }        

        self.updateRegex = re.compile(b'\x05\x14\x00[\x03|\x06]\x00\x00[\x00-\xFF]{3}')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x00\x62',
            '4:3': b'\x02\x64',
            '16:9': b'\x03\x65',
            '16:10': b'\x04\x66',
            'Anamorphic': b'\x05\x67',
            'Wide': b'\x06\x68'
        }

        AspectRatioCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x12\x04', ValueStateValues[value]])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0: 'Auto',
            2: '4:3',
            3: '16:9',
            4: '16:10',
            5: 'Anamorphic',
            6: 'Wide'
        }

        AspectRatioCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x04\x63'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x61',
            'Off': b'\x00\x60'
        }

        AudioMuteCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x14\x00', ValueStateValues[value]])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x00\x61'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x06\x14\x00\x04\x00\x34\x12\x05\x00\x63'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x60',
            'Off': b'\x00\x5F'
        }

        FreezeCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x13\x00', ValueStateValues[value]])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        FreezeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x00\x60'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': b'\x00\x60',
            'VGA 2': b'\x08\x68',
            'HDMI 1': b'\x03\x63',
            'HDMI 2': b'\x07\x67',
            'Composite': b'\x05\x65',
            'S-Video': b'\x06\x66'
        }

        InputCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x13\x01', ValueStateValues[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0: 'VGA 1',
            8: 'VGA 2',
            3: 'HDMI 1',
            7: 'HDMI 2',
            5: 'Composite',
            6: 'S-Video'
        }

        InputCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x13\x01\x61'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x00\x6D',
            'Economic': b'\x01\x6E',
            'Dynamic': b'\x02\x6F',
            'Sleep Mode': b'\x03\x70'
        }

        LampModeCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x11\x10', ValueStateValues[value]])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Economic',
            2: 'Dynamic',
            3: 'Sleep Mode'
        }

        LampModeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x10\x6E'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x15\x01\x63'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = 256 * res[7] + res[6]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x0F\x61',
            'Exit': b'\x13\x65',
            'Up': b'\x0B\x5D',
            'Down': b'\x0C\x5E',
            'Left': b'\x0D\x5F',
            'Right': b'\x0E\x60',
            'Enter': b'\x15\x67'
        }

        MenuNavigationCmdString = b''.join([b'\x02\x14\x00\x04\x00\x34\x02\x04', ValueStateValues[value]])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Brightest': b'\x00\x69',
            'Movie': b'\x01\x6A',
            'PC': b'\x04\x6D',
            'ViewMatch': b'\x05\x6E',
            'Dynamic': b'\x08\x71'
        }

        PictureModeCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x12\x0B', ValueStateValues[value]])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Brightest',
            1: 'Movie',
            4: 'PC',
            5: 'ViewMatch',
            8: 'Dynamic'
        }

        PictureModeCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x0B\x6A'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00\x00\x5D',
            'Off': b'\x01\x00\x5E'
        }

        PowerCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x11', ValueStateValues[value]])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            24: 'On',
            23: 'Off'
        }

        PowerCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x11\x00\x5E'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x68',
            'Off': b'\x00\x67'
        }

        VideoMuteCmdString = b''.join([b'\x06\x14\x00\x04\x00\x34\x12\x09', ValueStateValues[value]])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x12\x09\x68'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = b'\x07\x14\x00\x05\x00\x34\x00\x00\x14\x03\x64'
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolumeStatus')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Increase': b'\x06\x14\x00\x04\x00\x34\x14\x01\x00\x61',
            'Decrease': b'\x06\x14\x00\x04\x00\x34\x14\x02\x00\x62'
        }

        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex)
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
