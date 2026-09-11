from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
            'INSIGHT 4K Quad': self.dpl_1_3438_quad,
            'INSIGHT 4K Dual LED': self.dpl_1_3438_dual,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': {'Status': {}},
            '3DDominance': {'Status': {}},
            '3DFormat': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteLock': {'Status': {}},
            'Shutter': {'Status': {}},
            'VideoMute': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ack 3d\.enable = (on|off)\r'), self.__Match3D, None)
            self.AddMatchString(re.compile(b'ack 3d\.dominance = (left|right)\r'), self.__Match3DDominance, None)
            self.AddMatchString(re.compile(b'ack 3d\.format = (off|auto|seq|tab|sbs|fpack|dplr|dpew)\r'), self.__Match3DFormat, None)
            self.AddMatchString(re.compile(b'ack freeze = (on|off)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'ack input = ([012367])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ack lamp([1-4])\.hours = (\d{1,5}):\d{1,2}\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'ack osd\.enable = (on|off)\r'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'ack power = (on|off)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'ack ir\.enable = (on|off)\r'), self.__MatchRemoteLock, None)
            self.AddMatchString(re.compile(b'ack shutter = (on|off|open|close)\r'), self.__MatchShutter, None)
            self.AddMatchString(re.compile(b'ack pic\.mute = (on|off)\r'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'nack'), self.__MatchError, None)

    def Set3D(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        CmdString = '*3d.enable = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('3D', CmdString, value, qualifier)

    def Update3D(self, value, qualifier):

        CmdString = '*3d.enable ?\r'
        self.__UpdateHelper('3D', CmdString, value, qualifier)

    def __Match3D(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('3D', value, None)

    def Set3DDominance(self, value, qualifier):

        ValueStateValues = {
            'Left': 'left',
            'Right': 'right'
        }

        DominanceCmdString = '*3d.dominance = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DDominance', DominanceCmdString, value, qualifier)

    def Update3DDominance(self, value, qualifier):

        DominanceCmdString = '*3d.dominance ?\r'
        self.__UpdateHelper('3DDominance', DominanceCmdString, value, qualifier)

    def __Match3DDominance(self, match, tag):

        ValueStateValues = {
            'left': 'Left',
            'right': 'Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('3DDominance', value, None)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Off': 'off',
            'Auto': 'auto',
            'Sequential': 'seq',
            'Top and Bottom': 'tab',
            'Side by Side (Half)': 'sbs',
            'Frame Packing': 'fpack',
            'Dual Pipe Left/Right': 'dplr',
            'Dual Pipe East/West': 'dpew'
        }

        FormatCmdString = '*3d.format = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier):

        FormatCmdString = '*3d.format ?\r'
        self.__UpdateHelper('3DFormat', FormatCmdString, value, qualifier)

    def __Match3DFormat(self, match, tag):

        ValueStateValues = {
            'off': 'Off',
            'auto': 'Auto',
            'seq': 'Sequential',
            'tab': 'Top and Bottom',
            'sbs': 'Side by Side (Half)',
            'fpack': 'Frame Packing',
            'dplr': 'Dual Pipe Left/Right',
            'dpew': 'Dual Pipe East/West'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('3DFormat', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        FreezeCmdString = '*freeze = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '*freeze ?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI A': '0',
            'HDMI B': '1',
            'DisplayPort A': '2',
            'DisplayPort B': '3',
            'DisplayPort A+B Dual Pipe (East/West)': '6',
            'DisplayPort A+B Dual Pipe (Left/Right)': '7'
        }

        InputCmdString = '*input = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*input ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'HDMI A',
            '1': 'HDMI B',
            '2': 'DisplayPort A',
            '3': 'DisplayPort B',
            '6': 'DisplayPort A+B Dual Pipe (East/West)',
            '7': 'DisplayPort A+B Dual Pipe (Left/Right)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '82',
            '1': '42',
            '2': '46',
            '3': '50',
            '4': '55',
            '5': '59',
            '6': '63',
            '7': '68',
            '8': '72',
            '9': '76'
        }

        KeypadCmdString = '*ir.key = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        if qualifier['Lamp'] in self.LampStates:
            LampUsageCmdString = '*lamp{}.hours ?\r'.format(qualifier['Lamp'])
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, tag):

        qualifier = {'Lamp': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '9',
            'Up': '11',
            'Down': '33',
            'Left': '18',
            'Right': '26',
            'OK': '25',
            'Exit': '40'
        }

        MenuNavigationCmdString = '*ir.key = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        OnScreenDisplayCmdString = '*osd.enable = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = '*osd.enable ?\r'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIP(self, value, qualifier):

        PIPCmdString = '*ir.key = 112\r'
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '*ir.key = 113\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        PowerCmdString = '*power = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '*power ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        RemoteLockCmdString = '*ir.enable = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def UpdateRemoteLock(self, value, qualifier):

        RemoteLockCmdString = '*ir.enable ?\r'
        self.__UpdateHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def __MatchRemoteLock(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RemoteLock', value, None)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open': 'open',
            'Close': 'close'
        }

        ShutterCmdString = '*shutter = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = '*shutter ?\r'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            'off': 'Open',
            'open': 'Open',
            'on': 'Close',
            'close': 'Close'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        VideoMuteCmdString = '*pic.mute = {}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '*pic.mute ?\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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

        self.Error(['Error: Command not accepted'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def dpl_1_3438_dual(self):
        self.LampStates = ['1', '2']


    def dpl_1_3438_quad(self):
        self.LampStates = ['1', '2', '3', '4']

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