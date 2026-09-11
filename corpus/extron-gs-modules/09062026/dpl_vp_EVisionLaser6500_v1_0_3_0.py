from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self._DeviceID = '0'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'ProjectionMode': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }

        self.setRegex = re.compile(b'([PF]|OP POWER.ON\r\n)')
        self.updateRegex = re.compile(b'(F|P-?\d)')
        self.waitCommands = ['LampUsage','FilterUsage','Input','Zoom','Volume','DisplayMode']

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif int(value) in range(0,99):
            self._DeviceID = value.zfill(2)
        else:
            self.Error(['Device ID Parameter should be set to Broadcast or be in range 0 - 98.'])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill'       : 'V{}S03010\r', 
            '4:3'        : 'V{}S03011\r', 
            '16:9'       : 'V{}S03012\r', 
            'Letter Box' : 'V{}S03013\r', 
            'Native'     : 'V{}S03014\r', 
            '2.35:1'     : 'V{}S03015\r'
        }

        AspectRatioCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'P0' : 'Fill', 
            'P1' : '4:3', 
            'P2' : '16:9', 
            'P3' : 'Letter Box', 
            'P4' : 'Native', 
            'P5' : '2.35:1'
        }

        AspectRatioCmdString = 'V{}G0301\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except KeyError:
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'V{}S0003\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation' : 'V{}S01080\r', 
            'Bright'       : 'V{}S01081\r', 
            'Game'         : 'V{}S01082\r', 
            'Movie'        : 'V{}S01083\r', 
            'Vivid'        : 'V{}S01084\r', 
            'TV'           : 'V{}S01085\r', 
            'sRGB'         : 'V{}S01086\r', 
            'DICOM SIM'    : 'V{}S01088\r', 
            'User'         : 'V{}S01089\r', 
            'User 2'       : 'V{}S010810\r'
        }

        DisplayModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'P0' : 'Presentation', 
            'P1' : 'Bright', 
            'P2' : 'Game', 
            'P3' : 'Movie', 
            'P4' : 'Vivid', 
            'P5' : 'TV', 
            'P6' : 'sRGB', 
            'P8' : 'DICOM SIM', 
            'P9' : 'User', 
            'P10' : 'User 2'
        }

        DisplayModeCmdString = 'V{}G0108\r'.format(self._DeviceID)
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('DisplayMode', value, qualifier)
            except KeyError:
                self.Error(['Display Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'V{}G0005\r'.format(self._DeviceID)
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'V{}S03041\r', 
            'Off' : 'V{}S03040\r'
        }

        FreezeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            'P1' : 'On', 
            'P0' : 'Off'
        }

        FreezeCmdString = 'V{}G0304\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except KeyError:
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB'     : 'V{}S0201\r', 
            'DVI'     : 'V{}S0203\r', 
            'Video'   : 'V{}S0204\r', 
            'HDMI 1'  : 'V{}S0206\r', 
            'BNC'     : 'V{}S0207\r', 
            'HDMI 2'  : 'V{}S0209\r', 
            'HDBaseT' : 'V{}S0213\r'
        }

        InputCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'P1' : 'RGB', 
            'P3' : 'DVI', 
            'P4' : 'Video', 
            'P6' : 'HDMI 1',
            'P7' : 'BNC', 
            'P9' : 'HDMI 2', 
            'P13' : 'HDBaseT'
        }

        InputCmdString = 'V{}G0220\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Input', value, qualifier)
            except KeyError:
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'          : 'V{}S03190\r', 
            'Eco'             : 'V{}S03191\r', 
            'Eco Plus'        : 'V{}S03192\r', 
            'Dimming'         : 'V{}S03193\r', 
            'Extreme Dimming' : 'V{}S03194\r', 
            'Custom Light'    : 'V{}S03195\r'
        }

        LampModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            'P0' : 'Normal', 
            'P1' : 'Eco', 
            'P2' : 'Eco Plus', 
            'P3' : 'Dimming', 
            'P4' : 'Extreme Dimming', 
            'P5' : 'Custom Light'
        }

        LampModeCmdString = 'V{}G0319\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LampMode', value, qualifier)
            except KeyError:
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'V{}G0004\r'.format(self._DeviceID)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        if value == 'On':
            PowerCmdString = 'op power.on\r' 
        else:
            PowerCmdString ='V{}S0002\r'.format(self._DeviceID)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'P2' : 'On',
            'P1' : 'Off',
            'P0' : 'Reset',
            'P3' : 'Cooling'
        }

        PowerCmdString = 'V{}G0007\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Power', value, qualifier)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def SetProjectionMode(self, value, qualifier):

        ValueStateValues = {
            'Front'          : 'V{}S03080\r', 
            'Rear'           : 'V{}S03081\r', 
            'Ceiling'        : 'V{}S03082\r', 
            'Rear + Ceiling' : 'V{}S03083\r'
        }

        ProjectionModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('ProjectionMode', ProjectionModeCmdString, value, qualifier)

    def UpdateProjectionMode(self, value, qualifier):

        ValueStateValues = {
            'P0' : 'Front', 
            'P1' : 'Rear', 
            'P2' : 'Ceiling', 
            'P3' : 'Rear + Ceiling'
        }

        ProjectionModeCmdString = 'V{}G0308\r'.format(self._DeviceID)
        res = self.__UpdateHelper('ProjectionMode', ProjectionModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ProjectionMode', value, qualifier)
            except KeyError:
                self.Error(['Projection Mode: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'V{}S03021\r', 
            'Off' : 'V{}S03020\r'
        }

        VideoMuteCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'P1' : 'On', 
            'P0' : 'Off'
        }

        VideoMuteCmdString = 'V{}G0302\r'.format(self._DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except KeyError:
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 10
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'V{}S0305{}\r'.format(self._DeviceID,value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 10
        }

        VolumeCmdString = 'V{}G0305\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    self.Error(['Volume: Invalid/unexpected range received'])
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min' : -10,
            'Max' : 10
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomCmdString = 'V{}S0311{}\r'.format(self._DeviceID,value)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def UpdateZoom(self, value, qualifier):

        ValueConstraints = {
            'Min' : -10,
            'Max' : 10
        }

        ZoomCmdString = 'V{}G0311\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Zoom', ZoomCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:])
                if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                    self.WriteStatus('Zoom', value, qualifier)
                else:
                    self.Error(['Zoom: Invalid/unexpected range received'])
            except (ValueError, IndexError):
                self.Error(['Zoom: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response.startswith('F'):
            self.Error(['{}: Error executing command'.format(sourceCmdName)])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True' or self._DeviceID == '99':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '99':
            self.Discard('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if command in self.waitCommands:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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

