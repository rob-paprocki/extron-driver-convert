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
        self.Models = {
            'S718QL': self.dell_1_3063_S718QL,
            'S518WL': self.dell_1_3063_S518WL,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xBE\xEF\x10\x05\x00\x08\x7E\x11\x11\x01\x00\x17'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Original',
            b'\x01': '4:3',
            b'\x02': '16:9',
            b'\x03': '16:10'
        }

        AspectRatioCmdString = b'\xBE\xEF\x10\x05\x00\xD2\xFF\x11\x11\x01\x00\x31'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if(res[1:2] == b'\x31'):
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x10\x05\x00\x04\xBE\x11\x11\x01\x00\x07'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x10\x05\x00\x1D\x3E\x11\x11\x01\x00\x24',
            'Off': b'\xBE\xEF\x10\x05\x00\x05\xFE\x11\x11\x01\x00\x25'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x10\x05\x00\xC2\xBF\x11\x11\x01\x00\x0E',
            'Off': b'\xBE\xEF\x10\x05\x00\xEF\xBF\x11\x11\x01\x00\x62'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.setInputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x10\x05\x00\xDC\xBF\x11\x11\x01\x00\x26'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\x26'):
                    value = self.getInputState[res[2:3]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\xBE\xEF\x10\x05\x00\x19\x7E\x11\x11\x01\x00\x2B',
            'Eco': b'\xBE\xEF\x10\x05\x00\xD9\xBF\x11\x11\x01\x00\x2A'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Normal',
            b'\x00': 'Eco'
        }

        LampModeCmdString = b'\xBE\xEF\x10\x05\x00\xA7\x7F\x11\x11\x01\x00\x83'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\x83'):
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xBE\xEF\x10\x05\x00\xC7\xBF\x11\x11\x01\x00\x02',
            'Up': b'\xBE\xEF\x10\x05\x00\x07\x7E\x11\x11\x01\x00\x03',
            'Down': b'\xBE\xEF\x10\x05\x00\xC5\x3F\x11\x11\x01\x00\x04',
            'Left': b'\xBE\xEF\x10\x05\x00\x05\xFE\x11\x11\x01\x00\x05',
            'Right': b'\xBE\xEF\x10\x05\x00\x04\xBE\x11\x11\x01\x00\x06',
            'Enter': b'\xBE\xEF\x10\x05\x00\xF6\x3F\x11\x11\x01\x00\x40'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x10\x05\x00\xC3\xFF\x11\x11\x01\x00\x0D',
            'Off': b'\xBE\xEF\x10\x05\x00\x3E\x7E\x11\x11\x01\x00\x5F'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        MuteCmdString = b'\xBE\xEF\x10\x05\x00\xEE\xFF\x11\x11\x01\x00\x61'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\x61'):
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\xBE\xEF\x10\x05\x00\xDA\x7F\x11\x11\x01\x00\x2F'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\x2F'):
                    value = (256 * ord(res[3:4])) + ord(res[2:3])
                    self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x10\x05\x00\xC6\xFF\x11\x11\x01\x00\x01',
            'Off': b'\xBE\xEF\x10\x05\x00\x0C\x3E\x11\x11\x01\x00\x18'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x03': 'On',
            b'\x01': 'Off',
            b'\x02': 'Warming Up',
            b'\x04': 'Cooling Down',
            b'\x05': 'Power Saving'
        }

        PowerCmdString = b'\xBE\xEF\x10\x05\x00\x46\x7E\x11\x11\x01\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\xFF'):
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x10\x05\x00\x02\x7E\x11\x11\x01\x00\x0F',
            'Off': b'\xBE\xEF\x10\x05\x00\xED\x3F\x11\x11\x01\x00\x64'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x10\x05\x00\x2D\xFE\x11\x11\x01\x00\x65'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\x65'):
                    value = ValueStateValues[res[2:3]]
                    self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 20:
            VolumeCmdString = b'\xBE\xEF\x10\x06\x00\x18\xDB\x11\x11\x02\x00\x68' + pack('>B', value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xBE\xEF\x10\x05\x00\xF2\x7F\x11\x11\x01\x00\x4F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                if (res[1:2] == b'\x4F'):
                    value = ord(res[2:3])
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': "Invalid Command (on the control command list but not valid)",
            b'\x02': "Error Command (includes CRC error and unkown commands)"
        }
        if response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=1)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if command in ['OperationHours']:
            resLen = 4
        else:
            resLen = 3

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=resLen)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def dell_1_3063_S518WL(self):
        self.setInputState = {
            'VGA-A'         : b'\xBE\xEF\x10\x05\x00\xCC\xFF\x11\x11\x01\x00\x19',
            'Composite'     : b'\xBE\xEF\x10\x05\x00\xDF\x7F\x11\x11\x01\x00\x23', 
            'HDMI 1'        : b'\xBE\xEF\x10\x05\x00\x3A\x3E\x11\x11\x01\x00\x50', 
            'HDMI 2'        : b'\xBE\xEF\x10\x05\x00\x23\xBE\x11\x11\x01\x00\x72', 
            'USB Video'     : b'\xBE\xEF\x10\x05\x00\xB2\x3F\x11\x11\x01\x00\xB0', 
            'USB Music'     : b'\xBE\xEF\x10\x05\x00\x72\xFE\x11\x11\x01\x00\xB1', 
            'USB Photo'     : b'\xBE\xEF\x10\x05\x00\x73\xBE\x11\x11\x01\x00\xB2', 
            'USB Document'  : b'\xBE\xEF\x10\x05\x00\xB3\x7F\x11\x11\x01\x00\xB3', 
            'USB Setting'   : b'\xBE\xEF\x10\x05\x00\x71\x3E\x11\x11\x01\x00\xB4', 
            'Network'       : b'\xBE\xEF\x10\x05\x00\xB1\xFF\x11\x11\x01\x00\xB5'
        }

        self.getInputState = {
            b'\x00' : 'No Source', 
            b'\x01' : 'VGA-A',
            b'\x05' : 'Composite',
            b'\x03' : 'HDMI 1', 
            b'\x0C' : 'HDMI 2', 
            b'\x0F' : 'USB Video', 
            b'\x10' : 'USB Music', 
            b'\x11' : 'USB Photo', 
            b'\x12' : 'USB Document', 
            b'\x13' : 'USB Setting', 
            b'\x14' : 'Network'
        }

    def dell_1_3063_S718QL(self):
        self.setInputState = {
            'HDMI 1'        : b'\xBE\xEF\x10\x05\x00\x3A\x3E\x11\x11\x01\x00\x50', 
            'HDMI 2'        : b'\xBE\xEF\x10\x05\x00\x23\xBE\x11\x11\x01\x00\x72', 
            'HDMI 3'        : b'\xBE\xEF\x10\x05\x00\xE3\x7F\x11\x11\x01\x00\x73', 
            'USB Video'     : b'\xBE\xEF\x10\x05\x00\xB2\x3F\x11\x11\x01\x00\xB0', 
            'USB Music'     : b'\xBE\xEF\x10\x05\x00\x72\xFE\x11\x11\x01\x00\xB1', 
            'USB Photo'     : b'\xBE\xEF\x10\x05\x00\x73\xBE\x11\x11\x01\x00\xB2', 
            'USB Document'  : b'\xBE\xEF\x10\x05\x00\xB3\x7F\x11\x11\x01\x00\xB3', 
            'USB Setting'   : b'\xBE\xEF\x10\x05\x00\x71\x3E\x11\x11\x01\x00\xB4', 
            'Network'       : b'\xBE\xEF\x10\x05\x00\xB1\xFF\x11\x11\x01\x00\xB5'
        }

        self.getInputState = {
            b'\x00' : 'No Source', 
            b'\x03' : 'HDMI 1', 
            b'\x0C' : 'HDMI 2', 
            b'\x0D' : 'HDMI 3',
            b'\x0F' : 'USB Video', 
            b'\x10' : 'USB Music', 
            b'\x11' : 'USB Photo', 
            b'\x12' : 'USB Document', 
            b'\x13' : 'USB Setting', 
            b'\x14' : 'Network'
        }

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
