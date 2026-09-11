from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._ProjectorID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def ProjectorID(self):
        return self._ProjectorID

    @ProjectorID.setter
    def ProjectorID(self, value):
        if value == 'Broadcast':
            self._ProjectorID = '00'
        elif 1 <= int(value) <= 99:
            self._ProjectorID = value.zfill(2)
        else:
            self.Error(['Projector ID should be a value between 1 to 99 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': '60 1\r',
            '16:9': '60 2\r',
            'Letterbox': '60 5\r',
            'Superwide': '60 9\r',
            'Native': '60 6\r',
            'Auto': '60 7\r',
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            '1': '4:3',
            '2': '16:9',
            '5': 'Letterbox',
            '9': 'Superwide',
            '6': 'Native',
            '7': 'Auto',
            '0': 'No Aspect Ratio',
        }

        CmdString = '~{0}127 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Aspect Ratio'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '03 1\r',
            'Off': '03 0\r'
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        CmdString = '~{0}01 1\r'.format(self._ProjectorID)
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        States = {
            'On': '02 1\r',
            'Off': '02 0\r'
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('AVMute', CmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        States = {
            'Bright': '20 2\r',
            'Cinema': '20 3\r',
            'Reference': '20 4\r',
            'HDR SIM': '20 16\r',
            'User': '20 5\r',
            'Game': '20 12\r',
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('DisplayMode', CmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On': '103 1\r',
            'Off': '103 0\r'
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        States = {
            'On': '04 1\r',
            'Off': '04 0\r'
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'HDMI 1': '12 1\r',
            'HDMI 2': '12 15\r',
            'VGA': '12 5\r',
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '140 10\r',
            'Down': '140 14\r',
            'Left': '140 11\r',
            'Right': '140 13\r',
            'Enter': '140 12\r',
            'Menu': '140 20\r'
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        States = {
            'Up': '140 18\r',
            'Down': '140 17\r'
        }

        CmdString = '~{0}{1}'.format(self._ProjectorID, States[value])
        self.__SetHelper('Volume', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': '00 1\r',
            'Off': '00 0\r',
        }

        CmdString = '~{0}{1}\r'.format(self._ProjectorID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdatePower(self, value, qualifier):

        Power = ''

        PowerStates = {
            '1': 'On',
            '0': 'Off'
        }

        InputStates = {
            2: 'VGA',
            7: 'HDMI 1',
            8: 'HDMI 2',
            0: 'No Input',
        }

        DisplayStates = {
            2: 'Bright',
            3: 'Cinema',
            4: 'Reference',
            5: 'User',
            12: 'Game',
            16: 'HDR SIM',
            0: 'No Display Mode',
        }

        PowerCmdString = '~{0}150 1\r'.format(self._ProjectorID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                Power = PowerStates[res[2]]
                self.WriteStatus('Power', Power, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response for Power'])

            # other status is invalid when Power is Off
            if Power == 'On':
                try:
                    self.WriteStatus('LampUsage', int(res[3:8]), qualifier)
                except (IndexError, ValueError):
                    self.Error(['Invalid/Unexpected Response for Lamp Usage'])
                try:
                    self.WriteStatus('Input', InputStates[int(res[8:10])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/Unexpected Response for Input'])
                try:
                    self.WriteStatus('DisplayMode', DisplayStates[int(res[14:16])], qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/Unexpected Response for Display Mode'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or int(self._ProjectorID) == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['Invalid/Unexpected Response for {}.'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or int(self._ProjectorID) == 0:
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
