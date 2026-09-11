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
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DEnable': { 'Status': {}},
            '3DFormat': { 'Status': {}},
            '3DSyncDominance': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'Power': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ack 3d\.enable = (On|Off)\S*\r', re.IGNORECASE), self.__Match3DEnable, None)
            self.AddMatchString(re.compile(b'ack 3d\.format = (auto|seq|fpack|tab|sbs)\S*\r', re.IGNORECASE), self.__Match3DFormat, None)
            self.AddMatchString(re.compile(b'ack 3d\.dominance = (left|right)\S*\r', re.IGNORECASE), self.__Match3DSyncDominance, None)
            self.AddMatchString(re.compile(b'ack aspect\.ratio = ([0-4])\S*\r', re.IGNORECASE), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'ack freeze = (On|Off)\S*\r', re.IGNORECASE), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'ack input = ([0-9]+)\S*\r', re.IGNORECASE), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'ack lamp([1-4])\.hours = ([0-9]+):.*\r', re.IGNORECASE), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'ack pip\.input = ([0-7])\S*\r', re.IGNORECASE), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'ack pip\.mode = ([0-3])\S*\r', re.IGNORECASE), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'ack pip\.position = ([0-4])\S*\r', re.IGNORECASE), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'ack power = (on|off|standby)\S*\r', re.IGNORECASE), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'nack ([a-zA-z0-9 ]*)\S*\r', re.IGNORECASE), self.__MatchError, None)
    
    def Set3DEnable(self, value, qualifier):

        Enable3d_Values = {
            "Off" : "off" ,
            "On"  : "on" ,
        }
        
        CmdString = '*3d.enable = {0}\r'.format(Enable3d_Values[value])
        self.__SetHelper('3DEnable', CmdString, value, qualifier)

    def Update3DEnable(self, value, qualifier): 

        CmdString = '*3d.enable ?\r'
        self.__UpdateHelper('3DEnable', CmdString, value, qualifier)

    def __Match3DEnable(self, match, qualifier):

        Enable3d_State = {
            "off" : "Off" ,
            "on"  : "On" ,
        }

        temp_3d_val = match.group(1).decode()
        value = Enable3d_State[temp_3d_val.lower()]
        self.WriteStatus('3DEnable', value, None)

    def Set3DFormat(self, value, qualifier):

        Format_Values = {
            'Auto'           : '*3d.format = auto\r',
            'Frame Packing'  : '*3d.format = fpack\r',
            'Sequential'     : '*3d.format = seq\r',
            'Top and Bottom' : '*3d.format = tab\r',
            'Side by Side'   : '*3d.format = sbs\r'
        }
        
        CmdString = Format_Values[value]
        self.__SetHelper('3DFormat', CmdString, value, qualifier)

    def Update3DFormat(self, value, qualifier): 

        CmdString = '*3d.format ?\r'
        self.__UpdateHelper('3DFormat', CmdString, value, qualifier)

    def __Match3DFormat(self, match, qualifier):

        Format_State = {
            'auto'   : 'Auto',
            'fpack'  : 'Frame Packing',
            'seq'    : 'Sequential', 
            'tab'    : 'Top and Bottom',
            'sbs'    : 'Side by Side'  
        }

        value = Format_State[match.group(1).decode()]
        self.WriteStatus('3DFormat', value, None)

    def Set3DSyncDominance(self, value, qualifier):

        Dom_Values = {
            'Left'   : '*3d.dominance = left\r',
            'Right'  : '*3d.dominance = right\r',
        }
        
        CmdString = Dom_Values[value]
        self.__SetHelper('3DSyncDominance', CmdString, value, qualifier)

    def Update3DSyncDominance(self, value, qualifier): 

        CmdString = '*3d.dominance ?\r'
        self.__UpdateHelper('3DSyncDominance', CmdString, value, qualifier)

    def __Match3DSyncDominance(self, match, qualifier):

        Dom_State = {
            'left'   : 'Left',
            'right'  : 'Right',
        }


        value = Dom_State[match.group(1).decode()]
        self.WriteStatus('3DSyncDominance', value, None)

    def SetAspectRatio(self, value, qualifier):

        AR_Values = {
            'Source'           : '*aspect.ratio = 0\r',
            'Fill and Display' : '*aspect.ratio = 1\r',
            'Fill and Crop'    : '*aspect.ratio = 2\r',
            'Anamorphic'       : '*aspect.ratio = 3\r',
            'TheaterScope'     : '*aspect.ratio = 4\r'
        }
        
        CmdString = AR_Values[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier): 

        CmdString = '*aspect.ratio ?\r'
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, qualifier):

        AR_State = {
            '0'  : 'Source',
            '1'  : 'Fill and Display',
            '2'  : 'Fill and Crop', 
            '3'  : 'Anamorphic',
            '4'  : 'TheaterScope'  
        }

        value = AR_State[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetFocus(self, value, qualifier):

        Focus_Values = {
            'Near' : '*focus.near\r',
            'Far'  : '*focus.far\r',
        }
        
        CmdString = Focus_Values[value]
        self.__SetHelper('Focus', CmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        Freeze_Values = {
            "Off" : "off",
            "On"  : "on"
        }
                
        CmdString = '*freeze = {0}\r'.format(Freeze_Values[value])
        self.__SetHelper('Freeze', CmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier): 

        CmdString = '*freeze ?\r'
        self.__UpdateHelper('Freeze', CmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):


        Freeze_State = {
            "off" : "Off",
            "on"  : "On"
        }
        
        temp_freeze = match.group(1).decode()
        value = Freeze_State[temp_freeze.lower()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        Input_Values = {
            'CVBS 1'       : '*input = 0\r',
            'CVBS 2'       : '*input = 1\r',
            'S-Video'      : '*input = 2\r',
            'Component'    : '*input = 3\r',
            'VGA'          : '*input = 4\r',
            '3G-SDI'       : '*input = 5\r',
            'DVI'          : '*input = 6\r',
            'HDMI'         : '*input = 7\r',
            'Test Pattern' : '*input = 8\r',
            'Main/DVI'     : '*input = 9\r',
            'Sub/HDMI'     : '*input = 10\r',
            'Dual Pipe'    : '*input = 11\r',
        }        
        CmdString = Input_Values[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier): 

        CmdString = '*input ?\r'
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        Input_State = {
            '0'  : 'CVBS 1',  
            '1'  : 'CVBS 2',  
            '2'  : 'S-Video',  
            '3'  : 'Component',  
            '4'  : 'VGA',  
            '5'  : '3G-SDI',  
            '6'  : 'DVI',  
            '7'  : 'HDMI',
            '8'  : 'Test Pattern',
            '9'  : 'Main/DVI',  
            '10' : 'Sub/HDMI',
            '11' : 'Dual Pipe',
        }
        value = Input_State[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateLampUsage(self, value, qualifier): 

        lamp = qualifier['Lamp']
        if 0 < int(lamp) > 4:
            self.Discard('Invalid Command for UpdateLampUsage')
        else:
            LampUsageCmdString = '*lamp{0}.hours ?\r'.format(lamp)
            self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        lamp = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('LampUsage', value, {'Lamp': lamp})

    def SetPIPInput(self, value, qualifier):

        PIPIn_Values = {
            'CVBS 1'     : '*pip.input = 0\r',
            'CVBS 2'     : '*pip.input = 1\r',
            'S-Video'    : '*pip.input = 2\r',
            'Component'  : '*pip.input = 3\r',
            'VGA'        : '*pip.input = 4\r',
            '3G-SDI'     : '*pip.input = 5\r',
            'DVI'        : '*pip.input = 6\r',
            'HDMI'       : '*pip.input = 7\r',
        }
        
        CmdString = PIPIn_Values[value]
        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier): 

        CmdString = '*pip.input ?\r'
        self.__UpdateHelper('PIPInput', CmdString, value, qualifier)

    def __MatchPIPInput(self, match, qualifier):

        PIPIn_State = {
            '0'   : 'CVBS 1',
            '1'   : 'CVBS 2',
            '2'   : 'S-Video',
            '3'   : 'Component',
            '4'   : 'VGA',
            '5'   : '3G-SDI',
            '6'   : 'DVI',
            '7'   : 'HDMI',
        }
        value = PIPIn_State[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        PIPMode_Values = {
            'Off'  : '*pip.mode = 0\r',
            'PIP'  : '*pip.mode = 1\r',
            'PAP'  : '*pip.mode = 2\r',
            'POP'  : '*pip.mode = 3\r',
        }        
        CmdString = PIPMode_Values[value]
        self.__SetHelper('PIPMode', CmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier): 

        CmdString = '*pip.mode ?\r'
        self.__UpdateHelper('PIPMode', CmdString, value, qualifier)

    def __MatchPIPMode(self, match, qualifier):

        PIPMode_State = {
            '0'   : 'Off',
            '1'   : 'PIP',
            '2'   : 'PAP',
            '3'   : 'POP',
        }
        value = PIPMode_State[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        PIPPos_Values = {
            'Top Left'     : '*pip.position = 0\r',
            'Top Right'    : '*pip.position = 1\r',
            'Bottom Left'  : '*pip.position = 2\r',
            'Bottom Right' : '*pip.position = 3\r',
            'Custom'       : '*pip.position = 4\r',
        }        
        CmdString = PIPPos_Values[value]
        self.__SetHelper('PIPPosition', CmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier): 

        CmdString = '*pip.position ?\r'
        self.__UpdateHelper('PIPPosition', CmdString, value, qualifier)

    def __MatchPIPPosition(self, match, qualifier):

        PIPPos_State = {
            '0'   : 'Top Left',
            '1'   : 'Top Right',
            '2'   : 'Bottom Left',
            '3'   : 'Bottom Right',
            '4'   : 'Custom',            
        }
        value = PIPPos_State[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPower(self, value, qualifier):

        Power_Values = {
            "Off" : "off",
            "On"  : "on"
        }        

        CmdString = '*power = {0}\r'.format(Power_Values[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier): 

        CmdString = '*power ?\r'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, qualifier):

        Power_States = {
            "off" : "Off",
            "standby" : "Off",
            "on"  : "On"
        }
        temp_power = match.group(1).decode()
        value = Power_States[temp_power.lower()]
        self.WriteStatus('Power', value, None)

    def SetZoom(self, value, qualifier):

        Zoom_Values = {
            'In'     : '*zoom.in\r',
            'Out'    : '*zoom.out\r',
        }
        
        CmdString = Zoom_Values[value]
        self.__SetHelper('Zoom', CmdString, value, qualifier)

    def __MatchError(self, match, qualifier):
        self.counter = 0
        self.Error([match.group(1).decode()])

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

