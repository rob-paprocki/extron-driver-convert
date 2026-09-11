from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.Models = {}
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
             '3DInvert': { 'Status': {}},
             '3DMode': { 'Status': {}},
             '3DSync': { 'Status': {}},
             'AutoImage': { 'Status': {}},
             'Brightness': { 'Status': {}},
             'Channel': { 'Status': {}},
             'Contrast': { 'Status': {}},
             'Focus': { 'Status': {}},
             'Freeze': { 'Status': {}},
             'HorizontalShift': { 'Status': {}},
             'Input': { 'Status': {}},
             'LampOperation': { 'Status': {}},
             'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
             'PictureInPicture': { 'Status': {}},
             'PictureInPicturePosition': { 'Status': {}},
             'PictureInPictureSwap': { 'Status': {}},
             'Power': { 'Status': {}},
             'Shutter': { 'Status': {}},
             'SplitScreen': { 'Status': {}},
             'VerticalShift': { 'Status': {}},
             'VideoMute': { 'Status': {}},
             'Zoom': { 'Status': {}},
             }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(TDN!00([0,1])\)'), self.__Match3DInvert, None)
            self.AddMatchString(re.compile(b'\(TDM!00([0-8])\)'), self.__Match3DMode, None)
            self.AddMatchString(re.compile(b'\(TDO!00([0,1])\)'), self.__Match3DSync, None)
            self.AddMatchString(re.compile(b'\(BRT!(-{0,1}\d{3,4})\)'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'\(CHA!0(\d{2})\)'), self.__MatchChannel, None)
            self.AddMatchString(re.compile(b'\(CON!(\d{3,4})\)'), self.__MatchContrast, None)
            self.AddMatchString(re.compile(b'\(FRZ!00([0,1])\)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\(SIN!0([1-4][1-6])\)'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(HIS\+LMP(\d)!..0\s00\d\s.+"(\d{1,4}):\d\d"\)'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\(LOP!00([0-3])\)'), self.__MatchLampOperation, None)
            self.AddMatchString(re.compile(b'\(PIP!00([0-3])\)'), self.__MatchPictureInPicture, None)
            self.AddMatchString(re.compile(b'\(PPP!00([0-3])\)'), self.__MatchPictureInPicturePosition, None)
            self.AddMatchString(re.compile(b'\(PWR!0([0-3]{2})'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(SHU!00([0,1])\)'), self.__MatchShutter, None)
            self.AddMatchString(re.compile(b'\(SPT!00([0-2])\)'), self.__MatchSplitScreen, None)
            self.AddMatchString(re.compile(b'\(PMT!00([0,1])\)'), self.__MatchVideoMute, None)

    def Set3DInvert(self, value, qualifier):

        ThreeDInvertStateValues = {
            'On'   : 1,
            'Off'  : 0
            }        
        ThreeDInvertCmdString = '(TDN{0})'.format(ThreeDInvertStateValues[value])
        self.__SetHelper('3DInvert', ThreeDInvertCmdString, value, qualifier)
            
    def Update3DInvert(self, value, qualifier):

        ThreeDInvertCmdString = '(TDN?)'
        self.__UpdateHelper('3DInvert', ThreeDInvertCmdString, value, qualifier)
        
    def __Match3DInvert(self, match, tag):

        ThreeDInvertStateNames = {
            '1' : 'On',
            '0' : 'Off'
            }
        value = ThreeDInvertStateNames[match.group(1).decode()]
        self.WriteStatus('3DInvert', value, None)
        
    def Set3DMode(self, value, qualifier):

        ThreeDModeStateValues = {
            'Off'           : 0,
            'Auto'          : 1,
            'Native'        : 2,
            'Frame Doubled' : 3,
            'Dual Input'    : 4,
            'Side-by-Side'  : 5,
            'Top/Bottom'    : 6,
            'Frame Packed'  : 7
            }        
        ThreeDModeCmdString = '(TDM{0})'.format(ThreeDModeStateValues[value])
        self.__SetHelper('3DMode', ThreeDModeCmdString, value, qualifier)
            
    def Update3DMode(self, value, qualifier):

        ThreeDModeCmdString = '(TDM?)'
        self.__UpdateHelper('3DMode', ThreeDModeCmdString, value, qualifier)
        
    def __Match3DMode(self, match, tag):

        ThreeDModeStateNames = {
            '0' : 'Off',
            '1' : 'Auto',
            '2' : 'Native',
            '3' : 'Frame Doubled',
            '4' : 'Dual Input',
            '5' : 'Side-by-Side',
            '6' : 'Top/Bottom',
            '7' : 'Frame Packed'  
            }
        value = ThreeDModeStateNames[match.group(1).decode()]
        self.WriteStatus('3DMode', value, None)
        
    def Set3DSync(self, value, qualifier):

        ThreeDSyncStateValues = {
            'Off'   : 0,
            'On'    : 1
            }        
        ThreeDSyncCmdString = '(TDO{0})'.format(ThreeDSyncStateValues[value])
        self.__SetHelper('3DSync', ThreeDSyncCmdString, value, qualifier)
            
    def Update3DSync(self, value, qualifier):

        ThreeDSyncCmdString = '(TDO?)'
        self.__UpdateHelper('3DSync', ThreeDSyncCmdString, value, qualifier)
        
    def __Match3DSync(self, match, tag):

        ThreeDSyncStateNames = {
            '0' : 'Off',
            '1' : 'On'
            }
        value = ThreeDSyncStateNames[match.group(1).decode()]
        self.WriteStatus('3DSync', value, None)
        
    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '(ASU)'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetBrightness(self, value, qualifier):

        BrightnessConstraints = {
            'Min'           : -1000,
            'Max'           :  1000
            }
        
        if BrightnessConstraints['Min'] <= value <= BrightnessConstraints['Max']:
            BrightnessCmdString = '(BRT{0})'.format(value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')
            
    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = '(BRT?)'
        self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        
    def __MatchBrightness(self, match, tag):        
        
        value = int(match.group(1).decode())
        self.WriteStatus('Brightness', value, None)
        
    def SetChannel(self, value, qualifier):

        ChannelConstraints = {
            'Min'   : 1,
            'Max'   : 99 
            }
        
        intValue = int(value)
        if ChannelConstraints['Min'] <= intValue <= ChannelConstraints['Max']:
            ChannelCmdString = '(CHA{0})'.format(intValue)
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')
            
    def UpdateChannel(self, value, qualifier):

        ChannelCmdString = '(CHA?)'
        self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)
        
    def __MatchChannel(self, match, tag):        
        
        value = str(int(match.group(1).decode()))      
        self.WriteStatus('Channel', value, None)
        
    def SetContrast(self, value, qualifier):

        ContrastConstraints = {
            'Min'   : 0,
            'Max'   : 1000 
            }
        
        if ContrastConstraints['Min'] <= value <= ContrastConstraints['Max']:
            ContrastCmdString = '(CON{0})'.format(value)
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')
            
    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = '(CON?)'
        self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        
    def __MatchContrast(self, match, tag):        
        
        value = int(match.group(1).decode())
        self.WriteStatus('Contrast', value, None)
        
    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'In'   :  1,
            'Out'  : -1,
            'Stop' :  0
            }
        FocusCmdString = '(LMV+FRUN{0})'.format(FocusStateValues[value])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On'  : 1, 
            'Off' : 0 
            }
        FreezeCmdString = '(FRZ{0})'.format(FreezeStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier) 

    def UpdateFreeze(self, value, qualifier): 
      
        FreezeCmdString = '(FRZ?)'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeStateNames = {
           '1' : 'On', 
           '0' : 'Off'  
           }
        
        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetHorizontalShift(self, value, qualifier):

        HorizontalShiftStateValues = {
            'Left'   :  1,
            'Right'  : -1,
            'Stop'   :  0
            }
        HorizontalShiftCmdString = '(LMV+HRUN{0})'.format(HorizontalShiftStateValues[value])
        self.__SetHelper('HorizontalShift', HorizontalShiftCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'SLOT 1-1' : '11',
            'SLOT 1-2' : '12',
            'SLOT 1-3' : '13',
            'SLOT 1-4' : '14',
            'SLOT 1-5' : '15',
            'SLOT 1-6' : '16',
            'SLOT 2-1' : '21',
            'SLOT 2-2' : '22',
            'SLOT 2-3' : '23',
            'SLOT 2-4' : '24',
            'SLOT 2-5' : '25',
            'SLOT 2-6' : '26',
            'SLOT 3-1' : '31',
            'SLOT 3-2' : '32',
            'SLOT 3-3' : '33',
            'SLOT 3-4' : '34',
            'SLOT 3-5' : '35',
            'SLOT 3-6' : '36',
            'SLOT 4-1' : '41',
            'SLOT 4-2' : '42',
            'SLOT 4-3' : '43',
            'SLOT 4-4' : '44',
            'SLOT 4-5' : '45',
            'SLOT 4-6' : '46'
            }  
        InputCmdString = '(SIN{0})'.format(InputStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier) 

    def UpdateInput(self, value, qualifier): 
      
        InputCmdString = '(SIN?)'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputStateNames = {
            '11' : 'SLOT 1-1',
            '12' : 'SLOT 1-2',
            '13' : 'SLOT 1-3',
            '14' : 'SLOT 1-4',
            '15' : 'SLOT 1-5',
            '16' : 'SLOT 1-6',
            '21' : 'SLOT 2-1',
            '22' : 'SLOT 2-2',
            '23' : 'SLOT 2-3',
            '24' : 'SLOT 2-4',
            '25' : 'SLOT 2-5',
            '26' : 'SLOT 2-6',
            '31' : 'SLOT 3-1',
            '32' : 'SLOT 3-2',
            '33' : 'SLOT 3-3',
            '34' : 'SLOT 3-4',
            '35' : 'SLOT 3-5',
            '36' : 'SLOT 3-6',
            '41' : 'SLOT 4-1',
            '42' : 'SLOT 4-2',
            '43' : 'SLOT 4-3',
            '44' : 'SLOT 4-4',
            '45' : 'SLOT 4-5',
            '46' : 'SLOT 4-6' 
           }
        
        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampOperation(self, value, qualifier):

        LampOperationStateValues = {
            'Auto-select'   : 0, 
            'Lamp 1'        : 1,
            'Lamp 2'        : 2,
            'Dual Lamp'     : 3 
            }
        LampOperationCmdString = '(LOP{0})'.format(LampOperationStateValues[value])
        self.__SetHelper('LampOperation', LampOperationCmdString, value, qualifier) 

    def UpdateLampOperation(self, value, qualifier): 
      
        LampOperationCmdString = '(LOP?)'
        self.__UpdateHelper('LampOperation', LampOperationCmdString, value, qualifier)

    def __MatchLampOperation(self, match, tag):

        LampOperationStateNames = {
            '0' : 'Auto-select',
            '1' : 'Lamp 1',
            '2' : 'Lamp 2',
            '3' : 'Dual Lamp' 
           }
        
        value = LampOperationStateNames[match.group(1).decode()]
        self.WriteStatus('LampOperation', value, None)

    def UpdateLampUsage(self, value, qualifier):  
   
        LampNumber = int(qualifier['Lamp'])
        if(LampNumber in (1,2)):
            LampUsageCmdString = '(HIS+LMP{0}?)'.format(LampNumber)
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def __MatchLampUsage(self, match, tag):

        
        lampNumber = match.group(1).decode()
        value = int(match.group(2).decode())

        qualifier = {'Lamp':lampNumber}
        self.WriteStatus('LampUsage', value, qualifier)

    def SetPictureInPicture(self, value, qualifier):

        PictureInPictureStateValues = {
            'Disabled'            : 0, 
            'Enabled'             : 1,
            'Picture-by-Picture'  : 2
            }
        PictureInPictureCmdString = '(PIP{0})'.format(PictureInPictureStateValues[value])
        self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier) 

    def UpdatePictureInPicture(self, value, qualifier): 
      
        PictureInPictureCmdString = '(PIP?)'
        self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def __MatchPictureInPicture(self, match, tag):

        PictureInPictureStateNames = {
            '0' : 'Disabled',
            '1' : 'Enabled',
            '2' : 'Picture-by-Picture'
           }
        
        value = PictureInPictureStateNames[match.group(1).decode()]
        self.WriteStatus('PictureInPicture', value, None)

    def SetPictureInPicturePosition(self, value, qualifier):

        PictureInPicturePositionStateValues = {
            'Top Right'     : 0, 
            'Top Left'      : 1,
            'Bottom Left'   : 2,
            'Bottom Right'  : 3
            }
        PictureInPicturePositionCmdString = '(PPP{0})'.format(PictureInPicturePositionStateValues[value])
        self.__SetHelper('PictureInPicturePosition', PictureInPicturePositionCmdString, value, qualifier) 

    def UpdatePictureInPicturePosition(self, value, qualifier): 
      
        PictureInPicturePositionCmdString = '(PPP?)'
        self.__UpdateHelper('PictureInPicturePosition', PictureInPicturePositionCmdString, value, qualifier)

    def __MatchPictureInPicturePosition(self, match, tag):

        PictureInPicturePositionStateNames = {
            '0' : 'Top Right',
            '1' : 'Top Left',
            '2' : 'Bottom Left',
            '3' : 'Bottom Right'
            }
        
        value = PictureInPicturePositionStateNames[match.group(1).decode()]
        self.WriteStatus('PictureInPicturePosition', value, None)

    def SetPictureInPictureSwap(self, value, qualifier):

        PictureInPictureSwapCmdString = '(PPS)'
        self.__SetHelper('PictureInPictureSwap', PictureInPictureSwapCmdString, value, qualifier)
    def SetPower(self, value, qualifier): 

        PowerStateValues = {
            'On'  : 1,  
            'Off' : 0 
            }  
        PowerCmdString = '(PWR{0})'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)  

    def UpdatePower(self, value, qualifier):     

        PowerCmdString = '(PWR?)'   
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            '01' : 'On', 
            '00' : 'Off',
            '11' : 'Warming',
            '10' : 'Cooling'   
            }
        value = PowerStateNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier): 

        ShutterStateValues = {
            'Close' : 1,  
            'Open'  : 0 
            }  
        ShutterCmdString = '(SHU{0:2})'.format(ShutterStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)  

    def UpdateShutter(self, value, qualifier):  
   
        ShutterCmdString = '(SHU?)'   
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)   
        
    def __MatchShutter(self, match, tag):

        ShutterStateNames = {
            '1'  : 'Close', 
            '0'  : 'Open'
            }
        
        value = ShutterStateNames[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)        

    def SetSplitScreen(self, value, qualifier): 

        SplitScreenStateValues = {
            'Off'  : 0,  
            'Side' : 1,
            'Top'  : 2 
            }  
        SplitScreenCmdString = '(SPT{0})'.format(SplitScreenStateValues[value])
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)

    def UpdateSplitScreen(self, value, qualifier):  
   
        SplitScreenCmdString = '(SPT?)'   
        self.__UpdateHelper('SplitScreen', SplitScreenCmdString, value, qualifier)   

    def __MatchSplitScreen(self, match, tag):

        SplitScreenStateNames = {
            '0' : 'Off', 
            '1' : 'Side',
            '2' : 'Top'
            }
        
        value = SplitScreenStateNames[match.group(1).decode()]
        self.WriteStatus('SplitScreen', value, None)

    def SetVerticalShift(self, value, qualifier):

        VerticalShiftStateValues = {
            'Up'    :  1,
            'Down'  : -1,
            'Stop'  :  0
            }
        VerticalShiftCmdString = '(LMV+VRUN{0})'.format(VerticalShiftStateValues[value])
        self.__SetHelper('VerticalShift', VerticalShiftCmdString, value, qualifier)
    def SetVideoMute(self, value, qualifier): 

        VideoMuteStateValues = {
            'On'  : 1,  
            'Off' : 0 
            }  
        VideoMuteCmdString = '(PMT{0})'.format(VideoMuteStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)  

    def UpdateVideoMute(self, value, qualifier):  
   
        VideoMuteCmdString = '(PMT?)'   
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)   
        
    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
            '1'  : 'On', 
            '0'  : 'Off'
            }
        
        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'In'    :  1,
            'Out'   : -1,
            'Stop'  :  0
            }
        ZoomCmdString = '(LMV+ZRUN{0})'.format(ZoomStateValues[value])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)    
    
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)           

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

