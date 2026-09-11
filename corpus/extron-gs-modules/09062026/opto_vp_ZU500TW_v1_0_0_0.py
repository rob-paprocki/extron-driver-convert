from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LaserMode': {'Status': {}},
            'LaserUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{0:02d}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3': '1',
            '16:9': '2',
            '16:10': '3',
            'Auto': '7'
            }

        AspectRatioCmdString = '~{0}60 {1}\r'.format(self.DeviceID, AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '1': '4:3',
            '2': '16:9',
            '3': '16:10',
            '7': 'Auto'
            }

        AspectRatioCmdString = '~{0}127 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': '1',
            'Off': '0'
            }

        AudioMuteCmdString = '~{0}80 {1}\r'.format(self.DeviceID, AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            '1': 'On',
            '0': 'Off'
            }

        AudioMuteCmdString = '~{0}356 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~{0}01\r'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        AVMuteState = {
            'On': '1',
            'Off': '0'
            }

        AVMuteCmdString = '~{0}02 {1}\r'.format(self.DeviceID, AVMuteState[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteState = {
            '1': 'On',
            '0': 'Off'
            }

        AVMuteCmdString = '~{0}355 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = AVMuteState[res[2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4',
            'Off': '0'
            }

        ClosedCaptionCmdString = '~{0}88 {1}\r'.format(self.DeviceID, ClosedCaptionState[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            '1': 'CC1',
            '2': 'CC2',
            '3': 'CC3',
            '4': 'CC4',
            '0': 'Off'
            }

        ClosedCaptionCmdString = '~{0}354 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionState[res[2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': '1',
            'Off': '0'
            }

        FreezeCmdString = '~{0}04 {1}\r'.format(self.DeviceID, FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': '5',
            'HDMI 1': '1',
            'HDMI 2': '15',
            'HDBaseT': '21',  # based on opto_1_8932.pke
            'Network': '18',  # based on opto_1_8931.pke
            'USB Display': '19'  # based on opto_1_8931.pke
            }

        InputCmdString = '~{0}12 {1}\r'.format(self.DeviceID, InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetKeypad(self, value, qualifier):

        KeypadState = {
            '1': '51',
            '2': '52',
            '3': '53',
            '4': '54',
            '5': '55',
            '6': '56',
            '7': '57',
            '8': '58',
            '9': '59',
            '0': '60'
            }

        KeypadCmdString = '~{0}140 {1}\r'.format(self.DeviceID, KeypadState[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetLaserMode(self, value, qualifier):

        LaserModeState = {
            'Normal': '1',
            'Eco': '2'
            }

        LaserModeCmdString = '~{0}110 {1}\r'.format(self.DeviceID, LaserModeState[value])
        self.__SetHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def UpdateLaserMode(self, value, qualifier):

        LaserModeState = {
            '1': 'Normal',
            '2': 'Eco'
            }

        LaserModeCmdString = '~{0}150 15\r'.format(self.DeviceID)
        res = self.__UpdateHelper('LaserMode', LaserModeCmdString, value, qualifier)
        if res:
            try:
                value = LaserModeState[res[2]]
                self.WriteStatus('LaserMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Laser Mode: Invalid/unexpected response'])

    
    def UpdateLaserUsage(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': '10',
            'Down': '14',
            'Left': '11',
            'Right': '13',
            'Menu': '20',
            'Enter': '12',
            'Exit': '74'
            }

        MenuNavigationCmdString = '~{0}140 {1}\r'.format(self.DeviceID, MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': '1',
            'Off': '0'
            }

        PowerCmdString = '~{0}00 {1}\r'.format(self.DeviceID, PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):  # page 8 of the protocol manual

        PowerState = {
            '1': 'On',
            '0': 'Off'
            }

        InputState = {
            '05': 'VGA',
            '01': 'HDMI 1',
            '15': 'HDMI 2',
            '21': 'HDBaseT',
            '18': 'Network',
            '19': 'USB Display'
            }

        PowerCmdString = '~{0}150 1\r'.format(self.DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)  # Response:  Okabbbbbccddddee\r
        if res:
            try:
                PowerValue = PowerState[res[2]]
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

            try:
                LaserValue = int(res[3:8])
                self.WriteStatus('LaserUsage', LaserValue, qualifier)
            except (ValueError, IndexError):
                self.Error(['Laser Usage: Invalid/unexpected response'])

            try:
                InputValue = InputState[res[8:10]]
                self.WriteStatus('Input', InputValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 15
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '~{0}81 {1}\r'.format(self.DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == 'F':
            self.Error(['{0}: Failed to execute command.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self.DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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

