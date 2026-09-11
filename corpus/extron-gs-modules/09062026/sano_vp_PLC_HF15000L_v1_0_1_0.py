from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'LampStatus': {'Parameters': ['Lamp'], 'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'PowerManagement': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Status': {}}
        }
        
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.devicePassword = '0000'
        
        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(compile(b'PASSWORD:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Hello'), self.__MatchAuthenticated, None)
            
    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):        
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            print('Log in failed. Please supply proper password') 
        self.Authenticated = 'None'
        self.SetPassword(None, None)

    def __MatchAuthenticated(self, match, tag):

        self.Authenticated = 'Success'
        self.PasswdPromptCount = 0

    def SetAspectRatio(self, value, qualifier):
        Value = {
            'Full': 'CF SCREENASPECT FULL\r',
            '4:3': 'CF SCREENASPECT 43MODE\r',
            '16:9': 'CF SCREENASPECT 169MODE\r',
            '16:10': 'CF SCREENASPECT 1610MODE\r'
        }

        self.__SetHelper('AspectRatio', Value[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        Values = {
            '000 FULL\r': 'Full',
            '000 43MODE\r': '4:3',
            '000 169MODE\r': '16:9',
            '000 1610MODE\r': '16:10'
        }

        res = self.__UpdateHelper('AspectRatio', 'CR SCREENASPECT\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', 'C89\r', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        Value = {
            'Mode 1': 'CF KEYDIS RC\r',
            'Mode 2': 'CF KEYDIS KEY\r',
            'Off': 'CF KEYDIS NONE\r'
        }

        self.__SetHelper('ExecutiveMode', Value[value], value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        Values = {
            '000 RC\r': 'Mode 1',
            '000 KEY\r': 'Mode 2',
            '000 NONE\r': 'Off'
        }

        res = self.__UpdateHelper('ExecutiveMode', 'CR KEYDIS\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('ExecutiveMode', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateExecutiveMode')

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', 'CR FILH\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage', int(res[4:9]), qualifier)
            except (ValueError, IndexError):
                print('Invalid Response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': 'CF FREEZE ON\r',
            'Off': 'CF FREEZE OFF\r'
        }

        self.__SetHelper('Freeze', Value[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        Values = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        res = self.__UpdateHelper('Freeze', 'CR FREEZE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        Value = {
            'Input 1 RGB': 'CF INPUT1 ANALOG\r',
            'Input 1 SCART': 'CF INPUT1 SCART\r',
            'Input 1 DVI-D': 'CF INPUT1 DIGITAL\r',
            'Input 1 HDMI': 'CF INPUT1 HDMI\r',
            'Input 1 HDCP': 'CF INPUT1 HDCP\r',
            'Input 2 RGB': 'CF INPUT2 ANALOG\r',
            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 S-Video': 'CF INPUT2 S-VIDEO\r',
            'Input 2 YPbPr': 'CF INPUT2 YPBPR\r',
            'Input 2 YCbCr': 'CF INPUT2 YCBCR\r',
            'Input 3 RGB': 'CF INPUT3 ANALOG\r',
            'Input 3 DVI-D': 'CF INPUT3 DIGITAL\r',
            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 SDI-1': 'CF INPUT3 SDI1\r',
            'Input 3 SDI-2': 'CF INPUT3 SDI2\r',
            'Input 3 SCART': 'CF INPUT3 SCART\r',
            'Input 3 YPbPr': 'CF INPUT3 YPBPR\r',
            'Input 3 HDMI': 'CF INPUT3 HDMI\r',
            'Input 3 HDCP': 'CF INPUT3 HDCP\r',
            'Input 4 RGB': 'CF INPUT4 ANALOG\r',
            'Input 4 DVI-D': 'CF INPUT4 DIGITAL\r',
            'Input 4 Video': 'CF INPUT4 VIDEO\r',
            'Input 4 S-Video': 'CF INPUT4 S-VIDEO\r',
            'Input 4 SDI-1': 'CF INPUT4 SDI1\r',
            'Input 4 SDI-2': 'CF INPUT4 SDI2\r',
            'Input 4 SCART': 'CF INPUT4 SCART\r',
            'Input 4 YPbPr': 'CF INPUT4 YPBPR\r',
            'Input 4 YCbCr': 'CF INPUT4 YCBCR\r',
            'Input 4 HDMI': 'CF INPUT4 HDMI\r',
            'Input 4 HDCP': 'CF INPUT4 HDCP\r'
        }

        self.__SetHelper('Input', Value[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        Source = ''

        SourceQueries = {
            '1': 'CR SRCINP1\r',
            '2': 'CR SRCINP2\r',
            '3': 'CR SRCINP3\r',
            '4': 'CR SRCINP4\r',
        }

        Values = {
            '1': {
                '000 ANALOG\r': 'Input 1 RGB',
                '000 SCART\r': 'Input 1 SCART',
                '000 DIGITAL\r': 'Input 1 DVI-D',
                '000 HDMI\r': 'Input 1 HDMI',
                '000 HDCP\r': 'Input 1 HDCP',

                '000 BLANK\r': 'Input 1 Blank',
                '000 NOCARD\r': 'Input 1 No Card',
            },

            '2': {
                '000 ANALOG\r': 'Input 2 RGB',
                '000 VIDEO\r': 'Input 2 Video',
                '000 S-VIDEO\r': 'Input 2 S-Video',
                '000 YPBPR\r': 'Input 2 YPbPr',

                '000 LINKA-YCBCR\r': 'Input 2 YCbCr',
                '000 LINKB-YCBCR\r': 'Input 2 YCbCr',
                '000 DUAL-YCBCR1\r': 'Input 2 YCbCr',
                '000 DUAL-YCBCR2\r': 'Input 2 YCbCr',
                '000 DUAL-YCBCR3\r': 'Input 2 YCbCr',
                '000 DUAL-YCBCR4\r': 'Input 2 YCbCr',

                '000 BLANK\r': 'Input 2 Blank',
                '000 NOCARD\r': 'Input 2 No Card',
            },

            '3': {
                '000 ANALOG\r': 'Input 3 RGB',
                '000 DIGITAL\r': 'Input 3 DVI-D',
                '000 VIDEO\r': 'Input 3 Video',
                '000 S-VIDEO\r': 'Input 3 S-Video',
                '000 SDI1\r': 'Input 3 SDI-1',
                '000 SDI2\r': 'Input 3 SDI-2',
                '000 SCART\r': 'Input 3 SCART',
                '000 HDMI\r': 'Input 3 HDMI',
                '000 HDCP\r': 'Input 3 HDCP',
                '000 YPBPR\r': 'Input 3 YPbPr',

                '000 BLANK\r': 'Input 3 Blank',
                '000 NOCARD\r': 'Input 3 No Card',
            },

            '4': {
                '000 ANALOG\r': 'Input 4 RGB',
                '000 DIGITAL\r': 'Input 4 DVI-D',
                '000 VIDEO\r': 'Input 4 Video',
                '000 S-VIDEO\r': 'Input 4 S-Video',
                '000 SDI1\r': 'Input 4 SDI-1',
                '000 SDI2\r': 'Input 4 SDI-2',
                '000 SCART\r': 'Input 4 SCART',
                '000 YPBPR\r': 'Input 4 YPbPr',

                '000 LINKA-YCBCR\r': 'Input 4 YCbCr',
                '000 LINKB-YCBCR\r': 'Input 4 YCbCr',
                '000 DUAL-YCBCR1\r': 'Input 4 YCbCr',
                '000 DUAL-YCBCR2\r': 'Input 4 YCbCr',
                '000 DUAL-YCBCR3\r': 'Input 4 YCbCr',
                '000 DUAL-YCBCR4\r': 'Input 4 YCbCr',

                '000 HDMI\r': 'Input 4 HDMI',
                '000 HDCP\r': 'Input 4 HDCP',

                '000 BLANK\r': 'Input 4 Blank',
                '000 NOCARD\r': 'Input 4 No Card',
            },
        }

        res1 = self.__UpdateHelper('Input', 'CR INPUT\r', value, qualifier)
        if res1:
            try:
                Source = res1[4]
                Query = SourceQueries[Source]
            except (KeyError, IndexError):
                print('Invalid Response for UpdateInput')

        if Source in ['1', '2', '3', '4']:
            res2 = self.__UpdateHelper('Input', Query, value, qualifier)
            if res2:
                try:
                    self.WriteStatus('Input', Values[Source][res2], qualifier)
                except (KeyError, IndexError):
                    print('Invalid Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        Value = {
            'All 4': 'CF LAMPMODE 4LAMP\r',
            'Auto 3': 'CF LAMPMODE 3LAMPAUTO\r',
            'Auto 2': 'CF LAMPMODE 2LAMPAUTO\r',
            '1,2,3': 'CF LAMPMODE 3LAMP123\r',
            '2,3,4': 'CF LAMPMODE 3LAMP234\r',
            '2,3': 'CF LAMPMODE 2LAMP23\r',
            '1,4': 'CF LAMPMODE 2LAMP14\r',
            'Constant': 'CF LAMPMODE CONSTANT\r'
        }

        self.__SetHelper('LampMode', Value[value], value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        Values = {
            '000 4LAMP\r': 'All 4',
            '000 3LAMPAUTO\r': 'Auto 3',
            '000 2LAMPAUTO\r': 'Auto 2',
            '000 3LAMP123\r': '1,2,3',
            '000 3LAMP234\r': '2,3,4',
            '000 2LAMP23\r': '2,3',
            '000 2LAMP14\r': '1,4',
            '000 CONSTANT\r': 'Constant'
        }

        res = self.__UpdateHelper('LampMode', 'CR LAMPMODE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampMode')

    def UpdateLampStatus(self, value, qualifier):

        Values = {
            'I': 'On',
            'O': 'Off',
            'X': 'Lamp Failure'
        }

        res = self.__UpdateHelper('LampStatus', 'CR LAMPSTS\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampStatus', Values[res[5]], {'Lamp': '1'})
                self.WriteStatus('LampStatus', Values[res[6]], {'Lamp': '2'})
                self.WriteStatus('LampStatus', Values[res[7]], {'Lamp': '3'})
                self.WriteStatus('LampStatus', Values[res[8]], {'Lamp': '4'})
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampStatus')

        else:
            print('Device Is Busy')

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', 'CR LAMPH\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', int(res[4: 9]), {'Lamp': '1'})
                self.WriteStatus('LampUsage', int(res[10:15]), {'Lamp': '2'})
                self.WriteStatus('LampUsage', int(res[16:21]), {'Lamp': '3'})
                self.WriteStatus('LampUsage', int(res[22:27]), {'Lamp': '4'})
            except (KeyError, IndexError):
                print('Invalid Response for UpdateLampUsage')
        else:
            print('Device Is Busy')

    def SetLensShift(self, value, qualifier):

        Value = {
            'Up': 'C5D\r',
            'Down': 'C5E\r',
            'Left': 'C5F\r',
            'Right': 'C60\r'
        }

        self.__SetHelper('LensShift', Value[value], value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        Value = {
            'Menu On': 'CF MENU ON\r',
            'Menu Off': 'CF MENU OFF\r',
            'Right': 'CF KEYEMU RIGHT\r',
            'Left': 'CF KEYEMU LEFT\r',
            'Up': 'CF KEYEMU UP\r',
            'Down': 'CF KEYEMU DN\r',
            'Enter': 'CF KEYEMU SELECT\r'
        }

        self.__SetHelper('MenuNavigation', Value[value], value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', 'CR PROJH\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('OperationHours', int(res[4:11]), qualifier)
            except (ValueError, IndexError):
                print('Invalid Response for UpdateOperationHours')

    def UpdateSignalStatus(self, value, qualifier):

        Values = {
            '000 ON\r': 'Signal Present',
            '000 OFF\r': 'No Signal'
        }

        res = self.__UpdateHelper('SignalStatus', 'CR SIGNAL\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('SignalStatus', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateSignalStatus')

    def SetPower(self, value, qualifier):

        Value = {
            'On': 'CF POWER ON\r',
            'Off': 'CF POWER OFF\r',
        }

        self.__SetHelper('Power', Value[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        DeviceStates = {
            '00': 'Normal',
            '80': 'Normal',
            '40': 'Countdown in process',
            '20': 'Cooling down in process',
            '10': 'Power failure',
            '28': 'Cooling Down in process due to Temperature Anomaly',
            '88': 'Coming back after Temperature Anomaly',
            '24': 'Power Save/Cooling Down in process',
            '04': 'Power Save',
            '21': 'Cooling Down is in process after Power off due to lamp failure',
            '81': 'Standby after Cooling Down due to lamp failure',
            '2C': 'Cooling Down in process after Power Off due to Shutter management',
            '8C': 'Standby after Cooling Down due to Shutter management'
        }

        res = self.__UpdateHelper('Power', 'CR STATUS\r', value, qualifier)

        if res:
            try:
                res = res[4:6]
                status = DeviceStates[res]
                if res in ['00', '88']:
                    self.WriteStatus('Power', 'On', qualifier)
                    self.WriteStatus('DeviceStatus', status, qualifier)
                elif res in ['80', '10', '81', '04']:
                    self.WriteStatus('Power', 'Off', qualifier)
                    self.WriteStatus('DeviceStatus', status, qualifier)
                elif res in ['20', '40', '28', '24', '21', '2C', '8C']:
                    self.WriteStatus('Power', 'Cooling Down', qualifier)
                    self.WriteStatus('DeviceStatus', status, qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdatePower')

    def SetPowerManagement(self, value, qualifier):

        Value = {
            'Off': 'CF P-MANE OFF\r',
            'Ready': 'CF P-MANE READY\r',
            'Shutdown': 'CF P-MANE SHUTDOWN\r'
        }

        self.__SetHelper('PowerManagement', Value[value], value, qualifier)

    def UpdatePowerManagement(self, value, qualifier):

        Values = {
            '000 OFF\r': 'Off',
            '000 READY\r': 'Ready',
            '000 SHUTDOWN\r': 'Shutdown'
        }

        res = self.__UpdateHelper('PowerManagement', 'CR P-MANE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('PowerManagement', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdatePowerManagement')

    def SetVideoMute(self, value, qualifier):

        Value = {
            'On': 'CF VMUTE ON\r',
            'Off': 'CF VMUTE OFF\r'
        }

        self.__SetHelper('VideoMute', Value[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        Values = {
            '000 ON\r': 'On',
            '000 OFF\r': 'Off'
        }

        res = self.__UpdateHelper('VideoMute', 'CR VMUTE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', Values[res], qualifier)
            except (KeyError, IndexError):
                print('Invalid Response for UpdateVideoMute')

    def SetZoom(self, value, qualifier):

        Value = {
            'Up': 'CF SCREEN DZOOM UP\r',
            'Down': 'CF SCREEN DZOOM DOWN\r'
        }

        self.__SetHelper('Zoom', Value[value], value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        response = response.decode()
        if response:
            if response[0] == '?':
                print('{0} - Unacceptable command'.format(sourceCmdName))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        if self.Authenticated in ['Success', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                if not res:
                    print('No Response')
                else:
                    res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Authenticated in ['Success', 'Not Needed']:
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
                    return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True 

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
