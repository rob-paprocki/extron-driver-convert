from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
import random

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
            'ConferenceType': {'Status': {}},
            'MICConsoleVolume': {'Status': {}},
            'MICControl': {'Parameters': ['MIC Number'], 'Status': {}},
            'MICMainVolume': {'Status': {}},
            'MICMute': {'Parameters': ['MIC Number'], 'Status': {}},
            'TotalConnectedConsoles': {'Status': {}},
        }


    def CalCRC(self, Data):
        Crc = 0
        CrcLst = []
        for i in range(0, len(Data)):
            Crc = Crc + Data[i]
        Crc = 0xFFFF + Crc
        CrcLst1 = [x for x in divmod(Crc, 65536)]
        CrcLst.append(CrcLst1[1] % 256)
        CrcLst.append(CrcLst1[0] % 256)
        return (CrcLst)

    def escaped(self, Data):
        d = 0
        List = []
        for d in Data:
            if d == 0x02:
                List.append(0x02)
                List.append(0x00)
            else:
                List.append(d)
        return List

    def conversion(self, List):
        cmdStr = b''
        for i in range(len(List)):
            cmdStr += pack('>B', List[i])
        return cmdStr

    def SetConferenceType(self, value, qualifier):

        ValueStateValues = {
            'Free': 0x00,
            'Auto': 0x01,
            'Auto Timer': 0x02,
            'Manual': 0x03
        }

        rand_num = random.randrange(0, 255)
        temp = [0x44, 0x01, 0x00, 0x00, rand_num, 0x03, 0x00, 0x41, 0x00, ValueStateValues[value]]
        crc = self.CalCRC(temp)
        data_list = self.escaped(temp + crc)
        ConferenceTypeCmdString = b''.join([b'\x02\x02', self.conversion(data_list), b'\x02\x03'])
        self.__SetHelper('ConferenceType', ConferenceTypeCmdString, value, qualifier)

    def SetMICConsoleVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            rand_num = random.randrange(0, 255)
            temp = [0x44, 0x01, 0x00, 0x00, rand_num, 0x06, 0x00, 0x66]
            temp.extend([value] * 5)
            crc = self.CalCRC(temp)
            data_list = self.escaped(temp + crc)
            MICConsoleVolumeCmdString = b''.join([b'\x02\x02', self.conversion(data_list), b'\x02\x03'])
            self.__SetHelper('MICConsoleVolume', MICConsoleVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMICConsoleVolume')

    def SetMICControl(self, value, qualifier):

        MICNoConstraints = {
            'Min': 0,
            'Max': 120
        }
        ValueStateValues = {
            'Open': 0x6D,
            'Close': 0X66
        }

        mic = qualifier['MIC Number']
        if MICNoConstraints['Min'] <= int(mic) <= MICNoConstraints['Max']:
            rand_num = random.randrange(0, 255)
            temp = [0x44, 0x01, 0x00, 0x00, rand_num, 0x03, 0x00, 0x3F, int(mic), ValueStateValues[value]]
            crc = self.CalCRC(temp)
            data_list = self.escaped(temp + crc)
            MICControlCmdString = b''.join([b'\x02\x02', self.conversion(data_list), b'\x02\x03'])
            self.__SetHelper('MICControl', MICControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMICControl')

    def SetMICMainVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            rand_num = random.randrange(0, 255)
            temp = [0x44, 0x01, 0x00, 0x00, rand_num, 0x0A, 0x00, 0x65]
            temp.extend([value] * 9)
            crc = self.CalCRC(temp)
            data_list = self.escaped(temp + crc)
            MICMainVolumeCmdString = b''.join([b'\x02\x02', self.conversion(data_list), b'\x02\x03'])
            self.__SetHelper('MICMainVolume', MICMainVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMICMainVolume')

    def SetMICMute(self, value, qualifier):

        MICNoConstraints = {
            'Min': 0,
            'Max': 120
        }

        ValueStateValues = {
            'On': 0x68,
            'Off': 0x69
        }

        mic = qualifier['MIC Number']
        if MICNoConstraints['Min'] <= int(mic) <= MICNoConstraints['Max']:
            rand_num = random.randrange(0, 255)
            temp = [0x44, 0x01, 0x00, 0x00, rand_num, 0x03, 0x00, 0x3F, int(mic), ValueStateValues[value]]
            crc = self.CalCRC(temp)
            data_list = self.escaped(temp + crc)
            MICMuteCmdString = b''.join([b'\x02\x02', self.conversion(data_list), b'\x02\x03'])
            self.__SetHelper('MICMute', MICMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMICMute')

    def UpdateTotalConnectedConsoles(self, value, qualifier):

        TotalConnectedConsolesCmdString = b'\x02\x02\x44\x01\x00\x00\x68\x01\x00\x3C\xE9\x00\x02\x03'
        res = self.__UpdateHelper('TotalConnectedConsoles', TotalConnectedConsolesCmdString, value, qualifier)
        if res:
            try:
                value = int(res[12]) - 1
                if 0 <= value <= 120:
                    self.WriteStatus('TotalConnectedConsoles', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTotalConnectedConsoles')


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x02\x03')


    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x02\x03')
            if not res:
                return ''
            else:
                return res

            

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
