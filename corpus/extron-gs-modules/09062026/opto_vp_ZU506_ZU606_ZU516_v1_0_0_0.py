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
            'ZU506T': self.opto_1_4409_T,
            'ZU516SAT': self.opto_1_4409_T,
            'ZU606T-W': self.opto_1_4409_T,
            'ZU606T-B': self.opto_1_4409_T,
            'ZU606TST-W': self.opto_1_4409_T,
            'ZU606TST-B': self.opto_1_4409_T,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': { 'Status': {}},
            '3DInvert': { 'Status': {}},
            '3DMode': { 'Status': {}},
            '3Dto2D': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioInput': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }



    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto'             : '~00405 0\r', 
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
    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'DLP Link' : '~00230 1\r', 
            'IR'       : '~00230 3\r', 
            'Off'      : '~00230 0\r'
        }

        ThreeDModeCmdString = ValueStateValues[value]
        self.__SetHelper('3DMode', ThreeDModeCmdString, value, qualifier)
    def Set3Dto2D(self, value, qualifier):

        ValueStateValues = {
            '3D'    : '~00400 0\r', 
            'Left'  : '~00400 1\r', 
            'Right' : '~00400 2\r'
        }

        ThreeDtotwoDCmdString = ValueStateValues[value]
        self.__SetHelper('3Dto2D', ThreeDtotwoDCmdString, value, qualifier)
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'    : '~0060 1\r', 
            '16:9'   : '~0060 2\r', 
            'LBX'    : '~0060 5\r', 
            'Native' : '~0060 6\r', 
            'Auto'   : '~0060 7\r', 
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1' : '4:3', 
            '2' : '16:9', 
            '5' : 'LBX', 
            '6' : 'Native', 
            '7' : 'Auto', 
            '0' : 'None'
        }

        AspectRatioCmdString = '~00127 1\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Default' : '~0089 0\r', 
            'Audio 1' : '~0089 1\r', 
            'Audio 2' : '~0089 3\r'
        }

        AudioInputCmdString = ValueStateValues[value]
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~0003 1\r', 
            'Off' : '~0003 0\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~0001 1\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~0002 1\r', 
            'Off' : '~0002 0\r'
        }

        AVMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation' : '~0020 1\r', 
            'Bright'       : '~0020 2\r', 
            'Cinema'       : '~0020 3\r', 
            'sRGB'         : '~0020 4\r', 
            'DICOM SIM.'   : '~0020 13\r', 
            'User'         : '~0020 5\r', 
            'Game'         : '~0020 12\r', 
            'HDR SIM.'     : '~0020 22\r', 
        }

        DisplayModeCmdString = ValueStateValues[value]
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~00103 1\r', 
            'Off' : '~00103 0\r'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~0004 1\r', 
            'Off' : '~0004 0\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):


        InputCmdString = self.set_input_states[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : '~00140 10\r', 
            'Down'  : '~00140 14\r', 
            'Left'  : '~00140 11\r', 
            'Right' : '~00140 13\r', 
            'Enter' : '~00140 12\r', 
            'Menu'  : '~00140 20\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '~0000 1\r', 
            'Off' : '~0000 0\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerStates = {
            '1' : 'On', 
            '0' : 'Off'
        }

        DisplayModeStates = {
            '01' : 'Presentation',
            '02' : 'Bright',
            '03' : 'Cinema',
            '04' : 'sRGB',
            '05' : 'User',
            '09' : '3D',
            '12' : 'Game',
            '10' : 'DICOM SIM.',
            '22' : 'HDR SIM.',
            '00' : 'None'
        }

        PowerCmdString = '~00150 1\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStates[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])
            Power = self.ReadStatus('Power', qualifier)
            if Power == 'On':
                try:
                    value = int(res[3:8])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Usage: Invalid/Unexpected Response'])
                try:
                    value = self.get_input_states[res[8:10]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/Unexpected Response'])
                try:
                    value = DisplayModeStates[res[-3:-1]]
                    self.WriteStatus('DisplayMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Display Mode: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'   : '~00140 18\r', 
            'Down' : '~00140 17\r'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[0] == 'F':
            self.Error(['{0}: Failed to execute command.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

    def opto_1_4409_A(self):
        self.set_input_states = {
            'HDMI 1/MHL' : '~0012 1\r', 
            'HDMI 2'     : '~0012 15\r', 
            'VGA'        : '~0012 5\r', 
            'Video'      : '~0012 10\r'
        }

        self.get_input_states = {
            '02' : 'VGA',
            '05' : 'Video',
            '07' : 'HDMI 1/MHL',
            '08' : 'HDMI 2',
            '00' : 'None'
        }



    def opto_1_4409_T(self):
        self.set_input_states = {
            'HDMI 1/MHL' : '~0012 1\r', 
            'HDMI 2'     : '~0012 15\r', 
            'VGA'        : '~0012 5\r', 
            'Video'      : '~0012 10\r',
            'HDBaseT'    : '~0012 21\r'
        }

        self.get_input_states = {
            '02' : 'VGA',
            '05' : 'Video',
            '07' : 'HDMI 1/MHL',
            '08' : 'HDMI 2',
            '16' : 'HDBaseT',
            '00' : 'None'
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

