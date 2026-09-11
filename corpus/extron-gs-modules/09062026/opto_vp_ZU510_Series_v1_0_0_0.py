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
        self.Models = {
            'ZU510T': self.opto_1_2553_ZU510T,
            'ZU510': self.opto_1_2553_ZU510,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioOut': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Microphone': {'Status': {}},
            'MicrophoneVolume': {'Status': {}},
            'PIPLocation': {'Status': {}},
            'PIPMainSource': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSubSource': {'Status': {}},
            'Power': {'Status': {}},
            'Speaker': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '1',
            '16:9': '2',
            '16:10': '3',
            'Auto': '7',
        }

        CmdString = '~0060 {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': '4:3',
            '2': '16:9',
            '3': '16:10',
            '7': 'Auto',
            '0': 'No Aspect Ratio'
        }

        res = self.__UpdateHelper('AspectRatio', '~00127 1\r', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '~0001 1\r', value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '~0002 1\r',
            'Off': '~0002 0\r'
        }

        self.__SetHelper('AVMute', ValueStateValues[value], value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('AVMute', '~00355 1\r', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAVMute')

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '~0020 1\r',
            'Bright': '~0020 2\r',
            'Cinema': '~0020 3\r',
            'sRGB': '~0020 4\r',
            'User': '~0020 5\r',
            'DICOM SIM': '~0020 13\r',
            'Blending': '~0020 19\r',
        }

        self.__SetHelper('DisplayMode', ValueStateValues[value], value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', '~00321 1\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage', int(res[2:6]), qualifier)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '~0004 1\r',
            'Off': '~0004 0\r'
        }

        self.__SetHelper('Freeze', ValueStateValues[value], value, qualifier)

    def SetInput(self, value, qualifier):

        self.__SetHelper('Input', self.Inputs[value], value, qualifier, 3)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Bright': '~00110 1\r',
            'Eco': '~00110 2\r',
        }

        self.__SetHelper('LampMode', ValueStateValues[value], value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '~00140 10\r',
            'Down': '~00140 14\r',
            'Left': '~00140 11\r',
            'Right': '~00140 13\r',
            'Enter': '~00140 12\r',
            'Menu': '~00140 20\r'
        }

        self.__SetHelper('MenuNavigation', ValueStateValues[value], value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '~0000 1\r',
            'Off': '~0000 0\r',
        }

        self.__SetHelper('Power', ValueStateValues[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        DisplayStateValues = {
            1: 'Presentation',
            2: 'Bright',
            3: 'Cinema',
            4: 'sRGB',
            5: 'User',
            10: 'DICOM SIM',
            18: 'Blending',
            0: 'No Display Mode',
        }

        res = self.__UpdateHelper('Power', '~00150 1\r', value, qualifier)

        if res:
            try:
                power = PowerStateValues[res[2]]
                self.WriteStatus('Power', power, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

            if res[2] == '1':
                try:

                    lamp_hours = int(res[3:8])
                    self.WriteStatus('LampUsage', lamp_hours, qualifier)
                except (IndexError, ValueError):
                    print('Invalid/Unexpected Response for UpdatePower')

                try:

                    inputstate = self.InputStates[int(res[8:10])]
                    self.WriteStatus('Input', inputstate, qualifier)
                except (IndexError, ValueError):
                    print('Invalid/Unexpected Response for UpdatePower')

                try:

                    display = DisplayStateValues[int(res[13:15])]
                    self.WriteStatus('DisplayMode', display, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '~0080 1\r',
            'Off': '~0080 0\r'
        }

        self.__SetHelper('VideoMute', ValueStateValues[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('VideoMute', '~00356 1\r', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetSpeaker(self, value, qualifier):

        ValueStateValues = {
            'On': '~00310 1\r',
            'Off': '~00310 0\r'
        }

        self.__SetHelper('Speaker', ValueStateValues[value], value, qualifier)

    def SetAudioOut(self, value, qualifier):

        ValueStateValues = {
            'On': '~00510 1\r',
            'Off': '~00510 0\r'
        }

        self.__SetHelper('AudioOut', ValueStateValues[value], value, qualifier)

    def SetMicrophone(self, value, qualifier):

        ValueStateValues = {
            'On': '~00562 1\r',
            'Off': '~00562 0\r'
        }

        self.__SetHelper('Microphone', ValueStateValues[value], value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '~0080 1\r',
            'Off': '~0080 0\r'
        }

        self.__SetHelper('AudioMute', ValueStateValues[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('AudioMute', '~00356 1\r', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 15:
            VolumeCmdString = '~0081 {0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetMicrophoneVolume(self, value, qualifier):

        if 0 <= value <= 30:
            CmdString = '~0093 {0}\r'.format(value)
            self.__SetHelper('MicrophoneVolume', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '~00302 0\r',
            'PIP': '~00302 1\r',
            'PBP': '~00302 2\r'
        }

        self.__SetHelper('PIPMode', ValueStateValues[value], value, qualifier)

    def SetPIPMainSource(self, value, qualifier):

        self.__SetHelper('PIPMainSource', self.PIPMainSources[value], value, qualifier)

    def UpdatePIPMainSource(self, value, qualifier):
        res = self.__UpdateHelper('PIPMainSource', '~00121 1\r', value, qualifier)
        if res:
            try:
                value = self.PIPMainSourceStates[int(res[2:-1])]
                self.WriteStatus('PIPMainSource', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdatePIPMainSource')

    def SetPIPSubSource(self, value, qualifier):

        self.__SetHelper('PIPSubSource', self.PIPSubSources[value], value, qualifier)

    def UpdatePIPSubSource(self, value, qualifier):
        res = self.__UpdateHelper('PIPSubSource', '~00131 1\r', value, qualifier)
        if res:
            try:
                value = self.PIPSubSourceStates[int(res[2:-1])]
                self.WriteStatus('PIPSubSource', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdatePIPSubSource')

    def SetPIPLocation(self, value, qualifier):

        ValueStateValues = {
            'Top Left': '~00303 1\r',
            'Top Right': '~00303 2\r',
            'Bottom Left': '~00303 3\r',
            'Bottom Right': '~00303 4\r'
        }

        self.__SetHelper('PIPLocation', ValueStateValues[value], value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Large': '~00304 1\r',
            'Medium': '~00304 2\r',
            'Small': '~00304 3\r'
        }

        self.__SetHelper('PIPSize', ValueStateValues[value], value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def opto_1_2553_ZU510T(self):

        self.Inputs = {
            'HDMI 1': '~0012 1\r',
            'HDMI 2': '~0012 15\r',
            'Dongle': '~0012 16\r',
            'VGA': '~0012 20\r',
            'HDBaseT': '~0012 5\r',
        }

        self.InputStates = {
            7: 'HDMI 1',
            8: 'HDMI 2',
            14: 'Dongle',
            2: 'VGA',
            16: 'HDBaseT',
            0: 'No Input',
        }

        self.PIPMainSources = {
            'HDMI 1': '~0012 1\r',
            'HDMI 2': '~0012 15\r',
            'Dongle': '~0012 16\r',
            'VGA': '~0012 5\r',
            'HDBaseT': '~0012 21\r'
        }

        self.PIPMainSourceStates = {
            7: 'HDMI 1',
            8: 'HDMI 2',
            9: 'Dongle',
            2: 'VGA',
            16: 'HDBaseT'
        }

        self.PIPSubSources = {
            'HDMI 1': '~0013 1\r',
            'HDMI 2': '~0013 15\r',
            'Dongle': '~0013 16\r',
            'VGA': '~0013 5\r',
            'HDBaseT': '~0013 21\r'
        }

        self.PIPSubSourceStates = {
            7: 'HDMI 1',
            8: 'HDMI 2',
            9: 'Dongle',
            2: 'VGA',
            16: 'HDBaseT'
        }

    def opto_1_2553_ZU510(self):

        self.Inputs = {
            'HDMI 1': '~0012 1\r',
            'HDMI 2': '~0012 15\r',
            'Dongle': '~0012 16\r',
            'VGA': '~0012 20\r',
        }

        self.InputStates = {
            7: 'HDMI 1',
            8: 'HDMI 2',
            14: 'Dongle',
            2: 'VGA',
            0: 'No Input',
        }

        self.PIPMainSources = {
            'HDMI 1': '~0012 1\r',
            'HDMI 2': '~0012 15\r',
            'Dongle': '~0012 16\r',
            'VGA': '~0012 5\r',
        }

        self.PIPMainSourceStates = {
            7: 'HDMI 1',
            8: 'HDMI 2',
            9: 'Dongle',
            2: 'VGA',
        }

        self.PIPSubSources = {
            'HDMI 1': '~0013 1\r',
            'HDMI 2': '~0013 15\r',
            'Dongle': '~0013 16\r',
            'VGA': '~0013 5\r',
        }

        self.PIPSubSourceStates = {
            7: 'HDMI 1',
            8: 'HDMI 2',
            9: 'Dongle',
            2: 'VGA',
        }

        super().__init__(configs)
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
