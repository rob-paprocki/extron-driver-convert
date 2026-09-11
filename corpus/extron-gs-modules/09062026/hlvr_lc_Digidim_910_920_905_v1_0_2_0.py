from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait
import time


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceDirectLevel': {'Parameters': ['Device', 'Subnet', 'Router', 'Cluster', 'Fade Time'], 'Status': {}},
            'DeviceDirectLevelWithoutDelay': {'Parameters': ['Device', 'Subnet', 'Router', 'Cluster'], 'Status': {}},
            'DeviceRecallScene': {'Parameters': ['Device', 'Subnet', 'Router', 'Cluster', 'Block', 'Fade Time'], 'Status': {}},
            'DirectProportion': {'Parameters': ['Group', 'Fade Time'], 'Status': {}},
            'EmergencyTest': {'Parameters': ['Group'], 'Status': {}},
            'GroupDirectLevel': {'Parameters': ['Group', 'Fade Time'], 'Status': {}},
            'GroupRecallScene': {'Parameters': ['Group', 'Block', 'Constant Light', 'Fade Time'], 'Status': {}},
            'GroupRecallSceneStatus': {'Parameters': ['Group', 'Block'], 'Status': {}},
            'ModifyProportion': {'Parameters': ['Group', 'Fade Time'], 'Status': {}},
            'ModifyProportionWithoutDelay': {'Parameters': ['Group'], 'Status': {}},
            'UserDefinedString': {'Status': {}}
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'>V:2,C:15,G:([0-9]{1,5}),P:(-?[0-9]{1,3}),F:([0-9]{1,2})(00)?#'), self.__MatchDirectProportion, None)
            self.AddMatchString(re.compile(b'[!|\?]V:1,C:152,@([0-9]{1,3})\.([0-9]{1,3})\.([1-4])\.([0-9]{1,3})=([0-9]{1,3})#'), self.__MatchDeviceDirectLevelWithoutDelay, None)
            self.AddMatchString(re.compile(b'>V:2,C:11,G:([0-9]{1,5}),B:([1-8]),S:([0-9]{1,2}),F:([0-9]{1,2})(00)?#'), self.__MatchGroupRecallSceneStatus, None)
            self.AddMatchString(re.compile(b'>V:2,C:17,G:([0-9]{1,5}),P:(-?[0-9]{1,3}),F:([0-9]{1,2})(00)?#'), self.__MatchModifyProportionWithoutDelay, None)
            self.AddMatchString(re.compile(b'!.*=([0-9]|1[0-8])#'), self.__MatchError, None)

    def SetDeviceDirectLevel(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        FadeTime = qualifier['Fade Time']
        Subnet = qualifier['Subnet']
        Router = qualifier['Router']
        Cluster = qualifier['Cluster']
        Device = qualifier['Device']
        if ((ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= FadeTime <= 90)
            and (1 <= Cluster <= 253) and (1 <= Router <= 254) and (1 <= Subnet <= 4) and (1 <= Device <= 255)):
            FadeTime = str(FadeTime) + '00'
            DeviceDirectLevelCmdString = '>V:1,C:14,L:{0},F:{1},@{2}.{3}.{4}.{5}#'.format(value, FadeTime, Cluster, Router, Subnet, Device)
            self.__SetHelper('DeviceDirectLevel', DeviceDirectLevelCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetDeviceDirectLevel')

    def SetDeviceDirectLevelWithoutDelay(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }
        Subnet = qualifier['Subnet']
        Router = qualifier['Router']
        Cluster = qualifier['Cluster']
        Device = qualifier['Device']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= Cluster <= 253) and (1 <= Router <= 254) and (1 <= Subnet <= 4) and (1 <= Device <= 255):
            DeviceDirectLevelwithoutdelayCmdString = '>V:1,C:14,L:{0},F:000,@{1}.{2}.{3}.{4}#'.format(value, Cluster, Router, Subnet, Device)
            self.__SetHelper('DeviceDirectLevelWithoutDelay', DeviceDirectLevelwithoutdelayCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetDeviceDirectLevelWithoutDelay')

    def UpdateDeviceDirectLevelWithoutDelay(self, value, qualifier):
        Subnet = qualifier['Subnet']
        Router = qualifier['Router']
        Cluster = qualifier['Cluster']
        Device = qualifier['Device']
        if (1 <= Cluster <= 253) and (1 <= Router <= 254) and (1 <= Subnet <= 4) and (1 <= Device <= 255):
            DeviceDirectLevelStausCmdString = '>V:1,C:152,@{0}.{1}.{2}.{3}#'.format(Cluster, Router, Subnet, Device)
            self.__UpdateHelper('DeviceDirectLevelWithoutDelay', DeviceDirectLevelStausCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateDeviceDirectLevelWithoutDelay')

    def __MatchDeviceDirectLevelWithoutDelay(self, match, tag):
        qualifier = {}
        qualifier['Device'] = int(match.group(4).decode())
        qualifier['Subnet'] = int(match.group(3).decode())
        qualifier['Router'] = int(match.group(2).decode())
        qualifier['Cluster'] = int(match.group(1).decode())
        value = int(match.group(5).decode())
        self.WriteStatus('DeviceDirectLevelWithoutDelay', value, qualifier)

    def SetDeviceRecallScene(self, value, qualifier):

        Subnet = qualifier['Subnet']
        Router = qualifier['Router']
        Cluster = qualifier['Cluster']
        Device = qualifier['Device']
        FadeTime = qualifier['Fade Time']
        Block = int(qualifier['Block'])
        Value = int(value)
        if (1 <= Value <= 16 and 1 <= Block <= 8 and 0 <= FadeTime <= 90 and 1 <= Cluster <= 253
            and 1 <= Router <= 254 and 1 <= Subnet <= 4 and 1 <= Device <= 255):
            FadeTime = str(FadeTime) + '00'
            DeviceRecallSceneCmdString = '>V:1,C:12,B:{0},S:{1},F:{2},@{3}.{4}.{5}.{6}#'.format(Block, Value, FadeTime, Cluster, Router, Subnet, Device)
            self.__SetHelper('DeviceRecallScene', DeviceRecallSceneCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDeviceRecallScene')

    def SetDirectProportion(self, value, qualifier):
        ValueConstraints = {
            'Min': -100,
            'Max': 100
            }

        Group = qualifier['Group']
        FadeTime = qualifier['Fade Time']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 0 <= FadeTime <= 90 and 1 <= Group <= 16383:
            FadeTime = str(FadeTime) + '00'
            DirectProportionCmdString = '>V:1,C:15,P:{0},G:{1},F:{2}#'.format(value, Group, FadeTime)
            self.__SetHelper('DirectProportion', DirectProportionCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetDirectProportion')

    def __MatchDirectProportion(self, match, tag):
        qualifier = {}
        qualifier['Group'] = int(match.group(1).decode())
        qualifier['Fade Time'] = int(match.group(3).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('DirectProportion', value, qualifier)

    def SetEmergencyTest(self, value, qualifier):
        GroupConstraints = {
            'Min': 1,
            'Max': 16383
            }

        TypeStateValues = {
            'Function': '19',
            'Duration': '21',
            'Stop': '23'
        }

        Group = qualifier['Group']
        if GroupConstraints['Min'] <= Group <= GroupConstraints['Max']:
            EmergencyTestCmdString = '>V:1,C:{0},G:{1}#'.format(TypeStateValues[value], Group)
            self.__SetHelper('EmergencyTest', EmergencyTestCmdString, value, qualifier)
        else:
            print('Invalid Command for SetEmergencyTest')

    def SetGroupDirectLevel(self, value, qualifier):
        LevelConstraints = {
            'Min': 0,
            'Max': 100
            }

        Group = qualifier['Group']
        FadeTime = qualifier['Fade Time']
        if LevelConstraints['Min'] <= value <= LevelConstraints['Max'] and 0 <= FadeTime <= 90 and 1 <= Group <= 16383:
            FadeTime = str(FadeTime) + '00'
            GroupDirectLevelCmdString = '>V:1,C:13,G:{0},L:{1},F:{2}#'.format(Group, value, FadeTime)
            self.__SetHelper('GroupDirectLevel', GroupDirectLevelCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetGroupDirectLevel')

    def SetGroupRecallScene(self, value, qualifier):

        ConstantLightStates = {
            'On': '1',
            'Off': '0'
        }

        Group = qualifier['Group']
        Block = int(qualifier['Block'])
        FadeTime = qualifier['Fade Time']
        ConstantLightVar = qualifier['Constant Light']
        if 1 <= int(value) <= 16 and ConstantLightVar in ('On', 'Off') and 0 <= FadeTime <= 90 and 1 <= Group <= 16383 and 1 <= Block <= 8:
            FadeTime = str(FadeTime) + '00'
            GroupRecallSceneCmdString = '>V:1,C:11,G:{0},K:{1},B:{2},S:{3},F:{4}#'.format(Group, ConstantLightStates[ConstantLightVar], Block, value, FadeTime)
            self.__SetHelper('GroupRecallScene', GroupRecallSceneCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGroupRecallScene')

    def __MatchGroupRecallSceneStatus(self, match, tag):
        qualifier = {}
        qualifier['Group'] = int(match.group(1).decode())
        qualifier['Block'] = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('GroupRecallSceneStatus', value, qualifier)

    def SetModifyProportion(self, value, qualifier):
        ValueConstraints = {
            'Min': -100,
            'Max': 100
            }

        Group = qualifier['Group']
        FadeTime = qualifier['Fade Time']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 0 <= FadeTime <= 90 and 1 <= Group <= 16383:
            FadeTime = str(FadeTime) + '00'
            ModifyProportionCmdString = '>V:1,C:17,P:{0},G:{1},F:{2}#'.format(value, Group, FadeTime)
            self.__SetHelper('ModifyProportion', ModifyProportionCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetModifyProportion')

    def SetModifyProportionWithoutDelay(self, value, qualifier):
        ValueConstraints = {
            'Min': -100,
            'Max': 100
            }
        Group = qualifier['Group']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= Group <= 16383:
            ModifyProportionWithoutDelayCmdString = '>V:1,C:17,P:{0},G:{1},F:000#'.format(value, Group)
            self.__SetHelper('ModifyProportionWithoutDelay', ModifyProportionWithoutDelayCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetModifyProportionWithoutDelay')

    def __MatchModifyProportionWithoutDelay(self, match, tag):
        qualifier = {}
        qualifier['Group'] = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('ModifyProportion', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()


    def __MatchError(self, match, tag):
        MatchErrorCodes = {
            '0': 'Success',
            '1': 'Invalid group index parameter',
            '2': 'Invalid cluster parameter',
            '3': 'Invalid router parameter',
            '4': 'Invalid subnet parameter',
            '5': 'Invalid device parameter',
            '6': 'Invalid sub device parameter',
            '7': 'Invalid block parameter',
            '8': 'Invalid scene parameter',
            '9': 'Cluster does not exist',
            '10': 'Router does not exist',
            '11': 'Device does not exist',
            '12': 'Property does not exist',
            '13': 'Invalid RAW message size',
            '14': 'Invalid message type',
            '15': 'Invalid message command',
            '16': 'Missing ASCII terminator',
            '17': 'Missing ASCII parameter',
            '18': 'Incompatible version'
        }

        try:
            value = MatchErrorCodes[match.group(1).decode()]
            print(value)
        except KeyError:
            print('Uknown Command')

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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True      

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
