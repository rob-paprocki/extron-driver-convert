from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {
            '232-ATSC+': self.ctrs_8_51_0,
            '232-ATSC+1': self.ctrs_8_51_0,
            '232-ATSC+SDI': self.ctrs_8_51_SDI,
            '232-ATSC 4': self.ctrs_8_51_0,
            }
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ChannelDiscrete': { 'Status': {}},
            'ChannelStatus': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'ClosedCaptionChannel': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'MenuCall': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Output': { 'Status': {}},
            'Power': { 'Status': {}},
            'PreviousChannel': { 'Status': {}},
            'SetChannelDiscrete': { 'Status': {}},
            'TunerMode': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
        
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '>{0}KK=82\r'.format(self._DeviceID)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'Off' : 'X',
            'On'  : 'M'
            }
        AudioMuteCmdString = '>{0}V{1}\r'.format(self._DeviceID, AudioMuteStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateVolume(value, qualifier)

    def SetChannelDiscrete(self, value, qualifier):

        if value.find('-') != -1:
            SetChannelDiscreteCmdString = '>{0}TC={1}\r'.format(self._DeviceID, value.replace('-',':'))
        elif value.find('.') != -1:
            SetChannelDiscreteCmdString = '>{0}TC={1}\r'.format(self._DeviceID, value.replace('.',':'))
        else:
            SetChannelDiscreteCmdString = '>{0}TC={1}\r'.format(self._DeviceID, value)
        self.__SetHelper('ChannelDiscrete', SetChannelDiscreteCmdString, value, qualifier)

    def SetChannelStep(self, value, qualifier):

        ChannelStepValues = {
            'Up'   : 'U',
            'Down' : 'D'
            }
        ChannelStepCmdString = '>{0}T{1}\r'.format(self._DeviceID, ChannelStepValues[value])
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def UpdateChannelStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionValues = {
            'Off' : '0',
            'On'  : '1'
            }
        ClosedCaptionCmdString = '>{0}Q0={1}\r'.format(self._DeviceID, ClosedCaptionValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionNames = {
            '0' : 'Off',
            '1' : 'On'
            }
        ClosedCaptionChannelNames = {
            '1' : 'CC1',
            '2' : 'CC2',
            '3' : 'CC3',
            '4' : 'CC4',
            '5' : 'TEXT1',
            '6' : 'TEXT2',
            '7' : 'TEXT3',
            '8' : 'TEXT4'
            }
        ClosedCaptionCmdString = '>{0}SQ\r'.format(self._DeviceID)
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                CCValue = ClosedCaptionNames[res[3]]
                CCChannelValue = ClosedCaptionChannelNames[res[4]]
                
                self.WriteStatus('ClosedCaption', CCValue, qualifier)
                self.WriteStatus('ClosedCaptionChannel', CCChannelValue, None)

            except (KeyError, IndexError):
                self.Error(['ClosedCaption: Invalid/unexpected response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelValues = {
            'CC1' : '1',
            'CC2' : '2',
            'CC3' : '3',
            'CC4' : '4',
            'TEXT1' : '5',
            'TEXT2' : '6',
            'TEXT3' : '7',
            'TEXT4' : '8'
            }
        ClosedCaptionChannelCmdString = '>{0}Q1={1}\r'.format(self._DeviceID, ClosedCaptionChannelValues[value])
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        self.UpdateClosedCaption(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeValues = {
            'Off' : '0',
            'Ch+Menu' : '1',
            'Vol+Menu' : '2',
            'Ch+Vol+Menu' : '3',
            'Power' : '4',
            'Setup' : '5',
            'Menu' : '6',
            'All' : '7',
            'Setup+Menu' : '8',
            'Pwr+Setup+Menu' : '9'
            }
        ExecutiveModeCmdString = '>{0}S4={1}\r'.format(self._DeviceID, ExecutiveModeValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.UpdateOutput(value, qualifier)

    def SetMenuCall(self, value, qualifier):

        MenuCallValues = {
            'List' : '95',
            'Menu' : '105'
            }
        MenuCallCmdString = '>{0}KK={1}\r'.format(self._DeviceID, MenuCallValues[value])
        self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Right' : '106',
            'Left'  : '107',
            'Up'    : '108',
            'Down'  : '109',
            'Enter' : '110',
            'Exit'  : '111'
            }
        MenuNavigationCmdString = '>{0}KK={1}\r'.format(self._DeviceID, MenuNavigationValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOutput(self, value, qualifier):

        OutputCmdString = '>{0}KK={1}\r'.format(self._DeviceID, self.OutputValues[value])        
        self.__SetHelper('Output', OutputCmdString, value, qualifier)

    def UpdateOutput(self, value, qualifier):

        ExecutiveModeNames = {
            '0' : 'Off',
            '1' : 'Ch+Menu',
            '2' : 'Vol+Menu',
            '3' : 'Ch+Vol+Menu',
            '4' : 'Power',
            '5' : 'Setup',
            '6' : 'Menu',
            '7' : 'All',
            '8' : 'Setup+Menu',
            '9' : 'Pwr+Setup+Menu'
            }
        OutputCmdString = '>{0}SS\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Output', OutputCmdString, value, qualifier)
        if res:
            try:
                executiveModeValue = ExecutiveModeNames[res[5]]
                outputValue = self.OutputNames[res[9]]

                self.WriteStatus('ExecutiveMode', executiveModeValue, None)                
                self.WriteStatus('Output', outputValue, None)

            except (KeyError, IndexError):
                self.Error(['ExecutiveMode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerValues = {
            'On'  : '1',
            'Off' : '0'
            }
        PowerCmdString = '>{0}P{1}\r'.format(self._DeviceID, PowerValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerNames = {
            'U' : 'On',
            'M' : 'Off'
            }
        TunerModeNames = {
            'A' : 'Air',
            'C' : 'Cable'
            }
        PowerCmdString = '>{0}ST\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                powerValue = PowerNames[res[3]]
                tunerModeValue = TunerModeNames[res[9]]
                if powerValue is 'On':  
                    if res[11] is 'F': 
                        tempChannel = int(res[4:7])
                        modifier = int(res[12:14])*1000
                        channelStatusValue = str(tempChannel + modifier)
                    else:  
                        channelStatusValue = str(int(res[4:7])) + '-' + str(int(res[11:14]))  # Remove leading zeroes
                else:
                    channelStatusValue = None
                
                self.WriteStatus('ChannelStatus', channelStatusValue, None)
                self.WriteStatus('Power', powerValue, None)
                self.WriteStatus('TunerMode', tunerModeValue, None)

            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreviousChannel(self, value, qualifier):

        PreviousChannelCmdString = '>{0}TP\r'.format(self._DeviceID)
        self.__SetHelper('PreviousChannel', PreviousChannelCmdString, value, qualifier)

    def SetTunerMode(self, value, qualifier):

        TunerModeValues = {
            'Air'   : '153', 
            'Cable' : '154'
            }
        TunerModeCmdString = '>{0}KK={1}\r'.format(self._DeviceID, TunerModeValues[value])
        self.__SetHelper('TunerMode', TunerModeCmdString, value, qualifier)

    def UpdateTunerMode(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:
            self.Discard('Volume: Invalid Command for SetVolume')
        else:
            VolumeCmdString = '>{0}VH{1}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolume(self, value, qualifier):

        AudioMuteStateNames = {
            'U' : 'Off',
            'M' : 'On'
            }
        VolumeCmdString = '>{0}SV\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                volumeValue = int(res[8:11])
                audioMuteValue = AudioMuteStateNames[res[6]]

                self.WriteStatus('Volume', volumeValue, None)
                self.WriteStatus('AudioMute', audioMuteValue, None)

            except (KeyError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error([command + ': Invalid/unexpected response'])

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return res.decode()

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def ctrs_8_51_0(self):
        self.OutputValues = {
            'RGB'   : '149',
            'YPbPr' : '151'
            }
        self.OutputNames = {
            '0' : 'RGB',
            '2' : 'YPbPr'
            }

    def ctrs_8_51_SDI(self):
        self.OutputValues = {
            'YPbPr' : '151'
            }
        self.OutputNames = {
            '2' : 'YPbPr'
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

