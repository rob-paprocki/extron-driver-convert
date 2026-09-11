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
            'ChannelAnalog': {'Status': {}},
            'ChannelAnalogStatus': {'Status': {}},
            'ChannelDigitalAir': {'Status': {}},
            'ChannelDigitalAirStatus': {'Status': {}},
            'ChannelDigitalCable1': {'Status': {}},
            'ChannelDigitalCable1Status': {'Status': {}},
            'ChannelDigitalCable2': {'Status': {}},
            'ChannelDigitalCable2Status': {'Status': {}},
            'ChannelDigitalCableMajor': {'Status': {}},
            'ChannelDigitalCableMajorStatus': {'Status': {}},
            'ChannelDigitalCableMinor': {'Status': {}},
            'ChannelDigitalCableMinorStatus': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Side Bar [AV]': '1',
            'S.Stretch [AV]': '2',
            'Zoom [AV]': '3',
            'Stretch [AV]': '4',
            'Normal [PC]': '5',
            'Zoom [PC]': '6',
            'Stretch [PC]': '7',
            'Dot by Dot [PC][AV]': '8',
            'Full Screen [AV]': '9'
        }

        AspectRatioCmdString = 'WIDE{0}   \r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            1: 'Side Bar [AV]',
            2: 'S.Stretch [AV]',
            3: 'Zoom [AV]',
            4: 'Stretch [AV]',
            5: 'Normal [PC]',
            6: 'Zoom [PC]',
            7: 'Stretch [PC]',
            8: 'Dot by Dot [PC][AV]',
            9: 'Full Screen [AV]'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetChannelAnalog(self, value, qualifier):

        if 1 <= int(value) <= 135:
            value = int(value)
            SetChannelAnalogCmdString = 'DCCH{0:03d} \r'.format(value)
            self.__SetHelper('SetChannelAnalog', SetChannelAnalogCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelAnalog')

    def UpdateChannelAnalogStatus(self, value, qualifier):

        ChannelAnalogStatusCmdString = 'DCCH????\r'
        res = self.__UpdateHelper('ChannelAnalogStatus', ChannelAnalogStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('ChannelAnalogStatus', value, qualifier)
            except ValueError:
                self.Error(['Channel Analog Status: Invalid/Unexpected Response'])

    def SetChannelDigitalAir(self, value, qualifier):

        if 100 <= int(value) <= 9999:
            value = int(value)
            SetChannelDigitalAirCmdString = 'DA2P{0:04d}\r'.format(value)
            self.__SetHelper('SetChannelDigitalAir', SetChannelDigitalAirCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDigitalAir')

    def UpdateChannelDigitalAirStatus(self, value, qualifier):

        ChannelDigitalAirStatusCmdString = 'DA2P????\r'
        res = self.__UpdateHelper('ChannelDigitalAirStatus', ChannelDigitalAirStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('ChannelDigitalAirStatus', value, qualifier)
            except ValueError:
                self.Error(['Channel Digital Air Status: Invalid/Unexpected Response'])

    def SetChannelDigitalCable1(self, value, qualifier):

        if 0 <= int(value) <= 9999:
            value = int(value)
            SetChannelDigitalCable1CmdString = 'DC10{0:04d}\r'.format(value)
            self.__SetHelper('SetChannelDigitalCable1', SetChannelDigitalCable1CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDigitalCable1')

    def UpdateChannelDigitalCable1Status(self, value, qualifier):

        ChannelDigitalCable1StatusCmdString = 'DC10????\r'
        res = self.__UpdateHelper('ChannelDigitalCable1Status', ChannelDigitalCable1StatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('ChannelDigitalCable1Status', value, qualifier)
            except ValueError:
                self.Error(['Channel Digital Cable 1 Status: Invalid/Unexpected Response'])

    def SetChannelDigitalCable2(self, value, qualifier):

        if 0 <= int(value) <= 6383:
            value = int(value)
            SetChannelDigitalCable2CmdString = 'DC11{0:04d}\r'.format(value)
            self.__SetHelper('SetChannelDigitalCable2', SetChannelDigitalCable2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDigitalCable2')

    def UpdateChannelDigitalCable2Status(self, value, qualifier):

        ChannelDigitalCable2StatusCmdString = 'DC11????\r'
        res = self.__UpdateHelper('ChannelDigitalCable2Status', ChannelDigitalCable2StatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('ChannelDigitalCable2Status', value, qualifier)
            except ValueError:
                self.Error(['Channel Digital Cable 2 Status: Invalid/Unexpected Response'])

    def SetChannelDigitalCableMajor(self, value, qualifier):

        if 1 <= int(value) <= 999:
            value = int(value)
            SetChannelDigitalCableMajorCmdString = 'DC2U{0:03d} \r'.format(value)
            self.__SetHelper('SetChannelDigitalCableMajor', SetChannelDigitalCableMajorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDigitalCableMajor')

    def UpdateChannelDigitalCableMajorStatus(self, value, qualifier):

        ChannelDigitalCableMajorStatusCmdString = 'DC2U????\r'
        res = self.__UpdateHelper('ChannelDigitalCableMajorStatus', ChannelDigitalCableMajorStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('ChannelDigitalCableMajorStatus', value, qualifier)
            except ValueError:
                self.Error(['Channel Digital Cable Major Status: Invalid/Unexpected Response'])

    def SetChannelDigitalCableMinor(self, value, qualifier):

        if 0 <= int(value) <= 999:
            value = int(value)
            SetChannelDigitalCableMinorCmdString = 'DC2L{0:03d} \r'.format(value)
            self.__SetHelper('SetChannelDigitalCableMinor', SetChannelDigitalCableMinorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelDigitalCableMinor')

    def UpdateChannelDigitalCableMinorStatus(self, value, qualifier):

        ChannelDigitalCableMinorStatusCmdString = 'DC2L????\r'
        res = self.__UpdateHelper('ChannelDigitalCableMinorStatus', ChannelDigitalCableMinorStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('ChannelDigitalCableMinorStatus', value, qualifier)
            except ValueError:
                self.Error(['Channel Digital Cable Minor Status: Invalid/Unexpected Response'])

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP0   \r',
            'Down': 'CHDW0   \r'
        }

        ChannelStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP0   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': '0',
            'Input 1 Component': '1',
            'Input 2 S-Video': '2',
            'Input 3 Video': '3',
            'Input 4 PC': '4',
            'Input 5 HDMI 1': '5',
            'Input 6 HDMI 2': '6',
            'Input 7 HDMI 3': '7',
            'Input 8 HDMI 4': '8'
        }

        if value != 'TV':
            InputCmdString = 'IAVD{0}   \r'.format(ValueStateValues[value])
        else:
            InputCmdString = 'ITVD0   \r'

        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            1: 'Input 1 Component',
            2: 'Input 2 S-Video',
            3: 'Input 3 Video',
            4: 'Input 4 PC',
            5: 'Input 5 HDMI 1',
            6: 'Input 6 HDMI 2',
            7: 'Input 7 HDMI 3',
            8: 'Input 8 HDMI 4'
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '2'
        }

        MuteCmdString = 'MUTE{0}   \r'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = 'POWR{0}   \r'.format(ValueStateValues[value])
        if value == 'On':
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        elif value == 'Off':
            self.__SetHelper('Power', 'RSPW1   \r', value, qualifier)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[int(res)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 60
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOLM{0:02d}  \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except ValueError:
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                self.Error(['{0} Communication error or incorrect command'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
