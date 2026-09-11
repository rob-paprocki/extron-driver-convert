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

        self.Models = {
            'PowerLite 1985WU': self.epsn_1_209_1985WU,
            'EB-1985WU': self.epsn_1_209_1985WU,
            'CB-1985WU': self.epsn_1_209_1985WU,
            'EB-1980WU': self.epsn_1_209_Other,
            'PowerLite 1980WU': self.epsn_1_209_Other,
            'CB-1980WU': self.epsn_1_209_Other,
            'PowerLite 1975W': self.epsn_1_209_1985WU,
            'EB-1970W': self.epsn_1_209_1970W,
            'CB-1970W': self.epsn_1_209_1970W,
            'PowerLite 1970W': self.epsn_1_209_1970W,
            'EB-1975W': self.epsn_1_209_1985WU,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioVideoMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'SplitScreen': {'Status': {}},
            'SplitScreenInput': {'Parameters': ['Left or Right'], 'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=(00|[2-6]0|[023456]0 30)\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAudioVideoMute, None)
            self.AddMatchString(re.compile(b'CCAP=(00|11|12)\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=([0-6AF]{2})\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(0[0-1])\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,4})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(0[0-5])\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r:'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioControls = {
                                'Normal': '00',
                                '16:9': '20',
                                'Auto': '30',
                                'Full': '40',
                                'Zoom': '50',
                                'Real': '60'
                              }

        CommandString = 'ASPECT {0}\r'.format(AspectRatioControls[value])
        self.__SetHelper('AspectRatio', CommandString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CommandString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', CommandString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioNames = {
                             '00': 'Normal',
                             '20': '16:9',
                             '30': 'Auto',
                             '40': 'Full',
                             '50': 'Zoom',
                             '60': 'Real',
                             '00 30': 'Auto',
                             '20 30': 'Auto',
                             '30 30': 'Auto',
                             '40 30': 'Auto',
                             '50 30': 'Auto',
                             '60 30': 'Auto'
                           }

        value = AspectRatioNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioVideoMute(self, value, qualifier):

        AudioVideoMuteControls = {
                                   'On': 'ON',
                                   'Off': 'OFF'
                                 }

        CommandString = 'MUTE {0}\r'.format(AudioVideoMuteControls[value])
        self.__SetHelper('AudioVideoMute', CommandString, value, qualifier)

    def UpdateAudioVideoMute(self, value, qualifier):

        CommandString = 'MUTE?\r'
        self.__UpdateHelper('AudioVideoMute', CommandString, value, qualifier)

    def __MatchAudioVideoMute(self, match, tag):

        AudioVideoMuteNames = {
                                'ON': 'On',
                                'OFF': 'Off'
                              }

        value = AudioVideoMuteNames[match.group(1).decode()]
        self.WriteStatus('AudioVideoMute', value, None)

    def SetAutoImage(self, value, qualifier):

        CommandString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', CommandString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionControls = {
                                  'Off': '00',
                                  'CC1': '11',
                                  'CC2': '12'
                                }

        CommandString = 'CCAP {0}\r'.format(ClosedCaptionControls[value])
        self.__SetHelper('ClosedCaption', CommandString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        CommandString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', CommandString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionNames = {
                               '00': 'Off',
                               '11': 'CC1',
                               '12': 'CC2'
                             }

        value = ClosedCaptionNames[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeControls = {
                           'On': 'ON',
                           'Off': 'OFF'
                         }

        CommandString = 'FREEZE {0}\r'.format(FreezeControls[value])
        self.__SetHelper('Freeze', CommandString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        CommandString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', CommandString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeNames = {
                        'ON': 'On',
                        'OFF': 'Off'
                      }

        value = FreezeNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        CommandString = 'SOURCE {0}\r'.format(self.InputNameValues[value])
        self.__SetHelper('Input', CommandString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CommandString = 'SOURCE?\r'
        self.__UpdateHelper('Input', CommandString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeControls = {
                             'Normal': '00',
                             'Eco': '01'
                           }

        CommandString = 'LUMINANCE {0}\r'.format(LampModeControls[value])
        self.__SetHelper('LampMode', CommandString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        CommandString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', CommandString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeNames = {
                          '00': 'Normal',
                          '01': 'Eco'
                        }

        value = LampModeNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        CommandString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', CommandString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('LampUsage', value, None)

    def SetPower(self, value, qualifier):

        PowerControls = {
                          'On': 'ON',
                          'Off': 'OFF'
                        }

        CommandString = 'PWR {0}\r'.format(PowerControls[value])
        self.__SetHelper('Power', CommandString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CommandString = 'PWR?\r'
        self.__UpdateHelper('Power', CommandString, value, qualifier)
        
    def __MatchPower(self, match, tag):

        PowerControlNames = {
                              '00': 'Off',
                              '01': 'On',
                              '02': 'Warming',
                              '03': 'Cooling',
                              '04': 'Off',
                              '05': 'Abnormal Standby'
                            }

        value = PowerControlNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSplitScreen(self, value, qualifier):

        ValueStateValues = {
            'On': 'SPS 01 01\r',
            'Off': 'SPS 01 00\r',
            'Left Screen Zoom': 'SPS 02 01\r',
            'Right Screen Zoom': 'SPS 02 02\r',
            'Equal Screen Size': 'SPS 02 00\r',
            'Screen Swap': 'SPS 05\r'
        }

        SplitScreenCmdString = ValueStateValues[value]
        self.__SetHelper('SplitScreen', SplitScreenCmdString, value, qualifier)

    def SetSplitScreenInput(self, value, qualifier):

        LeftorRightStates = {
            'Left': 'SPS 03 {0}\r',
            'Right': 'SPS 04 {0}\r'
        }

        SplitScreenInputCmdString = LeftorRightStates[qualifier['Left or Right']].format(self.InputNameValues[value])
        self.__SetHelper('SplitScreenInput', SplitScreenInputCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
                              'Min': 0,
                              'Max': 20
                            }

        Volume = {
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

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            CommandString = 'VOL {0}\r'.format(Volume[value])
            self.__SetHelper('Volume', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CommandString = 'VOL?\r'
        self.__UpdateHelper('Volume', CommandString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(int(match.group(1).decode()) / 12)
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

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

        self.Error(['An error Occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
    def epsn_1_209_1970W(self):        

        self.InputNameValues = {
            'Input 1 RGB (Analog)'       : '11', 
            'Input 1 Component'          : '14', 
            'Input 2 RGB (Analog)'       : '21', 
            'Input 2 Component'          : '24', 
            'Input 3 HDMI 1'             : '30', 
            'Video (RCA)'                : '41', 
            'USB Display'                : '51', 
            'USB'                        : '52', 
            'LAN'                        : '53', 
            'HDMI 2'                     : 'A0', 
            'Auto 1'                     : '1F', 
            'Auto 2'                     : '2F', 
        }

        self.InputStateValues = {
            '11' : 'Input 1 RGB (Analog)', 
            '14' : 'Input 1 Component', 
            '21' : 'Input 2 RGB (Analog)', 
            '24' : 'Input 2 Component', 
            '30' : 'Input 3 HDMI 1', 
            '41' : 'Video  (RCA)', 
            '51' : 'USB Display', 
            '52' : 'USB', 
            '53' : 'LAN', 
            'A0' : 'HDMI 2', 
            '1F' : 'Auto 1', 
            '2F' : 'Auto 2', 
        }
        
    def epsn_1_209_1985WU(self):

        self.InputNameValues = {
            'Input 1 D-Sub'               : '10',
            'Input 1 RGB (Analog)'        : '11',
            'Input 1 Component'           : '14',
            'Input 2 D-Sub'               : '20',
            'Input 2 RGB (Analog)'        : '21',
            'Input 2 Component'           : '24',
            'HDMI 1'                      : '30',
            'Video'                       : '40',
            'Video (RCA)'                 : '41',
            'USB Display'                 : '51',
            'USB'                         : '52',
            'LAN'                         : '53',
            'Screen Mirroring'            : '56',
            'HDMI 2'                      : 'A0',
        }

        self.InputStateValues = {
            '10' : 'Input 1 D-Sub',
            '11' : 'Input 1 RGB (Analog)',
            '14' : 'Input 1 Component',
            '20' : 'Input 2 D-Sub',
            '21' : 'Input 2 RGB (Analog)',
            '24' : 'Input 2 Component',
            '30' : 'HDMI 1',
            '40' : 'Video',
            '41' : 'Video (RCA)',
            '51' : 'USB Display',
            '52' : 'USB',
            '53' : 'LAN',
            '56' : 'Screen Mirroring',
            'A0' : 'HDMI 2',
        }
        
    def epsn_1_209_Other(self):

        self.InputNameValues = {
            'Input 1 D-Sub'               : '10',
            'Input 1 RGB (Analog)'        : '11',
            'Input 1 Component'           : '14',
            'Input 2 D-Sub'               : '20',
            'Input 2 RGB (Analog)'        : '21',
            'Input 2 Component'           : '24',
            'Input 3 HDMI 1'              : '30',
            'Input 3 D-RGB'               : '31',
            'Input 3 RGB-Video'           : '33',
            'Input 3 YCbCr'               : '34',
            'Input 3 YPbPr'               : '35',
            'Video'                       : '40',
            'Video (RCA)'                 : '41',
            'USB Display'                 : '51',
            'USB'                         : '52',
            'LAN'                         : '53',
            'DVI/HDMI Expanded HDMI 2'    : 'A0',
            'DVI/HDMI Expanded D-RGB'     : 'A1',
            'DVI/HDMI Expanded RGB-Video' : 'A3',
            'DVI/HDMI Expanded YCbCr'     : 'A4',
            'DVI/HDMI Expanded YPbPr'     : 'A5'
        }

        self.InputStateValues = {
            '10' : 'Input 1 D-Sub',
            '11' : 'Input 1 RGB (Analog)',
            '14' : 'Input 1 Component',
            '20' : 'Input 2 D-Sub',
            '21' : 'Input 2 RGB (Analog)',
            '24' : 'Input 2 Component',
            '30' : 'Input 3 HDMI 1',
            '31' : 'Input 3 D-RGB',
            '33' : 'Input 3 RGB-Video',
            '34' : 'Input 3 YCbCr',
            '35' : 'Input 3 YPbPr',
            '40' : 'Video',
            '41' : 'Video (RCA)',
            '51' : 'USB Display',
            '52' : 'USB',
            '53' : 'LAN',
            'A0' : 'DVI/HDMI Expanded HDMI 2',
            'A1' : 'DVI/HDMI Expanded D-RGB',
            'A3' : 'DVI/HDMI Expanded RGB-Video',
            'A4' : 'DVI/HDMI Expanded YCbCr',
            'A5' : 'DVI/HDMI Expanded YPbPr'
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
