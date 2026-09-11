# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SPInterface
from re import compile, search
from extronlib.system import Wait

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'LightColorConfiguration': {'Parameters':['Color', 'Brightness'], 'Status': {}},
            'LightColorStatus': { 'Status': {}},
            'LightColorBrightnessStatus': { 'Status': {}},       
            'LightColorControl': { 'Status': {}},        
            
        }

        self.VerboseDisabled = True
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'LiteC([A-F0-9a-f]{6})\*(\d+)\r\n'), self.__MatchLightColorStatus, None)
            self.AddMatchString(compile(b'LiteS([01])\r\n'), self.__MatchLightColorControl, None)
            self.AddMatchString(compile(b'E([0-3][0-8])\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
		
    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        
    def SetLightColorConfiguration(self, value, qualifier):
        if 0 <= qualifier['Brightness'] <= 100:
            LightColorConfigurationCmdString = 'wC{0}*{1}LITE|'.format(qualifier['Color'], qualifier['Brightness'])
            self.__SetHelper('LightColorConfiguration', LightColorConfigurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLightColorConfiguration')
            
    def UpdateLightColorBrightnessStatus(self, value, qualifier):
        LightColorBrightnessStatusCmdString = 'wCLITE|'
        self.__UpdateHelper('LightColorBrightnessStatus', LightColorBrightnessStatusCmdString, value, qualifier)

    def UpdateLightColorStatus(self, value, qualifier):
        LightColorStatusCmdString = 'wCLITE|'
        self.__UpdateHelper('LightColorStatus', LightColorStatusCmdString, value, qualifier)

    def __MatchLightColorStatus(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('LightColorStatus', value, None)
        value = int(match.group(2).decode())
        self.WriteStatus('LightColorBrightnessStatus', value, None)

    def SetLightColorControl(self, value, qualifier):
        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            LightColorControlCmdString = 'wS{}LITE|'.format(ValueStateValues[value])
            self.__SetHelper('LightColorControl', LightColorControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLightColorControl')

    def UpdateLightColorControl(self, value, qualifier):
        LightColorControlCmdString = 'wSLITE|'
        self.__UpdateHelper('LightColorControl', LightColorControlCmdString, value, qualifier)

    def __MatchLightColorControl(self, match, tag):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LightColorControl', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
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
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchErrors(self, match, tag):

            DEVICE_ERROR_CODES = {
                '01': 'Invalid input number (too large)',
                '10': 'Invalid command',
                '11': 'Invalid preset number',
                '12': 'Invalid output number or port number',
                '13': 'Invalid parameter (out of range)',
                '14': 'Command not available for this configuration',
                '17': 'System timed out (caused by direct write of global presets)',
                '21': 'Invalid room number',
                '22': 'Busy',
                '24': 'Privilege violation',
                '25': 'Device not present',
                '26': 'Maximum number of connections exceeded',
                '28': 'Bad filename or file not found'
            }
            self.counter = 0
            value = match.group(1).decode()
            if value in DEVICE_ERROR_CODES:
                self.Error([DEVICE_ERROR_CODES[value]])
            else:
                self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True
        
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
                result = search(regexString, self.__receiveBuffer)
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

class SPIClass(SPInterface, DeviceClass):

    def __init__(self, spd, Model=None):
        SPInterface.__init__(self, spd)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        print('Module: {}'.format(__name__), 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        self.OnDisconnected()

