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
        self._DeviceID = b'\x01'
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FanSpeed': { 'Status': {}},
            'Mode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Temperature': { 'Status': {}},
            }
                        
        self.UpdateRes = re.compile(b'([\x00-\xFF][\x03-\x04]\x02[\x00-\xFF]{4,5})')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        id = int(value)
        if 1 <= id <= 255:
            self._DeviceID = bytes([id])

    def crc16(self, data):

        data = bytearray(data)
        poly = 0xA001
        crc = 0xFFFF
        for b in data:
            crc ^= (0xFF & b)
            for _ in range(0, 8):
                if (crc & 0x0001):
                    crc = ((crc >> 1) & 0xFFFF) ^ poly
                else:
                    crc = ((crc >> 1) & 0xFFFF)

        return crc & 0xFFFF

    def SetFanSpeed(self, value, qualifier):

        ValueStateValues = {
            'High'   : b'\x00\x01', 
            'Medium' : b'\x00\x02', 
            'Low'    : b'\x00\x03', 
            'Auto'   : b'\x00\x00'
        }

        CmdString = self._DeviceID + b'\x06\x00\x05' + ValueStateValues[value]
        CRC16 = self.crc16(CmdString)
        FanSpeedCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8]) 
        self.__SetHelper('FanSpeed', FanSpeedCmdString, value, qualifier)

    def UpdateFanSpeed(self, value, qualifier):

        ValueStateValues = {
            1 : 'High', 
            2 : 'Medium', 
            3 : 'Low', 
            0 : 'Auto'
        }

        CmdString = self._DeviceID + b'\x03\x00\x05\x00\x01'
        CRC16 = self.crc16(CmdString)
        FanSpeedCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8])
        res = self.__UpdateHelper('FanSpeed', FanSpeedCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3]]
                self.WriteStatus('FanSpeed', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Fan Speed: Invalid/unexpected response'])

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Cool'      : b'\x00\x01', 
            'Warm'      : b'\x00\x02', 
            'Ventilate' : b'\x00\x03'
        }

        CmdString = self._DeviceID + b'\x06\x00\x03' + ValueStateValues[value]
        CRC16 = self.crc16(CmdString)       
        ModeCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8]) 
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def UpdateMode(self, value, qualifier):

        ValueStateValues = {
            1 : 'Cool', 
            2 : 'Warm', 
            3 : 'Ventilate'
        }

        CmdString = self._DeviceID + b'\x03\x00\x03\x00\x01'
        CRC16 = self.crc16(CmdString)       
        ModeCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8])
        res = self.__UpdateHelper('Mode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3]]
                self.WriteStatus('Mode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x00\x01', 
            'Off' : b'\x00\x00', 
        }

        CmdString = self._DeviceID + b'\x06\x00\x02' + ValueStateValues[value]
        CRC16 = self.crc16(CmdString)    
        PowerCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        CmdString = self._DeviceID + b'\x03\x00\x02\x00\x01'
        CRC16 = self.crc16(CmdString) 
        PowerCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetTemperature(self, value, qualifier):

        if 3 <= value <= 35:
            CmdString = self._DeviceID + b'\x06\x00\x04' + (value*256).to_bytes(2, byteorder='big')
            CRC16 = self.crc16(CmdString)    
            TemperatureCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8]) 
            self.__SetHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemperature')

    def UpdateTemperature(self, value, qualifier):

        CmdString = self._DeviceID + b'\x04\x00\x00\x00\x01'
        CRC16 = self.crc16(CmdString)
        TemperatureCmdString = CmdString + bytes([CRC16&0xFF]) + bytes([CRC16>>8]) 
        res = self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        if res:
            try:
                value = int(int.from_bytes(res[-4:-2],byteorder='big')/256)
                self.WriteStatus('Temperature', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Temperature: Invalid/unexpected response'])

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRes)
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=4800, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model =None):
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

