from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re


class DeviceClass:
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

        self.Models = {
            'E-Vision Laser 7500': self.dpl_1_2036_others,
            'E-Vision Laser 8500': self.dpl_1_2036_others,
            'E-Vision Laser 10K': self.dpl_1_2036_others,
            'E-Vision Laser 4K': self.dpl_1_2036_4K,
        }

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
            'LaserPower': {'Status': {}},
            'LensLoad': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(ack|ACK) 3d\.dominance = (0|1)\r'), self.__Match3DDominance, None)
            self.AddMatchString(re.compile(b'(ack|ACK) 3d\.format = ([0-5])\r'), self.__Match3DFormat, None)
            self.AddMatchString(re.compile(b'(ack|ACK) aspect\.ratio = ([0-8])\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'(ack|ACK) freeze = (0|1)\r'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'(ack|ACK) input = ([0-7])\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'(ack|ACK) laser\.mode = ([0-2])\r'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'(ack|ACK) laser\.hours = (\d+)\r'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'(ack|ACK) laser\.power = (\d+)\r'), self.__MatchLaserPower, None)
            self.AddMatchString(re.compile(b'(ack|ACK) total\.hours = (\d+)\r'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'(ack|ACK) pip\.input = ([0-6])\r'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'(ack|ACK) pip\.mode = (0|1)\r'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'(ack|ACK) pip\.position = ([0-4])\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'(ack|ACK) status = ([0-4])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'(ack|ACK) shutter = (0|1)\r'), self.__MatchShutter, None)

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

        FormatCmdString = '*3d.format = {0}\r'.format(self.FormatStates[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier):

        FormatCmdString = '*3d.format ?\r'
        self.__UpdateHelper('3DFormat', FormatCmdString, value, qualifier)

    def __Match3DFormat(self, match, tag):

        value = self.FormatValues[match.group(2).decode()]
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

        InputCmdString = '*input = {0}\r'.format(self.InputStates[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*input ?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group(2).decode()]
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

    def SetLaserPower(self, value, qualifier):

        if 20 <= value <= 100:
            LaserPowerCmdString = '*laser.power = {0}\r'.format(value)
            self.__SetHelper('LaserPower', LaserPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLaserPower')

    def UpdateLaserPower(self, value, qualifier):

        LaserPowerCmdString = '*laser.power ?\r'
        self.__UpdateHelper('LaserPower', LaserPowerCmdString, value, qualifier)

    def __MatchLaserPower(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('LaserPower', value, None)

    def SetLensLoad(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        LensLoadCmdString = '*lens.load = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LensLoad', LensLoadCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '*total.hours ?\r'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = '*pip.input = {0}\r'.format(self.PIPInputStates[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '*pip.input ?\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        value = self.PIPInputValues[match.group(2).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PIPModeCmdString = '*pip.mode = {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '*pip.mode ?\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
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

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '*pip.swap\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }
        PowerCmdString = 'op power = {0}\r'.format(ValueStateValues[value])
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
        index = 0  # Start of possible good data

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


    def dpl_1_2036_others(self):
        self.FormatStates = {
            'Off': '0',
            'Auto': '1',
            'Side By Side (Half)': '2',
            'Top and Bottom': '3',
            'Dual Pipe': '4',
            'Frame Sequential': '5'
        }

        self.FormatValues = {
            '0': 'Off',
            '1': 'Auto',
            '2': 'Side By Side (Half)',
            '3': 'Top and Bottom',
            '4': 'Dual Pipe',
            '5': 'Frame Sequential'
        }

        self.InputStates = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'RGB (VGA)': '2',
            'Component': '3',
            'DVI': '4',
            'DisplayPort': '5',
            'HDBaseT': '6',
            '3G-SDI': '7'
        }

        self.InputValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'RGB (VGA)',
            '3': 'Component',
            '4': 'DVI',
            '5': 'DisplayPort',
            '6': 'HDBaseT',
            '7': '3G-SDI'
        }

        self.PIPInputStates = {
            'HDMI 1': '0',
            'HDMI 2': '1',
            'RGB (VGA)': '2',
            'Component': '3',
            'DisplayPort': '4',
            'HDBaseT': '5',
            '3G-SDI': '6'
        }

        self.PIPInputValues = {
            '0': 'HDMI 1',
            '1': 'HDMI 2',
            '2': 'RGB (VGA)',
            '3': 'Component',
            '4': 'DisplayPort',
            '5': 'HDBaseT',
            '6': '3G-SDI'
        }

    def dpl_1_2036_4K(self):
        self.FormatStates = {
            'Off': '0',
            'Auto': '1',
            'Dual Pipe': '2',
            'Frame Sequential': '3'
        }

        self.FormatValues = {
            '0': 'Off',
            '1': 'Auto',
            '2': 'Dual Pipe',
            '3': 'Frame Sequential'
        }

        self.InputStates = {
            'DisplayPort': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'HDBaseT': '3',
            '3G-SDI': '4',
            'HDMI 3': '5',
            'HDMI 4': '6'
        }

        self.InputValues = {
            '0': 'DisplayPort',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDBaseT',
            '4': '3G-SDI',
            '5': 'HDMI 3',
            '6': 'HDMI 4'
        }

        self.PIPInputStates = {
            'DisplayPort': '0',
            'HDMI 1': '1',
            'HDMI 2': '2',
            'HDBaseT': '3',
            '3G-SDI': '4'
        }

        self.PIPInputValues = {
            '0': 'DisplayPort',
            '1': 'HDMI 1',
            '2': 'HDMI 2',
            '3': 'HDBaseT',
            '4': '3G-SDI'
        }


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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