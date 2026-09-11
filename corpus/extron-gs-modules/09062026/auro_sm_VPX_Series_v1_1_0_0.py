from extronlib.interface import SerialInterface, EthernetClientInterface
import json

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceMode': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'EncoderDeviceID': { 'Status': {}},
            'EncoderStreamCommand': {'Parameters':['Encoder Name', 'Encoder Number', 'Stream Type'], 'Status': {}},
            'LineInMute': { 'Status': {}},
            'LineInVolume': { 'Status': {}},
            'LineOutMute': { 'Status': {}},
            'LineOutVolume': { 'Status': {}},
            'LocalDisplaySource': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'StreamSource': { 'Status': {}},
            }

    def SetDeviceMode(self, value, qualifier):

        ValueStateValues = {
            'Encoder' : 'encoder', 
            'Decoder' : 'decoder'
        }

        if value in ValueStateValues:
            DeviceModeCmdString = 'set mode {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('DeviceMode', DeviceModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceMode')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            's_init':         'System Initialization Completed',
            's_idle':         'System Idle, Not Searching for Connections',
            's_attaching':    'Connecting to Decoder or Waiting for Video',
            's_srv_on':       'Connection Established, Video is Available',
            's_search':       'Connecting to Encoder',
            's_start_srv_lp': 'Connection Initiating',
            's_start_srv_hp': 'Connection Initiating',
            's_stop':         'Connection Stopped',
            's_error':        'Error',
        }

        DeviceStatusCmdString = 'get status\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except KeyError:
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateEncoderDeviceID(self, value, qualifier):

        EncoderDeviceIDCmdString = 'get remote_hostname\r'
        res = self.__UpdateHelper('EncoderDeviceID', EncoderDeviceIDCmdString, value, qualifier)
        if res:
            try:
                value = res['result']
                self.WriteStatus('EncoderDeviceID', value, qualifier)
            except KeyError:
                self.Error(['Encoder Device ID: Invalid/unexpected response'])

    def SetEncoderStreamCommand(self, value, qualifier):

        StreamTypeStates = {
            'HDMI': 'HDMI',
            'All': 'ALL',
            'Video': 'VIDEO',
            'Audio': 'AUDIO',
            'USB': 'USB',
            'IR': 'IR'
        }

        number = qualifier['Encoder Number']
        if number and number.isdigit():
            encNum = number.zfill(4)
        else:
            return self.Discard('Invalid Command for SetEncoderStreamCommand')
        
        name = qualifier['Encoder Name']
        encName = name if name else 'vpx-series' 

        if qualifier['Stream Type'] in StreamTypeStates and value in ['Connect', 'Disconnect']:
            if value == 'Connect':
                EncoderStreamCommandCmdString = 'join {0} {1}-enc-{2}\r'.format(StreamTypeStates[qualifier['Stream Type']], encName, encNum)
            else:
                EncoderStreamCommandCmdString = 'leave {0}\r'.format(StreamTypeStates[qualifier['Stream Type']])
            self.__SetHelper('EncoderStreamCommand', EncoderStreamCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEncoderStreamCommand')

    def SetLineInMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'mute',
            'Off': 'unmute'
        }

        if value in ValueStateValues:
            LineInMuteCmdString = 'set linein_volume {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('LineInMute', LineInMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInMute')

    def UpdateLineInMute(self, value, qualifier):

        MuteStates = {
            'enable': 'On',
            'disable': 'Off'
        }

        LineInMuteCmdString = 'get audio_settings\r'
        res = self.__UpdateHelper('LineInMute', LineInMuteCmdString, value, qualifier)
        if res:
            try:
                value = MuteStates[res['linein_mute']]
                self.WriteStatus('LineInMute', value, qualifier)
            except KeyError:
                self.Error(['Line In Mute: Invalid/unexpected response'])

            try:
                value = int(res['linein_vol'])
                self.WriteStatus('LineInVolume', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Line In Volume: Invalid/unexpected response'])

            try:
                value = MuteStates[res['lineout_mute']]
                self.WriteStatus('LineOutMute', value, qualifier)
            except KeyError:
                self.Error(['Line Out Mute: Invalid/unexpected response'])

            try:
                value = int(res['lineout_vol'])
                self.WriteStatus('LineOutVolume', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Line Out Volume: Invalid/unexpected response'])

    def SetLineInVolume(self, value, qualifier):

        if 0 <= value <= 100:
            LineInVolumeCmdString = 'set linein_volume {0}\r'.format(value)
            self.__SetHelper('LineInVolume', LineInVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInVolume')

    def UpdateLineInVolume(self, value, qualifier):

        self.UpdateLineInMute(None, None)

    def SetLineOutMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'mute',
            'Off': 'unmute'
        }

        if value in ValueStateValues:
            LineOutMuteCmdString = 'set lineout_volume {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('LineOutMute', LineOutMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutMute')

    def UpdateLineOutMute(self, value, qualifier):

        self.UpdateLineInMute(None, None)

    def SetLineOutVolume(self, value, qualifier):

        if 0 <= value <= 100:
            LineOutVolumeCmdString = 'set lineout_volume {0}\r'.format(value)
            self.__SetHelper('LineOutVolume', LineOutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutVolume')

    def UpdateLineOutVolume(self, value, qualifier):

        self.UpdateLineInMute(None, None)

    def SetLocalDisplaySource(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'IN_PORT1',
            'HDMI 2': 'IN_PORT2',
            'Stream': 'STREAM'
        }

        if value in ValueStateValues:
            LocalDisplaySourceCmdString = 'set local_display_source {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('LocalDisplaySource', LocalDisplaySourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLocalDisplaySource')

    def UpdateLocalDisplaySource(self, value, qualifier):

        ValueStateValues = {
            'IN_PORT1' : 'HDMI 1', 
            'IN_PORT2' : 'HDMI 2', 
            'STREAM'   : 'Stream'
        }

        LocalDisplaySourceCmdString = 'get local_display_source\r'  
        res = self.__UpdateHelper('LocalDisplaySource', LocalDisplaySourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('LocalDisplaySource', value, qualifier)
            except KeyError:
                self.Error(['Local Display Source: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'reboot\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetStreamSource(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': 'IN_PORT1',
            'HDMI 2': 'IN_PORT2'
        }

        if value in ValueStateValues:
            StreamSourceCmdString = 'set stream_source {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('StreamSource', StreamSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamSource')

    def UpdateStreamSource(self, value, qualifier):

        ValueStateValues = {
            'IN_PORT1': 'HDMI 1', 
            'IN_PORT2': 'HDMI 2'
        }

        StreamSourceCmdString = 'get stream_source\r'
        res = self.__UpdateHelper('StreamSource', StreamSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('StreamSource', value, qualifier)
            except KeyError:
                self.Error(['Stream Source: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'INVALID PARAMETER'      : 'Invalid argument specified',
            'INVALID PARAMETER COUNT': 'Number parameters incorrect',
            'INVALID COMMAND'        : 'Command does not exist',
            'INVALID STATE'          : 'Failed to execute given current system state',
            'IO ERROR'               : 'Operation failed due to input/output error',
            'UNSUPPORTED FEATURE'    : 'Requested feature/module not supported'
        }

        try:
            results = json.loads(response.decode())
            if results['error'] != 'NULL':
                if results['error'].replace('_', ' ') in DEVICE_ERROR_CODES:
                    self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[results['error'].replace('_', ' ')])])
                else:
                    self.Error(['{0}: Unknown error occurred'.format(sourceCmdName)])
                return ''
            else:
                return results
        except (KeyError, json.decoder.JSONDecodeError):
            self.Error(['{0}: Invalid/unexpected response'.format(sourceCmdName)])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'}')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'}')
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

