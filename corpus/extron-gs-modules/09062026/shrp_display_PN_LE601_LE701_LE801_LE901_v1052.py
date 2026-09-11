from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'ATVChannelDirectCommand': { 'Status': {}},
            'AVMode': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DTVChannelAirCommand': { 'Status': {}},
            'DTVChannelCable1Command': { 'Status': {}},
            'DTVChannelCable2Command': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Side Bar (AV)'     : 'WIDE1   \r', 
            'S. Stretch (AV)'   : 'WIDE2   \r', 
            'Zoom (AV)'         : 'WIDE3   \r', 
            'Stretch (AV)'      : 'WIDE4   \r', 
            'Normal (PC)'       : 'WIDE5   \r', 
            'Dot by Dot (PC)'   : 'WIDE8   \r', 
            'Stretch (PC)'      : 'WIDE7   \r', 
            'Full Screen (AV)'  : 'WIDE9   \r', 
            'Auto'              : 'WIDE10  \r', 
            'Original'          : 'WIDE11  \r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Side Bar (AV)', 
            '2' : 'S. Stretch (AV)', 
            '3' : 'Zoom (AV)', 
            '4' : 'Stretch (AV)', 
            '5' : 'Normal (PC)', 
            '8' : 'Dot by Dot (PC)', 
            '7' : 'Stretch (PC)', 
            '9' : 'Full Screen (AV)', 
            '10' : 'Auto', 
            '11' : 'Original'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetATVChannelDirectCommand(self, value, qualifier):

        temp = value
        if temp:
            if 1 <= int(temp) <= 135:
                ATVChannelDirectCommandCmdString = 'DCCH{0} \r'.format(temp.zfill(3))
                self.__SetHelper('ATVChannelDirectCommand', ATVChannelDirectCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetATVChannelDirectCommand')
        else:
            self.Discard('Invalid Command for SetATVChannelDirectCommand')

    def SetAVMode(self, value, qualifier):

        ValueStateValues = {
            'Standard'        : 'AVMD1   \r', 
            'Movie'           : 'AVMD2   \r', 
            'User'            : 'AVMD4   \r', 
            'Dynamic (Fixed)' : 'AVMD5   \r', 
            'Dynamic'         : 'AVMD6   \r', 
            'PC'              : 'AVMD7   \r'
        }

        AVModeCmdString = ValueStateValues[value]
        self.__SetHelper('AVMode', AVModeCmdString, value, qualifier)

    def UpdateAVMode(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Standard', 
            '2' : 'Movie', 
            '4' : 'User', 
            '5' : 'Dynamic (Fixed)', 
            '6' : 'Dynamic', 
            '7' : 'PC'
        }

        AVModeCmdString = 'AVMD????\r'
        res = self.__UpdateHelper('AVMode', AVModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AVMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mode: Invalid/Unexpected Response'])

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 'CHUP1   \r', 
            'Down'  : 'CHDW1   \r'
        }

        ChannelStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'CLCP1   \r'
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
    def SetDTVChannelAirCommand(self, value, qualifier):

        temp = value
        if temp:
            if 100 <= int(temp) <= 9999:
                DTVChannelAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(temp))
                self.__SetHelper('DTVChannelAirCommand', DTVChannelAirCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTVChannelAirCommand')

    def SetDTVChannelCable1Command(self, value, qualifier):

        temp = value
        if temp:
            if temp.__contains__('.'):
                major, minor = temp.split('.')
            else:   #if major is the only value
                major = temp
                minor = '0'
            if 1 <= int(major) <= 999 and 0 <= int(minor) <= 999:
                DTVChannelCableMajorCommandCmdString = 'DC2U{0:03d} \rDC2L{1:03d} \r'.format(int(major), int(minor))
                self.__SetHelper('DTVChannelCable1Command', DTVChannelCableMajorCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTVChannelCable1Command')
        else:
            self.Discard('Invalid Command for SetDTVChannelCable1Command')

    def SetDTVChannelCable2Command(self, value, qualifier):

        temp = value
        if temp:
            if 0 <= int(temp) <= 16383:
                DTVChannelCable2CommandCmdString = 'DC1{0:05d}\r'.format(int(temp))
                self.__SetHelper('DTVChannelCable2Command', DTVChannelCable2CommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTVChannelCable2Command')
        else:
            self.Discard('Invalid Command for SetDTVChannelCable2Command')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'    : 'IAVD1   \r', 
            'HDMI 2'    : 'IAVD2   \r', 
            'HDMI 3'    : 'IAVD3   \r', 
            'Video'     : 'IAVD4   \r', 
            'Component' : 'IAVD5   \r', 
            'PC'        : 'IAVD6   \r', 
            'TV'        : 'ITVD0   \r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1' : 'HDMI 1', 
            '2' : 'HDMI 2', 
            '3' : 'HDMI 3', 
            '4' : 'Video', 
            '5' : 'Component', 
            '6' : 'PC', 
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'      : 'RCKY38  \r', 
            'Enter'     : 'RCKY40  \r', 
            'Return'    : 'RCKY45  \r', 
            'Exit'      : 'RCKY46  \r', 
            'Up'        : 'RCKY41  \r', 
            'Down'      : 'RCKY42  \r', 
            'Left'      : 'RCKY43  \r', 
            'Right'     : 'RCKY44  \r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MUTE1   \r', 
            'Off' : 'MUTE2   \r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '2' : 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : 'POWR1   \r', 
            'Off'   : 'POWR0   \r'
        }

        PowerCmdString = PowerState[value]
        if value == 'On':
                self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            if 'Serial' in self.ConnectionType:
                self.__SetHelper('Power', 'RSPW1   \r', value, qualifier)
                self.__SetHelper('Power', PowerCmdString, value, qualifier)
            else:
                self.__SetHelper('Power', 'RSPW2   \r', value, qualifier)
                self.__SetHelper('Power', PowerCmdString, value, qualifier)            

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'VOLM{0:03d} \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except ValueError:
                self.Error(['Volume: Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                self.Error(['{0} Communication error or incorrect command'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            if command == 'Power':
                self.SendAndWait(commandstring, 3.0, deliTag=b'\r')
            else:
                self.Send(commandstring)
        else:
            if command == 'Power':
                res = self.SendAndWait(commandstring, 3.0, deliTag=b'\r')
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{0} Invalid/Unexpected Response'.format(command)])
            else:
                self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')              
            if not res:
                self.Error(['{0} Invalid/Unexpected Response'.format(command)])
            else:
                return self.__CheckResponseForErrors(command, res.decode())          
                     

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

