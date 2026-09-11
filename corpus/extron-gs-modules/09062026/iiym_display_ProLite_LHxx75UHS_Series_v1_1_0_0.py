# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from functools import reduce

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
        self._DeviceID = b'\x01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Input': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        self.RegexDict = {
            'Set':              re.compile(b'\x21[\x01-\xFF]\x00\x00\x04\x01\x00([\x00-\x04])[\x00-\xFF]'),
            'AspectRatio':      re.compile(b'\x21[\x01-\xFF]\x00\x00\x04\x01\x3B([\x00-\x06])[\x00-\xFF]'),
            'Input':            re.compile(b'\x21[\x01-\xFF]\x00\x00\x07\x01\xAD([\x06-\x17])\x00\x01\x00[\x00-\xFF]'),
            'OperationHours':   re.compile(b'\x21[\x01-\xFF]\x00\x00\x05\x01\x0F([\x00-\xFF][\x00-\xFF])[\x00-\xFF]'),
            'Power':            re.compile(b'\x21[\x01-\xFF]\x00\x00\x04\x01\x18([\x01\x02])[\x00-\xFF]'),
            'Volume':           re.compile(b'\x21[\x01-\xFF]\x00\x00\x05\x01\x45([\x00-\x64])[\x00-\x64][\x00-\xFF]')
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x00'
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value).to_bytes(1, 'big')
        else:
            self.Error('Invalid Device ID Parameter.')

    def checkSumHelper(self, byteString):
        byteList = [byteString[i:i + 1] for i in range(0, len(byteString), 1)]
        intList = []
        for x in byteList:
            intList.append(int.from_bytes(x, byteorder="big"))
        return reduce(lambda x, y: x ^ y, intList).to_bytes(1, 'big')

    def MessageHelper(self, command):
        commandLength = len(command) + 2
        message = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00', commandLength.to_bytes(1, 'big'), b'\x01', command])
        cks = self.checkSumHelper(message)
        return b''.join([message, cks])
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':      b'\x00',
            'Custom':   b'\x01',
            '1:1':      b'\x02',
            'Full':     b'\x03',
            '21:9':     b'\x04',
            'Dynamic':  b'\x05',
            '16:9':     b'\x06'
            }

        if value in ValueStateValues:
            AspectRatioCmdString = self.MessageHelper(b''.join([b'\x3A', ValueStateValues[value]]))
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.MessageHelper(b'\x3B')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x00': '4:3',
                    b'\x01': 'Custom',
                    b'\x02': '1:1',
                    b'\x03': 'Full',
                    b'\x04': '21:9',
                    b'\x05': 'Dynamic',
                    b'\x06': '16:9'
                    }

                valueMatch = self.RegexDict["AspectRatio"].match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.MessageHelper(b'\x70\x40\x00')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1':               b'\x0D',
            'HDMI 2':               b'\x06',
            'HDMI 3':               b'\x0F',
            'Display Port':         b'\x0A',
            'USB 1':                b'\x0C',
            'USB 2':                b'\x08',
            'Browser':              b'\x10',
            'SmartCMS':             b'\x11',
            'Digital Media Server': b'\x12',
            'Internal Storage':     b'\x13',
            'Media Player':         b'\x16',
            'PDF Player':           b'\x17'
            }

        if value in ValueStateValues:
            InputCmdString = self.MessageHelper(b''.join([b'\xAC', ValueStateValues[value], b'\x00\x00\x00']))
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.MessageHelper(b'\xAD')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x0D': 'HDMI 1',
                    b'\x06': 'HDMI 2',
                    b'\x0F': 'HDMI 3',
                    b'\x0A': 'Display Port',
                    b'\x0C': 'USB 1',
                    b'\x08': 'USB 2',
                    b'\x10': 'Browser',
                    b'\x11': 'SmartCMS',
                    b'\x12': 'Digital Media Server',
                    b'\x13': 'Internal Storage',
                    b'\x16': 'Media Player',
                    b'\x17': 'PDF Player'
                    }

                valueMatch = self.RegexDict["Input"].match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = self.MessageHelper(b'\x0F\x02')
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                valueMatch = self.RegexDict["OperationHours"].match(res)
                value = int.from_bytes(valueMatch.group(1), byteorder='big')
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x02',
            'Off':  b'\x01'
            }

        if value in ValueStateValues:
            PowerCmdString = self.MessageHelper(b''.join([b'\x18', ValueStateValues[value]]))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.MessageHelper(b'\x19')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'\x02': 'On',
                    b'\x01': 'Off'
                    }

                valueMatch = self.RegexDict["Power"].match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.MessageHelper(b''.join([b'\x44', value.to_bytes(1, 'big'), value.to_bytes(1, 'big')]))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.MessageHelper(b'\x45')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                valueMatch = self.RegexDict["Volume"].match(res)
                value = int.from_bytes(valueMatch.group(1), byteorder='big')
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': 'Upper Limit Surpassed',
            b'\x02': 'Lower Limit Surpassed',
            b'\x03': 'Command Cancelled',
            b'\x04': 'Parse Error'
        }

        if response:
            valueMatch = self.RegexDict["Set"].match(response)
            if valueMatch:
                if valueMatch.group(1) in DEVICE_ERROR_CODES:
                    self.Error(['An error has occurred for {}, Error is {}'.format(sourceCmdName, DEVICE_ERROR_CODES[valueMatch.group(1)])])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.RegexDict['Set'])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.RegexDict[command])
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

        self.Unidirectional = 'False'
        self.DefaultResponseTimeout = 0.3
        self.Debug = False
        self._DeviceID = b'\x01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'Input': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Volume': { 'Status': {}}
        }

        self.SetRegex = re.compile(b'\x21[\x01-\xFF]\x00\x00\x04\x01\x00([\x00-\x04])[\x00-\xFF]')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\x00'
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value).to_bytes(1, 'big')
        else:
            self.Error('Invalid Device ID Parameter.')

    def checkSumHelper(self, byteString):
        byteList = [byteString[i:i + 1] for i in range(0, len(byteString), 1)]
        intList = []
        for x in byteList:
            intList.append(int.from_bytes(x, byteorder="big"))
        return reduce(lambda x, y: x ^ y, intList).to_bytes(1, 'big')

    def MessageHelper(self, command):
        commandLength = len(command) + 2
        message = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00', commandLength.to_bytes(1, 'big'), b'\x01', command])
        cks = self.checkSumHelper(message)
        return b''.join([message, cks])
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3':      b'\x00',
            'Custom':   b'\x01',
            '1:1':      b'\x02',
            'Full':     b'\x03',
            '21:9':     b'\x04',
            'Dynamic':  b'\x05',
            '16:9':     b'\x06'
            }

        if value in ValueStateValues:
            AspectRatioCmdString = self.MessageHelper(b''.join([b'\x3A', ValueStateValues[value]]))
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')
    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.MessageHelper(b'\x70\x40\x00')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1':               b'\x0D',
            'HDMI 2':               b'\x06',
            'HDMI 3':               b'\x0F',
            'Display Port':         b'\x0A',
            'USB 1':                b'\x0C',
            'USB 2':                b'\x08',
            'Browser':              b'\x10',
            'SmartCMS':             b'\x11',
            'Digital Media Server': b'\x12',
            'Internal Storage':     b'\x13',
            'Media Player':         b'\x16',
            'PDF Player':           b'\x17'
            }

        if value in ValueStateValues:
            InputCmdString = self.MessageHelper(b''.join([b'\xAC', ValueStateValues[value], b'\x00\x00\x00']))
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = self.MessageHelper(b'\x18\x01')
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.MessageHelper(b''.join([b'\x44', value.to_bytes(1, 'big'), value.to_bytes(1, 'big')]))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': 'Upper Limit Surpassed',
            b'\x02': 'Lower Limit Surpassed',
            b'\x03': 'Command Cancelled',
            b'\x04': 'Parse Error'
        }

        if response:
            valueMatch = self.SetRegex.match(response)
            if valueMatch:
                if valueMatch.group(1) in DEVICE_ERROR_CODES:
                    self.Error(['An error has occurred for {}, Error is {}'.format(sourceCmdName, DEVICE_ERROR_CODES[valueMatch.group(1)])])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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