from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video 1': b'\x02\x01',
            'Video 2': b'\x02\x02',
            'Component': b'\x03\x01',
            'HDMI 1': b'\x04\x01',
            'HDMI 2': b'\x04\x02',
            'HDMI 3': b'\x04\x03',
            'HDMI 4': b'\x04\x04',
            'PC': b'\x05\x01'
        }

        InputValue = ValueStateValues[value]
        checksum = 145 + int(InputValue[0]) + int(InputValue[1])

        InputCmdString = pack('<BBBBBBB', 0x8C, 0x00, 0x02, 0x03, InputValue[0], InputValue[1], checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x02\x01': 'Video 1',
            b'\x02\x02': 'Video 2',
            b'\x03\x01': 'Component',
            b'\x04\x01': 'HDMI 1',
            b'\x04\x02': 'HDMI 2',
            b'\x04\x03': 'HDMI 3',
            b'\x04\x04': 'HDMI 4',
            b'\x05\x01': 'PC'
        }

        InputCmdString = b'\x83\x00\x02\xFF\xFF\x83'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid command for UpdateInput')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x01',
            'Off': b'\x01\x00'
        }

        MuteValue = ValueStateValues[value]
        checksum = 149 + int(MuteValue[0]) + int(MuteValue[1])

        MuteCmdString = pack('<BBBBBBB', 0x8C, 0x00, 0x06, 0x03, MuteValue[0], MuteValue[1], checksum)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': b'\x01\x00',
            'Standard': b'\x01\x01',
            'Custom': b'\x01\x03'
        }

        if value == 'Toggle':
            PictureModeCmdString = b'\x8C\x00\x20\x02\x00\xAE'
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            PictureModeValue = ValueStateValues[value]
            checksum = 175 + int(PictureModeValue[0]) + int(PictureModeValue[1])
            PictureModeCmdString = pack('<BBBBBBB', 0x8C, 0x00, 0x20, 0x03, PictureModeValue[0], PictureModeValue[1], checksum)
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        PowerValue = ValueStateValues[value]
        checksum = 142 + int(PowerValue[0])

        PowerCmdString = pack('<BBBBBB', 0x8C, 0x00, 0x00, 0x02, PowerValue[0], checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)  

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\x83\x00\x00\xFF\xFF\x81'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid command for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x00\x00',
            'Down': b'\x00\x01'
        }

        VolumeValue = ValueStateValues[value]
        checksum = 148 + int(VolumeValue[0]) + int(VolumeValue[1])

        VolumeCmdString = pack('<BBBBBBB', 0x8C, 0x00, 0x05, 0x03, VolumeValue[0], VolumeValue[1], checksum)
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': 'Limit Over - Exceed Maximum Value',
            b'\x02': 'Limit Over - Exceed Minimum Value',
            b'\x03': 'Command Canceled',
            b'\x04': 'Parse Error'
            }

        if response:
            if response[1:2] == b'\x00':
                return response
            else:
                try:
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[1:2]])])
                except KeyError:
                    self.Error(['{0} Unknown Response'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                return ''
            else:
                res = self.__CheckResponseForErrors(command + ':' + str(value), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
            ResponseLength = {
                'Power': 5,
                'Input': 6
                }
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=ResponseLength[command])
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


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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

