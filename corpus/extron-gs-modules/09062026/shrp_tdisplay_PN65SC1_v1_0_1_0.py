from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide': b'WIDE   1\r\n',
            'Dot by Dot': b'WIDE   3\r\n',
            'Normal': b'WIDE   6\r\n'
        }
        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'1\r\n': 'Wide',
            b'3\r\n': 'Dot by Dot',
            b'6\r\n': 'Normal'
        }
        AspectRatioCmdString = b'WIDE????\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except KeyError:
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Remote Control': b'ALTG   0\r\n',
            'Monitor Buttons': b'ALTG   1\r\n',
            'Both': b'ALTG   2\r\n',
            'Off': b'ALTG   3\r\n'
        }
        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            b'0\r\n': 'Remote Control',
            b'1\r\n': 'Monitor Buttons',
            b'2\r\n': 'Both',
            b'3\r\n': 'Off'
        }
        ExecutiveModeCmdString = b'ALTG????\r\n'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except KeyError:
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'INPS   2\r\n',
            'HDMI 1': b'INPS  10\r\n',
            'HDMI 2': b'INPS  13\r\n',
            'HDMI 3': b'INPS  18\r\n',
            'HDMI 4': b'INPS  23\r\n',
            'DisplayPort': b'INPS  14\r\n',
            'Option': b'INPS  21\r\n'
        }
        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'2\r\n': 'VGA',
            b'10\r\n': 'HDMI 1',
            b'13\r\n': 'HDMI 2',
            b'18\r\n': 'HDMI 3',
            b'23\r\n': 'HDMI 4',
            b'14\r\n': 'DisplayPort',
            b'21\r\n': 'Option'
        }
        InputCmdString = b'INPS????\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Input', value, qualifier)
            except KeyError:
                self.Error(['Input: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'MUTE   1\r\n',
            'Off': b'MUTE   0\r\n'
        }
        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            b'1\r\n': 'On',
            b'0\r\n': 'Off'
        }
        MuteCmdString = b'MUTE????\r\n'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Mute', value, qualifier)
            except KeyError:
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'MWIP   2\r\n',
            'HDMI 1': b'MWIP  10\r\n',
            'HDMI 2': b'MWIP  13\r\n',
            'HDMI 3': b'MWIP  18\r\n',
            'HDMI 4': b'MWIP  23\r\n',
            'DisplayPort': b'MWIP  14\r\n',
            'Option': b'MWIP  21\r\n'
        }
        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            b'2\r\n': 'VGA',
            b'10\r\n': 'HDMI 1',
            b'13\r\n': 'HDMI 2',
            b'18\r\n': 'HDMI 3',
            b'23\r\n': 'HDMI 4',
            b'14\r\n': 'DisplayPort',
            b'21\r\n': 'Option'
        }
        PIPInputCmdString = b'MWIP????\r\n'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PIPInput', value, qualifier)
            except KeyError:
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': b'MWIN   0\r\n',
            'PIP': b'MWIN   1\r\n',
            'Picture by Picture': b'MWIN   2\r\n'
        }
        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'0\r\n': 'Off',
            b'1\r\n': 'PIP',
            b'2\r\n': 'Picture by Picture'
        }
        PIPModeCmdString = b'MWIN????\r\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PIPMode', value, qualifier)
            except KeyError:
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Right': b'MWPS   0\r\n',
            'Upper Left': b'MWPS   1\r\n',
            'Lower Right': b'MWPS   2\r\n',
            'Lower Left': b'MWPS   3\r\n'
        }
        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            b'0\r\n': 'Upper Right',
            b'1\r\n': 'Upper Left',
            b'2\r\n': 'Lower Right',
            b'3\r\n': 'Lower Left'
        }
        PIPPositionCmdString = b'MWPS????\r\n'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PIPPosition', value, qualifier)
            except KeyError:
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': b'MPSZ   0\r\n',
            'Medium': b'MPSZ   1\r\n',
            'Large': b'MPSZ   2\r\n'
        }
        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            b'0\r\n': 'Small',
            b'1\r\n': 'Medium',
            b'2\r\n': 'Large'
        }
        PIPSizeCmdString = b'MPSZ????\r\n'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PIPSize', value, qualifier)
            except KeyError:
                self.Error(['PIP Size: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'POWR   1\r\n',
            'Off': b'POWR   0\r\n',
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1\r\n': 'On',
            b'0\r\n': 'Off',
            b'2\r\n': 'Input Signal Waiting'
        }
        PowerCmdString = b'POWR????\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Power', value, qualifier)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{:04}\r\n'.format(value).encode()
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }
        VolumeCmdString = b'VOLM????\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    self.Error(['Volume: Not within expected range'])
            except ValueError:
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'ERR\r\n' in response:
            self.Error([sourceCmdName + ': An error occured'])
            return b''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return b''
            else:
                return self.__CheckResponseForErrors(command, res)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
