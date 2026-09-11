from extronlib.interface import EthernetClientInterface, SerialInterface
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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'GlobalSceneRouting': {'Status': {}},
            'Save': {'Status': {}},
            'ZoneBass': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneInputRouting': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneMute': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneSceneRouting': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneTreble': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneVolume': {'Parameters': ['Zone'], 'Status': {}}
        }
        
        self._DeviceAddress = 'M001'

    @property
    def DeviceAddress(self):
        return str(int(self._DeviceAddress[1:]))

    @DeviceAddress.setter
    def DeviceAddress(self, value):
        if 1 <= int(value) <= 100:
            self._DeviceAddress = 'M{0:03}'.format(int(value))
        else:
            print('Device Address set to an invalid value.')

    def SetGlobalSceneRouting(self, value, qualifier):
        if 1 <= int(value) <= 8:
            GlobalSceneRoutingCmdString = '#|{0}|F001|SR0|{1}|U|\r\n'.format(self._DeviceAddress, int(value) + 60)
            self.__SetHelper('GlobalSceneRouting', GlobalSceneRoutingCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGlobalSceneRouting')

    def SetSave(self, value, qualifier):

        SaveCmdString = '#|{0}|F001|SAVE|0|U|\r\n'.format(self._DeviceAddress)
        self.__SetHelper('Save', SaveCmdString, value, qualifier)

    def SetZoneBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -9,
            'Max': 9
        }

        zone = qualifier['Zone']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= int(zone) <= 8):
            ZoneBassCmdString = '#|{0}|F001|SB{1}|{2}|U|\r\n'.format(self._DeviceAddress, zone, value)
            self.__SetHelper('ZoneBass', ZoneBassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneBass')

    def UpdateZoneBass(self, value, qualifier):

        zone = qualifier['Zone']
        if 1 <= int(zone) <= 8:
            ZoneBassCmdString = '#|{0}|F001|GB{1}|0|U|\r\n'.format(self._DeviceAddress, zone)
            res = self.__UpdateHelper('ZoneBass', ZoneBassCmdString, value, qualifier)
            if res:
                try:
                    if res.split('|')[3][0:2] == 'B0' and res.split('|')[3][2] == zone:
                        value = int(res.split('|')[4])
                        self.WriteStatus('ZoneBass', value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateZoneTreble')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateZoneBass')
        else:
            print('Invalid Command for UpdateZoneBass')

    def SetZoneInputRouting(self, value, qualifier):

        ValueStateValues = {
            'Direct Input 1': '1',
            'Direct Input 2': '2',
            'Direct Input 3': '3',
            'Direct Input 4': '4',
            'Direct Input 5': '5',
            'Direct Input 6': '6',
            'Direct Input 7': '7',
            'Direct Input 8': '8',
            'Direct Input 9': '9',
            'Wall Plate Input 1': '17',
            'Wall Plate Input 2': '18',
            'Wall Plate Input 3': '19',
            'Wall Plate Input 4': '20',
            'Wall Plate Input 5': '21',
            'Wall Plate Input 6': '22',
            'Wall Plate Input 7': '23',
            'Wall Plate Input 8': '24',
            'Fiber Input 1': '25',
            'Fiber Input 2': '26',
            'Fiber Input 3': '27',
            'Fiber Input 4': '28',
            'Fiber Input 5': '29',
            'Fiber Input 6': '30',
            'Fiber Input 7': '31',
            'Fiber Input 8': '32',
            'Prio 1': '12',
            'Prio 2': '13',
            'Internal sine generator': '14',
            'Internal white noise generator': '15',
            'Internal pink noise generator': '16'
        }

        zone = qualifier['Zone']
        ZoneInputRoutingCmdString = ''
        if zone == 'All':
            ZoneInputRoutingCmdString = '#|{0}|F001|SRALL|{1}^{1}^{1}^{1}^{1}^{1}^{1}^{1}|U|\r\n'.format(self._DeviceAddress, ValueStateValues[value])
        elif 1 <= int(zone) <= 8:
            ZoneInputRoutingCmdString = '#|{0}|F001|SR{1}|{2}|U|\r\n'.format(self._DeviceAddress, zone, ValueStateValues[value])
        if ZoneInputRoutingCmdString:
            self.__SetHelper('ZoneInputRouting', ZoneInputRoutingCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneInputRouting')

    def UpdateZoneInputRouting(self, value, qualifier):

        ValueStateValues = {
            '1': 'Direct Input 1',
            '2': 'Direct Input 2',
            '3': 'Direct Input 3',
            '4': 'Direct Input 4',
            '5': 'Direct Input 5',
            '6': 'Direct Input 6',
            '7': 'Direct Input 7',
            '8': 'Direct Input 8',
            '9': 'Direct Input 9',
            '17': 'Wall Plate Input 1',
            '18': 'Wall Plate Input 2',
            '19': 'Wall Plate Input 3',
            '20': 'Wall Plate Input 4',
            '21': 'Wall Plate Input 5',
            '22': 'Wall Plate Input 6',
            '23': 'Wall Plate Input 7',
            '24': 'Wall Plate Input 8',
            '25': 'Fiber Input 1',
            '26': 'Fiber Input 2',
            '27': 'Fiber Input 3',
            '28': 'Fiber Input 4',
            '29': 'Fiber Input 5',
            '30': 'Fiber Input 6',
            '31': 'Fiber Input 7',
            '32': 'Fiber Input 8',
            '12': 'Prio 1',
            '13': 'Prio 2',
            '14': 'Internal sine generator',
            '15': 'Internal white noise generator',
            '16': 'Internal pink noise generator',
            '50': 'Other'
        }

        zone = qualifier['Zone']
        if (zone != 'All') and (1 <= int(zone) <= 8):
            ZoneInputRoutingCmdString = '#|{0}|F001|GR{1}|0|U|\r\n'.format(self._DeviceAddress, zone)
            res = self.__UpdateHelper('ZoneInputRouting', ZoneInputRoutingCmdString, value, qualifier)
            if res:
                try:
                    if res.split('|')[3][0:2] == 'R0' and res.split('|')[3][2] == zone:
                        value = str(int(res.split('|')[4].split('^')[1]))
                        if value in ValueStateValues:
                            self.WriteStatus('ZoneInputRouting', ValueStateValues[value], qualifier)
                        else:
                            self.WriteStatus('ZoneInputRouting', 'Other', qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateZoneTreble')
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateZoneInputRouting')
        else:
            print('Invalid Command for UpdateZoneInputRouting')

    def SetZoneMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        zone = qualifier['Zone']
        ZoneMuteCmdString = ''
        if zone == 'All':
            ZoneMuteCmdString = '#|{0}|F001|SMALL|{1}^{1}^{1}^{1}^{1}^{1}^{1}^{1}|U|\r\n'.format(self._DeviceAddress, ValueStateValues[value])
        elif 1 <= int(zone) <= 8:
            ZoneMuteCmdString = '#|{0}|F001|SM{1}|{2}|U|\r\n'.format(self._DeviceAddress, zone, ValueStateValues[value])

        if ZoneMuteCmdString:
            self.__SetHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneMute')

    def UpdateZoneMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        zone = qualifier['Zone']
        if (zone != 'All') and (1 <= int(zone) <= 8):
            ZoneMuteCmdString = '#|{0}|F001|GM{1}|0|U|\r\n'.format(self._DeviceAddress, zone)
            res = self.__UpdateHelper('ZoneMute', ZoneMuteCmdString, value, qualifier)
            if res:
                try:
                    if res.split('|')[3][0:2] == 'M0' and res.split('|')[3][2] == zone:
                        value = ValueStateValues[int(res.split('|')[4])]
                        self.WriteStatus('ZoneMute', value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateZoneTreble')
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateZoneMute')
        else:
            print('Invalid Command for UpdateZoneMute')

    def SetZoneSceneRouting(self, value, qualifier):

        zone = qualifier['Zone']
        if (1 <= int(value) <= 8) and 1 <= int(zone) <= 8:
            ZoneSceneRoutingCmdString = '#|{0}|F001|SR{1}|{2}|U|\r\n'.format(self._DeviceAddress, zone, int(value) + 50)
            self.__SetHelper('ZoneSceneRouting', ZoneSceneRoutingCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneSceneRouting')

    def SetZoneTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -9,
            'Max': 9
        }

        zone = qualifier['Zone']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(zone) <= 8:
            ZoneTrebleCmdString = '#|{0}|F001|ST{1}|{2}|U|\r\n'.format(self._DeviceAddress, zone, int(value))
            self.__SetHelper('ZoneTreble', ZoneTrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoneTreble')

    def UpdateZoneTreble(self, value, qualifier):

        zone = qualifier['Zone']
        if (1 <= int(zone) <= 8):
            ZoneTrebleCmdString = '#|{0}|F001|GT{1}|0|U|\r\n'.format(self._DeviceAddress, zone)
            res = self.__UpdateHelper('ZoneTreble', ZoneTrebleCmdString, value, qualifier)
            if res:
                try:
                    if res.split('|')[3][0:2] == 'T0' and res.split('|')[3][2] == zone:
                        value = int(res.split('|')[4])
                        self.WriteStatus('ZoneTreble', value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateZoneTreble')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateZoneTreble')
        else:
            print('Invalid Command for UpdateZoneTreble')

    def SetZoneVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -70,
            'Max': 0
        }

        zone = qualifier['Zone']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if zone == 'All':
                ZoneVolumeCmdString = '#|{0}|F001|SVALL|{1}^{1}^{1}^{1}^{1}^{1}^{1}^{1}|U|\r\n'.format(self._DeviceAddress, str(-value).zfill(2))
            elif 1 <= int(zone) <= 8:
                ZoneVolumeCmdString = '#|{0}|F001|SV{1}|{2}|U|\r\n'.format(self._DeviceAddress, zone, str(-value).zfill(2))
            if ZoneVolumeCmdString:
                self.__SetHelper('ZoneVolume', ZoneVolumeCmdString, value, qualifier)
            else:
                print('Invalid Command for SetZoneVolume')
        else:
            print('Invalid Command for SetZoneVolume')

    def UpdateZoneVolume(self, value, qualifier):

        zone = qualifier['Zone']
        if (zone != 'All') and (1 <= int(zone) <= 8):
            ZoneVolumeCmdString = '#|{0}|F001|GV{1}|0|U|\r\n'.format(self._DeviceAddress, zone)
            res = self.__UpdateHelper('ZoneVolume', ZoneVolumeCmdString, value, qualifier)
            if res:
                try:
                    if res.split('|')[3][0:2] == 'V0' and res.split('|')[3][2] == zone:
                        value = int(res.split('|')[4])
                        if value == 150:
                            self.WriteStatus('ZoneVolume', -70, qualifier)
                        else:
                            self.WriteStatus('ZoneVolume', -value, qualifier)
                    else:
                        print('Invalid/unexpected response for UpdateZoneTreble')
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateZoneVolume')
        else:
            print('Invalid Command for UpdateZoneVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == '#':
            if response.split('|')[4] == 'L':
                print('Cannot execute the command "{0}" because device load is greater than 90%'.format(sourceCmdName))
                response = ''
        elif response[0] != '#':
            print('Invalid/unexpected response')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n').decode()
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n').decode()
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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

    def __init__(self, Hostname, IPPort=5001, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
