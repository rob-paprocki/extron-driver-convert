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
            'DisplayMode': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPAudioInput': {'Status': {}},
            'PIPInput': {'Parameters': ['Window'], 'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }       

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': 'set displaymode=standard\r',
            'User': 'set displaymode=user\r',
            'Dynamic': 'set displaymode=dynamic\r'
        }

        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            's': 'Standard',
            'u': 'User',
            'd': 'Dynamic'
        }

        DisplayModeCmdString = 'get displaymode\r'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[13]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDisplayMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'set input=hdmi1\r',
            'HDMI 2': 'set input=hdmi2\r',
            'DisplayPort': 'set input=displayport\r',
            'OPS HDMI': 'set input=ops/hdmi\r',
            'OPS DisplayPort': 'set input=ops/displayport\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'hdmi1': 'HDMI 1',
            'hdmi2': 'HDMI 2',
            'displ': 'DisplayPort',
            'ops/h': 'OPS HDMI',
            'ops/d': 'OPS DisplayPort'
        }

        InputCmdString = 'get input\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:12]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'set mute=on\r',
            'Off': 'set mute=off\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            'n': 'On',
            'f': 'Off'
        }

        MuteCmdString = 'get mute\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetPIPAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Window 1': 'set mwaudioinput=window1\r',
            'Window 2': 'set mwaudioinput=window2\r',
            'Window 3': 'set mwaudioinput=window3\r',
            'Window 4': 'set mwaudioinput=window4\r'
        }

        PIPAudioInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPAudioInput', PIPAudioInputCmdString, value, qualifier)

    def UpdatePIPAudioInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'Window 1',
            '2': 'Window 2',
            '3': 'Window 3',
            '4': 'Window 4'
        }

        PIPAudioInputCmdString = 'get mwaudioinput\r'
        res = self.__UpdateHelper('PIPAudioInput', PIPAudioInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[20]]
                self.WriteStatus('PIPAudioInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPAudioInput')

    def SetPIPInput(self, value, qualifier):

        InputStates = {
            'HDMI 1': 'hdmi1\r',
            'HDMI 2': 'hdmi2\r',
            'DisplayPort': 'displayport\r',
            'OPS HDMI': 'opshdmi\r',
            'OPS HDMI/DisplayPort': 'opshdmidisplayport\r'
        }

        ValueStateValues = {
            '1': 'set mwwindow1input=',
            '2': 'set mwwindow2input=',
            '3': 'set mwwindow3input=',
            '4': 'set mwwindow4input='
        }

        PIPInputCmdString = ValueStateValues[qualifier['Window']] + InputStates[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'get mwwindow1input\r',
            '2': 'get mwwindow2input\r',
            '3': 'get mwwindow3input\r',
            '4': 'get mwwindow4input\r'
        }

        InputStates = {
            'hdmi1': 'HDMI 1',
            'hdmi2': 'HDMI 2',
            'displayport': 'DisplayPort',
            'opshdmi': 'OPS HDMI',
            'opshdmidisplayport': 'OPS HDMI/DisplayPort'
        }

        PIPInputCmdString = ValueStateValues[qualifier['Window']]
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = InputStates[res[16:-1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'set mw=off\r',
            'Dual': 'set mw=dual\r',
            'Quad': 'set mw=quad\r'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            'o': 'Off',
            'd': 'Dual',
            'q': 'Quad'
        }

        PIPModeCmdString = 'get mw\r'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'set powerstate=on\r',
            'Off': 'set powerstate=off\r',
            'Standby': 'set powerstate=standby\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'n': 'On',
            'f': 'Off',
            't': 'Standby'
        }

        PowerCmdString = 'get powerstate\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[13]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'set volume={0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[8:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'invalid' in response:
            print(response)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

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
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())
        

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
