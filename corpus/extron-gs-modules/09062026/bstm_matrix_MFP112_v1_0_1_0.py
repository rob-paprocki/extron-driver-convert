from extronlib.interface import SerialInterface, EthernetClientInterface

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
            'AudioInputMode': {'Parameters': ['Input'], 'Status': {}},
            'AudioOutputMode': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Type'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputBypass': {'Status': {}},
            'OutputMode': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'Power': {'Status': {}},
            'ScalerVolume': {'Status': {}},
        }

        self.Inputs = {'HDBT', 'HDMI1', 'HDMI2', 'HDMI3', 'HDMI4', 'VGA1', 'VGA2', 'VGA3', 'VGA4', 'YPBPR', 'AV'}

    def SetAudioInputMode(self, value, qualifier):

        InputStates = {
            'HDMI1': '01',
            'HDMI2': '02',
            'HDMI3': '03',
            'HDMI4': '04',
        }
        ValueStateValues = {
            'HDMI': 'AUDHDMI{}ORG\r',
            'Analog': 'AUDHDMI{}ANA\r',
            'Auto': 'AUDHDMI{}AUTO\r'
        }
        Input = qualifier['Input']
        if Input in InputStates:
            AudioInputModeCmdString = ValueStateValues[value].format(InputStates[Input])
            self.__SetHelper('AudioInputMode', AudioInputModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioInputMode')

    def SetAudioOutputMode(self, value, qualifier):

        ValueStateValues = {
            'Follow Port Selection': 'AUDSCAORG\r',
            'From Analog L/R Signal': 'AUDSCAANA\r'
        }
        AudioOutputModeCmdString = ValueStateValues[value]
        self.__SetHelper('AudioOutputMode', AudioOutputModeCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        TypeStates = {
            'IR Control': 'IR',
            'Key Control': 'KEY'
        }
        ValueStateValues = {
            'On': '{}ON\r',
            'Off': '{}OFF\r'
        }
        Type = qualifier['Type']
        if Type in TypeStates:
            ExecutiveModeCmdString = ValueStateValues[value].format(TypeStates[Type])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetExecutiveMode')

    def SetMatrixTieCommand(self, value, qualifier):

        InputStates = {
            'HDBT': '01',
            'HDMI1': '02',
            'HDMI2': '03',
            'HDMI3': '04',
            'HDMI4': '05',
            'VGA1': '06',
            'VGA2': '07',
            'VGA3': '08',
            'VGA4': '09',
            'YPBPR': '10',
            'AV': '11'
        }
        OutputStates = {
            'HDMI': '01',
            'HDBaseT': '02'
        }
        Input = qualifier['Input']
        Output = qualifier['Output']
        if Input in InputStates and Output in OutputStates:
            MatrixTieCommandCmdString = 'OUT{}FR{}\r'.format(OutputStates[Output], InputStates[Input])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixTieCommand')

    def SetOutputBypass(self, value, qualifier):

        ValueStateValues = {
            'On': 'OUTBYPON\r',
            'Off': 'OUTBYPOFF\r'
        }
        OutputBypassCmdString = ValueStateValues[value]
        self.__SetHelper('OutputBypass', OutputBypassCmdString, value, qualifier)

    def SetOutputMode(self, value, qualifier):

        ValueStateValues = {
            'Splitter': 'OUTSP\r',
            'Matrix': 'OUTMX\r'
        }
        OutputModeCmdString = ValueStateValues[value]
        self.__SetHelper('OutputMode', OutputModeCmdString, value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '1080P@50Hz': 'OUTRES01\r',
            '1080P@60Hz': 'OUTRES02\r',
            '720P@60Hz': 'OUTRES03\r',
            '720P@50Hz': 'OUTRES04\r',
            '1280x1024@60Hz': 'OUTRES05\r',
            '1024x768@60Hz': 'OUTRES06\r',
            '1360x768@60Hz': 'OUTRES07\r',
            '1440x900@60Hz': 'OUTRES08\r',
            '1680x1050@60Hz': 'OUTRES09\r'
        }
        OutputResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PON\r',
            'Off': 'POFF\r'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'STATUS\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:

            res = res.replace('\r\n', '\r').replace('\n', '\r')
            Lines = res.split('\r')
            try:

                Values = Lines[6].split()
                self.WriteStatus('Power', Values[0].title(), qualifier)
                self.WriteStatus('ExecutiveMode', Values[1].title(), {'Type': 'IR Control'})
                self.WriteStatus('ExecutiveMode', Values[2].title(), {'Type': 'Key Control'})
            except (IndexError, AttributeError):
                print('Invalid/unexpected response for UpdatePower')

            try:

                for Line in Lines[9:]:
                    if Line.strip():
                        Values = Line.split()
                        if 'HDMI' in Values[0]:
                            self.WriteStatus('AudioInputMode', 'HDMI' if Values[3] == 'Orginal' else 'Analog', {'Input': Values[0]})
                    else:
                        break
            except (IndexError, AttributeError):
                print('Invalid/unexpected response for UpdatePower')

            try:

                InputForOutput1 = Lines[16].split()[1].upper()

                InputForOutput2 = Lines[17].split()[1].upper()
                self.WriteStatus('OutputTieStatus', InputForOutput1, {'Output': 'HDMI'})
                self.WriteStatus('OutputTieStatus', InputForOutput2, {'Output': 'HDBaseT'})
                self.WriteStatus('InputTieStatus', 'Tied', {'Input': InputForOutput1, 'Output': 'HDMI'})
                self.WriteStatus('InputTieStatus', 'Tied', {'Input': InputForOutput2, 'Output': 'HDBaseT'})
                for a in self.Inputs ^ {InputForOutput1}:
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input': a, 'Output': 'HDMI'})
                for a in self.Inputs ^ {InputForOutput2}:
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input': a, 'Output': 'HDBaseT'})
            except (IndexError, AttributeError):
                print('Invalid/unexpected response for UpdatePower')

            try:

                Values = Lines[20].split()
                self.WriteStatus('AudioOutputMode', 'Follow Port Selection' if Values[0] == 'Orginal' else 'From Analog L/R Signal', qualifier)
                self.WriteStatus('ScalerVolume', int(Values[1]), qualifier)
                self.WriteStatus('OutputBypass', Values[3].title(), qualifier)
                self.WriteStatus('OutputResolution', Values[4], qualifier)
            except (IndexError, AttributeError, ValueError):
                print('Invalid/unexpected response for UpdatePower')

    def SetScalerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 30
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ScalerVolumeCmdString = 'AUD{:02}\r'.format(value)
            self.__SetHelper('ScalerVolume', ScalerVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetScalerVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if '[ERROR]' in response:
            print(response)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout).decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout).decode()
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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
