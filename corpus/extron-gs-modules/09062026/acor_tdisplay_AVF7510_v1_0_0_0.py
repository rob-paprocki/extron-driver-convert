from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPInputWindow2': {'Status': {}},
            'PIPInputWindow3': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'RCEmulation': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07\x01\x00ASP([\x00-\x03])\x08\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00MUT(\x00|\x01)\x08\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00KLC(\x00|\x01)\x08\x0D'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00MIN([\x00\x09-\x0E\x11\x12])\x08\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PSC([\x00-\x07])\x08\x0D'), self.__MatchPIP, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PIN([\x00\x09-\x0E\x11\x12])\x08\x0D'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PIO([\x00\x09-\x0E\x11\x12])\x08\x0D'), self.__MatchPIPInputWindow2, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PIP([\x00\x09-\x0E\x11\x12])\x08\x0D'), self.__MatchPIPInputWindow3, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00PPO([\x00-\x03])\x08\x0D'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00POW(\x00|\x01)\x08\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07\x01\x00VOL([\x00-\x64])\x08\x0D'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Native': b'\x07\x01\x02ASP\x00\x08\x0D',
            'Full Screen': b'\x07\x01\x02ASP\x01\x08\x0D',
            '4:3': b'\x07\x01\x02ASP\x02\x08\x0D',
            'Letterbox': b'\x07\x01\x02ASP\x03\x08\x0D'
        }
        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x07\x01\x01ASP\x08\x0D'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Native',
            b'\x01': 'Full Screen',
            b'\x02': '4:3',
            b'\x03': 'Letterbox'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x07\x01\x02MUT\x01\x08\x0D',
            'Off': b'\x07\x01\x02MUT\x00\x08\x0D'
        }
        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x07\x01\x01MUT\x08\x0D'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x07\x01\x02ADJ\x00\x08\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x07\x01\x02KLC\x01\x08\x0D',
            'Off': b'\x07\x01\x02KLC\x00\x08\x0D'
        }
        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\x07\x01\x01KLC\x08\x0D'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x07\x01\x02MIN\x00\x08\x0D',
            'HDMI 1': b'\x07\x01\x02MIN\x09\x08\x0D',
            'HDMI 2': b'\x07\x01\x02MIN\x0A\x08\x0D',
            'HDMI 3': b'\x07\x01\x02MIN\x0B\x08\x0D',
            'HDMI 4': b'\x07\x01\x02MIN\x0C\x08\x0D',
            'HDMI 5 (Front)': b'\x07\x01\x02MIN\x11\x08\x0D',
            'Display Port': b'\x07\x01\x02MIN\x0D\x08\x0D',
            'IPC/OPS': b'\x07\x01\x02MIN\x0E\x08\x0D',
            'Media Player (Win/Android)': b'\x07\x01\x02MIN\x12\x08\x0D'
        }
        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x07\x01\x01MIN\x08\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'HDMI 3',
            b'\x0C': 'HDMI 4',
            b'\x11': 'HDMI 5 (Front)',
            b'\x0D': 'Display Port',
            b'\x0E': 'IPC/OPS',
            b'\x12': 'Media Player (Win/Android)'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x07\x01\x02RCU\x00\x08\x0D',
            'Up': b'\x07\x01\x02RCU\x02\x08\x0D',
            'Down': b'\x07\x01\x02RCU\x03\x08\x0D',
            'Left': b'\x07\x01\x02RCU\x04\x08\x0D',
            'Right': b'\x07\x01\x02RCU\x05\x08\x0D',
            'Enter': b'\x07\x01\x02RCU\x06\x08\x0D',
            'Exit': b'\x07\x01\x02RCU\x07\x08\x0D'
        }
        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x07\x01\x02PSC\x00\x08\x0D',
            'Small': b'\x07\x01\x02PSC\x01\x08\x0D',
            'Medium': b'\x07\x01\x02PSC\x02\x08\x0D',
            'Large': b'\x07\x01\x02PSC\x03\x08\x0D',
            'Side by Side': b'\x07\x01\x02PSC\x04\x08\x0D',
            'Portrait': b'\x07\x01\x02PSC\x05\x08\x0D',
            '3 Windows': b'\x07\x01\x02PSC\x06\x08\x0D',
            '4 Windows': b'\x07\x01\x02PSC\x07\x08\x0D'
        }
        PIPCmdString = ValueStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        PIPCmdString = b'\x07\x01\x01PSC\x08\x0D'
        self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)

    def __MatchPIP(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'Small',
            b'\x02': 'Medium',
            b'\x03': 'Large',
            b'\x04': 'Side by Side',
            b'\x05': 'Portrait',
            b'\x06': '3 Windows',
            b'\x07': '4 Windows'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIP', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x07\x01\x02PIN\x00\x08\x0D',
            'HDMI 1': b'\x07\x01\x02PIN\x09\x08\x0D',
            'HDMI 2': b'\x07\x01\x02PIN\x0A\x08\x0D',
            'HDMI 3': b'\x07\x01\x02PIN\x0B\x08\x0D',
            'HDMI 4': b'\x07\x01\x02PIN\x0C\x08\x0D',
            'HDMI 5 (Front)': b'\x07\x01\x02PIN\x11\x08\x0D',
            'Display Port': b'\x07\x01\x02PIN\x0D\x08\x0D',
            'IPC/OPS': b'\x07\x01\x02PIN\x0E\x08\x0D',
            'Media Player (Win/Android)': b'\x07\x01\x02PIN\x12\x08\x0D'
        }
        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = b'\x07\x01\x01PIN\x08\x0D'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'HDMI 3',
            b'\x0C': 'HDMI 4',
            b'\x11': 'HDMI 5 (Front)',
            b'\x0D': 'Display Port',
            b'\x0E': 'IPC/OPS',
            b'\x12': 'Media Player (Win/Android)'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPInputWindow2(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x07\x01\x02PIO\x00\x08\x0D',
            'HDMI 1': b'\x07\x01\x02PIO\x09\x08\x0D',
            'HDMI 2': b'\x07\x01\x02PIO\x0A\x08\x0D',
            'HDMI 3': b'\x07\x01\x02PIO\x0B\x08\x0D',
            'HDMI 4': b'\x07\x01\x02PIO\x0C\x08\x0D',
            'HDMI 5 (Front)': b'\x07\x01\x02PIO\x11\x08\x0D',
            'Display Port': b'\x07\x01\x02PIO\x0D\x08\x0D',
            'IPC/OPS': b'\x07\x01\x02PIO\x0E\x08\x0D',
            'Media Player (Win/Android)': b'\x07\x01\x02PIO\x12\x08\x0D'
        }
        PIPInputWindow2CmdString = ValueStateValues[value]
        self.__SetHelper('PIPInputWindow2', PIPInputWindow2CmdString, value, qualifier)

    def UpdatePIPInputWindow2(self, value, qualifier):

        PIPInputWindow2CmdString = b'\x07\x01\x01PIO\x08\x0D'
        self.__UpdateHelper('PIPInputWindow2', PIPInputWindow2CmdString, value, qualifier)

    def __MatchPIPInputWindow2(self, match, tag):

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'HDMI 3',
            b'\x0C': 'HDMI 4',
            b'\x11': 'HDMI 5 (Front)',
            b'\x0D': 'Display Port',
            b'\x0E': 'IPC/OPS',
            b'\x12': 'Media Player (Win/Android)'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPInputWindow2', value, None)

    def SetPIPInputWindow3(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x07\x01\x02PIP\x00\x08\x0D',
            'HDMI 1': b'\x07\x01\x02PIP\x09\x08\x0D',
            'HDMI 2': b'\x07\x01\x02PIP\x0A\x08\x0D',
            'HDMI 3': b'\x07\x01\x02PIP\x0B\x08\x0D',
            'HDMI 4': b'\x07\x01\x02PIP\x0C\x08\x0D',
            'HDMI 5 (Front)': b'\x07\x01\x02PIP\x11\x08\x0D',
            'Display Port': b'\x07\x01\x02PIP\x0D\x08\x0D',
            'IPC/OPS': b'\x07\x01\x02PIP\x0E\x08\x0D',
            'Media Player (Win/Android)': b'\x07\x01\x02PIP\x12\x08\x0D'
        }
        PIPInputWindow3CmdString = ValueStateValues[value]
        self.__SetHelper('PIPInputWindow3', PIPInputWindow3CmdString, value, qualifier)

    def UpdatePIPInputWindow3(self, value, qualifier):

        PIPInputWindow3CmdString = b'\x07\x01\x01PIP\x08\x0D'
        self.__UpdateHelper('PIPInputWindow3', PIPInputWindow3CmdString, value, qualifier)

    def __MatchPIPInputWindow3(self, match, tag):

        ValueStateValues = {
            b'\x00': 'VGA',
            b'\x09': 'HDMI 1',
            b'\x0A': 'HDMI 2',
            b'\x0B': 'HDMI 3',
            b'\x0C': 'HDMI 4',
            b'\x11': 'HDMI 5 (Front)',
            b'\x0D': 'Display Port',
            b'\x0E': 'IPC/OPS',
            b'\x12': 'Media Player (Win/Android)'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPInputWindow3', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left': b'\x07\x01\x02PPO\x00\x08\x0D',
            'Bottom Right': b'\x07\x01\x02PPO\x01\x08\x0D',
            'Top Left': b'\x07\x01\x02PPO\x02\x08\x0D',
            'Top Right': b'\x07\x01\x02PPO\x03\x08\x0D'
        }
        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = b'\x07\x01\x01PPO\x08\x0D'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Bottom Left',
            b'\x01': 'Bottom Right',
            b'\x02': 'Top Left',
            b'\x03': 'Top Right'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b'\x07\x01\x02SWA\x00\x08\x0D'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x07\x01\x02POW\x01\x08\x0D',
            'Off': b'\x07\x01\x02POW\x00\x08\x0D'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x07\x01\x01POW\x08\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetRCEmulation(self, value, qualifier):

        ValueStateValues = {
            'Freeze': b'\x07\x01\x02RCU\x18\x08\x0D',
            'Mute': b'\x07\x01\x02RCU\x19\x08\x0D',
            'Blank Screen': b'\x07\x01\x02RCU\x28\x08\x0D'
        }
        RCEmulationCmdString = ValueStateValues[value]
        self.__SetHelper('RCEmulation', RCEmulationCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = value.to_bytes(1, 'big').join([b'\x07\x01\x02VOL', b'\x08\x0D'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x07\x01\x01VOL\x08\x0D'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = ord(match.group(1))
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

