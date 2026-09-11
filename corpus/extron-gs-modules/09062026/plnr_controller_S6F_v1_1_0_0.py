# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = b'\xFF\xFF'
        self.Models = {}

        self.Commands = {
            'Brightness': { 'Status': {}},
            'ColorTemperature': { 'Status': {}},
            'Input': { 'Status': {}},
            'Show': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = b'\xFF\xFF'
        elif value == 'First S6F':
            self._DeviceID = b'\x00\x00'
        elif value == 'Second S6F':
            self._DeviceID = b'\x00\x01'
        else:
            self.Error(['Invalid Device ID parameter.'])

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = b''.join([b'\x21\x00\x14\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', pack('<f', value / 100)])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetColorTemperature(self, value, qualifier):

        ValueConstraints = {
            'Min': 2000,
            'Max': 10000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ColorTemperatureCmdString = b''.join([b'\x22\x00\x12\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', pack('<h', value)])
            self.__SetHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorTemperature')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': b'\x10',
            'DVI':  b'\x01'
        }

        if value in ValueStateValues:
            InputCmdString = b''.join([b'\x33\x00\x12\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetShow(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x01',
            'Off':  b'\x00'
        }

        if value in ValueStateValues:
            ShowCmdString = b''.join([b'\x11\x00\x11\x00\x00\x00', self._DeviceID, b'\xFF\x00\x00\x00\x00\x00\x00\x00', ValueStateValues[value]])
            self.__SetHelper('Show', ShowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShow')

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