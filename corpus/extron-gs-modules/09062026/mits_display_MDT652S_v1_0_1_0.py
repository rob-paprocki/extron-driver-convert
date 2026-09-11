from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
from binascii import hexlify


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

        self._DeviceID = 'A'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.BusyTimer = 0

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if value == 'Broadcast':
            self._DeviceID = '*'
        elif 1 <= int(value) <= 26:
            temp = int(value) + 0x40
            self._DeviceID = '{0}'.format(chr(temp))

    def BuildString(self, buffer):
        CRC = 0
        for i in buffer:
            CRC = CRC ^ i
        return b'\x01' + buffer + pack('>B', CRC) + b'\r'

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': b'1',
            'Off': b'0'
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x02008D000', States[value], b'\x03')
        self.__SetHelper('AudioMute', self.BuildString(buffer), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            b'1': 'On',
            b'0': 'Off',
            b'2': 'Off'
        }

        buffer = pack('>1s1s10s', b'0', bytes(self._DeviceID.encode()), b'0C06\x02008D\x03')
        res = self.__UpdateHelper('AudioMute', self.BuildString(buffer), value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', States[res[-4:-3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        buffer = pack('>1s1s14s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x02001E0001\x03')
        self.__SetHelper('AutoImage', self.BuildString(buffer), value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'Lock': b'1',
            'Primary': b'3',
            'Secondary': b'4',
            'Normal': b'2'
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x02023F000', States[value], b'\x03')
        self.__SetHelper('ExecutiveMode', self.BuildString(buffer), value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'HDMI': b'03',
            'DVI-D': b'04',
            'D-Sub': b'01',
            'BNC': b'02',
            'CAT5': b'08',
            'DisplayPort': b'09',
            'Video': b'05',
            'DVD/HD': b'12',
            'S-Video': b'07',
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x02006000', States[value], b'\x03')
        self.__SetHelper('Input', self.BuildString(buffer), value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            b'03': 'HDMI',
            b'04': 'DVI-D',
            b'01': 'D-Sub',
            b'02': 'BNC',
            b'08': 'CAT5',
            b'09': 'DisplayPort',
            b'05': 'Video',
            b'12': 'DVD/HD',
            b'07': 'S-Video'
        }

        buffer = pack('>1s1s10s', b'0', bytes(self._DeviceID.encode()), b'0C06\x020060\x03')
        res = self.__UpdateHelper('Input', self.BuildString(buffer), value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', States[res[-5:-3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetPIP(self, value, qualifier):

        States = {
            'Off': b'1',
            'On': b'2',
            'Still': b'4'
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x020272000', States[value], b'\x03')
        self.__SetHelper('PIP', self.BuildString(buffer), value, qualifier)

    def SetPIPInput(self, value, qualifier):

        States = {
            'HDMI': b'03',
            'DVI-D': b'04',
            'D-Sub': b'01',
            'BNC': b'02',
            'CAT5': b'08',
            'DisplayPort': b'09',
            'Video': b'05',
            'DVD/HD': b'12',
            'S-Video': b'07',
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x02027300', States[value], b'\x03')
        self.__SetHelper('PIPInput', self.BuildString(buffer), value, qualifier)

    def SetPIPSize(self, value, qualifier):

        States = {
            'Small': b'1',
            'Medium': b'2',
            'Large': b'3'
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0E0A\x020271000', States[value], b'\x03')
        self.__SetHelper('PIPSize', self.BuildString(buffer), value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': b'1',
            'Off': b'4'
        }

        buffer = pack('>1s1s12s1s1s', b'0', bytes(self._DeviceID.encode()), b'0A0C\x02C203D6000', States[value], b'\x03')
        self.__SetHelper('Power', self.BuildString(buffer), value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            b'1': 'On',
            b'4': 'Off',
            b'F': 'Off'
        }

        buffer = pack('>1s1s10s', b'0', bytes(self._DeviceID.encode()), b'0A06\x0201D6\x03')
        res = self.__UpdateHelper('Power', self.BuildString(buffer), value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[res[-4:-3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>1s1s11s1sB', b'0', bytes(self._DeviceID.encode()), b'0E0A\x02006200', result, 0x03)
            self.__SetHelper('Volume', self.BuildString(buffer), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        buffer = pack('>1s1s10s', b'0', bytes(self._DeviceID.encode()), b'0C06\x020062\x03')
        res = self.__UpdateHelper('Volume', self.BuildString(buffer), value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res[-5:-3], 16), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if len(response) == 7:
            self.Error(['{0}: Error Occured'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True'or self._DeviceID == '*':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '*':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.BusyTimer = 0

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()