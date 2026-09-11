from extronlib.interface import DanteInterface
import re
from extronlib.system import Wait

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
            'AmpOutputAttenuation': {'Parameters':['Output'], 'Status': {}},
            'ATInputGain': {'Parameters':['Input'], 'Status': {}},
            'ATInputPremixerGain': {'Parameters':['Input'], 'Status': {}},
            'DCProtectionFault': {'Parameters':['Output'], 'Status': {}},
            'DigitalClip': {'Parameters':['Output'], 'Status': {}},
            'GroupInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters':['Group'], 'Status': {}},
            'GroupPostMixerTrim': {'Parameters':['Group'], 'Status': {}},
            'GroupPreMixerGain': {'Parameters':['Group'], 'Status': {}},
            'NegotiatedPoEPower': { 'Status': {}},
            'OverTempWarning': {'Parameters':['Output'], 'Status': {}},
            'OverTempShutDown': {'Parameters':['Output'], 'Status': {}},
            'OverloadProtect': {'Parameters':['Output'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'SignalPresence': {'Parameters':['Output'], 'Status': {}},
            'Temperature': { 'Status': {}},
            }

        self.VerboseDisabled = True
        self.SendNotify = True

        self.GroupFunction = {} #This is to maintain a global dictionary of groups and their assigned functions
        self.InputSize = 4
        self.OutputSize = 4
        self.LevelTypes = {
            'GroupInputGain'            : {'Min' : -18,  'Max' : 24},
            'GroupMixpointGain'         : {'Min' : -100,  'Max' : 12},
            'GroupOutputAttenuation'    : {'Min' : -100, 'Max' : 0},
            'GroupPostMixerTrim'        : {'Min' : -12,  'Max' : 12},
            'GroupPreMixerGain'         : {'Min' : -100, 'Max' : 12},
            'ATInputGain'                 : {'Min' : -18,  'Max' : 24},
            'ATInputPremixerGain'         : {'Min' : -100, 'Max' : 12},
            'AmpOutputAttenuation'         : {'Min' : -100, 'Max' : 0},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'32Stat[3-5]((?:\*[0-2]{6}){4})\r\n'), self.__MatchFaultStatus, None)
            self.AddMatchString(re.compile(b'53Stat([0-2*]{7})\*([0-2*]{7})\r\n', re.I), self.__MatchSystemFault, None)
            self.AddMatchString(re.compile(b'(54|57|62|64)Stat([0-2*]{3,8})\r\n', re.I), self.__MatchChannelFault, None)
            self.AddMatchString(re.compile(b'GrpmD([0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'DsG(50000|50001|50002|50003)\*([0-9 -]{1,5})\r\n'), self.__MatchATInputGain, None)
            self.AddMatchString(re.compile(b'DsG(50100|50101|50102|50103)\*([0-9 -]{1,5})\r\n'), self.__MatchATInputPremixerGain, None)
            self.AddMatchString(re.compile(b'DsG(60000|60001|60002|60003)\*([0-9 -]{1,5})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(re.compile(b'PoecK([345])\*[0345]\*[345]\r\n'), self.__MatchNegotiatedPoEPower, None)
            self.AddMatchString(re.compile(b'28Stat(\d+.\d+)C\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'E([0-9]{2})\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'NtfyM111\*1\r\n'), self.__MatchNotify, None) # Notify for unsolicited status

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchNotify(self, match, qualifier):
        self.SendNotify = False

    def UpdateFaultStatus(self, value, qualifier):

        cmdString = '\x1b32Stat\r'
        self.Send(cmdString)
        if self.SendNotify:
            cmdString = '\x1bM111*1NTFY\r'
            self.Send(cmdString)

    def SetAmpOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize and self.__CheckValidLevelValue('AmpOutputAttenuation', value):
            level = round(value*10)
            commandString = 'WG{0}*{1:05d}AU\r'.format(channel + 59999, level)
            self.__SetHelper('AmpOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmpOutputAttenuation')

    def UpdateAmpOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            commandString = 'WG{0}AU\r'.format(channel + 59999)
            self.__UpdateHelper('AmpOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmpOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):
    
        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output' : channel}
        value = int(match.group(2))/10
        self.WriteStatus('AmpOutputAttenuation', value, qualifier)

    def UpdateOverTempWarning(self, value, qualifier):
        self.UpdateFaultStatus( None, None)
        
    def UpdateOverTempShutDown(self, value, qualifier):
        self.UpdateFaultStatus( None, None)
        
    def UpdateDCProtectionFault(self, value, qualifier):
        self.UpdateFaultStatus( None, None)
        
    def UpdateSignalPresence(self, value, qualifier):
        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateSignalPresence')

    def UpdateOverloadProtect(self, value, qualifier):
        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateOverloadProtect')
    
    def UpdateDigitalClip(self, value, qualifier):
        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            self.UpdateFaultStatus( None, None)
        else:
            self.Discard('Invalid Command for UpdateDigitalClip')
    
    def __MatchChannelFault(self, match, tag):
    
        faulttable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault'
        }

        signalpresence = {
            '0': 'No Signal',
            '1': 'Signal'
        }

        type = match.group(1).decode()
        flt = match.group(2).decode()
        fltsplit = flt.split('*')
        if type == '57':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('OverloadProtect', faulttable[value], {'Output': str(index + 1)})
        elif type == '54':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('DCProtectionFault', faulttable[value], {'Output': str(index + 1)})
        elif type == '62':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('SignalPresence', signalpresence[value], {'Output': str(index + 1)})
        elif type == '64':
            for index, value in enumerate(fltsplit):
                self.WriteStatus('DigitalClip', faulttable[value], {'Output': str(index + 1)})

    def __MatchSystemFault(self, match, tag):

        faulttable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault'
        }

        flt = match.group(1).decode()
        fltsplit = flt.split('*')
        for index, value in enumerate(fltsplit):
                self.WriteStatus('OverTempWarning', faulttable[value], {'Output': str(index + 1)})
        flt = match.group(2).decode()
        fltsplit = flt.split('*')
        for index, value in enumerate(fltsplit):
                self.WriteStatus('OverTempShutDown', faulttable[value], {'Output': str(index + 1)})

    def __MatchFaultStatus(self, match, tag):
    
        faulttable = {
            '0': 'Never Faulted',
            '1': 'Not in Fault State but Has Faulted',
            '2': 'Fault'
        }

        signalpresence = {
            '0': 'No Signal',
            '1': 'Signal'
        }

        values = match.group(1).decode()
        values = values.split('*')
        values.pop(0)

        for index, items in enumerate(values):
            self.WriteStatus('SignalPresence', signalpresence[items[0]], {'Output': str(index + 1)})
            self.WriteStatus('OverloadProtect', faulttable[items[1]], {'Output': str(index + 1)})
            self.WriteStatus('OverTempWarning', faulttable[items[2]], {'Output': str(index + 1)})
            self.WriteStatus('OverTempShutDown', faulttable[items[3]], {'Output': str(index + 1)})
            self.WriteStatus('DigitalClip', faulttable[items[4]], {'Output': str(index + 1)})
            self.WriteStatus('DCProtectionFault', faulttable[items[5]], {'Output': str(index + 1)})

    def SetGroupInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8 and self.__CheckValidLevelValue('GroupInputGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupInputGain'
            self.__SetHelper('GroupInputGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupInputGain')

    def UpdateGroupInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupInputGain'
            self.__UpdateHelper('GroupInputGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupInputGain')

    def SetGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8 and self.__CheckValidLevelValue('GroupMixpointGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__SetHelper('GroupMixpointGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__UpdateHelper('GroupMixpointGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        GroupMuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'wd{0}*{1}grpm\r'.format(group, GroupMuteStateValues[value])
            self.GroupFunction[group] = 'GroupMute'
            self.__SetHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupMute'
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8 and self.__CheckValidLevelValue('GroupOutputAttenuation', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'Wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupOutputAttenuation')

    def SetGroupPostMixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8 and self.__CheckValidLevelValue('GroupPostMixerTrim', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupPostMixerTrim'
            self.__SetHelper('GroupPostMixerTrim', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupPostMixerTrim')

    def UpdateGroupPostMixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupPostMixerTrim'
            self.__UpdateHelper('GroupPostMixerTrim', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupPostMixerTrim')

    def SetGroupPreMixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8 and self.__CheckValidLevelValue('GroupPreMixerGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r'.format(group, level)
            self.GroupFunction[group] = 'GroupPreMixerGain'
            self.__SetHelper('GroupPreMixerGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupPreMixerGain')

    def UpdateGroupPreMixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 8:
            commandString = 'wd{0}grpm\r'.format(group)
            self.GroupFunction[group] = 'GroupPreMixerGain'
            self.__UpdateHelper('GroupPreMixerGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupPreMixerGain')

    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                        '1' : 'On',
                        '0' : 'Off'
                }
                qualifier = {'Group' : group}
                value = match.group(2).decode()[-1]
                self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
            elif command in ['GroupPreMixerGain', 'GroupOutputAttenuation',
                             'GroupMixpointGain', 'GroupPostMixerTrim',
                             'GroupInputGain',
                             ]:
                qualifier = {'Group' : group}
                value = int(match.group(2))/10
                self.WriteStatus(command, value, qualifier)
                
    def SetATInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= self.InputSize and self.__CheckValidLevelValue('ATInputGain', value):
            level = round(value*10)
            commandString = 'WG{0}*{1:05d}AU\r'.format(channel + 49999, level)
            self.__SetHelper('ATInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATInputGain')

    def UpdateATInputGain(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= self.InputSize:
            commandString = 'WG{0}AU\r'.format(channel + 49999)
            self.__UpdateHelper('ATInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATInputGain')

    def __MatchATInputGain(self, match, tag):

        channel = str(int(match.group(1)) - 49999)
        qualifier = {'Input' : channel}
        value = int(match.group(2))/10
        self.WriteStatus('ATInputGain', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) <= 8:
            commandString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdateNegotiatedPoEPower(self, value, qualifier):

        commandString = 'wKPOEC\r'
        self.__UpdateHelper('NegotiatedPoEPower', commandString, value, qualifier)
    
    def __MatchNegotiatedPoEPower(self, match, tag):
    
        poepowerValues = {
            '3': 'PoE Power Class 3 (15W)',
            '4': 'PoE Power Class 4 (30W)',
            '5': 'PoE Power Class 5 (45W)'
        }

        poepower = match.group(1).decode()
        self.WriteStatus('NegotiatedPoEPower', poepowerValues[poepower], None)
    
    def UpdateTemperature(self, value, qualifier):

        cmdString = 'w28STAT\r'

        self.__UpdateHelper('Temperature', cmdString, None, None)

    def __MatchTemperature(self, match, tag):

        value = float(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetATInputPremixerGain(self, value, qualifier):

        channel = qualifier['Input']
        if 1 <= int(channel) <= self.InputSize and self.__CheckValidLevelValue('ATInputPremixerGain', value):
            level=round(value*10)
            ChannelValue = int(channel) + 50099
            commandString = 'wG{0}*{1:05d}AU\r'.format(ChannelValue, level)
            self.__SetHelper('ATInputPremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATInputPremixerGain')

    def UpdateATInputPremixerGain(self, value, qualifier):

        channel = qualifier['Input']
        if 1 <= int(channel) <= self.InputSize:
            ChannelValue = int(channel) + 50099
            commandString = 'wG{0}AU\r'.format(ChannelValue)
            self.__UpdateHelper('ATInputPremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATInputPremixerGain')

    def __MatchATInputPremixerGain(self, match, tag):

        channel = int(match.group(1)) - 50099
        qualifier = {'Input' : str(channel)}
        value = int(match.group(2))/10
        self.WriteStatus('ATInputPremixerGain', value, qualifier)

    def __CheckValidLevelValue(self, command, value):
        return self.LevelTypes[command]['Min'] <= value <= self.LevelTypes[command]['Max']

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

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '10' : 'Unrecognized Command',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '18' : 'System/command timed out',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '27' : 'Invalid Event number',
            '28' : 'Bad Filename / File not found',
            '30' : 'Hardware Failure',
            '31' : 'Attempt to break Port Pass-thru when not set'
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
        self.VerboseDisabled = False
        self.SendNotify = True
                
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

class DanteClass(DanteInterface, DeviceClass):
    def __init__(self, Hostname, Protocol='Extron', DanteDomainManager=None, Domain=None, Model=None):
        DanteInterface.__init__(self, Hostname, Protocol, DanteDomainManager, Domain)
        DeviceClass.__init__(self)
        self.ConnectionType = 'Dante'
        self.HostName = Hostname
        self.IsSerial = False
        self.VerboseDisabled = False
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.HostName)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        DanteInterface.Disconnect(self)
        self.OnDisconnected()
