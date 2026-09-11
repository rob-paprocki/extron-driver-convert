from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceSerialClass:

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
            'ChannelStep': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.UpdateDelim = {
            'AudioMute': b'(^\x70[\x00-\x04]\x03\x01[\x01\x00][\x00-\xFF]$)',
            'Input': b'(^\x70[\x00-\x04](\x02\x01|\x03[\x02\x03]\x01|\x03\x04[\x01\x02\x03\x04])[\x00-\xFF]$)',
            'Power': b'(^\x70[\x00-\x04]\x02[\x01\x00][\x00-\xFF]$)',
            'Volume': b'(^\x70[\x00-\x04]\x03\x01[\x00-\xFF]{2}$)'
        }

        self.CompiledRegex = {k: re.compile(v) for k, v in self.UpdateDelim.items()}

    def AddChecksum(self, commandstring):

        checksum = 0
        for i in commandstring:
            checksum = checksum + i
        cks = checksum & 0xFF
        return b''.join([commandstring, bytes([cks])])

    def SetAspectRatio(self, value, qualifier):

        state = {'Wide Zoom': b'\x00', 'Full': b'\x01', 'Zoom': b'\x02', 'Normal': b'\x03'}[value]
        AspectRatioCmdString = b'\x44\x03\x01'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier, state)

    def SetAudioMute(self, value, qualifier):

        state = {'On': b'\x01', 'Off': b'\x00'}[value]
        AudioMuteCmdString = b'\x06\x03\x01'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier, state)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x06'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = {1: 'On', 0: 'Off'}[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AudioMute: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        state = {'Up': b'\x10', 'Down': b'\x11'}[value]
        ChannelStepCmdString = b'\x67\x03\x01'
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier, state)

    def SetInput(self, value, qualifier):

        state = {'TV': b'\x02\x01',
                 'Video 1': b'\x03\x02\x01',
                 'Video 2/Component': b'\x03\x03\x01',
                 'HDMI 1': b'\x03\x04\x01',
                 'HDMI 2': b'\x03\x04\x02',
                 'HDMI 3/ARC': b'\x03\x04\x03',
                 'HDMI 4': b'\x03\x04\x04'}[value]
        InputCmdString = b'\x02'
        self.__SetHelper('Input', InputCmdString, value, qualifier, state)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x02'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = {b'\x02\x01': 'TV',
                         b'\x03\x02\x01': 'Video',
                         b'\x03\x03\x01': 'Video 2/Component',
                         b'\x03\x04\x01': 'HDMI 1',
                         b'\x03\x04\x02': 'HDMI 2',
                         b'\x03\x04\x03': 'HDMI 3/ARC',
                         b'\x03\x04\x04': 'HDMI 4'}[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        state = {'0': b'\x01\x09',
                 '1': b'\x01\x00',
                 '2': b'\x01\x01',
                 '3': b'\x01\x02',
                 '4': b'\x01\x03',
                 '5': b'\x01\x04',
                 '6': b'\x01\x05',
                 '7': b'\x01\x06',
                 '8': b'\x01\x07',
                 '9': b'\x01\x08',
                 '.': b'\x97\x1D'}[value]
        KeypadCmdString = b'\x67\x03'
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier, state)

    def SetMenuNavigation(self, value, qualifier):

        state = {'Home': b'\x01\x60',
                 'Up': b'\x01\x74',
                 'Down': b'\x01\x75',
                 'Left': b'\x01\x34',
                 'Right': b'\x01\x33',
                 'Enter': b'\x01\x65',
                 'Options': b'\x97\x36',
                 'Return': b'\x97\x23'}[value]
        MenuNavigationCmdString = b'\x67\x03'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, state)

    def SetPictureMode(self, value, qualifier):

        state = {'Vivid': b'\x00',
                 'Standard': b'\x01',
                 'Cinema': b'\x02',
                 'Custom': b'\x03',
                 'Cine2': b'\x06',
                 'Sports': b'\x07',
                 'Game': b'\x08',
                 'Graphics': b'\x09'}[value]
        PictureModeCmdString = b'\x20\x03\x01'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier, state)

    def SetPower(self, value, qualifier):

        state = {'On': b'\x01', 'Off': b'\x00'}[value]
        PowerCmdString = b'\x00\x02'
        if value == 'Off':

            self.__SetHelper('Power', b'\x01\x02', value, qualifier, b'\x01')
        self.__SetHelper('Power', PowerCmdString, value, qualifier, state)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = {1: 'On', 0: 'Off'}[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        state = {'On': b'\x00', 'Off': b'\x01'}[value]
        VideoMuteCmdString = b'\x0D\x03\x01'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, state)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = b'\x05\x03\x01'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, bytes([value]))
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x05'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: "Limit Over (Over max value).",
            0x02: "Limit Over (Under min value).",
            0x03: "Command Cancelled.",
            0x04: "Parse Error."
        }

        if response[1] in DEVICE_ERROR_CODES:
            self.Error(["Unrecognized Command {0} and error is {1}".format(sourceCmdName, DEVICE_ERROR_CODES[response[1]])])
            return b''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier, state):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if state:
                commandstring = self.AddChecksum(b''.join([b'\x8C\x00', commandstring, state]))
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        regex = self.CompiledRegex[command]
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

            commandstring = self.AddChecksum(b''.join([b'\x83\x00', commandstring, b'\xFF\xFF']))
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


