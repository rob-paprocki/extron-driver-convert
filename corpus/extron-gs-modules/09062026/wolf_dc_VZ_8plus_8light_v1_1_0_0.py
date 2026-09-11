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
        self.Models = {
            'VZ-8plus3': self.wolf_16_746_plus,
            'VZ-8light3': self.wolf_16_746_light,
            'VZ-8light2': self.wolf_16_746_light,
            'VZ-8plus2': self.wolf_16_746_plus,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'ColorBW': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Status': {}},
            'Light': {'Status': {}},
            'LightBox': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'OutputSource': {'Status': {}},
            'PosNeg': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'TextEnhancer': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Status': {}},
            }


    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xEF',
            'Off': b'\xF0'
        }

        AutoFocusCmdString = ValueStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        AutoFocusCmdString = b'\xAD'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA7',
            'Off': b'\xA8'
        }

        AutoIrisCmdString = ValueStateValues[value]
        self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def UpdateAutoIris(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        AutoIrisCmdString = b'\xA6'
        res = self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('AutoIris', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Iris: Invalid/unexpected response'])

    def SetColorBW(self, value, qualifier):

        ValueStateValues = {
            'Color': b'\x31\x9B',
            'B/W': b'\x31\x9C'
        }

        ColorBWCmdString = ValueStateValues[value]
        self.__SetHelper('ColorBW', ColorBWCmdString, value, qualifier)

    def UpdateColorBW(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Color',
            b'1': 'B/W'
        }

        ColorBWCmdString = b'\x31\x9D'
        res = self.__UpdateHelper('ColorBW', ColorBWCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('ColorBW', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color BW: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': b'\x83',
            'Near': b'\x84',
            'Stop': b'\x80'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier) 
        
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31\xA6',
            'Off': b'\x31\xA7',
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }

        FreezeCmdString = b'\x31\xA8'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Open': b'\x85',
            'Close': b'\x86',
            'Stop': b'\x80'
        }

        IrisCmdString = ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier) 
        
    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xB2',
            'Off': b'\xCD',
        }

        LightCmdString = ValueStateValues[value]
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def UpdateLight(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }

        LightCmdString = b'\xAC'
        res = self.__UpdateHelper('Light', LightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('Light', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Light: Invalid/unexpected response'])

    def SetLightBox(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xB3',
            'Off': b'\xB2'
        }

        LightBoxCmdString = ValueStateValues[value]
        self.__SetHelper('LightBox', LightBoxCmdString, value, qualifier)

    def UpdateLightBox(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        LightBoxCmdString = b'\xB4'
        res = self.__UpdateHelper('LightBox', LightBoxCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('LightBox', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Light Box: Invalid/unexpected response'])

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x31\x92',
            'Up': b'\x31\x90',
            'Down': b'\x31\x91'
        }

        OutputResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = b'\x31\x93'
        res = self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        if res:
            try:
                if res[0:4] == b'AUTO':
                    value = self.OutputResolutionValues[res[0:4]]
                    self.WriteStatus('OutputResolution', value, qualifier)
                else:
                    value = self.OutputResolutionValues[res[0:7]]
                    self.WriteStatus('OutputResolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Output Resolution: Invalid/unexpected response'])

    def SetOutputSource(self, value, qualifier):

        ValueStateValues = {
            'Internal': b'\x31\x82',
            'External': b'\x31\x81',
        }

        OutputSourceCmdString = ValueStateValues[value]
        self.__SetHelper('OutputSource', OutputSourceCmdString, value, qualifier)

    def UpdateOutputSource(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Internal',
            b'1': 'External',
        }

        OutputSourceCmdString = b'\x31\x83'
        res = self.__UpdateHelper('OutputSource', OutputSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('OutputSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Output Source: Invalid/unexpected response'])

    def SetPosNeg(self, value, qualifier):

        ValueStateValues = {
            'Positive': b'\x31\x97',
            'Negative': b'\x31\x98',
            'Neg Blue': b'\x31\x99'
        }

        PosNegCmdString = ValueStateValues[value]
        self.__SetHelper('PosNeg', PosNegCmdString, value, qualifier)

    def UpdatePosNeg(self, value, qualifier):

        ValueStateValues = {
            b'0': 'Positive',
            b'1': 'Negative',
            b'2': 'Neg Blue'
        }

        PosNegCmdString = b'\x31\x9A'
        res = self.__UpdateHelper('PosNeg', PosNegCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('PosNeg', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Pos Neg: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xC8',
            'Off': b'\xC9',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        if value == 'On':
            self.__SetHelper('Power', b'\x9F', value, qualifier)  # Enable Replay String Mode (page 10)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }
        PowerCmdString = b'\xAB'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\xCA',
            '2': b'\xCB',
            '3': b'\xFD',
            '0': b'\xD5'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier) 
        
    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\xD8',
            '2': b'\xD9',
            '3': b'\xFE'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier) 
        
    def SetTextEnhancer(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31\x9E',
            'Off': b'\x31\x9F',
        }

        TextEnhancerCmdString = ValueStateValues[value]
        self.__SetHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)

    def UpdateTextEnhancer(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }

        TextEnhancerCmdString = b'\x31\xA0'
        res = self.__UpdateHelper('TextEnhancer', TextEnhancerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('TextEnhancer', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Text Enhancer: Invalid/unexpected response'])

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceCmdString = b'\x97'
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier) 
        
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': b'\x82',
            'Wide': b'\x81',
            'Stop': b'\x80'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, str):
            response = response.encode()

        DEVICE_ERROR_CODES = {b'ERROR': 'Error Ocurred'}

        if response[0:5] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Send(b'\x9F') #Enable Replay String Mode (page 10)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def wolf_16_746_plus(self):
        self.OutputResolutionValues = {
            b'SVGA/60' : 'SVGA / 60Hz', 
            b'720p/60' : '720p / 60Hz', 
            b'XGA/60\n': 'XGA / 60Hz',
            b'WXGA/60' : 'WXGA / 60Hz',
            b'SXGA/60' : 'SXGA / 60Hz',
            b'SXGA+/6' : 'SXGA / 60Hz',
            b'SXGA-/6' : 'SXGA / 60Hz',
            b'SVGA/75' : 'SVGA / 75Hz', 
            b'XGA/75\n': 'XGA / 75Hz',
            b'SXGA/75' : 'SXGA / 75Hz',
            b'SXGA+/7' : 'SXGA / 75Hz',
            b'SXGA-/7' : 'SXGA / 75Hz',
            b'SVGA/85' : 'SVGA / 85Hz', 
            b'XGA/85\n': 'XGA / 85Hz',
            b'SXGA/85' : 'SXGA / 85Hz',
            b'SXGA+/8' : 'SXGA / 85Hz',
            b'SXGA-/8' : 'SXGA / 85Hz',
            b'AUTO'    : 'Auto'
        }


    def wolf_16_746_light(self):
        self.OutputResolutionValues = {
            b'XGA/60\n': 'XGA / 60Hz',
            b'XGA/75\n': 'XGA / 75Hz',
            b'AUTO'    : 'Auto'
        }
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

