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

        self._DeviceID = 1
        self._GroupID = 0

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'IRRemoteControlLock': {'Status': {}},
            'KeypadLock': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value)
        else:
            self.Error(['DeviceID: Invalid Value, Value range must be 1 - 255 or Broadcast'])

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Off':
            self._GroupID = 0
        elif 1 <= int(value) <= 254:
            self._GroupID = int(value)
        else:
            self.Error(['GroupID: Invalid Value, Value range must be 1 - 254 or Off'])

    def calcChkSum(self, commandstring):
        ChkSum = 0
        for i in range(0, len(commandstring)):
            ChkSum = ChkSum ^ commandstring[i]
        return ChkSum.to_bytes(1, 'big')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0x00,
            'Custom': 0x01,
            'Real': 0x02,
            'Full': 0x03,
            '21:9': 0x04,
            '16:9': 0x06
        }

        CmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x3A, ValueStateValues[value])
        ChkSum = self.calcChkSum(CmdString)
        AspectRatioCmdString = CmdString + ChkSum
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x01: 'Custom',
            0x02: 'Real',
            0x03: 'Full',
            0x04: '21:9',
            0x06: '16:9'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x3B)
        ChkSum = self.calcChkSum(CmdString)
        AspectRatioCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        CmdString = pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x70, 0x40, 0x00)
        ChkSum = self.calcChkSum(CmdString)
        AutoImageCmdString = CmdString + ChkSum
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Internal Storage': 0x13,
            'Media Player': 0x16,
            'Browser': 0x10,
            'SmartCMS': 0x11,
            'PDF Player': 0x17,
            'Custom': 0x18,
            'Display Port': 0x0A,
            'HDMI 1': 0x0D,
            'HDMI 2': 0x06,
            'DVI-D': 0x0E,
            'USB': 0x0C,
            'VGA': 0x05
        }

        CmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0xAC, ValueStateValues[value], 0x09, 0x01, 0x00)
        ChkSum = self.calcChkSum(CmdString)
        InputCmdString = CmdString + ChkSum
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x13: 'Internal Storage',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x18: 'Custom',
            0x0A: 'Display Port',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0E: 'DVI-D',
            0x0C: 'USB',
            0x05: 'VGA'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0xAD)
        ChkSum = self.calcChkSum(CmdString)
        InputCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIRRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock all': 0x01,
            'Lock all': 0x02,
            'Lock all but Power': 0x03,
            'Lock all but Volume': 0x04,
            'Primary (Master)': 0x05,
            'Secondary (Daisy chain PD)': 0x06,
            'Lock all except Power & Volume': 0x07
        }

        CmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x1C, ValueStateValues[value])
        ChkSum = self.calcChkSum(CmdString)
        IRRemoteControlLockCmdString = CmdString + ChkSum
        self.__SetHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)

    def UpdateIRRemoteControlLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Unlock all',
            0x02: 'Lock all',
            0x03: 'Lock all but Power',
            0x04: 'Lock all but Volume',
            0x05: 'Primary (Master)',
            0x06: 'Secondary (Daisy chain PD)',
            0x07: 'Lock all except Power & Volume'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x1D)
        ChkSum = self.calcChkSum(CmdString)
        IRRemoteControlLockCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('IRRemoteControlLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Remote Control Lock: Invalid/unexpected response'])

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock all': 0x01,
            'Lock all': 0x02,
            'Lock all but Power': 0x03,
            'Lock all but Volume': 0x04,
            'Lock all except Power & Volume': 0x07
        }

        CmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x1A, ValueStateValues[value])
        ChkSum = self.calcChkSum(CmdString)
        KeypadLockCmdString = CmdString + ChkSum
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateKeypadLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Unlock all',
            0x02: 'Lock all',
            0x03: 'Lock all but Power',
            0x04: 'Lock all but Volume',
            0x07: 'Lock all except Power & Volume'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x1B)
        ChkSum = self.calcChkSum(CmdString)
        KeypadLockCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keypad Lock: Invalid/unexpected response'])

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Bottom-Left': 0x00,
            'Top-Left': 0x01,
            'Top-Right': 0x02,
            'Bottom-Right': 0x03,
            'Center': 0x04
        }

        if value == 'Off':
            CmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x3C, 0x00, 0x00, 0x00, 0x00)
        else:
            CmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x3C, 0x01, ValueStateValues[value], 0x00, 0x00)
        ChkSum = self.calcChkSum(CmdString)
        ChkSum = self.calcChkSum(CmdString)
        PIPCmdString = CmdString + ChkSum
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Bottom-Left',
            0x01: 'Top-Left',
            0x02: 'Top-Right',
            0x03: 'Bottom-Right',
            0x04: 'Center'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x3D)
        ChkSum = self.calcChkSum(CmdString)
        PIPCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                if res[-5] == 0:
                    value = 'Off'
                else:
                    value = ValueStateValues[res[-4]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'Display Port': 0x0A,
            'HDMI 1': 0x0D,
            'HDMI 2': 0x06,
            'DVI-D': 0x0E,
            'USB': 0x0C,
            'VGA': 0x05,
            'Internal Storage': 0x13,
            'Media Player': 0x16,
            'Browser': 0x10,
            'SmartCMS': 0x11,
            'PDF Player': 0x17,
            'Custom': 0x18
        }

        CmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x84, 0xFD, ValueStateValues[value], 0x00, 0x00)
        ChkSum = self.calcChkSum(CmdString)
        PIPInputCmdString = CmdString + ChkSum
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            0x0A: 'Display Port',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0E: 'DVI-D',
            0x0C: 'USB',
            0x05: 'VGA',
            0x13: 'Internal Storage',
            0x16: 'Media Player',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x17: 'PDF Player',
            0x18: 'Custom'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x85)
        ChkSum = self.calcChkSum(CmdString)
        PIPInputCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-4]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x01
        }

        CmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x18, ValueStateValues[value])
        ChkSum = self.calcChkSum(CmdString)
        PowerCmdString = CmdString + ChkSum
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x19)
        ChkSum = self.calcChkSum(CmdString)
        PowerCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x44, value, 0xFF)
            ChkSum = self.calcChkSum(CmdString)
            VolumeCmdString = CmdString + ChkSum
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x45)
        ChkSum = self.calcChkSum(CmdString)
        VolumeCmdString = CmdString + ChkSum
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-3])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }
        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        LenDict = {
            'AspectRatio': 6,
            'Input': 9,
            'IRRemoteControlLock': 6,
            'KeypadLock': 6,
            'PIP': 9,
            'PIPInput': 9,
            'Power': 6,
            'Volume': 7
        }

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=LenDict[command])
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

