from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import unpack

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
        self.Models = {
            'SDP-960': self.smsg_16_253_960,
            'SDP-860': self.smsg_16_253_860,
            }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Capture': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Lamp': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mode': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Rotate': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }
    
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA0\x60\x06([\x00-\xFF]{6})\xAF'), self.__MatchPower, None)
            
    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\xA0\x02\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        
    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\xA0\x21\x00\x05\x00\x00\x00\x00\x00\xAF', 
            'Down' : b'\xA0\x21\x00\x0A\x00\x00\x00\x00\x00\xAF'
        }

        BrightnessCmdString = ValueStateValues[value]
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        
    def SetCapture(self, value, qualifier):

        ValueStateValues = {
            'Picture' : b'\xA0\x07\x00\x00\x00\x00\x00\x00\x00\xAF', 
            'Movie'   : b'\xA0\x08\x00\x00\x00\x00\x00\x00\x00\xAF'
        }

        CaptureCmdString = ValueStateValues[value]
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)
        
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : b'\xA0\x25\x00\x05\x00\x00\x00\x00\x00\xAF', 
            'Near' : b'\xA0\x25\x00\x0A\x00\x00\x00\x00\x00\xAF', 
            'Stop' : b'\xA0\x2F\x00\x00\x00\x00\x00\x00\x00\xAF'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        
    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\xA0\x05\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = b'\xA0\x04\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLamp(self, value, qualifier):

        LampCmdString = self.lampCommandString
        self.__SetHelper('Lamp', LampCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\xA0\x0B\x00\x00\x00\x00\x00\x00\x00\xAF', 
            'Down'  : b'\xA0\x0C\x00\x00\x00\x00\x00\x00\x00\xAF', 
            'Left'  : b'\xA0\x0E\x00\x00\x00\x00\x00\x00\x00\xAF', 
            'Right' : b'\xA0\x0D\x00\x00\x00\x00\x00\x00\x00\xAF', 
            'Set'   : b'\xA0\x0A\x00\x00\x00\x00\x00\x00\x00\xAF', 
            'Exit'  : b'\xA0\x06\x00\x00\x00\x00\x00\x00\x00\xAF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        
    def SetMode(self, value, qualifier):

        ModeCmdString = b'\xA0\x09\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x6F\x00\x05\x00\x00\x00\x00\x00\xAF', 
            'Off' : b'\xA0\x6F\x00\x0A\x00\x00\x00\x00\x00\xAF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xA0\x60\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateNames = {
            0x01 : 'On', 
            0x00 : 'Off'
        }
        FreezeStateNames = {
            0x80: 'On',
            0x00: 'Off'
        }
        LampStateNames = {
            0x40: 'On',
            0x00: 'Off'
        }
        ModeStateNames = {
            0x00: 'Live',
            0x40: 'PIC Viewer',
            0x80: 'MOV Viewer'
        }
        RotateStateNames = {
            0x00: 'Off',
            0x01: '90 Degrees',
            0x02: '180 Degrees',
            0x03: '270 Degrees'
        }

        try:
            value = PowerStateNames[unpack('B', match.group(1)[4:5])[0] & 0x01]
            self.WriteStatus('Power', value, None)
        except (KeyError, IndexError):
            self.Error(['Power: Invalid/Unexpected response'])
        try:
            value = FreezeStateNames[unpack('B', match.group(1)[4:5])[0] & 0x80]
            self.WriteStatus('Freeze', value, None)
        except (KeyError, IndexError):
            self.Error(['Freeze: Invalid/Unexpected response'])
        try:
            value = LampStateNames[unpack('B', match.group(1)[4:5])[0] & 0x40]
            self.WriteStatus('Lamp', value, None)
        except (KeyError, IndexError):
            self.Error(['Lamp: Invalid/Unexpected response'])
        try:
            value = self.InputStateNames[unpack('B', match.group(1)[4:5])[0] & self.InputVal]
            self.WriteStatus('Input', value, None)
        except (KeyError, IndexError):
            self.Error(['Input: Invalid/Unexpected response'])
        try:
            value = ModeStateNames[unpack('>B', match.group(1)[0:1])[0] & 0xC0]
            self.WriteStatus('Mode', value, None)
        except (KeyError, IndexError):
            self.Error(['Mode: Invalid/Unexpected response'])
        try:
            value = RotateStateNames[unpack('>B', match.group(1)[3:4])[0] & 0x03]
            self.WriteStatus('Rotate', value, None)
        except (KeyError, IndexError):
            self.Error(['Rotate: Invalid/Unexpected response'])
            
    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\xA0\x18\x00\x01\x00\x00\x00\x00\x00\xAF', 
            '2' : b'\xA0\x18\x00\x02\x00\x00\x00\x00\x00\xAF', 
            '3' : b'\xA0\x18\x00\x03\x00\x00\x00\x00\x00\xAF', 
            '4' : b'\xA0\x18\x00\x04\x00\x00\x00\x00\x00\xAF'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        
    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : b'\xA0\x17\x00\x01\x00\x00\x00\x00\x00\xAF', 
            '2' : b'\xA0\x17\x00\x02\x00\x00\x00\x00\x00\xAF', 
            '3' : b'\xA0\x17\x00\x03\x00\x00\x00\x00\x00\xAF', 
            '4' : b'\xA0\x17\x00\x04\x00\x00\x00\x00\x00\xAF'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        
    def SetRotate(self, value, qualifier):

        ValueStateValues = {
            'Off'         : b'\xA0\x11\x00\x05\x00\x00\x00\x00\x00\xAF', 
            '90 Degrees'  : b'\xA0\x11\x00\x08\x00\x00\x00\x00\x00\xAF', 
            '180 Degrees' : b'\xA0\x11\x00\x0A\x00\x00\x00\x00\x00\xAF', 
            '270 Degrees' : b'\xA0\x11\x00\x0D\x00\x00\x00\x00\x00\xAF'
        }

        RotateCmdString = ValueStateValues[value]
        self.__SetHelper('Rotate', RotateCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Far'  : b'\xA0\x26\x00\x05\x00\x00\x00\x00\x00\xAF', 
            'Near' : b'\xA0\x26\x00\x0A\x00\x00\x00\x00\x00\xAF', 
            'Stop' : b'\xA0\x2F\x00\x00\x00\x00\x00\x00\x00\xAF'
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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def smsg_16_253_960(self):
        
        self.lampCommandString = b'\xA0\x03\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.InputVal = 0x20
        self.InputStateNames = {
            0x00: 'Internal',
            0x04: 'External 1',
            0x08: 'External 2'
        }
        
    def smsg_16_253_860(self):
        
        self.lampCommandString = b'\xA0\x04\x00\x00\x00\x00\x00\x00\x00\xAF'
        self.InputVal = 0x0C
        self.InputStateNames = {
            0x00: 'Internal',
            0x20: 'External'
        }
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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

