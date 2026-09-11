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
            'AudioMute': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Finalize': {'Status': {}},
            'Format': {'Status': {}},
            'Freeze': {'Status': {}},
            'FrontPanelLock': {'Status': {}},
            'Transport': {'Status': {}},
            'MemorySearch': {'Status': {}},
            'Playback': {'Status': {}},
            'PowerOff': {'Status': {}},
            'Repeat': {'Status': {}},
            'VideoMute': {'Status': {}}
        }

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': b'\x24',
            'Off': b'\x25'
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        res = self.__UpdateHelper('AudioMute', b'\xD7', value, qualifier)
        if res:

            try:
                if res[1] & 16 == 16:
                    self.WriteStatus('AudioMute', 'On', qualifier)
                else:
                    self.WriteStatus('AudioMute', 'Off', qualifier)
            except (IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

            try:

                if res[1] & 32 == 32:
                    self.WriteStatus('VideoMute', 'On', qualifier)
                else:
                    self.WriteStatus('VideoMute', 'Off', qualifier)
            except (IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

            try:

                if res[3] & 128 == 128:
                    self.WriteStatus('Transport', 'Play', qualifier)

                elif res[3] & 16 == 16:
                    self.WriteStatus('Transport', 'Stop', qualifier)

                elif res[3] & 2 == 2:
                    self.WriteStatus('Transport', 'Record', qualifier)

                elif res[3] & 4 == 4:
                    self.WriteStatus('Transport', 'Eject', qualifier)

                elif res[4] & 128 == 128:
                    self.WriteStatus('Transport', 'Pause', qualifier)
            except (IndexError):
                print('Invalid/Unexpected Response for UpdateAudioMute')

    def UpdateDeviceStatus(self, value, qualifier):

        res = self.__UpdateHelper('DeviceStatus', b'\x67', value, qualifier)
        if res:
            try:

                if res[0] & 1 == 1:
                    self.WriteStatus('DeviceStatus', 'Error', qualifier)

                elif res[0] & 8 == 8:
                    self.WriteStatus('DeviceStatus', 'No Disc', qualifier)
                else:
                    self.WriteStatus('DeviceStatus', 'Normal', qualifier)

            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetFinalize(self, value, qualifier):

        self.__SetHelper('Finalize', b'\xD9', value, qualifier)
        self.__SetHelper('Finalize', b'\x9F', value, qualifier)

    def SetFormat(self, value, qualifier):

        self.__SetHelper('Format', b'\xFA', value, qualifier)
        self.__SetHelper('Format', b'\xD9', value, qualifier)
        self.__SetHelper('Format', b'\xCF', value, qualifier)

    def SetFreeze(self, value, qualifier):

        self.__SetHelper('Freeze', b'\xD8', value, qualifier)
        self.__SetHelper('Freeze', b'\x98', value, qualifier)
        self.__SetHelper('Freeze', b'\x30', value, qualifier)

    def SetFrontPanelLock(self, value, qualifier):

        States = {
            'On': b'\x94',
            'Off': b'\x95'
        }

        self.__SetHelper('FrontPanelLock', b'\xD8', value, qualifier)
        self.__SetHelper('FrontPanelLock', States[value], value, qualifier)

    def UpdateFrontPanelLock(self, value, qualifier):

        res = self.__UpdateHelper('FrontPanelLock', b'\xB0', value, qualifier)
        if res:
            try:

                if res[4] & 2**5 == 2**5:
                    self.WriteStatus('FrontPanelLock', 'On', qualifier)
                else:
                    self.WriteStatus('FrontPanelLock', 'Off', qualifier)

            except (IndexError):
                print('Invalid/Unexpected Response for UpdateFrontPanelLock')

    def SetTransport(self, value, qualifier):

        Mode = self.ReadStatus('Transport', qualifier)

        if value == 'Play':
            self.__SetHelper('Transport', b'\x3A', value, qualifier)

        elif value == 'Stop':
            if Mode == 'Record':
                self.__SetHelper('Transport', b'\xD8', value, qualifier)
                self.__SetHelper('Transport', b'\xCD', value, qualifier)
            else:
                self.__SetHelper('Transport', b'\x3F', value, qualifier)

        elif value == 'Pause':
            if Mode == 'Record':
                self.__SetHelper('Transport', b'\xCB', value, qualifier)
            else:
                self.__SetHelper('Transport', b'\x4F', value, qualifier)

        elif value == 'Record':
            self.__SetHelper('Transport', b'\xFA', value, qualifier)
            self.__SetHelper('Transport', b'\xCA', value, qualifier)

        elif value == 'Eject':
            self.__SetHelper('Transport', b'\xA3', value, qualifier)

        elif value == 'Close Tray':
            self.__SetHelper('Transport', b'\xD8', value, qualifier)
            self.__SetHelper('Transport', b'\xCA', value, qualifier)


    def SetMemorySearch(self, value, qualifier):

        self.__SetHelper('MemorySearch', b'\x5B', value, qualifier)

    def SetPlayback(self, value, qualifier):

        States = {
            'Reverse': b'\x4A',
            'Reverse Step': b'\x4D',
            'Reverse Slow': b'\x4C',
            'Reverse Fast': b'\x4B',
            'Reverse 10x': b'\x4E',
            'Forward': b'\x3A',
            'Forward Step': b'\x3D',
            'Forward Slow': b'\x3C',
            'Forward Fast': b'\x3B',
            'Forward 10x': b'\x3E'
        }

        self.__SetHelper('Playback', States[value], value, qualifier)

    def SetPowerOff(self, value, qualifier):

        self.__SetHelper('PowerOff', b'\xD8', value, qualifier)
        self.__SetHelper('PowerOff', b'\xC9', value, qualifier)

    def SetRepeat(self, value, qualifier):

        States = {
            'Title': b'\x92',
            'Chapter': b'\x93',
            'A/B': b'\x94',
            'Time': b'\x91'
        }

        self.__SetHelper('Repeat', b'\xD9', value, qualifier)
        self.__SetHelper('Repeat', States[value], value, qualifier)

    def UpdateRepeat(self, value, qualifier):

        res = self.__UpdateHelper('Repeat', b'\x67', value, qualifier)
        if res:
            try:

                if res[1] & 4 == 4:
                    self.WriteStatus('Repeat', 'A/B', qualifier)

                elif res[1] & 32 == 32:
                    self.WriteStatus('Repeat', 'Time', qualifier)

                elif res[1] & 64 == 64:
                    self.WriteStatus('Repeat', 'Chapter', qualifier)

                elif res[1] & 128 == 128:
                    self.WriteStatus('Repeat', 'Title', qualifier)

            except (IndexError):
                print('Invalid/Unexpected Response for UpdateRepeat')

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': b'\x26',
            'Off': b'\x27'
        }

        self.__SetHelper('VideoMute', States[value], value, qualifier)

    def __CheckResponseForErrors(self, command, response):

        if command == 'AudioMute':
            if response[0] & 1 == 1:
                print('Error in Status Sense response')
                response = ''
        if response == b'\x0B':
            print('Error : NAK')
        elif response == b'\x05':
            print('Error : Not Target')
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=5)
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
