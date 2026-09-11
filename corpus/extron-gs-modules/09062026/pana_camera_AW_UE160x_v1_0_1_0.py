from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from extronlib.system import GetUnverifiedContext
import re
import base64
import urllib.error
import urllib.request

class DeviceSerialClass:
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
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'ColorBar': { 'Status': {}},
            'Detail': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'NDFilter': { 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'ResetPanTiltPosition': { 'Status': {}},
            'Tally': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'd1([01])\r'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'd3([01])\r'), self.__MatchAutoIris, None)
            self.AddMatchString(re.compile(b'\x02(?:OBR|DCB):([01])\x03'), self.__MatchColorBar, None)
            self.AddMatchString(re.compile(b'\x02ODT:([01])\x03'), self.__MatchDetail, None)
            self.AddMatchString(re.compile(b'iC(\d{2})\r'), self.__MatchIris, None)
            self.AddMatchString(re.compile(b'\x02OFT:([0-3])\x03'), self.__MatchNDFilter, None)
            self.AddMatchString(re.compile(b'p([013])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'tAE([01])\r'), self.__MatchTally, None)
            self.AddMatchString(re.compile(b'eR([1-3])', re.I), self.__MatchError, None)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            AutoFocusCmdString = '#D1{}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusCmdString = '#D1\r'
        self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoFocus', value, None)

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            AutoIrisCmdString = '#D3{}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoIris')

    def UpdateAutoIris(self, value, qualifier):

        AutoIrisCmdString = '#D3\r'
        self.__UpdateHelper('AutoIris', AutoIrisCmdString, value, qualifier)

    def __MatchAutoIris(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoIris', value, None)

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            ColorBarCmdString = '\x02DCB:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('ColorBar', ColorBarCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorBar')

    def UpdateColorBar(self, value, qualifier):

        ColorBarCmdString = '\x02QBR\x03'
        self.__UpdateHelper('ColorBar', ColorBarCmdString, value, qualifier)

    def __MatchColorBar(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ColorBar', value, None)

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            DetailCmdString = '\x02ODT:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('Detail', DetailCmdString, value, qualifier)
        else:            
            self.Discard('Invalid Command for SetDetail')

    def UpdateDetail(self, value, qualifier):

        DetailCmdString = '\x02QDT\x03'
        self.__UpdateHelper('Detail', DetailCmdString, value, qualifier)

    def __MatchDetail(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Detail', value, None)

    def SetFocus(self, value, qualifier):

        ValueStateValues = ('Far', 'Near', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Far':
                speed = 50 + qualifier['Speed']
            elif value == 'Near':
                speed = 50 - qualifier['Speed']
            else:
                speed = 50
            FocusCmdString = '#F{:02d}\r'.format(speed)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        if 1 <= value <= 99:
            IrisCmdString = '#I{:02d}\r'.format(value)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        IrisCmdString = '#I\r'
        self.__UpdateHelper('Iris', IrisCmdString, value, qualifier)

    def __MatchIris(self, match, tag):

        value = int(match.group(1).decode())
        if 1 <= value <= 99:
            self.WriteStatus('Iris', value, None)

    def SetNDFilter(self, value, qualifier):

        ValueStateValues = {
            'Through': '0',
            '1/4':     '1',
            '1/16':    '2',
            '1/64':    '3'
            }

        if value in ValueStateValues:
            NDFilterCmdString = '\x02OFT:{}\x03'.format(ValueStateValues[value])
            self.__SetHelper('NDFilter', NDFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNDFilter')

    def UpdateNDFilter(self, value, qualifier):

        NDFilterCmdString = '\x02QFT\x03'
        self.__UpdateHelper('NDFilter', NDFilterCmdString, value, qualifier)

    def __MatchNDFilter(self, match, tag):

        ValueStateValues = {
            '0': 'Through',
            '1': '1/4',
            '2': '1/16',
            '3': '1/64'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('NDFilter', value, None)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = ('Left', 'Right', 'Up', 'Down', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Left':
                PanTiltCmdString = '#P{:02d}\r'.format(50 - qualifier['Speed'])
            elif value == 'Right':
                PanTiltCmdString = '#P{:02d}\r'.format(50 + qualifier['Speed'])
            elif value == 'Up':
                PanTiltCmdString = '#T{:02d}\r'.format(50 + qualifier['Speed'])
            elif value == 'Down':
                PanTiltCmdString = '#T{:02d}\r'.format(50 - qualifier['Speed'])
            else:
                PanTiltCmdString = '#PTS5050\r'
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
            }

        if value in ValueStateValues:
            PowerCmdString = '#O{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):


        PowerCmdString = '#O\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '3': 'Warming Up'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetRecallCmdString = '#R{:02d}\r'.format(int(value) - 1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            PresetSaveCmdString = '#M{:02d}\r'.format(int(value) - 1)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResetPanTiltPosition(self, value, qualifier):

        ResetPanTiltPositionCmdString = '#APC80008000\r'
        self.__SetHelper('ResetPanTiltPosition', ResetPanTiltPositionCmdString, value, qualifier)

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            TallyCmdString = '#TAE{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Tally', TallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        TallyCmdString = '#TAE\r'
        self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)

    def __MatchTally(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Tally', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = ('Tele', 'Wide', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Tele':
                speed = 50 + qualifier['Speed']
            elif value == 'Wide':
                speed = 50 - qualifier['Speed']
            else:
                speed = 50
            ZoomCmdString = '#Z{:02d}\r'.format(speed)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

    def __MatchError(self, match, tag):

        self.counter = 0

        DEVICE_ERROR_CODES = {
            '1': 'Command not supported',
            '2': 'Camera in standby or busy',
            '3': 'Data out of range',
        }

        value = match.group(1).decode()
        self.Error([DEVICE_ERROR_CODES[value]])

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

class DeviceHTTPClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        if port == 443: # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        else:
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), 
                                                  urllib.request.HTTPSHandler(context=self._context))
        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoIris': { 'Status': {}},
            'ColorBar': { 'Status': {}},
            'Detail': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'NDFilter': { 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'ResetPanTiltPosition': { 'Status': {}},
            'Tally': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

        self.AutoFocusRegex = re.compile('d1([01])')
        self.AutoIrisRegex =  re.compile('d3([01])')
        self.ColorBarRegex =  re.compile('OBR:([01])')
        self.DetailRegex =    re.compile('ODT:([01])')
        self.IrisRegex =      re.compile('iC(\d{2})')
        self.NDFilterRegex =  re.compile('OFT:([0-3])')
        self.PowerRegex =     re.compile('p([013])')
        self.TallyRegex =     re.compile('tAE([01])')
        self.ErrorRegex =     re.compile('ER([123])', re.I)

    def __GetBasicAuthHeader(self):

        authHandler = '{0}:{1}'.format(self.deviceUsername, self.devicePassword).encode()
        authHeader = base64.b64encode(authHandler).decode("ascii")
        return authHeader
    
    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            AutoFocusCmdString = 'cmd=%23D1{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoFocus', value, qualifier, url=url, data=AutoFocusCmdString)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        AutoFocusCmdString = 'cmd=%23D1&res=1'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, url=url, data=AutoFocusCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.AutoFocusRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetAutoIris(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            AutoIrisCmdString = 'cmd=%23D3{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('AutoIris', value, qualifier, url=url, data=AutoIrisCmdString)
        else:
            self.Discard('Invalid Command for SetAutoIris')

    def UpdateAutoIris(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        AutoIrisCmdString = 'cmd=%23D3&res=1'
        res = self.__UpdateHelper('AutoIris', value, qualifier, url=url, data=AutoIrisCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.AutoIrisRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('AutoIris', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Auto Iris: Invalid/unexpected response'])

    def SetColorBar(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            ColorBarCmdString = 'cmd=DCB:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('ColorBar', value, qualifier, url=url, data=ColorBarCmdString)
        else:
            self.Discard('Invalid Command for SetColorBar')

    def UpdateColorBar(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        ColorBarCmdString = 'cmd=QBR&res=1'
        res = self.__UpdateHelper('ColorBar', value, qualifier, url=url, data=ColorBarCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.ColorBarRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('ColorBar', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Color Bar: Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            DetailCmdString = 'cmd=ODT:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Detail', value, qualifier, url=url, data=DetailCmdString)
        else:
            self.Discard('Invalid Command for SetDetail')

    def UpdateDetail(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        DetailCmdString = 'cmd=QDT&res=1'
        res = self.__UpdateHelper('Detail', value, qualifier, url=url, data=DetailCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.DetailRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Detail', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Detail: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = ('Far', 'Near', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Far':
                speed = 50 + qualifier['Speed']
            elif value == 'Near':
                speed = 50 - qualifier['Speed']
            else:
                speed = 50
                
            url = 'cgi-bin/aw_ptz?'
            FocusCmdString = 'cmd=%23F{:02d}&res=1'.format(speed)
            self.__SetHelper('Focus', value, qualifier, url=url, data=FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        if 1 <= value <= 99:
            url = 'cgi-bin/aw_ptz?'
            IrisCmdString = 'cmd=%23I{:02d}&res=1'.format(value)
            self.__SetHelper('Iris', value, qualifier, url=url, data=IrisCmdString)
        else:
            self.Discard('Invalid Command for SetIris')

    def UpdateIris(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        IrisCmdString = 'cmd=%23I&res=1'
        res = self.__UpdateHelper('Iris', value, qualifier, url=url, data=IrisCmdString)
        if res:
            try:
                valueMatch = self.IrisRegex.match(res)
                value = int(valueMatch.group(1))
                self.WriteStatus('Iris', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Iris: Invalid/unexpected response'])

    def SetNDFilter(self, value, qualifier):

        ValueStateValues = {
            'Through': '0',
            '1/4':     '1',
            '1/16':    '2',
            '1/64':    '3'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_cam?'
            NDFilterCmdString = 'cmd=OFT:{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('NDFilter', value, qualifier, url=url, data=NDFilterCmdString)
        else:
            self.Discard('Invalid Command for SetNDFilter')

    def UpdateNDFilter(self, value, qualifier):

        url = 'cgi-bin/aw_cam?'
        NDFilterCmdString = 'cmd=QFT&res=1'.format(value)
        res = self.__UpdateHelper('NDFilter', value, qualifier, url=url, data=NDFilterCmdString)
        if res:
            try:
                ValueStateValues = {
                    '0': 'Through',
                    '1': '1/4',
                    '2': '1/16',
                    '3': '1/64'
                    }

                valueMatch = self.NDFilterRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('NDFilter', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['ND Filter: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = ('Left', 'Right', 'Up', 'Down', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            if value == 'Left':
                PanTiltCmdString = 'cmd=%23P{:02d}&res=1'.format(50 - qualifier['Speed'])
            elif value == 'Right':
                PanTiltCmdString = 'cmd=%23P{:02d}&res=1'.format(50 + qualifier['Speed'])
            elif value == 'Up':
                PanTiltCmdString = 'cmd=%23T{:02d}&res=1'.format(50 + qualifier['Speed'])
            elif value == 'Down':
                PanTiltCmdString = 'cmd=%23T{:02d}&res=1'.format(50 - qualifier['Speed'])
            else:
                PanTiltCmdString = 'cmd=%23PTS5050&res=1'
            self.__SetHelper('PanTilt', value, qualifier, url=url, data=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            PowerCmdString = 'cmd=%23O{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, url=url, data=PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        PowerCmdString = 'cmd=%23O&res=1'
        res = self.__UpdateHelper('Power', value, qualifier, url=url, data=PowerCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off',
                    '3': 'Warming Up'
                    }

                valueMatch = self.PowerRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 100:
            url = 'cgi-bin/aw_ptz?'
            PresetRecallCmdString = 'cmd=%23R{:02d}&res=1'.format(int(value) - 1)
            self.__SetHelper('PresetRecall', value, qualifier, url=url, data=PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 100:
            url = 'cgi-bin/aw_ptz?'
            PresetSaveCmdString = 'cmd=%23M{:02d}&res=1'.format(int(value) - 1)
            self.__SetHelper('PresetSave', value, qualifier, url=url, data=PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResetPanTiltPosition(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        ResetPanTiltPositionCmdString = 'cmd=%23APC80008000&res=1'
        self.__SetHelper('ResetPanTiltPosition', value, qualifier, url=url, data=ResetPanTiltPositionCmdString)

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if value in ValueStateValues:
            url = 'cgi-bin/aw_ptz?'
            TallyCmdString = 'cmd=%23TAE{}&res=1'.format(ValueStateValues[value])
            self.__SetHelper('Tally', value, qualifier, url=url, data=TallyCmdString)
        else:
            self.Discard('Invalid Command for SetTally')

    def UpdateTally(self, value, qualifier):

        url = 'cgi-bin/aw_ptz?'
        TallyCmdString = 'cmd=%23TAE&res=1'
        res = self.__UpdateHelper('Tally', value, qualifier, url=url, data=TallyCmdString)
        if res:
            try:
                ValueStateValues = {
                    '1': 'On',
                    '0': 'Off'
                    }

                valueMatch = self.TallyRegex.match(res)
                value = ValueStateValues[valueMatch.group(1)]
                self.WriteStatus('Tally', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Tally: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = ('Tele', 'Wide', 'Stop')

        if 1 <= qualifier['Speed'] <= 49 and value in ValueStateValues:
            if value == 'Tele':
                speed = 50 + qualifier['Speed']
            elif value == 'Wide':
                speed = 50 - qualifier['Speed']
            else:
                speed = 50
                
            url = 'cgi-bin/aw_ptz?'
            ZoomCmdString = 'cmd=%23Z{:02d}&res=1'.format(speed)
            self.__SetHelper('Zoom', value, qualifier, url=url, data=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '1': 'Command not supported',
            '2': 'Camera in standby or busy',
            '3': 'Data out of range',
        }

        try:
            res = response.read().decode()
            valueMatch = self.ErrorRegex.match(res)
            if valueMatch:
                self.Error(['{}: {}'.format(sourceCmdName, DEVICE_ERROR_CODES[valueMatch.group(1)])])
                return ''
            else:
                return res
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        rootURL = self.RootURL.replace('http', 'https') if self.DefaultPort == 443 else self.RootURL
        url = '{}{}{}'.format(rootURL, url, data)  #self.RootURL = 'http://<IP Address>:<Port>/'
        
        headers = {}
        headers['Authorization'] = 'Basic {}'.format(self.__GetBasicAuthHeader())
        my_request = urllib.request.Request(url, headers=headers, method='GET')

        try:
            if self.DefaultPort == 443:
                res = urllib.request.urlopen(my_request, context=self._context, timeout=1)
            else:
                res = urllib.request.urlopen(my_request, timeout=1)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):
        
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        rootURL = self.RootURL.replace('http', 'https') if self.DefaultPort == 443 else self.RootURL
        url = '{}{}{}'.format(rootURL, url, data)  #self.RootURL = 'http://<IP Address>:<Port>/'

        headers = {}
        headers['Authorization'] = 'Basic {}'.format(self.__GetBasicAuthHeader())
        my_request = urllib.request.Request(url, headers=headers, method='GET')

        try:
            if self.DefaultPort == 443:
                res = urllib.request.urlopen(my_request, context=self._context, timeout=1)
            else:
                res = urllib.request.urlopen(my_request, timeout=1)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])