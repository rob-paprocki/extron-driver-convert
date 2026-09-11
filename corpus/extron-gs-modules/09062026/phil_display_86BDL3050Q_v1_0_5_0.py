from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self._DeviceID = 1
        self._GroupID = 0
        self.Models = {
            '86BDL3050Q': self.phil_10_3441_other,
            '65BDL3050Q': self.phil_10_3441_other,
            '75BDL3050Q': self.phil_10_3441_other,
            '55BDL3050Q': self.phil_10_3441_55_49,
            '49BDL3050Q': self.phil_10_3441_55_49,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'IRRemoteLock': {'Status': {}},
            'KeypadLock': {'Status': {}},
            'PIPInput': {'Parameters': ['Quadrant 2', 'Quadrant 3', 'Quadrant 4'], 'Status': {}},
            'PIPInputQuadrant2Status': {'Status': {}},
            'PIPInputQuadrant3Status': {'Status': {}},
            'PIPInputQuadrant4Status': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Parameters': ['Type'], 'Status': {}},
            'VolumeStep': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1<= int(value) <= 255:
            self._DeviceID= int(value)
        else:
            self.Error(['Group ID Out of Range'])

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Off':
            self._GroupID = 0
        elif 1<= int(value) <= 254:
            self._GroupID= int(value)
        else:
            self.Error(['Group ID Out of Range'])

    def calChkSum(self, commandstring):
        ChkSum = 0
        for i in range(0, len(commandstring)):
            ChkSum = ChkSum ^ commandstring[i]
        return ChkSum.to_bytes(1, 'big')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Normal': 0x00,
            'Custom': 0x01,
            'Real': 0x02,
            'Full': 0x03,
            '21:9': 0x04,
            'Dynamic': 0x05,
            '16:9': 0x06
            }

        AspectRatioCmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x3A, AspectRatioState[value])
        ChkSum = self.calChkSum(AspectRatioCmdString)
        AspectRatioCmdString = b''.join([AspectRatioCmdString, ChkSum])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            0x00: 'Normal',
            0x01: 'Custom',
            0x02: 'Real',
            0x03: 'Full',
            0x04: '21:9',
            0x05: 'Dynamic',
            0x06: '16:9'
            }

        AspectRatioCmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x3B)
        ChkSum = self.calChkSum(AspectRatioCmdString)
        AspectRatioCmdString = b''.join([AspectRatioCmdString, ChkSum])
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x70, 0x40, 0x00)
        ChkSum = self.calChkSum(AutoImageCmdString)
        AutoImageCmdString = b''.join([AutoImageCmdString, ChkSum])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0xAC, self.InputStates[value], 0x00, 0x01, 0x00)
        ChkSum = self.calChkSum(InputCmdString)
        InputCmdString = b''.join([InputCmdString, ChkSum])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0xAD)
        ChkSum = self.calChkSum(InputCmdString)
        InputCmdString = b''.join([InputCmdString, ChkSum])
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputValues[res[-5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input : Invalid/Unexpected Response'])

    def SetIRRemoteLock(self, value, qualifier):

        IRRemoteLockState = {
            'Unlock All': 0x01,
            'Lock All': 0x02,
            'Lock All but Power': 0x03,
            'Lock All but Volume': 0x04,
            'Primary': 0x05,
            'Secondary': 0x06,
            'Lock all except Power and Volume': 0x07
            }

        IRRemoteLockCmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x1C, IRRemoteLockState[value])
        ChkSum = self.calChkSum(IRRemoteLockCmdString)
        IRRemoteLockCmdString = b''.join([IRRemoteLockCmdString, ChkSum])
        self.__SetHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)

    def UpdateIRRemoteLock(self, value, qualifier):

        IRRemoteLockState = {
            0x01: 'Unlock All',
            0x02: 'Lock All',
            0x03: 'Lock All but Power',
            0x04: 'Lock All but Volume',
            0x05: 'Primary',
            0x06: 'Secondary',
            0x07: 'Lock all except Power and Volume'
            }

        IRRemoteLockCmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x1D)
        ChkSum = self.calChkSum(IRRemoteLockCmdString)
        IRRemoteLockCmdString = b''.join([IRRemoteLockCmdString, ChkSum])
        res = self.__UpdateHelper('IRRemoteLock', IRRemoteLockCmdString, value, qualifier)
        if res:
            try:
                value = IRRemoteLockState[res[-2]]
                self.WriteStatus('IRRemoteLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IR Remote Lock : Invalid/Unexpected Response'])

    def SetKeypadLock(self, value, qualifier):

        KeypadLockState = {
            'Unlock All': 0x01,
            'Lock All': 0x02,
            'Lock all but Power': 0x03,
            'Lock all but Volume': 0x04,
            'Lock all except Power and Volume': 0x07
            }

        KeypadLockCmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x1A, KeypadLockState[value])
        ChkSum = self.calChkSum(KeypadLockCmdString)
        KeypadLockCmdString = b''.join([KeypadLockCmdString, ChkSum])
        self.__SetHelper('KeypadLock', KeypadLockCmdString, value, qualifier)

    def UpdateKeypadLock(self, value, qualifier):

        KeypadLockState = {
            0x01: 'Unlock All',
            0x02: 'Lock All',
            0x03: 'Lock all but Power',
            0x04: 'Lock all but Volume',
            0x07: 'Lock all except Power and Volume'
            }

        KeypadLockCmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x1B)
        ChkSum = self.calChkSum(KeypadLockCmdString)
        KeypadLockCmdString = b''.join([KeypadLockCmdString, ChkSum])
        res = self.__UpdateHelper('KeypadLock', KeypadLockCmdString, value, qualifier)
        if res:
            try:
                value = KeypadLockState[res[-2]]
                self.WriteStatus('KeypadLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keypad Lock : Invalid/Unexpected Response'])

    def SetPIPInput(self, value, qualifier):

        q2 = qualifier['Quadrant 2']
        q3 = qualifier['Quadrant 3']
        q4 = qualifier['Quadrant 4']
        if q2 in self.InputStates and q3 in self.InputStates and q4 in self.InputStates:
            PIPInputCmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x84, 0xFD, self.InputStates[q2], self.InputStates[q3], self.InputStates[q4])
            ChkSum = self.calChkSum(PIPInputCmdString)
            PIPInputCmdString = b''.join([PIPInputCmdString, ChkSum])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInputQuadrant2Status(self, value, qualifier):

        PIPInputQuadrant2CmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x85)
        ChkSum = self.calChkSum(PIPInputQuadrant2CmdString)
        PIPInputQuadrant2CmdString = b''.join([PIPInputQuadrant2CmdString, ChkSum])
        res = self.__UpdateHelper('PIPInputQuadrant2Status', PIPInputQuadrant2CmdString, value, qualifier)
        if res:
            try:
                value = self.InputValues[res[-4]]  # Quadrant 2
                self.WriteStatus('PIPInputQuadrant2Status', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input Quadrant 2 Status : Invalid/Unexpected Response'])

            try:
                value = self.InputValues[res[-3]]  # Quadrant 3
                self.WriteStatus('PIPInputQuadrant3Status', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input Quadrant 3 Status : Invalid/Unexpected Response'])

            try:
                value = self.InputValues[res[-2]]  # Quadrant 4
                self.WriteStatus('PIPInputQuadrant4Status', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input Quadrant 4 Status : Invalid/Unexpected Response'])

    def UpdatePIPInputQuadrant3Status(self, value, qualifier):

        self.UpdatePIPInputQuadrant2Status(value, qualifier)

    def UpdatePIPInputQuadrant4Status(self, value, qualifier):

        self.UpdatePIPInputQuadrant2Status(value, qualifier)

    def SetPIPMode(self, value, qualifier):

        PIPModeState = {
            'On': 1,
            'POP': 2,
            'Quick Swap': 3,
            'PBP 2 Win': 4,
            'PBP 3 Win': 5,
            'PBP 4 Win': 6,
            'PBP 3 Win 1': 7,
            'PBP 3 Win 2': 8,
            'PBP 4 Win 1': 9,
            'SICP Custom': 10
            }

        PIPPositionState = {
            'Bottom Left': 0x00,
            'Top Left': 0x01,
            'Top Right': 0x02,
            'Bottom Right': 0x03,
            'Center': 0x04
            }

        if value == 'Off':
            PIPModeCmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x3C, 0x00, 0x00, 0x00, 0x00)
        else:
            PIPPosition = qualifier['PIPPosition']
            if not PIPPosition: PIPPosition = 'Top Right'
            PIPModeCmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x3C, PIPModeState[value], PIPPositionState[PIPPosition], 0x00, 0x00)

        ChkSum = self.calChkSum(PIPModeCmdString)
        PIPModeCmdString = b''.join([PIPModeCmdString, ChkSum])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeState = {
            1: 'On',
            2: 'POP',
            3: 'Quick Swap',
            4: 'PBP 2 Win',
            5: 'PBP 3 Win',
            6: 'PBP 4 Win',
            7: 'PBP 3 Win 1',
            8: 'PBP 3 Win 2',
            9: 'PBP 4 Win 1',
            10: 'SICP Custom'
            }

        PIPPositionState = {
            0x00: 'Bottom Left',
            0x01: 'Top Left',
            0x02: 'Top Right',
            0x03: 'Bottom Right',
            0x04: 'Center'
            }

        PIPModeCmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x3D)
        ChkSum = self.calChkSum(PIPModeCmdString)
        PIPModeCmdString = b''.join([PIPModeCmdString, ChkSum])
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeState[res[-5]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode : Invalid/Unexpected Response'])

            try:
                value = PIPPositionState[res[-4]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position : Invalid/Unexpected Response'])

    def SetPIPPosition(self, value, qualifier):

        PIPPositionState = {
            'Bottom Left': 0,
            'Top Left': 1,
            'Top Right': 2,
            'Bottom Right': 3,
            'Center': 4
            }

        PIPPositionCmdString = pack('>8B', 0x09, self._DeviceID, self._GroupID, 0x3C, 0x01, PIPPositionState[value], 0x00, 0x00)
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        self.UpdatePIPMode(value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 0x02,
            'Off': 0x01
            }

        PowerCmdString = pack('>5B', 0x06, self._DeviceID, self._GroupID, 0x18, PowerState[value])
        ChkSum = self.calChkSum(PowerCmdString)
        PowerCmdString = b''.join([PowerCmdString, ChkSum])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            0x02: 'On',
            0x01: 'Off'
            }

        PowerCmdString = pack('>4B', 0x05, self._DeviceID, self._GroupID, 0x19)
        ChkSum = self.calChkSum(PowerCmdString)
        PowerCmdString = b''.join([PowerCmdString, ChkSum])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        type_val = qualifier['Type']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and type_val == 'Speaker Out':
            cur_audVal = self.ReadStatus('Volume', {'Type': 'Audio Out'})
            VolumeCmdString = pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x44, value, cur_audVal)
            ChkSum = self.calChkSum(VolumeCmdString)
            VolumeCmdString = b''.join([VolumeCmdString, ChkSum])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        elif ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and type_val == 'Audio Out':
            cur_spkVal = self.ReadStatus('Volume', {'Type': 'Speaker Out'})
            VolumeCmdString = pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x44, cur_spkVal, value)
            ChkSum = self.calChkSum(VolumeCmdString)
            VolumeCmdString = b''.join([VolumeCmdString, ChkSum])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('4B', 0x05, self._DeviceID, self._GroupID, 0x45)
        ChkSum = self.calChkSum(VolumeCmdString)
        VolumeCmdString = b''.join([VolumeCmdString, ChkSum])
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value1 = int(res[-3])
                self.WriteStatus('Volume', value1, {'Type': 'Speaker Out'})
                value2 = int(res[-2])
                self.WriteStatus('Volume', value2, {'Type': 'Audio Out'})
            except (ValueError, IndexError):
                self.Error(['Volume : Make sure to have sent out an Update Volume command before changing volume level.'])

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x01,
            'Down': 0x00
        }

        VolumeStepCmdString = pack('>6B', 0x07, self._DeviceID, self._GroupID, 0x41, ValueStateValues[value], ValueStateValues[value])
        ChkSum = self.calChkSum(VolumeStepCmdString)
        VolumeStepCmdString = b''.join([VolumeStepCmdString, ChkSum])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available'
            }

        if response[3:4] == b'\x00' and response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['{0} : Invalid/Unappropriate command'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        LenDict = {
            'AspectRatio': 6,
            'Input': 9,
            'IRRemoteLock': 6,
            'KeypadLock': 6,
            'PIPInputQuadrant2Status': 9,
            'PIPInputQuadrant3Status': 9,
            'PIPInputQuadrant4Status': 9,
            'PIPMode': 9,
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

        
    def phil_10_3441_55_49(self):
    
    
        self.InputStates = {
            'VGA'          : 0x05, 
            'HDMI 1'       : 0x0D, 
            'HDMI 2'       : 0x06, 
            'DVI-D'        : 0x0E, 
            'Media Player' : 0x16, 
            'Browser'      : 0x10, 
            'SmartCMS'     : 0x11, 
            'PDF Player'   : 0x17, 
            'Card OPS'     : 0x0B, 
            'USB 1'        : 0x0C,
            'USB 2'        : 0x08
        }
        
        self.InputValues = {
            0x05 : 'VGA', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x0E : 'DVI-D', 
            0x16 : 'Media Player', 
            0x10 : 'Browser', 
            0x11 : 'SmartCMS', 
            0x17 : 'PDF Player', 
            0x0B : 'Card OPS', 
            0x0C : 'USB 1', 
            0x08 : 'USB 2'
        }
        

        
    def phil_10_3441_other(self):
    
    
        self.InputStates = {
            'VGA'           : 0x05, 
            'HDMI 1'        : 0x0D, 
            'HDMI 2'        : 0x06, 
            'HDMI 3'        : 0x0F,
            'HDMI 4'        : 0x19,
            'DisplayPort'   : 0x0A, 
            'Media Player'  : 0x16, 
            'Browser'       : 0x10, 
            'SmartCMS'      : 0x11, 
            'PDF Player'    : 0x17, 
            'Card OPS'      : 0x0B,
            'USB 1'         : 0x0C,
            'USB 2'         : 0x08
        }
        
        self.InputValues = {
            0x05 : 'VGA', 
            0x0D : 'HDMI 1', 
            0x06 : 'HDMI 2', 
            0x0F : 'HDMI 3',
            0x19 : 'HDMI 4',
            0x0A : 'DisplayPort', 
            0x16 : 'Media Player', 
            0x10 : 'Browser', 
            0x11 : 'SmartCMS', 
            0x17 : 'PDF Player', 
            0x0B : 'Card OPS',
            0x0C : 'USB 1',
            0x08 : 'USB 2'
        }
        

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

