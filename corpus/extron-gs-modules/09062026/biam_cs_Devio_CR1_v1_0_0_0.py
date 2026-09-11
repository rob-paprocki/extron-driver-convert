from extronlib.interface import EthernetClientInterface
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
            'CallInProgress': {'Status': {}},
            'EnableHeadset': {'Status': {}},
            'EnableUSBVideo': {'Status': {}},
            'FarEndAudioPresent': {'Status': {}},
            'LineFault': {'Status': {}},
            'MasterMicrophoneMute': {'Status': {}},
            'MicrophoneAudioPresent': {'Status': {}},
            }
        
        self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        self.Send('devio\r')

    def UpdateCallInProgress(self, value, qualifier):

        res = self.__UpdateHelper('CallInProgress', 'DEVICE get callInProgress\r' , value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('CallInProgress', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('CallInProgress', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateCallInProgress')

    def SetEnableHeadset(self, value, qualifier):

        States = {
            'True'  : 'DEVICE set enableHeadset true\r', 
            'False' : 'DEVICE set enableHeadset false\r', 
        }

        self.__SetHelper('EnableHeadset', States[value] , value, qualifier)
    def UpdateEnableHeadset(self, value, qualifier):

        res = self.__UpdateHelper('EnableHeadset', 'DEVICE get enableHeadset\r' , value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('EnableHeadset', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('EnableHeadset', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateEnableHeadset')

    def SetEnableUSBVideo(self, value, qualifier):

        States = {
            'True'  : 'DEVICE set enableUsbVideo true\r', 
            'False' : 'DEVICE set enableUsbVideo false\r', 
        }

        self.__SetHelper('EnableUSBVideo', States[value] , value, qualifier)
    def UpdateEnableUSBVideo(self, value, qualifier):

        res = self.__UpdateHelper('EnableUSBVideo', 'DEVICE get enableUsbVideo\r' , value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('EnableUSBVideo', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('EnableUSBVideo', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateEnableUSBVideo')

    def UpdateFarEndAudioPresent(self, value, qualifier):

        res = self.__UpdateHelper('FarEndAudioPresent', 'DEVICE get farEndAudioPresent\r', value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('FarEndAudioPresent', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('FarEndAudioPresent', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateFarEndAudioPresent')

    def UpdateLineFault(self, value, qualifier):

        res = self.__UpdateHelper('LineFault', 'DEVICE get lineFault\r' , value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('LineFault', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('LineFault', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateLineFault')

    def SetMasterMicrophoneMute(self, value, qualifier):

        States = {
            'True'  : 'DEVICE set masterMicMute true\r', 
            'False' : 'DEVICE set masterMicMute false\r', 
        }

        self.__SetHelper('MasterMicrophoneMute', States[value] , value, qualifier)
    def UpdateMasterMicrophoneMute(self, value, qualifier):

        res = self.__UpdateHelper('MasterMicrophoneMute', 'DEVICE get masterMicMute\r' , value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('MasterMicrophoneMute', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('MasterMicrophoneMute', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateMasterMicrophoneMute')

    def UpdateMicrophoneAudioPresent(self, value, qualifier):

        res = self.__UpdateHelper('MicrophoneAudioPresent', 'DEVICE get micAudioPresent\r' , value, qualifier)
        if res:
            try:
                if 'true' in res:
                    self.WriteStatus('MicrophoneAudioPresent', 'True', qualifier)  
                elif 'false' in res:
                    self.WriteStatus('MicrophoneAudioPresent', 'False', qualifier)  
            except:
                print('Invalid/unexpected response for UpdateMicrophoneAudioPresent')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if 'ERR' in response:
            print(response)
            return ''
        elif 'OK' in response:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command , res.decode())

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command , res.decode())

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
                
    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send('\r')
        return result
