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
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PAPMode': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }


    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '*SCIRCC0000000000000061\n'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On'    : '*SCAMUT0000000000000001\n', 
            'Off'   : '*SCAMUT0000000000000000\n'
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        AudioMuteCmdString = '*SEAMUT################\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up'    : '*SCIRCC0000000000000033\n', 
            'Down'  : '*SCIRCC0000000000000034\n'
        }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = '*SCIRCC0000000000000036\n'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        InputState = {
            'TV'                : '*SCINPT0000000000000000\n',
            'Video'             : '*SCINPT0000000300000001\n',
            'Component'         : '*SCINPT0000000400000001\n',
            'HDMI 1'            : '*SCINPT0000000100000001\n',
            'HDMI 2'            : '*SCINPT0000000100000002\n',
            'HDMI 3'            : '*SCINPT0000000100000003\n',
            'HDMI 4'            : '*SCINPT0000000100000004\n',
            'Screen Mirroring'  : '*SCINPT0000000500000001\n'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputState = {
            '0' : 'TV', 
            '3' : 'Video', 
            '4' : 'Component', 
            '1' : 'HDMI',
            '5' : 'Screen Mirroring',             
        }

        InputCmdString = '*SEINPT################\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[14]]
                if value == 'HDMI' and res[-2] == '1':
                    self.WriteStatus('Input', 'HDMI 1', qualifier)
                elif value == 'HDMI' and res[-2] == '2':
                    self.WriteStatus('Input', 'HDMI 2', qualifier)
                elif value == 'HDMI' and res[-2] == '3':
                    self.WriteStatus('Input', 'HDMI 3', qualifier)
                elif value == 'HDMI' and res[-2] == '4':
                    self.WriteStatus('Input', 'HDMI 4', qualifier)
                else:
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

    def SetKeypad(self, value, qualifier):

        KeypadState = {
            '1' : '*SCIRCC0000000000000018\n', 
            '2' : '*SCIRCC0000000000000019\n', 
            '3' : '*SCIRCC0000000000000020\n', 
            '4' : '*SCIRCC0000000000000021\n', 
            '5' : '*SCIRCC0000000000000022\n', 
            '6' : '*SCIRCC0000000000000023\n', 
            '7' : '*SCIRCC0000000000000024\n', 
            '8' : '*SCIRCC0000000000000025\n', 
            '9' : '*SCIRCC0000000000000026\n', 
            '0' : '*SCIRCC0000000000000027\n', 
            'Dot' : '*SCIRCC0000000000000038\n'
        }

        KeypadCmdString = KeypadState[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up'            : '*SCIRCC0000000000000009\n', 
            'Down'          : '*SCIRCC0000000000000010\n', 
            'Left'          : '*SCIRCC0000000000000012\n', 
            'Right'         : '*SCIRCC0000000000000011\n', 
            'Confirm'       : '*SCIRCC0000000000000013\n', 
            'Home'          : '*SCIRCC0000000000000006\n', 
            'Return'        : '*SCIRCC0000000000000008\n', 
            'Top Menu'      : '*SCIRCC0000000000000088\n', 
            'Popup Menu'    : '*SCIRCC0000000000000089\n'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPAPMode(self, value, qualifier):

        PAPModeCmdString = '*SCIRCC0000000000000063\n'
        self.__SetHelper('PAPMode', PAPModeCmdString, value, qualifier)
    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'On'    : '*SCPIPI0000000000000001\n', 
            'Off'   : '*SCPIPI0000000000000000\n'
        }

        PIPModeCmdString = PIPModeState[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
    def UpdatePIPMode(self, value, qualifier):

        PIPModeState = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PIPModeCmdString = '*SEPIPI################\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeState[res[-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode : Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : '*SCPOWR0000000000000001\n', 
            'Off'   : '*SCPOWR0000000000000000\n'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerState = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = '*SEPOWR################\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On'    : '*SCPMUT0000000000000001\n', 
            'Off'   : '*SCPMUT0000000000000000\n'
        }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            '1' : 'On', 
            '0' : 'Off'
        }

        VideoMuteCmdString = '*SEPMUT################\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '*SCVOLU0000000000000' + '{0:03d}'.format(value) + '\n'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '*SEVOLU################\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'FFFFFFFFFFFFFFFF' : 'Invalid Parameter',
            'NNNNNNNNNNNNNNNN' : 'The command does not exist',
        }
        response = response.decode()
        if response[7:-1] in DEVICE_ERROR_CODES:
            self.Error(['{0} ERROR: {1}\r'.format(sourceCmdName, DEVICE_ERROR_CODES[response[7:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n')
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

