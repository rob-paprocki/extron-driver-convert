from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import json
import re

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
            'DesiredDisplayMode': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Illumination': { 'Status': {}},
            'Input': { 'Status': {}},
            'InvertImageStereoGlassSync': { 'Status': {}},
            'LaserHours': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}}
        }

        self.delim = re.compile(b'{.*}+')

    def SetDesiredDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Mono':                     '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "Mono"}, "id": 270}\r\n',
            'Auto Stereo':              '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "AutoStereo"}, "id": 270}\r\n',
            'Active Stereo':            '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "ActiveStereo"}, "id": 270}\r\n',
            'Night Vision':             '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "NightVision"}, "id": 270}\r\n',
            'IG Pixel Shift':           '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "IGPixelShift"}, "id": 270}\r\n',
            'IG Pixel Shift NV':        '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "IGPixelShiftNV"}, "id": 270}\r\n',
            'IG Pixel Shift Full NV':   '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.display.desireddisplaymode", "value": "IGPixelShiftFullNV"}, "id": 270}\r\n'
        }

        if value in ValueStateValues:
            DesiredDisplayModeCmdString = ValueStateValues[value]
            self.__SetHelper('DesiredDisplayMode', DesiredDisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDesiredDisplayMode')
            
    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'In':   '{"jsonrpc": "2.0", "method": "optics.focus.stepforward", "params": {"steps": 1}, "id": 260}\r\n',
            'Out':  '{"jsonrpc": "2.0", "method": "optics.focus.stepreverse", "params": {"steps": 1}, "id": 260}\r\n'
        }

        if value in ValueStateValues:
            FocusCmdString = ValueStateValues[value]
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIllumination(self, value, qualifier):

        if 0 <= value <= 100:
            IlluminationCmdString = '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "illumination.sources.laser.power", "value": ' + str(float(value)) + '}, "id": 230}\r\n'
            self.__SetHelper('Illumination', IlluminationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIllumination')

    def UpdateIllumination(self, value, qualifier):

        IlluminationCmdString = '{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "illumination.sources.laser.power"}, "id": 230}\r\n'
        res = self.__UpdateHelper('Illumination', IlluminationCmdString, value, qualifier)
        if res:
            try:
                value = int(res['result'])
                self.WriteStatus('Illumination', value, qualifier)
            except (ValueError, KeyError, IndexError):
                self.Error(['Illumination: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'L1 DisplayPort':               '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 DisplayPort"}, "id": 150}\r\n',
            'L1 Quad SDI':                  '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 Quad SDI"}, "id": 150}\r\n',
            'L1 HDMI':                      '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 HDMI"}, "id": 150}\r\n',
            'L1 HDBaseT 1':                 '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 HDBaseT 1"}, "id": 150}\r\n',
            'L1 HDBaseT 2':                 '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 HDBaseT 2"}, "id": 150}\r\n',
            'L1 SDI A':                     '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 SDI A"}, "id": 150}\r\n',
            'L1 SDI B':                     '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 SDI B"}, "id": 150}\r\n',
            'L1 SDI C':                     '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 SDI C"}, "id": 150}\r\n',
            'L1 SDI D':                     '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L1 SDI D"}, "id": 150}\r\n',
            'L2 DisplayPort A':             '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 DisplayPort A"}, "id": 150}\r\n',
            'L2 DisplayPort B':             '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 DisplayPort B"}, "id": 150}\r\n',
            'L2 DisplayPort C':             '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 DisplayPort C"}, "id": 150}\r\n',
            'L2 DisplayPort D':             '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 DisplayPort D"}, "id": 150}\r\n',
            'L2 Dual DP - AB':              '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual DP - AB"}, "id": 150}\r\n',
            'L2 Dual DP - AC':              '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual DP - AC"}, "id": 150}\r\n',
            'L2 Dual DP - BD':              '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual DP - BD"}, "id": 150}\r\n',
            'L2 Dual DP - CD':              '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual DP - CD"}, "id": 150}\r\n',
            'L2 Dual Head DP - A|C':        '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual Head DP - A|C"}, "id": 150}\r\n',
            'L2 Dual Head DP - B|D':        '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual Head DP - B|D"}, "id": 150}\r\n',
            'L2 Dual Head Dual DP - AB|CD': '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Dual Head Dual DP - AB|CD"}, "id": 150}\r\n',
            'L2 Quad DP':                   '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Quad DP"}, "id": 150}\r\n',
            'L2 Quad column DP':            '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.window.main.source", "value": "L2 Quad column DP"}, "id": 150}\r\n'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'l1 displayport':               'L1 DisplayPort',
            'l1 hdmi':                      'L1 HDMI',
            'l1 hdbaset 1':                 'L1 HDBaseT 1',
            'l1 hdbaset 2':                 'L1 HDBaseT 2',
            'l1 sdi a':                     'L1 SDI A',
            'l1 sdi b':                     'L1 SDI B',
            'l1 sdi c':                     'L1 SDI C',
            'l1 sdi d':                     'L1 SDI D',
            'l1 quad sdi':                  'L1 Quad SDI',
            'l2 displayport a':             'L2 DisplayPort A',
            'l2 displayport b':             'L2 DisplayPort B',
            'l2 displayport c':             'L2 DisplayPort C',
            'l2 displayport d':             'L2 DisplayPort D',
            'l2 dual dp - ab':              'L2 Dual DP - AB',
            'l2 dual dp - ac':              'L2 Dual DP - AC',
            'l2 dual dp - bd':              'L2 Dual DP - BD',
            'l2 dual dp - cd':              'L2 Dual DP - CD',
            'l2 dual head dp - a|c':        'L2 Dual Head DP - A|C',
            'l2 dual head dp - b|d':        'L2 Dual Head DP - B|D',
            'l2 dual head dual dp - ab|cd': 'L2 Dual Head Dual DP - AB|CD',
            'l2 quad dp':                   'L2 Quad DP',
            'l2 quad column dp':            'L2 Quad column DP'
        }

        InputCmdString = '{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "image.window.main.source"}, "id": 150}\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = res['result'].lower()
                self.WriteStatus('Input', ValueStateValues[value], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetInvertImageStereoGlassSync(self, value, qualifier):

        ValueStateValues = {
            'On':  '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.stereo.glassync.invert", "value": true}, "id": 170}\r\n',
            'Off': '{"jsonrpc": "2.0", "method": "property.set", "params": {"property": "image.stereo.glassync.invert", "value": false}, "id": 170}\r\n'
        }

        if value in ValueStateValues:
            InvertImageStereoGlassSyncCmdString = ValueStateValues[value]
            self.__SetHelper('InvertImageStereoGlassSync', InvertImageStereoGlassSyncCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInvertImageStereoGlassSync')

    def UpdateInvertImageStereoGlassSync(self, value, qualifier):

        ValueStateValues = {
            True:  'On',
            False: 'Off'
        }

        InvertImageStereoGlassSyncCmdString = '{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "image.stereo.glassync.invert"}, "id": 170}\r\n'
        res = self.__UpdateHelper('InvertImageStereoGlassSync', InvertImageStereoGlassSyncCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('InvertImageStereoGlassSync', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invert Image Stereo Glass Sync: Invalid/unexpected response'])

    def UpdateLaserHours(self, value, qualifier):

        LaserHoursCmdString = '{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "statistics.laserruntime.value"}, "id": 2}\r\n'
        res = self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res['result']) // 3600
                self.WriteStatus('LaserHours', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Laser Hours: Invalid/unexpected response'])
    
    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '{"jsonrpc": "2.0", "method": "property.get", "params": {"property": "statistics.projectorruntime.value"}, "id": 1}\r\n'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res['result']) // 3600
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Operation Hours: Invalid/unexpected response'])
    
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  '{"jsonrpc": "2.0","method": "system.poweron","params": {},"id": 130}\r\n',
            'Off': '{"jsonrpc": "2.0","method": "system.poweroff","params": {},"id": 130}\r\n',
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'on':               'On',
            'ready':            'Off',
            'standby':          'Off',
            'conditioning':     'Warming Up',
            'deconditioning':   'Cooling Down',
            'boot':             'Booting Up',
            'eco':              'Eco / Power Save Mode',
            'service':          'Service',
            'error':            'Error'
        }

        PowerCmdString = '{"jsonrpc": "2.0","method": "property.get","params": {"property": "system.state"},"id": 130}\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            json_response = json.loads(response)

            if 'error' in json_response:
                self.Error(['{}: An error occurred: {}'.format(sourceCmdName, json_response['error']['message'])])
                return {}

            return json_response
        except json.decoder.JSONDecodeError:
            self.Error(['{}: An error occurred: received a malformed response'.format(sourceCmdName)])
        except Exception:
            self.Error(['{}: An unknown error occurred'.format(sourceCmdName)])

        return {}

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.delim)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return {}
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.delim)
            if not res:
                return {}
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()