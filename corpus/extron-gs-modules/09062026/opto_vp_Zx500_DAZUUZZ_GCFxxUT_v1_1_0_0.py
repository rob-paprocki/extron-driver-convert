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
            '3DFormat': {'Status': {}},
            '3DInvert': {'Status': {}},
            '3DMode': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioOut': {'Status': {}},
            'AVMute': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Microphone': {'Status': {}},
            'MicrophoneVolume': {'Status': {}},
            'Power': {'Status': {}},
            'Speaker': {'Status': {}},
            'Volume': {'Status': {}},
            }

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Frame Packing': '7',
            'Side by Side': '1',
            'Top and Bottom': '2',
            'Frame Sequential': '3',
            'Field Sequential': '9'
        }

        ThreeDFormatCmdString = '~00405 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DFormat', ThreeDFormatCmdString, value, qualifier)

    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ThreeDInvertCmdString = '~00231 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DInvert', ThreeDInvertCmdString, value, qualifier)

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'On': '5',
            'Off': '6',
            'Auto': '4'
        }

        ThreeDModeCmdString = '~00230 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('3DMode', ThreeDModeCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '7',
            '4:3': '1',
            '16:9': '2',
            '16:10': '3',
        }

        AspectRatioCmdString = '~0060 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '7': 'Auto',
            '1': '4:3',
            '2': '16:9',
            '3': '16:10',
            '0': 'None'
        }

        AspectRatioCmdString = '~00127 1\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '~0003 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAudioOut(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioOutCmdString = '~00510 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioOut', AudioOutCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '~0002 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '~0004 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': '5',
            'VGA 2': '6',
            'HDMI 1': '1',
            'HDMI 2': '15',
            'Video': '10',
            'Multimedia': '11',
            'Network Display': '16',
        }

        InputCmdString = '~0012 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '51',
            '2': '52',
            '3': '53',
            '4': '54',
            '5': '55',
            '6': '56',
            '7': '57',
            '8': '58',
            '9': '59',
            '0': '60'
        }

        KeypadCmdString = '~00140 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '10',
            'Down': '14',
            'Left': '11',
            'Right': '13',
            'Enter': '12',
            'Menu': '20',
            'Exit': '74'
        }

        MenuNavigationCmdString = '~00140 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMicrophone(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MicrophoneCmdString = '~00562 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Microphone', MicrophoneCmdString, value, qualifier)

    def SetMicrophoneVolume(self, value, qualifier):

        if 0 <= value <= 30:
            MicrophoneVolumeCmdString = '~0093 {}\r'.format(value)
            self.__SetHelper('MicrophoneVolume', MicrophoneVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneVolume')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '~0000 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStates = {
            '1': 'On',
            '0': 'Off'
        }

        InputStates = {
            '02': 'VGA 1',
            '03': 'VGA 2',
            '07': 'HDMI 1',
            '08': 'HDMI 2',
            '05': 'Video',
            '09': 'Multimedia',
            '12': 'Network Display',
            '00': 'No Signal'
        }

        PowerCmdString = '~00150 1\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStates[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])
            try:
                value = int(res[3:8])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])
            try:
                value = InputStates[res[8:10]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetSpeaker(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        SpeakerCmdString = '~00310 {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Speaker', SpeakerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 30:
            VolumeCmdString = '~0081 {}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
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

