from json import loads, dumps
import urllib.error
import urllib.request
import base64
import extronlib.standard.exml.etree.ElementTree as ET
from datetime import datetime, timedelta
from extronlib.device import ProcessorDevice, UIDevice
from extronlib.ui import Button, Label, Level
from extronlib.system import GetUnverifiedContext


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                  urllib.request.HTTPSHandler(context=self._context))
        urllib.request.install_opener(self.Opener)

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberofRecorders = 5
        self._NumberofScheduleEntries = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'RefreshRecorders': { 'Status': {}},
            'RefreshSchedule': {'Parameters':['Recorder'], 'Status': {}},
            'RefreshScheduleFixed': {'Parameters':['Recorder Name'], 'Status': {}},
            'RemoteRecorder': { 'Status': {}},
            'RecorderNavigation': { 'Status': {}},
            'RemoteRecorder': { 'Status': {}},
            'RemoteRecorderName': {'Parameters':['Recorder'], 'Status': {}},
            'RemoteRecorderRecordingState': {'Parameters':['Recorder'], 'Status': {}},
            'RemoteRecorderRecordingStateFixed': {'Parameters':['Recorder Name'], 'Status': {}},
            'RecordingName': {'Status': {}},
            'RemoteRecorderRecord': {'Parameters':['Recorder', 'Folder ID', 'Duration', 'Webcast'], 'Status': {}},
            'RemoteRecorderRecordFixed': {'Parameters':['Recorder Name', 'Folder ID', 'Duration', 'Webcast'], 'Status': {}},
            'RemoteRecorderStopRecording': {'Parameters':['Recorder'], 'Status': {}},
            'RemoteRecorderStopRecordingFixed': {'Parameters':['Recorder Name'], 'Status': {}},
            'Schedule': {'Parameters':['Recording', 'Selection', 'Recorder'], 'Status': {}},
            'ScheduleFixed': {'Parameters':['Recording', 'Selection', 'Recorder Name'], 'Status': {}},
            'ScheduleNavigation': {'Parameters':['Recorder'], 'Status': {}},
            'ScheduleNavigationFixed': {'Parameters':['Recorder Name'], 'Status': {}},
            'RecordingDuration': {'Parameters':['Recorder'], 'Status': {}},
            'RecordingDurationFixed': {'Parameters':['Recorder Name'], 'Status': {}},
            'ExtendCurrentRecording': {'Parameters':['Recorder'], 'Status': {}},
            'ExtendCurrentRecordingFixed': {'Parameters':['Recorder Name'], 'Status': {}},
            'StartRecordingNow': {'Parameters':['Recorder', 'Recording'], 'Status': {}},
            'StartRecordingNowFixed': {'Parameters':['Recorder Name', 'Recording'], 'Status': {}},
            'RecordabilityStatus': {'Status': {}},
        }

        self.RecorderID = []
        self.ScheduledRecordings = {}
        self.ScheduledRecordingLists = []
        self.SingleList = []
        self.RecordingNames = []
        self.RecordingStates = []
        self.startRecorderList = 1
        self.ScheduleNavigationName = {}
        self.ScheduleNavigationDate = {}
        self.ScheduleNavigationStartTime = {}
        self.ScheduleNavigationDuration = {}     
     
        self.recorder_name_navigation = Directory(self._NumberofRecorders, 'RemoteRecorderName', recorder_id = None, filler='')
        self.recorder_name_navigation.qualifier_name = 'Recorder'
        self.recorder_name_navigation.write_status_function = self.WriteStatus

        self.recorder_state_navigation = Directory(self._NumberofRecorders, 'RemoteRecorderRecordingState', recorder_id = None, filler='N/A')
        self.recorder_state_navigation.qualifier_name = 'Recorder'
        self.recorder_state_navigation.write_status_function = self.WriteStatus

    @property
    def NumberofRecorders(self):
        return self._NumberofRecorders

    @NumberofRecorders.setter
    def NumberofRecorders(self, value):
        self._NumberofRecorders= value

    @property
    def NumberofScheduleEntries(self):
        return self._NumberofScheduleEntries

    @NumberofScheduleEntries.setter
    def NumberofScheduleEntries(self, value):
        self._NumberofScheduleEntries= value

    def UpdateRecordingDurationFixed(self, value, qualifier):
        self.UpdateRecordingDuration(value, qualifier)

    def UpdateRecordingDuration(self, value, qualifier):
        try:
            try:
                recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
                start_position = next(recorder_position_iter)
                rcdrcmpr = (qualifier['Recorder'] - 1) + (start_position[1] - 1)
                rcdrrequest = rcdrcmpr
                recordings = self.ScheduledRecordings[self.RecorderID[rcdrcmpr]]
            except KeyError:
                rcdrcmpr = qualifier['Recorder Name']
                rcdrrequest = rcdrcmpr
                rcdrrequest = self.RecordingNames.index(rcdrrequest)
                recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
            if recordings:
                recordingstate = self.RecordingStates[rcdrrequest]
                if recordingstate == 'Recording':
                    starttime = self.ScheduledRecordingLists[rcdrrequest][0][2]
                    starttime = starttime.split('.')
                    try:
                        starttime = self.pstrptime(starttime[0], '%H:%M:%S.%f')
                    except ValueError:
                        starttime = self.pstrptime(starttime[0], '%H:%M:%S')
                    currenttime = datetime.now()
                    datestr = datetime.now().date()
                    startdatetime = datetime.combine(datestr, starttime.monotonic())
                    elapsedtime = currenttime - startdatetime
                    if elapsedtime.days == 0:
                        minutes = elapsedtime.seconds / 60
                        hours = minutes / 60
                        if isinstance(rcdrcmpr, int):
                            self.WriteStatus('RecordingDuration', '{0:02d}:{1:02d}:{2:02d}'.format(int(hours), int(minutes % 60), int(elapsedtime.seconds % 60)), qualifier)
                        else:
                            self.WriteStatus('RecordingDurationFixed', '{0:02d}:{1:02d}:{2:02d}'.format(int(hours), int(minutes % 60), int(elapsedtime.seconds % 60)), qualifier)
                    else:
                        self.WriteStatus('RecordingDuration', '00:00:00', qualifier)
                else:
                    if isinstance(rcdrcmpr, int):
                        self.WriteStatus('RecordingDuration', '00:00:00', qualifier)
                    else:
                        self.WriteStatus('RecordingDurationFixed', '00:00:00', qualifier)
            else:
                if isinstance(rcdrcmpr, int):
                    self.WriteStatus('RecordingDuration', '00:00:00', qualifier)
                else:
                    self.WriteStatus('RecordingDurationFixed', '00:00:00', qualifier)
        except (IndexError, AttributeError, ValueError) as e:
            if isinstance(rcdrcmpr, int):
                self.WriteStatus('RecordingDuration', '00:00:00', qualifier)
            else:
                self.WriteStatus('RecordingDurationFixed', '00:00:00', qualifier)

    def SetExtendCurrentRecordingFixed(self, value, qualifier):

        self.SetExtendCurrentRecording(value, qualifier)
    def SetExtendCurrentRecording(self, value, qualifier):

        try:
            recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
            start_position = next(recorder_position_iter)
            rcdrrequest = (qualifier['Recorder'] - 1) + (start_position[1] - 1)
            recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
        except KeyError:
            rcdrrequest = qualifier['Recorder Name']
            rcdrrequest = self.RecordingNames.index(rcdrrequest)
            recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
        if recordings:
            SourceCmdString = '/Panopto/PublicAPI/4.2/RemoteRecorderManagement.svc'
            templatesoap ='''
                    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
	                    <s:Body>
		                    <UpdateRecordingTime xmlns="http://tempuri.org/">
			                    <auth xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				                    <a:AuthCode i:nil="true"/>
			                        <a:Password>nill</a:Password>
				                    <a:UserKey>nill</a:UserKey>
			                    </auth>
			                    <sessionId>nill</sessionId>
                                <start>nill</start>
                                <end>nill</end>
		                      </UpdateRecordingTime >
	                       </s:Body>
                        </s:Envelope>     
                     '''

            recordingstate = self.RecordingStates[rcdrrequest]
            if recordingstate == 'Recording':
                starttime = self.ScheduledRecordingLists[rcdrrequest][0][2]
                duration = self.ScheduledRecordingLists[rcdrrequest][0][0]
                tme = datetime.now()
                utctime = datetime.utcnow()
                offset = tme.hour - utctime.hour
                if offset <= -10:
                    offset = offset + 24
                elif offset >=12:
                    offset = offset - 24

                starttme = starttime.split(':')
                starthrs = starttme[0]
                startmin = starttme[1]
                startsec = starttme[2]
                hrs = int(starthrs)
                min = int(startmin)
                dur = int(duration)
                if dur >= 60:
                    hrs = hrs + int(dur/60)
                    hrs = int(hrs)
                    if min + dur%60 > 59:
                        hrs = hrs + 1
                        min = (min + dur%60) % 59
                    else:
                        min = min + dur%60
                else:
                    if (min + dur) > 59:
                        hrs = hrs + 1
                        min = (min + dur) % 59
                    else:
                        min = min + dur

                dur = int(value)

                if dur >= 60:
                    hrs = hrs + int(dur/60)
                    hrs = int(hrs)
                    if min + dur%60 > 59:
                        hrs = hrs + 1
                        min = (min + dur%60) % 59
                else:
                    if (min + dur) > 59:
                        hrs = hrs + 1
                        min = (min + dur) % 59
                    else:
                        min = min + dur

                if '.' in startsec:
                    startsec = startsec.strip('.')
                    startsec = startsec[0]
                if offset < 0:
                    starttime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.000000{6:03d}:00'.format(tme.year, tme.month, tme.day, int(starthrs), int(startmin), int(startsec), offset)
                    stoptime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.000000{6:03d}:00'.format(tme.year, tme.month, tme.day, hrs, min, int(startsec), offset)
                else:
                    starttime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.000000+{6:02d}:00'.format(tme.year, tme.month, tme.day, int(starthrs), int(startmin), int(startsec), offset)
                    stoptime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.000000+{6:02d}:00'.format(tme.year, tme.month, tme.day, hrs, min, int(startsec), offset)
                sendsoap = templatesoap.replace('<sessionId>nill</sessionId>', '<sessionId>{}</sessionId>'.format(recordings[0]))
                sendsoap = sendsoap.replace('<a:Password>nill</a:Password>', '<a:Password>{}</a:Password>'.format(self.devicePassword))
                sendsoap = sendsoap.replace('<a:UserKey>nill</a:UserKey>', '<a:UserKey>{}</a:UserKey>'.format(self.deviceUsername))
                sendsoap = sendsoap.replace('<start>nill</start>', '<start>{}</start>'.format(stoptime))
                sendsoap = sendsoap.replace('<end>nill</end>', '<end>{}</end>'.format(stoptime))
                header = {'Content-Type': 'text/xml; charset=utf-8', 'soapAction': 'http://tempuri.org/IRemoteRecorderManagement/UpdateRecordingTime'}
                res = self.__SetHelper('ExtendCurrentRecording', value, qualifier, SourceCmdString, header, sendsoap)

    def SetStartRecordingNowFixed(self, value, qualifier):

        self.SetStartRecordingNow(value, qualifier)   

    def SetStartRecordingNow(self, value, qualifier):
        try:
            recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
            start_position = next(recorder_position_iter)
            rcdrrequest = (qualifier['Recorder'] - 1) + (start_position[1] - 1)
            recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
        except KeyError:
            rcdrrequest = qualifier['Recorder Name']
            rcdrrequest = self.RecordingNames.index(rcdrrequest)
            recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
        if recordings:
            SourceCmdString = '/Panopto/PublicAPI/4.2/RemoteRecorderManagement.svc'
            templatesoap = '''
                    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
	                    <s:Body>
		                    <UpdateRecordingTime xmlns="http://tempuri.org/">
			                    <auth xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				                    <a:AuthCode i:nil="true"/>
			                        <a:Password>nill</a:Password>
				                    <a:UserKey>nill</a:UserKey>
			                    </auth>
			                    <sessionId>nill</sessionId>
                                <start>nill</start>
                                <end>nill</end>
		                      </UpdateRecordingTime >
	                       </s:Body>
                        </s:Envelope>     
                     '''
            
            recordingstate = self.RecordingStates[rcdrrequest]
            if recordingstate != 'Recording':
                starttime = self.ScheduledRecordingLists[rcdrrequest][qualifier['Recording']-1][2]
                duration = self.ScheduledRecordingLists[rcdrrequest][qualifier['Recording']-1][0]
                tme = datetime.now()
                utctime = datetime.utcnow()
                offset = tme.hour - utctime.hour
                if offset <= -10:
                    offset = offset + 24
                elif offset >=12:
                    offset = offset - 24

                starttme = starttime.split(':')
                starthrs = starttme[0]
                startmin = starttme[1]
                startsec = starttme[2]
                hrs = int(tme.hour)
                min = int(tme.minute)
                dur = int(duration)
                if dur == 60:
                    hrs = hrs + 1
                else:
                    if (min + dur) > 59:
                        hrs = hrs + 1
                        min = (min + dur) % 59
                    else:
                        min = min + dur

                endhours = hrs
                endmins = min

                if '.' in startsec:
                    startsec = startsec.strip('.')
                    startsec = startsec[0]
                if offset < 0:
                    starttime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}{7:03d}:00'.format(tme.year, tme.month, tme.day, tme.hour, tme.minute, tme.second, tme.microsecond, offset)
                    stoptime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}{7:03d}:00'.format(tme.year, tme.month, tme.day, endhours, endmins, tme.second, tme.microsecond, offset)
                else:
                    starttime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}+{7:02d}:00'.format(tme.year, tme.month, tme.day, tme.hour, tme.minute, tme.second, tme.microsecond, offset)
                    stoptime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}+{7:02d}:00'.format(tme.year, tme.month, tme.day, endhours, endmins, tme.second, tme.microsecond, offset)
                sendsoap = templatesoap.replace('<sessionId>nill</sessionId>', '<sessionId>{}</sessionId>'.format(recordings[qualifier['Recording']-1]))
                sendsoap = sendsoap.replace('<a:Password>nill</a:Password>', '<a:Password>{}</a:Password>'.format(self.devicePassword))
                sendsoap = sendsoap.replace('<a:UserKey>nill</a:UserKey>', '<a:UserKey>{}</a:UserKey>'.format(self.deviceUsername))
                sendsoap = sendsoap.replace('<start>nill</start>', '<start>{}</start>'.format(starttime))
                sendsoap = sendsoap.replace('<end>nill</end>', '<end>{}</end>'.format(stoptime))
                header = {'Content-Type': 'text/xml; charset=utf-8', 'soapAction': 'http://tempuri.org/IRemoteRecorderManagement/UpdateRecordingTime'}
                res = self.__SetHelper('StartRecordingNow', value, qualifier, SourceCmdString, header, sendsoap)

    def SetRemoteRecorderStopRecordingFixed(self, value, qualifier):

        self.SetRemoteRecorderStopRecording(value, qualifier)
        
    def SetRemoteRecorderStopRecording(self, value, qualifier):

        try:
            recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
            start_position = next(recorder_position_iter)
            rcdrrequest = (qualifier['Recorder'] - 1) + (start_position[1] - 1)
            recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
        except KeyError:
            rcdrrequest = qualifier['Recorder Name']
            rcdrrequest = self.RecordingNames.index(rcdrrequest)
            recordings = self.ScheduledRecordings[self.RecorderID[rcdrrequest]]
            
        if self.RecorderID[rcdrrequest]:
            SourceCmdString = '/Panopto/PublicAPI/4.2/RemoteRecorderManagement.svc'
            templatesoap = '''
                    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
	                    <s:Body>
		                    <UpdateRecordingTime xmlns="http://tempuri.org/">
			                    <auth xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				                    <a:AuthCode i:nil="true"/>
			                        <a:Password>nill</a:Password>
				                    <a:UserKey>nill</a:UserKey>
			                    </auth>
			                    <sessionId>nill</sessionId>
                                <start>nill</start>
                                <end>nill</end>
		                      </UpdateRecordingTime >
	                       </s:Body>
                        </s:Envelope>     
                     '''
            tme = datetime.now()
            utctime = datetime.utcnow()
            offset = tme.hour - utctime.hour
            if offset <= -10:
                offset = offset + 24
            elif offset >=12:
                offset = offset - 24

            if offset < 0:
                stoptime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}{7:03d}:00'.format(tme.year, tme.month, tme.day, tme.hour, tme.minute, tme.second, tme.microsecond, offset)
            else:
                stoptime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}+{7:02d}:00'.format(tme.year, tme.month, tme.day, tme.hour, tme.minute, tme.second, tme.microsecond, offset)
            sendsoap = templatesoap.replace('<sessionId>nill</sessionId>', '<sessionId>{}</sessionId>'.format(recordings[0]))
            sendsoap = sendsoap.replace('<a:Password>nill</a:Password>', '<a:Password>{}</a:Password>'.format(self.devicePassword))
            sendsoap = sendsoap.replace('<a:UserKey>nill</a:UserKey>', '<a:UserKey>{}</a:UserKey>'.format(self.deviceUsername))
            sendsoap = sendsoap.replace('<start>nill</start>', '<start>{}</start>'.format(stoptime))
            sendsoap = sendsoap.replace('<end>nill</end>', '<end>{}</end>'.format(stoptime))
            header = {'Content-Type': 'text/xml; charset=utf-8', 'soapAction': 'http://tempuri.org/IRemoteRecorderManagement/UpdateRecordingTime'}
            res = self.__SetHelper('RemoteRecorderStopRecording', value, qualifier, SourceCmdString, header, sendsoap)
            self.UpdateRemoteRecorder( None, None)
            
    def SetScheduleNavigationFixed(self, value, qualifier):

        self.SetScheduleNavigation(value, qualifier)
        
    def SetScheduleNavigation(self, value, qualifier):

        try:
            recorder_id = qualifier['Recorder']
        except KeyError:
            recorder_id = qualifier['Recorder Name']

        if value == 'Up':
            self.ScheduleNavigationName[qualifier['Recorder']].scroll_up(1)
            self.ScheduleNavigationDate[qualifier['Recorder']].scroll_up(1)
            self.ScheduleNavigationStartTime[qualifier['Recorder']].scroll_up(1)
            self.ScheduleNavigationDuration[qualifier['Recorder']].scroll_up(1)
        elif value == 'Down':
            self.ScheduleNavigationName[qualifier['Recorder']].scroll_down(1)
            self.ScheduleNavigationDate[qualifier['Recorder']].scroll_down(1)
            self.ScheduleNavigationStartTime[qualifier['Recorder']].scroll_down(1)
            self.ScheduleNavigationDuration[qualifier['Recorder']].scroll_down(1)
        elif value == 'Page Up':
            self.ScheduleNavigationName[qualifier['Recorder']].scroll_up(self._NumberofScheduleEntries)
            self.ScheduleNavigationDate[qualifier['Recorder']].scroll_up(self._NumberofScheduleEntries)
            self.ScheduleNavigationStartTime[qualifier['Recorder']].scroll_up(self._NumberofScheduleEntries)
            self.ScheduleNavigationDuration[qualifier['Recorder']].scroll_up(self._NumberofScheduleEntries)
        elif value == 'Page Down':
            self.ScheduleNavigationName[qualifier['Recorder']].scroll_down(self._NumberofScheduleEntries)
            self.ScheduleNavigationDate[qualifier['Recorder']].scroll_down(self._NumberofScheduleEntries)
            self.ScheduleNavigationStartTime[qualifier['Recorder']].scroll_down(self._NumberofScheduleEntries)
            self.ScheduleNavigationDuration[qualifier['Recorder']].scroll_down(self._NumberofScheduleEntries)
        else:
            self.Discard('Invalid Command for SetScheduleNavigation')
        
    def SetRefreshScheduleFixed(self, value, qualifier):

        self.SetRefreshSchedule(value, qualifier)
            
    def SetRefreshSchedule(self, value, qualifier):

        try:
            recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
            start_position = next(recorder_position_iter)
            rcdrrequest = qualifier['Recorder']
            rcdrrequestindx = (qualifier['Recorder'] - 1) + (start_position[1] - 1)
        except KeyError:
            rcdrrequest = qualifier['Recorder Name']
            rcdrrequestindx = self.RecordingNames.index(rcdrrequest)
        schedulenamelist = []
        scheduledatelist = []
        schedulestarttimelist = []
        scheduledurationlist = []
        for schduledrecordings in self.ScheduledRecordingLists[rcdrrequestindx]:
            schedulenamelist.append(schduledrecordings[1])
            scheduledatelist.append(schduledrecordings[3])
            schedulestarttimelist.append(schduledrecordings[2])
            scheduledurationlist.append(schduledrecordings[0])
        self.ScheduleNavigationName[rcdrrequest].reset(schedulenamelist)
        self.ScheduleNavigationDate[rcdrrequest].reset(scheduledatelist)
        self.ScheduleNavigationStartTime[rcdrrequest].reset(schedulestarttimelist)
        self.ScheduleNavigationDuration[rcdrrequest].reset(scheduledurationlist)
        
    def UpdateRefreshSchedule(self, value, qualifier):

        SourceCmdString = '/Panopto/PublicAPI/4.2/SessionManagement.svc'
        try:
            recorder_id = qualifier['Recorder']
            recorder_name = self.RecordingNames[recorder_id - 1]
            if recorder_id:
                if recorder_id not in self.ScheduleNavigationName:
                    self.ScheduleNavigationName[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Name')
                    self.ScheduleNavigationName[recorder_id].qualifier_name = 'Recording'
                    self.ScheduleNavigationName[recorder_id].write_status_function = self.WriteStatus
                    self.ScheduleNavigationDate[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Date')
                    self.ScheduleNavigationDate[recorder_id].qualifier_name = 'Recording'
                    self.ScheduleNavigationDate[recorder_id].write_status_function = self.WriteStatus
                    self.ScheduleNavigationStartTime[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Start Time')
                    self.ScheduleNavigationStartTime[recorder_id].qualifier_name = 'Recording'
                    self.ScheduleNavigationStartTime[recorder_id].write_status_function = self.WriteStatus
                    self.ScheduleNavigationDuration[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Duration')
                    self.ScheduleNavigationDuration[recorder_id].qualifier_name = 'Recording'
                    self.ScheduleNavigationDuration[recorder_id].write_status_function = self.WriteStatus

                    self.ScheduleNavigationName[recorder_name] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_name, filler = '', schtype = 'Name')
                    self.ScheduleNavigationName[recorder_name].qualifier_name = 'Recording'
                    self.ScheduleNavigationName[recorder_name].write_status_function = self.WriteStatus
                    self.ScheduleNavigationDate[recorder_name] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_name, filler = '', schtype = 'Date')
                    self.ScheduleNavigationDate[recorder_name].qualifier_name = 'Recording'
                    self.ScheduleNavigationDate[recorder_name].write_status_function = self.WriteStatus
                    self.ScheduleNavigationStartTime[recorder_name] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_name, filler = '', schtype = 'Start Time')
                    self.ScheduleNavigationStartTime[recorder_name].qualifier_name = 'Recording'
                    self.ScheduleNavigationStartTime[recorder_name].write_status_function = self.WriteStatus
                    self.ScheduleNavigationDuration[recorder_name] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_name, filler = '', schtype = 'Duration')
                    self.ScheduleNavigationDuration[recorder_name].qualifier_name = 'Recording'
                    self.ScheduleNavigationDuration[recorder_name].write_status_function = self.WriteStatus
            recordings = self.ScheduledRecordings[self.RecorderID[recorder_id - 1]]
            rcdstr = ''
            for recording in recordings:
                rcdstr = rcdstr + ('<j:guid>{}</j:guid>'.format(recording))
            templatesoap = '''
                    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:j="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
	                    <s:Body>
		                    <GetSessionsById xmlns="http://tempuri.org/">
			                    <auth xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				                    <a:AuthCode i:nil="true"/>
			                        <a:Password>nill</a:Password>
				                    <a:UserKey>nill</a:UserKey>
			                    </auth>
			                    <sessionIds>nill</sessionIds>
		                      </GetSessionsById>
	                       </s:Body>
                        </s:Envelope>     
                     '''
            sendsoap = templatesoap.replace('<sessionIds>nill</sessionIds>', '<sessionIds>{}</sessionIds>'.format(rcdstr))
            sendsoap = sendsoap.replace('<a:Password>nill</a:Password>', '<a:Password>{}</a:Password>'.format(self.devicePassword))
            sendsoap = sendsoap.replace('<a:UserKey>nill</a:UserKey>', '<a:UserKey>{}</a:UserKey>'.format(self.deviceUsername))
            header = {'Content-Type': 'text/xml; charset=utf-8', 'soapAction': 'http://tempuri.org/ISessionManagement/GetSessionsById'}
            res = self.__UpdateHelper('RefreshSchedule', value, qualifier, SourceCmdString, header, sendsoap)
            if res:
                try:
                    root = ET.fromstring(res)
                    tme = datetime.now()
                    utctime = datetime.utcnow()
                    offset = tme.hour - utctime.hour
                    if offset <= -10:
                        offset = offset + 24
                    elif offset >=12:
                        offset = offset - 24
                    result = root.findall('*//{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}Session')
                    if result:
                        for elmt in result:
                            self.SingleList = []
                            for elm in elmt.getiterator():
                                if elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}Duration':
                                    try:
                                        duration = int(elm.text)/60
                                        duration = int(duration)
                                    except ValueError:
                                        duration = float(elm.text)/60
                                        duration = int(duration)
                                    self.SingleList.append(duration)
                                elif elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}StartTime':
                                    tme = elm.text
                                    dte = tme.split('T')
                                    date = dte[0]

                                    tme = dte[1]
                                    tme = tme[:-1]
                                    try:
                                        tme = tme.split('.')
                                        tme = tme[0].split(':')
                                    except Exception as e:
                                        tme = tme.split(':')
                                    hrs = int(tme[0])
                                    if hrs + offset < 0:
                                        newdate = date.split('-')
                                        dtobject = datetime.now()
                                        dtobject = dtobject.replace(year = int(newdate[0]), month = int(newdate[1]), day = int(newdate[2]))
                                        dtobject = dtobject - timedelta(days=1)
                                        date = '{0:04d}-{1:02d}-{2:02d}'.format(dtobject.year, dtobject.month, dtobject.day)
                                        newtme = hrs + offset + 24
                                    elif hrs + offset >= 24:
                                        newdate = date.split('-')
                                        dtobject = datetime.now()
                                        dtobject = dtobject.replace(year = int(newdate[0]), month = int(newdate[1]), day = int(newdate[2]))
                                        dtobject = dtobject + timedelta(days=1)
                                        date = '{0:04d}-{1:02d}-{2:02d}'.format(dtobject.year, dtobject.month, dtobject.day)
                                        newtme = hrs + offset - 24
                                    else:
                                        newtme = hrs + offset
                                    tmestr = '{0:02d}:{1}:{2}'.format(newtme, tme[1], tme[2])
                                    self.SingleList.append(tmestr)
                                    self.SingleList.append(date)
                                elif elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}Name':
                                    self.SingleList.append(elm.text)
                            self.ScheduledRecordingLists[recorder_id - 1].append(self.SingleList)
                except (KeyError, IndexError) as e:
                    self.ScheduleNavigationName[recorder_name].reset([''])
                    self.ScheduleNavigationDate[recorder_name].reset([''])
                    self.ScheduleNavigationStartTime[recorder_name].reset([''])
                    self.ScheduleNavigationDuration[recorder_name].reset([''])
            else:
                self.ScheduleNavigationName[recorder_name].reset([''])
                self.ScheduleNavigationDate[recorder_name].reset([''])
                self.ScheduleNavigationStartTime[recorder_name].reset([''])
                self.ScheduleNavigationDuration[recorder_name].reset([''])
        except (KeyError, IndexError):
            self.ScheduleNavigationName[recorder_name].reset([''])
            self.ScheduleNavigationDate[recorder_name].reset([''])
            self.ScheduleNavigationStartTime[recorder_name].reset([''])
            self.ScheduleNavigationDuration[recorder_name].reset([''])

    def SetRecorderNavigation(self, value, qualifier):

        if value == 'Up':
            self.recorder_name_navigation.scroll_up(1)
            self.recorder_state_navigation.scroll_up(1)
        elif value == 'Down':
            self.recorder_name_navigation.scroll_down(1)
            self.recorder_state_navigation.scroll_down(1)
        elif value == 'Page Up':
            self.recorder_name_navigation.scroll_up(self._NumberofRecorders)
            self.recorder_state_navigation.scroll_up(self._NumberofRecorders)
        elif value == 'Page Down':
            self.recorder_name_navigation.scroll_down(self._NumberofRecorders)
            self.recorder_state_navigation.scroll_down(self._NumberofRecorders)
        else:
            self.Discard('Invalid Command for SetRecorderNavigation')

    def SetRefreshRecorders(self, value, qualifier):

        try:
            self.recorder_name_navigation.reset(self.RecordingNames)
            self.recorder_state_navigation.reset(self.RecordingStates)
            for key, items in enumerate(self.RecordingNames):
                self.WriteStatus('RemoteRecorderRecordingStateFixed', self.RecordingStates[key], {'Recorder Name': items})
        except IndexError:
            self.Discard('Inappropriate Command for SetRefreshRecorders')
            
    def UpdateRemoteRecorder(self, value, qualifier):

        SourceCmdString = '/Panopto/PublicAPI/4.2/RemoteRecorderManagement.svc'
        soap = '''
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <ListRecorders xmlns="http://tempuri.org/">
                        <auth xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                            <a:AuthCode i:nil="true"/>
                            <a:Password>nill</a:Password>
                            <a:UserKey>nill</a:UserKey>
                        </auth>
                        <pagination xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                            <a:PageNumber>0</a:PageNumber>
                        </pagination>
                        <sortBy>Name</sortBy>
                    </ListRecorders>
                </s:Body>
            </s:Envelope>
        '''
        sendsoap = soap.replace('<a:Password>nill</a:Password>', '<a:Password>{}</a:Password>'.format(self.devicePassword))
        sendsoap = sendsoap.replace('<a:UserKey>nill</a:UserKey>', '<a:UserKey>{}</a:UserKey>'.format(self.deviceUsername))
        header = {'Content-Type': 'text/xml; charset=utf-8', 'soapAction': 'http://tempuri.org/IRemoteRecorderManagement/ListRecorders'}

        res = self.__UpdateHelper('RemoteRecorder', value, qualifier, SourceCmdString, header, sendsoap)
        if res:
            try:
                root = ET.fromstring(res)
                result = root.findall('*//{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}RemoteRecorder')
                self.RecorderID = []
                self.ScheduledRecordings = {}
                self.RecordingNames = []
                self.RecordingStates = []
                for index, items in enumerate(self.ScheduledRecordingLists):
                    self.ScheduledRecordingLists[index] = []
                for elmt in result:
                    for elm in elmt.getiterator():
                        if elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}Id':
                            self.RecorderID.append(elm.text)
                            self.ScheduledRecordings[elm.text] = {}
                            Recorder = elm.text
                        if elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}Name':
                            self.RecordingNames.append(elm.text)
                        if elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}State':
                            self.RecordingStates.append(elm.text)                           
                        if elm.tag == '{http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V42.Soap}ScheduledRecordings':
                            rcd = []
                            for elm in list(elm):
                                if elm.tag == '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}guid':
                                    rcd.append(elm.text)
                            self.ScheduledRecordings[Recorder] = rcd
                            if self.ScheduledRecordings[Recorder]:
                                self.UpdateRefreshSchedule( None, {'Recorder': len(self.RecordingNames) - 1})
                            else:
                                try:
                                    self.ScheduledRecordingLists[len(self.RecordingNames) - 1] = []
                                except Exception as e:
                                    self.ScheduledRecordingLists.append([])
                                try:
                                    recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
                                    start_position = next(recorder_position_iter)
                                    self.ScheduleNavigationName[len(self.RecordingNames) - (start_position[1] - 1)].reset([''])
                                    self.ScheduleNavigationDate[len(self.RecordingNames) - (start_position[1] - 1)].reset([''])
                                    self.ScheduleNavigationStartTime[len(self.RecordingNames) - (start_position[1] - 1)].reset([''])
                                    self.ScheduleNavigationDuration[len(self.RecordingNames) - (start_position[1] - 1)].reset([''])
                                except Exception as e:
                                    recorder_id = len(self.RecordingNames)
                                    if recorder_id:
                                        if recorder_id not in self.ScheduleNavigationName:
                                            self.ScheduleNavigationName[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Name')
                                            self.ScheduleNavigationName[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationName[recorder_id].write_status_function = self.WriteStatus
                                            self.ScheduleNavigationDate[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Date')
                                            self.ScheduleNavigationDate[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationDate[recorder_id].write_status_function = self.WriteStatus
                                            self.ScheduleNavigationStartTime[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Start Time')
                                            self.ScheduleNavigationStartTime[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationStartTime[recorder_id].write_status_function = self.WriteStatus
                                            self.ScheduleNavigationDuration[recorder_id] =  Directory(self._NumberofScheduleEntries, 'Schedule', recorder_id, filler = '', schtype = 'Duration')
                                            self.ScheduleNavigationDuration[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationDuration[recorder_id].write_status_function = self.WriteStatus
                                try:
                                    self.ScheduleNavigationName[self.RecordingNames[len(self.RecordingNames) - 1]].reset([''])
                                    self.ScheduleNavigationDate[self.RecordingNames[len(self.RecordingNames) - 1]].reset([''])
                                    self.ScheduleNavigationStartTime[self.RecordingNames[len(self.RecordingNames) - 1]].reset([''])
                                    self.ScheduleNavigationDuration[self.RecordingNames[len(self.RecordingNames) - 1]].reset([''])
                                except Exception as e:
                                    recorder_id = self.RecordingNames[len(self.RecordingNames) - 1]
                                    if recorder_id:
                                        if recorder_id not in self.ScheduleNavigationName:
                                            self.ScheduleNavigationName[recorder_id] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_id, filler = '', schtype = 'Name')
                                            self.ScheduleNavigationName[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationName[recorder_id].write_status_function = self.WriteStatus
                                            self.ScheduleNavigationDate[recorder_id] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_id, filler = '', schtype = 'Date')
                                            self.ScheduleNavigationDate[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationDate[recorder_id].write_status_function = self.WriteStatus
                                            self.ScheduleNavigationStartTime[recorder_id] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_id, filler = '', schtype = 'Start Time')
                                            self.ScheduleNavigationStartTime[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationStartTime[recorder_id].write_status_function = self.WriteStatus
                                            self.ScheduleNavigationDuration[recorder_id] =  Directory(self._NumberofScheduleEntries, 'ScheduleFixed', recorder_id, filler = '', schtype = 'Duration')
                                            self.ScheduleNavigationDuration[recorder_id].qualifier_name = 'Recording'
                                            self.ScheduleNavigationDuration[recorder_id].write_status_function = self.WriteStatus    
                for i in range(start_position[1], len(self.RecordingNames) - 1):                    
                    self.WriteStatus('RemoteRecorderRecordingStateFixed', self.RecordingStates[i-1], {'Recorder Name': self.RecordingNames[i-1]})
                self.recorder_state_navigation.refresh(self.RecordingStates)
                
            except (KeyError, IndexError) as e: 
                self.Error(['Source: Invalid/unexpected response'])
                self.RecorderID = []
                self.ScheduledRecordings = {}
                self.RecordingNames = []
                self.RecordingStates = []
        else:
            self.RecorderID = []
            self.ScheduledRecordings = {}
        
    def SetRemoteRecorderRecordFixed(self, value, qualifier):

        self.SetRemoteRecorderRecord(value, qualifier)
        
    def SetRemoteRecorderRecord(self, value, qualifier):
        
        duration = {
            '15'  : 15, 
            '30' : 30,
            '45'  : 45,
            '60' : 60,
        }

        webcaststate = {
            'On': 'true',
            'Off': 'false'
        }
        try:
            try:
                recorder_position_iter = self.recorder_name_navigation.get_displayed_entries()
                start_position = next(recorder_position_iter)
                rcdrrequest = (qualifier['Recorder'] - 1) + (start_position[1] - 1)
            except KeyError:
                rcdrrequest = qualifier['Recorder Name']
                rcdrrequest = self.RecordingNames.index(rcdrrequest)
                RecorderName = qualifier['Recorder Name']

            dur = duration[qualifier['Duration']]
            tme = datetime.now()
            utctime = datetime.utcnow()
            offset = tme.hour - utctime.hour
            if offset <= -10:
                offset = offset + 24
            elif offset >=12:
                offset = offset - 24
            hrs = tme.hour
            mins = tme.minute
            
            # Check if the upcoming scheduled recording time is less than 15 minutes to determine recordability
            upcomingstartime = self.ReadStatus('ScheduleFixed', {'Recorder Name': RecorderName,'Recording':1,'Selection':'Start Time'})
            if hrs-int(upcomingstartime[0:2])==0 and mins-int(upcomingstartime[3:5])<15:
                self.WriteStatus('RecordabilityStatus', 'False', None)
            else:
                self.WriteStatus('RecordabilityStatus', 'True', None)

            if dur == 60:
                hrs = hrs + 1
            else:
                if (mins + dur) > 59:
                    hrs = hrs + 1
                    mins = (mins + dur) % 59
                else:
                    mins = mins + dur
            if offset < 0:
                endtime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}{7:03d}:00'.format(tme.year, tme.month, tme.day, hrs, mins, tme.second, tme.microsecond, offset)
                starttime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}{7:03d}:00'.format(tme.year, tme.month, tme.day, tme.hour, tme.minute, tme.second, tme.microsecond, offset)
            else:
                endtime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}+{7:02d}:00'.format(tme.year, tme.month, tme.day, hrs, mins, tme.second, tme.microsecond, offset)
                starttime = '{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:02d}.{6}+{7:02d}:00'.format(tme.year, tme.month, tme.day, tme.hour, tme.minute, tme.second, tme.microsecond, offset)

            SourceCmdString = '/Panopto/PublicAPI/4.2/RemoteRecorderManagement.svc'
            templatesoap = '''
                <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
	                <s:Body>
		                <ScheduleRecording xmlns="http://tempuri.org/">
			                <auth xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				                <a:AuthCode i:nil="true"/>
				                <a:Password>nill</a:Password>
				                <a:UserKey>nill</a:UserKey>
			                </auth>
			                <name>nill</name>
			                <folderId>nill</folderId>
			                <isBroadcast>nill</isBroadcast>
			                <start>nill</start>
			                <end>nill</end>
			                <recorderSettings xmlns:a="http://schemas.datacontract.org/2004/07/Panopto.Server.Services.PublicAPI.V40" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
				                <a:RecorderSettings>
					            <a:RecorderId>nill</a:RecorderId>
					            <a:SuppressPrimary>false</a:SuppressPrimary>
					            <a:SuppressSecondary>false</a:SuppressSecondary>
				            </a:RecorderSettings>
			                </recorderSettings>
		                </ScheduleRecording>
	                </s:Body>
                </s:Envelope>            
            '''

            sendsoap = templatesoap.replace('<a:RecorderId>nill</a:RecorderId>', '<a:RecorderId>{}</a:RecorderId>'.format(self.RecorderID[rcdrrequest]))
            sendsoap = sendsoap.replace('<a:Password>nill</a:Password>', '<a:Password>{}</a:Password>'.format(self.devicePassword))
            sendsoap = sendsoap.replace('<a:UserKey>nill</a:UserKey>', '<a:UserKey>{}</a:UserKey>'.format(self.deviceUsername))
            sendsoap = sendsoap.replace('<name>nill</name>', '<name>{}</name>'.format(self.ReadStatus('RecordingName', None)))
            sendsoap = sendsoap.replace('<folderId>nill</folderId>', '<folderId>{}</folderId>'.format(qualifier['Folder ID']))
            sendsoap = sendsoap.replace('<isBroadcast>nill</isBroadcast>', '<isBroadcast>{}</isBroadcast>'.format(webcaststate[qualifier['Webcast']]))
            sendsoap = sendsoap.replace('<start>nill</start>', '<start>{}</start>'.format(starttime))
            sendsoap = sendsoap.replace('<end>nill</end>', '<end>{}</end>'.format(endtime))
            header = {'Content-Type': 'text/xml; charset=utf-8', 'soapAction': 'http://tempuri.org/IRemoteRecorderManagement/ScheduleRecording'}
            self.__SetHelper('RemoteRecorderRecord', value, qualifier, SourceCmdString, header, sendsoap)
        except (KeyError, IndexError, ValueError):
            self.Discard('Inappropriate Command for SetRemoteRecorderRecord')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, resource, header, soap, data = None):
        self.Debug = True
        rootURL = self.RootURL.replace('http', 'https') if self.DefaultPort == 443 else self.RootURL
        url = '{0}{1}'.format(rootURL.rstrip('/'), resource)
        my_request = urllib.request.Request(url, headers=header)
        
        try:
            res = self.Opener.open(my_request, soap.encode('utf-8'))
        except urllib.error.HTTPError as err: 
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: 
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: 
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)            
        return res

    def __UpdateHelper(self, command, value, qualifier, resource, header, soap, data=None):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        rootURL = self.RootURL.replace('http', 'https') if self.DefaultPort == 443 else self.RootURL
        
        url = '{0}{1}'.format(rootURL.rstrip('/'), resource)
        
        my_request = urllib.request.Request(url, headers=header) 


        try:
            res = self.Opener.open(my_request, soap.encode('utf-8'))
        except urllib.error.HTTPError as err: 
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
            
        except urllib.error.URLError as err: 
            self.Error(['{0} {1}'.format(command, err.reason)])            
            res = ''
        except Exception as err:          
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
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

        self.ScheduledRecordingLists = []
        self.SingleList = []
        self.RecordingNames = []
        self.RecordingStates = []
        self.startRecorderList = 1

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


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
                   
    def pstrptime(self, data_string, format="%a %b %d %H:%M:%S %Y"):
        """Return a 2-tuple consisting of a time struct and an int containing
        the number of microseconds based on the input string and the
        format string."""

        for index, arg in enumerate([data_string, format]):
            if not isinstance(arg, str):
                msg = "strptime() argument {} must be str, not {}"
                raise TypeError(msg.format(index, type(arg)))
    
        global _TimeRE_cache, _regex_cache
        #with _cache_lock:
    
        if _getlang() != _TimeRE_cache.locale_time.lang:
            _TimeRE_cache = TimeRE()
            _regex_cache.clear()
        if len(_regex_cache) > _CACHE_MAX_SIZE:
            _regex_cache.clear()
        locale_time = _TimeRE_cache.locale_time
        format_regex = _regex_cache.get(format)
        if not format_regex:
            try:
                format_regex = _TimeRE_cache.compile(format)
            # KeyError raised when a bad format is found; can be specified as
            # \\, in which case it was a stray % but with a space after it
            except KeyError as err:
                bad_directive = err.args[0]
                if bad_directive == "\\":
                    bad_directive = "%"
                del err
                raise ValueError("'%s' is a bad directive in format '%s'" %
                                    (bad_directive, format))
            # IndexError only occurs when the format string is "%"
            except IndexError:
                raise ValueError("stray %% in format '%s'" % format)
            _regex_cache[format] = format_regex
        found = format_regex.match(data_string)
        if not found:
            raise ValueError("time data %r does not match format %r" %
                             (data_string, format))
        if len(data_string) != found.end():
            raise ValueError("unconverted data remains: %s" %
                              data_string[found.end():])
    
        year = None
        month = day = 1
        hour = minute = second = fraction = 0
        tz = -1
        tzoffset = None
        # Default to -1 to signify that values not known; not critical to have,
        # though
        week_of_year = -1
        week_of_year_start = -1
        # weekday and julian defaulted to -1 so as to signal need to calculate
        # values
        weekday = julian = -1
        found_dict = found.groupdict()
        for group_key in found_dict.keys():
            # Directives not explicitly handled below:
            #   c, x, X
            #      handled by making out of other directives
            #   U, W
            #      worthless without day of the week
            if group_key == 'y':
                year = int(found_dict['y'])
                # Open Group specification for strptime() states that a %y
                #value in the range of [00, 68] is in the century 2000, while
                #[69,99] is in the century 1900
                if year <= 68:
                    year += 2000
                else:
                    year += 1900
            elif group_key == 'Y':
                year = int(found_dict['Y'])
            elif group_key == 'm':
                month = int(found_dict['m'])
            elif group_key == 'B':
                month = locale_time.f_month.index(found_dict['B'].lower())
            elif group_key == 'b':
                month = locale_time.a_month.index(found_dict['b'].lower())
            elif group_key == 'd':
                day = int(found_dict['d'])
            elif group_key == 'H':
                hour = int(found_dict['H'])
            elif group_key == 'I':
                hour = int(found_dict['I'])
                ampm = found_dict.get('p', '').lower()
                # If there was no AM/PM indicator, we'll treat this like AM
                if ampm in ('', locale_time.am_pm[0]):
                    # We're in AM so the hour is correct unless we're
                    # looking at 12 midnight.
                    # 12 midnight == 12 AM == hour 0
                    if hour == 12:
                        hour = 0
                elif ampm == locale_time.am_pm[1]:
                    # We're in PM so we need to add 12 to the hour unless
                    # we're looking at 12 noon.
                    # 12 noon == 12 PM == hour 12
                    if hour != 12:
                        hour += 12
            elif group_key == 'M':
                minute = int(found_dict['M'])
            elif group_key == 'S':
                second = int(found_dict['S'])
            elif group_key == 'f':
                s = found_dict['f']
                # Pad to always return microseconds.
                s += "0" * (6 - len(s))
                fraction = int(s)
            elif group_key == 'A':
                weekday = locale_time.f_weekday.index(found_dict['A'].lower())
            elif group_key == 'a':
                weekday = locale_time.a_weekday.index(found_dict['a'].lower())
            elif group_key == 'w':
                weekday = int(found_dict['w'])
                if weekday == 0:
                    weekday = 6
                else:
                    weekday -= 1
            elif group_key == 'j':
                julian = int(found_dict['j'])
            elif group_key in ('U', 'W'):
                week_of_year = int(found_dict[group_key])
                if group_key == 'U':
                    # U starts week on Sunday.
                    week_of_year_start = 6
                else:
                    # W starts week on Monday.
                    week_of_year_start = 0
            elif group_key == 'z':
                z = found_dict['z']
                tzoffset = int(z[1:3]) * 60 + int(z[3:5])
                if z.startswith("-"):
                    tzoffset = -tzoffset
            elif group_key == 'Z':
                # Since -1 is default value only need to worry about setting tz if
                # it can be something other than -1.
                found_zone = found_dict['Z'].lower()
                for value, tz_values in enumerate(locale_time.timezone):
                    if found_zone in tz_values:
                        # Deal with bad locale setup where timezone names are the
                        # same and yet time.daylight is true; too ambiguous to
                        # be able to tell what timezone has daylight savings
                        if (time.tzname[0] == time.tzname[1] and
                           time.daylight and found_zone not in ("utc", "gmt")):
                            break
                        else:
                            tz = value
                            break
        leap_year_fix = False
        if year is None and month == 2 and day == 29:
            year = 1904  # 1904 is first leap year of 20th century
            leap_year_fix = True
        elif year is None:
            year = 1900
        # If we know the week of the year and what day of that week, we can figure
        # out the Julian day of the year.
        if julian == -1 and week_of_year != -1 and weekday != -1:
            week_starts_Mon = True if week_of_year_start == 0 else False
            julian = _calc_julian_from_U_or_W(year, week_of_year, weekday,
                                                week_starts_Mon)
        # Cannot pre-calculate datetime_date() since can change in Julian
        # calculation and thus could have different value for the day of the week
        # calculation.
        if julian == -1:
            # Need to add 1 to result since first day of the year is 1, not 0.
            julian = datetime_date(year, month, day).toordinal() - \
                      datetime_date(year, 1, 1).toordinal() + 1
        else:  # Assume that if they bothered to include Julian day it will
               # be accurate.
            datetime_result = datetime_date.fromordinal((julian - 1) + datetime_date(year, 1, 1).toordinal())
            year = datetime_result.year
            month = datetime_result.month
            day = datetime_result.day
        if weekday == -1:
            weekday = datetime_date(year, month, day).weekday()
        # Add timezone info
        tzname = found_dict.get("Z")
        if tzoffset is not None:
            gmtoff = tzoffset * 60
        else:
            gmtoff = None
    
        if leap_year_fix:
            # the caller didn't supply a year but asked for Feb 29th. We couldn't
            # use the default of 1900 for computations. We set it back to ensure
            # that February 29th is smaller than March 1st.
            year = 1900
    
        return (year, month, day,
                hour, minute, second,
                weekday, julian, tz, tzname, gmtoff), fraction

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='On'):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
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
    def __init__(self, display_count, write_function_name, recorder_id = None, filler=None, schtype=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Recording'
        self._qualifier_type = 'Number'
        self._write_function_name = write_function_name 
        self.recorder_id = recorder_id
        self.schtype = schtype
        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
        self.first_filler = True
        
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
            if self.recorder_id:
                if isinstance(self.recorder_id, int): 
                    self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value, 'Recorder': self.recorder_id, 'Selection': self.schtype})
                else:
                    self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name : position_value, 'Recorder Name': self.recorder_id, 'Selection': self.schtype})
            else:
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

    @UseAutoUpdate
    def refresh(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = self._start_index
        
    