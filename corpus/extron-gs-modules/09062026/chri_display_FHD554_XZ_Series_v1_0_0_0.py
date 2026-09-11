from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Device ID'], 'Status': {}},
            'ExecutiveMode': {'Parameters':['Device ID'], 'Status': {}},
            'Input': {'Parameters':['Device ID'], 'Status': {}},
            'MasterPower': { 'Status': {}},
            'MenuNavigation': {'Parameters':['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters':['Device ID','Sub Window'], 'Status': {}},
            'PIPMode': {'Parameters':['Device ID'], 'Status': {}},
            'PIPPosition': {'Parameters':['Device ID'], 'Status': {}},
            'PIPSwap': {'Parameters':['Device ID'], 'Status': {}},
            'Power': {'Parameters':['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters':['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters':['Device ID'], 'Status': {}},
            'VideoWallDivision': {'Parameters':['Device ID','X','Y'], 'Status': {}},
            'VideoWallFrameless': {'Parameters':['Device ID'], 'Status': {}},
            'VideoWallMatrix': {'Parameters':['Device ID','X','Y'], 'Status': {}},
            'VideoWallMode': {'Parameters':['Device ID'], 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00ASP([\x00-\x03])\x08'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00KLC([\x00-\x03])\x08'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00MIN([\x09\x0A\x0D\x0E\x10])\x08'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00PI([NOP])([\x09\x0A\x0D\x0E\x10])\x08'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00PSC([\x00-\x04\x07])\x08'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00PPO([\x00-\x03])\x08'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00POW([\x00\x01])\x08'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00VWF([\x00\x01])\x08'), self.__MatchVideoWallFrameless, None)
            self.AddMatchString(re.compile(b'\x07([\x01-\x19])\x00VWS([\x00\x01])\x08'), self.__MatchVideoWallMode, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0x00
        elif 1 <= int(value) <= 25:
            self._DeviceID = int(value)
        else:
            print('Invalid Device ID Parameter.')

    def __CommandBuilder(self, idt, _type, cmd, value=[]):
        return bytes([0x07, idt, _type] + [ord(i) for i in cmd] + value + [0x08])

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Native'     : 0x00, 
            'Full Screen': 0x01, 
            '4:3'        : 0x02, 
            'Letterbox'  : 0x03
        }
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='ASP', value=[ValueStateValues[value]])
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='ASP')
            self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            0x00: 'Native', 
            0x01: 'Full Screen', 
            0x02: '4:3', 
            0x03: 'Letterbox'
        }

        self.WriteStatus('AspectRatio', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01, 
            'Off': 0x00
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='KLC', value=[ValueStateValues[value]])
            self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')
            
    def UpdateExecutiveMode(self, value, qualifier):
      
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='KLC')
            self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExecutiveMode')
            
    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            0x01: 'On', 
            0x00: 'Off'
        }

        self.WriteStatus('ExecutiveMode', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1': 0x0D, 
            'DisplayPort 2': 0x10, 
            'OPS'          : 0x0E, 
            'HDMI 1'       : 0x09, 
            'HDMI 2'       : 0x0A
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='MIN', value=[ValueStateValues[value]])
            self.__SetHelper('Input', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')
            
    def UpdateInput(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='MIN')
            self.__UpdateHelper('Input', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            0x0D: 'DisplayPort 1', 
            0x10: 'DisplayPort 2', 
            0x0E: 'OPS', 
            0x09: 'HDMI 1', 
            0x0A: 'HDMI 2'
        }

        self.WriteStatus('Input', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu' : 0x00, 
            'Up'   : 0x02, 
            'Down' : 0x03, 
            'Left' : 0x04, 
            'Right': 0x05, 
            'Enter': 0x06, 
            'Exit' : 0x07
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='RCU', value=[ValueStateValues[value]])
            self.__SetHelper('MenuNavigation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPIPInput(self, value, qualifier):

        SubWindowStates = {
            '1': 'PIN', 
            '2': 'PIO', 
            '3': 'PIP'
        }

        ValueStateValues = {
            'DisplayPort 1': 0x0D, 
            'DisplayPort 2': 0x10, 
            'OPS'          : 0x0E, 
            'HDMI 1'       : 0x09, 
            'HDMI 2'       : 0x0A
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25 and qualifier['Sub Window'] in SubWindowStates:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd=SubWindowStates[qualifier['Sub Window']], value=[ValueStateValues[value]])
            self.__SetHelper('PIPInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        SubWindowStates = {
            '1': 'PIN', 
            '2': 'PIO', 
            '3': 'PIP'
        }
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25 and qualifier['Sub Window'] in SubWindowStates:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd=SubWindowStates[qualifier['Sub Window']])
            self.__UpdateHelper('PIPInput', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPInput')

    def __MatchPIPInput(self, match, tag):

        SubWindowStates = {
            'N': '1', 
            'O': '2', 
            'P': '3'
        }

        ValueStateValues = {
            0x0D: 'DisplayPort 1', 
            0x10: 'DisplayPort 2', 
            0x0E: 'OPS', 
            0x09: 'HDMI 1', 
            0x0A: 'HDMI 2'
        }

        self.WriteStatus('PIPInput', ValueStateValues[match.group(3)[0]], {'Device ID': str(match.group(1)[0]), 'Sub Window': SubWindowStates[match.group(2).decode()]})

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off'       : 0x00, 
            'PIP Small' : 0x01, 
            'PIP Medium': 0x02, 
            'PIP Large' : 0x03, 
            'Dual View' : 0x04, 
            'Quad View' : 0x07
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='PSC', value=[ValueStateValues[value]])
            self.__SetHelper('PIPMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='PSC')
            self.__UpdateHelper('PIPMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPMode')

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            0x00: 'Off', 
            0x01: 'PIP Small', 
            0x02: 'PIP Medium', 
            0x03: 'PIP Large', 
            0x04: 'Dual View', 
            0x07: 'Quad View'
        }

        self.WriteStatus('PIPMode', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Bottom Left' : 0x00, 
            'Bottom Right': 0x01, 
            'Top Left'    : 0x02, 
            'Top Right'   : 0x03
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='PPO', value=[ValueStateValues[value]])
            self.__SetHelper('PIPPosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def UpdatePIPPosition(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='PPO')
            self.__UpdateHelper('PIPPosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePIPPosition')

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            0x00: 'Bottom Left', 
            0x01: 'Bottom Right', 
            0x02: 'Top Left', 
            0x03: 'Top Right'
        }

        self.WriteStatus('PIPPosition', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def SetPIPSwap(self, value, qualifier):

        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='SWA', value=[0x00])
            self.__SetHelper('PIPSwap', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSwap')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01, 
            'Off': 0x00
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='POW', value=[ValueStateValues[value]])
            self.__SetHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='POW')
            self.__UpdateHelper('Power', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            0x01: 'On', 
            0x00: 'Off'
        }
        
        device_id = match.group(1)[0]
        self.WriteStatus('Power', ValueStateValues[match.group(2)[0]], {'Device ID': str(device_id)})
        
    def SetPresetRecall(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= int(value) <= 127 and 0 <= device_id <= 25:
            PresetRecallCmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='PSR', value=[int(value)])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= int(value) <= 127 and 0 <= device_id <= 25:
            PresetSaveCmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='PSS', value=[int(value)])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVideoWallDivision(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        x_val, y_val = int(qualifier['X']), int(qualifier['Y'])
        
        if 0 <= device_id <= 25 and 1 <= x_val <= 10 and 1 <= y_val <= 10:
            VideoWallDivisionCmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='DIV', value=[(x_val << 4)+y_val])
            self.__SetHelper('VideoWallDivision', VideoWallDivisionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallDivision')

    def SetVideoWallFrameless(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01, 
            'Off': 0x00
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='VWF', value=[ValueStateValues[value]])
            self.__SetHelper('VideoWallFrameless', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallFrameless')

    def UpdateVideoWallFrameless(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='VWF')
            self.__UpdateHelper('VideoWallFrameless', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallFrameless')

    def __MatchVideoWallFrameless(self, match, tag):

        ValueStateValues = {
            0x01: 'On', 
            0x00: 'Off'
        }

        self.WriteStatus('VideoWallFrameless', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def SetVideoWallMatrix(self, value, qualifier):

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        x_val, y_val = int(qualifier['X']), int(qualifier['Y'])
        
        if 0 <= device_id <= 25 and 1 <= x_val <= 10 and 1 <= y_val <= 10:
            VideoWallMatrixCmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='MAT', value=[(x_val << 4)+y_val])
            self.__SetHelper('VideoWallMatrix', VideoWallMatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallMatrix')

    def SetVideoWallMode(self, value, qualifier):

        ValueStateValues = {
            'On' : 0x01, 
            'Off': 0x00
        }

        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if value in ValueStateValues and 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x02, cmd='VWS', value=[ValueStateValues[value]])
            self.__SetHelper('VideoWallMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoWallMode')

    def UpdateVideoWallMode(self, value, qualifier):
        
        device_id = 0x00 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        
        if 0 <= device_id <= 25:
            CmdString = self.__CommandBuilder(idt=device_id, _type=0x01, cmd='VWS')
            self.__UpdateHelper('VideoWallMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoWallMode')

    def __MatchVideoWallMode(self, match, tag):

        ValueStateValues = {
            0x01: 'On', 
            0x00: 'Off'
        }

        self.WriteStatus('VideoWallMode', ValueStateValues[match.group(2)[0]], {'Device ID': str(match.group(1)[0])})

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        
        if self.Unidirectional == 'True' or self._DeviceID == 0x00 or qualifier['Device ID'] == 'Broadcast':
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