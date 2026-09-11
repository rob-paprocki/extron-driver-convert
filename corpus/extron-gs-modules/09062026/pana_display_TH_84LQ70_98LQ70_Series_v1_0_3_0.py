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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'InputMultiDisplayMode': {'Status': {}},
            'InputMultiDisplaySettings': {'Parameters': ['Input Setting', 'Position'], 'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(FULL|NORM|ZOOM|ZOM2)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM[1-4]|D[PLV]1|PC1|SL[12]|S1[AB]|SL2[AB])\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QSU:4IM(0|1)\x03'), self.__MatchInputMultiDisplayMode, None)
            self.AddMatchString(re.compile(b'\x02QSU:4IM(1|2|3|4)(HM[1-4]|D[PLV]1|PC1)(FUL|)\x03'), self.__MatchInputMultiDisplaySettings, None)
            self.AddMatchString(re.compile(b'\x02QSP:OSD(0|1)\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(STD|DYN|CNM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-6][0-9])\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x02ER401\x03'), self.__MatchError, None)

    def MakeCmdString(self, CmdString):
        if 'Serial' not in self.ConnectionType:
            CmdString = CmdString + '\r'
        return CmdString

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': 'FULL',
            'Normal': 'NORM',
            'Zoom 1': 'ZOOM',
            'Zoom 2': 'ZOM2'
        }

        AspectRatioCmdString = '\x02DAM:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', '\x02QAS\x03', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            'FULL': 'Full',
            'NORM': 'Normal',
            'ZOOM': 'Zoom 1',
            'ZOM2': 'Zoom 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '\x02AMT:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '\x02QAM\x03', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '\x02DGE:ASU1\x03', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'HM1',
            'HDMI 2': 'HM2',
            'HDMI 3': 'HM3',
            'HDMI 4': 'HM4',
            'DisplayPort': 'DP1',
            'DIGITAL LINK': 'DL1',
            'DVI': 'DV1',
            'PC': 'PC1',
            'Slot 1': 'SL1',
            'Slot 1A': 'S1A',
            'Slot 1B': 'S1B',
            'Slot 2': 'SL2',
            'Slot 2A': 'SL2A',
            'Slot 2B': 'SL2B'
        }

        InputCmdString = '\x02IMS:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '\x02QMI\x03', value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'HM3': 'HDMI 3',
            'HM4': 'HDMI 4',
            'DP1': 'DisplayPort',
            'DL1': 'DIGITAL LINK',
            'DV1': 'DVI',
            'PC1': 'PC',
            'SL1': 'Slot 1',
            'S1A': 'Slot 1A',
            'S1B': 'Slot 1B',
            'SL2': 'Slot 2',
            'SL2A': 'Slot 2A',
            'SL2B': 'Slot 2B'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetInputMultiDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        InputMultiDisplayModeCmdString = '\x02SSU:4IM{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('InputMultiDisplayMode', InputMultiDisplayModeCmdString, value, qualifier)

    def UpdateInputMultiDisplayMode(self, value, qualifier):
        InputMultiDisplayModeCmdString = '\x02QSU:4IM\x03'
        self.__UpdateHelper('InputMultiDisplayMode', InputMultiDisplayModeCmdString, value, qualifier)

    def __MatchInputMultiDisplayMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputMultiDisplayMode', value, None)

    def SetInputMultiDisplaySettings(self, value, qualifier):

        PositionStates = {
            'Upper Left': '1',
            'Upper Right': '2',
            'Lower Left': '3',
            'Lower Right': '4'
        }

        ValueStateValues = {
            'HDMI 1': 'HM1',
            'HDMI 2': 'HM2',
            'HDMI 3': 'HM3',
            'HDMI 4': 'HM4',
            'Display Port': 'DP1',
            'DIGITAL LINK': 'DL1',
            'DVI': 'DV1',
            'PC': 'PC1'
        }

        InputSetting = qualifier['Input Setting']
        Position = qualifier['Position']
        if InputSetting == 'Full' and Position in PositionStates:
            CmdString = '\x02SSU:4IM{0}{1}FUL\x03'.format(PositionStates[Position], ValueStateValues[value])
            self.__SetHelper('InputMultiDisplaySettings', CmdString, value, qualifier)
        elif InputSetting == 'None' and Position in PositionStates:
            CmdString = '\x02SSU:4IM{0}{1}\x03'.format(PositionStates[Position], ValueStateValues[value])
            self.__SetHelper('InputMultiDisplaySettings', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMultiDisplaySettings')

    def UpdateInputMultiDisplaySettings(self, value, qualifier):

        PositionStates = {
            'Upper Left': '1',
            'Upper Right': '2',
            'Lower Left': '3',
            'Lower Right': '4'
        }

        Position = qualifier['Position']
        if Position in PositionStates:
            InputMultiDisplaySettingsCmdString = '\x02QSU:4IM{0}\x03'.format(PositionStates[Position])
            self.__UpdateHelper('InputMultiDisplaySettings', InputMultiDisplaySettingsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMultiDisplaySettings')

    def __MatchInputMultiDisplaySettings(self, match, tag):

        PositionStates = {
           '1': 'Upper Left',
           '2': 'Upper Right',
           '3': 'Lower Left',
           '4': 'Lower Right'
        }

        ValueStateValues = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'HM3': 'HDMI 3',
            'HM4': 'HDMI 4',
            'DP1': 'Display Port',
            'DL1': 'DIGITAL LINK',
            'DV1': 'DVI',
            'PC1': 'PC'
        }

        Position = PositionStates[match.group(1).decode()]
        InputSetting = match.group(3).decode()
        value = ValueStateValues[match.group(2).decode()]
        if InputSetting == 'FUL':
            self.WriteStatus('InputMultiDisplaySettings', value, {'Position': Position, 'Input Setting': 'Full'})
        else:
            self.WriteStatus('InputMultiDisplaySettings', value, {'Position': Position, 'Input Setting': 'None'})

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = '\x02OSP:OSD{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        OnScreenDisplayCmdString = '\x02QSP:OSD\x03'
        self.__UpdateHelper('OnScreenDisplay', '\x02QSP:OSD\x03', value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'STD',
            'Dynamic': 'DYN',
            'Cinema': 'CNM'
        }

        PictureModeCmdString = '\x02VPC:MEN{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        self.__UpdateHelper('PictureMode', '\x02QPC:MEN\x03', value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'STD': 'Normal',
            'DYN': 'Dynamic',
            'CNM': 'Cinema'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON',
            'Off': 'POF'
        }

        PowerCmdString = '\x02{0}\x03'.format(ValueStateValues[value])

        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', '\x02QPW\x03', value, qualifier)

    def __MatchPower(self, match, tag):

        Values = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Power', Values[match.group(1).decode()], None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '\x02VMT:{0}\x03'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', '\x02QVM\x03', value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            VolumeCmdString = '\x02AVL:{0:02d}\x03'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '\x02QAV\x03', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode()), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(self.MakeCmdString(commandstring))

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(self.MakeCmdString(commandstring))

    def __MatchError(self, match, tag):

        self.Error(['Invalid Command'])

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

