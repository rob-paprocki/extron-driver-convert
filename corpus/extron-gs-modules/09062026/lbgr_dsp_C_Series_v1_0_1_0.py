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
            'C 10:8X': self.lbgr_25_2748_8CH,
            'C 20:8X': self.lbgr_25_2748_8CH,
            'C 10:4X': self.lbgr_25_2748_4CH,
            'C 5:4X': self.lbgr_25_2748_4CH,
            'C 28:4': self.lbgr_25_2748_4CH,
            'C 16:4': self.lbgr_25_2748_4CH,
            'C 48:4': self.lbgr_25_2748_4CH,
            'C 68:4': self.lbgr_25_2748_4CH,
            'C 88:4': self.lbgr_25_2748_4CH,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceFaultStatus': {'Parameters': ['Device Name', 'Channel', 'Fault Type'], 'Status': {}},
            'DeviceMute': {'Parameters': ['Device Name', 'Channel'], 'Status': {}},
            'DevicePower': {'Parameters': ['Device Name'], 'Status': {}},
            'DeviceStatus': {'Parameters': ['Device Name'], 'Status': {}},
            'SubnetMute': {'Status': {}},
            'SubnetPower': {'Status': {}},
            'SubnetStatus': {'Status': {}},
        }

        self.status_types = ('VHF', 'DC', 'Load Shorted', 'Temperature', 'High impedance warning', 'Temperature warning')
        self.regex = re.compile('-?[0-9]{1,3} [01] [01] ([01]) ([01]) ([01]) ([01]) ([01]) ([01])')

    def UpdateDeviceFaultStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Present',
            '0': 'Not Present'
        }

        DevName = qualifier['Device Name']

        if DevName:
            DeviceFaultStatusCmdString = '{}.Status ?\r\n'.format(DevName)
            res = self.__UpdateHelper('DeviceFaultStatus', DeviceFaultStatusCmdString, value, qualifier)
            if res:
                try:
                    temp_res = re.findall(self.regex, res[6:])
                    if self.Length == len(temp_res):
                        for i in range(0, self.Length):
                            stat_len = len(self.status_types)
                            for j in range(0, stat_len):
                                self.WriteStatus('DeviceFaultStatus', ValueStateValues[temp_res[i][j]], {'Device Name': DevName, 'Channel': chr(i + 65), 'Fault Type': self.status_types[j]})
                except (ValueError, KeyError, IndexError):
                    self.Error(['Device Fault Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDeviceFaultStatus')

    def SetDeviceMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        DevName = qualifier['Device Name']
        channel = qualifier['Channel']
        if DevName and channel in self.ChannelStates:
            DeviceMuteCmdString = '{}.Mute{} = {}\r\n'.format(DevName, channel, ValueStateValues[value])
            self.__SetHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceMute')

    def UpdateDeviceMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        DevName = qualifier['Device Name']
        channel = qualifier['Channel']
        if DevName and channel in self.ChannelStates:
            DeviceMuteCmdString = '{}.Mute{} ?\r\n'.format(DevName, channel)
            res = self.__UpdateHelper('DeviceMute', DeviceMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('DeviceMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Device Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDeviceMute')

    def SetDevicePower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        DevName = qualifier['Device Name']
        if DevName:
            DevicePowerCmdString = '{}.Power = {}\r\n'.format(DevName, ValueStateValues[value])
            self.__SetHelper('DevicePower', DevicePowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDevicePower')

    def UpdateDevicePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        DevName = qualifier['Device Name']
        if DevName:
            DevicePowerCmdString = '{}.Power ?\r\n'.format(DevName)
            res = self.__UpdateHelper('DevicePower', DevicePowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('DevicePower', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Device Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDevicePower')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Faults are present',
            '0': 'No faults present'
        }

        DevName = qualifier['Device Name']
        if DevName:
            DeviceStatusCmdString = '{}.Status ?\r\n'.format(DevName)
            res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('DeviceStatus', ValueStateValues[res[0]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Device Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDeviceStatus')

    def SetSubnetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        SubnetMuteCmdString = 'Subnet.Mute = {}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('SubnetMute', SubnetMuteCmdString, value, qualifier)

    def UpdateSubnetMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        SubnetMuteCmdString = 'Subnet.Mute ?\r\n'
        res = self.__UpdateHelper('SubnetMute', SubnetMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('SubnetMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Subnet Mute: Invalid/unexpected response'])

    def SetSubnetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        SubnetPowerCmdString = 'Subnet.Power = {}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('SubnetPower', SubnetPowerCmdString, value, qualifier)

    def UpdateSubnetPower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Mixed, some are on and some are off',
            '3': 'In transition, one or more devices are changing status'
        }

        SubnetPowerCmdString = 'Subnet.Power ?\r\n'
        res = self.__UpdateHelper('SubnetPower', SubnetPowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('SubnetPower', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Subnet Power: Invalid/unexpected response'])

    def UpdateSubnetStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Faults are present',
            '1': 'No faults present'
        }

        SubnetStatusCmdString = 'Subnet.StatusOk ?\r\n'
        res = self.__UpdateHelper('SubnetStatus', SubnetStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('SubnetStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Subnet Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0:6] == 'ERROR!':
            self.Error(['{0}: {1}'.format(sourceCmdName, response[:-2])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
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

    def lbgr_25_2748_8CH(self):
        self.ChannelStates = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'}
        self.Length = 8

    def lbgr_25_2748_4CH(self):
        self.ChannelStates = {'A', 'B', 'C', 'D'}
        self.Length = 4

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
