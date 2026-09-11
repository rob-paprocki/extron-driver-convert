from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
        self.CameraAddress = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Aperture'          : {'Status': {}},
            'AutoFocus'        : {'Status': {}},
            'AutomaticExposure' : {'Status': {}},
            'BacklightMode'     : {'Status': {}},
            'Focus'             : {'Parameters':['Speed'], 'Status': {}},
            'Iris'              : {'Status': {}},
            'PanTilt'           : {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power'             : {'Status': {}},
            'Preset'            : {'Parameters':['Number'], 'Status': {}},
            'RequiredPolling'   : {'Status': {}},
            'Zoom'              : {'Parameters':['Speed'], 'Status': {}}
            } 

    @property
    def CameraAddress(self):
        return self._CameraAddress

    @CameraAddress.setter
    def CameraAddress(self, value):
        if 1 <= int(value) <= 7:
            self._CameraAddress = 0x80 + int(value)
        else:
            print('Camera Address set to an invalid value: {0}'.format(value))
        
    def SetAperture(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        ApertureCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x02, ValueStateValues[value], 0xFF)
        self.__SetHelper('Aperture', ApertureCmdString, value, qualifier)

    def SetAutoFocus(self, value, qualifier):
        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        AutoFocusCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):
        if self.cType == 'ser':
            ValueStateValues = {
                0x02 : 'On',
                0x03 : 'Off'
            }

            AutoFocusCmdString = pack('>5B', self._CameraAddress, 0x09, 0x04, 0x38, 0xFF)
            res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[2]]
                    self.WriteStatus('AutoFocus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAutoFocus')
        else:
            print('AutoFocus does not support Update.')

    def SetAutomaticExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto'        : 0x00, 
            'Manual'           : 0x03, 
            'Shutter Priority' : 0x0A, 
            'Iris Priority'    : 0x0B, 
            'Bright'           : 0x0D
        }

        AutomaticExposureCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
        self.__SetHelper('AutomaticExposure', AutomaticExposureCmdString, value, qualifier)

    def UpdateAutomaticExposure(self, value, qualifier):

        ValueStateValues = {
            0x00 : 'Full Auto', 
            0x03 : 'Manual', 
            0x0A : 'Shutter Priority', 
            0x0B : 'Iris Priority', 
            0x0D : 'Bright'
        }

        AutomaticExposureCmdString = pack('>5B', self._CameraAddress, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutomaticExposure', AutomaticExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutomaticExposure', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAutomaticExposure')

    def SetBacklightMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        BacklightModeCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
        self.__SetHelper('BacklightMode', BacklightModeCmdString, value, qualifier)

    def UpdateBacklightMode(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off'
        }

        BacklightModeCmdString = pack('>5B', self._CameraAddress, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('BacklightMode', BacklightModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('BacklightMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateBacklightMode')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : 0x20, 
            'Near' : 0x30
        }

        if value == 'Stop':
            FocusCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x08, 0x00, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        elif 0 <= int(qualifier['Speed']) <= 7:
            FocusCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x08, ValueStateValues[value] + int(qualifier['Speed']), 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')



    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Up'    : 0x02, 
            'Down'  : 0x03
        }

        IrisCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'        : [0x03,0x01],
            'Down'      : [0x03,0x02],
            'Left'      : [0x01,0x03],
            'Right'     : [0x02,0x03],
            'Up Left'   : [0x01,0x01],
            'Up Right'  : [0x02,0x01],
            'Down Left' : [0x01,0x02],
            'Down Right': [0x02,0x02],
            'Stop'      : [0x03,0x03]
        }

        if value == 'Home':
            PanTiltCmdString = pack('>5B', self._CameraAddress, 0x01, 0x06, 0x04, 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        elif self.cType == 'ser' and value == 'Reset':
            PanTiltCmdString = pack('>5B', self._CameraAddress, 0x01, 0x06, 0x05, 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            if 1 <= int(qualifier['Pan Speed']) <= 24 and 1 <= int(qualifier['Tilt Speed']) <= 20:
                PanTiltCmdString = pack('>9B', self._CameraAddress, 0x01, 0x06, 0x01, int(qualifier['Pan Speed']), 
                                        int(qualifier['Tilt Speed']), ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
                self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
            else:
                print('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        PowerCmdString = pack('>6B',self._CameraAddress, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02 : 'On', 
            0x03 : 'Off',
            0x04 : 'Internal Power Circuit Error'
        }

        PowerCmdString = pack('>5B', self._CameraAddress, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Reset' : 0x00, 
            'Set'   : 0x01, 
            'Recall': 0x02
        }

        if 0 <= qualifier['Number'] <= self.MaxPresets:
            PresetCmdString = pack('>7B', self._CameraAddress, 0x01, 0x04, 0x3F, ValueStateValues[value], qualifier['Number'], 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def UpdateRequiredPolling(self, value, qualifier):

        RequiredPollingCmdString = pack('>5B', self._CameraAddress, 0x09, 0x04, 0x47, 0xFF)
        res = self.__UpdateHelper('RequiredPolling', RequiredPollingCmdString, value, qualifier)
        if res:
            self.WriteStatus('RequiredPolling', '', None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20, 
            'Wide' : 0x30
        }
        if value == 'Stop':
            ZoomCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x07, 0x00, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        elif 0 <= int(qualifier['Speed']) <= 7:
            ZoomCmdString = pack('>6B', self._CameraAddress, 0x01, 0x04, 0x07, ValueStateValues[value] + int(qualifier['Speed']), 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')


    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x02 : 'Syntax Error',
            0x03 : 'Command Buffer Full',
            0x04 : 'Command Canceled',
            0x05 : 'No Socket',
            0x41 : 'Command Not Executable',
        }   
        if response:
            if (response[2] in DEVICE_ERROR_CODES) and (response[1] == 0x60):
                print('Error in {0}, {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[2]]))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True


        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                return b''
            else:
                return self.__CheckResponseForErrors(command, res)



    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        
    def avon_19_2788_ser(self):
        self.MaxPresets = 127
        self.cType = 'ser'

    def avon_19_2788_eth(self):
        self.MaxPresets = 254
        self.cType = 'eth'
        
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

        self.avon_19_2788_ser()
                

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

        self.avon_19_2788_ser()
                
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

        self.avon_19_2788_eth()
