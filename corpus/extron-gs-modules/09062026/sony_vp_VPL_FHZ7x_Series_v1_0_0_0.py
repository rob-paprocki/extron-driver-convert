from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import json
import hashlib
import binascii

class DeviceClass:
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.devicePassword = 'Projector'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampHours': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LensControl': { 'Status': {}},
            'LensShift': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MultiScreen': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

        self.lastLampHourUpdate = 0
        self.sha256hash = ''
        self.__is_authenticated = True
        if self.ConnectionType == 'Tcp':
            self.__is_authenticated = False
            self.AddMatchString(re.compile(b'([a-z0-9]{8})\r\n'), self.__MatchAuthentication, True)
            self.AddMatchString(re.compile(b'NOKEY\r\n|OK\r\n'), self.__MatchAuthentication, False)

    def SetAuthentication(self, value, qualifier):
        self.Send(self.sha256hash + '\r\n')

    def __MatchAuthentication(self, match, tag):
        if not tag:
            self.__is_authenticated = True
        else:
            rand_num = match.group(1).decode()
            full_str = rand_num + self.devicePassword
            code_hash = hashlib.sha256(full_str.encode())
            self.sha256hash = binascii.hexlify(code_hash.digest()).decode()
            self.SetAuthentication( None, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':      '"4_3"',
            '16:9':     '"16_9"',
            'Full 1':   '"full1"',
            'Full 2':   '"full2"',
            'Normal':   '"normal"',
            'Full':     '"full"',
            'Zoom':     '"zoom"'
        }

        AspectRatioCmdString = 'aspect {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '"4_3"':    '4:3',
            '"16_9"':   '16:9',
            '"full1"':  'Full 1',
            '"full2"':  'Full 2',
            '"normal"': 'Normal',
            '"full"':   'Full',
            '"zoom"':   'Zoom'
        }
        AspectRatioCmdString = 'aspect ?\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '"on"',
            'Off':  '"off"'
        }

        AudioMuteCmdString = 'muting {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '"on"':     'On',
            '"off"':    'Off'
        }
        AudioMuteCmdString = 'muting ?\r\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'apa_exec\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off':      '"off"',
            'CC1':      '"cc1"',
            'CC2':      '"cc2"',
            'CC3':      '"cc3"',
            'CC4':      '"cc4"',
            'Text1':    '"text1"',
            'Text2':    '"text2"',
            'Text3':    '"text3"',
            'Text4':    '"text4"'
        }

        ClosedCaptionCmdString = 'cc_display {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            '"off"':    'Off',
            '"cc1"':    'CC1',
            '"cc2"':    'CC2',
            '"cc3"':    'CC3',
            '"cc4"':    'CC4',
            '"text1"': 'Text1',
            '"text2"': 'Text2',
            '"text3"': 'Text3',
            '"text4"': 'Text4'
        }
        ClosedCaptionCmdString = 'cc_display ?\r\n'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            'no_err':           'No Error',
            'err_power':        'Power Supply Error',
            'err_power2':       'Power Supply (D5V) Error',
            'err_system2':      'System Error 2',
            'err_cover':        'Cover Error',
            'err_light_src':    'Light-source Error',
            'err_shock':        'Shock Error',
            'err_nolens':       'Lens Not Attached Error',
            'err_attitude':     'Installation Angle Error',
            'err_temp':         'Temperature Error',
            'err_fan':          'Fan Error',
            'err_wheel':        'Wheel Rotation Error',
            'err_light_over':   'Luminance Error',
            'err_assy':         'Assembling Error',
            'err_lens_shift':   'Lens Shift Error'
        }
        DeviceStatusCmdString = 'error ?\r\n'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = json.loads(res)
                deviceStatusValue = ValueStateValues[value[0]]
                self.WriteStatus('DeviceStatus', deviceStatusValue, qualifier)
            except (KeyError, IndexError, TypeError, json.decoder.JSONDecodeError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':  '"off"',
            'On':   '"on"'
        }

        ExecutiveModeCmdString = 'controlkey_lock {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '"off"':    'Off',
            '"on"':     'On'
        }
        ExecutiveModeCmdString = 'controlkey_lock ?\r\n'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':      '_far',
            'Near':     '_near',
            'Focus':    ''
        }

        FocusCmdString = 'key "lens_focus{0}"\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   '"on"',
            'Off':  '"off"'
        }

        FreezeCmdString = 'freeze {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '"on"':     'On',
            '"off"':    'Off'
        }
        FreezeCmdString = 'freeze ?\r\n'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video':    '"video1"',
            'RGB':      '"rgb1"',
            'DVI':      '"dvi1"',
            'HDMI':     '"hdmi1"',
            'HDBaseT':  '"hdbaset1"'
        }

        InputCmdString = 'input {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '"video1"':     'Video',
            '"rgb1"':       'RGB',
            '"dvi1"':       'DVI',
            '"hdmi1"':      'HDMI',
            '"hdbaset1"':   'HDBaseT'
        }
        InputCmdString = 'input ?\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampHours(self, value, qualifier):
        
        LampHoursCmdString = 'timer ?\r\n'
        res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        if res:
            try:
                value = json.loads(res)
                lampValue = value[1]['light_src']
                self.WriteStatus('LampHours', lampValue, qualifier)
            except (KeyError, IndexError, ValueError, TypeError):
                self.Error(['Lamp Hours: Invalid/unexpected response'])

            try:
                operationValue = value[0]['operation']
                self.WriteStatus('OperationHours', operationValue, qualifier)
            except (KeyError, IndexError, ValueError, NameError, TypeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '"high"',
            'Middle':   '"mid"',
            'Custom':   '"custom"',
            'Extended': '"extended"'
        }

        LampModeCmdString = 'light_output_mode {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '"high"':       'Standard',
            '"mid"':        'Middle',
            '"custom"':     'Custom',
            '"extended"':   'Extended'
        }
        LampModeCmdString = 'light_output_mode ?\r\n'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def SetLensControl(self, value, qualifier):

        ValueStateValues = {
            'On':   '"on"',
            'Off':  '"off"'
        }

        LensControlCmdString = 'lens_lock {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('LensControl', LensControlCmdString, value, qualifier)

    def UpdateLensControl(self, value, qualifier):

        ValueStateValues = {
            '"on"':     'On',
            '"off"':    'Off'
        }
        LensControlCmdString = 'lens_lock ?\r\n'
        res = self.__UpdateHelper('LensControl', LensControlCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('LensControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lens Control: Invalid/unexpected response'])

    def SetLensShift(self, value, qualifier):

        ValueStateValues = {
            'Up':       '_up',
            'Down':     '_down',
            'Left':     '_left',
            'Right':    '_right',
            'Shift':    ''
        }

        LensShiftCmdString = 'key "lens_shift{0}"\r\n'.format(ValueStateValues[value])
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu':     '"menu"',
            'Up':       '"up"',
            'Down':     '"down"',
            'Right':    '"right"',
            'Left':     '"left"',
            'Enter':    '"enter"',
            'Return':   '"return"'
        }

        MenuNavigationCmdString = 'key {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetMultiScreen(self, value, qualifier):

        ValueStateValues = {
            'On':   '"on"',
            'Off':  '"off"'
        }

        MultiScreenCmdString = 'multi_screen {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MultiScreen', MultiScreenCmdString, value, qualifier)

    def UpdateMultiScreen(self, value, qualifier):

        ValueStateValues = {
            '"on"':     'On',
            '"off"':    'Off'
        }
        MultiScreenCmdString = 'multi_screen ?\r\n'
        res = self.__UpdateHelper('MultiScreen', MultiScreenCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('MultiScreen', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Multi Screen: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        self.UpdateLampHours(value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic':              '"dynamic"',
            'Standard':             '"standard"',
            'Brightness Priority':  '"brt_priority"',
            'Multi Screen':         '"multi_screen"'
        }

        PictureModeCmdString = 'picture_mode {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            '"dynamic"':        'Dynamic',
            '"standard"':       'Standard',
            '"brt_priority"':   'Brightness Priority',
            '"multi_screen"':   'Multi Screen'
        }
        PictureModeCmdString = 'picture_mode ?\r\n'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '"on"',
            'Off':  '"off"'
        }

        PowerCmdString = 'power {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier if value == 'On' else 0)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '"on"':                 'On',
            '"startup"':            'Startup',
            '"cooling1"':           'Cooling 1',
            '"cooling2"':           'Cooling 2',
            '"saving_cooling1"':    'Power Saving Cooling 1',
            '"saving_cooling2"':    'Power Saving Cooling 2',
            '"saving_standby"':     'Power Saving Standby',
            '"standby"':            'Off'
        }
        PowerCmdString = 'power_status ?\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

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
            except ValueError:
                self.Error(['Volume: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Up':   '_up',
            'Down': '_down',
            'Zoom': ''
        }

        ZoomCmdString = 'key "lens_zoom{0}"\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            '"err_cmd"\r\n':        'Command format error.',
            '"err_option"\r\n':     'Command option error.',
            '"err_inactive"\r\n':   'Invalid error.',
            '"err_val"\r\n':        'Command value error.',
            '"err_auth"\r\n':       'Network authentication error.',
            '"err_internal1"\r\n':  'Internal communication error 1 of the projector.',
            '"err_internal2"\r\n':  'Internal communication error 2 of the projector.'
        }
        if response and response.lower() in error_map:
            self.Error(['An error occurred: {}: {}'.format(sourceCmdName, error_map[response.lower()])])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            if self.__is_authenticated:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
            else:
                self.Discard('Invalid Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.__is_authenticated:
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
        else:
            self.Discard('Inappropriate Command ' + command)           

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.sha256hash = ''
        self.lastLampHourUpdate = 0

        if self.ConnectionType == 'Tcp':
            self.__is_authenticated = False
        else:
            self.__is_authenticated = True

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)
    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 
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

