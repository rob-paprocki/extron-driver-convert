from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'CF SCREEN NORMAL\r',
            'Wide': 'CF SCREEN WIDE\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '000 NORMAL\r': 'Normal',
            '000 WIDE\r': 'Wide'
        }

        AspectRatioCmdString = 'CR SCREEN\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Aspect Ratio has received an invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'C0B\r',
            'Off': 'C0C\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        AudioMuteCmdString = 'CR MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Audio Mute has received an invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 'C4B\r',
            'Near': 'C4A\r'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'C43\r',
            'Off': 'C44\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        FreezeCmdString = 'CR FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Freeze has received an invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Input 1 Digital': 'CF INPUT1 DIGITAL\r',
            'Input 1 Analog': 'CF INPUT1 ANALOG\r',
            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 YPBPR': 'CF INPUT2 YPBPR\r',
            'Input 2 Analog': 'CF INPUT2 ANALOG\r',
            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 YPBPR': 'CF INPUT3 YPBPR\r',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'CF INPUT1 DIGITAL\r': 'Input 1 Digital',
            'CF INPUT1 ANALOG\r': 'Input 1 Analog',
            'CF INPUT2 VIDEO\r': 'Input 2 Video',
            'CF INPUT2 YPBPR\r': 'Input 2 YPBPR',
            'CF INPUT2 ANALOG\r': 'Input 2 Analog',
            'CF INPUT3 VIDEO\r': 'Input 3 Video',
            'CF INPUT3 S-VIDEO\r': 'Input 3 S-Video',
            'CF INPUT3 YPBPR\r': 'Input 3 YPBPR',
        }

        InputCmdString = 'CR INPUT\r'  # Pg. 10
        getInputNum = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if getInputNum:
            try:
                input = getInputNum[4:-1].strip('0')
                inputTypeCmdString = 'CR SRCINP{0}\r'.format(input)  # Pg. 11
                getSource = self.__UpdateHelper('Input', inputTypeCmdString, value, qualifier)
                if getSource:
                    try:
                        source = getSource[4:-1]
                        value = ValueStateValues['CF INPUT{0} {1}\r'.format(input, source)]
                        self.WriteStatus('Input', value, qualifier)
                    except(KeyError, IndexError):
                        self.Error(['Source response for Input {0} is invalid/unexpected'.format(input)])
            except (KeyError, IndexError):
                self.Error(['Update Input has received an invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': 'CF LAMPMODE ECO\r',
            'Normal': 'CF LAMPMODE FUL\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '000 ECO\r': 'Eco',
            '000 FUL\r': 'Normal'
        }

        LampModeCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode has received an invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR3\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

        if res:
            try:
                val = res.split(' ')
                value = int(val[1].encode())
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage has received an invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStates = {
            'On': 'C1C\r',
            'Up': 'C3C\r',
            'Down': 'C3D\r',
            'Left': 'C3B\r',
            'Right': 'C3A\r',
            'Enter': 'C3F\r',
            'Off': 'C1D\r'
        }

        MenuNavigationCmdString = ValueStates[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                val = res.split(' ')
                value = int(val[1].encode())
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours has received an invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'C00\r',
            'Off': 'C01\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '00': 'On',
            '02': 'On',
            '08': 'On',
            '88': 'On',
            '80': 'Off',
            '40': 'Warming Up',
            '20': 'Cooling Down',
            '28': 'Cooling Down',
            '24': 'Off',
            '10': 'Off',
            '04': 'Off'
        }

        DRStateValues = {
            '00': 'Normal',
            '80': 'Normal',
            '88': 'Temp Warning & Recovered',
            '40': 'Countdown in Process',
            '20': 'Cooling Down in Process',
            '28': 'Cooling Down (Abnormal Temp)',
            '24': 'Power Save (Cooling Down)',
            '10': 'Power Failure',
            '04': 'Power Save',
            '08': 'Temp Warning (Power On)',
            '02': 'No Key Input'
        }

        PowerCmdString = 'CR0\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                powerValue = PowerStateValues[res[:-1]]
                devresValue = DRStateValues[res[:-1]]
                self.WriteStatus('Power', powerValue, qualifier)
                self.WriteStatus('DeviceStatus', devresValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Power/Device Status has received an invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStates = {
            'On': 'C0D\r',
            'Off': 'C0E\r'
        }

        VideoMuteCmdString = ValueStates[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Update Video Mute has received an invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeCmdString = 'CF VOLUME {:03}\r'.format(value)

        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'CR VOLUME\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                val = res.split(' ')
                value = int(val[1].encode())
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Update Volume has received an invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStates = {
            'In': 'C47\r',
            'Out': 'C46\r'
        }

        ZoomCmdString = ValueStates[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'?\r': 'Data Cannot Be Decoded/Parameter Designation Error.',
                              '101\r': 'The Function is Not Available in the Selected Mode.',
                              '102\r': 'The Selected Value is Out of Range',
                              '103\r': 'Command Mismatched to the Hardware.'
                              }

        if response in DEVICE_ERROR_CODES:
            self.Error(['Error with {0} - Error Code: {1}: {2}'.format(sourceCmdName, response.strip(), DEVICE_ERROR_CODES[response])])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['Invalid/unexpected response while sending set command for {0}'.format(command)])
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

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
