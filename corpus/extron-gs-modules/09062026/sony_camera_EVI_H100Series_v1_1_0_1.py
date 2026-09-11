from re import search
from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
from struct import pack, unpack


class DeviceClass:
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        #Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoFocus': {'Parameters': ['Device ID'], 'Status': {}},
            'BacklightMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID', 'Focus Speed'], 'Status': {}},
            'Gain': {'Parameters': ['Device ID'], 'Status': {}},
            'Iris': {'Parameters': ['Device ID'], 'Status': {}},
            'MasterPower': {'Status': {}},
            'PanTilt': {'Parameters': ['Device ID', 'Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID'], 'Status': {}},
            'Shutter': {'Parameters': ['Device ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Device ID', 'Zoom Speed'], 'Status': {}}
            }

    def SetAutoExposure(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            AutoExposureStateValues = {
                'Full Auto' : 0x00,
                'Manual'    : 0x03,
                'Shutter'   : 0x0A,
                'Iris'      : 0x0B,
                'Bright'    : 0x0D
                }
            AutoExposureCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x39,AutoExposureStateValues[value],0xFF)
            self.__SetHelper('AutoExposure',  AutoExposureCmdString, value, qualifier)

    def UpdateAutoExposure(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            AutoExposureStateNames = {
                b'\x00' : 'Full Auto',
                b'\x03' : 'Manual',
                b'\x0A' : 'Shutter',
                b'\x0B' : 'Iris',
                b'\x0D' : 'Bright'
                }
            AutoExposureCmdString = pack('>BBBBB', DeviceID,0x09,0x04,0x39,0xFF)
            res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
            if res:
                try:
                    value = AutoExposureStateNames[res[-2:-1]]
                    self.WriteStatus('AutoExposure', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAutoExposure')

    def SetAutoFocus(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            AutoFocusStateValues = {
                'On' : 0x02,
                'Off': 0x03
                }
            AutoFocusCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x38,AutoFocusStateValues[value],0xFF)
            self.__SetHelper('AutoFocus',  AutoFocusCmdString, value, qualifier, 3)

    def UpdateAutoFocus(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            AutoFocusStateNames = {
                b'\x02' : 'On',
                b'\x03' : 'Off'
                }
            AutoFocusCmdString = pack('>BBBBB', DeviceID,0x09,0x04,0x38,0xFF)
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            if res:
                try:
                    value = AutoFocusStateNames[res[-2:-1]]
                    self.WriteStatus('AutoFocus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAutoFocus')

    def SetBacklightMode(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            BacklightModeStateValues = {
                'On' : 0x02,
                'Off': 0x03
                }
            BacklightModeCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x33,BacklightModeStateValues[value],0xFF)
            self.__SetHelper('BacklightMode',  BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            BacklightModeStateNames = {
                b'\x02' : 'On',
                b'\x03' : 'Off'
                }
            BacklightModeCmdString = pack('>BBBBB', DeviceID,0x09,0x04,0x33,0xFF)
            res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
            if res:
                try:
                    value = BacklightModeStateNames[res[-2:-1]]
                    self.WriteStatus('BacklightMode', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateBacklightMode')

    def SetFocus(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            FocusStateValues = {
                'Far'  : 0x20,
                'Near' : 0x30,
                }
            FocusConstraints = {
                'Min' : 0,
                'Max' : 7
                }
            if FocusConstraints['Min'] <= int(qualifier['Focus Speed']) <= FocusConstraints['Max']:
                if value == 'Stop':
                    focusspeed = 0x00
                else:
                    focusspeed = int(qualifier['Focus Speed']) + FocusStateValues[value]
                FocusCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x08,focusspeed,0xFF)
                self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)
            else:
                print('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            GainStateValues = {
                'Reset' : 0x00,
                'Up'    : 0x02,
                'Down'  : 0x03
                }
            GainCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x0C,GainStateValues[value],0xFF)
            self.__SetHelper('Gain',  GainCmdString, value, qualifier)

    def SetIris(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            IrisStateValues = {
                'Reset' : 0x00,
                'Up'    : 0x02,
                'Down'  : 0x03
                }
            IrisCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x0B,IrisStateValues[value],0xFF)
            self.__SetHelper('Iris',  IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            PanTiltStateValues = {
                'Up'        : [0x03,0x01],
                'Down'      : [0x03,0x02],
                'Left'      : [0x01,0x03],
                'Right'     : [0x02,0x03],
                'UpLeft'    : [0x01,0x01],
                'UpRight'   : [0x02,0x01],
                'DownLeft'  : [0x01,0x02],
                'DownRight' : [0x02,0x02],
                'Stop'      : [0x03,0x03]
                }
            PanConstraints = {
                'Min': 0,
                'Max': 24
                }
            TiltConstraints = {
                'Min': 0,
                'Max': 23
                }
            PanSpd = int(qualifier['Pan Speed'])
            TiltSpd = int(qualifier['Tilt Speed'])
            if (PanConstraints['Min'] <= PanSpd <= PanConstraints['Max']) and (TiltConstraints['Min'] <= TiltSpd <= TiltConstraints['Max']):
                PanTiltCmdString = pack('>BBBBBBBBB', DeviceID,0x01,0x06,0x01,PanSpd,TiltSpd,PanTiltStateValues[value][0],PanTiltStateValues[value][1],0xFF)
                self.__SetHelper('PanTilt',  PanTiltCmdString, value, qualifier, 3)
            else:
                print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            PowerStateValues = {
                'On' : 0x02,
                'Off': 0x03
                }
            PowerCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x00,PowerStateValues[value],0xFF)
            self.__SetHelper('Power',  PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            PowerStateNames = {
                b'\x02' : 'On',
                b'\x03' : 'Off'
                }
            PowerCmdString = pack('>BBBBB', DeviceID,0x09,0x04,0x00,0xFF)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = PowerStateNames[res[-2:-1]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')

    def SetPresetRecall(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            PresetRecallStateValues = {
                '1' : 0x00,
                '2' : 0x01,
                '3' : 0x02,
                '4' : 0x03,
                '5' : 0x04,
                '6' : 0x05
                }
            PresetRecallCmdString = pack('>BBBBBBB', DeviceID,0x01,0x04,0x3F,0x02,PresetRecallStateValues[value],0xFF)
            self.__SetHelper('PresetRecall',  PresetRecallCmdString, value, qualifier, 3)

    def SetPresetSave(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            PresetSaveStateValues = {
                '1' : 0x00,
                '2' : 0x01,
                '3' : 0x02,
                '4' : 0x03,
                '5' : 0x04,
                '6' : 0x05
                }
            PresetSaveCmdString = pack('>BBBBBBB', DeviceID,0x01,0x04,0x3F,0x01,PresetSaveStateValues[value],0xFF)
            self.__SetHelper('PresetSave',  PresetSaveCmdString, value, qualifier, 3)

    def SetShutter(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            ShutterStateValues = {
                'Reset' : 0x00,
                'Up'    : 0x02,
                'Down'  : 0x03
                }
            ShutterCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x0A,ShutterStateValues[value],0xFF)
            self.__SetHelper('Shutter',  ShutterCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):
        if 1 <= int(qualifier['Device ID']) <= 7:
            DeviceID = 0x80 + int(qualifier['Device ID'])
            ZoomStateValues = {
                'Tele' : 0x20,
                'Wide' : 0x30
                }
            ZoomConstraints = {
                'Min': 0,
                'Max': 7
                }
            if ZoomConstraints['Min'] <= int(qualifier['Zoom Speed']) <= ZoomConstraints['Max']:
                if value == 'Stop':
                    zoomspd = 0x00
                else:
                    zoomspd = int(qualifier['Zoom Speed']) + ZoomStateValues[value]
                ZoomCmdString = pack('>BBBBBB', DeviceID,0x01,0x04,0x07,zoomspd,0xFF)
                self.__SetHelper('Zoom',  ZoomCmdString, value, qualifier, 3)
            else:
                print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>BBBB', response)

                if (errorByte == 0x60) and (errorCode == 0x02):
                    print(sourceCmdName + ' Syntax Error')
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x03):
                    print(sourceCmdName + ' Command Buffer Full')
                    response = ''
                elif (errorByte == 0x06) and (errorCode == 0x04):
                    print(sourceCmdName + ' Command Cancelled')
                    response = ''
                elif (errorByte == 0x06) and (errorCode == 0x05):
                    print(sourceCmdName + ' No Socket')
                    response = ''
                elif (errorByte == 0x60) and (errorCode == 0x41):
                    print(sourceCmdName + ' Command Not Executable')
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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
        if self.connectionFlag == False:
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