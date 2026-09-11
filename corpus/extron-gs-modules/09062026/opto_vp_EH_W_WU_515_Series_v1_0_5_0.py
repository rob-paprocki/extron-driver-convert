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

        self._DeviceID = '01'
        
        self.Models = {
            'WU515T': self.opto_1_1264_XGAT,
            'WU515': self.opto_1_1264_XGA,
            'W515': self.opto_1_1264_1080,
            'EH515': self.opto_1_1264_1080,
            'EH515T': self.opto_1_1264_1080T,
            'X615': self.opto_1_1264_1080,
            'W515T': self.opto_1_1264_1080T,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DInvert': {'Status': {}},
            '3DMode': {'Status': {}},
            '3Dto2D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenType': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def ProjectorID(self):
        return self._ProjectorID

    @ProjectorID.setter
    def ProjectorID(self, value):

        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = value.zfill(2)

    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '405 0\r',
            'SBS': '405 1\r',
            'Top and Bottom': '405 2\r',
            'Frame Sequential': '405 3\r',
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
            'VESA 3D': '230 3\r',
            'Off': '230 0\r'
        }

        ModeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3DMode', ModeCmdString, value, qualifier)

    def Set3Dto2D(self, value, qualifier):

        ValueStateValues = {
            '3D': '400 0\r',
            'Left': '400 1\r',
            'Right': '400 2\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('3Dto2D', CmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '~{0}{1}'.format(self._DeviceID, self.AspectRatioValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '~{0}127 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.AspectRatioStates[res[2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AspectRatio: Invalid/Unexpected Response'])

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Default': '89 0\r',
            'Audio 1': '89 1\r',
            'Audio 2': '89 3\r',
            'Audio 3': '89 4\r'
        }

        AudioInputCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '03 1\r',
            'Off': '03 0\r'
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
            'CC1': '88 1\r',
            'CC2': '88 2\r'
        }

        ClosedCaptionCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': '20 1\r',
            'Bright': '20 2\r',
            'Movie': '20 3\r',
            'sRGB': '20 4\r',
            'Blackboard': '20 7\r',
            'DICOM SIM': '20 13\r',
            'User': '20 5\r',
            '3D': '20 9\r'
        }

        DisplayModeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '103 1\r',
            'Off': '103 0\r'
        }

        ExecutiveModeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '04 1\r',
            'Off': '04 0\r'
        }

        FreezeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = '~{0}{1}'.format(self._DeviceID, self.InputValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Bright': '110 1\r',
            'Eco': '110 2\r',
            'Power': '110 5\r'
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
            'Menu': '140 20\r'
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

        PowerStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        DisplayStateValues = {
            1: 'Presentation',
            2: 'Bright',
            3: 'Movie',
            4: 'sRGB',
            7: 'Blackboard',
            12: 'DICOM SIM',
            5: 'User',
            9: '3D',
            0: 'None',
        }

        PowerCmdString = '~{0}150 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:

                power = PowerStateValues[res[2]]
                self.WriteStatus('Power', power, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

            try:

                lamp_hours = int(res[3:7])
                self.WriteStatus('LampUsage', lamp_hours, qualifier)
            except (ValueError, IndexError):
                self.Error(['LampUsage: Invalid/Unexpected Response'])

            try:
                input_ = self.InputStates[int(res[7:9])]
                self.WriteStatus('Input', input_, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

            try:

                display = DisplayStateValues[int(res[13:-1])]
                self.WriteStatus('DisplayMode', display, qualifier)
            except (KeyError, IndexError):
                self.Error(['DisplayMode: Invalid/Unexpected Response'])

    def SetScreenType(self, value, qualifier):

        ValueStateValues = {
            '16:9': '90 0\r',
            '16:10': '90 1\r'
        }

        ScreenTypeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('ScreenType', ScreenTypeCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '140 18\r',
            'Down': '140 17\r'
        }

        VolumeCmdString = '~{0}{1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or int(self._DeviceID) == 0:
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

    def opto_1_1264_1080T(self):

        self.AspectRatioValues = {
            '4:3'       : '60 1\r', 
            'Letterbox' : '60 5\r', 
            'Native'    : '60 6\r', 
            'Auto'      : '60 7\r',
            '16:9'      : '60 2\r',
        }

        self.AspectRatioStates = {
            '1' : '4:3', 
            '5' : 'Letterbox', 
            '6' : 'Native', 
            '7' : 'Auto',
            '2' : '16:9',
        }

        self.InputValues = {
            'HDMI1'           : '12 1\r', 
            'HDMI2'           : '12 15\r', 
            'Display Port'    : '12 20\r', 
            'VGA1'            : '12 5\r', 
            'VGA2'            : '12 6\r', 
            'Video'           : '12 10\r', 
            'S-Video'         : '12 9\r',
            'HDBaseT'         : '12 21\r' 
        }

        self.InputStates = {
            7  :   'HDMI1',
            8  :   'HDMI2',
            15  :  'Display Port',
            2  :   'VGA1',
            3  :   'VGA2',
            5  :   'Video',
            4  :   'S-Video',
            0  :   'None',
            16  :   'HDBaseT',
        }

    def opto_1_1264_1080(self):

        self.AspectRatioValues = {
            '4:3'       : '60 1\r', 
            'Letterbox' : '60 5\r', 
            'Native'    : '60 6\r', 
            'Auto'      : '60 7\r',
            '16:9'      : '60 2\r',
        }

        self.AspectRatioStates = {
            '1' : '4:3', 
            '5' : 'Letterbox', 
            '6' : 'Native', 
            '7' : 'Auto',
            '2' : '16:9',
        }

        self.InputValues = {
            'HDMI1'           : '12 1\r', 
            'HDMI2'           : '12 15\r', 
            'Display Port'    : '12 20\r', 
            'VGA1'            : '12 5\r', 
            'VGA2'            : '12 6\r', 
            'Video'           : '12 10\r', 
            'S-Video'         : '12 9\r'
        }

        self.InputStates = {
            7  :   'HDMI1',
            8  :   'HDMI2',
            15  :  'Display Port',
            2  :   'VGA1',
            3  :   'VGA2',
            5  :   'Video',
            4  :   'S-Video',
            0  :   'None',
        }

    def opto_1_1264_XGA(self):
        
        self.AspectRatioValues = {
            '4:3'       : '60 1\r',   
            '16:10'     : '60 3\r', 
            'Letterbox' : '60 5\r', 
            'Native'    : '60 6\r', 
            'Auto'      : '60 7\r',
            '16:9'      : '60 2\r'
        }

        self.AspectRatioStates = {
            '1' : '4:3', 
            '3' : '16:10', 
            '5' : 'Letterbox', 
            '6' : 'Native', 
            '7' : 'Auto',
            '2' : '16:9',
        }

        self.InputValues = {
            'HDMI1'           : '12 1\r', 
            'HDMI2'           : '12 15\r', 
            'Display Port'    : '12 20\r', 
            'VGA1'            : '12 5\r', 
            'VGA2'            : '12 6\r', 
            'Video'           : '12 10\r', 
            'S-Video'         : '12 9\r'
        }

        self.InputStates = {
            7  :   'HDMI1',
            8  :   'HDMI2',
            15  :  'Display Port',
            2  :   'VGA1',
            3  :   'VGA2',
            5  :   'Video',
            4  :   'S-Video',
            0  :   'None',
        }

    def opto_1_1264_XGAT(self):
        
        self.AspectRatioValues = {
            '4:3'       : '60 1\r',   
            '16:10'     : '60 3\r', 
            'Letterbox' : '60 5\r', 
            'Native'    : '60 6\r', 
            'Auto'      : '60 7\r',
            '16:9'      : '60 2\r'
        }

        self.AspectRatioStates = {
            '1' : '4:3', 
            '3' : '16:10', 
            '5' : 'Letterbox', 
            '6' : 'Native', 
            '7' : 'Auto',
            '2' : '16:9',
        }

        self.InputValues = {
            'HDMI1'           : '12 1\r', 
            'HDMI2'           : '12 15\r', 
            'Display Port'    : '12 20\r', 
            'VGA1'            : '12 5\r', 
            'VGA2'            : '12 6\r', 
            'Video'           : '12 10\r', 
            'S-Video'         : '12 9\r',
            'HDBaseT'         : '12 21\r' 
        }

        self.InputStates = {
            7  :   'HDMI1',
            8  :   'HDMI2',
            15  :  'Display Port',
            2  :   'VGA1',
            3  :   'VGA2',
            5  :   'Video',
            4  :   'S-Video',
            0  :   'None',
            16  :   'HDBaseT',
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