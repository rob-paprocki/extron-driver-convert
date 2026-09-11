# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
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

        self.devicePassword = None
        self.Models = {}

        self._NumberofContentSourceListSearch = 5
        self._NumberofMountListSearch = 5
        self._NumberofDownloadListSearch = 5
        self._NumberofFileListSearch = 5

        self.WindowSourceStartIndex = 0

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioControl': {'Parameters': ['Window'], 'Status': {}},
            'BoxnameCommand': {'Status': {}},
            'BoxnameStatus': {'Status': {}},
            'BrowserControl': {'Parameters': ['Window'], 'Status': {}},
            'CloudConnect': {'Parameters': ['Service'], 'Status': {}},
            'CloudUploadCommand': {'Parameters': ['Service'], 'Status': {}},
            'ContentSourceListNavigation': {'Status': {}},
            'ContentSourceListSearchResults': {'Parameters': ['Button'], 'Status': {}},
            'ContentSourceListUpdate': {'Status': {}},
            'DeleteFileCommand': {'Status': {}},
            'DownloadListFilenameResults': {'Parameters': ['Button'], 'Status': {}},
            'DownloadListNavigation': {'Status': {}},
            'DownloadListProgressResults': {'Parameters': ['Button'], 'Status': {}},
            'DownloadListStatusResults': {'Parameters': ['Button'], 'Status': {}},
            'DownloadListUpdate': {'Status': {}},
            'DualScreenAllowMirrorOverride': {'Status': {}},
            'DualScreenMirrorOverride': {'Status': {}},
            'DualScreenMode': {'Status': {}},
            'EndPresentation': {'Parameters': ['Recording', 'Snapshot'], 'Status': {}},
            'FileListUpdate': {'Status': {}},
            'FileListNavigation': {'Status': {}},
            'FileListSearchResults': {'Parameters': ['Button'], 'Status': {}},
            'FileListSearchSet': {'Status': {}},
            'FileUploadCommand': {'Status': {}},
            'FileUploadStatus': {'Status': {}},
            'FTPSendFileCommand': {'Status': {}},
            'ImageControl': {'Parameters': ['Window'], 'Status': {}},
            'ImageSnapshot': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'LoginCommand': {'Status': {}},
            'LoginLevelStatus': {'Status': {}},
            'LoginStatus': {'Status': {}},
            'MainFreeze': {'Status': {}},
            'MainResolution': {'Status': {}},
            'MasterMute': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'MenuNavigation': {'Parameters': ['Action'], 'Status': {}},
            'MicrophoneMute': {'Status': {}},
            'MicrophoneStatus': {'Status': {}},
            'Mirroring': {'Status': {}},
            'MountListNavigation': {'Status': {}},
            'MountListSearchResults': {'Parameters': ['Button'], 'Status': {}},
            'MountListUpdate': {'Status': {}},
            'Network': {'Parameters': ['Feature'], 'Status': {}},
            'OfficeControl': {'Parameters': ['Window'], 'Status': {}},
            'OpenFileCommand': {'Status': {}},
            'PanoptoStartRecording': {'Parameters':['IP Camera Mode','Folder ID','Filename Prefix'], 'Status': {}},
            'PDFControl': {'Parameters': ['Window'], 'Status': {}},
            'PinStatus': {'Parameters': ['Type'], 'Status': {}},
            'PinStatusNumber': {'Status': {}},
            'Power': {'Status': {}},
            'PresentationMode': {'Status': {}},
            'QRCode': {'Status': {}},
            'QRCodeURLReturned': {'Status': {}},
            'RecordingFunction': {'Status': {}},
            'RecordingResolution': {'Status': {}},
            'ScreensaverStatus': { 'Status': {}},
            'StreamingFramerate': {'Status': {}},
            'StreamingFunction': {'Status': {}},
            'StreamingIPAddress': {'Status': {}},
            'StreamingMode': {'Status': {}},
            'StreamingPort': {'Status': {}},
            'StreamingResolution': {'Status': {}},
            'USBCopyFileCommand': {'Status': {}},
            'VideoControl': {'Parameters': ['Window'], 'Status': {}},
            'VideoRecording': {'Status': {}},
            'VisualizerControl': {'Parameters': ['Window'], 'Status': {}},
            'VisualizerFocus': {'Parameters': ['Window', 'Speed'], 'Status': {}},
            'VisualizerZoom': {'Parameters': ['Window', 'Speed'], 'Status': {}},
            'WebcastStreamingMode': {'Status': {}},
            'WindowAirplayName': {'Parameters': ['Window'], 'Status': {}},
            'WindowAuxCopyControl': {'Parameters': ['Window'], 'Status': {}},
            'WindowControlClose': {'Parameters': ['Window'], 'Status': {}},
            'WindowControlFullscreen': {'Parameters': ['Window'], 'Status': {}},
            'WindowControlMute': {'Parameters': ['Window'], 'Status': {}},
            'WindowControlVolume': {'Parameters': ['Window'], 'Status': {}},
            'WindowImageNumberStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowMiracastName': {'Parameters': ['Window'], 'Status': {}},
            'WindowOfficePageStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowPDFPageStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowRecordingorStreamingStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowStart': {'Parameters': ['Window'], 'Status': {}},
            'WindowStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowvSolutionName': {'Parameters': ['Window'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x08\xCB\xD7\x01(\x00|\x01)'), self.__MatchDualScreenAllowMirrorOverride, None)
            self.AddMatchString(re.compile(b'\x08\xCB\xD8\x01(\x00|\x01)'), self.__MatchDualScreenMirrorOverride, None)
            self.AddMatchString(re.compile(b'\x08\xCB\\x5B\x01([\x00-\x05])'), self.__MatchDualScreenMode, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x03([\x00-\x20])([\x20-\x7F]{1,32})'), self.__MatchBoxnameStatus, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x4C\x02([\x00-\x04])([\x00-\x04])([\x00-\x04])([\x00-\x04])([\x00-\x04])([\x00-\x04])'), self.__MatchCloudConnect, None)
            self.AddMatchString(re.compile(b'\x08\xCB\xBE\x01([\x00-\x02])'), self.__MatchFileUploadStatus, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x55\x01([\x00-\x02])'), self.__MatchLoginLevelStatus, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x5A\x01(\x00|\x01)'), self.__MatchMainFreeze, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x58\x01(\x00|\x01)'), self.__MatchMasterMute, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x56\x01([\x00-\x64])'), self.__MatchMasterVolume, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x59\x01(\x00|\x01)'), self.__MatchMicrophoneMute, None)
            self.AddMatchString(re.compile(b'\x08\xCB\xEA\x01(\x00|\x01|\x02)'), self.__MatchMicrophoneStatus, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x3B\x03(\x00|\x01)[\x00-\xFF]{2}'), self.__MatchMirroring, None)
            self.AddMatchString(re.compile(b'\x08\xCB(\x36|\x37|\x86|\xB2)\x01(\x00|\x01)'), self.__MatchNetwork, None)
            self.AddMatchString(re.compile(b'\x08\xCB([\x53-\x54])([\x00-\x05])([\x00-\x01][0-9]{0,4})'), self.__MatchPinStatus, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x0C\x01(\x00|\x01)'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x38\x01(\x00|\x01)'), self.__MatchPresentationMode, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x92\x01(\x00|\x01)'), self.__MatchRecordingFunction, None)
            self.AddMatchString(re.compile(b'\x08\xCC\x76\x01([\x00-\x03])'), self.__MatchScreensaverStatus, None)
            self.AddMatchString(re.compile(b'\x08\xCB\\x24\x01(\x00|\x01|\x02)'), self.__MatchStreamingFramerate, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x93\x01(\x00|\x01)'), self.__MatchStreamingFunction, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x20\x01(\x00|\x01)'), self.__MatchStreamingMode, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x25\x05([\x00-\x02])[\x00-\xFF]{4}'), self.__MatchVideoRecording, None)
            self.AddMatchString(re.compile(b'\x08\xCC\\x5C\x01(\x00|\x01)'), self.__MatchWebcastStreamingMode, None)

            self.AddMatchString(re.compile(b'(\x09\xCB\x42\x00)|([\x80-\x8F]\xCB[\x42|\x0C][\x01|\x07-\x09])'), self.__MatchLoginStatus, None)
            self.AddMatchString(re.compile(b'\x88\xCB\xD8\x07'), self.__MatchNotAuthenticated, None)

            self.AddMatchString(re.compile(b'\x08\xCB\x88((?:\x01\x00)|(?:[\x02-\xFF]\x01http:\/\/[\s\S]*?))'), self.__MatchQRCode, None)
            self.AddMatchString(re.compile(b'\x08\xCB\x79[\x00-\xFF](\x00|\x01)([\x00-\x03])[\s\S]{0,253}'), self.__MatchInput, None)

            self.SyncRegex = {
                'ContentSourceListUpdate': re.compile(rb'\x0C\xCB\x90[\s\S]{2,800}'),
                'DownloadListUpdate': re.compile(rb'\x0C\xCB\x7B[\x00-\xFF]{2}(\[[\s\S]*?\])'),
                'FileListUpdate': re.compile(rb'([\x80-\x8F]\xCB\x3E\x01)|(?:\x0A\x01\xCB\x3E[\x00-\xFF]{4}\[[\s\S]*?\n\])'),
                'MountListUpdate': re.compile(rb'\x0C\xCB\x3D[\x00-\xFF]{2}(\[[\s\S]*?\])'),
                'WindowStatus': re.compile(rb'\x0C\xCB\xBA[\s\S]{2,800}')
            }

        self.WindowStatus = None

        self.IPAddressPattern = re.compile('(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})')

        self.content_source_list = Directory(self._NumberofContentSourceListSearch, filler='')
        self.content_source_list.write_status_function = self.writeContentSourceList

        self.mount_list = Directory(self._NumberofMountListSearch, filler='')
        self.mount_list.write_status_function = self.writeMountList

        self.download_list_filename = Directory(self._NumberofDownloadListSearch, filler='')
        self.download_list_filename.write_status_function = self.writelist_filename

        self.download_list_status = Directory(self._NumberofDownloadListSearch, filler='')
        self.download_list_status.write_status_function = self.writelist_status

        self.download_list_progress = Directory(self._NumberofDownloadListSearch, filler='')
        self.download_list_progress.write_status_function = self.writelist_progress

        self.file_list = Directory(self._NumberofFileListSearch, filler='')
        self.file_list.write_status_function = self.writefile_list

    def writeContentSourceList(self, value, qualifier):
        self.WriteStatus('ContentSourceListSearchResults', value, qualifier)

    def writeMountList(self, value, qualifier):
        self.WriteStatus('MountListSearchResults', value, qualifier)

    def writelist_filename(self, value, qualifier):
        self.WriteStatus('DownloadListFilenameResults', value, qualifier)

    def writelist_status(self, value, qualifier):
        self.WriteStatus('DownloadListStatusResults', value, qualifier)

    def writelist_progress(self, value, qualifier):
        self.WriteStatus('DownloadListProgressResults', value, qualifier)

    def writefile_list(self, value, qualifier):
        self.WriteStatus('FileListSearchResults', value, qualifier)

    @property
    def NumberofContentSourceListSearch(self):
        return self._NumberofContentSourceListSearch

    @NumberofContentSourceListSearch.setter
    def NumberofContentSourceListSearch(self, value):
        self._NumberofContentSourceListSearch = int(value)

    @property
    def NumberofMountListSearch(self):
        return self._NumberofMountListSearch

    @NumberofMountListSearch.setter
    def NumberofMountListSearch(self, value):
        self._NumberofMountListSearch = int(value)

    @property
    def NumberofDownloadListSearch(self):
        return self._NumberofDownloadListSearch

    @NumberofDownloadListSearch.setter
    def NumberofDownloadListSearch(self, value):
        self._NumberofDownloadListSearch = int(value)

    @property
    def NumberofFileListSearch(self):
        return self._NumberofFileListSearch

    @NumberofFileListSearch.setter
    def NumberofFileListSearch(self, value):
        self._NumberofFileListSearch = int(value)

    def __MatchLoginStatus(self, match, tag):

        if match.group(1):
            self.WriteStatus('LoginStatus', 'Login Successful', None)
        else:
            self.WriteStatus('LoginStatus', 'Login Failed', None)

    def __MatchNotAuthenticated(self, match, tag):

        self.Error(['Error: Not Authenticated.'])

    def SetAudioControl(self, value, qualifier):

        ValueStateValues = {
            'Play': b'\x00',
            'Pause': b'\x01',
            'Stop': b'\x02',
            'Forward': b'\x03',
            'Rewind': b'\x04',
            'Loop Off': b'\x07',
            'Loop On': b'\x08'
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            win_field = pack('B', window - 1)
            AudioControlCmdString = b''.join([b'\x0D\xCB\xA2\x00\x02', win_field, ValueStateValues[value]])
            self.__SetHelper('AudioControl', AudioControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioControl')

    def SetBoxnameCommand(self, value, qualifier):

        name = qualifier['Name']
        if name:
            len_name = pack('B', len(name))
            BoxnameCommandCmdString = b''.join([b'\x09\xCB\x03', len_name, bytes(name, 'utf-8')])
            self.__SetHelper('BoxnameCommand', BoxnameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBoxnameCommand')

    def UpdateBoxnameStatus(self, value, qualifier):

        BoxnameStatusCmdString = b'\x08\xCB\x03\x00'
        self.__UpdateHelper('BoxnameStatus', BoxnameStatusCmdString, value, qualifier)

    def __MatchBoxnameStatus(self, match, tag):

        str_len = ord(match.group(1))
        value = match.group(2)[:str_len].decode()
        self.WriteStatus('BoxnameStatus', value, None)

    def SetBrowserControl(self, value, qualifier):

        ValueStateValues = {
            'Reload': b'\x01',
            'Stop': b'\x02',
            'Zoom In': b'\x03',
            'Zoom Out': b'\x04',
            'Cursor Down': b'\x05',
            'Cursor Up': b'\x06',
            'Cursor Right': b'\x07',
            'Cursor Left': b'\x08',
            'Back': b'\x09',
            'Forward': b'\x0A',
            'Next Page (PDF View)': b'\x0B',
            'Previous Page (PDF View)': b'\x0C',
            'Zoom Full Height (PDF View)': b'\x0E',
            'Zoom Full Width (PDF View)': b'\x0F',
            'Zoom Full Page (PDF View)': b'\x10',
            'Scroll Down': b'\x11',
            'Scroll Up': b'\x12',
            'Scroll Right': b'\x13',
            'Scroll Left': b'\x14'
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            win_field = pack('B', window - 1)
            BrowserControlCmdString = b''.join([b'\x0D\xCB\x2A\x00\x02', win_field, ValueStateValues[value]])
            self.__SetHelper('BrowserControl', BrowserControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrowserControl')

    def SetCloudConnect(self, value, qualifier):

        ServiceStates = {
            'Dropbox': b'\x00',
            'Google Drive': b'\x01',
            'Box': b'\x02',
            'Jianguoyun': b'\x03',
            'OneDrive': b'\x04',
            'WebDAV': b'\x05'
        }

        ValueStateValues = {
            'Connect': b'\x01',
            'Disconnect': b'\x00'
        }

        Service = qualifier['Service']
        if Service in ServiceStates:
            CloudConnectCmdString = b''.join([b'\x09\xCB\x45\x02', ServiceStates[Service], ValueStateValues[value]])
            self.__SetHelper('CloudConnect', CloudConnectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCloudConnect')

    def UpdateCloudConnect(self, value, qualifier):

        CloudConnectCmdString = b'\x08\xCB\x4C\x00'
        self.__UpdateHelper('CloudConnect', CloudConnectCmdString, value, qualifier)

    def __MatchCloudConnect(self, match, tag):

        ValueStateValues = {
            b'\x02': 'Connect',
            b'\x00': 'Disconnect',
            b'\x01': 'Authentication',
            b'\x03': 'Failed',
            b'\x04': 'Synced'
        }

        value1 = ValueStateValues[match.group(1)]
        self.WriteStatus('CloudConnect', value1, {'Service': 'Dropbox'})
        value2 = ValueStateValues[match.group(2)]
        self.WriteStatus('CloudConnect', value2, {'Service': 'Google Drive'})
        value1 = ValueStateValues[match.group(3)]
        self.WriteStatus('CloudConnect', value1, {'Service': 'Box'})
        value2 = ValueStateValues[match.group(4)]
        self.WriteStatus('CloudConnect', value2, {'Service': 'Jianguoyun'})
        value1 = ValueStateValues[match.group(5)]
        self.WriteStatus('CloudConnect', value1, {'Service': 'OneDrive'})
        value2 = ValueStateValues[match.group(6)]
        self.WriteStatus('CloudConnect', value2, {'Service': 'WebDAV'})

    def SetCloudUploadCommand(self, value, qualifier):

        ServiceStates = {
            'Dropbox': b'\x00',
            'Google Drive': b'\x01',
            'Box': b'\x02',
            'Jianguoyun': b'\x03',
            'OneDrive': b'\x04',
            'WebDAV': b'\x05'
        }

        ValueStateValues = {
            'Start': b'\x01',
            'Abort': b'\x00'
        }

        path_url = qualifier['URL']
        service_val = qualifier['Service']
        if path_url and service_val in ServiceStates:
            len_field = pack('>H', len(path_url) + 2)
            CloudUploadCommandCmdString = b''.join([b'\x0D\xCB\xA1', len_field, ServiceStates[service_val], ValueStateValues[value], bytes(path_url, 'utf-8')])
            self.__SetHelper('CloudUploadCommand', CloudUploadCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCloudUploadCommand')

    def SetContentSourceListNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.content_source_list.scroll_up(1)
        elif value == 'Down':
            self.content_source_list.scroll_down(1)
        elif value == 'Page Up':
            self.content_source_list.scroll_up(self._NumberofContentSourceListSearch)
        elif value == 'Page Down':
            self.content_source_list.scroll_down(self._NumberofContentSourceListSearch)
        else:
            self.Discard('Invalid Command for SetContentSourceListNavigation')

    def SetContentSourceListUpdate(self, value, qualifier):
        self.Debug = True

        CmdString = b'\x08\xCB\x90\x00'
        res = self.SendAndWait(CmdString, self.DefaultResponseTimeout, deliRex=self.SyncRegex['ContentSourceListUpdate'])
        if res:
            try:
                new_directory_data = self.ContentSources(res)
                new_directory_data.append('*** End of List ***')
                new_directory_data.append('')
                self.content_source_list.reset(new_directory_data)
            except (KeyError, IndexError):
                self.Error(['Content Source List Update: Invalid/unexpected response'])

    def ContentSources(self, res):

        SourceStatusStates = {
            1: 'Source available and ready',
            0: 'Source not ready'
        }

        SourceTypeStates = {
            0: 'HDMI',
            1: 'Visualizer',
            2: 'Discplayer',
            3: 'Computer',
            4: 'Browser',
            5: 'Local files',
            6: 'Cloud',
            7: 'Mirror',
            8: 'Whiteboard',
            9: 'Webconference',
            10: 'Webcam',
            11: 'Stream Input',
            12: 'Skype for Business',
            13: 'Cynap',
            255: 'Undefined'
        }

        pointer = 5
        numSrcBlocks = res[pointer]
        sourceList = list()
        for i in range(1, numSrcBlocks + 1):
            BlockLen = res[pointer + 1]
            SourceStatus = SourceStatusStates[res[pointer + 2]]
            SourceType = SourceTypeStates[res[pointer + 3]]
            NameLen = res[pointer + 4]
            if NameLen != 0:
                SourceName = res[pointer + 5:pointer + 5 + NameLen]
                sourceList.append('{}: {}, {}, {}'.format(i, SourceStatus, SourceType, SourceName.decode()))
            else:
                sourceList.append('{}: {}, {}'.format(i, SourceStatus, SourceType))
            pointer += BlockLen + 1
        return sourceList

    def SetDeleteFileCommand(self, value, qualifier):

        file_name = qualifier['File Name']
        if file_name:
            len_field = pack('>H', len(file_name))
            DeleteFileCommandCmdString = b''.join([b'\x0D\xCB\x7C', len_field, bytes(file_name, 'utf-8')])
            self.__SetHelper('DeleteFileCommand', DeleteFileCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeleteFileCommand')

    def SetDownloadListUpdate(self, value, qualifier):
        self.Debug = True

        CmdString = b'\x08\xCB\x7B\x00'
        res = self.SendAndWait(CmdString, self.DefaultResponseTimeout, deliRex=self.SyncRegex['DownloadListUpdate'])
        if res:
            try:
                new_directory_data = {'filename': [], 'status': [], 'progress': []}
                for typeVal in ['filename', 'status', 'progress']:
                    new_directory_data[typeVal] = self.DownloadLists(json.loads(res[5:].decode()), typeVal)
                    new_directory_data[typeVal].append('*** End of List ***')
                    new_directory_data[typeVal].append('')
                self.download_list_filename.reset(new_directory_data['filename'])
                self.download_list_status.reset(new_directory_data['status'])
                self.download_list_progress.reset(new_directory_data['progress'])
            except (KeyError, IndexError, TypeError):
                self.Error(['Download List Update: Invalid/unexpected response'])

    def DownloadLists(self, res, type_):

        tempList = []
        typeVal = 'preload' if type_ == 'progress' else type_
        for entry in res:
            try:
                tempList.append(entry[typeVal])
            except(KeyError):
                tempList.append('{} Unknown'.format(type_.title()))
        return tempList

    def SetDownloadListNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.download_list_filename.scroll_up(1)
            self.download_list_status.scroll_up(1)
            self.download_list_progress.scroll_up(1)
        elif value == 'Down':
            self.download_list_filename.scroll_down(1)
            self.download_list_status.scroll_down(1)
            self.download_list_progress.scroll_down(1)
        elif value == 'Page Up':
            self.download_list_filename.scroll_up(self._NumberofDownloadListSearch)
            self.download_list_status.scroll_up(self._NumberofDownloadListSearch)
            self.download_list_progress.scroll_up(self._NumberofDownloadListSearch)
        elif value == 'Page Down':
            self.download_list_filename.scroll_down(self._NumberofDownloadListSearch)
            self.download_list_status.scroll_down(self._NumberofDownloadListSearch)
            self.download_list_progress.scroll_down(self._NumberofDownloadListSearch
                                                    )
        else:
            self.Discard('Invalid Command for SetDownloadListNavigation')

    def SetDualScreenAllowMirrorOverride(self, value, qualifier):

        ValueStateValues = {
            'Yes': b'\x09\xCB\xD7\x01\x01',
            'No': b'\x09\xCB\xD7\x01\x00'
        }

        DualScreenAllowMirrorOverrideCmdString = ValueStateValues[value]
        self.__SetHelper('DualScreenAllowMirrorOverride', DualScreenAllowMirrorOverrideCmdString, value, qualifier)

    def UpdateDualScreenAllowMirrorOverride(self, value, qualifier):

        DualScreenAllowMirrorOverrideCmdString = b'\x08\xCB\xD7\x00'
        self.__UpdateHelper('DualScreenAllowMirrorOverride', DualScreenAllowMirrorOverrideCmdString, value, qualifier)

    def __MatchDualScreenAllowMirrorOverride(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Yes',
            b'\x00': 'No'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DualScreenAllowMirrorOverride', value, None)

    def SetDualScreenMirrorOverride(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCB\xD8\x01\x01',
            'Off': b'\x09\xCB\xD8\x01\x00'
        }

        DualScreenMirrorOverrideCmdString = ValueStateValues[value]
        self.__SetHelper('DualScreenMirrorOverride', DualScreenMirrorOverrideCmdString, value, qualifier)

    def UpdateDualScreenMirrorOverride(self, value, qualifier):

        DualScreenMirrorOverrideCmdString = b'\x08\xCB\xD8\x00'
        self.__UpdateHelper('DualScreenMirrorOverride', DualScreenMirrorOverrideCmdString, value, qualifier)

    def __MatchDualScreenMirrorOverride(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DualScreenMirrorOverride', value, None)

    def SetDualScreenMode(self, value, qualifier):

        ValueStateValues = {
            'Mirror 1:1': b'\x09\xCB\x5B\x01\x00',
            'Mirror 1080p@60Hz': b'\x09\xCB\x5B\x01\x01',
            'Mirror 720p@60Hz': b'\x09\xCB\x5B\x01\x02',
            'Content 1080p@60Hz': b'\x09\xCB\x5B\x01\x03',
            'Content 720p@60Hz': b'\x09\xCB\x5B\x01\x04',
            'Moderator 1080p@60Hz': b'\x09\xCB\x5B\x01\x05'
        }

        DualScreenModeCmdString = ValueStateValues[value]
        self.__SetHelper('DualScreenMode', DualScreenModeCmdString, value, qualifier)

    def UpdateDualScreenMode(self, value, qualifier):

        DualScreenModeCmdString = b'\x08\xCB\x5B\x00'
        self.__UpdateHelper('DualScreenMode', DualScreenModeCmdString, value, qualifier)

    def __MatchDualScreenMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Mirror 1:1',
            b'\x01': 'Mirror 1080p@60Hz',
            b'\x02': 'Mirror 720p@60Hz',
            b'\x03': 'Content 1080p@60Hz',
            b'\x04': 'Content 720p@60Hz',
            b'\x05': 'Moderator 1080p@60Hz'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('DualScreenMode', value, None)

    def SetEndPresentation(self, value, qualifier):

        RecordingStates = {
            'Keep': b'\x00',
            'Delete': b'\x01'
        }

        SnapshotStates = {
            'Keep': b'\x00',
            'Delete': b'\x01'
        }

        ValueStateValues = {
            'New Presentation': b'\x00',
            'Standby': b'\x01'
        }

        record = qualifier['Recording']
        snap = qualifier['Snapshot']
        if record in RecordingStates and snap in SnapshotStates:
            EndPresentationCmdString = b''.join([b'\x09\xCB\x49\x03', RecordingStates[record], SnapshotStates[snap], ValueStateValues[value]])
            self.__SetHelper('EndPresentation', EndPresentationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEndPresentation')

    def SetFileListUpdate(self, value, qualifier):

        temp_value = qualifier['Root Path']
        if temp_value is None:
            temp_value = ''
        lenField = pack('>H', len(temp_value))
        CmdString = b''.join([b'\x0C\xCB\x3E', lenField, bytes(temp_value, 'utf-8')])
        res = self.SendAndWait(CmdString, self.DefaultResponseTimeout, deliRex=self.SyncRegex['FileListUpdate'])
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
        self.Debug = True

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
        self.Debug = True

        ValueConstraints = {
            'Min': 1,
            'Max': self._NumberofFileListSearch
        }

        file_path = qualifier['File Path']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and file_path:
            fileName = self.ReadStatus('FileListSearchResults', {'Button': value})
            if fileName not in ['***Not Available***', '*** End of List ***']:
                fileName1 = ['{}{}'.format(file_path, entry[6:]) if 'Name' in entry else '' for entry in fileName.split('\r\n')][0]
        else:
            self.Discard('Invalid Command for SetFileListSearchSet')

    def SetFileUploadCommand(self, value, qualifier):

        ValueStateValues1 = {
            'Start': b'\x01',
            'Abort': b'\x00'
        }
        ValueStateValues2 = {
            'Restart Index': b'\x03',
            'Abort Index': b'\x02'
        }

        srcPath = qualifier['Upload Source']
        tarPath = qualifier['Upload Target']
        if srcPath and tarPath and value in ValueStateValues1:
            len_total = pack('>H', len(srcPath) + len(tarPath) + 5)
            len_srcPath = pack('>H', len(srcPath))
            len_tarPath = pack('>H', len(tarPath))
            FileUploadCommandCmdString = b''.join([b'\x0D\xCB\xBF', len_total, ValueStateValues1[value], len_srcPath, bytes(srcPath, 'utf-8'), len_tarPath, bytes(tarPath, 'utf-8')])
            self.__SetHelper('FileUploadCommand', FileUploadCommandCmdString, value, qualifier)
        elif srcPath and tarPath and value in ValueStateValues2:
            if srcPath.isdigit():
                len_total = pack('>H', len(tarPath) + 7)
                len_tarPath = pack('>H', len(tarPath))
                FileUploadCommandCmdString = b''.join([b'\x0D\xCB\xBF', len_total, ValueStateValues2[value], b'\x00\x02', pack('>H', int(srcPath)), len_tarPath, bytes(tarPath, 'utf-8')])
                self.__SetHelper('FileUploadCommand', FileUploadCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFileUploadCommand')

    def UpdateFileUploadStatus(self, value, qualifier):

        FileUploadStatusCmdString = b'\x08\xCB\xBE\x00'
        self.__UpdateHelper('FileUploadStatus', FileUploadStatusCmdString, value, qualifier)

    def __MatchFileUploadStatus(self, match, tag):

        ValueStateValues = {
            '\x00': 'Idle',
            '\x01': 'Upload of Current Presentation Active',
            '\x02': 'Upload of Current Presentation and/or Background Upload Active'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('FileUploadStatus', value, None)

    def SetFTPSendFileCommand(self, value, qualifier):

        name = qualifier['FTP Send File']
        if name:
            len_field = pack('>H', len(name))
            FTPSendFileCommandCmdString = b''.join([b'\x0D\xCB\x66', len_field, bytes(name, 'utf-8')])
            self.__SetHelper('FTPSendFileCommand', FTPSendFileCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFTPSendFileCommand')

    def SetImageControl(self, value, qualifier):

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            ValueStateValues = {
                'Previous': pack('>5sBs', b'\x0D\xCB\x39\x00\x02', window - 1, b'\x01'),
                'Next': pack('>5sBs', b'\x0D\xCB\x39\x00\x02', window - 1, b'\x02'),
                'First': pack('>5sBs', b'\x0D\xCB\x39\x00\x02', window - 1, b'\x03'),
                'Last': pack('>5sBs', b'\x0D\xCB\x39\x00\x02', window - 1, b'\x04'),
            }

            ImageControlCmdString = ValueStateValues[value]
            self.__SetHelper('ImageControl', ImageControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageControl')

    def SetImageSnapshot(self, value, qualifier):

        ImageSnapshotCmdString = b'\x09\xCB\x32\x01\x00'
        self.__SetHelper('ImageSnapshot', ImageSnapshotCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': b'\x00',
            'HDMI 2': b'\x01'
        }

        type_qual = qualifier['Type']
        if type_qual in ValueStateValues:
            InputCmdString = b''.join([b'\x08\xCB\x79\x01', ValueStateValues[type_qual]])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        TypeStates = {
            '\x00': 'HDMI 1',
            '\x01': 'HDMI 2'
        }

        ValueStateValues = {
            '\x00': 'Visualizer',
            '\x01': 'Generic HDMI',
            '\x02': 'Computer',
            '\x03': 'Disc-Player'
        }

        qualifier = dict()
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetLoginCommand(self, value, qualifier):

        if value == 'Admin':
            if self.devicePassword and len(self.devicePassword) < 18:
                len_field1 = pack('B', len(self.devicePassword) + 2)
                len_field2 = pack('B', len(self.devicePassword))
                LoginCommandCmdString = b''.join([b'\x09\xCB\x42', len_field1, b'\x02', len_field2, bytes(self.devicePassword, 'utf-8')])
                self.__SetHelper('LoginCommand', LoginCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoginCommand')
        else:
            password_ = qualifier['Password']
            if password_ and len(password_) < 18:
                len_field1 = pack('B', len(password_) + 2)
                len_field2 = pack('B', len(password_))
                LoginCommandCmdString = b''.join([b'\x09\xCB\x42', len_field1, b'\x01', len_field2, bytes(password_, 'utf-8')])
                self.__SetHelper('LoginCommand', LoginCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLoginCommand')

    def UpdateLoginLevelStatus(self, value, qualifier):

        LoginLevelStatusCmdString = b'\x08\xCB\x55\x00'
        self.__UpdateHelper('LoginLevelStatus', LoginLevelStatusCmdString, value, qualifier)

    def __MatchLoginLevelStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'None',
            b'\x01': 'User',
            b'\x02': 'Admin'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('LoginLevelStatus', value, None)

    def SetMainFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCB\x5A\x01\x01',
            'Off': b'\x09\xCB\x5A\x01\x00'
        }

        MainFreezeCmdString = ValueStateValues[value]
        self.__SetHelper('MainFreeze', MainFreezeCmdString, value, qualifier)

    def UpdateMainFreeze(self, value, qualifier):

        MainFreezeCmdString = b'\x08\xCB\x5A\x00'
        self.__UpdateHelper('MainFreeze', MainFreezeCmdString, value, qualifier)

    def __MatchMainFreeze(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('MainFreeze', value, None)

    def SetMainResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x09\xCB\x4D\x01\x00',
            '1080p60': b'\x09\xCB\x4D\x01\x01',
            '2160p30': b'\x09\xCB\x4D\x01\x02',
            '2160p60': b'\x09\xCB\x4D\x01\x03'
        }

        MainResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('MainResolution', MainResolutionCmdString, value, qualifier)

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCB\x58\x01\x01',
            'Off': b'\x09\xCB\x58\x01\x00'
        }

        MasterMuteCmdString = ValueStateValues[value]
        self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)

    def UpdateMasterMute(self, value, qualifier):

        MasterMuteCmdString = b'\x08\xCB\x58\x00'
        self.__UpdateHelper('MasterMute', MasterMuteCmdString, value, qualifier)

    def __MatchMasterMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('MasterMute', value, None)

    def SetMasterVolume(self, value, qualifier):

        if 0 <= value <= 100:
            MasterVolumeCmdString = pack('>4sB', b'\x09\xCB\x56\x01', value)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = b'\x08\xCB\x56\x00'
        self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)

    def __MatchMasterVolume(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('MasterVolume', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ActionStates = {
            'None': b'\x00',
            'Hit': b'\x01',
            'Release': b'\x02',
            'Tip': b'\x03'
        }

        ValueStateValues = {
            'None': b'\x00',
            'Left': b'\x01',
            'Right': b'\x02',
            'Up': b'\x03',
            'Down': b'\x04',
            'OK': b'\x05',
            'Menu': b'\x06',
            'Red': b'\x07',
            'Green': b'\x08',
            'Yellow': b'\x09',
            'Blue': b'\x0A',
            'Toolbox': b'\x0B'
        }

        if qualifier['Action'] in ActionStates:
            MenuNavigationCmdString = b'\x09\xCB\x01\x02' + ValueStateValues[value] + ActionStates[qualifier['Action']]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMicrophoneMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCB\x59\x01\x01',
            'Off': b'\x09\xCB\x59\x01\x00'
        }

        MicrophoneMuteCmdString = ValueStateValues[value]
        self.__SetHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)

    def UpdateMicrophoneMute(self, value, qualifier):

        MicrophoneMuteCmdString = b'\x08\xCB\x59\x00'
        self.__UpdateHelper('MicrophoneMute', MicrophoneMuteCmdString, value, qualifier)

    def __MatchMicrophoneMute(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('MicrophoneMute', value, None)

    def UpdateMicrophoneStatus(self, value, qualifier):

        MicrophoneStatusCmdString = b'\x08\xCB\xEA\x00'
        self.__UpdateHelper('MicrophoneStatus', MicrophoneStatusCmdString, value, qualifier)

    def __MatchMicrophoneStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Disabled',
            b'\x01': 'Working',
            b'\x02': 'Quiet'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('MicrophoneStatus', value, None)

    def SetMirroring(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        MirroringCmdString = b''.join([b'\x09\xCB\x3B\x01', ValueStateValues[value]])
        self.__SetHelper('Mirroring', MirroringCmdString, value, qualifier)

    def UpdateMirroring(self, value, qualifier):

        MirroringCmdString = b'\x08\xCB\x3B\x00'
        self.__UpdateHelper('Mirroring', MirroringCmdString, value, qualifier)

    def __MatchMirroring(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Mirroring', value, None)

    def SetMountListUpdate(self, value, qualifier):
        self.Debug = True

        CmdString = b'\x08\xCB\x3D\x00'
        res = self.SendAndWait(CmdString, self.DefaultResponseTimeout, deliRex=self.SyncRegex['MountListUpdate'])
        if res:
            try:
                new_directory_data = ['{}, {}, {}'.format(entry['id'], entry['type'], entry['status']) for entry in json.loads(res[5:].decode())]
                new_directory_data.append('*** End of List ***')
                new_directory_data.append('')
                self.mount_list.reset(new_directory_data)
            except(KeyError, IndexError):
                self.Error(['Mount List Update: Invalid/Unexpected response'])

    def SetMountListNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.mount_list.scroll_up(1)
        elif value == 'Down':
            self.mount_list.scroll_down(1)
        elif value == 'Page Up':
            self.mount_list.scroll_up(self._NumberofMountListSearch)
        elif value == 'Page Down':
            self.mount_list.scroll_down(self._NumberofMountListSearch)
        else:
            self.Discard('Invalid Command for SetMountListNavigation')

    def SetNetwork(self, value, qualifier):

        FeatureStates = {
            'Miracast': b'\x09\xCB\x36\x01',
            'Airplay': b'\x09\xCB\x37\x01',
            'vSolution Cast/App': b'\x09\xCB\x86\x01',
            'Chromecast': b'\x09\xCB\xB2\x01'
        }

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        NetworkCmdString = b''.join([FeatureStates[qualifier['Feature']], ValueStateValues[value]])
        self.__SetHelper('Network', NetworkCmdString, value, qualifier)

    def UpdateNetwork(self, value, qualifier):

        FeatureStates = {
            'Miracast': b'\x08\xCB\x36\x00',
            'Airplay': b'\x08\xCB\x37\x00',
            'vSolution Cast/App': b'\x08\xCB\x86\x00',
            'Chromecast': b'\x08\xCB\xB2\x00'
        }

        NetworkCmdString = FeatureStates[qualifier['Feature']]
        self.__UpdateHelper('Network', NetworkCmdString, value, qualifier)

    def __MatchNetwork(self, match, tag):

        FeatureStates = {
            b'\x36': 'Miracast',
            b'\x37': 'Airplay',
            b'\x86': 'vSolution Cast/App',
            b'\xB2': 'Chromecast'
        }

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        qualifier = dict()
        qualifier['Feature'] = FeatureStates[match.group(1)]
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Network', value, qualifier)

    def SetOfficeControl(self, value, qualifier):

        ValueStateValues = {
            'Zoom In': b'\x01',
            'Zoom Out': b'\x02',
            'Cursor Down': b'\x03',
            'Cursor Up': b'\x04',
            'Cursor Right': b'\x05',
            'Cursor Left': b'\x06',
            'Next Page': b'\x07',
            'Previous Page': b'\x08',
            'Next Worksheet': b'\x09',
            'Previous Worksheet': b'\x0A',
            'Full Page': b'\x0B',
            'Full Width': b'\x0C',
            'Scroll Down': b'\x0D',
            'Scroll Up': b'\x0E',
            'Scroll Right': b'\x0F',
            'Scroll Left': b'\x10'
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            win_field = pack('B', window - 1)
            OfficeControlCmdString = b''.join([b'\x0D\xCB\x4B\x00\x02', win_field, ValueStateValues[value]])
            self.__SetHelper('OfficeControl', OfficeControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOfficeControl')

    def SetOpenFileCommand(self, value, qualifier):

        temp_value = qualifier['File Name']
        if temp_value:
            len_field = pack('>H', len(temp_value))
            OpenFileCommandCmdString = b''.join([b'\x0D\xCB\x3C', len_field, bytes(temp_value, 'utf-8')])
            self.__SetHelper('OpenFileCommand', OpenFileCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOpenFileCommand')

    def SetPanoptoStartRecording(self, value, qualifier):

        IPCameraModeStates = {
            'Enabled'  : b'\x01',
            'Disabled' : b'\x00'
        }

        folderID = qualifier['Folder ID']
        prefix = qualifier['Filename Prefix']

        if qualifier['IP Camera Mode'] in IPCameraModeStates and 1 <= len(folderID) <= 255 and 1 <= len(prefix) <= 64:
            PanoptoStartRecordingCmdString = b''.join([b'\x09\xCC\x9D', pack('B', 2 + len(folderID) + len(prefix)), 
                                                       b'\x01\x00', pack('B', len(folderID)), bytes(folderID, 'utf-8'), 
                                                       pack('B', len(prefix)), bytes(prefix, 'utf-8')])
            self.__SetHelper('PanoptoStartRecording', PanoptoStartRecordingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanoptoStartRecording')

    def SetPDFControl(self, value, qualifier):

        ValueStateValues = {
            'Zoom In': b'\x01',
            'Zoom Out': b'\x02',
            'Cursor Down': b'\x03',
            'Cursor Up': b'\x04',
            'Cursor Right': b'\x05',
            'Cursor Left': b'\x06',
            'Next Page': b'\x07',
            'Previous Page': b'\x08',
            'Zoom To Full Height': b'\x0A',
            'Zoom To Full Width': b'\x0B',
            'Zoom To Full Page': b'\x0C',
            'Scroll Down': b'\x0D',
            'Scroll Up': b'\x0E',
            'Scroll Right': b'\x0F',
            'Scroll Left': b'\x10'
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            win_field = pack('B', window - 1)
            PDFControlCmdString = b''.join([b'\x0D\xCB\x4A\x00\x02', win_field, ValueStateValues[value]])
            self.__SetHelper('PDFControl', PDFControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPDFControl')

    def UpdatePinStatus(self, value, qualifier):

        PinStatusCmdString = ''
        pin_type = qualifier['Type']
        if pin_type == 'Local':
            PinStatusCmdString = b'\x08\xCB\x53\x00'
        elif pin_type == 'Room':
            PinStatusCmdString = b'\x08\xCB\x54\x00'
        if PinStatusCmdString:
            self.__UpdateHelper('PinStatus', PinStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePinStatus')

    def __MatchPinStatus(self, match, tag):

        TypeStates = {
            '\x53': 'Local',
            '\x54': 'Room'
        }

        ValueStateValues = {
            '\x01': 'Show',
            '\x00': 'Hide'
        }

        qualifier1 = dict()
        qualifier1['Type'] = TypeStates[match.group(1).decode()]
        qualifier2 = dict()
        value = match.group(3).decode()
        self.WriteStatus('PinStatus', ValueStateValues[value[0]], qualifier1)
        if ord(match.group(2)) == 1:
            self.WriteStatus('PinStatusNumber', '', qualifier2)
        elif ord(match.group(2)) > 1:
            self.WriteStatus('PinStatusNumber', value[1:], qualifier2)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCB\x0C\x01\x01',
            'Off': b'\x09\xCB\x0C\x01\x00'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', b'\x08\xCB\x0C\x00', value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Power', value, None)

    def SetPresentationMode(self, value, qualifier):

        ValueStateValues = {
            'Meeting': b'\x09\xCB\x38\x01\x00',
            'Lecture': b'\x09\xCB\x38\x01\x01'
        }

        PresentationModeCmdString = ValueStateValues[value]
        self.__SetHelper('PresentationMode', PresentationModeCmdString, value, qualifier)

    def UpdatePresentationMode(self, value, qualifier):

        PresentationModeCmdString = b'\x08\xCB\x38\x00'
        self.__UpdateHelper('PresentationMode', PresentationModeCmdString, value, qualifier)

    def __MatchPresentationMode(self, match, tag):

        ValueStateValues = {
            '\x00': 'Meeting',
            '\x01': 'Lecture'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationMode', value, None)

    def SetQRCode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        QRCodeCmdString = b''.join([b'\x09\xCB\x88\x01', ValueStateValues[value]])
        self.__SetHelper('QRCode', QRCodeCmdString, value, qualifier)

    def UpdateQRCode(self, value, qualifier):

        QRCodeCmdString = b'\x08\xCB\x88\x00'
        self.__UpdateHelper('QRCode', QRCodeCmdString, value, qualifier)

    def __MatchQRCode(self, match, tag):

        value = match.group(1).decode()
        if value == '\x01\x00':
            self.WriteStatus('QRCode', 'Off', None)
            self.WriteStatus('QRCodeURLReturned', '', None)
        elif value[1] == '\x01':
            self.WriteStatus('QRCode', 'On', None)
            self.WriteStatus('QRCodeURLReturned', value[2:], None)

    def SetRecordingFunction(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x09\xCB\x92\x01\x01',
            'Disable': b'\x09\xCB\x92\x01\x00'
        }

        RecordingFunctionCmdString = ValueStateValues[value]
        self.__SetHelper('RecordingFunction', RecordingFunctionCmdString, value, qualifier)

    def UpdateRecordingFunction(self, value, qualifier):

        RecordingFunctionCmdString = b'\x08\xCB\x92\x00'
        self.__UpdateHelper('RecordingFunction', RecordingFunctionCmdString, value, qualifier)

    def __MatchRecordingFunction(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Enable',
            b'\x00': 'Disable'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('RecordingFunction', value, None)

    def SetRecordingResolution(self, value, qualifier):

        ValueStateValues = {
            'Full HD': b'\x09\xCB\x26\x01\x00',
            'HD': b'\x09\xCB\x26\x01\x01',
            'qHD': b'\x09\xCB\x26\x01\x02',
            'nHD': b'\x09\xCB\x26\x01\x03'
        }

        RecordingResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('RecordingResolution', RecordingResolutionCmdString, value, qualifier)

    def UpdateScreensaverStatus(self, value, qualifier):
    
        ScreensaverStatusCmdString = b'\x08\xCC\x76\x00'
        self.__UpdateHelper('ScreensaverStatus', ScreensaverStatusCmdString, value, qualifier)

    def __MatchScreensaverStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'Standby Active',
            b'\x02': 'Screen Off Active',
            b'\x03': 'Screensaver Active'
            }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('ScreensaverStatus', value, None)

    def SetStreamingFramerate(self, value, qualifier):

        ValueStateValues = {
            'Low': b'\x09\xCB\x24\x01\x00',
            'Medium': b'\x09\xCB\x24\x01\x01',
            'High': b'\x09\xCB\x24\x01\x02'
        }

        StreamingFramerateCmdString = ValueStateValues[value]
        self.__SetHelper('StreamingFramerate', StreamingFramerateCmdString, value, qualifier)

    def UpdateStreamingFramerate(self, value, qualifier):

        StreamingFramerateCmdString = b'\x08\xCB\x24\x00'
        self.__UpdateHelper('StreamingFramerate', StreamingFramerateCmdString, value, qualifier)

    def __MatchStreamingFramerate(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Low',
            b'\x01': 'Medium',
            b'\x02': 'High'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('StreamingFramerate', value, None)

    def UpdateStreamingFunction(self, value, qualifier):

        StreamingFunctionCmdString = b'\x08\xCB\x93\x00'
        self.__UpdateHelper('StreamingFunction', StreamingFunctionCmdString, value, qualifier)

    def __MatchStreamingFunction(self, match, tag):

        ValueStateValues = {
            b'\x01': 'Enable',
            b'\x00': 'Disable'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('StreamingFunction', value, None)

    def SetStreamingIPAddress(self, value, qualifier):

        IP = self.IPAddressPattern.match(value)
        if IP and 0 <= int(IP.group(1)) <= 255 and 0 <= int(IP.group(2)) <= 255 and 0 <= int(IP.group(3)) <= 255 and 0 <= int(IP.group(4)) <= 255:
            CmdString = pack('>4s4B', b'\x09\xCB\x21\x04', int(IP.group(1)), int(IP.group(2)), int(IP.group(3)), int(IP.group(4)))
            self.__SetHelper('StreamingIPAddress', CmdString, value, qualifier)
        else:
            self.Error(['Invalid IP Address'])

    def SetStreamingMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCB\x20\x01\x01',
            'Off': b'\x09\xCB\x20\x01\x00'
        }

        StreamingModeCmdString = ValueStateValues[value]
        self.__SetHelper('StreamingMode', StreamingModeCmdString, value, qualifier)

    def UpdateStreamingMode(self, value, qualifier):

        StreamingModeCmdString = b'\x08\xCB\x20\x00'
        self.__UpdateHelper('StreamingMode', StreamingModeCmdString, value, qualifier)

    def __MatchStreamingMode(self, match, tag):

        ValueStateValues = {
            '\x00': 'Off',
            '\x01': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('StreamingMode', value, None)

    def SetStreamingPort(self, value, qualifier):

        if 8800 <= value <= 9000:
            StreamingPortCmdString = pack('>4sH', b'\x09\xCB\x22\x02', value)
            self.__SetHelper('StreamingPort', StreamingPortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStreamingPort')

    def SetStreamingResolution(self, value, qualifier):

        ValueStateValues = {
            'Full HD': b'\x09\xCB\x23\x01\x00',
            'HD': b'\x09\xCB\x23\x01\x01',
            'qHD': b'\x09\xCB\x23\x01\x02',
            'nHD': b'\x09\xCB\x23\x01\x03'
        }

        StreamingResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('StreamingResolution', StreamingResolutionCmdString, value, qualifier)

    def SetUSBCopyFileCommand(self, value, qualifier):

        filePath = qualifier['File Name']
        if filePath:
            len_filePath = pack('>H', len(filePath))
            USBCopyFileCommandCmdString = b''.join([b'\x0D\xCB\x6A', len_filePath, bytes(filePath, 'utf-8')])
            self.__SetHelper('USBCopyFileCommand', USBCopyFileCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBCopyFileCommand')

    def SetVideoControl(self, value, qualifier):

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            ValueStateValues = {
                'Play': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x00'),
                'Pause': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x01'),
                'Stop': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x02'),
                'Forward': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x03'),
                'Rewind': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x04'),
                'Loop Off': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x07'),
                'Loop On': pack('>5sBs', b'\x0D\xCB\x2B\x00\x02', window - 1, b'\x08')
            }
            VideoControlCmdString = ValueStateValues[value]
            self.__SetHelper('VideoControl', VideoControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoControl')

    def SetVideoRecording(self, value, qualifier):

        ValueStateValues = {
            'Start': b'\x09\xCB\x25\x01\x00',
            'Pause': b'\x09\xCB\x25\x01\x01',
            'Stop': b'\x09\xCB\x25\x01\x02'
        }

        VideoRecordingCmdString = ValueStateValues[value]
        self.__SetHelper('VideoRecording', VideoRecordingCmdString, value, qualifier)

    def UpdateVideoRecording(self, value, qualifier):

        VideoRecordingCmdString = b'\x08\xCB\x25\x00'
        self.__UpdateHelper('VideoRecording', VideoRecordingCmdString, value, qualifier)

    def __MatchVideoRecording(self, match, tag):

        ValueStateValues = {
            '\x00': 'Start',
            '\x01': 'Pause',
            '\x02': 'Stop'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoRecording', value, None)

    def SetVisualizerControl(self, value, qualifier):

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            ValueStateValues = {
                'Auto Focus On': pack('>4sBs', b'\x09\xCB\x29\x02', window - 1, b'\x04'),
                'Auto Focus Off': pack('>4sBs', b'\x09\xCB\x29\x02', window - 1, b'\x05'),
                'Freeze On': pack('>4sBs', b'\x09\xCB\x29\x02', window - 1, b'\x06'),
                'Freeze Off': pack('>4sBs', b'\x09\xCB\x29\x02', window - 1, b'\x07'),
                'Preset Set': pack('>4sBs', b'\x09\xCB\x29\x02', window - 1, b'\x08'),
                'Preset Recall': pack('>4sBs', b'\x09\xCB\x29\x02', window - 1, b'\x09')
            }

            VisualizerControlCmdString = ValueStateValues[value]
            self.__SetHelper('VisualizerControl', VisualizerControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVisualizerControl')

    def SetVisualizerFocus(self, value, qualifier):

        SpeedStates = {
            'Stop': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            '11': 11,
            '12': 12,
            '13': 13,
            '14': 14,
            '15': 15
        }

        ValueStateValues = {
            'Far': 0x02,
            'Near': 0x03
        }

        window = int(qualifier['Window'])
        speed = SpeedStates[qualifier['Speed']]
        direction = ValueStateValues[value]

        if 1 <= window <= 4:
            VisualizerFocusCmdString = pack('>4sBBH', b'\x09\xCB\x29\x04', window - 1, direction, speed)
            self.__SetHelper('VisualizerFocus', VisualizerFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVisualizerFocus')

    def SetVisualizerZoom(self, value, qualifier):

        SpeedStates = {
            'Stop': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            '11': 11,
            '12': 12,
            '13': 13,
            '14': 14,
            '15': 15
        }

        ValueStateValues = {
            'Wide': 0x00,
            'Tele': 0x01
        }

        window = int(qualifier['Window'])
        speed = SpeedStates[qualifier['Speed']]
        direction = ValueStateValues[value]

        if 1 <= window <= 4:
            VisualizerZoomCmdString = pack('>4sBBH', b'\x09\xCB\x29\x04', window - 1, direction, speed)
            self.__SetHelper('VisualizerZoom', VisualizerZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVisualizerZoom')

    def SetWebcastStreamingMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\xCC\x5C\x01\x01',
            'Off': b'\x09\xCC\x5C\x01\x00'
        }

        WebcastStreamingModeCmdString = ValueStateValues[value]
        self.__SetHelper('WebcastStreamingMode', WebcastStreamingModeCmdString, value, qualifier)

    def UpdateWebcastStreamingMode(self, value, qualifier):

        WebcastStreamingModeCmdString = b'\x08\xCC\x5C\x00'
        self.__UpdateHelper('WebcastStreamingMode', WebcastStreamingModeCmdString, value, qualifier)

    def __MatchWebcastStreamingMode(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('WebcastStreamingMode', value, None)

    def SetWindowAuxCopyControl(self, value, qualifier):

        ValueStateValues = {
            'On': 6,
            'Off': 7
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            WindowAuxCopyControlCmdString = pack('>4s2B', b'\x09\xCB\x28\x02', window - 1, ValueStateValues[value])
            self.__SetHelper('WindowAuxCopyControl', WindowAuxCopyControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowAuxCopyControl')

    def UpdateWindowAuxCopyControl(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def SetWindowControlClose(self, value, qualifier):

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            WindowControlCloseCmdString = pack('>4sBs', b'\x09\xCB\x28\x02', window - 1, b'\x00')
            self.__SetHelper('WindowControlClose', WindowControlCloseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowControlClose')

    def SetWindowControlFullscreen(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x02'
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            WindowControlFullscreenCmdString = pack('>4sBs', b'\x09\xCB\x28\x02', window - 1, ValueStateValues[value])
            self.__SetHelper('WindowControlFullscreen', WindowControlFullscreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowControlFullscreen')

    def UpdateWindowControlFullscreen(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def SetWindowControlMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        window = int(qualifier['Window'])
        if 1 <= window <= 4:
            WindowControlMuteCmdString = pack('>4sBss', b'\x09\xCB\x28\x03', window - 1, b'\x03', ValueStateValues[value])
            self.__SetHelper('WindowControlMute', WindowControlMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowControlMute')

    def UpdateWindowControlMute(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def SetWindowControlVolume(self, value, qualifier):

        window = int(qualifier['Window'])
        if 1 <= value <= 100 and 1 <= window <= 4:
            WindowControlVolumeCmdString = pack('>4sBsB', b'\x09\xCB\x28\x03', window - 1, b'\x04', value)
            self.__SetHelper('WindowControlVolume', WindowControlVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowControlVolume')

    def UpdateWindowControlVolume(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowImageNumberStatus(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowOfficePageStatus(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowPDFPageStatus(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowRecordingorStreamingStatus(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def SetWindowStart(self, value, qualifier):

        ValueStateValues = {
            'Visualizer': b'\x01\x00\x00',
            'HDMI 1': b'\x02\x00\x01\x00',
            'HDMI 2': b'\x02\x00\x01\x01',
            'Browser': b'\x03\x00\x00',
            'Video': b'\x06\x00\x00',
            'Image': b'\x08\x00\x00',
            'PDF': b'\x09\x00\x00',
            'Office PPT/PPTX': b'\x0A\x00\x00',
            'Office DOC/DOCX/TXT': b'\x0B\x00\x00',
            'Office XLS/XLSX': b'\x0C\x00\x00',
            'Whiteboard': b'\x0D\x00\x00',
            'Audio': b'\x0E\x00\x00',
            'Webconference': b'\x0F\x00\x00',
            'USB Webcam 1': b'\x10\x00\x01\x00',
            'USB Webcam 2': b'\x10\x00\x01\x01',
            'Stream Input 1' : b'\x11\x00\x01\x00',
            'Stream Input 2' : b'\x11\x00\x01\x01',
            'Stream Input 3' : b'\x11\x00\x01\x02',
            'Stream Input 4' : b'\x11\x00\x01\x03',
            'Stream Input 5' : b'\x11\x00\x01\x04',
            'Stream Input 6' : b'\x11\x00\x01\x05',
            'Stream Input 7' : b'\x11\x00\x01\x06',
            'Stream Input 8' : b'\x11\x00\x01\x07',
            'Stream Input 9' : b'\x11\x00\x01\x08',
            'Stream Input 10' : b'\x11\x00\x01\x09',
            'Stream Input 11' : b'\x11\x00\x01\x0A',
            'Stream Input 12' : b'\x11\x00\x01\x0B',
            'Stream Input 13' : b'\x11\x00\x01\x0C',
            'Stream Input 14' : b'\x11\x00\x01\x0D',
            'Stream Input 15' : b'\x11\x00\x01\x0E',
            'Stream Input 16' : b'\x11\x00\x01\x0F',
            'Stream Input 17' : b'\x11\x00\x01\x10',
            'Stream Input 18' : b'\x11\x00\x01\x11',
            'Stream Input 19' : b'\x11\x00\x01\x12',
            'Stream Input 20' : b'\x11\x00\x01\x13',
            'Office 365 Outlook': b'\x13\x00\x00',
            'Office 365 Word': b'\x14\x00\x00',
            'Office 365 Excel': b'\x15\x00\x00',
            'Office 365 PowerPoint': b'\x16\x00\x00',
            'Office 365 OneNote': b'\x17\x00\x00',
            'vMatrix Pull Stream': b'\x18\x00\x00',
            'vMatrix Push Stream': b'\x19\x00\x00',
            'Office 365 Teams': b'\x1B\x00\x00'
        }
        window = qualifier['Window']
        if window in ['1', '2', '3', '4', 'Auto Arrange']:
            window = 0xFF if window == 'Auto Arrange' else int(window) - 1
            win_field = pack('B', window)
            WindowStartCmdString = b''.join([b'\x0D\xCB\x2C\x00', bytes([len(ValueStateValues[value]) + 1]), win_field, ValueStateValues[value]])
            self.__SetHelper('WindowStart', WindowStartCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowStart')

    def UpdateWindowAirplayName(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowMiracastName(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowvSolutionName(self, value, qualifier):

        self.UpdateWindowStatus(value, qualifier)

    def UpdateWindowStatus(self, value, qualifier):

        StatusVal = {
            0: 'Off',
            1: 'On',
        }

        WindowType = {
            0: 'None',
            1: 'Visualizer',
            2: 'HDMI Input',
            3: 'Browser',
            4: 'Miracast',
            5: 'Airplay',
            6: 'Video',
            7: 'vSolution Cast',
            8: 'Image',
            9: 'PDF',
            10: 'Office Presentation',
            11: 'Office Text',
            12: 'Office Calc',
            13: 'Whiteboard',
            14: 'Audio',
            15: 'Webconference',
            16: 'Webcam',
            17: 'Stream Input',
            18: 'Skype for Business'
        }

        RecStream = {
            1: 'Active',
            0: 'Idle'
        }

        WindowStatusCmdString = b'\x08\xCB\xBA\x00'
        res = self.SendAndWait(WindowStatusCmdString, self.DefaultResponseTimeout, deliRex=self.SyncRegex['WindowStatus'])
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
                    except:
                        self.Error(['Window Status: Invalid/unexpected response'])

                    try:
                        fullscreen = StatusVal[res[pointer + 2]]
                        self.WriteStatus('WindowControlFullscreen', fullscreen, {'Window': str(position)})
                    except:
                        self.Error(['Window Control Fullscreen: Invalid/unexpected response'])

                    try:
                        muteVal = StatusVal[res[pointer + 11]]
                        self.WriteStatus('WindowControlMute', muteVal, {'Window': str(position)})
                    except:
                        self.Error(['Window Control Mute: Invalid/unexpected response'])
                    try:
                        volVal = res[pointer + 12]
                        self.WriteStatus('WindowControlVolume', volVal, {'Window': str(position)})
                    except:
                        self.Error(['Window Control Mute: Invalid/unexpected response'])

                    try:
                        DualScreenVal = StatusVal[res[pointer + 13]]
                        self.WriteStatus('WindowAuxCopyControl', DualScreenVal, {'Window': str(position)})
                    except:
                        self.Error(['Window Control Mute: Invalid/unexpected response'])

                    try:
                        recStrmVal = RecStream[res[pointer + 14]]
                        self.WriteStatus('WindowRecordingorStreamingStatus', recStrmVal, {'Window': str(position)})
                    except:
                        self.Error(['Window Control Mute: Invalid/unexpected response'])

                    typeSpecLen = unpack('>H', res[(pointer + 15):(pointer + 17)])[0]

                    if blockType == 'Miracast':
                        try:
                            MirSpecRes = res[(pointer + 17):(pointer + 17 + typeSpecLen)]
                            index = len(MirSpecRes)
                            MirName = '{}'.format(MirSpecRes[2:index].decode())
                            self.WriteStatus('WindowMiracastName', MirName, {'Window': str(position)})
                        except:
                            self.Error(['Window Miracast Name: Invalid/unexpected response'])
                    else:
                        self.WriteStatus('WindowMiracastName', 'Not Applicable', {'Window': str(position)})

                    if blockType == 'Airplay':
                        try:
                            AirplaySpecRes = res[(pointer + 17):(pointer + 17 + typeSpecLen)]
                            index = len(AirplaySpecRes)
                            AirplayName = '{}'.format(AirplaySpecRes[2:index].decode())
                            self.WriteStatus('WindowAirplayName', AirplayName, {'Window': str(position)})
                        except BaseException:
                            self.Error(['Window Airplay Name: Invalid/unexpected response'])
                    else:
                        self.WriteStatus('WindowAirplayName', 'Not Applicable', {'Window': str(position)})

                    if blockType == 'vSolution Cast':
                        try:
                            vSolutionSpecRes = res[(pointer + 17):(pointer + 17 + typeSpecLen)]
                            index = len(vSolutionSpecRes)
                            vSolutionsName = '{}'.format(vSolutionSpecRes[2:index].decode())
                            self.WriteStatus('WindowvSolutionName', vSolutionsName, {'Window': str(position)})
                        except BaseException:
                            self.Error(['Window vSolution Name: Invalid/unexpected response'])
                    else:
                        self.WriteStatus('WindowvSolutionName', 'Not Applicable', {'Window': str(position)})

                    if blockType == 'PDF':
                        try:
                            pdfSpecRes = res[(pointer + 17):(pointer + 17 + typeSpecLen)]
                            if len(pdfSpecRes) == 8:
                                pdfPageNo = '{}/{}'.format(unpack('>I', pdfSpecRes[0:4])[0], unpack('>I', pdfSpecRes[4:8])[0])
                                self.WriteStatus('WindowPDFPageStatus', pdfPageNo, {'Window': str(position)})
                        except:
                            self.Error(['Window PDF Page Status: Invalid/unexpected response'])
                    else:
                        self.WriteStatus('WindowPDFPageStatus', 'Not Applicable', {'Window': str(position)})

                    if blockType == 'Image':
                        try:
                            imageSpecRes = res[(pointer + 17):(pointer + 17 + typeSpecLen)]
                            imageNo = '{}/{}'.format(unpack('>I', imageSpecRes[0:4])[0], unpack('>I', imageSpecRes[4:8])[0])
                            self.WriteStatus('WindowImageNumberStatus', imageNo, {'Window': str(position)})
                        except:
                            self.Error(['Window Image Number Status: Invalid/unexpected response'])
                    else:
                        self.WriteStatus('WindowImageNumberStatus', 'Not Applicable', {'Window': str(position)})

                    if blockType == 'Office Presentation':
                        try:
                            officeSpecRes = res[(pointer + 17):(pointer + 17 + typeSpecLen)]
                            officeNo = '{}/{}'.format(unpack('>I', officeSpecRes[0:4])[0], unpack('>I', officeSpecRes[4:8])[0])
                            self.WriteStatus('WindowOfficePageStatus', officeNo, {'Window': str(position)})
                        except:
                            self.Error(['Window Office Page Status: Invalid/unexpected response'])
                    else:
                        self.WriteStatus('WindowOfficePageStatus', 'Not Applicable', {'Window': str(position)})

                    position += 1
                    pointer += 14 + 3 + typeSpecLen
                    if pointer >= totalLen:
                        endFound = True

                self.WindowStatus = sourceList
                self.__WindowStatusPositionHandler()
            except (KeyError, IndexError):
                self.Error(['Window Control Status: Invalid/unexpected response'])

    def __WindowStatusPositionHandler(self):

        index = self.WindowSourceStartIndex  # default is 0. Will change if FileListNavigation is used
        position = 1
        while index < len(self.WindowStatus):
            self.WriteStatus('WindowStatus', self.WindowStatus[index], {'Window': str(position)})
            position += 1
            index += 1
        else:
            while position <= 4:
                self.WriteStatus('WindowStatus', '', {'Window': str(position)})
                position += 1

# END AUTO GENERATION OF COMMAND DEF
    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if (response[0] >> 4) > 0:
                self.Error(['Command {0}: Error occurred.'.format(sourceCmdName)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetLoginCommand('Admin', None)

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
            except BaseException:
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
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

    def __init__(self, display_count, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Button'
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
            self.write_status_function(self.entry_function(entry[0]), {self.qualifier_name: position_value})

    def write_status_function(self, value, qualifier):
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
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1