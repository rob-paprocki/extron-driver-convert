from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re

class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ColorMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
            }
        
        
        self.match_pattern_single = re.compile('^\(.*,(\d)\)$')
        self.match_pattern_multi = re.compile('^\(.*,(\d+)\)$')

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Normal': '0',
            '16:9': '1',
            '4:3': '2',
            'Letter Box': '3',
            'Full': '4',
            'True': '5',
            '4:3 (Forced)': '6'
        }

        AspectRatioCmdString = '(ARZ{0})'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier, 3)

    def UpdateAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '0': 'Normal',
            '1': '16:9',
            '2': '4:3',
            '3': 'Letter Box',
            '4': 'Full',
            '5': 'True',
            '6': '4:3 (Forced)'
        }

        AspectRatioCmdString = '(ARZ?)'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_single.match(res).group(1)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for AspectRatio')

    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '(MUT{0})'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = '(MUT?)'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_single.match(res).group(1)]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for AudioMute')

    def SetColorMode(self, value, qualifier):
        ValueStateValues = {
            'Graphics': '1',
            'Theater': '2',
            'Standard': '3',
            'Blackboard': '4',
            'Natural': '5'
        }

        ColorModeCmdString = '(PST{0})'.format(ValueStateValues[value])
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):
        ValueStateValues = {
            '1': 'Graphics',
            '2': 'Theater',
            '3': 'Standard',
            '4': 'Blackboard',
            '5': 'Natural'
        }

        ColorModeCmdString = '(PST?)'
        res = self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_single.match(res).group(1)]
                self.WriteStatus('ColorMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for ColorMode')

    def UpdateDeviceStatus(self, value, qualifier):
        ValueStateValues = {
            '0': 'Normal',
            '1': 'Fan Error',
            '2': 'Temperature Error',
            '7': 'Light Error',
            '16': 'Other Error'
        }

        DeviceStatusCmdString = '(STS?)'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_multi.match(res).group(1)]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for DeviceStatus')

    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '(FRZ{0})'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '(FRZ?)'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_single.match(res).group(1)]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Freeze')

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'Computer 1': '0',
            'Component 1': '1',
            'Video': '2',
            'USB Display': '12',
            'Auto 1': '6',
            'HDMI': '7',
            'S-Video': '9',
            'Computer 2': '3',
            'Component 2': '4',
            'Network': '8',
            'Auto 2': '10',
            'File Viewer': '11',
            'USB Tool': '13'
        }

        InputCmdString = '(SRC{0})'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        ValueStateValues = {
            '0': 'Computer 1',
            '1': 'Component 1',
            '2': 'Video',
            '12': 'USB Display',
            '6': 'Auto 1',
            '7': 'HDMI',
            '9': 'S-Video',
            '3': 'Computer 2',
            '4': 'Component 2',
            '8': 'Network',
            '10': 'Auto 2',
            '11': 'File Viewer',
            '13': 'USB Tool'
        }

        InputCmdString = '(SRC?)'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_multi.match(res).group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Input')

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = '(LMP?)'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(self.match_pattern_multi.match(res).group(1))
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for LampUsage')

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up': '1',
            'Down': '2',
            'Left': '3',
            'Right': '4',
            'Enter': '5',
            'Esc': '6',
            'Menu': '11'
        }

        MenuNavigationCmdString = '(KEY{0})'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
#-----------------------------------------------------------------------------------------------------

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = '(PWR{0})'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '(PWR?)'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_single.match(res).group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Power')

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '(BLK{0})'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        
    def UpdateVideoMute(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '(BLK?)'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.match_pattern_single.match(res).group(1)]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for VideoMute')

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 30
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '(VOL{0})'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = '(VOL?)'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(self.match_pattern_multi.match(res).group(1))
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for Volume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=')').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        
        
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=')').decode()
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
################################################################
# HELPER METHODS SECTION
################################################################

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True      

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
