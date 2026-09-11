from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Shade': {'Parameters': ['Address'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b':([A-F\d]{2})030200([A-F\d]{2})[A-F\d]{2}\r\n'), self.__MatchShade, None)

    def SetShade(self, value, qualifier):

        address = int(qualifier['Address'])

        ValueStateValues = {
            'Previous Preset (Tilt)':   '04',
            'Next Preset (Tilt)':       '07',
            'Tilt Closed':              '16',
            'Tilt Open':                '1A',
            'Preset 1 (Extent)':        '1E',
            'Preset 2 (Extent)':        '1F',
            'Preset 3 (Extent)':        '20',
            'Preset 4 (Extent)':        '21',
            'Preset 5 (Extent)':        '22',
            'Preset 6 (Extent)':        '23',
            'Preset 7 (Extent)':        '24',
            'Preset 8 (Extent)':        '25',
            'Preset 9 (Extent)':        '26',
            'Preset 10 (Extent)':       '27',
            'Stop':                     '28',
            'Preset 1 (Tilt)':          '3A',
            'Preset 2 (Tilt)':          '3B',
            'Preset 3 (Tilt)':          '3C',
            'Preset 4 (Tilt)':          '3D',
            'Preset 5 (Tilt)':          '3E',
            'Preset 6 (Tilt)':          '3F',
            'Preset 7 (Tilt)':          '40',
            'Preset 8 (Tilt)':          '41',
            'Preset 9 (Tilt)':          '42',
            'Preset 10 (Tilt)':         '43',
            'Retract':                  '4B',
            'Clear Override':           '4C',
            'Extend':                   '4E',
            'Next Preset (Extent)':     '4F',
            'Previous Preset (Extent)': '50'
        }

        if 0 <= address <= 255 and value in ValueStateValues:
            ShadeCmdString = ':{:02X}06000100{}--\r\n'.format(address, ValueStateValues[value])
            self.__SetHelper('Shade', ShadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShade')

    def UpdateShade(self, value, qualifier):

        address = int(qualifier['Address'])

        if 0 <= address <= 255:
            ShadeCmdString = ':{:02X}0300010001--\r\n'.format(address)
            self.__UpdateHelper('Shade', ShadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateShade')

    def __MatchShade(self, match, tag):

        ValueStateValues = {
            '04': 'Previous Preset (Tilt)',
            '07': 'Next Preset (Tilt)',
            '16': 'Tilt Closed',
            '1A': 'Tilt Open',
            '1E': 'Preset 1 (Extent)',
            '1F': 'Preset 2 (Extent)',
            '20': 'Preset 3 (Extent)',
            '21': 'Preset 4 (Extent)',
            '22': 'Preset 5 (Extent)',
            '23': 'Preset 6 (Extent)',
            '24': 'Preset 7 (Extent)',
            '25': 'Preset 8 (Extent)',
            '26': 'Preset 9 (Extent)',
            '27': 'Preset 10 (Extent)',
            '28': 'Stop',
            '3A': 'Preset 1 (Tilt)',
            '3B': 'Preset 2 (Tilt)',
            '3C': 'Preset 3 (Tilt)',
            '3D': 'Preset 4 (Tilt)',
            '3E': 'Preset 5 (Tilt)',
            '3F': 'Preset 6 (Tilt)',
            '40': 'Preset 7 (Tilt)',
            '41': 'Preset 8 (Tilt)',
            '42': 'Preset 9 (Tilt)',
            '43': 'Preset 10 (Tilt)',
            '4B': 'Retract',
            '4C': 'Clear Override',
            '4E': 'Extend',
            '4F': 'Next Preset (Extent)',
            '50': 'Previous Preset (Extent)'
        }

        qualifier = {
            'Address': str(int(match.group(1).decode(), 16))
        }

        value = ValueStateValues.get(match.group(2).decode(), str(int(match.group(2).decode(), 16)))
        self.WriteStatus('Shade', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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
        
    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Shade': {'Parameters': ['Address'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x00\x00\x00\x00\x00\x05([\x00-\xFF])\x03\x02\x00([\x00-\xFF])'), self.__MatchShade, None)

    def SetShade(self, value, qualifier):

        address = int(qualifier['Address'])

        ValueStateValues = {
            'Previous Preset (Tilt)':   b'\x04',
            'Next Preset (Tilt)':       b'\x07',
            'Tilt Closed':              b'\x16',
            'Tilt Open':                b'\x1A',
            'Preset 1 (Extent)':        b'\x1E',
            'Preset 2 (Extent)':        b'\x1F',
            'Preset 3 (Extent)':        b'\x20',
            'Preset 4 (Extent)':        b'\x21',
            'Preset 5 (Extent)':        b'\x22',
            'Preset 6 (Extent)':        b'\x23',
            'Preset 7 (Extent)':        b'\x24',
            'Preset 8 (Extent)':        b'\x25',
            'Preset 9 (Extent)':        b'\x26',
            'Preset 10 (Extent)':       b'\x27',
            'Stop':                     b'\x28',
            'Preset 1 (Tilt)':          b'\x3A',
            'Preset 2 (Tilt)':          b'\x3B',
            'Preset 3 (Tilt)':          b'\x3C',
            'Preset 4 (Tilt)':          b'\x3D',
            'Preset 5 (Tilt)':          b'\x3E',
            'Preset 6 (Tilt)':          b'\x3F',
            'Preset 7 (Tilt)':          b'\x40',
            'Preset 8 (Tilt)':          b'\x41',
            'Preset 9 (Tilt)':          b'\x42',
            'Preset 10 (Tilt)':         b'\x43',
            'Retract':                  b'\x4B',
            'Clear Override':           b'\x4C',
            'Extend':                   b'\x4E',
            'Next Preset (Extent)':     b'\x4F',
            'Previous Preset (Extent)': b'\x50'
        }

        if 0 <= address <= 255 and value in ValueStateValues:
            ShadeCmdString = b'\x00\x00\x00\x00\x00\x06' + bytes([address]) + b'\x06\x00\x01\x00' + ValueStateValues[value]
            self.__SetHelper('Shade', ShadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShade')

    def UpdateShade(self, value, qualifier):

        address = int(qualifier['Address'])

        if 0 <= address <= 255:
            ShadeCmdString = b'\x00\x00\x00\x00\x00\x06' + bytes([address]) + b'\x03\x00\x01\x00\x01'
            self.__UpdateHelper('Shade', ShadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateShade')

    def __MatchShade(self, match, tag):

        ValueStateValues = {
            b'\x04': 'Previous Preset (Tilt)',
            b'\x07': 'Next Preset (Tilt)',
            b'\x16': 'Tilt Closed',
            b'\x1A': 'Tilt Open',
            b'\x1E': 'Preset 1 (Extent)',
            b'\x1F': 'Preset 2 (Extent)',
            b'\x20': 'Preset 3 (Extent)',
            b'\x21': 'Preset 4 (Extent)',
            b'\x22': 'Preset 5 (Extent)',
            b'\x23': 'Preset 6 (Extent)',
            b'\x24': 'Preset 7 (Extent)',
            b'\x25': 'Preset 8 (Extent)',
            b'\x26': 'Preset 9 (Extent)',
            b'\x27': 'Preset 10 (Extent)',
            b'\x28': 'Stop',
            b'\x3A': 'Preset 1 (Tilt)',
            b'\x3B': 'Preset 2 (Tilt)',
            b'\x3C': 'Preset 3 (Tilt)',
            b'\x3D': 'Preset 4 (Tilt)',
            b'\x3E': 'Preset 5 (Tilt)',
            b'\x3F': 'Preset 6 (Tilt)',
            b'\x40': 'Preset 7 (Tilt)',
            b'\x41': 'Preset 8 (Tilt)',
            b'\x42': 'Preset 9 (Tilt)',
            b'\x43': 'Preset 10 (Tilt)',
            b'\x4B': 'Retract',
            b'\x4C': 'Clear Override',
            b'\x4E': 'Extend',
            b'\x4F': 'Next Preset (Extent)',
            b'\x50': 'Previous Preset (Extent)'
        }

        qualifier = {
            'Address': str(match.group(1)[0])
        }

        value = ValueStateValues.get(match.group(2), str(match.group(2)[0]))
        self.WriteStatus('Shade', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
            
class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()