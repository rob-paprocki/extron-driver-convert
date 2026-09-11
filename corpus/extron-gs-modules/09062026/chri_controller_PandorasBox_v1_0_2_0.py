from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Cue': {'Parameters': ['Virtual COM Port'], 'Status': {}},
            'Transport': {'Parameters': ['Virtual COM Port'], 'Status': {}},

            'SparkRev7Connect': {'Parameters': ['IP Address'], 'Status': {}},
            'SparkRev7Disconnect': {'Status': {}},
            'SparkRev7SetCue': {'Parameters': ['Sequence ID'], 'Status': {}},
            'SparkRev7Transport': {'Parameters': ['Sequence ID'], 'Status': {}},

            'SparkRev16ActivateAll': {'Status': {}},
            'SparkRev16ActivateDevice': {'Parameters': ['Site ID', 'Device ID'], 'Status': {}},
            'SparkRev16ActivateParameter': {'Parameters': ['Device ID', 'Site ID', 'Parameter Name'], 'Status': {}},
            'SparkRev16ActivateSite': {'Parameters': ['Site ID'], 'Status': {}},
            'SparkRev16ClearActiveDevice': {'Parameters': ['Site ID', 'Device ID'], 'Status': {}},
            'SparkRev16ClearActiveParameter': {'Parameters': ['Device ID', 'Site ID', 'Parameter Name'], 'Status': {}},
            'SparkRev16ClearActiveSite': {'Parameters': ['Site ID'], 'Status': {}},
            'SparkRev16ClearAllActive': {'Status': {}},
            'SparkRev16SequenceTransport': {'Parameters': ['Sequence ID'], 'Status': {}},
        }

    def SetCue(self, value, qualifier):

        COM = int(qualifier['Virtual COM Port'])

        if 1 <= int(value) <= 16 and 0 <= COM <= 3:
            Cmdstring = bytes([0xFF, 0, 0, COM]) + '({})'.format(value).encode()
            self.__SetHelper('Cue', Cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCue')

    def SetTransport(self, value, qualifier):

        States = {
            'Play': b'(Play)',
            'Stop': b'(Stop)',
            'Pause': b'(Pause)'
        }

        COM = int(qualifier['Virtual COM Port'])

        if 0 <= COM <= 3:
            Cmdstring = bytes([0xFF, 0, 0, COM]) + States[value]
            self.__SetHelper('Transport', Cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetSparkRev7Connect(self, value, qualifier):

        IPAddr = qualifier['IP Address']
        IPAddr_Valid = False

        res = IPAddr.split('.')
        if len(res) is 4:
            if 0 <= int(res[0]) <= 255 and 0 <= int(res[1]) <= 255 and 0 <= int(res[2]) <= 255 and 0 <= int(res[3]) <= 255:
                IPAddr_Valid = True

        if 1 <= int(value) <= 99 and IPAddr_Valid:
            CmdString = '(PBA,Connect,{0},{1:02d})'.format(IPAddr, int(value))
            self.__SetHelper('SparkRev7Connect', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev7Connect')

    def SetSparkRev7Disconnect(self, value, qualifier):

        self.__SetHelper('SparkRev7Disconnect', '(PBA,Disconnect)', value, qualifier)

    def SetSparkRev7Transport(self, value, qualifier):

        Sequence = int(qualifier['Sequence ID'])

        if 0 <= Sequence <= 99 and value in ['Play', 'Pause', 'Stop']:
            CmdString = '(PBA,SetSeq,{0:02d},{1})'.format(Sequence, value)
            self.__SetHelper('SparkRev7Transport', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev7Transport')

    def SetSparkRev7SetCue(self, value, qualifier):

        Sequence = int(qualifier['Sequence ID'])
        value = int(value)

        if 0 <= Sequence <= 99 and 0 <= value <= 99:
            CmdString = '(PBA,SetCue,{0:02d},{1:02d})'.format(Sequence, value)
            self.__SetHelper('SparkRev7SetCue', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev7SetCue')

    def SetSparkRev16ActivateAll(self, value, qualifier):

        SparkRev16ActivateAllCmdString = '(PBA,ActivateAll)'
        self.__SetHelper('SparkRev16ActivateAll', SparkRev16ActivateAllCmdString, value, qualifier)

    def SetSparkRev16ActivateDevice(self, value, qualifier):

        siteID = int(qualifier['Site ID'])
        deviceID = int(qualifier['Device ID'])

        if 1 <= siteID <= 99 and 1 <= deviceID <= 99:
            SparkRev16ActivateDeviceCmdString = '(PBA,ActivateDevice,{0:02d},{1:02d})'.format(siteID, deviceID)
            self.__SetHelper('SparkRev16ActivateDevice', SparkRev16ActivateDeviceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16ActivateDevice')

    def SetSparkRev16ActivateParameter(self, value, qualifier):

        siteID = int(qualifier['Site ID'])
        deviceID = int(qualifier['Device ID'])
        ParamName = qualifier['Parameter Name']

        if 1 <= siteID <= 99 and 1 <= deviceID <= 99 and ParamName:
            SparkRev16ActivateParameterCmdString = '(PBA,ActivateParam,{0:02d},{1:02d},{2})'.format(siteID, deviceID, ParamName)
            self.__SetHelper('SparkRev16ActivateParameter', SparkRev16ActivateParameterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16ActivateParameter')

    def SetSparkRev16ActivateSite(self, value, qualifier):

        siteID = int(qualifier['Site ID'])

        if 1 <= siteID <= 99:
            SparkRev16ActivateSiteCmdString = '(PBA,ActivateSite,{0:02d})'.format(siteID)
            self.__SetHelper('SparkRev16ActivateSite', SparkRev16ActivateSiteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16ActivateSite')

    def SetSparkRev16ClearActiveDevice(self, value, qualifier):

        siteID = int(qualifier['Site ID'])
        deviceID = int(qualifier['Device ID'])

        if 1 <= siteID <= 99 and 1 <= deviceID <= 99:
            SparkRev16ClearActiveDeviceCmdString = '(PBA,ClearActiveDevice,{0:02d},{1:02d})'.format(siteID, deviceID)
            self.__SetHelper('SparkRev16ClearActiveDevice', SparkRev16ClearActiveDeviceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16ClearActiveDevice')

    def SetSparkRev16ClearActiveParameter(self, value, qualifier):

        siteID = int(qualifier['Site ID'])
        deviceID = int(qualifier['Device ID'])
        ParamName = qualifier['Parameter Name']

        if 1 <= siteID <= 99 and 1 <= deviceID <= 99 and ParamName:
            SparkRev16ClearActiveParameterCmdString = '(PBA,ClearActiveParam,{0:02d},{1:02d},{2})'.format(siteID, deviceID, ParamName)
            self.__SetHelper('SparkRev16ClearActiveParameter', SparkRev16ClearActiveParameterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16ClearActiveParameter')

    def SetSparkRev16ClearActiveSite(self, value, qualifier):

        siteID = int(qualifier['Site ID'])

        if 1 <= siteID <= 99:
            SparkRev16ClearActiveSiteCmdString = '(PBA,ClearActiveSite,{0:02d})'.format(siteID)
            self.__SetHelper('SparkRev16ClearActiveSite', SparkRev16ClearActiveSiteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16ClearActiveSite')

    def SetSparkRev16ClearAllActive(self, value, qualifier):

        SparkRev16ClearAllActiveCmdString = '(PBA,ClearAllActive)'
        self.__SetHelper('SparkRev16ClearAllActive', SparkRev16ClearAllActiveCmdString, value, qualifier)

    def SetSparkRev16SequenceTransport(self, value, qualifier):

        ValueStateValues = {
            'Next Cue': 'SeqNextCue',
            'Last Cue': 'SeqLastCue',
            'Next Frame': 'SeqNextFrame',
            'Last Frame': 'SeqLastFrame'
        }
        seqID = int(qualifier['Sequence ID'])

        if 1 <= seqID <= 99:
            SparkRev16SequenceTransportCmdString = '(PBA,{0},{1:02d})'.format(ValueStateValues[value], seqID)
            self.__SetHelper('SparkRev16SequenceTransport', SparkRev16SequenceTransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSparkRev16SequenceTransport')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return

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
            raise AttributeError(command + 'does not support Set.')


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
