from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'Backlight': {'Status': {}},
            'Focus': {'Status': {}},
            'Iris': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Status': {}}
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        DeviceIDMatch = {
            '1': b'\x81',
            '2': b'\x82',
            '3': b'\x83',
            '4': b'\x84',
            '5': b'\x85',
            '6': b'\x86',
            '7': b'\x87',
        }
        
        if value in DeviceIDMatch:
            self._DeviceID = DeviceIDMatch[value]
        else:
            print('Device ID out of range.')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x38\x02\xFF',
            'Off': b'\x01\x04\x38\x03\xFF'
        }

        AutoFocusCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x33\x02\xFF',
            'Off': b'\x01\x04\x33\x03\xFF'
        }

        BacklightCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        BacklightCmdString = self._DeviceID + b'\x09\x04\x33\xFF'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                print('Backlight: Invalid/unexpected response for UpdateBacklight')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': b'\x01\x04\x08\x03\xFF',
            'Far': b'\x01\x04\x08\x02\xFF',
            'Stop': b'\x01\x04\x08\x00\xFF'
        }

        FocusCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset': b'\x01\x04\x0B\x00\xFF',
            'Up': b'\x01\x04\x0B\x02\xFF',
            'Down': b'\x01\x04\x0B\x03\xFF'
        }

        IrisCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        PowerCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02': 'On',
            b'\x03': 'Off'
        }

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x00',
            '2': b'\x01',
            '3': b'\x02',
            '4': b'\x03',
            '5': b'\x04',
            '6': b'\x05',
            '7': b'\x06',
            '8': b'\x07',
            '9': b'\x08',
            '10': b'\x09',
            '11': b'\x0A',
            '12': b'\x0B',
            '13': b'\x0C',
            '14': b'\x0D',
            '15': b'\x0E',
            '16': b'\x0F'
        }

        PresetRecallCmdString = self._DeviceID + b'\x01\x04\x3F\x02' + ValueStateValues[value] + b'\xFF'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def UpdatePresetRecall(self, value, qualifier):

        ValueStateValues = {
            b'\x00': '1',
            b'\x01': '2',
            b'\x02': '3',
            b'\x03': '4',
            b'\x04': '5',
            b'\x05': '6',
            b'\x06': '7',
            b'\x07': '8',
            b'\x08': '9',
            b'\x09': '10',
            b'\x0A': '11',
            b'\x0B': '12',
            b'\x0C': '13',
            b'\x0D': '14',
            b'\x0E': '15',
            b'\x0F': '16'
        }

        PresetRecallCmdString = self._DeviceID + b'\x09\x04\x3F\xFF'
        res = self.__UpdateHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('PresetRecall', value, qualifier)
            except (KeyError, IndexError):
                print('Preset Recall: Invalid/unexpected response for UpdatePresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x00',
            '2': b'\x01',
            '3': b'\x02',
            '4': b'\x03',
            '5': b'\x04',
            '6': b'\x05',
            '7': b'\x06',
            '8': b'\x07',
            '9': b'\x08',
            '10': b'\x09',
            '11': b'\x0A',
            '12': b'\x0B',
            '13': b'\x0C',
            '14': b'\x0D',
            '15': b'\x0E',
            '16': b'\x0F'
        }

        PresetSaveCmdString = self._DeviceID + b'\x01\x04\x3F\x01' + ValueStateValues[value] + b'\xFF'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x04\x35\x00\xFF',
            'Indoor': b'\x01\x04\x35\x01\xFF',
            'Outdoor': b'\x01\x04\x35\x02\xFF',
            'One Push White Balance': b'\x01\x04\x35\x03\xFF',
            'Manual': b'\x01\x04\x35\x05\xFF'
        }

        WhiteBalanceCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Auto',
            b'\x01': 'Indoor',
            b'\x02': 'Outdoor',
            b'\x03': 'One Push White Balance',
            b'\x05': 'Manual'
        }

        WhiteBalanceCmdString = self._DeviceID + b'\x09\x04\x35\xFF'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:-1]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                print('White Balance: Invalid/unexpected response for UpdateWhiteBalance')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': b'\x01\x04\x07\x02\xFF',
            'Wide': b'\x01\x04\x07\x03\xFF',
            'Stop': b'\x01\x04\x07\x00\xFF'
        }

        ZoomCmdString = self._DeviceID + ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('{0}: Unexpected/Invalid response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res)

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
                return self.__CheckResponseForErrors(command, res)

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
