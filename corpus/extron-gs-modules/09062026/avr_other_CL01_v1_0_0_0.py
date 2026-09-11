from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
from struct import pack

class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'Home': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = bytes([0x80 + int(value)])
        else:
            self.Error(['Device ID Out of Range'])

    def SetHome(self, value, qualifier):

        HomeCmdString = self._DeviceID + b'\x01\x06\x04\xFF'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : b'\x03\x01',
            'Down'       : b'\x03\x02',
            'Left'       : b'\x01\x03',
            'Right'      : b'\x02\x03',
            'Up Left'    : b'\x01\x01',
            'Up Right'   : b'\x02\x01',
            'Down Left'  : b'\x01\x02',
            'Down Right' : b'\x02\x02',
            'Stop'       : b'\x03\x03'
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

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + b'\x01\x04\x00' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= value <= 255:
            PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + bytes([int(value)]) + b'\xFF'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= value <= 255:
            PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + bytes([int(value)]) + b'\xFF'
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        if value in ValueStateValues:
            ZoomCmdString = self._DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

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

class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'Home': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 8:
            self._DeviceID = bytes([0x80 + int(value)])
        else:
            self.Error(['Device ID Out of Range'])

    def SetHeader(self, commandstring):

        return b'\x01\x00\x00' + pack('B', len(commandstring)) + b'\x00\x00\x00\x01' + commandstring
    
    def SetHome(self, value, qualifier):

        HomeCmdString = self.SetHeader(self._DeviceID + b'\x01\x06\x04\xFF')
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : b'\x03\x01',
            'Down'       : b'\x03\x02',
            'Left'       : b'\x01\x03',
            'Right'      : b'\x02\x03',
            'Up Left'    : b'\x01\x01',
            'Up Right'   : b'\x02\x01',
            'Down Left'  : b'\x01\x02',
            'Down Right' : b'\x02\x02',
            'Stop'       : b'\x03\x03'
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
            
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x00' + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
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

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        if value in ValueStateValues:
            ZoomCmdString = self.SetHeader(self._DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF')
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])