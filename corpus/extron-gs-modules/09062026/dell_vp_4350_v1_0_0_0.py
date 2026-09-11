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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMode': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xbe\xef\x10\x05\x00\x08\x7e\x11\x11\x01\x00\x17'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Original',
            b'\x01': '4:3',
            b'\x02': '16:9',
            b'\x03': '16:10'
        }

        AspectRatioCmdString = b'\xbe\xef\x10\x05\x00\xd3\xbf\x11\x11\x01\x00\x32'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xbe\xef\x10\x05\x00\xc3\xff\x11\x11\x01\x00\x0d',
            'Off': b'\xbe\xef\x10\x05\x00\x3e\x7e\x11\x11\x01\x00\x5f'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AudioMuteCmdString = b'\xbe\xef\x10\x05\x00\xee\xff\x11\x11\x01\x00\x61'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xbe\xef\x10\x05\x00\xc4\x7f\x11\x11\x01\x00\x07'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xbe\xef\x10\x05\x00\x1d\x3e\x11\x11\x01\x00\x24',
            'Off': b'\xbe\xef\x10\x05\x00\xdd\xff\x11\x11\x01\x00\x25'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        ExecutiveModeCmdString = b'\xbe\xef\x10\x05\x00\xff\xff\x11\x11\x01\x00\x5d'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xbe\xef\x10\x05\x00\xc2\xbf\x11\x11\x01\x00\x0e',
            'Off': b'\xbe\xef\x10\x05\x00\xef\xbf\x11\x11\x01\x00\x62'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\xbe\xef\x10\x05\x00\xcc\xff\x11\x11\x01\x00\x19',
            'HDMI': b'\xbe\xef\x10\x05\x00\x3a\x3e\x11\x11\x01\x00\x50',
            'Composite': b'\xbe\xef\x10\x05\x00\xdf\x7f\x11\x11\x01\x00\x23',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'No Source',
            b'\x01': 'VGA',
            b'\x03': 'HDMI',
            b'\x05': 'Composite'
        }

        InputCmdString = b'\xbe\xef\x10\x05\x00\xdc\xbf\x11\x11\x01\x00\x26'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': b'\xbe\xef\x10\x05\x00\xd9\xbf\x11\x11\x01\x00\x2a',
            'Normal': b'\xbe\xef\x10\x05\x00\x19\x7e\x11\x11\x01\x00\x2b'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Eco',
            b'\x01': 'Normal',
            b'\x02': 'Dynamic'
        }

        LampModeCmdString = b'\xbe\xef\x10\x05\x00\xa7\x7f\x11\x11\x01\x00\x83'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xbe\xef\x10\x05\x00\xda\x7f\x11\x11\x01\x00\x2f'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = (256 * ord(res[3:4])) + ord(res[2:3])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xbe\xef\x10\x05\x00\xc7\xbf\x11\x11\x01\x00\x02',
            'Up': b'\xbe\xef\x10\x05\x00\x07\x7e\x11\x11\x01\x00\x03',
            'Down': b'\xbe\xef\x10\x05\x00\xc5\x3f\x11\x11\x01\x00\x04',
            'Right': b'\xbe\xef\x10\x05\x00\x04\xbe\x11\x11\x01\x00\x06',
            'Left': b'\xbe\xef\x10\x05\x00\x05\xfe\x11\x11\x01\x00\x05',
            'Enter': b'\xbe\xef\x10\x05\x00\xf6\x3f\x11\x11\x01\x00\x40'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\xbe\xef\x10\x05\x00\x65\x3e\x11\x11\x01\x00\x84'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = (256 * ord(res[3:4])) + ord(res[2:3])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xbe\xef\x10\x05\x00\xc6\xff\x11\x11\x01\x00\x01',
            'Off': b'\xbe\xef\x10\x05\x00\x0c\x3e\x11\x11\x01\x00\x18'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Off',
            b'\x02': 'Warming Up',
            b'\x03': 'On',
            b'\x04': 'Cooling Down',
            b'\x05': 'Power Saving'
        }

        PowerCmdString = b'\xbe\xef\x10\x05\x00\x46\x7e\x11\x11\x01\x00\xff'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMode(self, value, qualifier):

        VideoModeCmdString = b'\xbe\xef\x10\x05\x00\xca\x3f\x11\x11\x01\x00\x10'
        self.__SetHelper('VideoMode', VideoModeCmdString, value, qualifier)

    def UpdateVideoMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Presentation',
            b'\x01': 'Bright',
            b'\x02': 'Movie',
            b'\x03': 'sRGB',
            b'\x04': 'Custom'
        }

        VideoModeCmdString = b'\xbe\xef\x10\x05\x00\x37\xbe\x11\x11\x01\x00\x42'
        res = self.__UpdateHelper('VideoMode', VideoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('VideoMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMode')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xbe\xef\x10\x05\x00\x02\x7e\x11\x11\x01\x00\x0f',
            'Off': b'\xbe\xef\x10\x05\x00\xed\x3f\x11\x11\x01\x00\x64'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        VideoMuteCmdString = b'\xbe\xef\x10\x05\x00\x2d\xfe\x11\x11\x01\x00\x65'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\xbe\xef\x10\x06\x00\x18\xdb\x11\x11\x02\x00\x68' + pack('>B', value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xbe\xef\x10\x05\x00\xf2\x7f\x11\x11\x01\x00\x4f'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': b'\xbe\xef\x10\x05\x00\xc1\x7f\x11\x11\x01\x00\x0b',
            'Out': b'\xbe\xef\x10\x05\x00\x03\x3e\x11\x11\x01\x00\x0c'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': 'Invalid Command',
            b'\x02': 'Error Command'
        }
        if response[0:1] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=1)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if command in ['LampUsage', 'OperationHours']:
            delim = 4
        else:
            delim = 3
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=delim)
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
