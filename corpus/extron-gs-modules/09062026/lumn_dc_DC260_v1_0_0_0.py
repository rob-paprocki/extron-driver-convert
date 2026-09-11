from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
            'Brightness': { 'Status': {}},
            'BrightnessStatus': { 'Status': {}},
            'Capture': { 'Status': {}},
            'Color': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageMode': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'Iris': { 'Status': {}},
            'IrisMode': { 'Status': {}},
            'Lamp': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Negative': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Sharpness': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }

        self.lastIrisUpdate = 0
        self.IrisValue = 0



    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            '+' : 0x01,
            '-' : 0x00
        }

        BrightnessCmdString = pack('6B', 0xA0, 0x39, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)


    def UpdateBrightnessStatus(self, value, qualifier):

        BrightnessStatusCmdString = b'\xA0\x89\x00\x00\x00\xAF'
        res = self.__UpdateHelper('BrightnessStatus', BrightnessStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2])
                self.WriteStatus('BrightnessStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness Status: Invalid/unexpected response'])

    def SetCapture(self, value, qualifier):

        ValueStateValues = {
            'Capture' : 0x00,
            'Record' : 0x01
        }

        CaptureCmdString = pack('6B', 0xA0, 0xB2, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)


    def SetColor(self, value, qualifier):

        ValueStateValues = {
            'Photo' : 0x00,
            'Gray' : 0x01
        }

        ColorCmdString = pack('6B', 0xA0, 0x37, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Color', ColorCmdString, value, qualifier)
    def UpdateColor(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Photo',
            b'\x01' : 'Gray'
        }

        ColorCmdString = b'\xA0\x88\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Color', ColorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Color', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near' : 0x00,
            'Far' : 0x01
        }

        FocusCmdString = ''
        if 1 <= int(qualifier['Speed']) <= 5:
            if value == 'Stop':
                FocusCmdString = b'\xA0\x19\x00\x00\x00\xAF'
            else:
                FocusCmdString = pack('6B', 0xA0, 0x1A, ValueStateValues[value], int(qualifier['Speed']), 0x00, 0xAF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')


    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01,
            'Off' : 0x00
        }

        FreezeCmdString = pack('6B', 0xA0, 0x2C, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On',
            b'\x00' : 'Off'
        }

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : 0x00,
            'Slide' : 0x01,
            'Film' : 0x02,
            'Microscope' : 0x03
        }

        ImageModeCmdString = pack('6B', 0xA0, 0xA9, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)


    def SetImageRotation(self, value, qualifier):

        ValueStateValues = {
            '0' : 0x00,
            '90' : 0x01,
            '180' : 0x02,
            '270' : 0x03
        }

        ImageRotationCmdString = pack('6B', 0xA0, 0xB4, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)


    def SetIris(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 191
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.IrisValue = value
            IrisCmdString = pack('6B', 0xA0, 0x30, 0x01, value, 0x00, 0xAF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')
    def UpdateIris(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Auto',
            b'\x01' : 'Manual',
            b'\x02' : 'Stop'
        }

        IrisCmdString = b'\xA0\x7A\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('IrisMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Iris Mode: Invalid/unexpected response'])

            try:
                value = int(res[3])
                self.IrisValue = value
                self.WriteStatus('Iris', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Iris: Invalid/unexpected response'])

    def SetIrisMode(self, value, qualifier):

        ValueStateValues = {
            'Auto' : 0x00,
            'Manual' : 0x01,
            'Stop' : 0x02
        }

        IrisModeCmdString = pack('6B', 0xA0, 0x30, ValueStateValues[value], self.IrisValue, 0x00, 0xAF)
        self.__SetHelper('IrisMode', IrisModeCmdString, value, qualifier)
    def UpdateIrisMode(self, value, qualifier):

        self.UpdateIris(value, None)

    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01,
            'Off' : 0x00
        }

        LampCmdString = pack('6B', 0xA0, 0xC1, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)
    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On',
            b'\x00' : 'Off'
        }

        LampCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu' : 0x01,
            'Up' : 0x02,
            'Down' : 0x03,
            'Left' : 0x04,
            'Right' : 0x05,
            'Enter' : 0x06
        }

        MenuNavigationCmdString = pack('6B', 0xA0, 0xA0, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetNegative(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01,
            'Off' : 0x00
        }

        NegativeCmdString = pack('6B', 0xA0, 0x36, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Negative', NegativeCmdString, value, qualifier)
    def UpdateNegative(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On',
            b'\x00' : 'Off'
        }

        NegativeCmdString = b'\xA0\x87\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Negative', NegativeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Negative', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Negative: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01,
            'Off' : 0x00
        }

        PowerCmdString = pack('6B', 0xA0, 0xB1, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'On',
            b'\x00' : 'Off'
        }

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = 'Not Ready' if res[2:3] == b'\x00' else ValueStateValues[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = b'\xA0\x03\x00\x00\x00\xAF'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)


    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = b'\xA0\x03\x00\x01\x00\xAF'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)


    def SetSharpness(self, value, qualifier):

        ValueStateValues = {
            'Photo' : 0x00,
            'Text' : 0x01,
            'Gray' : 0x02
        }

        SharpnessCmdString = pack('6B', 0xA0, 0xA7, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)
    def UpdateSharpness(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Photo',
            b'\x01' : 'Text',
            b'\x02' : 'Gray'
        }

        SharpnessCmdString = b'\xA0\x51\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Sharpness', SharpnessCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Sharpness', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Sharpness: Invalid/unexpected response'])

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto Tune' : 0x00,
            'AWB' : 0x01
        }

        WhiteBalanceCmdString = pack('6B', 0xA0, 0x22, ValueStateValues[value], 0x00, 0x00, 0xAF)
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)


    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : [0x1D, 0x00],
            'Wide' : [0x1D, 0x01],
            'Stop' : [0x10, 0x00]
        }

        ZoomCmdString = pack('6B', 0xA0, ValueStateValues[value][0], ValueStateValues[value][1], 0x00, 0x00, 0xAF)
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {
            b'\x01': 'Command failed to execute',
            b'\x10': 'Command not supported'
        }

        if response[4:5] in ErrorStates:
            self.Error(['{0}: {1}'.format(sourceCmdName, ErrorStates[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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
            return self.__CheckResponseForErrors(command, res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastIrisUpdate = 0
        

    
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

