from extronlib.interface import SerialInterface, EthernetClientInterface

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
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PowerOff': {'Status': {}},
            'RepeatThisAB': {'Parameters': ['Repeat Number'], 'Status': {}},
            'RepeatThisChapter': {'Parameters': ['Repeat Number'], 'Status': {}},
            'RepeatThisTitle': {'Parameters': ['Repeat Number'], 'Status': {}},
            'SetAPoint': {'Status': {}},
            'SetBPoint': {'Status': {}},
            'Transport': {'Status': {}},
            'VideoMute': {'Status': {}}
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x24',
            'Off': b'\x25'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        MuteValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = b'\xD7'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                mute = '{0:08b}'.format(res[1])
                mute_value = MuteValues[mute[3]]
                self.WriteStatus('AudioMute', mute_value, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

            try:
                mute2 = '{0:08b}'.format(res[1])
                mute2_value = MuteValues[mute2[2]]
                self.WriteStatus('VideoMute', mute2_value, None)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

            try:

                transport = res[3]
                if transport == 128:
                    self.WriteStatus('Transport', 'Play', None)
                elif transport == 16:
                    self.WriteStatus('Transport', 'Stop', None)
                elif transport == 2:
                    self.WriteStatus('Transport', 'Record', None)
                else:
                    if res[4] == 128:
                        self.WriteStatus('Transport', 'Pause', None)
            except (IndexError):
                print('Invalid/unexpected response')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xD8\x94',
            'Off': b'\xD8\x95'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ExecutiveModeCmdString = b'\xB0'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                mode = '{0:08b}'.format(res[4])
                self.WriteStatus('ExecutiveMode', ValueStateValues[mode[2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\xD8\x98'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xD9\xC0',
            'Enter': b'\xD9\xC2',
            'Up': b'\xD9\xC3',
            'Down': b'\xD9\xC4',
            'Left': b'\xD9\xC5',
            'Right': b'\xD9\xC6'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = b'\xD8\xC9'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetRepeatThisAB(self, value, qualifier):

        RepeatNumber = int(qualifier['Repeat Number'])
        if 1 <= RepeatNumber <= 99:
            RepeatThisABCmdString = '\xD9\x94{0:02d}\x40'.format(RepeatNumber)
            self.__SetHelper('RepeatThisAB', RepeatThisABCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRepeatThisAB')

    def SetRepeatThisChapter(self, value, qualifier):

        RepeatNumber = int(qualifier['Repeat Number'])
        if 1 <= RepeatNumber <= 99:
            RepeatThisChapterCmdString = '\xD9\x93{0:02d}\x40'.format(RepeatNumber)
            self.__SetHelper('RepeatThisChapter', RepeatThisChapterCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRepeatThisChapter')

    def SetRepeatThisTitle(self, value, qualifier):

        RepeatNumber = int(qualifier['Repeat Number'])
        if 1 <= RepeatNumber <= 99:
            RepeatThisTitleCmdString = '\xD9\x92{0:02d}\x40'.format(RepeatNumber)
            self.__SetHelper('RepeatThisTitle', RepeatThisTitleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRepeatThisTitle')

    def SetSetAPoint(self, value, qualifier):

        SetAPointCmdString = '\xD9\x95'
        self.__SetHelper('SetAPoint', SetAPointCmdString, value, qualifier)

    def SetSetBPoint(self, value, qualifier):

        SetBPointCmdString = '\xD9\x96'
        self.__SetHelper('SetBPoint', SetBPointCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'FWD Play': b'\x3A',
            'FWD Fast': b'\x3B',
            'Stop': b'\x3F',
            'REV Play': b'\x4A',
            'REV Fast': b'\x4B',
            'Pause': b'\x4F',
            'Fast Forward': b'\xAB',
            'Rewind': b'\xAC',
            'Record': b'\xCA',
            'Record Pause': b'\xCB',
            'Eject': b'\xA3',
            'Record Stop': b'\xD8\xCD'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        
    def UpdateTransport(self, value, qualifier):
        self.UpdateAudioMute(value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x27',
            'Off': b'\x26'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        
    def UpdateVideoMute(self, value, qualifier):
        self.UpdateAudioMute(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            for rep in response:
                if int(rep) == 11:
                    print('{0} : Transmission Error Occurred'.format(sourceCmdName))
                    response = ''
                    return response
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=1)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        CommandLength = {
            'AudioMute': 5,
            'ExecutiveMode': 6,
        }

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=CommandLength[command])
            if not res:
                return b''
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
