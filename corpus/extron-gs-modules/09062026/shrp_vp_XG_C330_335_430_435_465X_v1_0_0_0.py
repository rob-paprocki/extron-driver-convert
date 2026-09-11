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
            'AspectRatio': {'Parameters':['Input'], 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampStatus': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }




    def SetAspectRatio(self, value, qualifier):

        InputStates = {
            'RGB 1' : 'RASR', 
            'RGB 2' : 'RBSR', 
            'DVI' : 'RCSR', 
            'S-Video' : 'RASV', 
            'Video' : 'RBSV'
        }

        ValueStateValues = {
            'Normal' : ' 1', 
            'Full' : ' 5', 
            'Dot by Dot' : ' 3', 
            'Stretch' : ' 2', 
            'Border' : ' 6', 
            'Area Zoom' : '10', 
            'V-Stretch' : '11'
        }

        input = qualifier['Input']
        if input in InputStates:
            AspectRatioCmdString = '{0}  {1}\r'.format(InputStates[input], ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')
    def UpdateAspectRatio(self, value, qualifier):

        InputStates = {
            'RGB 1'   : 'RASR', 
            'RGB 2'   : 'RBSR', 
            'DVI'     : 'RCSR', 
            'S-Video' : 'RASV', 
            'Video'   : 'RBSV'
        }

        RGBStateValues = {
            '1' : 'Normal', 
            '5' : 'Full', 
            '3' : 'Dot by Dot', 
            '2' : 'Stretch', 
            '6' : 'Border', 
        }

        VideoStateValues = {
            '1' : 'Normal', 
            '5' : 'Full', 
            '2' : 'Stretch', 
            '3' : 'Border', 
            '10' : 'Area Zoom', 
            '11' : 'V-Stretch'
        }

        input = qualifier['Input']
        if input in InputStates:
            AspectRatioCmdString = '{0}????\r'.format(InputStates[input])
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    if input in ['RGB 1', 'RGB 2', 'DVI']:
                        self.WriteStatus('AspectRatio', RGBStateValues[res[3]], qualifier)
                    else:
                        self.WriteStatus('AspectRatio', VideoStateValues[res[3:-1]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'ADJS   1\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)



    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        AVMuteCmdString = 'IMBK   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)
    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        AVMuteCmdString = 'IMBK????\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0' : 'Normal', 
            '1' : 'Temp High', 
            '2' : 'Fan Error', 
            '4' : 'Filter Cover Error', 
            '16' : 'Lamp Burnt-out', 
            '32' : 'Lamp Not Lit', 
            '64' : 'Temp Abnormally High', 
            '8' : 'Lamp Life 5% or Less'
        }

        DeviceStatusCmdString = 'TABN   1\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        FreezeCmdString = 'FREZ   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        FreezeCmdString = 'FREZ????\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1' : 'IRGB   1\r', 
            'RGB 2' : 'IRGB   2\r', 
            'DVI' : 'IRGB   3\r', 
            'S-Video' : 'IVED   1\r', 
            'Video' : 'IVED   2\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1' : 'RGB 1', 
            '2' : 'RGB 2', 
            '3' : 'DVI', 
            '4' : 'S-Video', 
            '5' : 'Video'
        }

        InputCmdString = 'ICHK????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco' : '1', 
            'Normal' : '0'
        }

        LampModeCmdString = 'THMD   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Eco', 
            '0' : 'Normal'
        }

        LampModeCmdString = 'THMD????\r'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:-1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off', 
            '2' : 'Retry', 
            '3' : 'Waiting', 
            '4' : 'Lamp Error'
        }

        LampStatusCmdString = 'TLPS   1\r'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('LampStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Status: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'TLTT   1\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        PowerCmdString = 'POWR   {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLA  {0:02d}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLA????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'ERR': "Invalid Command Reply."}   
        if response:
           if response[0:3] == 'ERR':
               self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:3]])])
               response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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
               
            return self.__CheckResponseForErrors(command, res.decode())

            

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

