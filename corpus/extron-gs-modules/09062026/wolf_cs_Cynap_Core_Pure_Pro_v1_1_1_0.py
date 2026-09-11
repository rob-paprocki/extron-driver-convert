from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack, unpack
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
        self._NumberofFileListSearch = 5
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BYODPinDisplay': { 'Status': {}},
            'EndPresentation': {'Parameters':['Delete Recordings Folder', 'Delete Snapshots Folder','Power Off Mode'], 'Status': {}},
            'FileListNavigation': { 'Status': {}},
            'FileListSearchResults': {'Parameters':['Button'], 'Status': {}},
            'FileListSearchSet': {'Parameters': ['File List Root Path'],  'Status': {}},
            'FileListUpdate': {'Parameters': ['File List Root Path'], 'Status': {}},
            'LoginCommand': {'Parameters': ['Password'], 'Status': {}},
            'MasterMute': { 'Status': {}},
            'MasterVolume': { 'Status': {}},
            'OpenFileCommand': {'Status': {}},
            'PowerOff': { 'Status': {}},
            'StreamingMode': { 'Status': {}},
            'VideoRecording': { 'Status': {}},
            'VisualizerControl': {'Parameters':['Window'], 'Status': {}},
            'WindowStart': {'Parameters':['Window'], 'Status': {}},
            'WindowControlClose': {'Parameters':['Window'], 'Status': {}},
            'WindowControlFullscreen': {'Parameters':['Window'], 'Status': {}},
            'WindowStatus': {'Parameters':['Window'], 'Status': {}},
            'ZoomMeetingID': { 'Status': {}},
            'ZoomMeetingName': { 'Status': {}},
            'ZoomMeetingPassword': { 'Status': {}},
            'ZoomMeetingStart': {'Parameters':['Window','Type', 'Meeting ID', 'Meeting Name', 'Meeting Password'], 'Status': {}},
            'ZoomWebconferenceControl': {'Parameters':['Window'], 'Status': {}},
        }

        self.OpenFileString = None
        self.WindowSourceStartIndex = 0
        
        if self.Unidirectional == 'False':
            self.deliRex = {
                'BYODPinDisplay' : re.compile(b'\x08\xCB\xE4\x05[\x01\x02]([0-9]{4})'),
                'FileListUpdate' : re.compile(b'([\x80-\x8F]\xCB\x3E\x01)|(?:\x0A\x01\xCB\x3E[\x00-\xFF]{4}\[[\s\S]*?\n\])'),
                'StreamingMode' : re.compile(b'\x08\xCB\x20\x01[\x00\x01]'),
                'WindowStatus' : re.compile(b'\x0C\xCB\xBA[\s\S]{2,800}')
            }

        self.file_list = Directory('FileListSearchResults', self._NumberofFileListSearch, filler='')
        self.file_list.write_status_function = self.WriteStatus

    @property
    def NumberofFileListSearch(self):
        return self._NumberofFileListSearch

    @NumberofFileListSearch.setter
    def NumberofFileListSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofFileListSearch = value
            self.file_list = Directory('FileListSearchResults', self._NumberofFileListSearch, filler='')
        else:
            self.Error(['The value of Number of File List Search is outside of the range of allowable values.'])

    def UpdateBYODPinDisplay(self, value, qualifier):

        BYODPinDisplayCmdString = b'\x08\xCB\xE4\x00'
        res = self.__UpdateHelper('BYODPinDisplay', BYODPinDisplayCmdString, value, qualifier)
        if res:
            try:
                value = res[5:].decode()
                self.WriteStatus('BYODPinDisplay', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['BYOD Pin Display: Invalid/unexpected response'])

    def SetEndPresentation(self, value, qualifier):

        DeleteRecordingsFolderStates = {
            'Yes': b'\x01', 
            'No' : b'\x00'
        }

        DeleteSnapshotsFolderStates = {
            'Yes': b'\x01', 
            'No' : b'\x00'
        }

        PowerOffModeStates = {
            'New Presentation' : b'\x00', 
            'Standby'          : b'\x01', 
            'Screen Off'       : b'\x02', 
            'Screensaver'      : b'\x03'
        }

        recordFolderState = qualifier['Delete Recordings Folder']
        snapshotFolderState = qualifier['Delete Snapshots Folder']
        powerOffModeState = qualifier['Power Off Mode']
        if (recordFolderState in DeleteRecordingsFolderStates and 
            snapshotFolderState in DeleteSnapshotsFolderStates and 
            powerOffModeState in PowerOffModeStates):
            EndPresentationCmdString = b''.join([b'\x09\xCB\x49\x03', 
                                                DeleteRecordingsFolderStates[recordFolderState],
                                                DeleteSnapshotsFolderStates[snapshotFolderState],
                                                PowerOffModeStates[powerOffModeState]])
            self.__SetHelper('EndPresentation', EndPresentationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEndPresentation')

    def SetFileListUpdate(self, value, qualifier):

        if qualifier is None:
            temp_value = ''
        else:
            temp_value = qualifier['File List Root Path']
        lenField = pack('>H', len(temp_value))
        CmdString = b''.join([b'\x0C\xCB\x3E', lenField, bytes(temp_value, 'utf-8')])
        res = self.SendAndWait(CmdString, self.DefaultResponseTimeout, deliRex=self.deliRex['FileListUpdate'])
        if res:
            try:        	
                if res[0:1] == b'\x0A':
                    new_directory_data = ['Name: {}/\r\nType: {}'.format(entry['name'], entry['type']) if entry['type'] == 'dir' else 'Name: {}\r\nType: {}'.format(entry['name'], entry['type']) for entry in json.loads(res[8:].decode())]
                    new_directory_data.append('*** End of List ***')
                    new_directory_data.append('')
                    self.file_list.reset(new_directory_data)    
                else:
                    self.Error(['File List Update: Invalid/unexpected response'])
            except(ValueError, KeyError, IndexError):
                self.Error(['File List Update: Invalid/unexpected response'])

    def SetFileListNavigation(self, value, qualifier):

        if value == 'Up':
            self.file_list.scroll_up(1)
        elif value == 'Down':
            self.file_list.scroll_down(1)
        elif value == 'Page Up':
            self.file_list.scroll_up(self._NumberofFileListSearch)
        elif value == 'Page Down':
            self.file_list.scroll_down(self._NumberofFileListSearch)
        else:
            self.Discard('Invalid Command for SetFileListNavigation')

    def SetFileListSearchSet(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : self._NumberofFileListSearch
        }

        file_path = qualifier['File List Root Path']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and file_path:
            fileName = self.ReadStatus('FileListSearchResults', {'Button': value})
            if fileName not in ['***Not Available***', '*** End of List ***']:
                fileName1 = ['{}{}'.format(file_path,entry[6:]) if 'Name' in entry else '' for entry in fileName.split('\r\n')][0]
                self.OpenFileString = fileName1
        else:
            self.Discard('Invalid Command for SetFileListSearchSet')

    def SetLoginCommand(self, value, qualifier):

        if value == 'Admin':
            if self.devicePassword and len(self.devicePassword) < 64:
                len_field1 = pack('B', len(self.devicePassword) + 2)
                len_field2 = pack('B', len(self.devicePassword))
                LoginCommandCmdString = b''.join([b'\x09\xCB\x42', len_field1, b'\x02', len_field2, bytes(self.devicePassword, 'utf-8')])
                self.__SetHelper('LoginCommand', LoginCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoginCommand')
        else:
            password_ = qualifier['Password']
            if password_ and len(password_) < 64:
                len_field1 = pack('B', len(password_) + 2)
                len_field2 = pack('B', len(password_))
                LoginCommandCmdString = b''.join([b'\x09\xCB\x42', len_field1, b'\x01', len_field2, bytes(password_, 'utf-8')])
                self.__SetHelper('LoginCommand', LoginCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoginCommand')

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On':     b'\x01', 
            'Off':    b'\x00',
            'Toggle': b'\x02'
        }

        if value in ValueStateValues:
            MasterMuteCmdString = b''.join([b'\x09\xCB\x58\x01', ValueStateValues[value]])
            self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterMute')

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = b''.join([b'\x09\xCB\x56\x01', pack('B',value)])
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def SetOpenFileCommand(self, value, qualifier):

        temp_value = self.OpenFileString
        if temp_value:
            len_field = pack('>H', len(temp_value))
            OpenFileCommandCmdString = b''.join([b'\x0D\xCB\x3C', len_field, bytes(temp_value, 'utf-8')])
            self.__SetHelper('OpenFileCommand', OpenFileCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOpenFileCommand')

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = b'\x09\xCB\x0C\x01\x00'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetStreamingMode(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x09\xCB\x20\x01\x01', 
            'Off': b'\x09\xCB\x20\x01\x00'
        }

        if value in ValueStateValues:
            StreamingModeCmdString = ValueStateValues[value]
            self.__SetHelper('StreamingMode', StreamingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamingMode')

    def UpdateStreamingMode(self, value, qualifier):

        StreamingModeCmdString = b'\x08\xCB\x20\x00'
        res = self.__UpdateHelper('StreamingMode', StreamingModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    1 : 'On',
                    0 : 'Off'
                }

                value = ValueStateValues[res[-1]]
                self.WriteStatus('StreamingMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Streaming Mode: Invalid/unexpected response'])

    def SetVideoRecording(self, value, qualifier):

        ValueStateValues = {
            'Start'         : b'\x00', 
            'Pause/Resume'  : b'\x01', 
            'Stop'          : b'\x02'
        }

        if value in ValueStateValues:
            VideoRecordingCmdString = b''.join([b'\x09\xCB\x25\x01', ValueStateValues[value]])
            self.__SetHelper('VideoRecording', VideoRecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoRecording')

    def SetVisualizerControl(self, value, qualifier):

        WindowStates = {
            '1' : b'\x00',
            '2' : b'\x01',
            '3' : b'\x02',
            '4' : b'\x03'
        }

        ValueStateValues = {
            'Auto Focus On'             : b'\x04',
            'Auto Focus Off'            : b'\x05',
            'Freeze On'                 : b'\x06',
            'Freeze Off'                : b'\x07',
            'Preset Save'               : b'\x08',
            'Preset Recall'             : b'\x09',
            'Auto Focus Toggle'         : b'\x0A',
            'Freeze Toggle'             : b'\x0B',
            'Power On'                  : b'\x0C',
            'Power Off'                 : b'\x0D',
            'Power Toggle'              : b'\x0E',
            'Light On'                  : b'\x0F',
            'Light Off'                 : b'\x10',
            'Light Toggle'              : b'\x11',
            'Capture Area Shift On'     : b'\x12',
            'Capture Area Shift Off'    : b'\x13',
            'Capture Area Shift Toggle' : b'\x14',
            'One-Push Auto Focus'       : b'\x15'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            VisualizerControlCmdString = b''.join([b'\x09\xCB\x29\x02', WindowStates[qualifier['Window']], ValueStateValues[value]])
            self.__SetHelper('VisualizerControl', VisualizerControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVisualizerControl')

    def SetWindowControlClose(self, value, qualifier):

        WindowStates = {
            '1' : b'\x00',
            '2' : b'\x01',
            '3' : b'\x02',
            '4' : b'\x03'
        }

        if qualifier['Window'] in WindowStates:
            WindowControlCloseCmdString = b''.join([b'\x09\xCB\x28\x02', WindowStates[qualifier['Window']], b'\x00'])
            self.__SetHelper('WindowControlClose', WindowControlCloseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowControlClose')

    def SetWindowControlFullscreen(self, value, qualifier):

        WindowStates = {
            '1' : b'\x00',
            '2' : b'\x01',
            '3' : b'\x02',
            '4' : b'\x03'
        }

        ValueStateValues = {
            'On'  : b'\x01',
            'Off' : b'\x02'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            WindowControlFullscreenCmdString = b''.join([b'\x09\xCB\x28\x02', WindowStates[qualifier['Window']], ValueStateValues[value]])
            self.__SetHelper('WindowControlFullscreen', WindowControlFullscreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowControlFullscreen')

    def UpdateWindowControlFullscreen(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def SetWindowStart(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1'         : b'\x02\x00\x01\x00',
            'HDMI 2'         : b'\x02\x00\x01\x01',
            'Webcam 1'       : b'\x10\x00\x01\x00', 
            'Webcam 2'       : b'\x10\x00\x01\x01',
            'Stream Input 1' : b'\x11\x00\x01\x00',
            'Stream Input 2' : b'\x11\x00\x01\x01',
            'Stream Input 3' : b'\x11\x00\x01\x02',
            'Stream Input 4' : b'\x11\x00\x01\x03',
            'Stream Input 5' : b'\x11\x00\x01\x04',
            'Stream Input 6' : b'\x11\x00\x01\x05',
            'Stream Input 7' : b'\x11\x00\x01\x06',
            'Stream Input 8' : b'\x11\x00\x01\x07',
            'Stream Input 9' : b'\x11\x00\x01\x08',
            'Stream Input 10': b'\x11\x00\x01\x09',
            'Stream Input 11': b'\x11\x00\x01\x0A',
            'Stream Input 12': b'\x11\x00\x01\x0B',
            'Stream Input 13': b'\x11\x00\x01\x0C',
            'Stream Input 14': b'\x11\x00\x01\x0D',
            'Stream Input 15': b'\x11\x00\x01\x0E',
            'Stream Input 16': b'\x11\x00\x01\x0F',
            'Stream Input 17': b'\x11\x00\x01\x10',
            'Stream Input 18': b'\x11\x00\x01\x11',
            'Stream Input 19': b'\x11\x00\x01\x12',
            'Stream Input 20': b'\x11\x00\x01\x13'
        }

        window = qualifier['Window']
        if window in ['1', '2', '3', '4', 'Auto Arrange'] and value in ValueStateValues:
            window = 0xFF if window == 'Auto Arrange' else int(window)-1
            win_field = pack('B', window)
            WindowStartCmdString = b''.join([b'\x0D\xCB\x2C\x00\x05', win_field, ValueStateValues[value]])
            self.__SetHelper('WindowStart', WindowStartCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowStart')

    def UpdateWindowStatus(self, value, qualifier):

        StatusVal = {
            0 : 'Off',
            1 : 'On',
        }

        WindowType = {
            0 : 'None',
            1 : 'Visualizer',
            2 : 'HDMI',
            3 : 'Browser',
            4 : 'Miracast',
            5 : 'Airplay/Chromecast',
            6 : 'Video',
            7 : 'vSolution Cast/App',
            8 : 'Image',
            9 : 'PDF',
            10 : 'Office PPT/PPTX',
            11 : 'Office DOC/DOCX/TXT',
            12 : 'Office XLS/XLSX',
            13 : 'Whiteboard',
            14 : 'Audio',
            15 : 'Webconference',
            16 : 'Webcam',
            17 : 'Stream Input',
            19 : 'Office 365 Outlook',
            20 : 'Office 365 Word',
            21 : 'Office 365 Excel',
            22 : 'Office 365 PowerPoint',
            23 : 'Office 365 OneNote',
            24 : 'vMatrix Pull Stream',
            25 : 'vMatrix Push Stream',
            26 : 'vMatrix Station Browser',
            27 : 'Office 365 Teams',
            28 : 'vMatrix Groupwork Stream',
            29 : 'Zoom Webconference',
            30 : 'Office365 Whiteboard',
            255 : 'Restricted Window'
        }

        if 1 <= int(qualifier['Window']) <= 4:
            WindowStatusCmdString = b'\x08\xCB\xBA\x00'
            res = self.SendAndWait(WindowStatusCmdString, self.DefaultResponseTimeout, deliRex=self.deliRex['WindowStatus'])
            if res:
                try:
                    endFound = False
                    pointer = 9
                    totalLen = unpack('>H', res[3:5])[0]
                    sourceList = list()
                    position = 1

                    while not endFound:
                        try:
                            blockType = WindowType[res[pointer + 1]]
                            sourceList.append('{}'.format(blockType))
                        except (ValueError, IndexError, AttributeError):
                            self.Error(['Window Status: Invalid/unexpected response'])

                        try:
                            fullscreen = StatusVal[res[pointer + 2]]
                            self.WriteStatus('WindowControlFullscreen', fullscreen, {'Window': str(position)})
                        except:
                            self.Error(['Window Control Fullscreen: Invalid/unexpected response'])

                        typeSpecLen = unpack('>H', res[(pointer + 15):(pointer + 17)])[0]

                        position += 1
                        pointer += 14 + 3 + typeSpecLen
                        if pointer >= totalLen:
                            endFound = True

                    self.WindowStatus = sourceList
                    self.__WindowStatusPositionHandler()

                except (KeyError, IndexError):
                    self.Error(['Window Control Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateWindowStatus')

    def __WindowStatusPositionHandler(self):    

        index = self.WindowSourceStartIndex # default is 0. Will change if FileListNavigation is used
        position = 1
        while index < len(self.WindowStatus):
            self.WriteStatus('WindowStatus', self.WindowStatus[index], {'Window' : str(position)})
            position += 1
            index += 1
        else:
            while position <= 4:
                self.WriteStatus('WindowStatus', '', {'Window' : str(position)})
                position += 1

    def SetZoomMeetingStart(self, value, qualifier):

        TypeStates = ('Host', 'Join')
        WindowStates = ('1', '2', '3', '4', 'Auto Arrange')

        window = qualifier['Window']
        type_val = qualifier['Type']
        id_val = qualifier['Meeting ID']
        name_val = qualifier['Meeting Name']
        password_val = qualifier['Meeting Password']
        if (window in WindowStates and type_val in TypeStates and
                id_val and name_val and password_val):
            window = 0xFF if window == 'Auto Arrange' else int(window)-1
            win_field = pack('B', window)
            parameter_field = b''.join([b'?type=', bytes(type_val.lower(), 'utf-8'), b'&id=', bytes(id_val, 'utf-8'),
                                        b'&name=', bytes(name_val, 'utf-8'), b'&password=', bytes(password_val, 'utf-8')])
            if len(parameter_field) <= 65531:
                parameter_fieldLen = pack('>H', len(parameter_field))
                command_fieldLen = pack('>H', len(parameter_field) + 4)
                ZoomMeetingStartCmdString = b''.join([b'\x0D\xCB\x2C', command_fieldLen, win_field, b'\x1D',
                                                    parameter_fieldLen, parameter_field])
                self.__SetHelper('ZoomMeetingStart', ZoomMeetingStartCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetZoomMeetingStart')
        else:
            self.Discard('Invalid Command for SetZoomMeetingStart')

    def SetZoomWebconferenceControl(self, value, qualifier):

        WindowStates = ('1', '2', '3', '4')

        ValueStateValues = {
            'Toggle Audio Mute'                                           : b'\x00', 
            'Leave Meeting'                                               : b'\x01', 
            'Toggle Screenshare'                                          : b'\x02', 
            'Toggle Video Mute'                                           : b'\x03', 
            'End Local Meeting'                                           : b'\x04', 
            'Toggle Audio Mute for All Participants (Local Meeting Only)' : b'\x05', 
            'Toggle Show Participants'                                    : b'\x06'
        }

        window = qualifier['Window']
        if window in WindowStates and value in ValueStateValues:
            ZoomWebconferenceControlCmdString = b''.join([b'\x09\xCD\x04\x02', pack('B', int(window)-1), ValueStateValues[value]])
            self.__SetHelper('ZoomWebconferenceControl', ZoomWebconferenceControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomWebconferenceControl')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if (response[0] >> 4) > 0:
                self.Error(['Command {0}: Error occurred.'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=4)
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.deliRex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetLoginCommand('Admin', None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.OpenFileString = None
        self.WindowSourceStartIndex = 0

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

def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res
    return wrapper

class Directory:
    
    def __init__(self, write_function_name, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Button'
        self._qualifier_type = 'Number'
        self._write_function_name = write_function_name
        
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
                self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value})
            elif self.entry_function(entry[0]) and self.entry_function(entry[0]) == '*** End of List ***':
                self.Advance = False
                self.write_status_function(self._write_function_name, '*** End of List ***', {self.qualifier_name : position_value})
            else:
                self.Advance = False
                for i in range(position_value,  self._display_count+1):
                    if self._qualifier_type == 'Number':
                        self.write_status_function(self._write_function_name, '', {self.qualifier_name : i})
                    else:
                        self.write_status_function(self._write_function_name, '', {self.qualifier_name : str(i)})

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
            self._start_index = len(self.entry_list) - 1 # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0
    
    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0
    
    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1