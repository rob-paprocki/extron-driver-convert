import time
from struct import pack, unpack
from binascii import hexlify
from extronlib.interface import EthernetClientInterface


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogInput': {'Parameters': ['Instance Number', 'Precision', 'Priority'], 'Status': {}},
            'AnalogInputCompare': {'Parameters': ['Instance Number Left', 'Operator', 'Instance Number Right', 'Priority'], 'Status': {}},
            'AnalogInputCompareToNumber': {'Parameters': ['Instance Number Left', 'Operator', 'Compare To', 'Priority'], 'Status': {}},
            'AnalogInputRange': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'AnalogOutput': {'Parameters': ['Instance Number', 'Precision', 'Priority'], 'Status': {}},
            'AnalogOutputCompare': {'Parameters': ['Instance Number Left', 'Operator', 'Instance Number Right', 'Priority'], 'Status': {}},
            'AnalogOutputCompareToNumber': {'Parameters': ['Instance Number Left', 'Operator', 'Compare To', 'Priority'], 'Status': {}},
            'AnalogOutputRange': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'AnalogValue': {'Parameters': ['Instance Number', 'Precision', 'Priority'], 'Status': {}},
            'AnalogValueCompare': {'Parameters': ['Instance Number Left', 'Operator', 'Instance Number Right', 'Priority'], 'Status': {}},
            'AnalogValueCompareToNumber': {'Parameters': ['Instance Number Left', 'Operator', 'Compare To', 'Priority'], 'Status': {}},
            'AnalogValueRange': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'BinaryInput': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'BinaryOutput': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'BinaryValue': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'MultiStateInput': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'MultiStateOutput': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'MultiStateValue': {'Parameters': ['Instance Number', 'Priority'], 'Status': {}},
            'Temperature': {'Parameters': ['Instance Number', 'Priority'],   'Status': {}},
        }

        self.InvokeIDs = eightBitGenerator()

    @property
    def InvokeID(self):
        return self.InvokeIDs.next()

    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def UpdateAnalogInput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PrecisionConstraints = {
            'Min': 0,
            'Max': 5,
            'Value': qualifier['Precision'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, PrecisionConstraints):
            bnm = BACnetMsg(['AnalogInput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogInput', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    formatString = '{0:.' + str(PrecisionConstraints['Value']) + 'f}'
                    self.WriteStatus('AnalogInput', formatString.format(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogInput')

    def UpdateAnalogInputCompare(self, value, qualifier):

        InstanceNumberLeftConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Left'],
        }

        InstanceNumberRightConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Right'],
        }

        OperatorStates = ('Greater Than', 'Less Than', 'Equal', 'Greater Or Equal', 'Less Or Equal')

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        operator = qualifier['Operator']
        if (operator in OperatorStates and priority in PriorityStates and
                self.__constraint_checker(InstanceNumberLeftConstraints, InstanceNumberRightConstraints)):
            bnm_left = BACnetMsg(['AnalogInput', InstanceNumberLeftConstraints['Value'], PriorityStates[priority]])
            bnm_right = BACnetMsg(['AnalogInput', InstanceNumberRightConstraints['Value'], PriorityStates[priority]])
            res_left = self.__UpdateHelper('AnalogInputCompare', bnm_left, value, qualifier)
            res_right = self.__UpdateHelper('AnalogInputCompare', bnm_right, value, qualifier)
            if res_left and res_right:
                try:
                    value = False
                    if operator == 'Greater Than':
                        value = res_left.value > res_right.value
                    elif operator == 'Less Than':
                        value = res_left.value < res_right.value
                    elif operator == 'Equal':
                        value = res_left.value == res_right.value
                    elif operator == 'Greater Or Equal':
                        value = res_left.value >= res_right.value
                    elif operator == 'Less Or Equal':
                        value = res_left.value <= res_right.value
                    self.WriteStatus('AnalogInputCompare', str(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Input Compare 2: Invalid/unexpected response'])
            else:
                self.Error(['Analog Input Compare 1: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogInputCompare')

    def UpdateAnalogInputCompareToNumber(self, value, qualifier):

        InstanceNumberLeftConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Left'],
        }

        OperatorStates = ('Greater Than', 'Less Than', 'Equal', 'Greater Or Equal', 'Less Or Equal')

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        operator = qualifier['Operator']
        compare_to = qualifier['Compare To']
        if (priority in PriorityStates and operator in OperatorStates and
                self.__constraint_checker(InstanceNumberLeftConstraints)):
            bnm_left = BACnetMsg(['AnalogInput', InstanceNumberLeftConstraints['Value'], PriorityStates[priority]])
            res_left = self.__UpdateHelper('AnalogInputCompareToNumber', bnm_left, value, qualifier)
            if res_left:
                try:
                    value = False
                    if operator == 'Greater Than':
                        value = res_left.value > compare_to
                    elif operator == 'Less Than':
                        value = res_left.value < compare_to
                    elif operator == 'Equal':
                        value = res_left.value == compare_to
                    elif operator == 'Greater Or Equal':
                        value = res_left.value >= compare_to
                    elif operator == 'Less Or Equal':
                        value = res_left.value <= compare_to
                    self.WriteStatus('AnalogInputCompareToNumber', str(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Input Compare To Number 2: Invalid/unexpected response'])
            else:
                self.Error(['Analog Input Compare To Number 1: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogInputCompareToNumber')

    def SetAnalogInputRange(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 65535,
            'Value': value
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, ValueConstraints):
            bnm = BACnetMsg(['AnalogInput', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = value
            self.__SetHelper('AnalogInputRange', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputRange')

    def UpdateAnalogInputRange(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['AnalogInput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogInputRange', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    self.WriteStatus('AnalogInputRange', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Input Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogInputRange')

    def SetAnalogOutput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PrecisionConstraints = {
            'Min': 0,
            'Max': 5,
            'Value': qualifier['Precision'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, PrecisionConstraints):
            bnm = BACnetMsg(['AnalogOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = float(value)
            self.__SetHelper('AnalogOutput', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogOutput')

    def UpdateAnalogOutput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PrecisionConstraints = {
            'Min': 0,
            'Max': 5,
            'Value': qualifier['Precision'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, PrecisionConstraints):
            bnm = BACnetMsg(['AnalogOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogOutput', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    formatString = '{0:.' + str(PrecisionConstraints['Value']) + 'f}'
                    self.WriteStatus('AnalogOutput', formatString.format(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Output: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogOutput')

    def UpdateAnalogOutputCompare(self, value, qualifier):

        InstanceNumberLeftConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Left'],
        }

        InstanceNumberRightConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Right'],
        }

        OperatorStates = ('Greater Than', 'Less Than', 'Equal', 'Greater Or Equal', 'Less Or Equal')

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        operator = qualifier['Operator']
        if (operator in OperatorStates and priority in PriorityStates and
                self.__constraint_checker(InstanceNumberLeftConstraints, InstanceNumberRightConstraints)):
            bnm_left = BACnetMsg(['AnalogOutput', InstanceNumberLeftConstraints['Value'], PriorityStates[priority]])
            bnm_right = BACnetMsg(['AnalogOutput', InstanceNumberRightConstraints['Value'], PriorityStates[priority]])
            res_left = self.__UpdateHelper('AnalogOutputCompare', bnm_left, value, qualifier)
            res_right = self.__UpdateHelper('AnalogOutputCompare', bnm_right, value, qualifier)
            if res_left and res_right:
                try:
                    value = False
                    if operator == 'Greater Than':
                        value = res_left.value > res_right.value
                    elif operator == 'Less Than':
                        value = res_left.value < res_right.value
                    elif operator == 'Equal':
                        value = res_left.value == res_right.value
                    elif operator == 'Greater Or Equal':
                        value = res_left.value >= res_right.value
                    elif operator == 'Less Or Equal':
                        value = res_left.value <= res_right.value
                    self.WriteStatus('AnalogOutputCompare', str(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Output Compare 2: Invalid/unexpected response'])
            else:
                self.Error(['Analog Output Compare 1: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogOutputCompare')

    def UpdateAnalogOutputCompareToNumber(self, value, qualifier):

        InstanceNumberLeftConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Left'],
        }

        OperatorStates = ('Greater Than', 'Less Than', 'Equal', 'Greater Or Equal', 'Less Or Equal')

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        operator = qualifier['Operator']
        compare_to = qualifier['Compare To']
        if (priority in PriorityStates and operator in OperatorStates and
                self.__constraint_checker(InstanceNumberLeftConstraints)):
            bnm_left = BACnetMsg(['AnalogOutput', InstanceNumberLeftConstraints['Value'], PriorityStates[priority]])
            res_left = self.__UpdateHelper('AnalogOutputCompareToNumber', bnm_left, value, qualifier)
            if res_left:
                try:
                    value = False
                    if operator == 'Greater Than':
                        value = res_left.value > compare_to
                    elif operator == 'Less Than':
                        value = res_left.value < compare_to
                    elif operator == 'Equal':
                        value = res_left.value == compare_to
                    elif operator == 'Greater Or Equal':
                        value = res_left.value >= compare_to
                    elif operator == 'Less Or Equal':
                        value = res_left.value <= compare_to
                    self.WriteStatus('AnalogOutputCompareToNumber', str(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Output Compare To Number 2: Invalid/unexpected response'])
            else:
                self.Error(['Analog Output Compare To Number 1: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogOutputCompareToNumber')

    def SetAnalogOutputRange(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 65535,
            'Value': value
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, ValueConstraints):
            bnm = BACnetMsg(['AnalogOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = value
            self.__SetHelper('AnalogOutputRange', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogOutputRange')

    def UpdateAnalogOutputRange(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['AnalogOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogOutputRange', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    self.WriteStatus('AnalogOutputRange', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Output Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogOutputRange')

    def SetAnalogValue(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PrecisionConstraints = {
            'Min': 0,
            'Max': 5,
            'Value': qualifier['Precision'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, PrecisionConstraints):

            bnm = BACnetMsg(['AnalogValue', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = float(value)
            self.__SetHelper('AnalogValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogValue')

    def UpdateAnalogValue(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PrecisionConstraints = {
            'Min': 0,
            'Max': 5,
            'Value': qualifier['Precision'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, PrecisionConstraints):
            bnm = BACnetMsg(['AnalogValue', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogValue', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    formatString = '{0:.' + str(PrecisionConstraints['Value']) + 'f}'
                    self.WriteStatus('AnalogValue', formatString.format(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValue')

    def UpdateAnalogValueCompare(self, value, qualifier):

        InstanceNumberLeftConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Left'],
        }

        InstanceNumberRightConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Right'],
        }

        OperatorStates = ('Greater Than', 'Less Than', 'Equal', 'Greater Or Equal', 'Less Or Equal')

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        operator = qualifier['Operator']
        if (operator in OperatorStates and priority in PriorityStates and
                self.__constraint_checker(InstanceNumberLeftConstraints, InstanceNumberRightConstraints)):
            bnm_left = BACnetMsg(['AnalogValue', InstanceNumberLeftConstraints['Value'], PriorityStates[priority]])
            bnm_right = BACnetMsg(['AnalogValue', InstanceNumberRightConstraints['Value'], PriorityStates[priority]])
            res_left = self.__UpdateHelper('AnalogValueCompare', bnm_left, value, qualifier)
            res_right = self.__UpdateHelper('AnalogValueCompare', bnm_right, value, qualifier)
            if res_left and res_right:
                try:
                    value = False
                    if operator == 'Greater Than':
                        value = res_left.value > res_right.value
                    elif operator == 'Less Than':
                        value = res_left.value < res_right.value
                    elif operator == 'Equal':
                        value = res_left.value == res_right.value
                    elif operator == 'Greater Or Equal':
                        value = res_left.value >= res_right.value
                    elif operator == 'Less Or Equal':
                        value = res_left.value <= res_right.value
                    self.WriteStatus('AnalogValueCompare', str(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Value Compare 2: Invalid/unexpected response'])
            else:
                self.Error(['Analog Value Compare 1: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValueCompare')

    def UpdateAnalogValueCompareToNumber(self, value, qualifier):

        InstanceNumberLeftConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number Left'],
        }

        OperatorStates = ('Greater Than', 'Less Than', 'Equal', 'Greater Or Equal', 'Less Or Equal')

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        operator = qualifier['Operator']
        compare_to = qualifier['Compare To']
        if (priority in PriorityStates and operator in OperatorStates and
                self.__constraint_checker(InstanceNumberLeftConstraints)):
            bnm_left = BACnetMsg(['AnalogValue', InstanceNumberLeftConstraints['Value'], PriorityStates[priority]])
            res_left = self.__UpdateHelper('AnalogValueCompareToNumber', bnm_left, value, qualifier)
            if res_left:
                try:
                    value = False
                    if operator == 'Greater Than':
                        value = res_left.value > compare_to
                    elif operator == 'Less Than':
                        value = res_left.value < compare_to
                    elif operator == 'Equal':
                        value = res_left.value == compare_to
                    elif operator == 'Greater Or Equal':
                        value = res_left.value >= compare_to
                    elif operator == 'Less Or Equal':
                        value = res_left.value <= compare_to
                    self.WriteStatus('AnalogValueCompareToNumber', str(value), qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Value Compare To Number 2: Invalid/unexpected response'])
            else:
                self.Error(['Analog Value Compare To Number 1: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValueCompareToNumber')

    def SetAnalogValueRange(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 65535,
            'Value': value
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, ValueConstraints):
            bnm = BACnetMsg(['AnalogValue', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = value
            self.__SetHelper('AnalogValueRange', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogValueRange')

    def UpdateAnalogValueRange(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['AnalogValue', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('AnalogValueRange', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    self.WriteStatus('AnalogValueRange', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Analog Value Range: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAnalogValueRange')

    def UpdateBinaryInput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['BinaryInput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('BinaryInput', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('BinaryInput', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Binary Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBinaryInput')

    def SetBinaryOutput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['BinaryOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = int(value)
            self.__SetHelper('BinaryOutput', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBinaryOutput')

    def UpdateBinaryOutput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['BinaryOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('BinaryOutput', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('BinaryOutput', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Binary Output: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBinaryOutput')

    def SetBinaryValue(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['BinaryValue', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = int(value)
            self.__SetHelper('BinaryValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBinaryValue')

    def UpdateBinaryValue(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['BinaryValue', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('BinaryValue', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('BinaryValue', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Binary Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBinaryValue')

    def UpdateMultiStateInput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['MultiStateInput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('MultiStateInput', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('MultiStateInput', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Multi State Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMultiStateInput')

    def SetMultiStateOutput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 255,
            'Value': int(value) if value.isdigit() else -1
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, ValueConstraints):
            bnm = BACnetMsg(['MultiStateOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = int(value)
            self.__SetHelper('MultiStateOutput', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiStateOutput')

    def UpdateMultiStateOutput(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['MultiStateOutput', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('MultiStateOutput', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('MultiStateOutput', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Multi State Output: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMultiStateOutput')

    def SetMultiStateValue(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 255,
            'Value': int(value) if value.isdigit() else -1
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, ValueConstraints):
            bnm = BACnetMsg(['MultiStateValue', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = int(value)
            self.__SetHelper('MultiStateValue', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiStateValue')

    def UpdateMultiStateValue(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['MultiStateValue', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('MultiStateValue', bnm, value, qualifier)
            if res:
                try:
                    value = str(res.value)
                    self.WriteStatus('MultiStateValue', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Multi State Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMultiStateValue')

    def SetTemperature(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 70,
            'Value': value,
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints, ValueConstraints):
            bnm = BACnetMsg(['AnalogValue', InstanceNumberConstraints['Value'], PriorityStates[priority]], 'WriteProperty')
            bnm.value = value
            self.__SetHelper('Temperature', bnm, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTemperature')

    def UpdateTemperature(self, value, qualifier):

        InstanceNumberConstraints = {
            'Min': 0,
            'Max': 4194303,
            'Value': qualifier['Instance Number'],
        }

        PriorityStates = {
            'Normal': 'Normal',
            'Urgent': 'Urgent',
            'Critical Equipment': 'CriticalEquipment',
            'Life Safety': 'LifeSafety',
        }

        priority = qualifier['Priority']
        if priority in PriorityStates and self.__constraint_checker(InstanceNumberConstraints):
            bnm = BACnetMsg(['AnalogValue', InstanceNumberConstraints['Value'], PriorityStates[priority]])
            res = self.__UpdateHelper('Temperature', bnm, value, qualifier)
            if res:
                try:
                    value = res.value
                    self.WriteStatus('Temperature', value, qualifier)
                except (TypeError, ValueError):
                    self.Error(['Temperature: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTemperature')

    def __CheckResponseForErrors(self, command, response, bnm):

        try:
            rbnm = BACnetMsg(Message=response)
        except:
            self.Error(['Error 1 occurred: {0}'.format(response)])
            return None

        if rbnm.InvokeID == bnm.InvokeID:
            return rbnm
        else:
            self.Error(['Error 2 occurred: {0}'.format(rbnm)])
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
                res = self.__CheckResponseForErrors(command, res, bnm)

    def __UpdateHelper(self, command, bnm, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            bnm.InvokeID = self.InvokeID

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(bnm.encodeMessage(), self.DefaultResponseTimeout)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
                return ''
            else:
                return self.__CheckResponseForErrors(command, res, bnm)

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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


def bLen(data):
    """ Binary safe len(). """
    count = 0
    for datum in data:
        count += 1
    return count


def bFind(value, data):
    """ Binary safe find(). """
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
        self.__value += 1
        if self.__value > 255:
            self.__value = 0
        return self.__value


class BACnetMsg(object):
    APDUTypes = {
        'ConfirmedRequest': 0,
        'UnconfirmedRequest': 1,
        'SimpleACK': 2,
        'ComplexACK': 3,
        'SegmentedACK': 4,
        'Error': 5,
        'Reject': 6,
        'Abort': 7,
    }

    ApplicationTags = {
        'Null': 0,
        'Boolean': 1,
        'UnsignedInteger': 2,
        'Integer': 3,
        'Real': 4,
        'Double': 5,
        'OctetString': 6,
        'CharacterString': 7,
        'BitString': 8,
        'Enumerated': 9,
        'Date': 10,
        'Time': 11,
        'BACnetObjectIdentifier': 12,
    }

    BVLCFunctions = {
        'WriteBroadcastDistributionTable': 1,
        'ReadBroadcastDistributionTable': 2,
        'ReadBroadcastDistributionTableACK': 3,
        'ForwardedNPDU': 4,
        'RegisterForeignDevice': 5,
        'OriginalUnicastNPDU': 10,
        'OriginalBroadcastNPDU': 11,
    }

    ObjectTypes = {
        'AnalogInput': 0,
        'AnalogOutput': 1,
        'AnalogValue': 2,
        'BinaryInput': 3,
        'BinaryOutput': 4,
        'BinaryValue': 5,
        'Calendar': 6,
        'Command': 7,
        'DeviceObject': 8,
        'EventEnrollment': 9,
        'File': 10,
        'Group': 11,
        'Loop': 12,
        'MultiStateInput': 13,
        'MultiStateOutput': 14,
        'NotificationClass': 15,
        'Program': 16,
        'Schedule': 17,
        'MultiStateValue': 19,
        'TrendLog': 20,
        'PulseConverter': 24,
        'StructuredView': 29,
        'IOUnit': 384,
    }

    Priorities = {
        'Normal': 0,
        'Urgent': 1,
        'CriticalEquipment': 2,
        'LifeSafety': 3,
    }

    ServiceChoices = {
        'SubscibeCOV': 5,
        'ReadProperty': 12,
        'ReadPropertyMultiple': 14,
        'WriteProperty': 15,
        'WritePropertyMultiple': 16,
        'ReinitializeDevice': 20,
    }

    def __init__(self, Data=[], ServiceChoice='ReadProperty', APDUType='ConfirmedRequest', Message=None):

        self.__BVLC = {
            'Type': 0x81,
            'Function': 10
        }  # Static for our purposes.

        self.__APDU = {
            'PDUFlags': 0x00,  # Static for our purposes. Unsegmented send/receive.
            'MaxResponseSegments': 0,  # Static for our purposes. Unsegmented send/receive.
            'MaxAPDUSize': 3,  # Standard?
            'Data': {
                'PropertyID': 85  # Static for our purposes. 'Present Value'
            }
        }

        priorityValue = self.Priorities['Normal'] | 0x04
        self.__NPDU = {
            'Version': 1,
            'Control': priorityValue,
        }  # Version 1 Static, Priority is variable

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
    def APDUType(self, value):
        self.__APDU['Type'] = self.APDUTypes[value] if value else None

    @property
    def InstanceNumber(self):
        return self.__APDU['Data'].get('Instance Number')

    @InstanceNumber.setter
    def InstanceNumber(self, value):
        if 0 <= value <= 0x3FFFFF:
            self.__APDU['Data']['Instance Number'] = value
        else:
            raise ValueError('Instance Number ({0}) out of range (0-4194303).'.format(value))

    @property
    def InvokeID(self):
        return self.__APDU.get('InvokeID', 0)

    @InvokeID.setter
    def InvokeID(self, value):
        if 0 <= value <= 255:
            self.__APDU['InvokeID'] = value
        else:
            raise ValueError('InvokeID ({0}) out of range (0-255).'.format(value))

    @property
    def ObjectType(self):
        try:
            return swapKV(self.ObjectTypes)[self.__APDU['Data']['ObjectType']]
        except KeyError:
            return None

    @ObjectType.setter
    def ObjectType(self, value):
        self.__APDU['Data']['ObjectType'] = self.ObjectTypes[value] if value else None

    @property
    def Priority(self):
        try:
            return swapKV(self.Priorities)[self.__NPDU['Control'] & 0x03]
        except KeyError:
            return None

    @Priority.setter
    def Priority(self, value):
        self.__NPDU['Control'] = self.Priorities[value] | 0x04 if value else None

    @property
    def ServiceChoice(self):
        try:
            return swapKV(self.ServiceChoices)[self.__APDU['ServiceChoice']]
        except KeyError:
            return None

    @ServiceChoice.setter
    def ServiceChoice(self, value):
        self.__APDU['ServiceChoice'] = self.ServiceChoices[value]

    @property
    def value(self):
        return self.__APDU['Data'].get('Value')

    @value.setter
    def value(self, value):
        self.__APDU['Data']['Value'] = value

    def getBVLC(self, output_format='BYTES'):
        if output_format == 'BYTES':
            return pack('>BBH', self.__BVLC['Type'], self.__BVLC['Function'], self.__BVLC['Length'])
        elif output_format == 'STRING':
            return 'BACnet:{0}'.format(swapKV(self.BVLCFunctions)[self.__BVLC['Function']])

    def getNPDU(self, output_format='BYTES'):
        if output_format == 'BYTES':
            return pack('>BB', self.__NPDU['Version'], self.__NPDU['Control'])
        elif output_format == 'STRING':
            return "'Version': 1, 'Priority': '{0}'".format(self.Priority)

    def getAPDU(self, output_format='BYTES'):
        if output_format == 'BYTES':
            m = pack('>5BI2B',
                     self.__APDU['Type'] | self.__APDU['PDUFlags'],
                     self.__APDU['MaxResponseSegments'] | self.__APDU['MaxAPDUSize'],
                     self.__APDU['InvokeID'],
                     self.__APDU['ServiceChoice'],
                     0x0C,
                     self.__APDU['Data']['ObjectType'] << 22 | self.__APDU['Data']['Instance Number'],
                     0x19,
                     self.__APDU['Data']['PropertyID'],
                     )
            if self.__APDU['ServiceChoice'] == 15 or self.value is not None:  # 15 == 'WriteProperty'
                ObjectType = self.__APDU['Data']['ObjectType']
                if ObjectType in [0, 1, 2]:  # Analog*, Float
                    m += pack('>2BfB', 0x3E, 0x44, self.value, 0x3F)
                elif ObjectType in [13, 14, 19]:  # MultiState*
                    m += pack('>4B', 0x3E, 0x21, self.value, 0x3F)
                elif ObjectType in [3, 4, 5]:  # Binary*
                    m += pack('>4B', 0x3E, 0x91, self.value, 0x3F)
            return m
        elif output_format == 'STRING':
            m = "'Type': '{0}', 'InvokeID': {1}, 'ServiceChoice': '{2}'".format(
                self.APDUType, self.InvokeID, self.ServiceChoice)
            if self.ServiceChoice == 'WriteProperty' or self.value is not None:
                m += ", 'Data': {" + "'ObjectType': '{0}', 'Instance Number': {1}, 'Priority':{2} 'Value': {3}".format(
                    self.ObjectType, self.InstanceNumber, self.Priority, self.value) + '}'
            else:
                m += ", 'Data': {" + "'ObjectType': '{0}', 'Instance Number': {1}, 'Priority':{2}".format(
                    self.ObjectType, self.InstanceNumber, self.Priority) + '}'
            return m

    def encodeMessage(self, output_format='BYTES'):

        if output_format == 'BYTES':
            m = self.getNPDU() + self.getAPDU()
            self.__BVLC['Length'] = 4 + bLen(m)
            return self.getBVLC() + m
        elif output_format == 'EXTRON':
            return (b'%' + b'%'.join([hexlify(b.to_bytes(1, 'big')) for b in self.encodeMessage()])).decode()
        else:
            raise ValueError('Invalid format: {}'.format(output_format))

    def separateData(self, data):
        Data = list()
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
            length = unpack('>h', m[2:4])[0]  # Separate length and message
            if length == bLen(m):  # Verify length
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
                if self.__APDU['Type'] == 3:  # ComplexACK
                    Data = self.separateData(data)
                    self.__APDU['Data'] = {
                        'ObjectType': Data[0] >> 22,
                        'Instance Number': Data[0] & 0x003FFFFF,
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
