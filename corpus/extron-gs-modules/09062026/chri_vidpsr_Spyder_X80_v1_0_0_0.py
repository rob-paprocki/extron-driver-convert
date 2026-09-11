# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {} 

        self.Commands = {
            'BasicPreset': {'Parameters':['Type'], 'Status': {}},
            'ClearStillonLayer': {'Parameters':['Layer ID'], 'Status': {}},
            'ClearStillonOutput': {'Parameters':['Output ID'], 'Status': {}},
            'FreezeLayer': {'Parameters':['Layer ID'], 'Status': {}},
            'FreezeOutput': {'Parameters':['Output ID'], 'Status': {}},
            'LoadStillonLayer': {'Parameters':['Layer ID','Filename'], 'Status': {}},
            'LoadStillonOutput': {'Parameters':['Output ID','Filename'], 'Status': {}},
            'OutputConfigurationSave': {'Parameters':['Output ID'], 'Status': {}},
            'RecallScriptCue': {'Parameters':['Register ID','Script Cue Number'], 'Status': {}}
        }

        if 'Serial' not in self.ConnectionType:
            self.header = 'spyder\x00\x00\x00\x00'
            self.footer = '\x20'
        else:
            self.header = ''
            self.footer = '\r'

    def SetBasicPreset(self, value, qualifier):

        TypeStates = {
            'Learn'  : 'BPL ',
            'Recall' : 'BPR '
        }

        if 1 <= int(value) <= 100 and qualifier['Type'] in TypeStates:
            BasicPresetCmdString = self.header + TypeStates[qualifier['Type']] + value + self.footer
            self.__SetHelper('BasicPreset', BasicPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBasicPreset')

    def SetClearStillonLayer(self, value, qualifier):

        layerID = int(qualifier['Layer ID'])
        if 1 <= layerID <= 24:
            ClearStillonLayerCmdString = self.header + 'SCL ' + str(layerID + 1) + self.footer
            self.__SetHelper('ClearStillonLayer', ClearStillonLayerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClearStillonLayer')

    def SetClearStillonOutput(self, value, qualifier):

        outputID = int(qualifier['Output ID'])
        if 1 <= int(qualifier['Output ID']) <= 16:
            ClearStillonOutputCmdString = self.header + 'CSO ' + str(outputID - 1) + self.footer
            self.__SetHelper('ClearStillonOutput', ClearStillonOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClearStillonOutput')

    def SetFreezeLayer(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'FRZ 1 ',
            'Off' : 'FRZ 0 '
        }

        layerID = int(qualifier['Layer ID'])
        if 1 <= layerID <= 24:
            FreezeLayerCmdString = self.header + ValueStateValues[value] + str(layerID + 1) + self.footer
            self.__SetHelper('FreezeLayer', FreezeLayerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreezeLayer')

    def SetFreezeOutput(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'OFZ 1 ',
            'Off' : 'OFZ 0 '
        }

        outputID = int(qualifier['Output ID'])
        if 1 <= int(outputID) <= 16:
            FreezeOutputCmdString = self.header + ValueStateValues[value] + str(outputID - 1) + self.footer
            self.__SetHelper('FreezeOutput', FreezeOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreezeOutput')

    def SetLoadStillonLayer(self, value, qualifier):

        layerID = int(qualifier['Layer ID'])
        if 1 <= layerID <= 24 and qualifier['Filename']:
            LoadStillonLayerCmdString = self.header + 'SLD ' + qualifier['Filename'] + ' ' + str(layerID + 1) + self.footer
            self.__SetHelper('LoadStillonLayer', LoadStillonLayerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadStillonLayer')

    def SetLoadStillonOutput(self, value, qualifier):

        outputID = int(qualifier['Output ID'])
        if 1 <= outputID <= 16 and qualifier['Filename']:
            LoadStillonOutputCmdString = self.header + 'LSO ' + qualifier['Filename'] + ' ' + str(outputID - 1) + self.footer
            self.__SetHelper('LoadStillonOutput', LoadStillonOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadStillonOutput')

    def SetOutputConfigurationSave(self, value, qualifier):

        outputID = int(qualifier['Output ID'])
        if 1 <= outputID <= 16:
            OutputConfigurationSaveCmdString = self.header + 'OCS ' + str(outputID - 1) + self.footer
            self.__SetHelper('OutputConfigurationSave', OutputConfigurationSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputConfigurationSave')

    def SetRecallScriptCue(self, value, qualifier):

        registerID = int(qualifier['Register ID'])
        scriptCueNumber = qualifier['Script Cue Number']
        if 1 <= registerID <= 50 and 1 <= int(scriptCueNumber) <= 50:
            tempRegisterID = registerID - 1
            if 10 < tempRegisterID <= 20:
                registerID = 2000 + tempRegisterID - 10
            elif 20 < tempRegisterID <= 30:
                registerID = 3000 + tempRegisterID - 20
            elif 30 < tempRegisterID <= 40:
                registerID = 4000 + tempRegisterID - 30
            elif 40 < tempRegisterID <= 50:
                registerID = 5000 + tempRegisterID - 40
            else:
                registerID = tempRegisterID
            RecallScriptCueCmdString = self.header + 'RSC ' + str(registerID) + ' ' + scriptCueNumber + self.footer
            self.__SetHelper('RecallScriptCue', RecallScriptCueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallScriptCue')

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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