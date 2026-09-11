from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import math
import re
import binascii


class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStep': {'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\xA0\xF0\x55\xFF\x14\xEB'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA0\xF0\x55\xFF\x55\xAA',
            'Down': b'\xA0\xF0\x55\xFF\x5A\xA5'
        }

        ChannelStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': b'\xA0\xF0\x55\xFF\xED\x12',
            'VGA': b'\xA0\xF0\x55\xFF\xEA\x15',
            'HDMI 1': b'\xA0\xF0\x55\xFF\xEC\x13',
            'HDMI 2': b'\xA0\xF0\x55\xFF\xE1\x1E',
            'HDMI 3': b'\xA0\xF0\x55\xFF\xE3\x1C',
            'S-Video': b'\xA0\xF0\x55\xFF\xE4\x1B',
            'TV': b'\xA0\xF0\x55\xFF\xE8\x17',
            'DTV': b'\xA0\xF0\x55\xFF\xE9\x16',
            'Component': b'\xA0\xF0\x55\xFF\xE7\x18',
            'USB': b'\xA0\xF0\x55\xFF\x57\xA8'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xA0\xF0\x55\xFF\x56\xA9',
            '1': b'\xA0\xF0\x55\xFF\x32\xBD',
            '2': b'\xA0\xF0\x55\xFF\x43\xBC',
            '3': b'\xA0\xF0\x55\xFF\x0F\xF0',
            '4': b'\xA0\xF0\x55\xFF\x1E\xE1',
            '5': b'\xA0\xF0\x55\xFF\x1D\xE2',
            '6': b'\xA0\xF0\x55\xFF\x1C\xE3',
            '7': b'\xA0\xF0\x55\xFF\x18\xE7',
            '8': b'\xA0\xF0\x55\xFF\x45\xBA',
            '9': b'\xA0\xF0\x55\xFF\x4C\xB3'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xA0\xF0\x55\xFF\x4E\xB1',
            'Up': b'\xA0\xF0\x55\xFF\x17\xE8',
            'Down': b'\xA0\xF0\x55\xFF\x0D\xF2',
            'Left': b'\xA0\xF0\x55\xFF\x0C\xF3',
            'Right': b'\xA0\xF0\x55\xFF\x05\xFA',
            'OK': b'\xA0\xF0\x55\xFF\x02\xFD',
            'Exit': b'\xA0\xF0\x55\xFF\x1B\xE4'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0\xF0\x55\xFF\xAE\x51',
            'Off': b'\xA0\xF0\x55\xFF\xAF\x50'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            '25': b'\xA0\xF0\x55\xFF\x21\xDE',
            '50': b'\xA0\xF0\x55\xFF\x22\xDD',
            '75': b'\xA0\xF0\x55\xFF\x23\xDC',
            '100': b'\xA0\xF0\x55\xFF\x24\xDB'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xA0\xF0\x55\xFF\x0A\xF5',
            'Down': b'\xA0\xF0\x55\xFF\x40\xBF'
        }

        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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


class DeviceUDPClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Writecommunity = 'private'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Humidity': {'Status': {}},
            'Relay12V': {'Status': {}},
            'Relay5V': {'Status': {}},
            'Temperature1': {'Status': {}},
            'Temperature2': {'Status': {}},
            'Temperature3': {'Status': {}},
        }

        self.CommandOIDDict = {
            'Humidity': '1.3.6.1.4.1.19865.3.1.0',
            'Relay12V': '1.3.6.1.4.1.19865.5.1.0',
            'Relay5V': '1.3.6.1.4.1.19865.5.2.0',
            'Temperature1': '1.3.6.1.4.1.19865.2.1.0',
            'Temperature2': '1.3.6.1.4.1.19865.2.2.0',
            'Temperature3': '1.3.6.1.4.1.19865.2.3.0'
        }


    @property
    def Writecommunity(self):
        return self._Writecommunity

    @Writecommunity.setter
    def Writecommunity(self, value):
        self._Writecommunity = value
        self.SNMP = SNMPDevice(self._Writecommunity, self.CommandOIDDict)

    def UpdateHumidity(self, value, qualifier):

        res = self.__UpdateHelper('Humidity', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('Humidity', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Humidity: Invalid/unexpected response'])

    def SetRelay12V(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        self.__SetHelper('Relay12V', ValueStateValues[value], qualifier)

    def UpdateRelay12V(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        res = self.__UpdateHelper('Relay12V', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Relay12V', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Relay12V: Invalid/unexpected response'])

    def SetRelay5V(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        self.__SetHelper('Relay5V', ValueStateValues[value], qualifier)

    def UpdateRelay5V(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        res = self.__UpdateHelper('Relay5V', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Relay5V', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Relay5V: Invalid/unexpected response'])

    def UpdateTemperature1(self, value, qualifier):

        res = self.__UpdateHelper('Temperature1', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('Temperature1', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Temperature 1: Invalid/unexpected response'])

    def UpdateTemperature2(self, value, qualifier):

        res = self.__UpdateHelper('Temperature2', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('Temperature2', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Temperature 2: Invalid/unexpected response'])

    def UpdateTemperature3(self, value, qualifier):

        res = self.__UpdateHelper('Temperature3', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('Temperature3', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Temperature 3: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1: "Response message too large to transport",
            2: "The name of the requested object was not found",
            3: "A data type in the request did not match the data type in the SNMP agent",
            4: "The SNMP manager attempted to set a read-only parameter",
            5: "General Error",
            6: "The specified SNMP variable is not accessible.",
            7: "The value specifies a type that is inconsistent with the type required for the variable.",
            8: "The value specifies a length that is inconsistent with the length required for the variable.",
            9: "The value contains an Abstract Syntax Notation One (ASN.1) encoding that is inconsistent with the ASN.1 tag of the field.",
            10: "The value cannot be assigned to the variable.",
            11: "The variable does not exist, and the agent cannot create it.",
            12: "The value is inconsistent with values of other managed objects.",
            13: "Assigning the value to the variable requires allocation of resources that are currently unavailable.",
            14: "No validation errors occurred, but no variables were updated.",
            15: "No validation errors occurred. Some variables were updated because it was not possible to undo their assignment.",
            16: "An authorization error occurred.",
            17: "The variable exists but the agent cannot modify it.",
            18: "The variable does not exist; the agent cannot create it because the named object instance is inconsistent with the values of other managed objects."
        }

        if response[0] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0]])])
            response = ''
        else:
            response = response[1]

        return response

    def __SetHelper(self, command, value, qualifier):
        self.Debug = True
        commandstring = self.SNMP.encodeMsg('Set', command, value)
        self.Send(commandstring)

    def __UpdateHelper(self, command, value, qualifier):

        commandstring = self.SNMP.encodeMsg('Get', command)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                resDecode = self.SNMP.decodeMsg(res, command)
                return self.__CheckResponseForErrors(command, resDecode)

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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


class SNMPDeviceException(Exception):
    pass


class SNMPDevice:

    def __init__(self, community, CommandOIDDict):

        self.community = community
        self.CommandOIDDict = CommandOIDDict
        self.oidList = {}
        for command in CommandOIDDict:
            self.oidList[command] = self.__BuildOID(self.CommandOIDDict[command])
        self.community = community
        self.communityString = b'\x04' + pack('>B', len(self.community)) + self.community.encode()
        self.GetNext = False

    def addOID(self, command, oid):

        if command in self.oidList:
            raise SNMPDeviceException('Command/UID already associated with a different OID')
        self.oidList[command] = self.__BuildOID(oid)

    def getOID(self, command):

        if command not in self.oidList:
            raise SNMPDeviceException('Command/UID not in OID List of the device')
        return self.__RebuildOIDString(self.oidList[command])

    def decodeOID(self, msg, command=None, OID=None):

        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if OID is None and command is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')
        try:
            if OID is not None:
                oidIndex = msg.index(self.__BuildOID(OID))
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex - 1]
            OID = msg[oidIndex: oidIndex + oidLength]
            value = self.__RebuildOIDString(OID)
            return value
        except ValueError:
            raise SNMPDeviceException('OID for that command/UID not found in the message')

    def encodeMsg(self, queryType, command=None, value=None, OID=None):

        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
        }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04' + pack('>B', valueLen) + valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:]) / 2) * 2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02' + pack('>B', valueLen) + valueBytes
            else:
                raise TypeError('Value is not of type int or string')
        else:
            valueMsg = b'\x05\x00'

        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
            else:
                oid = self.oidList[command]
        else:
            oid = self.nextOID
            self.GetNext = False
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x00'
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(requestID + error + errorIndex + varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(snmpVersion + self.communityString + snmpPduMsg)) + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg

    def encodeMsgMultiOID(self, queryType, command=None, value=None, OID=None, NextOID=None):  ## 06/10/15

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
        }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04' + pack('>B', valueLen) + valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:]) / 2) * 2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02' + pack('>B', valueLen) + valueBytes
            else:
                pass
        else:
            valueMsg = b'\x05\x00'

        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
        else:
            oid = self.nextOID
            self.GetNext = False

        varbindListMsg = b''
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x00'
        pduType = typeDict[queryType]
        for command2do in command:
            if NextOID:
                oid = self.oidList[command2do] + pack('>B', NextOID)
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
            varbindListMsg += varbindMsg
        if len(varbindListMsg) < 128:
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg
        elif len(varbindListMsg) < 4096:
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg)) + varbindListMsg

        pduLen = len(requestID + error + errorIndex + varbindListMsg)
        if pduLen < 128:
            pduLenMsg = pack('>B', pduLen)
        elif pduLen < 4096:
            pduLenMsg = b'\x81' + pack('>B', pduLen)

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg

        snmpLen = len(snmpVersion + self.communityString + snmpPduMsg)
        if snmpLen < 128:
            snmpLenMsg = pack('>B', snmpLen)
        elif snmpLen < 4096:
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg

    def decodeMsg(self, msg, command=None, OID=None):

        ValueTypeDict = {
            2: 'Integer',
            4: 'Octet String',
            5: 'Null',
            6: 'OID',
            64: 'IPAdddress',
            65: 'Counter32',
            66: 'Gauge',
            67: 'Timeticks',
            68: 'Opaque',
            69: 'NsapAddress',
            70: 'Counter64',
        }

        oidIndex = -1
        valueType = '???'

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. You must specify at least one')

        try:
            if OID is not None:
                cutomOIDHex = self.__BuildOID(OID)
                oidIndex = msg.index(cutomOIDHex)
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex - 1]
            self.nextOID = msg[oidIndex: oidIndex + oidLength]
            valueIndex = oidIndex + oidLength
            valueType = ValueTypeDict[msg[valueIndex]]
            valueLen = msg[valueIndex + 1]
            if valueType == 'Octet String':
                value = msg[valueIndex + 2:valueIndex + 2 + valueLen].decode()
            elif valueType == 'Null':
                value = None
            elif valueType in ['Integer', 'Timeticks', 'Counter32', 'Gauge']:
                valueBytes = msg[valueIndex + 2:valueIndex + 2 + valueLen]
                value = int(binascii.hexlify(valueBytes), 16)
            elif valueType == 'OID':
                value = self.__RebuildOIDString(msg[valueIndex + 2:valueIndex + 2 + valueLen])
            elif valueType == 'IPAdddress':
                valueBytes = msg[valueIndex + 2:valueIndex + 2 + valueLen]
                ipAddress = [byte for byte in valueBytes]
                value = '.'.join([str(i) for i in ipAddress])
            error = self.__DecodeError(msg)
            if OID is not None:
                oidCheck = self.nextOID != cutomOIDHex
            else:
                oidCheck = self.nextOID != self.oidList[command]
            if oidCheck and error == 0:
                self.GetNext = True
                return error, value, self.encodeMsg('Get-Next', command=command)
            return error, value
        except ValueError:
            pass
        except KeyError:
            pass

    def __DecodeError(self, msg):

        try:
            pduIndex = msg.index(self.community.encode()) + len(self.community.encode())
            requestIdIndex = pduIndex + 2
            ErrorIndex = requestIdIndex + 2 + msg[requestIdIndex + 1]
            error = msg[ErrorIndex + 2]
            return error
        except ValueError:
            pass

    def __BuildOID(self, oidValue):

        try:
            oidValueNumberList = [int(i) for i in oidValue.split('.')]
        except ValueError:
            raise SNMPDeviceException('OIDs supplied is of invalid type/format')

        oid = pack('>B', 40 * oidValueNumberList[0] + oidValueNumberList[1])
        for number in oidValueNumberList[2:]:
            if number < 128:
                oid += pack('>B', number)
            else:
                oid += self.__ConvertToMultipleBytes(number)
        return oid

    def __ConvertToMultipleBytes(self, number):

        binaryNumberSplit = re.findall('[0-1]{7}', bin(number)[2:].zfill(math.ceil(len(bin(number)[2:]) / 7) * 7))
        return pack('>' + 'B' * len(binaryNumberSplit), *[int(i, 2) if e == len(binaryNumberSplit) - 1 else int(i, 2) + 0x80 for e, i in enumerate(binaryNumberSplit)])

    def __RebuildOIDString(self, oidBytes):

        if oidBytes[0] == 43:
            oid = [1, 3]
        else:
            oid = [0, 0]
        highBitCheck = False
        oidbin = ''
        for byte in oidBytes[1:]:
            if byte < 127:
                if highBitCheck:
                    oidbin += bin(byte)[2:].zfill(7)
                    oid.append(int(oidbin, 2))
                    oidbin = ''
                    highBitCheck = False
                else:
                    oid.append(byte)
            else:
                oidbin += bin(byte - 0x80)[2:].zfill(7)
                highBitCheck = True
        return '.'.join([str(i) for i in oid])


class DeviceTCPClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'KeyLock': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Relay12V': {'Status': {}},
            'Relay5V': {'Status': {}},
            'VolumeStep': {'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x02RC000MUT_\x03'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': 'VGA',
            'HDMI 1': 'HD1',
            'HDMI 2': 'HD2',
            'HDMI 3': 'HD3',
            'DisplayPort': '-DP',
            'USB': 'USB'
        }

        InputCmdString = '\x02RC000{}_\x03'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeyLock(self, value, qualifier):

        ValueStateValues = {
            'On': 'N',
            'Off': 'F'
        }

        KeyLockCmdString = '\x02RC000KL{}_\x03'.format(ValueStateValues[value])
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'MEN',
            'Up': '-UP',
            'Down': 'DOW',
            'Left': 'LEF',
            'Right': 'RIG',
            'OK': '-OK',
            'Exit': 'EXI'
        }

        MenuNavigationCmdString = '\x02RC000{}_\x03'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '-ON',
            'Off': 'OFF'
        }

        PowerCmdString = '\x02RC000{}_\x03'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRelay12V(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Relay12VCmdString = '\x02RC000P1{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Relay12V', Relay12VCmdString, value, qualifier)

    def SetRelay5V(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Relay5VCmdString = '\x02RC000P2{}\x03'.format(ValueStateValues[value])
        self.__SetHelper('Relay5V', Relay5VCmdString, value, qualifier)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'VO+',
            'Down': 'VO-'
        }

        VolumeStepCmdString = '\x02RC000{}_\x03'.format(ValueStateValues[value])
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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


class TCPClass(EthernetClientInterface, DeviceTCPClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceTCPClass.__init__(self)
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


class UDPClass(EthernetClientInterface, DeviceUDPClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceUDPClass.__init__(self)
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
