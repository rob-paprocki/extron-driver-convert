# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from binascii import hexlify

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
        self._DeviceID = 0x41
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Input': { 'Status': {}},
            'MultiPictureActiveFrame': { 'Status': {}},
            'MultiPictureActivePicture': { 'Status': {}},
            'MultiPictureAudio': { 'Status': {}},
            'MultiPictureInput': {'Parameters': ['Picture'], 'Status': {}},
            'MultiPictureMode': { 'Status': {}},
            'MultiPicturePosition': {'Parameters': ['Axis'], 'Status': {}},
            'MultiPictureSize': { 'Status': {}},
            'MultiPictureSizeDiscrete': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        groupMatch = {
            'Broadcast':    0x2A,
            'Group A':      0x31,
            'Group B':      0x32,
            'Group C':      0x33,
            'Group D':      0x34,
            'Group E':      0x35,
            'Group F':      0x36,
            'Group G':      0x37,
            'Group H':      0x38,
            'Group I':      0x39,
            'Group J':      0x3A,
        }
        if value in groupMatch:
            self._DeviceID = groupMatch[value]
        elif 1 <= int(value) <= 100:
            self._DeviceID = 0x40 + int(value)
        else:
            print('Invalid Device ID Parameter.')

    def keep_alive(self):

        command_string = b'\x010\x2A0A06\x0201D6\x03'
        checksum = self.__calculate_checksum(command_string)

        self.Send(command_string + checksum + b'\r')
    
    def __calculate_checksum(self, command_string):

        checksum = 0
        for byte in command_string[1:]:
            checksum ^= byte
        return bytes([checksum])

    def __build_setstring(self, op_code_page, op_code, value):

        header = b'\x010' + bytes([self._DeviceID]) + b'0E0A'
        message = b'\x02' + op_code_page + op_code + b'00' + value + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter

    def __build_getstring(self, op_code_page, op_code):

        header = b'\x010' + bytes([self._DeviceID]) + b'0C06'
        message = b'\x02' + op_code_page + op_code + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'01',
            'Full':   b'02',
            'Wide':   b'03',
            'Zoom':   b'04',
            '1:1':    b'07',
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.__build_setstring(b'02', b'70', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.__build_getstring(b'02', b'70')
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'Normal',
                    b'2': 'Full',
                    b'3': 'Wide',
                    b'4': 'Zoom',
                    b'7': '1:1',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  b'01',
            'Off': b'02',
        }

        if value in ValueStateValues:
            AudioMuteCmdString = self.__build_setstring(b'00', b'8D', ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = self.__build_getstring(b'00', b'8D')
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'On',
                    b'2': 'Off',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1':  b'0F',
            'DisplayPort 2':  b'10',
            'HDMI 1':         b'11',
            'HDMI 2':         b'12',
            'Compute Module': b'88',
            'Option':         b'0D',
        }

        if value in ValueStateValues:
            InputCmdString = self.__build_setstring(b'00', b'60', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.__build_getstring(b'00', b'60')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'0F': 'DisplayPort 1',
                    b'10': 'DisplayPort 2',
                    b'11': 'HDMI 1',
                    b'12': 'HDMI 2',
                    b'88': 'Compute Module',
                    b'0D': 'Option',
                }

                value = ValueStateValues[bytes(res[22:24])]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMultiPictureActiveFrame(self, value, qualifier):

        ValueStateValues = {
            'Off': b'01',
            'On':  b'02',
        }

        if value in ValueStateValues:
            MultiPictureActiveFrameCmdString = self.__build_setstring(b'11', b'0D', ValueStateValues[value])
            self.__SetHelper('MultiPictureActiveFrame', MultiPictureActiveFrameCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureActiveFrame')

    def UpdateMultiPictureActiveFrame(self, value, qualifier):

        MultiPictureActiveFrameCmdString = self.__build_getstring(b'11', b'0D')
        res = self.__UpdateHelper('MultiPictureActiveFrame', MultiPictureActiveFrameCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'Off',
                    b'2': 'On',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('MultiPictureActiveFrame', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Multi Picture Active Frame: Invalid/unexpected response'])

    def SetMultiPictureActivePicture(self, value, qualifier):

        ValueStateValues = {
            'Window 1': b'01',
            'Window 2': b'02',
            'Window 3': b'03',
            'Window 4': b'04',
        }

        if value in ValueStateValues:
            MultiPictureActivePictureCmdString = self.__build_setstring(b'11', b'0B', ValueStateValues[value])
            self.__SetHelper('MultiPictureActivePicture', MultiPictureActivePictureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureActivePicture')

    def UpdateMultiPictureActivePicture(self, value, qualifier):

        MultiPictureActivePictureCmdString = self.__build_getstring(b'11', b'0B')
        res = self.__UpdateHelper('MultiPictureActivePicture', MultiPictureActivePictureCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'Window 1',
                    b'2': 'Window 2',
                    b'3': 'Window 3',
                    b'4': 'Window 4',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('MultiPictureActivePicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Multi Picture Active Picture: Invalid/unexpected response'])

    def SetMultiPictureAudio(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1':    b'14',
            'DisplayPort 2':    b'15',
            'HDMI 1':           b'16',
            'HDMI 2':           b'17',
            'Option (Digital)': b'18',
            'Raspberry PI':     b'1A',
        }

        if value in ValueStateValues:
            MultiPictureAudioCmdString = self.__build_setstring(b'10', b'80', ValueStateValues[value])
            self.__SetHelper('MultiPictureAudio', MultiPictureAudioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureAudio')

    def UpdateMultiPictureAudio(self, value, qualifier):

        MultiPictureAudioCmdString = self.__build_getstring(b'10', b'80')
        res = self.__UpdateHelper('MultiPictureAudio', MultiPictureAudioCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'14': 'DisplayPort 1',
                    b'15': 'DisplayPort 2',
                    b'16': 'HDMI 1',
                    b'17': 'HDMI 2',
                    b'18': 'Option (Digital)',
                    b'1A': 'Raspberry PI',
                }

                value = ValueStateValues[bytes(res[22:24])]
                self.WriteStatus('MultiPictureAudio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Multi Picture Audio: Invalid/unexpected response'])

    def SetMultiPictureInput(self, value, qualifier):

        PictureStates = {
            '1': b'0E',
            '2': b'0F',
            '3': b'10',
            '4': b'11',
        }

        ValueStateValues = {
            'DisplayPort 1':  b'0F',
            'DisplayPort 2':  b'10',
            'HDMI 1':         b'11',
            'HDMI 2':         b'12',
            'Compute Module': b'88',
            'Option':         b'0D',
        }

        if qualifier['Picture'] in PictureStates and value in ValueStateValues:
            picture_num = PictureStates[qualifier['Picture']]
            MultiPictureInputCmdString = self.__build_setstring(b'11', picture_num, ValueStateValues[value])
            self.__SetHelper('MultiPictureInput', MultiPictureInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureInput')

    def UpdateMultiPictureInput(self, value, qualifier):

        PictureStates = {
            '1': b'0E',
            '2': b'0F',
            '3': b'10',
            '4': b'11',
        }

        if qualifier['Picture'] in PictureStates:
            picture_num = PictureStates[qualifier['Picture']]
            MultiPictureInputCmdString = self.__build_getstring(b'11', picture_num)
            res = self.__UpdateHelper('MultiPictureInput', MultiPictureInputCmdString, value, qualifier)
            if res:
                try:
                    ValueStateValues = {
                        b'0F': 'DisplayPort 1',
                        b'10': 'DisplayPort 2',
                        b'11': 'HDMI 1',
                        b'12': 'HDMI 2',
                        b'88': 'Compute Module',
                        b'0D': 'Option',
                    }

                    value = ValueStateValues[bytes(res[22:24])]
                    self.WriteStatus('MultiPictureInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Multi Picture Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMultiPictureInput')

    def SetMultiPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Off':  b'01',
            '2PIP': b'02',
            '2PBP': b'03',
            '4PBP': b'04',
        }

        if value in ValueStateValues:
            MultiPictureModeCmdString = self.__build_setstring(b'11', b'EB', ValueStateValues[value])
            self.__SetHelper('MultiPictureMode', MultiPictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureMode')

    def UpdateMultiPictureMode(self, value, qualifier):

        MultiPictureModeCmdString = self.__build_getstring(b'11', b'EB')
        res = self.__UpdateHelper('MultiPictureMode', MultiPictureModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'Off',
                    b'2': '2PIP',
                    b'3': '2PBP',
                    b'4': '4PBP',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('MultiPictureMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Multi Picture Mode: Invalid/unexpected response'])

    def SetMultiPicturePosition(self, value, qualifier):

        AxisStates = {
            'X': b'74',
            'Y': b'75',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if qualifier['Axis'] in AxisStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            axis = AxisStates[qualifier['Axis']]
            MultiPicturePositionCmdString = self.__build_setstring(b'02', axis,
                                                                        hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('MultiPicturePosition', MultiPicturePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPicturePosition')

    def UpdateMultiPicturePosition(self, value, qualifier):

        AxisStates = {
            'X': b'74',
            'Y': b'75',
        }

        if qualifier['Axis'] in AxisStates:
            axis = AxisStates[qualifier['Axis']]
            MultiPicturePositionCmdString = self.__build_getstring(b'02', axis)
            res = self.__UpdateHelper('MultiPicturePosition', MultiPicturePositionCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    if 0 <= value <= 100:
                        self.WriteStatus('MultiPicturePosition', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Multi Picture Position: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMultiPicturePosition')

    def SetMultiPictureSize(self, value, qualifier):

        ValueStateValues = {
            'Small':  b'01',
            'Middle': b'02',
            'Large':  b'03',
        }

        if value in ValueStateValues:
            MultiPictureSizeCmdString = self.__build_setstring(b'02', b'71', ValueStateValues[value])
            self.__SetHelper('MultiPictureSize', MultiPictureSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureSize')

    def UpdateMultiPictureSize(self, value, qualifier):

        MultiPictureSizeCmdString = self.__build_getstring(b'02', b'71')
        res = self.__UpdateHelper('MultiPictureSize', MultiPictureSizeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'Small',
                    b'2': 'Middle',
                    b'3': 'Large',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('MultiPictureSize', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Multi Picture Size: Invalid/unexpected response'])

    def SetMultiPictureSizeDiscrete(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 80,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MultiPictureSizeDiscreteCmdString = self.__build_setstring(b'10', b'B9',
                                                                            hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('MultiPictureSizeDiscrete', MultiPictureSizeDiscreteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiPictureSizeDiscrete')

    def UpdateMultiPictureSizeDiscrete(self, value, qualifier):

        MultiPictureSizeDiscreteCmdString = self.__build_getstring(b'10', b'B9')
        res = self.__UpdateHelper('MultiPictureSizeDiscrete', MultiPictureSizeDiscreteCmdString, value, qualifier)
        if res:
            try:
                value = int(res[22:24], 16)
                if 0 <= value <= 80:
                    self.WriteStatus('MultiPictureSizeDiscrete', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Multi Picture Size Discrete: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'1',
            'Off': b'4',
        }

        if value in ValueStateValues:
            temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A0C\x02C203D6000', ValueStateValues[value], b'\x03'])
            PowerCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A06\x0201D6\x03'])
        PowerCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'On',
                    b'4': 'Off',
                    b'2': 'Standby (Power Save)',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':  b'01',
            'Off': b'02',
        }

        if value in ValueStateValues:
            VideoMuteCmdString = self.__build_setstring(b'10', b'B6', ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = self.__build_getstring(b'10', b'B6')
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'On',
                    b'2': 'Off',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = self.__build_setstring(b'00', b'62', hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = self.__build_getstring(b'00', b'62')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[22:24], 16)
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0x2A or (0x31 <= self._DeviceID <= 0x3A):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0x2A or (0x31 <= self._DeviceID <= 0x3A):
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
                return self.__CheckResponseForErrors(command, res)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and response[8:10].decode() == '01':
            self.Error(['{0}: An error occurred.'.format(sourceCmdName)])
            response = ''
        return response

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