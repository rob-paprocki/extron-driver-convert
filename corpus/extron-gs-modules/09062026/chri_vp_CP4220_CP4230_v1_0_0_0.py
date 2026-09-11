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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Channel': {'Status': {}},
            'Focus': {'Status': {}},
            'Input': {'Parameters': ['Channel'],'Status': {}},
            'LampUsage': {'Status': {}},
            'LensShiftHorizontal': {'Status': {}},
            'LensShiftVertical': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(CHA!1([0-9]{2})\)'), self.__MatchChannel, None)
            self.AddMatchString(re.compile(b'\(SIN!00(0|1|2|3|4|5) .*?\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(LPH!(\d+)\)'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\(PWR!0(00|01|03|11|10) .*?\)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!0000(0|1)\)'), self.__MatchVideoMute, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(LLM+AUTO 1)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        if 1 <= int(value) <= 64:
            ChannelCmdString = '(CHA 1{0:02})'.format(int(value))
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = '(CHA?)'
        self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)

    def __MatchChannel(self, match, tag):

        ChannelStates = {
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8',
            '09': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20',
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24',
            '25': '25',
            '26': '26',
            '27': '27',
            '28': '29',
            '30': '30',
            '31': '31',
            '32': '32',
            '33': '33',
            '34': '34',
            '35': '35',
            '36': '36',
            '37': '37',
            '38': '38',
            '39': '39',
            '40': '40',
            '41': '41',
            '42': '42',
            '43': '43',
            '44': '44',
            '45': '45',
            '46': '46',
            '47': '47',
            '48': '48',
            '49': '49',
            '50': '50',
            '51': '51',
            '52': '52',
            '53': '53',
            '54': '54',
            '55': '55',
            '56': '56',
            '57': '57',
            '58': '58',
            '59': '59',
            '60': '60',
            '61': '61',
            '62': '62',
            '63': '63',
            '64': '64'
            }

        value = ChannelStates[match.group(1).decode()]
        self.WriteStatus('Channel', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 'STRT 1)',
            'Near': 'STRT -1)',
            'Stop': 'STOP)'
        }

        FocusCmdString = '(FCS+' + ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '292-A': 1,
            '292-B': 2,
            '292-Dual': 3,
            'DVI-A': 4,
            'DVI-B': 5,
            'DVI-Dual/Twin': 6
        }

        Channel = qualifier['Channel']
        if 1 <= int(Channel) <= 64:
            InputCmdString = '(SIN+C1{0:02} {1})'.format(int(Channel), ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': '292-A',
            '1': '292-B',
            '2': '292-Dual',
            '3': 'DVI-A',
            '4': 'DVI-B',
            '5': 'DVI-Dual/Twin'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '(LPH?)'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetLensShiftHorizontal(self, value, qualifier):

        ValueStateValues = {
            'Right': 'STRT 1)',
            'Left': 'STRT -1)',
            'Stop': 'STOP)'
        }

        LensShiftHorizontalCmdString = '(LHO+' + ValueStateValues[value]
        self.__SetHelper('LensShiftHorizontal', LensShiftHorizontalCmdString, value, qualifier)

    def SetLensShiftVertical(self, value, qualifier):

        ValueStateValues = {
            'Up': 'STRT 1)',
            'Down': 'STRT -1)',
            'Stop': 'STOP)'
        }

        LensShiftVerticalCmdString = '(LVO+' + ValueStateValues[value]
        self.__SetHelper('LensShiftVertical', LensShiftVerticalCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 3,
            'Full Power Mode': 0
        }

        PowerCmdString = '(PWR{0})'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '(PWR?)'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '03': 'Off',
            '11': 'Warming Up',
            '10': 'Cooling Down',
            '00': 'Full Power Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0,
            'Off': 1
        }

        VideoMuteCmdString = '(SHU {0})'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '(SHU?)'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 'STRT 1)',
            'Wide': 'STRT -1)',
            'Stop': 'STOP)'
        }

        ZoomCmdString = '(ZOM+' + ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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

