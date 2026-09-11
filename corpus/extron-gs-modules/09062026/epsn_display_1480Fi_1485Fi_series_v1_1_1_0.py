from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
        self.Models = {
            'BrightLink 1485Fi': self.epsn_1_4487_1485Fi,
            'CB-1485Fi': self.epsn_1_4487_1485Fi,
            'EB-1485Fi': self.epsn_1_4487_1485Fi,
            'BrightLink 1480Fi': self.epsn_1_4487_1480Fi,
            'CB-1480Fi': self.epsn_1_4487_1480Fi,
            'EB-1480Fi': self.epsn_1_4487_1480Fi,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LaserHours': {'Status': {}},
            'LightMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'SplitScreen': {'Status': {}},
            'SplitScreenSize': {'Status': {}},
            'SplitScreenSource': {'Parameters': ['Side'], 'Status': {}},
            'SplitScreenSwap': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(?:.{2}) (30)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'ASPECT=([3456]0)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CCAP=(00|11|12)\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=([0-9]{2})\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(rb'LAMP=(\d+)\r:'), self.__MatchLaserHours, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[0145])\r:'), self.__MatchLightMode, None)
            self.AddMatchString(re.compile(b'PWR=(0[0123459])\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(rb'VOL=(\d{1,3})\r:'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': '30',
            'Full': '40',
            'Zoom': '50',
            'Native': '60'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = 'ASPECT {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '30': 'Auto',
            '40': 'Full',
            '50': 'Zoom',
            '60': 'Native'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            AVMuteCmdString = 'MUTE {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAVMute')

    def UpdateAVMute(self, value, qualifier):

        AVMuteCmdString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'CC1': '11',
            'CC2': '12'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = 'CCAP {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '00': 'Off',
            '11': 'CC1',
            '12': 'CC2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            FreezeCmdString = 'FREEZE {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        if value in self.SetInput_ValueStateValues:
            InputCmdString = 'SOURCE {}\r'.format(self.SetInput_ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'SOURCE?\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.MatchInput_ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLaserHours(self, value, qualifier):

        LaserHoursCmdString = 'LAMP?\r'
        self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)

    def __MatchLaserHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LaserHours', value, None)

    def SetLightMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '00',
            'Quiet': '01',
            'Extended': '04',
            'Custom': '05'
        }

        if value in ValueStateValues:
            LightModeCmdString = 'LUMINANCE {}\r'.format(ValueStateValues[value])
            self.__SetHelper('LightMode', LightModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLightMode')

    def UpdateLightMode(self, value, qualifier):

        LightModeCmdString = 'LUMINANCE?\r'
        self.__UpdateHelper('LightMode', LightModeCmdString, value, qualifier)

    def __MatchLightMode(self, match, tag):

        ValueStateValues = {
            '00': 'Normal',
            '01': 'Quiet',
            '04': 'Extended',
            '05': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LightMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '03',
            'Up': '35',
            'Down': '36',
            'Left': '37',
            'Right': '38',
            'Enter': '16',
            'Esc': '05'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'KEY {}\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            PowerCmdString = 'PWR {}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'PWR?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '01': 'On',
            '00': 'Off',
            '04': 'Off',
            '05': 'Off',
            '09': 'Off',
            '02': 'Warming Up',
            '03': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        if value in ValueStateValues:
            SplitScreenCmdString = 'SPS 01 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSplitScreen')

    def SetSplitScreenSize(self, value, qualifier):

        ValueStateValues = {
            'Equal': '00',
            'Larger Left': '01',
            'Larger Right': '02'
        }

        if value in ValueStateValues:
            SplitScreenSizeCmdString = 'SPS 02 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('SplitScreenSize', SplitScreenSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSplitScreenSize')

    def SetSplitScreenSource(self, value, qualifier):

        SideStates = {
            'Left': '03',
            'Right': '04'
        }
        side = qualifier['Side']

        if side in SideStates and value in self.SetSplitScreenSource_ValueStateValues:
            SplitScreenSourceCmdString = 'SPS {} {}\r'.format(SideStates[side], self.SetSplitScreenSource_ValueStateValues[value])
            self.__SetHelper('SplitScreenSource', SplitScreenSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSplitScreenSource')

    def SetSplitScreenSwap(self, value, qualifier):

        SplitScreenSwapCmdString = 'SPS 05\r'
        self.__SetHelper('SplitScreenSwap', SplitScreenSwapCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeStateTable = {
            0: 0,
            1: 12,
            2: 24,
            3: 36,
            4: 48,
            5: 60,
            6: 73,
            7: 85,
            8: 97,
            9: 109,
            10: 121,
            11: 134,
            12: 146,
            13: 158,
            14: 170,
            15: 182,
            16: 195,
            17: 207,
            18: 219,
            19: 231,
            20: 243
        }

        if 0 <= value <= 20:
            VolumeCmdString = 'VOL {}\r'.format(VolumeStateTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode()) // 12

        if 0 <= value <= 20:
            self.WriteStatus('Volume', value, None)

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

    def __MatchError(self, match, tag):
        self.counter = 0

        self.Error(['An error occurred.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def epsn_1_4487_1480Fi(self):
        self.SetInput_ValueStateValues = {
            'Computer 1':           '10',
            'Computer 2':           '20',
            'HDMI 1':               '30',
            'HDMI 2':               'A0',
            'HDMI 3':               'C0',
            'Video':                '41',
            'USB Display':          '51',
            'USB 1':                '52',
            'USB 2':                '54',
            'LAN':                  '53',
            'Screen Mirroring 1':   '56',
            'Screen Mirroring 2':   '59'
        }

        self.MatchInput_ValueStateValues = {
            '10': 'Computer 1',
            '20': 'Computer 2',
            '30': 'HDMI 1',
            'A0': 'HDMI 2',
            'C0': 'HDMI 3',
            '41': 'Video',
            '51': 'USB Display',
            '52': 'USB 1',
            '54': 'USB 2',
            '53': 'LAN',
            '56': 'Screen Mirroring 1',
            '59': 'Screen Mirroring 2'
        }

        self.SetSplitScreenSource_ValueStateValues = {
            'Computer 1':           '10',
            'Computer 2':           '20',
            'HDMI 1':               '30',
            'HDMI 2':               'A0',
            'HDMI 3':               'C0',
            'Video':                '41',
            'USB Display':          '51',
            'USB 1':                '52',
            'USB 2':                '54',
            'LAN':                  '53',
            'Screen Mirroring 1':   '56',
            'Screen Mirroring 2':   '59'
        }




    def epsn_1_4487_1485Fi(self):
        self.SetInput_ValueStateValues = {
            'Computer 1':           '10',
            'Computer 2':           '20',
            'HDMI 1':               '30',
            'HDMI 2':               'A0',
            'HDMI 3':               'C0',
            'Video':                '41',
            'USB Display':          '51',
            'USB 1':                '52',
            'USB 2':                '54',
            'LAN':                  '53',
            'HDBaseT':              '80',
            'Screen Mirroring 1':   '56',
            'Screen Mirroring 2':   '59'
        }

        self.MatchInput_ValueStateValues = {
            '10': 'Computer 1',
            '20': 'Computer 2',
            '30': 'HDMI 1',
            'A0': 'HDMI 2',
            'C0': 'HDMI 3',
            '41': 'Video',
            '51': 'USB Display',
            '52': 'USB 1',
            '54': 'USB 2',
            '53': 'LAN',
            '80': 'HDBaseT',
            '56': 'Screen Mirroring 1',
            '59': 'Screen Mirroring 2'
        }

        self.SetSplitScreenSource_ValueStateValues = {
            'Computer 1':           '10',
            'Computer 2':           '20',
            'HDMI 1':               '30',
            'HDMI 2':               'A0',
            'HDMI 3':               'C0',
            'Video':                '41',
            'USB Display':          '51',
            'USB 1':                '52',
            'USB 2':                '54',
            'LAN':                  '53',
            'HDBaseT':              '80',
            'Screen Mirroring 1':   '56',
            'Screen Mirroring 2':   '59'
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
