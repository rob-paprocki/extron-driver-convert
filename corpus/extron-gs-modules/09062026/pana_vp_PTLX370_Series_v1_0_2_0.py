from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input Signal'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatio1StateValues = {
            'Auto': b'\x02VS1:00\x03',
            'Normal': b'\x02VS1:01\x03',
            'Native': b'\x02VS1:05\x03',
            'Full': b'\x02VS1:06\x03',
            'H Fit': b'\x02VS1:09\x03',
            }

        AspectRatio2StateValues = {
            'Wide': b'\x02VS1:01\x03',
            'Normal': b'\x02VS1:02\x03',
            }

        Input = qualifier['Input Signal']

        if Input in ['Normal', '16:9']:
            try:
                if Input == 'Normal':
                    AspectRatioCmdString = AspectRatio1StateValues[value]
                elif Input == '16:9':
                    AspectRatioCmdString = AspectRatio2StateValues[value]
                self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            except:
                self.Discard('Invalid Command for SetAspectRatio')
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatio1StateNames = {
            b'0': 'Auto',
            b'1': 'Normal',
            b'5': 'Native',
            b'6': 'Full',
            b'9': 'H Fit'
           }

        AspectRatio2StateNames = {
            b'1': 'Wide',
            b'2': 'Normal',
           }

        Input = qualifier['Input Signal']

        if Input in ['Normal', '16:9']:
            res = self.__UpdateHelper('AspectRatio', b'\x02QS1\x03', value, qualifier)
            if res:
                try:
                    if Input == 'Normal':
                        value = AspectRatio1StateNames[res[2:3]]
                    elif Input == '16:9':
                        value = AspectRatio2StateNames[res[2:3]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', b'\x02OAS\x03', value, qualifier)

    def SetAVMute(self, value, qualifier):

        States = {
            'On': b'\x02OSH:1\x03',
            'Off': b'\x02OSH:0\x03'
            }

        self.__SetHelper('AVMute', States[value], value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        States = {
            b'1': 'On',
            b'0': 'Off'
           }

        res = self.__UpdateHelper('AVMute', b'\x02QSH\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('AVMute', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/Unexpected Response'])

    def SetClosedCaption(self, value, qualifier):

        States = {
            'CC1': b'\x02OCC:1\x03',
            'CC2': b'\x02OCC:2\x03',
            'CC3': b'\x02OCC:3\x03',
            'CC4': b'\x02OCC:4\x03',
            'Off': b'\x02OCC:0\x03'
            }

        self.__SetHelper('ClosedCaption', States[value], value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        States = {
            b'1': 'CC1',
            b'2': 'CC2',
            b'3': 'CC3',
            b'4': 'CC4',
            b'0': 'Off'
           }

        res = self.__UpdateHelper('ClosedCaption', b'\x02QCC\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaption', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['CLosed Caption: Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        States = {
            'On': b'\x02OFZ:1\x03',
            'Off': b'\x02OFZ:0\x03'
            }

        self.__SetHelper('Freeze', States[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            b'1': 'On',
            b'0': 'Off',
           }

        res = self.__UpdateHelper('Freeze', b'\x02QFZ\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        States = {
            'Video': b'\x02IIS:VID\x03',
            'S-Video': b'\x02IIS:SVD\x03',
            'Computer': b'\x02IIS:RG1\x03',
            'HDMI 1': b'\x02IIS:HD1\x03',
            'HDMI 2': b'\x02IIS:HD2\x03',
            'Component': b'\x02IIS:YUV\x03'
            }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            b'VID': 'Video',
            b'SVD': 'S-Video',
            b'RG1': 'Computer',
            b'HD1': 'HDMI 1',
            b'HD2': 'HDMI 2',
            b'YUV': 'Component'
           }

        res = self.__UpdateHelper('Input', b'\x02QIN\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', States[res[1:4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal': b'\x02OLP:1\x03',
            'Eco': b'\x02OLP:0\x03'
            }

        self.__SetHelper('LampMode', States[value], value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        States = {
            b'1': 'Normal',
            b'0': 'Eco',
           }

        res = self.__UpdateHelper('LampMode', b'\x02QLP\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', b'\x02Q$L\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', int(res[1:-1]), qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Menu': b'\x02OMN\x03',
            'Up': b'\x02OCU\x03',
            'Down': b'\x02OCD\x03',
            'Left': b'\x02OCL\x03',
            'Right': b'\x02OCR\x03',
            'Enter': b'\x02OEN\x03',
            'Return': b'\x02OBK\x03'
            }

        self.__SetHelper('MenuNavigation', States[value], value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Natural': b'\x02VPM:NAT\x03',
            'Standard': b'\x02VPM:STD\x03',
            'Cinema': b'\x02VPM:CIB\x03',
            'Dynamic': b'\x02VPM:DYN\x03',
            'DICOM': b'\x02VPM:DIC\x03',
            'Blackboard': b'\x02VPM:BBD\x03',
            'Whiteboard': b'\x02VPM:BDD\x03',
            }

        self.__SetHelper('PictureMode', States[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        States = {
            b'NAT': 'Natural',
            b'STD': 'Standard',
            b'CIN': 'Cinema',
            b'DYN': 'Dynamic',
            b'DIC': 'DICOM',
            b'BBD': 'Blackboard',
            b'WBD': 'Whiteboard',
           }

        res = self.__UpdateHelper('PictureMode', b'\x02QPM\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureMode', States[res[1:4]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\x02PON\x03',
            'Off': b'\x02POF\x03',
            }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            b'2': 'On',
            b'0': 'Off',
            b'1': 'Warming Up',
            b'3': 'Cooling Down'
            }

        res = self.__UpdateHelper('Power', b'\x02Q$S\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            self.__SetHelper('Volume', '\x02AVL:{0:03d}\x03'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', b'\x02QAV\x03', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res[1:-1]), qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02ER401\x03': "Invalid Command Reply.",
            b'\x02ER402\x03': "Invalid Parameter"
            }

        if response in DEVICE_ERROR_CODES:
            self.Error([sourceCmdName + ' ' + DEVICE_ERROR_CODES[response]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if res:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

