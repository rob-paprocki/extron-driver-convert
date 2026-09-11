from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface


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
        self._DeviceID = b'\x81'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': {'Status': {}},
            'Iris': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Zoom': {'Status': {}}
            }

        DeviceIDMatch = {
        '1': b'\x81',
        '2': b'\x82',
        '3': b'\x83',
        '4': b'\x84',
        '5': b'\x85',
        '6': b'\x86',
        '7': b'\x87',
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value
        if self._DeviceID in DeviceIDMatch:
            self._DeviceID = DeviceIDMatch[self._DeviceID]
              

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': b'\x01\x04\x08\x03\xFF',
            'Far': b'\x01\x04\x08\x02\xFF',
            'Auto': b'\x01\x04\x38\x02\xFF',
            'Manual': b'\x01\x04\x38\x03\xFF',
            'Stop': b'\x01\x04\x08\x00\xFF'
        }
        FocusCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x0B\x00\xFF',
            'Up': b'\x01\x04\x0B\x02\xFF',
            'Down': b'\x01\x04\x0B\x03\xFF',
        }

        IrisCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        PanSpeedStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F',
            '16': b'\x10',
            '17': b'\x11',
            '18': b'\x12',
            '19': b'\x13',
            '20': b'\x14',
            '21': b'\x15',
            '22': b'\x16',
            '23': b'\x17',
            '24': b'\x18'
        }

        TiltSpeedStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F',
            '16': b'\x10',
            '17': b'\x11',
            '18': b'\x12',
            '19': b'\x13',
            '20': b'\x14'
        }

        ValueStateValues = {
            'P/T Up': b'\x03\x01\xFF',
            'P/T Down': b'\x03\x02\xFF',
            'P/T Left': b'\x01\x03\xFF',
            'P/T Right': b'\x02\x03\xFF',
            'P/T UpLeft': b'\x01\x01\xFF',
            'P/T UpRight': b'\x02\x01\xFF',
            'P/T DownLeft': b'\x01\x02\xFF',
            'P/T DownRight': b'\x02\x02\xFF',
            'P/T Stop': b'\x03\x03\xFF',
            'Home': b'\x01\x06\x04\xFF'
        }

        if value == 'Home':
            PanTiltCmdString = self._DeviceID + ValueStateValues[value]
        else:
            PanTiltCmdString = self._DeviceID + b'\x01\x06\x01' + TiltSpeedStates[qualifier['Tilt Speed']] + PanSpeedStates[qualifier['Pan Speed']] + ValueStateValues[value]
        self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier, 3)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        PowerCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 3)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            value = ValueStateValues[res[2:-1]]
            self.WriteStatus('Power', value, qualifier)
        else:
            print('Invalid response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
             '0': b'\x00',
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F'
        }

        PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + ValueStateValues[value] + b'\xFF'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier, 3)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x00',
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F'
        }

        PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + ValueStateValues[value] + b'\xFF'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier, 3)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': b'\x01\x04\x07\x02\xFF',
            'Wide': b'\x01\x04\x07\x03\xFF',
            'Stop': b'\x01\x04\x07\x00\xFF'
        }

        ZoomCmdString = self._DeviceID + ValueStateValues[value]

        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier, 3)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Debug = True
        self.Send(commandstring)
        
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return ''
            else:
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
