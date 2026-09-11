from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self._DeviceID = '01'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ButtonLock': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuLock': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerLock': { 'Status': {}},
            'RemoteControl': { 'Status': {}},
            'Volume': { 'Status': {}},
            }




        



                    

                        
        if self.Unidirectional == 'False' and self._DeviceID != '99':
            self.AddMatchString(re.compile(b'k[0-9]{2}rg00(0|1)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}rl00(0|1)\r'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}rh0([0-9a-bA-B]{2})'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}rm00(0|1)\r'), self.__MatchMenuLock, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}rk00(0|1)\r'), self.__MatchPowerLock, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}rj00(0|1)\r'), self.__MatchRemoteControl, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}rf([0-9]{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'k[0-9]{2}n\r'), self.__MatchError, None)
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 1 <= int(value) <= 98:
            self._DeviceID = '{0:02d}'.format(int(value))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full'    : '000', 
            'Normal'  : '001', 
            'Custom'  : '002', 
            'Dynamic' : '003', 
            'Real'    : '004'
        }

        AspectRatioCmdString = 'k{}sM{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '001', 
            'Off' : '000'
        }

        AudioMuteCmdString = 'k{}sQ{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'k{}gg000\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On'  : '001', 
            'Off' : '000'
        }

        ButtonLockCmdString = 'k{}sR{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        ButtonLockCmdString = 'k{}gl000\r'.format(self._DeviceID)
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonLock', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'ATV'           : '000', 
            'DTV'           : '010', 
            'AV'            : '001', 
            'S-Video 1'     : '002', 
            'S-Video 2'     : '012', 
            'YPbPr'         : '003', 
            'HDMI'          : '004', 
            'HDMI 1'        : '014', 
            'HDMI 2'        : '024', 
            'HDMI 3'        : '034', 
            'HDMI 4'        : '044', 
            'DVI'           : '005', 
            'VGA'           : '006', 
            'OPS 1'         : '007', 
            'OPS 2'         : '017', 
            'USB'           : '008', 
            'DisplayPort'   : '009', 
            'Main(Android)' : '00A', 
            'SDI 1'         : '00B', 
            'SDI 2'         : '01B'
        }

        InputCmdString = 'k{}sB{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'k{}gh000\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '00' : 'ATV', 
            '10' : 'DTV', 
            '01' : 'AV', 
            '02' : 'S-Video 1', 
            '12' : 'S-Video 2', 
            '03' : 'YPbPr', 
            '04' : 'HDMI', 
            '14' : 'HDMI 1', 
            '24' : 'HDMI 2', 
            '34' : 'HDMI 3', 
            '44' : 'HDMI 4', 
            '05' : 'DVI', 
            '06' : 'VGA', 
            '07' : 'OPS 1', 
            '17' : 'OPS 2', 
            '08' : 'USB', 
            '09' : 'DisplayPort', 
            '0A' : 'Main(Android)', 
            '0B' : 'SDI 1', 
            '1B' : 'SDI 2'
        }

        value = ValueStateValues[match.group(1).decode().upper()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : '000', 
            '1' : '001', 
            '2' : '002', 
            '3' : '003', 
            '4' : '004', 
            '5' : '005', 
            '6' : '006', 
            '7' : '007', 
            '8' : '008', 
            '9' : '009'
        }

        KeypadCmdString = 'k{}sT{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuLock(self, value, qualifier):

        ValueStateValues = {
            'On'  : '001', 
            'Off' : '000'
        }

        MenuLockCmdString = 'k{}sS{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def UpdateMenuLock(self, value, qualifier):

        MenuLockCmdString = 'k{}gm000\r'.format(self._DeviceID)
        self.__UpdateHelper('MenuLock', MenuLockCmdString, value, qualifier)

    def __MatchMenuLock(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MenuLock', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '006', 
            'Up'    : '000', 
            'Down'  : '001', 
            'Left'  : '002', 
            'Right' : '003', 
            'Enter' : '004', 
            'Exit'  : '007'
        }

        MenuNavigationCmdString = 'k{}sU{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '001', 
            'Off' : '000'
        }

        PowerCmdString = 'k{}sA{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def SetPowerLock(self, value, qualifier):

        ValueStateValues = {
            'On'  : '001', 
            'Off' : '000'
        }

        PowerLockCmdString = 'k{}sO{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('PowerLock', PowerLockCmdString, value, qualifier)

    def UpdatePowerLock(self, value, qualifier):


        PowerLockCmdString = 'k{}gk000\r'.format(self._DeviceID)
        self.__UpdateHelper('PowerLock', PowerLockCmdString, value, qualifier)

    def __MatchPowerLock(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerLock', value, None)

    def SetRemoteControl(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '001', 
            'Disable' : '000'
        }

        RemoteControlCmdString = 'k{}sV{}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('RemoteControl', RemoteControlCmdString, value, qualifier)

    def UpdateRemoteControl(self, value, qualifier):

        RemoteControlCmdString = 'k{}gj000\r'.format(self._DeviceID)
        self.__UpdateHelper('RemoteControl', RemoteControlCmdString, value, qualifier)

    def __MatchRemoteControl(self, match, tag):

        ValueStateValues = {
            '1' : 'Enable', 
            '0' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RemoteControl', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'k{}sP{:03d}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'k{}gf000\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '99':
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

        self.Error(['The command is not valid.'])

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
        
        #check incoming data if it matched any expected data from device module
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

