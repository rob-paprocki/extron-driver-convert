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
        self.Models = {}
        self._DeviceID = 0x81

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture': {'Status': {}},
            'AutoExposure': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'BacklightMode': {'Status': {}},
            'Brightness': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gain': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Shutter': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }        

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)

    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        ApertureCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto': 0x00,
            'Manual': 0x03,
            'Bright': 0x0D
        }

        AutoExposureCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Full Auto',
            b'\x03': 'Manual',
            b'\x0A': 'Shutter Priority',
            b'\x0B': 'Iris Priority',
            b'\x0D': 'Bright'
        }

        AutoExposureCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                print('Auto Exposure: Invalid/unexpected response')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        AutoFocusCmdString = ''
        if value == 'One Push':
            AutoFocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x18, 0x01, 0xFF)
        else:
            AutoFocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        if AutoFocusCmdString:
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        AutoFocusCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                print('Auto Focus: Invalid/unexpected response')

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        BacklightModeCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        BrightnessCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0D, ValueStateValues[value], 0xFF)
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        DigitalZoomCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x06, ValueStateValues[value], 0xFF)
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        DigitalZoomCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x06, 0xFF)
        res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('DigitalZoom', value, qualifier)
            except (KeyError, IndexError):
                print('Digital Zoom: Invalid/unexpected response')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x02,
            'Near': 0x03,
            'Stop': 0x00
        }

        FocusCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF)
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        FreezeCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x62, ValueStateValues[value], 0xFF)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        GainCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
        self.__SetHelper('Gain', GainCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        IrisCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min': 1,
            'Max': 24
            }

        TiltSpeedConstraints = {
            'Min': 1,
            'Max': 20
            }

        ValueStateValues = {
            'Up': (0x03, 0x01),
            'Down': (0x03, 0x02),
            'Left': (0x01, 0x03),
            'Right': (0x02, 0x03),
            'Stop': (0x03, 0x03),
            'Up Left': (0x01, 0x01),
            'Up Right': (0x02, 0x01),
            'Down Left': (0x01, 0x02),
            'Down Right': (0x02, 0x02),
            'Home': 0x04,
            'Reset': 0x05
        }

        PanSpd = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])
        PanTiltCmdString = ''
        if (PanSpeedConstraints['Min'] <= PanSpd <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= TiltSpd <= TiltSpeedConstraints['Max']):
            if value not in ('Home', 'Reset'):
                PanTiltCmdString = pack('>9B', self._DeviceID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            elif value in ('Home', 'Reset'):
                PanTiltCmdString = pack('>5B', self._DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            if PanTiltCmdString:
                self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
            else:
                print('Invalid Command for SetPanTilt')
        else:
            print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x02,
            'Off': 0x03
        }

        PowerCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = pack('>5B', self._DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 0x01,
            'Recall': 0x02,
            'Reset': 0x00
        }

        if 0 <= int(value) <= 127:
            PresetCmdString = pack('>7B', self._DeviceID, 0x01, 0x04, 0x3F, ActionStates[qualifier['Action']], int(value), 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x02,
            'Down': 0x03,
            'Reset': 0x00
        }

        ShutterCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
            }

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30
        }

        if SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']:
            speed = 0x00 if value == 'Stop' else int(qualifier['Speed']) + ValueStateValues[value]
            ZoomCmdString = pack('>6B', self._DeviceID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>4B', response)
                if (errorByte == 0x60) and (errorCode == 0x02):
                    print(sourceCmdName, 'Syntax Error')
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x41):
                    print(sourceCmdName, 'Command Not Executable')
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('{0}: Invalid/unexpected response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
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
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)           

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

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Mode='RS232', Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
