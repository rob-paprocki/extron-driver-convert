from extronlib.interface import SerialInterface, EthernetClientInterface


class DeviceSerialClass:

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

        self._DeviceID = '00'

        self.Models = {
            'DU4671Z': self.vvtk_1_3231_1Z,
            'DX4630Z': self.vvtk_1_3231_0Z,
            'DW4650Z': self.vvtk_1_3231_0Z,
            'DH4661Z': self.vvtk_1_3231_1Z,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DSyncInvert': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Gamma': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 0 <= int(value) <= 98:
            self._DeviceID = value.zfill(2)

    def Set3D(self, value, qualifier):

        state = {'Off': '0', 'DLP-Link': '1', 'IR': '2'}[value]
        self.__SetHelper('3D', 'V{}S0315{}\r'.format(self.DeviceID, state), value, qualifier)

    def Update3D(self, value, qualifier):

        res = self.__UpdateHelper('3D', 'V{}G0315\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'0': 'Off', '1': 'DLP-Link', '2': 'IR'}[res[1]]
                self.WriteStatus('3D', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3D: Invalid/unexpected response'])

    def Set3DFormat(self, value, qualifier):

        state = {'Frame Sequential': '0', 'Top/Bottom': '1', 'Side-By-Side': '2', 'Frame Packing': '3'}[value]
        self.__SetHelper('3DFormat', 'V{}S0317{}\r'.format(self.DeviceID, state), value, qualifier)

    def Update3DFormat(self, value, qualifier):

        res = self.__UpdateHelper('3DFormat', 'V{}G0317\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'0': 'Frame Sequential', '1': 'Top/Bottom', '2': 'Side-By-Side', '3': 'Frame Packing'}[res[1]]
                self.WriteStatus('3DFormat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3DFormat: Invalid/unexpected response'])

    def Set3DSyncInvert(self, value, qualifier):

        state = {'On': '1', 'Off': '0'}[value]
        self.__SetHelper('3DSyncInvert', 'V{}S0316{}\r'.format(self.DeviceID, state), value, qualifier)

    def Update3DSyncInvert(self, value, qualifier):

        res = self.__UpdateHelper('3DSyncInvert', 'V{}G0316\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'1': 'On', '0': 'Off'}[res[1]]
                self.WriteStatus('3DSyncInvert', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['3DSyncInvert: Invalid/unexpected response'])

    def SetAspectRatio(self, value, qualifier):

        state = {'Fill': '0', '4:3': '1', '16:9': '2', 'Letterbox': '3', 'Native': '4', '2.35:1': '5'}[value]
        self.__SetHelper('AspectRatio', 'V{}S0301{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        res = self.__UpdateHelper('AspectRatio', 'V{}G0301\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'0': 'Fill', '1': '4:3', '2': '16:9', '3': 'Letterbox', '4': 'Native', '5': '2.35:1'}[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AspectRatio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'V{}S0003\r'.format(self.DeviceID), value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        state = {'Presentation': '0', 'Bright': '1', 'Game': '2', 'Movie': '3', 'Vivid': '4', 'TV': '5',
                 'sRGB': '6', 'DICOM SIM': '8', 'User': '9', 'User 2': '10'}[value]
        self.__SetHelper('DisplayMode', 'V{}S0108{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):

        res = self.__UpdateHelper('DisplayMode', 'V{}G0108\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'0': 'Presentation', '1': 'Bright', '2': 'Game', '3': 'Movie', '4': 'Vivid', '5': 'TV',
                         '6': 'sRGB', '8': 'DICOM SIM', '9': 'User', '10': 'User 2'}[res[1:-1]]
                self.WriteStatus('DisplayMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['DisplayMode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', 'V{}G0005\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['FilterUsage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        state = {'On': '1', 'Off': '0'}[value]
        self.__SetHelper('Freeze', 'V{}S0304{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        res = self.__UpdateHelper('Freeze', 'V{}G0304\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'1': 'On', '0': 'Off'}[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetGamma(self, value, qualifier):

        state = {'1.8': '0', '2.0': '1', '2.2': '2', '2.4': '3', 'B&W': '4', 'Linear': '5'}[value]
        self.__SetHelper('Gamma', 'V{}S0107{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateGamma(self, value, qualifier):

        res = self.__UpdateHelper('Gamma', 'V{}G0107\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'0': '1.8', '1': '2.0', '2': '2.2', '3': '2.4', '4': 'B&W', '5': 'Linear'}[res[1]]
                self.WriteStatus('Gamma', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Gamma: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        state = self.input_states[value]
        self.__SetHelper('Input', 'V{}S02{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateInput(self, value, qualifier):

        res = self.__UpdateHelper('Input', 'V{}G0220\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = self.input_values[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        state = {'Normal': '0', 'Eco': '1', 'Eco Plus': '2', 'Dimming': '3',
                 'Extreme Dimming': '4', 'Custom Light': '5'}[value]
        self.__SetHelper('LampMode', 'V{}S0319{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        res = self.__UpdateHelper('LampMode', 'V{}G0319\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'0': 'Normal', '1': 'Eco', '2': 'Eco Plus', '3': 'Dimming', '4': 'Extreme Dimming',
                         '5': 'Custom Light'}[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LampMode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', 'V{}G0004\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['LampUsage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        state = {'On': '1', 'Off': '2'}[value]
        self.__SetHelper('Power', 'V{}S000{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdatePower(self, value, qualifier):

        res = self.__UpdateHelper('Power', 'V{}G0007\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'2': 'On', '1': 'Off', '0': 'Reset', '3': 'Cooling Down'}[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        state = {'On': '1', 'Off': '0'}[value]
        self.__SetHelper('VideoMute', 'V{}S0302{}\r'.format(self.DeviceID, state), value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        res = self.__UpdateHelper('VideoMute', 'V{}G0302\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = {'1': 'On', '0': 'Off'}[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['VideoMute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 10:
            self.__SetHelper('Volume', 'V{}S0305{}\r'.format(self.DeviceID, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', 'V{}G0305\r'.format(self.DeviceID), value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'F\r': 'Fail'}
        if response in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self.DeviceID == '99':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '99':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def vvtk_1_3231_1Z(self):

        self.input_states = {
            'RGB':          '01',
            'DVI':          '03',
            'Video':        '04',
            'HDMI 1':       '06',
            'BNC':          '07',
            'HDMI 2':       '09',
            'HDMI 3 / MHL': '12',
            'HDBaseT':      '15',
        }

        self.input_values = {
            '1':  'RGB',
            '3':  'DVI',
            '4':  'Video',
            '6':  'HDMI 1',
            '7':  'BNC',
            '9':  'HDMI 2',
            '12': 'HDMI 3 / MHL',
            '15': 'HDBaseT',
        }

    def vvtk_1_3231_0Z(self):

        self.input_states = {
            'RGB':          '01',
            'DVI':          '03',
            'Video':        '04',
            'HDMI 1':       '06',
            'BNC':          '07',
            'HDMI 2':       '09',
            'HDMI 3 / MHL': '12',
        }

        self.input_values = {
            '1':  'RGB',
            '3':  'DVI',
            '4':  'Video',
            '6':  'HDMI 1',
            '7':  'BNC',
            '9':  'HDMI 2',
            '12': 'HDMI 3 / MHL',
        }

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
        self._DeviceID = '00'

        self.Models = {
            'DH4661Z': self.vvtk_1_3231_1Z,
            'DU4671Z': self.vvtk_1_3231_1Z,
            'DW4650Z': self.vvtk_1_3231_0Z,
            'DX4630Z': self.vvtk_1_3231_0Z,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': { 'Status': {}},
            '3DFormat': { 'Status': {}},
            '3DSyncInvert': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Gamma': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'Shutdown': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 0 <= int(value) <= 98:
            self._DeviceID = value.zfill(2)

    def Set3D(self, value, qualifier):

        state = {'Off': '0', 'DLP-Link': '1', 'IR': '2'}[value]
        self.__SetHelper('3D', 'V{}S0315{}\r'.format(self.DeviceID, state), value, qualifier)
    def Set3DFormat(self, value, qualifier):

        state = {'Frame Sequential': '0', 'Top/Bottom': '1', 'Side-By-Side': '2', 'Frame Packing': '3'}[value]
        self.__SetHelper('3DFormat', 'V{}S0317{}\r'.format(self.DeviceID, state), value, qualifier)
    def Set3DSyncInvert(self, value, qualifier):

        state = {'On': '1', 'Off': '0'}[value]
        self.__SetHelper('3DSyncInvert', 'V{}S0316{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetAspectRatio(self, value, qualifier):

        state = {'Fill': '0', '4:3': '1', '16:9': '2', 'Letterbox': '3', 'Native': '4', '2.35:1': '5'}[value]
        self.__SetHelper('AspectRatio', 'V{}S0301{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'V{}S0003\r'.format(self.DeviceID), value, qualifier)
    def SetDisplayMode(self, value, qualifier):

        state = {'Presentation': '0', 'Bright': '1', 'Game': '2', 'Movie': '3', 'Vivid': '4', 'TV': '5',
                 'sRGB': '6', 'DICOM SIM': '8', 'User': '9', 'User 2': '10'}[value]
        self.__SetHelper('DisplayMode', 'V{}S0108{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetFreeze(self, value, qualifier):

        state = {'On': '1', 'Off': '0'}[value]
        self.__SetHelper('Freeze', 'V{}S0304{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetGamma(self, value, qualifier):

        state = {'1.8': '0', '2.0': '1', '2.2': '2', '2.4': '3', 'B&W': '4', 'Linear': '5'}[value]
        self.__SetHelper('Gamma', 'V{}S0107{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetInput(self, value, qualifier):

        state = self.input_states[value]
        self.__SetHelper('Input', 'V{}S02{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetLampMode(self, value, qualifier):

        state = {'Normal': '0', 'Eco': '1', 'Eco Plus': '2', 'Dimming': '3',
                 'Extreme Dimming': '4', 'Custom Light': '5'}[value]
        self.__SetHelper('LampMode', 'V{}S0319{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetShutdown(self, value, qualifier):

        self.__SetHelper('Shutdown', 'V{}S0002\r'.format(self.DeviceID), value, qualifier)
    def SetVideoMute(self, value, qualifier):

        state = {'On': '1', 'Off': '0'}[value]
        self.__SetHelper('VideoMute', 'V{}S0302{}\r'.format(self.DeviceID, state), value, qualifier)
    def SetVolume(self, value, qualifier):

        if 0 <= value <= 10:
            self.__SetHelper('Volume', 'V{}S0305{}\r'.format(self.DeviceID, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def vvtk_1_3231_1Z(self):

        self.input_states = {
            'RGB':          '01',
            'DVI':          '03',
            'Video':        '04',
            'HDMI 1':       '06',
            'BNC':          '07',
            'HDMI 2':       '09',
            'HDMI 3 / MHL': '12',
            'HDBaseT':      '15',
        }

    def vvtk_1_3231_0Z(self):

        self.input_states = {
            'RGB':          '01',
            'DVI':          '03',
            'Video':        '04',
            'HDMI 1':       '06',
            'BNC':          '07',
            'HDMI 2':       '09',
            'HDMI 3 / MHL': '12',
        }

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