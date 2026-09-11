from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog

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
            'DeviceColorLevel': {'Parameters':['Cluster','Router','Subnet','Device'], 'Status': {}},
            'DeviceColorLevelFadeTime': { 'Status': {}},
            'DeviceColorTemperature': {'Parameters':['Cluster','Router','Subnet','Device'], 'Status': {}},
            'DeviceColorTemperatureFadeTime': { 'Status': {}},
            'DeviceColorXCoordinate': { 'Status': {}},
            'DeviceColorXCoordinateStatus': {'Parameters':['Cluster','Router','Subnet','Device'], 'Status': {}},
            'DeviceColorYCoordinate': { 'Status': {}},
            'DeviceColorYCoordinateStatus': {'Parameters':['Cluster','Router','Subnet','Device'], 'Status': {}},
            'DeviceDirectLevel': {'Parameters': ['Cluster', 'Router', 'Subnet', 'Device'], 'Status': {}},
            'DeviceDirectLevelFadeTime': { 'Status': {}},
            'DeviceDirectProportion': {'Parameters': ['Cluster', 'Router', 'Subnet', 'Device', 'Fade Time'], 'Status': {}},
            'DeviceEmergencyTest': {'Parameters': ['Cluster', 'Router', 'Subnet', 'Device'], 'Status': {}},
            'DeviceRecallScene': {'Parameters': ['Cluster', 'Router', 'Subnet', 'Device', 'Fade Time', 'Block'], 'Status': {}},
            'DeviceSaveAsScene': {'Parameters': ['Cluster', 'Router', 'Subnet', 'Device', 'Force Store', 'Block'], 'Status': {}},
            'DeviceSaveScene': {'Parameters': ['Cluster', 'Router', 'Subnet', 'Device', 'Force Store', 'Block', 'Scene'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'GroupColorLevel': {'Parameters':['Group'], 'Status': {}},
            'GroupColorLevelFadeTime': { 'Status': {}},
            'GroupColorTemperature': {'Parameters':['Group'], 'Status': {}},
            'GroupColorTemperatureFadeTime': { 'Status': {}},
            'GroupColorXCoordinate': { 'Status': {}},
            'GroupColorYCoordinate': { 'Status': {}},
            'GroupDirectLevel': {'Parameters': ['Group'], 'Status': {}},
            'GroupDirectLevelFadeTime': { 'Status': {}},
            'GroupDirectProportion': {'Parameters': ['Group', 'Fade Time'], 'Status': {}},
            'GroupEmergencyTest': {'Parameters': ['Group'], 'Status': {}},
            'GroupRecallScene': {'Parameters': ['Constant Light', 'Fade Time', 'Group', 'Block'], 'Status': {}},
            'GroupRecallSceneStatus': {'Parameters': ['Group', 'Block'], 'Status': {}},
            'GroupSaveAsScene': {'Parameters': ['Force Store', 'Group', 'Block'], 'Status': {}},
            'GroupSaveScene': {'Parameters': ['Force Store', 'Group', 'Block', 'Scene'], 'Status': {}},
            'ModifyProportion': {'Parameters': ['Group'], 'Status': {}},
            'ModifyProportionFadeTime': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'[!?]V:2,C:157,@:([0-9]{1,3})\.([0-9]{1,3})\.([1-4])\.([0-9]{1,3}),A:1=CX:(0\.\d+),CY:(0\.\d+)#'), self.__MatchDeviceColorXCoordinateStatus, None)
            self.AddMatchString(compile(b'[!?]V:2,C:157,@:([0-9]{1,3})\.([0-9]{1,3})\.([1-4])\.([0-9]{1,3}),A:1=K:(\d+)#'), self.__MatchDeviceColorTemperature, None)
            self.AddMatchString(compile(b'[!?]V:1,C:152,@([0-9]{1,3})\.([0-9]{1,3})\.([1-4])\.([0-9]{1,3})=(\d{1,3})#'), self.__MatchDeviceDirectLevel, None)
            self.AddMatchString(compile(b'\?V:1,C:190=([0-9]{8,10})'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'>V:2,C:15,G:([0-9]{1,5}),P:(-?[0-9]{1,3}),F:([0-9]{1,2})(00)?#'), self.__MatchGroupDirectProportion, None)
            self.AddMatchString(compile(b'>V:2,C:11,G:([0-9]{1,5}),B:([1-8]),S:([0-9]{1,2}),F:([0-9]{1,2})(00)?#'), self.__MatchGroupRecallSceneStatus, None)
            self.AddMatchString(compile(b'>V:2,C:17,G:([0-9]{1,5}),P:(-?[0-9]{1,3}),F:([0-9]{1,2})(00)?#'), self.__MatchModifyProportion, None)
            self.AddMatchString(compile(b'!.*=([1-9]|1[0-8])#'), self.__MatchError, None)


    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))


    def SetDeviceColorLevel(self, value, qualifier):

        ClusterConstraints = {
            'Min' : 1,
            'Max' : 253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min' : 1,
            'Max' : 254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min' : 1,
            'Max' : 4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min' : 1,
            'Max' : 255,
            'Value': qualifier['Device']
        }

        fade_time = self.ReadStatus('DeviceColorLevelFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }
        
        x_val = self.ReadStatus('GroupColorXCoordinate', None)
        XCoordinateConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': x_val if (x_val or x_val == 0) else -1
        }
        
        y_val = self.ReadStatus('GroupColorYCoordinate', None)
        YCoordinateConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': y_val if (y_val or y_val == 0) else -1
        }

        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints,
                                     FadeTimeConstraints, XCoordinateConstraints, YCoordinateConstraints):
            DeviceColorLevelCmdString = '>V:2,C:14,@:{0}.{1}.{2}.{3},CX:{4},CY:{5},F:{6},A:1#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'],
                XCoordinateConstraints['Value'],
                YCoordinateConstraints['Value'],
                FadeTimeConstraints['Value']*100)

            self.__SetHelper('DeviceColorLevel', DeviceColorLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceColorLevel')
    def SetDeviceColorLevelFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('DeviceColorLevelFadeTime', value, None)
        else:
            self.Discard('Invalid Command for SetDeviceColorLevelFadeTime')

    def SetDeviceColorXCoordinate(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('DeviceColorXCoordinate', value, None)
        else:
            self.Discard('Invalid Command for SetDeviceColorXCoordinate')

    def SetDeviceColorYCoordinate(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('DeviceColorYCoordinate', value, None)
        else:
            self.Discard('Invalid Command for SetDeviceColorYCoordinate')

    def UpdateDeviceColorXCoordinateStatus(self, value, qualifier):

        ClusterConstraints = {
            'Min' : 1,
            'Max' : 253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min' : 1,
            'Max' : 254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min' : 1,
            'Max' : 4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min' : 1,
            'Max' : 255,
            'Value': qualifier['Device']
        }
        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints):
            DeviceColorXCoordinateStatusCmdString = '>V:2,C:157,@:{0}.{1}.{2}.{3},A:1#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__UpdateHelper('DeviceColorXCoordinateStatus', DeviceColorXCoordinateStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDeviceColorXCoordinateStatus')

    def __MatchDeviceColorXCoordinateStatus(self, match, tag):

        qualifier = {}
        qualifier['Cluster'] = int(match.group(1).decode())
        qualifier['Router'] = int(match.group(2).decode())
        qualifier['Subnet'] = int(match.group(3).decode())
        qualifier['Device'] = int(match.group(4).decode())
        x_value = float(match.group(5).decode())
        y_value = float(match.group(6).decode())
        if 0.00 <= round(x_value, 2) <= 1.00:
            self.WriteStatus('DeviceColorXCoordinateStatus', round(x_value, 2), qualifier)
        if 0.00 <= round(y_value, 2) <= 1.00:
            self.WriteStatus('DeviceColorYCoordinateStatus', round(y_value, 2), qualifier)

    def UpdateDeviceColorYCoordinateStatus(self, value, qualifier):

        ClusterConstraints = {
            'Min' : 1,
            'Max' : 253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min' : 1,
            'Max' : 254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min' : 1,
            'Max' : 4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min' : 1,
            'Max' : 255,
            'Value': qualifier['Device']
        }
        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints):
            self.UpdateDeviceColorXCoordinateStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDeviceColorYCoordinateStatus')

    def SetDeviceColorTemperature(self, value, qualifier):

        ClusterConstraints = {
            'Min' : 1,
            'Max' : 253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min' : 1,
            'Max' : 254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min' : 1,
            'Max' : 4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min' : 1,
            'Max' : 255,
            'Value': qualifier['Device']
        }

        fade_time = self.ReadStatus('DeviceColorTemperatureFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }
        
        ValueConstraints = {
            'Min':   1700,
            'Max':   50000,
            'Value': value
            }

        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints,
                                     FadeTimeConstraints, ValueConstraints):
            DeviceColorTemperatureCmdString = '>V:2,C:14,@:{0}.{1}.{2}.{3},K:{4},F:{5},A:1#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'],
                ValueConstraints['Value'],
                FadeTimeConstraints['Value']*100)
            self.__SetHelper('DeviceColorTemperature', DeviceColorTemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceColorTemperature')

    def UpdateDeviceColorTemperature(self, value, qualifier):

        ClusterConstraints = {
            'Min' : 1,
            'Max' : 253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min' : 1,
            'Max' : 254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min' : 1,
            'Max' : 4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min' : 1,
            'Max' : 255,
            'Value': qualifier['Device']
        }
        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints):
            DeviceColorTemperatureCmdString = '>V:2,C:157,@:{0}.{1}.{2}.{3},A:1#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__UpdateHelper('DeviceColorTemperature', DeviceColorTemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDeviceColorTemperature')

    def __MatchDeviceColorTemperature(self, match, tag):

        qualifier = {}
        qualifier['Cluster'] = int(match.group(1).decode())
        qualifier['Router'] = int(match.group(2).decode())
        qualifier['Subnet'] = int(match.group(3).decode())
        qualifier['Device'] = int(match.group(4).decode())
        value = int(match.group(5).decode())
        if 1700 <= value <= 50000:
            self.WriteStatus('DeviceColorTemperature', value, qualifier)

    def SetDeviceColorTemperatureFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('DeviceColorTemperatureFadeTime', value, None)
        else:
            self.Discard('Invalid Command for SetDeviceColorTemperatureFadeTime')

    def SetDeviceDirectLevel(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
            'Value': value
        }
        
        fade_time = self.ReadStatus('DeviceDirectLevelFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }

        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints,
                                     FadeTimeConstraints, ValueConstraints):
            DeviceDirectLevelCmdString = '>V:1,C:14,L:{0},F:{1},@{2}.{3}.{4}.{5}#'.format(
                ValueConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']),
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__SetHelper('DeviceDirectLevel', DeviceDirectLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceDirectLevel')

    def UpdateDeviceDirectLevel(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints):
            DeviceDirectLevelCmdString = '>V:1,C:152,@{0}.{1}.{2}.{3}#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__UpdateHelper('DeviceDirectLevel', DeviceDirectLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDeviceDirectLevel')

    def __MatchDeviceDirectLevel(self, match, tag):

        qualifier = dict()
        qualifier['Cluster'] = int(match.group(1).decode())
        qualifier['Router'] = int(match.group(2).decode())
        qualifier['Subnet'] = int(match.group(3).decode())
        qualifier['Device'] = int(match.group(4).decode())
        value = int(match.group(5).decode())
        self.WriteStatus('DeviceDirectLevel', value, qualifier)

    def SetDeviceDirectLevelFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
        }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('DeviceDirectLevelFadeTime', value, None)
            
        else:
            self.Discard('Invalid Command for SetDeviceDirectLevelFadeTime')

    def SetDeviceDirectProportion(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': qualifier['Fade Time']
        }

        ValueConstraints = {
            'Min': -100,
            'Max': 100,
            'Value': value
        }

        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints,
                                     FadeTimeConstraints, ValueConstraints):
            DeviceDirectProportionCmdString = '>V:1,C:16,P:{0},F:{1},@{2}.{3}.{4}.{5}#'.format(
                ValueConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']),
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__SetHelper('DeviceDirectProportion', DeviceDirectProportionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceDirectProportion')

    def SetDeviceEmergencyTest(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        ValueStateValues = {
            'Function': '20',
            'Duration': '22',
            'Stop': '24'
        }

        if (self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints) and
                value in ValueStateValues):
            DeviceEmergencyTestCmdString = '>V:1,C:{0},@{1}.{2}.{3}.{4}#'.format(
                ValueStateValues[value],
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__SetHelper('DeviceEmergencyTest', DeviceEmergencyTestCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceEmergencyTest')
    def SetDeviceRecallScene(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': qualifier['Fade Time']
        }

        BlockConstraints = {
            'Min':   1,
            'Max':   8,
            'Value': int(qualifier['Block']) if qualifier['Block'].isdigit() else -1
        }

        ValueConstraints = {
            'Min':   1,
            'Max':   16,
            'Value': int(value) if value.isdigit() else -1
        }

        if self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints,
                                     BlockConstraints, FadeTimeConstraints, ValueConstraints):
            DeviceRecallSceneCmdString = '>V:1,C:12,B:{0},S:{1},F:{2},@{3}.{4}.{5}.{6}#'.format(
                BlockConstraints['Value'],
                ValueConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']),
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'])
            self.__SetHelper('DeviceRecallScene', DeviceRecallSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceRecallScene')
    def SetDeviceSaveAsScene(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        ForceStoreStates = {
            'On':  '1',
            'Off': '0'
        }

        BlockConstraints = {
            'Min':   1,
            'Max':   8,
            'Value': int(qualifier['Block']) if qualifier['Block'].isdigit() else -1
        }

        ValueConstraints = {
            'Min':   1,
            'Max':   16,
            'Value': int(value) if value.isdigit() else -1
        }

        if (self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints, DeviceConstraints,
                                      BlockConstraints, ValueConstraints) and
                qualifier['Force Store'] in ForceStoreStates):
            DeviceSaveAsSceneCmdString = '>V:1,C:204,@{0}.{1}.{2}.{3},O:{4},B:{5},S:{6}#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'],
                ForceStoreStates[qualifier['Force Store']],
                BlockConstraints['Value'],
                ValueConstraints['Value'])
            self.__SetHelper('DeviceSaveAsScene', DeviceSaveAsSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceSaveAsScene')
    def SetDeviceSaveScene(self, value, qualifier):

        ClusterConstraints = {
            'Min':   1,
            'Max':   253,
            'Value': qualifier['Cluster']
        }

        RouterConstraints = {
            'Min':   1,
            'Max':   254,
            'Value': qualifier['Router']
        }

        SubnetConstraints = {
            'Min':   1,
            'Max':   4,
            'Value': qualifier['Subnet']
        }

        DeviceConstraints = {
            'Min':   1,
            'Max':   255,
            'Value': qualifier['Device']
        }

        ForceStoreStates = {
            'On':  '1',
            'Off': '0'
        }

        BlockConstraints = {
            'Min':   1,
            'Max':   8,
            'Value': int(qualifier['Block']) if qualifier['Block'].isdigit() else -1
        }

        SceneConstraints = {
            'Min':   1,
            'Max':   16,
            'Value': int(qualifier['Scene']) if qualifier['Scene'].isdigit() else -1
        }

        lvl_correct = False
        if value.isdigit():
            ValueConstraints = {
                'Min':   0,
                'Max':   100,
                'Value': int(value)
            }
            if self.__constraint_checker(ValueConstraints):
                lvl_value = ValueConstraints['Value']
                lvl_correct = True
        elif value == 'Last Level':
            lvl_value = 253
            lvl_correct = True
        elif value == 'Ignore':
            lvl_value = 254
            lvl_correct = True

        if (lvl_correct and self.__constraint_checker(ClusterConstraints, RouterConstraints, SubnetConstraints,
                                                      DeviceConstraints, SceneConstraints, BlockConstraints) and
                qualifier['Force Store'] in ForceStoreStates):
            DeviceSaveSceneCmdString = '>V:1,C:202,@{0}.{1}.{2}.{3},O:{4},B:{5},S:{6},L:{7}#'.format(
                ClusterConstraints['Value'],
                RouterConstraints['Value'],
                SubnetConstraints['Value'],
                DeviceConstraints['Value'],
                ForceStoreStates[qualifier['Force Store']],
                BlockConstraints['Value'],
                SceneConstraints['Value'],
                lvl_value)
            self.__SetHelper('DeviceSaveScene', DeviceSaveSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceSaveScene')
    def UpdateFirmwareVersion(self, value, qualifier):


        FirmwareVersionCmdString = '>V:1,C:190#'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):


        value = int(match.group(1).decode())
        major = (value & 0xFF000000) >> 24
        minor = (value & 0xFF0000) >> 16
        revision = (value & 0xFF00) >> 8
        value = '{}.{}.{}'.format(major, minor, revision)
        self.WriteStatus('FirmwareVersion', value, None)

    def SetGroupColorLevel(self, value, qualifier):

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }
        
        fade_time = self.ReadStatus('GroupColorLevelFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }
        
        x_val = self.ReadStatus('GroupColorXCoordinate', None)
        XCoordinateConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': x_val if (x_val or x_val == 0) else -1
        }
        
        y_val = self.ReadStatus('GroupColorYCoordinate', None)
        YCoordinateConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': y_val if (y_val or y_val == 0) else -1
        }

        if self.__constraint_checker(GroupConstraints, FadeTimeConstraints,
                                     XCoordinateConstraints, YCoordinateConstraints):
            GroupColorLevelCmdString = '>V:2,C:13,G:{0},CX:{1},CY:{2},F:{3},A:1#'.format(
                GroupConstraints['Value'],
                XCoordinateConstraints['Value'],
                YCoordinateConstraints['Value'],
                FadeTimeConstraints['Value']*100)
            self.__SetHelper('GroupColorLevel', GroupColorLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupColorLevel')
    def SetGroupColorLevelFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('GroupColorLevelFadeTime', value, None)
        else:
            self.Discard('Invalid Command for SetGroupColorLevelFadeTime')

    def SetGroupColorXCoordinate(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('GroupColorXCoordinate', value, None)
        else:
            self.Discard('Invalid Command for SetGroupColorXCoordinate')

    def SetGroupColorYCoordinate(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   1,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('GroupColorYCoordinate', value, None)
        else:
            self.Discard('Invalid Command for SetGroupColorYCoordinate')

    def SetGroupColorTemperature(self, value, qualifier):

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }
        
        fade_time = self.ReadStatus('GroupColorTemperatureFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }

        ValueConstraints = {
            'Min':   1700,
            'Max':   50000,
            'Value': value
            }

        if self.__constraint_checker(GroupConstraints, FadeTimeConstraints, ValueConstraints):
            GroupColorTemperatureCmdString = '>V:2,C:13,G:{0},K:{1},F:{2},A:1#'.format(
                GroupConstraints['Value'],
                ValueConstraints['Value'],
                FadeTimeConstraints['Value']*100)
            self.__SetHelper('GroupColorTemperature', GroupColorTemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupColorTemperature')

    def SetGroupColorTemperatureFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
            }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('GroupColorTemperatureFadeTime', value, None)
        else:
            self.Discard('Invalid Command for SetGroupColorTemperatureFadeTime')

    def SetGroupDirectLevel(self, value, qualifier):

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        ValueConstraints = {
            'Min':   0,
            'Max':   100,
            'Value': value
        }

        fade_time = self.ReadStatus('GroupDirectLevelFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }

        if self.__constraint_checker(GroupConstraints, FadeTimeConstraints, ValueConstraints):
            GroupDirectLevelCmdString = '>V:1,C:13,G:{0},L:{1},F:{2}#'.format(
                GroupConstraints['Value'],
                ValueConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']))
            self.__SetHelper('GroupDirectLevel', GroupDirectLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupDirectLevel')

    def SetGroupDirectLevelFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
        }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('GroupDirectLevelFadeTime', value, None)
            
        else:
            self.Discard('Invalid Command for SetGroupDirectLevelFadeTime')

    def SetGroupDirectProportion(self, value, qualifier):

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': qualifier['Fade Time']
        }

        ValueConstraints = {
            'Min': -100,
            'Max': 100,
            'Value': value
        }

        if self.__constraint_checker(GroupConstraints, FadeTimeConstraints, ValueConstraints):
            GroupDirectProportionCmdString = '>V:1,C:15,P:{0},G:{1},F:{2}#'.format(
                ValueConstraints['Value'],
                GroupConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']))
            self.__SetHelper('GroupDirectProportion', GroupDirectProportionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupDirectProportion')

    def __MatchGroupDirectProportion(self, match, tag):

        qualifier = dict()
        qualifier['Group'] = int(match.group(1).decode())
        qualifier['Fade Time'] = int(match.group(3).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('GroupDirectProportion', value, qualifier)

    def SetGroupEmergencyTest(self, value, qualifier):

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        ValueStateValues = {
            'Function': '19',
            'Duration': '21',
            'Stop':     '23'
        }

        if value in ValueStateValues and self.__constraint_checker(GroupConstraints):
            GroupEmergencyTestCmdString = '>V:1,C:{0},G:{1}#'.format(ValueStateValues[value], GroupConstraints['Value'])
            self.__SetHelper('GroupEmergencyTest', GroupEmergencyTestCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupEmergencyTest')
    def SetGroupRecallScene(self, value, qualifier):

        ConstantLightStates = {
            'On':  '1',
            'Off': '0'
        }

        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': qualifier['Fade Time']
        }

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        BlockConstraints = {
            'Min':   1,
            'Max':   8,
            'Value': int(qualifier['Block']) if qualifier['Block'].isdigit() else -1
        }

        ValueConstraints = {
            'Min':   1,
            'Max':   16,
            'Value': int(value) if value.isdigit() else -1
        }

        if (self.__constraint_checker(GroupConstraints, BlockConstraints, FadeTimeConstraints, ValueConstraints) and
                qualifier['Constant Light'] in ConstantLightStates):
            GroupRecallSceneCmdString = '>V:1,C:11,G:{0},K:{1},B:{2},S:{3},F:{4}#'.format(
                GroupConstraints['Value'],
                ConstantLightStates[qualifier['Constant Light']],
                BlockConstraints['Value'],
                ValueConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']))
            self.__SetHelper('GroupRecallScene', GroupRecallSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupRecallScene')
    def __MatchGroupRecallSceneStatus(self, match, tag):

        qualifier = dict()
        qualifier['Group'] = int(match.group(1).decode())
        qualifier['Block'] = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('GroupRecallSceneStatus', value, qualifier)

    def SetGroupSaveAsScene(self, value, qualifier):

        ForceStoreStates = {
            'On':  '1',
            'Off': '0'
        }

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        BlockConstraints = {
            'Min':   1,
            'Max':   8,
            'Value': int(qualifier['Block']) if qualifier['Block'].isdigit() else -1
        }

        ValueConstraints = {
            'Min':   1,
            'Max':   16,
            'Value': int(value) if value.isdigit() else -1
        }

        if (self.__constraint_checker(GroupConstraints, BlockConstraints, ValueConstraints) and
                qualifier['Force Store'] in ForceStoreStates):
            GroupSaveAsSceneCmdString = '>V:1,C:203,G:{0},O:{1},B:{2},S:{3}#'.format(
                GroupConstraints['Value'],
                ForceStoreStates[qualifier['Force Store']],
                BlockConstraints['Value'],
                ValueConstraints['Value'])
            self.__SetHelper('GroupSaveAsScene', GroupSaveAsSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupSaveAsScene')
    def SetGroupSaveScene(self, value, qualifier):

        ForceStoreStates = {
            'On':  '1',
            'Off': '0'
        }

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        BlockConstraints = {
            'Min':   1,
            'Max':   8,
            'Value': int(qualifier['Block']) if qualifier['Block'].isdigit() else -1
        }

        SceneConstraints = {
            'Min':   1,
            'Max':   16,
            'Value': int(qualifier['Scene']) if qualifier['Scene'].isdigit() else -1
        }

        ValueConstraints = {
            'Min':   0,
            'Max':   100,
            'Value': int(value) if value.isdigit() else -1
        }

        if (self.__constraint_checker(GroupConstraints, SceneConstraints, BlockConstraints, ValueConstraints) and
                qualifier['Force Store'] in ForceStoreStates):
            GroupSaveSceneCmdString = '>V:1,C:201,G:{0},O:{1},B:{2},S:{3},L:{4}#'.format(
                GroupConstraints['Value'],
                ForceStoreStates[qualifier['Force Store']],
                BlockConstraints['Value'],
                SceneConstraints['Value'],
                ValueConstraints['Value'])
            self.__SetHelper('GroupSaveScene', GroupSaveSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupSaveScene')
    def SetModifyProportion(self, value, qualifier):

        GroupConstraints = {
            'Min':   1,
            'Max':   16383,
            'Value': qualifier['Group']
        }

        ValueConstraints = {
            'Min': -100,
            'Max': 100,
            'Value': value
        }

        fade_time = self.ReadStatus('ModifyProportionFadeTime', None)
        FadeTimeConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': fade_time if fade_time else 0
        }

        if self.__constraint_checker(GroupConstraints, FadeTimeConstraints, ValueConstraints):
            ModifyProportionCmdString = '>V:1,C:17,P:{0},G:{1},F:{2}#'.format(
                ValueConstraints['Value'],
                GroupConstraints['Value'],
                ''.join([str(FadeTimeConstraints['Value']), '00']))
            self.__SetHelper('ModifyProportion', ModifyProportionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetModifyProportion')

    def __MatchModifyProportion(self, match, tag):

        qualifier = dict()
        qualifier['Group'] = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('ModifyProportion', value, qualifier)
    def SetModifyProportionFadeTime(self, value, qualifier):

        ValueConstraints = {
            'Min':   0,
            'Max':   90,
            'Value': value
        }

        if self.__constraint_checker(ValueConstraints):
            self.WriteStatus('ModifyProportionFadeTime', value, None)
            
        else:
            self.Discard('Invalid Command for SetModifyProportionFadeTime')

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):
        self.counter = 0

        MatchErrorCodes = {
            '1':  'Invalid group index parameter.',
            '2':  'Invalid cluster parameter.',
            '3':  'Invalid router parameter.',
            '4':  'Invalid subnet parameter.',
            '5':  'Invalid device parameter.',
            '6':  'Invalid sub device parameter.',
            '7':  'Invalid block parameter.',
            '8':  'Invalid scene parameter.',
            '9':  'Cluster does not exist.',
            '10': 'Router does not exist.',
            '11': 'Device does not exist.',
            '12': 'Property does not exist.',
            '13': 'Invalid RAW message size.',
            '14': 'Invalid message type.',
            '15': 'Invalid message command.',
            '16': 'Missing ASCII terminator.',
            '17': 'Missing ASCII parameter.',
            '18': 'Incompatible version.'
        }

        try:
            value = MatchErrorCodes[match.group(1).decode()]
            self.Error([value])
        except KeyError:
            self.Error(['Unknown Error.'])

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
    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

