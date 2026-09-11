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
        self.Models = {
            'S67U': self.bxlt_1_4357_B,
            'S68X': self.bxlt_1_4357_A,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DigitalZoom': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal'   : b'\x43\x30\x46\x0D', 
            'Wide'     : b'\x43\x31\x30\x0D'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x43\x30\x42\x0D', 
            'Off'   : b'\x43\x30\x43\x0D'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x43\x38\x39\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            'In'    : b'\x43\x33\x30\x0D', 
            'Out'   : b'\x43\x33\x31\x0D'
        }

        DigitalZoomCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        InputCmdString = self.set_input_states[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x43\x52\x31\x0D'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.get_input_states[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        LampModeCmdString = b'\x43\x52\x37\x0D'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x43\x52\x33\x0D'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\x43\x33\x43\x0D',  
            'Left'      : b'\x43\x33\x42\x0D',  
            'Right'     : b'\x43\x33\x41\x0D',  
            'Down'      : b'\x43\x33\x44\x0D', 
            'Menu On'   : b'\x43\x31\x43\x0D',  
            'Menu Off'  : b'\x43\x31\x44\x0D',  
            'Enter'     : b'\x43\x33\x46\x0D'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x43\x30\x30\x0D', 
            'Off'   : b'\x43\x30\x31\x0D'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0   : 'On', 
            80  : 'Off',
            20  : 'Cooling Down',
            21  : 'Cooling down after Lamp Off',
            81  : 'Standby After Cooling Down due to Lamp Off',
            28  : 'Cooling Down due to Temperature Anomaly',
            88  : 'Coming Back after Temperature Anomaly',
            40  : 'Counting Down',
            10  : 'Power Failure',
            24  : 'Power Management Cooling',
            4   : 'Suspend Status (Power Management Ready)',
        }

        PowerCmdString = b'\x43\x52\x30\x0D'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[int(res)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Power: Invalid/unexpected response'])


    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\x43\x30\x44\x0D', 
            'Off'   : b'\x43\x30\x45\x0D'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x43\x30\x39\x0D',  
            'Down'  : b'\x43\x30\x41\x0D'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In'    : b'\x43\x34\x37\x0D',   
            'Out'   : b'\x43\x34\x36\x0D'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            if response.decode().strip() == "NAK":
                self.Error(['{0}: Failed to execute command.'.format(sourceCmdName)])
                response = ''
        except:
            self.Error(['{0}: Failed to execute command.'.format(sourceCmdName)])

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\x0D')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag= b'\x0D')
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

    def bxlt_1_4357_A(self):
        self.set_input_states = {
            'VGA'           : b'\x43\x30\x35\x0D', 
            'Video'         : b'\x43\x30\x37\x0D', 
            'S-Video'       : b'\x43\x33\x34\x0D',
            'Component'     : b'\x43\x33\x33\x0D', 
            'HDMI 1'        : b'\x43\x33\x36\x0D', 
            'HDMI 2(MHL)'   : b'\x43\x33\x38\x0D',  
            'RGBHV'         : b'\x43\x33\x37\x0D',  
            'Network'       : b'\x43\x31\x35\x0D',  
            'Memory Viewer' : b'\x43\x31\x36\x0D',  
            'USB Display'   : b'\x43\x31\x37\x0D'
        }

        self.get_input_states = {
            1   : 'HDMI 1',
            3   : 'VGA',
            4   : 'Component',
            5   : 'S-Video',
            6   : 'Video',
            7   : 'RGBHV',
            8   : 'HDMI 2(MHL)',
            9   : 'Memory Viewer',
            10  : 'Network', 
            11  : 'USB Display'
        }




    def bxlt_1_4357_B(self):
        self.set_input_states = {
            'VGA'           : b'\x43\x30\x35\x0D', 
            'Video'         : b'\x43\x30\x37\x0D', 
            'S-Video'       : b'\x43\x33\x34\x0D', 
            'HDBaseT'       : b'\x43\x35\x31\x0D', 
            'Component'     : b'\x43\x33\x33\x0D', 
            'HDMI 1'        : b'\x43\x33\x36\x0D', 
            'HDMI 2(MHL)'   : b'\x43\x33\x38\x0D',  
            'RGBHV'         : b'\x43\x33\x37\x0D',  
            'Network'       : b'\x43\x31\x35\x0D',  
            'Memory Viewer' : b'\x43\x31\x36\x0D',  
            'USB Display'   : b'\x43\x31\x37\x0D'
        }

        self.get_input_states = {
            1   : 'HDMI 1',
            2   : 'HDBaseT',
            3   : 'VGA',
            4   : 'Component',
            5   : 'S-Video',
            6   : 'Video',
            7   : 'RGBHV',
            8   : 'HDMI 2(MHL)',
            9   : 'Memory Viewer',
            10  : 'Network', 
            11  : 'USB Display'
        }


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

