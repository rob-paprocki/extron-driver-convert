from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import json

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
            'BandwidthMode': {'Parameters':['Source'], 'Status': {}},
            'BandwidthTarget': {'Parameters':['Source'], 'Status': {}},
            'ChromaThreshold': {'Parameters':['Source'], 'Status': {}},
            'Chrominance': {'Parameters':['Source'], 'Status': {}},
            'DeviceType': {'Parameters':['Device'], 'Status': {}},
            'FrameRateDropPercentage': {'Parameters':['Source'], 'Status': {}},
            'Lock': {'Parameters':['Source'], 'Status': {}},
            'Luminance': {'Parameters':['Source'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Source','Display','Tie Type'], 'Status': {}},
            'Motion': {'Parameters':['Source'], 'Status': {}},
            'MouseKeyboardMode': {'Parameters':['Source'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Display'], 'Status': {}},
            'OutputTieStatusRefresh': { 'Status': {}},
            'PlaybackPresetRecall': { 'Status': {}},
            'PresetRecallbyName': {'Parameters':['Name'], 'Status': {}},
            'RecordingPresetRecall': { 'Status': {}},
            'Refresh': {'Parameters':['Source'], 'Status': {}},
            'SourceStatus': {'Parameters':['Source'], 'Status': {}},
            'SwitchingPresetRecall': { 'Status': {}},
            'Temporal': {'Parameters':['Source'], 'Status': {}},
            'Threshold': {'Parameters':['Source'], 'Status': {}},
            'Transform': {'Parameters':['Source'], 'Status': {}},
            'RecordingPresetPlaybackStatus': {'Parameters':['Source','Preset Name'], 'Status': {}},
            'RecordingPresetPlaybackDurationStatus': {'Parameters':['Source','Preset Name'], 'Status': {}},
            'RecordingPresetRecordingStatus': {'Parameters':['Source','Preset Name'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.regex = re.compile('\"(\w*)\"\r')
            self.bandwidth_target_pattern = re.compile('\"(\d*).(\d*)\"\r')
            self.source_status_pattern = re.compile('{\"name\":\"(\w*)\",\"source_status\":(\"active\"|null|\"unplugged\")}')
            self.position_timecode_pattern = re.compile('\"(ts_position_timecode|position_timecode)\":\"(\d\d:\d\d:\d\d:\d\d)\"')
            self.duration_timecode_pattern = re.compile('\"(ts_duration_timecode|duration_timecode)\":\"(\d\d:\d\d:\d\d:\d\d)\"')
            self.recording_status_pattern = re.compile('"recordstate":"(disable|enable)"')

    def SetBandwidthMode(self, value, qualifier):

        ValueStateValues = {
            'Flow Rate Peak'   : 'flowratePeak', 
            'Flow Rate Shared' : 'flowrateShared', 
            'Manual Drop'      : 'manualdrop', 
            'PBR-F'            : 'variableCompressionRate', 
            'PBR-F (FD)'       : 'variableCompressionRateFD', 
            'None'             : 'none'
        }

        if qualifier['Source']:
            BandwidthModeCmdString = 'set device {0} videoport 0 bandwidthMode {1}\r\n'.format(qualifier['Source'], ValueStateValues[value])
            self.__SetHelper('BandwidthMode', BandwidthModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBandwidthMode')

    def UpdateBandwidthMode(self, value, qualifier):

        ValueStateValues = {
            'flowratePeak'              : 'Flow Rate Peak',
            'flowrateShared'            : 'Flow Rate Shared',
            'manualdrop'                : 'Manual Drop',
            'variableCompressionRate'   : 'PBR-F',
            'variableCompressionRateFD' : 'PBR-F (FD)',
            'none'                      : 'None'
        }

        if qualifier['Source']:
            BandwidthModeCmdString = 'get device {0} videoport 0 bandwidthMode\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('BandwidthMode', BandwidthModeCmdString, value, qualifier)
            if res:
                match = re.match(self.regex, res)
                try:
                    value = ValueStateValues[match.group(1)]
                    self.WriteStatus('BandwidthMode', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['BandwidthMode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBandwidthMode')

    def SetBandwidthTarget(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 200
            }

        if qualifier['Source'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BandwidthTargetCmdString = 'set device {0} videoport 0 bandwidthTarget {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('BandwidthTarget', BandwidthTargetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBandwidthTarget')

    def UpdateBandwidthTarget(self, value, qualifier):

        if qualifier['Source']:
            BandwidthTargetCmdString = 'get device {0} videoport 0 bandwidthTarget\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('BandwidthTarget', BandwidthTargetCmdString, value, qualifier)
            if res:
                match = re.match(self.bandwidth_target_pattern, res)
                try:
                    value = int(match.group(1))
                    self.WriteStatus('BandwidthTarget', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['BandwidthTarget: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBandwidthTarget')

    def SetChromaThreshold(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if qualifier['Source']:
            ChromaThresholdCmdString = 'set device {0} videoport 0 chromaThreshold {1}\r\n'.format(qualifier['Source'],ValueStateValues[value])
            self.__SetHelper('ChromaThreshold', ChromaThresholdCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChromaThreshold')

    def UpdateChromaThreshold(self, value, qualifier):

        ValueStateValues = {
            1 : 'Enable',
            0 : 'Disable'
        }

        if qualifier['Source']:
            ChromaThresholdCmdString = 'get device {0} videoport 0 chromaThreshold\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('ChromaThreshold', ChromaThresholdCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[int(res)]
                    self.WriteStatus('ChromaThreshold', value, qualifier)
                except (KeyError, ValueError):
                    self.Error(['ChromaThreshold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateChromaThreshold')

    def SetChrominance(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 11
            }

        if qualifier['Source'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ChrominanceCmdString = 'set device {0} videoport 0 chrominance {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('Chrominance', ChrominanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChrominance')

    def UpdateChrominance(self, value, qualifier):

        if qualifier['Source']:
            ChrominanceCmdString = 'get device {0} videoport 0 chrominance\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Chrominance', ChrominanceCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('Chrominance', value, qualifier)
                except ValueError:
                    self.Error(['Chrominance: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateChrominance')

    def SetDeviceType(self, value, qualifier):

        ValueStateValues = {
            'Source'  : 'createsource',
            'Display' : 'createdisplay'
        }

        if qualifier['Device']:
            DeviceTypeCmdString = '{0} {1}\r\n'.format(ValueStateValues[value], qualifier['Device'])
            self.__SetHelper('DeviceType', DeviceTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceType')
    def SetFrameRateDropPercentage(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 99
            }

        if qualifier['Source'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FrameRateDropPercentageCmdString = 'set device {0} videoport 0 frameDropPercentage {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('FrameRateDropPercentage', FrameRateDropPercentageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFrameRateDropPercentage')

    def UpdateFrameRateDropPercentage(self, value, qualifier):

        if qualifier['Source']:
            FrameRateDropPercentageCmdString = 'get device {0} videoport 0 frameDropPercentage\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('FrameRateDropPercentage', FrameRateDropPercentageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('FrameRateDropPercentage', value, qualifier)
                except ValueError:
                    self.Error(['FrameRateDropPercentage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFrameRateDropPercentage')

    def SetLock(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 'enable',
            'Disable' : 'disable'
        }

        if qualifier['Source']:
            LockCmdString = 'set device {0} videoport 0 lock {1}\r\n'.format(qualifier['Source'],ValueStateValues[value])
            self.__SetHelper('Lock', LockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLock')

    def UpdateLock(self, value, qualifier):

        ValueStateValues = {
            'enable'  : 'Enable',
            'disable' : 'Disable'
        }

        if qualifier['Source']:
            LockCmdString = 'get device {0} videoport 0 lock\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Lock', LockCmdString, value, qualifier)
            if res:
                match = re.match(self.regex, res)
                try:
                    value = ValueStateValues[match.group(1)]
                    self.WriteStatus('Lock', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Lock: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLock')

    def SetLuminance(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 10
            }

        if qualifier['Source'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LuminanceCmdString = 'set device {0} videoport 0 luminance {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('Luminance', LuminanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLuminance')

    def UpdateLuminance(self, value, qualifier):

        if qualifier['Source']:
            LuminanceCmdString = 'get device {0} videoport 0 luminance\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Luminance', LuminanceCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('Luminance', value, qualifier)
                except ValueError:
                    self.Error(['Luminance: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLuminance')

    def SetMatrixTieCommand(self, value, qualifier):

        MatrixTieTypeValues = {
            'Video' : ' streams=v',
            'Audio/Video' : ' streams=a,v',
            'Audio/Video and Data' : ' streams=a,v,d',
            'Audio' : ' streams=a',
            'Data' : ' streams=d',
            }

        source = qualifier['Source']
        display = qualifier['Display']
        tieType = MatrixTieTypeValues[qualifier['Tie Type']]

        if source.upper() == 'NONE':
            source = 'none'

        if display.upper() == 'NONE':
            display = 'none'

        if source and display:
            MatrixTieCmdString = 'connect {0} {1}{2}\r\n'.format(source, display, tieType)
            self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')
    def SetMotion(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 15
            }

        if qualifier['Source'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MotionCmdString = 'set device {0} videoport 0 motion {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('Motion', MotionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotion')

    def UpdateMotion(self, value, qualifier):

        if qualifier['Source']:
            MotionCmdString = 'get device {0} videoport 0 motion\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Motion', MotionCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('Motion', value, qualifier)
                except ValueError:
                    self.Error(['Motion: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMotion')

    def SetMouseKeyboardMode(self, value, qualifier):

        ValueStateValues = {
            'Enable' : 'enable',
            'Disable' : 'disable'
        }

        if qualifier['Source']:
            MouseKeyboardModeCmdString = 'set device {0} MKMode {1}\r\n'.format(qualifier['Source'],ValueStateValues[value])
            self.__SetHelper('MouseKeyboardMode', MouseKeyboardModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMouseKeyboardMode')

    def UpdateMouseKeyboardMode(self, value, qualifier):

        ValueStateValues = {
            'enable' : 'Enable',
            'disable' : 'Disable'
        }

        if qualifier['Source']:
            MouseKeyboardModeCmdString = 'get device {0} MKMode\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('MouseKeyboardMode', MouseKeyboardModeCmdString, value, qualifier)
            if res:
                match = re.match(self.regex, res)
                try:
                    value = ValueStateValues[match.group(1)]
                    self.WriteStatus('MouseKeyboardMode', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['MouseKeyboardMode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMouseKeyboardMode')

    def SetOutputTieStatusRefresh(self, value, qualifier):

        OutputTieStatusCmdString = 'getdevices keys=name,source_device where=\"type=\'display\'\"\r\n' # get ties for all displays where display names are tied to source ID's
        res = self.__SetHelper('OutputTieStatusRefresh', OutputTieStatusCmdString, value, qualifier)
        if res:
            try:
                tieData = {}
                for tie in json.loads(res):
                    tieData[tie['name']] = tie['source_device']
            except Exception:
                self.Error(['Get ties for Output Tie Status: Invalid/unexpected response'])

            else:
                OutputTieStatusCmdString = 'getdevices keys=name,device_id\r\n' # get all source names and ID's to lookup source name based on source ID from first query
                res = self.__SetHelper('OutputTieStatusRefresh', OutputTieStatusCmdString, value, qualifier)
                if res:
                    try:
                        sourceData = {}
                        for source in json.loads(res):
                            sourceData[source['device_id']] = source['name']

                        for displayName in tieData:
                            try:
                                self.WriteStatus('OutputTieStatus', sourceData[tieData[displayName]], {'Display': displayName})
                            except KeyError:
                                self.WriteStatus('OutputTieStatus', 'None', {'Display': displayName})
                    except Exception:
                        self.Error(['Get sources for Output Tie Status: Invalid/unexpected response'])

    def SetPlaybackPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 50
            }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PlaybackPresetRecallCmdString = 'presetload playback_preset{0}\r\n'.format(value)
            self.__SetHelper('PlaybackPresetRecall', PlaybackPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaybackPresetRecall')
    def SetPresetRecallbyName(self, value, qualifier):

        name = qualifier['Name']
        if name:
            PresetRecallbyNameCmdString = 'presetlaunch {0}\r\n'.format(name)
            self.__SetHelper('PresetRecallbyName', PresetRecallbyNameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallbyName')
    def UpdateRecordingPresetPlaybackStatus(self, value, qualifier):

        Preset = qualifier['Preset Name']
        Source = qualifier['Source']
        if Preset and Source:
            CmdString = 'presetgetplayerstatus {0} {1}\r\n'.format(Preset, Source)
            res = self.__UpdateHelper('RecordingPresetPlaybackStatus', CmdString, value, qualifier)
            if res:
                try:
                    res = res[:30]
                    if 'STOP' in res:
                        self.WriteStatus('RecordingPresetPlaybackStatus', 'Stopped', qualifier)
                    elif 'PLAY' in res:
                        self.WriteStatus('RecordingPresetPlaybackStatus', 'Playing', qualifier)
                    elif 'PAUSE' in res:
                        self.WriteStatus('RecordingPresetPlaybackStatus', 'Paused', qualifier)
                except IndexError:
                    self.Error(['RecordingPresetPlaybackStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecordingPresetPlaybackStatus')

    def UpdateRecordingPresetPlaybackDurationStatus(self, value, qualifier):

        Preset = qualifier['Preset Name']
        Source = qualifier['Source']
        if Preset and Source:
            CmdString = 'presetgetplayerstatus {0} {1}\r\n'.format(Preset, Source)
            res = self.__UpdateHelper('RecordingPresetPlaybackStatus', CmdString, value, qualifier)
            if res:
                try:
                    Position = re.search(self.position_timecode_pattern, res)
                    Duration = re.search(self.duration_timecode_pattern, res)
                    if Position and Duration:
                        String = '{} / {}'.format(Position.group(2),Duration.group(2))
                        self.WriteStatus('RecordingPresetPlaybackDurationStatus', String, qualifier)
                except (IndexError, AttributeError):
                    self.Error(['RecordingPresetPlaybackDurationStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecordingPresetPlaybackDurationStatus')

    def UpdateRecordingPresetRecordingStatus(self, value, qualifier):

        Preset = qualifier['Preset Name']
        Source = qualifier['Source']

        record_values = {
            'enable' : 'Enabled',
            'disable' : 'Disabled'
        }

        if Preset and Source:
            CmdString = 'presetgetrecorderstatus {0} {1}\r\n'.format(Preset, Source)
            res = self.__UpdateHelper('RecordingPresetRecordingStatus', CmdString, value, qualifier)
            if res:
                match = self.recording_status_pattern.search(res)
                try:
                    self.WriteStatus('RecordingPresetRecordingStatus', record_values[match.group(1)], qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['RecordingPresetRecordingStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRecordingPresetRecordingStatus')

    def SetRecordingPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 50
            }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            RecordingPresetRecallCmdString = 'presetload recording_preset{0}\r\n'.format(value)
            self.__SetHelper('RecordingPresetRecall', RecordingPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordingPresetRecall')
    def SetRefresh(self, value, qualifier):

        if qualifier['Source']:
            RefreshCmdString = 'set device {0} videoport 0 refresh {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('Refresh', RefreshCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRefresh')

    def UpdateRefresh(self, value, qualifier):

        if qualifier['Source']:
            RefreshCmdString = 'get device {0} videoport 0 refresh\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Refresh', RefreshCmdString, value, qualifier)
            if res:
                try:
                    if res[:1] == '"' and res[-2:] == '"\r':
                        value = res[1:-2]
                    elif res[-1:] == '\r':
                        value = res[:-1]
                    else:
                        value = ''
                    if value in ['0.25', '0.5', '1', '2', '5', '10']:
                        self.WriteStatus('Refresh', value, qualifier)
                    else:
                        self.Error(['Refresh: Invalid/unexpected response'])
                except (KeyError, IndexError):
                    self.Error(['Refresh: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRefresh')

    def UpdateSourceStatus(self, value, qualifier):

        ValueStateValues = {
            '"active"' : 'Active',
            '"unplugged"' : 'Unplugged',
            'null' : 'Null'
        }

        source = qualifier['Source']
        if source:
            SourceStatusCmdString = 'getdevices keys=name,source_status\r\n'
            res = self.__UpdateHelper('SourceStatus', SourceStatusCmdString, value, qualifier)
            if res:
                try:
                    match = re.findall(self.source_status_pattern, res)
                    value = ValueStateValues[dict(match)[source]]
                    self.WriteStatus('SourceStatus', value, qualifier)
                except (KeyError, TypeError):
                    self.Error(['SourceStatus: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSourceStatus')

    def SetSwitchingPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 50
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            SwitchingPresetRecallCmdString = 'presetload switch_preset{0}\r\n'.format(value)
            self.__SetHelper('SwitchingPresetRecall', SwitchingPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchingPresetRecall')
    def SetTemporal(self, value, qualifier):

        ValueStateValues = {
            'Enable' : 'enable',
            'Disable' : 'disable'
        }

        if qualifier['Source']:
            TemporalCmdString = 'set device {0} videoport 0 temporal {1}\r\n'.format(qualifier['Source'],ValueStateValues[value])
            self.__SetHelper('Temporal', TemporalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemporal')

    def UpdateTemporal(self, value, qualifier):

        ValueStateValues = {
            'enable' : 'Enable',
            'disable' : 'Disable'
        }

        if qualifier['Source']:
            TemporalCmdString = 'get device {0} videoport 0 temporal\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Temporal', TemporalCmdString, value, qualifier)
            if res:
                match = re.match(self.regex, res)
                try:
                    value = ValueStateValues[match.group(1)]
                    self.WriteStatus('Temporal', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Temporal: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTemporal')

    def SetThreshold(self, value, qualifier):

        if qualifier['Source']:
            ThresholdCmdString = 'set device {0} videoport 0 threshold {1}\r\n'.format(qualifier['Source'],value)
            self.__SetHelper('Threshold', ThresholdCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetThreshold')

    def UpdateThreshold(self, value, qualifier):

        if qualifier['Source']:
            ThresholdCmdString = 'get device {0} videoport 0 threshold\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Threshold', ThresholdCmdString, value, qualifier)
            if res:
                try:
                    value = str(int(res))
                    if value in ['0', '1', '2', '3', '4']:
                        self.WriteStatus('Threshold', value, qualifier)
                    else:
                        self.Error(['Threshold: Invalid/unexpected response'])
                except ValueError:
                    self.Error(['Threshold: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateThreshold')

    def SetTransform(self, value, qualifier):

        ValueStateValues = {
            'Video' : 'video',
            'Graphics' : 'graphics'
        }

        if qualifier['Source']:
            TransformCmdString = 'set device {0} videoport 0 transform {1}\r\n'.format(qualifier['Source'],ValueStateValues[value])
            self.__SetHelper('Transform', TransformCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransform')

    def UpdateTransform(self, value, qualifier):

        ValueStateValues = {
            'video'    : 'Video',
            'graphics' : 'Graphics'
        }

        if qualifier['Source']:
            TransformCmdString = 'get device {0} videoport 0 transform\r\n'.format(qualifier['Source'])
            res = self.__UpdateHelper('Transform', TransformCmdString, value, qualifier)
            if res:
                match = re.match(self.regex, res)
                try:
                    value = ValueStateValues[match.group(1)]
                    self.WriteStatus('Transform', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Transform: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTransform')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if len(response) > 6:
            if response.find('fail:') >= 1:
                self.Error(['{0}: {1}'.format(sourceCmdName, response[7:-2])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        self.Send(commandstring)

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

