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
            'Aperture': { 'Status': {}},
            'AutoColor': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'Input': { 'Status': {}},
            'Iris': { 'Status': {}},
            'Lamp': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }


    def SetAperture(self, value, qualifier):


        ApertureCmdString = {
            'On'  : '\xB0\x09\x00\x05\x00\xBF', 
            'Off' : '\xB0\x09\x00\x0A\x00\xBF'
        }[value]

        self.__SetHelper('Aperture', ApertureCmdString.encode(encoding='iso-8859-1'), value, qualifier)
    def SetAutoColor(self, value, qualifier):

        
        AutoColorCmdString = '\xB0\x01\x00\x05\x00\xBF'
        self.__SetHelper('AutoColor', AutoColorCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = '\xB0\x02\x00\x05\x00\xBF'
        self.__SetHelper('AutoFocus', AutoFocusCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def SetFocus(self, value, qualifier):


        FocusCmdString = {
            'Far'  : '\xB0\x25\x00\x05\x00\xBF', 
            'Near' : '\xB0\x25\x00\x0A\x00\xBF', 
            'Stop' : '\xB0\x2F\x00\x05\x00\xBF'
        }[value]

        self.__SetHelper('Focus', FocusCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def SetFreeze(self, value, qualifier):


        FreezeCmdString = {
            'On'  : '\xB0\x12\x00\x05\x00\xBF', 
            'Off' : '\xB0\x12\x00\x0A\x00\xBF'
        }[value]

        self.__SetHelper('Freeze', FreezeCmdString.encode(encoding='iso-8859-1'), value, qualifier)
    def SetImageRotation(self, value, qualifier):

        
        ImageRotationCmdString = {
            'Off'         : '\xB0\x11\x00\x05\x00\xBF', 
            '90 Degrees'  : '\xB0\x11\x00\x08\x00\xBF', 
            '180 Degrees' : '\xB0\x11\x00\x0A\x00\xBF', 
            '270 Degrees' : '\xB0\x11\x00\x0D\x00\xBF'
        }[value]

        self.__SetHelper('ImageRotation', ImageRotationCmdString.encode(encoding='iso-8859-1'), value, qualifier)
    def SetInput(self, value, qualifier):

        
        InputCmdString = {
            'Internal' : '\xB0\x04\x00\x05\x00\xBF', 
            'External' : '\xB0\x04\x00\x0A\x00\xBF'
        }[value]

        self.__SetHelper('Input', InputCmdString.encode(encoding='iso-8859-1'), value, qualifier)
    def SetIris(self, value, qualifier):

        
        IrisCmdString = {
            'Up'   : '\xB0\x21\x00\x05\x00\xBF', 
            'Down' : '\xB0\x21\x00\x0A\x00\xBF', 
            'Stop' : '\xB0\x2F\x00\x05\x00\xBF'
        }[value]

        self.__SetHelper('Iris', IrisCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def SetLamp(self, value, qualifier):

        
        LampCmdString = {
            'On'  : '\xB0\x03\x00\x0A\x00\xBF', 
            'Off' : '\xB0\x03\x00\x05\x00\xBF'
        }[value]

        self.__SetHelper('Lamp', LampCmdString.encode(encoding='iso-8859-1'), value, qualifier)
    def SetPower(self, value, qualifier):

        
        PowerCmdString = {
            'On'  : '\xB0\x0F\x00\x05\x00\xBF', 
            'Off' : '\xB0\x0F\x00\x0A\x00\xBF'
        }[value]

        self.__SetHelper('Power', PowerCmdString.encode(encoding='iso-8859-1'), value, qualifier)
    def UpdatePower(self, value, qualifier):

        
        power_states = {
            128 : 'On', 
            0   : 'Off'
        }

        aperture_states = {
            8   : 'On', 
            0   : 'Off'
        }

        lamp_states = {
            16  : 'On', 
            0   : 'Off'
        }

        input_states = {
            0   : 'Internal', 
            32  : 'External'
        }

        freeze_states = {
            4   : 'On', 
            0   : 'Off'
        }

        rotation_states = {
            0   : 'Off', 
            1   : '90 Degrees',
            2   : '180 Degrees',
            3   : '270 Degrees'
        }

        PowerCmdString = '\xB0\x61\x00\x00\x00\xBF'.encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                power_value = power_states[res[4]&128]
                self.WriteStatus('Power', power_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

            try:
                aperture_value = aperture_states[res[3]&8]
                self.WriteStatus('Aperture', aperture_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aperture: Invalid/unexpected response'])

            try:
                lamp_value = lamp_states[res[4]&16]
                self.WriteStatus('Lamp', lamp_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

            try:
                input_value = input_states[res[4]&32]
                self.WriteStatus('Input', input_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

            try:
                freeze_value = freeze_states[res[3]&4]
                self.WriteStatus('Freeze', freeze_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

            try:
                rotation_value = rotation_states[res[3]&3]
                self.WriteStatus('ImageRotation', rotation_value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ImageRotation: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        
        PresetRecallCmdString = {
            '1' : '\xB0\x18\x00\x01\x00\xBF', 
            '2' : '\xB0\x18\x00\x02\x00\xBF', 
            '3' : '\xB0\x18\x00\x03\x00\xBF', 
            '4' : '\xB0\x18\x00\x04\x00\xBF'
        }[value]

        self.__SetHelper('PresetRecall', PresetRecallCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def SetPresetSave(self, value, qualifier):

        
        PresetSaveCmdString = {
            '1' : '\xB0\x17\x00\x01\x00\xBF', 
            '2' : '\xB0\x17\x00\x02\x00\xBF', 
            '3' : '\xB0\x17\x00\x03\x00\xBF', 
            '4' : '\xB0\x17\x00\x04\x00\xBF'
        }[value]

        self.__SetHelper('PresetSave', PresetSaveCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def SetZoom(self, value, qualifier):

        
        ZoomCmdString = {
            'Tele' : '\xB0\x26\x00\x05\x00\xBF', 
            'Wide' : '\xB0\x26\x00\x0A\x00\xBF', 
            'Stop' : '\xB0\x2F\x00\x05\x00\xBF'
        }[value]

        self.__SetHelper('Zoom', ZoomCmdString.encode(encoding='iso-8859-1'), value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True




        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xBF')
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

