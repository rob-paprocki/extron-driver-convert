from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DisplayCommand': { 'Status': {}},
            'KnobTurn': { 'Status': {}},
            'Mode': { 'Status': {}},
            'Timer': { 'Status': {}},
            'TimerCommand': {'Parameters':['Type','Format'], 'Status': {}},
            'YellowWarningTimeCommand': {'Parameters':['Type','Format'], 'Status': {}},
        }

    def SetDisplayCommand(self, value, qualifier):

        string = value
        DisplayCommandCmdString = '\nDSP{}\r'.format('' if string is None else string)
        self.__SetHelper('DisplayCommand', DisplayCommandCmdString, value, qualifier)

    def SetKnobTurn(self, value, qualifier):

        ValueStateValues = {
            'Clockwise'       : '+',
            'Counterclockwise': '-'
        }

        if value in ValueStateValues:
            KnobTurnCmdString = '\n\x22KP{}\r'.format(ValueStateValues[value])
            self.__SetHelper('KnobTurn', KnobTurnCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKnobTurn')

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Display Mode (Count Up/Down)' : 'A',
            'Beeper Setup Mode'            : 'a',
            'Select Button (Knob Function)': 'B',
            'Warning Time Setup Mode'      : 'b'
        }

        if value in ValueStateValues:
            ModeCmdString = '\n\x22KP{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Mode', ModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMode')

    def SetTimer(self, value, qualifier):

        ValueStateValues = {
            'Start'     : 'U',
            'Stop'      : 'V',
            'Reset'     : 'K',
            'Start/Stop': 'L'
        }

        if value in ValueStateValues:
            TimerCmdString = '\n\x22KP{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Timer', TimerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimer')

    def SetTimerCommand(self, value, qualifier):

        TypeStates = {
            'Count Up'   : 'U',
            'Count Down' : 'D',
            'Count Start': 'C'
        }

        type_ = qualifier['Type']
        format = qualifier['Format']
        string = value
        try:
            string = string.split(':')
            if len(string) == 3 and format == 'HH:MM:SS':
                hours, minutes, seconds = string[0].zfill(2), string[1].zfill(2), string[2].zfill(2)
            elif len(string) == 2 and format in ['HH:MM', 'MM:SS']:
                if format == 'HH:MM':
                    hours, minutes, seconds = string[0].zfill(2), string[1].zfill(2), '00' 
                else:
                    hours, minutes, seconds = '00', string[0].zfill(2), string[1].zfill(2)
            elif len(string) == 1 and format in ['HH', 'MM', 'SS']:
                if format == 'HH':
                    hours, minutes, seconds = string[0].zfill(2), '00', '00'
                elif format == 'MM':
                    hours, minutes, seconds = '00', string[0].zfill(2), '00'
                else:
                    hours, minutes, seconds = '00', '00', string[0].zfill(2)
            else:
                return self.Discard('Invalid Command for SetTimerCommand')
                
            if type_ in TypeStates and 0 <= int(hours) <= 99 and 0 <= int(minutes) <= 99 and 0 <= int(seconds) <= 99:
                TimerCommandCmdString = '\n\x22T{}{}{}{}\r'.format(TypeStates[type_], hours, minutes, seconds)
                self.__SetHelper('TimerCommand', TimerCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTimerCommand')
        except Exception:
            self.Discard('Invalid Command for SetTimerCommand')

    def SetYellowWarningTimeCommand(self, value, qualifier):

        TypeStates = {
            'Steady': 'W',
            'Blink' : 'G'
        }

        type_ = qualifier['Type']
        format = qualifier['Format']
        string = value
        try:
            string = string.split(':')
            if len(string) == 2 and format == 'MM:SS':
                minutes, seconds = string[0].zfill(2), string[1].zfill(2)
            elif len(string) == 1 and format in ['MM', 'SS']:
                if format == 'MM':
                    minutes, seconds = string[0].zfill(2), '00'
                else:
                    minutes, seconds = '00', string[0].zfill(2)
            else:
                return self.Discard('Invalid Command for SetYellowWarningTimeCommand')

            if type_ in TypeStates and 0 <= int(minutes) <= 99 and 0 <= int(seconds) <= 99:
                YellowWarningTimeCommandCmdString = '\n\x22T{}{}{}\r'.format(TypeStates[type_], minutes, seconds)
                self.__SetHelper('YellowWarningTimeCommand', YellowWarningTimeCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetYellowWarningTimeCommand')
        except Exception:
            self.Discard('Invalid Command for SetYellowWarningTimeCommand')

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

    def __init__(self, Host, Port, Baud=2400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()