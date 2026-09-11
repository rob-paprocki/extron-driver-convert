from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self._DeviceID = 1
        self.Models = {}
        self._DeviceID = '01'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoSearch': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PAPMode': {'Status': {}},
            'PAPSize': {'Status': {}},
            'PAPSubSource': {'Status': {}},
            'PAPSwap': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'PowerSave': {'Status': {}},
            'Speaker': {'Status': {}},
            'TouchControlMode': {'Status': {}},
            'TouchControlSetting': {'Status': {}},
            'TouchFeature': {'Status': {}},
            'TouchOSDMode': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1<= int(value) <= 98:
            self._DeviceID = value.zfill(2)
        else:
            print('DeviceID invalid, range is from 1 to 98')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '001',
            'Off': '000'
        }

        AudioMuteCmdString = '8{0}s\x36{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '8{0}g\x67000\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '8{0}s\x8F000\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAutoSearch(self, value, qualifier):

        ValueStateValues = {
            'On': '001',
            'Off': '000'
        }

        AutoSearchCmdString = '8{0}s\x96{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('AutoSearch', AutoSearchCmdString, value, qualifier)

    def UpdateAutoSearch(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AutoSearchCmdString = '8{0}g\xC6000\x0D'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('AutoSearch', AutoSearchCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AutoSearch', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Search: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': '0',
            'HDMI': '1',
            'Computer': '2',
            'DVI': '6',
            'DisplayPort': '7'
        }

        InputCmdString = '8{0}s\x2200{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'VGA',
            '1': 'HDMI',
            '2': 'Computer',
            '6': 'DVI',
            '7': 'DisplayPort'
        }

        InputCmdString = '8{0}g\x6A000\x0D'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '001',
            'Off': '000'
        }

        OnScreenDisplayCmdString = '8{0}s\x5B{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = '8{0}g\x5D000\r'.format(self._DeviceID)
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def SetPAPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '000',
            'PIP': '001',
            'PBP': '002'
        }

        PAPModeCmdString = '8{0}s\x8A{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('PAPMode', PAPModeCmdString, value, qualifier)

    def UpdatePAPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PBP'
        }

        PAPModeCmdString = '8{0}g\xBA000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('PAPMode', PAPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PAPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PAP Mode: Invalid/unexpected response'])

    def SetPAPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '00000',
            'Large': '10000'
        }

        PAPSizeCmdString = '\x3A{0}s\x8D{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('PAPSize', PAPSizeCmdString, value, qualifier)

    def UpdatePAPSize(self, value, qualifier):

        ValueStateValues = {
            '0': 'Small',
            '1': 'Large'
        }

        PAPSizeCmdString = '\x3A{0}g\xBD00000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('PAPSize', PAPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-6]]
                self.WriteStatus('PAPSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PAP Size: Invalid/unexpected response'])

    def SetPAPSubSource(self, value, qualifier):

        ValueStateValues = {
            'VGA': '000',
            'HDMI 1': '001',
            'HDMI 2 (OPS)': '002',
            'DVI': '006',
            'DisplayPort': '007'
        }

        PAPSubSourceCmdString = '8{0}s\x8B{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('PAPSubSource', PAPSubSourceCmdString, value, qualifier)

    def UpdatePAPSubSource(self, value, qualifier):

        ValueStateValues = {
            '0': 'VGA',
            '1': 'HDMI 1',
            '2': 'HDMI 2 (OPS)',
            '6': 'DVI',
            '7': 'DisplayPort'
        }

        PAPSubSourceCmdString = '8{0}g\xBB000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('PAPSubSource', PAPSubSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PAPSubSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PAP Sub Source: Invalid/unexpected response'])

    def SetPAPSwap(self, value, qualifier):

        PAPSwapCmdString = '8{0}s\x8C\r'.format(self._DeviceID)
        self.__SetHelper('PAPSwap', PAPSwapCmdString, value, qualifier)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Left': '00000',
            'Upper Right': '10000',
            'Lower Left': '20000',
            'Lower Right': '30000'
        }

        PIPPositionCmdString = '\x3A{0}s\x8E{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            '0': 'Upper Left',
            '1': 'Upper Right',
            '2': 'Lower Left',
            '3': 'Lower Right'
        }

        PIPPositionCmdString = '\x3A{0}g\xBF00000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-6]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Position: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '001',
            'Off': '000'
        }

        PowerCmdString = '8{0}s\x21{1}\r'.format(self._DeviceID, ValueStateValues[value])  # confirmed w/ previous developer no delay required
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '8{0}g\x6C000\x0D'.format(self._DeviceID)  # confirmed w/ previous developer query was obtained via testing w/ device
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPowerSave(self, value, qualifier):

        ValueStateValues = {
            'Off': '000',
            'Low': '001',
            'High': '002'
        }

        PowerSaveCmdString = '8{0}s\xA9{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('PowerSave', PowerSaveCmdString, value, qualifier)

    def UpdatePowerSave(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Low',
            '2': 'High'
        }

        PowerSaveCmdString = '8{0}g\xD9000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('PowerSave', PowerSaveCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PowerSave', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Save: Invalid/unexpected response'])

    def SetSpeaker(self, value, qualifier):

        ValueStateValues = {
            'Internal': '000',
            'External': '001'
        }

        SpeakerCmdString = '8{0}s\x89{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('Speaker', SpeakerCmdString, value, qualifier)

    def UpdateSpeaker(self, value, qualifier):

        ValueStateValues = {
            '0': 'Internal',
            '1': 'External'
        }

        SpeakerCmdString = '8{0}g\xB9000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('Speaker', SpeakerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Speaker', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Speaker: Invalid/unexpected response'])

    def SetTouchControlMode(self, value, qualifier):

        ValueStateValues = {
            'Old': '000',
            'New': '001',
            'Off': '002'
        }

        TouchControlModeCmdString = '8{0}s\xEC{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('TouchControlMode', TouchControlModeCmdString, value, qualifier)

    def UpdateTouchControlMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Old',
            '1': 'New',
            '2': 'Off'
        }

        TouchControlModeCmdString = '8{0}g\xEC000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('TouchControlMode', TouchControlModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('TouchControlMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Control Mode: Invalid/unexpected response'])

    def SetTouchControlSetting(self, value, qualifier):

        ValueStateValues = {
            'Auto': '000',
            'Computer In': '001',
            'USB': '002'
        }

        TouchControlSettingCmdString = '8{0}s\xEB{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('TouchControlSetting', TouchControlSettingCmdString, value, qualifier)

    def UpdateTouchControlSetting(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Computer In',
            '2': 'USB'
        }

        TouchControlSettingCmdString = '8{0}g\xEB000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('TouchControlSetting', TouchControlSettingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('TouchControlSetting', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Control Setting: Invalid/unexpected response'])

    def SetTouchFeature(self, value, qualifier):

        ValueStateValues = {
            'On': '001',
            'Off': '000'
        }

        TouchFeatureCmdString = '8{0}s\x9E{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('TouchFeature', TouchFeatureCmdString, value, qualifier)

    def UpdateTouchFeature(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        TouchFeatureCmdString = '8{0}g\x9E000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('TouchFeature', TouchFeatureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('TouchFeature', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Feature: Invalid/unexpected response'])

    def SetTouchOSDMode(self, value, qualifier):

        ValueStateValues = {
            'On': '001',
            'Off': '000'
        }

        TouchOSDModeCmdString = '8{0}s\xED{1}\r'.format(self._DeviceID, ValueStateValues[value]).encode(encoding='iso-8859-1')
        self.__SetHelper('TouchOSDMode', TouchOSDModeCmdString, value, qualifier)

    def UpdateTouchOSDMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        TouchOSDModeCmdString = '8{0}g\xED000\r'.format(self._DeviceID).encode(encoding='iso-8859-1')
        res = self.__UpdateHelper('TouchOSDMode', TouchOSDModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('TouchOSDMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch OSD Mode: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '8{0}s\x35{1:03d}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '8{0}g\x66000\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            try:
                if '401' in response:
                    self.Error(['Device is Busy'])
                    response = ''
            except (TypeError):
                response = response.decode("utf-8", "replace")
                if '401' in response:
                    self.Error(['Device is Busy'])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode('iso-8859-1'))

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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

