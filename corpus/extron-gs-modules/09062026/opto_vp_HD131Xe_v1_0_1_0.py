from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
        self._DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DInvert': {'Status': {}},
            '3DMode': {'Status': {}},
            '3Dto2D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

    @property
    def ProjectorID(self):
        return self._ProjectorID

    @ProjectorID.setter
    def ProjectorID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        else:
            self._DeviceID = value.zfill(2)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '405 0\r',
            'SBS': '405 1\r',
            'Top and Bottom': '405 2\r',
            'Frame Sequential': '405 3\r'
        }

        FormatCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)

    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On': '231 0\r',
            'Off': '231 1\r'
        }

        InvertCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DInvert', InvertCmdString, value, qualifier)

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'DLP-Link': '230 1\r',
            'IR': '230 3\r'
        }

        ModeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)

    def Set3Dto2D(self, value, qualifier):

        ValueStateValues = {
            '3D': '400 0\r',
            'L': '400 1\r',
            'R': '400 2\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3Dto2D', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '60 1\r',
            '16:9': '60 2\r',
            'LBX': '60 5\r',
            'Native': '60 6\r',
            'Auto': '60 7\r',
            'Superwide': '60 9\r'
        }

        AspectRatioCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': '4:3',
            '1': '16:9',
            '2': 'LBX',
            '3': 'Native',
            '4': 'Auto',
        }

        AspectRatioCmdString = '~{0}127 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '80 1\r',
            'Off': '80 0\r'
        }

        AudioMuteCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '~{0}01 1\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '02 1\r',
            'Off': '02 0\r'
        }

        AVMuteCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '88 0\r',
            'CC 1': '88 1\r',
            'CC 2': '88 2\r'
        }

        ClosedCaptionCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '04 1\r',
            'Off': '04 0\r'
        }

        FreezeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': '12 1\r',
            'HDMI 2': '12 15\r',
            'VGA': '12 5\r',
            'Video': '12 10\r'
        }

        InputCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Bright': '110 1\r',
            'Eco': '110 2\r'
        }

        LampModeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '140 10\r',
            'Down': '140 14\r',
            'Left': '140 11\r',
            'Right': '140 13\r',
            'Enter': '140 12\r',
            'Menu': '140 20\r',
        }

        MenuNavigationCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '00 1\r',
            'Off': '00 0\r'
        }

        PowerCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        InputStateValues = {
            '04': 'HDMI 1',
            '05': 'HDMI 2',
            '01': 'VGA',
            '03': 'Video',
            '00': 'None'
        }

        PowerCmdString = '~{0}150 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                Power = ValueStateValues[res[2]]
                self.WriteStatus('Power', Power, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

            try:
                Input = InputStateValues[res[7:9]]
                self.WriteStatus('Input', Input, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

            try:
                if Power == 'On':
                    LampUsage = int(res[3:7])
                    self.WriteStatus('LampUsage', LampUsage, qualifier)
            except (ValueError, IndexError, NameError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '03 1\r',
            'Off': '03 0\r'
        }

        VideoMuteCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 10
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '~{0}81 {1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == 'F\r':
            print('{0} Command Failed'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r').decode()
            if res:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
