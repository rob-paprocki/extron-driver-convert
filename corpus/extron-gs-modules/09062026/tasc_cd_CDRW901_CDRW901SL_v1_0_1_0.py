from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack
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
            'AutoReady': { 'Status': {}},
            'CurrentTrack': { 'Status': {}},
            'CurrentTrackTime': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FadeInTime': { 'Status': {}},
            'FadeOutTime': { 'Status': {}},
            'Index': { 'Status': {}},
            'Pitch': { 'Status': {}},
            'PitchControl': { 'Status': {}},
            'Record': { 'Status': {}},
            'Repeat': { 'Status': {}},
            'Transports': { 'Status': {}},
            }

        self.Header = b'\x0A\x30'





                    

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x0A\x30\x42\x36\x30([\x30]|[\x31])\x0D'), self.__MatchAutoReady, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x44\x37([\x30-\x39]{4})([\x30-\x39]{6})\x30\x30\x0D'), self.__MatchCurrentTrack, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x44\x30([\x30-\x38]{2})\x0D'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x43\x43\x30([\x30]|[\x31])\x0D'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x41\x45([\x30-\x39]{2})([\x30-\x39]{2})\x0D'), self.__MatchFadeInTime, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x42\x35([\x30]|[\x31])\x0D'), self.__MatchPitch, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x41\x35([\x30-\x39]{4})\x0D'), self.__MatchPitchControl, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x42\x37([\x30]|[\x31])\x0D'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'\x0A\x30\x46(\x30|\x32)\x0D'), self.__MatchError, None)




    def SetAutoReady(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x30\x31', 
            'Off' : b'\x30\x30'
        }

        AutoReadyCmdString = self.Header + b'\x33\x36' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('AutoReady', AutoReadyCmdString, value, qualifier)
    def UpdateAutoReady(self, value, qualifier):

        AutoReadyCmdString = self.Header + b'\x33\x36\x46\x46\x0D'
        self.__UpdateHelper('AutoReady', AutoReadyCmdString, value, qualifier)

    def __MatchAutoReady(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoReady', value, None)

    def UpdateCurrentTrack(self, value, qualifier):

        CurrentTrackCmdString = self.Header + b'\x35\x37\x0D'
        self.__UpdateHelper('CurrentTrack', CurrentTrackCmdString, value, qualifier)


    def __MatchCurrentTrack(self, match, tag):

        TrackNumValue = match.group(1).decode()
        TrackTimeValue = match.group(2).decode()
        TrueTrackNumValue = int('{0}{1}{2}{3}'.format(TrackNumValue[2],TrackNumValue[3],TrackNumValue[0],TrackNumValue[1]))
        TrueTrackTimeValue = float('{0}{1}{2}{3}.{4}{5}'.format(TrackTimeValue[3],TrackTimeValue[2],TrackTimeValue[0],TrackTimeValue[1],TrackTimeValue[4],TrackTimeValue[5]))
        if 1 <= TrueTrackNumValue <= 999:
            self.WriteStatus('CurrentTrack', TrueTrackNumValue, None)
        else:
            self.Discard('Invalid Command')

        if 0.01 <= TrueTrackTimeValue <= 9999.59:
            self.WriteStatus('CurrentTrackTime', TrueTrackTimeValue, None)
        else:
            self.Discard('Invalid Command')

    def UpdateCurrentTrackTime(self, value, qualifier):

        self.UpdateCurrentTrack(value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = self.Header + b'\x35\x30\x0D'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00' : 'No Disc',
            '01' : 'Tray In Motion', 
            '02' : 'Tray Open', 
            '10' : 'Stop', 
            '11' : 'Play', 
            '12' : 'Ready', 
            '80' : 'Monitor', 
            '81' : 'Recording', 
            '82' : 'Record Ready', 
            '83' : 'TOC Writing'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x30\x30',
            'Off' : b'\x30\x31'
        }

        ExecutiveModeCmdString = self.Header + b'\x34\x43' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def UpdateExecutiveMode(self, value, qualifier):


        ExecutiveModeCmdString = self.Header + b'\x34\x43\x46\x46\x0D'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0' : 'On', 
            '1' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFadeInTime(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 30
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if len(str(value)) == 2:
                Temp1 = str(value)[0]
                Temp2 = str(value)[1]
                FadeInTimeCmdString = self.Header + b'\x32\x45\x30\x30' + pack('BB', int(Temp1), int(Temp2)) + b'\x0D'
                self.__SetHelper('FadeInTime', FadeInTimeCmdString, value, qualifier)
            elif len(str(value)) == 1:
                FadeInTimeCmdString = self.Header + b'\x32\x45\x30\x30\x30' + pack('B', value) + b'\x0D'
                self.__SetHelper('FadeInTime', FadeInTimeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFadeInTime')
        else:
            self.Discard('Invalid Command for SetFadeInTime')
    def UpdateFadeInTime(self, value, qualifier):

        FadeInTimeCmdString = self.Header + b'\x32\x45\x46\x46\x0D'
        self.__UpdateHelper('FadeInTime', FadeInTimeCmdString, value, qualifier)

    def __MatchFadeInTime(self, match, tag):

        ValueIn = int(match.group(1).decode())
        self.WriteStatus('FadeInTime', ValueIn, None)

        ValueOut = int(match.group(2).decode())
        self.WriteStatus('FadeOutTime', ValueOut, None)

    def SetFadeOutTime(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 30
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if len(str(value)) == 2:
                Temp1 = str(value)[0]
                Temp2 = str(value)[1]
                FadeOutTimeCmdString = self.Header + b'\x32\x45\x30\x31' + pack('BB', int(Temp1), int(Temp2)) + b'\x0D'
                self.__SetHelper('FadeOutTime', FadeOutTimeCmdString, value, qualifier)
            elif len(str(value)) == 1:
                FadeOutTimeCmdString = self.Header + b'\x32\x45\x30\x31\x30' + pack('B', value) + b'\x0D'
                self.__SetHelper('FadeOutTime', FadeOutTimeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFadeOutTime')
        else:
            self.Discard('Invalid Command for SetFadeOutTime')
    def UpdateFadeOutTime(self, value, qualifier):

        self.UpdateFadeInTime(value, None)

    def SetIndex(self, value, qualifier):

        ValueStateValues = {
            'Next'     : b'\x31\x30', 
            'Previous' : b'\x31\x31'
        }

        IndexCmdString = self.Header + b'\x31\x41' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Index', IndexCmdString, value, qualifier)


    def SetPitch(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x30\x31', 
            'Off' : b'\x30\x30'
        }

        PitchCmdString = self.Header + b'\x33\x35' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Pitch', PitchCmdString, value, qualifier)
    def UpdatePitch(self, value, qualifier):

        PitchCmdString = self.Header + b'\x33\x35\x46\x46\x0D'
        self.__UpdateHelper('Pitch', PitchCmdString, value, qualifier)

    def __MatchPitch(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Pitch', value, None)

    def SetPitchControl(self, value, qualifier):

        ValueConstraints = {
            'Min' : -16.0,
            'Max' : 16.0
            }
        PitchStatus = self.ReadStatus('Pitch', qualifier)
        if PitchStatus == 'On':
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                Stringx = '{0:.2f}'.format(value)
                if len(Stringx) == 6 and Stringx[0] == '-' and Stringx[5] == '0':
                    String = Stringx[0:5]
                elif len(Stringx) == 5 and Stringx[0] != '-' and Stringx[4] == '0':
                    String = Stringx[0:4]
                elif len(Stringx) == 5 and Stringx[0] == '-' and Stringx[4] == '0':
                    String = Stringx[0:4]
                elif len(Stringx) == 4 and Stringx[0] != '-' and Stringx[3] == '0':
                    String = Stringx[0:3]
                else:
                    String = Stringx
                if String[0] == '-':
                    if len(String) == 5:
                        PitchControlCmdString = self.Header + b'\x32\x35' + pack('BB', int(String[2]), int(String[4])) + b'\x31' + pack('B', int(String[1])) + b'\x0D'
                        self.__SetHelper('PitchControl', PitchControlCmdString, value, qualifier)
                    elif len(String) == 4:
                        PitchControlCmdString = self.Header + b'\x32\x35' + pack('BB', int(String[1]), int(String[3])) + b'\x31\x30\x0D'
                        self.__SetHelper('PitchControl', PitchControlCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetPitchControl')
                else:
                    if len(String) == 4:
                        PitchControlCmdString = self.Header + b'\x32\x35' + pack('BB', int(String[1]), int(String[3])) + b'\x30' + pack('B', int(String[0])) + b'\x0D'
                        self.__SetHelper('PitchControl', PitchControlCmdString, value, qualifier)
                    elif len(String) == 3:
                        PitchControlCmdString = self.Header + b'\x32\x35' + pack('BB', int(String[0]), int(String[2])) + b'\x30\x30\x0D'
                        self.__SetHelper('PitchControl', PitchControlCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetPitchControl')
            else:
                self.Discard('Invalid Command for SetPitchControl')
        else:
            self.Discard('Invalid Command for SetPitchControl')

    def UpdatePitchControl(self, value, qualifier):

        PitchControlCmdString = self.Header + b'\x32\x35\x46\x46\x0D'
        self.__UpdateHelper('PitchControl', PitchControlCmdString, value, qualifier)

    def __MatchPitchControl(self, match, tag):

        valuex = match.group(1).decode()
        String = str(valuex)
        if String[2] == '1':
            value = float('-{0}{1}.{2}'.format(String[3], String[0], String[1]))
        else:
            value = float('{0}{1}.{2}'.format(String[3], String[0], String[1]))
        if -16.0 <= value <= 16.0:
            self.WriteStatus('PitchControl', value, None)
        else:
            self.Discard('Invalid Command')

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Ready'  : b'\x30\x31', 
            'Track Mark'    : b'\x30\x32',
            'Input Monitor' : b'\x30\x33'
        }

        RecordCmdString = self.Header + b'\x31\x33' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Record', RecordCmdString, value, qualifier)


    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x30\x31', 
            'Off' : b'\x30\x30'
        }

        RepeatCmdString = self.Header + b'\x33\x37' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)
    def UpdateRepeat(self, value, qualifier):

        RepeatCmdString = self.Header + b'\x33\x37\x46\x46\x0D'
        self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Repeat', value, None)

    def SetTransports(self, value, qualifier):

        ValueStateValues = {
            'Play'       : b'\x31\x32', 
            'Stop'       : b'\x31\x30', 
            'Previous'   : b'\x31\x41\x30\x31', 
            'Next'       : b'\x31\x41\x30\x30', 
            'Open/Close' : b'\x31\x38', 
            'Ready'      : b'\x30\x31\x31\x34'
        }

        TransportsCmdString = self.Header + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Transports', TransportsCmdString, value, qualifier)


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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
            
            self.Send(commandstring)

            

    def __MatchError(self, match, tag):

        self.Error(['Illegal Command'])

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

