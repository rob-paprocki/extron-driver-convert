from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import ProgramLog

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

        self.devicePassword = '0000'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}}
            }

        if self.Unidirectional == 'False' and self.ConnectionType == 'Ethernet':
            self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPassword, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'CF SCREEN NORMAL\r',
            'Wide': 'CF SCREEN WIDE\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '000 NORMAL\r': 'Normal',
            '000 WIDE\r': 'Wide'
        }

        AspectRatioCmdString = 'CR SCREEN\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Update Aspect Ratio has received an invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'C0B\r',
            'Off': 'C0C\r'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        AudioMuteCmdString = 'CR MUTE\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Update Audio Mute has received an invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'CF KEYDIS NONE\r',
            'RC': 'CF KEYDIS RC\r',
            'Key': 'CF KEYDIS KEY\r'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '000 NONE\r': 'Off',
            '000 RC\r': 'RC',
            '000 KEY\r': 'Key'
        }

        ExecutiveModeCmdString = 'CR KEYDIS\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Update Executive Mode has received an invalid/unexpected response for UpdateExecutiveMode')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 'C4B\r',
            'Near': 'C4A\r'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'C43\r',
            'Off': 'C44\r'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        FreezeCmdString = 'CR FREEZE\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Update Freeze has received an invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Input 1 Digital': 'CF INPUT1 DIGITAL\r',
            'Input 1 Analog': 'CF INPUT1 ANALOG\r',
            'Input 1 Scart': 'CF INPUT1 SCART\r',
            'Input 1 DVI HDCP': 'CF INPUT1 HDCP\r',
            'Input 1 Monitor Out': 'CF INPUT1 OUT\r',

            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 YPBPR': 'CF INPUT2 YPBPR\r',
            'Input 2 Analog': 'CF INPUT2 ANALOG\r',

            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 YPBPR': 'CF INPUT3 YPBPR\r',

            'Input 4 Network': 'CF INPUT4 NETWORK\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'CF INPUT1 DIGITAL\r': 'Input 1 Digital',
            'CF INPUT1 ANALOG\r': 'Input 1 Analog',
            'CF INPUT1 SCART\r': 'Input 1 Scart',
            'CF INPUT1 HDCP\r': 'Input 1 DVI HDCP',
            'CF INPUT1 OUT\r': 'Input 1 Monitor Out',

            'CF INPUT2 VIDEO\r': 'Input 2 Video',
            'CF INPUT2 YPBPR\r': 'Input 2 YPBPR',
            'CF INPUT2 ANALOG\r': 'Input 2 Analog',

            'CF INPUT3 VIDEO\r': 'Input 3 Video',
            'CF INPUT3 S-VIDEO\r': 'Input 3 S-Video',
            'CF INPUT3 YPBPR\r': 'Input 3 YPBPR',

            'CF INPUT4 NETWORK\r': 'Input 4 Network',
            'CF INPUT4 NOCARD\r': 'Input 4 No Network Installed',
        }

        InputCmdString = 'CR INPUT\r'
        getInputNum = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if getInputNum:
            try:
                input = getInputNum[4:-1].strip('0')
                inputTypeCmdString = 'CR SRCINP{0}\r'.format(input)
                getSource = self.__UpdateHelper('Input', inputTypeCmdString, value, qualifier)
                if getSource:
                    try:
                        source = getSource[4:-1]
                        value = ValueStateValues['CF INPUT{0} {1}\r'.format(input, source)]
                        self.WriteStatus('Input', value, qualifier)
                    except(KeyError, IndexError):
                        print('Source response for Input {0} is invalid/unexpected'.format(input))
            except (KeyError, IndexError):
                print('Update Input has received an invalid/unexpected response')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'CF LAMPMODE AUTO\r',
            'Eco Mode': 'CF LAMPMODE ECO\r',
            'Normal Mode': 'CF LAMPMODE NORMAL\r'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '000 AUTO\r': 'Auto',
            '000 ECO\r': 'Eco Mode',
            '000 NORMAL\r': 'Normal Mode'
        }

        LampModeCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Lamp Mode has received an invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)

        if res:
            try:
                val = res.split(' ')
                value = int(val[1].encode())
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Lamp Usage has received an invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStates = {
            'On': 'C1C\r',
            'Up': 'C3C\r',
            'Down': 'C3D\r',
            'Left': 'C3B\r',
            'Right': 'C3A\r',
            'Enter': 'C3F\r',
            'Off': 'C1D\r'
        }

        MenuNavigationCmdString = ValueStates[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                val = res.split(' ')
                value = int(val[1].encode())
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                print('Operation Hours has received an invalid/unexpected response for UpdateOperationHours')

    def __MatchPassword(self, match, tag):

        self.SetOnReceivingPassword(None, None)

    def SetOnReceivingPassword(self, value, qualifier):

        if self.devicePassword is not None:
            cmdString = self.devicePassword + '\r'
            self.Send(cmdString)
        else:
            self.MissingCredentialsLog('Password')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'C00\r',
            'Off': 'C01\r',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '00': 'On',
            '80': 'Off',
            '88': 'Off',
            '81': 'Off',
            '40': 'Warming Up',
            '20': 'Cooling Down',
            '28': 'Cooling Down',
            '21': 'Cooling Down',
            '24': 'Off',
            '10': 'Off',
            '04': 'Off'
        }

        DRStateValues = {
            '00': 'Normal',
            '80': 'Normal',
            '88': 'Standby after Cooling Down (Abnormal Temp)',
            '81': 'Standby after Cooling Down (Lamp Failure)',
            '40': 'Countdown in Process',
            '20': 'Cooling Down in Process',
            '28': 'Cooling Down (Abnormal Temp)',
            '21': 'Cooling Down (Lamp Failure)',
            '24': 'Power Save (Cooling Down)',
            '10': 'Power Failure',
            '04': 'Power Save'
        }

        PowerCmdString = 'CR0\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                powerValue = PowerStateValues[res[:-1]]
                devresValue = DRStateValues[res[:-1]]
                self.WriteStatus('Power', powerValue, qualifier)
                self.WriteStatus('DeviceStatus', devresValue, qualifier)
            except (KeyError, IndexError):
                print('Update Power/Device Status has received an invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStates = {
            'On': 'C0D\r',
            'Off': 'C0E\r'
        }

        VideoMuteCmdString = ValueStates[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Update Video Mute has received an invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        VolumeCmdString = 'CF VOLUME {:03}\r'.format(value)

        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'CR VOLUME\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                val = res.split(' ')
                value = int(val[1].encode())
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                print('Update Volume has received an invalid/unexpected response for UpdateVolume')

    def SetZoom(self, value, qualifier):

        ValueStates = {
            'In': 'C47\r',
            'Out': 'C46\r'
        }

        ZoomCmdString = ValueStates[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'?\r': 'Data Cannot Be Decoded/Parameter Designation Error.',
                              '101\r': 'The Function is Not Available in the Selected Mode.',
                              '102\r': 'The Selected Value is Out of Range',
                              '103\r': 'Command Mismatched to the Hardware.'
                              }

        if response in DEVICE_ERROR_CODES:
            print('Error with {0} - Error Code: {1}: {2}'.format(sourceCmdName, response.strip(), DEVICE_ERROR_CODES[response]))
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('Invalid/unexpected response while sending set command for {0}'.format(command))
            else:
                res = res.decode()
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                res = res.decode()
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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

    def MissingCredentialsLog(self, credentialType):
        if isinstance(self, EthernetClientInterface):
            portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        elif isinstance(self, SerialInterface):
            portInfo = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credentialType, portInfo), 'warning')

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
