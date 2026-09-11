from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._Sender = b'\x00\x00'
        self.Models = {}

        self.Commands = {
            'PresetRecall': { 'Status': {}},
            'Screen': { 'Status': {}},
        }

    @property
    def Sender(self):
        return self._Sender

    @Sender.setter
    def Sender(self, value):
        if value == 'All':
            self._Sender = b'\xFF\xFF'
        elif 1 <= int(value) <= 15:
            self._Sender = pack('>h', int(value) - 1)
        else:
            self.Error(['Invalid Sender Parameter range.'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = b'\x74\x00\x11\x00\x00\x00' + self._Sender + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + pack('B', int(value) - 1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetScreen(self, value, qualifier):

        ValueStateValues = {
            'Wakeup'    : b'\x01',
            'Blackout'  : b'\x00'
        }

        if value in ValueStateValues:
            ScreenCmdString = b'\x11\x00\x11\x00\x00\x00' + self._Sender + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + ValueStateValues[value]
            self.__SetHelper('Screen', ScreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreen')

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])