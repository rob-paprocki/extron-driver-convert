# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

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
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputSignalStatus': {'Parameters':['Card','Input'], 'Status': {}},
            'AudioGainAttenuation': {'Parameters':['Card','Input'], 'Status': {}},
            'AudioInputFormat': {'Parameters':['Card','Input'], 'Status': {}},
            'AudioMute': {'Parameters':['Card','Output'], 'Status': {}},
            'FanSpeed': {'Parameters':['Fan'], 'Status': {}},
            'FanStatus': {'Parameters':['Fan'], 'Status': {}},
            'FiberLinkStatus': {'Parameters':['Card','Input', 'Link'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Card','Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Card','Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Card','Output'], 'Status': {}},
            'PowerSupplyStatus': {'Parameters':['Power Supply'], 'Status': {}},
            'QueryCommand': { 'Status': {}},
            'SlotStatus': {'Parameters':['Slot'], 'Status': {}},
            'Temperature': { 'Status': {}},
            'VideoMute': {'Parameters':['Card','Output'], 'Status': {}},
            }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Slot([01])([01])([01])([01]) PS([01])([01])'), self.__MatchSlotandPowerStatus, None)
            self.AddMatchString(re.compile(b'Sts[0-9]+\.[0-9]+ [0-9]+\.[0-9]+ \+([0-9]+\.[0-9]+)F ([0-9]{5}) ([0-9]{5}) ([0-9]{5}) ([0-9]{5}) ([0-2]) ([0-2])'), self.__MatchTemperatureFanSpeed, None)
            self.AddMatchString(re.compile(b'{([0-4])}Amt([1-2])\*([0-3])'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'{([0-4])}Vmt([1-2])\*([0-2])'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'FAILED: Fan ([1-4])'), self.__FanStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}HdcpE([1-2])\*([0-1])'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'{([0-4])}HdcpO([1-2])\*([0-2])'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}AfmtI([1-2])\*([0-2])'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(re.compile(b'{([0-4])}Aud([1-2])\*([+-])([0-1][0-8])'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'{([0-4])}Reconfig([1-2])'), self.__MatchReconfig, None)
            self.AddMatchString(re.compile(b'{([0-4])}Inf00\*([1-2])\*1Lnk([0-1]) 2Lnk([0-1]) SigI([0-1]) HdcpI([0-2]) Aud[IO][0-1] (SM|MM) (TX|RX)'), self.__MatchStatus, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):        
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword(None, None)

    def __MatchLoginAdmin(self, match, tag):
        
        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0
        
    def __MatchLoginUser(self, match, tag):
        
        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def __MatchStatus(self, match, qualifier):

        hdcpValues = {
            '0': 'No Source Connected',
            '1': 'Source Connected and HDCP',
            '2': 'Source Connected and No HDCP'
        }
        sigValues = {
            '0': 'Not Active',
            '1': 'Active'
        }

        linkValues = {
            '1' : 'Detected',
            '0' : 'Not Detected'
        }

        card_ = match.group(1).decode()
        input_ = match.group(2).decode()
        value = hdcpValues[match.group(6).decode()]
        self.WriteStatus('HDCPInputStatus', value, {'Card': card_, 'Input': input_})
        value = sigValues[match.group(5).decode()]
        self.WriteStatus('InputSignalStatus', value, {'Card': card_, 'Input': input_})

        link_1 = linkValues[match.group(3).decode()]
        link_2 = linkValues[match.group(4).decode()]
        self.WriteStatus('FiberLinkStatus', link_1, {'Card' : qualifier['Card'], 'Input' : qualifier['Input'], 'Link': '1'})
        self.WriteStatus('FiberLinkStatus', link_2, {'Card' : qualifier['Card'], 'Input' : qualifier['Input'], 'Link': '2'})

    def Config(self, value, qualifier):
        self.Send('{{{0}:{1}*I}}/r/n'.format(value, qualifier))

    def __MatchReconfig(self, match, qualifier):
        self.Config( match.group(1).decode(), match.group(2).decode())

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def UpdateHDCPInputStatus(self, value, qualifier):
        HDCPInputStatusCmdString = '{1:1*I}\r\n{1:2*I}\r\n{2:1*I}\r\n{2:2*I}\r\n{3:1*I}\r\n{3:2*I}\r\n{4:1*I}\r\n{4:2*I}\r\n'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):
        InputSignalStatusCmdString = '{1:1*I}\r\n{1:2*I}\r\n{2:1*I}\r\n{2:2*I}\r\n{3:1*I}\r\n{3:2*I}\r\n{4:1*I}\r\n{4:2*I}\r\n'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def SetAudioGainAttenuation(self, value, qualifier):

        ValueConstraints = {
            'Min' : -18,
            'Max' : 10
            }
        card = int(qualifier['Card'])
        input_ = int(qualifier['Input'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for SetAudioGainAttenuation')
        elif input_ < 1 or input_ > 2:
            self.Discard('Invalid Command for SetAudioGainAttenuation')
        elif ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioGainandAttenuationCmdString = '{{{0}:{1}*{2}G}}\r\n'.format(qualifier['Card'], qualifier['Input'], value)
            self.__SetHelper('AudioGainAttenuation', AudioGainandAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        card = int(qualifier['Card'])
        input_ = int(qualifier['Input'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')
        elif input_ < 1 or input_ > 2:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')
        else:
            AudioGainandAttenuationCmdString = '{{{0}:{1}G}}\r\n'.format(qualifier['Card'], qualifier['Input'])
            self.__UpdateHelper('AudioGainAttenuation', AudioGainandAttenuationCmdString, value, qualifier)

    def __MatchAudioGainAttenuation(self, match, tag):

        card_ = match.group(1).decode()
        input_ = match.group(2).decode()
        value = int(match.group(4).decode())
        if match.group(3).decode() == '-':
            value = -value
        self.WriteStatus('AudioGainAttenuation', value, {'Card': card_, 'Input': input_})

    def SetAudioInputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto' : '0', 
            'Digital' : '1', 
            'Analog' : '2'
        }
        card = int(qualifier['Card'])
        input_ = int(qualifier['Input'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for SetAudioInputFormat')
        elif input_ < 1 or input_ > 2:
            self.Discard('Invalid Command for SetAudioInputFormat')
        else:
            AudioInputFormatCmdString = '{{{0}:\x1BI{1}*{2}AFMT}}\r\n'.format(qualifier['Card'], qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def UpdateAudioInputFormat(self, value, qualifier):

        card = int(qualifier['Card'])
        input_ = int(qualifier['Input'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for UpdateAudioInputFormat')
        elif input_ < 1 or input_ > 2:
            self.Discard('Invalid Command for UpdateAudioInputFormat')
        else:
            AudioInputFormatCmdString = '{{{0}:\x1BI{1}AFMT}}\r\n'.format(qualifier['Card'], qualifier['Input'])
            self.__UpdateHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def __MatchAudioInputFormat(self, match, tag):

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : 'Digital', 
            '2' : 'Analog'
        }

        card_ = match.group(1).decode()
        input_ = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('AudioInputFormat', value, {'Card': card_, 'Input': input_})

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'No Mute' : '0', 
            'Digital Out' : '1',
            'Analog Out' : '2', 
            'Mute All' : '3',
        }
        card = int(qualifier['Card'])
        output = int(qualifier['Output'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for SetAudioMute')
        elif output < 1 or output > 2:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            AudioMuteCmdString = '{{{0}:{1}*{2}Z}}\r\n'.format(qualifier['Card'], qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        card = int(qualifier['Card'])
        output = int(qualifier['Output'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for UpdateAudioMute')
        elif output < 1 or output > 2:
            self.Discard('Invalid Command for UpdateAudioMute')
        else:
            AudioMuteCmdString = '{{{0}:{1}Z}}\r\n'.format(qualifier['Card'], qualifier['Output'])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'No Mute', 
            '1': 'Digital Out',
            '2': 'Analog Out', 
            '3': 'Mute All',
        }

        card_ = match.group(1).decode()
        output_ = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('AudioMute', value, {'Card': card_, 'Output': output_})

    def UpdateTemperature(self, value, qualifier):

        FanSpeedCmdString = '\rSI'
        self.__UpdateHelper('Temperature', FanSpeedCmdString, value, qualifier)

    def UpdateFanStatus(self, value, qualifier):

        FanSpeedCmdString = '\rSI'
        self.__UpdateHelper('FanStatus', FanSpeedCmdString, value, qualifier)

    def UpdateFanSpeed(self, value, qualifier):

        FanSpeedCmdString = '\rSI'
        self.__UpdateHelper('FanSpeed', FanSpeedCmdString, value, qualifier)

    def __MatchTemperatureFanSpeed(self, match, tag):

        FanStates = {
            '1' : '', 
            '2' : '', 
            '3' : '', 
            '4' : ''
        }

        qualifier = {}
        self.WriteStatus('Temperature', float(match.group(1).decode()), None)
        fan1 = int(match.group(2).decode())
        if fan1 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '1'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '1'})
        fan2 = int(match.group(3).decode())
        if fan2 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '2'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '2'})
        fan3 = int(match.group(4).decode())
        if fan3 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '3'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '3'})
        fan4 = int(match.group(5).decode())
        if fan4 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '4'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '4'})
        
        self.WriteStatus('FanSpeed', fan1, {'Fan': '1'})
        self.WriteStatus('FanSpeed', fan2, {'Fan': '2'})
        self.WriteStatus('FanSpeed', fan3, {'Fan': '3'})
        self.WriteStatus('FanSpeed', fan4, {'Fan': '4'})

    def __FanStatus(self, match, tag):

        qualifier = {}
        qual = match.group(1).decode()
        value = 'Failed'
        self.WriteStatus('FanStatus', value, {'Fan': qual})

    def UpdateFiberLinkStatus(self, value, qualifier):

        if 1 <= int(qualifier['Card']) <= 4 and 1 <= int(qualifier['Input']) <= 2 and 1 <= int(qualifier['Link']) <= 2:
            FiberLinkStatusCmdString = '{{{0}:{1}*i|}}\r'.format(qualifier['Card'], qualifier['Input'])
            self.__UpdateHelper('FiberLinkStatus', FiberLinkStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFiberLinkStatus')

    def SetHDCPInputAuthorization(self, value, qualifier):


        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        card = int(qualifier['Card'])
        input_ = int(qualifier['Input'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')
        elif input_ < 1 or input_ > 2:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')
        else:
            HDCPAuthorizedDeviceCmdString = '{{{0}:\x1BE{1}*{2}Hdcp}}\r\n'.format(qualifier['Card'], qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPAuthorizedDeviceCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        card = int(qualifier['Card'])
        input_ = int(qualifier['Input'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')
        elif input_ < 1 or input_ > 2:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')
        else:
            HDCPAuthorizedDeviceCmdString = '{{{0}:\x1BE{1}Hdcp}}\r\n'.format(qualifier['Card'], qualifier['Input'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPAuthorizedDeviceCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        card_ = match.group(1).decode()
        input_ = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Card': card_, 'Input': input_})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        card = int(qualifier['Card'])
        output = int(qualifier['Output'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')
        elif output < 1 or output > 2:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')
        else:
            HDCPOutputStatusCmdString = '{{{0}:\x1BO{1}HDCP}}\r\n'.format(qualifier['Card'], qualifier['Output'])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Sync Detected', 
            '1' : 'Sync Detected with HDCP', 
            '2' : 'Sync Detected with No HDCP'
        }

        card_ = match.group(1).decode()
        output_ = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('HDCPOutputStatus', value, {'Card': card_, 'Output': output_})

    def __MatchSlotandPowerStatus(self, match, tag):

        PowerSupplyStateValues = {
            '1' : 'On', 
            '0' : 'Failed', 
            '2' : 'Not Installed'
        }

        SlotStateValues = {
            '1': 'Installed', 
            '0': 'Not Installed'
        }

        Slot1 = match.group(1).decode()
        Slot2 = match.group(2).decode()
        Slot3 = match.group(3).decode()
        Slot4 = match.group(4).decode()
        PowerSupply1 = match.group(5).decode()
        PowerSupply2 = match.group(6).decode()

        self.WriteStatus('SlotStatus', SlotStateValues[Slot1], {'Slot' : '1'})
        self.WriteStatus('SlotStatus', SlotStateValues[Slot2], {'Slot' : '2'})
        self.WriteStatus('SlotStatus', SlotStateValues[Slot3], {'Slot' : '3'})
        self.WriteStatus('SlotStatus', SlotStateValues[Slot4], {'Slot' : '4'})
        self.WriteStatus('PowerSupplyStatus', PowerSupplyStateValues[PowerSupply1], {'Power Supply' : '1'})
        self.WriteStatus('PowerSupplyStatus', PowerSupplyStateValues[PowerSupply2], {'Power Supply' : '2'})

    def __MatchTemperature(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Mute Video Only' : '1', 
            'Mute Video and Sync' : '2',
            'Off' : '0', 
        }

        card = int(qualifier['Card'])
        output = int(qualifier['Output'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for SetVideoMute')
        elif output < 1 or output > 2:
            self.Discard('Invalid Command for SetVideoMute')
        else:
            VideoMuteCmdString = '{{{0}:{1}*{2}B}}\r\n'.format(qualifier['Card'], qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        card = int(qualifier['Card'])
        output = int(qualifier['Output'])
        if card < 1 or card > 4:
            self.Discard('Invalid Command for UpdateVideoMute')
        elif output < 1 or output > 2:
            self.Discard('Invalid Command for UpdateVideoMute')
        else:
            VideoMuteCmdString = '{{{0}:{1}B}}\r\n'.format(qualifier['Card'], qualifier['Output'])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off', 
            '1': 'Mute Video Only',
            '2': 'Mute Video and Sync', 
        }

        card_ = match.group(1).decode()
        output_ = match.group(2).decode()
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('VideoMute', value, {'Card': card_, 'Output': output_})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            self.Send('w3cv\r\n')
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
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
                    self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '12': 'Invalid port number',
            '13': 'Invalid value (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found',
        }
        
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 


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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()