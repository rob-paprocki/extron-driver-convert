from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait

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
            'AutoImage': {'Status': {}},
            'AutoSource': {'Status': {}},
            'Brightness': {'Status': {}},
            'CeilingMode': {'Status': {}},
            'ColorGain': {'Parameters': ['Color'], 'Status': {}},
            'ColorOffset': {'Parameters': ['Color'], 'Status': {}},
            'Contrast': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RearProjection': {'Status': {}},
            'Saturation': {'Status': {}},
            'TestPattern': {'Status': {}},
            'Tint': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'op aspect = ([0-6])\r', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'op auto.source = (0|1)\r', re.I), self.__MatchAutoSource, None)
            self.AddMatchString(re.compile(b'op bright = ([0-9]{1,3})\r', re.I), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'op ceil.mode = (0|1)\r', re.I), self.__MatchCeilingMode, None)
            self.AddMatchString(re.compile(b'op (red|green|blue).gain = ([0-9]{1,3})\r', re.I), self.__MatchColorGain, None)
            self.AddMatchString(re.compile(b'op (red|green|blue).off = ([0-9]{1,3})\r', re.I), self.__MatchColorOffset, None)
            self.AddMatchString(re.compile(b'op contrast = ([0-9]{1,3})\r', re.I), self.__MatchContrast, None)
            self.AddMatchString(re.compile(b'op source.sel = ([0-7])\r', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'op lamp.hours = ([0-9]{1,5})\r', re.I), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'op status.check = ([0-4])\r', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'op rear.proj = (0|1)\r', re.I), self.__MatchRearProjection, None)
            self.AddMatchString(re.compile(b'op saturate = ([0-9]{1,3})\r', re.I), self.__MatchSaturation, None)
            self.AddMatchString(re.compile(b'op tint = ([0-9]{1,3})\r', re.I), self.__MatchTint, None)
            # BEGIN AUTO GENERATION OF COMMAND DEF    def SetAspectRatio(self, value, qualifier):

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '16:10': '0',
            '16:9': '1',
            'Letterbox': '2',
            '4:3': '3',
            '4:3 Narrow': '4',
            'Square': '5',
            'Native': '6'
        }

        AspectRatioCmdString = 'op aspect = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'op aspect ?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': '16:10',
            '1': '16:9',
            '2': 'Letterbox',
            '3': '4:3',
            '4': '4:3 Narrow',
            '5': 'Square',
            '6': 'Native'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'op resync\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAutoSource(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        AutoSourceCmdString = 'op auto.source = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoSource', AutoSourceCmdString, value, qualifier)

    def UpdateAutoSource(self, value, qualifier):

        AutoSourceCmdString = 'op auto.source ?\r'
        self.__UpdateHelper('AutoSource', AutoSourceCmdString, value, qualifier)

    def __MatchAutoSource(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSource', value, None)

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 200
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = 'op bright = {0}\r'.format(value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'op bright ?\r'
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)

    def __MatchBrightness(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Brightness', value, None)

    def SetCeilingMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1',
        }

        CeilingModeCmdString = 'op ceil.mode = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CeilingMode', CeilingModeCmdString, value, qualifier)

    def UpdateCeilingMode(self, value, qualifier):

        CeilingModeCmdString = 'op ceil.mode ?\r'
        self.__UpdateHelper('CeilingMode', CeilingModeCmdString, value, qualifier)

    def __MatchCeilingMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CeilingMode', value, None)

    def SetColorGain(self, value, qualifier):

        ColorStates = {
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 200
            }
        color = ColorStates[qualifier['Color']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and qualifier['Color'] in ['Red', 'Green', 'Blue']:
            ColorGainCmdString = 'op {0}.gain = {1}\r'.format(color, value)
            self.__SetHelper('ColorGain', ColorGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorGain')

    def UpdateColorGain(self, value, qualifier):

        ColorStates = {
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue'
        }
        color = ColorStates[qualifier['Color']]
        ColorGainCmdString = 'op {0}.gain ?\r'.format(color)
        self.__UpdateHelper('ColorGain', ColorGainCmdString, value, qualifier)

    def __MatchColorGain(self, match, tag):

        ColorStates = {
            'red': 'Red',
            'green': 'Green',
            'blue': 'Blue'
        }

        qualifier = {}
        qualifier['Color'] = ColorStates[match.group(1).decode().lower()]
        value = int(match.group(2).decode())
        self.WriteStatus('ColorGain', value, qualifier)

    def SetColorOffset(self, value, qualifier):

        ColorStates = {
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 200
            }
        color = ColorStates[qualifier['Color']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and qualifier['Color'] in ['Red', 'Green', 'Blue']:
            ColorOffsetCmdString = 'op {0}.off = {1}\r'.format(color, value)
            self.__SetHelper('ColorOffset', ColorOffsetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorOffset')

    def UpdateColorOffset(self, value, qualifier):

        ColorStates = {
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue'
        }
        color = ColorStates[qualifier['Color']]
        ColorOffsetCmdString = 'op {}.off ?\r'.format(color)
        self.__UpdateHelper('ColorOffset', ColorOffsetCmdString, value, qualifier)

    def __MatchColorOffset(self, match, tag):

        ColorStates = {
            'red': 'Red',
            'green': 'Green',
            'blue': 'Blue'
        }

        qualifier = {}
        qualifier['Color'] = ColorStates[match.group(1).decode().lower()]
        value = int(match.group(2).decode())
        self.WriteStatus('ColorOffset', value, qualifier)

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 200
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ContrastCmdString = 'op contrast = {0}\r'.format(value)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = 'op contrast ?\r'
        self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)

    def __MatchContrast(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Contrast', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'RGB': '2',
            'Component 1': '3',
            'Component 2': '4',
            'S-Video': '5',
            'Video': '6',
            'SCART': '7'
        }

        InputCmdString = 'op source.sel = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'op source.sel ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'RGB',
            '3': 'Component 1',
            '4': 'Component 2',
            '5': 'S-Video',
            '6': 'Video',
            '7': 'SCART'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'op lamp.hours ?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu/ Exit Menu': 'ky menu\r',
            'Enter': 'ky enter\r',
            'Down': 'ky cur.down\r',
            'Up': 'ky cur.up\r',
            'Left': 'ky cur.left\r',
            'Right': 'ky cur.righ\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': 'ky pow.off\r',
            'On': 'ky pow.on\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'op status.check ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Warming Up',
            '2': 'On',
            '3': 'Cooling Down',
            '4': 'Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetRearProjection(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        RearProjectionCmdString = 'op rear.proj = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('RearProjection', RearProjectionCmdString, value, qualifier)

    def UpdateRearProjection(self, value, qualifier):

        RearProjectionCmdString = 'op rear.proj ?\r'
        self.__UpdateHelper('RearProjection', RearProjectionCmdString, value, qualifier)

    def __MatchRearProjection(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RearProjection', value, None)

    def SetSaturation(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 200
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SaturationCmdString = 'op saturate = {0}\r'.format(value)
            self.__SetHelper('Saturation', SaturationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaturation')

    def UpdateSaturation(self, value, qualifier):

        SaturationCmdString = 'op saturate ?\r'
        self.__UpdateHelper('Saturation', SaturationCmdString, value, qualifier)

    def __MatchSaturation(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Saturation', value, None)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'White': '0',
            'Black': '1',
            'Red': '2',
            'Green': '3',
            'Blue': '4',
            'Cyan': '5',
            'Magenta': '6',
            'Yellow': '7',
            'ANSI Checkerboard': '8',
            'Off': '11',
            'Vertical Burst': '9',
            'Horizontal Burst': '10'
        }

        TestPatternCmdString = 'op pattern = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def SetTint(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 200
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TintCmdString = 'op tint = {0}\r'.format(value)
            self.__SetHelper('Tint', TintCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTint')

    def UpdateTint(self, value, qualifier):

        TintCmdString = 'op tint ?\r'
        self.__UpdateHelper('Tint', TintCmdString, value, qualifier)

    def __MatchTint(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Tint', value, None)

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

