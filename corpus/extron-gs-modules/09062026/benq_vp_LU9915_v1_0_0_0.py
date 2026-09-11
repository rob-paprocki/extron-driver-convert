from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from itertools import cycle

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
            '3DFormat': { 'Status': {}},
            '3DInvert': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DLPLink': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }


        self.queryList = []
        self.firstPower = True
        self.secondPower = False
        self.qcycle = []





                    

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*ASP=(4:3|16:9|16:10|AUTO|REAL|THEA|5:4|1.88|2.35)#'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*DLPLINK=(ON|OFF)#'), self.__MatchDLPLink, None)
            self.AddMatchString(re.compile(b'\*FREEZE=(ON|OFF)#'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*SOUR=(RGB|RGB2|DVID|HDMI|DP|SDI|HDBASET)#'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*LAMPM=(LNOR|ECO|CUST)#'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'\*LTIM=(\d+)#'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'\*APPMOD=(PRESET|BRIGHT|CINE|DICOM|VIVID)#'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\*PSOUR=(RGB|RGB2|DVID|HDMI|DP|SDI|HDBASET)#'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\*POW=(ON|OFF)#'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*BLANK=(ON|OFF)#'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'(Illegal format|Block item|Unsupported item)'), self.__MatchError, None)
    def Set3DFormat(self, value, qualifier):

        ValueStateValues = {
            'Off'              : '\r*3d=off#\r', 
            'Auto'             : '\r*3d=auto#\r', 
            'Side by Side'     : '\r*3d=sbs#\r', 
            'Top Bottom'       : '\r*3d=tb#\r', 
            'Frame Sequential' : '\r*3d=fs#\r'
        }

        FormatCmdString = ValueStateValues[value]
        self.__SetHelper('3DFormat', FormatCmdString, value, qualifier)
    def Set3DInvert(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\r*3d=iv#\r', 
            'Off' : '\r*3d=da#\r'
        }

        InvertCmdString = ValueStateValues[value]
        self.__SetHelper('3DInvert', InvertCmdString, value, qualifier)
    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3'          : '\r*asp=4:3#\r', 
            '16:9'         : '\r*asp=16:9#\r', 
            '16:10'        : '\r*asp=16:10#\r', 
            'Auto'         : '\r*asp=AUTO#\r', 
            'Real'         : '\r*asp=REAL#\r', 
            'Theaterscope' : '\r*asp=THEA#\r', 
            '5:4'          : '\r*asp=5:4#\r', 
            '1.88'         : '\r*asp=1.88#\r', 
            '2.35'         : '\r*asp=2.35#\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        if 'AspectRatio' not in self.queryList:
            self.queryList.append('AspectRatio')
            self.queryList.append('Power')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '4:3'   : '4:3', 
            '16:9'  : '16:9', 
            '16:10' : '16:10', 
            'AUTO'  : 'Auto', 
            'REAL'  : 'Real', 
            'THEA'  : 'Theaterscope', 
            '5:4'   : '5:4', 
            '1.88'  : '1.88', 
            '2.35'  : '2.35'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetDLPLink(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\r*dlplink=on#\r', 
            'Off' : '\r*dlplink=off#\r'
        }

        DLPLinkCmdString = ValueStateValues[value]
        self.__SetHelper('DLPLink', DLPLinkCmdString, value, qualifier)
    def UpdateDLPLink(self, value, qualifier):

        if 'DLPLink' not in self.queryList:
            self.queryList.append('DLPLink')
            self.queryList.append('Power')

    def __MatchDLPLink(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DLPLink', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\r*freeze=on#\r', 
            'Off' : '\r*freeze=off#\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        if 'Freeze' not in self.queryList:
            self.queryList.append('Freeze')
            self.queryList.append('Power')

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1/YPbPr 1' : '\r*sour=RGB#\r', 
            'Computer 2/YPbPr 2' : '\r*sour=RGB2#\r', 
            'DVI-D'              : '\r*sour=dvid#\r', 
            'HDMI'               : '\r*sour=hdmi#\r', 
            'DisplayPort'        : '\r*sour=dp#\r', 
            '3G-SDI'             : '\r*sour=sdi#\r', 
            'HDBaseT'            : '\r*sour=hdbaset#\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        if 'Input' not in self.queryList:
            self.queryList.append('Input')
            self.queryList.append('Power')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'RGB'     : 'Computer 1/YPbPr 1', 
            'RGB2'    : 'Computer 2/YPbPr 2', 
            'DVID'    : 'DVI-D', 
            'HDMI'    : 'HDMI', 
            'DP'      : 'DisplayPort', 
            'SDI'     : '3G-SDI', 
            'HDBASET' : 'HDBaseT'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal' : '\r*lampm=lnor#\r', 
            'Eco'    : '\r*lampm=eco#\r', 
            'Custom' : '\r*lampm=cust#\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        if 'LampMode' not in self.queryList:
            self.queryList.append('LampMode')
            self.queryList.append('Power')

    def __MatchLampMode(self, match, tag):

        ValueStateValues = {
            'LNOR' : 'Normal', 
            'ECO'  : 'Eco', 
            'CUST' : 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        if 'LampUsage' not in self.queryList:
            self.queryList.append('LampUsage')
            self.queryList.append('Power')

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu On'  : '\r*menu=on#\r', 
            'Menu Off' : '\r*menu=off#\r', 
            'Up'       : '\r*up#\r', 
            'Down'     : '\r*down#\r', 
            'Right'    : '\r*right#\r', 
            'Left'     : '\r*left#\r', 
            'Enter'    : '\r*enter#\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation' : '\r*appmod=preset#\r', 
            'Bright'       : '\r*appmod=bright#\r', 
            'Cinema'       : '\r*appmod=cine#\r', 
            'DICOM SIM'    : '\r*appmod=dicom#\r', 
            'Vivid'        : '\r*appmod=vivid#\r'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def UpdatePictureMode(self, value, qualifier):

        if 'PictureMode' not in self.queryList:
            self.queryList.append('PictureMode')
            self.queryList.append('Power')

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'PRESET' : 'Presentation', 
            'BRIGHT' : 'Bright', 
            'CINE'   : 'Cinema', 
            'DICOM'  : 'DICOM SIM', 
            'VIVID'  : 'Vivid'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1/YPbPr 1' : '\r*psour=RGB\r', 
            'Computer 2/YPbPr 2' : '\r*psour=RGB2\r', 
            'DVI-D'              : '\r*psour=dvid#\r', 
            'HDMI'               : '\r*psour=hdmi#\r', 
            'DisplayPort'        : '\r*psour=dp#\r', 
            '3G-SDI'             : '\r*psour=sdi#\r', 
            'HDBaseT'            : '\r*psour=hdbaset#\r'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
    def UpdatePIPInput(self, value, qualifier):

        if 'PIPInput' not in self.queryList:
            self.queryList.append('PIPInput')
            self.queryList.append('Power')

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            'RGB'     : 'Computer 1/YPbPr 1', 
            'RGB2'    : 'Computer 2/YPbPr 2', 
            'DVID'    : 'DVI-D', 
            'HDMI'    : 'HDMI', 
            'DP'      : 'DisplayPort', 
            'SDI'     : '3G-SDI', 
            'HDBASET' : 'HDBaseT'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\r*pip=on#\r', 
            'Off' : '\r*pip=off#\r'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left'     : '\r*pippos=tl#\r', 
            'Top Right'    : '\r*pippos=tr#\r', 
            'Bottom Left'  : '\r*pippos=bl#\r', 
            'Bottom Right' : '\r*pippos=br#\r', 
            'PBP'          : '\r*pippos=pbp#\r'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\r*pow=on#\r', 
            'Off' : '\r*pow=off#\r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        CommandDictionary = {
            'AspectRatio' : '\r*asp=?#\r',      
            'DLPLink'     : '\r*dlplink=?#\r',     
            'Freeze'      : '\r*freeze=?#\r',   
            'Input'       : '\r*sour=?#\r',     
            'LampMode'    : '\r*lampm=?#\r',    
            'LampUsage'   : '\r*ltim=?#\r',     
            'PictureMode' : '\r*appmod=?#\r',   
            'PIPInput'    : '\r*psour=?#\r',
            'Power'       : '\r*pow=?#\r',      
            'VideoMute'   : '\r*blank=?#\r',     
            }

        if self.firstPower:
            self.queryList.append('Power')
            current_command = 'Power'
            self.firstPower = False
            self.secondPower = True
        elif self.secondPower:
            current_command = 'Power'
            self.qcycle = cycle(self.queryList)
            self.secondPower = False
        elif self.ReadStatus('Power', qualifier) in ['Off', None]:
            current_command = 'Power'
        else:
            current_command = next(self.qcycle)

        if current_command == 'Power':

            self.__UpdateHelper(current_command, CommandDictionary[current_command], value, qualifier)
        else:
            self.__UpdateHelper(current_command, CommandDictionary[current_command], value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)


    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\r*blank=on#\r', 
            'Off' : '\r*blank=off#\r'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        if 'VideoMute' not in self.queryList:
            self.queryList.append('VideoMute')
            self.queryList.append('Power')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            'ON'  : 'On', 
            'OFF' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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

        value = match.group(0).decode()
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.queryList = []
        self.firstPower = True
        self.secondPower = False
        self.qcycle = []

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

