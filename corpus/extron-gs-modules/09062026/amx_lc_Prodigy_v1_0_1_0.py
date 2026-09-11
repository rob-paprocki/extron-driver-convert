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
            'Curve'             : {'Parameters':['Channel'], 'Status': {}},
            'Level'             : {'Parameters':['Channel'], 'Status': {}},
            'LoadPreset'        : {'Parameters':['Fade Time'], 'Status': {}},
            'Ramp'              : {'Parameters':['Channel'], 'Status': {}},
            'SavePreset'        : {'Parameters':['Fade Time'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'CHAN:(\d{1,2})\s+CURV:(1|2|N|O|F)\s+LEV:(100|\d{1,2})\s'), self.__MatchLevel, None)

    def SetCurve(self, value, qualifier):

        ValueStateValues = {
            'Standard' : '1', 
            'Economy' : '2', 
            'Non-Dim' : 'N', 
            'Always Off' : 'O', 
            'Always On' : 'F'
        }
        ID = ''
        if qualifier['Channel'] == 'Broadcast':
            ID = 'A'
        elif 1 <= int(qualifier['Channel']) <= 96:
            ID = qualifier['Channel']
        if ID:
            CurveCmdString = '{0}/{1}\r'.format(ID, ValueStateValues[value])
            self.__SetHelper('Curve', CurveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCurve')

    def UpdateCurve(self, value, qualifier):
        self.UpdateLevel(value,qualifier)

    def SetLevel(self, value, qualifier):
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }
        
        ID = ''
        if qualifier['Channel'] == 'Broadcast':
            ID = 'A'
        elif 1 <= int(qualifier['Channel']) <= 96:
            ID = qualifier['Channel']
        
        if ID and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LevelCmdString = '{0}L{1}\r'.format(ID,value)
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLevel')

    def UpdateLevel(self, value, qualifier):

        if qualifier['Channel'] != 'Broadcast' and 1 <= int(qualifier['Channel']) <= 96:
            LevelCmdString = '{0}\r'.format(qualifier['Channel'])
            self.__UpdateHelper('Level', LevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateLevel')

    def __MatchLevel(self, match, tag):

        CurveValues = {
            '1' : 'Standard', 
            '2' : 'Economy', 
            'N' : 'Non-Dim', 
            'O' : 'Always Off', 
            'F' : 'Always On'
        }
        qualifier = {}
        qualifier['Channel'] = match.group(1).decode()
        level = int(match.group(3).decode())
        curve = CurveValues[match.group(2).decode()]
        
        self.WriteStatus('Level', level, qualifier)
        self.WriteStatus('Curve', curve, qualifier)

    def SetLoadPreset(self, value, qualifier):

        FadeTimeConstraints = {
            'Min' : 0,
            'Max' : 255
            }
        if FadeTimeConstraints['Min'] <= qualifier['Fade Time'] <= FadeTimeConstraints['Max'] and 1 <= int(value) <= 255:
            if qualifier['Fade Time'] == 0:
                fade = ''
            else:
                fade = qualifier['Fade Time']
            LoadPresetCmdString = '{0}B{1}\r'.format(value,fade)
            self.__SetHelper('LoadPreset', LoadPresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLoadPreset')

    def SetRamp(self, value, qualifier):

        ValueStateValues = {
            'Up' : 'U',
            'Down' : 'D',
            'Stop' : '\r'
        }
        ID = ''
        if qualifier['Channel'] == 'Broadcast':
            ID = 'A'
        elif 1 <= int(qualifier['Channel']) <= 96:
            ID = qualifier['Channel']
        if ID:
            if value == 'Stop':
                RampCmdString = ValueStateValues[value]
            else:
                RampCmdString = '{0}{1}'.format(ID,ValueStateValues[value])
            
            self.__SetHelper('Ramp', RampCmdString, value, qualifier)
        else:
            print('Invalid Command for SetRamp')

    def SetSavePreset(self, value, qualifier):

        FadeTimeConstraints = {
            'Min' : 1,
            'Max' : 255
            }

        if FadeTimeConstraints['Min'] <= qualifier['Fade Time'] <= FadeTimeConstraints['Max'] and 1 <= int(value) <= 255:
            SavePresetCmdString = '{0}R{1}\r'.format(value,qualifier['Fade Time'])
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSavePreset')


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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