from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ClosedCaptionAnalog': { 'Status': {}},
            'ClosedCaptionDigital': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Standby': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.UpdateRegex = re.compile(b'\x70[\x00-\x02][\x02][\x00-\x01][\x00-\xFF]|\x70[\x00-\x02][\x03][\x01-\x07][\x00-\xFF]{2}|\x70[\x03-\x04][\x00-\xFF]')

    def CalCRC(self, Data):
        Crc = 0
        for i in range(0, len(Data)):
            if type(Data[i]) is int:
                Crc += Data[i]
            else:
                Crc += ord(Data[i])
        return Crc & 0xFF

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom'   : 0x00, 
            'Zoom'        : 0x02, 
            'Normal'      : 0x03, 
            'Normal (PC)' : 0x05, 
            'Full 1'      : 0x01, 
            'Full 2'      : 0x06, 
            'Full 3'      : 0x07
        }

        Data = [0x8C, 0x00, 0x44, 0x03, 0x01, ValueStateValues[value]]
        AspectRatioCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        Data = [0x8C, 0x00, 0x06, 0x03, 0x01, ValueStateValues[value]]
        AudioMuteCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 0x10,
            'Down' : 0x11
        }

        Data = [0x8C, 0x00, 0x67, 0x03, 0x01, ValueStateValues[value]]
        ChannelCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        Data = [0x8C, 0x00, 0x10, 0x03, 0x01, ValueStateValues[value]]
        ClosedCaptionCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC1'   : 0x01,
            'CC2'   : 0x02,
            'CC3'   : 0x03,
            'CC4'   : 0x04,
            'Text1' : 0x05,
            'Text2' : 0x06,
            'Text3' : 0x07,
            'Text4' : 0x08
        }

        Data = [0x8C, 0x00, 0x10, 0x04, 0x02, 0x00, ValueStateValues[value]]
        ClosedCaptionAnalogCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'CC1'      : 0x07,
            'CC2'      : 0x08,
            'CC3'      : 0x09,
            'CC4'      : 0x0a,
            'Service1' : 0x01,
            'Service2' : 0x02,
            'Service3' : 0x03,
            'Service4' : 0x04,
            'Service5' : 0x05,
            'Service6' : 0x06
        }

        Data = [0x8C, 0x00, 0x10, 0x04, 0x02, 0x01, ValueStateValues[value]]
        ClosedCaptionDigitalCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video 1'   : (0x02, 0x01),
            'Video 2'   : (0x02, 0x02),
            'Component' : (0x03, 0x01), 
            'HDMI 1'    : (0x04, 0x01), 
            'HDMI 2'    : (0x04, 0x02), 
            'HDMI 3'    : (0x04, 0x03), 
            'HDMI 4'    : (0x04, 0x04)
        }

        if value == 'TV':
             InputCmdString = b'\x8C\x00\x02\x02\x01\x91'
        else:
            Data = [0x8C, 0x00, 0x02, 0x03, ValueStateValues[value][0], ValueStateValues[value][1]]
            InputCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x02\x01' : 'Video 1',
            b'\x02\x02' : 'Video 2',
            b'\x03\x01' : 'Component',
            b'\x04\x01' : 'HDMI 1',
            b'\x04\x02' : 'HDMI 2',
            b'\x04\x03' : 'HDMI 3',
            b'\x04\x04' : 'HDMI 4',
        }

        Data = [0x83, 0x00, 0x02, 0xFF, 0xFF]
        InputCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[3] == 1:
                    self.WriteStatus('Input', 'TV', qualifier)
                else:
                    value = ValueStateValues[res[3:5]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0'  : [0x01, 0x09],
            '1'  : [0x01, 0x00],
            '2'  : [0x01, 0x01],
            '3'  : [0x01, 0x02],
            '4'  : [0x01, 0x03],
            '5'  : [0x01, 0x04],
            '6'  : [0x01, 0x05],
            '7'  : [0x01, 0x06],
            '8'  : [0x01, 0x07],
            '9'  : [0x01, 0x08],
            'Dot': [0x97, 0x1D]
        }

        Data = [0x8C, 0x00, 0x67, 0x03, ValueStateValues[value][0], ValueStateValues[value][1]]
        KeypadCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left'   : [0x01, 0x34],
            'Right'  : [0x01, 0x33],
            'Up'     : [0x01, 0x74],
            'Down'   : [0x01, 0x75],
            'Home'   : [0x01, 0x60],
            'Return' : [0x97, 0x23],
            'Select' : [0x01, 0x65],
            'Options': [0x97, 0x36]
        }

        Data = [0x8C, 0x00, 0x67, 0x03, ValueStateValues[value][0], ValueStateValues[value][1]]
        MenuNavigationCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        Data = [0x8C, 0x00, 0x00, 0x02, ValueStateValues[value]]
        PowerCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01 : 'On',
            0x00 : 'Off'
        }

        Data = [0x83, 0x00, 0x00, 0xFF, 0xFF]
        PowerCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : 0x01, 
            'Disable' : 0x00
        }

        Data = [0x8C, 0x00, 0x01, 0x02, ValueStateValues[value]]
        StandbyCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x00,
            'Off' : 0x01,
        }

        Data = [0x8C, 0x00, 0x0D, 0x03, 0x01, ValueStateValues[value]]
        VideoMuteCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Data = [0x8C, 0x00, 0x05, 0x03, 0x01, value]
            VolumeCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        Data = [0x83, 0x00, 0x05, 0xFF, 0xFF]
        VolumeCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1 : 'Limit Over (Abnormal End - over max value)',
            2 : 'Limit Over (Abnormal End - under min value)',
            3 : 'Command Canceled (Abnormal End)',
            4 : 'Parse Error (Data Format Error)'
        }

        if len(response) == 3 and response[1] in DEVICE_ERROR_CODES:
            self.Error(['{0} Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen = 3)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex = self.UpdateRegex)
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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureinPicture': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '*SCAMUT0000000000000001\n',
            'Off' : '*SCAMUT0000000000000000\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        AudioMuteCmdString = '*SEAMUT################\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'    : '*SCIRCC0000000000000033\n',
            'Down'  : '*SCIRCC0000000000000034\n'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV'               : '*SCINPT0000000000000000\n',
            'Component'        : '*SCINPT0000000400000001\n',
            'Video 1'          : '*SCINPT0000000300000001\n',
            'Video 2'          : '*SCINPT0000000300000002\n',
            'HDMI 1'           : '*SCINPT0000000100000001\n',
            'HDMI 2'           : '*SCINPT0000000100000002\n',
            'HDMI 3'           : '*SCINPT0000000100000003\n',
            'HDMI 4'           : '*SCINPT0000000100000004\n',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '*SEINPT################\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[14] == '0':
                    value = 'TV'
                elif res[14] == '4' and res[22] == '1':
                    value = 'Component'
                elif res[14] == '3' and res[22] in ['1', '2']:
                    value = 'Video {}'.format(res[22])
                elif res[14] == '1' and res[22] in ['1', '2', '3', '4']:
                    value = 'HDMI {}'.format(res[22])
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

            if value:
                self.WriteStatus('Input', value, qualifier)
            else:
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0'   : '*SCIRCC0000000000000027\n',
            '1'   : '*SCIRCC0000000000000018\n',
            '2'   : '*SCIRCC0000000000000019\n',
            '3'   : '*SCIRCC0000000000000020\n',
            '4'   : '*SCIRCC0000000000000021\n',
            '5'   : '*SCIRCC0000000000000022\n',
            '6'   : '*SCIRCC0000000000000023\n',
            '7'   : '*SCIRCC0000000000000024\n',
            '8'   : '*SCIRCC0000000000000025\n',
            '9'   : '*SCIRCC0000000000000026\n',
            '11'  : '*SCIRCC0000000000000028\n',
            '12'  : '*SCIRCC0000000000000029\n',
            'Dot' : '*SCIRCC0000000000000038\n'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Left'      : '*SCIRCC0000000000000012\n',
            'Right'     : '*SCIRCC0000000000000011\n',
            'Up'        : '*SCIRCC0000000000000009\n',
            'Down'      : '*SCIRCC0000000000000010\n',
            'Home'      : '*SCIRCC0000000000000006\n',
            'Return'    : '*SCIRCC0000000000000008\n',
            'Select'    : '*SCIRCC0000000000000013\n',
            'Options'   : '*SCIRCC0000000000000007\n'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : '*SCPOWR0000000000000001\n',
            'Off'   : '*SCPOWR0000000000000000\n'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        PowerCmdString = '*SEPOWR################\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '*SCPMUT0000000000000001\n',
            'Off' : '*SCPMUT0000000000000000\n'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        VideoMuteCmdString = '*SEPMUT################\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '*SCVOLU0000000000000{0:03d}\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '*SEVOLU################\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'FFFFFFFFFFFFFFFF': 'Invalid Parameter',
            'NNNNNNNNNNNNNNNN': 'The command does not exist',
        }

        if response[7:-1] in DEVICE_ERROR_CODES:
            self.Error(['{0} Error: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[7:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()