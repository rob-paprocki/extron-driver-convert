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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': { 'Status': {}},
            '3DInvert': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'DLPLink': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PIPPBPInput': { 'Status': {}},
            'PIPPBPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Frame Packing'    : '~00405 7\r', 
            'Side by Side'     : '~00405 1\r', 
            'Top and Bottom'   : '~00405 2\r', 
            'Frame Sequential' : '~00405 3\r'
        }

        ThreeDFormatCmdString = ValueStateValues[value]
        self.__SetHelper('3DFormat', ThreeDFormatCmdString, value, qualifier)
    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~00231 1\r', 
            'Off' : '~00231 0\r'
        }

        ThreeDInvertCmdString = ValueStateValues[value]
        self.__SetHelper('3DInvert', ThreeDInvertCmdString, value, qualifier)
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : '~0060 7\r', 
            '4:3'    : '~0060 1\r', 
            '16:9'   : '~0060 2\r', 
            '16:10'  : '~0060 3\r', 
            'Native' : '~0060 6\r', 
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '7' : 'Auto', 
            '1' : '4:3', 
            '2' : '16:9', 
            '3' : '16:10', 
            '6' : 'Native'
        }

        AspectRatioCmdString = '~00127 1\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Bright'       : '~0020 2\r', 
            'Presentation' : '~0020 1\r', 
            'Movie'        : '~0020 3\r', 
            'sRGB'         : '~0020 4\r', 
            'Blending'     : '~0020 19\r', 
            'DICOM SIM.'   : '~0020 13\r', 
            'User'         : '~0020 5\r'
        }

        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
    def UpdateDisplayMode(self, value, qualifier):

        ValueStateValues = {
            '2'  : 'Bright', 
            '1'  : 'Presentation', 
            '3'  : 'Movie', 
            '4'  : 'sRGB', 
            '19' : 'Blending', 
            '13' : 'DICOM SIM.', 
            '5'  : 'User'
        }

        DisplayModeCmdString = '~00123 1\r'
        res = self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Display Mode: Invalid/unexpected response'])

    def SetDLPLink(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~00230 1\r', 
            'Off' : '~00230 0\r'
        }

        DLPLinkCmdString = ValueStateValues[value]
        self.__SetHelper('DLPLink', DLPLinkCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~0004 1\r', 
            'Off' : '~0004 0\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'     : '~0012 5\r', 
            'HDMI 1'  : '~0012 1\r', 
            'HDMI 2'  : '~0012 3\r', 
            'DVI-D'   : '~0012 2\r', 
            'HDBaseT' : '~0012 21\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '2'   : 'VGA', 
            '7'   : 'HDMI 1', 
            '3'   : 'HDMI 2', 
            '1'   : 'DVI-D', 
            '12'  : 'HDBaseT', 
        }

        InputCmdString = '~00121 1\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '~00150 19\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[2:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '~00140 20\r', 
            'Up'    : '~00140 10\r', 
            'Left'  : '~00140 11\r', 
            'Right' : '~00140 13\r', 
            'Down'  : '~00140 14\r', 
            'Enter' : '~00140 12\r', 
            'Exit'  : '~00140 72\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPIPPBPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'     : '~00305 2\r', 
            'HDMI 1'  : '~00305 1\r', 
            'HDMI 2'  : '~00305 3\r', 
            'DVI-D'   : '~00305 9\r', 
            'HDBaseT' : '~00305 10\r'
        }

        PIPPBPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPBPInput', PIPPBPInputCmdString, value, qualifier)
    def UpdatePIPPBPInput(self, value, qualifier):

        ValueStateValues = {
            '2'  : 'VGA', 
            '7'  : 'HDMI 1', 
            '3'  : 'HDMI 2', 
            '1'  : 'DVI-D', 
            '16' : 'HDBaseT'
        }

        PIPPBPInputCmdString = '~00131 1\r'
        res = self.__UpdateHelper('PIPPBPInput', PIPPBPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('PIPPBPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP/PBP Input: Invalid/unexpected response'])

    def SetPIPPBPMode(self, value, qualifier):

        ValueStateValues = {
            'Off' : '~00302 0\r', 
            'PIP' : '~00302 2\r', 
            'PBP' : '~00302 1\r'
        }

        PIPPBPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPBPMode', PIPPBPModeCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~0000 1\r', 
            'Off' : '~0000 0\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = '~00124 1\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~00325 1\r', 
            'Off' : '~00325 0\r'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        VideoMuteCmdString = '~00355 1\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
    
        if response:
            response = response.decode()

            if response[0] == 'F':
                self.Error(['{0}: Failed to execute command.'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

