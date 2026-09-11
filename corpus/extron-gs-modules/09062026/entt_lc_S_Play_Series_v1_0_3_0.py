# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import struct

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'S-Play Lite': self.entt_13_16996_Lite,
            'S-Play Mini': self.entt_13_16996_Mini,
            'S-Play Nano': self.entt_13_16996_Nano
        }

        self.Commands = {
            'Control': {'Parameters':['Playlist'], 'Status': {}},
            'Intensity': {'Parameters':['Playlist'], 'Status': {}}
        }

    def pad(self, value):
        if not isinstance(value, str):
            raise ValueError()

        to_pad = 4 - (len(value) % 4)
        return (value + ('\x00' * to_pad)).encode(encoding='iso-8859-1')

    def ftoh(self, value):
        if not isinstance(value, float):
            raise ValueError()

        return struct.pack('>f', value)

    def build_set_string(self, command, types='', *values):
        try:
            command = self.pad(command) + self.pad(',' + types)

            for i in range(0, len(types)):
                if types[i] == 'f':
                    command += self.ftoh(values[i])
                else:
                    raise ValueError()

            return command
        except ValueError:
            self.Discard('Invalid Command')

    def SetControl(self, value, qualifier):

        ValueStateValues = {
            'Play': 'play',
            'Pause': 'pause',
            'Stop': 'stop'
            }

        
        if qualifier['Playlist'] == "All":
            playlist = 'all'
        else:
            playlist = int(qualifier['Playlist'])
        if playlist == 'all' or 1 <= playlist <= self.playlistNumber and value in ValueStateValues:
            ControlCmdString = self.build_set_string('/splay/playlist/{}/{}'.format(ValueStateValues[value], playlist))
            self.__SetHelper('Control', ControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControl')

    def SetIntensity(self, value, qualifier):

        if qualifier['Playlist'] == "All":
            playlist = 'master'
        else:
            playlist = int(qualifier['Playlist'])

        if playlist == 'master' or 1 <= playlist <= self.playlistNumber and 0 <= value <= 100:
            if playlist == 'master':
                IntensityCmdString = self.build_set_string('/splay/master/intensity',
                                                           'f',
                                                           value/100)
            else:
                IntensityCmdString = self.build_set_string('/splay/playlist/intensity/{}'.format(playlist),
                                                           'f',
                                                           value/100)
            self.__SetHelper('Intensity', IntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIntensity')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def entt_13_16996_Lite(self):

        self.playlistNumber = 100

    def entt_13_16996_Mini(self):

        self.playlistNumber = 8

    def entt_13_16996_Nano(self):

        self.playlistNumber = 4

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