from extronlib.interface import EthernetClientInterface, SerialInterface
from struct import pack
import math
import re
import binascii


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
        self._DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'InputSignal': {'Status': {}},
            'InputSource': {'Status': {}},
            'LandscapeMode': {'Status': {}},
            'Power': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        try:
            if value == 'Broadcast':
                self._DeviceID = 255
            elif 1 <= int(value) <= 254:
                self._DeviceID = int(value)
            else:
                print('Invalid Device ID')
        except:
            print('Invalid Device ID format provide: {}'.format(value))

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x40, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2])
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateBrightness')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ContrastCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x46, value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            print('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x46, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2])
                self.WriteStatus('Contrast', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateContrast')

    def SetInputSource(self, value, qualifier):

        ValueStateValues = {
            'DP': 0x80,
            'DVI': 0x00
        }

        InputSourceCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x38, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
        self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)

    def UpdateInputSource(self, value, qualifier):

        ValueStateValues = {
            0x80: 'DP',
            0x00: 'DVI'
        }

        InputSourceCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('InputSource', InputSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('InputSource', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInputSource')

    def SetLandscapeMode(self, value, qualifier):

        ValueStateValues = {
            'Landscape': 0x80,
            'Portrait': 0x00
        }

        LandscapeModeCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x5C, ValueStateValues[value], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA)
        self.__SetHelper('LandscapeMode', LandscapeModeCmdString, value, qualifier)

    def UpdateLandscapeMode(self, value, qualifier):

        ValueStateValues = {
            0x80: 'Landscape',
            0x00: 'Portrait'
        }

        LandscapeModeCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x5C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xAA)
        res = self.__UpdateHelper('LandscapeMode', LandscapeModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('LandscapeMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLandscapeMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0xFF,
            'Off': 0x7F
        }

        PowerCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x54, ValueStateValues[value], 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0xAA)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x80: 'On',
            0xA0: 'On',
            0x00: 'Off',
            0x20: 'Off'
        }

        PowerCmdString = pack('>BBBBBBBBBB', self._DeviceID, 0x4E, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xAA)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                if res[5] == 0x80 or res[5] == 0x00:
                    self.WriteStatus('InputSignal', 'Present', qualifier)
                else:
                    self.WriteStatus('InputSignal', 'No Input', qualifier)
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 255:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                return self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
    
        if self.Unidirectional == 'True' or self._DeviceID == 255:
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=10)
            return res if res else ''

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
        self.Debug = False
        self.Models = {}
        self._Community = 'public'

        self.Commands = {
            'InputSource': {'Status': {}},
            'LandscapeMode': {'Status': {}},
            'Power': {'Status': {}},
        }

        self.CommandDicIO = {
            'InputSource': '1.3.6.1.4.1.44268.1.129',
            'LandscapeMode': '1.3.6.1.4.1.44268.1.123',
            'Power': '1.3.6.1.4.1.44268.1.101',
        }

        self.SNMP = SNMPDevice(self._Community, self.CommandDicIO, 1)

    @property
    def Community(self):
        return self._Community

    @Community.setter
    def Community(self, value):
        self._Community = value
        self.SNMP = SNMPDevice(self._Community, self.CommandDicIO, 1)

    def SetInputSource(self, value, qualifier):

        ValueStateValues = {
            'DP': 'Main Source:DP',
            'DVI': 'Main Source:DVI'
        }

        InputSourceCmdString = ValueStateValues[value]
        self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)

    def SetLandscapeMode(self, value, qualifier):

        ValueStateValues = {
            'Landscape': 'Display Mode:PORTRAIT',
            'Portrait': 'Display Mode:LANDSCAPE'
        }

        LandscapeModeCmdString = ValueStateValues[value]
        self.__SetHelper('LandscapeMode', LandscapeModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'Power:ON',
            'Off': 'Power:OFF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

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
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0]]))
            response = ''
        else:
            response = response[1]
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        commandstring = self.SNMP.encodeMsg('Set', command, value)
        self.Send(commandstring)

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


class SNMPDeviceException(Exception):
    pass


class SNMPDevice:

    def __init__(self, community, CommandOIDDict, version=2):

        self.community = community
        self.oidList = {}
        for command in CommandOIDDict:
            self.oidList[command] = self.__BuildOID(CommandOIDDict[command])
        self.community = community
        self.communityString = b'\x04' + pack('>B', len(self.community)) + self.community.encode()
        self.GetNext = False
        versionDict = {
            1: b'\x00',
            2: b'\x01'
        }
        self.versionBytes = versionDict[version]

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
        snmpVersion = b'\x02\x01' + self.versionBytes
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(requestID + error + errorIndex + varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(snmpVersion + self.communityString + snmpPduMsg)) + snmpVersion + self.communityString + snmpPduMsg
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
            129: 'No Such Instance'
        }

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
            elif valueType == 'No Such Instance':
                raise SNMPDeviceException('SNMP error - No Such Instance')
            error = self.__DecodeError(msg)
            if OID is not None:
                oidCheck = self.nextOID != cutomOIDHex
            else:
                oidCheck = self.nextOID != self.oidList[command]
            if oidCheck and error == 0:
                self.GetNext = True
                return (error, value, self.encodeMsg('Get-Next', command=command))
            return (error, value)
        except ValueError:
            raise SNMPDeviceException('OID for that command/UID not found in the message')
        except KeyError:
            raise SNMPDeviceException('The return type of value in the message is not in the list: [Integer|String|Null]')

    def __DecodeError(self, msg):

        try:
            pduIndex = msg.index(self.community.encode()) + len(self.community.encode())
            requestIdIndex = pduIndex + 2
            ErrorIndex = requestIdIndex + 2 + msg[requestIdIndex + 1]
            error = msg[ErrorIndex + 2]
            return error
        except ValueError:
            raise SNMPDeviceException('Error in retriving error bytes from message, message is incomplete or not fully formed.')

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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
