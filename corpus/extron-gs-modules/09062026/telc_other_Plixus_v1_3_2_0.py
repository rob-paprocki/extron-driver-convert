import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveMicrophone': {'Parameters':['Position'], 'Status': {}},
            'ClearMicrophoneList': { 'Status': {}},
            'Heartbeat': { 'Status': {}},
            'LEDSet': {'Parameters': ['Seat Number', 'LED'], 'Status': {}},
            'LEDSetAllSeats': {'Parameters': ['LED'], 'Status': {}},
            'MaxActiveMicrophone': { 'Status': {}},
            'MicrophoneMode': {'Parameters': ['Microphone Active', 'Microphone Request'], 'Status': {}},
            'MicrophoneState': {'Parameters': ['Microphone'], 'Status': {}},
            'Recording': { 'Status': {}},
            'RoomVolume': { 'Status': {}},
            'WCAPCoupledMode': {'Parameters': ['Serial Number'], 'Status': {}}
        }

        self.__MinMics = 1
        self.__MaxMics = 500
        
    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def UpdateActiveMicrophone(self, value, qualifier):

        self.UpdateMicrophoneState( None, {'Microphone': 1})

    def SetClearMicrophoneList(self, value, qualifier):

        ValueStateValues = {
            'Speakers And Requests' : 'SpeakersAndRequests',
            'Speakers'              : 'Speakers'
        }

        if value in ValueStateValues:
            ClearMicrophoneListCmdString = '/CoCon/Microphone/ClearMicrophoneList/?Type={}'.format(ValueStateValues[value])
            self.__SetHelper('ClearMicrophoneList', value, qualifier, url=ClearMicrophoneListCmdString)
        else:
            self.Discard('Invalid Command for SetClearMicrophoneList')

    def UpdateHeartbeat(self, value, qualifier):

        HeartbeatCmdString = '/CoCon/Connect'
        self.__UpdateHelper('Heartbeat', value, qualifier, url=HeartbeatCmdString)

    def SetLEDSet(self, value, qualifier):

        SeatNumberConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': qualifier['Seat Number'],
        }

        LEDConstraints = {
            'Min': 1,
            'Max': 5,
            'Value': int(qualifier['LED']) if qualifier['LED'].isdigit() else -1,
        }

        ValueStateValues = ('On', 'Off', 'Blinking')

        if value in ValueStateValues and self.__constraint_checker(SeatNumberConstraints, LEDConstraints):
            LEDSetCmdString = '/CoCon/ButtonLED_Event/SetLED/?SeatNr={0}&LEDNr={1}&State={2}'.format(
                SeatNumberConstraints['Value'], LEDConstraints['Value'], value)
            self.__SetHelper('LEDSet', value, qualifier, url=LEDSetCmdString)
        else:
            self.Discard('Invalid Command for SetLEDSet')

    def SetLEDSetAllSeats(self, value, qualifier):

        LEDConstraints = {
            'Min': 1,
            'Max': 5,
            'Value': int(qualifier['LED']) if qualifier['LED'].isdigit() else -1,
        }

        ValueStateValues = ('On', 'Off', 'Blinking')

        if value in ValueStateValues and self.__constraint_checker(LEDConstraints):
            LEDSetAllSeatsCmdString = '/CoCon/ButtonLED_Event/SetLED/?SeatNr=9999&LEDNr={0}&State={1}'.format(LEDConstraints['Value'], value)
            self.__SetHelper('LEDSetAllSeats', value, qualifier, url=LEDSetAllSeatsCmdString)
        else:
            self.Discard('Invalid Command for SetLEDSetAllSeats')

    def UpdateMaxActiveMicrophone(self, value, qualifier):

        self.UpdateMicrophoneState( None, {'Microphone': value})

    def SetMicrophoneMode(self, value, qualifier):

        ValueStateValues = {
            'Operator':     'Operator',
            'Direct Speak': 'DirectSpeak',
            'Request':      'Request',
            'Vox':          'Vox',
            'Only Request': 'OnlyRequest',
        }

        MicActiveConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': qualifier['Microphone Active'],
        }

        MicRequestConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': qualifier['Microphone Request'],
        }

        if value in ValueStateValues and self.__constraint_checker(MicActiveConstraints, MicRequestConstraints):
            MicrophoneModeCmdString = '/CoCon/Microphone/SetMicrophoneMode/?Mode={0}&MaxNrActive={1}&MaxNrRequest={2}'.format(
                ValueStateValues[value], MicActiveConstraints['Value'], MicRequestConstraints['Value'])
            self.__SetHelper('MicrophoneMode', value, qualifier, url=MicrophoneModeCmdString)
        else:
            self.Discard('Invalid Command for SetMicrophoneMode')

    def SetMicrophoneState(self, value, qualifier):

        MicConstraints = {
            'Min': self.__MinMics,
            'Max': self.__MaxMics,
            'Value': qualifier['Microphone'],
        }

        ValueStateValues = ('On', 'Off', 'Request')

        if value in ValueStateValues and self.__constraint_checker(MicConstraints):
            MicrophoneStateCmdString = '/CoCon/Microphone/SetState/?State={0}&SeatNr={1}'.format(value, MicConstraints['Value'])
            self.__SetHelper('MicrophoneState', value, qualifier, url=MicrophoneStateCmdString)
        else:
            self.Discard('Invalid Command for SetMicrophoneState')

    def UpdateMicrophoneState(self, value, qualifier):

        MicrophoneStateCmdString = '/CoCon/Microphone/Get'
        res = self.__UpdateHelper('MicrophoneState', value, qualifier, url=MicrophoneStateCmdString)
        if res:
            try:

                res = json.loads(res.decode())
                state_reply = json.loads(res)
                mic_list = set(range(self.__MinMics, self.__MaxMics + 1))
                speakerList = state_reply['Get']['State']['Speakers']
                for idx in speakerList:
                    self.WriteStatus('MicrophoneState', 'On', {'Microphone': idx})
                    mic_list.remove(idx)
                speakerList.reverse()
                for position in range(5):
                    try:
                        if position < len(speakerList):
                            self.WriteStatus('ActiveMicrophone', speakerList[position], {'Position' : str(position + 1)})
                        else:
                            self.WriteStatus('ActiveMicrophone', 0, {'Position' : str(position + 1)})
                    except (ValueError, IndexError, AttributeError):
                        self.Error(['Active Microphone: Invalid/unexpected response'])
                if state_reply['Get']['State']['Requests']:
                    self.WriteStatus('MicrophoneState', 'First in Request', {'Microphone': state_reply['Get']['State']['Requests'][0]})
                    mic_list.remove(state_reply['Get']['State']['Requests'][0])
                for idx in state_reply['Get']['State']['Requests'][1:]:
                    self.WriteStatus('MicrophoneState', 'Request', {'Microphone': idx})
                    mic_list.remove(idx)
                for idx in mic_list:
                    self.WriteStatus('MicrophoneState', 'Off', {'Microphone': idx})
                max_mic_active = state_reply['Get']['MicrophoneMode']['MaxNrActive']
                if self.__MinMics <= max_mic_active <= self.__MaxMics:
                    self.WriteStatus('MaxActiveMicrophone', max_mic_active, None)
            except (KeyError, ValueError, TypeError, AttributeError):
                self.Error(['Microphone State: Invalid/unexpected response'])

    def SetRecording(self, value, qualifier):

        if value in ('Start', 'Stop'):
            RecordingCmdString = '/CoCon/Recording/{}recording'.format(value)
            self.__SetHelper('Recording', value, qualifier, url=RecordingCmdString)
        else:
            self.Discard('Invalid Command for SetRecording')

    def UpdateRecording(self, value, qualifier):

        ValueStateValues = {
            'active':  'Active',
            'error':   'Error',
            'idle':    'Idle',
            'paused':  'Paused',
            'unknown': 'Unknown'
        }

        RecordingCmdString = '/CoCon/Recording/Getrecordingstate'
        res = self.__UpdateHelper('Recording', value, qualifier, url=RecordingCmdString)
        if res:
            try:
                res = json.loads(res.decode())
                state_reply = json.loads(res)

                value = ValueStateValues[state_reply['GetRecordingState']['RecordingState']]
                self.WriteStatus('Recording', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Recording: Invalid/unexpected response'])

    def SetRoomVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 25,
            'Value': value,
        }

        if self.__constraint_checker(ValueConstraints):
            RoomVolumeCmdString = '/CoCon/Room/SetVolumeForRoom/?Room=1&Volume={}'.format(ValueConstraints['Value'])
            self.__SetHelper('RoomVolume', value, qualifier, url=RoomVolumeCmdString)
        else:
            self.Discard('Invalid Command for SetRoomVolume')

    def SetWCAPCoupledMode(self, value, qualifier):

        if value in ('True', 'False') and qualifier['Serial Number']:
            WCAPCoupledModeCmdString = '/CoCon/Wireless/SetWcapCoupledMode/?WcapSerial={}&CoupledMode={}'.format(
                qualifier['Serial Number'], value)
            self.__SetHelper('WCAPCoupledMode', value, qualifier, url=WCAPCoupledModeCmdString)
        else:
            self.Discard('Invalid Command for SetWCAPCoupledMode')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        response = response.read()
        if b'ER1' in response:
            self.Error(['Device Error: unsupported command'])
            response = b''
        elif b'ER2' in response:
            self.Error(['Device Error: busy status'])
            response = b''
        elif b'ER3' in response:
            self.Error(['Device Error: outside acceptable range'])
            response = b''
        return response

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
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
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port)
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