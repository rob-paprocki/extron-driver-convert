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
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoColor': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Frequency': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampControl': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Zoom': { 'Status': {}},
        } 
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xB0\x62\x80([\x00-\xFF])[\x00-\xFF]\xBF'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\xB0\x61\x80([\x00-\xFF])([\x00-\xFF])\xBF'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xB0([\x00-\xFF])[\x00-\x79][\x00-\xFF][\x00-\xFF]\xBF'), self.__MatchError, None)

    def SetAutoColor(self, value, qualifier):

        AutoColorCmdString = b'\xB0\x01\x00\x05\x00\xBF'
        self.__SetHelper('AutoColor', AutoColorCmdString, value, qualifier)
    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\xB0\x02\x00\x05\x00\xBF'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':  b'\xB0\x25\x00\x05\x00\xBF',
            'Near': b'\xB0\x25\x00\x0A\x00\xBF',
            'Stop': b'\xB0\x2F\x00\x05\x00\xBF'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\xB0\x12\x00\x05\x00\xBF',
            'Off':  b'\xB0\x12\x00\x0A\x00\xBF'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = b'\xB0\x62\x00\x00\x00\xBF'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        msb = '{:08b}'.format(match.group(1)[0])
        value = ValueStateValues[msb[1]]
        self.WriteStatus('Freeze', value, None)

    def SetFrequency(self, value, qualifier):

        ValueStateValues = {
            '60Hz': b'\xB0\x0A\x00\x0A\x00\xBF',
            '75Hz': b'\xB0\x0A\x00\x05\x00\xBF'
        }

        FrequencyCmdString = ValueStateValues[value]
        self.__SetHelper('Frequency', FrequencyCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Internal': b'\xB0\x04\x00\x05\x00\xBF',
            'External': b'\xB0\x04\x00\x0A\x00\xBF',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampControl(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\xB0\x03\x00\x05\x00\xBF',
            'Off':  b'\xB0\x03\x00\x0A\x00\xBF'
        }

        LampControlCmdString = ValueStateValues[value]
        self.__SetHelper('LampControl', LampControlCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\xB0\x0F\x00\x05\x00\xBF',
            'Off':  b'\xB0\x0F\x00\x0A\x00\xBF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        PowerCmdString = b'\xB0\x61\x00\x00\x00\xBF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):


        FrequencyStateValues = {
            '1': '60Hz',
            '0': '75Hz'
        }

        InputStateValues = {
            ('0', '0', '0'): 'Internal',
            ('1', '1', '1'): 'External',
            ('1', '0', '1'): 'No Signal'
        }

        LampControlStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        msb = '{:08b}'.format(match.group(1)[0])
        lsb = '{:08b}'.format(match.group(2)[0])

        self.WriteStatus('Frequency', FrequencyStateValues[msb[4]], None)
        self.WriteStatus('Input', InputStateValues[(lsb[1], lsb[2], lsb[3])], None)
        self.WriteStatus('LampControl', LampControlStateValues[lsb[5]], None)
        self.WriteStatus('Power', PowerStateValues[msb[6]], None)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\xB0\x18\x00\x01\x00\xBF',
            '2': b'\xB0\x18\x00\x02\x00\xBF',
            '3': b'\xB0\x18\x00\x03\x00\xBF',
            '4': b'\xB0\x18\x00\x04\x00\xBF'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\xB0\x17\x00\x01\x00\xBF',
            '2': b'\xB0\x17\x00\x02\x00\xBF',
            '3': b'\xB0\x17\x00\x03\x00\xBF',
            '4': b'\xB0\x17\x00\x04\x00\xBF'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': b'\xB0\x26\x00\x05\x00\xBF',
            'Wide': b'\xB0\x26\x00\x0A\x00\xBF',
            'Stop': b'\xB0\x2F\x00\x05\x00\xBF'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



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

            self.Send(commandstring)            

    def __MatchError(self, match, tag):
        self.counter = 0

        command_map = {
            b'\x01': 'Auto Color',
            b'\x02': 'Auto Focus',
            b'\x25': 'Focus',
            b'\x12': 'Freeze',
            b'\x0A': 'Frequency',
            b'\x04': 'Input',
            b'\x03': 'Lamp Control',
            b'\x0F': 'Power',
            b'\x18': 'Preset Recall',
            b'\x17': 'Preset Save',
            b'\x26': 'Zoom',
            b'\x2D': 'Focus/Zoom',
            b'\x61': 'Power',
            b'\x62': 'Freeze'
        }

        self.Error(['An error occurred: {}.'.format(command_map.get(match.group(1), 'Unknown command'))])

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

