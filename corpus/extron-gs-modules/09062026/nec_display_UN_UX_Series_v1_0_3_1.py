from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Mute': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHAdjustment': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHSize': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrix': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixComp': {'Parameters': ['Device ID'], 'Status': {}},
            'TilePosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVAdjustment': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
            }

        self.groupID = {
        'Broadcast': 0x2A,
        'Group A': 0x31,
        'Group B': 0x32,
        'Group C': 0x33,
        'Group D': 0x34,
        'Group E': 0x35,
        'Group F': 0x36,
        'Group G': 0x37,
        'Group H': 0x38,
        'Group I': 0x39,
        'Group J': 0x3A
        }     

    def SetQualifierDeviceID(self, value):
        if value in self.groupID:
            return self.groupID[value]
        elif 1 <= int(value) <= 100:
            return 0x40 + int(value)
        else:
            return False

    def __calculate_checksum(self, command_string):
        checksum = 0
        for byte in command_string[1:]:
            checksum ^= byte
        return bytes([checksum])

    def __build_setstring(self, op_code_page, op_code, value, device_id):
        header = b'\x010' + bytes([device_id]) + b'0E0A'
        message = b'\x02' + op_code_page + op_code + b'00' + value + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter

    def __build_getstring(self, op_code_page, op_code, device_id):
        header = b'\x010' + bytes([device_id]) + b'0C06'
        message = b'\x02' + op_code_page + op_code + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter

    def __keep_alive(self):
        command_string = b'\x010\x2A0A06\x0201D6\x03'
        checksum = self.__calculate_checksum(command_string)
        PowerCmdString = command_string + checksum + b'\r'
        self.Send(PowerCmdString)
        
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'01',
            'Full': b'02',
            'Wide': b'03',
            'Zoom': b'04',
            'Dynamic': b'06',
            '1:1': b'07'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            AspectRatioCmdString = self.__build_setstring(b'02', b'70', ValueStateValues[value], qualifier_dev_id)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Normal',
            b'2': 'Full',
            b'3': 'Wide',
            b'4': 'Zoom',
            b'6': 'Dynamic',
            b'7': '1:1'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            AspectRatioCmdString = self.__build_getstring(b'02', b'70', qualifier_dev_id)
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[bytes(res)[23:24]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            AutoImageCmdString = self.__build_setstring(b'00', b'1E', b'01', qualifier_dev_id)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = self.__build_setstring(b'00', b'92',
                                                              hexlify(value.to_bytes(1, 'big')).upper(),
                                                              qualifier_dev_id)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            BrightnessCmdString = self.__build_getstring(b'00', b'92', qualifier_dev_id)
            res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Brightness', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ContrastCmdString = self.__build_setstring(b'00', b'12',
                                                            hexlify(value.to_bytes(1, 'big')).upper(),
                                                            qualifier_dev_id)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            ContrastCmdString = self.__build_getstring(b'00', b'12', qualifier_dev_id)
            res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Contrast', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Contrast: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateContrast')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'01',
            'DVI': b'03',
            'Video': b'05',
            'YGA (YPbPr)': b'0C',
            'Option': b'0D',
            'DisplayPort 1': b'0F',
            'DisplayPort 2': b'10',
            'HDMI 1': b'11',
            'HDMI 2': b'12',
            'HDMI 3': b'82',
            'MP': b'87',
            'Compute Module': b'88'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            InputCmdString = self.__build_setstring(b'00', b'60', ValueStateValues[value], qualifier_dev_id)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'01': 'VGA',
            b'03': 'DVI',
            b'05': 'Video',
            b'0C': 'YGA (YPbPr)',
            b'0D': 'Option',
            b'0F': 'DisplayPort 1',
            b'10': 'DisplayPort 2',
            b'11': 'HDMI 1',
            b'12': 'HDMI 2',
            b'82': 'HDMI 3',
            b'87': 'MP',
            b'88': 'Compute Module'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            InputCmdString = self.__build_getstring(b'00', b'60', qualifier_dev_id)
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')    

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'01',
            'Off': b'02'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            MuteCmdString = self.__build_setstring(b'00', b'8D', ValueStateValues[value], qualifier_dev_id)
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'2': 'Off'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            MuteCmdString = self.__build_getstring(b'00', b'8D', qualifier_dev_id)
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[bytes(res)[23:24]]
                    self.WriteStatus('Mute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'sRGB': b'01',
            'Highbright': b'03',
            'Standard': b'04',
            'Cinema': b'05',
            'Custom 1': b'08',
            'Custom 2': b'09'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            PictureModeCmdString = self.__build_setstring(b'02', b'1A', ValueStateValues[value], qualifier_dev_id)
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'1': 'sRGB',
            b'3': 'Highbright',
            b'4': 'Standard',
            b'5': 'Cinema',
            b'8': 'Custom 1',
            b'9': 'Custom 2'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            PictureModeCmdString = self.__build_getstring(b'02', b'1A', qualifier_dev_id)
            res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[bytes(res)[23:24]]
                    self.WriteStatus('PictureMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'1',
            'Off': b'4',
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            command_string = b''.join([b'\x010', bytes([qualifier_dev_id]), b'0A0C\x02C203D6000',
                                       ValueStateValues[value], b'\x03'])
            checksum = self.__calculate_checksum(command_string)
            PowerCmdString = b''.join([command_string, checksum, b'\r'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'4': 'Off',
            b'2': 'Stand-by (Power Save)',
            b'3': 'Suspend (Power Save)'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            command_string = b''.join([b'\x010', bytes([qualifier_dev_id]), b'0A06\x0201D6\x03'])
            checksum = self.__calculate_checksum(command_string)
            PowerCmdString = b''.join([command_string, checksum, b'\r'])
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[bytes(res)[23:24]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetTileHAdjustment(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and 0 <= int(value) <= 200:
            TileHAdjustmentCmdString = self.__build_setstring(b'11', b'98',
                                                                   hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                                   qualifier_dev_id)
            self.__SetHelper('TileHAdjustment', TileHAdjustmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileHAdjustment')

    def SetTileHMonitor(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and value in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10'}:
            TileHMonitorCmdString = self.__build_setstring(b'02', b'D0',
                                                                hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                                qualifier_dev_id)
            self.__SetHelper('TileHMonitor', TileHMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileHMonitor')

    def SetTileHSize(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and 0 <= int(value) <= 200:
            TileHSizeCmdString = self.__build_setstring(b'11', b'96',
                                                             hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                             qualifier_dev_id)
            self.__SetHelper('TileHSize', TileHSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileHSize')

    def SetTileMatrix(self, value, qualifier):

        ValueStateValues = {
            'On': b'02',
            'Off': b'01'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            TileMatrixCmdString = self.__build_setstring(b'02', b'D3', ValueStateValues[value], qualifier_dev_id)
            self.__SetHelper('TileMatrix', TileMatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrix')

    def UpdateTileMatrix(self, value, qualifier):

        ValueStateValues = {
            b'2': 'On',
            b'1': 'Off'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            TileMatrixCmdString = self.__build_getstring(b'02', b'D3', qualifier_dev_id)
            res = self.__UpdateHelper('TileMatrix', TileMatrixCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[bytes(res)[23:24]]
                    self.WriteStatus('TileMatrix', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tile Matrix: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTileMatrix')

    def SetTileMatrixComp(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'02',
            'Disable': b'01'
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            TileMatrixCompCmdString = self.__build_setstring(b'02', b'D5',
                                                                  ValueStateValues[value],
                                                                  qualifier_dev_id)
            self.__SetHelper('TileMatrixComp', TileMatrixCompCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixComp')

    def SetTilePosition(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and 1 <= int(value) <= 100:
            TilePositionCmdString = self.__build_setstring(b'02', b'D2',
                                                                hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                                qualifier_dev_id)
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetTileVAdjustment(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and 0 <= int(value) <= 200:
            TileVAdjustmentCmdString = self.__build_setstring(b'11', b'99',
                                                                   hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                                   qualifier_dev_id)
            self.__SetHelper('TileVAdjustment', TileVAdjustmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileVAdjustment')

    def SetTileVMonitor(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and value in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10'}:
            TileVMonitorCmdString = self.__build_setstring(b'02', b'D1',
                                                                hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                                qualifier_dev_id)
            self.__SetHelper('TileVMonitor', TileVMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileVMonitor')

    def SetTileVSize(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and 0 <= int(value) <= 200:
            TileVSizeCmdString = self.__build_setstring(b'11', b'97',
                                                             hexlify(int(value).to_bytes(1, 'big')).upper(),
                                                             qualifier_dev_id)
            self.__SetHelper('TileVSize', TileVSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileVSize')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = self.__build_setstring(b'00', b'62',
                                                          hexlify(value.to_bytes(1, 'big')).upper(),
                                                          qualifier_dev_id)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        qualifier_dev_id = self.SetQualifierDeviceID(qualifier['Device ID'])
        if qualifier_dev_id != 0:
            VolumeCmdString = self.__build_getstring(b'00', b'62', qualifier_dev_id)
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and response[8:10].decode() == '01':
            self.Error(['{0}: An error occurred.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if (self.Unidirectional == 'True'or (qualifier['Device ID'] in self.groupID)):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if (self.Unidirectional == 'True'):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

