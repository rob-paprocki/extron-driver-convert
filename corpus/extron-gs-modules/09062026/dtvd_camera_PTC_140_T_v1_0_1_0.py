from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
from struct import pack

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
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'StorePreset': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            print('Device ID Parameter is out of range.')

    def SetHeader(self, commandstring):

        if 'Serial' not in self.ConnectionType:
            len_val = len(commandstring) + 2
            commandstring = b''.join([b'\x00', bytes([len_val]), commandstring])
        return commandstring

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority': 0x0B,
            'Bright': 0x0D
        }

        if value in ValueStateValues:
            AutoExposureCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = self.SetHeader(pack('5B', self._DeviceID, 0x09, 0x04, 0x39, 0xFF))
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[2])]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, ValueError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF))
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        AutoFocusCmdString = self.SetHeader(pack('5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF))
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[2])]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, ValueError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedStates = {
            '0': [0x20, 0x30],
            '1': [0x21, 0x31],
            '2': [0x22, 0x32],
            '3': [0x23, 0x33],
            '4': [0x24, 0x34],
            '5': [0x25, 0x35],
            '6': [0x26, 0x36],
            '7': [0x27, 0x37],
            '8': [0x28, 0x38],
            '9': [0x29, 0x39],
            '10': [0x2A, 0x3A],
            '11': [0x2B, 0x3B],
            '12': [0x2C, 0x3C],
            '13': [0x2D, 0x3D],
            '14': [0x2E, 0x3E],
            '15': [0x2F, 0x3F]
        }

        if qualifier['Speed'] in SpeedStates:
            ValueStateValues = {
                'Far': SpeedStates[qualifier['Speed']][0],
                'Near': SpeedStates[qualifier['Speed']][1],
                'Stop': 0x00
            }
            if value in ValueStateValues:
                FocusCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF))
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFocus')
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        if value in ValueStateValues:
            IrisCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF))
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        PanSpeedStates = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14,
            '21': 0x15,
            '22': 0x16,
            '23': 0x17,
            '24': 0x18
        }

        TiltSpeedStates = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,
            '10': 0x0A,
            '11': 0x0B,
            '12': 0x0C,
            '13': 0x0D,
            '14': 0x0E,
            '15': 0x0F,
            '16': 0x10,
            '17': 0x11,
            '18': 0x12,
            '19': 0x13,
            '20': 0x14
        }

        ValueStateValues = {
            'Up': [0x03, 0x01],
            'Down': [0x03, 0x02],
            'Left': [0x01, 0x03],
            'Right': [0x02, 0x03],
            'Up Left': [0x01, 0x01],
            'Up Right': [0x02, 0x01],
            'Down Left': [0x01, 0x02],
            'Down Right': [0x02, 0x02],
            'Stop': [0x03, 0x03],
            'Home': 0x04,
            'Reset': 0x05
        }

        if (qualifier['Pan Speed'] in PanSpeedStates and qualifier['Tilt Speed'] in TiltSpeedStates and
                    value in ValueStateValues):
            if value in ['Home', 'Reset']:
                PanTiltCmdString = self.SetHeader(pack('5B', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF))
            else:
                PanTiltCmdString = self.SetHeader(pack('9B', self._DeviceID, 0x01, 0x06, 0x01,
                                                PanSpeedStates[qualifier['Pan Speed']],
                                                TiltSpeedStates[qualifier['Tilt Speed']],
                                                ValueStateValues[value][0], ValueStateValues[value][1], 0xFF))
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            PowerCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PowerCmdString = self.SetHeader(pack('5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res[2])]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, ValueError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetRecallPreset(self, value, qualifier):

        if 0 <= int(value) <= 254:
            RecallPresetCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value), 0xFF))
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetStorePreset(self, value, qualifier):

        if 0 <= int(value) <= 254:
            StorePresetCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF))
            self.__SetHelper('StorePreset', StorePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStorePreset')

    def SetZoom(self, value, qualifier):

        SpeedStates = {
            '0': [0x20, 0x30],
            '1': [0x21, 0x31],
            '2': [0x22, 0x32],
            '3': [0x23, 0x33],
            '4': [0x24, 0x34],
            '5': [0x25, 0x35],
            '6': [0x26, 0x36],
            '7': [0x27, 0x37],
            '8': [0x28, 0x38],
            '9': [0x29, 0x39],
            '10': [0x2A, 0x3A],
            '11': [0x2B, 0x3B],
            '12': [0x2C, 0x3C],
            '13': [0x2D, 0x3D],
            '14': [0x2E, 0x3E],
            '15': [0x2F, 0x3F]
        }

        if qualifier['Speed'] in SpeedStates:
            ValueStateValues = {
                'Tele': SpeedStates[qualifier['Speed']][0],
                'Wide': SpeedStates[qualifier['Speed']][1],
                'Stop': 0x00
            }
            if value in ValueStateValues:
                ZoomCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x07, ValueStateValues[value], 0xFF))
                self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetZoom')
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if 'Serial' not in self.ConnectionType:
                response = response[2:]

            if response[1:3] == b'\x60\x02':
                self.Error(['{0}: Syntax Error'.format(sourceCmdName)])
                response = ''
            if response[1:3] == b'\x61\x41':
                self.Error(['{0}: Command Not Executable'.format(sourceCmdName)])
                response = ''
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

        if self.ConnectionType == 'Serial':
            self.Send(b'\x88\x30\x01\xFF')
            self.Send(b'\x88\x01\x00\x01\xFF')

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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