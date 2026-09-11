from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

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
        self.MonitorID = '1'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoAdjust': { 'Status': {}},
            'Input': { 'Status': {}},
            'IRRemoteLock': { 'Status': {}},
            'KeypadLock': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    @property
    def MonitorID(self):
        return self._MonitorID

    @MonitorID.setter
    def MonitorID(self, value):
        if value == 'Broadcast':
            self._MonitorID = b'\x00'
        elif 1 <= int(value) <= 255:
            self._MonitorID = pack('>B', int(value))
        else:
            print('Monitor ID Out of Range')

    def calcChecksum(self, commandstring):
        checksum = 0
        for i in commandstring:
            checksum = checksum ^ i
        return b''.join([commandstring, bytes([checksum])])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'    : b'\x00',
            'Custom' : b'\x01',
            'Real'   : b'\x02',
            'Full'   : b'\x03',
            '21:9'   : b'\x04'
        }

        AspectRatioCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x3A', ValueStateValues[value]]))
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : '4:3',
            b'\x01' : 'Custom',
            b'\x02' : 'Real',
            b'\x03' : 'Full',
            b'\x04' : '21:9'
        }

        AspectRatioCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x3B']))
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoAdjust(self, value, qualifier):

        AutoAdjustCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x05\x01\x70\x40\x00']))
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'           : b'\x05',
            'HDMI 1'        : b'\x0D',
            'HDMI 2'        : b'\x06',
            'HDMI 3'        : b'\x0F',
            'HDMI 4'        : b'\x19',
            'DisplayPort'   : b'\x0A',
            'DVI-D'         : b'\x0E',
            'OPS'           : b'\x0B',
            'Browser'       : b'\x10',
            'CMS'           : b'\x11',
            'Media Player'  : b'\x16',
            'PDF Player'    : b'\x17',
            'Custom'        : b'\x18'
        }

        InputCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x07\x01\xAC', ValueStateValues[value], b'\x00\x00\x00']))
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x05' : 'VGA',
            b'\x0D' : 'HDMI 1',
            b'\x06' : 'HDMI 2',
            b'\x0F' : 'HDMI 3',
            b'\x19' : 'HDMI 4',
            b'\x0A' : 'DisplayPort',
            b'\x0E' : 'DVI-D',
            b'\x0B' : 'OPS',
            b'\x10' : 'Browser',
            b'\x11' : 'CMS',
            b'\x16' : 'Media Player',
            b'\x17' : 'PDF Player',
            b'\x18' : 'Custom'
        }

        InputCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\xAD']))
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIRRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock All'                    : b'\x01',
            'Lock All'                      : b'\x02',
            'Lock All but Power'            : b'\x03',
            'Lock All but Volume'           : b'\x04',
            'Primary (Master)'              : b'\x05',
            'Secondary (Daisy Chain)'       : b'\x06',
            'Lock All but Power & Volume'   : b'\x07'
        }

        IRRemoteLockCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x1C', ValueStateValues[value]]))
        self.__SetHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def UpdateIRRemoteLock(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'Unlock All',
            b'\x02' : 'Lock All',
            b'\x03' : 'Lock All but Power',
            b'\x04' : 'Lock All but Volume',
            b'\x05' : 'Primary (Master)',
            b'\x06' : 'Secondary (Daisy Chain)',
            b'\x07' : 'Lock All but Power & Volume'
        }

        IRRemoteLockCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x1D']))
        res = self.__UpdateHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('IRRemoteLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Remote Lock: Invalid/unexpected response'])

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock All'                    : b'\x01',
            'Lock All'                      : b'\x02',
            'Lock All but Power'            : b'\x03',
            'Lock All but Volume'           : b'\x04',
            'Lock All but Power & Volume'   : b'\x07'
        }

        KeypadLockCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x1A', ValueStateValues[value]]))
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateKeypadLock(self, value, qualifier):

        ValueStateValues = {
            b'\x01' : 'Unlock All',
            b'\x02' : 'Lock All',
            b'\x03' : 'Lock All but Power',
            b'\x04' : 'Lock All but Volume',
            b'\x07' : 'Lock All but Power & Volume'
        }

        KeypadLockCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x1B']))
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keypad Lock: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x01'
        }

        PowerCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x18', ValueStateValues[value]]))
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On',
            b'\x01' : 'Off'
        }

        PowerCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x19']))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            volumeValue = bytes([value])
            VolumeCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x05\x01\x44', volumeValue, volumeValue]))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.calcChecksum(b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x45']))
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-2])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x03' : "NAK",
            b'\x00\x04' : "NAV (Checksum Error)"
        }

        if response[-3:-1] in DEVICE_ERROR_CODES:
            self.Error(['{0}: Error, {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[-3:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or self.MonitorID == b'\x00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = 9)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.MonitorID == b'\x00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = 9)
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
            print(command, 'does not exist in the module')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

