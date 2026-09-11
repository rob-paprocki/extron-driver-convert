from extronlib.interface import SPInterface
import re
from extronlib.system import Wait
import time
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
        self._NumberOfPendingUsers = 5
        self._NumberOfConnectedUsers = 5
        self._NumberOfSharingUsers = 5
        self._NumberOfOutgoingActiveLearningTies = 5
        self._NumberOfFiles = 5
        
        self.Models = {
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AccessMode': { 'Status': {}},
            'ActiveLearningDisplayOption': { 'Status': {}},
            'ActiveLearningEncoderSourceMode' : { 'Status': {}},
            'ActiveLearningTie': {'Parameters': ['Action', 'IP Address/Hostname'], 'Status': {}},
            'ActiveLearningUsernameCommand': { 'Status': {}},
            'ActiveLearningUsernameStatus': { 'Status': {}},
            'AllPendingUserConnections': { 'Status': {}},
            'AllUsersConnectionTime': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersContentSharingStatus': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersContentType': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersIdleTime': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersName': {'Parameters': ['Button'], 'Status': {}},
            'AllUsersNavigation': { 'Status': {}},
            'AllUsersNumberofContentShared': {'Parameters': ['Button'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ChannelPresetRecall': { 'Status': {}},
            'ChannelPresetRecallStep': { 'Status': {}},
            'ClosedCaption': {'Parameters': ['Output'], 'Status': {}},
            'CompareOutgoingActiveLearningTies': { 'Status': {}},
            'ConfirmationCode': { 'Status': {}},
            'ConfirmationCodeMode': { 'Status': {}},
            'ConnectedUserConnectionTime': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserContentSharingStatus': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserIdleTime': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserName': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedUserNavigation': { 'Status': {}},
            'ConnectedUserNumberofContentShared': {'Parameters': ['Button'], 'Status': {}},
            'CurrentSourceItem': {'Parameters': ['Output'], 'Status': {}},
            'DisconnectAllUsers': { 'Status': {}},
            'DisconnectUser': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'ExpoMode': { 'Status': {}},
            'FileName': {'Parameters': ['Button'], 'Status': {}},
            'FileNavigation': { 'Status': {}},
            'FullScreenSharedContent': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'FullScreenSharedContentRevert': { 'Status': {}},
            'FullScreenSharedContentStatus': { 'Status': {}},
            'FullScreenSharedContentUserName': { 'Status': {}},
            'HDCPInputAuthorization': { 'Status': {}},
            'HDCPInputStatus': { 'Status': {}},
            'HDCPMode': {'Parameters': ['Output'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIInputPassThrough': { 'Status': {}},
            'HDMIInputWindow': { 'Status': {}},
            'Hostname': { 'Status': {}},
            'InputSignalStatus': { 'Status': {}},
            'IPAddress': {'Parameters': ['LAN'], 'Status': {}},
            'LabelVisibility': {'Parameters': ['Label'], 'Status': {}},
            'LoopPlay': {'Parameters': ['Output'], 'Status': {}},
            'NumberofContentSharedonOutput': { 'Status': {}},
            'NumberofUsersConnected': { 'Status': {}},
            'NumberofUsersNotSharing': { 'Status': {}},
            'NumberofUsersPending': { 'Status': {}},
            'NumberofUsersSharing': { 'Status': {}},
            'OutgoingActiveLearningTieRemove': { 'Status': {}},
            'OutgoingActiveLearningTies': {'Parameters': ['Button'], 'Status': {}},
            'OutgoingActiveLearningTiesNavigation': { 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'PendingUserConnection': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'PendingUserName': {'Parameters': ['Button'], 'Status': {}},
            'PendingUserNavigation': { 'Status': {}},
            'Playback': {'Parameters': ['Output'], 'Status': {}},
            'PlayerStatus': { 'Status': {}},
            'RefreshAllUsers': { 'Status': {}},
            'RefreshConnectedUsers': { 'Status': {}},
            'RefreshFiles': { 'Status': {}},
            'RefreshOutgoingActiveLearningTies': { 'Status': {}},
            'RefreshPendingUsers': { 'Status': {}},
            'RefreshSharingUsers': { 'Status': {}},
            'RemoveAllActiveLearningTies': { 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'SharingUserContentType': {'Parameters': ['Button'], 'Status': {}},
            'SharingUserName': {'Parameters': ['Button'], 'Status': {}},
            'SharingUserNavigation': { 'Status': {}},
            'SharingUserNumberofContentShared': {'Parameters': ['Button'], 'Status': {}},
            'StatusBar': { 'Status': {}},
            'StopAllShares': { 'Status': {}},
            'StopIndividualShare': {'Parameters': ['Group', 'Button'], 'Status': {}},
            'StopShare': {'Parameters': ['Group', 'Button'], 'Status': {}},        
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True

        self.AllUsersData = [] # ex: [['1038276244', 'SALESLOANER', '519789643', '440x440_gray_WeatherChannel_sel.png', '1', '0', '0', '5000', '10000', '9014', '1126080', '']]
        self.ConnectedUserData = []
        self.PendingUserData = []
        self.SharingUserData = []
        self.IdleStartTime = {'AllUsers': {}, 'ConnectedUser': {}} # ex: {'AllUsers': {'1038276244': 5}, 'ConnectedUser': {'1038276244': 5}}
        self.ConfiguredSetRefreshCommands = [] # determines which user lists to write status for
        self.AccessMode = None # used to store user permission level
        self.HDMIName = '' # used to store HDMI Client App Controls Label
        self.FileRegex = []

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(?:MylkC\d{1,2}|SharK\d{1,2}|(Pips|In)([0-1])|UserChg|SharW\d+\*\d+|SharChg)\r\n'), self.__MatchUpdateUsers, None) # triggers main query for all user data
            self.AddMatchString(re.compile(b'SharL([\S \r\n]+)?\r\n\r\n'), self.__MatchAllUsers, None) # main query response for all user data
            self.AddMatchString(re.compile(b'SharM([1-3]\*[1-2])\r\n'), self.__MatchAccessMode, None) # determines user permission level (unsolicited responses only supported for fw above 1.01.0000-b003)
            self.AddMatchString(re.compile(b'Nmi1,([\S ]+)\r\n'), self.__MatchHDMIName, None) # determines name shown for HDMI user

            self.AddMatchString(re.compile(b'VdrtD([01])\r\n'), self.__MatchActiveLearningDisplayOption, None)
            self.AddMatchString(re.compile(b'VdrtH([0123])\r\n'), self.__MatchActiveLearningEncoderSourceMode, None)
            self.AddMatchString(re.compile(b'AppcN([\S ]+)?\r\n'), self.__MatchActiveLearningUsernameStatus, None)
            self.AddMatchString(re.compile(b'Amt([12])\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'TvprT1\*(\d{2,3})\r\n'), self.__MatchChannelPresetRecall, None)
            self.AddMatchString(re.compile(b'SubtE([12])\*([01])\r\n'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'PincV (\d{4})?\r\n'), self.__MatchConfirmationCode, None)
            self.AddMatchString(re.compile(b'PincM([0-3])\r\n'), self.__MatchConfirmationCodeMode, None)
            self.AddMatchString(re.compile(b'PlyrU([12])\*([\S ]+)?\r\n'), self.__MatchCurrentSourceItem, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'SharP([0-2])\r\n'), self.__MatchExpoMode, None)
            self.AddMatchString(re.compile(b'SharF(\d+)?\*?([01])\r\n'), self.__MatchFullScreenSharedContentStatus, None)
            self.AddMatchString(re.compile(b'HdcpE1\*([0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI1\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpS([12])\*([0-4])\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(re.compile(b'HdcpO([12])\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Ipn ([\S ]+)\r\n'), self.__MatchHostname, None)
            self.AddMatchString(re.compile(b'In00 ([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Cisg ([12])\*([\d.]+)\/[\d.]+\*[\d.]+\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(re.compile(b'OsdlV([1-7])\*([01])\r\n'), self.__MatchLabelVisibility, None)
            self.AddMatchString(re.compile(b'PlyrR([12])\*([01])\r\n'), self.__MatchLoopPlay, None)
            self.AddMatchString(re.compile(b'VdrtI([\S \r\n]+)?\r\n\r\n'), self.__MatchOutgoingActiveLearningTies, None)
            self.AddMatchString(re.compile(b'Rate([12])\*0(\d{2})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'Plyr([YSOE])([12])(?:\*([0-2]))?(\.0)?\r\n'), self.__MatchPlayback, None)
            self.AddMatchString(re.compile(b'SharQ([1-5])\r\n'), self.__MatchPlayerStatus, None)
            self.AddMatchString(re.compile(b'SsavS1\*([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(b'OsdlM([0-3])\r\n'), self.__MatchStatusBar, None)
            self.AddMatchString(re.compile(b'Vmt([12])\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol([+-])(\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(01|1[0-7]|2[245678]|3[012])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'(?P<file>.*..*)\s\w{1,3},.*\sGMT\s\d*'), self.__MatchFiles, None)
            self.AddMatchString(re.compile(b'Bytes Left\r\n'), self.__MatchEndFiles, None)
            
        self.all_users_name_directory = Directory('AllUsersName', self._NumberOfAllUsers, filler='')
        self.all_users_name_directory.write_status_function = self.WriteStatus

        self.all_users_number_of_content_shared_directory = Directory('AllUsersNumberofContentShared', self._NumberOfAllUsers, filler='0')
        self.all_users_number_of_content_shared_directory.write_status_function = self.WriteStatus

        self.all_users_content_sharing_status_directory = Directory('AllUsersContentSharingStatus', self._NumberOfAllUsers, filler='N/A')
        self.all_users_content_sharing_status_directory.write_status_function = self.WriteStatus

        self.all_users_content_type_directory = Directory('AllUsersContentType', self._NumberOfAllUsers, filler='')
        self.all_users_content_type_directory.write_status_function = self.WriteStatus

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

        self.outgoing_active_learning_ties_directory = Directory('OutgoingActiveLearningTies', self._NumberOfOutgoingActiveLearningTies, filler='')
        self.outgoing_active_learning_ties_directory.write_status_function = self.WriteStatus
        
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

        self.all_users_connection_time_directory = Directory('AllUsersConnectionTime', self._NumberOfAllUsers, filler=0)
        self.all_users_connection_time_directory.write_status_function = self.WriteStatus

        self.all_users_idle_time_directory = Directory('AllUsersIdleTime', self._NumberOfAllUsers, filler=0)
        self.all_users_idle_time_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfPendingUsers(self):
        return self._NumberOfPendingUsers

    @NumberOfPendingUsers.setter
    def NumberOfPendingUsers(self, value):
        self._NumberOfPendingUsers= value
        self.pending_user_name_directory = Directory('PendingUserName', self._NumberOfPendingUsers, filler='')
        self.pending_user_name_directory.write_status_function = self.WriteStatus

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

    @property
    def NumberOfOutgoingActiveLearningTies(self):
        return self._NumberOfOutgoingActiveLearningTies

    @NumberOfOutgoingActiveLearningTies.setter
    def NumberOfOutgoingActiveLearningTies(self, value):
        self._NumberOfOutgoingActiveLearningTies= value
        self.outgoing_active_learning_ties_directory = Directory('OutgoingActiveLearningTies', self._NumberOfOutgoingActiveLearningTies, filler='')
        self.outgoing_active_learning_ties_directory.write_status_function = self.WriteStatus

    @property
    def NumberOfFiles(self):
        return self._NumberOfFiles

    @NumberOfFiles.setter
    def NumberOfFiles(self, value):
        self._NumberOfFiles= value
        self.file_directory = Directory('FileName', self._NumberOfFiles, filler='')
        self.file_directory.write_status_function = self.WriteStatus

    def __MatchVerboseMode(self, match, tag):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, tag):
        self.EchoDisabled = False

    def RefreshUserData(self, value, qualifier):
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

                    self.AllUsersData.append([data[0], name, data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]])
                    listLookup['AllUsersName'].append(name)
                    listLookup['AllUsersContentType'].append(data[3])
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

    def SetActiveLearningDisplayOption(self, value, qualifier):

        ValueStateValues = {
            'Add as a Quadrant': '0',
            'Overlay': '1',
        }

        if value in ValueStateValues:
            ActiveLearningDisplayOptionCmdString = 'wD{}VDRT\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ActiveLearningDisplayOption', ActiveLearningDisplayOptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveLearningDisplayOption')

    def UpdateActiveLearningDisplayOption(self, value, qualifier):

        ActiveLearningDisplayOptionCmdString = 'wDVDRT\r\n'
        self.__UpdateHelper('ActiveLearningDisplayOption', ActiveLearningDisplayOptionCmdString, value, qualifier)

    def __MatchActiveLearningDisplayOption(self, match, tag):

        ValueStateValues = {
            '0': 'Add as a Quadrant',
            '1': 'Overlay',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ActiveLearningDisplayOption', value, None)
        
    def SetActiveLearningEncoderSourceMode(self, value, qualifier):
        
        ValueStateValues = {
            'Internal Capture': '0',
            'HDMI Output Loopback': '1',
            'HDMI Input with PASS-THROUGH': '2',
            'HDMI Input Only': '3'
        }

        if value in ValueStateValues:
            ActiveLearningEncoderSourceModeCmdString = 'wH{}VDRT\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ActiveLearningEncoderSourceMode', ActiveLearningEncoderSourceModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveLearningEncoderSourceMode')

    def UpdateActiveLearningEncoderSourceMode(self, value, qualifier):

        ActiveLearningEncoderSourceModeCmdString = 'wHVDRT\r\n'
        self.__UpdateHelper('ActiveLearningEncoderSourceMode', ActiveLearningEncoderSourceModeCmdString, value, qualifier)

    def __MatchActiveLearningEncoderSourceMode(self, match, tag):

        ValueStateValues = {
            '0': 'Internal Capture',
            '1': 'HDMI Output Loopback',
            '2': 'HDMI Input with PASS-THROUGH',
            '3': 'HDMI Input Only'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ActiveLearningEncoderSourceMode', value, None)

    def SetActiveLearningTie(self, value, qualifier):

        ActionStates = {
            'Create': 'T',
            'Remove': 'R',
        }

        if qualifier['Action'] in ActionStates and qualifier['IP Address/Hostname']:
            ActiveLearningTieCmdString = 'w{}{}VDRT\r\n'.format(ActionStates[qualifier['Action']], qualifier['IP Address/Hostname'])
            self.__SetHelper('ActiveLearningTie', ActiveLearningTieCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveLearningTie')
            
    def SetActiveLearningUsernameCommand(self, value, qualifier):

        name = value
        if name:
            ActiveLearningUsernameCommandCmdString = 'wN{}APPC\r\n'.format(name)
            self.__SetHelper('ActiveLearningUsernameCommand', ActiveLearningUsernameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveLearningUsernameCommand')
            
    def UpdateActiveLearningUsernameStatus(self, value, qualifier):

        ActiveLearningUsernameStatusCmdString = 'wNAPPC\r\n'
        self.__UpdateHelper('ActiveLearningUsernameStatus', ActiveLearningUsernameStatusCmdString, value, qualifier)

    def __MatchActiveLearningUsernameStatus(self, match, tag):

        value = '' if not match.group(1) else match.group(1).decode('unicode_escape') # accounts for Unicode characters (e.g. different languages)
        self.WriteStatus('ActiveLearningUsernameStatus', value, None)

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
            self.all_users_connection_time_directory.scroll_up(1)
            self.all_users_idle_time_directory.scroll_up(1)
        elif value == 'Down':
            self.all_users_name_directory.scroll_down(1)
            self.all_users_number_of_content_shared_directory.scroll_down(1)
            self.all_users_content_sharing_status_directory.scroll_down(1)
            self.all_users_content_type_directory.scroll_down(1)
            self.all_users_connection_time_directory.scroll_down(1)
            self.all_users_idle_time_directory.scroll_down(1)
        elif value == 'Page Up':
            self.all_users_name_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_number_of_content_shared_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_content_sharing_status_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_content_type_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_connection_time_directory.scroll_up(self._NumberOfAllUsers)
            self.all_users_idle_time_directory.scroll_up(self._NumberOfAllUsers)
        elif value == 'Page Down':
            self.all_users_name_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_number_of_content_shared_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_content_sharing_status_directory.scroll_down(self._NumberOfAllUsers)
            self.all_users_content_type_directory.scroll_down(self._NumberOfAllUsers)
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
            AudioMuteCmdString = '{}*{}Z'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '{}Z'.format(qualifier['Output'])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, {'Output': output})

    def SetChannelPresetRecall(self, value, qualifier):

        if 1 <= value <= 999:
            ChannelPresetRecallCmdString = '{0}T'.format(value)
            self.__SetHelper('ChannelPresetRecall', ChannelPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelPresetRecall')

    def UpdateChannelPresetRecall(self, value, qualifier):

        ChannelPresetRecallCmdString = 'T'
        self.__UpdateHelper('ChannelPresetRecall', ChannelPresetRecallCmdString, value, qualifier)

    def __MatchChannelPresetRecall(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('ChannelPresetRecall', value, None)

    def SetChannelPresetRecallStep(self, value, qualifier):

        ValueStateValues = {
            'Next'    : '+',
            'Previous': '-'
        }

        if value in ValueStateValues:
            ChannelPresetRecallStepCmdString = '{0}T'.format(ValueStateValues[value])
            self.__SetHelper('ChannelPresetRecallStep', ChannelPresetRecallStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelPresetRecallStep')
            
    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = 'wE{0}*{1}SUBT\r\n'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionCmdString = 'wE{0}SUBT\r\n'.format(qualifier['Output'])
        self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ClosedCaption', value, {'Output': output})

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

    def UpdateCurrentSourceItem(self, value, qualifier):

        CurrentSourceItemCmdString = 'wU{0}PLYR\r\n'.format(qualifier['Output'])
        self.__UpdateHelper('CurrentSourceItem', CurrentSourceItemCmdString, value, qualifier)

    def __MatchCurrentSourceItem(self, match, tag):

        output = match.group(1).decode()
        value = '' if not match.group(2) else match.group(2).decode()
        self.WriteStatus('CurrentSourceItem', value, {'Output': output})

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
            
    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On' : '1X', 
            'Off' : '0X'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetExpoMode(self, value, qualifier):

        ValueStateValues = {
            'Off' : '0',
            'Lock-Out' : '1',
            'Temporary' : '2'
        }

        if value in ValueStateValues:
            ExpoModeCmdString = 'wP{}SHAR\r\n'.format(ValueStateValues[value])
            self.__SetHelper('ExpoMode', ExpoModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExpoMode')

    def UpdateExpoMode(self, value, qualifier):

        ExpoModeCmdString = 'wPSHAR\r\n'
        self.__UpdateHelper('ExpoMode', ExpoModeCmdString, value, qualifier)

    def __MatchExpoMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Off',
            '1' : 'Lock-Out',
            '2' : 'Temporary'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExpoMode', value, None)

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

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        if value in ValueStateValues:
            HDCPInputAuthorizationCmdString = '\x1bE1*{}HDCP\r\n'.format(ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = '\x1bE1HDCP\r\n'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

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

    def SetHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'Follow Input' : '0', 
            'Always Encrypt' : '1',
            'Follow Input (with continuous DVI trials)': '2',
            'Always Encrypt (with continuous DVI trials)': '3',
            'Disable Authentication': '4'
        }

        if value in ValueStateValues:
            HDCPModeCmdString = '\x1bS{}*{}HDCP\r\n'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('HDCPMode', HDCPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPMode')

    def UpdateHDCPMode(self, value, qualifier):

        HDCPModeCmdString = '\x1bS{}HDCP\r\n'.format(qualifier['Output'])
        self.__UpdateHelper('HDCPMode', HDCPModeCmdString, value, qualifier)

    def __MatchHDCPMode(self, match, tag):

        ValueStateValues = {
            '0' : 'Follow Input', 
            '1' : 'Always Encrypt',
            '2': 'Follow Input (with continuous DVI trials)',
            '3': 'Always Encrypt (with continuous DVI trials)',
            '4': 'Disable Authentication'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPMode', value, {'Output': output})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = '\x1bO{}HDCP\r\n'.format(qualifier['Output'])
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No monitor connected', 
            '1' : 'Monitor connected, not encrypted', 
            '2' : 'Monitor connected, currently encrypted'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, {'Output': output})

    def SetHDMIInputPassThrough(self, value, qualifier):

        ValueStateValues = {
            'Enabled' : '1', 
            'Disabled' : '0'
        }

        if value in ValueStateValues:
            HDMIInputPassThroughCmdString = '{}!'.format(ValueStateValues[value])
            self.__SetHelper('HDMIInputPassThrough', HDMIInputPassThroughCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIInputPassThrough')

    def UpdateHDMIInputPassThrough(self, value, qualifier):

        HDMIInputPassThroughCmdString = '!'
        self.__UpdateHelper('HDMIInputPassThrough', HDMIInputPassThroughCmdString, value, qualifier)

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
            'A' : '1',
            'B' : '2'
        }

        if qualifier['LAN'] in LANStates:
            IPAddressCmdString = 'w{}CISG\r\n'.format(LANStates[qualifier['LAN']])
            self.__UpdateHelper('IPAddress', IPAddressCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateIPAddress')

    def __MatchIPAddress(self, match, tag):

        LANStates = {
            '1' : 'A',
            '2' : 'B'
        }

        qualifier = {'LAN': LANStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('IPAddress', value, qualifier)

    def SetLabelVisibility(self, value, qualifier):

        ValueStateValues = {
            'Show' : '1', 
            'Hide' : '0'
        }
        
        LabelStates = {
            'Hostname' : '1', 
            'IP Address A' : '2', 
            'IP Address B' : '3', 
            'Message Text' : '5', 
            'Code' : '4', 
            'Date/Time' : '7', 
            'Notifications/Messages' : '6'
        }

        if qualifier['Label'] in LabelStates and value in ValueStateValues:
            LabelVisibilityCmdString = 'wV{}*{}OSDL\r\n'.format(LabelStates[qualifier['Label']], ValueStateValues[value])
            self.__SetHelper('LabelVisibility', LabelVisibilityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLabelVisibility')

    def UpdateLabelVisibility(self, value, qualifier):

        LabelStates = {
            'Hostname' : '1', 
            'IP Address A' : '2', 
            'IP Address B' : '3', 
            'Message Text' : '5', 
            'Code' : '4', 
            'Date/Time' : '7', 
            'Notifications/Messages' : '6'
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

        LabelValues = {
            '1' : 'Hostname', 
            '2' : 'IP Address A', 
            '3' : 'IP Address B', 
            '5' : 'Message Text', 
            '4' : 'Code', 
            '7' : 'Date/Time', 
            '6' : 'Notifications/Messages'
        }
        
        qualifier = {'Label': LabelValues[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LabelVisibility', value, qualifier)

    def SetLoopPlay(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            LoopPlayCmdString = 'wR{0}*{1}PLYR\r\n'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('LoopPlay', LoopPlayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoopPlay')

    def UpdateLoopPlay(self, value, qualifier):

        LoopPlayCmdString = 'wR{0}PLYR\r\n'.format(qualifier['Output'])
        self.__UpdateHelper('LoopPlay', LoopPlayCmdString, value, qualifier)

    def __MatchLoopPlay(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LoopPlay', value, {'Output': output})

    def SetPlayback(self, value, qualifier):

        ValueStateValues = {
            'Play'     : 'wS',
            'Pause'    : 'wE',
            'Stop'     : 'wO',
            'Next'     : 'wN',
            'Previous' : 'wP'
        }

        if value in ValueStateValues:
            if value == 'Play':
                PlaybackCmdString = '{0}{1}*1PLYR\r\n'.format(ValueStateValues[value], qualifier['Output'])
            else:
                PlaybackCmdString = '{0}{1}PLYR\r\n'.format(ValueStateValues[value], qualifier['Output'])
            self.__SetHelper('Playback', PlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlayback')

    def UpdatePlayback(self, value, qualifier):

        PlaybackCmdString = 'wY{0}PLYR\r\n'.format(qualifier['Output'])
        self.__UpdateHelper('Playback', PlaybackCmdString, value, qualifier)

    def __MatchPlayback(self, match, tag):

        ValueStateValuesY = {
            '1' : 'Play',
            '2' : 'Pause',
            '0' : 'Stop'
        }

        ValueStateValuesS = {
            '1' : 'Play',
            '0' : 'Pause'
        }
        
        output = match.group(2).decode()
        if match.group(1).decode() == 'Y':
            value = ValueStateValuesY[match.group(3).decode()]
            self.WriteStatus('Playback', value, {'Output': output})
        elif match.group(1).decode() == 'O':
            value = 'Stop'
            self.WriteStatus('Playback', value, {'Output': output})
        elif match.group(1).decode() == 'E':
            value = 'Pause'
            self.WriteStatus('Playback', value, {'Output': output})
        else:
            value = ValueStateValuesS[match.group(3).decode()]
            self.WriteStatus('Playback', value, {'Output': output})

    def UpdatePlayerStatus(self, value, qualifier):

        PlayerStatusCmdString = 'wQSHAR\r\n'
        self.__UpdateHelper('PlayerStatus', PlayerStatusCmdString, value, qualifier)

    def __MatchPlayerStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Standby',
            '2' : 'Connected',
            '3' : 'Expo',
            '4' : 'Expo Standby',
            '5' : 'Sharing'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PlayerStatus', value, None)

    def SetOutgoingActiveLearningTieRemove(self, value, qualifier):

        IPAddressHostname = self.outgoing_active_learning_ties_directory.get_entry(value)
        if IPAddressHostname:
            OutgoingActiveLearningTieRemoveCmdString = 'wR{}VDRT\r\n'.format(IPAddressHostname)
            self.__SetHelper('OutgoingActiveLearningTieRemove', OutgoingActiveLearningTieRemoveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutgoingActiveLearningTieRemove')
            
    def __MatchOutgoingActiveLearningTies(self, match, tag):

        OutgoingActiveLearningTiesList = []
        if match.group(1):
            resultsList = match.group(1).decode().strip().split('\r\n') # ex: ['10.113.113.141*10.113.113.121*1*playing*ok**', '10.113.113.141*10.113.113.77*1*playing*ok**']
            for result in resultsList:
                data = result.split('*')
                if data[0] == self.IPAddressHostname: # only append if outgoing active learning tie
                    OutgoingActiveLearningTiesList.append(data[1])
        self.outgoing_active_learning_ties_directory.reset(OutgoingActiveLearningTiesList)
        self.WriteStatus('CompareOutgoingActiveLearningTies', ', '.join(OutgoingActiveLearningTiesList), None) # convert list to string and write status

    def SetOutgoingActiveLearningTiesNavigation(self, value, qualifier):

        if value == 'Up':
            self.outgoing_active_learning_ties_directory.scroll_up(1)
        elif value == 'Down':
            self.outgoing_active_learning_ties_directory.scroll_down(1)
        elif value == 'Page Up':
            self.outgoing_active_learning_ties_directory.scroll_up(self._NumberOfOutgoingActiveLearningTies)
        elif value == 'Page Down':
            self.outgoing_active_learning_ties_directory.scroll_down(self._NumberOfOutgoingActiveLearningTies)
        else:
            self.Discard('Invalid Command for SetOutgoingActiveLearningTiesNavigation')
            
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
            '4K 3840x2160 (30 Hz)' : '63',
            '4K 3840x2160 (29.97 Hz)' : '62',
            '4K 3840x2160 (25 Hz)' : '61',
            '4K 3840x2160 (24 Hz)' : '60',
            '4K 3840x2160 (23.98 Hz)' : '59',
            '4096x2160 (30 Hz)' : '73',
            '4096x2160 (29.97 Hz)' : '72',
            '4096x2160 (25 Hz)' : '71',
            '4096x2160 (24 Hz)' : '70',
            '4096x2160 (23.98 Hz)' : '69'
        }

        if value in ValueStateValues:
            OutputResolutionCmdString = 'w{}*{}RATE\r\n'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'w{}RATE\r\n'.format(qualifier['Output'])
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
            '63' : '4K 3840x2160 (30 Hz)',
            '62' : '4K 3840x2160 (29.97 Hz)',
            '61' : '4K 3840x2160 (25 Hz)',
            '60' : '4K 3840x2160 (24 Hz)',
            '59' : '4K 3840x2160 (23.98 Hz)',
            '73' : '4096x2160 (30 Hz)',
            '72' : '4096x2160 (29.97 Hz)',
            '71' : '4096x2160 (25 Hz)',
            '70' : '4096x2160 (24 Hz)',
            '69' : '4096x2160 (23.98 Hz)'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputResolution', value, {'Output': output})

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

        self.FileRegex = []
        RefreshFilesCmdString = 'wLF\r'
        self.__SetHelper('RefreshFiles', RefreshFilesCmdString, value, qualifier)
                
    def SetRefreshOutgoingActiveLearningTies(self, value, qualifier):

        RefreshOutgoingActiveLearningTiesCmdString = 'wIVDRT\r\n'
        self.__SetHelper('RefreshOutgoingActiveLearningTies', RefreshOutgoingActiveLearningTiesCmdString, value, qualifier)
        
    def SetRefreshPendingUsers(self, value, qualifier):

        if 'SetRefreshPendingUsers' not in self.ConfiguredSetRefreshCommands:
            self.ConfiguredSetRefreshCommands.append('SetRefreshPendingUsers')

        self.RefreshUserData(None, None)
        
    def SetRefreshSharingUsers(self, value, qualifier):

        if 'SetRefreshSharingUsers' not in self.ConfiguredSetRefreshCommands:
            self.ConfiguredSetRefreshCommands.append('SetRefreshSharingUsers')

        self.RefreshUserData(None, None)

    def __MatchUpdateUsers(self, match, tag):

        if match.group(1):
            ValueStateValues = {
                '1' : 'Enabled',
                '0' : 'Disabled'
            }

            value = ValueStateValues[match.group(2).decode()]
            if match.group(1).decode() == 'Pips': # if HDMI Input Window response
                self.WriteStatus('HDMIInputWindow', value, None)
            else: # if HDMI Input Pass Through response
                self.WriteStatus('HDMIInputPassThrough', value, None)

        self.RefreshUserData( None, None)
        
    def SetRemoveAllActiveLearningTies(self, value, qualifier):

        RemoveAllActiveLearningTiesCmdString = 'wR0VDRT\r\n'
        self.__SetHelper('RemoveAllActiveLearningTies', RemoveAllActiveLearningTiesCmdString, value, qualifier)

    def SetSharingUserNavigation(self, value, qualifier):

        if value == 'Up':
            self.sharing_user_name_directory.scroll_up(1)
            self.sharing_user_number_of_content_shared_directory.scroll_up(1)
            self.sharing_user_content_type_directory.scroll_up(1)
        elif value == 'Down':
            self.sharing_user_name_directory.scroll_down(1)
            self.sharing_user_number_of_content_shared_directory.scroll_down(1)
            self.sharing_user_content_type_directory.scroll_down(1)
        elif value == 'Page Up':
            self.sharing_user_name_directory.scroll_up(self._NumberOfSharingUsers)
            self.sharing_user_number_of_content_shared_directory.scroll_up(self._NumberOfSharingUsers)
            self.sharing_user_content_type_directory.scroll_up(self._NumberOfSharingUsers)
        elif value == 'Page Down':
            self.sharing_user_name_directory.scroll_down(self._NumberOfSharingUsers)
            self.sharing_user_number_of_content_shared_directory.scroll_down(self._NumberOfSharingUsers)
            self.sharing_user_content_type_directory.scroll_down(self._NumberOfSharingUsers)
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

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0', 
            'On with Sync' : '2'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = '{0}*{1}b'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '{}b'.format(qualifier['Output'])
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off', 
            '2' : 'On with Sync'
        }

        output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, {'Output': output})

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
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
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
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
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

class SPIClass(SPInterface, DeviceClass):

    def __init__(self, spd, Model=None):
        SPInterface.__init__(self, spd)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        print('Module: {}'.format(__name__), 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
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