import base64
from json import loads, dumps
import urllib.error
import urllib.request


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelDirectSelect': {'Parameters': ['IP Address'], 'Status': {}},
            'ChannelListNavigation': {'Status': {}},
            'ChannelListSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'ChannelListSearchSet': {'Parameters': ['IP Address'], 'Status': {}},
            'ChannelListUpdate': {'Status': {}},
            'ControlSTBCommand': {'Status': {}},
            'MuteStatus': {'Parameters': ['IP Address'], 'Status': {}},
            'Volume': {'Parameters': ['IP Address'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['IP Address'], 'Status': {}},
        }

        self.StartingEntry = 1
        self.EndEntry = 0
        self.Advance = True

        self.NumberOfButton = 0
        self.ChannelList = []
        self.ChannelId = dict()

        self.ChannelStartIndex = 0
        self._PINNumber = None
        self.NumberOfButton = 5

    @property
    def PINNumber(self):
        return self._PINNumber

    @PINNumber.setter
    def PINNumber(self, value):
        self._PINNumber = value

    @property
    def NumberOfChannelSearch(self):
        return self.NumberOfButton

    @NumberOfChannelSearch.setter
    def NumberOfChannelSearch(self, value):
        if 1 <= value <= 15:
            self.NumberOfButton = value
        else:
            self.Error(['Number of Channel Search must be between 1 to 15.'])

    def SetChannelDirectSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 250
        }

        ip_address = qualifier['IP Address']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
                ip_address and self.ChannelList and value <= len(self.ChannelList)):
            ChannelDirectSelectCmdString = ('mobile/sendstbcommand/{0}/CHANGE_CHANNEL,{1}'.
                format(ip_address, self.ChannelId[self.ChannelList[value - 1]]))
            self.__SetHelper('ChannelDirectSelect', value, qualifier, url=ChannelDirectSelectCmdString, data=None)
        else:
            self.Discard('Invalid Command for SetChannelDirectSelect')

    def SetChannelListNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self.NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.Advance:
                    self.StartingEntry += NumberOfAdvance
            elif 'Up' in value:
                self.StartingEntry -= NumberOfAdvance

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self.NumberOfButton - 1

            numOfName = len(self.ChannelList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < numOfName and index < self.EndEntry:
                name = self.ChannelList[index]
                self.WriteStatus('ChannelListSearchResult', name, {'Button': int(button)})
                button = button + 1
                index = index + 1

            if button <= self.NumberOfButton:
                self.Advance = False
                self.WriteStatus('ChannelListSearchResult', '***End of list***', {'Button': button})
                button = button + 1
                for i in range(button, int(self.NumberOfButton) + 1):
                    self.WriteStatus('ChannelListSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetChannelListNavigation')

    def SetChannelListSearchSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': self.NumberOfButton
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Channel = self.ReadStatus('ChannelListSearchResult', {'Button': value})
            if Channel not in ['***Not Available***', '***End of list***']:
                ipaddress = qualifier['IP Address']
                if ipaddress and Channel:
                    LoadChannelCmdString = 'mobile/sendstbcommand/{0}/CHANGE_CHANNEL,{1}'.format(ipaddress, self.ChannelId[Channel])
                    self.__SetHelper('ChannelListSearchSet', value, qualifier, url=LoadChannelCmdString, data=None)
        else:
            self.Discard('Invalid Command for SetChannelListSearchSet')

    def UpdateMuteStatus(self, value, qualifier):
        self.UpdateChannelListUpdate(value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):
        self.UpdateChannelListUpdate(value, qualifier)

    def UpdateChannelListUpdate(self, value, qualifier):

        MuteStatus = {
            'True': 'On',
            'False': 'Off'
        }
        VolumeIPqualifier = dict()

        StatusCmdString = 'mobile/getendpointgroupsforpin/{0}'.format(self._PINNumber)
        res = self.__UpdateHelper('ChannelListUpdate', value, qualifier, url=StatusCmdString, data=None)

        if res:
            try:
                ChannelStatus = loads(res)

                index = 0
                if ChannelStatus:
                    while index < len(ChannelStatus["groups"][0]["endpoints"]):
                        if 'volume' and 'mute' in ChannelStatus["groups"][0]["endpoints"][index].keys():
                            VolumeIPqualifier = {'IP Address': ChannelStatus["groups"][0]["endpoints"][index]['ipAddress']}
                            self.WriteStatus('VolumeStatus', ChannelStatus["groups"][0]["endpoints"][index]["volume"], VolumeIPqualifier)
                            self.WriteStatus('MuteStatus', MuteStatus[str(ChannelStatus["groups"][0]["endpoints"][index]["mute"])], VolumeIPqualifier)
                            index += 1

                    index = 0
                    NewChannelList = []
                    while index < len(ChannelStatus["groups"][0]['channels']):
                        NewChannelList.append(ChannelStatus["groups"][0]['channels'][index]['name'])
                        self.ChannelId[ChannelStatus["groups"][0]['channels'][index]['name']] = ChannelStatus["groups"][0]['channels'][index]['id']
                        index += 1
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

            if not (NewChannelList == self.ChannelList):
                self.ChannelList = NewChannelList
                self.SetChannelListUpdateHandler()

    def SetChannelListUpdateHandler(self):
        res = len(self.ChannelList)
        if res:
            searchMax = len(self.ChannelList)
            if searchMax > self.NumberOfButton:
                searchMax = self.NumberOfButton
            button = 1
            for name in range(0, searchMax):
                name = self.ChannelList[button - 1]
                self.WriteStatus('ChannelListSearchResult', name, {'Button': button})
                button = button + 1

            if button <= self.NumberOfButton:
                self.WriteStatus('ChannelListSearchResult', '***End of list***', {'Button': button})
                button = button + 1
                for i in range(button, self.NumberOfButton + 1):
                    self.WriteStatus('ChannelListSearchResult', '', {'Button': i})
        else:
            self.__MatchNoContact(None, None)

    def __MatchNoContact(self, match, tag):
        button = 1
        self.Advance = False
        self.WriteStatus('ChannelListSearchResult', '***Not Available***', {'Button': button})
        button = button + 1
        for i in range(button, int(self.NumberOfButton) + 1):
            self.WriteStatus('ChannelListSearchResult', '', {'Button': i})

    def SetControlSTBCommand(self, value, qualifier):

        ValueStateValues = {
            'Subtitles On': 'SUBTITLES_ON',
            'Subtitles Off': 'SUBTITLES_OFF',
            'Enter Full Screen': 'ENTER_FULL_SCREEN',
            'Exit Full Screen': 'EXIT_FULL_SCREEN'
        }
        stbip = qualifier['STB IP']
        if stbip:
            ControlSTBCommandCmdString = 'mobile/sendstbcommand/{0}/{1}'.format(stbip, ValueStateValues[value])
            self.__SetHelper('ControlSTBCommand', value, qualifier, url=ControlSTBCommandCmdString, data=None)
        else:
            self.Discard('Invalid Command for SetControlSTBCommand')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        VolumeSTBIP = qualifier['IP Address']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and VolumeSTBIP:
            VolumeCmdString = 'mobile/sendstbcommand/{0}/CHANGE_VOLUME,{1}'.format(VolumeSTBIP, value)
            self.__SetHelper('Volume', value, qualifier, url=VolumeCmdString, data=None)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url, data):
        self.Debug = True

        my_request = urllib.request.Request('{0}{1}'.format(self.RootURL, url), data=None, headers={'Content-Type': 'application/json'}, method='GET')
        try:
            res = self.Opener.open(my_request)
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

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        my_request = urllib.request.Request('{0}{1}'.format(self.RootURL, url), data=None, headers={'Content-Type': 'application/json'}, method='GET')

        try:
            res = self.Opener.open(my_request)
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
                    except:
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
        except:
            return None


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
