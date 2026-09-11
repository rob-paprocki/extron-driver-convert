from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'ColorMode': { 'Status': {}},
            'EraseAll': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageRecall': { 'Status': {}},
            'ImageSave': { 'Status': {}},
            'ImageTurn': { 'Status': {}},
            'Iris': { 'Status': {}},
            'Menu': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'PosNegBlue': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'ShowAll': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x00\x31\x01(\x00|\x01)'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'\x00\x32\x01(\x00|\x01)'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'\x00\x6D\x01(\x00|\x01|\x02|\x03|\x04)'), self.__MatchColorMode, None)
            self.AddMatchString(re.compile(b'\x00\x80\x01(\x00|\x01)'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x00\x56\x01(\x00|\x01)'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\x00\x83\x01([\x00-\x03])'), self.__MatchImageTurn, None)
            self.AddMatchString(re.compile(b'\x00\x51\x01([\x00-\xFF])'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'\x00\x54\x01(\x00|\x01|\x02)'), self.__MatchPosNegBlue, None)
            self.AddMatchString(re.compile(b'\x00\x30\x01(\x00|\x01)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x00\x93\x01(\x00|\x01)'), self.__MatchShowAll, None)
            self.AddMatchString(re.compile(b'\x00\x86\x01(\x00|\x01)'), self.__MatchVideoMute, None)

    def SetAutoFocus(self, value, qualifier):

        AutoFocusStateValues = {
            'On'     : b'\x01\x31\x01\x01',
            'Off'    : b'\x01\x31\x01\x00',
            'Toggle' : b'\x01\x31\x01\x02'
            }

        AutoFocusCmdString = AutoFocusStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier): 

        AutoFocusCmdString = b'\x00\x31\x00'
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, qualifier):

        AutoFocusStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        value = AutoFocusStateNames[match.group(1)]
        self.WriteStatus('AutoFocus', value, None)

    def SetAutoIris(self, value, qualifier):

        AutoIrisStateValues = {
            'On'     : b'\x01\x32\x01\x01',
            'Off'    : b'\x01\x32\x01\x00',
            'Toggle' : b'\x01\x32\x01\x02'
            }

        AutoIrisCmdString = AutoIrisStateValues[value]
        self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def UpdateAutoIris(self, value, qualifier): 

        AutoIrisCmdString = b'\x00\x32\x00'
        self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def __MatchAutoIris(self, match, qualifier):

        AutoIrisStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        value = AutoIrisStateNames[match.group(1)]
        self.WriteStatus('AutoIris', value, None)

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'Black/White' : b'\x01\x6D\x01\x00', 
            'Presentation' : b'\x01\x6D\x01\x01', 
            'Natural' : b'\x01\x6D\x01\x02',
            'Video Conference' :b'\x01\x6D\x01\x03',
            'Manual' : b'\x01\x6D\x01\x04'
        }

        ColorModeCmdString = ValueStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        ColorModeCmdString = b'\x00\x6D\x00'
        self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def __MatchColorMode(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'Black/White', 
            b'\x01' : 'Presentation', 
            b'\x02' : 'Natural', 
            b'\x03' : 'Video Conference', 
            b'\x04' : 'Manual'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ColorMode', value, None)

    def SetEraseAll(self, value, qualifier):

        EraseAllCmdString = b'\x01\x92\x01\x20'
        self.__SetHelper('EraseAll', EraseAllCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'On'  : b'\x01\x80\x01\x01',
            'Off' : b'\x01\x80\x01\x00',
            'Toggle' : b'\x01\x80\x01\x02'
            }

        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier): 

        ExecutiveModeCmdString = b'\x00\x80\x00'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        value = ExecutiveModeStateNames[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFocus(self, value, qualifier):

        FocusStateValues = {
            'Far' : b'\x01\x21\x01\x11',
            'Near' : b'\x01\x21\x01\x12',
            'Stop' : b'\x01\x2F\x01\x00',
            }

        FocusCmdString = FocusStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On'  : b'\x01\x56\x01\x01',
            'Off' : b'\x01\x56\x01\x00',
            'Toggle' : b'\x01\x56\x01\x02'
            }

        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier): 

        FreezeCmdString = b'\x00\x56\x00'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):

        FreezeStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }

        value = FreezeStateNames[match.group(1)]
        self.WriteStatus('Freeze', value, None)

    def SetImageRecall(self, value, qualifier):

        if 1 <= int(value) <= 9:
            ImageRecallCmdString = pack('>BBBB',0x01,0x91,0x01,int(value))
            self.__SetHelper('ImageRecall', ImageRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageRecall')
    def SetImageSave(self, value, qualifier):

        if 1 <= int(value) <= 9:
            ImageSaveCmdString = pack('>BBBB',0x01,0x92,0x01,int(value))
            self.__SetHelper('ImageSave', ImageSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageSave')
    def SetImageTurn(self, value, qualifier):

        ImageTurnStateValues = {
            'Toggle': b'\x01\x83\x01\x02',
            'Off'   : b'\x01\x83\x01\x00',
            }

        ImageTurnCmdString = ImageTurnStateValues[value]
        self.__SetHelper('ImageTurn', ImageTurnCmdString, value, qualifier)

    def UpdateImageTurn(self, value, qualifier): 

        ImageTurnCmdString = b'\x00\x83\x00'
        self.__UpdateHelper('ImageTurn', ImageTurnCmdString, value, qualifier)

    def __MatchImageTurn(self, match, qualifier):

        ImageTurnStateNames = {
            '\x00' : '0 Degrees',
            '\x01' : '-90 Degrees',
            '\x02' : '180 Degrees',
            '\x03' : '90 Degrees',
           }

        value = ImageTurnStateNames[match.group(1).decode()]
        self.WriteStatus('ImageTurn', value, None)

    def SetIris(self, value, qualifier):

        IrisStateValues = {
            'Open'  : b'\x01\x22\x01\x11',
            'Close' : b'\x01\x22\x01\x12',
            'Stop'  : b'\x01\x2F\x01\x00',
            }
        IrisCmdString = IrisStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)
    def SetMenu(self, value, qualifier):

        ValueStateValues = {
            'On'     : b'\x01\x98\x01\x01',
            'Off'    : b'\x01\x98\x01\x00',
            'Toggle' : b'\x01\x98\x01\x02',
            'Reset'  : b'\x01\x99\x01\x90',
            'Help'   : b'\x01\x99\x01\x10'
        }

        MenuCmdString = ValueStateValues[value]
        self.__SetHelper('Menu', MenuCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x01\x99\x01\x02',
            'Down'  : b'\x01\x99\x01\x08',
            'Left'  : b'\x01\x99\x01\x04',
            'Right' : b'\x01\x99\x01\x06',
            'Enter' : b'\x01\x99\x01\x05'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            'Off'       : b'\x01\x51\x01\xFF', 
            'Auto'      : b'\x01\x51\x01\x00', 
            'SVGA/60'   : b'\x01\x51\x01\x01', 
            'XGA/60'    : b'\x01\x51\x01\x04', 
            'XGA/75'    : b'\x01\x51\x01\x05', 
            'SXGA-/60'  : b'\x01\x51\x01\x08', 
            'SXGA-/85'  : b'\x01\x51\x01\x09', 
            'SXGA/60'   : b'\x01\x51\x01\x0A', 
            'SXGA/75'   : b'\x01\x51\x01\x0B', 
            'SXGA+/60'  : b'\x01\x51\x01\x12', 
            'VGA/60'    : b'\x01\x51\x01\x14', 
            '720p/50'   : b'\x01\x51\x01\x15', 
            '720p/60'   : b'\x01\x51\x01\x16', 
            '1080p/50'  : b'\x01\x51\x01\x17', 
            '1080p/60'  : b'\x01\x51\x01\x18', 
            'WSXGA/60'  : b'\x01\x51\x01\x1A', 
            'WXGA/60'   : b'\x01\x51\x01\x1B', 
            'WXGA+/60'  : b'\x01\x51\x01\x1D', 
            'WXGA*/60'  : b'\x01\x51\x01\x1E'
        }

        OutputResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = b'\x00\x51\x00'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            b'\xFF' : 'Off', 
            b'\x00' : 'Auto', 
            b'\x01' : 'SVGA/60', 
            b'\x04' : 'XGA/60', 
            b'\x05' : 'XGA/75', 
            b'\x08' : 'SXGA-/60', 
            b'\x09' : 'SXGA-/85', 
            b'\x0A' : 'SXGA/60', 
            b'\x0B' : 'SXGA/75', 
            b'\x12' : 'SXGA+/60', 
            b'\x14' : 'VGA/60', 
            b'\x15' : '720p/50', 
            b'\x16' : '720p/60', 
            b'\x17' : '1080p/50', 
            b'\x18' : '1080p/60', 
            b'\x1A' : 'WSXGA/60', 
            b'\x1B' : 'WXGA/60', 
            b'\x1D' : 'WXGA+/60', 
            b'\x1E' : 'WXGA*/60'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('OutputResolution', value, None)

    def SetPosNegBlue(self, value, qualifier):

        ValueStateValues = {
            'Positive On' : b'\x01\x54\x01\x00', 
            'Negative On' : b'\x01\x54\x01\x01', 
            'Blue On' : b'\x01\x54\x01\x02'
        }

        PosNegBlueCmdString = ValueStateValues[value]
        self.__SetHelper('PosNegBlue', PosNegBlueCmdString, value, qualifier)

    def UpdatePosNegBlue(self, value, qualifier):

        PosNegBlueCmdString = b'\x00\x54\x00'
        self.__UpdateHelper('PosNegBlue', PosNegBlueCmdString, value, qualifier)

    def __MatchPosNegBlue(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'Positive On', 
            b'\x01' : 'Negative On', 
            b'\x02' : 'Blue On'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PosNegBlue', value, None)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : b'\x01\x30\x01\x01',
            'Off' : b'\x01\x30\x01\x00',
            'Toggle' : b'\x01\x30\x01\x02'
            }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier): 


        PowerCmdString = b'\x00\x30\x00'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, qualifier):

        PowerStateNames = {
            b'\x01' : 'On',
            b'\x00' : 'Off',
           }


        value = PowerStateNames[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 3:
            PresetRecallCmdString = pack('>BBBB',0x01,0x40,0x01,int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 3:
            PresetSaveCmdString = pack('>BBBB',0x01,0x41,0x01,int(value))
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')
    def SetShowAll(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01\x93\x01\x01', 
            'Off' : b'\x01\x93\x01\x00'
        }

        ShowAllCmdString = ValueStateValues[value]
        self.__SetHelper('ShowAll', ShowAllCmdString, value, qualifier)

    def UpdateShowAll(self, value, qualifier):

        ShowAllCmdString = b'\x00\x93\x00'
        self.__UpdateHelper('ShowAll', ShowAllCmdString, value, qualifier)

    def __MatchShowAll(self, match, tag):

        ValueStateValues = {
            b'\x01' : 'On', 
            b'\x00' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ShowAll', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x01\x86\x01\x00', 
            'Off' : b'\x01\x86\x01\x01'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x00\x86\x00'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            b'\x00' : 'On', 
            b'\x01' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def SetWhiteBalance(self, value, qualifier):

        WhiteBalanceCmdString = b'\x01\x65\x01\x10'
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'Tele' : b'\x01\x20\x01\x12',
            'Wide' : b'\x01\x20\x01\x11',
            'Stop' : b'\x01\x2F\x01\x00',
            }

        ZoomCmdString = ZoomStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



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
    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}class SerialClass(SerialInterface, DeviceClass):

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

