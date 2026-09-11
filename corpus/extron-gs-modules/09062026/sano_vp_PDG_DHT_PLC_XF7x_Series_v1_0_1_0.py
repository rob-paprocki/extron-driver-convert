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
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampPower': {'Status': {}},
            'LampStatus': {'Parameters': ['Input'], 'Status': {}},
            'LampUsage': {'Parameters': ['Input'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
            }

        if self.Unidirectional == 'False' and self.ConnectionType == 'Ethernet':
            self.AddMatchString(re.compile(b'PASSWORD:'), self.__MatchPassword, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'CF SCREEN NORMAL\r',
            'Wide': 'CF SCREEN WIDE\r',
            'True': 'CF SCREEN TRUE\r',
            'Full': 'CF SCREEN FULL\r',
            'Custom': 'CF SCREEN CUSTOM\r'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = ValueStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '000 NORMAL\r': 'Normal',
            '000 WIDE\r': 'Wide',
            '000 TRUE\r': 'True',
            '000 FULL\r': 'Full',
            '000 CUSTOM\r': 'Custom'
        }

        AspectRatioCmdString = 'CR SCREEN\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': 'CF KEYDIS KEY\r',
            'Mode 2': 'CF KEYDIS RC\r',
            'Off': 'CF KEYDIS NONE\r'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '000 KEY\r': 'Mode 1',
            '000 RC\r': 'Mode 2',
            '000 NONE\r': 'Off'
        }

        ExecutiveModeCmdString = 'CR KEYDIS\r'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateExecutiveMode')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = 'CR FILH\r'

        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:9])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid Response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'C43\r',
            'Off': 'C44\r'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFreeze')

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
                print('Invalid Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Input 1 SCART': 'CF INPUT1 SCART\r',
            'Input 1 RGB': 'CF INPUT1 ANALOG\r',
            'Input 1 DVI (Digital)': 'CF INPUT1 DIGITAL\r',
            'Input 1 DVI (HDCP)': 'CF INPUT1 HDCP\r',
            'Input 1 HDMI': 'CF INPUT1 HDMI\r',
            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 YPbPr': 'CF INPUT2 YPBPR\r',
            'Input 2 S-Video': 'CF INPUT2 S-VIDEO\r',
            'Input 2 YCbCr': 'CF INPUT2 YCBCR\r',
            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 DF-SDI 1': 'CF INPUT3 SDI1\r',
            'Input 3 DF-SDI 2': 'CF INPUT3 SDI2\r',
            'Input 3 YPbPr': 'CF INPUT3 YPBPR\r',
            'Input 3 DVI': 'CF INPUT3 DIGITAL\r',
            'Input 3 RGB': 'CF INPUT3 ANALOG\r',
            'Input 3 YCbCr': 'CF INPUT3 YCBCR\r',
            'Input 4 RGB': 'CF INPUT4 ANALOG\r',
            'Input 4 Video': 'CF INPUT4 VIDEO\r',
            'Input 4 S-Video': 'CF INPUT4 S-VIDEO\r',
            'Input 4 YCbCr': 'CF INPUT4 YCBCR\r',
            'Input 4 YPbPr': 'CF INPUT4 YPBPR\r',
            'Input 4 DF-SDI 1': 'CF INPUT4 SDI1\r',
            'Input 4 DF-SDI 2': 'CF INPUT4 SDI2\r',
            'Input 4 DVI': 'CF INPUT4 DIGITAL\r',
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'CF INPUT1 SCART\r'     : 'Input 1 SCART', 
            'CF INPUT1 ANALOG\r'    : 'Input 1 RGB', 
            'CF INPUT1 DIGITAL\r'   : 'Input 1 DVI (Digital)', 
            'CF INPUT1 HDCP\r'      : 'Input 1 DVI (HDCP)', 
            'CF INPUT1 HDMI\r'      : 'Input 1 HDMI', 
            'CF INPUT2 VIDEO\r'     : 'Input 2 Video', 
            'CF INPUT2 YPBPR\r'     : 'Input 2 YPbPr', 
            'CF INPUT2 S-VIDEO\r'   : 'Input 2 S-Video', 
            'CF INPUT3 VIDEO\r'     : 'Input 3 Video', 
            'CF INPUT3 S-VIDEO\r'   : 'Input 3 S-Video', 
            'CF INPUT3 SDI1\r'      : 'Input 3 DF-SDI 1', 
            'CF INPUT3 SDI2\r'      : 'Input 3 DF-SDI 2', 
            'CF INPUT3 YPBPR\r'     : 'Input 3 YPbPr', 
            'CF INPUT3 DIGITAL\r'   : 'Input 3 DVI', 
            'CF INPUT3 ANALOG\r'    : 'Input 3 RGB',  
            'CF INPUT4 ANALOG\r'    : 'Input 4 RGB', 
            'CF INPUT4 VIDEO\r'     : 'Input 4 Video', 
            'CF INPUT4 S-VIDEO\r'   : 'Input 4 S-Video', 
            'CF INPUT4 YPBPR\r'     : 'Input 4 YPbPr', 
            'CF INPUT4 SDI1\r'      : 'Input 4 DF-SDI 1', 
            'CF INPUT4 SDI2\r'      : 'Input 4 DF-SDI 2', 
            'CF INPUT4 DIGITAL\r'   : 'Input 4 DVI', 
            'BLANK'                 : 'No Source (LAN card)', 
            'NOCARD'                : 'No Board Inserted'
        }


        getInputCmdString       = 'CR INPUT\r'
        getInputNum             = self.__UpdateHelper('Input', getInputCmdString, value, qualifier)

        if getInputNum:
            try:
                input = getInputNum[4:-1]
                inputTypeCmdString = 'CR SRCINP{0}\r'.format(input)
                getSource = self.__UpdateHelper('Input', inputTypeCmdString, value, qualifier)    
                source = getSource[4:-1]
                if source == 'BLANK' or source == 'NOCARD':
                    value = ValueStateValues[source]
                else:
                    value = ValueStateValues['CF INPUT{0} {1}\r'.format(input, source)]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Full' : 'CF LAMPMODE FULL\r', 
            'Half' : 'CF LAMPMODE HALF\r'
        }

        if value in ValueStateValues:
            LampModeCmdString = ValueStateValues[value]
            self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '000 FULL\r' : 'Full', 
            '000 HALF\r' : 'Half'
        }

        LampModeCmdString = 'CR LAMPMODE\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampMode')

    def SetLampPower(self, value, qualifier):

        ValueStateValues = {
            'Normal'    : 'CF AUTOLAMPCONTRL NORMAL\r', 
            'Eco'       : 'CF AUTOLAMPCONTRL ECO\r', 
            'Auto'      : 'CF AUTOLAMPCONTRL AUTO\r'
        }
        
        if value in ValueStateValues:
            LampPowerCmdString = ValueStateValues[value]
            self.__SetHelper('LampPower', LampPowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLampPower')

    def UpdateLampPower(self, value, qualifier):

        ValueStateValues = {
            '000 NORMAL\r'                  : 'Normal', 
            '000 ECO\r'                     : 'Eco', 
            '000 AUTO\r'                    : 'Auto'
        }

        LampPowerCmdString = 'CR AUTOLAMPCONTRL\r'

        res = self.__UpdateHelper('LampPower', LampPowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LampPower', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampPower')

    def UpdateLampStatus(self, value, qualifier):


        ValueStateValues = {
            'I' : 'On', 
            'O' : 'Off', 
            'X' : 'Failure'
        }

        LampStatusCmdString = 'CR LAMPSTS\r'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)        
        if res:
            try:
                if qualifier['Input'] is '1':
                    value = ValueStateValues[res[5]]                
                elif qualifier['Input'] is '2':
                    value = ValueStateValues[res[6]]
                self.WriteStatus('LampStatus', value, qualifier)           
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampStatus')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'CR LAMPH\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                if   qualifier['Input'] == '1':
                    value = int(res[4:8])
                elif qualifier['Input'] == '2':
                    value = int(res[9:13])
             
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'C1C\r', 
            'Up'    : 'C3C\r', 
            'Down'  : 'C3D\r', 
            'Left'  : 'C3B\r', 
            'Right' : 'C3A\r', 
            'Enter' : 'C3F\r', 
            'Off'   : 'C1D\r'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMenuNavigation')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'CR PROJH\r'

        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4:11])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid Response for UpdateOperationHours')

    def __MatchPassword(self, match, tag):
        self.SetPassword()

    def SetPassword(self):
        if self.devicePassword is not None:
            self.Send('{0}\r'.format(devicePassword))
        else:
            self.MissingCredentialsLog('Password') 

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'C00\r', 
            'Off'   : 'C01\r'
        }
        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPower')


    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '00'    : 'On', 
            '80'    : 'Off',
            '88'    : 'Off',
            '8C'    : 'Off',
            '81'    : 'Off',
            '40'    : 'On', 
            '20'    : 'Cooling Down',  
            '28'    : 'Cooling Down',  
            '21'    : 'Cooling Down',
            '2C'    : 'Cooling Down',
            '24'    : 'Cooling Down', 
            '10'    : 'Off', 
            '02'    : 'On', 
            '04'    : 'Off'
        }

        DRStateValues = {
            '00'    : 'Normal', 
            '80'    : 'Normal',
            '88'    : 'Standby after Cooling Down (Abnormal Temp)',
            '8C'    : 'Standby after Cooling Down (Shutter Mgmt)',
            '81'    : 'Standby after Cooling Down (Lamp Failure)',
            '40'    : 'Countdown in Process', 
            '20'    : 'Normal',  
            '28'    : 'Cooling Down (Abnormal Temp)',  
            '21'    : 'Cooling Down (Lamp Failure)',
            '2C'    : 'Process Cooling Down after Off (Shutter Mgmt)',
            '24'    : 'Power Save (Cooling Down)', 
            '10'    : 'Power Failure', 
            '02'    : 'Invalid Command', 
            '04'    : 'Power Save'
        }

        PowerCmdString = 'CR STATUS\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                powerValue  = PowerStateValues[res[4:6]]
                devresValue = DRStateValues[res[4:6]]
                self.WriteStatus('Power', powerValue, qualifier)
                self.WriteStatus('DeviceStatus', devresValue, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'    : 'C0D\r', 
            'Off'   : 'C0E\r'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '000 ON\r'  : 'On', 
            '000 OFF\r' : 'Off'
        }

        VideoMuteCmdString = 'CR VMUTE\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'?\r'   :   'Data Cannot Be Decoded/Parameter Designation Error.',
                              '101\r' :   'Specified Function is Not Available in the Selected Mode.',
                              '102\r' :   'Specified Value is Out of Range (Not Reflected).',
                              '103\r' :   'Command Mismatched to Hardware.',
                              '201\r' :   'Incremented or Decremented Value or Values are Beyond Upper or Lower Limits.',
                              '301\r' :   'Not Executable Due to Screen Capturing in Process.',
                              '302\r' :   'Not Executable Due to Auto Set Up in Operation.',
                              '303\r' :   'Not Executable Due to Memory Card Viewer in Process.',
                              '402\r' :   'Not Executable Due to PIN Code in Operation.'
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' , res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)            

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
