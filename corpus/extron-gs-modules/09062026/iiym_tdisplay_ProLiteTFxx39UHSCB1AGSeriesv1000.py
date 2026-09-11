from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
from functools import reduce
from operator import xor
from struct import unpack

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
            'AspectRatio': { 'Status': {}},
            'AudioOutVolume': { 'Status': {}},
            'AutoAdjust': { 'Status': {}},
            'Input': { 'Status': {}},
            'KeypadLock': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.cur_vol = -1
        self.cur_out_vol = -1

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
            self.Error(['Device ID Parameter is set to a wrong value.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal (4:3)': b'\x00',
            'Custom':       b'\x01',
            'Real (1:1)':   b'\x02',
            'Full':         b'\x03',
            '21:9':         b'\x04',
            'Dynamic':      b'\x05',
            '16:9':         b'\x06',
            }

        if value in ValueStateValues:
            AspectRatioCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x04\x01\x3A', ValueStateValues[value]])
            AspectRatioCmdString = b''.join([AspectRatioCmdString, reduce(xor, AspectRatioCmdString).to_bytes(1, 'big')])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x03\x01\x3B'])
        AspectRatioCmdString = b''.join([AspectRatioCmdString, reduce(xor, AspectRatioCmdString).to_bytes(1, 'big')])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0: 'Normal (4:3)',
                    1: 'Custom',
                    2: 'Real (1:1)',
                    3: 'Full',
                    4: '21:9',
                    5: 'Dynamic',
                    6: '16:9'
                    }

                value = ValueStateValues[res[7]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioOutVolume(self, value, qualifier):

        if 0 <= value <= 100 and 0 <= self.cur_vol <= 100:
            AudioOutVolumeCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x05\x01\x44',
                                                self.cur_vol.to_bytes(1, 'big'), value.to_bytes(1, 'big')])
            AudioOutVolumeCmdString = b''.join([AudioOutVolumeCmdString,
                                                reduce(xor, AudioOutVolumeCmdString).to_bytes(1, 'big')])
            self.__SetHelper('AudioOutVolume', AudioOutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutVolume')

    def UpdateAudioOutVolume(self, value, qualifier):

        self.UpdateVolume( None, None)

    def SetAutoAdjust(self, value, qualifier):

        AutoAdjustCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x05\x01\x70\x40\x00'])
        AutoAdjustCmdString = b''.join([AutoAdjustCmdString, reduce(xor, AutoAdjustCmdString).to_bytes(1, 'big')])
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA':         b'\x05',
            'HDMI 1':      b'\x0D',
            'HDMI 2':      b'\x06',
            'DisplayPort': b'\x0A',
            }

        if value in ValueStateValues:
            InputCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x07\x01\xAC', ValueStateValues[value], b'\x00\x00\x00'])
            InputCmdString = b''.join([InputCmdString, reduce(xor, InputCmdString).to_bytes(1, 'big')])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x03\x01\xAD'])
        InputCmdString = b''.join([InputCmdString, reduce(xor, InputCmdString).to_bytes(1, 'big')])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    5:  'VGA',
                    13: 'HDMI 1',
                    6:  'HDMI 2',
                    10: 'DisplayPort'
                    }

                value = ValueStateValues[res[7]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock All':                       b'\x01',
            'Lock All':                         b'\x02',
            'Lock all but Power':               b'\x03',
            'Lock all but Volume':              b'\x04',
            'Lock all except Power and Volume': b'\x07',
            }

        if value in ValueStateValues:
            KeypadLockCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x04\x01\x1A', ValueStateValues[value]])
            KeypadLockCmdString = b''.join([KeypadLockCmdString, reduce(xor, KeypadLockCmdString).to_bytes(1, 'big')])
            self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateKeypadLock(self, value, qualifier):

        KeypadLockCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x03\x01\x1B'])
        KeypadLockCmdString = b''.join([KeypadLockCmdString, reduce(xor, KeypadLockCmdString).to_bytes(1, 'big')])
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    1: 'Unlock All',
                    2: 'Lock All',
                    3: 'Lock all but Power',
                    4: 'Lock all but Volume',
                    7: 'Lock all except Power and Volume'
                    }

                value = ValueStateValues[res[7]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Keypad Lock: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x04\x01\x0F\x02'])
        OperationHoursCmdString = b''.join([OperationHoursCmdString, reduce(xor, OperationHoursCmdString).to_bytes(1, 'big')])
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>H', res[7:9])[0]
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x02',
            'Off': b'\x01',
            }

        if value in ValueStateValues:
            PowerCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x04\x01\x18', ValueStateValues[value]])
            PowerCmdString = b''.join([PowerCmdString, reduce(xor, PowerCmdString).to_bytes(1, 'big')])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x03\x01\x19'])
        PowerCmdString = b''.join([PowerCmdString, reduce(xor, PowerCmdString).to_bytes(1, 'big')])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    2: 'On',
                    1: 'Off'
                    }

                value = ValueStateValues[res[7]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100 and 0 <= self.cur_out_vol <= 100:
            VolumeCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x05\x01\x44',
                                        value.to_bytes(1, 'big'), self.cur_out_vol.to_bytes(1, 'big')])
            VolumeCmdString = b''.join([VolumeCmdString, reduce(xor, VolumeCmdString).to_bytes(1, 'big')])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b''.join([b'\xA6', self._DeviceID, b'\x00\x00\x00\x03\x01\x45'])
        VolumeCmdString = b''.join([VolumeCmdString, reduce(xor, VolumeCmdString).to_bytes(1, 'big')])
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                self.cur_vol = res[7]
                self.WriteStatus('Volume', self.cur_vol, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])
            try:
                self.cur_out_vol = res[8]
                self.WriteStatus('AudioOutVolume', self.cur_out_vol, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Audio Out Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1: 'Upper Limit Over.',
            2: 'Lower Limit Over.',
            3: 'Command canceled.',
            4: 'Parse Error.',
        }

        if len(response) > 7:
            if response[7] in DEVICE_ERROR_CODES:
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[7]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == b'\x00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=9)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        lenVal = {
            'AspectRatio':    9,
            'Input':          12,
            'KeypadLock':     9,
            'OperationHours': 10,
            'Power':          9,
            'Volume':         10,
        }

        if self.Unidirectional == 'True' or self._DeviceID == b'\x00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=lenVal[command])
            if not res:
                return ''
            else:
                return res

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.cur_vol = -1
        self.cur_spk_vol = -1
        
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()