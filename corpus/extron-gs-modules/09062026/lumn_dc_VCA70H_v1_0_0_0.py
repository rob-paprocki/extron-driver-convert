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
            'AddressSet': {'Status': {}},
            'Backlight': {'Status': {}},
            'CameraPosition': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'FactoryReset': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'FocusMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'IRReceive': {'Status': {}},
            'MirrorImage': {'Status': {}},
            'MotionlessPreset': {'Status': {}},
            'Mute': {'Status': {}},
            'PanandTiltSpeedMode': {'Status': {}},
            'PanNormal': {'Parameters': ['Pan Speed'], 'Status': {}},
            'PanSmooth': {'Parameters': ['Pan Speed'], 'Status': {}},
            'PictureFlip': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetReset': {'Status': {}},
            'PresetSave': {'Status': {}},
            'PresetSpeed': {'Status': {}},
            'TallyLamp': {'Status': {}},
            'TallyMode': {'Status': {}},
            'TiltNormal': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'TiltSmooth': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
            }

        self.CameraID = '1'
        if self.Unidirectional == 'False':
            self.matchError = re.compile(b'[\x90\xA0\xB0\xC0\xD0\xE0\xF0][\x60-\x62]([\x02-\x05\x41])\xFF')

    @property
    def CameraID(self):
        return self.cameraID

    @CameraID.setter
    def CameraID(self, value):
        if 1 <= int(value) <= 7:
            self.cameraID = 0x80 + int(value)
        else:
            print('Invalid CameraID parameter')

    def SetAddressSet(self, value, qualifier):

        AddressSetCmdString = pack('>4s', b'\x88\x30\x01\xFF')
        self.__SetHelper('AddressSet', AddressSetCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x33\x02\xFF',
            'Off': b'\x01\x04\x33\x03\xFF'
        }

        BacklightCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x04: 'On',
            0x00: 'Off'
        }

        BacklightCmdString = pack('>B5s', self.cameraID, b'\x09\x7E\x7E\x01\xFF')
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[9] & 0x04]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateBacklight')

    def SetCameraPosition(self, value, qualifier):

        ValueStateValues = {
            'Home': b'\x01\x06\x04\xFF',
            'Reset': b'\x01\x06\x05\xFF'
        }

        CameraPositionCmdString = pack('>B4s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('CameraPosition', CameraPositionCmdString, value, qualifier)

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x06\x02\xFF',
            'Off': b'\x01\x04\x06\x03\xFF',
            'Clear Image Zoom': b'\x01\x04\x06\x04\xFF'
        }

        DigitalZoomCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier):

        DigitalZoomValues = {
            0x02: 'On',
            0x00: 'Off',
            0x40: 'Clear Image Zoom'

        }
        FocusModeValues = {
            0x01: 'Auto',
            0x00: 'Manual',

        }

        DigitalZoomCmdString = pack('>B5s', self.cameraID, b'\x09\x7E\x7E\x00\xFF')
        res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('DigitalZoom', DigitalZoomValues[res[13] & 0x42], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDigitalZoom')
            try:
                self.WriteStatus('FocusMode', FocusModeValues[res[13] & 0x01], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDigitalZoom')

    def SetFactoryReset(self, value, qualifier):

        FactoryResetCmdString = pack('>B6s', self.cameraID, b'\x01\x04\x3F\x03\x00\xFF')
        self.__SetHelper('FactoryReset', FactoryResetCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusSpeed = int(qualifier['Focus Speed'])
        if 0 <= FocusSpeed <= 7:
            if value == 'Far':
                FocusCmdString = pack('>B3sBB', self.cameraID, b'\x01\x04\x08', FocusSpeed + 0x20, 0xFF)
            elif value == 'Near':
                FocusCmdString = pack('>B3sBB', self.cameraID, b'\x01\x04\x08', FocusSpeed + 0x30, 0xFF)
            elif value == 'Stop':
                FocusCmdString = pack('>B5s', self.cameraID, b'\x01\x04\x08\x00\xFF')
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x04\x38\x02\xFF',
            'Manual': b'\x01\x04\x38\x03\xFF',
            'One Push Trigger': b'\x01\x04\x18\x01\xFF',
        }

        FocusModeCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)

    def UpdateFocusMode(self, value, qualifier):
        self.UpdateDigitalZoom(value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x62\x02\xFF',
            'Off': b'\x01\x04\x62\x03\xFF',
        }

        FreezeCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        FreezeCmdString = pack('>B4s', self.cameraID, b'\x09\x04\x62\xFF')
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetIRReceive(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x06\x08\x02\xFF',
            'Off': b'\x01\x06\x08\x03\xFF'
        }

        IRReceiveCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('IRReceive', IRReceiveCmdString, value, qualifier)

    def UpdateIRReceive(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        IRReceiveCmdString = pack('>B4s', self.cameraID, b'\x09\x06\x08\xFF')
        res = self.__UpdateHelper('IRReceive', IRReceiveCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('IRReceive', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateIRReceive')

    def SetMirrorImage(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x61\x02\xFF',
            'Off': b'\x01\x04\x61\x03\xFF'
        }

        MirrorImageCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('MirrorImage', MirrorImageCmdString, value, qualifier)

    def SetMotionlessPreset(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x07\x01\x02\xFF',
            'Off': b'\x01\x07\x01\x03\xFF'
        }

        MotionlessPresetCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('MotionlessPreset', MotionlessPresetCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x75\x02\xFF',
            'Off': b'\x01\x04\x75\x03\xFF'
        }

        MuteCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        MuteCmdString = pack('>B4s', self.cameraID, b'\x09\x04\x75\xFF')
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Mute', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetPanandTiltSpeedMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x01\x06\x1F\x00\xFF',
            'Smooth': b'\x01\x06\x1F\x01\xFF'
        }

        PanandTiltSpeedModeCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('PanandTiltSpeedMode', PanandTiltSpeedModeCmdString, value, qualifier)

    def SetPanNormal(self, value, qualifier):

        PanSpeed = int(qualifier['Pan Speed'])

        if 1 <= PanSpeed <= 24:
            ValueStateValues = {
                'Left': pack('>B3sB4s', self.cameraID, b'\x01\x06\x01', PanSpeed, b'\x00\x01\x03\xFF'),
                'Right': pack('>B3sB4s', self.cameraID, b'\x01\x06\x01', PanSpeed, b'\x00\x02\x03\xFF'),
                'Stop': pack('>B8s', self.cameraID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
            }
            PanNormalCmdString = ValueStateValues[value]
            self.__SetHelper('PanNormal', PanNormalCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanNormal')

    def SetPanSmooth(self, value, qualifier):

        PanSpeed = int(qualifier['Pan Speed'])

        if 1 <= PanSpeed <= 100:
            ValueStateValues = {
                'Left': pack('>B3sB4s', self.cameraID, b'\x01\x06\x01', PanSpeed, b'\x00\x01\x03\xFF'),
                'Right': pack('>B3sB4s', self.cameraID, b'\x01\x06\x01', PanSpeed, b'\x00\x02\x03\xFF'),
                'Stop': pack('>B8s', self.cameraID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
            PanSmoothCmdString = ValueStateValues[value]
            self.__SetHelper('PanSmooth', PanSmoothCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanSmooth')

    def SetPictureFlip(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x66\x02\xFF',
            'Off': b'\x01\x04\x66\x03\xFF'
        }

        PictureFlipCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('PictureFlip', PictureFlipCmdString, value, qualifier)

    def UpdatePictureFlip(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        PictureFlipCmdString = pack('>B4s', self.cameraID, b'\x09\x04\x66\xFF')
        res = self.__UpdateHelper('PictureFlip', PictureFlipCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureFlip', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureFlip')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        PowerCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            0x01: 'On',
            0x00: 'Off',
           }

        MirrorImageStateNames = {
            0x04: 'On',
            0x00: 'Off',
        }

        PowerCmdString = pack('>B5s', self.cameraID, b'\x09\x7E\x7E\x02\xFF')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', PowerStateNames[res[2] & 0x01], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')
            try:
                self.WriteStatus('MirrorImage', MirrorImageStateNames[res[3] & 0x04], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetRecallCmdString = pack('>B4sBB', self.cameraID, b'\x01\x04\x3F\x02', int(value), 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetResetCmdString = pack('>B4sBB', self.cameraID, b'\x01\x04\x3F\x00', int(value), 0xFF)
            self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(value) <= 127:
            PresetSaveCmdString = pack('>B4sBB', self.cameraID, b'\x01\x04\x3F\x01', int(value), 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetPresetSpeed(self, value, qualifier):

        ValueStateValues = {
            '150 degree/second': b'\x01\x06\x20\x00\xFF',
            '250 degree/second': b'\x01\x06\x20\x01\xFF',
            '300 degree/second': b'\x01\x06\x20\x02\xFF'
        }

        PresetSpeedCmdString = pack('>B5s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('PresetSpeed', PresetSpeedCmdString, value, qualifier)

    def SetTallyLamp(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x7E\x01\x0A\x00\x02\xFF',
            'Off': b'\x01\x7E\x01\x0A\x00\x03\xFF'
        }

        TallyLampCmdString = pack('>B7s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('TallyLamp', TallyLampCmdString, value, qualifier)

    def UpdateTallyLamp(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        TallyLampCmdString = pack('>B6s', self.cameraID, b'\x09\x7E\x01\x0A\x00\xFF')
        res = self.__UpdateHelper('TallyLamp', TallyLampCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('TallyLamp', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTallyLamp')

    def SetTallyMode(self, value, qualifier):

        ValueStateValues = {
            'On (Low)': b'\x01\x7E\x01\x0A\x01\x04\xFF',
            'On (High)': b'\x01\x7E\x01\x0A\x01\x05\xFF',
            'Off': b'\x01\x7E\x01\x0A\x01\x00\xFF'
        }

        TallyModeCmdString = pack('>B7s', self.cameraID, ValueStateValues[value])
        self.__SetHelper('TallyMode', TallyModeCmdString, value, qualifier)

    def UpdateTallyMode(self, value, qualifier):

        ValueStateValues = {
            0x04: 'On (Low)',
            0x05: 'On (High)',
            0x00: 'Off'
        }

        TallyModeCmdString = pack('>B6s', self.cameraID, b'\x09\x7E\x01\x0A\x01\xFF')
        res = self.__UpdateHelper('TallyMode', TallyModeCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('TallyMode', ValueStateValues[res[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTallyMode')

    def SetTiltNormal(self, value, qualifier):

        TiltSpeed = int(qualifier['Tilt Speed'])

        if 1 <= TiltSpeed <= 24:
            ValueStateValues = {
                    'Up': pack('>B4sB3s', self.cameraID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x01\xFF'),
                    'Down': pack('>B4sB3s', self.cameraID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x02\xFF'),
                    'Stop': pack('>B8s', self.cameraID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
            TiltNormalCmdString = ValueStateValues[value]
            self.__SetHelper('TiltNormal', TiltNormalCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTiltNormal')

    def SetTiltSmooth(self, value, qualifier):

        TiltSpeed = int(qualifier['Tilt Speed'])

        if 1 <= TiltSpeed <= 100:
            ValueStateValues = {
                    'Up': pack('>B4sB3s', self.cameraID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x01\xFF'),
                    'Down': pack('>B4sB3s', self.cameraID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x02\xFF'),
                    'Stop': pack('>B8s', self.cameraID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
            TiltSmoothCmdString = ValueStateValues[value]
            self.__SetHelper('TiltSmooth', TiltSmoothCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTiltSmooth')

    def SetZoom(self, value, qualifier):

        ZoomSpeed = int(qualifier['Zoom Speed'])

        if 0 <= ZoomSpeed <= 7:
            ValueStateValues = {
                'Tele': pack('>B3sBB', self.cameraID, b'\x01\x04\x07', 0x20 + ZoomSpeed, 0xFF),
                'Wide': pack('>B3sBB', self.cameraID, b'\x01\x04\x07', 0x30 + ZoomSpeed, 0xFF),
                'Stop': pack('>B5s', self.cameraID, b'\x01\x04\x07\x00\xFF'),
            }
            ZoomCmdString = ValueStateValues[value]
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02': 'Syntax Error',
            b'\x03': 'Command buffer full',
            b'\x04': 'Command cancelled',
            b'\x05': 'No socket (to be cancelled)',
            b'\x41': 'Command not executable'
        }

        matchedInfo = re.search(self.matchError, response)

        if matchedInfo:
            print('{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[matchedInfo.group(1)]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

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
