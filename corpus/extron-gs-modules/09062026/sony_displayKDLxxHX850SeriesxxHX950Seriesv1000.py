from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
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
            'PictureinPicture': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*SAAMUT0{15}([01])\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SAINPT0{7}([0-6])0{7}([0-4])\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*SAPIPI0{15}([01])\n'), self.__MatchPictureinPicture, None)
            self.AddMatchString(re.compile(b'\*SAPOWR0{15}([01])\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*SAPMUT0{15}([01])\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*SAVOLU0{13}(0[0-9]{2}|100)\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\*SA(AMUT|INPT|IRCC|PIPI|PMUT|VOLU)(F|N){16}\n'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        state = {
            'On': b'1',
            'Off': b'0'
        }[value]

        AudioMuteCmdString = b''.join(['AMUT'.ljust(19, '0').encode(), state])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'AMUT'.ljust(20, '#').encode()
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannelStep(self, value, qualifier):

        state = {
            'Up': b'33',
            'Down': b'34'
        }[value]

        ChannelStepCmdString = b''.join(['IRCC'.ljust(18, '0').encode(), state])
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        state = {
            'TV'            	: ['0', b'0'],
            'SCART'				: ['2', b'1'],
            'Composite'     	: ['3', b'1'],
            'Component'     	: ['4', b'1'],
            'HDMI 1'        	: ['1', b'1'],
            'HDMI 2'        	: ['1', b'2'],
            'HDMI 3'        	: ['1', b'3'],
            'HDMI 4'        	: ['1', b'4'],
            'PC'            	: ['6', b'1'],
            'Screen Mirroring': ['5', b'1']
        }[value]

        InputCmdString = b''.join(['INPT'.ljust(11, '0').encode(), state[0].ljust(8, '0').encode(), state[1]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'INPT'.ljust(20, '#').encode()
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        inpVal = {
            '0': 'TV',
            '1': 'HDMI',
            '2': 'SCART',
            '3': 'Composite',
            '4': 'Component',
            '6': 'PC',
            '5': 'Screen Mirroring'
        }[match.group(1).decode()]

        if inpVal == 'HDMI':
        	value = '{} {}'.format(inpVal, match.group(2).decode())
        else:
        	value = inpVal
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        state = {
            '0': b'27',
            '1': b'18',
            '2': b'19',
            '3': b'20',
            '4': b'21',
            '5': b'22',
            '6': b'23',
            '7': b'24',
            '8': b'25',
            '9': b'26',
            '.': b'38'
        }[value]

        KeypadCmdString = b''.join(['IRCC'.ljust(18, '0').encode(), state])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        state = {
            'Up': b'09',
            'Down': b'10',
            'Right': b'11',
            'Left': b'12',
            'Enter': b'13',
            'Home': b'06',
            'Return': b'08',
            'Exit': b'41',
            'Menu': b'89'
        }[value]

        MenuNavigationCmdString = b''.join(['IRCC'.ljust(18, '0').encode(), state])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureinPicture(self, value, qualifier):

        state = {
            'On': b'1',
            'Off': b'0'
        }[value]

        PictureinPictureCmdString = b''.join(['PIPI'.ljust(19, '0').encode(), state])
        self.__SetHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)

    def UpdatePictureinPicture(self, value, qualifier):

        PictureinPictureCmdString = 'PIPI'.ljust(20, '#').encode()
        self.__UpdateHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)

    def __MatchPictureinPicture(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]
        self.WriteStatus('PictureinPicture', value, None)

    def SetPower(self, value, qualifier):

        state = {
            'On': b'1',
            'Off': b'0'
        }[value]

        PowerCmdString = b''.join(['POWR'.ljust(19, '0').encode(), state])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'POWR'.ljust(20, '#').encode()
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        state = {
            'On': b'1',
            'Off': b'0'
        }[value]

        VideoMuteCmdString = b''.join(['PMUT'.ljust(19, '0').encode(), state])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'PMUT'.ljust(20, '#').encode()
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        value = {
            '1': 'On',
            '0': 'Off'
        }[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b''.join(['VOLU'.ljust(17, '0').encode(), str(value).zfill(3).encode()])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLU'.ljust(20, '#').encode()
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        commandstring = b''.join([b'*SC', commandstring, b'\n'])
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = b''.join([b'*SE', commandstring, b'\n'])
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        CommandNames = {
            'AMUT' : 'Audio Mute',
            'INPT' : 'Input',
            'PIPI' : 'Picture in Picture',
            'POWR' : 'Power',
            'VOLU' : 'Volume',
            'PMUT' : 'Video Mute'
        }

        value = match.group(1).decode()
        error_code = match.group(2).decode()

        if error_code[0] == 'F':
            errorstring = 'Error: {0}'.format(CommandNames[value])
        elif error_code[0] == 'N':
            errorstring = 'Not Found: {0}'.format(CommandNames[value])
        else:
            errorstring = 'Unknown Error.'
        self.Error([errorstring])

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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

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

