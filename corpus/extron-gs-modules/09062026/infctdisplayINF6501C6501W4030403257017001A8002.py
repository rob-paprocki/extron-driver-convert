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
        self.Models = {
            'INF6501c': self.infc_39_2014_a,
            'INF6501w': self.infc_39_2014_a,
            'INF4030': self.infc_39_2014_a,
            'INF4032': self.infc_39_2014_a,
            'INF5701': self.infc_39_2014_b,
            'INF7001a': self.infc_39_2014_b,
            'INF8002': self.infc_39_2014_c,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PictureReset': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenReset': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'5b0050500(0|1)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'5b0035500(0|1)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'5b0051900(0|1)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'5b0031c00(0|1|2)\r'), self.__MatchGamma, None)
            self.AddMatchString(re.compile(b'5b0030100(0|1|2|3|4|5|6|8)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'5b0050400(0|1|2)\r'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'5b0036100(0|1|2|3|4)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'5b0036000(0|1|2)\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'5b0030000(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'5b0050000(0|1)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'5b00350([0-9]{1,3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'560036\r|5600-\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide': '0',
            '4:3': '1'
        }

        AspectRatioCmdString = '5b0060600' + ValueStateValues[value] + '\r'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '5800405\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Wide',
            '1': '4:3'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '5b0015500' + ValueStateValues[value] + '\r'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '5800255\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '5b0065000' + ValueStateValues[value] + '\r'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '5800419\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGamma(self, value, qualifier):

        ValueStateValues = {
            'Native': '0',
            '2.2': '1',
            '2.4': '2'
        }

        GammaCmdString = '5b0011c00' + ValueStateValues[value] + '\r'
        self.__SetHelper('Gamma', GammaCmdString, value, qualifier)

    def UpdateGamma(self, value, qualifier):

        GammaCmdString = '580021c\r'
        self.__UpdateHelper('Gamma', GammaCmdString, value, qualifier)

    def __MatchGamma(self, match, tag):

        ValueStateValues = {
            '0': 'Native',
            '1': '2.2',
            '2': '2.4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Gamma', value, None)

    def SetInput(self, value, qualifier):

        InputCmdString = '5b0010100' + self.SetInputStateValues['Input'][value] + '\r'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '5800201\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.UpdateInputStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'HighBright': '1',
            'Soft': '2'
        }

        PictureModeCmdString = '5b0060400' + ValueStateValues[value] + '\r'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '5800404\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'HighBright',
            '2': 'Soft'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPictureReset(self, value, qualifier):

        PictureResetCmdString = '5b00605001\r'
        self.__SetHelper('PictureReset', PictureResetCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = '5b0061500' + self.SetInputStateValues['PIPInput'][value] + '\r'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off' 	: '0',
            'PIP' 	: '1',
            'POP' 	: '2',
            'PBP-1': '3',
            'PBP-2': '4'
        }

        PIPModeCmdString = '5b0016100' + ValueStateValues[value] + '\r'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '5800261\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'POP',
            '3': 'PBP-1',
            '4': 'PBP-2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left' 		: '40',
            'Top Right' 	: '41',
            'Bottom Left' 	: '50',
            'Bottom Right' 	: '51'
        }

        PIPPositionCmdString = '5b0016' + ValueStateValues[value] + '00\r'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '0',
            'Medium': '1',
            'Large': '2'
        }

        PIPSizeCmdString = '5b0016000' + ValueStateValues[value] + '\r'
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = '5800260\r'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '0': 'Small',
            '1': 'Medium',
            '2': 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '5b00617000\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '5b0010000' + ValueStateValues[value] + '\r'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '5800200\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetScreenReset(self, value, qualifier):

        ScreenResetCmdString = '5b00607001\r'
        self.__SetHelper('ScreenReset', ScreenResetCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '5b0066000' + ValueStateValues[value] + '\r'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '5800500\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '5b00150' + str(value).zfill(3) + '\r'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '5800250\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
        	print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)

    def __MatchError(self, match, tag):


        value = 'Error: ' + match.group(0).decode() + ' = Invalid Command.'
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def infc_39_2014_a(self):
        self.SetInputStateValues = {
			'Input'		: {
				'HDMI 1' 	: '0',
				'HDMI 2' 	: '1',
				'HDMI 3' 	: '2',
				'HDMI 4' 	: '4',
				'VGA'	 	: '3',
				'Component'	: '6',
				'Composite' : '8',
				'LitePort'  : '7'
			},

			'PIPInput'	: {
				'HDMI 1' 	: '0',
				'HDMI 2' 	: '1',
				'HDMI 3' 	: '6',
				'HDMI 4' 	: '7',
				'VGA'	 	: '3',
				'Component'	: '4',
				'Composite' : '5',
				'LiteCast'	: '8'				
			}
		}
        self.UpdateInputStateValues = {
			'0' : 'HDMI 1',
			'1' : 'HDMI 2',
			'2' : 'HDMI 3',
			'4' : 'HDMI 4',
			'3' : 'VGA',
			'6' : 'Component',
			'8' : 'Composite',
			'5' : 'LitePort'
		}

    def infc_39_2014_b(self):
        self.SetInputStateValues = {
			'Input'		: {
				'HDMI 1' 	: '0',
				'HDMI 2' 	: '1',
				'VGA'	 	: '3',
				'LitePort'	: '7'
			},

			'PIPInput'	: {
				'HDMI 1' 	: '0',
				'HDMI 2' 	: '1',
				'VGA'	 	: '3',
				'LiteCast'	: '8'				
			}
		}
        self.UpdateInputStateValues = {
			'0' : 'HDMI 1',
			'1' : 'HDMI 2',
			'3' : 'VGA',
			'5' : 'LitePort'
		}

    def infc_39_2014_c(self):
        self.SetInputStateValues = {
			'Input'		: {
				'HDMI 1' 	  : '0',
				'HDMI 2' 	  : '1',
				'HDMI 3'	  : '2',
				'VGA'	 	  : '3',
				'Component'	  : '6',
				'LitePort' 	  : '7'
			},

			'PIPInput'	: {
				'HDMI 1' 	  : '0',
				'HDMI 2' 	  : '1',
				'HDMI 3'	  : '6',
				'VGA'	 	  : '3',
				'Component'	  : '4',
				'LiteCast' 	  : '8'				
			}
		}
        self.UpdateInputStateValues = {
			'0' : 'HDMI 1',
			'1' : 'HDMI 2',
			'2' : 'HDMI 3',
			'3' : 'VGA',
			'6' : 'Component',
			'5' : 'LitePort'
		}

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
