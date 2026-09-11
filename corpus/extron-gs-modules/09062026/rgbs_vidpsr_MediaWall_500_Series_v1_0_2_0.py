from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from itertools import cycle

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
        self.deviceUsername = 'ADMINENTER'
        self.devicePassword = 'RGB'
        self.Models = {
            'MediaWall 500-2K': self.rgbs_29_1496_2K,
            'MediaWall 500-4K': self.rgbs_29_1496_4K,
            'MediaWall 500AP-2K': self.rgbs_29_1496_AP2K,
            'MediaWall 500AP-4K': self.rgbs_29_1496_AP4K,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AuxOutput': {'Parameters':['Aux'], 'Status': {}},
            'BackgroundColor': {'Parameters':['Red','Green','Blue'], 'Status': {}},
            'Brightness': {'Parameters':['Input'], 'Status': {}},
            'Contrast': {'Parameters':['Input'], 'Status': {}},
            'Gamma': { 'Status': {}},
            'Hue': {'Parameters':['Input'], 'Status': {}},
            'OutputEnabled': {'Parameters':['Output'], 'Status': {}},
            'OutputMode': {'Parameters':['Output'], 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'Saturation': {'Parameters':['Input'], 'Status': {}},
            'Sharpness': {'Parameters':['Input'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'WindowAdd': {'Parameters':['Position','Type'], 'Status': {}},
            'WindowBorderColor': {'Parameters':['Window Number'], 'Status': {}},
            'WindowEnabled': {'Parameters':['Window Number'], 'Status': {}},
            'WindowInput': {'Parameters':['Window Number'], 'Status': {}},
            'WindowMove': {'Parameters':['Window Number', 'Amount'], 'Status': {}},
            'WindowRemove': { 'Status': {}},
            'WindowSize': {'Parameters':['Window Number', 'Amount'], 'Status': {}},
            'WindowZoom': {'Parameters':['Window Number', 'Amount'], 'Status': {}},
        }

        self.PasswdPromptCount = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auxout ([12])\r\n\r\r\n(\d+)\r\r\n'), self.__MatchAuxOutput, None)
            self.AddMatchString(re.compile(b'brightness ([0-9]{1,2})\r\n\r\r\n([0-9-]{1,4})\r\r\n'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'contrast ([0-9]{1,2})\r\n\r\r\n([0-9-]{1,4})\r\r\n'), self.__MatchContrast, None)
            self.AddMatchString(re.compile(b'gamma\r\n([0-2]\.[0-9])\r\r\n'), self.__MatchGamma, None)
            self.AddMatchString(re.compile(b'hue ([0-9]{1,2})\r\n\r\r\n([0-9-]{1,4})\r\r\n'), self.__MatchHue, None)
            self.AddMatchString(re.compile(b'outputenable ([0-9]{1,2})\r\n(ON|OFF) ?\r\r\n'), self.__MatchOutputEnabled, None)
            self.AddMatchString(re.compile(b'outputmode ([0-9]{1,2})\r\n(Auto|auto|AUTO|HDMI|DVI)\r\r\n'), self.__MatchOutputMode, None)
            self.AddMatchString(re.compile(b'saturation ([0-9]{1,2})\r\n\r\r\n([0-9]{1,3})\r\r\n'), self.__MatchSaturation, None)
            self.AddMatchString(re.compile(b'sharpness ([0-9]{1,2})\r\n\r\r\n([0-9-]{1,2})\r\r\n'), self.__MatchSharpness, None)
            self.AddMatchString(re.compile(b'systeminfo\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n.*\r\r\n(.*\r\r\n)'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'temperature\r\nMB REAR RIGHT    ([.0-9]{1,6})  \r\nMB REAR MIDDLE   ([.0-9]{1,6})  \r\nMB FRONT LEFT    ([.0-9]{1,6})  \r\nMB FRONT RIGHT   ([.0-9]{1,6})  \r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'user>'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):

        self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):

        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password.'])
        self.SetPassword( None, None)

    def SetUsername(self, value, qualifier):

        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):

        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAuxOutput(self, value, qualifier):

        aux = int(qualifier['Aux'])

        if 1 <= aux <= 2 and value in self.InputStatesWindow:
            AuxOutputCmdString = 'auxout {} {}\r'.format(aux, value)
            self.__SetHelper('AuxOutput', AuxOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxOutput')

    def UpdateAuxOutput(self, value, qualifier):

        aux = int(qualifier['Aux']) 

        if 1 <= aux <= 2:
            AuxOutputCmdString = 'auxout {}\r'.format(aux)
            self.__UpdateHelper('AuxOutput', AuxOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAuxOutput')

    def __MatchAuxOutput(self, match, tag):

        qualifier = {
            'Aux': match.group(1).decode()
        }

        value = match.group(2).decode()
        self.WriteStatus('AuxOutput', value, qualifier)

    def SetBackgroundColor(self, value, qualifier):

        Red = qualifier['Red']
        Green = qualifier['Green']
        Blue = qualifier['Blue']
        if (0 <= Red <= 255 and 0 <= Green <= 255 and 0 <= Blue <= 255):
            CmdString = 'bgcolor {0} {1} {2}\r'.format(Red, Green, Blue)
            self.__SetHelper('BackgroundColor', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundColor')

    def SetBrightness(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.InputStates and -127 <= value <= 128:
            CmdString = 'brightness {0} {1}\r'.format(Input.upper(),value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        Input = qualifier['Input']
        if not Input == 'All':
            CmdString = 'brightness {0}\r'.format(Input)
            self.__UpdateHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def __MatchBrightness(self, match, tag):
        
        self.WriteStatus('Brightness',  int(match.group(2).decode()) , {'Input' : match.group(1).decode()} )

    def SetContrast(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.InputStates and 0 <= value <= 255:
            CmdString = 'contrast {0} {1}\r'.format(Input.upper(),value)
            self.__SetHelper('Contrast', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        Input = qualifier['Input']
        if not Input == 'All':
            CmdString = 'contrast {0}\r'.format(Input)
            self.__UpdateHelper('Contrast', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateContrast')

    def __MatchContrast(self, match, tag):

        self.WriteStatus('Contrast',  int(match.group(2).decode()) , {'Input' : match.group(1).decode()} )

    def SetGamma(self, value, qualifier):

        if 0.5 <= value <= 2.0:
            CmdString = 'gamma {0:.1f}\r'.format(value)
            self.__SetHelper('Gamma', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGamma')

    def UpdateGamma(self, value, qualifier):

        self.__UpdateHelper('Gamma', 'gamma\r', value, qualifier)

    def __MatchGamma(self, match, tag):

        self.WriteStatus('Gamma',  float(match.group(1).decode()) , None)

    def SetHue(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.InputStates and -180 <= value <= 180:
            CmdString = 'hue {0} {1}\r'.format(Input.upper(),value)
            self.__SetHelper('Hue', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHue')

    def UpdateHue(self, value, qualifier):

        Input = qualifier['Input']
        if not Input == 'All':
            CmdString = 'hue {0}\r'.format(Input)
            self.__UpdateHelper('Hue', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHue')

    def __MatchHue(self, match, tag):

        self.WriteStatus('Hue',  int(match.group(2).decode()) , {'Input' : match.group(1).decode()} )

    def SetOutputEnabled(self, value, qualifier):

        OutputStates = ('1','2','3','4','5','6','7','8','9','10','11','12','All')
        States = {
            'Yes' : 'ON', 
            'No' : 'OFF'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in States:
            CmdString = 'outputenable {0} {1}\r'.format(Output.upper(),States[value])
            self.__SetHelper('OutputEnabled', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputEnabled')

    def UpdateOutputEnabled(self, value, qualifier):

        Output = qualifier['Output']
        if not Output == 'All':
            CmdString = 'outputenable {0}\r'.format(Output)
            self.__UpdateHelper('OutputEnabled', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputEnabled')

    def __MatchOutputEnabled(self, match, tag):

        States = {
            'ON' : 'Yes', 
            'OFF' : 'No'
        }

        self.WriteStatus('OutputEnabled',  States[match.group(2).decode()] , {'Output' : match.group(1).decode()} )

    def SetOutputMode(self, value, qualifier):

        OutputStates = ('1','2','3','4','5','6','7','8','9','10','11','12','All')
        States = {
            'Auto' : 'AUTO', 
            'HDMI' : 'HDMI', 
            'DVI' : 'DVI'
        }

        Output = qualifier['Output']
        if Output in OutputStates and value in States:
            CmdString = 'outputmode {0} {1}\r'.format(Output.upper(),States[value])
            self.__SetHelper('OutputMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMode')

    def UpdateOutputMode(self, value, qualifier):

        Output = qualifier['Output']
        if not Output == 'All':
            CmdString = 'outputmode {0}\r'.format(Output)
            self.__UpdateHelper('OutputMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMode')

    def __MatchOutputMode(self, match, tag):

        States = {
            'AUTO' : 'Auto', 
            'HDMI' : 'HDMI', 
            'DVI' : 'DVI'
        }

        self.WriteStatus('OutputMode',  States[match.group(2).decode()] , {'Output':match.group(1).decode()} )

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Delete' : 'PDEL', 
            'Load' : 'PLOAD', 
            'Save' : 'PSAVE'
        }

        Preset = int(value)
        Action = qualifier['Action']
        if 1 <= Preset <= 60 and Action in ActionStates:
            CmdString = '{0} {1}{2}\r'.format(ActionStates[Action], Preset, ' 1' if Action == 'Save' else '')
            self.__SetHelper('Preset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetSaturation(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.InputStates and 0 <= value <= 255:
            CmdString = 'saturation {0} {1}\r'.format(Input.upper(), value)
            self.__SetHelper('Saturation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaturation')

    def UpdateSaturation(self, value, qualifier):

        Input = qualifier['Input']
        if not Input == 'All':
            CmdString = 'saturation {0}\r'.format(Input)
            self.__UpdateHelper('Saturation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSaturation')

    def __MatchSaturation(self, match, tag):

        self.WriteStatus('Saturation',  int(match.group(2).decode()) , {'Input' : match.group(1).decode()} )

    def SetSharpness(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.InputStates and -5 <= value <= 5:
            CmdString = 'sharpness {0} {1}\r'.format(Input.upper(), value)
            self.__SetHelper('Sharpness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')

    def UpdateSharpness(self, value, qualifier):

        Input = qualifier['Input']
        if not Input == 'All':
            CmdString = 'sharpness {0}\r'.format(Input)
            self.__UpdateHelper('Sharpness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSharpness')

    def __MatchSharpness(self, match, tag):

        self.WriteStatus('Sharpness',  int(match.group(2).decode()) , {'Input' : match.group(1).decode()} )

    def UpdateFirmwareVersion(self, value, qualifier):

        self.__UpdateHelper('FirmwareVersion', 'systeminfo\r', value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        self.WriteStatus('FirmwareVersion', match.group(1).decode(), None)

    def UpdateTemperature(self, value, qualifier):
            
        self.__UpdateHelper('Temperature', 'temperature\r', value, qualifier)

    def __MatchTemperature(self, match, tag):

        self.WriteStatus('Temperature', 'Rear Right: ' + match.group(1).decode() +
                              ', Rear Middle: ' + match.group(2).decode() +
                              ', Front Left: ' + match.group(3).decode() +
                              ', Front Right: ' + match.group(4).decode(), None)

    def SetTestPattern(self, value, qualifier):

        States = ('VRRAMP','VGRAMP','VBRAMP','VWRAMP','HRRAMP','HBRAMP','HWRAMP','BARS','ALIGN','MOIRE','TBARS','OFF','HGRAMP')

        if value in States:
            CmdString = 'testpattern {0}\r'.format(value)
            self.__SetHelper('TestPattern', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def SetWindowAdd(self, value, qualifier):

        PositionStates = {
            'Any' : 'global', 
            'Row 1' : 'local1', 
            'Row 2' : 'local2', 
            'Row 3' : 'local3', 
            'Row 4' : 'local4', 
            'Row 5' : 'local5', 
            'Row 6' : 'local6', 
            'Row 7' : 'local7', 
            'Row 8' : 'local8', 
            'Row 1 & 2' : 'row1n2', 
            'Row 2 & 3' : 'row2n3', 
            'Row 3 & 4' : 'row3n4', 
            'Row 4 & 5' : 'row4n5', 
            'Row 5 & 6' : 'row5n6', 
            'Row 6 & 7' : 'row6n7', 
            'Row 7 & 8' : 'row7n8'
        }

        Position = qualifier['Position']
        Type = qualifier['Type']
        if (Position in PositionStates and Type in self.TypeStates and 1 <= int(value) <= 32):
            CmdString = 'winalloc 1 {0} {1} {2}\r'.format(value, PositionStates[Position], self.TypeStates[Type])
            self.__SetHelper('WindowAdd', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowAdd')

    def SetWindowBorderColor(self, value, qualifier):

        WindowNumberStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17',
                              '18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','All')
        States = ('White','Yellow','Cyan','Green','Magenta','Red','Blue','Black')

        WindowNumber = qualifier['Window Number']
        if WindowNumber in WindowNumberStates and value in States:
            CmdString = 'windowbordercolor 1 {0} {1}\r'.format(WindowNumber.upper(),value.upper())
            self.__SetHelper('WindowBorderColor', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowBorderColor')

    def SetWindowEnabled(self, value, qualifier):

        WindowNumberStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17',
                              '18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','All')
        States = {
            'Yes' : 'ON', 
            'No' : 'OFF'
        }

        WindowNumber = qualifier['Window Number']
        if WindowNumber in WindowNumberStates and value in States:
            CmdString = 'windowenable 1 {0} {1}\r'.format(WindowNumber.upper(),States[value])
            self.__SetHelper('WindowEnabled', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowEnabled')

    def SetWindowInput(self, value, qualifier):

        WindowNumberStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17',
                              '18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','All')

        WindowNumber = qualifier['Window Number']
        if WindowNumber in WindowNumberStates and value in self.InputStatesWindow:
            CmdString = 'windowsource 1 {0} {1}\r'.format(WindowNumber.upper(),value)
            self.__SetHelper('WindowInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowInput')

    def SetWindowMove(self, value, qualifier):

        AmountStates = {
            'Little' : '1', 
            'More' : '5', 
            'Most' : '20'
        }

        States = {
            'Up' : 'i', 
            'Down' : 'm', 
            'Left' : 'j', 
            'Right' : 'l'
        }

        WindowNumber = qualifier['Window Number']
        Amount = qualifier['Amount']
        if 1 <= int(WindowNumber) <= 32 and value in States and Amount in AmountStates:
            CmdString = 'windowposition 1 {0} {1} {2}\r'.format(WindowNumber,States[value],AmountStates[Amount])
            self.__SetHelper('WindowMove', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowMove')

    def SetWindowRemove(self, value, qualifier):


        if 1 <= int(value) <= 32:
            CmdString = 'windowfree 1 {0}\r'.format(value)
            self.__SetHelper('WindowRemove', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowRemove')

    def SetWindowSize(self, value, qualifier):


        AmountStates = {
            'Little' : '1', 
            'More' : '5', 
            'Most' : '20'
        }
        States = {
            'Larger' : 'l', 
            'Smaller' : 's'
        }

        WindowNumber = qualifier['Window Number']
        Amount = qualifier['Amount']
        if 1 <= int(WindowNumber) <= 32 and Amount in AmountStates:
            CmdString = 'windowsize 1 {0} {1} {2}\r'.format(WindowNumber,States[value],AmountStates[Amount])
            self.__SetHelper('WindowSize', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowSize')

    def SetWindowZoom(self, value, qualifier):

        AmountStates = {
            'Little' : '1', 
            'More' : '5', 
            'Most' : '20'
        }
        States = {
            'In' : 'i', 
            'Out' : 'o', 
            'Reset' : 'x'
        }

        WindowNumber = qualifier['Window Number']
        Amount = qualifier['Amount']
        if 1 <= int(WindowNumber) <= 32 and value in States and Amount in AmountStates:
            if value == 'Reset':
                CmdString = 'windowunzoom 1 {0}\r'.format(WindowNumber)
            else:
                CmdString = 'windowzoom 1 {0} {1} {2}\r'.format(WindowNumber,States[value],AmountStates[Amount])
            self.__SetHelper('WindowZoom', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowZoom')

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
        self.PasswdPromptCount = 0
        
    def rgbs_29_1496_2K(self):

        self.TypeStates = {
            'HD' : 'hd', 
            'Group' : 'grp'
        }

        self.InputStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','All')
        self.InputStatesWindow = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18')

    def rgbs_29_1496_4K(self):

        self.TypeStates = {
            'HD' : 'hd', 
            'UHD' : 'uhd', 
            'Group' : 'grp'
        }

        self.InputStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','All')
        self.InputStatesWindow = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18')

    def rgbs_29_1496_AP2K(self):

        self.TypeStates = {
            'HD' : 'hd', 
            'Group' : 'grp'
        }

        self.InputStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','All')
        self.InputStatesWindow = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16')

    def rgbs_29_1496_AP4K(self):

        self.TypeStates = {
            'HD' : 'hd', 
            'UHD' : 'uhd', 
            'Group' : 'grp'
        }

        self.InputStates = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','All')
        self.InputStatesWindow = ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16')

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='SW', CharDelay=0, Mode='RS232', Model =None):
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