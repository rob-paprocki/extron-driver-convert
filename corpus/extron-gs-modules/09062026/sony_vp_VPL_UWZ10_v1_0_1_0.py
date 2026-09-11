from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import json


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
            'ClosedCaption': {'Status': {}},
            'ControlKeyLock': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3': '"4_3"',
            '16:9': '"16_9"',
            'Full': '"full"',
            'Zoom': '"zoom"'
            }

        AspectRatioCmdString = 'aspect {0}\r\n'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '"4_3"': '4:3',
            '"16_9"': '16:9',
            '"full"': 'Full',
            '"zoom"': 'Zoom'
            }

        AspectRatioCmdString = 'aspect ?\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[:-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': '"on"',
            'Off': '"off"'
            }

        AudioMuteCmdString = 'muting {0}\r\n'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            '"on"': 'On',
            '"off"': 'Off'
            }

        AudioMuteCmdString = 'muting ?\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[:-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'CC1': '"cc1"',
            'CC2': '"cc2"',
            'CC3': '"cc3"',
            'CC4': '"cc4"',
            'Text 1': '"text1"',
            'Text 2': '"text2"',
            'Text 3': '"text3"',
            'Text 4': '"text4"',
            'Off': '"off"'
            }

        ClosedCaptionCmdString = 'cc_display {0}\r\n'.format(ClosedCaptionState[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            '"cc1"': 'CC1',
            '"cc2"': 'CC2',
            '"cc3"': 'CC3',
            '"cc4"': 'CC4',
            '"text1"': 'Text 1',
            '"text2"': 'Text 2',
            '"text3"': 'Text 3',
            '"text4"': 'Text 4',
            '"off"': 'Off'
            }

        ClosedCaptionCmdString = 'cc_display ?\r\n'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionState[res[:-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption : Invalid/Unexpected Response'])

    def SetControlKeyLock(self, value, qualifier):

        ControlKeyLockState = {
            'On': '"on"',
            'Off': '"off"'
            }

        ControlKeyLockCmdString = 'controlkey_lock {0}\r\n'.format(ControlKeyLockState[value])
        self.__SetHelper('ControlKeyLock', ControlKeyLockCmdString, value, qualifier)

    def UpdateControlKeyLock(self, value, qualifier):

        ControlKeyLockState = {
            '"on"': 'On',
            '"off"': 'Off'
            }

        ControlKeyLockCmdString = 'controlkey_lock ?\r\n'
        res = self.__UpdateHelper('ControlKeyLock', ControlKeyLockCmdString, value, qualifier)
        if res:
            try:
                value = ControlKeyLockState[res[:-2]]
                self.WriteStatus('ControlKeyLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Control Key Lock : Invalid/Unexpected Response'])

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusState = {
            '["no_err"]': 'No Error',
            '["err_power"]': 'Power Supply Error',
            '["err_power2"]': 'Power Supply DV5 Error',
            '["err_system2"]': 'System error',
            '["err_cover"]': 'Cover error',
            '["err_light_src"]': 'Light-source error',
            '["err_lens_cover"]': 'Lens cover error',
            '["err_shock"]': 'Shock error',
            '["err_nolens"]': 'Lens not attached error',
            '["err_attitude"]': 'Installation angle error',
            '["err_temp"]': 'Temperature error',
            '["err_fan"]': 'Fan error',
            '["err_wheel"]': 'Wheel rotation error',
            '["err_light_over"]': 'Luminance error',
            '["err_assy"]': 'Assembling error',
            '["err_lens_shift"]': 'Lens shift error',
            '["err_shutter"]': 'Shutter error'
            }

        DeviceStatusCmdString = 'error ?\r\n'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusState[res[:-2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status : Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'RGB 1': '"rgb1"',
            'RGB 2': '"rgb2"',
            'Video': '"video1"',
            'S-Video': '"svideo1"',
            'USB-B': '"usb_b"',
            'HDMI 1': '"hdmi1"',
            'HDMI 2': '"hdmi2"',
            'LAN': '"network"'
            }

        InputCmdString = 'input {0}\r\n'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '"rgb1"': 'RGB 1',
            '"rgb2"': 'RGB 2',
            '"video1"': 'Video',
            '"svideo1"': 'S-Video',
            '"usb_b"': 'USB-B',
            '"hdmi1"': 'HDMI 1',
            '"hdmi2"': 'HDMI 2',
            '"network"': 'LAN'
            }

        InputCmdString = 'input ?\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[:-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'High': '"high"',
            'Mid': '"mid"',
            'Low': '"low"',
            'Auto': '"auto"'
            }

        LampModeCmdString = 'light_output_mode {0}\r\n'.format(LampModeState[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            '"high"': 'High',
            '"mid"': 'Mid',
            '"low"': 'Low',
            '"auto"': 'Auto'
            }

        LampModeCmdString = 'light_output_mode ?\r\n'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[res[:-2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode : Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'timer ?\r\n'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = json.loads(res)
                lampValue = value[0]['light_src']
                self.WriteStatus('LampUsage', lampValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Lamp Usage : Invalid/Unexpected Response'])

            try:
                value = json.loads(res)
                operationValue = value[1]['operation']
                self.WriteStatus('OperationHours', operationValue, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Operation Hours : Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': '"up"',
            'Down': '"down"',
            'Left': '"left"',
            'Right': '"right"',
            'Enter': '"enter"',
            'Menu': '"menu"',
            'Return': '"return"'
            }

        MenuNavigationCmdString = 'key {0}\r\n'.format(MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        self.UpdateLampUsage(value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '"on"',
            'Off': '"off"',
            }

        PowerCmdString = 'power {0}\r\n'.format(PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '"on"': 'On',
            '"standby"': 'Off',
            '"startup"': 'Warming Up',
            '"cooling1"': 'Cooling Down',
            '"cooling2"': 'Cooling Down',
            '"saving_cooling1"': 'Power Saving Cooling',
            '"saving_cooling2"': 'Power Saving Cooling',
            '"saving_standby"': 'Power Saving Standby'
            }

        PowerCmdString = 'power_status ?\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '"on"',
            'Off': '"off"'
            }

        VideoMuteCmdString = 'blank {0}\r\n'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            '"on"': 'On',
            '"off"': 'Off'
            }

        VideoMuteCmdString = 'blank ?\r\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[:-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'volume {0}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'volume ?\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '"err_cmd"\r\n': 'Command format error',
            '"err_option"\r\n': 'Command option error',
            '"err_inactive"\r\n': 'Invalid error',
            '"err_val"\r\n': 'Command value error',
            '"err_auth"\r\n': 'Network authentication error',
            '"err_internal1\r\n': 'Internal communication error 1 of the projector',
            '"err_internal2\r\n': 'Internal communication error 2 of the projector'
            }
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}\r'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Even', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()