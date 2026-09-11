from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
            'AutoFocus': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampPower': { 'Status': {}},
            'LampStatus': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Pan': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Volume': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }            

       
    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\xA0\xA3\x01\x00\x00\xAF'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        BrightnessState = {
           'Up' : b'\xA0\x39\x01\x00\x00\xAF',
           'Down' : b'\xA0\x39\x00\x00\x00\xAF'
           }
        BrightnessCmdString = BrightnessState[value]
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):  

        FocusState = {
            'Far' : 0x01,
            'Near' : 0x00,
            'Stop' : 0x00
            }
        FocusConstraints = {
            'Min' : 0,
            'Max' : 6
            }
        if FocusConstraints['Min'] <= int(qualifier['Focus Speed']) <= FocusConstraints['Max']:
            if value == 'Stop':
                focusspeed = pack('>BBBBBB',0xA0,0x19,FocusState[value],0x00,0x00,0xAF)
            else:
                focusspeed = pack('>BBBBBB',0xA0,0x1A,FocusState[value],int(qualifier['Focus Speed']),0x00,0xAF)
            FocusCmdString = focusspeed
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        FreezeState = {
           'On' : b'\xA0\x2C\x01\x00\x00\xAF',
           'Off' : b'\xA0\x2C\x00\x00\x00\xAF'
           }
        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
           b'\x01' : 'On',
           b'\x00' : 'Off'
           }

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[2:-3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (ValueError, IndexError):
                self.Discard('Invalid response for UpdateFreeze')

    def SetImageRotation(self, value, qualifier):

        ImageRotationState = {
           '0' : b'\xA0\xB4\x00\x00\x00\xAF',
           '180' : b'\xA0\xB4\x01\x00\x00\xAF',
           'Flip' : b'\xA0\xB4\x02\x00\x00\xAF',
           'Mirror' : b'\xA0\xB4\x03\x00\x00\xAF'
           }
        ImageRotationCmdString = ImageRotationState[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        InputState = {
           'Camera' : b'\xA0\x3A\x00\x00\x00\xAF',
           'PC' : b'\xA0\x3A\x01\x00\x00\xAF',
           'Off' : b'\xA0\x3A\x02\x00\x00\xAF'
           }
        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampPower(self, value, qualifier):

        LampPowerState = {
           'Lamp On'      : b'\xA0\xC1\x01\x00\x00\xAF',
           'Backlight On' : b'\xA0\xC1\x02\x00\x00\xAF',
           'Both Off'     : b'\xA0\xC1\x00\x00\x00\xAF'
           }
        LampPowerCmdString = LampPowerState[value]
        self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)

    def UpdateLampStatus(self, value, qualifier):

        LampStatusState = {
           b'\x02' : 'Lamp On',
           b'\x03' : 'Head Led On',
           b'\x01' : 'Both On',
           b'\x00' : 'Both Off'
           }

        LampStatusCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = LampStatusState[res[2:-3]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Discard('Invalid response for UpdateLampStatus')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
           'Up' : b'\xA0\xA0\x02\x00\x00\xAF',
           'Down' : b'\xA0\xA0\x03\x00\x00\xAF',
           'Left' : b'\xA0\xA0\x04\x00\x00\xAF',
           'Right' : b'\xA0\xA0\x05\x00\x00\xAF',
           'Enter' : b'\xA0\xA0\x01\x00\x00\xAF',
           'Menu' : b'\xA0\xA0\x06\x00\x00\xAF'
           }
        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPan(self, value, qualifier):

        PanState = {
           'On' : b'\xA0\x26\x01\x00\x00\xAF',
           'Off' : b'\xA0\x26\x00\x00\x00\xAF'
           }
        PanCmdString = PanState[value]
        self.__SetHelper('Pan', PanCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        PowerState = {
           'On' : b'\xA0\xB1\x01\x00\x00\xAF',
           'Off' : b'\xA0\xB1\x00\x00\x00\xAF'
           }
        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
           b'\x01' : 'On',
           b'\x00' : 'Off'
           }

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[3:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (ValueError, IndexError):
                self.Discard('Invalid response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = b'\xA0\x03\x00\x00\x00\xAF'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = b'\xA0\x03\x00\x01\x00\xAF'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):  

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 31
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = pack('>BBBBBB',0xA0,0xD6,value,0x00,0x00,0xAF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xA0\xD7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[3:4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Discard('Invalid response for UpdateVolume')

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
           'Auto Tune' : b'\xA0\x22\x00\x00\x00\xAF',
           'AWB' : b'\xA0\x22\x01\x00\x00\xAF'
           }
        WhiteBalanceCmdString = WhiteBalanceState[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomState = {
           'Tele' : b'\xA0\x1D\x00\x00\x00\xAF',
           'Wide' : b'\xA0\x1D\x01\x00\x00\xAF',
           'Stop' : b'\xA0\x10\x00\x00\x00\xAF'
           }
        ZoomCmdString = ZoomState[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if  res:            
                res = self.__CheckResponseForErrors(command + ':', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)        

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

