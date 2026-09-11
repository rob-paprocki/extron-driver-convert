from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaptionDisplay': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }


    def SetAspectRatio(self, value, qualifier):


        States = {
            'Normal'    : 'NORMAL', 
            'Full'      : 'FULL', 
            'Wide'      : 'WIDE', 
            'Zoom'      : 'ZOOM', 
            'True'      : 'TRUE', 
            'Custom'    : 'CUSTOM'
            }

        self.__SetHelper('AspectRatio', 'CF SCREEN {0}\r'.format(States[value]) , value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            '000 NORMAL\r'  : 'Normal', 
            '000 FULL\r'    : 'Full', 
            '000 WIDE\r'    : 'Wide', 
            '000 ZOOM\r'    : 'Zoom', 
            '000 TRUE\r'    : 'True', 
            '000 CUSTOM\r'  : 'Custom'
            }

        res = self.__UpdateHelper('AspectRatio', 'CR SCREEN\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : 'ON', 
            'Off' : 'OFF'
            }

        self.__SetHelper('AudioMute', 'CF MUTE {0}\r'.format(States[value]) , value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            '000 ON\r'  : 'On', 
            '000 OFF\r' : 'Off'
            }

        res = self.__UpdateHelper('AudioMute', 'CR MUTE\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'CF AUTOSETUP START\r' , value, qualifier)

    def SetClosedCaptionDisplay(self, value, qualifier):

        States = {
            'CC1' : 'CC1', 
            'CC2' : 'CC2', 
            'CC3' : 'CC3', 
            'CC4' : 'CC4', 
            'Off' : 'OFF'
            }

        self.__SetHelper('ClosedCaptionDisplay', 'CF CCAPTIONDISP {0}\r'.format(States[value]) , value, qualifier)

    def UpdateClosedCaptionDisplay(self, value, qualifier):

        States = {
            '000 C1\r' : 'CC1', 
            '000 C2\r' : 'CC2', 
            '000 C3\r' : 'CC3', 
            '000 C4\r' : 'CC4', 
            '000 OFF\r' : 'Off'
            }

        res = self.__UpdateHelper('ClosedCaptionDisplay', 'CR CCAPTIONDISP\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaptionDisplay',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'Off'           : 'NONE', 
            'Remote Lock'   : 'RC', 
            'Key Lock'      : 'KEY'
            }

        self.__SetHelper('ExecutiveMode', 'CF KEYDIS {0}\r'.format(States[value]) , value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        States = {
            '000 NONE\r'    : 'Off', 
            '000 RC\r'      : 'Remote Lock', 
            '000 KEY\r'     : 'Key Lock'
            }

        res = self.__UpdateHelper('ExecutiveMode', 'CR KEYDIS\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('ExecutiveMode',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', 'CR FILH\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage',  int(res[4:9]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        States = {
            'On'    : 'ON', 
            'Off'   : 'OFF'
            }

        self.__SetHelper('Freeze', 'CF FREEZE {0}\r'.format(States[value]) , value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            '000 ON\r'  : 'On', 
            '000 OFF\r' : 'Off'
            }

        res = self.__UpdateHelper('Freeze', 'CR FREEZE\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        States = {
            'RGB'       : 'CF INPUT1 ANALOG\r', 
            'Component' : 'CF INPUT1 YPBPR\r',
            'S-Video'   : 'CF INPUT1 S-VIDEO\r',
            'Scart'     : 'CF INPUT1 SCART\r', 
            'HDMI'      : 'CF INPUT2 HDMI\r',
            'Video'     : 'CF INPUT3 VIDEO\r'
            }

        self.__SetHelper('Input', States[value] , value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            '1G' : 'RGB', 
            '1R' : 'Component', 
            '1O' : 'S-Video', 
            '1T' : 'Scart', 
            '2I' : 'HDMI', 
            '3O' : 'Video'
            }

        InputCmdString = 'CR INPUT\r'
        res1 = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res1:
            InputNumber = res1[4:-1]
            InputTypeCmdString = 'CR SRCINP{0}\r'.format(InputNumber)
            res2 = self.__UpdateHelper('Input', InputTypeCmdString, value, qualifier)
            if res2:
                try:
                    InputType = res2[-2]
                    value = InputState[InputNumber + InputType]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        States = {
            'High'      : 'HIGH', 
            'Normal'    : 'NORMAL', 
            'Eco'       : 'ECO'
            }

        self.__SetHelper('LampMode', 'CF LAMPMODE {0}\r'.format(States[value]) , value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        States = {
            '000 HIGH\r' : 'High', 
            '000 NORMAL\r' : 'Normal', 
            '000 ECO\r' : 'Eco'
            }

        res = self.__UpdateHelper('LampMode', 'CR LAMPMODE\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', 'CR LAMPH\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage',  int(res[4:8]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', 'CR PROJH\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('OperationHours',  int(res[4:11]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        States = {
            'On' : 'ON', 
            'Off' : 'OFF', 
            }

        self.__SetHelper('Power', 'CF POWER {0}\r'.format(States[value]) , value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            '00' : 'On', 
            '80' : 'Off', 
            '40' : 'Warming Up', 
            '20' : 'Cooling Down',
            '10' : 'Off',
            '28' : 'Cooling Down',
            '88' : 'Off',
            '24' : 'Cooling Down',
            '04' : 'Off',
            '21' : 'Cooling Down',
            '81' : 'Off'
            }

        DeviceState = {
            '00' : 'Normal',
            '80' : 'Normal',
            '40' : 'Normal',
            '20' : 'Normal',
            '10' : 'Power Failure',
            '28' : 'Cooling down due to abnormal temperature',
            '88' : 'Standby after Cooling Down',
            '24' : 'Power saving Cooling Down',
            '04' : 'Power saving',
            '21' : 'Cooling down due to Lamp Failure',
            '81' : 'Standby after Cooling Down due to Lamp Failure'
            }

        PowerCmdString = 'CR STATUS\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerState[res[4:6]]
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])
            try:
                DeviceValue = DeviceState[res[4:6]]
                self.WriteStatus('DeviceStatus', DeviceValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        States = {
            'On'    : 'ON', 
            'Off'   : 'OFF'
            }

        self.__SetHelper('VideoMute', 'CF VMUTE {0}\r'.format(States[value]) , value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        States = {
            '000 ON\r'  : 'On', 
            '000 OFF\r' : 'Off'
            }

        res = self.__UpdateHelper('VideoMute', 'CR VMUTE\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute',  States[res] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):


        if 0 <= value <= 63:
            VolumeCmdString = 'CF VOLUME {0:03d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', 'CR VOLUME\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume',  int(res[4:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'?\r'   : 'Data cannot be decoded / Parameter designation error',
                              '101\r' : 'The function is not available in the selected Mode',
                              '102\r' : 'Selected value is out of range',
                              '103\r' : 'Command mismatched to Hardware',
                              '201\r' : 'When reached upper or lower limit of increasing or decreasing data',
                              '301\r' : 'Command cannot be executed during capturing display',
                              '302\r' : 'Command cannot be executed during Auto PC operation',
                              '402\r' : 'Command cannot be executed during PIN code operation'
                              }
        
        if response in DEVICE_ERROR_CODES:
            self.Error(['Error with {0} - Error Code: {1}: {2}'.format(sourceCmdName, response.strip(), DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['Invalid/Unexpected Response'])
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
           ### HELPER METHODS SECTION      
        ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

