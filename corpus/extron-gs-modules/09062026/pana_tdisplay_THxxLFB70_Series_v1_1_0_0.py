from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
import binascii

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
        self.devicePassword  = 'panasonic'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }

        self.md5hash = ''
        self.Security = False

        if self.ConnectionType == 'Ethernet':
            self.AddMatchString(re.compile(b'PDPCONTROL 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PDPCONTROL 0\r'), self.__MatchNoAuthentication, None)


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02QAS:(ZOOM|FULL|JUST|NORM|ZOM2|ZOM3|SJST|SNOM|SFUL|14:9)\x03'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x02QAM:(0|1)\x03'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x02QMI:(HM1|HM2|SL1|S1A|S1B|VD1|YP1|DV1|PC1|DL1|MG1|NW1|MV1|WB1)\x03'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x02QSP:OSD(1|0)\x03'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x02QPC:MEN(STD|DYN|CNM)\x03'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x02QPW:(0|1)\x03'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x02QVM:(0|1)\x03'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\x02QAV:([0-9]{2})\x03'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(ERR[1-5]|ER401|PDPCONTROL ERRA)'), self.__MatchError, None)

    def __MatchAuthentication(self, match, tag):

        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = binascii.hexlify(code_hash.digest()).decode()
        self.Security = True

    def __MatchNoAuthentication(self, match, tag):
        self.Security = False

    def CommandStringBuild(self, command, commandstring):

        if self.ConnectionType == 'Serial':
            return commandstring
        else:
            if self.Security == True:
                commandstring = self.md5hash + commandstring + '\r'
            else:
                commandstring = commandstring + '\r'
            return commandstring

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Zoom 1': 'ZOOM',
            '16:9': 'FULL',
            'Just': 'JUST',
            '4:3': 'NORM',
            'Zoom 2': 'ZOM2',
            'Zoom 3': 'ZOM3',
            'Side cut Just': 'SJST',
            '4:3 Side cut': 'SNOM',
            '4:3 Full': 'SFUL',
            '14:9': '14:9'
        }

        self.__SetHelper('AspectRatio', '\x02DAM:{0}\x03'.format(States[value]), value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        self.__UpdateHelper('AspectRatio', '\x02QAS\x03', value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            'ZOOM': 'Zoom 1',
            'FULL': '16:9',
            'JUST': 'Just',
            'NORM': '4:3',
            'ZOM2': 'Zoom 2',
            'ZOM3': 'Zoom 3',
            'SJST': 'Side cut Just',
            'SNOM': '4:3 Side cut',
            'SFUL': '4:3 Full',
            '14:9': '14:9'
        }

        self.WriteStatus('AspectRatio', States[match.group(1).decode()], None)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '\x02AMT:1\x03',
            'Off': '\x02AMT:0\x03'
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '\x02QAM\x03', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '\x02OSP:ASUAUT\x03', value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'HDMI 1': 'IMS:HM1',
            'HDMI 2': 'IMS:HM2',
            'Slot': 'IMS:SL1',
            'Slot A': 'IMS:S1A',
            'Slot B': 'IMS:S1B',
            'Video': 'IMS:VD1',
            'Component': 'IMS:YP1',
            'PC': 'IMS:PC1',
            'DVI': 'IMS:DV1',
            'Digital Link': 'IMS:DL1',
            'Miracast': 'IMS:MG1',
            'Panasonic Application': 'IMS:NW1',
            'Memory Viewer': 'IMS:MV1',
            'Whiteboard': 'IMS:WB1'
        }

        self.__SetHelper('Input', '\x02{0}\x03'.format(States[value]), value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '\x02QMI\x03', value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            'HM1': 'HDMI 1',
            'HM2': 'HDMI 2',
            'SL1': 'Slot',
            'S1A': 'Slot A',
            'S1B': 'Slot B',
            'VD1': 'Video',
            'YP1': 'Component',
            'PC1': 'PC',
            'DV1': 'DVI',
            'DL1': 'Digital Link',
            'MG1': 'Miracast',
            'NW1': 'Panasonic Application',
            'MV1': 'Memory Viewer',
            'WB1': 'Whiteboard'
        }

        self.WriteStatus('Input', States[match.group(1).decode()], None)

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On': '\x02OSP:OSD1\x03',
            'Off': '\x02OSP:OSD0\x03',
            'Clear': '\x02VDO\x03'
        }

        self.__SetHelper('OnScreenDisplay', States[value], value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        self.__UpdateHelper('OnScreenDisplay', '\x02QSP:OSD\x03', value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('OnScreenDisplay', States[match.group(1).decode()], None)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Normal': '\x02VPC:MENSTD\x03',
            'Dynamic': '\x02VPC:MENDYN\x03',
            'Cinema': '\x02VPC:MENCNM\x03'
        }

        self.__SetHelper('PictureMode', States[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):
        self.__UpdateHelper('PictureMode', '\x02QPC:MEN\x03', value, qualifier)

    def __MatchPictureMode(self, match, tag):

        States = {
            'STD': 'Normal',
            'DYN': 'Dynamic',
            'CNM': 'Cinema'
        }

        self.WriteStatus('PictureMode', States[match.group(1).decode()], None)

    def SetPower(self, value, qualifier):

        States = {
            'On': '\x02PON\x03',
            'Off': '\x02POF\x03'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):
        self.__UpdateHelper('Power', '\x02QPW\x03', value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('VideoMute', '\x02VMT:{0}\x03'.format(States[value]), value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', '\x02QVM\x03', value, qualifier)

    def __MatchVideoMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('VideoMute', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 63:
            self.__SetHelper('Volume', '\x02AVL:{0:02d}\x03'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '\x02QAV\x03', value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode()), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = self.CommandStringBuild(command, commandstring)
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandstring = self.CommandStringBuild(command, commandstring)
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

        DEVICE_ERROR_CODES = {
                'ERR1'              : 'Undefined Control Command.',
                'ERR2'              : 'Out of Parameter Range.',
                'ERR3'              : 'Busy State or No-acceptable Period.',
                'ERR4'              : 'Timeout or No-acceptable Period.',
                'ERR5'              : 'Wrong Data Length.',
                'PDPCONTROL ERRA'   : 'Password Mismatch.',
                'ER401'             : 'Invalid Command Reply.'
            }
            
        if match.group(1).decode() in DEVICE_ERROR_CODES.keys():
            self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.md5hash = ''
        self.Security = False
    
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()