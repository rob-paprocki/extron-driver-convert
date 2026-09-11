from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, search

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
            'AudioMute': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'DisplayMute': { 'Status': {}},
            'DisplayPower': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': {'Parameters':['Type'], 'Status': {}},
            'InputType': {'Parameters':['Input'], 'Status': {}},
            'Resolution': { 'Status': {}},
            'RoomFunction': {'Parameters':['Room'], 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False' :
            self.AddMatchString(compile(b'E([0-3][0-9])\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Amt([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Mut([0-1])\r\n'), self.__MatchDisplayMute, None)
            self.AddMatchString(compile(b'Pwr([0-3])\r\n'), self.__MatchDisplayPower, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frz([0-1])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'Vid0([0-7]) Aud0([0-7]) Std(\d+) Max(\d+)\r\n'), self.__MatchInput, 'Update')
            self.AddMatchString(compile(b'(Chn|Aud|Vid)0?([0-7])\r\n'), self.__MatchInput, 'Set')
            self.AddMatchString(compile(b'Rte(\d+)\r\n'), self.__MatchResolution, None)
            self.AddMatchString(compile(b'Rly([1-2])\*([0-1])\r\n'), self.__MatchRoomFunction, None)
            self.AddMatchString(compile(b'Vol(\d+)\r\n'), self.__MatchVolume, None)

        self.InputTypeRegex = compile(b'Typ([0-7])=(Vid|Y-C|YUV|YUVp|RGB)\r\n|E([0-3][0-9])\r\n')

    def SetAudioMute(self, value, qualifier):

        
        AudioMuteStateValues = {
            'Off' : '0',
            'On'  : '1'
        }

        AudioMuteCmdString = '{0}Z'.format(AudioMuteStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):


        audioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', audioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):


        AudioMuteStateNames = {
            '0' : 'Off',
            '1' : 'On'
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetDisplayMode(self, value, qualifier):

        DisplayModeCmdString = 'J'
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def SetDisplayMute(self, value, qualifier):

        DisplayMuteStateValues = {
            'Off' : '0',
            'On'  : '1'
        }

        DisplayMuteCmdString = '{0}M'.format(DisplayMuteStateValues[value])
        self.__SetHelper('DisplayMute', DisplayMuteCmdString, value, qualifier) 

    def UpdateDisplayMute(self, value, qualifier):

        displayMuteCmdString = 'M'
        self.__UpdateHelper('DisplayMute', displayMuteCmdString, value, qualifier)

    def __MatchDisplayMute(self, match, tag):

        DisplayMuteStateNames = {
            '0' : 'Off',
            '1' : 'On'
        }

        value = DisplayMuteStateNames[match.group(1).decode()]
        self.WriteStatus('DisplayMute', value, None)

    def SetDisplayPower(self, value, qualifier):
        
        DisplayPowerStateValues = {
            'Off' : '0',
            'On'  : '1'
        }

        DisplayPowerCmdString = '{0}P'.format(DisplayPowerStateValues[value])
        self.__SetHelper('DisplayPower', DisplayPowerCmdString, value, qualifier)

    def UpdateDisplayPower(self, value, qualifier):     
 
        displayPowerCmdString = 'P'
        self.__UpdateHelper('DisplayPower', displayPowerCmdString, value, qualifier)

    def __MatchDisplayPower(self, match, tag):

        DisplayPowerStateNames = {
            '0' : 'Off',
            '1' : 'On',
            '2' : 'Cooling',
            '3' : 'Warming'
        }

        value = DisplayPowerStateNames[match.group(1).decode()]
        self.WriteStatus('DisplayPower', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'Off' : '0',
            'Mode 1' : '1',
            'Mode 2' : '2'
        }

        ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        	
        commandString = 'X'
        self.__UpdateHelper('ExecutiveMode', commandString, value, qualifier)
        	        	
    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
           '0' : 'Off',
           '1' : 'Mode 1',
           '2' : 'Mode 2'
          }


        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'Off' : '0',
            'On'  : '1'
        }

        FreezeCmdString = '{0}F'.format(FreezeStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):   

        freezeCmdString = 'F'
        self.__UpdateHelper('Freeze', freezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeStateNames = {
	        '0' : 'Off',
	        '1' : 'On'
        } 

        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)    

    def SetInput(self, value, qualifier): 

        SwitchType = qualifier['Type']

        SwitchTypeValues = {
            'Audio' : '$',
            'Video' : '&',
            'Audio/Video' : '!'
        }

        InputConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        if InputConstraints['Min'] <= int(value) <= InputConstraints['Max']:
            InputCmdString = '{0}{1}'.format(value, SwitchTypeValues[SwitchType])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)


    def __MatchInput(self, match, tag):

        InputTypeNames = {
            'Aud' : 'Audio',
            'Vid' : 'Video',
            'Chn' : 'Audio/Video'
            }

        if tag == 'Set':
            value = match.group(2).decode()
            Type = InputTypeNames[match.group(1).decode()]
            if Type != 'Audio/Video':
                qualifier = {'Type' : Type}
                self.WriteStatus('Input', value, qualifier)
            else:
                for type in ['Audio', 'Video', 'Audio/Video']:
                    qualifier = {'Type' : type}
                    self.WriteStatus('Input', value, qualifier)

        if tag == 'Update':
            videoInputValue = match.group(1).decode()
            audioInputValue = match.group(2).decode()

            if videoInputValue == audioInputValue:  # Check to see if video and audio inputs are the same
                AVInputValue = videoInputValue      # If same, then A/V set to match value
            else:                                   
                AVInputValue = '0'                  # If different, then A/V set to 0

            self.WriteStatus('Input', audioInputValue, {'Type':'Audio'})
            self.WriteStatus('Input', videoInputValue, {'Type':'Video'})
            self.WriteStatus('Input', AVInputValue, {'Type':'Audio/Video'})

    def SetInputType(self, value, qualifier):

        InputTypeValues = {
            'RGB' : '0',
            'Video' : '1',
            'S-Video' : '3',
            'YUVi' : '5',
            'YUVp' : '7'
            }

        InputConstraints = {
            'Min' : 1,
            'Max' : 7
            }
        
        InputSelect = qualifier['Input']

        if InputConstraints['Min'] <= int(InputSelect) <= InputConstraints['Max']:
            InputTypeCmdString = '{0}*{1}\\'.format(InputSelect, InputTypeValues[value])
            self.__SetHelper('InputType', InputTypeCmdString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetInputType') 

    def UpdateInputType(self, value, qualifier):

        InputConstraints = {
            'Min' : 1,
            'Max' : 7
        }

        InputTypeNames = {
            'RGB' : 'RGB',
            'Vid' : 'Video',
            'Y-C' : 'S-Video',
            'YUV' : 'YUVi',
            'YUVp' : 'YUVp'
        }

        inputVal = qualifier['Input']

        if InputConstraints['Min'] <= int(inputVal) <= InputConstraints['Max']:
            res = self.__UpdateHelper('InputType', '{0}\\'.format(inputVal), value, qualifier)
            if res:
            	try:
            		value = InputTypeNames[res[5:-2]]
            		self.WriteStatus('InputType', value, qualifier)
            	except(KeyError, IndexError):
            		self.Error(['InputType: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputType') 

    def SetResolution(self, value, qualifier):

        ResolutionStateValues = {
            '640x480 @ 50 Hz' : '1',
            '640x480 @ 60 Hz' : '2',
            '640x480 @ 75 Hz' : '3',
            '640x480 @ Lock' : '4',
            '800x600 @ 50 Hz' : '5',
            '800x600 @ 60 Hz' : '6',
            '800x600 @ 75 Hz' : '7',
            '800x600 @ Lock' : '8',  
            '832x624 @ 60 Hz' : '9',
            '832x624 @ 75 Hz' : '10',
            '832x624 @ Lock' : '11',
            '848x480 @ 60 Hz' : '12',
            '852x480 @ 60 Hz' : '13',
            '1024x768 @ 50 Hz' : '14',
            '1024x768 @ 60 Hz' : '15',
            '1024x768 @ 75 Hz' : '16',
            '1024x768 @ Lock' : '17',
            '1280x768 @ 56 Hz' : '18',
            '1280x1024 @ 50 Hz' : '19',
            '1280x1024 @ 60 Hz' : '20',
            '1280x1024 @ Lock': '21',
            '1360x765 @ 60 Hz' : '22',
            '1365x1024 @ 60 Hz' : '23',
            '1365x1024 @ Lock' : '24',
            '480p @ 60 Hz' : '25',
            '480p @ Lock' : '26',
            '720p @ 60 Hz' : '27',
            '720p @ Lock' : '28',
            '1080p @ 60 Hz' : '29',
            '1080p @ Lock' : '30',
            '1080i @ 60 Hz' : '31',
            '1080i @ Lock' : '32'
            }

        ResolutionCmdString = '{0}='.format(ResolutionStateValues[value])
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):

        resolutionCmdString = '='
        self.__UpdateHelper('Resolution', resolutionCmdString, value, qualifier)

    def __MatchResolution(self, match, tag):

        ResolutionStateNames = {
            '01' : '640x480 @ 50 Hz',
            '10': '832x624 @ 75 Hz',
            '11': '832x624 @ Lock', 
            '12': '848x480 @ 60 Hz', 
            '13': '852x480 @ 60 Hz',
            '14': '1024x768 @ 50 Hz',
            '15': '1024x768 @ 60 Hz',
            '16': '1024x768 @ 75 Hz', 
            '17': '1024x768 @ Lock',
            '18': '1280x768 @ 56 Hz', 
            '19': '1280x1024 @ 50 Hz',
            '02' : '640x480 @ 60 Hz',
            '20': '1280x1024 @ 60 Hz',
            '21': '1280x1024 @ Lock', 
            '22': '1360x765 @ 60 Hz', 
            '23': '1365x1024 @ 60 Hz',
            '24': '1365x1024 @ Lock',
            '25': '480p @ 60 Hz', 
            '26': '480p @ Lock',
            '27': '720p @ 60 Hz',
            '28': '720p @ Lock',
            '29': '1080p @ 60 Hz',
            '03' : '640x480 @ 75 Hz',
            '30': '1080p @ Lock',
            '31': '1080i @ 60 Hz',
            '32': '1080i @ Lock',
            '04' : '640x480 @ Lock',
            '05' : '800x600 @ 50 Hz',
            '06' : '800x600 @ 60 Hz',
            '07' : '800x600 @ 75 Hz',
            '08' : '800x600 @ Lock',
            '09' : '832x624 @ 60 Hz',
        }

        value = ResolutionStateNames[match.group(1).decode()]
        self.WriteStatus('Resolution', value, None)    

    def SetRoomFunction(self, value, qualifier): 

        RoomFunctionStateValues = {
            'Off' : '0',
            'On'  : '1'
            }

        RoomConstraints = {
            'Min' : 1,
            'Max' : 2
            }

        RoomNumber = qualifier['Room']

        if RoomConstraints['Min'] <= int(RoomNumber) <= RoomConstraints['Max']:
            RoomFunctionCmdString = '{0}*{1}O'.format(RoomNumber, RoomFunctionStateValues[value])
            self.__SetHelper('RoomFunction', RoomFunctionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomFunction')

    def UpdateRoomFunction(self, value, qualifier):

        RoomConstraints = {
            'Min' : 1,
            'Max' : 2
            }

        roomNumber = qualifier['Room']
        
        if RoomConstraints['Min'] <= int(roomNumber) <= RoomConstraints['Max']:  
            roomFunctionCmdString = '{0}O'.format(roomNumber)
            self.__UpdateHelper('RoomFunction', roomFunctionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRoomFunction')

    def __MatchRoomFunction(self, match, tag):

        RoomFunctionStateNames = {
            '0' : 'Off',
            '1' : 'On'
        }

        value = RoomFunctionStateNames[match.group(2).decode()]
        self.WriteStatus('RoomFunction', value, {'Room': match.group(1).decode()})   

    def SetVolume(self, value, qualifier): 
  
        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }  
          
        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:   
            self.Discard('Invalid Command for SetVolume')
        else:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier) 

    def UpdateVolume(self, value, qualifier):     
        
        VolumeCmdString = 'V'   
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = (int(match.group(1)))
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01' : 'Invalid input number (too large)',
            'E10' : 'Invalid command',
            'E11' : 'Invalid preset number',
            'E12' : 'Invalid port number',
            'E13' : 'Invalid value',
            'E14' : 'Command not available for this configuration',
            'E17' : 'System timed out',
            'E22' : 'Busy',
            'E23' : 'Checksum error',
            'E24' : 'Privilege violation',
            'E25' : 'Device not present',
            'E26' : 'Maximum number of connections exceeded',
            'E27' : 'Invalid event number',
            'E28' : 'Bad filename or file not found',
            'E30' : 'Hardware failure (followed by a colon [:] and a descriptor number)',
            'E31' : 'Attempt to break port pass-through when it has not been set',
            'E32' : 'Incorrect V-chip password'
        }   

        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    self.Error(['{0} {1} {2}'.format(sourceCmdName, k, v)])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command')
        else:
            if command == 'InputType':
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.InputTypeRegex)
                return self.__CheckResponseForErrors(command, res.decode())
            else:
            	self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        DeviceErrorCodes = {
            '01' : 'Invalid input number (too large)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid value',
            '14' : 'Command not available for this configuration',
            '17' : 'System timed out',
            '22' : 'Busy',
            '23' : 'Checksum error',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '27' : 'Invalid event number',
            '28' : 'Bad filename or file not found',
            '30' : 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31' : 'Attempt to break port pass-through when it has not been set',
            '32' : 'Incorrect V-chip password'
        }

        if match.group(1).decode('ascii') in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode('ascii')]])
        else:
            self.Error(['Unrecognize error code: '+ match.group(0).decode('ascii')]) 
  
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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

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

