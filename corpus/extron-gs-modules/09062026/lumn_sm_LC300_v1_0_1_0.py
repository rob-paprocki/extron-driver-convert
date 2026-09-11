from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutputMute': {'Parameters':['Output'], 'Status': {}},
            'AudioOutputVolume': {'Parameters':['Output'], 'Status': {}},
            'Background': { 'Status': {}},
            'CameraMove': {'Parameters':['Channel','Speed'], 'Status': {}},
            'CameraPresetRecall': {'Parameters':['Channel'], 'Status': {}},
            'CameraPresetSave': {'Parameters':['Channel'], 'Status': {}},
            'CameraZoom': {'Parameters':['Channel','Speed'], 'Status': {}},
            'ChannelSource': {'Parameters':['Channel'], 'Status': {}},
            'Layout': { 'Status': {}},
            'Macro': { 'Status': {}},
            'Overlay': { 'Status': {}},
            'Power': { 'Status': {}},
            'Record': { 'Status': {}},
            'Scene': { 'Status': {}},
            'Stream': {'Parameters':['Stream'], 'Status': {}},
            'SystemStatus': { 'Status': {}}
        }

        error_string = re.compile(b'\x55\xF0[\x04-\x07]\x01\x15'
                b'(\x4D\x43|\x41\x4D\x4F|\x41\x56\x4F|\x43\x48|\x52[\x43\x50]|\x53[\x43\x50\x52\x54]|'
                b'\x43[\x50\x53\x4D\x5A]|\x4C\x4F|\x42\x47|\x4F\x4C|\x54\x45)\x0D')

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x55\xF0\x07\x01\x06\x41\x4D\x4F([\x31-\x34])([\x30\x31])\x0D'), self.__MatchAudioOutputMute, None)
            self.AddMatchString(re.compile(b'\x55\xF0\x07\x01\x06\x41\x56\x4F([\x31-\x34])([\x00-\x7D])\x0D'), self.__MatchAudioOutputVolume, None)
            self.AddMatchString(re.compile(b'\x55\xF0\x05\x01\x06\x42\x47([\x00-\x09])\x0D'), self.__MatchBackground, None)
            self.AddMatchString(re.compile(b'\x55\xF0\x05\x01\x06\x4C\x4F([\x01-\x12])\x0D'), self.__MatchLayout, None)
            self.AddMatchString(re.compile(b'\x55\xF0\x05\x01\x06\x4F\x4C([\x00-\x1E])\x0D'), self.__MatchOverlay, None)
            self.AddMatchString(re.compile(b'\x55\xF0\x05\x01\x06\x53\x54([\x30-\x37])\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x55\xF0\x06\x01\x06\x53\x43([\x31-\x39])([\x00\x01\x02])\x0D'), self.__MatchStream, None)

            self.AddMatchString(error_string, self.__MatchError, None)

    def SetAudioOutputMute(self, value, qualifier):

        OutputStates = {
            'PGM Level':      b'\x31',
            'PGM HDMI':       b'\x32',
            'Multiview HDMI': b'\x33',
            'Line Out & XLR': b'\x34'
            }

        ValueStateValues = {
            'On':  b'\x31',
            'Off': b'\x30'
            }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            AudioOutputMuteCmdString = b'\x55\xF0\x07\x01\x73\x41\x4D\x4F' + OutputStates[qualifier['Output']] + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputMute')

    def UpdateAudioOutputMute(self, value, qualifier):

        OutputStates = {
            'PGM Level':      b'\x31',
            'PGM HDMI':       b'\x32',
            'Multiview HDMI': b'\x33',
            'Line Out & XLR': b'\x34'
            }

        if qualifier['Output'] in OutputStates:
            AudioOutputMuteCmdString = b'\x55\xF0\x06\x01\x67\x41\x4D\x4F' + OutputStates[qualifier['Output']] + b'\x0D'
            self.__UpdateHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutputMute')

    def __MatchAudioOutputMute(self, match, tag):

        OutputStates = {
            b'\x31': 'PGM Level',
            b'\x32': 'PGM HDMI',
            b'\x33': 'Multiview HDMI',
            b'\x34': 'Line Out & XLR'
            }

        ValueStateValues = {
            b'\x31': 'On',
            b'\x30': 'Off'
            }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AudioOutputMute', value, qualifier)

    def SetAudioOutputVolume(self, value, qualifier):

        OutputStates = {
            'PGM Level':      b'\x31',
            'PGM HDMI':       b'\x32',
            'Multiview HDMI': b'\x33',
            'Line Out & XLR': b'\x34'
            }

        if qualifier['Output'] in OutputStates and 0 <= value <= 125:
            AudioOutputVolumeCmdString = b'\x55\xF0\x07\x01\x73\x41\x56\x4F' + OutputStates[qualifier['Output']] + value.to_bytes(1, 'big') + b'\x0D'
            self.__SetHelper('AudioOutputVolume', AudioOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputVolume')

    def UpdateAudioOutputVolume(self, value, qualifier):

        OutputStates = {
            'PGM Level':      b'\x31',
            'PGM HDMI':       b'\x32',
            'Multiview HDMI': b'\x33',
            'Line Out & XLR': b'\x34'
            }

        if qualifier['Output'] in OutputStates:
            AudioOutputVolumeCmdString = b'\x55\xF0\x06\x01\x67\x41\x56\x4F' + OutputStates[qualifier['Output']] + b'\x0D'
            self.__UpdateHelper('AudioOutputVolume', AudioOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutputVolume')

    def __MatchAudioOutputVolume(self, match, tag):

        OutputStates = {
            b'\x31': 'PGM Level',
            b'\x32': 'PGM HDMI',
            b'\x33': 'Multiview HDMI',
            b'\x34': 'Line Out & XLR'
            }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1)]
        value = ord(match.group(2))
        if 0 <= value <= 125:
            self.WriteStatus('AudioOutputVolume', value, qualifier)

    def SetBackground(self, value, qualifier):

        ValueStateValues = {
            'Off':  b'\x00',
            '1':    b'\x01',
            '2':    b'\x02',
            '3':    b'\x03',
            '4':    b'\x04',
            '5':    b'\x05',
            '6':    b'\x06',
            '7':    b'\x07',
            '8':    b'\x08',
            '9':    b'\x09'
        }

        if value in ValueStateValues:
            BackgroundCmdString = b'\x55\xF0\x05\x01\x73\x42\x47' + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('Background', BackgroundCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackground')

    def UpdateBackground(self, value, qualifier):

        BackgroundCmdString = b'\x55\xF0\x04\x01\x67\x42\x47\x0D'
        self.__UpdateHelper('Background', BackgroundCmdString, value, qualifier)

    def __MatchBackground(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
            b'\x05': '5',
            b'\x06': '6',
            b'\x07': '7',
            b'\x08': '8',
            b'\x09': '9'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Background', value, None)

    def SetCameraMove(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Up':    b'\x55',
            'Down':  b'\x44',
            'Left':  b'\x4C',
            'Right': b'\x52',
            'Stop':  b'\x53'
            }
        
        ChannelStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34'
            }

        if 1 <= int(qualifier['Channel']) <= 4 and 1 <= speed <= 24 and value in ValueStateValues:
            CameraMoveCmdString = b'\x55\xF0\x07\x01\x73\x43\x4D' + ValueStateValues[value] + ChannelStates[qualifier['Channel']] + speed.to_bytes(1, 'big') + b'\x0D'
            self.__SetHelper('CameraMove', CameraMoveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraMove')

    def SetCameraPresetRecall(self, value, qualifier):

        ChannelStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34'
            }
        
        if 1 <= int(qualifier['Channel']) <= 4 and 1 <= int(value) <= 9:
            CameraPresetRecallCmdString = b'\x55\xF0\x06\x01\x73\x43\x50' + ChannelStates[qualifier['Channel']] + int(value).to_bytes(1, 'big') + b'\x0D'
            self.__SetHelper('CameraPresetRecall', CameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):

        ChannelStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34'
            }
        
        if 1 <= int(qualifier['Channel']) <= 4 and 1 <= int(value) <= 9:
            CameraPresetSaveCmdString = b'\x55\xF0\x06\x01\x73\x43\x53' + ChannelStates[qualifier['Channel']] + int(value).to_bytes(1, 'big') + b'\x0D'
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])
        ChannelStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34'
            }
        
        ValueStateValues = {
            'In':   b'\x49',
            'Out':  b'\x4F',
            'Stop': b'\x53'
            }

        if 1 <= int(qualifier['Channel']) <= 4 and 1 <= speed <= 7 and value in ValueStateValues:
            CameraZoomCmdString = b'\x55\xF0\x07\x01\x73\x43\x5A' + ValueStateValues[value] + ChannelStates[qualifier['Channel']] + speed.to_bytes(1, 'big') + b'\x0D'
            self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetChannelSource(self, value, qualifier):

        ChannelStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34'
            }

        if 1 <= int(qualifier['Channel']) <= 4 and 1 <= value <= 255:
            ChannelSourceCmdString = b'\x55\xF0\x06\x01\x73\x43\x48' + ChannelStates[qualifier['Channel']] + value.to_bytes(1, 'big') + b'\x0D'
            self.__SetHelper('ChannelSource', ChannelSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelSource')

    def SetLayout(self, value, qualifier):

        if 1 <= int(value) <= 18:
            LayoutCmdString = b'\x55\xF0\x05\x01\x73\x4C\x4F' + int(value).to_bytes(1,'big') + b'\x0D'
            self.__SetHelper('Layout', LayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayout')

    def UpdateLayout(self, value, qualifier):

        LayoutCmdString =  b'\x55\xF0\x04\x01\x67\x4C\x4F\x0D'
        self.__UpdateHelper('Layout', LayoutCmdString, value, qualifier)

    def __MatchLayout(self, match, tag):

        value = str(ord(match.group(1)))
        self.WriteStatus('Layout', value, None)

    def SetMacro(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34',
            '5': b'\x35',
            '6': b'\x36',
            '7': b'\x37',
            '8': b'\x38',
            '9': b'\x39'
            }

        if 1 <= int(value) <= 9:
            MacroCmdString = b'\x55\xF0\x05\x01\x73\x4D\x43' + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('Macro', MacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def SetOverlay(self, value, qualifier):

        ValueStateValues = {
            'Off':  b'\x00',
            '1':    b'\x01',
            '2':    b'\x02',
            '3':    b'\x03',
            '4':    b'\x04',
            '5':    b'\x05',
            '6':    b'\x06',
            '7':    b'\x07',
            '8':    b'\x08',
            '9':    b'\x09',
            '10':   b'\x0A',
            '11':   b'\x0B', 
            '12':   b'\x0C', 
            '13':   b'\x0D', 
            '14':   b'\x0E', 
            '15':   b'\x0F', 
            '16':   b'\x10', 
            '17':   b'\x11', 
            '18':   b'\x12', 
            '19':   b'\x13', 
            '20':   b'\x14', 
            '21':   b'\x15', 
            '22':   b'\x16', 
            '23':   b'\x17', 
            '24':   b'\x18', 
            '25':   b'\x19', 
            '26':   b'\x1A', 
            '27':   b'\x1B', 
            '28':   b'\x1C', 
            '29':   b'\x1D', 
            '30':   b'\x1E'
        }

        if value in ValueStateValues:
            OverlayCmdString = b'\x55\xF0\x05\x01\x73\x4F\x4C' + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('Overlay', OverlayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverlay')

    def UpdateOverlay(self, value, qualifier):

        OverlayCmdString = b'\x55\xF0\x04\x01\x67\x4F\x4C\x0D'
        self.__UpdateHelper('Overlay', OverlayCmdString, value, qualifier)

    def __MatchOverlay(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
            b'\x05': '5',
            b'\x06': '6',
            b'\x07': '7',
            b'\x08': '8',
            b'\x09': '9', 
            b'\x0A': '10', 
            b'\x0B': '11', 
            b'\x0C': '12', 
            b'\x0D': '13', 
            b'\x0E': '14', 
            b'\x0F': '15', 
            b'\x10': '16', 
            b'\x11': '17', 
            b'\x12': '18', 
            b'\x13': '19', 
            b'\x14': '20', 
            b'\x15': '21', 
            b'\x16': '22', 
            b'\x17': '23', 
            b'\x18': '24', 
            b'\x19': '25', 
            b'\x1A': '26', 
            b'\x1B': '27', 
            b'\x1C': '28', 
            b'\x1D': '29', 
            b'\x1E': '30'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Overlay', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x32',
            'Off': b'\x31'
            }

        if value in ValueStateValues:
            PowerCmdString = b'\x55\xF0\x05\x01\x73\x53\x52' + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x55\xF0\x04\x01\x67\x53\x54\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        Power_ValueStateValues = {
            b'\x30': 'On',
            b'\x31': 'On',
            b'\x32': 'On',
            b'\x33': 'On',
            b'\x34': 'On',
            b'\x35': 'On',
            b'\x36': 'On',
            b'\x37': 'Off'
        }

        SystemStatus_ValueStateValues = {
            b'\x30': 'Uninitialized',
            b'\x31': 'Ready',
            b'\x32': 'Stopped',
            b'\x33': 'Recording',
            b'\x34': 'Paused',
            b'\x35': 'Waiting',
            b'\x36': 'Stopping',
            b'\x37': 'Standby'
        }

        
        value = Power_ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)
        
        value = SystemStatus_ValueStateValues[match.group(1)]
        self.WriteStatus('SystemStatus', value, None)

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start':  b'\x52\x43',
            'Pause':  b'\x50\x53',
            'Resume': b'\x52\x50',
            'Stop':   b'\x53\x50'
            }

        if value in ValueStateValues:
            RecordCmdString = b'\x55\xF0\x04\x01\x73' + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('Record', RecordCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecord')

    def SetScene(self, value, qualifier):

        if 1 <= int(value) <= 18:
            SceneCmdString = b'\x55\xF0\x05\x01\x73\x54\x45' + int(value).to_bytes(1, 'big') +b'\x0D'
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def SetStream(self, value, qualifier):

        StreamStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34',
            '5': b'\x35',
            '6': b'\x36',
            '7': b'\x37',
            '8': b'\x38',
            '9': b'\x39'
            }
        
        ValueStateValues = {
            'Start': b'\x02',
            'Stop':  b'\x01'
            }

        if 1 <= int(qualifier['Stream']) <= 9 and value in ValueStateValues:
            StreamCmdString = b'\x55\xF0\x06\x01\x73\x53\x43' + StreamStates[qualifier['Stream']] + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('Stream', StreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStream')

    def UpdateStream(self, value, qualifier):

        StreamStates = {
            '1': b'\x31',
            '2': b'\x32',
            '3': b'\x33',
            '4': b'\x34',
            '5': b'\x35',
            '6': b'\x36',
            '7': b'\x37',
            '8': b'\x38',
            '9': b'\x39',
            }
        
        if 1 <= int(qualifier['Stream']) <= 9:
            StreamCmdString = b'\x55\xF0\x05\x01\x67\x53\x43' + StreamStates[qualifier['Stream']] + b'\x0D'
            self.__UpdateHelper('Stream', StreamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStream')

    def __MatchStream(self, match, tag):

        StreamStates = {
            b'\x31': '1',
            b'\x32': '2',
            b'\x33': '3',
            b'\x34': '4',
            b'\x35': '5',
            b'\x36': '6',
            b'\x37': '7',
            b'\x38': '8',
            b'\x39': '9',
            }

        ValueStateValues = {
            b'\x00': 'Sync',
            b'\x01': 'Ready',
            b'\x02': 'Streaming'
            }

        qualifier = {}
        qualifier['Stream'] = StreamStates[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Stream', value, qualifier)
    
    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        error_map = {
            b'\x41\x4D\x4F':    'Audio Output Mute',
            b'\x41\x56\x4F':    'Audio Output Volume',
            b'\x43\x48':        'Channel Source',
            b'\x4D\x43':        'Macro',
            b'\x53\x52':        'Power',
            b'\x52\x43':        'Record',
            b'\x53\x50':        'Record',
            b'\x53\x53':        'Record',
            b'\x53\x43':        'Stream',
            b'\x53\x54':        'Power/System Status',
            b'\x43\x53':        'Camera Preset Save',
            b'\x43\x50':        'Camera Preset Recall',
            b'\x43\x4D':        'Camera Move',
            b'\x43\x5A':        'Camera Zoom',
            b'\x42\x47':        'Background',
            b'\x54\x45':        'Scene',
            b'\x4F\x4C':        'Overlay',
            b'\x4C\x4F':        'Layout',
        }

        self.Error(['An error occurred: {}.'.format(error_map[match.group(1)])])

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()