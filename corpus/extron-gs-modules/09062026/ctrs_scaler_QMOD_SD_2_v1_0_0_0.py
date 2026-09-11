from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Parameters': ['Program'], 'Status': {}},
            'AudioInput': {'Parameters': ['Program', 'Input'], 'Status': {}},
            'AutoResolution': {'Parameters': ['Program'], 'Status': {}},
            'BitrateMode': {'Parameters': ['Program'], 'Status': {}},
            'Channel': {'Status': {}},
            'ClosedCaption': {'Parameters': ['Program'], 'Status': {}},
            'Input': {'Parameters': ['Program'], 'Status': {}},
            'OutputResolution': {'Parameters': ['Program'], 'Status': {}},
            'ProgramChannel': {'Parameters': ['Program', 'Major', 'Minor'], 'Status': {}},
            'VideoBitrate': {'Parameters': ['Program'], 'Status': {}},
        }
        
    def SetAspectRatio(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }

        ValueStateValues = {
            '4:3': '0',
            '16:9': '1'
        }

        program = qualifier['Program']

        if program in ProgramStates and value in ValueStateValues:
            AspectRatioCmdString = '>{}ar={}\r\n'.format(ProgramStates[program], ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioInput(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        InputStates = {
            '1': 'fa',
            '2': 'fd'
        }
        input_ = qualifier['Input']

        ValueStateValues = {
            'None': '0',
            'Analog 1': '1',
            'Analog 2': '2',
            'SPDIF 1': '3',
            'SPDIF 2': '4',
            'SDI 1 - P1': '9',
            'SDI 1 - P2': '10',
            'SDI 1 - P3': '11',
            'SDI 1 - P4': '12',
            'SDI 1 - P5': '13',
            'SDI 1 - P6': '14',
            'SDI 1 - P7': '15',
            'SDI 1 - P8': '16',
            'SDI 2 - P1': '17',
            'SDI 2 - P2': '18',
            'SDI 2 - P3': '19',
            'SDI 2 - P4': '20',
            'SDI 2 - P5': '21',
            'SDI 2 - P6': '22',
            'SDI 2 - P7': '23',
            'SDI 2 - P8': '24'
        }

        if program in ProgramStates and input_ in InputStates and value in ValueStateValues:
            AudioInputCmdString = '>{}{}={}\r\n'.format(ProgramStates[program], InputStates[input_], ValueStateValues[value])
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def SetAutoResolution(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if program in ProgramStates and value in ValueStateValues:
            AutoResolutionCmdString = '>{}xa={}\r\n'.format(ProgramStates[program], ValueStateValues[value])
            self.__SetHelper('AutoResolution', AutoResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoResolution')

    def SetBitrateMode(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        ValueStateValues = {
            'Constant': '0',
            'Variable': '1'
        }

        if program in ProgramStates and value in ValueStateValues:
            BitrateModeCmdString = '>{}bm={}\r\n'.format(ProgramStates[program], ValueStateValues[value])
            self.__SetHelper('BitrateMode', BitrateModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBitrateMode')

    def SetChannel(self, value, qualifier):

        if 2 <= int(value) <= 135:
            ChannelCmdString = '>tc={}\r\n'.format(int(value))
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetClosedCaption(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        ValueStateValues = {
            'Video 1': '3',
            'Video 2': '4',
            'SDI 1': '9',
            'SDI 2': '10'
        }

        if program in ProgramStates and value in ValueStateValues:
            ClosedCaptionCmdString = '>{}cc={}\r\n'.format(ProgramStates[program], ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def SetInput(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        ValueStateValues = {
            'SDI 1': '9',
            'SDI 2': '10',
            'Video 1': '3',
            'Video 2': '4',
            'None': '0'
        }

        if program in ProgramStates and value in ValueStateValues and not (program == 'A' and value == 'None'):
            InputCmdString = '>{}x9={}\r\n'.format(ProgramStates[program], ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetOutputResolution(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        ValueStateValues = {
            '1080i': '0',
            '720p': '1',
            '480p': '2',
            '480i': '3'
        }

        if program in ProgramStates and value in ValueStateValues:
            OutputResolutionCmdString = '>{}x8={}\r\n'.format(ProgramStates[program], ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def SetProgramChannel(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        major = qualifier['Major']
        minor = qualifier['Minor']

        if program in ProgramStates and 0 <= int(major) <= 9999 and 0 <= int(minor) <= 999:
            ProgramChannelCmdString_Major = '>{}ta={}\r\n'.format(ProgramStates[program], int(major))
            ProgramChannelCmdString_Minor = '>{}ti={}\r\n'.format(ProgramStates[program], int(minor))
            self.__SetHelper('ProgramChannel', ProgramChannelCmdString_Major, value, qualifier)
            self.__SetHelper('ProgramChannel', ProgramChannelCmdString_Minor, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramChannel')

    def SetVideoBitrate(self, value, qualifier):

        ProgramStates = {
            'A': '1',
            'B': '2'
        }
        program = qualifier['Program']

        if program in ProgramStates and 4 <= value <= 20:
            VideoBitrateCmdString = '>{}f4={:.1f}\r\n'.format(ProgramStates[program], value)
            self.__SetHelper('VideoBitrate', VideoBitrateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoBitrate')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


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
