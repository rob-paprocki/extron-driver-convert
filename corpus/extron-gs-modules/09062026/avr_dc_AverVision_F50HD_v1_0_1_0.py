from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
        self.Models = {
            'AVerVision F50HD': self.avr_16_1553_HD,
            'AVerVision F50-8M': self.avr_16_1553_8M,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Lamp': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mode': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'SplitScreenMode': {'Status': {}},
            'SplitScreenPosition': {'Status': {}},
            'VideoOutput': {'Status': {}},
            'Zoom': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.regex = re.compile(b'(\x53\x00\x02[\x0B|\x03]\x00\x52[\x00-\xFF])|(\x53\x00\x01[\x01|\x02|\x04]\x52[\x00-\xFF])')

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x52\x0B\x03\x36\x01\x00\x53\x6C',
            'Off': b'\x52\x0B\x03\x36\x00\x00\x53\x6D'
        }

        AutoImageCmdString = ValueStateValues[value]
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        if self.Brightness_Min <= value <= self.Brightness_Max:
            checksum = 75 ^ value
            BrightnessCmdString = pack('>8B', 0x52, 0x0B, 0x03, 0x12, 0x02, value, 0x53, checksum)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = b'\x52\x0A\x01\x0A\x53\x52'
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = res[3:4][0]
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        if self.Contrast_Min <= value <= self.Contrast_Max:
            checksum = 72 ^ value
            ContrastCmdString = pack('>8B', 0x52, 0x0B, 0x03, 0x11, 0x02, value, 0x53, checksum)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = b'\x52\x0A\x01\x0B\x53\x53'
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        if res:
            try:
                value = res[3:4][0]
                self.WriteStatus('Contrast', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Contrast: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': b'\x52\x0B\x03\x48\x01\x00\x53\x13',
            'Near': b'\x52\x0B\x03\x48\x00\x00\x53\x12',
            'Auto': b'\x52\x0B\x03\x40\x00\x00\x53\x1B'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'Toggle': b'\x52\x0B\x03\x44\x00\x00\x53\x1F'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        FreezeCmdString = b'\x52\x0A\x01\x08\x53\x50'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetLamp(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x52\x0B\x03\x49\x01\x00\x53\x13',
            'Off': b'\x52\x0B\x03\x49\x00\x00\x53\x12'
        }

        LampCmdString = ValueStateValues[value]
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def UpdateLamp(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        LampCmdString = b'\x52\x0A\x01\x05\x53\x5D'
        res = self.__UpdateHelper('Lamp', LampCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Lamp', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x52\x0B\x03\x42\x01\x00\x53\x18',
            'Down': b'\x52\x0B\x03\x42\x00\x00\x53\x19',
            'Left': b'\x52\x0B\x03\x42\x02\x00\x53\x1B',
            'Right': b'\x52\x0B\x03\x42\x03\x00\x53\x1A',
            'Menu': b'\x52\x0B\x03\x41\x00\x00\x53\x1A',
            'Enter': b'\x52\x0B\x03\x43\x00\x00\x53\x18'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Camera': b'\x52\x0B\x03\x02\x00\x00\x53\x59',
            'Playback': b'\x52\x0B\x03\x03\x00\x00\x53\x58',
            'Pass Through': b'\x52\x0B\x03\x04\x00\x00\x53\x5F'
        }

        ModeCmdString = ValueStateValues[value]
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def UpdateMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Camera',
            b'\x01': 'Playback',
            b'\x02': 'Pass Through'
        }

        ModeCmdString = b'\x52\x0A\x01\x06\x53\x5E'
        res = self.__UpdateHelper('Mode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Mode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mode: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x52\x0B\x03\x1F\x01\x00\x53\x45',
            'Off': b'\x52\x0B\x03\x1F\x00\x00\x53\x44'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': b'\x52\x0B\x03\x20\x01\x00\x53\x7A',
            'Top Right': b'\x52\x0B\x03\x20\x02\x00\x53\x79',
            'Bottom Left': b'\x52\x0B\x03\x20\x00\x00\x53\x7B',
            'Bottom Right': b'\x52\x0B\x03\x20\x03\x00\x53\x78'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x52\x0B\x03\x01\x01\x00\x53\x5B',
            'Off': b'\x52\x0B\x03\x01\x00\x00\x53\x5A'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x52\x0A\x01\x04\x53\x5C'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            if res == b'\x51\xFF\x01\x0A\x51\xA5':
                self.WriteStatus('Power', 'Off', qualifier)
            elif res == b'\x53\x0C\x01\x01\x52\x5E':
                self.WriteStatus('Power', 'On', qualifier)
            else:
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x52\x0B\x03\x33\x00\x00\x53\x68',
            '2': b'\x52\x0B\x03\x33\x01\x00\x53\x69',
            '3': b'\x52\x0B\x03\x33\x02\x00\x53\x6A'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x52\x0B\x03\x32\x00\x00\x53\x69',
            '2': b'\x52\x0B\x03\x32\x01\x00\x53\x68',
            '3': b'\x52\x0B\x03\x32\x02\x00\x53\x6B'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetSplitScreenMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x52\x0B\x03\x21\x01\x00\x53\x7B',
            'Off': b'\x52\x0B\x03\x21\x00\x00\x53\x7A'
        }

        SplitScreenModeCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreenMode', SplitScreenModeCmdString, value, qualifier)

    def SetSplitScreenPosition(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x52\x0B\x03\x22\x00\x00\x53\x79',
            'Down': b'\x52\x0B\x03\x22\x01\x00\x53\x78',
            'Left': b'\x52\x0B\x03\x22\x02\x00\x53\x7B',
            'Right': b'\x52\x0B\x03\x22\x03\x00\x53\x7A'
        }

        SplitScreenPositionCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreenPosition', SplitScreenPositionCmdString, value, qualifier)

    def UpdateVideoOutput(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x01': 'TV'
        }

        VideoOutputCmdString = b'\x52\x0A\x01\x07\x53\x5F'
        res = self.__UpdateHelper('VideoOutput', VideoOutputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('VideoOutput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Output: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x52\x0B\x03\x46\x01\x00\x53\x1C',
            'Down': b'\x52\x0B\x03\x46\x00\x00\x53\x1D',
            'Reset': b'\x52\x0B\x03\x47\x00\x00\x53\x1C'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x03': 'Invalid command.',
            b'\x01': 'Type Fail.',
            b'\x02': 'Checksum Fail.',
            b'\x04': 'Invalid command.'
            }
        if response[3:4] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[3:4]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                return ''
            else:
                return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def avr_16_1553_HD(self):
        self.Brightness_Min = 0
        self.Brightness_Max = 63
        self.Contrast_Min = 0
        self.Contrast_Max = 255

    def avr_16_1553_8M(self):
        self.Brightness_Min = 1
        self.Brightness_Max = 64
        self.Contrast_Min = 1
        self.Contrast_Max = 32
        
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

