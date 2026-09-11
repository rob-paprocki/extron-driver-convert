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
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'DLA-RS6710U': self.jvc_1_1878_other,
            'DLA-RS49U': self.jvc_1_1878_49,
            'DLA-RS57U': self.jvc_1_1878_other,
            'DLA-RS4910U': self.jvc_1_1878_49,
            'DLA-RS67U': self.jvc_1_1878_other,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'EcoMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            }

        self.Init_Flag = False


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x40\x89\x01\x50\x57([\x30-\x34])\x0A'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x40\x89\x01\x49\x50(\x36|\x37)\x0A'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x40\x89\x01\x49\x53\x41\x53([\x30-\x35])\x0A'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x40\x89\x01\x46\x55\x45\x4D([\x30-\x31])\x0A'), self.__MatchEcoMode, None)
            self.AddMatchString(re.compile(b'\x40\x89\x01\x50\x4D\x4C\x50([\x30-\x31])\x0A'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\x40\x89\x01\x50\x4D\x50\x4D([\x30-\x31][\x30-\x46])\x0A'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'PJ_OK'), self.__MatchOnConnectedString, None)
            self.AddMatchString(re.compile(b'PJACK'), self.__MatchReceive, None)

    def __MatchOnConnectedString(self, match, tag):

        self.Send('PJREQ')

    def __MatchReceive(self, match, tag):

        value = match.group(0).decode()
        if value == 'PJACK':
            self.Init_Flag = True
            self.UpdatePower( None, None)
        else:
            self.Init_Flag = False
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'  : b'\x30', 
            '16:9' : b'\x31', 
            'Zoom' : b'\x32', 
            'Auto' : b'\x33', 
            'Just' : b'\x34', 
            'Full' : b'\x35'
        }

        AspectRatioCmdString = b''.join([b'\x21\x89\x01\x49\x53\x41\x53', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x3F\x89\x01\x49\x53\x41\x53\x0A'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x30' : '4:3',
            b'\x31' : '16:9',
            b'\x32' : 'Zoom',
            b'\x33' : 'Auto',
            b'\x34' : 'Just',
            b'\x35' : 'Full'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x21\x89\x01\x52\x43\x37\x33\x37\x32\x0A'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x31', 
            'Off' : b'\x30'
        }

        EcoModeCmdString = b''.join([b'\x21\x89\x01\x46\x55\x45\x4D', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        EcoModeCmdString = b'\x3F\x89\x01\x46\x55\x45\x4D\x0A'
        self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def __MatchEcoMode(self, match, tag):

        ValueStateValues = {
            b'\x31' : 'On',
            b'\x30' : 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('EcoMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1' : b'\x36', 
            'HDMI 2' : b'\x37'
        }

        InputCmdString = b''.join([b'\x21\x89\x01\x49\x50', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x3F\x89\x01\x49\x50\x0A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x36' : 'HDMI 1', 
            b'\x37' : 'HDMI 2'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : b'\x30', 
            'High'   : b'\x31'
        }

        LampModeCmdString = b''.join([b'\x21\x89\x01\x50\x4D\x4C\x50', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\x3F\x89\x01\x50\x4D\x4C\x50\x0A'
        self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            b'\x30' : 'Normal',
            b'\x31' : 'High'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('LampMode', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x30\x31', 
            'Down'  : b'\x30\x32', 
            'Right' : b'\x33\x34', 
            'Left'  : b'\x33\x36', 
            'Ok'    : b'\x32\x46', 
            'Menu'  : b'\x32\x35', 
            'Back'  : b'\x30\x33'
        }

        MenuNavigationCmdString = b''.join([b'\x21\x89\x01\x52\x43\x37\x33', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        PictureModeCmdString = b''.join([b'\x21\x89\x01\x50\x4D\x50\x4D', self.PictureModeValues[value], b'\x0A'])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x3F\x89\x01\x50\x4D\x50\x4D\x0A'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        if match.group(1) in self.PictureModeNames:
            value = self.PictureModeNames[match.group(1)]
            self.WriteStatus('PictureMode', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x31', 
            'Off' : b'\x30', 
        }

        PowerCmdString = b''.join([b'\x21\x89\x01\x50\x57', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

            
        PowerCmdString = b'\x3F\x89\x01\x50\x57\x0A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x31' : 'On', 
            b'\x30' : 'Off', 
            b'\x32' : 'Cooling Down', 
            b'\x33' : 'Reserved', 
            b'\x34' : 'Error'
        }

        
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.Init_Flag or 'Serial' in self.ConnectionType:
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

        if 'Serial' not in self.ConnectionType:
            self.Init_Flag = False 
    def jvc_1_1878_other(self):


        self.PictureModeValues = {
            'Film'      : b'\x30\x30', 
            'Cinema'    : b'\x30\x31', 
            'Animation' : b'\x30\x32', 
            'Natural'   : b'\x30\x33', 
            'Stage'     : b'\x30\x34', 
            'THX'       : b'\x30\x36', 
            '4K 50/60P' : b'\x30\x42', 
            'User 1'    : b'\x30\x43', 
            'User 2'    : b'\x30\x44', 
            'User 3'    : b'\x30\x45', 
            'User 4'    : b'\x30\x46', 
            'Photo'     : b'\x31\x32'
        }
        
        self.PictureModeNames = {
            b'\x30\x30' : 'Film', 
            b'\x30\x31' : 'Cinema', 
            b'\x30\x32' : 'Animation', 
            b'\x30\x33' : 'Natural', 
            b'\x30\x34' : 'Stage', 
            b'\x30\x36' : 'THX', 
            b'\x30\x42' : '4K 50/60P', 
            b'\x30\x43' : 'User 1', 
            b'\x30\x44' : 'User 2', 
            b'\x30\x45' : 'User 3', 
            b'\x30\x46' : 'User 4', 
            b'\x31\x32' : 'Photo'
        }
        


    def jvc_1_1878_49(self):


        self.PictureModeValues = {
            'Cinema'    : b'\x30\x31', 
            'Animation' : b'\x30\x32', 
            'Natural'   : b'\x30\x33', 
            'Stage'     : b'\x30\x34', 
            '4K 50/60P' : b'\x30\x42', 
            'User 1'    : b'\x30\x43', 
            'User 2'    : b'\x30\x44', 
            'User 3'    : b'\x30\x45', 
            'User 4'    : b'\x30\x46'
        }
        
        self.PictureModeNames = {
            b'\x30\x31' : 'Cinema', 
            b'\x30\x32' : 'Animation', 
            b'\x30\x33' : 'Natural', 
            b'\x30\x34' : 'Stage', 
            b'\x30\x42' : '4K 50/60P', 
            b'\x30\x43' : 'User 1', 
            b'\x30\x44' : 'User 2', 
            b'\x30\x45' : 'User 3', 
            b'\x30\x46' : 'User 4'
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

