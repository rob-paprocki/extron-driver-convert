from extronlib.system import GetUnverifiedContext
from extronlib.system import Wait, ProgramLog
from datetime import timedelta, timezone
import base64
import extronlib.standard.exml.etree.ElementTree as ET
import urllib.error
import urllib.request

import time
from datetime import datetime, timedelta, timezone

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.port = port

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        if self.port in [443, 8443]:  # HTTPS
            self.RootURL = 'https://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(),
                                                      urllib.request.HTTPSHandler(context=self._context))
        else:  # HTTP
            self.RootURL = 'http://{0}:{1}/'.format(ipAddress, self.port)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        urllib.request.install_opener(self.Opener)
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self._TimeFormat = '%H:%M:%S %Z'
        self._DateFormat = '%Y-%m-%d'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioPeakLevel': {'Parameters': ['Channel'], 'Status': {}},
            'CaptureControl': {'Status': {}},
            'CurrentCaptureStatus': {'Parameters': ['Status Tag'], 'Status': {}},
            'DeviceLocation': {'Status': {}},
            'DeviceState': {'Status': {}},
            'ExtendCapture': {'Parameters': ['Duration'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Channel'], 'Status': {}},
            'NewCapture': {'Parameters': ['Duration', 'Title', 'Profile'], 'Status': {}},
            'NextCaptureStatus': {'Parameters': ['Status Tag'], 'Status': {}},
            'WallClock': {'Parameters': ['Status'], 'Status': {}},
        }

    @property
    def TimeFormat(self):
        return self._TimeFormat

    @TimeFormat.setter
    def TimeFormat(self, value):
        self._TimeFormat = value

    @property
    def DateFormat(self):
        return self._DateFormat

    @DateFormat.setter
    def DateFormat(self, value):
        self._DateFormat = value

    def SetCaptureControl(self, value, qualifier):
        ValueStateValues = {
            'Start/Resume': 'record',
            'Stop': 'stop',
            'Pause': 'pause'
        }

        if value in ValueStateValues:
            uri = '/capture/{}'.format(ValueStateValues[value])
            self.__SetHelper('CaptureControl', value, qualifier, uri)
        else:
            self.Discard('Invalid Command for SetCaptureControl')

    def UpdateCurrentCaptureStatus(self, value, qualifier):
        uri = '/status/current_capture'
        res = self.__UpdateHelper('CurrentCaptureStatus', None, qualifier, uri)
        if res:
            try:
                self.ParseMessage(res, 'Current', 'CurrentCaptureStatus')
            except:
                self.Error(['Current Capture Status: Invalid/unexpected response'])

    def UpdateDeviceLocation(self, value, qualifier):
        uri = '/status/system'
        res = self.__UpdateHelper('DeviceLocation', None, qualifier, uri)
        if res:
            try:
                root = ET.fromstring(res)
                try:
                    CurrentDateTime = get_dt_from_str(root.findall(".//wall-clock-time")[0].text.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    CurrentDateTimeTZ = self.UTCtoLocal(CurrentDateTime)
                    CurrentTime = CurrentDateTimeTZ.strftime(self.TimeFormat)
                    if '-' in CurrentTime:
                        CurrentTime = CurrentTime.replace('-', '+')
                    elif '+' in CurrentTime:
                        CurrentTime = CurrentTime.replace('+', '-')
                    CurrentDate = CurrentDateTimeTZ.strftime(self.DateFormat)
                except IndexError:
                    self.Error(['Cannot find wall-clock-time in Response'])
                    CurrentTime = ''
                    CurrentDate = ''
                self.WriteStatus('WallClock', CurrentTime, {'Status': 'Time'})
                self.WriteStatus('WallClock', CurrentDate, {'Status': 'Date'})
                try:
                    value = root.findall(".//location")[0].text
                except IndexError:
                    self.Error(['Cannot find location in Response'])
                    value = ''
                self.WriteStatus('DeviceLocation', value, None)
            except:
                self.Error(['Device Location: Invalid/unexpected response'])

    def UpdateDeviceState(self, value, qualifier):
        ValueStateValues = {
            'active': 'Active',
            'inactive': 'Inactive',
            'paused': 'Paused'
        }

        uri = '/status/monitoring'
        res = self.__UpdateHelper('DeviceState', None, qualifier, uri)
        if res:
            try:
                root = ET.fromstring(res)

                try:
                    state = root.findall(".//state")[0].text
                    value = ValueStateValues.get(state, 'Inactive')
                    self.WriteStatus('DeviceState', value, qualifier)
                except:
                    self.WriteStatus('DeviceState', 'Inactive', qualifier)

                try:
                    ValueStateValues = {
                        'true':     'Active',
                        'false':    'Not Active'
                    }
                    sources = root.find('sources').findall('source')
                    values = []
                    for source in sources:
                        if source.find('class').text in ['vga', 'video']:
                            values.append(ValueStateValues[source.find('signal-present').text])
                        elif source.find('class').text in ['audio']:
                            for channel in source.find('channels').findall('channel'):
                                if channel.find('position').text == 'left':
                                    self.WriteStatus('AudioPeakLevel', int(channel.find('peak').text), {'Channel': 'Left'})
                                elif channel.find('position').text == 'right':
                                    self.WriteStatus('AudioPeakLevel', int(channel.find('peak').text), {'Channel': 'Right'})

                    self.WriteStatus('InputSignalStatus', values[0], {'Channel': '1'})
                    self.WriteStatus('InputSignalStatus', values[1], {'Channel': '2'})
                except:
                    if self.ReadStatus('DeviceState', qualifier) in ['Inactive', 'Paused']:
                        self.WriteStatus('InputSignalStatus', 'Idle', {'Channel': '1'})
                        self.WriteStatus('InputSignalStatus', 'Idle', {'Channel': '2'})
                    else:
                        self.Error(['Input Signal Status: Invalid/unexpected response'])
            except:
                self.Error(['Device State/Input Signal Status: Invalid/unexpected response'])
    
    def SetExtendCapture(self, value, qualifier):
        durationString = qualifier['Duration']
        try:
            if durationString and 0 < int(durationString) < 525600:
                duration = int(durationString) * 60
                uri = '/capture/extend'
                data = 'duration={}'.format(duration)
                self.__SetHelper('ExtendCapture', value, qualifier, uri, data)
            else:
                self.Discard('Invalid Command for SetExtendCapture')
        except ValueError:
            self.Discard('Invalid Command for SetExtendCapture')
            
    def SetNewCapture(self, value, qualifier):
        durationString = qualifier['Duration']
        captureProfile = qualifier['Profile']
        description = qualifier['Title']

        try:
            if durationString and 0 < int(durationString) < 525600 and captureProfile and description is not None:
                duration = int(durationString) * 60
                uri = '/capture/new_capture'
                data = 'duration={}&capture_profile_name={}&description={}'.format(duration, captureProfile, description)
                self.__SetHelper('NewCapture', value, qualifier, uri, data)
            else:
                self.Discard('Invalid Command for SetNewCapture')
        except ValueError:
            self.Discard('Invalid Command for SetNewCapture')

    def UpdateNextCaptureStatus(self, value, qualifier):
        uri = '/status/next_capture'
        res = self.__UpdateHelper('NextCaptureStatus', None, qualifier, uri)
        if res:
            try:
                self.ParseMessage(res, 'Next', 'NextCaptureStatus')
            except:
                self.Error(['Next Capture Status: Invalid/unexpected response'])

    def UTCtoLocal(self, dt):
        return dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def ParseMessage(self, msg, capture, writeFunc):
        root = ET.fromstring(msg)
        startDateTimeRaw = None
        durationDelta = None
        try:
            startDateTimeString = root.findall(".//start-time")[0].text.split('.')[0]
            startDateTimeRaw = get_dt_from_str(startDateTimeString, '%Y-%m-%dT%H:%M:%S')
            startDateTimeTZ = self.UTCtoLocal(startDateTimeRaw)
            startTime = startDateTimeTZ.strftime(self.TimeFormat)
            if '-' in startTime:
                startTime = startTime.replace('-', '+')
            elif '+' in startTime:
                startTime = startTime.replace('+', '-')
            startDate = startDateTimeTZ.strftime(self.DateFormat)
        except IndexError:
            self.Error(['Cannot find start-time/date in Response'])
            startTime = ''
            startDate = ''
        self.WriteStatus(writeFunc, startTime, {'Status Tag': 'Start Time'})
        self.WriteStatus(writeFunc, startDate, {'Status Tag': 'Start Date'})

        try:
            title = root.findall(".//title")[0].text
        except IndexError:
            self.Error('Cannot find title in Response')
            title = ''
        self.WriteStatus(writeFunc, title, {'Status Tag': 'Title'})

        try:
            duration_list = root.findall(".//duration")
            dur_lst = []
            for val in duration_list:
                dur_lst.append(int(val.text))
            if dur_lst:
                duration = max(dur_lst) # To make sure that capture duration is correct even when user extend the capture time
                durationDelta = timedelta(seconds=duration)
                durationStringList = str(durationDelta).split(':')
                durationString = '{0} hrs {1} min'.format(durationStringList[0], durationStringList[1])
            else:
                durationString = ''
        except IndexError:
            self.Error(['Cannot find duration in Response'])
            durationString = ''
        self.WriteStatus(writeFunc, durationString, {'Status Tag': 'Duration'})

        try:
            presenters = ''
            for presenter in root.findall(".//presenter"):
                presenters += '{0}, '.format(presenter.text)
            presenters = presenters[:-2]
        except IndexError:
            self.Error(['Cannot find presenters in Response'])
            presenters = ''
        self.WriteStatus(writeFunc, presenters, {'Status Tag': 'Presenters'})

        if capture == 'Current':
            try:
                state = root.findall(".//state")[0].text.title()
            except IndexError:
                self.Error(['Cannot find state in Response'])
                state = ''
            self.WriteStatus(writeFunc, state, {'Status Tag': 'State'})
            try:
                currentDateTime = get_dt_from_str(root.findall(".//wall-clock-time")[0].text.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                delta = currentDateTime - startDateTimeRaw
                if delta > timedelta(seconds=0):
                    timeRemainingDelta = durationDelta - delta
                    if timeRemainingDelta > timedelta(seconds=0):
                        deltaStrList = str(durationDelta-delta).split(':')
                        timeRemaining = '{0} hrs {1} min'.format(deltaStrList[0], deltaStrList[1])
                    else:
                        timeRemaining = 'Capture has completed'
                else:
                    timeRemaining = 'Capture has not begun'
            except:
                self.Error(['Cannot calculate time remaining from Response'])
                timeRemaining = ''
            self.WriteStatus(writeFunc, timeRemaining, {'Status Tag': 'Time Remaining'})

    def __CheckResponseForErrors(self, sourceCmdName, res):
        return res.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True
        url = '{}{}'.format(self.RootURL.rstrip('/'), url)
        if data:
            data = data.encode()
        headers = {
            'Authorization': self.authentication.decode(),
            'Content-Type': 'application/xml'
        }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=5)  # open() returns a http.client.HTTPResponse object if successful
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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL.rstrip('/'), url)
        headers = {
            'Authorization': self.authentication.decode(),
            'Content-Type': 'application/xml'
        }
        my_request = urllib.request.Request(url, headers=headers, method='GET')
        try:
            res = self.Opener.open(my_request, timeout=5)
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
                    except BaseException:
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
        except BaseException:
            return None

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

def get_dt_from_str(date_string: str, format_str: str='%Y-%m-%dT%H:%M:%SZ') -> datetime:
    """Convert 2024-09-01T14:34:02Z -> datetime(), ignoring timezone offset.Í"""

    if format_str not in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M']:
        raise ValueError('unsupport format: {}'.format(format_str))

    date, time_ = date_string.split('T')

    year, month, day = date.split('-')
    year, month, day = int(year), int(month), int(day)
    
    if format_str[-1] == 'Z':
        time_ = time_[:-1]

    if format_str in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S']:
        hour, minute, second = time_.split(':')
    elif format_str == '%Y-%m-%dT%H:%M':
        hour, minute = time_.split(':')
        second = '0'
    
    hour, minute, second = int(hour), int(minute), int(second)    
    
    return datetime(year, month, day, hour, minute, second)