from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.DeviceID = '1'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioChannel': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PlayFolder': {'Status': {}},
            'PowerToggle': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            DeviceID = '00'
        if 0 <= int(value) <= 99:
            self._DeviceID = '@' + value.zfill(2)
        else:
            print("DeviceID value should be in range '01' - '99' or Broadcast.")

    def SetAudioChannel(self, value, qualifier):
        AudioChannelCmdString = self._DeviceID + ':AUDIO$'
        self.__SetHelper('AudioChannel', AudioChannelCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'OK': ':OK$',
            'Up': ':UP$',
            'Left': ':LEFT$',
            'Down': ':DOWN$',
            'Right': ':RIGHT$',
            'Enter': ':ENTER$'
        }
        MenuNavigationCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = self._DeviceID + ':MUTE$'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPlayFolder(self, value, qualifier):

        FolderConstraints = {
            'Min': 0,
            'Max': 99
        }
        if FolderConstraints['Min'] <= int(value) <= FolderConstraints['Max']:
            PlayFolderCmdString = ''.join([self._DeviceID, ':', value, '$'])
            self.__SetHelper('PlayFolder', PlayFolderCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPlayFolder')

    def SetPowerToggle(self, value, qualifier):

        PowerToggleCmdString = self._DeviceID + ':POWER$'
        self.__SetHelper('PowerToggle', PowerToggleCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Reverse': ':REV$',
            'Fast Forward': ':FWD$',
            'Stop': ':STOP$',
            'Previous File': ':PREV$',
            'Next File': ':NEXT$',
            'Repeat': ':REP$',
            'Replay File': ':SYNC$',
            'Pause': ':PAUSE$'
        }
        TransportCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': ':VOL+$',
            'Down': ':VOL-$'
        }
        VolumeCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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
