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
            'AutoAdjust': {'Status': {}},
            'AudioMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIPAdjust': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00ASP([\x00-\x03])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00MUT([\x00\x01])\x08'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00SCM([\x00-\x04])\x08'), self.__MatchDisplayMode, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00MIN([\x00\x09-\x0E\x10])\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00PSC([\x00-\x07])\x08'), self.__MatchPIPAdjust, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00PIN([\x00\x09-\x0E\x10])\x08'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00PPO([\x00-\x03])\x08'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00POW([\x00\x01])\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07[\x01-\x19]\x00VOL([\x00-\x64])\x08'), self.__MatchVolume, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 25:
            self._DeviceID = int(value)
        else:
            self.Error(['Invalid DeviceID, range is from 1 to 25 or Broadcast'])
            

    def SetAspectRatio(self, value, qualifier):

        Values = {
            'Native': 0,
            'Fill': 1,
            'Pillarbox/4:3': 2,
            'Letterbox': 3
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'ASP', Values[value], 8)

        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'ASP', 8)
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        Values = {
            0: 'Native',
            1: 'Fill',
            2: 'Pillarbox/4:3',
            3: 'Letterbox'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        Values = {
            'On': 1,
            'Off': 0
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'MUT', Values[value], 8)
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'MUT', 8)
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        Values = {
            1: 'On',
            0: 'Off'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoAdjust(self, value, qualifier):

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'RCU', 28, 8)
        self.__SetHelper('AutoAdjust', CmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        Values = {
            'User': 0,
            'Sport': 1,
            'Game': 2,
            'Cinema': 3,
            'Vivid': 4
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'SCM', Values[value], 8)
        self.__SetHelper('DisplayMode', CmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'SCM', 8)
        self.__UpdateHelper('DisplayMode', CmdString, value, qualifier)

    def __MatchDisplayMode(self, match, tag):

        Values = {
            0: 'User',
            1: 'Sport',
            2: 'Game',
            3: 'Cinema',
            4: 'Vivid'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('DisplayMode', value, None)

    def SetFreeze(self, value, qualifier):

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'RCU', 24, 8)
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        Values = {
            'VGA': 0,
            'HDMI 1': 9,
            'HDMI 2': 10,
            'HDMI 3': 11,
            'HDMI 4': 12,
            'DisplayPort': 13,
            'IPC/OPS': 14,
            'DisplayPort 2': 16
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'MIN', Values[value], 8)
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'MIN', 8)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        Values = {
            0: 'VGA',
            9: 'HDMI 1',
            10: 'HDMI 2',
            11: 'HDMI 3',
            12: 'HDMI 4',
            13: 'DisplayPort',
            14: 'IPC/OPS',
            16: 'DisplayPort 2'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        Values = {
            'Menu': 0,
            'Info': 1,
            'Up': 2,
            'Down': 3,
            'Left': 4,
            'Right': 5,
            'Enter': 6,
            'Exit': 7
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'RCU', Values[value], 8)
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPIPAdjust(self, value, qualifier):

        Values = {
            'Off': 0,
            'Small': 1,
            'Medium': 2,
            'Large': 3,
            'Side by Side': 4,
            'PbP Portrait': 5,
            '3 Windows': 6,
            '4 Windows': 7
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'PSC', Values[value], 8)
        self.__SetHelper('PIPAdjust', CmdString, value, qualifier)

    def UpdatePIPAdjust(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'PSC', 8)
        self.__UpdateHelper('PIPAdjust', CmdString, value, qualifier)

    def __MatchPIPAdjust(self, match, tag):

        Values = {
            0: 'Off',
            1: 'Small',
            2: 'Medium',
            3: 'Large',
            4: 'Side by Side',
            5: 'PbP Portrait',
            6: '3 Windows',
            7: '4 Windows'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('PIPAdjust', value, None)

    def SetPIPInput(self, value, qualifier):

        Values = {
            'VGA': 0,
            'HDMI 1': 9,
            'HDMI 2': 10,
            'HDMI 3': 11,
            'HDMI 4': 12,
            'DisplayPort': 13,
            'IPC/OPS': 14,
            'DisplayPort 2': 16
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'PIN', Values[value], 8)

        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'PIN', 8)
        self.__UpdateHelper('PIPInput', CmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        Values = {
            0: 'VGA',
            9: 'HDMI 1',
            10: 'HDMI 2',
            11: 'HDMI 3',
            12: 'HDMI 4',
            13: 'DisplayPort',
            14: 'IPC/OPS',
            16: 'DisplayPort 2'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPosition(self, value, qualifier):

        Values = {
            'Bottom Left': 0,
            'Bottom Right': 1,
            'Top Left': 2,
            'Top Right': 3,
        }

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'PPO', Values[value], 8)

        self.__SetHelper('PIPPosition', CmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'PPO', 8)
        self.__UpdateHelper('PIPPosition', CmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        Values = {
            0: 'Bottom Left',
            1: 'Bottom Right',
            2: 'Top Left',
            3: 'Top Right'
        }

        value = Values[ord(match.group(1))]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSwap(self, value, qualifier):

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'SWA', 0, 8)
        self.__SetHelper('PIPSwap', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        Values = {'On': 1, 'Off': 0}
        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'POW', Values[value], 8)

        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'POW', 8)

        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        Values = {
            1: 'On',
            0: 'Off'
        }

        self.WriteStatus('Power', Values[ord(match.group(1))], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'VOL', value, 8)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CmdString = pack('3B3sB', 7, self.DeviceID, 1, b'VOL', 8)
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        CmdString = pack('3B3s2B', 7, self.DeviceID, 2, b'ZOM', {'In': 0, 'Out': 1}[value], 8)

        self.__SetHelper('Zoom', CmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

