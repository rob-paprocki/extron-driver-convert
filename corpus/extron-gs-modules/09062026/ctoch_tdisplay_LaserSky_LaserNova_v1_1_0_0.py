from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

class DeviceSerialClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}
        self._DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Screenshot': {'Status': {}},
            'Volume': {'Status': {}},
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 0 < int(value) < 256:
            self._DeviceID = int(value)
        else:
            print('Invalid DeviceID, range is from 1 to 255 (exclude 138 and 168) and Broadcast.')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        AudioMuteCmdString = pack('5B', 0xA9, 0x14, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
        }

        AudioMuteCmdString = pack('5B', 0xA9, 0x14, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        ExecutiveModeCmdString = pack('5B', 0xA9, 0x17, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        ExecutiveModeCmdString = pack('5B', 0xA9, 0x17, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        FreezeCmdString = pack('5B', 0xA9, 0x1B, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        FreezeCmdString = pack('5B', 0xA9, 0x1B, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 0x05,
            'HDMI 2': 0x06,
            'HDMI 3': 0x08,
            'HDMI 4 / RK Android': 0x0D,
            'DisplayPort': 0x07,
            'VGA': 0x14,
            'Inside PC': 0x09,
            'Home / COS': 0x0C
        }

        InputCmdString = pack('5B', 0xA9, 0x15, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x05': 'HDMI 1',
            b'\x06': 'HDMI 2',
            b'\x08': 'HDMI 3',
            b'\x0D': 'HDMI 4 / RK Android',
            b'\x07': 'DisplayPort',
            b'\x14': 'VGA',
            b'\x04': 'VGA',    # Device inhouse use \x04 for VGA (only update, set works fine)
            b'\x09': 'Inside PC',
            b'\x0C': 'Home / COS'
        }

        InputCmdString = pack('5B', 0xA9, 0x15, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x84,
            'Up': 0x92,
            'Down': 0xD8,
            'Left': 0x97,
            'Right': 0x9F,
            'Home': 0xBC,
            'Enter': 0x9B,
            'Exit': 0xD4
        }

        MenuNavigationCmdString = pack('5B', 0xA9, 0x16, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': 0x00,
            'Standard': 0x01,
            'Soft': 0x02,
            'User': 0x03,
            'Writing': 0x06
        }

        PictureModeCmdString = pack('5B', 0xA9, 0x18, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Dynamic',
            b'\x01': 'Standard',
            b'\x02': 'Soft',
            b'\x03': 'User',
            b'\x06': 'Writing'
        }

        PictureModeCmdString = pack('5B', 0xA9, 0x18, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('5B', 0xA9, 0x11, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
        }

        PowerCmdString = pack('5B', 0xA9, 0x11, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetScreenshot(self, value, qualifier):

        ScreenshotCmdString = pack('5B', 0xA9, 0x16, self._DeviceID, 0x62, 0x8A)
        self.__SetHelper('Screenshot', ScreenshotCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('5B', 0xA9, 0x13, self._DeviceID, value, 0x8A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = pack('5B', 0xA9, 0x13, self._DeviceID, 0xAA, 0x8A)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x01': 'Invalid Command',
            b'\x02': 'Invalid Data',
            b'\xFF': 'Unknown Error',
        }
        if response[1:2] == b'\x4E':
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x8A')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x8A')
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


class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self.deviceUsername = 'Username'
        self.devicePassword = None
        self.Models = {}
        self._DeviceID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Screenshot': { 'Status': {}},
            'Volume': { 'Status': {}},
            }



    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 0 < int(value) < 256:
            self._DeviceID = int(value)
        else:
            print('Invalid DeviceID, range is from 1 to 255 (exclude 138 and 168) and Broadcast.')


    def SetAudioMute(self, value, qualifier):
        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
        }

        AudioMuteCmdString = pack('5B', 0xA9, 0x14, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
        }

        ExecutiveModeCmdString = pack('5B', 0xA9, 0x17, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
        }

        FreezeCmdString = pack('5B', 0xA9, 0x1B, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'              : 0x05, 
            'HDMI 2'              : 0x06,
            'HDMI 3'              : 0x08, 
            'HDMI 4 / RK Android' : 0x0D, 
            'DisplayPort'         : 0x07, 
            'VGA'                 : 0x14, 
            'Inside PC'           : 0x09, 
            'Home / COS'          : 0x0C
        }

        InputCmdString = pack('5B', 0xA9, 0x15, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 0x84, 
            'Up'    : 0x92, 
            'Down'  : 0xD8, 
            'Left'  : 0x97, 
            'Right' : 0x9F, 
            'Home'  : 0xBC, 
            'Enter' : 0x9B, 
            'Exit'  : 0xD4
        }

        MenuNavigationCmdString = pack('5B', 0xA9, 0x16, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic'  : 0x00, 
            'Standard' : 0x01, 
            'Soft'     : 0x02, 
            'User'     : 0x03, 
            'Writing'  : 0x06
        }

        PictureModeCmdString = pack('5B', 0xA9, 0x18, self._DeviceID, ValueStateValues[value], 0x8A)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = pack('5B', 0xA9, 0x11, self._DeviceID, 0x00, 0x8A)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)
    def SetScreenshot(self, value, qualifier):

        ScreenshotCmdString = pack('5B', 0xA9, 0x16, self._DeviceID, 0x62, 0x8A)
        self.__SetHelper('Screenshot', ScreenshotCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = pack('5B', 0xA9, 0x13, self._DeviceID, value, 0x8A)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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
