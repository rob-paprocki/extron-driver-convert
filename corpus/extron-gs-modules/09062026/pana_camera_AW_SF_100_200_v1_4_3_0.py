import base64
from re import compile, search
import urllib.error
import urllib.request


class DeviceClass:
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

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberOfFaceRecognitionEntries = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AngleMode': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraConnection': {'Parameters': ['Camera ID'], 'Status': {}},
            'FaceRecognition': {'Parameters': ['Camera ID'], 'Status': {}},
            'FaceRecognitionNavigation': {'Status': {}},
            'FaceRecognitionResult': {'Parameters': ['Entry'], 'Status': {}},
            'FaceRecognitionSearch': {'Status': {}},
            'FaceRecognitionSet': {'Parameters': ['Camera ID', 'Entry'], 'Status': {}},
            'FaceRecognitionUpdate': {'Status': {}},
            'Heartbeat': {'Status': {}},
            'ManualDetection': {'Parameters': ['Camera ID', 'X Position', 'Y Position'], 'Status': {}},
            'TargetDetectionStatus': {'Parameters': ['Camera ID'], 'Status': {}},
            'Tracking': {'Parameters': ['Camera ID'], 'Status': {}},
        }

        self.AngleMode = compile('angle_type:(0|1|2|3)')
        self.CameraConnection = compile('connection:(0|1)')
        self.FaceRecognition = compile('face_recognition:(0|1)')
        self.TargetDetection = compile('detection:(0|1)')
        self.Tracking = compile('tracking:(0|1)')
        self.Datalist = compile('data_list:([\\S\\s]+),page_num:([0-9]{1,3})')
        self.Target = compile('id:([0-9]{1,3}),key_id:[0-9]{1,3},target_name:\"([\\S ]+?)\",face_contents')

        self.NameList = []
        self.IDList = []

    @property
    def NumberOfFaceRecognitionEntries(self):
        return self._NumberOfFaceRecognitionEntries

    @NumberOfFaceRecognitionEntries.setter
    def NumberOfFaceRecognitionEntries(self, value):
        self._NumberOfFaceRecognitionEntries = int(value)
        self.directory = Directory('FaceRecognitionResult', self._NumberOfFaceRecognitionEntries, filler='')
        self.directory.write_status_function = self.WriteStatus

    def SetAngleMode(self, value, qualifier):

        ValueStateValues = {
            'Upper Body': 'upper',
            'Full Body': 'body',
            'Full': 'full',
            'Off': 'off'
        }

        camID = int(qualifier['Camera ID'])
        if 1 <= camID <= 99 and value in ValueStateValues:
            AngleModeCmdString = '/cgi-bin/auto_tracking?cmd=Angle&id={0}&mode={1}'.format(camID, ValueStateValues[value])
            self.__SetHelper('AngleMode', value, qualifier, AngleModeCmdString)
        else:
            self.Discard('Invalid Command for SetAngleMode')

    def UpdateAngleMode(self, value, qualifier):

        camID = qualifier['Camera ID']
        if 1 <= int(camID) <= 99:
            self.UpdateCameraConnection(None, {'Camera ID': camID})
        else:
            self.Discard('Invalid Command for UpdateAngleMode')

    def SetCameraConnection(self, value, qualifier):

        ValueStateValues = {
            'Connect': 'start',
            'Disconnect': 'stop'
        }

        camID = int(qualifier['Camera ID'])
        if 1 <= camID <= 99 and value in ValueStateValues:
            CameraConnectionCmdString = '/cgi-bin/auto_tracking?cmd=CameraControl&id={0}&control={1}'.format(camID, ValueStateValues[value])
            self.__SetHelper('CameraConnection', value, qualifier, CameraConnectionCmdString)
        else:
            self.Discard('Invalid Command for SetCameraConnection')

    def UpdateCameraConnection(self, value, qualifier):

        CamConnectionStates = {
            '1': 'Connect',
            '0': 'Disconnect'
        }

        TrackingStates = {
            '1': 'Start',
            '0': 'Stop'
        }

        TargetDetectingStates = {
            '1': 'Detected',
            '0': 'Not Detected'
        }

        AngleModeStates = {
            '0': 'Upper Body',
            '1': 'Full Body',
            '2': 'Full',
            '3': 'Off'
        }

        FaceRecognitionStates = {
            '1': 'On',
            '0': 'Off'
        }

        camID = int(qualifier['Camera ID'])
        if 1 <= camID <= 99:
            CameraConnectionCmdString = '/cgi-bin/auto_tracking?cmd=CameraState&id={0}'.format(camID)
            res = self.__UpdateHelper('CameraConnection', value, qualifier, CameraConnectionCmdString)
            if res:
                try:
                    mGroup = self.CameraConnection.search(res)
                    if mGroup is not None:
                        value = mGroup.group(1)
                    else:
                        value = ''
                    self.WriteStatus('CameraConnection', CamConnectionStates[value], {'Camera ID': str(camID)})
                except KeyError:
                    self.Error(['Camera Connection: Invalid/unexpected response'])
                try:
                    mGroup = self.Tracking.search(res)
                    if mGroup is not None:
                        value = mGroup.group(1)
                    else:
                        value = ''
                    self.WriteStatus('Tracking', TrackingStates[value], {'Camera ID': str(camID)})
                except KeyError:
                    self.Error(['Tracking: Invalid/unexpected response'])
                try:
                    mGroup = self.TargetDetection.search(res)
                    if mGroup is not None:
                        value = mGroup.group(1)
                    else:
                        value = ''
                    self.WriteStatus('TargetDetectionStatus', TargetDetectingStates[value], {'Camera ID': str(camID)})
                except KeyError:
                    self.Error(['Target Detection Status: Invalid/unexpected response'])
                try:
                    mGroup = self.AngleMode.search(res)
                    if mGroup is not None:
                        value = mGroup.group(1)
                    else:
                        value = ''
                    self.WriteStatus('AngleMode', AngleModeStates[value], {'Camera ID': str(camID)})
                except KeyError:
                    self.Error(['Angle Mode: Invalid/unexpected response'])
                try:
                    mGroup = self.FaceRecognition.search(res)
                    if mGroup is not None:
                        value = mGroup.group(1)
                    else:
                        value = ''
                    self.WriteStatus('FaceRecognition', FaceRecognitionStates[value], {'Camera ID': str(camID)})
                except KeyError:
                    self.Error(['Face Recognition: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCameraConnection')

    def SetFaceRecognition(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        camID = int(qualifier['Camera ID'])
        if 1 <= camID <= 99 and value in ValueStateValues:
            FaceRecognitionCmdString = '/cgi-bin/auto_tracking?cmd=CameraSetting&id={0}&face_recognition={1}'.format(camID, ValueStateValues[value])
            self.__SetHelper('FaceRecognition', value, qualifier, FaceRecognitionCmdString)
        else:
            self.Discard('Invalid Command for SetFaceRecognition')

    def UpdateFaceRecognition(self, value, qualifier):

        camID = qualifier['Camera ID']
        if 1 <= int(camID) <= 99:
            self.UpdateCameraConnection(None, {'Camera ID': camID})
        else:
            self.Discard('Invalid Command for UpdateFaceRecognition')

    def SetFaceRecognitionNavigation(self, value, qualifier):

        if value == 'Up':
            self.directory.scroll_up(1)
        elif value == 'Down':
            self.directory.scroll_down(1)
        elif value == 'Page Up':
            self.directory.scroll_up(self._NumberOfFaceRecognitionEntries)
        elif value == 'Page Down':
            self.directory.scroll_down(self._NumberOfFaceRecognitionEntries)

    def SetFaceRecognitionUpdate(self, value, qualifier):

        FaceRecognitionUpdateCmdString = '/cgi-bin/auto_tracking?cmd=GetFaceRecognition&page=0&data_num={}'.format(self._NumberOfFaceRecognitionEntries)
        res = self.__UpdateHelper('FaceRecognitionUpdate', value, qualifier, FaceRecognitionUpdateCmdString)
        if res:
            try:
                self.NameList = []
                self.IDList = []
                TotalPageNum = int(self.Datalist.search(res).group(2))  # Get required number of query
                result = self.Datalist.search(res).group(1)
                result = result.split('},{')
                for i in range(0, len(result)):
                    ID = self.Target.search(result[i]).group(1)
                    self.IDList.append(ID)
                    Name = self.Target.search(result[i]).group(2)
                    self.NameList.append(Name)

                for j in range(1, TotalPageNum):
                    FaceRecognitionUpdateCmdString = '/cgi-bin/auto_tracking?cmd=GetFaceRecognition&page={}&data_num={}'.format(j, self._NumberOfFaceRecognitionEntries)
                    res = self.__UpdateHelper('FaceRecognitionUpdate', value, qualifier, FaceRecognitionUpdateCmdString)
                    if res:
                        result = self.Datalist.search(res).group(1)
                        result = result.split('},{')
                        for i in range(0, len(result)):
                            ID = self.Target.search(result[i]).group(1)
                            self.IDList.append(ID)
                            Name = self.Target.search(result[i]).group(2)
                            self.NameList.append(Name)

                new_facerecognition_data = ['{0} : {1}'.format(entry[0], entry[1]) for entry in zip(self.IDList, self.NameList)]
                new_facerecognition_data.append('*** End of List ***')
                self.directory.reset(new_facerecognition_data)
                self.Advance = True
            except (KeyError, IndexError, AttributeError):
                self.Error(['Face Recognition Update: Invalid/unexpected response'])

    def SetFaceRecognitionSearch(self, value, qualifier):

        NewNameList = []
        NewIDList = []
        SearchString = value
        if SearchString:
            for i in range(0, len(self.NameList)):
                if SearchString.lower() in self.NameList[i].lower():
                    NewNameList.append(self.NameList[i])
                    NewIDList.append(self.IDList[i])

            new_facerecognition_data = ['{0} : {1}'.format(entry[0], entry[1]) for entry in zip(NewIDList, NewNameList)]
            new_facerecognition_data.append('*** End of List ***')
            self.directory.reset(new_facerecognition_data)
            self.Advance = True
        else:
            self.Discard('Invalid Command for SetFaceRecognitionSearch')

    def SetFaceRecognitionSet(self, value, qualifier):

        camID = int(qualifier['Camera ID'])
        entry = qualifier['Entry']

        if 1 <= camID <= 99 and 1 <= entry <= 15:
            ID = self.ReadStatus('FaceRecognitionResult', {'Entry': entry})
            if ID and ID != '*** End of List ***':
                ID = ID.split(' : ')
                FaceRecognitionSetCmdString = '/cgi-bin/auto_tracking?cmd=CameraSetting&id={0}&face_recognition_id={1}'.format(camID, ID[0])
                self.__SetHelper('FaceRecognitionSet', value, qualifier, FaceRecognitionSetCmdString)
            else:
                self.Discard('Invalid Command for SetFaceRecognitionSet')
        else:
            self.Discard('Invalid Command for SetFaceRecognitionSet')

    def UpdateHeartbeat(self, value, qualifier):

        CamConnectionStates = {
            '1': 'Connect',
            '0': 'Disconnect'
        }

        TrackingStates = {
            '1': 'Start',
            '0': 'Stop'
        }

        TargetDetectingStates = {
            '1': 'Detected',
            '0': 'Not Detected'
        }

        AngleModeStates = {
            '0': 'Upper Body',
            '1': 'Full Body',
            '2': 'Full',
            '3': 'Off'
        }

        FaceRecognitionStates = {
            '1': 'On',
            '0': 'Off'
        }

        HeartbeatCmdString = '/cgi-bin/auto_tracking?cmd=CameraState&id=1'
        res = self.__UpdateHelper('Heartbeat', value, qualifier, HeartbeatCmdString)
        if res:
            try:
                mGroup = self.CameraConnection.search(res)
                if mGroup is not None:
                    value = mGroup.group(1)
                else:
                    value = ''
                self.WriteStatus('CameraConnection', CamConnectionStates[value], {'Camera ID': '1'})
            except KeyError:
                self.Error(['Camera Connection: Invalid/unexpected response'])
            try:
                mGroup = self.Tracking.search(res)
                if mGroup is not None:
                    value = mGroup.group(1)
                else:
                    value = ''
                self.WriteStatus('Tracking', TrackingStates[value], {'Camera ID': '1'})
            except KeyError:
                self.Error(['Tracking: Invalid/unexpected response'])
            try:
                mGroup = self.TargetDetection.search(res)
                if mGroup is not None:
                    value = mGroup.group(1)
                else:
                    value = ''
                self.WriteStatus('TargetDetectionStatus', TargetDetectingStates[value], {'Camera ID': '1'})
            except KeyError:
                self.Error(['Target Detection Status: Invalid/unexpected response'])
            try:
                mGroup = self.AngleMode.search(res)
                if mGroup is not None:
                    value = mGroup.group(1)
                else:
                    value = ''
                self.WriteStatus('AngleMode', AngleModeStates[value], {'Camera ID': '1'})
            except KeyError:
                self.Error(['Angle Mode: Invalid/unexpected response'])
            try:
                mGroup = self.FaceRecognition.search(res)
                if mGroup is not None:
                    value = mGroup.group(1)
                else:
                    value = ''
                self.WriteStatus('FaceRecognition', FaceRecognitionStates[value], {'Camera ID': '1'})
            except KeyError:
                self.Error(['Face Recognition: Invalid/unexpected response'])

    def SetManualDetection(self, value, qualifier):

        camID = int(qualifier['Camera ID'])
        XPos = qualifier['X Position']
        YPos = qualifier['Y Position']
        if 1 <= camID <= 99 and XPos and YPos:
            ManualDetectionCmdString = '/cgi-bin/auto_tracking?cmd=Detect&id={0}&process=start&mode=manual&position_x={1}&position_y={2}'.format(camID, XPos, YPos)
            self.__SetHelper('ManualDetection', value, qualifier, ManualDetectionCmdString)
        else:
            self.Discard('Invalid Command for SetManualDetection')

    def UpdateTargetDetectionStatus(self, value, qualifier):

        camID = qualifier['Camera ID']
        if 1 <= int(camID) <= 99:
            self.UpdateCameraConnection(None, {'Camera ID': camID})
        else:
            self.Discard('Invalid Command for UpdateTargetDetectionStatus')

    def SetTracking(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop'
        }

        camID = int(qualifier['Camera ID'])
        if 1 <= camID <= 99 and value in ValueStateValues:
            TrackingCmdString = '/cgi-bin/auto_tracking?cmd=Tracking&id={0}&process={1}'.format(camID, ValueStateValues[value])
            self.__SetHelper('Tracking', value, qualifier, TrackingCmdString)
        else:
            self.Discard('Invalid Command for SetTracking')

    def UpdateTracking(self, value, qualifier):

        camID = qualifier['Camera ID']
        if 1 <= int(camID) <= 99:
            self.UpdateCameraConnection(None, {'Camera ID': camID})
        else:
            self.Discard('Invalid Command for UpdateTracking')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        response = response.read().decode()
        if 'resp:"nack"' in response:
            self.Error(['{} : Invalid/unexpected response'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        my_request = urllib.request.Request(url)  # method defaults to GET when data is None

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):
        url = '{0}{1}'.format(self.RootURL.rstrip('/'), resource)
        my_request = urllib.request.Request(url)  # method defaults to GET when data is None

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False
                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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


class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
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

def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res

    return wrapper

class Directory:

    def __init__(self, write_function_name, display_count, filler=None):
        self.write_function_name = write_function_name
        self._display_count = int(display_count)
        self.qualifier_name = 'Entry'
        self._qualifier_type = 'Number'

        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
        self.entry_function = lambda entry: entry

    @property
    def display_count(self):
        return self._display_count

    @property
    def qualifier_type(self):
        return self._qualifier_type

    @qualifier_type.setter
    def qualifier_type(self, value):
        if value in ('Enum', 'Number'):
            self._qualifier_type = value

    def write_to_driver(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            if self.entry_function(entry[0]) and self.entry_function(entry[0]) != '*** End of List ***':
                self.Advance = True
                self.write_status_function(self.write_function_name, self.entry_function(entry[0]), {self.qualifier_name: position_value})
            elif self.entry_function(entry[0]) and self.entry_function(entry[0]) == '*** End of List ***':
                self.Advance = False
                self.write_status_function(self.write_function_name, '*** End of List ***', {self.qualifier_name: position_value})
            else:
                self.Advance = False
                for i in range(position_value,  self._display_count +1):
                    if self._qualifier_type == 'Number':
                        self.write_status_function(self.write_function_name, '', {self.qualifier_name: i})
                    else:
                        self.write_status_function(self.write_function_name, '', {self.qualifier_name: str(i)})

    def write_status_function(self, value, qualifier, context):
        pass

    @UseAutoUpdate
    def add_entry(self, entry):
        if isinstance(entry, list):
            self.entry_list.extend(entry)
        else:
            self.entry_list.append(entry)

    @UseAutoUpdate
    def reset(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = 0

    @UseAutoUpdate
    def remove_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_displayed_entries(self):

        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1

            index += 1

    def __display_position_check(self, position):

        return 0 < position <= self._display_count

    @UseAutoUpdate
    def scroll_up(self, step=1):
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0

    @UseAutoUpdate
    def scroll_down(self, step=1):
        if self._start_index + step < len(self.entry_list) and self.Advance:
            self._start_index += step
        elif self._start_index + step >= len(self.entry_list) and self.Advance:
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1
