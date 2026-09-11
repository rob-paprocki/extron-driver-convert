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
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Active3DFile': {'Status': {}},
            'ActiveChannelFile': {'Status': {}},
            'ActiveCLUTFile': {'Status': {}},
            'ActiveCSCFile': {'Status': {}},
            'ActiveDegammaFile': {'Status': {}},
            'ActiveEDIDFile': {'Status': {}},
            'ActiveILSFile': {'Status': {}},
            'ActiveMCGDLeftFile': {'Status': {}},
            'ActiveMCGDRightFile': {'Status': {}},
            'ActiveScreenFile': {'Status': {}},
            'ActiveSourceFile': {'Status': {}},
            'ActiveTCGDFile': {'Status': {}},
            'ActiveWarpFile': {'Status': {}},
            'CPULoadPercentage': {'Status': {}},
            'CSenseBoardOnline': {'Status': {}},
            'Dolby3DSystem': {'Status': {}},
            'FreeMemorySpace': {'Status': {}},
            'FreePrimaryDiskSpace': {'Status': {}},
            'LvpsStatusDescription': {'Parameters': ['ID'], 'Status': {}},
            'LvpsStatusValue': {'Parameters': ['ID'], 'Status': {}},
            'MarriageRingTamper': {'Status': {}},
            'NewDrive': {'Status': {}},
            'NumberOfConfiguredDASDevices': {'Status': {}},
            'NumberOfConfiguredNASDevices': {'Status': {}},
            'NumberOfContentDrives': {'Status': {}},
            'NumberOfIngestDrives': {'Status': {}},
            'PhysicalSecurityEnclosureTamper': {'Status': {}},
            'PlayBackAudioBufferPercentage': {'Status': {}},
            'PlayBackAudioDelayInMilliseconds': {'Status': {}},
            'PlayBackAudioSampleRate': {'Status': {}},
            'PlayBackBufferUnderrunError': {'Status': {}},
            'PlayBackContentProcessingError': {'Status': {}},
            'PlayBackCurrentCPLOffsetInMilliseconds': {'Status': {}},
            'PlayBackCurrentCPLUUID': {'Status': {}},
            'PlayBackDolbyConfigFile': {'Status': {}},
            'PlayBackDurationInSeconds': {'Status': {}},
            'PlayBackLoadedContentUUID': {'Status': {}},
            'PlayBackLoadedStage': {'Status': {}},
            'PlayBackLoadedState': {'Status': {}},
            'PlayBackLoopMode': {'Status': {}},
            'PlayBackRealDConfigFile': {'Status': {}},
            'PlayBackState': {'Status': {}},
            'PlayBackTimeInSeconds': {'Status': {}},
            'PlayBackVideoBufferPercentage': {'Status': {}},
            'PrimaryDrive': {'Status': {}},
            'RealD3DEQ': {'Status': {}},
            'SelectedIMBType': {'Status': {}},
            'ServiceDoorTamper': {'Status': {}},
            'SMAlgorithmIntegrity': {'Status': {}},
            'SMBatteryEvent': {'Status': {}},
            'SMBatteryLow': {'Status': {}},
            'SMConnection': {'Status': {}},
            'SMConnectionStatus': {'Status': {}},
            'SMCryptoState': {'Status': {}},
            'SMImageIntegrity': {'Status': {}},
            'SMLogSpaceWarning': {'Status': {}},
            'SMMarriage': {'Status': {}},
            'SMSecurityLogStatus': {'Status': {}},
            'SMTamper': {'Status': {}},
            'SMZeroization': {'Status': {}},
            'StorageActivePath': {'Status': {}},
            'SystemDouser': {'Status': {}},
            'SystemLightSource': {'Status': {}},
            'TemperatureSensorLocation': {'Parameters': ['Sensor ID'], 'Status': {}},
            'TemperatureSensorValue': {'Parameters': ['Sensor ID'], 'Status': {}},
            'TotalMemorySpace': {'Status': {}},
            'TotalPrimaryDiskSpace': {'Status': {}},
            'TotalRootDiskSpace': {'Status': {}},
            'UsedRootDiskSpace': {'Status': {}},
        }

        self.CommandOIDDict = {
            'Active3DFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.6.0',
            'ActiveChannelFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.1.0',
            'ActiveCLUTFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.12.0',
            'ActiveCSCFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.13.0',
            'ActiveDegammaFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.2.0',
            'ActiveEDIDFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.14.0',
            'ActiveILSFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.10.0',
            'ActiveMCGDLeftFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.3.0',
            'ActiveMCGDRightFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.4.0',
            'ActiveScreenFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.8.0',
            'ActiveSourceFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.7.0',
            'ActiveTCGDFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.5.0',
            'ActiveWarpFile': '1.3.6.1.4.1.25766.1.12.1.122.2.6.17.0',
            'CPULoadPercentage': '1.3.6.1.4.1.25766.1.12.1.122.2.5.3.5.0',
            'CSenseBoardOnline': '1.3.6.1.4.1.25766.1.12.1.122.2.5.4.0',
            'Dolby3DSystem': '1.3.6.1.4.1.25766.1.12.1.122.2.6.15.0',
            'FreeMemorySpace': '1.3.6.1.4.1.25766.1.12.1.122.2.5.3.4.0',
            'FreePrimaryDiskSpace': '1.3.6.1.4.1.25766.1.12.1.122.2.8.2.0',
            'Lvps1StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.1',
            'Lvps2StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.2',
            'Lvps3StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.3',
            'Lvps4StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.4',
            'Lvps5StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.5',
            'Lvps6StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.6',
            'Lvps7StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.7',
            'Lvps8StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.8',
            'Lvps9StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.9',
            'Lvps10StatusDescription': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.2.10',
            'Lvps1StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.1',
            'Lvps2StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.2',
            'Lvps3StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.3',
            'Lvps4StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.4',
            'Lvps5StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.5',
            'Lvps6StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.6',
            'Lvps7StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.7',
            'Lvps8StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.8',
            'Lvps9StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.9',
            'Lvps10StatusValue': '1.3.6.1.4.1.25766.1.12.1.122.2.5.7.1.3.10',
            'MarriageRingTamper': '1.3.6.1.4.1.25766.1.12.1.122.2.1.11.0',
            'NewDrive': '1.3.6.1.4.1.25766.1.12.1.122.2.8.5.0',
            'NumberOfConfiguredDASDevices': '1.3.6.1.4.1.25766.1.12.1.122.2.8.7.0',
            'NumberOfConfiguredNASDevices': '1.3.6.1.4.1.25766.1.12.1.122.2.8.6.0',
            'NumberOfContentDrives': '1.3.6.1.4.1.25766.1.12.1.122.2.8.8.0',
            'NumberOfIngestDrives': '1.3.6.1.4.1.25766.1.12.1.122.2.8.9.0',
            'PhysicalSecurityEnclosureTamper': '1.3.6.1.4.1.25766.1.12.1.122.2.1.10.0',
            'PlayBackAudioBufferPercentage': '1.3.6.1.4.1.25766.1.12.1.122.2.7.6.0',
            'PlayBackAudioDelayInMilliseconds': '1.3.6.1.4.1.25766.1.12.1.122.2.7.10.0',
            'PlayBackAudioSampleRate': '1.3.6.1.4.1.25766.1.12.1.122.2.7.11.0',
            'PlayBackBufferUnderrunError': '1.3.6.1.4.1.25766.1.12.1.122.2.7.12.0',
            'PlayBackContentProcessingError': '1.3.6.1.4.1.25766.1.12.1.122.2.7.13.0',
            'PlayBackCurrentCPLOffsetInMilliseconds': '1.3.6.1.4.1.25766.1.12.1.122.2.7.17.0',
            'PlayBackCurrentCPLUUID': '1.3.6.1.4.1.25766.1.12.1.122.2.7.16.0',
            'PlayBackDolbyConfigFile': '1.3.6.1.4.1.25766.1.12.1.122.2.7.15.0',
            'PlayBackDurationInSeconds': '1.3.6.1.4.1.25766.1.12.1.122.2.7.4.0',
            'PlayBackLoadedContentUUID': '1.3.6.1.4.1.25766.1.12.1.122.2.7.2.0',
            'PlayBackLoadedStage': '1.3.6.1.4.1.25766.1.12.1.122.2.7.8.0',
            'PlayBackLoadedState': '1.3.6.1.4.1.25766.1.12.1.122.2.7.7.0',
            'PlayBackLoopMode': '1.3.6.1.4.1.25766.1.12.1.122.2.7.9.0',
            'PlayBackRealDConfigFile': '1.3.6.1.4.1.25766.1.12.1.122.2.7.14.0',
            'PlayBackState': '1.3.6.1.4.1.25766.1.12.1.122.2.7.1.0',
            'PlayBackTimeInSeconds': '1.3.6.1.4.1.25766.1.12.1.122.2.7.3.0',
            'PlayBackVideoBufferPercentage': '1.3.6.1.4.1.25766.1.12.1.122.2.7.5.0',
            'PrimaryDrive': '1.3.6.1.4.1.25766.1.12.1.122.2.8.4.0',
            'RealD3DEQ': '1.3.6.1.4.1.25766.1.12.1.122.2.6.16.0',
            'SelectedIMBType': '1.3.6.1.4.1.25766.1.12.1.122.2.1.16.0',
            'ServiceDoorTamper': '1.3.6.1.4.1.25766.1.12.1.122.2.1.12.0',
            'SMAlgorithmIntegrity': '1.3.6.1.4.1.25766.1.12.1.122.2.1.7.0',
            'SMBatteryEvent': '1.3.6.1.4.1.25766.1.12.1.122.2.1.13.0',
            'SMBatteryLow': '1.3.6.1.4.1.25766.1.12.1.122.2.1.14.0',
            'SMConnection': '1.3.6.1.4.1.25766.1.12.1.122.2.1.1.0',
            'SMConnectionStatus': '1.3.6.1.4.1.25766.1.12.1.122.2.1.2.0',
            'SMCryptoState': '1.3.6.1.4.1.25766.1.12.1.122.2.1.3.0',
            'SMImageIntegrity': '1.3.6.1.4.1.25766.1.12.1.122.2.1.6.0',
            'SMLogSpaceWarning': '1.3.6.1.4.1.25766.1.12.1.122.2.1.9.0',
            'SMMarriage': '1.3.6.1.4.1.25766.1.12.1.122.2.1.5.0',
            'SMSecurityLogStatus': '1.3.6.1.4.1.25766.1.12.1.122.2.1.15.0',
            'SMTamper': '1.3.6.1.4.1.25766.1.12.1.122.2.1.4.0',
            'SMZeroization': '1.3.6.1.4.1.25766.1.12.1.122.2.1.8.0',
            'StorageActivePath': '1.3.6.1.4.1.25766.1.12.1.122.2.8.3.0',
            'SystemDouser': '1.3.6.1.4.1.25766.1.12.1.122.2.5.5.0',
            'SystemLightSource': '1.3.6.1.4.1.25766.1.12.1.122.2.5.6.0',
            'TemperatureSensor1Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.1',
            'TemperatureSensor2Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.2',
            'TemperatureSensor3Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.3',
            'TemperatureSensor4Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.4',
            'TemperatureSensor5Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.5',
            'TemperatureSensor6Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.6',
            'TemperatureSensor7Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.7',
            'TemperatureSensor8Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.8',
            'TemperatureSensor9Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.9',
            'TemperatureSensor10Location': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.2.10',
            'TemperatureSensor1Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.1',
            'TemperatureSensor2Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.2',
            'TemperatureSensor3Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.3',
            'TemperatureSensor4Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.4',
            'TemperatureSensor5Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.5',
            'TemperatureSensor6Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.6',
            'TemperatureSensor7Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.7',
            'TemperatureSensor8Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.8',
            'TemperatureSensor9Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.9',
            'TemperatureSensor10Value': '1.3.6.1.4.1.25766.1.12.1.122.2.2.1.1.3.10',
            'TotalMemorySpace': '1.3.6.1.4.1.25766.1.12.1.122.2.5.3.3.0',
            'TotalPrimaryDiskSpace': '1.3.6.1.4.1.25766.1.12.1.122.2.8.1.0',
            'TotalRootDiskSpace': '1.3.6.1.4.1.25766.1.12.1.122.2.5.3.1.0',
            'UsedRootDiskSpace': '1.3.6.1.4.1.25766.1.12.1.122.2.5.3.2.0'
        }

        self._CommunityString = 'public'
        self.SNMP = SNMPDevice(self._CommunityString, self.CommandOIDDict)

    @property
    def CommunityString(self):
        return self._CommunityString

    @CommunityString.setter
    def CommunityString(self, value):
        self._CommunityString = value
        self.SNMP = SNMPDevice(self._CommunityString, self.CommandOIDDict)

    def UpdateActive3DFile(self, value, qualifier):

        Active3DFileCmdString = self.SNMP.encodeMsg('Get', 'Active3DFile')
        res = self.__UpdateHelper('Active3DFile', Active3DFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('Active3DFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active 3D File: Invalid/unexpected response'])

    def UpdateActiveChannelFile(self, value, qualifier):

        ActiveChannelFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveChannelFile')
        res = self.__UpdateHelper('ActiveChannelFile', ActiveChannelFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveChannelFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active Channel File: Invalid/unexpected response'])

    def UpdateActiveCLUTFile(self, value, qualifier):

        ActiveCLUTFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveCLUTFile')
        res = self.__UpdateHelper('ActiveCLUTFile', ActiveCLUTFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveCLUTFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active CLUT File: Invalid/unexpected response'])

    def UpdateActiveCSCFile(self, value, qualifier):

        ActiveCSCFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveCSCFile')
        res = self.__UpdateHelper('ActiveCSCFile', ActiveCSCFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveCSCFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active CSC File: Invalid/unexpected response'])

    def UpdateActiveDegammaFile(self, value, qualifier):

        ActiveDegammaFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveDegammaFile')
        res = self.__UpdateHelper('ActiveDegammaFile', ActiveDegammaFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveDegammaFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active Degamma File: Invalid/unexpected response'])

    def UpdateActiveEDIDFile(self, value, qualifier):

        ActiveEDIDFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveEDIDFile')
        res = self.__UpdateHelper('ActiveEDIDFile', ActiveEDIDFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveEDIDFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active EDID File: Invalid/unexpected response'])

    def UpdateActiveILSFile(self, value, qualifier):

        ActiveILSFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveILSFile')
        res = self.__UpdateHelper('ActiveILSFile', ActiveILSFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveILSFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active ILS File: Invalid/unexpected response'])

    def UpdateActiveMCGDLeftFile(self, value, qualifier):

        ActiveMCGDLeftFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveMCGDLeftFile')
        res = self.__UpdateHelper('ActiveMCGDLeftFile', ActiveMCGDLeftFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveMCGDLeftFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active MCGD Left File: Invalid/unexpected response'])

    def UpdateActiveMCGDRightFile(self, value, qualifier):

        ActiveMCGDRightFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveMCGDRightFile')
        res = self.__UpdateHelper('ActiveMCGDRightFile', ActiveMCGDRightFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveMCGDRightFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active MCGD Right File: Invalid/unexpected response'])

    def UpdateActiveScreenFile(self, value, qualifier):

        ActiveScreenFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveScreenFile')
        res = self.__UpdateHelper('ActiveScreenFile', ActiveScreenFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveScreenFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active Screen File: Invalid/unexpected response'])

    def UpdateActiveSourceFile(self, value, qualifier):

        ActiveSourceFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveSourceFile')
        res = self.__UpdateHelper('ActiveSourceFile', ActiveSourceFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveSourceFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active Source File: Invalid/unexpected response'])

    def UpdateActiveTCGDFile(self, value, qualifier):

        ActiveTCGDFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveTCGDFile')
        res = self.__UpdateHelper('ActiveTCGDFile', ActiveTCGDFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveTCGDFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active TCGD File: Invalid/unexpected response'])

    def UpdateActiveWarpFile(self, value, qualifier):

        ActiveWarpFileCmdString = self.SNMP.encodeMsg('Get', 'ActiveWarpFile')
        res = self.__UpdateHelper('ActiveWarpFile', ActiveWarpFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ActiveWarpFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Active Warp File: Invalid/unexpected response'])

    def UpdateCPULoadPercentage(self, value, qualifier):

        CPULoadPercentageCmdString = self.SNMP.encodeMsg('Get', 'CPULoadPercentage')
        res = self.__UpdateHelper('CPULoadPercentage', CPULoadPercentageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('CPULoadPercentage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['CPU Load Percentage: Invalid/unexpected response'])

    def UpdateCSenseBoardOnline(self, value, qualifier):

        ValueStateValues = {
            1: 'True',
            2: 'False'
        }

        CSenseBoardOnlineCmdString = self.SNMP.encodeMsg('Get', 'CSenseBoardOnline')
        res = self.__UpdateHelper('CSenseBoardOnline', CSenseBoardOnlineCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('CSenseBoardOnline', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['CSense board online: Invalid/unexpected response'])

    def UpdateDolby3DSystem(self, value, qualifier):

        ValueStateValues = {
            1: 'Enabled',
            2: 'Disabled'
        }

        Dolby3DSystemCmdString = self.SNMP.encodeMsg('Get', 'Dolby3DSystem')
        res = self.__UpdateHelper('Dolby3DSystem', Dolby3DSystemCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Dolby3DSystem', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Dolby 3D System: Invalid/unexpected response'])

    def UpdateFreeMemorySpace(self, value, qualifier):

        FreeMemorySpaceCmdString = self.SNMP.encodeMsg('Get', 'FreeMemorySpace')
        res = self.__UpdateHelper('FreeMemorySpace', FreeMemorySpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('FreeMemorySpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Free Memory Space: Invalid/unexpected response'])

    def UpdateFreePrimaryDiskSpace(self, value, qualifier):

        FreePrimaryDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'FreePrimaryDiskSpace')
        res = self.__UpdateHelper('FreePrimaryDiskSpace', FreePrimaryDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('FreePrimaryDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Free Primary Disk Space: Invalid/unexpected response'])

    def UpdateLvpsStatusDescription(self, value, qualifier):

        id = qualifier['ID']
        if 1 <= int(id) <= 10:
            LvpsStatusDescriptionCmdString = self.SNMP.encodeMsg('Get', 'Lvps{}StatusDescription'.format(id))
            res = self.__UpdateHelper('LvpsStatusDescription', LvpsStatusDescriptionCmdString, value, qualifier, 'Lvps{}StatusDescription'.format(id))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('LvpsStatusDescription', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lvps Status Description: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLvpsStatusDescription')

    def UpdateLvpsStatusValue(self, value, qualifier):

        id = qualifier['ID']
        if 1 <= int(id) <= 10:
            LvpsStatusValueCmdString = self.SNMP.encodeMsg('Get', 'Lvps{}StatusValue'.format(id))
            res = self.__UpdateHelper('LvpsStatusValue', LvpsStatusValueCmdString, value, qualifier, 'Lvps{}StatusValue'.format(id))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('LvpsStatusValue', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lvps Status Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLvpsStatusValue')

    def UpdateMarriageRingTamper(self, value, qualifier):

        MarriageRingTamperCmdString = self.SNMP.encodeMsg('Get', 'MarriageRingTamper')
        res = self.__UpdateHelper('MarriageRingTamper', MarriageRingTamperCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('MarriageRingTamper', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Marriage Ring Tamper: Invalid/unexpected response'])

    def UpdateNewDrive(self, value, qualifier):

        ValueStateValues = {
            1: 'Detected',
            2: 'Undetected'
        }

        NewDriveCmdString = self.SNMP.encodeMsg('Get', 'NewDrive')
        res = self.__UpdateHelper('NewDrive', NewDriveCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('NewDrive', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['New Drive: Invalid/unexpected response'])

    def UpdateNumberOfConfiguredDASDevices(self, value, qualifier):

        NumberOfConfiguredDASDevicesCmdString = self.SNMP.encodeMsg('Get', 'NumberOfConfiguredDASDevices')
        res = self.__UpdateHelper('NumberOfConfiguredDASDevices', NumberOfConfiguredDASDevicesCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('NumberOfConfiguredDASDevices', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Number Of Configured DAS Devices: Invalid/unexpected response'])

    def UpdateNumberOfConfiguredNASDevices(self, value, qualifier):

        NumberOfConfiguredNASDevicesCmdString = self.SNMP.encodeMsg('Get', 'NumberOfConfiguredNASDevices')
        res = self.__UpdateHelper('NumberOfConfiguredNASDevices', NumberOfConfiguredNASDevicesCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('NumberOfConfiguredNASDevices', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Number Of Configured NAS Devices: Invalid/unexpected response'])

    def UpdateNumberOfContentDrives(self, value, qualifier):

        NumberOfContentDrivesCmdString = self.SNMP.encodeMsg('Get', 'NumberOfContentDrives')
        res = self.__UpdateHelper('NumberOfContentDrives', NumberOfContentDrivesCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('NumberOfContentDrives', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Number Of Content Drives: Invalid/unexpected response'])

    def UpdateNumberOfIngestDrives(self, value, qualifier):

        NumberOfIngestDrivesCmdString = self.SNMP.encodeMsg('Get', 'NumberOfIngestDrives')
        res = self.__UpdateHelper('NumberOfIngestDrives', NumberOfIngestDrivesCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('NumberOfIngestDrives', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Number Of Ingest Drives: Invalid/unexpected response'])

    def UpdatePhysicalSecurityEnclosureTamper(self, value, qualifier):

        PhysicalSecurityEnclosureTamperCmdString = self.SNMP.encodeMsg('Get', 'PhysicalSecurityEnclosureTamper')
        res = self.__UpdateHelper('PhysicalSecurityEnclosureTamper', PhysicalSecurityEnclosureTamperCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PhysicalSecurityEnclosureTamper', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Physical Security Enclosure Tamper: Invalid/unexpected response'])

    def UpdatePlayBackAudioBufferPercentage(self, value, qualifier):

        PlayBackAudioBufferPercentageCmdString = self.SNMP.encodeMsg('Get', 'PlayBackAudioBufferPercentage')
        res = self.__UpdateHelper('PlayBackAudioBufferPercentage', PlayBackAudioBufferPercentageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('PlayBackAudioBufferPercentage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Audio Buffer Percentage: Invalid/unexpected response'])

    def UpdatePlayBackAudioDelayInMilliseconds(self, value, qualifier):

        PlayBackAudioDelayInMillisecondsCmdString = self.SNMP.encodeMsg('Get', 'PlayBackAudioDelayInMilliseconds')
        res = self.__UpdateHelper('PlayBackAudioDelayInMilliseconds', PlayBackAudioDelayInMillisecondsCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('PlayBackAudioDelayInMilliseconds', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Audio Delay In Milliseconds: Invalid/unexpected response'])

    def UpdatePlayBackAudioSampleRate(self, value, qualifier):

        ValueStateValues = {
            1: 'Auto',
            2: '48k',
            3: '96k'
        }

        PlayBackAudioSampleRateCmdString = self.SNMP.encodeMsg('Get', 'PlayBackAudioSampleRate')
        res = self.__UpdateHelper('PlayBackAudioSampleRate', PlayBackAudioSampleRateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackAudioSampleRate', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Back Audio Sample Rate: Invalid/unexpected response'])

    def UpdatePlayBackBufferUnderrunError(self, value, qualifier):

        ValueStateValues = {
            1: 'True',
            2: 'False'
        }

        PlayBackBufferUnderrunErrorCmdString = self.SNMP.encodeMsg('Get', 'PlayBackBufferUnderrunError')
        res = self.__UpdateHelper('PlayBackBufferUnderrunError', PlayBackBufferUnderrunErrorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackBufferUnderrunError', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Back Buffer Underrun Error: Invalid/unexpected response'])

    def UpdatePlayBackContentProcessingError(self, value, qualifier):

        ValueStateValues = {
            1: 'True',
            2: 'False'
        }

        PlayBackContentProcessingErrorCmdString = self.SNMP.encodeMsg('Get', 'PlayBackContentProcessingError')
        res = self.__UpdateHelper('PlayBackContentProcessingError', PlayBackContentProcessingErrorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackContentProcessingError', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Back Content Processing Error: Invalid/unexpected response'])

    def UpdatePlayBackCurrentCPLOffsetInMilliseconds(self, value, qualifier):

        PlayBackCurrentCPLOffsetInMillisecondsCmdString = self.SNMP.encodeMsg('Get', 'PlayBackCurrentCPLOffsetInMilliseconds')
        res = self.__UpdateHelper('PlayBackCurrentCPLOffsetInMilliseconds', PlayBackCurrentCPLOffsetInMillisecondsCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('PlayBackCurrentCPLOffsetInMilliseconds', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Current CPL Offset In Milliseconds: Invalid/unexpected response'])

    def UpdatePlayBackCurrentCPLUUID(self, value, qualifier):

        PlayBackCurrentCPLUUIDCmdString = self.SNMP.encodeMsg('Get', 'PlayBackCurrentCPLUUID')
        res = self.__UpdateHelper('PlayBackCurrentCPLUUID', PlayBackCurrentCPLUUIDCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PlayBackCurrentCPLUUID', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Current CPL UUID: Invalid/unexpected response'])

    def UpdatePlayBackDolbyConfigFile(self, value, qualifier):

        PlayBackDolbyConfigFileCmdString = self.SNMP.encodeMsg('Get', 'PlayBackDolbyConfigFile')
        res = self.__UpdateHelper('PlayBackDolbyConfigFile', PlayBackDolbyConfigFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PlayBackDolbyConfigFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Dolby Config File: Invalid/unexpected response'])

    def UpdatePlayBackDurationInSeconds(self, value, qualifier):

        PlayBackDurationInSecondsCmdString = self.SNMP.encodeMsg('Get', 'PlayBackDurationInSeconds')
        res = self.__UpdateHelper('PlayBackDurationInSeconds', PlayBackDurationInSecondsCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('PlayBackDurationInSeconds', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Duration In Seconds: Invalid/unexpected response'])

    def UpdatePlayBackLoadedContentUUID(self, value, qualifier):

        PlayBackLoadedContentUUIDCmdString = self.SNMP.encodeMsg('Get', 'PlayBackLoadedContentUUID')
        res = self.__UpdateHelper('PlayBackLoadedContentUUID', PlayBackLoadedContentUUIDCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PlayBackLoadedContentUUID', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back Loaded Content UUID: Invalid/unexpected response'])

    def UpdatePlayBackLoadedStage(self, value, qualifier):

        ValueStateValues = {
            2: 'Prep Assets',
            3: 'Security',
            4: 'Prep Subtitles',
            5: 'Loaded',
            1: 'None'
        }

        PlayBackLoadedStageCmdString = self.SNMP.encodeMsg('Get', 'PlayBackLoadedStage')
        res = self.__UpdateHelper('PlayBackLoadedStage', PlayBackLoadedStageCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackLoadedStage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Back Loaded Stage: Invalid/unexpected response'])

    def UpdatePlayBackLoadedState(self, value, qualifier):

        ValueStateValues = {
            1: 'loadSuccess',
            185: 'loadErrorNotMarried',
            499: 'loadErrorContentCurrentlyLoaded',
            500: 'loadErrorContentNotLoaded',
            501: 'loadErrorIdNotFound',
            502: 'loadErrorKeyNotFound',
            503: 'loadErrorPlayOk',
            504: 'loadErrorCplIssue',
            505: 'loadErrorCplValidate',
            506: 'loadErrorKdmValidate',
            507: 'loadErrorContentIssue',
            508: 'loadErrorSmFatal',
            509: 'loadErrorSmIssue',
            510: 'loadErrorValidate',
            511: 'loadErrorPrepSuite',
            512: 'loadErrorMissingAssets',
            513: 'loadErrorKdmMissing',
            514: 'loadErrorAssetsHashFailure',
            515: 'loadErrorPrepFailure',
            516: 'loadErrorHfrLicenseRequired',
            518: 'loadErrorTdl',
            519: 'loadErrorKdmHasExpired',
            1309: 'loadErrorKdmHasExpired',
            520: 'loadErrorKdmNotYetValid',
            521: 'loadErrorKdmExtendBeyond6Hours',
            522: 'loadErrorRemoveSlaveOffline',
            523: 'loadErrorRemoveSlaveLoadFailure',
            524: 'loadErrorNoValidKdms',
            1201: 'loadErrorCplNoError',
            1202: 'loadErrorCplNotWellFormatted',
            1203: 'loadErrorCplIntegrityValidationError',
            1204: 'loadErrorCplSignatureValidationError',
            1205: 'loadErrorCplSchemaValidationError',
            1206: 'loadErrorCplCertificateValidationError',
            1207: 'loadErrorCplLogValidationError',
            1208: 'loadErrorCplUnspecifiedError',
            1301: 'loadErrorKdmNoError',
            1302: 'loadErrorKdmNotWellFormatted',
            1303: 'loadErrorKdmIntegrityValidationError',
            1304: 'loadErrorKdmSignatureValidationError',
            1305: 'loadErrorKdmSchemaValidationError',
            1306: 'loadErrorKdmCertificateValidationError',
            1307: 'loadErrorKdmAdditionalValidationError',
            1308: 'loadErrorKdmLogValidationError',
            1310: 'loadErrorKdmStructureIdIncorrect',
            1311: 'loadErrorKdmValidationError',
            1312: 'loadErrorKdmUnspecifiedError',
            1401: 'loadErrorPlayOkNoError',
            1402: 'loadErrorPlayOkCplNotValidated',
            1403: 'loadErrorPlayOkCplValidationError',
            1404: 'loadErrorPlayOkKdmNotValidated',
            1405: 'loadErrorPlayOkPlayNotAllowed',
            1406: 'loadErrorPlayOkTdlValidationError',
            1407: 'loadErrorPlayOkUnableToContactProjector',
            1408: 'loadErrorPlayOkKeyMissing',
            1409: 'loadErrorPlayOkCrossCheckError',
            1410: 'loadErrorPlayOkLogPlayOkError',
            1411: 'loadErrorPlayOkPlayOkNotAllowedInCurrentState',
            1412: 'loadErrorPlayOkPlayOkRspbNotInTdl',
            1413: 'loadErrorPlayOkAssetHashError',
            1414: 'loadErrorPlayOkAssetMissing',
            1415: 'loadErrorPlayOkKeyTypeInconsistent',
            1416: 'loadErrorPlayOkProjectorTypeInconsistent',
            1417: 'loadErrorPlayOkMarriageStateUnknown',
            1418: 'loadErrorPlayOkPlayOkKdmHasExpired',
            1419: 'loadErrorPlayOkUnspecifiedError',
            1501: 'loadErrorPrepSuiteNoError',
            1502: 'loadErrorPrepSuiteCplNotAllowedPlay',
            1503: 'loadErrorPrepSuiteKeysExpired',
            1504: 'loadErrorPrepSuiteTdlValidationError',
            1505: 'loadErrorPrepSuiteProjectorDisconnected',
            1506: 'loadErrorPrepSuiteKeysNotYetValid',
            1507: 'loadErrorPrepSuiteSetLinkToSmError',
            1508: 'loadErrorPrepSuiteKeysExtendBeyondSixHours',
            1509: 'loadErrorPrepSuiteLoadContentKeysError',
            1510: 'loadErrorPrepSuiteLogPrepSuiteFailed',
            1511: 'loadErrorPrepSuiteCmdNotAllowedRightNow',
            1512: 'loadErrorPrepSuiteAssetHashError',
            1513: 'loadErrorPrepSuiteAssetMissing',
            1514: 'loadErrorPrepSuiteUnexpectedError',
            1515: 'loadErrorPrepSuiteRspbLogUploadError',
            1516: 'loadErrorPrepSuiteSetFmToSmError',
            1517: 'loadErrorPrepSuiteCrossCheckError',
            1518: 'loadErrorPrepSuiteCplNotFound',
            1519: 'loadErrorPrepSuiteUnspecifiedError',
            1601: 'loadErrorMarriageNoError',
            1602: 'loadErrorMarriageNotAllowedWhilePlaying',
            1603: 'loadErrorMarriageFailedToComplete',
            1604: 'loadErrorMarriageFailedAuthentication',
            1605: 'loadErrorMarriageUnspecifiedError',
            1701: 'loadErrorPurgeSuiteNoError',
            1702: 'loadErrorPurgeSuitePurgePackagesError',
            1703: 'loadErrorPurgeSuiteClearLeKeyError',
            1704: 'loadErrorPurgeSuiteUnspecifiedError'
        }

        PlayBackLoadedStateCmdString = self.SNMP.encodeMsg('Get', 'PlayBackLoadedState')
        res = self.__UpdateHelper('PlayBackLoadedState', PlayBackLoadedStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackLoadedState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Back Loaded State: Invalid/unexpected response'])

    def UpdatePlayBackLoopMode(self, value, qualifier):

        ValueStateValues = {
            1: 'Enabled',
            2: 'Disabled'
        }

        PlayBackLoopModeCmdString = self.SNMP.encodeMsg('Get', 'PlayBackLoopMode')
        res = self.__UpdateHelper('PlayBackLoopMode', PlayBackLoopModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackLoopMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Playback Loop Mode: Invalid/unexpected response'])

    def UpdatePlayBackRealDConfigFile(self, value, qualifier):

        PlayBackRealDConfigFileCmdString = self.SNMP.encodeMsg('Get', 'PlayBackRealDConfigFile')
        res = self.__UpdateHelper('PlayBackRealDConfigFile', PlayBackRealDConfigFileCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PlayBackRealDConfigFile', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Play Back RealD Config File: Invalid/unexpected response'])

    def UpdatePlayBackState(self, value, qualifier):

        ValueStateValues = {
            1: 'Stop',
            2: 'Play',
            3: 'Pause'
        }

        PlayBackStateCmdString = self.SNMP.encodeMsg('Get', 'PlayBackState')
        res = self.__UpdateHelper('PlayBackState', PlayBackStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PlayBackState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Back State: Invalid/unexpected response'])

    def UpdatePlayBackTimeInSeconds(self, value, qualifier):

        PlayBackTimeInSecondsCmdString = self.SNMP.encodeMsg('Get', 'PlayBackTimeInSeconds')
        res = self.__UpdateHelper('PlayBackTimeInSeconds', PlayBackTimeInSecondsCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('PlayBackTimeInSeconds', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Playback Time In Seconds: Invalid/unexpected response'])

    def UpdatePlayBackVideoBufferPercentage(self, value, qualifier):

        PlayBackVideoBufferPercentageCmdString = self.SNMP.encodeMsg('Get', 'PlayBackVideoBufferPercentage')
        res = self.__UpdateHelper('PlayBackVideoBufferPercentage', PlayBackVideoBufferPercentageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('PlayBackVideoBufferPercentage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Playback Video Buffer Percentage: Invalid/unexpected response'])

    def UpdatePrimaryDrive(self, value, qualifier):

        ValueStateValues = {
            1: 'Available',
            2: 'Unavailable'
        }

        PrimaryDriveCmdString = self.SNMP.encodeMsg('Get', 'PrimaryDrive')
        res = self.__UpdateHelper('PrimaryDrive', PrimaryDriveCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PrimaryDrive', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Primary Drive: Invalid/unexpected response'])

    def UpdateRealD3DEQ(self, value, qualifier):

        ValueStateValues = {
            1: 'Enabled',
            2: 'Disabled'
        }

        RealD3DEQCmdString = self.SNMP.encodeMsg('Get', 'RealD3DEQ')
        res = self.__UpdateHelper('RealD3DEQ', RealD3DEQCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('RealD3DEQ', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['RealD 3D EQ: Invalid/unexpected response'])

    def UpdateSelectedIMBType(self, value, qualifier):

        SelectedIMBTypeCmdString = self.SNMP.encodeMsg('Get', 'SelectedIMBType')
        res = self.__UpdateHelper('SelectedIMBType', SelectedIMBTypeCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SelectedIMBType', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Selected IMB Type: Invalid/unexpected response'])

    def UpdateServiceDoorTamper(self, value, qualifier):

        ServiceDoorTamperCmdString = self.SNMP.encodeMsg('Get', 'ServiceDoorTamper')
        res = self.__UpdateHelper('ServiceDoorTamper', ServiceDoorTamperCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ServiceDoorTamper', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Service Door Tamper: Invalid/unexpected response'])

    def UpdateSMAlgorithmIntegrity(self, value, qualifier):

        SMAlgorithmIntegrityCmdString = self.SNMP.encodeMsg('Get', 'SMAlgorithmIntegrity')
        res = self.__UpdateHelper('SMAlgorithmIntegrity', SMAlgorithmIntegrityCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMAlgorithmIntegrity', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Algorithm Integrity: Invalid/unexpected response'])

    def UpdateSMBatteryEvent(self, value, qualifier):

        SMBatteryEventCmdString = self.SNMP.encodeMsg('Get', 'SMBatteryEvent')
        res = self.__UpdateHelper('SMBatteryEvent', SMBatteryEventCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMBatteryEvent', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Battery Event: Invalid/unexpected response'])

    def UpdateSMBatteryLow(self, value, qualifier):

        SMBatteryLowCmdString = self.SNMP.encodeMsg('Get', 'SMBatteryLow')
        res = self.__UpdateHelper('SMBatteryLow', SMBatteryLowCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMBatteryLow', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Battery Low: Invalid/unexpected response'])

    def UpdateSMConnection(self, value, qualifier):

        ValueStateValues = {
            1: 'Secure',
            2: 'Unsecure'
        }

        SMConnectionCmdString = self.SNMP.encodeMsg('Get', 'SMConnection')
        res = self.__UpdateHelper('SMConnection', SMConnectionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SMConnection', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SM Connection: Invalid/unexpected response'])

    def UpdateSMConnectionStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'Connected',
            2: 'Disconnected'
        }

        SMConnectionStatusCmdString = self.SNMP.encodeMsg('Get', 'SMConnectionStatus')
        res = self.__UpdateHelper('SMConnectionStatus', SMConnectionStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SMConnectionStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SM Connection Status: Invalid/unexpected response'])

    def UpdateSMCryptoState(self, value, qualifier):

        ValueStateValues = {
            2: 'Ok',
            1: 'Failed'
        }

        SMCryptoStateCmdString = self.SNMP.encodeMsg('Get', 'SMCryptoState')
        res = self.__UpdateHelper('SMCryptoState', SMCryptoStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SMCryptoState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SM Crypto State: Invalid/unexpected response'])

    def UpdateSMImageIntegrity(self, value, qualifier):

        SMImageIntegrityCmdString = self.SNMP.encodeMsg('Get', 'SMImageIntegrity')
        res = self.__UpdateHelper('SMImageIntegrity', SMImageIntegrityCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMImageIntegrity', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Image Integrity: Invalid/unexpected response'])

    def UpdateSMLogSpaceWarning(self, value, qualifier):

        SMLogSpaceWarningCmdString = self.SNMP.encodeMsg('Get', 'SMLogSpaceWarning')
        res = self.__UpdateHelper('SMLogSpaceWarning', SMLogSpaceWarningCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMLogSpaceWarning', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Log Space Warning: Invalid/unexpected response'])

    def UpdateSMMarriage(self, value, qualifier):

        SMMarriageCmdString = self.SNMP.encodeMsg('Get', 'SMMarriage')
        res = self.__UpdateHelper('SMMarriage', SMMarriageCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMMarriage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Marriage: Invalid/unexpected response'])

    def UpdateSMSecurityLogStatus(self, value, qualifier):

        SMSecurityLogStatusCmdString = self.SNMP.encodeMsg('Get', 'SMSecurityLogStatus')
        res = self.__UpdateHelper('SMSecurityLogStatus', SMSecurityLogStatusCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMSecurityLogStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Security Log Status: Invalid/unexpected response'])

    def UpdateSMTamper(self, value, qualifier):

        SMTamperCmdString = self.SNMP.encodeMsg('Get', 'SMTamper')
        res = self.__UpdateHelper('SMTamper', SMTamperCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMTamper', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Tamper: Invalid/unexpected response'])

    def UpdateSMZeroization(self, value, qualifier):

        SMZeroizationCmdString = self.SNMP.encodeMsg('Get', 'SMZeroization')
        res = self.__UpdateHelper('SMZeroization', SMZeroizationCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('SMZeroization', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['SM Zeroization: Invalid/unexpected response'])

    def UpdateStorageActivePath(self, value, qualifier):

        StorageActivePathCmdString = self.SNMP.encodeMsg('Get', 'StorageActivePath')
        res = self.__UpdateHelper('StorageActivePath', StorageActivePathCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('StorageActivePath', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Storage Active Path: Invalid/unexpected response'])

    def UpdateSystemDouser(self, value, qualifier):

        ValueStateValues = {
            1: 'Open',
            2: 'Close'
        }

        SystemDouserCmdString = self.SNMP.encodeMsg('Get', 'SystemDouser')
        res = self.__UpdateHelper('SystemDouser', SystemDouserCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SystemDouser', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System Douser: Invalid/unexpected response'])

    def UpdateSystemLightSource(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off'
        }

        SystemLightSourceCmdString = self.SNMP.encodeMsg('Get', 'SystemLightSource')
        res = self.__UpdateHelper('SystemLightSource', SystemLightSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SystemLightSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System Light Source: Invalid/unexpected response'])

    def UpdateTemperatureSensorLocation(self, value, qualifier):

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 10:
            TemperatureSensorLocationCmdString = self.SNMP.encodeMsg('Get', 'TemperatureSensor{}Location'.format(sensorid))
            res = self.__UpdateHelper('TemperatureSensorLocation', TemperatureSensorLocationCmdString, value, qualifier, 'TemperatureSensor{}Location'.format(sensorid))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('TemperatureSensorLocation', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Temperature Sensor Location: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTemperatureSensorLocation')

    def UpdateTemperatureSensorValue(self, value, qualifier):

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 10:
            TemperatureSensorValueCmdString = self.SNMP.encodeMsg('Get', 'TemperatureSensor{}Value'.format(sensorid))
            res = self.__UpdateHelper('TemperatureSensorValue', TemperatureSensorValueCmdString, value, qualifier, 'TemperatureSensor{}Value'.format(sensorid))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('TemperatureSensorValue', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Temperature Sensor Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTemperatureSensorValue')

    def UpdateTotalMemorySpace(self, value, qualifier):

        TotalMemorySpaceCmdString = self.SNMP.encodeMsg('Get', 'TotalMemorySpace')
        res = self.__UpdateHelper('TotalMemorySpace', TotalMemorySpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('TotalMemorySpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Total Memory Space: Invalid/unexpected response'])

    def UpdateTotalPrimaryDiskSpace(self, value, qualifier):

        TotalPrimaryDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'TotalPrimaryDiskSpace')
        res = self.__UpdateHelper('TotalPrimaryDiskSpace', TotalPrimaryDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('TotalPrimaryDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Total Primary Disk Space: Invalid/unexpected response'])

    def UpdateTotalRootDiskSpace(self, value, qualifier):

        TotalRootDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'TotalRootDiskSpace')
        res = self.__UpdateHelper('TotalRootDiskSpace', TotalRootDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('TotalRootDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Total Root Disk Space: Invalid/unexpected response'])

    def UpdateUsedRootDiskSpace(self, value, qualifier):

        UsedRootDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'UsedRootDiskSpace')
        res = self.__UpdateHelper('UsedRootDiskSpace', UsedRootDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('UsedRootDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Used Root Disk Space: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response, checkrescmdname):

        if checkrescmdname:
            response = self.SNMP.decodeMsg(response, command=checkrescmdname)
        else:
            response = self.SNMP.decodeMsg(response, command=sourceCmdName)
        if response[0] != 0:
            self.Error(['{} has error.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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
                if valueLen < 2:  ##fix to make Int32        11/03/14
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
        errorIndex = b'\x02\x01\x00'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x04\x21\xaf\xbb\x7d'
        snmpVersion = b'\x02\x01\x01'
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
                if valueLen < 2:  ##fix to make Int32        11/03/14
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

        varbindListMsg = b''  ## 6/10/15
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        for command2do in command:
            if NextOID:
                oid = self.oidList[command2do] + pack('>B', NextOID)  ## 6/10/15
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
            varbindListMsg += varbindMsg  ## accumulate OIDs
        if len(varbindListMsg) < 128:  ## 6/10/15
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg  ## 6/10/15
        elif len(varbindListMsg) < 4096:  ## 6/10/15
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg)) + varbindListMsg  ## 6/10/15

        pduLen = len(requestID + error + errorIndex + varbindListMsg)  ## 6/10/15
        if pduLen < 128:  ## 6/10/15
            pduLenMsg = pack('>B', pduLen)  ## 6/10/15
        elif pduLen < 4096:  ## 6/10/15
            pduLenMsg = b'\x81' + pack('>B', pduLen)  ## 6/10/15

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg  ## 6/10/15

        snmpLen = len(snmpVersion + self.communityString + snmpPduMsg)  ## 6/10/15
        if snmpLen < 128:  ## 6/10/15
            snmpLenMsg = pack('>B', snmpLen)  ## 6/10/15
        elif snmpLen < 4096:  ## 6/10/15
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)  ## 6/10/15

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg  ## 6/10/15
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

        oidIndex = -1  ################################temp 6/10/15
        valueType = '???'  ################################temp 6/10/15

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
