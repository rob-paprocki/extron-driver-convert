from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack


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
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Shutter': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
            }              

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0x88
        elif (1 <= int(value) <= 7):
            self._DeviceID = 0x80 + int(value)

    def SetAutoExposure(self, value, qualifier):

        AutoExposureState = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Bright': 0x0D
            }

        AutoExposureCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x39, AutoExposureState[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        AutoExposureState = {
            b'\x00': 'Full Auto',
            b'\x03': 'Manual',
            b'\x0A': 'Shutter Priority',
            b'\x0B': 'Iris Priority',
            b'\x0D': 'Bright'
            }

        AutoExposureCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = AutoExposureState[res[2:3]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAutoExposure')

    def SetAutoFocus(self, value, qualifier):

        AutoFocusState = {
            'On': 0x02,
            'Off': 0x03
            }

        AutoFocusCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x38, AutoFocusState[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusState = {
            b'\x02': 'On',
            b'\x03': 'Off'
            }

        AutoFocusCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = AutoFocusState[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAutoFocus')

    def SetBacklight(self, value, qualifier):

        BacklightState = {
            'On': 0x02,
            'Off': 0x03
            }

        BacklightCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x33, BacklightState[value], 0xFF)
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        BacklightState = {
            b'\x02': 'On',
            b'\x03': 'Off'
            }

        BacklightCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = BacklightState[res[2:3]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateBacklight')

    def SetFocus(self, value, qualifier):

        FocusSpeedConstraints = {
            'Min': 0,
            'Max': 7
            }

        FocusState = {
            'Far': 0x20,
            'Near': 0x30,
            'Stop': 0x00
            }

        if FocusSpeedConstraints['Min'] <= int(qualifier['Focus Speed']) <= FocusSpeedConstraints['Max']:
            if value == 'Stop':
                focusspeed = 0x00
            else:
                focusspeed = int(qualifier['Focus Speed']) + FocusState[value]
            FocusCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x08, focusspeed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On': 0x02,
            'Off': 0x03
            }

        FreezeCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x62, FreezeState[value], 0xFF)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        IrisState = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
            }

        IrisCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x0B, IrisState[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        panspeed = int(qualifier['Pan Speed'])
        tiltspeed = int(qualifier['Tilt Speed'])

        PanSpeedConstraints = {
            'Min': 1,
            'Max': 24
            }

        TiltSpeedConstraints = {
            'Min': 1,
            'Max': 20
            }

        PanTiltState = {
            'Up': (0x03, 0x01),
            'Down': (0x03, 0x02),
            'Left': (0x01, 0x03),
            'Right': (0x02, 0x03),
            'Up Left': (0x01, 0x01),
            'Up Right': (0x02, 0x01),
            'Down Left': (0x01, 0x02),
            'Down Right': (0x02, 0x02),
            'Stop': (0x03, 0x03)
            }

        if (PanSpeedConstraints['Min'] <= panspeed <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= tiltspeed <= TiltSpeedConstraints['Max']):
            PanTiltCmdString = pack('>9B', self._DeviceID, 0x01, 0x06, 0x01, panspeed, tiltspeed, PanTiltState[value][0], PanTiltState[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 0x02,
            'Off': 0x03
            }

        PowerCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x00, PowerState[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            b'\x02': 'On',
            b'\x03': 'Off'
            }

        PowerCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallConstraints = {
            'Min': 1,
            'Max': 127
            }

        if PresetRecallConstraints['Min'] <= int(value) <= PresetRecallConstraints['Max']:
            PresetRecallCmdString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value), 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        PresetResetConstraints = {
            'Min': 1,
            'Max': 127
            }

        if PresetResetConstraints['Min'] <= int(value) <= PresetResetConstraints['Max']:
            PresetResetCmdString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x00, int(value), 0xFF)
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        PresetSaveConstraints = {
            'Min': 1,
            'Max': 127
            }

        if PresetSaveConstraints['Min'] <= int(value) <= PresetSaveConstraints['Max']:
            PresetSaveCmdString = pack('>BBBBBBB', self._DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetShutter(self, value, qualifier):

        ShutterState = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
            }

        ShutterCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x0A, ShutterState[value], 0xFF)
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
            'Auto': 0x00,
            'Indoor': 0x01,
            'Outdoor': 0x02,
            'One Push': 0x03,
            'Manual': 0x05,
            'Outdoor Auto': 0x06,
            'Sodium Lamp Auto': 0x07,
            'Sodium Auto': 0x08
            }

        WhiteBalanceCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x35, WhiteBalanceState[value], 0xFF)
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        WhiteBalanceState = {
            0x00: 'Auto',
            0x01: 'Indoor',
            0x02: 'Outdoor',
            0x03: 'One Push',
            0x05: 'Manual',
            0x04: 'ATW'
            }

        WhiteBalanceCmdString = pack('>BBBBB', self._DeviceID, 0x09, 0x04, 0x35, 0xFF)
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = WhiteBalanceState[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateWhiteBalance')

    def SetZoom(self, value, qualifier):

        ZoomSpeedConstraints = {
            'Min': 0,
            'Max': 7
            }

        ZoomState = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
            }

        if ZoomSpeedConstraints['Min'] <= int(qualifier['Zoom Speed']) <= ZoomSpeedConstraints['Max']:
            if value == 'Stop':
                zoomspeed = 0x00
            else:
                zoomspeed = int(qualifier['Zoom Speed']) + ZoomState[value]
            ZoomCmdString = pack('>BBBBBB', self._DeviceID, 0x01, 0x04, 0x07, ZoomState[value], 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)

                if(errorByte == 0x60) and (errorCode == 0x02):
                    print(sourceCmdName + 'Syntax Error')
                    response = ''
                elif(errorByte == 0x61) and (errorCode == 0x41):
                    self.Error([sourceCmdName + 'Command Not Executable'])
                    response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 'Broadcast':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 'Broadcast':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if res:
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
