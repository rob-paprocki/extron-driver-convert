from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
from binascii import hexlify, unhexlify

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
            'AnalogValue': {'Parameters': ['InstanceNumber', 'Precision', 'Priority'], 'Status': {}},
            'AnalogValueCompare': {'Parameters': ['InstanceNumberLeft', 'Operator', 'InstanceNumberRight', 'Priority'], 'Status': {}},
            'AnalogValueComparetoNumber': {'Parameters': ['InstanceNumberLeft', 'CompareTo', 'Operator', 'Priority'], 'Status': {}},
            'AnalogValueRange': {'Parameters': ['InstanceNumber', 'Priority'], 'Status': {}},
            'BinaryValue': {'Parameters': ['InstanceNumber', 'Priority'], 'Status': {}},
            'MultiStateValue': {'Parameters': ['InstanceNumber', 'Priority'], 'Status': {}},
            'Temperature': {'Parameters': ['InstanceNumber', 'Priority'], 'Status': {}}
        }

        self.InvokeIDs = eightBitGenerator()
    
    @property
    def InvokeID(self):
        return self.InvokeIDs.next()    # increment command ID by 1
    
    def SetAnalogValue(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        Precision = qualifier['Precision']
        if 0 <= int(InstanceNumber) <= 4194303 and 0 <= int(Precision) <= 5 and priority in PriorityStates:
            
            bnm = BACnetMsg(['AnalogValue', InstanceNumber, PriorityStates[priority]], 'WriteProperty')
            bnm.value = float(value)
            self.__SetHelper('AnalogValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogValue')

    def UpdateAnalogValue(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        Precision = qualifier['Precision']
        if 0 <= int(InstanceNumber) <= 4194303 and 0 <= int(Precision) <= 5 and priority in PriorityStates:
            bnm = BACnetMsg(['AnalogValue', InstanceNumber, PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogValue', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    formatString = '{{0:.{}f}}'.format(Precision)
                    self.WriteStatus('AnalogValue', formatString.format(value), qualifier)  
                except:
                    self.Error(['Analog Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValue')
    
    def UpdateAnalogValueCompare(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumberLeft = qualifier['InstanceNumberLeft']
        InstanceNumberRight = qualifier['InstanceNumberRight']
        Operator = qualifier['Operator']
        if (0 <= int(InstanceNumberLeft) <= 4194303 and 0 <= int(InstanceNumberRight) <= 4194303 
                     and priority in PriorityStates):
            bnmL = BACnetMsg(['AnalogValue', InstanceNumberLeft, PriorityStates[priority]])
            bnmR = BACnetMsg(['AnalogValue', InstanceNumberRight, PriorityStates[priority]])
            resL = self.__UpdateHelper('AnalogValueCompare', bnmL, value, qualifier)
            resR = self.__UpdateHelper('AnalogValueCompare', bnmR, value, qualifier)
            if resL and resR:
                try:
                    value = None
                    if Operator == 'GreaterThan':
                        value = resL.value > resR.value
                    elif Operator == 'LessThan':
                        value = resL.value < resR.value
                    elif Operator == 'Equal':
                        value = resL.value == resR.value
                    elif Operator == 'GreaterOrEqual':
                        value = resL.value >= resR.value
                    elif Operator == 'LessOrEqual':
                        value = resL.value <= resR.value
                    self.WriteStatus('AnalogValueCompare', 'True' if value else 'False', qualifier)  
                except:
                    self.Error(['Analog Value Compare: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValueCompare')
    
    def UpdateAnalogValueComparetoNumber(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }
        
        OperatorStates = ('GreaterThan', 'LessThan', 'Equal', 'GreaterOrEqual', 'LessOrEqual')

        priority = qualifier['Priority']
        InstanceNumberLeft = qualifier['InstanceNumberLeft']
        Operator = qualifier['Operator']
        CompareTo = qualifier['CompareTo']
        if 0 <= int(InstanceNumberLeft) <= 4194303 and priority in PriorityStates and Operator in OperatorStates:
            bnmL = BACnetMsg(['AnalogValue', InstanceNumberLeft, PriorityStates[priority]])
            resL = self.__UpdateHelper('AnalogValueComparetoNumber', bnmL, value, qualifier)
            if resL:
                try:
                    value = None
                    if Operator == 'GreaterThan':
                        value = resL.value > CompareTo
                    elif Operator == 'LessThan':
                        value = resL.value < CompareTo
                    elif Operator == 'Equal':
                        value = resL.value == CompareTo
                    elif Operator == 'GreaterOrEqual':
                        value = resL.value >= CompareTo
                    elif Operator == 'LessOrEqual':
                        value = resL.value <= CompareTo
                    self.WriteStatus('AnalogValueComparetoNumber', 'True' if value else 'False', qualifier)  
                except:
                    self.Error(['Analog Value Compare To Number: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValueComparetoNumber')
    
    def SetAnalogValueRange(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= value <= 65535 and 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['AnalogValue', InstanceNumber, PriorityStates[priority]], 'WriteProperty')
            bnm.value = value
            self.__SetHelper('AnalogValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogValueRange')

    def UpdateAnalogValueRange(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['AnalogValue', InstanceNumber, PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogValueRange', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    self.WriteStatus('AnalogValueRange', value, qualifier)
                except:
                    self.Error(['Analog Value Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValueRange')
    
    def SetBinaryValue(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['BinaryValue', InstanceNumber, PriorityStates[priority]], 'WriteProperty')
            bnm.value = int(value)
            self.__SetHelper('BinaryValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBinaryValue')

    def UpdateBinaryValue(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['BinaryValue', InstanceNumber, PriorityStates[priority]])
            res = self.__UpdateHelper('BinaryValue', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('BinaryValue', value, qualifier)  
                except:
                    self.Error(['Binary Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBinaryValue')
    
    def SetMultiStateValue(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['MultiStateValue', InstanceNumber, PriorityStates[priority]], 'WriteProperty')
            bnm.value = int(value)
            self.__SetHelper('MultiStateValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiStateValue')

    def UpdateMultiStateValue(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['MultiStateValue', InstanceNumber, PriorityStates[priority]])
            res = self.__UpdateHelper('MultiStateValue', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('MultiStateValue', value, qualifier)  
                except:
                    self.Error(['Multi State Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMultiStateValue')
    
    def SetTemperature(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            bnm = BACnetMsg(['AnalogValue', InstanceNumber, PriorityStates[priority]], 'WriteProperty')
            bnm.value = value
            self.__SetHelper('Temperature', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemperature')

    def UpdateTemperature(self, value, qualifier):

        PriorityStates = {
            'Normal':             'Normal',
            'Urgent':             'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety':        'LifeSafety',
        }

        priority = qualifier['Priority']
        InstanceNumber = qualifier['InstanceNumber']
        if 0 <= int(InstanceNumber) <= 4194303 and priority in PriorityStates:
            
            bnm = BACnetMsg(['AnalogValue', InstanceNumber, PriorityStates[priority]])
            res = self.__UpdateHelper('Temperature', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    self.WriteStatus('Temperature', value, qualifier)  
                except:
                    self.Error(['Temperature: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTemperature')
    
    def __CheckResponseForErrors(self, command, response, bnm):
        try:
            rbnm = BACnetMsg(Message=response)
        except:
            self.Error(['{0} Error occured: {1}'.format(command, response)])
            return None

        if rbnm.InvokeID == bnm.InvokeID:
            return rbnm
        else:
            self.Error(['{0} Error occured: {1}'.format(command, rbnm)])
            return None
    
    def __SetHelper(self, command, bnm, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(bnm.encodeMessage())
        else:
            bnm.InvokeID = self.InvokeID
            res = self.SendAndWait(bnm.encodeMessage(), self.DefaultResponseTimeout)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                self.__CheckResponseForErrors(command, res, bnm)

    def __UpdateHelper(self, command, bnm, value, qualifier):
        
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            bnm.InvokeID = self.InvokeID
            res = self.SendAndWait(bnm.encodeMessage(), self.DefaultResponseTimeout)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                self.__CheckResponseForErrors(command, res, bnm)

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

def bLen(data):

    count = 0
    for datum in data:
        count += 1
    return count

def bFind(value, data):

    count, found = 0, True
    for datum in data:
        if datum == value:
            break
        count += 1
    else:
        found = False
    return count if found else None

def swapKV(dictionary):
    return dict(zip(dictionary.values(), dictionary.keys()))

class eightBitGenerator():
    def __init__(self):
        self.__value = 255

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.__value > 255:
            self.__value = 0
        return self.__value

class BACnetMsg(object):
    
    APDUTypes = {
        'ConfirmedRequest':     0,
        'UnconfirmedRequest':   1,
        'SimpleACK':            2,
        'ComplexACK':           3,
        'SegmentedACK':         4,
        'Error':                5,
        'Reject':               6,
        'Abort':                7,
        }

    ApplicationTags = {
        'Null':                     0,
        'Boolean':                  1,
        'UnsignedInteger':          2,
        'Integer':                  3,
        'Real':                     4,
        'Double':                   5,
        'OctetString':              6,
        'CharacterString':          7,
        'BitString':                8,
        'Enumerated':               9,
        'Date':                     10,
        'Time':                     11,
        'BACnetObjectIdentifier':   12,
        }

    BVLCFunctions = {
        'WriteBroadcastDistributionTable':      1,
        'ReadBroadcastDistributionTable':       2,
        'ReadBroadcastDistributionTableACK':    3,
        'ForwardedNPDU':                        4,
        'RegisterForeignDevice':                5,
        'OriginalUnicastNPDU':                  10,
        'OriginalBroadcastNPDU':                11,
        }

    ObjectTypes = {
        'AnalogInput':          0,
        'AnalogOutput':         1,
        'AnalogValue':          2,
        'BinaryInput':          3,
        'BinaryOutput':         4,
        'BinaryValue':          5,
        'Calendar':             6,
        'Command':              7,
        'DeviceObject':         8,
        'EventEnrollment':      9,
        'File':                 10, 
        'Group':                11,
        'Loop':                 12,
        'MutliStateInput':      13,
        'MutliStateOutput':     14,
        'NotificationClass':    15,
        'Program':              16,
        'Schedule':             17,
        'MultiStateValue':      19,
		'TrendLog':             20,
		'PulseConverter':       24,
		'StructuredView':       29,
		'IOUnit':               384,
        }

    Priorities = {
        'Normal':            0,
        'Urgent':            1,
        'CriticalEquipment': 2,
        'LifeSafety':        3,
        }

    ServiceChoices = {
        'SubscibeCOV':           5,
        'ReadProperty':          12,
        'ReadPropertyMultiple':  14,
        'WriteProperty':         15,
        'WritePropertyMultiple': 16,
        'ReinitializeDevice':    20,
        }

    def __init__(self, Data=[], ServiceChoice='ReadProperty', APDUType='ConfirmedRequest', Message=None):
        
        self.__BVLC = {
            'Type': 0x81,
            'Function': 10
            }    # Static for our purposes
            
        priorityValue = self.Priorities['Normal'] | 0x04
        self.__NPDU = {
            'Version': 1,
            'Control': priorityValue
            }   # Version is static, Priority is variable
        
        self.__APDU = {
            'PDUFlags': 0x00,                           # Static for our purposes. Unsegmented send/receive.                 
            'MaxResponseSegments': 0,                   # Static for our purposes. Unsegmented send/receive.
            'MaxAPDUSize': 3,                           # Standard?
            'Data': {
                'PropertyID': 85                        # Static for our purposes. 'Present Value'
                }
            }
        
        if Data:
            self.ObjectType = Data[0]
            self.InstanceNumber = Data[1]
            self.Priority = Data[2]
        elif not Message:
            raise ValueError("Data required. Ex: foo = BACnetMsg(['AnalogInput', 5])")
        
        self.ServiceChoice = ServiceChoice
        self.APDUType = APDUType

        if Message:
            self.decodeMessage(Message)

    def __str__(self):
        return self.getAPDU('STRING')

    @property
    def APDUType(self):
        return swapKV(self.APDUTypes).get(self.__APDU['Type'])
        
    @APDUType.setter
    def APDUType(self, Value):
        self.__APDU['Type'] = self.APDUTypes[Value] if Value else None

    @property
    def InstanceNumber(self):
        return self.__APDU['Data'].get('InstanceNumber')
        
    @InstanceNumber.setter
    def InstanceNumber(self, Value):
        if 0 <= Value <= 0x3FFFFF:
            self.__APDU['Data']['InstanceNumber'] = Value
        else:
            raise ValueError('InstanceNumber ({0}) out of range (0-4194303).'.format(Value))

    @property
    def InvokeID(self):
        return self.__APDU.get('InvokeID', 0)
        
    @InvokeID.setter
    def InvokeID(self, Value):
        if 0 <= Value <= 255:
            self.__APDU['InvokeID'] = Value
        else:
            raise ValueError('InvokeID ({0}) out of range (0-255).'.format(Value))

    @property
    def ObjectType(self):
        try:
            return swapKV(self.ObjectTypes)[self.__APDU['Data']['ObjectType']]
        except KeyError:
            return None

    @ObjectType.setter
    def ObjectType(self, Value):
        self.__APDU['Data']['ObjectType'] = self.ObjectTypes[Value] if Value else None

    @property
    def Priority(self):
        try:
            return swapKV(self.Priorities)[self.__NPDU['Control'] & 0x03]
        except KeyError:
            return None

    @Priority.setter
    def Priority(self, Value):
        self.__NPDU['Control'] = self.Priorities[Value] | 0x04 if Value else None

    @property
    def ServiceChoice(self):
        try:
            return swapKV(self.ServiceChoices)[self.__APDU['ServiceChoice']]
        except KeyError:
            return None

    @ServiceChoice.setter
    def ServiceChoice(self, Value):
        self.__APDU['ServiceChoice'] = self.ServiceChoices[Value]

    @property
    def value(self):
        return self.__APDU['Data'].get('Value')
        
    @value.setter
    def value(self, Value):
        self.__APDU['Data']['Value'] = Value

    def getBVLC(self, Format='BYTES'):
        if Format == 'BYTES':
            return pack('>BBH', self.__BVLC['Type'], self.__BVLC['Function'], self.__BVLC['Length'])
        elif Format == 'STRING':
            return 'BACnet:{0}'.format(swapKV(self.BVLCFunctions)[self.__BVLC['Function']])

    def getNPDU(self, Format='BYTES'):
        if Format == 'BYTES':
            return pack('BB', self.__NPDU['Version'], self.__NPDU['Control'])
        elif Format == 'STRING':
            return "'Version': 1, 'Priority': '{0}'".format(self.Priority)

    def getAPDU(self, Format='BYTES'):
        if Format == 'BYTES':
            m = pack('>BBBBBIBB',
                self.__APDU['Type'] | self.__APDU['PDUFlags'],
                self.__APDU['MaxResponseSegments'] | self.__APDU['MaxAPDUSize'],
                self.__APDU['InvokeID'],
                self.__APDU['ServiceChoice'],
                0x0C,
                self.__APDU['Data']['ObjectType'] << 22 | self.__APDU['Data']['InstanceNumber'],
                0x19,
                self.__APDU['Data']['PropertyID'],
                )
            if self.__APDU['ServiceChoice'] == 15 or self.value is not None:    # 15 == 'WriteProperty'
                ObjectType = self.__APDU['Data']['ObjectType']
                if ObjectType in [0, 1, 2]:                      # Analog*, Float
                    m += pack('>BBfB', 0x3E, 0x44, self.value, 0x3F)
                elif ObjectType == 19:                           # MultiStateValue
                    m += pack('BBBB', 0x3E, 0x21, self.value, 0x3F)
                elif ObjectType == 5:                            # BinaryValue
                    m += pack('BBBB', 0x3E, 0x91, self.value, 0x3F)
            return m
        elif Format == 'STRING':
            m = "'Type': '{0}', 'InvokeID': {1}, 'ServiceChoice': '{2}'".format(self.APDUType, self.InvokeID, self.ServiceChoice)
            if self.ServiceChoice == 'WriteProperty' or self.value is not None:
                m += ", 'Data': {" + "'ObjectType': '{0}', 'InstanceNumber': {1}, 'Value': {2}".format(
                        self.ObjectType, self.InstanceNumber, self.value) + '}'
            else:
                m += ", 'Data': {" + "'ObjectType': '{0}', 'InstanceNumber': {1}".format(self.ObjectType,
                        self.InstanceNumber) + '}'
            return m
    
    def encodeMessage(self, Format='BYTES'):

        if Format == 'BYTES':
            m = self.getNPDU() + self.getAPDU()
            self.__BVLC['Length'] = 4 + bLen(m)
            return self.getBVLC() + m
        elif Format == 'EXTRON':
            return (b'%' + b'%'.join([hexlify(b.to_bytes(1, 'big')) for b in self.encodeMessage()])).decode()
        else:
            raise ValueError('Invalid format: {}'.format(Format))

    def separateData(self, data):
        Data = []
        while data:
            tag, data = data[0], data[1:]
            if tag & 0x08:
                if tag == 0x0C:
                    value, data = unpack('>I', data[:4])[0], data[4:]
                    Data.append(value)
                elif tag == 0x19:
                    value, data = data[0], data[1:]
                    Data.append(value)
                elif tag & 0x0F == 0x0E:
                    size = bFind(tag | 0x0F, data)
                    if size <= (data[0] & 0x0F):
                        size = 1 + (data[0] & 0x0F)
                    Data.append(tuple(self.separateData(data[:size])))
                    data = data[size:]
            elif tag == 0x44:
                value, data = data[:4], data[4:]
                Data.append(unpack('>f', value)[0])
            elif tag in [0x21, 0x91]:
                value, data = data[0], data[1:]
                Data.append(value)
            else:
                print('Unknown: {}'.format(tag))
        return Data
    
    def decodeMessage(self, m):

        if bLen(m) > 4:
            length = unpack('>h', m[2:4])[0]                            # Separate length and message
            if length == bLen(m):                                       # Verify length
                BVLC, NPDU, APDU = m[:4], m[4:6], m[6:]
                self.__BVLC['Type'] = BVLC[0]
                self.__BVLC['Function'] = BVLC[1]
                self.__BVLC['Length'] = length
                self.__NPDU['Version'] = NPDU[0]
                self.__NPDU['Control'] = NPDU[1]
                self.__APDU['Type'] = APDU[0] >> 4
                self.__APDU['PDUFlags'] = APDU[0] & 0x0F
                self.__APDU['InvokeID'] = APDU[1]
                self.__APDU['ServiceChoice'] = APDU[2]
                data = APDU[3:]
                if self.__APDU['Type'] == 3:                            # ComplexACK
                    Data = self.separateData(data)
                    self.__APDU['Data'] = {
                        'ObjectType': Data[0] >> 22,
                        'InstanceNumber': Data[0] & 0x003FFFFF,
                        'PropertyID': Data[1],
                        'Value': Data[2][0],
                        }
                elif self.__APDU['Type'] == self.APDUTypes['SimpleACK']:
                    pass
                elif self.__APDU['Type'] == self.APDUTypes['Error']:
                    pass
            else:
                raise ValueError('Incomplete message: expected {0} bytes, received {1} bytes.'.format(length, bLen(m)))
        else:
            raise ValueError('Unknown message type or unhandled function: {}'.format(m))