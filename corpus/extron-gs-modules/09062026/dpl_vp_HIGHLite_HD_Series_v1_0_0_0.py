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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.regex1 = re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{5}$)')
            self.regex2 = re.compile(b'(^[\xA2][\x00-\xFF]{7}$)|(^[\x22][\x00-\xFF]{6}$)')
            self.regex3 = re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{133}$)')
            self.regex4 = re.compile(b'(^[\xA0][\x00-\xFF]{7}$)|(^[\x20][\x00-\xFF]{17}$)')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x1A\x00\x00\x02\x01\x01\x20',
            'Off': b'\x02\x1A\x00\x00\x02\x01\x00\x1F'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00\x00': 'Normal',
            b'\x01\x00\x00': 'Cover Not Closed',
            b'\x02\x00\x00': 'Temperature Error',
            b'\x10\x00\x00': 'Fan Stop',
            b'\x20\x00\x00': 'Power Abnormal',
            b'\x40\x00\x00': 'Lamp Failure',
            b'\x80\x00\x00': 'Lamp Life Expired',
            b'\x00\x01\x00': 'Lamp Beyond Limit',
            b'\x00\x00\x02': 'FPGA Error',
            b'\x00\x00\x04': 'Temp Sensor Failure',
            b'\x00\x00\x08': 'No Lamp',
            b'\x00\x00\x10': 'Lamp Data Error'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues.get(res[5:8], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateDeviceStatus')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02\x0F\x00\x00\x02\x14\x00\x27',
            'Down': b'\x02\x0F\x00\x00\x02\x15\x00\x28',
            'Stop': b'\x02\x18\x00\x00\x02\x01\x00\x1D'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x02\x0F\x00\x00\x02\x8A\x00\x9D'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Slot1-1': b'\x02\x03\x00\x00\x02\x01\x24\x2C',
            'Slot1-2': b'\x02\x03\x00\x00\x02\x01\x25\x2D',
            'Slot1-3': b'\x02\x03\x00\x00\x02\x01\x26\x2E',
            'Slot1-4': b'\x02\x03\x00\x00\x02\x01\x27\x2F',
            'Slot1-5': b'\x02\x03\x00\x00\x02\x01\x28\x30',
            'Slot2-1': b'\x02\x03\x00\x00\x02\x01\x29\x31',
            'Slot2-2': b'\x02\x03\x00\x00\x02\x01\x2A\x32',
            'Slot2-3': b'\x02\x03\x00\x00\x02\x01\x2B\x33',
            'Slot2-4': b'\x02\x03\x00\x00\x02\x01\x2C\x34',
            'Slot2-5': b'\x02\x03\x00\x00\x02\x01\x2D\x35',
            'Slot3-1': b'\x02\x03\x00\x00\x02\x01\x2E\x36',
            'Slot3-2': b'\x02\x03\x00\x00\x02\x01\x2F\x37',
            'Slot3-3': b'\x02\x03\x00\x00\x02\x01\x30\x38',
            'Slot3-4': b'\x02\x03\x00\x00\x02\x01\x31\x39',
            'Slot3-5': b'\x02\x03\x00\x00\x02\x01\x32\x3A',
            'Slot4-1': b'\x02\x03\x00\x00\x02\x01\x33\x3B',
            'Slot4-2': b'\x02\x03\x00\x00\x02\x01\x34\x3C',
            'Slot4-3': b'\x02\x03\x00\x00\x02\x01\x35\x3D',
            'Slot4-4': b'\x02\x03\x00\x00\x02\x01\x36\x3E',
            'Slot4-5': b'\x02\x03\x00\x00\x02\x01\x37\x3F'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19',
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Cancel': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x14\x00\x00\x00\x16',
            'Off': b'\x02\x15\x00\x00\x00\x17'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            b'\x04': 'On',
            b'\x00': 'Off',
            b'\x06': 'Off',
            b'\x05': 'Cooling Down',

        }
        InputStateValues = {
            b'\x01\x08': 'Slot1-1',
            b'\x02\x08': 'Slot1-2',
            b'\x03\x08': 'Slot1-3',
            b'\x01\x09': 'Slot2-1',
            b'\x02\x09': 'Slot2-2',
            b'\x03\x09': 'Slot2-3',
            b'\x01\x0A': 'Slot3-1',
            b'\x02\x0A': 'Slot3-2',
            b'\x03\x0A': 'Slot3-3',
            b'\x01\x0B': 'Slot4-1',
            b'\x02\x0B': 'Slot4-2',
            b'\x03\x0B': 'Slot4-3'
        }
        OtherStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\x00\xC0\x00\x00\x00\xC0'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                InputStatValue = InputStateValues[res[11:13]]
                VideoMuteValue = OtherStateValues[res[33:34]]
                AudioMuteValue = OtherStateValues[res[34:35]]
                OSDStatesValue = OtherStateValues[res[71:72]]
                PowerStatValue = PowerStateValues[res[73:74]]

                self.WriteStatus('Input', InputStatValue, qualifier)
                self.WriteStatus('VideoMute', VideoMuteValue, qualifier)
                self.WriteStatus('AudioMute', AudioMuteValue, qualifier)
                self.WriteStatus('OnScreenDisplay', OSDStatesValue, qualifier)
                self.WriteStatus('Power', PowerStatValue, qualifier)

            except (KeyError, IndexError):
                print('Invalid response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x02\x0F\x00\x00\x02\x16\x00\x29',
            'Down': b'\x02\x0F\x00\x00\x02\x17\x00\x2A',
            'Stop': b'\x02\x18\x00\x00\x02\x00\x00\x1C'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': 'Unknown command.',
            b'\x00\x01': 'Unsupported Command.',
            b'\x01\x00': 'Invalid values specificed.',
            b'\x01\x01': 'Specified terminal is unavailable or cannot be selected.',
            b'\x01\x02': 'Selected language is not available.',
            b'\x01\x03': 'Specified terminal is not installed.',
            b'\x02\x00': 'Available memory reservation error.',
            b'\x02\x02': 'Operating memory.',
            b'\x02\x03': 'Setting not possible.',
            b'\x02\x04': 'On Forced on-screen mute mode.',
            b'\x02\x06': 'Displaying signal other than PC Viewer.',
            b'\x02\x07': 'No Signal.',
            b'\x02\x08': 'Displaying a test pattern or PC Card Fills screen.',
            b'\x02\x0A': 'Memory Operation Failed.',
            b'\x02\x0C': 'Displaying the entry list.',
            b'\x02\x0D': 'Power Off inhibited.',
            b'\x02\x0E': 'Execution error.',
            b'\x02\x0F': 'No operation authority.',
            b'\x03\x00': 'Specified gain number is wrong.',
            b'\x03\x01': 'Specified gain not available.',
            b'\x03\x02': 'Adjustment failed.'
            }
        if response[0] in [0xA2, 0xA0]:
            if response[5:7] in DEVICE_ERROR_CODES:
                errorString = sourceCmdName + ' Error : ' + DEVICE_ERROR_CODES[response[5:7]]
                print(errorString)
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command in ['Power', 'OnScreenDisplay', 'VideoMute']:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex1)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex2)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

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

            if command == 'Power':
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex3)
            if command == 'DeviceStatus':
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex4)

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
