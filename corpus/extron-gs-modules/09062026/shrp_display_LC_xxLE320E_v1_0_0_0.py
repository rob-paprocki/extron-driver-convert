from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogTVDirectCommand'		: {'Status': {}},
            'AnalogTVStep'				: {'Status': {}},
            'AspectRatio'				: {'Status': {}},
            'AudioMute'					: {'Status': {}},
            'AVMode'					: {'Status': {}},
            'DTVDirectStep'				: {'Status': {}},
            'DTVFourDigitDirectCommand'	: {'Status': {}},
            'DTVThreeDigitDirectCommand': {'Status': {}},
            'Input'						: {'Status': {}},
            'Power'						: {'Status': {}},
            'Volume'					: {'Status': {}}
        }


    def SetAnalogTVStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'CHUP    \r',
            'Down': 'CHDW    \r'
        }

        AnalogTVStepCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogTVStep', AnalogTVStepCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Normal': '2',
            'Zoom 1': '3',
            'Zoom 2': '4',
            'Wide': '5',
            'Full Screen': '6',
            '4:3': '7'
        }

        AspectRatioCmdString = 'WIDE{0}   \r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '2'
        }

        AudioMuteCmdString = 'MUTE{0}   \r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAVMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': '1',
            'Movie': '2',
            'Eco': '3',
            'Personal': '4',
            'Standard': '5'
        }

        AVModeCmdString = 'AVMD{0}   \r'.format(ValueStateValues[value])
        self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)

    def SetDTVDirectStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'DTUP    \r',
            'Down': 'DTDW    \r'
        }

        DTVDirectStepCmdString = ValueStateValues[value]
        self.__SetHelper('DTVDirectStep', DTVDirectStepCmdString, value, qualifier)

    def SetDTVThreeDigitDirectCommand(self, value, qualifier):
        if value:
            if 1 <= int(value) <= 999:
                DTVThreeDigitDirectCommandCmdString = 'DTVD{0:03d} \r'.format(int(value))
                self.__SetHelper('DTVThreeDigitDirectCommand', DTVThreeDigitDirectCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVThreeDigitDirectCommand')

    def SetDTVFourDigitDirectCommand(self, value, qualifier):
        if value:
            if 1 <= int(value) <= 9999:
                DTVFourDigitDirectCommandCmdString = 'DTVD{0:04d}\r'.format(int(value))
                self.__SetHelper('DTVFourDigitDirectCommand', DTVFourDigitDirectCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVFourDigitDirectCommand')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': 'ITVD    \r',
            'DTV': 'IDTV    \r',
            'SCART': 'IAVD1   \r',
            'YPbPr': 'IAVD3   \r',
            'AV': 'IAVD4   \r',
            'HDMI 1': 'IAVD5   \r',
            'HDMI 2': 'IAVD6   \r',
            'HDMI 3': 'IAVD7   \r',
            'PC': 'IAVD8   \r',
            'Y/C (SCART)': 'INP10   \r',
            'CVBS (SCART)': 'INP11   \r',
            'RGB (SCART)': 'INP12   \r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'POWR1   \r',
            'Off': 'POWR0   \r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetAnalogTVDirectCommand(self, value, qualifier):

        if value:
            if 1 <= int(value) <= 99:
                AnalogTVDirectCommandCmdString = 'DCCH{0:02}  \r'.format(int(value))
                self.__SetHelper('AnalogTVDirectCommand', AnalogTVDirectCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetAnalogTVDirectCommand')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value == 100:
                VolumeCmdString = 'VOLM100 \r'
            else:
                VolumeCmdString = 'VOLM{0:02d}  \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'ERR\r': "Communication Error or Incorrect Command"}
        if response:
            if response in DEVICE_ERROR_CODES:
                print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        res = self.SendAndWait(commandstring, 1, deliTag='\r').decode()
        if not res:
            print('No Response')
            print('Invalid/unexpected response')
        else:
            res = self.__CheckResponseForErrors(command, res)

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