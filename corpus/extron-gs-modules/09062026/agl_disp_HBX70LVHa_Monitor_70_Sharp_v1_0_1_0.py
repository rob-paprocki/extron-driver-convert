from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
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
        self._DeviceID = '\x01'
        self.Models = {
            'HBX70LVHa': self.agl_10_1731_HBX,
            'Monitor 70 Sharp': self.agl_10_1731_70,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoAdjust': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PIPAdjust': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'SchemeSelection': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x41\x53\x50([\x00-\x03])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x4D\x55\x54([\x00-\x01])\x08'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x4D\x49\x4E([\x00\x01\x09\x0A\x0D])\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x50\x53\x43([\x00-\x04])\x08'), self.__MatchPIPAdjust, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x50\x49\x4E([\x00\x01\x09\x0A\x0D])\x08'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x50\x50\x4F([\x00-\x03])\x08'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x50\x4F\x57([\x00-\x01])\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x53\x43\x4D([\x00-\x04])\x08'), self.__MatchSchemeSelection, None)
            self.AddMatchString(re.compile(b'\x07[\x00-\x19]\x00\x56\x4F\x4C([\x00-\x64])\x08'), self.__MatchVolume, None)




    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '\x00'
        elif 1 <= int(value) <= 25:
            self._DeviceID = pack('>B', int(value)).decode()
        else:
            self.Error(['Device ID Out of Range'])
    def SetAspectRatio(self, value, qualifier):


        AspectRatioCmdString = '\x07' + self.DeviceID + '\x02\x41\x53\x50' + self.aspectValues[value] + '\x08'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\x07' + self.DeviceID + '\x01\x41\x53\x50\x08'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):


        value = self.aspectMatch[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'Off' : '\x00', 
            'On'  : '\x01'
        }

        AudioMuteCmdString = '\x07' + self.DeviceID + '\x02\x4D\x55\x54' + ValueStateValues[value] + '\x08'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '\x07' + self.DeviceID + '\x01\x4D\x55\x54\x08'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x00' : 'Off', 
            '\x01' : 'On'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoAdjust(self, value, qualifier):

        AutoAdjustCmdString = '\x07' + self.DeviceID + '\x02\x41\x44\x4A\x00\x08'
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)



    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '\x07' + self.DeviceID + '\x02\x52\x43\x55\x18\x08'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)



    def SetInput(self, value, qualifier):


        InputCmdString = '\x07' + self.DeviceID + '\x02\x4D\x49\x4E' + self.inputValues[value] + '\x08'
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x07' + self.DeviceID + '\x01\x4D\x49\x4E\x08'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):


        
        value = self.inputMatch[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : '\x00', 
            'Up'    : '\x02', 
            'Down'  : '\x03', 
            'Left'  : '\x04', 
            'Right' : '\x05', 
            'Enter' : '\x06', 
            'Exit'  : '\x07'
        }

        MenuNavigationCmdString = '\x07' + self.DeviceID + '\x02\x52\x43\x55' + ValueStateValues[value] + '\x08'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)



    def SetPIPAdjust(self, value, qualifier):

        ValueStateValues = {
            'Off'           : '\x00', 
            'Small'         : '\x01', 
            'Medium'        : '\x02', 
            'Large'         : '\x03', 
            'Side-by-Side'  : '\x04'
        }

        PIPAdjustCmdString = '\x07' + self.DeviceID + '\x02\x50\x53\x43' + ValueStateValues[value] + '\x08'
        self.__SetHelper('PIPAdjust', PIPAdjustCmdString, value, qualifier)
    def UpdatePIPAdjust(self, value, qualifier):

        PIPAdjustCmdString = '\x07' + self.DeviceID + '\x01\x50\x53\x43\x08'
        self.__UpdateHelper('PIPAdjust', PIPAdjustCmdString, value, qualifier)

    def __MatchPIPAdjust(self, match, tag):

        ValueStateValues = {
            '\x00' : 'Off', 
            '\x01' : 'Small', 
            '\x02' : 'Medium', 
            '\x03' : 'Large', 
            '\x04' : 'Side-by-Side'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPAdjust', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA'         : '\x00', 
            'Digital DVI' : '\x01', 
            'HDMI 1'      : '\x09', 
            'HDMI 2'      : '\x0A', 
            'Displayport' : '\x0D'
        }

        PIPInputCmdString = '\x07' + self.DeviceID + '\x02\x50\x49\x4E' + ValueStateValues[value] + '\x08'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '\x07' + self.DeviceID + '\x01\x50\x49\x4E\x08'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            '\x00' : 'VGA', 
            '\x01' : 'Digital DVI', 
            '\x09' : 'HDMI 1', 
            '\x0A' : 'HDMI 2', 
            '\x0D' : 'Displayport'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom-Left'  : '\x00', 
            'Bottom-Right' : '\x01', 
            'Top-Left'     : '\x02', 
            'Top-Right'    : '\x03'
        }

        PIPPositionCmdString = '\x07' + self.DeviceID + '\x02\x50\x50\x4F' + ValueStateValues[value] + '\x08'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = '\x07' + self.DeviceID + '\x01\x50\x50\x4F\x08'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            '\x00' : 'Bottom-Left', 
            '\x01' : 'Bottom-Right', 
            '\x02' : 'Top-Left', 
            '\x03' : 'Top-Right'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '\x07' + self.DeviceID + '\x02\x53\x57\x41\x00\x08'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)



    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off' : '\x00', 
            'On'  : '\x01'
        }

        PowerCmdString = '\x07' + self.DeviceID + '\x02\x50\x4F\x57' + ValueStateValues[value] + '\x08'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\x07' + self.DeviceID + '\x01\x50\x4F\x57\x08'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x00' : 'Off', 
            '\x01' : 'On'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetSchemeSelection(self, value, qualifier):

        ValueStateValues = {
            'User'   : '\x00', 
            'Sport'  : '\x01', 
            'Game'   : '\x02', 
            'Cinema' : '\x03', 
            'Vivid'  : '\x04'
        }

        SchemeSelectionCmdString = '\x07' + self.DeviceID + '\x02\x53\x43\x4D' + ValueStateValues[value] + '\x08'
        self.__SetHelper('SchemeSelection', SchemeSelectionCmdString, value, qualifier)
    def UpdateSchemeSelection(self, value, qualifier):

        SchemeSelectionCmdString = '\x07' + self.DeviceID + '\x01\x53\x43\x4D\x08'
        self.__UpdateHelper('SchemeSelection', SchemeSelectionCmdString, value, qualifier)

    def __MatchSchemeSelection(self, match, tag):

        ValueStateValues = {
            '\x00' : 'User', 
            '\x01' : 'Sport', 
            '\x02' : 'Game', 
            '\x03' : 'Cinema', 
            '\x04' : 'Vivid'
        }

        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SchemeSelection', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '\x07' + self.DeviceID + '\x02\x56\x4F\x4C' + pack('>B', value).decode() + '\x08'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\x07' + self.DeviceID + '\x01\x56\x4F\x4C\x08'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        
        value = unpack('>B', match.group(1))[0]
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Zoom In'  : '\x00', 
            'Zoom Out' : '\x01'
        }

        ZoomCmdString = '\x07' + self.DeviceID + '\x02\x5A\x4F\x4D' + ValueStateValues[value] + '\x08'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)



    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '\x00':
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

        

    def agl_10_1731_HBX(self):
        self.aspectValues = {
            'Native' : '\x00', 
            'Fill'   : '\x01', 
            'Pillar' : '\x02', 
            'Letter' : '\x03'
        }
        self.aspectMatch = {
            '\x00' : 'Native', 
            '\x01' : 'Fill', 
            '\x02' : 'Pillar', 
            '\x03' : 'Letter'
        }
        self.inputValues = {
            'VGA'         : '\x00', 
            'Digital DVI' : '\x01', 
            'HDMI 1'      : '\x09', 
            'HDMI 2'      : '\x0A', 
            'Displayport' : '\x0D'
        }
        self.inputMatch = {
            '\x00' : 'VGA', 
            '\x01' : 'Digital DVI', 
            '\x09' : 'HDMI 1', 
            '\x0A' : 'HDMI 2', 
            '\x0D' : 'Displayport'
        }
        

    def agl_10_1731_70(self):
        self.aspectValues = {
            'Fill'   : '\x01', 
            'Pillar' : '\x02', 
        }
        self.aspectMatch = {
            '\x01' : 'Fill', 
            '\x02' : 'Pillar', 
        }
        self.inputValues = {
            'VGA'         : '\x00', 
            'Digital DVI' : '\x01', 
            'HDMI 1'      : '\x09', 
            'Displayport' : '\x0D'
        }
        self.inputMatch = {
            '\x00' : 'VGA', 
            '\x01' : 'Digital DVI', 
            '\x09' : 'HDMI 1', 
            '\x0D' : 'Displayport'
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

