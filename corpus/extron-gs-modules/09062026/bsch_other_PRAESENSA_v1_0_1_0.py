from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack, unpack

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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AllFaults': { 'Status': {}},
            'BGMChannelVolume': {'Parameters':['Channel'], 'Status': {}},
            'BGMRouting': {'Parameters':['Channel'], 'Status': {}},
            'BGMRoutingRemove': {'Parameters':['Channel'], 'Status': {}},
            'BGMVolume': {'Parameters':['Zone'], 'Status': {}},
            'CallControl': {'Parameters':['Call ID'], 'Status': {}},
            'CallRouting': {'Parameters':['Call ID','Routing'], 'Status': {}},
            'CancelAllCalls': { 'Status': {}},
            'EmergencyAlarmAcknowledge': { 'Status': {}},
            'EmergencyAlarmReset': { 'Status': {}},
            'Heartbeat': { 'Status': {}},
            'ResourceFaultState': {'Parameters':['Zone'], 'Status': {}},
            'VirtualControlInput': {'Parameters':['Name','Deactivation Type'], 'Status': {}}
        }

        self.RoutedChannels = {}

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x25\x70\x44\x00[\x00-\xFF]{4}\x00{8}(\x00|\x01)([\x00-\xFF]{8,})'), self.__MatchBGMRouting, None)
            self.AddMatchString(re.compile(b'\x34\x70\x44\x00[\x00-\xFF]{4}\x00{8}([\x00-\xFF]{4})([\x00-\xFF]+)([\x00-\xFF]{4})'), self.__MatchBGMVolume, None)
            self.AddMatchString(re.compile(b'\x3D\x70\x44\x00[\x00-\xFF]{4}\x00{8}(\x00|\x01)\x00{3}([\x00-\xFF]{4})([\x00-\xFF]+)'), self.__MatchResourceFaultState, None)

    def SetLogin(self, value, qualifier):
        
        len_val = len(self.deviceUsername) + len(self.devicePassword) + 24
        LoginString = b''.join([pack('5I', 0x00447002, len_val, 0, 0, len(self.deviceUsername)), self.deviceUsername.encode('utf-8'),
                                        pack('I', len(self.devicePassword)), self.devicePassword.encode('utf-8')])
        res = self.SendAndWait(LoginString, self.DefaultResponseTimeout)
        if res:
            try:
                if res[-4:] != b'\x00\x00\x00\x00':
                    self.Error(['Login: Invalid/unexpected response'])
            except:
                self.Error(['Login: Invalid/unexpected response'])
        else:
            self.Error(['Login Failed'])

    def SetAllFaults(self, value, qualifier):

        ValueStateValues = {
            'Acknowledge': 0x00447008,
            'Reset':       0x00447009
        }

        if value in ValueStateValues:
            AllFaultsCmdString =  pack('4I', ValueStateValues[value], 16, 0, 0)
            self.__SetHelper('AllFaults', AllFaultsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAllFaults')

    def SetBGMChannelVolume(self, value, qualifier):

        ValueStateValues = {
            'Up':   0x00447035,
            'Down': 0x00447036
            }

        channel_val = qualifier['Channel']
        if channel_val and value in ValueStateValues:
            len_val = len(channel_val) + 20
            BGMChannelVolumeCmdString = b''.join([pack('4I', ValueStateValues[value], len_val, 0, 0), 
                                            pack('I', len(channel_val)), channel_val.encode('utf-8')])
            self.__SetHelper('BGMChannelVolume', BGMChannelVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBGMChannelVolume')

    def SetBGMRouting(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val and value:
            len_val = len(channel_val) + len(value) + 24
            BGMRoutingCmdString = b''.join([pack('4I', 0x00447013, len_val, 0, 0), 
                                        pack('I', len(channel_val)), channel_val.encode('utf-8'),
                                        pack('I', len(value)), value.encode('utf-8')])
            self.__SetHelper('BGMRouting', BGMRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBGMRouting')

    def UpdateBGMRouting(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val:
            len_val = len(channel_val) + 21
            BGMRoutingCmdString = b''.join([pack('5I', 0x00447016, len_val, 0, 0, len(channel_val)),
                                            channel_val.encode('utf-8'), b'\x01'])
            self.__UpdateHelper('BGMRouting', BGMRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBGMRouting')

    def __MatchBGMRouting(self, match, tag):

        res = match.group(2)
        
        len_chn = res[0:4][0]
        chn_val = res[4:len_chn+4].decode('utf-8')
        
        
        if chn_val not in self.RoutedChannels:
            self.RoutedChannels[chn_val] = []
        len_val = res[len_chn+4:len_chn+8][0]
        if len_val != 0:
            zone_val = res[len_chn+8:len_chn+8+len_val].decode('utf-8')
            if ',' in zone_val:
                zone_val = zone_val.split(',')
                for val_ in zone_val:
                    if val_ not in self.RoutedChannels[chn_val] and match.group(1) == b'\x01':
                        self.RoutedChannels[chn_val].append(val_)
                    elif val_ in self.RoutedChannels[chn_val] and match.group(1) == b'\x00':
                        self.RoutedChannels[chn_val].remove(val_)
            else:
                if zone_val not in self.RoutedChannels[chn_val] and match.group(1) == b'\x01':
                    self.RoutedChannels[chn_val].append(zone_val)
                elif zone_val in self.RoutedChannels[chn_val] and match.group(1) == b'\x00':
                    self.RoutedChannels[chn_val].remove(zone_val)
        for val in self.RoutedChannels:
            qualifier = {'Channel' : val}
            value_list = self.RoutedChannels[val] if self.RoutedChannels[val] else ['No routing Established']
            final_value = ''
            for item_ in value_list:
                final_value = ','.join([final_value, item_])
            self.WriteStatus('BGMRouting', final_value[1:], qualifier)
            del qualifier

    def SetBGMRoutingRemove(self, value, qualifier):

        channel_val = qualifier['Channel']
        if channel_val and value:
            len_val = len(channel_val) + len(value) + 24
            BGMRoutingRemoveCmdString = b''.join([pack('4I', 0x00447014, len_val, 0, 0), 
                                        pack('I', len(channel_val)), channel_val.encode('utf-8'),
                                        pack('I', len(value)), value.encode('utf-8')])
            self.__SetHelper('BGMRoutingRemove', BGMRoutingRemoveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBGMRoutingRemove')

    def SetBGMVolume(self, value, qualifier):

        zone_val = qualifier['Zone']
        if zone_val and  -96 <= value <= 0:
            if value == 0:
                temp_val = 0
            else:
                temp_val = (value + (1 << 32)) % (1 << 32)
            len_val = len(zone_val) + 24
            BGMVolumeCmdString = b''.join([pack('5I', 0x00447012, len_val, 0, 0, temp_val),
                                           pack('I', len(zone_val)), zone_val.encode('utf-8')])
            self.__SetHelper('BGMVolume', BGMVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBGMVolume')

    def UpdateBGMVolume(self, value, qualifier):

        zone_val = qualifier['Zone']
        if zone_val:
            len_val = len(zone_val) + 21
            BGMVolumeCmdString = b''.join([pack('4I', 0x00447031, len_val, 0, 0),
                                           pack('I', len(zone_val)), zone_val.encode('utf-8'), b'\x01'])
            self.__UpdateHelper('BGMVolume', BGMVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBGMVolume')
        
    def __MatchBGMVolume(self, match, tag):

        len_val = unpack('I', match.group(1))[0]
        if len_val == len(match.group(2)):
            qualifier = {}
            qualifier['Zone'] = match.group(2).decode('utf-8')
            if match.group(3) == b'\x00\x00\x00\x00':
                value = 0
            else:
                value = unpack('I', match.group(3))[0] - (1 << 32)
            if -96 <= value <= 0:
                self.WriteStatus('BGMVolume', value, qualifier)

    def SetCallControl(self, value, qualifier):

        ValueStateValues = {
            'Start Created Call':   0x00447029,
            'Stop':                 0x00447004,
            'Abort':                0x00447005
            }

        if 0 <= qualifier['Call ID'] <= 4294967295 and value in ValueStateValues:
            CallControlCmdString = pack('5I', ValueStateValues[value], 20, 0, 0, qualifier['Call ID'])
            self.__SetHelper('CallControl', CallControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallControl')

    def SetCallRouting(self, value, qualifier):

        ValueStateValues = {
            'Add':      0x00447006,
            'Remove':   0x00447007
            }

        route_val = qualifier['Routing']
        if route_val and 0 <= qualifier['Call ID'] <= 4294967295 and value in ValueStateValues:
            len_val = len(route_val) + 24
            CallRoutingCmdString =  b''.join([pack('5I', ValueStateValues[value], len_val, 0, 0, qualifier['Call ID']),
                                              pack('I', len(route_val)), route_val.encode('utf-8')])  
            self.__SetHelper('CallRouting', CallRoutingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallRouting')

    def SetCancelAllCalls(self, value, qualifier):

        CancelAllCallsCmdString = pack('4I', 0x00447038, 16, 0, 0)
        self.__SetHelper('CancelAllCalls', CancelAllCallsCmdString, value, qualifier)

    def SetEmergencyAlarmAcknowledge(self, value, qualifier):

        EmergencyAlarmAcknowledgeCmdString = pack('4I', 0x0044700A, 16, 0, 0)
        self.__SetHelper('EmergencyAlarmAcknowledge', EmergencyAlarmAcknowledgeCmdString, value, qualifier)

    def SetEmergencyAlarmReset(self, value, qualifier):

        ValueStateValues = {
            'Abort running evacuation priority calls':        1,
            'Do not abort running evacuation priority calls': 0
            }

        if value in ValueStateValues:
            EmergencyAlarmResetCmdString = pack('4IB', 0x00447038, 17, 0, 0, ValueStateValues[value])
            self.__SetHelper('EmergencyAlarmReset', EmergencyAlarmResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEmergencyAlarmReset')

    def UpdateHeartbeat(self, value, qualifier):

        HeartbeatCmdString = pack('4I', 0x00447027, 16, 0, 0)
        self.__UpdateHelper('Heartbeat', HeartbeatCmdString, value, qualifier)

    def UpdateResourceFaultState(self, value, qualifier):

        zone_val = qualifier['Zone']
        if zone_val:
            len_val = len(zone_val) + 21
            ResourceFaultStateCmdString = b''.join([pack('4I', 0x0044703C, len_val, 0, 0),
                                           pack('I', len(zone_val)), zone_val.encode('utf-8'), b'\x01'])
            self.__UpdateHelper('ResourceFaultState', ResourceFaultStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateResourceFaultState')

    def __MatchResourceFaultState(self, match, tag):

        ValueStateValues = {
            '\x01': 'Faults',
            '\x00': 'No Faults'
            }

        len_val = unpack('I', match.group(2))[0]
        if len_val == len(match.group(3)):
            qualifier = {}
            qualifier['Zone'] = match.group(3).decode('utf-8')
            value = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('ResourceFaultState', value, qualifier)

    def SetVirtualControlInput(self, value, qualifier):

        DeactivationTypeStates = {
            'Stop the running action gracefully':   0x00000000,
            'Abort the running action immediately': 0x00000001
            }

        ValueStateValues = ('Activate', 'Deactivate')

        name_val = qualifier['Name']
        if name_val and qualifier['Deactivation Type'] in DeactivationTypeStates and value in ValueStateValues:
            if value == 'Activate':
                len_val = len(name_val) + 20
                VirtualControlInputCmdString = b''.join([pack('4I', 0x0044703F, len_val, 0, 0), 
                                                         pack('I', len(name_val)), name_val.encode('utf-8')])
            else:
                len_val = len(name_val) + 24
                VirtualControlInputCmdString = b''.join([pack('4I', 0x00447040, len_val, 0, 0), 
                                                         pack('I', len(name_val)), name_val.encode('utf-8'),
                                                         pack('I', DeactivationTypeStates[qualifier['Deactivation Type']])])
            self.__SetHelper('VirtualControlInput', VirtualControlInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualControlInput')

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

        self.SetLogin( None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.RoutedChannels = {}
        
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()