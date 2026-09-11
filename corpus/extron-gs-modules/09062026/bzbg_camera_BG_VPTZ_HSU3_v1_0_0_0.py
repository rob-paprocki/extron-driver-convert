from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
import urllib.error
import urllib.request

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
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': { 'Status': {}},
            'FocusMode': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Type'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = pack('B', 0x80 + int(value))
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : b'\x02',
            'Near' : b'\x03',
            'Stop' : b'\x00'
        }

        if value in ValueStateValues:
            FocusCmdString = self._DeviceID + b'\x01\x04\x08' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : b'\x02',
            'Manual' : b'\x03'
        }

        if value in ValueStateValues:
            FocusModeCmdString = self._DeviceID + b'\x01\x04\x38' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        FocusModeCmdString = self._DeviceID + b'\x09\x04\x38\xFF'
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02 : 'Auto',
                    0x03 : 'Manual'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('FocusMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\x03\x01',
            'Down'      : b'\x03\x02',
            'Left'      : b'\x01\x03',
            'Right'     : b'\x02\x03',
            'Up Left'   : b'\x01\x01',
            'Up Right'  : b'\x02\x01',
            'Down Left' : b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop'      : b'\x03\x03',
            'Home'      : b'\x04',
            'Reset'     : b'\x05'
        }

        if 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 23 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = self._DeviceID + b'\x01\x06' + ValueStateValues[value] + b'\xFF'
            else:
                PanTiltCmdString = self._DeviceID + b'\x01\x06\x01' + pack('>2B', qualifier['Pan Speed'], qualifier['Tilt Speed']) + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02',
            'Off' : b'\x03'
        }

        if value in ValueStateValues:
            PowerCmdString = self._DeviceID + b'\x01\x04\x00' + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
    def UpdatePower(self, value, qualifier):

        PowerCmdString = self._DeviceID + b'\x09\x04\x00\xFF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x02 : 'On',
                    0x03 : 'Off'
                }

                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Recall' : b'\x02',
            'Save'   : b'\x01'
        }

        if qualifier['Type'] in TypeStates and 0 <= int(value) <= 254:
            PresetCmdString = self._DeviceID + b'\x01\x04\x3F' + TypeStates[qualifier['Type']] + pack('B', int(value)) + b'\xFF'
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele' : 0x20,
            'Wide' : 0x30,
            'Stop' : 0x00
        }

        zoom_speed = qualifier['Speed']
        if 0 <= zoom_speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                zoom_speed = 0x00
            else:
                zoom_speed += ValueStateValues[value]

            ZoomCmdString = self._DeviceID + b'\x01\x04\x07' + pack('B', zoom_speed) + b'\xFF'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) >= 4:
            address, errorbyte, errorcode, terminator = unpack('>4B', response[:4])
            if errorbyte & 0x60 == 0x60:
                self.Error(['An error occurred.'])
                return b''
            return response

        return b''

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
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

class DeviceHTTPClass:

    def __init__(self, ipAddress, port):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': { 'Status': {}},
            'FocusMode': { 'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'Preset': {'Parameters':['Type'], 'Status': {}},
            'Zoom': { 'Status': {}},
        }

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Add Start'      : 'focusadd_start',
            'Add Stop'       : 'focusadd_stop',
            'Decrease Start' : 'focusdec_start',
            'Decrease Stop'  : 'focusdec_stop'
        }

        if value in ValueStateValues:
            FocusCmdString = 'ajaxcom?szCmd={"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"' + ValueStateValues[value] + '","byValue":0}}}'
            self.__SetHelper('Focus', value, qualifier, url=FocusCmdString)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : '2',
            'Manual' : '3'
        }

        if value in ValueStateValues:
            FocusModeCmdString = 'ajaxcom?szCmd={"SetEnv":{"VideoParam":[{"stAF":{"emAFMode":' + ValueStateValues[value] + '},"nChannel":0}]}}'
            self.__SetHelper('FocusMode', value, qualifier, url=FocusModeCmdString)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Left Start'        : 'left_start',
            'Left Stop'         : 'left_stop',
            'Left Up Start'     : 'leftup_start',
            'Left Up Stop'      : 'leftup_stop',
            'Left Down Start'   : 'leftdown_start',
            'Left Down Stop'    : 'leftdown_stop',
            'Right Start'       : 'right_start',
            'Right Stop'        : 'right_stop',
            'Right Up Start'    : 'rightup_start',
            'Right Up Stop'     : 'rightup_stop',
            'Right Down Start'  : 'rightdown_start',
            'Right Down Stop'   : 'rightdown_stop',
            'Up Start'          : 'up_start',
            'Up Stop'           : 'up_stop',
            'Down Start'        : 'down_start',
            'Down Stop'         : 'down_stop',
            'Home'              : 'go_home'
        }

        if 0 <= qualifier['Speed'] <= 100 and value in ValueStateValues:
            PanTiltCmdString = 'ajaxcom?szCmd={"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"' + ValueStateValues[value] + '","byValue":' + str(qualifier['Speed']) + '}}}'
            self.__SetHelper('PanTilt', value, qualifier, url=PanTiltCmdString)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPreset(self, value, qualifier):

        TypeStates = {
            'Recall' : 'preset_call',
            'Save'   : 'preset_set'
        }

        if qualifier['Type'] in TypeStates and 0 <= int(value) <= 254:
            PresetCmdString = 'ajaxcom?szCmd={"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"' + TypeStates[qualifier['Type']] + '","byValue":' + str(value) + '}}}'
            self.__SetHelper('Preset', value, qualifier, url=PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')
            
    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Add Start'      : 'zoomadd_start',
            'Add Stop'       : 'zoomadd_stop',
            'Decrease Start' : 'zoomdec_start',
            'Decrease Stop'  : 'zoomdec_stop'
        }

        if value in ValueStateValues:
            ZoomCmdString = 'ajaxcom?szCmd={"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"' + ValueStateValues[value] + '","byValue":0}}}'
            self.__SetHelper('Zoom', value, qualifier, url=ZoomCmdString)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port)
        # Check if Model belongs to a subclass      
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')             
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])