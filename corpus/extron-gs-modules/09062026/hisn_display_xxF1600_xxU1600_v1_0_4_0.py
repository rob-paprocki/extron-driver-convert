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
        self._ClientID = b'\x41\x4C\x4C'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AVSettingMenu': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'KeypadLock': { 'Status': {}},
            'MenuControl': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'RemoteLock': { 'Status': {}},
            'StandbyLED': { 'Status': {}},
            'Volume': { 'Status': {}},
        }


    @property
    def ClientID(self):
        return self._ClientID

    @ClientID.setter
    def ClientID(self, value):
        if value == 'Broadcast':
            self._ClientID = b'\x41\x4C\x4C'
        elif len(value) == 3:
            self._ClientID = b''
            for i in value:
                self._ClientID = b''.join([self._ClientID, bytes([ord(i)])])
        else:
            self.Error(['Client ID Out of Range'])
    def AddChecksum(self, commandstring):
        checksum = 0
        for i in commandstring:
            checksum = checksum + i
        checksum = checksum&0xFF
        if checksum == 0: #Check is created for Volume command for when the cks value is 0. Creates an error in the bytes() function
            cks = b'\x00'
        else:
            cks = bytes([256-checksum])
        return b''.join([commandstring, cks, b'\x0D'])
    def SetAspectRatio(self, value, qualifier):

        state = {
            'Auto'              : b'\x30',
            'Normal'            : b'\x32',
            'Zoom'              : b'\x33',
            'Wide'              : b'\x34',
            'Direct'            : b'\x35',
            'Pixel Map (1-to-1)': b'\x36',
            'Panoramic'         : b'\x37',
            'Cinema'            : b'\x38'
        }[value]

        AspectRatioCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x41\x53\x50\x54\x30\x30\x30', state]))
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x41\x53\x50\x54\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0': 'Auto',
                    b'2': 'Normal',
                    b'3': 'Zoom',
                    b'4': 'Wide',
                    b'5': 'Direct',
                    b'6': 'Pixel Map (1-to-1)',
                    b'7': 'Panoramic',
                    b'8': 'Cinema'
                }[res[-2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AspectRatio: Invalid/unexpected response'])

    def SetAVSettingMenu(self, value, qualifier):

        state = {
            'Enable' : b'\x31',
            'Disable': b'\x30'
        }[value]

        AVSettingMenuCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x41\x56\x4D\x4E\x30\x30\x30', state]))
        self.__SetHelper('AVSettingMenu', AVSettingMenuCmdString, value, qualifier)
    def UpdateAVSettingMenu(self, value, qualifier):


        AVSettingMenuCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x41\x56\x4D\x4E\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('AVSettingMenu', AVSettingMenuCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'1' : 'Enable',
                    b'0': 'Disable'
                }[res[-2:-1]]
                self.WriteStatus('AVSettingMenu', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AVSettingMenu: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        state = {
            'Up'   : b'\x33\x34',
            'Down' : b'\x33\x35'
        }[value]

        ChannelStepCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x42\x54\x54\x4E\x31\x30', state]))
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        state = {
            'Off' : b'\x30',
            'On'  : b'\x32',
            'CC (on when mute)': b'\x33'
        }[value]

        ClosedCaptionCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x43\x43\x23\x23\x30\x30\x30', state]))
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x43\x43\x23\x23\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0' : 'Off',
                    b'2' : 'On',
                    b'3' : 'CC (on when mute)'
                }[res[-2:-1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ClosedCaption: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        state = {
            'TV'        : b'\x30\x31',
            'AV'        : b'\x30\x34',
            'Component' : b'\x30\x33',
            'HDMI 1'    : b'\x30\x39',
            'HDMI 2'    : b'\x31\x30',
            'HDMI 3'    : b'\x31\x31',
            'HDMI 4'    : b'\x31\x32',
            'VGA'       : b'\x30\x36'
        }[value]

        InputCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x49\x4E\x50\x54\x30\x30', state]))
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):


        InputCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x49\x4E\x50\x54\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'01' : 'TV',
                    b'04' : 'AV',
                    b'03' : 'Component',
                    b'09' : 'HDMI 1',
                    b'10' : 'HDMI 2',
                    b'11' : 'HDMI 3',
                    b'12' : 'HDMI 4',
                    b'06' : 'VGA'
                }[res[-3:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        state = {
            '0' : b'\x30\x30',
            '1' : b'\x30\x31',
            '2' : b'\x30\x32',
            '3' : b'\x30\x33',
            '4' : b'\x30\x34',
            '5' : b'\x30\x35',
            '6' : b'\x30\x36',
            '7' : b'\x30\x37',
            '8' : b'\x30\x38',
            '9' : b'\x30\x39',
            '-' : b'\x31\x30'
        }[value]

        KeypadCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x42\x54\x54\x4E\x30\x30', state]))
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def SetKeypadLock(self, value, qualifier):

        state = {
            'Enable'  : b'\x30',
            'Disable' : b'\x31'
        }[value]

        KeypadLockCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x50\x41\x4E\x4C\x30\x30\x30', state]))
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
    def UpdateKeypadLock(self, value, qualifier):

        KeypadLockCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x50\x41\x4E\x4C\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0' : 'Enable',
                    b'1' : 'Disable'
                }[res[-2:-1]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['KeypadLock: Invalid/unexpected response'])

    def SetMenuControl(self, value, qualifier):

        state = {
            'Enable'  : b'\x30',
            'Disable' : b'\x31'
        }[value]

        MenuControlCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x4D\x45\x4E\x55\x30\x30\x30', state]))
        self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)
        
    def UpdateMenuControl(self, value, qualifier):

        MenuControlCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x4D\x45\x4E\x55\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('MenuControl', MenuControlCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0' : 'Enable',
                    b'1' : 'Disable'
                }[res[-2:-1]]
                self.WriteStatus('MenuControl', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['MenuControl: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        state = {
            'Menu'  : b'\x33\x38',
            'Up'    : b'\x34\x31',
            'Down'  : b'\x34\x32',
            'Left'  : b'\x34\x33',
            'Right' : b'\x34\x34',
            'Enter' : b'\x34\x30',
            'Back'  : b'\x34\x35',
            'Exit'  : b'\x34\x36'
        }[value]

        MenuNavigationCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x42\x54\x54\x4E\x30\x30', state]))
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetMute(self, value, qualifier):

        state = {
            'On'  : b'\x31',
            'Off' : b'\x30'
        }[value]

        MuteCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x4D\x55\x54\x45\x30\x30\x30', state]))
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        
    def UpdateMute(self, value, qualifier):


        MuteCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x4D\x55\x54\x45\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'1' : 'On',
                    b'0' : 'Off'
                }[res[-2:-1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        state = {
            'Enable'  : b'\x30',
            'Disable' : b'\x31'
        }[value]

        OnScreenDisplayCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x4F\x53\x44\x23\x30\x30\x30', state]))
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        
    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x4F\x53\x44\x23\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0' : 'Enable',
                    b'1' : 'Disable'
                }[res[-2:-1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['OnScreenDisplay: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        state = {
            'Standard'      : b'\x30',
            'Vivid'         : b'\x32',
            'Energy Saving' : b'\x33',
            'Theater'       : b'\x34',
            'Game'          : b'\x35',
            'Sport'         : b'\x36'
        }[value]

        PictureModeCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x50\x4D\x4F\x44\x30\x30\x30', state]))
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        
    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x50\x4D\x4F\x44\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0' : 'Standard',
                    b'2' : 'Vivid',
                    b'3' : 'Energy Saving',
                    b'4' : 'Theater',
                    b'5' : 'Game',
                    b'6' : 'Sport'
                }[res[-2:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PictureMode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        state = {
            'On'  : b'\x31',
            'Off' : b'\x30'
        }[value]

        PowerCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x50\x4F\x57\x52\x30\x30\x30', state]))
        if value == 'Off':
            self.__SetHelper('Power', self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x50\x57\x52\x45\x30\x30\x30\x31'])), value, qualifier)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def SetRemoteLock(self, value, qualifier):

        state = {
            'Enable'  : b'\x30',
            'Disable' : b'\x31',
            'Partial' : b'\x32'
        }[value]

        RemoteLockCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x52\x4D\x4F\x54\x30\x30\x30', state]))
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)
    def UpdateRemoteLock(self, value, qualifier):

        RemoteLockCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x52\x4D\x4F\x54\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('RemoteLock', RemoteLockCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'0' : 'Enable',
                    b'1' : 'Disable',
                    b'2' : 'Partial'
                }[res[-2:-1]]
                self.WriteStatus('RemoteLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['RemoteLock: Invalid/unexpected response'])

    def SetStandbyLED(self, value, qualifier):

        state = {
            'On'  : b'\x32',
            'Off' : b'\x30'
        }[value]

        StandbyLEDCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x50\x4C\x45\x44\x30\x30\x30', state]))
        self.__SetHelper('StandbyLED', StandbyLEDCmdString, value, qualifier)
    def UpdateStandbyLED(self, value, qualifier):

        StandbyLEDCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x50\x4C\x45\x44\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('StandbyLED', StandbyLEDCmdString, value, qualifier)
        if res:
            try:
                value = {
                    b'2' : 'On',
                    b'0' : 'Off'
                }[res[-2:-1]]
                self.WriteStatus('StandbyLED', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Standby LED: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            state = b''
            temp = str(value).zfill(3)
            for i in temp:
                state = b''.join([state, bytes([ord(i)])])
            VolumeCmdString = self.AddChecksum(b''.join([b'\x53', self._ClientID, b'\x56\x4F\x4C\x4D\x30', state]))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
            
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.AddChecksum(b''.join([b'\x51', self._ClientID, b'\x56\x4F\x4C\x4D\x3F\x3F\x3F\x3F']))
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-5:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'ERROR' in response:
            self.Error(['{}: Error'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or self._ClientID == b'\x41\x4C\x4C':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._ClientID == b'\x41\x4C\x4C':
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

