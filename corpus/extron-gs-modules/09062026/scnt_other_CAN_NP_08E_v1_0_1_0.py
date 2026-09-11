from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import math
import re
import binascii


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
        self._DeviceID = '1'
        self._Writecommunity = 'private'
        self._Readcommunity = 'public'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'SwitchMode': {'Parameters': ['Outlet'], 'Status': {}},
            }

        self.CommandOIDDict = {
            'Outlet 1': '1.3.6.1.4.1.2.{}.3.1.4.0'.format(self.DeviceID),
            'Outlet 2': '1.3.6.1.4.1.2.{}.3.2.4.0'.format(self.DeviceID),
            'Outlet 3': '1.3.6.1.4.1.2.{}.3.3.4.0'.format(self.DeviceID),
            'Outlet 4': '1.3.6.1.4.1.2.{}.3.4.4.0'.format(self.DeviceID),
            'Outlet 5': '1.3.6.1.4.1.2.{}.3.5.4.0'.format(self.DeviceID),
            'Outlet 6': '1.3.6.1.4.1.2.{}.3.6.4.0'.format(self.DeviceID),
            'Outlet 7': '1.3.6.1.4.1.2.{}.3.7.4.0'.format(self.DeviceID),
            'Outlet 8': '1.3.6.1.4.1.2.{}.3.8.4.0'.format(self.DeviceID),
            }        
        
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1<= int(value) <= 10:
            self._DeviceID = value

    @property
    def Writecommunity(self):
        return self._Writecommunity

    @Writecommunity.setter
    def Writecommunity(self, value):
        self._Writecommunity = value
        self.SNMP_Set = SNMPDevice(self._Writecommunity, self.CommandOIDDict)

    @property
    def Readcommunity(self):
        return self._Readcommunity

    @Readcommunity.setter
    def Readcommunity(self, value):
        self._Readcommunity = value
        self.SNMP_Get = SNMPDevice(self._Readcommunity, self.CommandOIDDict)   

    def SetSwitchMode(self, value, qualifier):

        OutletStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01
        }

        outletValue = qualifier['Outlet']
        if outletValue in OutletStates and value in ValueStateValues:
            SwitchModeCmdString = self.SNMP_Set.encodeMsg('Set', 'Outlet {}'.format(OutletStates[outletValue]), ValueStateValues[value])
            self.__SetHelper('SwitchMode', SwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchMode')

    def UpdateSwitchMode(self, value, qualifier):

        OutletStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueStateValues = {
            0x00: 'On',
            0x01: 'Off'
        }

        outletValue = qualifier['Outlet']
        if outletValue in OutletStates:
            SwitchModeCmdString = self.SNMP_Get.encodeMsg('Get', 'Outlet {}'.format(OutletStates[outletValue]))
            res = self.__UpdateHelper('SwitchMode', SwitchModeCmdString, value, qualifier, 'Outlet {}'.format(OutletStates[outletValue]))
            if res:
                try:
                    value = ValueStateValues[res[1]]
                    self.WriteStatus('SwitchMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Switch Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSwitchMode')

    def __CheckResponseForErrors(self, sourceCmdName, response, checkrescmdname=None):

        if checkrescmdname:
            response = self.SNMP_Get.decodeMsg(response, command=checkrescmdname)
        else:
            response = self.SNMP_Get.decodeMsg(response, command=sourceCmdName)  
        if response[0] != 0:
            if checkrescmdname:
                self.Error(['Error : {0} {1}.'.format(sourceCmdName, checkrescmdname)])
            else:
                self.Error(['Error : {0}.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)
        print(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier, checkrescmdname=None):

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
            print(commandstring)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res, checkrescmdname)            

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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

class SNMPDeviceException(Exception):
    pass

class SNMPDevice():
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
                if valueLen < 2:  # fix to make Int32        11/03/14
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
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(requestID + error + errorIndex + varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(snmpVersion + self.communityString + snmpPduMsg)) + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg

    def encodeMsgMultiOID(self, queryType, command=None, value=None, OID=None, NextOID=None):  # 06/10/15


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
                if valueLen < 2:  # fix to make Int32        11/03/14
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

        varbindListMsg = b''  # 6/10/15
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        for command2do in command:  # --------------------------------
            if NextOID:
                oid = self.oidList[command2do] + pack('>B', NextOID)  # 6/10/15
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
            varbindListMsg += varbindMsg  # accumulate OIDs
        if len(varbindListMsg) < 128:  # 6/10/15
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg  # 6/10/15
        elif len(varbindListMsg) < 4096:  # 6/10/15
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg)) + varbindListMsg  # 6/10/15

        pduLen = len(requestID + error + errorIndex + varbindListMsg)  # 6/10/15
        if pduLen < 128:  # 6/10/15
            pduLenMsg = pack('>B', pduLen)  # 6/10/15
        elif pduLen < 4096:  # 6/10/15
            pduLenMsg = b'\x81' + pack('>B', pduLen)  # 6/10/15

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg  # 6/10/15

        snmpLen = len(snmpVersion + self.communityString + snmpPduMsg)  # 6/10/15
        if snmpLen < 128:  # 6/10/15
            snmpLenMsg = pack('>B', snmpLen)  # 6/10/15
        elif snmpLen < 4096:  # 6/10/15
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)  # 6/10/15

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg  # 6/10/15
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

        oidIndex = -1  # temp 6/10/15
        valueType = '???'  # temp 6/10/15

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
                return (error, value, self.encodeMsg('Get-Next', command=command))
            return (error, value)
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
