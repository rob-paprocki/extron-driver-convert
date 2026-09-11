# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import EthernetClientInterface
import re
import time
from extronlib.system import Wait, ProgramLog
from json import loads
from collections import OrderedDict

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 100000
        self.__matchStringDict = OrderedDict()
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberOfAllUsers = 5
        self._NumberOfConnectedUsers = 5
        self._NumberOfFiles = 5
        self._NumberOfPendingUsers = 5
        self._NumberOfSharingUsers = 5
        self._NumberOfUSBCameras = 5
        self._NumberOfUSBMicrophones = 5
        self._NumberOfUSBSpeakers = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AccessMode': { 'Status': {}},
            'AllPendingUserConnections': { 'Status': {}},
            'AllUsersConnectionTime': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersContentSharingLocation': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersContentSharingStatus': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersContentType': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersIdleTime': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersName': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersNavigation': { 'Status': {}},
            'AllUsersNumberofContentShared': {'Parameters': ['Button'], 'Status': {}},
            'DigitalAudioInputMute': { 'Status': {}},
            'DigitalAudioInputGain': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ConfirmationCode': { 'Status': {}},
            'ConfirmationCodeMode': { 'Status': {}},
            'ConnectedUserConnectionTime': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserContentSharingStatus': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserIdleTime': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserName': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserNavigation': { 'Status': {}},
            'ConnectedUserNumberofContentShared': {'Parameters': ['Button'], 'Status': {}},
            'DisconnectAllUsers': { 'Status': {}},
            'DisconnectUser': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'DisplayLayout': { 'Status': {}},
            'DisplayLayoutGroup': { 'Status': {}},
            'FileName': {'Parameters': ['Button'], 'Status': {}},
            'FileNavigation': { 'Status': {}},
            'FullScreenSharedContent': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'FullScreenSharedContentRevert': { 'Status': {}},
            'FullScreenSharedContentStatus': { 'Status': {}},
            'FullScreenSharedContentUserName': { 'Status': {}},
            'HDCPInputStatus': { 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'HDMIInputWindow': { 'Status': {}},
            'Hostname': { 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'IPAddress': {'Parameters': ['LAN'], 'Status': {}},
            'LabelVisibility': {'Parameters': ['Label'], 'Status': {}},
            'NumberofContentSharedonOutput': { 'Status': {}},
            'NumberofUsersConnected': { 'Status': {}},
            'NumberofUsersNotSharing': { 'Status': {}},
            'NumberofUsersPending': { 'Status': {}},
            'NumberofUsersSharing': { 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'PendingUserConnection': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'PendingUserName': {'Parameters': ['Button'], 'Status': {}},
            'PendingUserNavigation': { 'Status': {}},
            'RefreshAllUsers': { 'Status': {}},
            'RefreshConnectedUsers': { 'Status': {}},
            'RefreshFiles': { 'Status': {}},
            'RefreshPendingUsers': { 'Status': {}},
            'RefreshSharingUsers': { 'Status': {}},
            'RefreshUSBCameras': { 'Status': {}},
            'RefreshUSBMicrophones': { 'Status': {}},
            'RefreshUSBSpeakers': { 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'SharingUserContentSharingLocation': {'Parameters': ['Button'], 'Status': {}},
            'SharingUserContentType': {'Parameters': ['Button'], 'Status': {}},
            'SharingUserName': {'Parameters': ['Button'], 'Status': {}},
            'SharingUserNavigation': { 'Status': {}},
            'SharingUserNumberofContentShared': {'Parameters': ['Button'], 'Status': {}},
            'StatusBar': { 'Status': {}},
            'StopAllShares': { 'Status': {}},
            'StopIndividualShare': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'StopShare': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'SwapContentSharingLocation': {'Parameters': ['Group', 'Location 1', 'Location 2'], 'Status': {}},
            'USBCamera': {'Parameters': ['Button'], 'Status': {}},
            'USBCameraNavigation': { 'Status': {}},
            'USBCameraSelect': {'Parameters': ['Button'], 'Status': {}},
            'USBCameraSelectStatus': { 'Status': {}},
            'USBMicrophone': {'Parameters': ['Button'], 'Status': {}},
            'USBMicrophoneNavigation': { 'Status': {}},
            'USBMicrophoneGain': {'Parameters': ['Button'], 'Status': {}},                     
            'USBMicrophoneMute': {'Parameters': ['Button'], 'Status': {}},
            'USBMicrophoneSelect': {'Parameters': ['Button'], 'Status': {}},
            'USBMicrophoneSelectStatus': { 'Status': {}},
            'USBSpeaker': {'Parameters': ['Button'], 'Status': {}},
            'USBSpeakerNavigation': { 'Status': {}},
            'USBSpeakerVolume': {'Parameters': ['Button'], 'Status': {}},                     
            'USBSpeakerMaster': { 'Status': {}},
            'USBSpeakerMute': {'Parameters': ['Button'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.AllUsersData = [] # ex: [['1038276244', 'SALESLOANER', '519789643', '440x440_gray_WeatherChannel_sel.png', '1', '0', '0', '5000', '10000', '9014', '1126080', '']]
        self.ConnectedUserData = []
        self.PendingUserData = []
        self.SharingUserData = []
        self.USBNames = []
        self.USBMicrophoneGains = []
        self.USBMicrophoneMutes = []
        self.USBIDs = []
        self.USBSpeakerNames = []
        self.USBSpeakerGains = []
        self.USBSpeakerMutes = []
        self.USBSpeakerIDs = []
        self.USBCameraNames = []
        self.USBCameraIDs = []
        self.IdleStartTime = {'AllUsers': {}, 'ConnectedUser': {}} # ex: {'AllUsers': {'1038276244': 5}, 'ConnectedUser': {'1038276244': 5}}
        self.ConfiguredSetRefreshCommands = [] # determines which user lists to write status for
        self.AccessMode = None # used to store user permission level
        self.HDMIName = '' # used to store HDMI Client App Controls Label
        self.LayoutNumber = None # used to store current layout number
        self.AudioInputID = None
        self.FileRegex = []
                
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:MylkC\d{1,2}|SharK\d{1,2}|(Pips|In)([0-1])|UserChg|SharW\d+\*\d+|SharChg)\r\n'), self.__MatchUpdateUsers, None) # triggers main query for all user data
            self.AddMatchString(re.compile(b'UsbsJ3\*(\[{.*}\])\r\n'), self.__MatchUSBJson, None)
            self.AddMatchString(re.compile(b'UsbsJ1\*(\[{.*}\])\r\n'), self.__MatchUSBCameras, None)
            self.AddMatchString(re.compile(b'UsbsJ4\*(\[{?.*}?\])\r\n'), self.__MatchUSBSpeakers, None)
            self.AddMatchString(re.compile(b'SharL([\S \r\n]+)?\r\n\r\n'), self.__MatchAllUsers, None) # main query response for all user data
            self.AddMatchString(re.compile(b'SharM([1-3]\*[1-2])\r\n'), self.__MatchAccessMode, None) # determines user permission level (unsolicited responses only supported for fw above 1.01.0000-b003)
            self.AddMatchString(re.compile(b'Nmi1,([\S ]+)\r\n'), self.__MatchHDMIName, None) # determines name shown for HDMI user
            self.AddMatchString(re.compile(b'Omod([1-9][01]?)\*([1-9][0-9]?)\r\n'), self.__MatchDisplayLayoutGroup, None) # determines content sharing location
            self.AddMatchString(re.compile(b'Amt1\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'PincV (\d{4})?\r\n'), self.__MatchConfirmationCode, None)
            self.AddMatchString(re.compile(b'PincM([0-3])\r\n'), self.__MatchConfirmationCodeMode, None)
            self.AddMatchString(re.compile(b'SharF(\d+)?\*?([01])\r\n'), self.__MatchFullScreenSharedContentStatus, None)
            self.AddMatchString(re.compile(b'HdcpI1\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO1\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Ipn ([\S ]+)\r\n'), self.__MatchHostname, None)
            self.AddMatchString(re.compile(b'In00 ([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Cisg ([123])\*([\d.]+)\/[\d.]+\*[\d.]+\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(re.compile(b'OsdlV([1-8])\*([01])\r\n'), self.__MatchLabelVisibility, None)
            self.AddMatchString(re.compile(b'Rate1\*0(\d{2})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'SsavS1\*([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(b'OsdlM([0-3])\r\n'), self.__MatchStatusBar, None)
            self.AddMatchString(re.compile(b'UsbsL4\*\d+\r\n'), self.__MatchUpdateUSB, 'Speakers')
            self.AddMatchString(re.compile(b'UsbsL1\*\d+\r\n'), self.__MatchUpdateUSB, 'Cameras')
            self.AddMatchString(re.compile(b'UsbsL3\*\d+\r\n'), self.__MatchUpdateUSB, 'USB')
            self.AddMatchString(re.compile(b'Vmt1\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol([+-])(\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(01|1[0-7]|2[245678]|3[012])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'(?P<file>.*..*)\s\w{1,3},.*\sGMT\s\d*'), self.__MatchFiles, None)
            self.AddMatchString(re.compile(b'Bytes Left\r\n'), self.__MatchEndFiles, None)
            self.AddMatchString(re.compile(b'UsbsN1\*([0-9]+)\r\n'), self.__MatchUSBCameraSelectStatus, None)
            self.AddMatchString(re.compile(b'UsbsG\*{0,1}([0-9]+)\*([-0-9]+)\r\n'), self.__MatchUSBMicrophoneGain, None)
            self.AddMatchString(re.compile(b'UsbsY\*{0,1}([0-9]+)\*([01])\r\n'), self.__MatchUSBMicrophoneMute, None)
            self.AddMatchString(re.compile(b'UsbsN3\*([0-9]+)\r\n'), self.__MatchUSBMicrophoneSelectStatus, None)
            self.AddMatchString(re.compile(b'UsbsK([0-9]+)\*([-0-9]+)\r\n'), self.__MatchUSBSpeakerVolume, None)
            self.AddMatchString(re.compile(b'UsbsZ([0-9]+)\*([01])\r\n'), self.__MatchUSBSpeakerMute, None)
            self.AddMatchString(re.compile(b'UsbsF([01])\r\n'), self.__MatchUSBSpeakerMaster, None)
        
        self.all_users_name_directory = Directory('AllUsersName', self._NumberOfAllUsers, filler='')
        self.all_users_name_directory.write_status_function = self.WriteStatus

        self.all_users_number_of_content_shared_directory = Directory('AllUsersNumberofContentShared', self._NumberOfAllUsers, filler='0')
        self.all_users_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.all_users_content_sharing_status_directory = Directory('AllUsersContentSharingStatus',self._NumberOfAllUsers, filler='N/A')
        self.all_users_content_sharing_status_directory.write_status_function = self.WriteStatus

        self.all_users_content_type_directory = Directory('AllUsersContentType', self._NumberOfAllUsers, filler='')
        self.all_users_content_type_directory.write_status_function = self.WriteStatus

        self.all_users_content_sharing_location_directory = Directory('AllUsersContentSharingLocation', self._NumberOfAllUsers, filler='N/A')
        self.all_users_content_sharing_location_directory.write_status_function = self.WriteStatus

        self.all_users_connection_time_directory = Directory('AllUsersConnectionTime', self._NumberOfAllUsers, filler=0)
        self.all_users_connection_time_directory.write_status_function = self.WriteStatus

        self.all_users_idle_time_directory = Directory('AllUsersIdleTime', self._NumberOfAllUsers, filler=0)
        self.all_users_idle_time_directory.write_status_function = self.WriteStatus

        self.connected_user_name_directory = Directory('ConnectedUserName', self._NumberOfConnectedUsers, filler='')
        self.connected_user_name_directory.write_status_function = self.WriteStatus

        self.connected_user_number_of_content_shared_directory = Directory('ConnectedUserNumberofContentShared', self._NumberOfConnectedUsers, filler='0')
        self.connected_user_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.connected_user_content_sharing_status_directory = Directory('ConnectedUserContentSharingStatus', self._NumberOfConnectedUsers, filler='N/A')
        self.connected_user_content_sharing_status_directory.write_status_function = self.WriteStatus

        self.connected_user_connection_time_directory = Directory('ConnectedUserConnectionTime', self._NumberOfConnectedUsers, filler=0)
        self.connected_user_connection_time_directory.write_status_function = self.WriteStatus

        self.connected_user_idle_time_directory = Directory('ConnectedUserIdleTime', self._NumberOfConnectedUsers, filler=0)
        self.connected_user_idle_time_directory.write_status_function = self.WriteStatus

        self.file_directory = Directory('FileName', self._NumberOfFiles, filler='')
        self.file_directory.write_status_function = self.WriteStatus

        self.pending_user_name_directory = Directory('PendingUserName', self._NumberOfPendingUsers, filler='')
        self.pending_user_name_directory.write_status_function = self.WriteStatus

        self.sharing_user_name_directory = Directory('SharingUserName', self._NumberOfSharingUsers, filler='')
        self.sharing_user_name_directory.write_status_function = self.WriteStatus

        self.sharing_user_number_of_content_shared_directory = Directory('SharingUserNumberofContentShared', self._NumberOfSharingUsers, filler='0')
        self.sharing_user_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.sharing_user_content_type_directory = Directory('SharingUserContentType', self._NumberOfSharingUsers, filler='')
        self.sharing_user_content_type_directory.write_status_function = self.WriteStatus

        self.sharing_user_content_sharing_location_directory = Directory('SharingUserContentSharingLocation', self._NumberOfSharingUsers, filler='N/A')
        self.sharing_user_content_sharing_location_directory.write_status_function = self.WriteStatus

        self.usb_camera_name_directory = Directory('USBCamera', self._NumberOfUSBCameras, filler='')
        self.usb_camera_name_directory.write_status_function = self.WriteStatus
        
        self.usb_name_directory = Directory('USBMicrophone', self._NumberOfUSBMicrophones, filler='')
        self.usb_name_directory.write_status_function = self.WriteStatus
        
        self.usb_gain_directory = Directory('USBMicrophoneGain', self._NumberOfUSBMicrophones, filler='')
        self.usb_gain_directory.write_status_function = self.WriteStatus
        
        self.usb_mute_directory = Directory('USBMicrophoneMute', self._NumberOfUSBMicrophones, filler='N/A')
        self.usb_mute_directory.write_status_function = self.WriteStatus
        
        self.usb_speakers_name_directory = Directory('USBSpeaker', self._NumberOfUSBSpeakers, filler='')
        self.usb_speakers_name_directory.write_status_function = self.WriteStatus
        
        self.usb_speakers_volume_directory = Directory('USBSpeakerVolume', self._NumberOfUSBSpeakers, filler='')
        self.usb_speakers_volume_directory.write_status_function = self.WriteStatus
        
        self.usb_speakers_mute_directory = Directory('USBSpeakerMute', self._NumberOfUSBSpeakers, filler='N/A')
        self.usb_speakers_mute_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfAllUsers(self):
        return self._NumberOfAllUsers

    @NumberOfAllUsers.setter
    def NumberOfAllUsers(self, value):
        self._NumberOfAllUsers= value
        self.all_users_name_directory = Directory('AllUsersName', self._NumberOfAllUsers, filler='')
        self.all_users_name_directory.write_status_function = self.WriteStatus

        self.all_users_number_of_content_shared_directory = Directory('AllUsersNumberofContentShared', self._NumberOfAllUsers, filler='0')
        self.all_users_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.all_users_content_sharing_status_directory = Directory('AllUsersContentSharingStatus', self._NumberOfAllUsers, filler='N/A')
        self.all_users_content_sharing_status_directory.write_status_function = self.WriteStatus

        self.all_users_content_type_directory = Directory('AllUsersContentType', self._NumberOfAllUsers, filler='')
        self.all_users_content_type_directory.write_status_function = self.WriteStatus

        self.all_users_content_sharing_location_directory = Directory('AllUsersContentSharingLocation', self._NumberOfAllUsers, filler='N/A')
        self.all_users_content_sharing_location_directory.write_status_function = self.WriteStatus

        self.all_users_connection_time_directory = Directory('AllUsersConnectionTime', self._NumberOfAllUsers, filler=0)
        self.all_users_connection_time_directory.write_status_function = self.WriteStatus

        self.all_users_idle_time_directory = Directory('AllUsersIdleTime', self._NumberOfAllUsers, filler=0)
        self.all_users_idle_time_directory.write_status_function = self.WriteStatus
        

    @property
    def NumberOfConnectedUsers(self):
        return self._NumberOfConnectedUsers

    @NumberOfConnectedUsers.setter
    def NumberOfConnectedUsers(self, value):
        self._NumberOfConnectedUsers= value
        self.connected_user_name_directory = Directory('ConnectedUserName', self._NumberOfConnectedUsers, filler='')
        self.connected_user_name_directory.write_status_function = self.WriteStatus

        self.connected_user_number_of_content_shared_directory = Directory('ConnectedUserNumberofContentShared', self._NumberOfConnectedUsers, filler='0')
        self.connected_user_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.connected_user_content_sharing_status_directory = Directory('ConnectedUserContentSharingStatus', self._NumberOfConnectedUsers, filler='N/A')
        self.connected_user_content_sharing_status_directory.write_status_function = self.WriteStatus

        self.connected_user_connection_time_directory = Directory('ConnectedUserConnectionTime', self._NumberOfConnectedUsers, filler=0)
        self.connected_user_connection_time_directory.write_status_function = self.WriteStatus

        self.connected_user_idle_time_directory = Directory('ConnectedUserIdleTime', self._NumberOfConnectedUsers, filler=0)
        self.connected_user_idle_time_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfFiles(self):
        return self._NumberOfFiles

    @NumberOfFiles.setter
    def NumberOfFiles(self, value):
        self._NumberOfFiles= value
        self.file_directory = Directory('FileName', self._NumberOfFiles, filler='')
        self.file_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfPendingUsers(self):
        return self._NumberOfPendingUsers

    @NumberOfPendingUsers.setter
    def NumberOfPendingUsers(self, value):
        self._NumberOfPendingUsers= value
        self.pending_user_name_directory = Directory('PendingUserName', self._NumberOfPendingUsers, filler='')
        self.pending_user_name_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfSharingUsers(self):
        return self._NumberOfSharingUsers

    @NumberOfSharingUsers.setter
    def NumberOfSharingUsers(self, value):
        self._NumberOfSharingUsers= value
        self.sharing_user_name_directory = Directory('SharingUserName', self._NumberOfSharingUsers, filler='')
        self.sharing_user_name_directory.write_status_function = self.WriteStatus

        self.sharing_user_number_of_content_shared_directory = Directory('SharingUserNumberofContentShared', self._NumberOfSharingUsers, filler='0')
        self.sharing_user_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.sharing_user_content_type_directory = Directory('SharingUserContentType', self._NumberOfSharingUsers, filler='')
        self.sharing_user_content_type_directory.write_status_function = self.WriteStatus

        self.sharing_user_content_sharing_location_directory = Directory('SharingUserContentSharingLocation', self._NumberOfSharingUsers, filler='N/A')
        self.sharing_user_content_sharing_location_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfUSBCameras(self):
        return self._NumberOfUSBCameras

    @NumberOfUSBCameras.setter
    def NumberOfUSBCameras(self, value):
        self._NumberOfUSBCameras= value
        self.usb_camera_name_directory = Directory('USBCamera', self._NumberOfUSBCameras, filler='')
        self.usb_camera_name_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfUSBMicrophones(self):
        return self._NumberOfUSBMicrophones

    @NumberOfUSBMicrophones.setter
    def NumberOfUSBMicrophones(self, value):
        self._NumberOfUSBMicrophones= value
        self.usb_name_directory = Directory('USBMicrophone', self._NumberOfUSBMicrophones, filler='')
        self.usb_name_directory.write_status_function = self.WriteStatus
        
        self.usb_gain_directory = Directory('USBMicrophoneGain', self._NumberOfUSBMicrophones, filler='')
        self.usb_gain_directory.write_status_function = self.WriteStatus
        
        self.usb_mute_directory = Directory('USBMicrophoneMute', self._NumberOfUSBMicrophones, filler='N/A')
        self.usb_mute_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfUSBSpeakers(self):
        return self._NumberOfUSBSpeakers

    @NumberOfUSBSpeakers.setter
    def NumberOfUSBSpeakers(self, value):
        self._NumberOfUSBSpeakers= value
        self.usb_speakers_name_directory = Directory('USBSpeaker', self._NumberOfUSBSpeakers, filler='')
        self.usb_speakers_name_directory.write_status_function = self.WriteStatus
        
        self.usb_speakers_volume_directory = Directory('USBSpeakerVolume', self._NumberOfUSBSpeakers, filler='')
        self.usb_speakers_volume_directory.write_status_function = self.WriteStatus
        
        self.usb_speakers_mute_directory = Directory('USBSpeakerMute', self._NumberOfUSBSpeakers, filler='N/A')
        self.usb_speakers_mute_directory.write_status_function = self.WriteStatus

    def __MatchVerboseMode(self, match, tag):
        self.OnConnected()        
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, tag):
        self.EchoDisabled = False

    def RefreshUserData(self, value, qualifier):
        if self.LayoutNumber is None:
            self.Send('wOMOD\r\n')
        self.Send('\x1BL0SHAR\r\n')

    def UpdateHDMIName(self, value, qualifier):
        self.Send('w1NI\r\n')

    def __MatchHDMIName(self, match, tag):
        self.HDMIName = match.group(1).decode()

    def __MatchAllUsers(self, match, tag):

        self.AllUsersData.clear()
        self.ConnectedUserData.clear()
        self.PendingUserData.clear()
        self.SharingUserData.clear()

        listLookup = {
            'AllUsersName' : [],
            'AllUsersNumberofContentShared' : [],
            'AllUsersContentSharingStatus' : [],
            'AllUsersContentType' : [],
            'AllUsersContentSharingLocation' : [],
            'AllUsersConnectionTime' : [],
            'AllUsersIdleTime' : [],
            'ConnectedUserName' : [],
            'ConnectedUserNumberofContentShared' : [],
            'ConnectedUserContentSharingStatus' : [],
            'ConnectedUserConnectionTime' : [],
            'ConnectedUserIdleTime' : [],
            'PendingUserName' : [],
            'SharingUserName' : [],
            'SharingUserNumberofContentShared' : [],
            'SharingUserContentType' : [],
            'SharingUserContentSharingLocation' : []
        }
        LocationStates = {
            1: {
                '0*0*10000*10000'     : 'Full Screen'
            },
            2: {
                '0*0*5000*5000'       : 'Quadrant 1',
                '5000*0*5000*5000'    : 'Quadrant 2',
                '0*5000*5000*5000'    : 'Quadrant 3',
                '5000*5000*5000*5000' : 'Quadrant 4'
            },
            3: {
                '3328*0*6664*10000'   : 'Quadrant 1',
                '0*0*3328*3326'       : 'Quadrant 2',
                '0*3326*3328*3326'    : 'Quadrant 3',
                '0*6663*3328*3326'    : 'Quadrant 4'
            },
            4: {
                '0*0*6664*10000'      : 'Quadrant 1',
                '6664*0*3328*3326'    : 'Quadrant 2',
                '6664*3326*3328*3326' : 'Quadrant 3',
                '6664*6663*3328*3326' : 'Quadrant 4'
            },
            5: {
                '0*0*10000*6663'      : 'Quadrant 1',
                '0*6663*3328*3326'    : 'Quadrant 2',
                '3328*6663*3328*3326' : 'Quadrant 3',
                '6664*6663*3328*3326' : 'Quadrant 4'
            },
            6: {
                '0*3326*10000*6663'       : 'Quadrant 1',
                '0*0*3328*3326'    : 'Quadrant 2',
                '3328*0*3328*3326'    : 'Quadrant 3',
                '6664*0*3328*3326'   : 'Quadrant 4'
            },
            7: {
                '0*0*5000*5000'       : 'Quadrant 1',
                '5000*0*5000*5000'    : 'Quadrant 2',
                '0*5000*10000*5000'   : 'Quadrant 3'
            },
            8: {
                '3328*0*6664*10000'       : 'Quadrant 1',
                '0*0*3328*5000'   : 'Quadrant 2',
                '0*5000*3328*5000'    : 'Quadrant 3'
            },
            9: {
                '0*0*6664*10000'      : 'Quadrant 1',
                '6664*0*3328*5000'    : 'Quadrant 2',
                '6664*5000*3328*5000' : 'Quadrant 3'
            },
            10: {
                '0*0*10000*6663'      : 'Quadrant 1',
                '0*6663*5000*3326'    : 'Quadrant 2',
                '5000*6663*5000*3326' : 'Quadrant 3'
            },
            11: {
                '0*3326*10000*6663'       : 'Quadrant 1',
                '0*0*5000*3326'    : 'Quadrant 2',
                '5000*0*5000*3326'   : 'Quadrant 3'
            },
            12: {
                '0*0*5000*10000'      : 'Quadrant 1',
                '5000*0*5000*10000'   : 'Quadrant 2'
            },
            13: {
                '3328*0*6664*10000'      : 'Quadrant 1',
                '0*0*3328*10000'   : 'Quadrant 2'
            },
            14: {
                '0*0*6664*10000'      : 'Quadrant 1',
                '6664*0*3328*10000'   : 'Quadrant 2'
            },
            15: {
                '0*0*10000*6663'      : 'Quadrant 1',
                '0*6663*10000*3326'   : 'Quadrant 2'
            },
            16: {
                '0*3326*10000*6663'      : 'Quadrant 1',
                '0*0*10000*3326'   : 'Quadrant 2'
            },
            17: {
                '0*0*5000*10000'      : 'Full Screen'
            },
            18: {
                '0*0*2500*10000'       : 'Quadrant 1',
                '2500*0*2500*10000'    : 'Quadrant 2',
                '5000*0*2500*10000'    : 'Quadrant 3',
                '7500*0*2500*10000' : 'Quadrant 4'
            },
            19: {
                '0*0*5000*5000'       : 'Quadrant 1',
                '0*5000*5000*5000'    : 'Quadrant 2',
                '5000*0*5000*5000'    : 'Quadrant 3',
                '5000*5000*5000*5000' : 'Quadrant 4'
            },
            20: {
                '0*0*5000*10000'       : 'Quadrant 1',
                '5000*0*2500*5000'    : 'Quadrant 2',
                '7500*0*2500*5000'    : 'Quadrant 3',
                '5000*5000*5000*5000' : 'Quadrant 4'
            },
            21: {
                '0*0*2500*5000'       : 'Quadrant 1',
                '2500*0*2500*5000'    : 'Quadrant 2',
                '0*5000*5000*5000'    : 'Quadrant 3',
                '5000*0*5000*10000' : 'Quadrant 4'
            },
            22: {
                '0*0*2500*10000'       : 'Quadrant 1',
                '2500*0*2500*10000'    : 'Quadrant 2',
                '5000*0*5000*10000'    : 'Quadrant 3',
            },
            23: {
                '0*0*5000*10000'       : 'Quadrant 1',
                '5000*0*2500*10000'    : 'Quadrant 2',
                '7500*0*2500*10000'    : 'Quadrant 3',
            },
            24: {
                '0*0*5000*5000'       : 'Quadrant 1',
                '0*5000*5000*5000'    : 'Quadrant 2',
                '5000*0*5000*10000'    : 'Quadrant 3',
            },
            25: {
                '0*0*5000*10000'       : 'Quadrant 1',
                '5000*0*5000*5000'    : 'Quadrant 2',
                '5000*5000*5000*5000'    : 'Quadrant 3',
            },
        }

        shareCount = {} # used to count Number of Content Shared per user
        shareList = [] # used to prevent counting more than once for a single user for Number of Users Sharing
        totalCountLookup = {'Sharing': 0, 'Not Sharing': 0, 'Output Sharing': 0} # used to count Number of Users Sharing, Number of Users Not Sharing, and Number of Content Shared on Output

        if match.group(1):
            resultsList = match.group(1).decode('unicode_escape').split('\r\n') # ex: ['1437233304**1970871729*HDMI Window*1*5000*0*5000*10000*4229*1378056*', '1857684395*SOHARA***1*0*0*0*0*7130**', '1038276244*SALESLOANER*519789643*,sharelink,stream*1*0*0*5000*10000*9915*1126080*BlueTeam']
 # delay other queries to ensure these statuses update
            self.UpdateAccessMode( None, None)
            self.UpdateHDMIName( None, None)
            for result in resultsList:
                data = result.split('*') # split individual user data items

                if data[4] == '0': # if connection not approved (pending user)
                    if self.AccessMode in ['Moderated', 'Run-time Moderated']:
                        self.AllUsersData.append([data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]]) # ex: [['1038276244', 'SALESLOANER', '519789643', ',sharelink,stream', '0', '0', '0', '5000', '10000', '9915', '1126080', 'BlueTeam']]
                        listLookup['AllUsersName'].append(data[1])
                        listLookup['AllUsersContentSharingStatus'].append('Not Sharing')
                        listLookup['AllUsersContentType'].append('')
                        listLookup['AllUsersContentSharingLocation'].append('N/A')
                        listLookup['AllUsersConnectionTime'].append(int(data[9]))
                        listLookup['AllUsersIdleTime'].append(int(data[9])) # same as connection time

                        self.PendingUserData.append([data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]])
                        listLookup['PendingUserName'].append(data[1])

                else: # if connection approved (connected user)
                    if 'wired,hdmi-input' in data[3] or data[1] == '': # check if HDMI user ('None' or no name)
                        name = self.HDMIName # use HDMI Client App Controls Label
                    elif 'sharelink,stream' in data[3]: # if active learning tie
                        name = data[11] # use device name
                    else:
                        name = data[1] # use user name

                    locationData = '{0}*{1}*{2}*{3}'.format(data[5], data[6], data[7], data[8]) # format as X*Y*W*H
                    if locationData == '0*0*10000*10000': # handles case if full screen shared content (layout number is irrelevant)
                        location = 'Full Screen'
                    else:
                        try:
                            location = LocationStates[self.LayoutNumber][locationData] # use layout number to determine location
                        except KeyError:
                            location = 'N/A' # '0*0*0*0' or '***' (not sharing)

                    self.AllUsersData.append([data[0], name, data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]])
                    listLookup['AllUsersName'].append(name)
                    listLookup['AllUsersContentType'].append(data[3])
                    listLookup['AllUsersContentSharingLocation'].append(location)
                    listLookup['AllUsersConnectionTime'].append(int(data[9]))

                    if name not in listLookup['ConnectedUserName']: # prevents duplicate users from being added to Connected User list
                        self.ConnectedUserData.append([data[0], name, data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]])
                        listLookup['ConnectedUserName'].append(name)
                        listLookup['ConnectedUserConnectionTime'].append(int(data[9]))

                    if data[2]: # if Stream ID exists (sharing)
                        self.IdleStartTime['AllUsers'][data[0]] = 0 # initialize/reset idle start time to zero
                        listLookup['AllUsersContentSharingStatus'].append('Sharing')
                        listLookup['AllUsersIdleTime'].append(0)

                        if len(listLookup['ConnectedUserName']) != len(listLookup['ConnectedUserContentSharingStatus']): # only add data if not duplicate user
                            self.IdleStartTime['ConnectedUser'][data[0]] = 0
                            listLookup['ConnectedUserContentSharingStatus'].append('Sharing')
                            listLookup['ConnectedUserIdleTime'].append(0)

                        self.SharingUserData.append([data[0], name, data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]])
                        listLookup['SharingUserName'].append(name)
                        listLookup['SharingUserContentType'].append(data[3])
                        listLookup['SharingUserContentSharingLocation'].append(location)

                        if data[0] in shareCount: # if connection ID already in shareCount
                            shareCount[data[0]] = shareCount[data[0]]+1 # increment count, ex: {'1715790165': 2, '1706866040': 1}
                        else:
                            shareCount[data[0]] = 1 # add connection ID as key and count as value

                        if data[0] not in shareList: # if connection ID not in shareList
                            shareList.append(data[0]) # add it so count only increments once
                            totalCountLookup['Sharing'] = totalCountLookup['Sharing']+1 # increment count
                        totalCountLookup['Output Sharing'] = totalCountLookup['Output Sharing']+1 # increment count

                    else: # if Stream ID doesn't exist (not sharing)
                        listLookup['AllUsersContentSharingStatus'].append('Not Sharing')
                        if len(listLookup['ConnectedUserName']) != len(listLookup['ConnectedUserContentSharingStatus']):
                            listLookup['ConnectedUserContentSharingStatus'].append('Not Sharing')

                        try:
                            if self.IdleStartTime['AllUsers'][data[0]] == 0: # if idle start time exists and not marked yet
                                self.IdleStartTime['AllUsers'][data[0]] = time.monotonic() # mark it
                            else:
                                listLookup['AllUsersIdleTime'].append(round(time.monotonic() - self.IdleStartTime['AllUsers'][data[0]])) # calc difference of current time and idle start time
                        except KeyError:
                            self.IdleStartTime['AllUsers'][data[0]] = time.monotonic() # initialize and mark idle start time
                            listLookup['AllUsersIdleTime'].append(0) # used to write initial status to zero

                        if len(listLookup['ConnectedUserName']) != len(listLookup['ConnectedUserIdleTime']):
                            try:
                                if self.IdleStartTime['ConnectedUser'][data[0]] == 0: # if idle start time exists and not marked yet
                                    self.IdleStartTime['ConnectedUser'][data[0]] = time.monotonic() # mark it
                                else:
                                    listLookup['ConnectedUserIdleTime'].append(round(time.monotonic() - self.IdleStartTime['ConnectedUser'][data[0]])) # calc difference of current time and idle start time
                            except KeyError:
                                self.IdleStartTime['ConnectedUser'][data[0]] = time.monotonic() # initialize and mark idle start time
                                listLookup['ConnectedUserIdleTime'].append(0) # used to write initial status to zero

                        totalCountLookup['Not Sharing'] = totalCountLookup['Not Sharing']+1 # increment count
            for data in self.AllUsersData: # ex: [['1038276244', 'SALESLOANER', '519789643', ',sharelink,stream', '1', '0', '0', '5000', '10000', '9915', 'BlueTeam']]
                if data[4] == '0': # if connection not approved (pending user)
                    listLookup['AllUsersNumberofContentShared'].append('0') # append zero
                elif data[0] in shareCount: # if connection approved (connected user) and connection ID in shareCount (sharing)
                    listLookup['AllUsersNumberofContentShared'].append(str(shareCount[data[0]])) # append count
                    if len(listLookup['ConnectedUserName']) != len(listLookup['ConnectedUserNumberofContentShared']):
                        listLookup['ConnectedUserNumberofContentShared'].append(str(shareCount[data[0]]))
                    listLookup['SharingUserNumberofContentShared'].append(str(shareCount[data[0]]))
                else: # (not sharing)
                    listLookup['AllUsersNumberofContentShared'].append('0') # append zero
                    if len(listLookup['ConnectedUserName']) != len(listLookup['ConnectedUserNumberofContentShared']):
                        listLookup['ConnectedUserNumberofContentShared'].append('0')

        if self.ConfiguredSetRefreshCommands: # only update status if a SetRefresh command was triggered
            self.WriteStatus('NumberofContentSharedonOutput', str(totalCountLookup['Output Sharing']), None)
            self.WriteStatus('NumberofUsersConnected', str(totalCountLookup['Sharing']+totalCountLookup['Not Sharing']), None)
            self.WriteStatus('NumberofUsersNotSharing', str(totalCountLookup['Not Sharing']), None)
            self.WriteStatus('NumberofUsersPending', str(len(self.PendingUserData)), None)
            self.WriteStatus('NumberofUsersSharing', str(totalCountLookup['Sharing']), None)
            if 'SetRefreshAllUsers' in self.ConfiguredSetRefreshCommands:
                self.all_users_name_directory.reset(listLookup['AllUsersName'])
                self.all_users_number_of_content_shared_directory.reset(listLookup['AllUsersNumberofContentShared'])
                self.all_users_content_sharing_status_directory.reset(listLookup['AllUsersContentSharingStatus'])
                self.all_users_content_type_directory.reset(listLookup['AllUsersContentType'])
                self.all_users_content_sharing_location_directory.reset(listLookup['AllUsersContentSharingLocation'])
                self.all_users_connection_time_directory.reset(listLookup['AllUsersConnectionTime'])
                self.all_users_idle_time_directory.reset(listLookup['AllUsersIdleTime'])

            if 'SetRefreshConnectedUsers' in self.ConfiguredSetRefreshCommands:
                self.connected_user_name_directory.reset(listLookup['ConnectedUserName'])
                self.connected_user_number_of_content_shared_directory.reset(listLookup['ConnectedUserNumberofContentShared'])
                self.connected_user_content_sharing_status_directory.reset(listLookup['ConnectedUserContentSharingStatus'])
                self.connected_user_connection_time_directory.reset(listLookup['ConnectedUserConnectionTime'])
                self.connected_user_idle_time_directory.reset(listLookup['ConnectedUserIdleTime'])

            if 'SetRefreshPendingUsers' in self.ConfiguredSetRefreshCommands:
                self.pending_user_name_directory.reset(listLookup['PendingUserName'])

            if 'SetRefreshSharingUsers' in self.ConfiguredSetRefreshCommands:
                self.sharing_user_name_directory.reset(listLookup['SharingUserName'])
                self.sharing_user_number_of_content_shared_directory.reset(listLookup['SharingUserNumberofContentShared'])
                self.sharing_user_content_type_directory.reset(listLookup['SharingUserContentType'])
                self.sharing_user_content_sharing_location_directory.reset(listLookup['SharingUserContentSharingLocation'])
    
    def SetAccessMode(self, value, qualifier):

        ValueStateValues = {
            'Full Control' : '1',
            'Moderated' : '2',
            'Run-time' : '3',
        }

        if value in ValueStateValues:
            AccessModeCmdString = 'wM{}SHAR\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AccessMode', AccessModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAccessMode')

    def UpdateAccessMode(self, value, qualifier):

        AccessModeCmdString = 'wMSHAR\r\n'
        self.__UpdateHelper('AccessMode', AccessModeCmdString, value, qualifier)

    def __MatchAccessMode(self, match, tag):

        ValueStateValues = {
            '1*1' : 'Full Control',
            '2*2' : 'Moderated',
            '3*1' : 'Run-time Full Control',
            '3*2' : 'Run-time Moderated'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AccessMode', value, None)

        self.AccessMode = value # used in MatchAllUsers

    def SetAllPendingUserConnections(self, value, qualifier):

        ValueStateValues = {
            'Approve' : '1',
            'Reject' : '0',
            'Pending': '2'
        }

        if value in ValueStateValues:
            AllPendingUserConnectionsCmdString = '\x1bC0*{}SHAR\r\n'.format(ValueStateValues[value])
            self.__SetHelper('AllPendingUserConnections', AllPendingUserConnectionsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAllPendingUserConnections')

    def SetAllUsersNavigation(self, value, qualifier):

        if value == 'Up':
            self.all_users_name_directory.scroll_up(1)
            self.all_users_number_of_content_shared_directory.scroll_up(1)
            self.all_users_content_sharing_status_directory.scroll_up(1)
            self.all_users_content_type_directory.scroll_up(1)
            self.all_users_content_sharing_location_directory.scroll_up(1)
            self.all_users_connection_time_directory.scroll_up(1)
            self.all_users_idle_time_directory.scroll_up(1)
        elif value == 'Down':
            self.all_users_name_directory.scroll_down(1)
            self.all_users_number_of_content_shared_directory.scroll_down(1)
            self.all_users_content_sharing_status_directory.scroll_down(1)
            self.all_users_content_type_directory.scroll_down(1)
            self.all_users_content_sharing_location_directory.scroll_down(1)
            self.all_users_connection_time_directory.scroll_down(1)
            self.all_users_idle_time_directory.scroll_down(1)
        elif value == 'Page Up':
            self.all_users_name_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_number_of_content_shared_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_content_sharing_status_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_content_type_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_content_sharing_location_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_connection_time_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_idle_time_directory.scroll_up(self._NumberOfAllUsers)
        elif value == 'Page Down':
            self.all_users_name_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_number_of_content_shared_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_content_sharing_status_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_content_type_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_content_sharing_location_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_connection_time_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_idle_time_directory.scroll_down(self._NumberOfAllUsers)
        else:
            self.Discard('Invalid Command for SetAllUsersNavigation')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '1*{}Z'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '1Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def UpdateConfirmationCode(self, value, qualifier):

        ConfirmationCodeCmdString = '\x1bVPINC\r\n'
        self.__UpdateHelper('ConfirmationCode', ConfirmationCodeCmdString, value, qualifier)

    def __MatchConfirmationCode(self, match, tag):

        value = 'N/A' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('ConfirmationCode', value, None)

    def UpdateConfirmationCodeMode(self, value, qualifier):

        ConfirmationCodeModeCmdString = '\x1bMPINC\r\n'
        self.__UpdateHelper('ConfirmationCodeMode', ConfirmationCodeModeCmdString, value, qualifier)

    def __MatchConfirmationCodeMode(self, match, tag):

        ValueStateValues = {
            '3': 'Enterprise Discovery Service',
            '2' : 'Random', 
            '1' : 'Fixed',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ConfirmationCodeMode', value, None)

    def SetConnectedUserNavigation(self, value, qualifier):

        if value == 'Up':
            self.connected_user_name_directory.scroll_up(1)
            self.connected_user_number_of_content_shared_directory.scroll_up(1)
            self.connected_user_content_sharing_status_directory.scroll_up(1)
            self.connected_user_connection_time_directory.scroll_up(1)
            self.connected_user_idle_time_directory.scroll_up(1)
        elif value == 'Down':
            self.connected_user_name_directory.scroll_down(1)
            self.connected_user_number_of_content_shared_directory.scroll_down(1)
            self.connected_user_content_sharing_status_directory.scroll_down(1)
            self.connected_user_connection_time_directory.scroll_down(1)
            self.connected_user_idle_time_directory.scroll_down(1)
        elif value == 'Page Up':
            self.connected_user_name_directory.scroll_up(self._NumberOfConnectedUsers)
            self.connected_user_number_of_content_shared_directory.scroll_up(self._NumberOfConnectedUsers)
            self.connected_user_content_sharing_status_directory.scroll_up(self._NumberOfConnectedUsers)
            self.connected_user_connection_time_directory.scroll_up(self._NumberOfConnectedUsers)
            self.connected_user_idle_time_directory.scroll_up(self._NumberOfConnectedUsers)
        elif value == 'Page Down':
            self.connected_user_name_directory.scroll_down(self._NumberOfConnectedUsers)
            self.connected_user_number_of_content_shared_directory.scroll_down(self._NumberOfConnectedUsers)
            self.connected_user_content_sharing_status_directory.scroll_down(self._NumberOfConnectedUsers)
            self.connected_user_connection_time_directory.scroll_down(self._NumberOfConnectedUsers)
            self.connected_user_idle_time_directory.scroll_down(self._NumberOfConnectedUsers)
        else:
            self.Discard('Invalid Command for SetConnectedUserNavigation')
            
    def SetDisconnectAllUsers(self, value, qualifier):

        DisconnectAllUsersCmdString = '\x1bD0SHAR\r\n'
        self.__SetHelper('DisconnectAllUsers', DisconnectAllUsersCmdString, value, qualifier)

    def SetDisconnectUser(self, value, qualifier):

        GroupStates = {
            'All Users' : [self._NumberOfAllUsers, self.all_users_name_directory, self.AllUsersData],
            'Connected User' : [self._NumberOfConnectedUsers, self.connected_user_name_directory, self.ConnectedUserData]
        }

        if qualifier['Group'] in GroupStates and 1 <= qualifier['Button'] <= GroupStates[qualifier['Group']][0]:
            startPosition = next(GroupStates[qualifier['Group']][1].get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                connectionID = GroupStates[qualifier['Group']][2][lookupIndex][0] # Connection ID -> index 0
                DisconnectUserCmdString = '\x1bD{}SHAR\r\n'.format(connectionID)
            except IndexError:
                return self.Discard('Invalid Command for SetDisconnectUser')
            self.__SetHelper('DisconnectUser', DisconnectUserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisconnectUser')

    def UpdateDisplayLayout(self, value, qualifier):

        self.UpdateDisplayLayoutGroup(value, qualifier)

    def SetDisplayLayoutGroup(self, value, qualifier):

        if 1 <= int(value) <= 11:
            DisplayLayoutGroupCmdString = 'w{}OMOD\r\n'.format(int(value))
            self.__SetHelper('DisplayLayoutGroup', DisplayLayoutGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayLayoutGroup')

    def UpdateDisplayLayoutGroup(self, value, qualifier):

        DisplayLayoutGroupCmdString = 'wOMOD\r\n'
        self.__UpdateHelper('DisplayLayoutGroup', DisplayLayoutGroupCmdString, value, qualifier)

    def __MatchDisplayLayoutGroup(self, match, tag):

        self.LayoutNumber = int(match.group(2).decode())
        self.WriteStatus('DisplayLayout', str(self.LayoutNumber), None)
        self.WriteStatus('DisplayLayoutGroup', str(int(match.group(1).decode())), None)
        self.RefreshUserData( None, None)

    def SetFileNavigation(self, value, qualifier):

        if value == 'Up':
            self.file_directory.scroll_up(1)
        elif value == 'Down':
            self.file_directory.scroll_down(1)
        elif value == 'Page Up':
            self.file_directory.scroll_up(self._NumberOfFiles)
        elif value == 'Page Down':
            self.file_directory.scroll_down(self._NumberOfFiles)
        else:
            self.Discard('Invalid Command for SetFileNavigation')

    def SetFullScreenSharedContent(self, value, qualifier):

        GroupStates = {
            'All Users' : [self._NumberOfAllUsers, self.all_users_name_directory, self.AllUsersData],
            'Sharing User' : [self._NumberOfSharingUsers, self.sharing_user_name_directory, self.SharingUserData],
        }

        if qualifier['Group'] in GroupStates and 1 <= qualifier['Button'] <= GroupStates[qualifier['Group']][0]:
            startPosition = next(GroupStates[qualifier['Group']][1].get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                portID = GroupStates[qualifier['Group']][2][lookupIndex][10] # Video Port ID -> index 10
                FullScreenSharedContentUserCmdString = 'wF{}*1SHAR\r\n'.format(portID)
            except IndexError:
                return self.Discard('Invalid Command for SetFullScreenSharedContent')
            self.__SetHelper('FullScreenSharedContent', FullScreenSharedContentUserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFullScreenSharedContent')

    def SetFullScreenSharedContentRevert(self, value, qualifier):

        FullScreenSharedContentRevertCmdString = 'wF0SHAR\r\n'
        self.__SetHelper('FullScreenSharedContentRevert', FullScreenSharedContentRevertCmdString, value, qualifier)

    def UpdateFullScreenSharedContentStatus(self, value, qualifier):

        FullScreenSharedContentStatusCmdString = 'wFSHAR\r\n'
        self.__UpdateHelper('FullScreenSharedContentStatus', FullScreenSharedContentStatusCmdString, value, qualifier)

    def __MatchFullScreenSharedContentStatus(self, match, tag):

        self.RefreshUserData( None, None)

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FullScreenSharedContentStatus', value, None)
        if value == 'On': # if full screen is on for sharing user
            portID = match.group(1).decode() # Video Port ID of sharing user with full screen
            for user in self.AllUsersData: # lookup sharing user name
                if user[10] == portID: # if video port ID's match
                    value = user[1] # store user name
                    self.WriteStatus('FullScreenSharedContentUserName', value, None)
        else: # if full screen is off for sharing user
            self.WriteStatus('FullScreenSharedContentUserName', 'N/A', None)

    def UpdateFullScreenSharedContentUserName(self, value, qualifier):

        self.UpdateFullScreenSharedContentStatus(None, None)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = '\x1bI1HDCP\r\n'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Source Connected', 
            '1' : 'No HDCP Content', 
            '2' : 'HDCP Content'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputStatus', value, None)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = '\x1bO1HDCP\r\n'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No monitor connected', 
            '1' : 'Monitor connected, not encrypted', 
            '2' : 'Monitor connected, currently encrypted'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetHDMIInputWindow(self, value, qualifier):

        ValueStateValues = {
            'Enabled' : '1', 
            'Disabled' : '0'
        }

        if value in ValueStateValues:
            HDMIInputWindowCmdString = '\x1b{}PIPS\r\n'.format(ValueStateValues[value])
            self.__SetHelper('HDMIInputWindow', HDMIInputWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIInputWindow')

    def UpdateHDMIInputWindow(self, value, qualifier):

        HDMIInputWindowCmdString = '\x1bPIPS\r\n'
        self.__UpdateHelper('HDMIInputWindow', HDMIInputWindowCmdString, value, qualifier)

    def UpdateHostname(self, value, qualifier):

        HostnameCmdString = 'wCN\r\n'
        self.__UpdateHelper('Hostname', HostnameCmdString, value, qualifier)

    def __MatchHostname(self, match, tag):

        value = match.group(1).decode('unicode_escape')
        self.WriteStatus('Hostname', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '\x1b0LS\r\n'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Not Active'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSignalStatus', value, None)

    def UpdateIPAddress(self, value, qualifier):

        LANStates = {
            'A': '1',
            'B': '2',
            'AV': '3'
        }
        lan = qualifier['LAN']
        
        if lan in LANStates:
            IPAddressCmdString = 'w{}CISG\r\n'.format(LANStates[lan])
            self.__UpdateHelper('IPAddress', IPAddressCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateIPAddress')

    def __MatchIPAddress(self, match, tag):

        LANStates = {
            '1': 'A',
            '2': 'B',
            '3': 'AV'
        }

        qualifier = {
            'LAN': LANStates[match.group(1).decode()]
        }

        value = match.group(2).decode()
        self.WriteStatus('IPAddress', value, qualifier)

    def SetLabelVisibility(self, value, qualifier):

        ValueStateValues = {
            'Show' : '1', 
            'Hide' : '0'
        }
        
        LabelStates = {
            'Hostname': '1',
            'IP Address A': '2',
            'IP Address B': '3',
            'Message Text': '5',
            'Code': '4',
            'Date/Time': '7',
            'Notifications/Messages': '6',
            'IP Address AV': '8'
            }

        if qualifier['Label'] in LabelStates and value in ValueStateValues:
            LabelVisibilityCmdString = 'wV{}*{}OSDL\r\n'.format(LabelStates[qualifier['Label']], ValueStateValues[value])
            self.__SetHelper('LabelVisibility', LabelVisibilityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLabelVisibility')

    def UpdateLabelVisibility(self, value, qualifier):

        LabelStates = {
            'Hostname': '1',
            'IP Address A': '2',
            'IP Address B': '3',
            'Message Text': '5',
            'Code': '4',
            'Date/Time': '7',
            'Notifications/Messages': '6',
            'IP Address AV': '8'
            }
        
        if qualifier['Label'] in LabelStates:
            LabelVisibilityCmdString = 'wV{}OSDL\r\n'.format(LabelStates[qualifier['Label']])
            self.__UpdateHelper('LabelVisibility', LabelVisibilityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLabelVisibility')

    def __MatchLabelVisibility(self, match, tag):

        ValueStateValues = {
            '1' : 'Show', 
            '0' : 'Hide'
        }
        
        LabelStates = {
            '1': 'Hostname',
            '2': 'IP Address A',
            '3': 'IP Address B',
            '5': 'Message Text',
            '4': 'Code',
            '7': 'Date/Time',
            '6': 'Notifications/Messages',
            '8': 'IP Address AV'
            }

        qualifier = {'Label': LabelStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LabelVisibility', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60 Hz)' : '10',
            '800x600 (60 Hz)' : '11',
            '1024x768 (60 Hz)' : '12',
            '1280x768 (60 Hz)' : '13',
            '1280x800 (60 Hz)' : '14',
            '1280x1024 (60 Hz)' : '15',
            '1360x768 (60 Hz)' : '16',
            '1366x768 (60 Hz)' : '17',
            '1440x900 (60 Hz)' : '18',
            '1400x1050 (60 Hz)' : '19',
            '1600x900 (60 Hz)' : '20',
            '1680x1050 (60 Hz)' : '21',
            '1600x1200 (60 Hz)' : '22',
            '1920x1200 (60 Hz)' : '23',
            '480p (60 Hz)' : '25',
            '480p (59.94 Hz)' : '24',
            '576p (50 Hz)' : '26',
            '720p (60 Hz)' : '34',
            '720p (59.94 Hz)' : '33',
            '720p (50 Hz)' : '32',
            '720p (30 Hz)' : '31',
            '720p (29.97 Hz)' : '30',
            '720p (25 Hz)' : '29',
            '1080i (60 Hz)' : '37',
            '1080i (59.94 Hz)' : '36',
            '1080i (50 Hz)' : '35',
            '1080p (60 Hz)' : '45',
            '1080p (59.94 Hz)' : '44',
            '1080p (50 Hz)' : '43',
            '1080p (30 Hz)' : '42',
            '1080p (29.97 Hz)' : '41',
            '1080p (25 Hz)' : '40',
            '1080p (24 Hz)' : '39',
            '1080p (23.98 Hz)' : '38',
            '2K 2048x1080 (60 Hz)' : '53',
            '2K 2048x1080 (59.94 Hz)' : '52',
            '2K 2048x1080 (50 Hz)' : '51',
            '2K 2048x1080 (30 Hz)' : '50',
            '2K 2048x1080 (29.97 Hz)' : '49',
            '2K 2048x1080 (25 Hz)' : '48',
            '2K 2048x1080 (24 Hz)' : '47',
            '2K 2048x1080 (23.98 Hz)' : '46',
            '2048x1200 (60 Hz)' : '54',
            '2048x1536 (60 Hz)' : '55',
            '2560x1080 (60 Hz)' : '56',
            '2560x1440 (60 Hz)' : '57',
            '2560x1600 (60 Hz)' : '58',
            '4K 3840x2160 (60 Hz)' : '66',
            '4K 3840x2160 (59.94 Hz)' : '65',
            '4K 3840x2160 (50 Hz)' : '64',
            '4K 3840x2160 (30 Hz)' : '63',
            '4K 3840x2160 (29.97 Hz)' : '62',
            '4K 3840x2160 (25 Hz)' : '61',
            '4K 3840x2160 (24 Hz)' : '60',
            '4K 3840x2160 (23.98 Hz)' : '59',
            '4096x2160 (60 Hz)' : '76',
            '4096x2160 (59.94 Hz)' : '75',
            '4096x2160 (50 Hz)' : '74',
            '4096x2160 (30 Hz)' : '73',
            '4096x2160 (29.97 Hz)' : '72',
            '4096x2160 (25 Hz)' : '71',
            '4096x2160 (24 Hz)' : '70',
            '4096x2160 (23.98 Hz)' : '69'
        }

        if value in ValueStateValues:
            OutputResolutionCmdString = 'w1*{}RATE\r\n'.format(ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'w1RATE\r\n'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10' : '640x480 (60 Hz)',
            '11' : '800x600 (60 Hz)',
            '12' : '1024x768 (60 Hz)',
            '13' : '1280x768 (60 Hz)',
            '14' : '1280x800 (60 Hz)',
            '15' : '1280x1024 (60 Hz)',
            '16' : '1360x768 (60 Hz)',
            '17' : '1366x768 (60 Hz)',
            '18' : '1440x900 (60 Hz)',
            '19' : '1400x1050 (60 Hz)',
            '20' : '1600x900 (60 Hz)',
            '21' : '1680x1050 (60 Hz)',
            '22' : '1600x1200 (60 Hz)',
            '23' : '1920x1200 (60 Hz)',
            '25' : '480p (60 Hz)',
            '24' : '480p (59.94 Hz)',
            '26' : '576p (50 Hz)',
            '34' : '720p (60 Hz)',
            '33' : '720p (59.94 Hz)',
            '32' : '720p (50 Hz)',
            '31' : '720p (30 Hz)',
            '30' : '720p (29.97 Hz)',
            '29' : '720p (25 Hz)',
            '37' : '1080i (60 Hz)',
            '36' : '1080i (59.94 Hz)',
            '35' : '1080i (50 Hz)',
            '45' : '1080p (60 Hz)',
            '44' : '1080p (59.94 Hz)',
            '43' : '1080p (50 Hz)',
            '42' : '1080p (30 Hz)',
            '41' : '1080p (29.97 Hz)',
            '40' : '1080p (25 Hz)',
            '39' : '1080p (24 Hz)',
            '38' : '1080p (23.98 Hz)',
            '53' : '2K 2048x1080 (60 Hz)',
            '52' : '2K 2048x1080 (59.94 Hz)',
            '51' : '2K 2048x1080 (50 Hz)',
            '50' : '2K 2048x1080 (30 Hz)',
            '49' : '2K 2048x1080 (29.97 Hz)',
            '48' : '2K 2048x1080 (25 Hz)',
            '47' : '2K 2048x1080 (24 Hz)',
            '46' : '2K 2048x1080 (23.98 Hz)',
            '54' : '2048x1200 (60 Hz)',
            '55' : '2048x1536 (60 Hz)',
            '56' : '2560x1080 (60 Hz)',
            '57' : '2560x1440 (60 Hz)',
            '58' : '2560x1600 (60 Hz)',
            '66' : '4K 3840x2160 (60 Hz)', 
            '65' : '4K 3840x2160 (59.94 Hz)',
            '64' : '4K 3840x2160 (50 Hz)',
            '63' : '4K 3840x2160 (30 Hz)',
            '62' : '4K 3840x2160 (29.97 Hz)',
            '61' : '4K 3840x2160 (25 Hz)',
            '60' : '4K 3840x2160 (24 Hz)',
            '59' : '4K 3840x2160 (23.98 Hz)',
            '76' : '4096x2160 (60 Hz)',
            '75' : '4096x2160 (59.94 Hz)',
            '74' : '4096x2160 (50 Hz)',
            '73' : '4096x2160 (30 Hz)',
            '72' : '4096x2160 (29.97 Hz)',
            '71' : '4096x2160 (25 Hz)',
            '70' : '4096x2160 (24 Hz)',
            '69' : '4096x2160 (23.98 Hz)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetPendingUserConnection(self, value, qualifier):

        GroupStates = {
            'All Users' : [self._NumberOfAllUsers, self.all_users_name_directory, self.AllUsersData],
            'Pending User' : [self._NumberOfPendingUsers, self.pending_user_name_directory, self.PendingUserData]
        }

        ValueStateValues = {
            'Approve' : '1',
            'Reject' : '0',
            'Pending': '2'
        }

        if qualifier['Group'] in GroupStates and 1 <= qualifier['Button'] <= GroupStates[qualifier['Group']][0] and value in ValueStateValues:
            startPosition = next(GroupStates[qualifier['Group']][1].get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                connectionID = GroupStates[qualifier['Group']][2][lookupIndex][0] # Connection ID -> index 0
                PendingUserConnectionCmdString = '\x1bC{}*{}SHAR\r\n'.format(connectionID, ValueStateValues[value])
            except IndexError:
                return self.Discard('Invalid Command for SetPendingUserConnection')
            self.__SetHelper('PendingUserConnection', PendingUserConnectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPendingUserConnection')

    def SetPendingUserNavigation(self, value, qualifier):

        if value == 'Up':
            self.pending_user_name_directory.scroll_up(1)
        elif value == 'Down':
            self.pending_user_name_directory.scroll_down(1)
        elif value == 'Page Up':
            self.pending_user_name_directory.scroll_up(self._NumberOfPendingUsers)
        elif value == 'Page Down':
            self.pending_user_name_directory.scroll_down(self._NumberOfPendingUsers)
        else:
            self.Discard('Invalid Command for SetPendingUserNavigation')

    def SetRefreshAllUsers(self, value, qualifier):

        if 'SetRefreshAllUsers' not in self.ConfiguredSetRefreshCommands:
            self.ConfiguredSetRefreshCommands.append('SetRefreshAllUsers')

        self.RefreshUserData(None, None)

    def SetRefreshConnectedUsers(self, value, qualifier):

        if 'SetRefreshConnectedUsers' not in self.ConfiguredSetRefreshCommands:
            self.ConfiguredSetRefreshCommands.append('SetRefreshConnectedUsers')

        self.RefreshUserData(None, None)

    def SetRefreshFiles(self, value, qualifier):

        RefreshFilesCmdString = 'wLF\r'
        self.FileRegex = []
        self.__SetHelper('RefreshFiles', RefreshFilesCmdString, value, qualifier)

    def SetRefreshPendingUsers(self, value, qualifier):

        if 'SetRefreshPendingUsers' not in self.ConfiguredSetRefreshCommands:
            self.ConfiguredSetRefreshCommands.append('SetRefreshPendingUsers')

        self.RefreshUserData(None, None)

    def SetRefreshSharingUsers(self, value, qualifier):

        if 'SetRefreshSharingUsers' not in self.ConfiguredSetRefreshCommands:
            self.ConfiguredSetRefreshCommands.append('SetRefreshSharingUsers')

        self.RefreshUserData(None, None)

    def __MatchUpdateUSB(self, match, tag):
        if tag == 'USB':
            self.SetRefreshUSBMicrophones(None, None)
        elif tag == 'Cameras':
            self.SetRefreshUSBCameras(None, None)
        elif tag == 'Speakers':
            self.SetRefreshUSBSpeakers(None, None)
            
    def SetRefreshUSBCameras(self, value, qualifier):
        self.Send('\x1BJ1USBS\r\n')
        self.UpdateUSBCameraSelectStatus(None,None)
            
    def SetRefreshUSBMicrophones(self, value, qualifier):
        self.Send('\x1BJ3USBS\r\n')
        self.UpdateUSBMicrophoneSelectStatus(None,None)
        
    def SetRefreshUSBSpeakers(self, value, qualifier):
        self.Send('\x1BJ4USBS\r\n')

    def __MatchUpdateUsers(self, match, tag):

        if match.group(1):
            ValueStateValues = {
                '1' : 'Enabled',
                '0' : 'Disabled'
            }

            value = ValueStateValues[match.group(2).decode()]
            if match.group(1).decode() == 'Pips': # if HDMI Input Window response
                self.WriteStatus('HDMIInputWindow', value, None)

        self.RefreshUserData( None, None)

    def SetSharingUserNavigation(self, value, qualifier):

        if value == 'Up':
            self.sharing_user_name_directory.scroll_up(1)
            self.sharing_user_number_of_content_shared_directory.scroll_up(1)
            self.sharing_user_content_type_directory.scroll_up(1)
            self.sharing_user_content_sharing_location_directory.scroll_up(1)
        elif value == 'Down':
            self.sharing_user_name_directory.scroll_down(1)
            self.sharing_user_number_of_content_shared_directory.scroll_down(1)
            self.sharing_user_content_type_directory.scroll_down(1)
            self.sharing_user_content_sharing_location_directory.scroll_down(1)
        elif value == 'Page Up':
            self.sharing_user_name_directory.scroll_up(self._NumberOfSharingUsers)
            self.sharing_user_number_of_content_shared_directory.scroll_up(self._NumberOfSharingUsers)
            self.sharing_user_content_type_directory.scroll_up(self._NumberOfSharingUsers)
            self.sharing_user_content_sharing_location_directory.scroll_up(self._NumberOfSharingUsers)
        elif value == 'Page Down':
            self.sharing_user_name_directory.scroll_down(self._NumberOfSharingUsers)
            self.sharing_user_number_of_content_shared_directory.scroll_down(self._NumberOfSharingUsers)
            self.sharing_user_content_type_directory.scroll_down(self._NumberOfSharingUsers)
            self.sharing_user_content_sharing_location_directory.scroll_down(self._NumberOfSharingUsers)
        else:
            self.Discard('Invalid Command for SetSharingUserNavigation')

    def UpdateScreenSaverStatus(self, value, qualifier):

        ScreenSaverStatusCmdString = 'wS1SSAV\r\n'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'Active Input Detected; Timer not running', 
            '1' : 'No Active Input; Timer running; Output sync enabled', 
            '2' : 'No Active Input; Timer expired; Output sync disabled'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def SetStatusBar(self, value, qualifier):

        ValueStateValues = {
            'Always Visible' : '1', 
            'Always Hidden' : '3', 
            'Hide when one content is shared' : '2', 
            'Hide whenever content is shared' : '0'
        }

        if value in ValueStateValues:
            StatusBarCmdString = 'wM{}OSDL\r\n'.format(ValueStateValues[value])
            self.__SetHelper('StatusBar', StatusBarCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStatusBar')

    def UpdateStatusBar(self, value, qualifier):

        StatusBarCmdString = 'wMOSDL\r\n'
        self.__UpdateHelper('StatusBar', StatusBarCmdString, value, qualifier)

    def __MatchStatusBar(self, match, tag):

        ValueStateValues = {
            '1' : 'Always Visible', 
            '3' : 'Always Hidden', 
            '2' : 'Hide when one content is shared', 
            '0' : 'Hide whenever content is shared'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('StatusBar', value, None)

    def SetStopAllShares(self, value, qualifier):

        StopAllSharesCmdString = '\x1bS0SHAR\r\n'
        self.__SetHelper('StopAllShares', StopAllSharesCmdString, value, qualifier)

    def SetStopIndividualShare(self, value, qualifier):

        GroupStates = {
            'All Users' : [self._NumberOfAllUsers, self.all_users_name_directory, self.AllUsersData],
            'Sharing User' : [self._NumberOfSharingUsers, self.sharing_user_name_directory, self.SharingUserData],
        }

        if qualifier['Group'] in GroupStates and 1 <= qualifier['Button'] <= GroupStates[qualifier['Group']][0]:
            startPosition = next(GroupStates[qualifier['Group']][1].get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                connectionID = GroupStates[qualifier['Group']][2][lookupIndex][0] # Connection ID -> index 0
                streamID = GroupStates[qualifier['Group']][2][lookupIndex][2] # Stream ID -> index 2
                StopIndividualShareUserCmdString = '\x1bS{}*{}SHAR\r\n'.format(connectionID, streamID)
            except IndexError:
                return self.Discard('Invalid Command for SetStopIndividualShare')
            self.__SetHelper('StopIndividualShare', StopIndividualShareUserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStopIndividualShare')

    def SetStopShare(self, value, qualifier):

        GroupStates = {
            'All Users' : [self._NumberOfAllUsers, self.all_users_name_directory, self.AllUsersData],
            'Connected User' : [self._NumberOfConnectedUsers, self.connected_user_name_directory, self.ConnectedUserData],
            'Sharing User' : [self._NumberOfSharingUsers, self.sharing_user_name_directory, self.SharingUserData],
        }

        if qualifier['Group'] in GroupStates and 1 <= qualifier['Button'] <= GroupStates[qualifier['Group']][0]:
            startPosition = next(GroupStates[qualifier['Group']][1].get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                connectionID = GroupStates[qualifier['Group']][2][lookupIndex][0] # Connection ID -> index 0
                StopShareUserCmdString = '\x1bS{}SHAR\r\n'.format(connectionID)
            except IndexError:
                return self.Discard('Invalid Command for SetStopShare')
            self.__SetHelper('StopShare', StopShareUserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStopShare')

    def SetSwapContentSharingLocation(self, value, qualifier):

        GroupStates = {
            'All Users' : [self._NumberOfAllUsers, self.all_users_content_sharing_location_directory, self.AllUsersData],
            'Sharing User' : [self._NumberOfSharingUsers,self.sharing_user_content_sharing_location_directory, self.SharingUserData],
        }

        LocationStates = ['Quadrant 1', 'Quadrant 2', 'Quadrant 3', 'Quadrant 4', 'Full Screen']

        if qualifier['Group'] in GroupStates and qualifier['Location 1'] in LocationStates and qualifier['Location 2'] in LocationStates:
            locations = GroupStates[qualifier['Group']][0].get_displayed_entries()
            for location in locations:
                if location[0] == qualifier['Location 1']:
                    lookupIndex1 = location[1] - 1
                elif location[0] == qualifier['Location 2']:
                    lookupIndex2 = location[1] - 1
            try:
                portID1 = GroupStates[qualifier['Group']][1][lookupIndex1][10] # Video Port ID -> index 10
                portID2 = GroupStates[qualifier['Group']][1][lookupIndex2][10]
                SwapContentSharingLocationCmdString = '\x1bW{}*{}SHAR\r\n'.format(portID1, portID2)
            except Exception:
                return self.Discard('Invalid Command for SetSwapContentSharingLocation')
            self.__SetHelper('SwapContentSharingLocation', SwapContentSharingLocationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwapContentSharingLocation')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0', 
            'On with Sync' : '2'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = '1*{0}b'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '1b'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off', 
            '2' : 'On with Sync'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetDigitalAudioInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -18,
            'Max' : 60
            }
        
        if self.AudioInputID is not None and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            DigitalAudioInputGainCmdString = 'wG{0}*{1}Usbs\r\n'.format(self.AudioInputID, int(value))
            self.__SetHelper('DigitalAudioInputGain', DigitalAudioInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalAudioInputGain')
    
    def SetDigitalAudioInputMute(self, value, qualifier):

        ValueConstraints = {
            'On' : '1',
            'Off' : '0'
            }
    
        if self.AudioInputID is not None and value in ValueConstraints:
            startPosition = next(self.usb_gain_directory.get_displayed_entries())[1]
            DigitalAudioInputMuteCmdString = 'wY{0}*{1}Usbs\r\n'.format(self.AudioInputID, ValueConstraints[value])
            self.__SetHelper('DigitalAudioInputMute', DigitalAudioInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalAudioInputMute')
    
    def SetUSBMicrophoneNavigation(self, value, qualifier):

        if value == 'Up':
            self.usb_name_directory.scroll_up(1)
            self.usb_gain_directory.scroll_up(1)
            self.usb_mute_directory.scroll_up(1)
        elif value == 'Down':
            self.usb_name_directory.scroll_down(1)
            self.usb_gain_directory.scroll_down(1)
            self.usb_mute_directory.scroll_down(1)
        elif value == 'Page Up':
            self.usb_name_directory.scroll_up(self._NumberOfUSBMicrophones)
            self.usb_gain_directory.scroll_up(self._NumberOfUSBMicrophones)
            self.usb_mute_directory.scroll_up(self._NumberOfUSBMicrophones)
        elif value == 'Page Down':
            self.usb_name_directory.scroll_down(self._NumberOfUSBMicrophones)
            self.usb_gain_directory.scroll_down(self._NumberOfUSBMicrophones)
            self.usb_mute_directory.scroll_down(self._NumberOfUSBMicrophones)
        else:
            self.Discard('Invalid Command for SetUSBMicrophoneNavigation')
    
    def __MatchUSBJson(self, match, tag):

        data = match.group(1).decode()
        data = loads(data)
        datadigital = data.pop(1)
        self.AudioInputID = str(datadigital['id'])
        self.USBNames = []
        self.USBMicrophoneGains = []
        self.USBMicrophoneMutes = []
        self.USBIDs = []
        mutedict = {
            1: 'On',
            0: 'Off'
        }
        self.WriteStatus('DigitalAudioInputMute', mutedict[datadigital['mute']], None)
        self.WriteStatus('DigitalAudioInputGain', int(datadigital['gain']), None)
        for items in data:
            if '(removed)' in items['name']:
                continue
            else:
                self.USBIDs.append(str(items['id']))
                self.USBNames.append(items['name'])
                self.USBMicrophoneMutes.append(mutedict[items['mute']])
                self.USBMicrophoneGains.append(int(items['gain']))
        self.usb_name_directory.reset(self.USBNames)
        self.usb_gain_directory.reset(self.USBMicrophoneGains)
        self.usb_mute_directory.reset(self.USBMicrophoneMutes)

    def SetUSBMicrophoneSelect(self, value, qualifier):


        if 1 <= qualifier['Button'] <= self._NumberOfUSBMicrophones:
            startPosition = next(self.usb_name_directory.get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                USBID = self.USBIDs[lookupIndex] # Connection ID -> index 0
                USBMicrophoneSelectUserCmdString = '\x1bN3*{}USBS\r\n'.format(USBID)
            except IndexError:
                return self.Discard('Invalid Command for SetUSBMicrophoneSelect')
            self.__SetHelper('USBMicrophoneSelect', USBMicrophoneSelectUserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBMicrophoneSelect')

    def UpdateUSBMicrophoneSelectStatus(self, value, qualifier):
        self.Send('wN3USBS\r\n')

    def __MatchUSBMicrophoneSelectStatus(self, match, tag):
        mic = match.group(1).decode()
        if mic == '0' or self.AudioInputID == mic:
            self.WriteStatus('USBMicrophoneSelectStatus', '', None)
        else:
            try:
                miclookup = self.USBIDs.index(mic)
                micname = self.USBNames[miclookup]
                self.WriteStatus('USBMicrophoneSelectStatus', micname, None)
            except ValueError:
                self.WriteStatus('USBMicrophoneSelectStatus', 'N/A', None)

    def SetUSBCameraNavigation(self, value, qualifier):

        if value == 'Up':
            self.usb_camera_name_directory.scroll_up(1)
        elif value == 'Down':
            self.usb_camera_name_directory.scroll_down(1)
        elif value == 'Page Up':
            self.usb_camera_name_directory.scroll_up(self._NumberOfUSBCameras)
        elif value == 'Page Down':
            self.usb_camera_name_directory.scroll_down(self._NumberOfUSBCameras)
        else:
            self.Discard('Invalid Command for SetUSBCameraNavigation')

    def __MatchUSBCameras(self, match, tag):

        data = match.group(1).decode()
        data = loads(data)
        self.USBCameraNames = []
        self.USBCameraIDs = []
        for items in data:
            if items:
                self.USBCameraIDs.append(items['id'])
                self.USBCameraNames.append(items['name'])
        self.usb_camera_name_directory.reset(self.USBCameraNames)

    def SetUSBCameraSelect(self, value, qualifier):

        if 1 <= qualifier['Button'] <= self._NumberOfUSBCameras:
            startPosition = next(self.usb_camera_name_directory.get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                USBID = self.USBCameraIDs[lookupIndex] # Connection ID -> index 0
                USBCameraSelectUserCmdString = '\x1bN1*{}USBS\r\n'.format(USBID)
            except IndexError:
                return self.Discard('Invalid Command for SetUSBCameraSelect')
            self.__SetHelper('USBCameraSelect', USBCameraSelectUserCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBCameraSelect')

    def UpdateUSBCameraSelectStatus(self, value, qualifier):
        self.Send('wN1USBS\r\n')

    def __MatchUSBCameraSelectStatus(self, match, tag):
        camera = match.group(1).decode()
        if camera == '0':
            self.WriteStatus('USBCameraSelectStatus', '', None)
        else:
            try:
                cameralookup = self.USBCameraIDs.index(int(camera))
                cameraname = self.USBCameraNames[cameralookup]
                self.WriteStatus('USBCameraSelectStatus', cameraname, None)
            except ValueError:
                self.WriteStatus('USBCameraSelectStatus', 'N/A', None)

    def __MatchUSBMicrophoneGain(self, match, tag):

        id = match.group(1).decode()
        value = int(match.group(2).decode())
        if id == self.AudioInputID:
            self.WriteStatus('DigitalAudioInputGain', value, None)
        else:
            try:
                pos = self.USBIDs.index(id)
                self.USBMicrophoneGains[pos] = value
                self.usb_gain_directory.refresh(self.USBMicrophoneGains)
            except ValueError:
                pass

    def SetUSBMicrophoneGain(self, value, qualifier):

        ValueConstraints = {
            'Min' : -18,
            'Max' : 60
            }
        startPosition = next(self.usb_gain_directory.get_displayed_entries())[1]
        lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            try:
                USBID = self.USBIDs[lookupIndex]
                USBMicrophoneGainCmdString = 'wG{0}*{1}Usbs\r\n'.format(USBID, int(value))
            except IndexError:
                return self.Discard('Invalid Command for SetUSBMicrophoneGain')
            self.__SetHelper('USBMicrophoneGain', USBMicrophoneGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBMicrophoneGain')
    
    def SetUSBMicrophoneMute(self, value, qualifier):
    
        ValueConstraints = {
            'On' : '1',
            'Off' : '0'
            }
    
        if 1 <= qualifier['Button'] <= self._NumberOfUSBMicrophones:
            startPosition = next(self.usb_mute_directory.get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                USBID = self.USBIDs[lookupIndex]
                USBMicrophoneMuteCmdString = 'wY{0}*{1}Usbs\r\n'.format(USBID, ValueConstraints[value])
            except IndexError:
                return self.Discard('Invalid Command for SetUSBMicrophoneMute')
            self.__SetHelper('USBMicrophoneMute', USBMicrophoneMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBMicrophoneMute')
                
    def __MatchUSBMicrophoneMute(self, match, tag):

        ValueConstraints = {
            '1' : 'On',
            '0' : 'Off'
            }
        id = match.group(1).decode()
        value = match.group(2).decode()
        if id == self.AudioInputID:
            self.WriteStatus('DigitalAudioInputMute', ValueConstraints[value], None)
        else:
            try:
                pos = self.USBIDs.index(id)
                self.USBMicrophoneMutes[pos] = ValueConstraints[value]
                self.usb_mute_directory.refresh(self.USBMicrophoneMutes)
            except ValueError:
                pass
    
    def SetUSBSpeakerNavigation(self, value, qualifier):

        if value == 'Up':
            self.usb_speakers_name_directory.scroll_up(1)
            self.usb_speakers_volume_directory.scroll_up(1)
            self.usb_speakers_mute_directory.scroll_up(1)
        elif value == 'Down':
            self.usb_speakers_name_directory.scroll_down(1)
            self.usb_speakers_volume_directory.scroll_down(1)
            self.usb_speakers_mute_directory.scroll_down(1)
        elif value == 'Page Up':
            self.usb_speakers_name_directory.scroll_up(self._NumberOfUSBSpeakers)
            self.usb_speakers_volume_directory.scroll_up(self._NumberOfUSBSpeakers)
            self.usb_speakers_mute_directory.scroll_up(self._NumberOfUSBSpeakers)
        elif value == 'Page Down':
            self.usb_speakers_name_directory.scroll_down(self._NumberOfUSBSpeakers)
            self.usb_speakers_volume_directory.scroll_down(self._NumberOfUSBSpeakers)
            self.usb_speakers_mute_directory.scroll_down(self._NumberOfUSBSpeakers)
        else:
            self.Discard('Invalid Command for SetUSBSpeakerNavigation')

    def __MatchUSBSpeakers(self, match, tag):

        data = match.group(1).decode()
        data = loads(data)
        self.USBSpeakerNames = []
        self.USBSpeakerGains = []
        self.USBSpeakerMutes = []
        self.USBSpeakerIDs = []
        mutedict = {
            '1': 'On',
            '0': 'Off'
        }
        
        masterdict = {
            '1': 'Enable',
            '0': 'Disable'
        }
        for items in data:
            if items:
                self.USBSpeakerIDs.append(items['id'])
                self.USBSpeakerNames.append(items['name'])
                self.USBSpeakerMutes.append(mutedict[str(items['mute'])])
                self.USBSpeakerGains.append(int(items['volume']))
        self.usb_speakers_name_directory.reset(self.USBSpeakerNames)
        self.usb_speakers_volume_directory.reset(self.USBSpeakerGains)
        self.usb_speakers_mute_directory.reset(self.USBSpeakerMutes)
        
    def __MatchUSBSpeakerVolume(self, match, tag):

        id = match.group(1).decode()
        value = match.group(2).decode()
        try:
            pos = self.USBSpeakerIDs.index(int(id))
            self.USBSpeakerGains[pos] = int(value)
            self.usb_speakers_volume_directory.refresh(self.USBSpeakerGains)
        except ValueError:
            pass
        
    def SetUSBSpeakerVolume(self, value, qualifier):
    
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        
        if 1 <= qualifier['Button'] <= self._NumberOfUSBSpeakers:
            if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
                startPosition = next(self.usb_speakers_volume_directory.get_displayed_entries())[1]
                lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
                try:
                    USBID = self.USBSpeakerIDs[lookupIndex]
                    USBSpeakerVolumeCmdString = 'wK{0}*{1}Usbs\r\n'.format(USBID, int(value))
                except IndexError:
                    return self.Discard('Invalid Command for SetUSBSpeakerVolume')
                self.__SetHelper('USBSpeakerVolume', USBSpeakerVolumeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetUSBSpeakerVolume')
        else:
            self.Discard('Invalid Command for SetUSBSpeakerVolume')
    
    def SetUSBSpeakerMute(self, value, qualifier):
                
        ValueConstraints = {
            'On' : '1',
            'Off' : '0'
            }
    
        if 1 <= qualifier['Button'] <= self._NumberOfUSBSpeakers:
            startPosition = next(self.usb_speakers_mute_directory.get_displayed_entries())[1]
            lookupIndex = (qualifier['Button'] - 1) + (startPosition - 1)
            try:
                USBID = self.USBSpeakerIDs[lookupIndex]
                USBSpeakerMuteCmdString = 'wZ{0}*{1}Usbs\r\n'.format(USBID, ValueConstraints[value])
            except IndexError:
                return self.Discard('Invalid Command for SetUSBSpeakerMute')
            self.__SetHelper('USBSpeakerMute', USBSpeakerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBSpeakerMute')
                
    def __MatchUSBSpeakerMute(self, match, tag):

        ValueConstraints = {
            '1' : 'On',
            '0' : 'Off'
            }
        id = match.group(1).decode()
        value = match.group(2).decode()
        try:
            pos = self.USBSpeakerIDs.index(int(id))
            self.USBSpeakerMutes[pos] = ValueConstraints[value]
            self.usb_speakers_mute_directory.refresh(self.USBSpeakerMutes)
        except ValueError:
            pass
    
    def SetUSBSpeakerMaster(self, value, qualifier):

        ValueConstraints = {
            'Enable' : '1',
            'Disable' : '0'
            }
    
        USBSpeakerMasterCmdString = 'wF{0}USBS\r\n'.format(ValueConstraints[value])
        self.__SetHelper('USBSpeakerMaster', USBSpeakerMasterCmdString, value, qualifier)
            
    def UpdateUSBSpeakerMaster(self, value, qualifier):

        USBSpeakerMasterCmdString = 'wFUSBS\r\n'
        self.__UpdateHelper('USBSpeakerMaster', USBSpeakerMasterCmdString, value, qualifier)
                
    def __MatchUSBSpeakerMaster(self, match, tag):

        ValueConstraints = {
            '1' : 'Enable',
            '0' : 'Disable'
            }
        value = ValueConstraints[match.group(1).decode()]
        self.WriteStatus('USBSpeakerMaster', value, None)
    
    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -100,
            'Max' : 0
            }
        
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        sign = match.group(1).decode()
        value = int(match.group(2).decode())
        if sign == '-':
            value = -value
        self.WriteStatus('Volume', value, None)

    def __MatchFiles(self, match, tag):

        self.FileRegex.append(match.group('file').decode())
        
    def __MatchEndFiles(self, match, tag):

        try:
            self.file_directory.reset(self.FileRegex)
        except:
            self.Error(['Refresh Files: Invalid/unexpected response'])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '35' : 'Account does not exist'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E'+ value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.LayoutNumber = None
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
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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
            self.write_to_module()
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

    def write_to_module(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value})

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
    def refresh(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()

    @UseAutoUpdate
    def refresh(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()

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
            self._start_index = len(self.entry_list) - 1 # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1