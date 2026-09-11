from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'GXD-L52H1': self.sony_10_2552_GXD,
            'FWD-S47H1': self.sony_10_2552_FWD,
            'FWD-S42H1': self.sony_10_2552_FWD,
            'GXD-L65H1': self.sony_10_2552_GXD,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Parameters': ['Input'], 'Status': {}},
            'Volume': {'Status': {}}
            }

    def BuildCommandString(self, commandstring):
        sum_ = 0
        for i in range(0, len(commandstring)):
            sum_ = sum_ + commandstring[i]
        checksum = pack('B', sum_ & 0xFF)
        message = b''.join([commandstring, checksum])
        return message

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x00',
            'Zoom': b'\x01',
            'Full': b'\x02',
            'Normal': b'\x04',
            'Full 1': b'\x05',
            'Full 2': b'\x06'
        }

        AspectRatioCmdString = b''.join([b'\x20\x04\x02', ValueStateValues[value]])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0: 'Wide Zoom',
            1: 'Zoom',
            2: 'Full',
            4: 'Normal',
            5: 'Full 1',
            6: 'Full 2'
        }

        AspectRatioCmdString = b'\x20\x04\xFF\xFF'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        AudioMuteCmdString = b''.join([b'\x00\x03\x02', ValueStateValues[value]])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\x00\x03\xFF\xFF'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x20\x06\x02\xFF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': b'\x00',
            'Mode 2': b'\x01',
            'Mode 3': b'\x02',
            'Off': b'\x03'
        }

        ExecutiveModeCmdString = b''.join([b'\x00\x45\x02', ValueStateValues[value]])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Mode 1',
            1: 'Mode 2',
            2: 'Mode 3',
            3: 'Off'
        }

        ExecutiveModeCmdString = b'\x00\x45\xFF\xFF'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetInput(self, value, qualifier):

        InputCmdString = b''.join([b'\x00\x01\x02', self.SetInputStates[value]])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x00\x01\xFF\xFF'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInputStates[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x00',
            'Vivid': b'\x01',
            'Custom': b'\x02',
            'TC Control': b'\x05',
            'Conference': b'\x06'
        }

        PictureModeCmdString = b''.join([b'\x10\x10\x02', ValueStateValues[value]])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Standard',
            1: 'Vivid',
            2: 'Custom',
            5: 'TC Control',
            6: 'Conference'
        }

        PictureModeCmdString = b'\x10\x10\xFF\xFF'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerCmdString = b''.join([b'\x00\x00\x02', ValueStateValues[value]])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x00\x00\xFF\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        VideoMuteCmdString = b''.join([b'\x00\x8D\x03', self.VideoMuteInput[qualifier['Input']], ValueStateValues[value]])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = b''.join([b'\x00\x8D', self.VideoMuteInput[qualifier['Input']], b'\xFF'])
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volumeValue = pack('B', value)
            VolumeCmdString = b''.join([b'\x10\x30\x02', volumeValue])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x10\x30\xFF\xFF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    print('Invalid/unexpected response for UpdateVolume')
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0: 'No Function Error',
            1: 'Check Sum Error',
            2: 'Data Length Error'
        }

        DEVICE_ERROR_CODES2 = {
            1: 'Limit Over',
            2: 'Limit Under',
            3: 'Command Canceled'
        }

        if response[0] == 224:
            print('Error: {0}'.format(DEVICE_ERROR_CODES[response[1]]))
            response = ''
        elif response[1] in DEVICE_ERROR_CODES2:
            self.Error(['Error: {0}'.format(DEVICE_ERROR_CODES2[response[1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            commandstring = self.BuildCommandString(b''.join([b'\x8C', commandstring]))
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
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
            
        commandstring = self.BuildCommandString(b''.join([b'\x83', commandstring]))

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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

        

    def sony_10_2552_FWD(self):
        self.SetInputStates = {
            'HD15 RGB'                           : b'\x08', 
            'HD15 YUV'                           : b'\x09', 
            'Option RGB'                         : b'\x0E', 
            'Option Component'                   : b'\x0F', 
            'DVI'                                : b'\x20', 
            'Video'                              : b'\x30', 
            'S-Video'                            : b'\x31', 
            'Option Digital 1 (HDMI 1/SDI/FW50)' : b'\x84', 
            'Option Digital 2 (HDMI 2)'          : b'\x85'
        }

        self.UpdateInputStates = {
            8  : 'HD15 RGB', 
            9  : 'HD15 YUV', 
            14 : 'Option RGB', 
            15 : 'Option Component', 
            32 : 'DVI', 
            48 : 'Video', 
            49 : 'S-Video', 
            132 : 'Option Digital 1 (HDMI 1/SDI/FW50)', 
            133 : 'Option Digital 2 (HDMI 2)'
        }

        self.VideoMuteInput = {
            'HD15'   : b'\x00', 
            'Option' : b'\x01',
        }


    def sony_10_2552_GXD(self):
        self.SetInputStates = {
            'HD15 RGB'                           : b'\x08', 
            'HD15 YUV'                           : b'\x09', 
            'Option RGB'                         : b'\x0E', 
            'Option Component'                   : b'\x0F', 
            'DVI'                                : b'\x20', 
            'Video'                              : b'\x30', 
            'S-Video'                            : b'\x31', 
            'HDMI'                               : b'\x44', 
            'Option Digital 1 (HDMI 1/SDI/FW50)' : b'\x84', 
            'Option Digital 2 (HDMI 2)'          : b'\x85'
        }

        self.UpdateInputStates = {
            8  : 'HD15 RGB', 
            9  : 'HD15 YUV', 
            14 : 'Option RGB', 
            15 : 'Option Component', 
            32 : 'DVI', 
            48 : 'Video', 
            49 : 'S-Video', 
            68 : 'HDMI', 
            132 : 'Option Digital 1 (HDMI 1/SDI/FW50)', 
            133 : 'Option Digital 2 (HDMI 2)'
        }

        self.VideoMuteInput = {
            'HD15'   : b'\x00', 
            'Option' : b'\x01',
            'HDMI'   : b'\x02'
        }

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
            print(command, 'does not exist in the module')

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
        
class DeviceEthernetClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'FWD-S42H1': self.sony_10_2552_FWD,
            'FWD-S47H1': self.sony_10_2552_FWD,
            'GXD-L52H1': self.sony_10_2552_GXD,
            'GXD-L65H1': self.sony_10_2552_GXD,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Parameters': ['Input'], 'Status': {}},
            'Volume': {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x04\x02\x00\xB2',
            'Zoom': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x04\x02\x01\xB3',
            'Full': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x04\x02\x02\xB4',
            'Normal': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x04\x02\x04\xB6',
            'Full 1': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x04\x02\x05\xB7',
            'Full 2': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x04\x02\x06\xB8'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0: 'Wide Zoom',
            1: 'Zoom',
            2: 'Full',
            4: 'Normal',
            5: 'Full 1',
            6: 'Full 2'
        }

        AspectRatioCmdString = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x20\x04\xFF\xFF\xA5'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x03\x02\x01\x92',
            'Off': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x03\x02\x00\x91'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x00\x03\xFF\xFF\x84'

        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x20\x06\x02\xFF\xB3'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x45\x02\x00\xD3',
            'Mode 2': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x45\x02\x01\xD4',
            'Mode 3': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x45\x02\x02\xD5',
            'Off': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x45\x02\x03\xD6'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Mode 1',
            1: 'Mode 2',
            2: 'Mode 3',
            3: 'Off'
        }

        ExecutiveModeCmdString = b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x83\x00\x45\xFF\xFF\xC6'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetInput(self, value, qualifier):

        InputCmdString = self.SetInputStates[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x00\x01\xFF\xFF\x82'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.UpdateInputStates[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x10\x10\x02\x00\xAE',
            'Vivid': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x10\x10\x02\x01\xAF',
            'Custom': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x10\x10\x02\x02\xB0',
            'TC Control': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x10\x10\x02\x05\xB3',
            'Conference': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x10\x10\x02\x06\xB4'
        }

        PictureModeCmdString = ValueStateValues[value]

        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Standard',
            1: 'Vivid',
            2: 'Custom',
            5: 'TC Control',
            6: 'Conference'
        }

        PictureModeCmdString = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x10\x10\xFF\xFF\xA1'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x00\x02\x01\x8F',
            'Off': b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x00\x02\x00\x8E'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x00\x00\xFF\xFF\x81'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = self.SetVideoMuteState[qualifier['Input']][value]

        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = self.GetVideoMuteState[qualifier['Input']]
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            volumeValue = pack('B', value)

            header = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06'
            commandstring = b''.join([b'\x8C\x10\x30\x02', volumeValue])

            sum_ = 0
            for i in range(0, len(commandstring)):
                sum_ = sum_ + i
            checksum = pack('B', sum_ & 0xFF)

            VolumeCmdString = b''.join([header, commandstring, checksum])

            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x10\x30\xFF\xFF\xC1'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    print('Invalid/unexpected response for UpdateVolume')
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODE = {
            b'\x01\x01': 'Invalid Item',
            b'\x01\x02': 'Invalid Item Request',
            b'\x01\x03': 'Invalid Item Length',
            b'\x01\x04': 'Invalid Item Data',
            b'\x01\x11': 'Short Data',
            b'\x01\x80': 'Item Not Applicable',
            b'\x02\x01': 'Different Community',
            b'\x10\x01': 'Invalid Version',
            b'\x10\x02': 'Invalid Category',
            b'\x10\x03': 'Invalid Request',
            b'\x10\x11': 'Short Header',
            b'\x10\x12': 'Short Community',
            b'\x10\x13': 'Short Command',
            b'\x20\x01': 'Timeout',
            b'\xF0\x01': 'Timeout',
            b'\xF0\x10': 'Checksum Error',
            b'\xF0\x20': 'Framing Error',
            b'\xF0\x30': 'Parity Error',
            b'\xF0\x40': 'Over Run Error',
            b'\xF0\x50': 'Other Comm Error',
            b'\xF0\xF0': 'Unknown Response',
            b'\xF1\x10': 'Read Error',
            b'\xF1\x20': 'Write Error'
        }
        if response[6] == 0:
            print('Error: {0}'.format(DEVICE_ERROR_CODE[response[-3:-1]]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=13)
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
            print('Inappropriate Command ', command)
            return ''
        else:

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=15)
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
        

    def sony_10_2552_FWD(self):
        self.SetInputStates = {
            'HD15 RGB'                           : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x08\x97', 
            'HD15 YUV'                           : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x09\x98', 
            'Option RGB'                         : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x0E\x9D', 
            'Option Component'                   : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x0F\x9E', 
            'DVI'                                : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x20\xAF', 
            'Video'                              : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x30\xBF', 
            'S-Video'                            : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x31\xC0', 
            'Option Digital 1 (HDMI 1/SDI/FW50)' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x84\x13', 
            'Option Digital 2 (HDMI 2)'          : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x85\x14'
        }

        self.UpdateInputStates = {
            8  : 'HD15 RGB', 
            9  : 'HD15 YUV', 
            14 : 'Option RGB', 
            15 : 'Option Component', 
            32 : 'DVI', 
            48 : 'Video', 
            49 : 'S-Video', 
            132 : 'Option Digital 1 (HDMI 1/SDI/FW50)', 
            133 : 'Option Digital 2 (HDMI 2)'
        }

        self.SetVideoMuteState = {
            'HD15'   : { 'On'  : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x00\x01\x1D',
                         'Off' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x00\x00\x1C'},
            'Option' : { 'On'  : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x01\x01\x1E',
                         'Off' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x01\x00\x1D'}
        }

        self.VideoMuteInput = {
            'HD15'   : b'\x00', 
            'Option' : b'\x01',
        }

        self.GetVideoMuteState = {
            'HD15'   : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x83\x00\x8D\x00\xFF\x0F',
            'Option' : b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x00\x8D\x01\xFF\x10'
        }


    def sony_10_2552_GXD(self):
        self.SetInputStates = {
            'HD15 RGB'                           : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x08\x97', 
            'HD15 YUV'                           : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x09\x98', 
            'Option RGB'                         : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x0E\x9D', 
            'Option Component'                   : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x0F\x9E', 
            'DVI'                                : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x20\xAF', 
            'Video'                              : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x30\xBF', 
            'S-Video'                            : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x31\xC0', 
            'HDMI'                               : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x44\xD3', 
            'Option Digital 1 (HDMI 1/SDI/FW50)' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x84\x13', 
            'Option Digital 2 (HDMI 2)'          : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x01\x02\x85\x14'
        }

        self.UpdateInputStates = {
            8  : 'HD15 RGB', 
            9  : 'HD15 YUV', 
            14 : 'Option RGB', 
            15 : 'Option Component', 
            32 : 'DVI', 
            48 : 'Video', 
            49 : 'S-Video', 
            68 : 'HDMI', 
            132 : 'Option Digital 1 (HDMI 1/SDI/FW50)', 
            133 : 'Option Digital 2 (HDMI 2)'
        }

        self.SetVideoMuteState = {
            'HD15'   : { 'On'  : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x00\x01\x1D',
                         'Off' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x00\x00\x1C'},
            'Option' : { 'On'  : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x01\x01\x1E',
                         'Off' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x01\x00\x1D'},
            'HDMI'   : { 'On'  : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x02\x01\x1F',
                         'Off' : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x8C\x00\x8D\x03\x02\x00\x1E'}
        }

        self.VideoMuteInput = {
            'HD15'   : b'\x00', 
            'Option' : b'\x01',
            'HDMI'   : b'\x02'
        }

        self.GetVideoMuteState = {
            'HD15'   : b'\x02\x10\x53\x4F\x4E\x59\x00\xF1\x00\x06\x83\x00\x8D\x00\xFF\x0F',
            'Option' : b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x00\x8D\x01\xFF\x10',
            'HDMI'   : b'\x02\x10\x53\x4F\x4E\x59\x01\xF1\x00\x06\x83\x00\x8D\x02\xFF\x11'
        }

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
            print(command, 'does not exist in the module')

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
        
class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
