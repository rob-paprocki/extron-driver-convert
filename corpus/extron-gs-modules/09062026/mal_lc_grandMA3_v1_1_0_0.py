# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'CueGo': {'Parameters':['Object'], 'Status': {}},
            'CueGoto': {'Parameters':['Object','Fade Time'], 'Status': {}},
            'FaderMaster': {'Parameters':['Object','Fade Time'], 'Status': {}},
            'MacroRecall': { 'Status': {}},
            'MacroSave': { 'Status': {}},
            'Playback': {'Parameters':['Object'], 'Status': {}}
        }

    def SetCueGo(self, value, qualifier):

        ValueStateValues = {
            'Next':     '+',
            'Previous': '-'
            }

        obj = qualifier['Object']
        if obj != '' and value in ValueStateValues:
            CueGoCmdString = '/cmd\00\00\00\00,s\00\00,Go{} {}'.format(ValueStateValues[value], obj)
            self.__SetHelper('CueGo', CueGoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCueGo')

    def SetCueGoto(self, value, qualifier):

        obj = qualifier['Object']
        time = qualifier['Fade Time']
        if obj != '' and 1 <= int(time) <= 60 and 0 <= value <= 999:
            CueGotoCmdString = '/cmd\00\00\00\00,s\00\00,Goto Cue {} {} Fade {}'.format(value, obj, time)
            self.__SetHelper('CueGoto', CueGotoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCueGoto')

    def SetFaderMaster(self, value, qualifier):

        obj = qualifier['Object']
        time = qualifier['Fade Time']
        if obj != '' and 1 <= int(time) <= 60 and 0 <= value <= 100:
            FaderMasterCmdString = '/cmd\00\00\00\00,s\00\00,FaderMaster {} At {} Fade {}'.format(obj, value, time)
            self.__SetHelper('FaderMaster', FaderMasterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderMaster')

    def SetMacroRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            MacroRecallCmdString = '/cmd\00\00\00\00,s\00\00,Macro {}'.format(value)
            self.__SetHelper('MacroRecall', MacroRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacroRecall')

    def SetMacroSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            MacroSaveCmdString = '/cmd\00\00\00\00,s\00\00,Store Macro {}'.format(value)
            self.__SetHelper('MacroSave', MacroSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacroSave')

    def SetPlayback(self, value, qualifier):

        ValueStateValues = {
            'Resume': 'Off',
            'Pause':  'On'
            }

        obj = qualifier['Object']
        if obj != '' and value in ValueStateValues:
            PlaybackCmdString = '/cmd\00\00\00\00,s\00\00,Pause {} {}'.format(ValueStateValues[value], obj)
            self.__SetHelper('Playback', PlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlayback')

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