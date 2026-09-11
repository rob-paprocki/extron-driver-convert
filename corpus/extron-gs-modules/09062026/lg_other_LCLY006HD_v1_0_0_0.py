from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import struct

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
            'BigPackageModeStatus': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'ColumnLength': {'Parameters': ['Ethernet Port'], 'Status': {}},
            'ColumnStartingPoint': {'Parameters': ['Ethernet Port'], 'Status': {}},
            'Contrast': { 'Status': {}},
            'Display': { 'Status': {}},
            'FrameRate': { 'Status': {}},
            'Luminance': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'OutputSettings':           {'Set': True,  'Update': False, 'Live': False, 'Emulated': False, 'Parameters': ['Receiving Card',
                                                                                                                         'Flexible Flat Cable',
                                                                                                                         'Virtual Screen Mark',
                                                                                                                         'Packets Space',
                                                                                                                         'Big Package Mode',
                                                                                                                         'Ethernet Port 1 Row Start',
                                                                                                                         'Ethernet Port 1 Row Height',
                                                                                                                         'Ethernet Port 1 Column Start',
                                                                                                                         'Ethernet Port 1 Column Width',
                                                                                                                         'Ethernet Port 2 Row Start',
                                                                                                                         'Ethernet Port 2 Row Height',
                                                                                                                         'Ethernet Port 2 Column Start',
                                                                                                                         'Ethernet Port 2 Column Width'], 'Status': {}},
            'Resolution': { 'Status': {}},
            'RowHeight': {'Parameters': ['Ethernet Port'], 'Status': {}},
            'RowStartingPort': {'Parameters': ['Ethernet Port'], 'Status': {}},
            'TemporaryBrightness': { 'Status': {}},
            'TemporarySwitchScreen': { 'Status': {}},
            'Version': { 'Status': {}},
            'VirtualPixelMode': { 'Status': {}},
        }


        self._set_regex = re.compile(b'[\x00-\xFF]\x03[\x00-\xFF]*')
        self._rp_regex = re.compile(b'\xAA\x00[\x00-\xFF]{70}')

    def _run_steps(self, command, value, qualifier, steps):
        temp = self.DefaultResponseTimeout

        for command_string, timeout in steps:
            self.DefaultResponseTimeout = timeout
            if not self.__SetHelper(command, command_string, value, qualifier):
                break

        self.DefaultResponseTimeout = temp
        
    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            steps = [
                (b'\xAA\x23\x03\x00\x00' + (b'\x00' * 257),                         10),
                (b'\xAA\x85\x03\x00\x00' + (bytes([value]) * 16) + (b'\x00' * 241), 1),
                (b'\xAA\x44\x03\x00\x00' + (b'\x00' * 257),                         1)
            ]

            self._run_steps('Brightness', value, qualifier, steps)
        else:
            self.Discard('Invalid Command for SetBrightness')
            
    def UpdateBrightness(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateBigPackageModeStatus(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateColumnLength(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateColumnStartingPoint(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateContrast(self, value, qualifier):
        self.UpdateVersion(value, qualifier) 

    def UpdateDisplay(self, value, qualifier):
        self.UpdateVersion(value, qualifier)  

    def UpdateFrameRate(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateLuminance(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateOperationHours(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateResolution(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateRowHeight(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateRowStartingPort(self, value, qualifier):
        self.UpdateVersion(value, qualifier)
        
    def UpdateVirtualPixelMode(self, value, qualifier):
        self.UpdateVersion(value, qualifier)

    def SetOutputSettings(self, value, qualifier):

        ReceivingCardStates = {
            '5A': b'\x33',
            'T9': b'\x00'
        }

        FlexibleFlatCableStates = {
            'Right to Left': b'\x00',
            'Left to Right': b'\x01',
            'Top to Bottom': b'\x10',
            'Bottom to Top': b'\x11'
        }

        VirtualScreenMarkStates = {
            'Non-virtual':  b'\x00',
            'Virtual':      b'\x01'
        }

        PacketsSpaceStates = {
            'Small':    b'\x00',
            'Middle':   b'\x32',
            'Large':    b'\x64'
        }

        BigPackageModeStates = {
            'On':   b'\x01',
            'Off':  b'\x00'
        }

        try:
            receiving_card = ReceivingCardStates[qualifier['Receiving Card']]
            flexible_flat_cable = FlexibleFlatCableStates[qualifier['Flexible Flat Cable']]
            virtual_screen_mark = VirtualScreenMarkStates[qualifier['Virtual Screen Mark']]
            packets_space = PacketsSpaceStates[qualifier['Packets Space']]
            big_package_mode = BigPackageModeStates[qualifier['Big Package Mode']]
            port1_row_start = int(qualifier['Ethernet Port 1 Row Start'])
            port1_row_height = int(qualifier['Ethernet Port 1 Row Height'])
            port1_column_start = int(qualifier['Ethernet Port 1 Column Start'])
            port1_column_width = int(qualifier['Ethernet Port 1 Column Width'])
            port2_row_start = int(qualifier['Ethernet Port 2 Row Start'])
            port2_row_height = int(qualifier['Ethernet Port 2 Row Height'])
            port2_column_start = int(qualifier['Ethernet Port 2 Column Start'])
            port2_column_width = int(qualifier['Ethernet Port 2 Column Width'])
        except (KeyError, ValueError):
            self.Discard('Invalid Command for SetOutputSettings')
            return

        EthernetPortConstraints = {
            'Min': 0,
            'Max': 65535
        }

        range_qualifiers = ['Ethernet Port 1 Row Start',
                            'Ethernet Port 1 Row Height',
                            'Ethernet Port 1 Column Start',
                            'Ethernet Port 1 Column Width',
                            'Ethernet Port 2 Row Start',
                            'Ethernet Port 2 Row Height',
                            'Ethernet Port 2 Column Start',
                            'Ethernet Port 2 Column Width']

        if all(EthernetPortConstraints['Min'] <= qualifier[q] <= EthernetPortConstraints['Max'] for q in range_qualifiers):
                steps = [
                        (b'\xAA\x23\x05\x00\x00' + (b'\x00' * 257), 10),
                    (b'\xAA\x85\x05\x00\x00\x06' +
                     struct.pack('sssss', receiving_card, flexible_flat_cable, virtual_screen_mark, packets_space, big_package_mode) +
                     (b'\x00' * 10) +
                     struct.pack('<HH', port1_row_start, port1_row_height) +
                     struct.pack('<HH', port1_column_start, port1_column_width) +
                     (b'\x00' * 233), 1),
                    (b'\xAA\x85\x05\x04\x00' +
                     struct.pack('<HH', port2_row_start, port2_row_height) +
                     struct.pack('<HH', port2_column_start, port2_column_width) +
                     (b'\x00' * 249), 1),
                    (b'\xAA\x44\x05\x00\x00' + (b'\x00' * 257), 1)
                ]

                self._run_steps('OutputSettings', value, qualifier, steps)
        else:
            self.Discard('Invalid Command for SetOutputSettings')
    def SetTemporaryBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TemporaryBrightnessCmdString = b'\x80\x11\x22\x33\x44' + bytes([value]) + (b'\x00' * 8)
            self.__SetHelper('TemporaryBrightness', TemporaryBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemporaryBrightness')

    def SetTemporarySwitchScreen(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
        }

        TemporarySwitchScreenCmdString = b'\x81\x11\x22\x33\x44' + ValueStateValues[value] + b'\x00\x00'
        self.__SetHelper('TemporarySwitchScreen', TemporarySwitchScreenCmdString, value, qualifier)
    def UpdateVersion(self, value, qualifier):

        VersionCmdString = b'\xAA\x44' + (b'\x00' * 260)
        res = self.__UpdateHelper('Version', VersionCmdString, value, qualifier)
        if res:
            try:
                states = {
                    b'\x01': 'On',
                    b'\x00': 'Off'
                }

                value = states[res[42:43]]
                self.WriteStatus('BigPackageModeStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Big Package Mode Status: Invalid/unexpected response'])
            try:
                value = res[57]
                self.WriteStatus('Contrast', value, qualifier)
            except IndexError:
                self.Error(['Contrast: Invalid/unexpected response'])
            try:
                states = {
                    b'\x01': 'Display',
                    b'\x00': 'No Display'
                }

                value = states[res[36:37]]
                self.WriteStatus('Display', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display: Invalid/unexpected response'])
            try:
                states = {
                    30:     '30',
                    60:     '60',
                    120:    '120'
                }

                value = states[res[59]]
                self.WriteStatus('FrameRate', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Frame Rate: Invalid/unexpected response'])
            try:
                value = res[38]
                self.WriteStatus('Luminance', value, qualifier)
            except IndexError:
                self.Error(['Luminance: Invalid/unexpected response'])
            try:
                value = int.from_bytes(res[53:57], byteorder='big') // 60
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError, TypeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])
            try:
                columns = int.from_bytes(res[68:70], byteorder='big')
                rows = int.from_bytes(res[70:72], byteorder='big')
                value = '{}x{}'.format(columns, rows)

                self.WriteStatus('Resolution', value, qualifier)
            except (ValueError, IndexError, TypeError):
                self.Error(['Resolution: Invalid/unexpected response'])
            try:
                major = res[2]
                minor = res[3]
                value = '{}.{}'.format(major, minor)

                self.WriteStatus('Version', value, qualifier)
            except IndexError:
                self.Error(['Version: Invalid/unexpected response'])
            try:
                states = {
                    b'\x01': 'Virtual',
                    b'\x00': 'Real'
                }

                value = states[res[39:40]]
                self.WriteStatus('VirtualPixelMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Virtual Pixel Mode: Invalid/unexpected response'])

            offset = 4

            for q in ['1', '2', '3', '4']:
                try:
                    value = int.from_bytes(res[offset + 6:offset + 8], byteorder='little')
                    self.WriteStatus('ColumnLength', value, {'Ethernet Port': q})
                except (ValueError, IndexError, TypeError):
                    self.Error(['Column Length: Invalid/unexpected response'])

                try:
                    value = int.from_bytes(res[offset + 4:offset + 6], byteorder='little')
                    self.WriteStatus('ColumnStartingPoint', value, {'Ethernet Port': q})
                except (ValueError, IndexError, TypeError):
                    self.Error(['Column Starting Point: Invalid/unexpected response'])

                try:
                    value = int.from_bytes(res[offset + 2:offset + 4], byteorder='little')
                    self.WriteStatus('RowHeight', value, {'Ethernet Port': q})
                except (ValueError, IndexError, TypeError):
                    self.Error(['Row Height: Invalid/unexpected response'])
                try:
                    value = int.from_bytes(res[offset:offset + 2], byteorder='little')
                    self.WriteStatus('RowStartingPort', value, {'Ethernet Port': q})
                except (ValueError, IndexError, TypeError):
                    self.Error(['Row Starting Port: Invalid/unexpected response'])
                offset += 8

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        elif command in {'TemporaryBrightness', 'TemporarySwitchScreen'}:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self._set_regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

            return res

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
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self._rp_regex)
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

