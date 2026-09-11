from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters':['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters':['Device ID'], 'Status': {}},
            'Input': {'Parameters':['Device ID'], 'Status': {}},
            'Keypad': {'Parameters':['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters':['Device ID'], 'Status': {}},
            'Power': {'Parameters':['Device ID'], 'Status': {}},
            'TileMode': {'Parameters':['Device ID', 'Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters':['Device ID', 'Tile ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9a-f]{2}) OK(01|02)x',re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'b ([0-9a-f]{2}) OK(20|40|60|70|A0|D0|E0)x',re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'm ([0-9a-f]{2}) OK0(0|1)x',re.I), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'a ([0-9a-f]{2}) OK0(1|0)x',re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'(u|c|b|a) [0-9a-f]{2} NG(.*)x',re.I), self.__MatchError, None)
        
        self.regexSet = re.compile(b'(OK|NG)[0-9a-f]{2}x')

    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return '00'
        elif 1 <= int(ID) <= 99:
            return '{0:02X}'.format(int(ID))
        else:
            self.Error(['Invalid Device ID provided'])
      
    def SetAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        AspectRatioState = {
            '4:3' : '01', 
            '16:9' : '02'
            }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(ID, AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        AspectRatioCmdString = 'kc {0} FF\r'.format(ID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ID = int(match.group(1).decode(), 16)

        AspectRatioState = {
            '01' : '4:3', 
            '02' : '16:9'
            }

        if 0 <= ID <= 99:
            value = AspectRatioState[match.group(2).decode()]
            self.WriteStatus('AspectRatio', value, {'Device ID' : str(ID)})
        else:
            self.Error(['Aspect Ratio : Invalid Response'])

    def SetAutoImage(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        AutoImageCmdString = 'ju {0} 01\r'.format(ID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        ExecutiveModeState = {
            'On' : '01', 
            'Off' : '00'
            }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(ID, ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        ExecutiveModeCmdString = 'km {0} FF\r'.format(ID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ID = int(match.group(1).decode(), 16)

        ExecutiveModeState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        if 0 <= ID <= 99:
            value = ExecutiveModeState[match.group(2).decode()]
            self.WriteStatus('ExecutiveMode', value, {'Device ID' : str(ID)})
        else:
            self.Error(['Executive Mode : Invalid Response'])

    def SetInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        InputState = {
            'AV' : '20', 
            'Component' : '40', 
            'RGB' : '60', 
            'DVI-D' : '70', 
            'HDMI' : 'A0', 
            'DisplayPort' : 'D0'
            }

        InputCmdString = 'xb {0} {1}\r'.format(ID, InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        InputCmdString = 'xb {0} FF\r'.format(ID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ID = int(match.group(1).decode(), 16)

        InputState = {
            '20' : 'AV', 
            '40' : 'Component', 
            '60' : 'RGB', 
            '70' : 'DVI-D', 
            'A0' : 'HDMI', 
            'D0' : 'DisplayPort'
            }

        if 0 <= ID <= 99:
            value = InputState[match.group(2).decode()]
            self.WriteStatus('Input', value, {'Device ID' : str(ID)})
        else:
            self.Error(['Input : Invalid Response'])

    def SetKeypad(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        KeypadState = {
            '0' : '10', 
            '1' : '11', 
            '2' : '12', 
            '3' : '13', 
            '4' : '14', 
            '5' : '15', 
            '6' : '16', 
            '7' : '17', 
            '8' : '18', 
            '9' : '19'
            }

        KeypadCmdString = 'mc {0} {1}\r'.format(ID, KeypadState[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        MenuNavigationState = {
            'Up'    : '40', 
            'Down'  : '41', 
            'Left'  : '07', 
            'Right' : '06', 
            'Enter' : '44', 
            'Menu'  : '43', 
            'Back'  : '28', 
            'Exit'  : '5B'
            }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(ID, MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        PowerState = {
            'On' : '01', 
            'Off' : '00'
            }

        PowerCmdString = 'ka {0} {1}\r'.format(ID, PowerState[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        PowerCmdString = 'ka {0} FF\r'.format(ID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ID = int(match.group(1).decode(), 16)

        PowerState = {
            '1' : 'On', 
            '0' : 'Off'
            }

        value = PowerState[match.group(2).decode()]

        if 0 <= ID <= 99:
            self.WriteStatus('Power', value, {'Device ID' : str(ID)})
        else:
            self.Error(['Power : Invalid Response'])

    def SetTileMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        column = int(qualifier['Column'])
        row = int(qualifier['Row'])

        if 1 <= row <= 15 and 1 <= column <= 15:
            TileModeCmdString = 'dd {0} {1:X}{2:X}\r'.format(ID, column, row)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        TileID = int(qualifier['Tile ID'])

        if 1 <= TileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(ID, TileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetTilePosition')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'OK' in response:
            return response
        elif 'NG' in response:
            err = 'Error in command: {0}'.format(sourceCmdName)
            self.Error([err])
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{0} : Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif 'Broadcast' in [qualifier['Device ID']]:
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

        State = {
            'u' : 'Auto Image',
            'c' : 'Aspect Ratio, Menu Navigation or Keypad',
            'b' : 'Input',
            'a' : 'Power',
            }

        temp1 = State[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1,temp2)
        self.Error([value])

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



class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False        
        self.Models = {}
        self.DeviceID = '1'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'TileMode': {'Parameters':['Column', 'Row'], 'Status': {}},
            'TilePosition': {'Parameters':['Tile ID'], 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99: 
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            self.Error(['Device ID Out of Range'])
    def SetAspectRatio(self, value, qualifier):

        AspectRatio = {
            '4:3' : '01', 
            '16:9' : '02'
            }

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self.DeviceID, AspectRatio[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ju {0} 01\r'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On' : '01', 
            'Off' : '00'
            }

        ExecutiveModeCmdString = 'km {0} {1}\r'.format(self.DeviceID, ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        InputState = {
            'AV' : '20', 
            'Component' : '40', 
            'RGB' : '60', 
            'DVI-D' : '70', 
            'HDMI' : 'A0', 
            'DisplayPort' : 'D0'
            }

        InputCmdString = 'xb {0} {1}\r'.format(self.DeviceID, InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetKeypad(self, value, qualifier):

        KeypadState = {
            '0' : '10', 
            '1' : '11', 
            '2' : '12', 
            '3' : '13', 
            '4' : '14', 
            '5' : '15', 
            '6' : '16', 
            '7' : '17', 
            '8' : '18', 
            '9' : '19'
            }

        KeypadCmdString = 'mc {0} {1}\r'.format(self.DeviceID, KeypadState[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up' : '40', 
            'Down' : '41', 
            'Left' : '07', 
            'Right' : '06', 
            'Enter' : '44', 
            'Menu' : '43', 
            'Back' : '28', 
            'Exit' : '5B'
            }

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self.DeviceID, MenuNavigationState[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = 'ka {0} 00\r'.format(self.DeviceID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)
    def SetTileMode(self, value, qualifier):

        column = int(qualifier['Column'])
        row = int(qualifier['Row'])

        if 1 <= row <= 15 and 1 <= column <= 15:
            TileModeCmdString = 'dd {0} {1:X}{2:X}\r'.format(self.DeviceID, column, row)
            self.__SetHelper('TileMode', TileModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')
    def SetTilePosition(self, value, qualifier):

        TileID = int(qualifier['Tile ID'])

        if 1 <= TileID <= 225:
            TilePositionCmdString = 'di {0} {1:02X}\r'.format(self.DeviceID, TileID)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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