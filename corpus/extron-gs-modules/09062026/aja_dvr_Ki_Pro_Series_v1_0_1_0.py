from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import urllib.error
import urllib.request
import base64
from json import loads


class DeviceSerialClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'MenuNavigation': {'Status': {}},
            'Transport': {'Status': {}},
            }

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
           'Up': b'\x21\x13\x4A\x7E',
           'Down': b'\x21\x23\x4A\x8E',
           'Left': b'\x21\x23\x40\x84',
           'Right': b'\x21\x13\x40\x74'
           }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)



    def SetTransport(self, value, qualifier):

        TransportState = {
           'Play' : b'\x20\x01\x21',
           'Stop' : b'\x20\x00\x20',
           'Record' : b'\x20\x02\x22',
           'Eject' : b'\x20\x0F\x2F',
           'Fast Forward' : b'\x20\x10\x30',
           'Rewind' : b'\x20\x20\x40'
           }

        TransportCmdString = TransportState[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)


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

class DeviceHTTPClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInput': {'Status': {}},
            'CurrentClip': {'Status': {}},
            'CurrentPlaylist': {'Status': {}},
            'Input': {'Status': {}},
            'LoopPlay': {'Status': {}},
            'MediaAvailable': {'Status': {}},
            'PlayMedia': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'SystemState': {'Status': {}},
            'Timecode': {'Status': {}},
            'Transport': {'Status': {}},
            'TransportState': {'Status': {}},
        }


    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'SDI': '0',
            'XLR': '2',
            'HDMI': '3',
            'AES': '4'
        }

        AudioInputCmdString = 'config?action=set&paramid=eParamID_AudioInSelect&value={}'.format(ValueStateValues[value])
        self.__SetHelper('AudioInput', value, qualifier, url=AudioInputCmdString)

    def UpdateAudioInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'SDI',
            '2': 'XLR',
            '3': 'HDMI',
            '4': 'AES'
        }

        AudioInputCmdString = 'config?action=get&paramid=eParamID_AudioInSelect'
        res = self.__UpdateHelper('AudioInput', value, qualifier, url=AudioInputCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('AudioInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Input: Invalid/unexpected response'])

    def UpdateCurrentClip(self, value, qualifier):

        CurrentClipCmdString = 'config?action=get&paramid=eParamID_CurrentClip'
        res = self.__UpdateHelper('CurrentClip', value, qualifier, url=CurrentClipCmdString)
        if res:
            try:
                value = res['value']
                self.WriteStatus('CurrentClip', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Current Clip: Invalid/unexpected response'])

    def UpdateCurrentPlaylist(self, value, qualifier):

        CurrentPlaylistCmdString = 'config?action=get&paramid=eParamID_CurrentPlaylist'
        res = self.__UpdateHelper('CurrentPlaylist', value, qualifier, url=CurrentPlaylistCmdString)
        if res:
            try:
                value = res['value']
                self.WriteStatus('CurrentPlaylist', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Current Playlist: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'SDI 1': '0',
            'HDMI': '1',
            'Component': '2',
            'SDI 2': '4',
            'CVBS on Y': '5'
        }

        InputCmdString = 'config?action=set&paramid=eParamID_VideoInSelect&value={}'.format(ValueStateValues[value])
        self.__SetHelper('Input', value, qualifier, url=InputCmdString)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'SDI 1',
            '1': 'HDMI',
            '2': 'Component',
            '4': 'SDI 2',
            '5': 'CVBS on Y'
        }

        InputCmdString = 'config?action=get&paramid=eParamID_VideoInSelect'
        res = self.__UpdateHelper('Input', value, qualifier, url=InputCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLoopPlay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        LoopPlayCmdString = 'config?action=set&paramid=eParamID_LoopPlay&value={}'.format(ValueStateValues[value])
        self.__SetHelper('LoopPlay', value, qualifier, url=LoopPlayCmdString)

    def UpdateLoopPlay(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        LoopPlayCmdString = 'config?action=get&paramid=eParamID_LoopPlay'
        res = self.__UpdateHelper('LoopPlay', value, qualifier, url=LoopPlayCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('LoopPlay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Loop Play: Invalid/unexpected response'])

    def UpdateMediaAvailable(self, value, qualifier):

        MediaAvailableCmdString = 'config?action=get&paramid=eParamID_CurrentMediaAvailable'
        res = self.__UpdateHelper('MediaAvailable', value, qualifier, url=MediaAvailableCmdString)
        if res:
            try:
                value = int(res['value'])
                self.WriteStatus('MediaAvailable', value, qualifier)
            except (ValueError, KeyError):
                self.Error(['Media Available: Invalid/unexpected response'])

    def SetPlayMedia(self, value, qualifier):

        ValueStateValues = {
            'One': '0',
            'All': '1',
            'Playlist': '2'
        }

        PlayMediaCmdString = 'config?action=set&paramid=eParamID_PlayMedia&value={}'.format(ValueStateValues[value])
        self.__SetHelper('PlayMedia', value, qualifier, url=PlayMediaCmdString)

    def UpdatePlayMedia(self, value, qualifier):

        ValueStateValues = {
            '0': 'One',
            '1': 'All',
            '2': 'Playlist'
        }

        PlayMediaCmdString = 'config?action=get&paramid=eParamID_PlayMedia'
        res = self.__UpdateHelper('PlayMedia', value, qualifier, url=PlayMediaCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('PlayMedia', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Play Media: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 20:
            PresetRecallCmdString = 'config?action=set&paramid=eParamID_RegisterRecall&value={}'.format(value)
            self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 20:
            PresetSaveCmdString = 'config?action=set&paramid=eParamID_RegisterSave&value={}'.format(value)
            self.__SetHelper('PresetSave', value, qualifier, url=PresetSaveCmdString)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def UpdateSystemState(self, value, qualifier):

        ValueStateValues = {
            '0': 'Uninitialized',
            '1': 'Initializing Config',
            '2': 'Initializing Firmware',
            '3': 'Initialized',
            '4': 'Running',
            '5': 'Power Save',
            '6': 'Low Battery',
            '7': 'Shutdown Requested',
            '8': 'Shutting Down',
            '9': 'Shutdown',
            '10': 'Fatal Error'
        }

        SystemStateCmdString = 'config?action=get&paramid=eParamID_SystemState'
        res = self.__UpdateHelper('SystemState', value, qualifier, url=SystemStateCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('SystemState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System State: Invalid/unexpected response'])

    def UpdateTimecode(self, value, qualifier):

        TimecodeCmdString = 'config?action=get&paramid=eParamID_TransportTimecode'
        res = self.__UpdateHelper('Timecode', value, qualifier, url=TimecodeCmdString)
        if res:
            try:
                value = res['value']
                self.WriteStatus('Timecode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Timecode: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '1',
            'Record': '3',
            'Stop': '4',
            'Fast Forward': '5',
            'Fast Reverse': '6',
            'Single Step Forward': '7',
            'Single Step Reverse': '8',
            'Next Clip': '9',
            'Previous Clip': '10',
            'Variable Speed Play': '11',
            'Preroll': '12',
            'Assemble Edit': '13',
            'Cue': '14',
            'Shutdown': '15',
            'Play At System Time': '16',
            'Record At System Time': '17',
            'Go To Idle': '18'
        }

        TransportCmdString = 'config?action=set&paramid=eParamID_TransportCommand&value={}'.format(ValueStateValues[value])
        self.__SetHelper('Transport', value, qualifier, url=TransportCmdString)

    def UpdateTransportState(self, value, qualifier):

        ValueStateValues = {
            '0': 'Uninitialized',
            '1': 'Idle',
            '2': 'Recording',
            '3': 'Playing Forward',
            '4': 'Forward 2X',
            '5': 'Forward 4X',
            '6': 'Forward 8X',
            '7': 'Forward 16X',
            '8': 'Forward Step',
            '9': 'Playing Reverse',
            '10': 'Reverse 2X',
            '11': 'Reverse 4X',
            '12': 'Reverse 8X',
            '13': 'Reverse 16X',
            '14': 'Reverse Step',
            '15': 'Paused',
            '16': 'Error in Idle',
            '17': 'Error in Record',
            '18': 'Error in Play',
            '19': 'Error in Pause',
            '20': 'Shutdown'
        }

        TransportStateCmdString = 'config?action=get&paramid=eParamID_TransportState'
        res = self.__UpdateHelper('TransportState', value, qualifier, url=TransportStateCmdString)
        if res:
            try:
                value = ValueStateValues[res['value']]
                self.WriteStatus('TransportState', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Transport State: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = loads(response.read().decode())
        except ValueError:
            self.Error(['Invalid Response'])
            response = ''
        return response

    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            res = self.Opener.open(req)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL, url)
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            res = self.Opener.open(req)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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

class HTTPClass(DeviceHTTPClass):

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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