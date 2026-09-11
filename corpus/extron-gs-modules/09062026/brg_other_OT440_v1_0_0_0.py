from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = '01'
        self.Models = {}
        self.Commands = {
            'LongDurationTimer': { 'Status': {}},
            'ResetTimer': { 'Status': {}},
            'TimerControl': { 'Status': {}},
            'TimerEndTime': {'Parameters':['Seconds','Minutes','Hours'], 'Status': {}},
            'TimerStartTime': {'Parameters':['Seconds','Minutes','Hours'], 'Status': {}},
        }                    

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{:02}'.format(int(value))

    def SetLongDurationTimer(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        LongDurationTimerCmdString = '*!{0}64{1}{2}#'.format(self._DeviceID, ValueStateValues[value], 'x' * 27)
        self.__SetHelper('LongDurationTimer', LongDurationTimerCmdString, value, qualifier)

    def SetResetTimer(self, value, qualifier):

        ResetTimerCmdString = '*!{0}63{1}#'.format(self._DeviceID, 'x' * 28)
        self.__SetHelper('ResetTimer', ResetTimerCmdString, value, qualifier)

    def SetTimerControl(self, value, qualifier):

        ValueStateValues = {
            'Start / Pause' : '61',
            'Stop'          : '62'
        }

        TimerControlCmdString = '*!{0}{1}{2}#'.format(self._DeviceID, ValueStateValues[value],'x' * 28)
        self.__SetHelper('TimerControl', TimerControlCmdString, value, qualifier)

    def SetTimerEndTime(self, value, qualifier):

        if 0 <= qualifier['Seconds'] <= 59 and 0 <= qualifier['Minutes'] <= 59 and 0 <= qualifier['Hours'] <= 23:
            TimerEndTimeCmdString = '*!{0}52{1:02}{2:02}{3:02}{4}#'.format(self._DeviceID, qualifier['Seconds'], qualifier['Minutes'],
                                                                           qualifier['Hours'], 'x' * 22)
            self.__SetHelper('TimerEndTime', TimerEndTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimerEndTime')

    def SetTimerStartTime(self, value, qualifier):

        if 0 <= qualifier['Seconds'] <= 59 and 0 <= qualifier['Minutes'] <= 59 and 0 <= qualifier['Hours'] <= 23:
            TimerStartTimeCmdString = '*!{0}53{1:02}{2:02}{3:02}{4}#'.format(self._DeviceID, qualifier['Seconds'], qualifier['Minutes'],
                                                                           qualifier['Hours'], 'x' * 22)
            self.__SetHelper('TimerStartTime', TimerStartTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimerStartTime')

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

