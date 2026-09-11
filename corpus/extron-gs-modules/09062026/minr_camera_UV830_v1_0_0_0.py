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

        self._DeviceID = b'\x81'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ApertureControl': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Bright': {'Status': {}},
            'Focus': {'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'IRReceiver': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        DeviceIDStates = {
            '1': b'\x81',
            '2': b'\x82',
            '3': b'\x83',
            '4': b'\x84'
        }
        try:
            self._DeviceID = DeviceIDStates[value]
        except KeyError:
            self.Error(['DeviceID: Invalid Range.'])

    def SetApertureControl(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x04\x02\x02\xFF',
            'Down': b'\x01\x04\x02\x03\xFF',
            'Reset': b'\x01\x04\x02\x00\xFF'
        }

        ApertureControlCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('ApertureControl', ApertureControlCmdString, value, qualifier)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': b'\x01\x04\x39\x00\xFF',
            'Manual': b'\x01\x04\x39\x03\xFF',
            'Shutter Priority': b'\x01\x04\x39\x0A\xFF',
            'Iris Priority': b'\x01\x04\x39\x0B\xFF',
            'Bright': b'\x01\x04\x39\x0D\xFF'
        }

        AutoExposureCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0: 'Full Auto',
            3: 'Manual',
            10: 'Shutter Priority',
            11: 'Iris Priority',
            13: 'Bright'
        }

        AutoExposureCmdString = self._DeviceID + b'\x09\x04\x39\xFF'
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = self._DeviceID + b'\x01\x04\x18\x01\xFF'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            2: 'Auto',
            3: 'Manual'
        }

        AutoFocusCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBright(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x04\x0D\x02\xFF',
            'Down': b'\x01\x04\x0D\x03\xFF',
            'Reset': b'\x01\x04\x0D\x00\xFF'
        }

        BrightCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Bright', BrightCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': b'\x01\x04\x08\x03\xFF',
            'Far': b'\x01\x04\x08\x02\xFF',
            'Stop': b'\x01\x04\x08\x00\xFF'
        }

        FocusCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x04\x0C\x02\xFF',
            'Down': b'\x01\x04\x0C\x03\xFF',
            'Reset': b'\x01\x04\x0C\x00\xFF'
        }

        GainCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Gain', GainCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x0B\x00\xFF',
            'Up': b'\x01\x04\x0B\x02\xFF',
            'Down': b'\x01\x04\x0B\x03\xFF'
        }

        IrisCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetIRReceiver(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x06\x08\x02\xFF',
            'Off': b'\x01\x06\x08\x03\xFF'
        }

        IRReceiverCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('IRReceiver', IRReceiverCmdString, value, qualifier)

    def UpdateIRReceiver(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            3: 'Off'
        }

        IRReceiverCmdString = self._DeviceID + b'\x09\x06\x08\xFF'
        res = self.__UpdateHelper('IRReceiver', IRReceiverCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('IRReceiver', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Receiver: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Up Left': b'\x01\x01',
            'Up Right': b'\x02\x01',
            'Down Left': b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop': b'\x03\x03'
        }

        panSpeed = qualifier['Pan Speed']
        tiltSpeed = qualifier['Tilt Speed']

        PanTiltCmdString = ''
        if value == 'Home':
            PanTiltCmdString = self._DeviceID + b'\x01\x06\x04\xFF'
        elif value == 'Reset':
            PanTiltCmdString = self._DeviceID + b'\x01\x06\x05\xFF'
        elif 1 <= panSpeed <= 24 and 1 <= tiltSpeed <= 20:
            PanTiltCmdString = b''.join([self._DeviceID, b'\x01\x06\x01', bytes([panSpeed, tiltSpeed]), ValueStateValues[value], b'\xFF'])
        if PanTiltCmdString:
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        PowerCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            3: 'Off'
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

        if 0 <= int(value) <= 9:
            PresetRecallCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F\x02', bytes([int(value)]), b'\xFF'])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 9:
            PresetSaveCmdString = b''.join([self._DeviceID, b'\x01\x04\x3F\x01', bytes([int(value)]), b'\xFF'])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x04\x0A\x02\xFF',
            'Down': b'\x01\x04\x0A\x03\xFF',
            'Reset': b'\x01\x04\x0A\x00\xFF'
        }

        ShutterCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x04\x35\x00\xFF',
            'Indoor': b'\x01\x04\x35\x01\xFF',
            'Outdoor': b'\x01\x04\x35\x02\xFF',
            'OnePush': b'\x01\x04\x35\x03\xFF',
            'Manual': b'\x01\x04\x35\x05\xFF'
        }

        WhiteBalanceCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0: 'Auto',
            1: 'Indoor',
            2: 'Outdoor',
            3: 'OnePush',
            4: 'ATW',
            5: 'Manual'
        }

        WhiteBalanceCmdString = self._DeviceID + b'\x09\x04\x35\xFF'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30
        }

        zoomSpeed = qualifier['Speed']
        ZoomCmdString = ''
        if value == 'Stop':
            ZoomCmdString = self._DeviceID + b'\x01\x04\x07\x00\xFF'
        elif 0 <= zoomSpeed <= 7 and value in ValueStateValues:
            ZoomCmdString = b''.join([self._DeviceID, b'\x01\x04\x07', bytes([ValueStateValues[value] + zoomSpeed]), b'\xFF'])

        if ZoomCmdString:
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {
            0x60: '{} : Syntax Error.'.format(sourceCmdName),
            0x61: '{} : Command Not Executable.'.format(sourceCmdName)
        }
        if len(response) == 4 and response[1] in ErrorStates:
            self.Error([ErrorStates[response[1]]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{0} : Unexpected/Invalid response'.format(command)])
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