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
        self.__GroupID = 0
        self.__DeviceID = 1

        self.Models = {
            '65BDL4050D': self.phil_10_2497_others,
            '55BDL4050D': self.phil_10_2497_others,
            '49BDL4050D': self.phil_10_2497_others,
            '43BDL4050D': self.phil_10_2497_43BDL,
            '32BDL4050D': self.phil_10_2497_others,
            }

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
            'VolumeStatus': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self.__DeviceID
    
    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self.__DeviceID = 0
        elif 1 <= int(value) <= 255:
            self.__DeviceID = int(value)
        else:
            print('Device ID Parameter is invalid.')
    
    @property
    def GroupID(self):
        return self.__GroupID
    
    @GroupID.setter
    def GroupID(self, value):
        if value == 'Off':
            self.__GroupID = 0
        elif 1 <= int(value) <= 254:
            self.__GroupID = int(value)
        else:
            print('Group ID Parameter is invalid.')

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
            'Dynamic': 0x05,
            '16:9': 0x06
        }

        AspectRatioCmdString = pack('>5B', 0x06, self.__DeviceID, self.__GroupID, 0x3A, ValueStateValues[value])
        ChkSum = self.calcChkSum(AspectRatioCmdString)
        AspectRatioCmdString = AspectRatioCmdString + ChkSum
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x01: 'Custom',
            0x02: 'Real',
            0x03: 'Full',
            0x04: '21:9',
            0x05: 'Dynamic',
            0x06: '16:9'
        }

        AspectRatioCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x3B)
        ChkSum = self.calcChkSum(AspectRatioCmdString)
        AspectRatioCmdString = AspectRatioCmdString + ChkSum
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = pack('>6B', 0x07, self.__DeviceID, self.__GroupID, 0x70, 0x40, 0x00)
        ChkSum = self.calcChkSum(AutoImageCmdString)
        AutoImageCmdString = AutoImageCmdString + ChkSum
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = pack('>8B', 0x09, self.__DeviceID, self.__GroupID, 0xAC, self.InputStateValues[value], 0x09, 0x01, 0x00)
        ChkSum = self.calcChkSum(InputCmdString)
        InputCmdString = InputCmdString + ChkSum
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0xAD)
        ChkSum = self.calcChkSum(InputCmdString)
        InputCmdString = InputCmdString + ChkSum
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res[-5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

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

        IRRemoteControlLockCmdString = pack('>5B', 0x06, self.__DeviceID, self.__GroupID, 0x1C, ValueStateValues[value])
        ChkSum = self.calcChkSum(IRRemoteControlLockCmdString)
        IRRemoteControlLockCmdString = IRRemoteControlLockCmdString + ChkSum
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

        IRRemoteControlLockCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x1D)
        ChkSum = self.calcChkSum(IRRemoteControlLockCmdString)
        IRRemoteControlLockCmdString = IRRemoteControlLockCmdString + ChkSum
        res = self.__UpdateHelper('IRRemoteControlLock', IRRemoteControlLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('IRRemoteControlLock', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateIRRemoteControlLock')

    def SetKeypadLock(self, value, qualifier):

        ValueStateValues = {
            'Unlock all': 0x01,
            'Lock all': 0x02,
            'Lock all but Power': 0x03,
            'Lock all but Volume': 0x04,
            'Lock all except Power & Volume': 0x07
        }

        KeypadLockCmdString = pack('>5B', 0x06, self.__DeviceID, self.__GroupID, 0x1A, ValueStateValues[value])
        ChkSum = self.calcChkSum(KeypadLockCmdString)
        KeypadLockCmdString = KeypadLockCmdString + ChkSum
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateKeypadLock(self, value, qualifier):

        ValueStateValues = {
            0x01: 'Unlock all',
            0x02: 'Lock all',
            0x03: 'Lock all but Power',
            0x04: 'Lock all but Volume',
            0x07: 'Lock all except Power & Volume'
        }

        KeypadLockCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x1B)
        ChkSum = self.calcChkSum(KeypadLockCmdString)
        KeypadLockCmdString = KeypadLockCmdString + ChkSum
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateKeypadLock')

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Bottom-Left': 0x00,
            'Top-Left': 0x01,
            'Top-Right': 0x02,
            'Bottom-Right': 0x03
        }

        if value == 'Off':
            PIPCmdString = pack('>8B', 0x09, self.__DeviceID, self.__GroupID, 0x3C, 0x00, 0x00, 0x00, 0x00)
        else:
            PIPCmdString = pack('>8B', 0x09, self.__DeviceID, self.__GroupID, 0x3C, 0x01, ValueStateValues[value], 0x00, 0x00)
        ChkSum = self.calcChkSum(PIPCmdString)
        PIPCmdString = PIPCmdString + ChkSum
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Bottom-Left',
            0x01: 'Top-Left',
            0x02: 'Top-Right',
            0x03: 'Bottom-Right'
        }

        PIPCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x3D)
        ChkSum = self.calcChkSum(PIPCmdString)
        PIPCmdString = PIPCmdString + ChkSum
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                if res[-5] == 0x00:
                    value = 'Off'
                else:
                    value = ValueStateValues[res[-4]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIP')

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = pack('>6B', 0x07, self.__DeviceID, self.__GroupID, 0x84, 0xFD, self.PictureInPictureValues[value])
        ChkSum = self.calcChkSum(PIPInputCmdString)
        PIPInputCmdString = PIPInputCmdString + ChkSum
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x85)
        ChkSum = self.calcChkSum(PIPInputCmdString)
        PIPInputCmdString = PIPInputCmdString + ChkSum
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PictureInPictureNames[res[5]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x01
        }

        PowerCmdString = pack('>5B', 0x06, self.__DeviceID, self.__GroupID, 0x18, ValueStateValues[value])
        ChkSum = self.calcChkSum(PowerCmdString)
        PowerCmdString = PowerCmdString + ChkSum
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x01: 'Off'
        }

        PowerCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x19)
        ChkSum = self.calcChkSum(PowerCmdString)
        PowerCmdString = PowerCmdString + ChkSum
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x01,
            'Down': 0x00
            }

        VolumeCmdString = pack('>6B', 0x07, self.__DeviceID, self.__GroupID, 0x41, ValueStateValues[value], ValueStateValues[value])
        ChkSum = self.calcChkSum(VolumeCmdString)
        VolumeCmdString = VolumeCmdString + ChkSum
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = pack('>4B', 0x05, self.__DeviceID, self.__GroupID, 0x45)
        ChkSum = self.calcChkSum(VolumeStatusCmdString)
        VolumeStatusCmdString = VolumeStatusCmdString + ChkSum
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-3])
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolumeStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }
        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            print('Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        LenDict = {
            'AspectRatio': 6,
            'Input': 9,
            'IRRemoteControlLock': 6,
            'KeypadLock': 6,
            'PIP': 9,
            'PIPInput': 7,
            'Power': 6,
            'VolumeStatus': 7
        }

        if self.Unidirectional == 'True' or self.__DeviceID == 0:
            print('Inappropriate Command ', command)
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

        self.lastPIPInputUpdate = 0
        

    def phil_10_2497_others(self):
    
    
        self.InputStateValues = {
            'Display Port'     : 0x0A, 
            'HDMI 1'           : 0x0D, 
            'HDMI 2'           : 0x06, 
            'DVI-D'            : 0x0E, 
            'USB'              : 0x08, 
            'VGA'              : 0x05, 
            'Internal Storage' : 0x13,
            'Media Player'     : 0x16,
            'Browser'          : 0x10,
            'SmartCMS'         : 0x11,
            'PDF Player'       : 0x17,
            'Custom'           : 0x18
        }
        
        self.InputStateNames = {
            0x0A : 'Display Port', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x0E : 'DVI-D', 
            0x0C : 'USB', 
            0x05 : 'VGA', 
            0x13 : 'Internal Storage',
            0x16 : 'Media Player',
            0x10 : 'Browser',
            0x11 : 'SmartCMS',
            0x17 : 'PDF Player',
            0x18 : 'Custom'    
        }
        self.PictureInPictureValues = {
            'Display Port'     : 0x0A, 
            'HDMI 1'           : 0x0D, 
            'HDMI 2'           : 0x06, 
            'DVI-D'            : 0x0E, 
            'VGA'              : 0x05, 
            'Internal Storage' : 0x13,
            'Media Player'     : 0x16,
            'Browser'          : 0x10,
            'SmartCMS'         : 0x11,
            'PDF Player'       : 0x17,
            'Custom'           : 0x18
        }

        self.PictureInPictureNames = {
            0x0A : 'Display Port', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x0E : 'DVI-D', 
            0x05 : 'VGA', 
            0x13 : 'Internal Storage',
            0x16 : 'Media Player',
            0x10 : 'Browser',
            0x11 : 'SmartCMS',
            0x17 : 'PDF Player',
            0x18 : 'Custom'
        } 
        

    def phil_10_2497_43BDL(self):
    
    
        self.InputStateValues = {
            'Display Port'     : 0x0A, 
            'HDMI 1'           : 0x0D, 
            'HDMI 2'           : 0x06, 
            'DVI-D'            : 0x0E, 
            'VGA'              : 0x05, 
            'Media Player'     : 0x16,
            'Browser'          : 0x10,
            'SmartCMS'         : 0x11,
            'PDF Player'       : 0x17,
            'Custom'           : 0x18
        }
        
        self.InputStateNames = {
            0x0A : 'Display Port', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x0E : 'DVI-D', 
            0x05 : 'VGA', 
            0x16 : 'Media Player',
            0x10 : 'Browser',
            0x11 : 'SmartCMS',
            0x17 : 'PDF Player',
            0x18 : 'Custom'    
        }
        self.PictureInPictureValues = {
            'Display Port'     : 0x0A, 
            'HDMI 1'           : 0x0D, 
            'HDMI 2'           : 0x06, 
            'DVI-D'            : 0x0E, 
            'VGA'              : 0x05, 
            'Media Player'     : 0x16,
            'Browser'          : 0x10,
            'SmartCMS'         : 0x11,
            'PDF Player'       : 0x17,
            'Custom'           : 0x18
        }

        self.PictureInPictureNames = {
            0x0A : 'Display Port', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x0E : 'DVI-D', 
            0x05 : 'VGA', 
            0x16 : 'Media Player',
            0x10 : 'Browser',
            0x11 : 'SmartCMS',
            0x17 : 'PDF Player',
            0x18 : 'Custom'
        } 
        

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
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
