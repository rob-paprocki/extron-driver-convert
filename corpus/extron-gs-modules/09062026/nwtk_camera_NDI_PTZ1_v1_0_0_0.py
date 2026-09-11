from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack

class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'RecallPreset': { 'Status': {}},
            'SavePreset': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
        }


        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = 0

    def ResetSequence(self, value, qualifier):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')

    def IncSequenceNumber(self):
        if self.StartSequence == 0:
            self.ResetSequence(None, None)
            self.PrevSequence = 1
        else:
            self.PrevSequence = (self.PrevSequence + 1) & 0xFFFFFFFF

        return pack('>I', self.PrevSequence)

    def SetHeader(self, commandstring):
        return b'\x01\x00\x00' + pack('B', len(commandstring)) + self.IncSequenceNumber() + commandstring

    def GetHeader(self, commandstring):
        return b'\x01\x10\x00' + pack('B', len(commandstring)) + self.IncSequenceNumber() + commandstring

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : 0x0301,
            'Down'       : 0x0302,
            'Left'       : 0x0103,
            'Right'      : 0x0203,
            'Up Left'    : 0x0101,
            'Up Right'   : 0x0201,
            'Down Left'  : 0x0102,
            'Down Right' : 0x0202,
            'Stop'       : 0x0303
        }

        if value in ValueStateValues and 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 24:
            PanTiltCmdString = self.SetHeader(pack('>6BHB', 0x81, 0x01, 0x06, 0x01, qualifier['Tilt Speed'], qualifier['Pan Speed'], ValueStateValues[value], 0xFF))
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        if value in ValueStateValues:
            PowerCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x00,ValueStateValues[value], 0xFF))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On',
            b'\x03' : 'Off'
        }

        PowerCmdString = self.GetHeader(pack('>5B', 0x81, 0x09, 0x04, 0x00, 0xFF))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            RecallPresetCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x02, int(value)-1, 0xFF))
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')
    def SetSavePreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            SavePresetCmdString = self.SetHeader(pack('>7B', 0x81, 0x01, 0x04, 0x3F, 0x01, int(value)-1, 0xFF))
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        if value in ValueStateValues and 0 <= qualifier['Zoom Speed'] <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = qualifier['Zoom Speed'] + ValueStateValues[value]

            ZoomCmdString = self.SetHeader(pack('>6B', 0x81, 0x01, 0x04, 0x07, zoomSpeed, 0xFF))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if len(response) > 8:
            response = response[8:]

        if response:
            if len(response) == 4:
                Errors = {
                    0x01: 'Message Length Error',
                    0x02: 'Syntax Error',
                    0x03: 'Command Buffer Full',
                    0x04: 'Command Cancelled',
                    0x05: 'No Socket',
                    0x41: 'Command Not Executable',
                }

                address, errorbyte, errorcode, terminator = unpack('>4B', response)
                if errorbyte & 0x60 == 0x60:
                    self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, Errors.get(errorcode, 'Unknown Error'))])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['Invalid/unexpected response'])
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
                if command == 'Power':
                    self.StartSequence = 0

                return ''
            else:
                self.StartSequence = 1

                return self.__CheckResponseForErrors(command, res)
     
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.ResetSequence( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = 0

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
        self._DeviceID = 1
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'RecallPreset': { 'Status': {}},
            'SavePreset': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            self.Error(['Device ID Out of Range'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'         : 0x0301,
            'Down'       : 0x0302,
            'Left'       : 0x0103,
            'Right'      : 0x0203,
            'Up Left'    : 0x0101,
            'Up Right'   : 0x0201,
            'Down Left'  : 0x0102,
            'Down Right' : 0x0202,
            'Stop'       : 0x0303
        }

        if value in ValueStateValues and 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 24:
            PanTiltCmdString = pack('>6BHB', self.DeviceID, 0x01, 0x06, 0x01, qualifier['Tilt Speed'], qualifier['Pan Speed'], ValueStateValues[value], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x00,ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On',
            b'\x03' : 'Off'
        }

        PowerCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            RecallPresetCmdString = pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value)-1, 0xFF)
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')
    def SetSavePreset(self, value, qualifier):

        if 1 <= int(value) <= 16:
            SavePresetCmdString = pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value)-1, 0xFF)
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        if value in ValueStateValues and 0 <= qualifier['Zoom Speed'] <= 7:
            if value == 'Stop':
                zoomSpeed = 0x00
            else:
                zoomSpeed = qualifier['Zoom Speed'] + ValueStateValues[value]

            ZoomCmdString =pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, zoomSpeed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                Errors = {
                    0x01: 'Message Length Error',
                    0x02: 'Syntax Error',
                    0x03: 'Command Buffer Full',
                    0x04: 'Command Cancelled',
                    0x05: 'No Socket',
                    0x41: 'Command Not Executable',
                }

                address, errorbyte, errorcode, terminator = unpack('>4B', response)
                if errorbyte & 0x60 == 0x60:
                    self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, Errors.get(errorcode, 'Unknown Error'))])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['Invalid/unexpected response'])
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
                if command == 'Power':
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
