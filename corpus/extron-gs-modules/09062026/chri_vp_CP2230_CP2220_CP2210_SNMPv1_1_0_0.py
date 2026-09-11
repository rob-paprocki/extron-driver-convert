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
        self._Writecommunity = 'public'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ACSignal': {'Status': {}},
            'AvailableICPDiskSpace': {'Status': {}},
            'AvailableTPCDiskSpace': {'Status': {}},
            'AvailableTPCMemorySpace': {'Status': {}},
            'BatterySecurity': {'Status': {}},
            'BatteryState': {'Status': {}},
            'BottomEnclosure': {'Status': {}},
            'CertificateState': {'Status': {}},
            'DCSignal': {'Status': {}},
            'FanSensorLocation': {'Parameters': ['Sensor ID'], 'Status': {}},
            'FreeICPDiskSpace': {'Status': {}},
            'ICP1v2Measurement': {'Status': {}},
            'ICP1v8Measurement': {'Status': {}},
            'ICP2v5Measurement': {'Status': {}},
            'ICP3v3Measurement': {'Status': {}},
            'InterlockSensorLocation': {'Parameters': ['Sensor ID'], 'Status': {}},
            'InterlockSensorState': {'Parameters': ['Sensor ID'], 'Status': {}},
            'LDLinkCommunication': {'Status': {}},
            'LDLinkState': {'Parameters': ['Link Number'], 'Status': {}},
            'LogicalMarriageState': {'Status': {}},
            'MarriageState': {'Status': {}},
            'PeripheralsBoardID': {'Status': {}},
            'PeripheralsBootVersion': {'Status': {}},
            'PeripheralsCommunication': {'Status': {}},
            'PhysicalMarriageState': {'Status': {}},
            'Power1v2and2v5Signal': {'Status': {}},
            'Power1v8and3v3Signal': {'Status': {}},
            'Power24VExternal': {'Status': {}},
            'Power24VStandby': {'Status': {}},
            'PowerVidSignal': {'Status': {}},
            'SecurityEnclosure': {'Status': {}},
            'SecurityLog': {'Status': {}},
            'SecurityState': {'Status': {}},
            'ServiceDoor': {'Status': {}},
            'TemperatureSensorLocation': {'Parameters': ['Sensor ID'], 'Status': {}},
            'TemperatureSensorValue': {'Parameters': ['Sensor ID'], 'Status': {}},
            'TopEnclosure': {'Status': {}},
            'TPCOS': {'Status': {}},
            'TPCType': {'Status': {}},
            'UsedTPCDiskSpace': {'Status': {}},
        }

        self.CommandOIDDict = {
            'ACSignal': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.1.0',
            'AvailableICPDiskSpace': '1.3.6.1.4.1.25766.1.12.1.4.2.5.5.1.0',
            'AvailableTPCDiskSpace': '1.3.6.1.4.1.25766.1.12.1.4.2.5.1.3.0',
            'AvailableTPCMemorySpace': '1.3.6.1.4.1.25766.1.12.1.4.2.5.1.5.0',
            'BatterySecurity': '1.3.6.1.4.1.25766.1.12.1.4.2.1.10.0',
            'BatteryState': '1.3.6.1.4.1.25766.1.12.1.4.2.1.11.0',
            'BottomEnclosure': '1.3.6.1.4.1.25766.1.12.1.4.2.1.9.0',
            'CertificateState': '1.3.6.1.4.1.25766.1.12.1.4.2.1.6.0',
            'DCSignal': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.2.0',
            'FanSensor1Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.1',
            'FanSensor2Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.2',
            'FanSensor3Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.3',
            'FanSensor4Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.4',
            'FanSensor5Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.5',
            'FanSensor6Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.6',
            'FanSensor7Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.7',
            'FanSensor8Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.8',
            'FanSensor9Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.2.1.2.9',
            'FreeICPDiskSpace': '1.3.6.1.4.1.25766.1.12.1.4.2.5.5.2.0',
            'ICP1v2Measurement': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.8.0',
            'ICP1v8Measurement': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.9.0',
            'ICP2v5Measurement': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.10.0',
            'ICP3v3Measurement': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.11.0',
            'InterlockSensor1Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.2.1',
            'InterlockSensor2Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.2.2',
            'InterlockSensor3Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.2.3',
            'InterlockSensor4Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.2.4',
            'InterlockSensor1State': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.3.1',
            'InterlockSensor2State': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.3.2',
            'InterlockSensor3State': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.3.3',
            'InterlockSensor4State': '1.3.6.1.4.1.25766.1.12.1.4.2.2.3.1.3.4',
            'LDLinkCommunication': '1.3.6.1.4.1.25766.1.12.1.4.2.5.4.1.0',
            'LDLink0State': '1.3.6.1.4.1.25766.1.12.1.4.2.5.4.2.0',
            'LDLink1State': '1.3.6.1.4.1.25766.1.12.1.4.2.5.4.3.0',
            'LDLink2State': '1.3.6.1.4.1.25766.1.12.1.4.2.5.4.4.0',
            'LDLink3State': '1.3.6.1.4.1.25766.1.12.1.4.2.5.4.5.0',
            'LogicalMarriageState': '1.3.6.1.4.1.25766.1.12.1.4.2.1.5.0',
            'MarriageState': '1.3.6.1.4.1.25766.1.12.1.4.2.1.3.0',
            'PeripheralsBoardID': '1.3.6.1.4.1.25766.1.12.1.4.2.6.1.1.1.2.0',
            'PeripheralsBootVersion': '1.3.6.1.4.1.25766.1.12.1.4.2.6.1.1.1.3.1.0',
            'PeripheralsCommunication': '1.3.6.1.4.1.25766.1.12.1.4.2.6.1.1.1.1.0',
            'PhysicalMarriageState': '1.3.6.1.4.1.25766.1.12.1.4.2.1.4.0',
            'Power1v2and2v5Signal': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.4.0',
            'Power1v8and3v3Signal': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.5.0',
            'Power24VExternal': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.6.0',
            'Power24VStandby': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.7.0',
            'PowerVidSignal': '1.3.6.1.4.1.25766.1.12.1.4.2.5.2.3.0',
            'SecurityEnclosure': '1.3.6.1.4.1.25766.1.12.1.4.2.1.1.0',
            'SecurityLog': '1.3.6.1.4.1.25766.1.12.1.4.2.1.12.0',
            'SecurityState': '1.3.6.1.4.1.25766.1.12.1.4.2.1.2.0',
            'ServiceDoor': '1.3.6.1.4.1.25766.1.12.1.4.2.1.7.0',
            'TemperatureSensor1Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.1',
            'TemperatureSensor2Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.2',
            'TemperatureSensor3Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.3',
            'TemperatureSensor4Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.4',
            'TemperatureSensor5Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.5',
            'TemperatureSensor6Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.6',
            'TemperatureSensor7Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.7',
            'TemperatureSensor8Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.8',
            'TemperatureSensor9Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.9',
            'TemperatureSensor10Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.10',
            'TemperatureSensor11Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.11',
            'TemperatureSensor12Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.12',
            'TemperatureSensor13Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.13',
            'TemperatureSensor14Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.14',
            'TemperatureSensor15Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.15',
            'TemperatureSensor16Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.16',
            'TemperatureSensor17Location': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.2.17',
            'TemperatureSensor1Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.1',
            'TemperatureSensor2Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.2',
            'TemperatureSensor3Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.3',
            'TemperatureSensor4Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.4',
            'TemperatureSensor5Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.5',
            'TemperatureSensor6Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.6',
            'TemperatureSensor7Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.7',
            'TemperatureSensor8Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.8',
            'TemperatureSensor9Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.9',
            'TemperatureSensor10Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.10',
            'TemperatureSensor11Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.11',
            'TemperatureSensor12Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.12',
            'TemperatureSensor13Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.13',
            'TemperatureSensor14Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.14',
            'TemperatureSensor15Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.15',
            'TemperatureSensor16Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.16',
            'TemperatureSensor17Value': '1.3.6.1.4.1.25766.1.12.1.4.2.2.1.1.6.17',
            'TopEnclosure': '1.3.6.1.4.1.25766.1.12.1.4.2.1.8.0',
            'TPCOS': '1.3.6.1.4.1.25766.1.12.1.4.2.5.1.2.0',
            'TPCType': '1.3.6.1.4.1.25766.1.12.1.4.2.5.1.1.0',
            'UsedTPCDiskSpace': '1.3.6.1.4.1.25766.1.12.1.4.2.5.1.4.0'
        }


        self.SNMP = SNMPDevice(self._Writecommunity, self.CommandOIDDict)    
        
    @property
    def Writecommunity(self):
        return self._Writecommunity

    @Writecommunity.setter
    def Writecommunity(self, value):
        self._Writecommunity = value

    def UpdateACSignal(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        ACSignalCmdString = self.SNMP.encodeMsg('Get', 'ACSignal')
        res = self.__UpdateHelper('ACSignal', ACSignalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ACSignal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AC Signal: Invalid/unexpected response'])

    def UpdateAvailableICPDiskSpace(self, value, qualifier):

        AvailableICPDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'AvailableICPDiskSpace')
        res = self.__UpdateHelper('AvailableICPDiskSpace', AvailableICPDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('AvailableICPDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Available ICP Disk Space: Invalid/unexpected response'])

    def UpdateAvailableTPCDiskSpace(self, value, qualifier):

        AvailableTPCDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'AvailableTPCDiskSpace')
        res = self.__UpdateHelper('AvailableTPCDiskSpace', AvailableTPCDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('AvailableTPCDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Available TPC Disk Space: Invalid/unexpected response'])

    def UpdateAvailableTPCMemorySpace(self, value, qualifier):

        AvailableTPCMemorySpaceCmdString = self.SNMP.encodeMsg('Get', 'AvailableTPCMemorySpace')
        res = self.__UpdateHelper('AvailableTPCMemorySpace', AvailableTPCMemorySpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('AvailableTPCMemorySpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Available TPC Memory Space: Invalid/unexpected response'])

    def UpdateBatterySecurity(self, value, qualifier):

        ValueStateValues = {
            2: 'Ok',
            1: 'Failed'
        }

        BatterySecurityCmdString = self.SNMP.encodeMsg('Get', 'BatterySecurity')
        res = self.__UpdateHelper('BatterySecurity', BatterySecurityCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('BatterySecurity', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Battery Security: Invalid/unexpected response'])

    def UpdateBatteryState(self, value, qualifier):

        ValueStateValues = {
            2: 'Ok',
            1: 'Low'
        }

        BatteryStateCmdString = self.SNMP.encodeMsg('Get', 'BatteryState')
        res = self.__UpdateHelper('BatteryState', BatteryStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('BatteryState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Battery State: Invalid/unexpected response'])

    def UpdateBottomEnclosure(self, value, qualifier):

        ValueStateValues = {
            1: 'Tampered',
            2: 'Secure'
        }

        BottomEnclosureCmdString = self.SNMP.encodeMsg('Get', 'BottomEnclosure')
        res = self.__UpdateHelper('BottomEnclosure', BottomEnclosureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('BottomEnclosure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Bottom Enclosure: Invalid/unexpected response'])

    def UpdateCertificateState(self, value, qualifier):

        ValueStateValues = {
            1: 'Zeroed',
            2: 'Ok'
        }

        CertificateStateCmdString = self.SNMP.encodeMsg('Get', 'CertificateState')
        res = self.__UpdateHelper('CertificateState', CertificateStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('CertificateState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Certificate State: Invalid/unexpected response'])

    def UpdateDCSignal(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        DCSignalCmdString = self.SNMP.encodeMsg('Get', 'DCSignal')
        res = self.__UpdateHelper('DCSignal', DCSignalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('DCSignal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['DC Signal: Invalid/unexpected response'])

    def UpdateFanSensorLocation(self, value, qualifier):

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 9:
            FanSensorLocationCmdString = self.SNMP.encodeMsg('Get', 'FanSensor{}Location'.format(sensorid))
            res = self.__UpdateHelper('FanSensorLocation', FanSensorLocationCmdString, value, qualifier, 'FanSensor{}Location'.format(sensorid))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('FanSensorLocation', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Fan Sensor Location: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFanSensorLocation')

    def UpdateFreeICPDiskSpace(self, value, qualifier):

        FreeICPDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'FreeICPDiskSpace')
        res = self.__UpdateHelper('FreeICPDiskSpace', FreeICPDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('FreeICPDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Free ICP Disk Space: Invalid/unexpected response'])

    def UpdateICP1v2Measurement(self, value, qualifier):

        ICP1v2MeasurementCmdString = self.SNMP.encodeMsg('Get', 'ICP1v2Measurement')
        res = self.__UpdateHelper('ICP1v2Measurement', ICP1v2MeasurementCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ICP1v2Measurement', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['ICP 1.2V Measurement: Invalid/unexpected response'])

    def UpdateICP1v8Measurement(self, value, qualifier):

        ICP1v8MeasurementCmdString = self.SNMP.encodeMsg('Get', 'ICP1v8Measurement')
        res = self.__UpdateHelper('ICP1v8Measurement', ICP1v8MeasurementCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ICP1v8Measurement', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['ICP 1.8V Measurement: Invalid/unexpected response'])

    def UpdateICP2v5Measurement(self, value, qualifier):

        ICP2v5MeasurementCmdString = self.SNMP.encodeMsg('Get', 'ICP2v5Measurement')
        res = self.__UpdateHelper('ICP2v5Measurement', ICP2v5MeasurementCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ICP2v5Measurement', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['ICP 2.5V Measurement: Invalid/unexpected response'])

    def UpdateICP3v3Measurement(self, value, qualifier):

        ICP3v3MeasurementCmdString = self.SNMP.encodeMsg('Get', 'ICP3v3Measurement')
        res = self.__UpdateHelper('ICP3v3Measurement', ICP3v3MeasurementCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('ICP3v3Measurement', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['ICP 3.3V Measurement: Invalid/unexpected response'])

    def UpdateLDLinkCommunication(self, value, qualifier):

        ValueStateValues = {
            1: 'Communicating',
            2: 'Not Communicating'
        }

        LDLinkCommunicationCmdString = self.SNMP.encodeMsg('Get', 'LDLinkCommunication')
        res = self.__UpdateHelper('LDLinkCommunication', LDLinkCommunicationCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LDLinkCommunication', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ICP Communcation: Invalid/unexpected response'])

    def UpdateInterlockSensorLocation(self, value, qualifier):

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 4:
            InterlockSensorLocationCmdString = self.SNMP.encodeMsg('Get', 'InterlockSensor{}Location'.format(sensorid))
            res = self.__UpdateHelper('InterlockSensorLocation', InterlockSensorLocationCmdString, value, qualifier, 'InterlockSensor{}Location'.format(sensorid))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('InterlockSensorLocation', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Interlock Sensor Location: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Commnad for UpdateInterlockSensorLocation')

    def UpdateInterlockSensorState(self, value, qualifier):

        ValueStateValues = {
            1: 'Open',
            2: 'Closed',
            3: 'Trouble Open',
            4: 'Trouble Close'
        }

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 4:
            InterlockSensorStateCmdString = self.SNMP.encodeMsg('Get', 'InterlockSensor{}State'.format(sensorid))
            res = self.__UpdateHelper('InterlockSensorState', InterlockSensorStateCmdString, value, qualifier, 'InterlockSensor{}State'.format(sensorid))
            if res:
                try:
                    value = ValueStateValues[res[1]]
                    self.WriteStatus('InterlockSensorState', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Interlock Sensor State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Commnad for UpdateInterlockSensorState')

    def UpdateLDLinkState(self, value, qualifier):

        ValueStateValues = {
            1: 'No Source',
            2: 'Decryption Inactive',
            3: 'Decryption Active',
            4: 'Decryption Error',
            5: 'Unknow'
        }

        linknum = qualifier['Link Number']
        if 0 <= int(linknum) <= 3:
            LDLinkStateCmdString = self.SNMP.encodeMsg('Get', 'LDLink{}State'.format(linknum))
            res = self.__UpdateHelper('LDLinkState', LDLinkStateCmdString, value, qualifier, 'LDLink{}State'.format(linknum))
            if res:
                try:
                    value = ValueStateValues[res[1]]
                    self.WriteStatus('LDLinkState', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['LD Link State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Commnad for UpdateLDLinkState')

    def UpdateLogicalMarriageState(self, value, qualifier):

        ValueStateValues = {
            1: 'Tampered',
            2: 'Secure'
        }

        LogicalMarriageStateCmdString = self.SNMP.encodeMsg('Get', 'LogicalMarriageState')
        res = self.__UpdateHelper('LogicalMarriageState', LogicalMarriageStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LogicalMarriageState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Logical Marriage State: Invalid/unexpected response'])

    def UpdateMarriageState(self, value, qualifier):

        ValueStateValues = {
            1: 'Married',
            2: 'Broken'
        }

        MarriageStateCmdString = self.SNMP.encodeMsg('Get', 'MarriageState')
        res = self.__UpdateHelper('MarriageState', MarriageStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('MarriageState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Marriage State: Invalid/unexpected response'])

    def UpdatePeripheralsBoardID(self, value, qualifier):

        PeripheralsBoardIDCmdString = self.SNMP.encodeMsg('Get', 'PeripheralsBoardID')
        res = self.__UpdateHelper('PeripheralsBoardID', PeripheralsBoardIDCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PeripheralsBoardID', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Peripherals Board ID: Invalid/unexpected response'])

    def UpdatePeripheralsBootVersion(self, value, qualifier):

        PeripheralsBootVersionCmdString = self.SNMP.encodeMsg('Get', 'PeripheralsBootVersion')
        res = self.__UpdateHelper('PeripheralsBootVersion', PeripheralsBootVersionCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('PeripheralsBootVersion', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Peripherals Boot Version: Invalid/unexpected response'])

    def UpdatePeripheralsCommunication(self, value, qualifier):

        ValueStateValues = {
            1: 'Communicating',
            2: 'Not Communicating'
        }

        PeripheralsCommunicationCmdString = self.SNMP.encodeMsg('Get', 'PeripheralsCommunication')
        res = self.__UpdateHelper('PeripheralsCommunication', PeripheralsCommunicationCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PeripheralsCommunication', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Peripherals Communication: Invalid/unexpected response'])

    def UpdatePhysicalMarriageState(self, value, qualifier):

        ValueStateValues = {
            1: 'Tampered',
            2: 'Secure'
        }

        PhysicalMarriageStateCmdString = self.SNMP.encodeMsg('Get', 'PhysicalMarriageState')
        res = self.__UpdateHelper('PhysicalMarriageState', PhysicalMarriageStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PhysicalMarriageState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Physical Marriage State: Invalid/unexpected response'])

    def UpdatePower1v2and2v5Signal(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        Power1v2and2v5SignalCmdString = self.SNMP.encodeMsg('Get', 'Power1v2and2v5Signal')
        res = self.__UpdateHelper('Power1v2and2v5Signal', Power1v2and2v5SignalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power1v2and2v5Signal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power 1.2V & 2.5V Signal: Invalid/unexpected response'])

    def UpdatePower1v8and3v3Signal(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        Power1v8and3v3SignalCmdString = self.SNMP.encodeMsg('Get', 'Power1v8and3v3Signal')
        res = self.__UpdateHelper('Power1v8and3v3Signal', Power1v8and3v3SignalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power1v8and3v3Signal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power 1.8V & 3.3V Signal: Invalid/unexpected response'])

    def UpdatePower24VExternal(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        Power24VExternalCmdString = self.SNMP.encodeMsg('Get', 'Power24VExternal')
        res = self.__UpdateHelper('Power24VExternal', Power24VExternalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power24VExternal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power 24V External: Invalid/unexpected response'])

    def UpdatePower24VStandby(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        Power24VStandbyCmdString = self.SNMP.encodeMsg('Get', 'Power24VStandby')
        res = self.__UpdateHelper('Power24VStandby', Power24VStandbyCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power24VStandby', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power 24V Standby: Invalid/unexpected response'])

    def UpdatePowerVidSignal(self, value, qualifier):

        ValueStateValues = {
            1: 'Active',
            2: 'Inactive'
        }

        PowerVidSignalCmdString = self.SNMP.encodeMsg('Get', 'PowerVidSignal')
        res = self.__UpdateHelper('PowerVidSignal', PowerVidSignalCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PowerVidSignal', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Vid Signal: Invalid/unexpected response'])

    def UpdateSecurityEnclosure(self, value, qualifier):

        ValueStateValues = {
            1: 'Armed',
            2: 'Not Armed'
        }

        SecurityEnclosureCmdString = self.SNMP.encodeMsg('Get', 'SecurityEnclosure')
        res = self.__UpdateHelper('SecurityEnclosure', SecurityEnclosureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SecurityEnclosure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Security Enclosure: Invalid/unexpected response'])

    def UpdateSecurityLog(self, value, qualifier):

        ValueStateValues = {
            1: 'Ok',
            2: 'Warning',
            3: 'Error'
        }

        SecurityLogCmdString = self.SNMP.encodeMsg('Get', 'SecurityLog')
        res = self.__UpdateHelper('SecurityLog', SecurityLogCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SecurityLog', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Security Log: Invalid/unexpected response'])

    def UpdateSecurityState(self, value, qualifier):

        ValueStateValues = {
            1: 'Tampered',
            2: 'Secure'
        }

        SecurityStateCmdString = self.SNMP.encodeMsg('Get', 'SecurityState')
        res = self.__UpdateHelper('SecurityState', SecurityStateCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('SecurityState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Security State: Invalid/unexpected response'])

    def UpdateServiceDoor(self, value, qualifier):

        ValueStateValues = {
            1: 'Tampered',
            2: 'Secure'
        }

        ServiceDoorCmdString = self.SNMP.encodeMsg('Get', 'ServiceDoor')
        res = self.__UpdateHelper('ServiceDoor', ServiceDoorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ServiceDoor', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Service Door: Invalid/unexpected response'])

    def UpdateTemperatureSensorLocation(self, value, qualifier):

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 17:
            TemperatureSensorLocationCmdString = self.SNMP.encodeMsg('Get', 'TemperatureSensor{}Location'.format(sensorid))
            res = self.__UpdateHelper('TemperatureSensorLocation', TemperatureSensorLocationCmdString, value, qualifier, 'TemperatureSensor{}Location'.format(sensorid))
            if res:
                try:
                    value = str(res[1])
                    self.WriteStatus('TemperatureSensorLocation', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Temperature Sensor Location: Invalid/unexpected response'])
        else:
            self.Discard('Invalid command for UpdateTemperatureSensorLocation')

    def UpdateTemperatureSensorValue(self, value, qualifier):

        sensorid = qualifier['Sensor ID']
        if 1 <= int(sensorid) <= 17:
            TemperatureSensorValueCmdString = self.SNMP.encodeMsg('Get', 'TemperatureSensor{}Value'.format(sensorid))
            res = self.__UpdateHelper('TemperatureSensorValue', TemperatureSensorValueCmdString, value, qualifier, 'TemperatureSensor{}Value'.format(sensorid))
            if res:
                try:
                    value = int(res[1])
                    self.WriteStatus('TemperatureSensorValue', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Temperature Sensor Value: Invalid/unexpected response'])
        else:
            self.Discard('Invalid command for UpdateTemperatureSensorValue')

    def UpdateTopEnclosure(self, value, qualifier):

        ValueStateValues = {
            1: 'Tampered',
            2: 'Secure'
        }

        TopEnclosureCmdString = self.SNMP.encodeMsg('Get', 'TopEnclosure')
        res = self.__UpdateHelper('TopEnclosure', TopEnclosureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('TopEnclosure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Top Enclosure: Invalid/unexpected response'])

    def UpdateTPCOS(self, value, qualifier):

        TPCOSCmdString = self.SNMP.encodeMsg('Get', 'TPCOS')
        res = self.__UpdateHelper('TPCOS', TPCOSCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('TPCOS', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['TPC OS: Invalid/unexpected response'])

    def UpdateTPCType(self, value, qualifier):

        TPCTypeCmdString = self.SNMP.encodeMsg('Get', 'TPCType')
        res = self.__UpdateHelper('TPCType', TPCTypeCmdString, value, qualifier)
        if res:
            try:
                value = str(res[1])
                self.WriteStatus('TPCType', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['TPC Type: Invalid/unexpected response'])

    def UpdateUsedTPCDiskSpace(self, value, qualifier):

        UsedTPCDiskSpaceCmdString = self.SNMP.encodeMsg('Get', 'UsedTPCDiskSpace')
        res = self.__UpdateHelper('UsedTPCDiskSpace', UsedTPCDiskSpaceCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('UsedTPCDiskSpace', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Used TPC Disk Space: Invalid/unexpected response'])

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


class SNMPDevice():

    def __init__(self, community, CommandOIDDict):

        self.community = community
        self.CommandOIDDict = CommandOIDDict
        self.oidList = {}
        for command in CommandOIDDict:
            self.oidList[command] = self.__BuildOID(self.CommandOIDDict[command])
        self.community = community
        self._Writecommunity = b'\x04' + pack('>B', len(self.community)) + self.community.encode()
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
        errorIndex = b'\x02\x01\x00'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x04\x21\xaf\xbb\x7d'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg + valueMsg)) + oidMsg + valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(requestID + error + errorIndex + varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(snmpVersion + self._Writecommunity + snmpPduMsg)) + snmpVersion + self._Writecommunity + snmpPduMsg
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

        snmpLen = len(snmpVersion + self._Writecommunity + snmpPduMsg)  # 6/10/15
        if snmpLen < 128:  # 6/10/15
            snmpLenMsg = pack('>B', snmpLen)  # 6/10/15
        elif snmpLen < 4096:  # 6/10/15
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)  # 6/10/15

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self._Writecommunity + snmpPduMsg  # 6/10/15
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
