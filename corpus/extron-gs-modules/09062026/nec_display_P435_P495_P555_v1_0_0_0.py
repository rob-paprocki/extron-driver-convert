from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
        self.org_device_id = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'MasterPower': { 'Status': {}},
            'PictureMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'SpectraViewEngine': {'Parameters': ['Device ID'], 'Status': {}},
            'SpectraViewEnginePictureModes': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self.group_match = {
            'Broadcast': 0x2A,
            'Group A':   0x31,
            'Group B':   0x32,
            'Group C':   0x33,
            'Group D':   0x34,
            'Group E':   0x35,
            'Group F':   0x36,
            'Group G':   0x37,
            'Group H':   0x38,
            'Group I':   0x39,
            'Group J':   0x3A
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self.org_device_id = value
        if value in self.group_match:
            self._DeviceID = self.group_match[value]
        elif 1 <= int(value) <= 100:
            self._DeviceID = 0x40 + int(value)
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def keep_alive(self):

        command_string = b'\x010\x2A0A06\x0201D6\x03'
        checksum = self.__calculate_checksum(command_string)

        self.Send(command_string + checksum + b'\r')

    def __calculate_checksum(self, command_string):

        checksum = 0
        for byte in command_string[1:]:
            checksum ^= byte
        return bytes([checksum])

    def __build_setstring(self, device_id, op_code_page, op_code, value):

        header = b'\x010' + bytes([device_id]) + b'0E0A'
        message = b'\x02' + op_code_page + op_code + b'00' + value + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter

    def __build_getstring(self, device_id, op_code_page, op_code):

        header = b'\x010' + bytes([device_id]) + b'0C06'
        message = b'\x02' + op_code_page + op_code + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter

    def __set_device_id(self, device_id):

        try:
            if device_id in self.group_match:
                ret_val = self.group_match[device_id]
            elif 1 <= int(device_id) <= 100:
                ret_val = 0x40 + int(device_id)
            else:
                ret_val = None
        except (KeyError, ValueError, TypeError):
            ret_val = None

        return ret_val

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))
    
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'01',
            'Full':   b'02',
            'Wide':   b'03',
            'Zoom':   b'04',
            '1:1':    b'07',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            AspectRatioCmdString = self.__build_setstring(device_id, b'02', b'70', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            AspectRatioCmdString = self.__build_getstring(device_id, b'02', b'70')
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
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  b'01',
            'Off': b'02',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            AudioMuteCmdString = self.__build_setstring(device_id, b'00', b'8D', ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            AudioMuteCmdString = self.__build_getstring(device_id, b'00', b'8D')
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    ValueStateValues = {
                        b'1': 'On',
                        b'2': 'Off',
                    }

                    value = ValueStateValues[bytes(res[23:24])]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   100,
            'Value': value,
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and self.__constraint_checker(ValueConstraints):
            set_value = hexlify(ValueConstraints['Value'].to_bytes(1, 'big')).upper()
            BrightnessCmdString = self.__build_setstring(device_id, b'00', b'92', set_value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            BrightnessCmdString = self.__build_getstring(device_id, b'00', b'92')
            res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
            if res:
                try:
                    ValueConstraints = {
                        'Min': 0,
                        'Max': 100,
                        'Value': int(res[22:24], 16),
                    }

                    if self.__constraint_checker(ValueConstraints):
                        self.WriteStatus('Brightness', ValueConstraints['Value'], qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   100,
            'Value': value,
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and self.__constraint_checker(ValueConstraints):
            set_value = hexlify(ValueConstraints['Value'].to_bytes(1, 'big')).upper()
            ContrastCmdString = self.__build_setstring(device_id, b'00', b'12', set_value)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            ContrastCmdString = self.__build_getstring(device_id, b'00', b'12')
            res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
            if res:
                try:
                    ValueConstraints = {
                        'Min': 0,
                        'Max': 100,
                        'Value': int(res[22:24], 16),
                    }

                    if self.__constraint_checker(ValueConstraints):
                        self.WriteStatus('Contrast', ValueConstraints['Value'], qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Contrast: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateContrast')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1':  b'0F',
            'DisplayPort 2':  b'10',
            'HDMI 1':         b'11',
            'HDMI 2':         b'12',
            'Compute Module': b'88',
            'Option':         b'0D',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            InputCmdString = self.__build_setstring(device_id, b'00', b'60', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            InputCmdString = self.__build_getstring(device_id, b'00', b'60')
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
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def UpdateMasterPower(self, value, qualifier):

        temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A06\x0201D6\x03'])
        MasterPowerCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
        res = self.__UpdateHelper('MasterPower', MasterPowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    b'1': 'On',
                    b'4': 'Off',
                    b'2': 'Standby (Power Save)',
                }

                value = ValueStateValues[bytes(res[23:24])]
                self.WriteStatus('Power', value, {'Device ID': self.org_device_id})
            except (KeyError, IndexError, AttributeError):
                self.Error(['Master Power: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Highbright':     b'03',
            'Custom 1':       b'08',
            'Retail':         b'1C',
            'Conferencing':   b'1D',
            'Transportation': b'1E',
            'Native':         b'1F',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            PictureModeCmdString = self.__build_setstring(device_id, b'02', b'1A', ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            PictureModeCmdString = self.__build_getstring(device_id, b'02', b'1A')
            res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
            if res:
                try:
                    ValueStateValues = {
                        b'03': 'Highbright',
                        b'08': 'Custom 1',
                        b'1C': 'Retail',
                        b'1D': 'Conferencing',
                        b'1E': 'Transportation',
                        b'1F': 'Native',
                        b'0D': 'SVE-1 Setting',
                    }

                    value = ValueStateValues[bytes(res[22:24])]
                    self.WriteStatus('PictureMode', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Picture Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'1',
            'Off': b'4',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            temp = b''.join([b'\x010', bytes([device_id]), b'0A0C\x02C203D6000', ValueStateValues[value], b'\x03'])
            PowerCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            temp = b''.join([b'\x010', bytes([device_id]), b'0A06\x0201D6\x03'])
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
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetSpectraViewEngine(self, value, qualifier):

        ValueStateValues = {
            'On':  b'02',
            'Off': b'01',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            SpectraViewEngineCmdString = self.__build_setstring(device_id, b'11', b'47', ValueStateValues[value])
            self.__SetHelper('SpectraViewEngine', SpectraViewEngineCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpectraViewEngine')

    def UpdateSpectraViewEngine(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            SpectraViewEngineCmdString = self.__build_getstring(device_id, b'11', b'47')
            res = self.__UpdateHelper('SpectraViewEngine', SpectraViewEngineCmdString, value, qualifier)
            if res:
                try:
                    ValueStateValues = {
                        b'2': 'On',
                        b'1': 'Off',
                    }

                    value = ValueStateValues[bytes(res[23:24])]
                    self.WriteStatus('SpectraViewEngine', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['SpectraView Engine: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpectraViewEngine')

    def SetSpectraViewEnginePictureModes(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 5,
            'Value': int(value) if value.isdigit() else -1,
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and self.__constraint_checker(ValueConstraints):
            set_value = hexlify(ValueConstraints['Value'].to_bytes(1, 'big')).upper()
            SpectraViewEnginePictureModesCmdString = self.__build_setstring(device_id, b'11', b'B0', set_value)
            self.__SetHelper('SpectraViewEnginePictureModes', SpectraViewEnginePictureModesCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpectraViewEnginePictureModes')

    def UpdateSpectraViewEnginePictureModes(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            SpectraViewEnginePictureModesCmdString = self.__build_getstring(device_id, b'11', b'B0')
            res = self.__UpdateHelper('SpectraViewEnginePictureModes', SpectraViewEnginePictureModesCmdString, value, qualifier)
            if res:
                try:
                    ValueConstraints = {
                        'Min': 1,
                        'Max': 5,
                        'Value': int(res[22:24], 16),
                    }

                    if self.__constraint_checker(ValueConstraints):
                        self.WriteStatus('SpectraViewEnginePictureModes', str(ValueConstraints['Value']), qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['SpectraView Engine Picture Modes: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSpectraViewEnginePictureModes')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':  b'01',
            'Off': b'02',
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and value in ValueStateValues:
            VideoMuteCmdString = self.__build_setstring(device_id, b'10', b'B6', ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            VideoMuteCmdString = self.__build_getstring(device_id, b'10', b'B6')
            res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
            if res:
                try:
                    ValueStateValues = {
                        b'1': 'On',
                        b'2': 'Off',
                    }

                    value = ValueStateValues[bytes(res[23:24])]
                    self.WriteStatus('VideoMute', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Video Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
            'Value': value,
        }

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id and self.__constraint_checker(ValueConstraints):
            set_value = hexlify(ValueConstraints['Value'].to_bytes(1, 'big')).upper()
            VolumeCmdString = self.__build_setstring(device_id, b'00', b'62', set_value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        device_id = self.__set_device_id(qualifier['Device ID'])
        if device_id:
            VolumeCmdString = self.__build_getstring(device_id, b'00', b'62')
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    ValueConstraints = {
                        'Min': 0,
                        'Max': 100,
                        'Value': int(res[22:24], 16),
                    }

                    if self.__constraint_checker(ValueConstraints):
                        self.WriteStatus('Volume', ValueConstraints['Value'], qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if (self.Unidirectional == 'True' or self._DeviceID in self.group_match or qualifier['Device ID'] in self.group_match):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if command != 'MasterPower':
            device_id = self.__set_device_id(qualifier['Device ID'])
        else:
            device_id = None

        if (self.Unidirectional == 'True' or self._DeviceID in self.group_match or
              (device_id and device_id in self.group_match)):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()