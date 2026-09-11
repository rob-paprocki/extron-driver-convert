from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import ProgramLog

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {
            'PN-L603A': self.shrp_39_742_A,
            'PN-L703A': self.shrp_39_742_A,
            'PN-L603WA': self.shrp_39_742_W,
            'PN-L703WA': self.shrp_39_742_W,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input Type'], 'Status': {}},
            'AdjustmentLock': {'Status': {}},
            'AdjustmentLockTarget': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Parameters': ['Direction'], 'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'TouchOperationMode': {'Status': {}},
            'TouchPanelMode': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
         self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
         self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

        def SetPassword(self, value, qualifier):
            if self.devicePassword:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')

    def SetAdjustmentLock(self, value, qualifier):

        AdjustmentLockStateValues = {
            'Mode 1': 'ALCK   1\r\n',
            'Off': 'ALCK   0\r\n',
            'Mode 2': 'ALCK   2\r\n',
            }

        AdjustmentLockCmdString = AdjustmentLockStateValues[value]
        self.__SetHelper('AdjustmentLock', AdjustmentLockCmdString, value, qualifier)

    def UpdateAdjustmentLock(self, value, qualifier):

        AdjustmentLockStateNames = {
            '1': 'Mode 1',
            '0': 'Off',
            '2': 'Mode 2',
           }

        AdjustmentLockCmdString = 'ALCK????\r\n'
        res = self.__UpdateHelper('AdjustmentLock', AdjustmentLockCmdString, value, qualifier)
        if res:
            try:
                value = AdjustmentLockStateNames[res[0]]
                self.WriteStatus('AdjustmentLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Adjustment Lock: Invalid/Unexpected Response'])

    def SetAdjustmentLockTarget(self, value, qualifier):

        AdjustmentLockTargetStateValues = {
            'Remote Control': 'ALTG   0\r\n',
            'Monitor Buttons': 'ALTG   1\r\n',
            'Both': 'ALTG   2\r\n',
            }

        AdjustmentLockTargetCmdString = AdjustmentLockTargetStateValues[value]
        self.__SetHelper('AdjustmentLockTarget', AdjustmentLockTargetCmdString, value, qualifier)

    def UpdateAdjustmentLockTarget(self, value, qualifier):

        AdjustmentLockTargetStateNames = {
            '0': 'Remote Control',
            '1': 'Monitor Buttons',
            '2': 'Both',
           }

        AdjustmentLockTargetCmdString = 'ALTG????\r\n'
        res = self.__UpdateHelper('AdjustmentLockTarget', AdjustmentLockTargetCmdString, value, qualifier)
        if res:
            try:
                value = AdjustmentLockTargetStateNames[res[0]]
                self.WriteStatus('AdjustmentLockTarget', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Adjustment Lock Target: Invalid/Unexpected Response'])

    def SetAspectRatio(self, value, qualifier):

        PCAspectRatioStateValues = {
            'Wide': 'WIDE   1\r\n',
            'Normal': 'WIDE   2\r\n',
            'Dot by Dot': 'WIDE   3\r\n',
            'Zoom 1': 'WIDE   4\r\n',
            'Zoom 2': 'WIDE   5\r\n',
            }

        AVAspectRatioStateValues = {
            'Wide': 'WIDE   1\r\n',
            'Normal': 'WIDE   4\r\n',
            'Dot by Dot': 'WIDE   5\r\n',
            'Zoom 1': 'WIDE   2\r\n',
            'Zoom 2': 'WIDE   3\r\n',
            }

        InputType = qualifier['Input Type']

        if InputType not in ['PC', 'AV']:
            self.Discard('Invalid Command for SetAspectRatio')
        else:
            if InputType == 'PC':
                AspectRatioCmdString = PCAspectRatioStateValues[value]
            elif InputType == 'AV':
                AspectRatioCmdString = AVAspectRatioStateValues[value]

            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        PCAspectRatioStateNames = {
            '1': 'Wide',
            '2': 'Normal',
            '3': 'Dot by Dot',
            '4': 'Zoom 1',
            '5': 'Zoom 2',
           }

        AVAspectRatioStateNames = {
            '1': 'Wide',
            '4': 'Normal',
            '5': 'Dot by Dot',
            '2': 'Zoom 1',
            '3': 'Zoom 2',
           }

        InputType = qualifier['Input Type']

        AspectRatioCmdString = 'WIDE????\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if InputType == 'PC':
                    value = PCAspectRatioStateNames[res[0]]
                elif InputType == 'AV':
                    value = AVAspectRatioStateNames[res[0]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'AGIN   1\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'INPS????\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[int(res)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetMute(self, value, qualifier):

        MuteStateValues = {
            'On': 'MUTE   1\r\n',
            'Off': 'MUTE   0\r\n',
            }

        MuteCmdString = MuteStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off',
           }

        MuteCmdString = 'MUTE????\r\n'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteStateNames[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/Unexpected Response'])

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = self.PIPInputStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = 'MWIP????\r\n'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.PIPInputStateNames[int(res)]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Input: Invalid/Unexpected Response'])

    def SetPIPMode(self, value, qualifier):

        PIPModeStateValues = {
            'PIP': 'MWIN   1\r\n',
            'PbyP': 'MWIN   2\r\n',
            'PbyP 2': 'MWIN   3\r\n',
            'Off': 'MWIN   0\r\n',
            }

        PIPModeCmdString = PIPModeStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeStateNames = {
            '1': 'PIP',
            '2': 'PbyP',
            '3': 'PbyP 2',
            '0': 'Off',
           }

        PIPModeCmdString = 'MWIN????\r\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = PIPModeStateNames[res[0]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode: Invalid/Unexpected Response'])

    def SetPIPPosition(self, value, qualifier):

        PIPPositionConstraints = {
            'Min': 0,
            'Max': 100
            }

        Direction = qualifier['Direction']

        if PIPPositionConstraints['Min'] <= value <= PIPPositionConstraints['Max'] and Direction in ['Horizontal', 'Vertical']:
            if Direction == 'Horizontal':
                PIPPositionCmdString = 'MHPS{0: >4}\r\n'.format(value)
            elif Direction == 'Vertical':
                PIPPositionCmdString = 'MVPS{0: >4}\r\n'.format(value)
            self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def UpdatePIPPosition(self, value, qualifier):

        Direction = qualifier['Direction']
        if Direction == 'Horizontal':
            PIPPositionCmdString = 'MHPS????\r\n'
        elif Direction == 'Vertical':
            PIPPositionCmdString = 'MVPS????\r\n'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('PIPPosition', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP Position: Invalid/Unexpected Response'])

    def SetPIPSize(self, value, qualifier):

        PIPSizeConstraints = {
            'Min': 1,
            'Max': 64
            }

        if PIPSizeConstraints['Min'] <= value <= PIPSizeConstraints['Max']:
            PIPSizeCmdString = 'MPSZ{0: >4}\r\n'.format(value)
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'MPSZ????\r\n'
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('PIPSize', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['PIP Size: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerCmdString = self.PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'POWR????\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = self.PowerStateNames[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetTouchOperationMode(self, value, qualifier):

        TouchOperationModeStateValues = {
            'Auto': 'TOMD   0\r\n',
            'Multi-Touch Mode': 'TOMD   1\r\n',
            'Mouse Mode': 'TOMD   2\r\n',
            }

        TouchOperationModeCmdString = TouchOperationModeStateValues[value]
        self.__SetHelper('TouchOperationMode', TouchOperationModeCmdString, value, qualifier)

    def UpdateTouchOperationMode(self, value, qualifier):

        TouchOperationModeStateNames = {
            '0': 'Auto',
            '1': 'Multi-Touch Mode',
            '2': 'Mouse Mode',
           }

        TouchOperationModeCmdString = 'TOMD????\r\n'
        res = self.__UpdateHelper('TouchOperationMode', TouchOperationModeCmdString, value, qualifier)
        if res:
            try:
                value = TouchOperationModeStateNames[res[0]]
                self.WriteStatus('TouchOperationMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Operation Mode: Invalid/Unexpected Response'])

    def SetTouchPanelMode(self, value, qualifier):

        TouchPanelModeStateValues = {
            'On': 'GMDP   1\r\n',
            'Off': 'GMDP   0\r\n',
            }
        TouchPanelModeCmdString = TouchPanelModeStateValues[value]
        self.__SetHelper('TouchPanelMode', TouchPanelModeCmdString, value, qualifier)

    def UpdateTouchPanelMode(self, value, qualifier):

        TouchPanelModeStateNames = {
            '1': 'On',
            '0': 'Off',
           }

        TouchPanelModeCmdString = 'GMDP????\r\n'
        res = self.__UpdateHelper('TouchPanelMode', TouchPanelModeCmdString, value, qualifier)
        if res:
            try:
                value = TouchPanelModeStateNames[res[0]]
                self.WriteStatus('TouchPanelMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Touch Panel Mode: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 31
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOLM{0: >4}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                self.Error(['{0} no relevant command or command cannot be used in the current state of the device'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def shrp_39_742_A(self):

        self.InputStateValues = {
            'D-SUB 1 RGB'       : 'INPS   2\r\n',
            'D-SUB 1 Component' : 'INPS   3\r\n',
            'D-SUB 1 Video'     : 'INPS   4\r\n',
            'HDMI 1 AV'         : 'INPS   9\r\n',
            'HDMI 1 PC'         : 'INPS  10\r\n',
            'HDMI 2 AV'         : 'INPS  12\r\n',
            'HDMI 2 PC'         : 'INPS  13\r\n',
            'Display Port'      : 'INPS  14\r\n',
            'D-SUB 2'           : 'INPS  16\r\n',
            'HDMI 3 AV'         : 'INPS  17\r\n',
            'HDMI 3 PC'         : 'INPS  18\r\n',
            'Whiteboard'        : 'INPS  19\r\n'
            }

        self.InputStateNames = {
            2  : 'D-SUB 1 RGB',
            3  : 'D-SUB 1 Component',
            4  : 'D-SUB 1 Video',
            9  : 'HDMI 1 AV',
            10 : 'HDMI 1 PC',
            12 : 'HDMI 2 AV',
            13 : 'HDMI 2 PC',
            14 : 'Display Port',
            16 : 'D-SUB 2',
            17 : 'HDMI 3 AV',
            18 : 'HDMI 3 PC',
            19 : 'Whiteboard'
           }

        self.PIPInputStateValues = {
            'D-SUB 1 RGB'       : 'MWIP   2\r\n',
            'D-SUB 1 Component' : 'MWIP   3\r\n',
            'D-SUB 1 Video'     : 'MWIP   4\r\n',
            'HDMI 1 AV'         : 'MWIP   9\r\n',
            'HDMI 1 PC'         : 'MWIP  10\r\n',
            'HDMI 2 AV'         : 'MWIP  12\r\n',
            'HDMI 2 PC'         : 'MWIP  13\r\n',
            'Display Port'      : 'MWIP  14\r\n',
            'D-SUB 2'           : 'MWIP  16\r\n',
            'HDMI 3 AV'         : 'MWIP  17\r\n',
            'HDMI 3 PC'         : 'MWIP  18\r\n',
            'Whiteboard'        : 'MWIP  19\r\n'
            }                             

        self.PIPInputStateNames = {
            2  : 'D-SUB 1 RGB',
            3  : 'D-SUB 1 Component',
            4  : 'D-SUB 1 Video',
            9  : 'HDMI 1 AV',
            10 : 'HDMI 1 PC',
            12 : 'HDMI 2 AV',
            13 : 'HDMI 2 PC',
            14 : 'Display Port',
            16 : 'D-SUB 2',
            17 : 'HDMI 3 AV',
            18 : 'HDMI 3 PC',
            19 : 'Whiteboard'
           }

        self.PowerStateValues = {
            'On'  : 'POWR   1\r\n',
            'Off' : 'POWR   0\r\n',
            'Whiteboard Standby Mode'  : 'POWR  99\r\n'
            }   
                       
        self.PowerStateNames = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Input Signal Waiting Mode',
            '9' : 'Whiteboard Standby Mode'
           }        


    def shrp_39_742_W(self):

        self.InputStateValues = {
            'D-SUB 1 RGB'       : 'INPS   2\r\n',
            'D-SUB 1 Component' : 'INPS   3\r\n',
            'D-SUB 1 Video'     : 'INPS   4\r\n',
            'HDMI 1 AV'         : 'INPS   9\r\n',
            'HDMI 1 PC'         : 'INPS  10\r\n',
            'HDMI 2 AV'         : 'INPS  12\r\n',
            'HDMI 2 PC'         : 'INPS  13\r\n',
            'Display Port'      : 'INPS  14\r\n',
            'D-SUB 2'           : 'INPS  16\r\n',
            'HDMI 3 AV'         : 'INPS  17\r\n',
            'HDMI 3 PC'         : 'INPS  18\r\n',
            'Direct Drawing'    : 'INPS  19\r\n',
            'Wireless'          : 'INPS  20\r\n',
            }

        self.InputStateNames = {
            2  : 'D-SUB 1 RGB',
            3  : 'D-SUB 1 Component',
            4  : 'D-SUB 1 Video',
            9  : 'HDMI 1 AV',
            10 : 'HDMI 1 PC',
            12 : 'HDMI 2 AV',
            13 : 'HDMI 2 PC',
            14 : 'Display Port',
            16 : 'D-SUB 2',
            17 : 'HDMI 3 AV',
            18 : 'HDMI 3 PC',
            19 : 'Direct Drawing',
            20 : 'Wireless'
           }

        self.PIPInputStateValues = {
            'D-SUB 1 RGB'       : 'MWIP   2\r\n',
            'D-SUB 1 Component' : 'MWIP   3\r\n',
            'D-SUB 1 Video'     : 'MWIP   4\r\n',
            'HDMI 1 AV'         : 'MWIP   9\r\n',
            'HDMI 1 PC'         : 'MWIP  10\r\n',
            'HDMI 2 AV'         : 'MWIP  12\r\n',
            'HDMI 2 PC'         : 'MWIP  13\r\n',
            'Display Port'      : 'MWIP  14\r\n',
            'D-SUB 2'           : 'MWIP  16\r\n',
            'HDMI 3 AV'         : 'MWIP  17\r\n',
            'HDMI 3 PC'         : 'MWIP  18\r\n',
            'Direct Drawing'    : 'MWIP  19\r\n',
            'Wireless'          : 'MWIP  20\r\n'
             }                             

        self.PIPInputStateNames = {
            2  : 'D-SUB 1 RGB',
            3  : 'D-SUB 1 Component',
            4  : 'D-SUB 1 Video',
            9  : 'HDMI 1 AV',
            10 : 'HDMI 1 PC',
            12 : 'HDMI 2 AV',
            13 : 'HDMI 2 PC',
            14 : 'Display Port',
            16 : 'D-SUB 2',
            17 : 'HDMI 3 AV',
            18 : 'HDMI 3 PC',
            19 : 'Direct Drawing',
            20 : 'Wireless'
           }

        self.PowerStateValues = {
            'On'  : 'POWR   1\r\n',
            'Off' : 'POWR   0\r\n',
            }   
                       
        self.PowerStateNames = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Input Signal Waiting Mode',
           }
        
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

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

