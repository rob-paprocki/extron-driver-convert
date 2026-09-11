from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack

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
            'ClosedCaption': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\xbe\xef\x10\x05\x00\x08\x7e\x11\x11\x01\x00\x17'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Original',
            b'\x01': '4:3',
            b'\x02': '16:9',
            b'\x03': '16:10',
        }

        AspectRatioCmdString = b'\xbe\xef\x10\x05\x00\xd3\xbf\x11\x11\x01\x00\x32'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/unexpected response'])

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
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xbe\xef\x10\x05\x00\xc4\x7f\x11\x11\x01\x00\x07'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\xbe\xef\x10\x60\x00\x2a\x7e\x11\x11\x20\x00\x6f\x00',
            'CC1': b'\xbe\xef\x10\x60\x00\x2a\x7e\x11\x11\x20\x00\x6f\x01',
            'CC2': b'\xbe\xef\x10\x60\x00\x2a\x7e\x11\x11\x20\x00\x6f\x02',
            'CC3': b'\xbe\xef\x10\x60\x00\x2a\x7e\x11\x11\x20\x00\x6f\x03',
            'CC4': b'\xbe\xef\x10\x60\x00\x2a\x7e\x11\x11\x20\x00\x6f\x04'
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

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
            b'\x02': 'Off'
        }

        ExecutiveModeCmdString = b'\xbe\xef\x10\x05\x00\xff\xff\x11\x11\x01\x00\x5d'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

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
            'HDMI 1': b'\xbe\xef\x10\x05\x00\x3a\x3e\x11\x11\x01\x00\x50',
            'HDMI 2': b'\xbe\xef\x10\x05\x00\x23\xbe\x11\x11\x01\x00\x72',
            'Composite': b'\xbe\xef\x10\x05\x00\xdf\x7f\x11\x11\x01\x00\x23'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'VGA',
            b'\x03': 'HDMI 1',
            b'\x0c': 'HDMI 2',
            b'\x05': 'Composite'
        }

        InputCmdString = b'\xbe\xef\x10\x05\x00\xdc\xbf\x11\x11\x01\x00\x26'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': b'\xbe\xef\x10\x05\x00\xd9\xbf\x11\x11\x01\x00\x2a',
            'Normal': b'\xbe\xef\x10\x05\x00\x19\x7e\x11\x11\x01\x00\x2b',
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
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x10\x05\x00\xDA\x7F\x11\x11\x01\x00\x2F'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = unpack('<h', res[-2:4])[0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xbe\xef\x10\x05\x00\xc7\xbf\x11\x11\x01\x00\x02',
            'Up': b'\xbe\xef\x10\x05\x00\x07\x7e\x11\x11\x01\x00\x03',
            'Down': b'\xbe\xef\x10\x05\x00\xc5\x3f\x11\x11\x01\x00\x04',
            'Left': b'\xbe\xef\x10\x05\x00\x05\xfe\x11\x11\x01\x00\x05',
            'Right': b'\xbe\xef\x10\x05\x00\x04\xbe\x11\x11\x01\x00\x06',
            'Enter': b'\xbe\xef\x10\x05\x00\xf6\x3f\x11\x11\x01\x00\x40'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = b'\xbe\xef\x10\x05\x00\x65\x3e\x11\x11\x01\x00\x84'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = (256 * unpack('B', res[3:4])[0]) + unpack('B', res[2:3])[0]
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xbe\xef\x10\x05\x00\xc6\xff\x11\x11\x01\x00\x01',
            'Off': b'\xbe\xef\x10\x05\x00\x0c\x3e\x11\x11\x01\x00\x18'
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

        PowerCmdString = b'\xbe\xef\x10\x05\x00\x46\x7e\x11\x11\x01\x00\xff'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

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
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\xbe\xef\x10\x06\x00\x18\xdb\x11\x11\x02\x00\x68' + pack('>B', value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\xbe\xef\x10\x05\x00\xf2\x7f\x11\x11\x01\x00\x4f'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': 'Invalid Command',
            b'\x02': 'Error Command'
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
            delim = 4
        else:
            delim = 3
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

