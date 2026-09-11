from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re


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
        self._DeviceID = 1
        self._GroupID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoAdjust': {'Status': {}},
            'Input': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPInputQuadrant2': {'Status': {}},
            'PIPInputQuadrant3': {'Status': {}},
            'PIPInputQuadrant4': {'Status': {}},
            'PIPMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.UpdateRegex = re.compile(b'([\x06-\x09])([\x00-\xFF])([\x00-\xFF])([\x00-\xFF]{3})')
        self.UpdateRegexPIP = re.compile(b'\x09([\x00-\xFF])([\x00-\xFF])\x85([\x00-\xFF]{5})')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 255:
            self._DeviceID = int(value)
        else:
            self.Error(['Device ID should be a value between 1 to 255 or Broadcast.'])

    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if value == 'Broadcast':
            self._GroupID = 0
        elif 1 <= int(value) <= 255:
            self._GroupID = int(value)
        else:
            self.Error(['Group ID should be a value between 1 to 255 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Normal': 0,
            'Custom': 1,
            'Real': 2,
            'Full': 3,
            '21:9': 4,
            'Dynamic': 5,
            '16:9': 6,
        }

        checksum = 0x06 ^ self._DeviceID ^ self._GroupID ^ 0x3A ^ AspectRatioStateValues[value]
        AspectRatioCmdString = pack('>6B', 6, self._DeviceID, self._GroupID, 0x3A, AspectRatioStateValues[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Custom',
            b'\x02': 'Real',
            b'\x03': 'Full',
            b'\x04': '21:9',
            b'\x05': 'Dynamic',
            b'\x06': '16:9',
        }

        checksum = 0x05 ^ self._DeviceID ^ self._GroupID ^ 0x3B
        AspectRatioCmdString = pack('>5B', 5, self._DeviceID, self._GroupID, 0x3B, checksum)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoAdjust(self, value, qualifier):

        checksum = 0x07 ^ self._DeviceID ^ self._GroupID ^ 0x70 ^ 0x40
        AutoAdjustCmdString = pack('>7B', 7, self._DeviceID, self._GroupID, 0x70, 0x40, 0x00, checksum)
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVI-D': (0x0E, 0),
            'DisplayPort': (0x0A, 0),
            'Component': (0x03, 0),
            'VGA': (0x05, 0),
            'HDMI 1': (0x0D, 0),
            'HDMI 2': (0x06, 0),
            'HDMI 3': (0x0F, 0),
            'USB': (0x0C, 0),
            'Browser': (0x10, 0),
            'SmartCMS': (0x11, 0),
            'Card OPS': (0x0B, 0),
            'Video': (0x01, 0),
        }
        checksum = 0x09 ^ self._DeviceID ^ self._GroupID ^ 0xAC ^ ValueStateValues[value][0] ^ ValueStateValues[value][1] ^ 1 ^ 0
        InputCmdString = pack('>9B', 9, self._DeviceID, self._GroupID, 0xAC, ValueStateValues[value][0], ValueStateValues[value][1], 1, 0, checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x0E: 'DVI-D',
            0x0A: 'DisplayPort',
            0x03: 'Component',
            0x05: 'VGA',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0C: 'USB',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x0B: 'Card OPS',
            0x01: 'Video',
        }

        checksum = 0x05 ^ self._DeviceID ^ self._GroupID ^ 0xAD
        InputCmdString = pack('>5B', 5, self._DeviceID, self._GroupID, 0xAD, checksum)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'DVI-D': 0x0E,
            'Component': 0x03,
            'VGA': 0x05,
            'DisplayPort': 0x0A,
            'HDMI 1': 0x0D,
            'HDMI 2': 0x06,
            'HDMI 3': 0x0F,
            'USB': 0x0C,
            'Browser': 0x10,
            'SmartCMS': 0x11,
            'Card OPS': 0x0B,
            'Video': 0x01,
        }

        q2 = qualifier['Quadrant 2']
        q3 = qualifier['Quadrant 3']
        q4 = qualifier['Quadrant 4']

        if q2 in ValueStateValues and q3 in ValueStateValues and q4 in ValueStateValues:
            checksum = 0x09 ^ self._DeviceID ^ self._GroupID ^ 0x84 ^ 0xFD ^ ValueStateValues[q2] ^ ValueStateValues[q3] ^ ValueStateValues[q4]
            PIPInputCmdString = pack('>9B', 9, self._DeviceID, self._GroupID, 0x84, 0xFD, ValueStateValues[q2], ValueStateValues[q3], ValueStateValues[q4], checksum)
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInputQuadrant2(self, value, qualifier):

        ValueStateValues = {
            0x0E: 'DVI-D',
            0x0A: 'DisplayPort',
            0x03: 'Component',
            0x05: 'VGA',
            0x0D: 'HDMI 1',
            0x06: 'HDMI 2',
            0x0F: 'HDMI 3',
            0x0C: 'USB',
            0x10: 'Browser',
            0x11: 'SmartCMS',
            0x0B: 'Card OPS',
            0x01: 'Video'
        }

        checksum = 0x05 ^ self._DeviceID ^ self._GroupID ^ 0x85
        PIPInputQuadrant2CmdString = pack('>5B', 5, self._DeviceID, self._GroupID, 0x85, checksum)
        res = self.__UpdateHelper('PIPInputQuadrant2', PIPInputQuadrant2CmdString, value, qualifier)

        if res:
            try:
                self.WriteStatus('PIPInputQuadrant2', ValueStateValues[res[-4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Quadrant 2: Invalid/unexpected response'])

            try:
                self.WriteStatus('PIPInputQuadrant3', ValueStateValues[res[-3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Quadrant 3: Invalid/unexpected response'])

            try:
                self.WriteStatus('PIPInputQuadrant4', ValueStateValues[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Quadrant 4: Invalid/unexpected response'])

    def UpdatePIPInputQuadrant3(self, value, qualifier):
        self.UpdatePIPInputQuadrant2(value, qualifier)

    def UpdatePIPInputQuadrant4(self, value, qualifier):
        self.UpdatePIPInputQuadrant2(value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP Bottom-Left': 0x00,
            'PIP Top-Left': 0x01,
            'PIP Top-Right': 0x02,
            'PIP Bottom-Right': 0x03,
            'PIP Center': 0x04,
            'Off': 0x00,
            'PBP 2win': 0x04,
            'PBP 3win': 0x05,
            'PBP 4win': 0x06,
            'POP': 0x02,
            'Quick swap': 0x03,
        }
        if value in ValueStateValues:
            if value[0:3] == 'PIP':
                checksum = 0x09 ^ self._DeviceID ^ self._GroupID ^ 0x3C ^ 0x01 ^ ValueStateValues[value] ^ 0x00 ^ 0x00
                PIPModeCmdString = pack('>9B', 9, self._DeviceID, self._GroupID, 0x3C, 0x01, ValueStateValues[value], 0x00, 0x00, checksum)
            else:
                checksum = 0x09 ^ self._DeviceID ^ self._GroupID ^ 0x3C ^ ValueStateValues[value] ^ 0x00 ^ 0x00 ^ 0x00
                PIPModeCmdString = pack('>9B', 9, self._DeviceID, self._GroupID, 0x3C, ValueStateValues[value], 0x00, 0x00, 0x00, checksum)

            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        PIPValueStateValues = {
            0x00: 'PIP Bottom-Left',
            0x01: 'PIP Top-Left',
            0x02: 'PIP Top-Right',
            0x03: 'PIP Bottom-Right',
            0x04: 'PIP Center',
        }
        ValueStateValues = {
            0x00: 'Off',
            0x04: 'PBP 2win',
            0x05: 'PBP 3win',
            0x06: 'PBP 4win',
            0x02: 'POP',
            0x03: 'Quick swap'
        }

        checksum = 0x05 ^ self._DeviceID ^ self._GroupID ^ 0x3D
        PIPModeCmdString = pack('>5B', 5, self._DeviceID, self._GroupID, 0x3D, checksum)
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                if res[-2] == 1:
                    value = PIPValueStateValues[res[-1]]
                else:
                    value = ValueStateValues[res[-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 2,
            'Off': 1,
        }

        checksum = 0x06 ^ self._DeviceID ^ self._GroupID ^ 0x18 ^ ValueStateValues[value]
        PowerCmdString = pack('>6B', 6, self._DeviceID, self._GroupID, 0x18, ValueStateValues[value], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x01': 'Off'
        }

        checksum = 0x05 ^ self._DeviceID ^ self._GroupID ^ 0x19
        PowerCmdString = pack('>5B', 5, self._DeviceID, self._GroupID, 0x19, checksum)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 254
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            checksum = 0x06 ^ self._DeviceID ^ self._GroupID ^ 0x44 ^ value
            VolumeCmdString = pack('>6B', 6, self._DeviceID, self._GroupID, 0x44, int(value), checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = 0x05 ^ self._DeviceID ^ self._GroupID ^ 0x45
        VolumeCmdString = pack('>5B', 5, self._DeviceID, self._GroupID, 0x45, checksum)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }
        if response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or (self._DeviceID == 0 and self._GroupID == 0):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or (self._DeviceID == 0 and self._GroupID == 0):
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if command != 'PIPInputQuadrant2':
                tempRex = self.UpdateRegex
            else:
                tempRex = self.UpdateRegexPIP
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=tempRex)
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
