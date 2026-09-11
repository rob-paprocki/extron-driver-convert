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
        self._ModuleAddress = '00'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ModuleConfiguration': {'Status': {}},
            'Scene': {'Status': {}},
            'SceneIntensity': {'Status': {}},
            'WriteScene': {'Status': {}},
            'Zone': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneIntensity': {'Parameters': ['Zone'], 'Status': {}},
            'ZoneIntensityStatus': {'Parameters': ['Zone'], 'Status': {}},
        }


    @property
    def ModuleAddress(self):
        return self._ModuleAddress

    @ModuleAddress.setter
    def ModuleAddress(self, value):
        if 0 <= int(value) <= 29:
            self.ModuleAddress = str(tempAddress).zfill(2)
        else:
            print('Invalid ModuleAddress Parameter. Range is from 0 to 29')


    def SetModuleConfiguration(self, value, qualifier):

        state = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Mode 3': '3',
            'Mode 5': '5',
            'Mode 6': '6',
            'Mode 7': '7'
        }[value]

        ModuleConfigurationCmdString = '$D{0}P{1}ST\r'.format(self.ModuleAddress, state)
        self.__SetHelper('ModuleConfiguration', ModuleConfigurationCmdString, value, qualifier)

    def SetScene(self, value, qualifier):

        state = int(value) - 1
        if 0 <= state <= 99:
            SceneCmdString = '$D{0}C{1}\r'.format(self.ModuleAddress, str(state).zfill(2))
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def UpdateZoneIntensityStatus(self, value, qualifier):
        self.UpdateScene(value, qualifier)
        
    def UpdateScene(self, value, qualifier):

        SceneCmdString = '$D{0}ST\r'.format(self.ModuleAddress)
        res = self.__UpdateHelper('Scene', SceneCmdString, value, qualifier)
        if res:
            try:
                tempVal = re.search('\*D\d+C(\d+)\r', res)
                value = str(int(tempVal.group(1)) + 1)
                self.WriteStatus('Scene', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Scene: Invalid/unexpected response'])

            try:
                zoneVal = re.findall('\*D\d+Z(\d)I(\d+)\r', res)
                for zone in zoneVal:
                    self.WriteStatus('ZoneIntensityStatus', int(zone[1]), {'Zone': zone[0]})
            except (ValueError, IndexError):
                self.Error(['ZoneIntensityStatus: Invalid/unexpected response'])

    def SetSceneIntensity(self, value, qualifier):

        state = {
            'Increment': '+',
            'Decrement': '-'
        }[value]

        SceneIntensityCmdString = '$D{0}C{1}\r'.format(self.ModuleAddress, state)
        self.__SetHelper('SceneIntensity', SceneIntensityCmdString, value, qualifier)

    def SetWriteScene(self, value, qualifier):

        WriteSceneCmdString = '$D{0}GRAVA\r'.format(self.ModuleAddress)
        self.__SetHelper('WriteScene', WriteSceneCmdString, value, qualifier)

    def SetZone(self, value, qualifier):

        state = {
            'On': 'L',
            'Off': 'D'
        }[value]

        zone = int(qualifier['Zone'])

        if 1 <= zone <= 8:
            ZoneCmdString = '$D{0}Z{1}{2}\r'.format(self.ModuleAddress, zone, state)
            self.__SetHelper('Zone', ZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone')

    def SetZoneIntensity(self, value, qualifier):

        state = {
            'Increment': '+',
            'Decrement': '-'
        }[value]

        zone = int(qualifier['Zone'])

        if 1 <= zone <= 8:
            ZoneIntensityCmdString = '$D{0}Z{1}{2}\r'.format(self.ModuleAddress, zone, state)
            self.__SetHelper('ZoneIntensity', ZoneIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneIntensity')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'E1' in response:
            self.Error(['Start Buffer Error'])
            response = ''
        elif 'E2' in response:
            self.Error(['End Buffer Error'])
            response = ''
        elif 'E3' in response:
            self.Error(['Module Non-existent'])
            response = ''
        elif 'E4' in response:
            self.Error(['Syntax Error'])
            response = ''
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
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
