from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from functools import reduce
from operator import add

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
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'InputSignalDetect': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x15(\x0B|\x00|\x01|\x04|\x05|\x06|\x09|\x31|\x0C|\x0D|\x0E|\x0F)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x14(\x0C|\x21|\x23|\x31)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x08\x41\x0D[\x00\x01][\x00\x01][\x00\x01\x02]([\x00\x01])[\x00-\x7D][\x00\x01][\x00-\xFF]'), self.__MatchInputSignalDetect, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x63])\x03\x4E(\x15|\x5D|\x14|\x0D|\x3C|\x11|\x84|\x5C|\x12)([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)


    def GetDeviceID(self, value):
        if value == 'Broadcast':
            return b'\xFE'
        try:
            value = int(value)
        except ValueError:
            return 'Error'
        else:
            if value >= 0 and value <= 99:
                return value.to_bytes(1, 'big')
            return 'Error'

    def CheckSum(self, CmdString):
        Cks = reduce(add, CmdString) & 0xFF
        return CmdString.join([b'\xAA', Cks.to_bytes(1, 'big')])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\x01\x0B',
            'Auto Wide': b'\x01\x00',
            '16:9': b'\x01\x01',
            'Zoom': b'\x01\x04',
            'Zoom 1': b'\x01\x05',
            'Zoom 2': b'\x01\x06',
            'Just Scan (Fit Screen)': b'\x01\x09',
            'Wide Zoom': b'\x01\x31',
            'Wide Fit': b'\x01\x0C',
            'Custom': b'\x01\x0D',
            'Smart View 1': b'\x01\x0E',
            'Smart View 2': b'\x01\x0F'
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            AspectRatioCmdString = DeviceID.join([b'\x15', ValueStateValues[value]])
            AspectRatioCmdString = self.CheckSum(AspectRatioCmdString)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            AspectRatioCmdString = DeviceID.join([b'\x15', b'\x00'])
            AspectRatioCmdString = self.CheckSum(AspectRatioCmdString)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x0B': '4:3',
            b'\x00': 'Auto Wide',
            b'\x01': '16:9',
            b'\x04': 'Zoom',
            b'\x05': 'Zoom 1',
            b'\x06': 'Zoom 2',
            b'\x09': 'Just Scan (Fit Screen)',
            b'\x31': 'Wide Zoom',
            b'\x0C': 'Wide Fit',
            b'\x0D': 'Custom',
            b'\x0E': 'Smart View 1',
            b'\x0F': 'Smart View 2'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            AutoImageCmdString = DeviceID.join([b'\x3D', b'\x01\x00'])
            AutoImageCmdString = self.CheckSum(AutoImageCmdString)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x01',
            'Off': b'\x01\x00',
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            ExecutiveModeCmdString = DeviceID.join([b'\x5D', ValueStateValues[value]])
            ExecutiveModeCmdString = self.CheckSum(ExecutiveModeCmdString)
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            ExecutiveModeCmdString = DeviceID.join([b'\x5D', b'\x00'])
            ExecutiveModeCmdString = self.CheckSum(ExecutiveModeCmdString)
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': b'\x01\x0C',
            'HDMI 1': b'\x01\x21',
            'HDMI 2': b'\x01\x23',
            'HDMI 3': b'\x01\x31'
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            InputCmdString = DeviceID.join([b'\x14', ValueStateValues[value]])
            InputCmdString = self.CheckSum(InputCmdString)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            InputCmdString = DeviceID.join([b'\x14', b'\x00'])
            InputCmdString = self.CheckSum(InputCmdString)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x0C': 'AV',
            b'\x21': 'HDMI 1',
            b'\x23': 'HDMI 2',
            b'\x31': 'HDMI 3'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Input', value, qualifier)

    def UpdateInputSignalDetect(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            InputSignalDetectCmdString = DeviceID.join([b'\x0D', b'\x00'])
            InputSignalDetectCmdString = self.CheckSum(InputSignalDetectCmdString)
            self.__UpdateHelper('InputSignalDetect', InputSignalDetectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalDetect')

    def __MatchInputSignalDetect(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Present',
            b'\x01': 'Not Present'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('InputSignalDetect', value, qualifier)


    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x01',
            'Off': b'\x01\x00'
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            PIPModeCmdString = DeviceID.join([b'\x3C', ValueStateValues[value]])
            PIPModeCmdString = self.CheckSum(PIPModeCmdString)
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            PIPModeCmdString = DeviceID.join([b'\x3C', b'\x00'])
            PIPModeCmdString = self.CheckSum(PIPModeCmdString)
            self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPMode')

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('PIPMode', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x01',
            'Off': b'\x01\x00'
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            PowerCmdString = DeviceID.join([b'\x11', ValueStateValues[value]])
            PowerCmdString = self.CheckSum(PowerCmdString)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            PowerCmdString = DeviceID.join([b'\x11', b'\x00'])
            PowerCmdString = self.CheckSum(PowerCmdString)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        DeviceID = match.group(1)
        qualifier = {'Device ID': str(ord(DeviceID))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Power', value, qualifier)

    def SetVideoWall(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x01',
            'Off': b'\x01\x00'
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            VideoWallCmdString = DeviceID.join([b'\x84', ValueStateValues[value]])
            VideoWallCmdString = self.CheckSum(VideoWallCmdString)
            self.__SetHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWall')

    def UpdateVideoWall(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            VideoWallCmdString = DeviceID.join([b'\x84', b'\x00'])
            VideoWallCmdString = self.CheckSum(VideoWallCmdString)
            self.__UpdateHelper('VideoWall', VideoWallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWall')

    def __MatchVideoWall(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('VideoWall', value, qualifier)

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x01\x01',
            'Natural': b'\x01\x00'
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            VideoWallModeCmdString = DeviceID.join([b'\x5C', ValueStateValues[value]])
            VideoWallModeCmdString = self.CheckSum(VideoWallModeCmdString)
            self.__SetHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallMode')

    def UpdateVideoWallMode(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            VideoWallModeCmdString = DeviceID.join([b'\x5C', b'\x00'])
            VideoWallModeCmdString = self.CheckSum(VideoWallModeCmdString)
            self.__UpdateHelper('VideoWallMode', VideoWallModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallMode')

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Full',
            b'\x00': 'Natural'
        }
        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('VideoWallMode', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error' and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = DeviceID.join([b'\x12', value.to_bytes(1, 'big')])
            VolumeCmdString = self.CheckSum(VolumeCmdString)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DeviceID = self.GetDeviceID(qualifier['Device ID'])
        if DeviceID != 'Error':
            VolumeCmdString = DeviceID.join([b'\x12', b'\x00'])
            VolumeCmdString = self.CheckSum(VolumeCmdString)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = {'Device ID': str(ord(match.group(1)))}
        value = ord(match.group(2))
        self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif qualifier['Device ID'] == 'Broadcast':
            self.Discard('Inappropriate Command {}. Qualifier Broadcast set to Broadcast does not support status'.format(command))
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        Commands = {
            b'\x15': 'Aspect Ratio',
            b'\x5D': 'Executive Mode',
            b'\x14': 'Input',
            b'\x0D': 'Input Signal Detect',
            b'\x3C': 'PIP Mode',
            b'\x11': 'Power',
            b'\x84': 'Video Wall',
            b'\x5C': 'Video Wall Mode',
            b'\x12': 'Volume',
        }
        self.Error(['{}: Error number {} occured on device with ID {}.'.format(Commands[match.group(2)],ord(match.group(3)),ord(match.group(1)))])

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

