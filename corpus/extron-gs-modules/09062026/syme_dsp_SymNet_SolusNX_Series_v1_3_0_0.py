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
        self.Models = {}
        self.initialize = False

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallerID': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'CallStatusVoIP': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'DialedNumber': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'ExecuteControllerNumber': {'Parameters': ['Controller Number'], 'Status': {}},
            'HookStatus': {'Parameters': ['Controller Number'], 'Status': {}},
            'HookToggle': {'Parameters': ['Controller Number'], 'Status': {}},
            'Mute': {'Parameters': ['Controller Number'], 'Status': {}},
            'NumbertoDialVoIPStatus': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'NumbertoDialVoIPCommand': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'Preset': {'Status': {}},
            'PresetStatus': {'Status': {}},
            'SetUnit': {'Parameters': ['Ring Number', 'Device Address'], 'Status': {}},
            'SpeedDialNameCommand': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'SpeedDialNameStatus': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'SpeedDialNumberCommand': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'SpeedDialNumberStatus': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'TimeinCallVoIP': {'Parameters': ['Channel', 'Card', 'Enum', 'Unit'], 'Status': {}},
            'Volume': {'Parameters': ['Controller Number'], 'Status': {}}
        }

    def UpdateCallStatusVoIP(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            CallStatusVoIPCmdString = 'GSYSS {0}.1005.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('CallStatusVoIP', CallStatusVoIPCmdString, value, qualifier)
            if res:
                self.WriteStatus('CallStatusVoIP', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateCallStatusVoIP')
        else:
            print('Invalid Command for UpdateCallStatusVoIP')

    def UpdateCallerID(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            CallerIDCmdString = 'GSYSS {0}.1003.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('CallerID', CallerIDCmdString, value, qualifier)
            if res:
                self.WriteStatus('CallerID', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateCallerID')
        else:
            print('Invalid Command for UpdateCallerID')

    def UpdateDialedNumber(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            DialedNumberCmdString = 'GSYSS {0}.1002.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('DialedNumber', DialedNumberCmdString, value, qualifier)
            if res:
                self.WriteStatus('DialedNumber', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateDialedNumber')
        else:
            print('Invalid Command for UpdateDialedNumber')

    def SetExecuteControllerNumber(self, value, qualifier):

        if 1 <= int(qualifier['Controller Number']) <= 10000:
            CmdString = 'CS {0} 65535\r'.format(qualifier['Controller Number'])
            self.__SetHelper('ExecuteControllerNumber', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetExecuteControllerNumber')

    def UpdateHookStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'On',
            65535: 'Off'
        }

        controller = qualifier['Controller Number']

        if 1 <= int(controller) <= 10000:
            HookStatusCmdString = 'GS {0}\r'.format(controller)
            res = self.__UpdateHelper('HookStatus', HookStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[int(res)]
                    self.WriteStatus('HookStatus', value, qualifier)
                except (KeyError, ValueError):
                    print('Invalid/unexpected response for UpdateHookStatus')
        else:
            print('Invalid Command for UpdateHookStatus')

    def SetHookToggle(self, value, qualifier):

        if 1 <= int(qualifier['Controller Number']) <= 10000:
            HookToggleCmdString = 'CS {0} 65535\r'.format(qualifier['Controller Number'])
            self.__SetHelper('HookToggle', HookToggleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetHookToggle')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '65535',
            'Off': '0'
        }

        if 1 <= int(qualifier['Controller Number']) <= 10000:
            MuteCmdString = 'CS {0} {1}\r'.format(qualifier['Controller Number'], ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        MuteStates = {
            65535: 'On',
            0: 'Off'
        }

        controller = qualifier['Controller Number']

        if 1 <= int(controller) <= 10000:
            MuteCmdString = 'GS {0}\r'.format(controller)
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
                try:
                    value = MuteStates[int(res)]
                    self.WriteStatus('Mute', value, qualifier)
                except (KeyError, ValueError):
                    print('Invalid/unexpected response for UpdateMute')
        else:
            print('Invalid Command for UpdateMute')

    def SetNumbertoDialVoIPCommand(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            DialStr = value
            if DialStr:
                NumbertoDialVoIPCommandCmd = 'SSYSS {0}.1004.{1}.{2}.{3}={4}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'], DialStr)
                NumbertoDialVoIPCommandCmd = NumbertoDialVoIPCommandCmd.encode(encoding='iso-8859-1')
                self.__SetHelper('NumbertoDialVoIPCommand', NumbertoDialVoIPCommandCmd, value, qualifier)
        else:
            print('Invalid Command for SetNumbertoDialVoIPCommand')

    def UpdateNumbertoDialVoIPStatus(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            NumbertoDialVoIPStatusCmdString = 'GSYSS {0}.1004.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('NumbertoDialVoIPStatus', NumbertoDialVoIPStatusCmdString, value, qualifier)
            if res:
                self.WriteStatus('NumbertoDialVoIPStatus', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateNumbertoDialVoIPStatus')
        else:
            print('Invalid Command for UpdateNumbertoDialVoIPStatus')

    def SetPreset(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 1000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PresetCmdString = 'LP {0}\r'.format(value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def UpdatePresetStatus(self, value, qualifier):

        PresetCmdString = 'GPR\r'
        res = self.__UpdateHelper('PresetStatus', PresetCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                if value == 0:
                    self.WriteStatus('PresetStatus', 'No Preset Currently Selected', qualifier)
                elif 1 <= value <= 1000:
                    self.WriteStatus('PresetStatus', value, qualifier)
                else:
                    print('Invalid/unexpected response for UpdatePresetStatus')
            except ValueError:
                print('Invalid/unexpected response for UpdatePresetStatus')

    def SetSetUnit(self, value, qualifier):

        RingValue = int(qualifier['Ring Number'])
        DeviceValue = int(qualifier['Device Address'])
        if 1 <= RingValue <= 65535 and 1 <= DeviceValue <= 65535:
            UnitID = (RingValue - 1) * 100 + DeviceValue
            SetUnitCmdString = 'SU {0}\r'.format(UnitID)
            self.__SetHelper('SetUnit', SetUnitCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetUnit')

    def SetSpeedDialNumberCommand(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            DialNum = value
            if DialNum:
                SpeedDialNumberCommandCmd = 'SSYSS {0}.1000.{1}.{2}.{3}={4}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'], DialNum)
                SpeedDialNumberCommandCmd = SpeedDialNumberCommandCmd.encode(encoding='iso-8859-1')
                self.__SetHelper('SpeedDialNumberCommand', SpeedDialNumberCommandCmd, value, qualifier)
        else:
            print('Invalid Command for SetSpeedDialNumberCommand')

    def UpdateSpeedDialNumberStatus(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            SpeedDialNumberCmdString = 'GSYSS {0}.1000.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('SpeedDialNumberStatus', SpeedDialNumberCmdString, value, qualifier)
            if res:
                self.WriteStatus('SpeedDialNumberStatus', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateSpeedDialNumberStatus')
        else:
            print('Invalid Command for UpdateSpeedDialNumberStatus')

    def SetSpeedDialNameCommand(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            NameStr = value
            if NameStr:
                SpeedDialNameCommandCmd = 'SSYSS {0}.1001.{1}.{2}.{3}={4}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'], NameStr)
                SpeedDialNameCommandCmd = SpeedDialNameCommandCmd.encode(encoding='iso-8859-1')
                self.__SetHelper('SpeedDialNameCommand', SpeedDialNameCommandCmd, value, qualifier)
        else:
            print('Invalid Command for SetSpeedDialNameCommand')

    def UpdateSpeedDialNameStatus(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            SpeedDialNameCmdString = 'GSYSS {0}.1001.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('SpeedDialNameStatus', SpeedDialNameCmdString, value, qualifier)
            if res:
                self.WriteStatus('SpeedDialNameStatus', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateSpeedDialNameStatus')
        else:
            print('Invalid Command for UpdateSpeedDialNameStatus')

    def UpdateTimeinCallVoIP(self, value, qualifier):

        CardStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }

        if 0 <= int(qualifier['Channel']) <= 9 and 0 <= int(qualifier['Enum']) <= 19 and 0 <= int(qualifier['Unit']) <= 9:
            TimeinCallVoIPCmdString = 'GSYSS {0}.1006.{1}.{2}.{3}\r'.format(qualifier['Unit'], qualifier['Enum'], CardStates[qualifier['Card']], qualifier['Channel'])
            res = self.__UpdateHelper('TimeinCallVoIP', TimeinCallVoIPCmdString, value, qualifier)
            if res:
                self.WriteStatus('TimeinCallVoIP', res, qualifier)
            else:
                print('Invalid/unexpected response for UpdateTimeinCallVoIP')
        else:
            print('Invalid Command for UpdateTimeinCallVoIP')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -72,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Controller Number']) <= 10000:
            position = int(((value + 72) / 84) * 65535)
            VolumeCmdString = 'CS {0} {1:05d}\r'.format(qualifier['Controller Number'], position)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        controller = qualifier['Controller Number']

        if 1 <= int(controller) <= 10000:
            VolumeCmdString = 'GS {0}\r'.format(controller)
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    volume = int(round(-72 + 84 * (value / 65535), 0))
                    if -72 <= volume <= 12:
                        self.WriteStatus('Volume', volume, qualifier)
                    else:
                        print('Invalid Command for UpdateVolume')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateVolume')
        else:
            print('Invalid Command for UpdateVolume')
            
    def SetOnConnectedString(self, value, qualifier):
        self.SendAndWait('EH 0\r', self.DefaultResponseTimeout, deliTag=b'\r')
        self.SendAndWait('SQ 1\r', self.DefaultResponseTimeout, deliTag=b'\r')
        self.initialize = True

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'NAK\r': "Invalid Command Reply."}

        if response in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if not self.initialize:
            self.SetOnConnectedString(None, None)

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):       
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if res:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        if not self.initialize:
            self.SetOnConnectedString(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.initialize = False

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
