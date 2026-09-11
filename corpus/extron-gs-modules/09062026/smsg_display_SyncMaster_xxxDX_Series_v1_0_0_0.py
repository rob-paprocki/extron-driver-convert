from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }       

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x15(\x00|\x05|\x06|\x0B|\x01)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x13(\x01|\x00)[\x00-\xFF]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x14(\x14|\x1E|\x18|\x0C|\x04|\x08|\x20|\x30|\x40|\x21)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x70(\x01|\x00)[\x00-\xFF]'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x40(\x14|\x18|\x0C|\x04|\x08)[\x00-\xFF]'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x43(\x01|\x02|\x04|\x03)[\x00-\xFF]'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x42(\x06|\x08|\x04|\x05|\x09|\x00)[\x00-\xFF]'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF[\x00-\xFF]\x03\x4E([\x00-\xFF])([\x00-\xFF])([\x00-\xFF])'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):        
        if value == 'Broadcast':
            self._DeviceID = 254
        elif int(value) == 0:
            self._DeviceID = 255
        elif 1 <= int(value) <= 99:
            self._DeviceID = int(value)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
           'Wide': 0x00,
           'Zoom 1': 0x05,
           'Zoom 2': 0x06,
           '4:3': 0x0B,
           '16:9': 0x01
           }

        checksum = int(hex(0x15 + self._DeviceID + 0x01 + AspectRatioState[value])[-2:], 16)
        AspectRatioCmdString = pack('>BBBBBB', 0xAA, 0x18, self._DeviceID, 0x01, AspectRatioState[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        checksum = int(hex(0x15 + self._DeviceID + 0x00)[-2:], 16)
        AspectRatioCmdString = pack('>BBBBB', 0xAA, 0x15, self._DeviceID, 0x00, checksum)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioNames = {
            '\x00': 'Wide',
            '\x05': 'Zoom 1',
            '\x06': 'Zoom 2',
            '\x0B': '4:3',
            '\x01': '16:9'
            }

        value = AspectRatioNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        checksum = int(hex(0x3D + self._DeviceID + 0x01 + 0x00)[-2:], 16)
        AutoImageCmdString = pack('>BBBBBB', 0xAA, 0x3D, self._DeviceID, 0x01, 0x00, checksum)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        
    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        checksum = int(hex(0x13 + self._DeviceID + 0x01 + AudioMuteState[value])[-2:],16)
        AudioMuteCmdString = pack('>BBBBBB',0xAA,0x13,self._DeviceID,0x01,AudioMuteState[value],checksum)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        checksum = int(hex(0x13 + self._DeviceID + 0x00)[-2:],16)
        AudioMuteCmdString = pack('>BBBBB',0xAA,0x13,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteNames = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }
    
        value = AudioMuteNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannelStep(self, value, qualifier):

        ChannelStepState = {
           'Up' : 0x00,
           'Down' : 0x01
           }

        checksum = int(hex(0x61 + self._DeviceID + 0x01 + ChannelStepState[value])[-2:],16)
        ChannelStepCmdString = pack('>BBBBBB',0xAA,0x61,self._DeviceID,0x01,ChannelStepState[value],checksum)
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        
    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On' : 0x01,
            'Off' : 0x00
            }

        checksum = int(hex(0x5D + self._DeviceID + 0x01 + ExecutiveModeState[value])[-2:],16)
        ExecutiveModeCmdString = pack('>BBBBBB',0xAA,0x5D,self._DeviceID,0x01,ExecutiveModeState[value],checksum)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        checksum = int(hex(0x5D + self._DeviceID + 0x00)[-2:],16)
        ExecutiveModeCmdString = pack('>BBBBB',0xAA,0x5D,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeNames = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }
        value = ExecutiveModeNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)
    
    def SetInput(self, value, qualifier):

        InputState = {
           'PC' : 0x14,
           'BNC' : 0x1E,
           'DVI' : 0x18,
           'AV' : 0x0C,
           'S-Video' : 0x04,
           'Component' : 0x08,
           'MagicNet' : 0x20,
           'RF' : 0x30,
           'DTV' : 0x40,
           'HDMI' : 0x21,
           'DVI (HDCP)' : 0x1F
           }

        checksum = int(hex(0x14 + self._DeviceID + 0x01 + InputState[value])[-2:],16)
        InputCmdString = pack('>BBBBBB',0xAA,0x14,self._DeviceID,0x01,InputState[value],checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        checksum = int(hex(0x14 + self._DeviceID + 0x00)[-2:],16)
        InputCmdString = pack('>BBBBB',0xAA,0x14,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputNames = {
           '\x14' : 'PC',
           '\x1E' : 'BNC',
           '\x18' : 'DVI',
           '\x0C' : 'AV',
           '\x04' : 'S-Video',
           '\x08' : 'Component',
           '\x20' : 'MagicNet',
           '\x30' : 'RF',
           '\x40' : 'DTV',
           '\x21' : 'HDMI',
           '\x1F' : 'DVI (HDCP)'
           }
        value = InputNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)
    
    def SetOnScreenDisplay(self, value, qualifier):

        OSDState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        checksum = int(hex(0x70 + self._DeviceID + 0x01 + OSDState[value])[-2:],16)
        OSDCmdString = pack('>BBBBBB',0xAA,0x70,self._DeviceID,0x01,OSDState[value],checksum)
        self.__SetHelper('OnScreenDisplay', OSDCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        checksum = int(hex(0x70 + self._DeviceID + 0x00)[-2:],16)
        OSDCmdString = pack('>BBBBB',0xAA,0x70,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('OnScreenDisplay', OSDCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        OSDNames = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }
        value = OSDNames[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
           'PC' : 0x14,
           'DVI' : 0x18,
           'AV' : 0x0C,
           'S-Video' : 0x04,
           'Component' : 0x08
           }

        checksum = int(hex(0x40 + self._DeviceID + 0x01 + PIPInputState[value])[-2:],16)
        PIPInputCmdString = pack('>BBBBBB',0xAA,0x40,self._DeviceID,0x01,PIPInputState[value],checksum)
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        checksum = int(hex(0x40 + self._DeviceID + 0x00)[-2:], 16)
        PIPInputCmdString = pack('>BBBBB',0xAA,0x40,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        PIPInputStateNames = {
            '\x14' : 'PC',
            '\x18' : 'DVI',
            '\x0C' : 'AV',
            '\x04' : 'S-Video',
            '\x08' : 'Component'
            }
        value = PIPInputStateNames[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
           'Upper Left' : 0x01,
           'Upper Right' : 0x02,
           'Lower Left' : 0x04,
           'Lower Right' : 0x03
           }

        checksum = int(hex(0x43 + self._DeviceID + 0x01 + PIPPositionState[value])[-2:],16)
        PIPPositionCmdString = pack('>BBBBBB',0xAA,0x43,self._DeviceID,0x01,PIPPositionState[value],checksum)
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        checksum = int(hex(0x43 + self._DeviceID + 0x00)[-2:],16)
        PIPPositionCmdString = pack('>BBBBB',0xAA,0x43,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('PIPInput', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        PIPPositionStateNames = {
            '\x01' : 'Upper Left',
            '\x02' : 'Upper Right',
            '\x04' : 'Lower Left',
            '\x03' : 'Lower Right'
            }
        value = PIPPositionStateNames[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        PIPSizeState = {
           'Large' : 0x06,
           'Small' : 0x08,
           'Double 1' : 0x04,
           'Double 2' : 0x05,
           'Double 3' : 0x09,
           'Off' : 0x00
           }

        checksum = int(hex(0x42 + self._DeviceID + 0x01 + PIPSizeState[value])[-2:],16)
        PIPSizeCmdString = pack('>BBBBBB',0xAA,0x42,self._DeviceID,0x01,PIPSizeState[value],checksum)
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        checksum = int(hex(0x42 + self._DeviceID + 0x00)[-2:],16)
        PIPSizeCmdString = pack('>BBBBB',0xAA,0x42,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        PIPSizeState = {
           '\x06' : 'Large',
           '\x08' : 'Small',
           '\x04' : 'Double 1',
           '\x05' : 'Double 2',
           '\x09' : 'Double 3',
           '\x00' : 'Off'
           }
        value = PIPSizeState[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPower(self, value, qualifier):

        PowerState = {
           'On' : 0x01,
           'Off' : 0x00
           }

        checksum = int(hex(0x11 + self._DeviceID + 0x01 + PowerState[value])[-2:],16)
        PowerCmdString = pack('>BBBBBB',0xAA,0x11,self._DeviceID,0x01,PowerState[value],checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        checksum = int(hex(0x11 + self._DeviceID + 0x00)[-2:],16)
        PowerCmdString = pack('>BBBBB',0xAA,0x11,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '\x01' : 'On',
            '\x00' : 'Off'
            }
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            checksum = int(hex(0x12 + self._DeviceID + 0x01 + value)[-2:], 16)
            VolumeCmdString = pack('>BBBBBB',0xAA,0x12,self._DeviceID,0x01,value,checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = int(hex(0x12 + self._DeviceID + 0x00)[-2:], 16)
        VolumeCmdString = pack('>BBBBB',0xAA,0x12,self._DeviceID,0x00,checksum)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 254: #Broadcast
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
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '\x01' : 'Other error',
            '\x00' : 'Checksum error'
            }

        COMMAND_ERROR_CODES = {
            '\x15' : 'Aspect Ratio',
            '\x13' : 'Audio Mute',
            '\x5D' : 'Executive Mode',
            '\x14' : 'Input',
            '\x70' : 'On Screen Display',
            '\x40' : 'PIP Input',
            '\x43' : 'PIP Position',
            '\x42' : 'PIP Size',
            '\x11' : 'Power',
            '\x12' : 'Volume'
            }

        value = DEVICE_ERROR_CODES.get(match.group(2).decode(), 'Error')
        value1 = COMMAND_ERROR_CODES.get(match.group(1).decode(), 'Error')
        errorstring = 'Command: {0}, Error Type: {1}'.format(value1, value)
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
        
        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
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

