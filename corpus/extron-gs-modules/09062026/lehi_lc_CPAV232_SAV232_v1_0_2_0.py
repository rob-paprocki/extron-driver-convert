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
        self.Models = {
            'CPAV232': self.lehi_13_3106_cpav,
            'SAV232': self.lehi_13_3106_sav,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelLock': {'Parameters': ['Area', 'Channel'], 'Status': {}},
            'ChannelRamp': {'Parameters': ['Area', 'Channel'], 'Status': {}},
            'Curtain': {'Status': {}},
            'DefaultReset': {'Status': {}},
            'Master': {'Parameters': ['Area'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Area'], 'Status': {}},
            'Screen': {'Status': {}},
            'SequenceOff': {'Parameters': ['Area'], 'Status': {}},
            'SequenceOn': {'Parameters': ['Area', 'Preset'], 'Status': {}},
            'StationLock': {'Parameters': ['Area', 'Type'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.RespList = re.compile('[0-9A-IPX][XRLMN]')

    def SetChannelLock(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': 'A',
            '11': 'B',
            '12': 'C',
            '13': 'D',
            '14': 'E',
            '15': 'F',
            '16': 'G',
            '17': 'H',
            '18': 'I',
            '19': 'J',
            '20': 'K',
            '21': 'L',
            '22': 'M',
            '23': 'N',
            '24': 'O',
            '25': 'P',
            '26': 'Q',
            '27': 'R',
            '28': 'S',
            '29': 'T',
            '30': 'U',
            '31': 'V',
            '32': 'W',
            '33': 'X',
            '34': 'Y',
            '35': 'Z',
            '36': '[',
            'All': ''
        }

        ValueStateValues = {
            'Lock': 'LC',
            'Unlock': 'UC'
        }

        Area = self.AreaStates[qualifier['Area']]
        Channel = ChannelStates[qualifier['Channel']]
        if Channel:
            ChannelLockCmdString = ';{0}{1},{2}\r'.format(ValueStateValues[value], Area, Channel)
        else:
            ChannelLockCmdString = ';{0}{1}\r'.format(ValueStateValues[value], Area)
        self.__SetHelper('ChannelLock', ChannelLockCmdString, value, qualifier)

    def SetChannelRamp(self, value, qualifier):

        ChannelStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': 'A',
            '11': 'B',
            '12': 'C',
            '13': 'D',
            '14': 'E',
            '15': 'F',
            '16': 'G',
            '17': 'H',
            '18': 'I',
            '19': 'J',
            '20': 'K',
            '21': 'L',
            '22': 'M',
            '23': 'N',
            '24': 'O',
            '25': 'P',
            '26': 'Q',
            '27': 'R',
            '28': 'S',
            '29': 'T',
            '30': 'U',
            '31': 'V',
            '32': 'W',
            '33': 'X',
            '34': 'Y',
            '35': 'Z',
            '36': '[',
            'All': ''
        }

        ValueStateValues = {
            'Raise': 'CR',
            'Lower': 'CL',
            'Raise Stop': 'CRS',
            'Lower Stop': 'CLS'
        }
        Area = self.AreaStates[qualifier['Area']]
        Channel = ChannelStates[qualifier['Channel']]
        if Channel:
            ChannelRampCmdString = ';{0}{1},{2}\r'.format(ValueStateValues[value], Area, Channel)
        else:
            ChannelRampCmdString = ';{0}{1}\r'.format(ValueStateValues[value], Area)
        self.__SetHelper('ChannelRamp', ChannelRampCmdString, value, qualifier)

    def SetCurtain(self, value, qualifier):

        ValueStateValues = {
            'Open': 'COP',
            'Close': 'CCL'
        }

        CurtainCmdString = ';{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Curtain', CurtainCmdString, value, qualifier)

    def SetDefaultReset(self, value, qualifier):

        DefaultResetCmdString = ';DFLT\r'
        self.__SetHelper('DefaultReset', DefaultResetCmdString, value, qualifier)

    def SetMaster(self, value, qualifier):

        ValueStateValues = {
            'Raise': 'MR',
            'Lower': 'ML',
            'Raise Stop': 'MRS',
            'Lower Stop': 'MLS'
        }
        Area = self.AreaStates[qualifier['Area']]
        MasterCmdString = ';{0}{1}\r'.format(Area, ValueStateValues[value])
        self.__SetHelper('Master', MasterCmdString, value, qualifier)

    def UpdateMaster(self, value, qualifier):

        PresetNames = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'A': '10',
            'B': '11',
            'C': '12',
            'D': '13',
            'E': '14',
            'F': '15',
            'G': '16',
            'H': '17',
            'I': '18',
            'P': 'Full',
            '0': 'Off',
            'X': 'N/A'
        }
        MasterCmdString = ';ST\r'
        res = self.__UpdateHelper('Master', MasterCmdString, value, qualifier)
        if res:
            tempList = re.findall(self.RespList, res)
            try:
                all_preset = True
                prev_preset = 0
                for index, item in enumerate(tempList):
                    area = str(index + 1)
                    preset = item[0]
                    status = item[1]

                    if preset != 'X':
                        if prev_preset:
                            if prev_preset != preset:
                                all_preset = False
                        else:
                            prev_preset = preset

                        self.WriteStatus('PresetRecall', PresetNames[preset], {'Area': area})
                        if status == 'R':
                            self.WriteStatus('Master', 'Raise', {'Area': area})
                        if status == 'L':
                            self.WriteStatus('Master', 'Lower', {'Area': area})
                    else:
                        self.WriteStatus('PresetRecall', 'N/A', {'Area': area})
                if all_preset:
                    self.WriteStatus('PresetRecall', PresetNames[preset], {'Area': 'All'})
                else:
                    self.WriteStatus('PresetRecall', 'N/A', {'Area': 'All'})
            except (KeyError, IndexError):
                self.Error(['{0}: Invalid/unexpected response'.format('Master')])

    def SetPresetRecall(self, value, qualifier):

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
            '10': 'A',
            '11': 'B',
            '12': 'C',
            '13': 'D',
            '14': 'E',
            '15': 'F',
            '16': 'G',
            '17': 'H',
            '18': 'I',
            'Full': 'P',
            'Off': '0'
        }
        Area = self.AreaStates[qualifier['Area']]
        if Area:
            PresetRecallCmdString = ';P{0},{1}\r'.format(Area, ValueStateValues[value])
        else:
            PresetRecallCmdString = ';P,{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def UpdatePresetRecall(self, value, qualifier):
        self.UpdateMaster(value, qualifier)

    def SetScreen(self, value, qualifier):

        ValueStateValues = {
            'Raise': 'RSC',
            'Lower': 'LSC'
        }

        ScreenCmdString = ';{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Screen', ScreenCmdString, value, qualifier)

    def SetSequenceOff(self, value, qualifier):

        Area = self.AreaStates[qualifier['Area']]
        SequenceOffCmdString = ';SQF{0}\r'.format(Area)
        self.__SetHelper('SequenceOff', SequenceOffCmdString, value, qualifier)

    def SetSequenceOn(self, value, qualifier):

        PresetStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': 'A',
            '11': 'B',
            '12': 'C',
            '13': 'D',
            '14': 'E',
            '15': 'F',
            '16': 'G',
            '17': 'H',
            '18': 'I'
        }
        Area = self.AreaStates[qualifier['Area']]
        Preset = PresetStates[qualifier['Preset']]
        SequenceOnCmdString = ';SQN{0},{1}\r'.format(Area, Preset)
        self.__SetHelper('SequenceOn', SequenceOnCmdString, value, qualifier)

    def SetStationLock(self, value, qualifier):

        TypeStates = {
            'Master': 'M',
            'Remote': 'R'
        }

        ValueStateValues = {
            'Lock': 'L',
            'Unlock': 'U'
        }
        Area = self.AreaStates[qualifier['Area']]
        Type = TypeStates[qualifier['Type']]
        StationLockCmdString = ';{0}{1}{2}\r'.format(ValueStateValues[value], Type, Area)
        self.__SetHelper('StationLock', StationLockCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=36)
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

    def lehi_13_3106_cpav(self):
        self.AreaStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            '11': 'A',
            '12': 'B',
            '13': 'C',
            '14': 'D',
            '15': 'E',
            '16': 'F',
            'All': ''
        }

    def lehi_13_3106_sav(self):
        self.AreaStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            'All': ''
        }

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
