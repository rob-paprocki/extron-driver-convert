from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Light': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetStore': {'Status': {}},
            'Recording': {'Status': {}},
            'Snapshot': {'Status': {}},
            'Source': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }

        self.SetRegex = re.compile(b'(\x01[\x00-\xFF]\x00)|(\x81[\x00-\xFF][\x01-\x09])')
        self.UpdateRegex = re.compile(b'([\x00|\x08][\x00-\xFF][\x00-\x04][\x00-\x05][\x00-\x64]{0,3})|(\x80[\x00-\xFF][\x01-\x09])')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x31\x01\x01',
            'Off': b'\x01\x31\x01\x00'
        }

        if value in ValueStateValues:
            AutoFocusCmdString = ValueStateValues[value]
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AutoFocusCmdString = b'\x00\x31\x00'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x01,
            'Near': 0x02,
            'Stop': 0x00
        }

        if value in ValueStateValues and 1 <= int(qualifier['Speed']) <= 15:
            if value == 'Stop':
                FocusCmdString = pack('>4B', 0x01, 0x2F, 0x01, ValueStateValues[value])
            else:
                FocusCmdString = pack('>6B', 0x01, 0x21, 0x03, ValueStateValues[value], 0x00, int(qualifier['Speed']))
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x56\x01\x01',
            'Off': b'\x01\x56\x01\x00'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        FreezeCmdString = b'\x00\x56\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\xA0\x01\x01',
            'Off': b'\x01\xA0\x01\x00',
            'Slidebox On': b'\x01\xA0\x01\x03'
        }

        if value in ValueStateValues:
            LightCmdString = ValueStateValues[value]
            if value != 'Slidebox On':
                self.__SetHelper('Light', LightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLight')

    def UpdateLight(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
        }

        LightCmdString = b'\x00\xA0\x00'
        res = self.__UpdateHelper('Light', LightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Light', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Light: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x30\x01\x01',
            'Off': b'\x01\x30\x01\x00'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\x00\x30\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x01\x40\x01\x00',
            '1': b'\x01\x40\x01\x01',
            '2': b'\x01\x40\x01\x02',
            '3': b'\x01\x40\x01\x03',
            'Default': b'\x01\x40\x01\x04'
        }

        if value in ValueStateValues:
            PresetRecallCmdString = ValueStateValues[value]
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetStore(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x01\x41\x01\x00',
            '1': b'\x01\x41\x01\x01',
            '2': b'\x01\x41\x01\x02',
            '3': b'\x01\x41\x01\x03'
        }

        if value in ValueStateValues:
            PresetStoreCmdString = ValueStateValues[value]
            self.__SetHelper('PresetStore', PresetStoreCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetStore')

    def SetRecording(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\x01\x03\x01\x01\x01',
            'Stop': b'\x01\x03\x01\x01\x00',
            'Pause': b'\x01\x03\x01\x01\x02'
        }

        if value in ValueStateValues:
            RecordingCmdString = ValueStateValues[value]
            self.__SetHelper('Recording', RecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecording')

    def SetSnapshot(self, value, qualifier):

        SnapshotCmdString = b'\x01\x95\x01\x00'
        self.__SetHelper('Snapshot', SnapshotCmdString, value, qualifier)

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'Live': b'\x01\x9E\x01\x00',
            'Memory': b'\x01\x9E\x01\x01',
            'USB': b'\x01\x9E\x01\x02',
            'HDMI 1': b'\x01\x9E\x01\x03',
            'HDMI 2': b'\x01\x9E\x01\x04'
        }

        if value in ValueStateValues:
            SourceCmdString = ValueStateValues[value]
            self.__SetHelper('Source', SourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSource')

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Live',
            b'\x01': 'Memory',
            b'\x02': 'USB',
            b'\x03': 'HDMI 1',
            b'\x04': 'HDMI 2'
        }

        SourceCmdString = b'\x00\x9E\x00'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Wide': 0x01,
            'Tele': 0x02,
            'Stop': 0x00
        }

        if value in ValueStateValues and 1 <= int(qualifier['Speed']) <= 15:
            if value == 'Stop':
                ZoomCmdString = pack('>4B', 0x01, 0x2F, 0x01, ValueStateValues[value])
            else:
                ZoomCmdString = pack('>6B', 0x01, 0x20, 0x03, ValueStateValues[value], 0x00, int(qualifier['Speed']))
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        CommandAction = {
            b'\x80': 'Get',
            b'\x81': 'Set'
        }

        CommandList = {
            b'\x31': 'Auto Focus',
            b'\x2F': 'Focus or Zoom Stop',
            b'\x21': 'Focus',
            b'\x56': 'Freeze',
            b'\xA0': 'Light',
            b'\x30': 'Power',
            b'\x40': 'Preset Recall',
            b'\x41': 'Preset Store',
            b'\x90': 'Snapshot',
            b'\x9E': 'Source',
            b'\x20': 'Zoom'
        }

        ErrorType = {
            b'\x01': 'Time Out',
            b'\x02': 'Invalid Cmd',
            b'\x03': 'Invalid Parameter',
            b'\x04': 'Invalid Length',
            b'\x05': 'FiFo Full',
            b'\x06': 'Firmware Update Error',
            b'\x07': 'Access Denied',
            b'\x08': 'AUTH Required',
            b'\x09': 'Busy'
        }

        if response:
            if response[0:1] in CommandAction and response[1:2] in CommandList and response[2:3] in ErrorType:
                self.Error(['{0} {1} Error: {2}'.format(CommandList[response[1:2]], CommandAction[response[0:1]], ErrorType[response[2:3]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

