from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait, ProgramLog

def print(*args):
    printStr = ''    
    for s in args:
        printStr += '{} '.format(s)
    ProgramLog(printStr, 'info')
    
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
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'FansStatus': {'Parameters': ['Location'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Device Number', 'Output Card Number', 'Connector Number'], 'Status': {}},
            'Input': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'InputNameCommand': {'Parameters': ['Input'], 'Status': {}},
            'InputNameRefresh': {'Parameters': ['Input'], 'Status': {}},
            'InputNameStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'PartNumber': {'Status': {}},
            'PowerSupplyStatus': {'Parameters': ['Unit'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Canvas'], 'Status': {}},
            'PresetSave': {'Parameters': ['Canvas'], 'Status': {}},
            'TemperatureStatus': {'Parameters': ['Type'], 'Status': {}},
            'WindowBorderStyle': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowHorizontalShift': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowHorizontalShiftStatus': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowHorizontalSize': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowHorizontalSizeStatus': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowMute': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowPriority': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowPriorityStatus': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowVerticalShift': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowVerticalShiftStatus': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowVerticalSize': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
            'WindowVerticalSizeStatus': {'Parameters': ['Window', 'Canvas'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'HdcpO([1-8])([0-9]{2})([1-4])\*([012])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Grp([0-9]{2}) Win([0-9]{3}) In([0-9]{4})\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'Nmi(\d{4}),([ \S]{1,32})\r\n'), self.__MatchInputNameStatus, None)
            self.AddMatchString(compile(b'Grp([0-9]{2}) Win([0-9]{3}) In([0-9]{4}) Typ([0-9]{2}) Blk(0|1) Res(.*) Vrt([0-9]{3}\.[0-9])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Pno([0-9-]+)\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(compile(b'(?:Sts)?([01]) ([01]) ([01]) ([01]) (\d{1,2}) (\d{1,2}) (\d{1,2})\r\n'), self.__MatchPowerSupplyStatus, None)
            self.AddMatchString(compile(b'PrstL1\*(0[1-9]|10)\*(0\d\d|1(?:[01]\d|2[0-8]))\r\n'), self.__MatchPresetRecall, None)
            self.AddMatchString(compile(b'WndwB([0-9]{2})\*([0-9]{3})\*([0-9]{3})\r\n'), self.__MatchWindowBorderStyle, None)
            self.AddMatchString(compile(b'HctrW([0-9]{2})\*([0-9]{3})\*([+-][0-9]{6})\r\n'), self.__MatchWindowHorizontalShiftStatus, None)
            self.AddMatchString(compile(b'HsizW([0-9]{2})\*([0-9]{3})\*([0-9]{6})\r\n'), self.__MatchWindowHorizontalSizeStatus, None)
            self.AddMatchString(compile(b'Vmt([0-9]{2})\*([0-9]{3})\*([0-1])\r\n'), self.__MatchWindowMute, None)
            self.AddMatchString(compile(b'WndwP([0-9]{2})\*([0-9]{3})\*([0-9]{1,3})\r\n'), self.__MatchWindowPriorityStatus, None)
            self.AddMatchString(compile(b'VctrW([0-9]{2})\*([0-9]{3})\*([+-][0-9]{6})\r\n'), self.__MatchWindowVerticalShiftStatus, None)
            self.AddMatchString(compile(b'VsizW([0-9]{2})\*([0-9]{3})\*([0-9]{6})\r\n'), self.__MatchWindowVerticalSizeStatus, None)
            self.AddMatchString(compile(b'E([0-2][0-8])\r\n'), self.__MatchError, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)


    def SetPassword(self):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

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

    def SetVerbose(self, value, qualifier):

        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def UpdateFansStatus(self, value, qualifier):

        location = qualifier['Location']
        if location in ['Front', 'Rear']:
            self.UpdatePowerSupplyStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFansStatus')

    def UpdateHDCPOutputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Device Number']) <= 8 and 1 <= int(qualifier['Output Card Number']) <= 99 and 1 <= int(qualifier['Connector Number']) <= 4:
            HDCPOutputStatusCmdString = 'wO{0}{1}{2}HDCP\r'.format(qualifier['Device Number'], qualifier['Output Card Number'].zfill(2), qualifier['Connector Number'])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink',
            '1': 'Non-HDCP Compliant Sink',
            '2': 'HDCP Compliant Sink'
            }

        qualifier = {}
        qualifier['Device Number'] = match.group(1).decode()
        qualifier['Output Card Number'] = match.group(2).decode().lstrip('0')
        qualifier['Connector Number'] = match.group(3).decode()
        value = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetInput(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])

        if 1 <= Window <= 999 and 1 <= Canvas <= 10 and 1 <= int(value) <= 9999:
            self.__SetHelper('Input', '{0}*{1}*{2}!'.format(Canvas, Window, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('Input', '{0}*{1}!'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, qualifier):

        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())

        self.WriteStatus('Input', value, {'Canvas': Canvas, 'Window': Window})

    def SetInputNameCommand(self, value, qualifier):

        input_ = qualifier['Input']
        name = value
        if 1 <= input_ <= 9999 and name is not None and name and 1 <= len(name) <= 32 and all(c not in name for c in '\\/:*?<>|"'):
            InputNameCommandCmdString = 'w{},{}NI\r'.format(input_, name)
            self.__SetHelper('InputNameCommand', InputNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputNameCommand')

    def SetInputNameRefresh(self, value, qualifier):

        input_ = qualifier['Input']

        if 1 <= input_ <= 9999:
            InputNameRefreshCmdString = 'w{}NI\r'.format(input_)
            self.__SetHelper('InputNameRefresh', InputNameRefreshCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputNameRefresh')

    def __MatchInputNameStatus(self, match, tag):

        qualifier = {
            'Input': int(match.group(1).decode())
        }

        value = match.group(2).decode()
        self.WriteStatus('InputNameStatus', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('InputSignalStatus', '{0}*{1}*I'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        qualifier = {}
        qualifier['Window'] = int(match.group(2).decode())
        qualifier['Canvas'] = match.group(1).decode().lstrip('0')
        if match.group(6):
            self.WriteStatus('InputSignalStatus', 'Active', qualifier)
        else:
            self.WriteStatus('InputSignalStatus', 'Not Active', qualifier)

    def UpdatePartNumber(self, value, qualifier):

        self.__UpdateHelper('PartNumber', 'n', None, None)

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
        self.WriteStatus('TemperatureStatus', value1, qualifier1)
        self.WriteStatus('TemperatureStatus', value2, qualifier2)
        self.WriteStatus('TemperatureStatus', value3, qualifier3)

    def SetPresetRecall(self, value, qualifier):

        Canvas = qualifier['Canvas']
        Canvas = 0 if Canvas == 'All' else int(Canvas)
        if 0 <= Canvas <= 10 and 1 <= int(value) <= 128:
            if Canvas:
                self.__SetHelper('PresetRecall', '1*{0}*{1}.'.format(Canvas, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdatePresetRecall(self, value, qualifier):

        Canvas = qualifier['Canvas']
        Canvas = 0 if Canvas == 'All' else int(Canvas)
        if Canvas and 1 <= Canvas <= 10:
            PresetRecallCmdString = 'WL1*{:02}PRST\r'.format(Canvas)
            self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresetRecall')

    def __MatchPresetRecall(self, match, tag):

        qualifier = {'Canvas': '{}'.format(int(match.group(1).decode()))}
        preset_result = int(match.group(2).decode())
        value = 'None' if preset_result == 0 else '{}'.format(preset_result)
        self.WriteStatus('PresetRecall', value, qualifier)

    def SetPresetSave(self, value, qualifier):

        Canvas = qualifier['Canvas']
        if 1 <= int(Canvas) <= 10 and 1 <= int(value) <= 128:
            self.__SetHelper('PresetSave', '1*{0}*{1},'.format(Canvas, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def UpdateTemperatureStatus(self, value, qualifier):

        temp_type = qualifier['Type']
        if temp_type in ['Ambient', 'SBC', 'Card']:
            self.UpdatePowerSupplyStatus(value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperatureStatus')

    def SetWindowHorizontalShift(self, value, qualifier):

        WindowHorizontalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])

        if 1 <= Window <= 999 and 1 <= Canvas <= 10 and value in WindowHorizontalShiftValues:
            self.__SetHelper('WindowHorizontalShift', '\x1BW{0}*{1}{2}HCTR\r\n'.format(Canvas, Window, WindowHorizontalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalShift')

    def UpdateWindowHorizontalShiftStatus(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('WindowHorizontalShiftStatus', '\x1BW{0}*{1}HCTR\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalShiftStatus')

    def __MatchWindowHorizontalShiftStatus(self, match, tag):
        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())
        self.WriteStatus('WindowHorizontalShiftStatus', value, {'Canvas': Canvas, 'Window': Window})

    def SetWindowHorizontalSize(self, value, qualifier):

        WindowHorizontalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])

        if 1 <= Window <= 999 and 1 <= Canvas <= 10 and value in WindowHorizontalSizeValues:
            self.__SetHelper('WindowHorizontalSize', '\x1BW{0}*{1}{2}HSIZ\r\n'.format(Canvas, Window, WindowHorizontalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowHorizontalSize')

    def UpdateWindowHorizontalSizeStatus(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('WindowHorizontalSizeStatus', '\x1BW{0}*{1}HSIZ\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowHorizontalSizeStatus')

    def __MatchWindowHorizontalSizeStatus(self, match, tag):
        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowHorizontalSizeStatus', value, {'Canvas': Canvas, 'Window': Window})

    def SetWindowBorderStyle(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])

        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            if value == 'No Border':
                self.__SetHelper('WindowBorderStyle', '\x1BB{0}*{1}*0WNDW\r\n'.format(Canvas, Window), value, qualifier)
            else:
                if 1 <= int(value) <= 64:
                    self.__SetHelper('WindowBorderStyle', '\x1BB{0}*{1}*{2}WNDW\r\n'.format(Canvas, Window, value), value, qualifier)
                else:
                    self.Discard('Invalid Command')
        else:
            self.Discard('Invalid Command for SetWindowBorderStyle')

    def UpdateWindowBorderStyle(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('WindowBorderStyle', '\x1BB{0}*{1}WNDW\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowBorderStyle')

    def __MatchWindowBorderStyle(self, match, tag):

        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())  # str(int()) removes leading zeroes
        if value == 0:
            self.WriteStatus('WindowBorderStyle', 'No Border', {'Canvas': Canvas, 'Window': Window})
        else:
            self.WriteStatus('WindowBorderStyle', str(value), {'Canvas': Canvas, 'Window': Window})

    def SetWindowMute(self, value, qualifier):

        ValueStateValues = {
            'Mute': '1B',
            'Unmute': '0B'
        }
        Window = qualifier['Window']
        Canvas = qualifier['Canvas']
        Canvas = 0 if Canvas == 'All' else int(Canvas)

        if 0 <= Window <= 999 and 0 <= Canvas <= 10 and value in ValueStateValues:
            self.__SetHelper('WindowMute', '{0}*{1}*{2}\r\n'.format(Canvas, Window, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowMute')

    def UpdateWindowMute(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = qualifier['Canvas']
        Canvas = 0 if Canvas == 'All' else int(Canvas)
        if 0 <= Window <= 999 and 0 <= Canvas <= 10:
            self.__UpdateHelper('WindowMute', '{0}*{1}B\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowMute')

    def __MatchWindowMute(self, match, tag):

        ValueStateValues = {
            '1': 'Mute',
            '0': 'Unmute'
        }

        Canvas = str(int(match.group(1).decode()))
        if Canvas == '0':
            Canvas = 'All'
        Window = int(match.group(2).decode())
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('WindowMute', value, {'Canvas': Canvas, 'Window': Window})

    def SetWindowPriority(self, value, qualifier):

        ValueStateValues = {
            'Send to Back': '0',
            'Send Backward': '1',
            'Bring Forward': '2',
            'Bring to Front': '3'
        }

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10 and value in ValueStateValues:
            self.__SetHelper('WindowPriority', '\x1BP{0}*{1}*{2}WNDW\r\n'.format(Canvas, Window, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPriority')

    def UpdateWindowPriorityStatus(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('WindowPriorityStatus', '\x1BP{0}*{1}WNDW\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowPriorityStatus')

    def __MatchWindowPriorityStatus(self, match, tag):

        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())
        self.WriteStatus('WindowPriorityStatus', value, {'Canvas': Canvas, 'Window': Window})

    def SetWindowVerticalShift(self, value, qualifier):

        WindowVerticalShiftValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])

        if 1 <= Window <= 999 and 1 <= Canvas <= 10 and value in WindowVerticalShiftValues:
            self.__SetHelper('WindowVerticalShift', '\x1BW{0}*{1}{2}VCTR\r\n'.format(Canvas, Window, WindowVerticalShiftValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalShift')

    def UpdateWindowVerticalShiftStatus(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('WindowVerticalShiftStatus', '\x1BW{0}*{1}VCTR\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalShiftStatus')

    def __MatchWindowVerticalShiftStatus(self, match, tag):
        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())
        self.WriteStatus('WindowVerticalShiftStatus', value, {'Canvas': Canvas, 'Window': Window})

    def SetWindowVerticalSize(self, value, qualifier):

        WindowVerticalSizeValues = {
            'Increment': '+',
            'Decrement': '-'
            }

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])

        if 1 <= Window <= 999 and 1 <= Canvas <= 10 and value in WindowVerticalSizeValues:
            self.__SetHelper('WindowVerticalSize', '\x1BW{0}*{1}{2}VSIZ\r\n'.format(Canvas, Window, WindowVerticalSizeValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowVerticalSize')

    def UpdateWindowVerticalSizeStatus(self, value, qualifier):

        Window = qualifier['Window']
        Canvas = int(qualifier['Canvas'])
        if 1 <= Window <= 999 and 1 <= Canvas <= 10:
            self.__UpdateHelper('WindowVerticalSizeStatus', '\x1BW{0}*{1}VSIZ\r\n'.format(Canvas, Window), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindowVerticalSizeStatus')

    def __MatchWindowVerticalSizeStatus(self, match, tag):
        Canvas = str(int(match.group(1).decode()))
        Window = int(match.group(2).decode())
        value = int(match.group(3).decode())  # str(int()) removes leading zeroes
        self.WriteStatus('WindowVerticalSizeStatus', value, {'Canvas': Canvas, 'Window': Window})

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
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '13': 'Invalid parameter',
            '14': 'Invalid command for this configuration',
            '17': 'Invalid command for signal type',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad file name or file not found'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: ' + match.group(1).decode()])

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
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]))#, sep='\r\n')
  
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
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]))#, sep='\r\n')
  
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
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]))#, sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

