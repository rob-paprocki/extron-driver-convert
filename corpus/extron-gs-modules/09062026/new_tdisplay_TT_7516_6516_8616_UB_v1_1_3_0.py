from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack

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
            'AutoImage': { 'Status': {}},
            'EcoMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'MuteStatus': { 'Status': {}},
            'Power': { 'Status': {}},
            'Screenshot': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Whiteboard': { 'Status': {}},
            'WiFi': { 'Status': {}},
        }

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x20\xCF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Standard' : b'\x00', 
            'ECO'      : b'\x01', 
            'Auto'     : b'\x02'
        }

        EcoModeCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x06', ValueStateValues[value], b'\xCF'])
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        ValueStateValues = {
            0 : 'Standard', 
            1 : 'ECO', 
            2 : 'Auto'
        }

        EcoModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x35\xCF'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['EcoMode: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x3B\xCF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'        : b'\x0A', 
            'HDMI 2'        : b'\x0B', 
            'HDMI 3'        : b'\x0C', 
            'HDMI 4'        : b'\x51', 
            'OPS'           : b'\x38', 
            'DisplayPort'   : b'\x56', 
            'VGA'           : b'\x0D', 
            'Video'         : b'\x11'
        }

        InputCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01', ValueStateValues[value], b'\xCF'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            23 : 'HDMI 1', 
            24 : 'HDMI 2', 
            32 : 'HDMI 3', 
            81 : 'HDMI 4', 
            25 : 'OPS', 
            86 : 'DisplayPort', 
            0  : 'VGA', 
            2  : 'Video'
        }

        InputCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x32\xCF'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        
        ValueStateValues = {
            '1' : b'\x21', 
            '2' : b'\x22', 
            '3' : b'\x23', 
            '4' : b'\x24', 
            '5' : b'\x25', 
            '6' : b'\x26', 
            '7' : b'\x27', 
            '8' : b'\x28', 
            '9' : b'\x29', 
            '0' : b'\x2A'
        }

        KeypadCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01', ValueStateValues[value], b'\xCF'])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):
        
        ValueStateValues = {
            'Up'       : b'\x2E', 
            'Down'     : b'\x2F', 
            'Left'     : b'\x2C', 
            'Right'    : b'\x2D', 
            'Ok'       : b'\x2B', 
            'Menu'     : b'\x1B', 
            'Back'     : b'\x1D', 
            'Home'     : b'\x1C',
            'Page Up'  : b'\x13',
            'Page Down': b'\x14'
        }

        MenuNavigationCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01', ValueStateValues[value], b'\xCF'])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):
        
        MuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x02\xCF'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMuteStatus(self, value, qualifier):

        self.UpdateVolume(value, qualifier)

    def SetPower(self, value, qualifier):
        
        ValueStateValues = {
            'On'  : b'\x00', 
            'Off' : b'\x01'
        }

        PowerCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01', ValueStateValues[value], b'\xCF'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        PowerCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x37\xCF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetScreenshot(self, value, qualifier):

        ScreenshotCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1F\xCF'
        self.__SetHelper('Screenshot', ScreenshotCmdString, value, qualifier)

    def SetSoundMode(self, value, qualifier):

        ValueStateValues = {
            'Standard'   : b'\x00', 
            'Music'      : b'\x01', 
            'Movie'      : b'\x02', 
            'News'       : b'\x03', 
            'User'       : b'\x04', 
            'Surround 1' : b'\x05', 
            'Surround 2' : b'\x06'
        }

        SoundModeCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x03', ValueStateValues[value], b'\xCF'])
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)

    def UpdateSoundMode(self, value, qualifier):

        ValueStateValues = {
            0 : 'Standard',
            1 : 'Music', 
            2 : 'Movie', 
            3 : 'News', 
            4 : 'User', 
            5 : 'Surround 1', 
            6 : 'Surround 2'
        }

        SoundModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x34\xCF'
        res = self.__UpdateHelper('SoundMode', SoundModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('SoundMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['SoundMode: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):
        
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b''.join([b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x05', bytes([value]), b'\xCF'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        
        VolumeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x33\xCF'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[-2]
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

            try:
                value = res[-2]
                if value == 0:
                    self.WriteStatus('MuteStatus', 'On', None)
                else:
                    self.WriteStatus('MuteStatus', 'Off', None)
            except (KeyError, IndexError):
                self.Error(['MuteStatus: Invalid/unexpected response'])

    def SetWhiteboard(self, value, qualifier):
        
        WhiteboardCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x07\xCF'
        self.__SetHelper('Whiteboard', WhiteboardCmdString, value, qualifier)

    def SetWiFi(self, value, qualifier):
        
        WiFiCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x04\xCF'
        self.__SetHelper('WiFi', WiFiCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(commandstring, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
            if not res:
                return ''
            else:
               return self.__CheckResponseForErrors(commandstring, res)

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