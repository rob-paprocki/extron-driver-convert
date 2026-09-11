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
            '3DDominance': {'Status': {}},
            '3DFormat': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(ack|ACK) 3d\.dominance = ([01])\r'), self.__Match3DDominance, None)
            self.AddMatchString(re.compile(b'(ack|ACK) 3d\.format = ([0-5])\r'), self.__Match3DFormat, None)
            self.AddMatchString(re.compile(b'(ack|ACK) aspect\.ratio = ([0-8])\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'(ack|ACK) freeze = ([01])\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'(ack|ACK) input = ([0-7])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'(ack|ACK) laser\.mode = ([0-2])\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'(ack|ACK) laser\.hours = (\d+)\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'(ack|ACK) total\.hours = (\d+)\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'(ack|ACK) pip\.input = ([0-6])\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'(ack|ACK) pip\.mode = ([01])\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'(ack|ACK) pip\.position = ([0-4])\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'(ack|ACK) status = ([0-4])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'(ack|ACK) shutter = ([01])\r'), self.__MatchShutter, None)

    def Set3DDominance(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            'Reverse': '1'
        }

        DominanceCmdString = '*3d.dominance = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DDominance', DominanceCmdString, value, qualifier)

    def Update3DDominance(self, value, qualifier):

        DominanceCmdString = '*3d.dominance ?\r'
        self.__UpdateHelper('3DDominance', DominanceCmdString, value, qualifier)

    def __Match3DDominance(self, match, tag):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Reverse'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('3DDominance', value, None)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Auto': '1',
            'Side By Side (Half)': '2',
            'Top and Bottom': '3',
            'Dual Pipe': '4',
            'Frame Sequential': '5'
        }

        FormatCmdString = '*3d.format = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier):

        FormatCmdString = '*3d.format ?\r'
        self.__UpdateHelper('3DFormat', FormatCmdString, value, qualifier)

    def __Match3DFormat(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Auto',
            '2': 'Side By Side (Half)',
            '3': 'Top and Bottom',
            '4': 'Dual Pipe',
            '5': 'Frame Sequential'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('3DFormat', value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '5:4': '0',
            '4:3': '1',
            '16:10': '2',
            '16:9': '3',
            '1.88': '4',
            '2.35': '5',
            'Theaterscope': '6',
            'Source': '7',
            'Unscaled': '8'
        }

        AspectRatioCmdString = '*aspect.ratio = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '*aspect.ratio ?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': '5:4',
            '1': '4:3',
            '2': '16:10',
            '3': '16:9',
            '4': '1.88',
            '5': '2.35',
            '6': 'Theaterscope',
            '7': 'Source',
            '8': 'Unscaled'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '*resync\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '*freeze = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '*freeze ?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'RGB': '2',
            'BNC': '3',
            'DVI': '4',
            'DisplayPort': '5',
            'HDBaseT': '6',
            'HD-SDI': '7'
        }

        InputCmdString = '*input = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*input ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'RGB',
            '3': 'BNC',
            '4': 'DVI',
            '5': 'DisplayPort',
            '6': 'HDBaseT',
            '7': 'HD-SDI'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': '0',
            'Normal': '1',
            'Custom': '2'
        }

        LampModeCmdString = '*laser.mode = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = '*laser.mode ?\r'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            '0': 'Eco',
            '1': 'Normal',
            '2': 'Custom'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '*laser.hours ?\r'
        self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '*total.hours ?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'RGB (VGA)': '2',
            'Component': '3',
            'DisplayPort': '4',
            'HDBaseT': '5',
            '3G-SDI': '6'
        }

        PIPInputCmdString = '*pip.input = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '*pip.input ?\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'RGB (VGA)',
            '3': 'Component',
            '4': 'DisplayPort',
            '5': 'HDBaseT',
            '6': '3G-SDI'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        PIPModeCmdString = '*pip.mode = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '*pip.mode ?\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': '0',
            'Top Right': '1',
            'Bottom Left': '2',
            'Bottom Right': '3',
            'PBP': '4'
        }

        PIPPositionCmdString = '*pip.position = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = '*pip.position ?\r'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            '0': 'Top Left',
            '1': 'Top Right',
            '2': 'Bottom Left',
            '3': 'Bottom Right',
            '4': 'PBP'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = '*power = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '*status ?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '3': 'Cooling Down',
            '4': 'Error'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open': '0',
            'Close': '1'
        }

        ShutterCmdString = '*shutter = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = '*shutter ?\r'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Shutter', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
