from extronlib.interface import EthernetClientInterface


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Cue': {'Status': {}},
            'DMX': {'Status': {}},
            'MasterFade': {'Status': {}},
            'MasterIntensity': {'Status': {}},
            'MasterRate': {'Status': {}},
            'PlaybackIntensity': {'Status': {}},
            'PlaybackRate': {'Status': {}},
            'ReleasePlayback': {'Status': {}},
            'StopRecording': {'Status': {}},
            'Timer': {'Status': {}},
            'Track': {'Status': {}},
        }

    def SetCue(self, value, qualifier):

        PlaybackStates = ['1', '2', '3', '4', '5', '6']

        ValueConstraints = {
            'Min': 1,
            'Max': 32
        }

        playback_val = qualifier['Playback']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and playback_val in PlaybackStates:
            CueCmdString = 'core-pb-{0}-jump={1}'.format(playback_val, value)
            self.__SetHelper('Cue', CueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCue')

    def SetDMX(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 512
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and ChannelConstraints['Min'] <= channel_val <= ChannelConstraints['Max']:
            DMXCmdString = 'core-dmx-{0}={1}'.format(channel_val, value)
            self.__SetHelper('DMX', DMXCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDMX')

    def SetMasterFade(self, value, qualifier):

        time_string = qualifier['Time']
        if time_string:
            MasterFadeCmdString = 'core-pb-fade={0}'.format(time_string)
            self.__SetHelper('MasterFade', MasterFadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterFade')

    def SetMasterIntensity(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterIntensityCmdString = 'core-pb-intensity={0:.2f}'.format(value)
            self.__SetHelper('MasterIntensity', MasterIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterIntensity')

    def SetMasterRate(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterRateCmdString = 'core-pb-rate={0:.2f}'.format(value)
            self.__SetHelper('MasterRate', MasterRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterRate')

    def SetPlaybackIntensity(self, value, qualifier):

        PlaybackStates = ['1', '2', '3', '4', '5', '6']

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        playback_val = qualifier['Playback']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and playback_val in PlaybackStates:
            PlaybackIntensityCmdString = 'core-pb-{0}-intensity={1:.2f}'.format(playback_val, value)
            self.__SetHelper('PlaybackIntensity', PlaybackIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaybackIntensity')

    def SetPlaybackRate(self, value, qualifier):

        PlaybackStates = ['1', '2', '3', '4', '5', '6']

        ValueConstraints = {
            'Min': -100,
            'Max': 100
        }

        playback_val = qualifier['Playback']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and playback_val in PlaybackStates:
            PlaybackRateCmdString = 'core-pb-{0}-rate={1:.2f}'.format(playback_val, value)
            self.__SetHelper('PlaybackRate', PlaybackRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaybackRate')

    def SetReleasePlayback(self, value, qualifier):

        ValueStateValues = ['1', '2', '3', '4', '5', '6']

        ReleasePlaybackCmdString = ''
        if value == 'All':
            ReleasePlaybackCmdString = 'core-pb-release'
        elif value in ValueStateValues:
            ReleasePlaybackCmdString = 'core-pb-{0}-release'.format(value)
        if ReleasePlaybackCmdString:
            self.__SetHelper('ReleasePlayback', ReleasePlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleasePlayback')

    def SetStopRecording(self, value, qualifier):

        StopRecordingCmdString = 'core-tr-stop'
        self.__SetHelper('StopRecording', StopRecordingCmdString, value, qualifier)

    def SetTimer(self, value, qualifier):

        NumberStates = ['1', '2', '3', '4']

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop',
            'Restart': 'restart',
            'Pause': 'pause'
        }

        timer_val = qualifier['Number']
        if timer_val in NumberStates:
            TimerCmdString = 'core-tm-{0}-{1}'.format(timer_val, ValueStateValues[value])
            self.__SetHelper('Timer', TimerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimer')

    def SetTrack(self, value, qualifier):

        ValueStateValues = {
            'Erase': 'erase',
            'Record': 'record'
        }

        track_num = qualifier['Number']
        if 1 <= int(track_num) <= 128:
            TrackCmdString = 'core-tr-{0}-{1}'.format(track_num, ValueStateValues[value])
            self.__SetHelper('Track', TrackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrack')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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