from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Home': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'PiPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'ProfileRecall': { 'Status': {}},
            'ProfileSave': { 'Status': {}},
            'Tracking': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 8:
            self._DeviceID = bytes([0x80 + int(value)])
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetHome(self, value, qualifier):

        HomeCmdString = self._DeviceID + b'\x01\x06\x04\xFF'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'            : b'\x03\x01',
            'Down'          : b'\x03\x02',
            'Left'          : b'\x01\x03',
            'Right'         : b'\x02\x03',
            'Up Left'       : b'\x01\x01',
            'Up Right'      : b'\x02\x01',
            'Down Left'     : b'\x01\x02',
            'Down Right'    : b'\x02\x02',
            'Stop'          : b'\x03\x03'
        }

        if 1 <= qualifier['Pan Speed'] <= 15 and 1 <= qualifier['Tilt Speed'] <= 15:
            if value == 'Stop':
                speed = b'\x00\x00'
            else:
                speed = bytes([qualifier['Pan Speed'], qualifier['Tilt Speed']])
            PanTiltCmdString = self._DeviceID + b'\x01\x06\x01' + speed + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('PanTilt', PanTiltCmdString, value,qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPiPMode(self, value, qualifier):

        ValueStateValues = {
            'Off'   : b'\x02\x00',
            '1'     : b'\x01\x01',
            '2'     : b'\x01\x02',
            '3'     : b'\x01\x03',
            '4'     : b'\x01\x04',
            '5'     : b'\x01\x05',
            '6'     : b'\x01\x06',
            '7'     : b'\x01\x07',
            '8'     : b'\x01\x08'
        }

        if value in ValueStateValues:
            PiPModeCmdString = self._DeviceID + b'\x01\x04\x7F' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('PiPMode', PiPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPiPMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + b'\x01\x04\x00' + ValueStateValues[value] + b'\xFF'
            PowerCmdString += PowerCmdString #Based on testing with the device
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 255:
            PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + bytes([int(value)]) + b'\xFF'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = self._DeviceID + b'\x09\x04\x3F\xFF'
        res = self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        if res:
            try:
                value = res[2]
                self.WriteStatus('PresetRecall', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Preset Recall: Invalid/unexpected response'])

    def SetPresetSave(self, value, qualifier):

        if 1 <= value <= 255:
            PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + bytes([int(value)]) + b'\xFF'
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetProfileRecall(self, value, qualifier):

        if 1 <= int(value) <= 5:
            ProfileRecallCmdString = self._DeviceID + b'\x01\x04\x40\x01' + bytes([int(value)]) + b'\xFF'
            self.__SetHelper('ProfileRecall', ProfileRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProfileRecall')

    def SetProfileSave(self, value, qualifier):

        if 1 <= int(value) <= 5:
            ProfileSaveCmdString = self._DeviceID + b'\x01\x04\x40\x02' + bytes([int(value)]) + b'\xFF'
            self.__SetHelper('ProfileSave', ProfileSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProfileSave')

    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            TrackingCmdString = self._DeviceID + b'\x01\x04\x7D' + ValueStateValues[value] + b'\x00\xFF'
            self.__SetHelper('Tracking', TrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTracking')

    def SetZoom(self, value, qualifier):

        if 0 <= qualifier['Speed'] <= 7 and value in ['Tele', 'Wide', 'Stop']:
            ValueStateValues = {
                'Tele': 0x20 + qualifier['Speed'],
                'Wide': 0x30 + qualifier['Speed'],
                'Stop': 0x00
            }
            ZoomCmdString = self._DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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

class DeviceEthernetClass:
    
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self._DeviceID = b'\x81'
        self.ConnectionType = 'Ethernet'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Home': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'PiPMode': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'ProfileRecall': { 'Status': {}},
            'ProfileSave': { 'Status': {}},
            'Tracking': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

    def SetHeader(self, commandstring):

        if 'Serial' in self.ConnectionType:
            return commandstring
        else:
            return b'\x01\x00\x00' + pack('B', len(commandstring)) + b'\x00\x00\x00\x01' + commandstring
        
    def SetHome(self, value, qualifier):

        HomeCmdString = self.SetHeader(self._DeviceID + b'\x01\x06\x04\xFF')
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'            : b'\x03\x01',
            'Down'          : b'\x03\x02',
            'Left'          : b'\x01\x03',
            'Right'         : b'\x02\x03',
            'Up Left'       : b'\x01\x01',
            'Up Right'      : b'\x02\x01',
            'Down Left'     : b'\x01\x02',
            'Down Right'    : b'\x02\x02',
            'Stop'          : b'\x03\x03'
        }

        if 1 <= qualifier['Pan Speed'] <= 15 and 1 <= qualifier['Tilt Speed'] <= 15:
            if value == 'Stop':
                speed = b'\x00\x00'
            else:
                speed = bytes([qualifier['Pan Speed'], qualifier['Tilt Speed']])
            PanTiltCmdString = self.SetHeader(self._DeviceID + b'\x01\x06\x01' + speed + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('PanTilt', PanTiltCmdString, value,qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPiPMode(self, value, qualifier):

        ValueStateValues = {
            'Off'   : b'\x02\x00',
            '1'     : b'\x01\x01',
            '2'     : b'\x01\x02',
            '3'     : b'\x01\x03',
            '4'     : b'\x01\x04',
            '5'     : b'\x01\x05',
            '6'     : b'\x01\x06',
            '7'     : b'\x01\x07',
            '8'     : b'\x01\x08'
        }

        if value in ValueStateValues:
            PiPModeCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x7F' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('PiPMode', PiPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPiPMode')
            
    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x00\x03\xFF')
        PowerOffCmdString += PowerOffCmdString #Based on testing with the device
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 255:
            PresetRecallCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x3F\x02' + bytes([int(value)]) + b'\xFF')
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= value <= 255:
            PresetSaveCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x3F\x01' + bytes([int(value)]) + b'\xFF')
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetProfileRecall(self, value, qualifier):

        if 1 <= int(value) <= 5:
            ProfileRecallCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x40\x01' + bytes([int(value)]) + b'\xFF')
            self.__SetHelper('ProfileRecall', ProfileRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProfileRecall')

    def SetProfileSave(self, value, qualifier):

        if 1 <= int(value) <= 5:
            ProfileSaveCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x40\x02' + bytes([int(value)]) + b'\xFF')
            self.__SetHelper('ProfileSave', ProfileSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProfileSave')

    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            TrackingCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x7D' + ValueStateValues[value] + b'\x00\xFF')
            self.__SetHelper('Tracking', TrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTracking')

    def SetZoom(self, value, qualifier):

        if 0 <= qualifier['Speed'] <= 7 and value in ['Tele', 'Wide', 'Stop']:
            ValueStateValues = {
                'Tele': 0x20 + qualifier['Speed'],
                'Wide': 0x30 + qualifier['Speed'],
                'Stop': 0x00
            }
            ZoomCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF')
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if 'Serial' not in self.ConnectionType:
            self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')  # send Reset Sequence command
        self.Send(commandstring)

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])