from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {
            'Quantum Ultra Connect 84': self.extr_18_4916_84,
            'Quantum Ultra Connect 128': self.extr_18_4916_128,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FansStatus': {'Parameters': ['Location'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Window'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Window'], 'Status': {}},
            'PartNumber': {'Status': {}},
            'PowerSupplyStatus': {'Parameters': ['Unit'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'TemperatureStatus': {'Parameters': ['Type'], 'Status': {}},
            'WindowHorizontalShift': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalShiftStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalSize': {'Parameters': ['Window'], 'Status': {}},
            'WindowHorizontalSizeStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowMute': {'Parameters': ['Window'], 'Status': {}},
            'WindowPriority': {'Parameters': ['Window'], 'Status': {}},
            'WindowPriorityStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalShift': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalShiftStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalSize': {'Parameters': ['Window'], 'Status': {}},
            'WindowVerticalSizeStatus': {'Parameters': ['Window'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'


        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'HdcpO([012]{4,8})\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Grp01 Win([0-9]{3}) In(00[0-1][0-9])\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(rb'Grp01 Win([0-9]{3}) In([0-9]{4}) Typ([0-9]{2}) Blk(0|1) Res(.*) Vrt([0-9]{3}\.[0-9])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Pno(.*)\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(compile(rb'(?:Sts)?([01]) ([01]) ([01]) ([01]) (\d{1,2}) (\d{1,2}) (\d{1,2})\r\n'), self.__MatchPowerSupplyStatus, None)
            self.AddMatchString(compile(rb'PrstL1\*01\*(0\d\d|1(?:[01]\d|2[0-8]))\r\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(compile(rb'HctrW01\*([0-9]{3})\*([+-][0-9]{6})\r\n'), self.__MatchWindowHorizontalShiftStatus, None)
            self.AddMatchString(compile(rb'HsizW01\*([0-9]{3})\*([0-9]{6})\r\n'), self.__MatchWindowHorizontalSizeStatus, None)
            self.AddMatchString(compile(rb'Vmt01\*([0-9]{3})\*([0-1])\r\n'), self.__MatchWindowMute, None)
            self.AddMatchString(compile(rb'WndwP01\*([0-9]{3})\*([0-9]{3})\r\n'), self.__MatchWindowPriorityStatus, None)
            self.AddMatchString(compile(rb'VctrW01\*([0-9]{3})\*([+-][0-9]{6})\r\n'), self.__MatchWindowVerticalShiftStatus, None)
            self.AddMatchString(compile(rb'VsizW01\*([0-9]{3})\*([0-9]{6})\r\n'), self.__MatchWindowVerticalSizeStatus, None)
            self.AddMatchString(compile(b'E([0-3][0-9])\r\n'), self.__MatchError, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)


    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __QueuePassword(self):

        if self.Authenticated == 'Not Needed':
            self.SetPassword(None, None)

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword()

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def UpdateFansStatus(self, value, qualifier):

        location = qualifier['Location']
        if location in ('Front', 'Rear'):
            self.UpdatePowerSupplyStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFansStatus')

    def UpdateHDCPOutputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.MAX_OUTPUTS:
            HDCPOutputStatusCmdString = 'wOHDCP\r'
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink',
            '1': 'Non-HDCP Compliant Sink',
            '2': 'HDCP Compliant Sink'
            }
        out = 1
        for outputs in match.group(1).decode():
            self.WriteStatus('HDCPOutputStatus', ValueStateValues[outputs], {'Output': str(out)})
            out += 1

    def SetInput(self, value, qualifier):

        Window = qualifier['Window']

        if 1 <= Window <= 999 and 1 <= int(value) <= self.MAX_INPUTS:
            self.__SetHelper('Input', '1*{0}*{1}!'.format(Window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('Input', '1*{0}!'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, qualifier):

        Window = int(match.group(1).decode())
        value = str(int(match.group(2).decode()))  # str(int()) removes leading zeroes

        self.WriteStatus('Input', value, {'Window': Window})  # General case

    def UpdateInputSignalStatus(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('InputSignalStatus', '1*{0}*I'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        qualifier = {}
        qualifier['Window'] = int(match.group(1).decode())
        if match.group(5).decode():
            self.WriteStatus('InputSignalStatus', 'Active', qualifier)
        else:
            self.WriteStatus('InputSignalStatus', 'Not Active', qualifier)

    def UpdatePartNumber(self, value, qualifier):

        cmdString = 'n'

        self.__UpdateHelper('PartNumber', cmdString, None, None)

    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def UpdatePowerSupplyStatus(self, value, qualifier):

        PowerSupplyStatusCmdString = 's'
        self.__UpdateHelper('PowerSupplyStatus', PowerSupplyStatusCmdString, value, qualifier)


    def __MatchPowerSupplyStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Normal',
            '0': 'Failure',
        }
        qualifier1 = {'Unit': 'Primary'}
        qualifier2 = {'Unit': 'Redundant'}
        value1 = ValueStateValues[match.group(1).decode()]
        value2 = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PowerSupplyStatus', value1, qualifier1)
        self.WriteStatus('PowerSupplyStatus', value2, qualifier2)
        qualifier1 = {'Location': 'Front'}
        qualifier2 = {'Location': 'Rear'}
        value1 = ValueStateValues[match.group(3).decode()]
        value2 = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('FansStatus', value1, qualifier1)
        self.WriteStatus('FansStatus', value2, qualifier2)
        qualifier1 = {'Type': 'Ambient'}
        qualifier2 = {'Type': 'SBC'}
        qualifier3 = {'Type': 'Card'}
        value1 = '{}'.format(int(match.group(5).decode()))
        value2 = '{}'.format(int(match.group(6).decode()))
        value3 = '{}'.format(int(match.group(7).decode()))
        self.WriteStatus('TemperatureStatus', int(value1), qualifier1)
        self.WriteStatus('TemperatureStatus', int(value2), qualifier2)
        self.WriteStatus('TemperatureStatus', int(value3), qualifier3)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            self.__SetHelper('PresetRecall', '1*1*{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'WL1*01PRST\r'
        self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def __MatchPresetRecall(self, match, tag):

        preset_result = int(match.group(1).decode())
        value = 'None' if preset_result == 0 else '{}'.format(preset_result)
        self.WriteStatus('PresetRecall', value, None)

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            self.__SetHelper('PresetSave', '1*1*{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def UpdateTemperatureStatus(self, value, qualifier):

        temp_type = qualifier['Type']
        if temp_type in ('Ambient', 'SBC', 'Card'):
            self.UpdatePowerSupplyStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperatureStatus')

    def SetWindowHorizontalShift(self, value, qualifier):

        WindowHorizontalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']

        if 1 <= Window <= 999 and value in ['Increment', 'Decrement']:
            self.__SetHelper('WindowHorizontalShift', '\x1BW1*{0}{1}HCTR\r\n'.format(Window, WindowHorizontalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalShift')

    def UpdateWindowHorizontalShiftStatus(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('WindowHorizontalShiftStatus', '\x1BW1*{0}HCTR\r\n'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalShiftStatus')

    def __MatchWindowHorizontalShiftStatus(self, match, tag):
        Window = int(match.group(1).decode())
        value = int(match.group(2).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowHorizontalShiftStatus', value, {'Window': Window})

    def SetWindowHorizontalSize(self, value, qualifier):

        WindowHorizontalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']

        if 1 <= Window <= 999 and value in ['Increment', 'Decrement']:
            self.__SetHelper('WindowHorizontalSize', '\x1BW1*{0}{1}HSIZ\r\n'.format(Window, WindowHorizontalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalSize')

    def UpdateWindowHorizontalSizeStatus(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('WindowHorizontalSizeStatus', '\x1BW1*{0}HSIZ\r\n'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalSizeStatus')

    def __MatchWindowHorizontalSizeStatus(self, match, tag):
        Window = int(match.group(1).decode())
        value = int(match.group(2).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowHorizontalSizeStatus', value, {'Window': Window})

    def SetWindowMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'Off': '0B'
        }
        Window = qualifier['Window']

        if 1 <= Window <= 999 and value in ['On', 'Off']:
            self.__SetHelper('WindowMute', '1*{0}*{1}\r\n'.format(Window, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowMute')

    def UpdateWindowMute(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('WindowMute', '1*{0}B\r\n'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowMute')

    def __MatchWindowMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        Window = int(match.group(1).decode())
        if Window == 0:
            value = ValueStateValues[match.group(2).decode()]  # str(int()) removes leading zeroes
            for i in range(1, 1000):
                self.WriteStatus('WindowMute', value, {'Window': i})
        else:
            value = ValueStateValues[match.group(2).decode()]  # str(int()) removes leading zeroes
            self.WriteStatus('WindowMute', value, {'Window': Window})

    def SetWindowPriority(self, value, qualifier):

        ValueStateValues = {
            'Send to Back': '0',
            'Send Backward': '1',
            'Bring Forward': '2',
            'Bring to Front': '3'
        }

        Window = qualifier['Window']
        if 1 <= Window <= 999 and value in ['Send to Back', 'Send Backward', 'Bring Forward', 'Bring to Front']:
            self.__SetHelper('WindowPriority', '\x1BP1*{0}*{1}WNDW\r\n'.format(Window, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPriority')

    def UpdateWindowPriorityStatus(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('WindowPriorityStatus', '\x1BP1*{0}WNDW\r\n'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowPriorityStatus')

    def __MatchWindowPriorityStatus(self, match, tag):

        Window = int(match.group(1).decode())
        value = int(match.group(2).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowPriorityStatus', value, {'Window': Window})

    def SetWindowVerticalShift(self, value, qualifier):

        WindowVerticalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']

        if 1 <= Window <= 999 and value in ['Increment', 'Decrement']:
            self.__SetHelper('WindowVerticalShift', '\x1BW1*{0}{1}VCTR\r\n'.format(Window, WindowVerticalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalShift')

    def UpdateWindowVerticalShiftStatus(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('WindowVerticalShiftStatus', '\x1BW1*{0}VCTR\r\n'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalShiftStatus')

    def __MatchWindowVerticalShiftStatus(self, match, tag):
        Window = int(match.group(1).decode())
        value = int(match.group(2).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowVerticalShiftStatus', value, {'Window': Window})

    def SetWindowVerticalSize(self, value, qualifier):

        WindowVerticalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']
        if 1 <= Window <= 999 and value in ['Increment', 'Decrement']:
            self.__SetHelper('WindowVerticalSize', '\x1BW1*{0}{1}VSIZ\r\n'.format(Window, WindowVerticalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalSize')

    def UpdateWindowVerticalSizeStatus(self, value, qualifier):

        Window = qualifier['Window']
        if 1 <= Window <= 999:
            self.__UpdateHelper('WindowVerticalSizeStatus', '\x1BW1*{0}VSIZ\r\n'.format(Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalSizeStatus')

    def __MatchWindowVerticalSizeStatus(self, match, tag):
        Window = int(match.group(1).decode())
        value = int(match.group(2).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowVerticalSizeStatus', value, {'Window': Window})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)


    def __MatchError(self, match, qualifier):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }
        ErrorCode = DEVICE_ERROR_CODES.get(match.group(1).decode(), 'Unknown error: ' + match.group(0).decode())
        self.Error([ErrorCode])

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
        self.VerboseDisabled = True


    def extr_18_4916_128(self):
        self.MAX_INPUTS = 12
        self.MAX_OUTPUTS = 8
        self.HDCPOutput = {
            '1': '1041',
            '2': '1042',
            '3': '1043',
            '4': '1044',
            '5': '1051',
            '6': '1052',
            '7': '1053',
            '8': '1054',
        }

        self.HDCPOutputValues = {
            '1041': '1',
            '1042': '2',
            '1043': '3',
            '1044': '4',
            '1051': '5',
            '1052': '6',
            '1053': '7',
            '1054': '8',
        }


    def extr_18_4916_84(self):
        self.MAX_INPUTS = 8
        self.MAX_OUTPUTS = 4
        self.HDCPOutput = {
            '1': '1031',
            '2': '1032',
            '3': '1033',
            '4': '1034',
        }

        self.HDCPOutputValues = {
            '1031': '1',
            '1032': '2',
            '1033': '3',
            '1034': '4',
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
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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