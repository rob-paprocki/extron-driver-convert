from extronlib.software import SummitConnect
from extronlib.system import Wait, ProgramLog
import re
import time
import json

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
        self.VtlpName = 'Extron Control for Web'
        self.Models = {}

        self.Commands = {
            'AutoTracking' : {'Parameters': ['Camera ID'], 'Status' : {}},
            'ConnectionStatus': {'Status': {}},
            'CameraConnected': {'Status': {}},
            'CameraFrameSize': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraPeopleCount': {'Parameters': ['Camera ID'], 'Status' : {}},
            'CameraStreaming' :  {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraTrackingSpeed': {'Parameters': ['Camera ID'], 'Status': {}},
            'CurrentState': {'Status': {}},
            'Devices' : {'Status': {}},
            'DisplayCount': {'Status': {}},
            'PartNumber': {'Status': {}},
            'ExtronControl': {'Status': {}},
            'HideReturn': {'Status': {}},
            'LiteMode': { 'Status': {}},
            'MicConnected': {'Status': {}},
            'MTRDisplay': {'Status': {}},
            'PanTilt': {'Parameters': ['Camera ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Camera ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Camera ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Camera ID'], 'Status': {}},
            'RoomControl': {'Status': {}},
        }

        self.CameraPeopleCount = []

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"action":"change","name":"CameraAutoTracking","param":{"cameraId":"Camera([1-4])","newMode":"(GroupFraming|SpeakerFraming|PresenterFraming|PeopleFraming|Disable|NotSupported|Unknown)"}}'), self.__MatchAutoTracking, None)
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"CameraAutoTracking","param":{"cameraId":"Camera([1-4])","currentMode":"(GroupFraming|SpeakerFraming|PresenterFraming|PeopleFraming|Disable|NotSupported|Unknown)","supportedModes":\["[a-zA-z,"]+"\]}}'), self.__MatchAutoTracking, None)
            self.AddMatchString(re.compile(b'{"action":"error","name":"CameraAutoTracking","param":{"code":"(E25|E14|E30)","cameraId":"Camera([1-4])","message":"[a-zA-Z ]*"}}'), self.__MatchAutoTracking, 'Error')
            self.AddMatchString(re.compile(b'{"action":"change","name":"CameraFrameSize","param":{"cameraId":"Camera([1-4])","newFrameSize":"(Tight|Normal|Wide|NotSupported)"}}'), self.__MatchCameraFrameSize, None)
            self.AddMatchString(re.compile(b'{"action":"error","name":"CameraFrameSize","param":{"code":"(E25|E14|E30)","cameraId":"Camera([1-4])","message":"[a-zA-Z ]*"}}'), self.__MatchCameraFrameSize, 'Error')
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"CameraFrameSize","param":{"cameraId":"Camera([1-4])","currentFrameSize":"(Tight|Normal|Wide|NotSupported)","supportedFrameSizes":\["[a-zA-z,"]+"\]}}'), self.__MatchCameraFrameSize, None)
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"CameraPeopleCount","param":{"cameraId":"Camera([1-4])","value":(\d+)}}'), self.__MatchCameraPeopleCount, None)
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"CameraStreaming","param":{"cameraId":"Camera([1-4])","status":"(On|Off|NotSupported)"}}'), self.__MatchCameraStreaming, None)
            self.AddMatchString(re.compile(b'{"action":"change","name":"CameraTrackingSpeed","param":{"cameraId":"Camera([1-4])","newSpeed":"(Instant|Smooth|Moderate|NotSupported)"}}'), self.__MatchCameraTrackingSpeed, None)
            self.AddMatchString(re.compile(b'{"action":"response","name":"CameraTrackingSpeed","param":{"cameraId":"Camera([1-4])","currentSpeed":"(Instant|Smooth|Moderate|NotSupported)","supportedSpeeds":\["[a-zA-Z,"]+"\]}}'), self.__MatchCameraTrackingSpeed, None)
            self.AddMatchString(re.compile(b'{"action":"error","name":"CameraTrackingSpeed","param":{"code":"(E25|E14|E30)","cameraId":"Camera([1-4])","message":"[a-zA-Z ]*"}}'), self.__MatchCameraTrackingSpeed, 'Error')
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"Plugin","param":{"status":"(Shown|Hidden)"}}'), self.__MatchExtronControl, None)
            self.AddMatchString(re.compile(b'{"action":"response","name":"Plugin","param":{"partnumber":"(79-642-02)"}}'), self.__MatchPartNumber, None)
            self.AddMatchString(re.compile(b'hostname'), self.__MatchSendHostName, None)
            self.AddMatchString(re.compile(b'vtlpname'), self.__MatchSendVTLPName, None)
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"LiteMode","param":{"currentStatus":"(On|Off)"}}'), self.__MatchLiteMode, None)
            #self.AddMatchString(re.compile(b'{"action":"change","name":"MTRAppData","param":{"state":"Subscribed"}}'), self.__MatchMTRSubscribe, None)
            self.AddMatchString(re.compile(b'{"action":"response","name":"MTRAppData","param":{"status":({.*})}}'), self.__MatchCurrentState, None)
            self.AddMatchString(re.compile(b'{"action":"change","name":"MTRAppData","param":{"type":"status","name":"appState","newValue":"(SfbMeeting|TeamsMeeting|ThirdPartyMeeting|HdmiIngest|Idle)"}}'), self.__MatchCurrentState, 'Change')

            self.AddMatchString(re.compile(b'{"action":"response","name":"MTRAppData","param":{"devices":({.*})}}'), self.__MatchDevices, None)
            self.AddMatchString(re.compile(b'{"action":"change","name":"MTRAppData","param":({"type":"devices",.*})}'), self.__MatchDevices, 'Change')
            #self.AddMatchString(re.compile(b'{"action":"error","name":"CameraAutoTracking","param":{"code":"E25","message":"Camera([1-4])"}}'), self.__MatchNoCamera, None)
            #self.AddMatchString(re.compile(b'{"action":"change","name":"CameraPTZControl","param":
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"RoomControl","param":{"status":"(Enable|Disable)"}}'), self.__MatchRoomControl, None)
            self.AddMatchString(re.compile(b'{"action":(?:"response"|"change"),"name":"MTRDisplay","param":{"status":"(On|Off)"}}'), self.__MatchMTRDisplay, None)

    @property
    def VTLPName(self):
        return self.VtlpName

    @VTLPName.setter
    def VTLPName(self, value):
        self.VtlpName = value

    def SendVTLPName(self, value, qualifier):

        commandstring = json.dumps({"action": "get", "name": "Plugin", "param": {"vtlpname": "{}".format(self.VtlpName)}}, sort_keys = True).encode()
        self.Send(commandstring)

    def SendHostName(self, value, qualifier):

        commandstring = json.dumps({"action": "get", "name": "Plugin", "param": {"hostname": "{}".format(self.Hostname)}}, sort_keys = True).encode()
        self.Send(commandstring)

    def SendSubscribe(self, value, qualifier):
        commandstring = json.dumps({"action": "set", "name": "MTRAppData", "param": {"state": "Subscribe"}}, sort_keys = True).encode()
        self.Send(commandstring)

    def __MatchSendVTLPName(self, match, tag):

        self.SendVTLPName(None, None)

    def __MatchSendHostName(self, match, tag):

        self.SendHostName(None, None)

    def SetAutoTracking(self, value, qualifier):

        ValueStateValues = {
            'Group Framing' : 'GroupFraming', 
            'Speaker Framing' : 'SpeakerFraming',
            'Presenter Framing': 'PresenterFraming',
            'People Framing': 'PeopleFraming',
            'Disable': 'Disable',
        }

        if value in ValueStateValues and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            AutoTrackingCmdString = {"action": "set", "name": "CameraAutoTracking", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "newMode": "{}".format(ValueStateValues[value])}}
            self.__SetHelper('AutoTracking', AutoTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoTracking')

    def UpdateAutoTracking(self, value, qualifier):

        if qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            self.__UpdateHelper('AutoTracking', {"action": "get", "name": "CameraAutoTracking", "param": {"cameraId": "{}".format(qualifier['Camera ID'])}}, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoTracking')

    def __MatchAutoTracking(self, match, tag):

        CameraStateValues = {
                '1' : 'Camera1', 
                '2' : 'Camera2',
                '3' : 'Camera3',
                '4' : 'Camera4',
            }
        if tag == 'Error':
            ErrorStateValues = {
                'E14': 'Not Supported',
                'E25': 'Unknown',
                'E30': 'Unknown'
            }
            errorcode = ErrorStateValues[match.group(1).decode()]
            camera = CameraStateValues[match.group(2).decode()]
            self.WriteStatus('AutoTracking', errorcode, {'Camera ID': camera})
        else:    
            ValueStateValues = {
                                'GroupFraming' : 'Group Framing', 
                                'SpeakerFraming' : 'Speaker Framing',
                                'PresenterFraming' : 'Presenter Framing',
                                'PeopleFraming': 'People Framing',
                                'Disable': 'Disable',
                                'NotSupported': 'Not Supported',
                                'Unknown': 'Unknown'
                            }
            camera = CameraStateValues[match.group(1).decode()]
            self.WriteStatus('AutoTracking', ValueStateValues[match.group(2).decode()], {'Camera ID': camera})

    def __MatchNoCamera(self, match, tag):

        CameraStateValues = {
            '1' : 'Camera1', 
            '2' : 'Camera2',
            '3' : 'Camera3',
            '4' : 'Camera4',
        }
        
        camera = CameraStateValues[match.group(1).decode()]
        self.WriteStatus('AutoTracking', 'No Camera', {'Camera ID': camera})

    def __MatchPollCameras(self, match, tag):

        self.UpdateAutoTracking( None, {'Camera ID': 'Camera1'})
        self.UpdateAutoTracking( None, {'Camera ID': 'Camera2'})
        self.UpdateAutoTracking( None, {'Camera ID': 'Camera3'})
        self.UpdateAutoTracking( None, {'Camera ID': 'Camera4'})

    def SetCameraFrameSize(self, value, qualifier):
        
        if value in ['Normal', 'Tight', 'Wide'] and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            CameraFrameSizeCmdString = {"action": "set", "name": "CameraFrameSize", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "newFrameSize": "{}".format(value)}}
            self.__SetHelper('CameraFrameSize', CameraFrameSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFrameSize')

    def UpdateCameraFrameSize(self, value, qualifier):

        if qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            self.__UpdateHelper('CameraFrameSize', {"action": "get", "name": "CameraFrameSize", "param": {"cameraId": "{}".format(qualifier['Camera ID'])}}, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCameraFrameSize')

    def __MatchCameraFrameSize(self, match, tag):

        CameraStateValues = {
            '1' : 'Camera1', 
            '2' : 'Camera2',
            '3' : 'Camera3',
            '4' : 'Camera4',
        }
        if tag == 'Error':
            ErrorStateValues = {
                'E14': 'Not Supported',
                'E25': 'Unknown',
                'E30': 'Unknown'
            }
            errorcode = ErrorStateValues[match.group(1).decode()]
            camera = CameraStateValues[match.group(2).decode()]
            self.WriteStatus('CameraFrameSize', errorcode, {'Camera ID': camera})
        else:
            camera = CameraStateValues[match.group(1).decode()]
            framesize = match.group(2).decode()
            if framesize == 'NotSupported':
                framesize = 'Not Supported'
            self.WriteStatus('CameraFrameSize', framesize, {'Camera ID': camera})

    def SetCameraTrackingSpeed(self, value, qualifier):

        ValueStateValues = {
            'Instant' : 'Instant', 
            'Smooth' : 'Smooth',
            'Moderate': 'Moderate',
            'Not Supported': 'NotSupported',
        }

        if value in ValueStateValues and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            CameraTrackingSpeedCmdString = {"action": "set", "name": "CameraTrackingSpeed", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "newSpeed": "{}".format(ValueStateValues[value])}}
            self.__SetHelper('CameraTrackingSpeed', CameraTrackingSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraTrackingSpeed')

    def UpdateCameraTrackingSpeed(self, value, qualifier):

        if qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            self.__UpdateHelper('CameraTrackingSpeed', {"action": "get", "name": "CameraTrackingSpeed", "param": {"cameraId": "{}".format(qualifier['Camera ID'])}}, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCameraTrackingSpeed')

    def __MatchCameraTrackingSpeed(self, match, tag):

        CameraStateValues = {
            '1' : 'Camera1', 
            '2' : 'Camera2',
            '3' : 'Camera3',
            '4' : 'Camera4',
        }
        if tag == 'Error':
            ErrorStateValues = {
                'E14': 'Not Supported',
                'E25': 'Unknown',
                'E30': 'Unknown'
            }
            errorcode = ErrorStateValues[match.group(1).decode()]
            camera = CameraStateValues[match.group(2).decode()]
            self.WriteStatus('CameraTrackingSpeed', errorcode, {'Camera ID': camera})
        else:
            ValueStateValues = {
                'Instant' : 'Instant', 
                'Smooth' : 'Smooth',
                'Moderate': 'Moderate',
                'NotSupported': 'Not Supported',
            }
            
            camera = CameraStateValues[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('CameraTrackingSpeed', value, {'Camera ID': camera})

    def UpdatePartNumber(self, value, qualifier):

        self.__UpdateHelper('PartNumber', {"action": "get", "name": "Plugin", "param": {"attribute": "partnumber"}}, value, qualifier)

    def __MatchPartNumber(self, match, tag):

        self.WriteStatus('PartNumber', match.group(1).decode(), None)

    def UpdateDevices(self, value, qualifier):

        commandstring = json.dumps({"action": "get", "name": "MTRAppData", "param": {"type": "devices"}}).encode()
        self.Send(commandstring)

    def __MatchDevices(self, match, tag):

        if tag == 'Change':
            jsn = json.loads(match.group(1).decode())
            if jsn['name'] == 'connectedCameras':
                if jsn['newValue']:
                    self.WriteStatus('CameraConnected', 'True', None)
                else:
                    self.WriteStatus('CameraConnected', 'False', None)
            elif jsn['name'] == 'connectedMicrophones':
                if jsn['newValue']:
                    self.WriteStatus('MicConnected', 'True', None)
                else:
                    self.WriteStatus('MicConnected', 'False', None)
            elif jsn['name'] == 'displayCount':
                self.WriteStatus('DisplayCount', int(jsn['newValue']), None)
        else:
            jsn = match.group(1)
            jsn = jsn.replace(b'\\', b'')
            jsn = jsn.decode()
            jsn = json.loads(jsn)
            displaycount = jsn['displayCount']
            self.WriteStatus('DisplayCount', int(displaycount), None)
            try:
                if jsn['connectedMicrophones']:
                    self.WriteStatus('MicConnected', 'True', None)
                else:
                    self.WriteStatus('MicConnected', 'False', None)
            except KeyError:
                self.WriteStatus('MicConnected', 'False', None)
            try:
                if jsn['connectedCameras']:
                    self.WriteStatus('CameraConnected', 'True', None)
                else:
                    self.WriteStatus('CameraConnected', 'False', None)
            except KeyError:
                self.WriteStatus('CameraConnected', 'False', None)

    def UpdateDisplayCount(self, value, qualifier):

        self.UpdateDevices( None, None)

    def SetLiteMode(self, value, qualifier):

        if value in ['On', 'Off']:
            LiteModeCmdString = {"action": "set", "name": "LiteMode", "param": {"newStatus": "{}".format(value)}}
            self.__SetHelper('LiteMode', LiteModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLiteMode')

    def UpdateLiteMode(self, value, qualifier):

        self.__UpdateHelper('LiteMode', {"action": "get", "name": "LiteMode"}, value, qualifier)

    def __MatchLiteMode(self, match, tag):
        
        value = match.group(1).decode()
        self.WriteStatus('LiteMode', value, None)
    
    def UpdateMicConnected(self, value, qualifier):

        self.UpdateDevices( None, None)

    def UpdateCameraConnected(self, value, qualifier):

        self.UpdateDevices( None, None)

    def UpdateMTRDisplay(self, value, qualifier):

        self.__UpdateHelper('MTRDisplay', {"action": "get", "name": "MTRDisplay"}, value, qualifier)

    def __MatchMTRDisplay(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MTRDisplay', value, None)

    def UpdateCameraPeopleCount(self, value, qualifier):

        if qualifier['Camera ID'] not in self.CameraPeopleCount:
            commandstring = {"action": "set", "name": "CameraPeopleCount", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "status": "On"}}
            self.__UpdateHelper('CameraPeopleCount', commandstring, value, qualifier)
            self.CameraPeopleCount.append(qualifier['Camera ID'])
        commandstring = {"action": "get", "name": "CameraPeopleCount", "param": {"cameraId": "{}".format(qualifier['Camera ID'])}}
        self.__UpdateHelper('CameraPeopleCount', commandstring, value, qualifier)

    def __MatchCameraPeopleCount(self, match, tag):

        CameraStateValues = {
            '1' : 'Camera1',
            '2' : 'Camera2',
            '3' : 'Camera3',
            '4' : 'Camera4',
        }

        value = int(match.group(2).decode())
        camera = CameraStateValues[match.group(1).decode()]
        self.WriteStatus('CameraPeopleCount', value, {'Camera ID': camera})

    def UpdateCameraStreaming(self, value, qualifier):

        commandstring = {"action": "get", "name": "CameraStreaming", "param": {"cameraId": "{}".format(qualifier['Camera ID'])}}
        self.__UpdateHelper('CameraStreaming', commandstring, value, qualifier)

    def __MatchCameraStreaming(self, match, tag):

        CameraStateValues = {
            '1' : 'Camera1', 
            '2' : 'Camera2',
            '3' : 'Camera3',
            '4' : 'Camera4',
        }
        
        value = match.group(2).decode()
        if value == 'NotSupported':
            value = 'Not Supported'
        camera = CameraStateValues[match.group(1).decode()]
        self.WriteStatus('CameraStreaming', value, {'Camera ID': camera})

    def UpdateCurrentState(self, value, qualifier):

        self.__UpdateHelper('CurrentState', {"action": "get", "name": "MTRAppData", "param": {"type": "status"}}, value, qualifier)

    def __MatchCurrentState(self, match, tag):

        ValueStateValues = {
            'SfbMeeting' : 'Skype for Business Meeting',
            'TeamsMeeting' : 'Teams Meeting',
            'ThirdPartyMeeting' : 'Third Party Meeting',
            'HdmiIngest' : 'HDMI Ingest', 
            'Idle' :'Idle'
        }
        if tag == 'Change':
            self.WriteStatus('CurrentState', ValueStateValues[match.group(1).decode()], None)
        else:
            jsn = json.loads(match.group(1).decode())
            appState = jsn['appState']
            self.WriteStatus('CurrentState', ValueStateValues[appState], None)
            
    def SetExtronControl(self, value, qualifier):

        ValueStateValues = {
            'Show' : 'Show', 
            'Hide' : 'Hide'
        }

        if value in ValueStateValues:
            ExtronControlCmdString = {"action": "set", "name": "Plugin", "param": {"status": "{}".format(ValueStateValues[value])}}
            self.__SetHelper('ExtronControl', ExtronControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExtronControl')

    def UpdateExtronControl(self, value, qualifier):

        self.__UpdateHelper('ExtronControl', {"action": "get", "name": "Plugin", "param": {"attribute": "status"}}, value, qualifier)

    def __MatchExtronControl(self, match, tag):

        ValueStateValues = {
            'Shown' : 'Show', 
            'Hidden' : 'Hide'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExtronControl', value, None)
            
    def SetHideReturn(self, value, qualifier):

        self.__SetHelper('HideReturn', {"action": "set", "name": "Plugin", "param": {"status": "HideReturn"}}, value, qualifier)

    def SetPanTilt(self, value, qualifier):

        if value in ['Up', 'Down', 'Right', 'Left', 'Stop'] and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            PanTiltCmdString = {"action": "set", "name": "CameraPTZControl", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "direction": "{}".format(value)}}
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPresetRecall(self, value, qualifier):

        if value in ['Home', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            if value == 'Home':
                PresetRecallCmdString = {"action": "set", "name": "CameraPTZControl", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "direction": "Home"}}
            else:
                PresetRecallCmdString = {"action": "set", "name": "CameraPreset", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "preset": "{}".format(value), "mutator": "recall"}}
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if value in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            PresetRecallCmdString = {"action": "set", "name": "CameraPreset", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "preset": "{}".format(value), "mutator": "set"}}
            self.__SetHelper('PresetSave', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRoomControl(self, value, qualifier):

        ValueStateValues = {
            'Enable' : 'Enable',
            'Disable' : 'Disable'
        }

        if value in ValueStateValues:
            RoomControlCmdString = {"action": "set", "name": "RoomControl", "param": {"status": "{}".format(ValueStateValues[value])}}
            self.__SetHelper('RoomControl', RoomControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomControl')

    def UpdateRoomControl(self, value, qualifier):

        self.__UpdateHelper('RoomControl', {"action": "get", "name": "RoomControl", "param": {"attribute": "status"}}, value, qualifier)

    def __MatchRoomControl(self, match, tag):

        ValueStateValues = {
            'Enable' : 'Enable',
            'Disable' : 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RoomControl', value, None)

    def SetZoom(self, value, qualifier):

        if value in ['In', 'Out', 'Stop'] and qualifier['Camera ID'] in ['Camera1', 'Camera2', 'Camera3', 'Camera4']:
            if value != 'Stop':
                value = 'Zoom' + value
            ZoomCmdString = {"action": "set", "name": "CameraPTZControl", "param": {"cameraId": "{}".format(qualifier['Camera ID']), "direction": "{}".format(value)}}
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):
        
        self.Debug = True
        commandstring = json.dumps(commandstring, sort_keys=True).encode()
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        commandstring = json.dumps(commandstring).encode()
        self.Send(commandstring)

    
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SendVTLPName( None, None)
        self.SendHostName( None, None)
        self.SendSubscribe( None, None)
    
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
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


class EthernetClass(SummitConnect, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        SummitConnect.__init__(self, Hostname, IPPort)
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
        SummitConnect.Disconnect(self)
        self.OnDisconnected()