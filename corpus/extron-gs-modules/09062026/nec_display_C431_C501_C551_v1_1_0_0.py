from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog, Timer
from struct import pack
from binascii import hexlify


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
            'Input': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.KeepAliveTimer = None
        self._DeviceID = b'A'

        self.groupMatch = {
            'Broadcast': 0x2A,
            'Group A': 0x31,
            'Group B': 0x32,
            'Group C': 0x33,
            'Group D': 0x34,
            'Group E': 0x35,
            'Group F': 0x36,
            'Group G': 0x37,
            'Group H': 0x38,
            'Group I': 0x39,
            'Group J': 0x3A,}

        if self.Unidirectional == 'False' and 65 <= self._DeviceID[0] <= 164:
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x0200027000[\x00-\xFF]{4}000([1-7])\x03[\x00-\xFF]\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x0200008D00[\x00-\xFF]{4}000([12])\x03[\x00-\xFF]\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x0200006000[\x00-\xFF]{4}00([018][\x31-\x46])\x03[\x00-\xFF]\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x0200021A00[\x00-\xFF]{4}000([134589])\x03[\x00-\xFF]\x0D'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x020200D600[\x00-\xFF]{4}000([1-4])\x03[\x00-\xFF]\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x020010B600[\x00-\xFF]{4}000([12])\x03[\x00-\xFF]\x0D'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x0200006200[\x00-\xFF]{4}00([0-5][0-9A-F]|6[0-4])\x03[\x00-\xFF]\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x0100[\x41-\xA4][\x00-\xFF]{3}\x02\x30\x31'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value in self.groupMatch:
            self._DeviceID = pack('>B', self.groupMatch[value])
        elif 1 <= int(value) <= 100:
            self._DeviceID = pack('>B', 0x40 + int(value))
        else:
            print('Invalid Device ID parameter')

    def checkSumCalc(self, cmdStr):
        checkSumStr = b'\x30' + self._DeviceID + cmdStr + b'\x03'
        checksum = 0
        for i in checkSumStr:
            checksum ^= i
        return b'\x01' + checkSumStr + pack('>B', checksum) + b'\x0D'

    def KeepAlive(self, count, timer):
        PowerCmdString = self.checkSumCalc(b'\x30\x41\x30\x36\x02\x30\x31\x44\x36')
        self.Send(PowerCmdString)
        self.KeepAliveTimer.Restart()

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x31',
            'Full': b'\x32',
            'Wide': b'\x33',
            'Zoom': b'\x34',
            'Dynamic': b'\x36',
            '1:1': b'\x37'
        }

        AspectRatioCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30' + ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.checkSumCalc(b'\x30\x43\x30\x36\x02\x30\x32\x37\x30')
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x31': 'Normal',
            b'\x32': 'Full',
            b'\x33': 'Wide',
            b'\x34': 'Zoom',
            b'\x36': 'Dynamic',
            b'\x37': '1:1'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x32'
        }

        AudioMuteCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30' + ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.checkSumCalc(b'\x30\x43\x30\x36\x02\x30\x30\x38\x44')
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x32': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x30\x30\x31\x45\x30\x30\x30\x31')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)  # No query delay is needed based on testing on C551. Refer to NEC C551 dataviewer log1.txt

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA (RGB)': b'\x30\x31',
            'Video': b'\x30\x35',
            'YGA (YPbPr)': b'\x30\x43',
            'DisplayPort': b'\x30\x46',
            'HDMI 1': b'\x31\x31',
            'HDMI 2': b'\x31\x32',
            'HDMI 3': b'\x38\x32',
            'MP': b'\x38\x37',
        }

        InputCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30' + ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)  # No query delay is needed based on testing on C551. Refer to NEC C551 dataviewer log1.txt

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.checkSumCalc(b'\x30\x43\x30\x36\x02\x30\x30\x36\x30')
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x30\x31': 'VGA (RGB)',
            b'\x30\x35': 'Video',
            b'\x30\x43': 'YGA (YPbPr)',
            b'\x30\x46': 'DisplayPort',
            b'\x31\x31': 'HDMI 1',
            b'\x31\x32': 'HDMI 2',
            b'\x38\x32': 'HDMI 3',
            b'\x38\x37': 'MP'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'sRGB': b'\x31',
            'High Bright': b'\x33',
            'Standard': b'\x34',
            'Cinema': b'\x35',
            'Custom 1': b'\x38',
            'Custom 2': b'\x39',
        }

        PictureModeCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30' + ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = self.checkSumCalc(b'\x30\x43\x30\x36\x02\x30\x32\x31\x41')
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            b'\x31': 'sRGB',
            b'\x33': 'High Bright',
            b'\x34': 'Standard',
            b'\x35': 'Cinema',
            b'\x38': 'Custom 1',
            b'\x39': 'Custom 2'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x34'
        }

        PowerCmdString = self.checkSumCalc(b'\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30' + ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)  # No query delay is needed based on testing on C551. Refer to NEC C551 dataviewer log1.txt

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.checkSumCalc(b'\x30\x41\x30\x36\x02\x30\x31\x44\x36')

        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x32': 'Standby (Power Save)',
            b'\x33': 'Suspend (Power Save)',
            b'\x34': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x32'
        }

        VideoMuteCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x31\x30\x42\x36\x30\x30\x30' + ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)  # No query delay is needed based on testing on C551. Refer to NEC C551 dataviewer log1.txt

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = self.checkSumCalc(b'\x30\x43\x30\x36\x02\x31\x30\x42\x36')
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            b'\x31': 'On',
            b'\x32': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.checkSumCalc(b'\x30\x45\x30\x41\x02\x30\x30\x36\x32\x30\x30' + hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)  # No query delay is needed based on testing on C551. Refer to NEC C551 dataviewer log1.txt
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.checkSumCalc(b'\x30\x43\x30\x36\x02\x30\x30\x36\x32')
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID[0] == 42 or 49 <= self._DeviceID[0] <= 58:
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

        self.Error(['An error occurred.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False


        if self.ConnectionType == 'Ethernet' and self.KeepAliveTimer:
            self.KeepAliveTimer.Pause()
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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
        self.KeepAliveTimer.Pause()
        self.OnDisconnected()

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.KeepAliveTimer = Timer(600, self.KeepAlive)
        return result

