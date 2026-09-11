from extronlib.interface import SerialInterface, EthernetClientInterface
from functools import reduce
from operator import add

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
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ClosedCaptionAnalog': { 'Status': {}},
            'ClosedCaptionDigital': { 'Status': {}},
            'ClosedCaptionMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom' : b'\x8C\x00\x44\x03\x01\x00', 
            'Full'      : b'\x8C\x00\x44\x03\x01\x01', 
            'Zoom'      : b'\x8C\x00\x44\x03\x01\x02', 
            'Normal'    : b'\x8C\x00\x44\x03\x01\x03', 
            'PC Normal' : b'\x8C\x00\x44\x03\x01\x05', 
            'PC Full 1' : b'\x8C\x00\x44\x03\x01\x06', 
            'PC Full 2' : b'\x8C\x00\x44\x03\x01\x07'
        }
        AspectRatioCmdString = ValueStateValues[value]
        AspectRatioCmdString += (reduce(add,AspectRatioCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x8C\x00\x06\x03\x01\x01', 
            'Off' : b'\x8C\x00\x06\x03\x01\x00'
        }
        AudioMuteCmdString = ValueStateValues[value]
        AudioMuteCmdString += (reduce(add,AudioMuteCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        
    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off', 
        }

        AudioMuteCmdString = b'\x83\x00\x06\xFF\xFF'
        AudioMuteCmdString += (reduce(add,AudioMuteCmdString) & 255).to_bytes(1,'big')
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x8C\x00\x67\x03\x01\x10', 
            'Down' : b'\x8C\x00\x67\x03\x01\x11'
        }
        ChannelCmdString = ValueStateValues[value]
        ChannelCmdString += (reduce(add,ChannelCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        
    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC 1'   : b'\x8C\x00\x10\x04\x02\x00\x01', 
            'CC 2'   : b'\x8C\x00\x10\x04\x02\x00\x02', 
            'CC 3'   : b'\x8C\x00\x10\x04\x02\x00\x03', 
            'CC 4'   : b'\x8C\x00\x10\x04\x02\x00\x04', 
            'Text 1' : b'\x8C\x00\x10\x04\x02\x00\x05', 
            'Text 2' : b'\x8C\x00\x10\x04\x02\x00\x06', 
            'Text 3' : b'\x8C\x00\x10\x04\x02\x00\x07', 
            'Text 4' : b'\x8C\x00\x10\x04\x02\x00\x08'
        }
        ClosedCaptionAnalogCmdString = ValueStateValues[value]
        ClosedCaptionAnalogCmdString += (reduce(add,ClosedCaptionAnalogCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)
        
    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'Service 1' : b'\x8C\x00\x10\x04\x02\x01\x01', 
            'Service 2' : b'\x8C\x00\x10\x04\x02\x01\x02', 
            'Service 3' : b'\x8C\x00\x10\x04\x02\x01\x03', 
            'Service 4' : b'\x8C\x00\x10\x04\x02\x01\x04', 
            'Service 5' : b'\x8C\x00\x10\x04\x02\x01\x05', 
            'Service 6' : b'\x8C\x00\x10\x04\x02\x01\x06', 
            'CC 1'      : b'\x8C\x00\x10\x04\x02\x01\x07', 
            'CC 2'      : b'\x8C\x00\x10\x04\x02\x01\x08', 
            'CC 3'      : b'\x8C\x00\x10\x04\x02\x01\x09', 
            'CC 4'      : b'\x8C\x00\x10\x04\x02\x01\x0A'
        }
        ClosedCaptionDigitalCmdString = ValueStateValues[value]
        ClosedCaptionDigitalCmdString += (reduce(add,ClosedCaptionDigitalCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)
        
    def SetClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x8C\x00\x10\x03\x01\x01', 
            'Off' : b'\x8C\x00\x10\x03\x01\x00'
        }
        ClosedCaptionModeCmdString = ValueStateValues[value]
        ClosedCaptionModeCmdString += (reduce(add,ClosedCaptionModeCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV'           : b'\x8C\x00\x02\x02\x01', 
            'Video'        : b'\x8C\x00\x02\x03\x02\x01', 
            'Component'    : b'\x8C\x00\x02\x03\x03\x01', 
            'HDMI 1'       : b'\x8C\x00\x02\x03\x04\x01', 
            'HDMI 2'       : b'\x8C\x00\x02\x03\x04\x02', 
            'HDMI 3'       : b'\x8C\x00\x02\x03\x04\x03', 
            'HDMI 4'       : b'\x8C\x00\x02\x03\x04\x04', 
            'Shared Input' : b'\x8C\x00\x02\x03\x07\x01'
        }
        InputCmdString = ValueStateValues[value]
        InputCmdString += (reduce(add,InputCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('Input', InputCmdString, value, qualifier)
        
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'\x02\x01' : 'Video', 
            b'\x03\x01' : 'Component', 
            b'\x04\x01' : 'HDMI 1', 
            b'\x04\x02' : 'HDMI 2', 
            b'\x04\x03' : 'HDMI 3', 
            b'\x04\x04' : 'HDMI 4', 
            b'\x07\x01' : 'Shared Input'
        }

        InputCmdString = b'\x83\x00\x02\xFF\xFF'
        InputCmdString += (reduce(add,InputCmdString) & 255).to_bytes(1,'big')
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[3] == 1:
                    self.WriteStatus('Input', 'TV', qualifier)
                else:
                    value = ValueStateValues[res[3:5]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : b'\x8C\x00\x67\x03\x01\x09', 
            '1' : b'\x8C\x00\x67\x03\x01\x00', 
            '2' : b'\x8C\x00\x67\x03\x01\x01', 
            '3' : b'\x8C\x00\x67\x03\x01\x02', 
            '4' : b'\x8C\x00\x67\x03\x01\x03', 
            '5' : b'\x8C\x00\x67\x03\x01\x04', 
            '6' : b'\x8C\x00\x67\x03\x01\x05', 
            '7' : b'\x8C\x00\x67\x03\x01\x06', 
            '8' : b'\x8C\x00\x67\x03\x01\x07', 
            '9' : b'\x8C\x00\x67\x03\x01\x08',
            'Dot' : b'\x8C\x00\x67\x03\x97\x1D',
        }
        KeypadCmdString = ValueStateValues[value]
        KeypadCmdString += (reduce(add,KeypadCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home'   : b'\x8C\x00\x67\x03\x01\x60', 
            'Up'     : b'\x8C\x00\x67\x03\x01\x74', 
            'Down'   : b'\x8C\x00\x67\x03\x01\x75', 
            'Left'   : b'\x8C\x00\x67\x03\x01\x34', 
            'Right'  : b'\x8C\x00\x67\x03\x01\x33', 
            'Select' : b'\x8C\x00\x67\x03\x01\x65', 
            'Return' : b'\x8C\x00\x67\x03\x97\x23'
        }
        MenuNavigationCmdString = ValueStateValues[value]
        MenuNavigationCmdString += (reduce(add,MenuNavigationCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : (b'\x8C\x00\x00\x02\x01', 20), # BRAVIA_RS232C_Protocol_Manual_1.00.pdf page 4 and 12
            'Off' : (b'\x8C\x00\x00\x02\x00', 5)
        }
        
        PowerCmdString = ValueStateValues[value][0]
        PowerCmdString += (reduce(add,PowerCmdString) & 255).to_bytes(1,'big')
        if value == 'Off':
            self.__SetHelper('Power', b'\x8C\x00\x01\x02\x01\x90', value, qualifier)  # Send Standby Command, based on customer test (Sony PWR off.png)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }
        PowerCmdString = b'\x83\x00\x00\xFF\xFF'
        PowerCmdString += (reduce(add,PowerCmdString) & 255).to_bytes(1,'big')
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x8C\x00\x0D\x03\x01\x01', 
            'Off' : b'\x8C\x00\x0D\x03\x01\x00'
        }
        VideoMuteCmdString = ValueStateValues[value]
        VideoMuteCmdString += (reduce(add,VideoMuteCmdString) & 255).to_bytes(1,'big')
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        
    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = bytes((0x8C,0,5,3,1,value))
            VolumeCmdString += (reduce(add,VolumeCmdString) & 255).to_bytes(1,'big')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x83\x00\x05\xFF\xFF'
        VolumeCmdString += (reduce(add,VolumeCmdString) & 255).to_bytes(1,'big')
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[4]
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
                else:
                    self.Error(['Volume: Invalid/unexpected response'])
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        Errors = {
            1: ': The value given is too large',  # should only be triggered by set commands
            2: ': The value given is too small',  # should only be triggered by set commands
            3: ': Command is not permitted and has been canceled',
            4: ': Malformed command and/or checksum error'
        }
        if len(response) > 2:
            if response[1] != 0:  # 0 == no error
                Error = sourceCmdName + Errors.get(response[1],': An unknown error occured')
                self.Error([Error])
                return ''
        else:
            self.Error([sourceCmdName + ': Device reply data is too short for it to be valid'])
            return ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['{0}: No response received'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
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
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'IREmulation': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'    : '*SCAMUT0000000000000001\n', 
            'Off'   : '*SCAMUT0000000000000000\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        AudioMuteCmdString = '*SEAMUT################\n'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'    : '*SCIRCC0000000000000033\n', 
            'Down'  : '*SCIRCC0000000000000034\n'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV'        : '*SCINPT0000000000000000\n', 
            'Video'     : '*SCINPT0000000300000001\n', 
            'Component' : '*SCINPT0000000400000001\n', 
            'HDMI 1'    : '*SCINPT0000000100000001\n', 
            'HDMI 2'    : '*SCINPT0000000100000002\n', 
            'HDMI 3'    : '*SCINPT0000000100000003\n', 
            'HDMI 4'    : '*SCINPT0000000100000004\n'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0' : 'TV', 
            '3' : 'Video', 
            '4' : 'Component'
        }
        HDMIStateValues = {
            '1' : 'HDMI 1', 
            '2' : 'HDMI 2', 
            '3' : 'HDMI 3', 
            '4' : 'HDMI 4'
        }
        
        InputCmdString = '*SEINPT################\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                temp = res[14]
                if temp == '1':
                    self.WriteStatus('Input', HDMIStateValues[res[22]], qualifier)
                else:
                    self.WriteStatus('Input', ValueStateValues[temp], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected response'])

    def SetIREmulation(self, value, qualifier):

        ValueStateValues = {
            'GGuide'                             : '*SCIRCC0000000000000002\n', 
            'EPG'                                : '*SCIRCC0000000000000003\n', 
            'Display'                            : '*SCIRCC0000000000000005\n', 
            'Options'                            : '*SCIRCC0000000000000007\n', 
            'Red'                                : '*SCIRCC0000000000000014\n', 
            'Green'                              : '*SCIRCC0000000000000015\n', 
            'Yellow'                             : '*SCIRCC0000000000000016\n', 
            'Blue'                               : '*SCIRCC0000000000000017\n', 
            'Volume Up'                          : '*SCIRCC0000000000000030\n', 
            'Volume Down'                        : '*SCIRCC0000000000000031\n', 
            'Mute'                               : '*SCIRCC0000000000000032\n', 
            'Subtitle'                           : '*SCIRCC0000000000000035\n', 
            'Closed Caption'                     : '*SCIRCC0000000000000036\n', 
            'Analog'                             : '*SCIRCC0000000000000039\n', 
            'Teletext'                           : '*SCIRCC0000000000000040\n', 
            'Exit'                               : '*SCIRCC0000000000000041\n', 
            'AD'                                 : '*SCIRCC0000000000000043\n', 
            'Digital'                            : '*SCIRCC0000000000000044\n', 
            'BS'                                 : '*SCIRCC0000000000000046\n', 
            'CS'                                 : '*SCIRCC0000000000000047\n', 
            'BS/CS'                              : '*SCIRCC0000000000000048\n', 
            'Ddata'                              : '*SCIRCC0000000000000049\n', 
            'Picture Off'                        : '*SCIRCC0000000000000050\n', 
            'TV Radio'                           : '*SCIRCC0000000000000051\n', 
            'Netflix'                            : '*SCIRCC0000000000000056\n', 
            'Mode3D'                             : '*SCIRCC0000000000000058\n', 
            'iManual'                            : '*SCIRCC0000000000000059\n', 
            'Wide'                               : '*SCIRCC0000000000000061\n', 
            'Jump'                               : '*SCIRCC0000000000000062\n', 
            'PAP'                                : '*SCIRCC0000000000000063\n', 
            'Ten Key'                            : '*SCIRCC0000000000000068\n', 
            'Media'                              : '*SCIRCC0000000000000075\n', 
            'Sync Menu'                          : '*SCIRCC0000000000000076\n', 
            'Forward'                            : '*SCIRCC0000000000000077\n', 
            'Play'                               : '*SCIRCC0000000000000078\n', 
            'Rewind'                             : '*SCIRCC0000000000000079\n', 
            'Previous'                           : '*SCIRCC0000000000000080\n', 
            'Stop'                               : '*SCIRCC0000000000000081\n', 
            'Next'                               : '*SCIRCC0000000000000082\n', 
            'Record'                             : '*SCIRCC0000000000000083\n', 
            'Pause'                              : '*SCIRCC0000000000000084\n', 
            'Flash Plus'                         : '*SCIRCC0000000000000086\n', 
            'Flash Minus'                        : '*SCIRCC0000000000000087\n', 
            'Top Menu'                           : '*SCIRCC0000000000000088\n', 
            'Popup Menu'                         : '*SCIRCC0000000000000089\n', 
            'One Touch Time Record'              : '*SCIRCC0000000000000091\n', 
            'One Touch View'                     : '*SCIRCC0000000000000092\n', 
            'DUX'                                : '*SCIRCC0000000000000095\n', 
            'Football Mode'                      : '*SCIRCC0000000000000096\n', 
            'TV Power'                           : '*SCIRCC0000000000000098\n', 
            'Media Audio Track'                  : '*SCIRCC0000000000000099\n', 
            'TV'                                 : '*SCIRCC0000000000000100\n', 
            'TV Input'                           : '*SCIRCC0000000000000101\n', 
            'TV Antenna Cable'                   : '*SCIRCC0000000000000102\n', 
            'Wake Up'                            : '*SCIRCC0000000000000103\n', 
            'Sleep'                              : '*SCIRCC0000000000000104\n', 
            'Sleep Timer'                        : '*SCIRCC0000000000000105\n', 
            'TV Analog'                          : '*SCIRCC0000000000000106\n', 
            'Picture Mode'                       : '*SCIRCC0000000000000110\n', 
            'DPAD Center'                        : '*SCIRCC0000000000000113\n', 
            'Cursor Up'                          : '*SCIRCC0000000000000114\n', 
            'Cursor Down'                        : '*SCIRCC0000000000000115\n', 
            'Cursor Left'                        : '*SCIRCC0000000000000116\n', 
            'Cursor Right'                       : '*SCIRCC0000000000000117\n', 
            'Shop Remote Control Forced Dynamic' : '*SCIRCC0000000000000118\n', 
            'Demo Mode'                          : '*SCIRCC0000000000000119\n', 
            'Digital Toggle'                     : '*SCIRCC0000000000000120\n', 
            'Demo Surround'                      : '*SCIRCC0000000000000121\n', 
            'Audio Mix Up'                       : '*SCIRCC0000000000000122\n', 
            'Audio Mix Down'                     : '*SCIRCC0000000000000123\n', 
            'Assists'                            : '*SCIRCC0000000000000128\n', 
            'Action Menu'                        : '*SCIRCC0000000000000129\n', 
            'Help'                               : '*SCIRCC0000000000000130\n', 
            'TV Satellite'                       : '*SCIRCC0000000000000131\n', 
            'Wireless Subwoofer'                 : '*SCIRCC0000000000000132\n'
        }

        IREmulationCmdString = ValueStateValues[value]
        self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)
    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0'   : '*SCIRCC0000000000000027\n', 
            '1'   : '*SCIRCC0000000000000018\n', 
            '2'   : '*SCIRCC0000000000000019\n', 
            '3'   : '*SCIRCC0000000000000020\n', 
            '4'   : '*SCIRCC0000000000000021\n', 
            '5'   : '*SCIRCC0000000000000022\n', 
            '6'   : '*SCIRCC0000000000000023\n', 
            '7'   : '*SCIRCC0000000000000024\n', 
            '8'   : '*SCIRCC0000000000000025\n', 
            '9'   : '*SCIRCC0000000000000026\n', 
            '11'  : '*SCIRCC0000000000000028\n', 
            '12'  : '*SCIRCC0000000000000029\n', 
            'Dot' : '*SCIRCC0000000000000038\n'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home'   : '*SCIRCC0000000000000006\n', 
            'Up'     : '*SCIRCC0000000000000009\n', 
            'Down'   : '*SCIRCC0000000000000010\n', 
            'Right'  : '*SCIRCC0000000000000011\n', 
            'Left'   : '*SCIRCC0000000000000012\n', 
            'Select' : '*SCIRCC0000000000000013\n', 
            'Return' : '*SCIRCC0000000000000008\n'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On'    : '*SCPIPI0000000000000001\n', 
            'Off'   : '*SCPIPI0000000000000000\n'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PIPModeCmdString = '*SEPIPI################\n'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode : Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : '*SCPOWR0000000000000001\n', 
            'Off'   : '*SCPOWR0000000000000000\n'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = '*SEPOWR################\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'    : '*SCPMUT0000000000000001\n', 
            'Off'   : '*SCPMUT0000000000000000\n'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        VideoMuteCmdString = '*SEPMUT################\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute : Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = ''.join(['*SCVOLU0000000000000', '{0:03d}'.format(value), '\n'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '*SEVOLU################\n'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-4:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError, ValueError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'FFFFFFFFFFFFFFFF' : 'Invalid Parameter',
            'NNNNNNNNNNNNNNNN' : 'The command does not exist',
        }
        response = response.decode()
        if response[7:-1] in DEVICE_ERROR_CODES:
            self.Error(['ERROR:{0}'.format(DEVICE_ERROR_CODES[response[7:-1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\n')
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