class DeviceEthernetClass:
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
            'ChannelStep': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }
        
    def SetAudioMute(self, value, qualifier):

        state = {'On': '1',
                 'Off': '0'}[value]
        AudioMuteCmdString = 'AMUT'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier, state)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'AMUT'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = {'1': 'On',
                         '0': 'Off'}[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AudioMute: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        state = {'Up': '33',
                 'Down': '34'}[value]
        ChannelStepCmdString = 'IRCC'
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier, state)

    def SetInput(self, value, qualifier):

        state = {'TV': '000000000',
                 'Video 1': '300000001',
                 'Video 2/Component': '400000001',
                 'HDMI 1': '100000001',
                 'HDMI 2': '100000002',
                 'HDMI 3/ARC': '100000003',
                 'HDMI 4': '100000004',
                 'Screen Mirroring': '500000001'}[value]
        InputCmdString = 'INPT'
        self.__SetHelper('Input', InputCmdString, value, qualifier, state)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'INPT'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = {
                    '000000000': 'TV',
                    '000000001': 'TV',
                    '300000001': 'Video 1',
                    '400000001': 'Video 2/Component',
                    '100000001': 'HDMI 1',
                    '100000002': 'HDMI 2',
                    '100000003': 'HDMI 3/ARC',
                    '100000004': 'HDMI 4',
                    '500000001': 'Screen Mirroring'
                }[res[-10:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        state = \
        {'0': '27',
         '1': '18',
         '2': '19',
         '3': '20',
         '4': '21',
         '5': '22',
         '6': '23',
         '7': '24',
         '8': '25',
         '9': '26',
         '.': '38'}[value]
        KeypadCmdString = 'IRCC'
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier, state)

    def SetMenuNavigation(self, value, qualifier):

        state = {'Home': '06',
                 'Up': '09',
                 'Down': '10',
                 'Left': '12',
                 'Right': '11',
                 'Enter': '13',
                 'Options': '07',
                 'Return': '08'}[value]
        MenuNavigationCmdString = 'IRCC'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, state)

    def SetPictureinPicture(self, value, qualifier):

        state = {'On': '1',
                 'Off': '0'}[value]
        PictureinPictureCmdString = 'PIPI'
        self.__SetHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier, state)

    def UpdatePictureinPicture(self, value, qualifier):

        PictureinPictureCmdString = 'PIPI'
        res = self.__UpdateHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)
        if res:
            try:
                value = {'1': 'On',
                         '0': 'Off'}[res[-2]]
                self.WriteStatus('PictureinPicture', value, None)
            except (KeyError, IndexError):
                self.Error(['PictureinPicture: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        state = {'On': '1',
                 'Off': '0'}[value]
        PowerCmdString = 'POWR'
        self.__SetHelper('Power', PowerCmdString, value, qualifier, state)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'POWR'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = {'1': 'On',
                         '0': 'Off'}[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        state = {'On': '1',
                 'Off': '0'}[value]
        VideoMuteCmdString = 'PMUT'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, state)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'PMUT'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = {'1': 'On',
                         '0': 'Off'}[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['VideoMute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            state = str(value).zfill(3)
            VolumeCmdString = 'VOLU'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, state)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'VOLU'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        command = {
            'AMUT': 'Audio Mute',
            'INPT': 'Input',
            'IRCC': 'Channel Step, Keypad, or Menu Navigation',
            'POWR': 'Power',
            'VOLU': 'Volume',
            'PMUT': 'Video Mute'
        }[response[3:7]]

        if response[7] == 'F':
            errorstring = 'Error: {0}'.format(command)
            response = ''
        elif response[7] == 'N':
            errorstring = 'Not Found: {0}'.format(command)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, state):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if state:
                commandstring = '*SC{0}{1}\n'.format(commandstring, state.zfill(16))
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            commandstring = '*SE{0}\n'.format(commandstring.ljust(20, '#'))
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n')
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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