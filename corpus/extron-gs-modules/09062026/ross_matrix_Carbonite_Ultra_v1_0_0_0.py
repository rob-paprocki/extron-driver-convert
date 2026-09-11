from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AutoTransition': {'Parameters':['Source'], 'Status': {}},
            'CustomControl': {'Parameters':['Bank'], 'Status': {}},
            'Cut': {'Parameters':['Source'], 'Status': {}},
            'FadetoBlack': { 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Source','Destination'], 'Status': {}},
            'TransitionRate': {'Parameters':['Source'], 'Status': {}},
            'TransitionType': {'Parameters':['Source'], 'Status': {}},
        }
        
    def SetAutoTransition(self, value, qualifier):

        SourceStates = {
            'MiniME 1' : 'MME:1', 
            'MiniME 2' : 'MME:2', 
            'MiniME 3' : 'MME:3', 
            'MiniME 4' : 'MME:4', 
            'ME 1' : 'ME:1', 
            'ME 2' : 'ME:2', 
            'ME P/P' : 'ME:P/P'
        }

        if qualifier['Source'] in SourceStates:
            AutoTransitionCmdString = 'MEAUTO {}\r\n'.format(SourceStates[qualifier['Source']])
            self.__SetHelper('AutoTransition', AutoTransitionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTransition')

    def SetCustomControl(self, value, qualifier):

        if 1 <= int(qualifier['Bank']) <= 8 and 1 <= int(value) <= 32:
            CustomControlCmdString = 'CC {0}:{1:02}\r\n'.format(qualifier['Bank'], int(value))
            self.__SetHelper('CustomControl', CustomControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCustomControl')

    def SetCut(self, value, qualifier):

        SourceStates = {
            'MiniME 1' : 'MME:1', 
            'MiniME 2' : 'MME:2', 
            'MiniME 3' : 'MME:3', 
            'MiniME 4' : 'MME:4', 
            'ME 1' : 'ME:1', 
            'ME 2' : 'ME:2', 
            'ME P/P' : 'ME:P/P'
        }

        if qualifier['Source'] in SourceStates:
            CutCmdString = 'MECUT {}\r\n'.format(SourceStates[qualifier['Source']])
            self.__SetHelper('Cut', CutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCut')

    def SetFadetoBlack(self, value, qualifier):

        FadetoBlackCmdString = 'FTB\r\n'
        self.__SetHelper('FadetoBlack', FadetoBlackCmdString, value, qualifier)

    def SetMatrixTieCommand(self, value, qualifier):

        SourceStates = {
            'Aux 1' : 'AUX:1', 
            'Aux 2' : 'AUX:2', 
            'Aux 3' : 'AUX:3', 
            'Aux 4' : 'AUX:4', 
            'Aux 5' : 'AUX:5', 
            'Aux 6' : 'AUX:6', 
            'Aux 7' : 'AUX:7', 
            'Aux 8' : 'AUX:8', 
            'Aux 9' : 'AUX:9', 
            'Aux 10' : 'AUX:10', 
            'Aux 11' : 'AUX:11', 
            'Aux 12' : 'AUX:12', 
            'Aux 13' : 'AUX:13', 
            'Aux 14' : 'AUX:14', 
            'Aux 15' : 'AUX:15', 
            'Aux 16' : 'AUX:16', 
            'Aux 17' : 'AUX:17', 
            'Aux 18' : 'AUX:18', 
            'Aux 19' : 'AUX:19', 
            'Aux 20' : 'AUX:20', 
            'Aux 21' : 'AUX:21', 
            'Aux 22' : 'AUX:22', 
            'Aux 23' : 'AUX:23', 
            'Aux 24' : 'AUX:24', 
            'Aux 25' : 'AUX:25', 
            'Aux 26' : 'AUX:26', 
            'Aux 27' : 'AUX:27', 
            'Aux 28' : 'AUX:28', 
            'Black' : 'BK', 
            'Input 1' : 'IN:1', 
            'Input 2' : 'IN:2', 
            'Input 3' : 'IN:3', 
            'Input 4' : 'IN:4', 
            'Input 5' : 'IN:5', 
            'Input 6' : 'IN:6', 
            'Input 7' : 'IN:7', 
            'Input 8' : 'IN:8', 
            'Input 9' : 'IN:9', 
            'Input 10' : 'IN:10', 
            'Input 11' : 'IN:11', 
            'Input 12' : 'IN:12', 
            'Input 13' : 'IN:13', 
            'Input 14' : 'IN:14', 
            'Input 15' : 'IN:15', 
            'Input 16' : 'IN:16', 
            'Input 17' : 'IN:17', 
            'Input 18' : 'IN:18', 
            'Input 19' : 'IN:19', 
            'Input 20' : 'IN:20', 
            'Input 21' : 'IN:21', 
            'Input 22' : 'IN:22', 
            'Input 23' : 'IN:23', 
            'Input 24' : 'IN:24', 
            'Matte Color' : 'BG', 
            'Media-Store 1' : 'MS:1', 
            'Media-Store 2' : 'MS:2', 
            'Media-Store 3' : 'MS:3', 
            'Media-Store 4' : 'MS:4', 
            'ME 1 Program' : 'ME:1:PGM', 
            'ME 2 Program' : 'ME:2:PGM', 
            'ME P/P Program' : 'ME:P/P:PGM', 
            'ME 1 Preview' : 'ME:1:PV', 
            'ME 2 Preview' : 'ME:2:PV', 
            'ME P/P Preview' : 'ME:P/P:PV', 
            'ME 1 Clean' : 'ME:1:CLN', 
            'ME 2 Clean' : 'ME:2:CLN', 
            'ME P/P Clean' : 'ME:P/P:CLN', 
            'ME 1 MediaWipe' : 'ME:1:MW', 
            'ME 2 MediaWipe' : 'ME:2:MW', 
            'ME P/P MediaWipe' : 'ME:P/P:MW', 
            'ME 1 MediaWipe Alpha' : 'ME:1:MWA', 
            'ME 2 MediaWipe Alpha' : 'ME:2:MWA', 
            'ME P/P MediaWipe Alpha' : 'ME:P/P:MWA', 
            'ME 1 Background' : 'ME:1:BKGD', 
            'ME 2 Background' : 'ME:2:BKGD', 
            'ME P/P Background' : 'ME:P/P:BKGD', 
            'ME 1 Preset' : 'ME:1:PST', 
            'ME 2 Preset' : 'ME:2:PST', 
            'ME P/P Preset' : 'ME:P/P:PST', 
            'MiniME 1 Program' : 'MME:1:PGM', 
            'MiniME 2 Program' : 'MME:2:PGM', 
            'MiniME 3 Program' : 'MME:3:PGM', 
            'MiniME 4 Program' : 'MME:4:PGM', 
            'MiniME 1 Preview' : 'MME:1:PV', 
            'MiniME 2 Preview' : 'MME:2:PV', 
            'MiniME 3 Preview' : 'MME:3:PV', 
            'MiniME 4 Preview' : 'MME:4:PV', 
            'MiniME 1 Combined Key' : 'MME:1:CMB', 
            'MiniME 2 Combined Key' : 'MME:2:CMB', 
            'MiniME 3 Combined Key' : 'MME:3:CMB', 
            'MiniME 4 Combined Key' : 'MME:4:CMB', 
            'MiniME 1 Background' : 'MME:1:BKGD', 
            'MiniME 2 Background' : 'MME:2:BKGD', 
            'MiniME 3 Background' : 'MME:3:BKGD', 
            'MiniME 4 Background' : 'MME:4:BKGD', 
            'MiniME 1 Preset' : 'MME:1:PST', 
            'MiniME 2 Preset' : 'MME:2:PST', 
            'MiniME 3 Preset' : 'MME:3:PST', 
            'MiniME 4 Preset' : 'MME:4:PST', 
            'Program' : 'PGM', 
            'Preview' : 'PV', 
            'Clean Feed' : 'CLN'
        }

        DestinationStates = {
            'Aux 1' : 'AUX:1', 
            'Aux 2' : 'AUX:2', 
            'Aux 3' : 'AUX:3', 
            'Aux 4' : 'AUX:4', 
            'Aux 5' : 'AUX:5', 
            'Aux 6' : 'AUX:6', 
            'Aux 7' : 'AUX:7', 
            'Aux 8' : 'AUX:8', 
            'Aux 9' : 'AUX:9', 
            'Aux 10' : 'AUX:10', 
            'Aux 11' : 'AUX:11', 
            'Aux 12' : 'AUX:12', 
            'Aux 13' : 'AUX:13', 
            'Aux 14' : 'AUX:14', 
            'Aux 15' : 'AUX:15', 
            'Aux 16' : 'AUX:16', 
            'Aux 17' : 'AUX:17', 
            'Aux 18' : 'AUX:18', 
            'Aux 19' : 'AUX:19', 
            'Aux 20' : 'AUX:20', 
            'Aux 21' : 'AUX:21', 
            'Aux 22' : 'AUX:22', 
            'Aux 23' : 'AUX:23', 
            'Aux 24' : 'AUX:24', 
            'Aux 25' : 'AUX:25', 
            'Aux 26' : 'AUX:26', 
            'Aux 27' : 'AUX:27', 
            'Aux 28' : 'AUX:28', 
            'MiniME 1' : 'MME:1', 
            'MiniME 2' : 'MME:2', 
            'MiniME 3' : 'MME:3', 
            'MiniME 4' : 'MME:4', 
            'ME 1 Preset' : 'ME:1:PST', 
            'ME 2 Preset' : 'ME:2:PST', 
            'ME P/P Preset' : 'ME:P/P:PST', 
            'ME 1 Program' : 'ME:1:PGM', 
            'ME 2 Program' : 'ME:2:PGM', 
            'ME P/P Program' : 'ME:P/P:PGM'
        }

        if qualifier['Source'] in SourceStates and qualifier['Destination'] in DestinationStates:
            MatrixTieCommandCmdString = 'XPT {}:{}\r\n'.format(DestinationStates[qualifier['Destination']], SourceStates[qualifier['Source']])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetTransitionRate(self, value, qualifier):

        SourceStates = {
            'MiniME 1' : 'MME:1', 
            'MiniME 2' : 'MME:2', 
            'MiniME 3' : 'MME:3', 
            'MiniME 4' : 'MME:4', 
            'ME 1' : 'ME:1', 
            'ME 2' : 'ME:2', 
            'ME P/P' : 'ME:P/P'
        }

        ValueConstraints = {
            'Min' : 1,
            'Max' : 999
            }

        if qualifier['Source'] in SourceStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TransitionRateCmdString = 'TRANSRATE {}:{}\r\n'.format(SourceStates[qualifier['Source']], value)
            self.__SetHelper('TransitionRate', TransitionRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransitionRate')

    def SetTransitionType(self, value, qualifier):

        SourceStates = {
            'MiniME 1' : 'MME:1', 
            'MiniME 2' : 'MME:2', 
            'MiniME 3' : 'MME:3', 
            'MiniME 4' : 'MME:4', 
            'ME 1' : 'ME:1', 
            'ME 2' : 'ME:2', 
            'ME P/P' : 'ME:P/P'
        }

        ValueStateValues = {
            'Dissolve' : 'DISS', 
            'DVE' : 'DVE', 
            'Media Wipe' : 'MEDIA', 
            'Wipe' : 'WIPE'
        }

        if qualifier['Source'] in SourceStates and value in ValueStateValues:
            TransitionTypeCmdString = 'TRANSTYPE {}:{}\r\n'.format(SourceStates[qualifier['Source']], ValueStateValues[value])
            self.__SetHelper('TransitionType', TransitionTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransitionType')

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()