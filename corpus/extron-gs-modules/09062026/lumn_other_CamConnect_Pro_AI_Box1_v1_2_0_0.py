from extronlib.interface import EthernetClientInterface
from extronlib.system import Wait, ProgramLog

import json
import re
import struct
import random
import array
from base64 import encodebytes as base64encode

FIN = 0x80
OPCODE = 0x0f
MASKED = 0x80
PAYLOAD_LEN = 0x7f
PAYLOAD_LEN_EXT16 = 0x7e
PAYLOAD_LEN_EXT64 = 0x7f
TEXT = 0x1

def _mask(_m, _d):
    for i in range(len(_d)):
        _d[i] ^= _m[i % 4]
    return _d.tostring()

class DeviceClass:

    def __init__(self, IPAddress):

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
            'CameraConnect': {'Parameters':['IP Address'], 'Status': {}},
            'Focus': {'Parameters':['IP Address'], 'Status': {}},
            'FocusMode': {'Parameters':['IP Address'], 'Status': {}},
            'PanTilt': {'Parameters':['IP Address'], 'Status': {}},
            'Preset': {'Parameters':['IP Address','Action'], 'Status': {}},
            'ProfileCommand': {'Parameters':['Action', 'Name'], 'Status': {}},
            'VideoSourceLayout': { 'Status': {}},
            'VideoSourcePosition': {'Parameters':['Camera'], 'Status': {}},
            'VideoStreaming': { 'Status': {}},
            'VoiceTracking': { 'Status': {}},
            'Zoom': {'Parameters':['IP Address'], 'Status': {}},
        }

        self.ipAddress = IPAddress
        self.uri = '/'
        self._handshake = (
            "GET %(uri)s HTTP/1.1\r\n"
            "Host: %(ipAddress)s\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Origin: https://%(origin)s\r\n"
            "Sec-WebSocket-Key: %(randomstring)s\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )

    def SetLoginHandShake(self, value, url):
        handshake = self._handshake % {'uri': self.uri, 'ipAddress': self.ipAddress, "origin": self.ipAddress, 'randomstring': self.generatestring()}
        self.Send(handshake)

    def SetCameraConnect(self, value, qualifier):

        if qualifier['IP Address'] and value in ['Connect', 'Disconnect']:
            CameraConnectCmdString = {
                "Command": "Camera"+value,
                "IPAddress" : qualifier['IP Address']
            }
            self.__SetHelper('CameraConnect', CameraConnectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraConnect')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':  'Start',
            'Near': 'Start',
            'Stop': 'Stop'
        }

        if qualifier['IP Address'] and value in ValueStateValues:
            FocusCmdString = {
                "Command": "SetFocus"+ValueStateValues[value],
                "IPAddress": qualifier['IP Address']
            }
            if value != 'Stop':
                FocusCmdString["Direction"] = value
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        if qualifier['IP Address'] and value in ('Auto', 'Manual'):
            FocusModeCmdString = {
                "Command": "SetFocusMode",
                "IPAddress": qualifier['IP Address'],
                "Mode": value
            }
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        if not qualifier['IP Address']:
            self.Discard('Invalid Command for UpdateFocusMode')
            return

        FocusModeCmdString = {
            "Command": "GetFocusMode",
            "IPAddress": qualifier['IP Address']
        }
        res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
        if res:
            try:
                value = res["Mode"]
                if value in ('Auto', 'Manual'):
                    self.WriteStatus('FocusMode', value, qualifier)
                else:
                    raise ValueError
            except (KeyError, ValueError):
                self.Error(['Focus Mode: Invalid/unexpected response'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Left Up':    ('Start', 'LeftUp'),
            'Up':         ('Start', 'Up'),
            'Right Up':   ('Start', 'RightUp'),
            'Left':       ('Start', 'Left'),
            'Right':      ('Start', 'Right'),
            'Left Down':  ('Start', 'LeftDown'),
            'Down':       ('Start', 'Down'),
            'Right Down': ('Start', 'RightDown'),
            'Stop':       ('Stop'),
            'Home':       ('Home')
        }

        if qualifier['IP Address'] and value in ValueStateValues:
            PanTiltCmdString = {
                "Command": "SetPanTilt"+ValueStateValues[value][0],
                "IPAddress": qualifier['IP Address']
            }
            if value not in ('Stop', 'Home'):
                PanTiltCmdString["Direction"] = ValueStateValues[value][1]
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 'Save',
            'Recall': 'Call'
        }

        if qualifier['IP Address'] and qualifier['Action'] in ActionStates and 0 <= value <= 255: # min/max values confirmed w/ manufacturer
            PresetCmdString = {
                "Command": "SetTo{}Preset".format(ActionStates[qualifier['Action']]),
                "IPAddress": qualifier['IP Address'],
                "Preset": value
            }
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetProfileCommand(self, value, qualifier):

        ActionStates = {
            'Save' : 'SaveAs',
            'Load' : 'Load'
        }

        if qualifier['Action'] in ActionStates and 1 <= int(value) <= 8:
            ProfileCmdString = {
                "Command": ActionStates[qualifier['Action']]+"Profile",
                "ID": int(value)
            }

            save_name = qualifier['Name']
            if save_name:
                ProfileCmdString = {
                    "Command": ActionStates[qualifier['Action']]+"Profile",
                    "Name": save_name,
                    "ID": int(value)
                }
            else:
                ProfileCmdString = {
                    "Command": ActionStates[qualifier['Action']]+"Profile",
                    "ID": int(value)
                }
            self.__SetHelper('ProfileCommand', ProfileCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProfileCommand')

    def SetVideoSourceLayout(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : 0,
            'Custom' : 1
        }

        if value in ValueStateValues:
            VideoSourceLayoutCmdString = {
                "Command": "SetVideoSourceLayoutDefine",
                "SourceLayoutDefine": ValueStateValues[value]
            }
            self.__SetHelper('VideoSourceLayout', VideoSourceLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoSourceLayout')

    def SetVideoSourcePosition(self, value, qualifier):

        if qualifier['Camera'] and 1 <= int(value) <= 4:
            VideoSourcePositionCmdString = {
                "Command": "SetVideoSourcePos"+value,
                "Camera": qualifier['Camera']
            }
            self.__SetHelper('VideoSourcePosition', VideoSourcePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoSourcePosition')

    def SetVideoStreaming(self, value, qualifier):

        ValueStateValues = {
            'On': 'Start',
            'Off': 'Stop'
            }

        if value in ValueStateValues:
            VideoStreamingCmdString = {"Command": ValueStateValues[value]+"VideoStreaming"}
            self.__SetHelper('VideoStreaming', VideoStreamingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoStreaming')

    def UpdateVideoStreaming(self, value, qualifier):

        ValueStateValues = {
            True: 'On',
            False: 'Off'
        }

        VideoStreamingCmdString = {"Command": "GetVideoOutputSetting"}
        res = self.__UpdateHelper('VideoStreaming', VideoStreamingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res["IsStartStreaming"]]
                self.WriteStatus('VideoStreaming', value, qualifier)
            except KeyError:
                self.Error(['Video Streaming: Invalid/unexpected response'])

    def SetVoiceTracking(self, value, qualifier):

        ValueStateValues = {
            'On'  : True,
            'Off' : False
        }

        if value in ValueStateValues:
            VoiceTrackingCmdString = {
                "Command": "SetVoiceTracking",
                "Status": ValueStateValues[value]
            }
            self.__SetHelper('VoiceTracking', VoiceTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVoiceTracking')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': ('Start', 'In'),
            'Wide': ('Start', 'Out'),
            'Stop': ('Stop')
        }

        if qualifier['IP Address'] and value in ValueStateValues:
            ZoomCmdString = {
                "Command": "SetZoom"+ValueStateValues[value][0],
                "IPAddress": qualifier['IP Address']
            }
            if value != 'Stop':
                ZoomCmdString["Direction"] = ValueStateValues[value][1]
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            results = json.loads(response.decode(), strict=False) # strict=False allows for control characters within JSON responses
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
            results = ''
        else:
            if "Reply" not in results:
                self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
                results = ''
        return results

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True' or command != 'VideoStreaming':
            self.send_text('Async', json.dumps(commandstring))
        else:
            res = self.send_text('Sync', json.dumps(commandstring))
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

            res = self.send_text('Sync', json.dumps(commandstring))
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetLoginHandShake(None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def generatestring(self):
        return base64encode('{}'.format(random.randint(-27555755, 666333366)).zfill(16).encode()).decode(
            'utf-8').strip()

    def get_mask_key(self):
        return '{}'.format(random.randint(0, 6553)).zfill(4).encode()

    def try_decode_UTF8(self, data):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return False
        except Exception as e:
            self.Error([str(e)])

    def encode_to_UTF8(self, data):
        try:
            return data.encode('utf-8', 'ignore')
        except UnicodeEncodeError as e:
            return False
        except Exception as e:
            self.Error([str(e)])

    def mask(self, mask_key, data):

        if data is None:
            data = ""

        _m = array.array("B", mask_key)
        _d = array.array("B", data)
        return _mask(_m, _d)

    def _get_masked(self, mask_key, message):
        s = self.mask(mask_key, message)
        return mask_key + s

    def send_text(self, send, message, masked=True, opcode=TEXT):

        if isinstance(message, bytes):
            message = self.try_decode_UTF8(message)  # this is slower but ensures we have UTF-8
            if not message:
                return False

        header = bytearray()
        payload = self.encode_to_UTF8(message)
        payload_length = len(payload)
        if payload_length <= 125:
            header.append(FIN | opcode)
            header.append(1 << 7 | payload_length)
        elif payload_length >= 126 and payload_length <= 65535:
            header.append(FIN | opcode)
            header.append(1 << 7 | PAYLOAD_LEN_EXT16)
            header.extend(struct.pack(">H", payload_length))
        elif payload_length < 18446744073709551616:
            header.append(FIN | opcode)
            header.append(1 << 7 | PAYLOAD_LEN_EXT64)
            header.extend(struct.pack(">Q", payload_length))

        else:
            self.Error(["Message is too big. Consider breaking it into chunks."])
            return

        if masked:
            mask_key = self.get_mask_key()
            cmdString = bytes(header + self._get_masked(mask_key, payload))
        else:
            cmdString = bytes(header + payload)

        if send == 'Async':
            self.Send(cmdString)
        else:
            return self.SendAndWait(cmdString, self.DefaultResponseTimeout, deliRex=re.compile(b'\{[\S\s]+\}'))

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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Hostname) 
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