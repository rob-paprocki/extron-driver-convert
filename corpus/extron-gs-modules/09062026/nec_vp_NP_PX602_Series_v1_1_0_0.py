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
            'AspectRatio'       : {'Status': {}},
            'AudioMute'         : {'Status': {}},
            'AutoImage'         : {'Status': {}},
            'DeviceStatus'      : {'Status': {}},
            'FilterUsage'       : {'Status': {}},
            'Focus'             : {'Status': {}},
            'Freeze'            : {'Status': {}},
            'Input'             : {'Status': {}},
            'InputSignalStatus' : {'Status': {}},
            'LampBrightness'    : {'Status': {}},
            'LampMode'          : {'Status': {}},
            'LampUsage'         : {'Status': {}},
            'MenuNavigation'    : {'Status': {}},
            'OnScreenDisplay'   : {'Status': {}},
            'Power'             : {'Status': {}},
            'VideoMute'         : {'Status': {}},
            'Volume'            : {'Status': {}},
            'Zoom'              : {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.regex1 = re.compile(b'([\xA1][\x00-\xFF]{7})|([\x21][\x00-\xFF]{6})')# Freeze
            self.regex2 = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')# Pow, AM, VM
            self.regex3 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')# Vol, Aspect, LMode
            self.regex4 = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')# Input, AI, MN
            self.regex5 = re.compile(b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{17})')# DeviceStatus
            self.regex6 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{13})')# F.Usage
            self.regex7 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')# L.Mode
            self.regex8 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{11})')# L.Usage
            self.regex9 = re.compile(b'([\xA3|\xA0][\x00-\xFF]{7})|([\x20|\x23][\x00-\xFF]{21})')# Power
            self.regex10 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{18})')# Vol status
            

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'    : b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34', 
            '5:4'    : b'\x03\x10\x00\x00\x05\x18\x00\x00\x08\x00\x38', 
            '15:9'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35', 
            '16:9'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32', 
            '16:10'  : b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36', 
            'Auto'   : b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30', 
            'Native' : b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x12\x00\x00\x00\x14', 
            'Off' : b'\x02\x13\x00\x00\x00\x15'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    


    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00\x00\x00' : 'Normal', 
            b'\x01\x00\x00\x00' : 'Cover Error', 
            b'\x02\x00\x00\x00' : 'Temp Error(Bi-metallic strip)', 
            b'\x10\x00\x00\x00' : 'Fan Error', 
            b'\x20\x00\x00\x00' : 'Power Error', 
            b'\x40\x00\x00\x00' : 'Lamp Off', 
            b'\x80\x00\x00\x00' : 'Replace Lamp', 
            b'\x00\x01\x00\x00' : 'Lamp Life Expired', 
            b'\x00\x02\x00\x00' : 'Formatter Error', 
            b'\x00\x00\x02\x00' : 'FPGA Error', 
            b'\x00\x00\x04\x00' : 'Temp Sensor Error', 
            b'\x00\x00\x08\x00' : 'Lamp Not Present', 
            b'\x00\x00\x10\x00' : 'Lamp Data Error', 
            b'\x00\x00\x20\x00' : 'Mirror Cover Error', 
            b'\x00\x00\x00\x04' : 'Temperature Error due to Dust', 
            b'\x00\x00\x00\x10' : 'Foreign Matter Sensor Error', 
            b'\x00\x00\x00\x20' : 'Ballast Communication Error', 
            b'\x00\x00\x00\x40' : 'Iris Callibration Error', 
            b'\x00\x00\x00\x80' : 'Lens not properly installed'
        }
        ExtendedStateValues = {
            0x01 : 'Portrait cover side is up', 
            0x02 : 'Interlock switch is open', 
            0x04 : 'System Error', 
            0x10 : 'System Formatter Error'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if res[13] != 0x00:
                    value = ExtendedStateValues[res[13]]
                else:
                    value = ValueStateValues.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Update Device Status provided an Invalid/unexpected response for UpdateDeviceStatus')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x95\x00\x00\x00\x98'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                FilterHours = ((res[8]<<24) + (res[7]<<16) + (res[6]<<8) + res[5])/3600
                self.WriteStatus('FilterUsage', int(FilterHours), qualifier)
            except (ValueError, IndexError):
                print('Update Filter Usage provided an Invalid/unexpected response for UpdateFilterUsage')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x02\x18\x00\x00\x02\x01\x7F\x9C', 
            'Down' : b'\x02\x18\x00\x00\x02\x01\x81\x9E',
            'Stop' : b'\x02\x18\x00\x00\x02\x01\x00\x1D'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)



    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x01\x98\x00\x00\x01\x01\x9B', 
            'Off' : b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI'        : b'\x02\x03\x00\x00\x02\x01\xA1\xA9', 
            'DisplayPort' : b'\x02\x03\x00\x00\x02\x01\xA6\xAE', 
            'BNC'         : b'\x02\x03\x00\x00\x02\x01\x02\x0A', 
            'BNC(CV)'     : b'\x02\x03\x00\x00\x02\x01\x06\x0E', 
            'BNC(Y/C)'    : b'\x02\x03\x00\x00\x02\x01\x0B\x13', 
            'RGB'         : b'\x02\x03\x00\x00\x02\x01\x01\x09', 
            'HDBaseT'     : b'\x02\x03\x00\x00\x02\x01\x20\x28', 
            'SLOT'        : b'\x02\x03\x00\x00\x02\x01\xAB\xB3'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco' : b'\x03\xB1\x00\x00\x02\x07\x01\xBE', 
            'Off' : b'\x03\xB1\x00\x00\x02\x07\x00\xBD'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'Eco', 
            b'\x00' : 'Off'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6:7]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Update Lamp Mode provided an Invalid/unexpected response for UpdateLampMode')
    
    def SetLampBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 65535
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp = (429 + value) & 255
            LampBrightnessCmdString = b''.join([b'\x03\x10\x00\x00\x05\x96\xFF\x00', pack('<H', value), pack('>B', temp)])
            self.__SetHelper('LampBrightness', LampBrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLampBrightness')
    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = ((res[10]<<24) + (res[9]<<16) + (res[8]<<8) + res[7])/3600
                self.WriteStatus('LampUsage', int(value), qualifier)
            except (ValueError, IndexError):
                print('Update Lamp Usage provided an Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : b'\x02\x0F\x00\x00\x02\x06\x00\x19', 
            'Up'    : b'\x02\x0F\x00\x00\x02\x07\x00\x1A', 
            'Down'  : b'\x02\x0F\x00\x00\x02\x08\x00\x1B', 
            'Left'  : b'\x02\x0F\x00\x00\x02\x0A\x00\x1D', 
            'Right' : b'\x02\x0F\x00\x00\x02\x09\x00\x1C', 
            'Enter' : b'\x02\x0F\x00\x00\x02\x0B\x00\x1E', 
            'Exit'  : b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x14\x00\x00\x00\x16', 
            'Off' : b'\x02\x15\x00\x00\x00\x17'
        }

        OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x00\x00\x00\x00\x02', 
            'Off' : b'\x02\x01\x00\x00\x00\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            0x04 : 'On', 
            0x00 : 'Off',
            0x06 : 'Off',
            0x0F : 'Off',
            0x10 : 'Off',
            0x05 : 'Cooling Down'
            
        }
        InputSignalStatusValues = {
            0x00 : 'Video Signal', 
            0x04 : 'LAN', 
            0x05 : 'Test Pattern(User)', 
            0x03 : 'Viewer', 
            0x02 : 'Test Pattern', 
            0x10 : 'Signal being switched', 
            0x01 : 'No Signal'
        }
        InputStateValues = {
            0x21 : 'HDMI', 
            0x22 : 'DisplayPort', 
            0x01 : 'RGB', 
            0x05 : 'Reserved', 
            0xFF : 'Not Source Input'
        }
        OtherStateValues = {
            0x01 : 'On', 
            0x00 : 'Off'
        }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerStateValues[res[6]]
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                print('Update Power provided an Invalid/unexpected response for UpdatePower')
                
            try:
                InputSignalStatusValue = InputSignalStatusValues[res[7]]
                self.WriteStatus('InputSignalStatus', InputSignalStatusValue, qualifier)
            except (KeyError, IndexError):
                print('Update Input Signal Status provided an Invalid/unexpected response')
                
            try:
                InputValue = InputStateValues[res[8]]
                self.WriteStatus('Input', InputValue, qualifier)
            except (KeyError, IndexError):
                print('Update Input provided an Invalid/unexpected response')
                
            try:
                VideoMuteValue = OtherStateValues[res[11]]
                self.WriteStatus('VideoMute', VideoMuteValue, qualifier)
            except (KeyError, IndexError):
                print('Update Video Mute provided an Invalid/unexpected response')
                
            try:
                AudioMuteValue = OtherStateValues[res[12]]
                self.WriteStatus('AudioMute', AudioMuteValue, qualifier)
            except (KeyError, IndexError):
                print('Update Audio Mute provided an Invalid/unexpected response')
                
            try:
                OSDValue = OtherStateValues[res[13]]
                self.WriteStatus('OnScreenDisplay', OSDValue, qualifier)
            except (KeyError, IndexError):
                print('Update On Screen Display provided an Invalid/unexpected response')
                
            try:
                FreezeValue = OtherStateValues[res[14]]
                self.WriteStatus('Freeze', FreezeValue, qualifier)
            except (KeyError, IndexError):
                print('Update Freeze provided an Invalid/unexpected response')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x10\x00\x00\x00\x12', 
            'Off' : b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 31
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Checksum = 0x1D + value
            VolumeCmdString = pack('>11B', 0x03, 0x10, 0x00, 0x00, 0x05, 0x05, 0x00, 0x00, value, 0x00, Checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 31
            }
        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[12]
                self.WriteStatus('Volume', value, qualifier)
            except IndexError:
                print('Update Volume has provided an Invalid/unexpected response for UpdateVolume')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x02\x18\x00\x00\x02\x00\x7F\x9B', 
            'Down' : b'\x02\x18\x00\x00\x02\x00\x81\x9D',
            'Stop' : b'\x02\x18\x00\x00\x02\x00\x00\x1C'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00' : 'Command not recognized.',
            b'\x00\x01' : 'Unsupported Command.',
            b'\x01\x00' : 'Invalid values specificed.',
            b'\x01\x01' : 'Specified input terminal is invalid.',
            b'\x01\x02' : 'Selected language is invalid.',
            b'\x02\x00' : 'Memory allocation error.',
            b'\x02\x02' : 'Memory in use.',
            b'\x02\x03' : 'Specified value cannot be set.',
            b'\x02\x04' : 'Forced onscreen mute on.',
            b'\x02\x06' : 'Viewer Error.',
            b'\x02\x07' : 'No Signal.',
            b'\x02\x08' : 'Displaying a test pattern or Filer.',
            b'\x02\x09' : 'No PC Card is inserted.',
            b'\x02\x0A' : 'Memory Operation Failed.',
            b'\x02\x0C' : 'An entry list is Displayed.',
            b'\x02\x0D' : 'Command cannot be accepted because Power is Off.',
            b'\x02\x0E' : 'Command Execution Failed.',
            b'\x02\x0F' : 'No authority neccessary for the operation .',
            b'\x03\x00' : 'Specified gain number is incorrect.',
            b'\x03\x01' : 'Specified gain is invalid.',
            b'\x03\x02' : 'Adjustment failed.'
            }   
        if response[0] in [ 0xA3, 0xA2, 0xA1, 0xA0]:
            if response[5:7] in DEVICE_ERROR_CODES:
                errorString = ''.join([sourceCmdName, ', Error : ', DEVICE_ERROR_CODES[response[5:7]]])
                print(errorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command == 'Freeze':
                regex = self.regex1
            elif command in ['Power', 'AudioMute', 'VideoMute'] :
                regex = self.regex2
            elif command in ['Volume', 'AspectRatio', 'LampMode']:
                regex = self.regex3
            else:
                regex = self.regex4
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                print('Setting {} command does not provide any response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if command == 'DeviceStatus' :
            regex = self.regex5
        elif command == 'FilterUsage':
            regex = self.regex6
        elif command == 'LampMode':
            regex = self.regex7
        elif command == 'LampUsage':
            regex = self.regex8
        elif command == 'Volume':
            regex = self.regex10
        else:
            regex = self.regex9
        
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
