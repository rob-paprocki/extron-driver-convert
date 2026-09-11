from extronlib.system import GetUnverifiedContext
from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request
from json import loads, dumps
import binascii

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode='On'):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None
        
        url = 'http://{0}:{1}/'.format(ipAddress, port)
        self.RootURL = url.replace('http', 'https') if port == 4003 else url
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._NumberOfButtonSearch = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutput': { 'Status': {}},
            'InputCard': {'Parameters':['Index','Source Name'], 'Status': {}},
            'InputCardSignalStatus': {'Parameters':['Index'], 'Status': {}},
            'OutputScreenStatus': {'Parameters':['Index'], 'Status': {}},
            'PairedButtonConnectionCount': {'Parameters':['Button'], 'Status': {}},
            'PairedButtonConnectionStatus': {'Parameters':['Button'], 'Status': {}},
            'PairedButtonNavigation': { 'Status': {}},
            'PairedButtonStatus': {'Parameters':['Button'], 'Status': {}},
            'PairedButtonUpdate': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'Standby': { 'Status': {}},
            'SystemSharingStatus': { 'Status': {}},
            'SystemUseStatus': { 'Status': {}},
            'VideoMode': { 'Status': {}},
            'WiredRoomDock': { 'Status': {}}
        }

        self.ButtonListStartingEntry = 0
        self.ButtonAdvance = True
        self.AllButtonsList = []

    @property
    def NumberOfButtonSearch(self):
        return self._NumberOfButtonSearch

    @NumberOfButtonSearch.setter
    def NumberOfButtonSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfButtonSearch = value
        else:
            self.Error(['Number of Button Search Parameter must be within range 1 to 15'])

    def __GetBasicAuthHeader(self):

        cred = '{}:{}'.format(self.deviceUsername, self.devicePassword)
        return binascii.b2a_base64(cred.encode()).decode().strip()
    
    def SetAudioOutput(self, value, qualifier):

        ValueStateValues = ('Jack', 'HDMI', 'SPDIF', 'DisplayPort')

        if value in ValueStateValues:
            url = 'v2/configuration/audio'
            data = dumps({
                              "enabled": True,
                              "output": value
                            }) 
            self.__SetHelper('AudioOutput', value, qualifier, url, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetAudioOutput')

    def UpdateAudioOutput(self, value, qualifier):

        url = 'v2/configuration/audio'
        res = self.__UpdateHelper('AudioOutput', value, qualifier, url)
        if res:
            try:
                value = res["output"]
                self.WriteStatus('AudioOutput', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Audio Output: Invalid/unexpected response'])

    def SetInputCard(self, value, qualifier):

        ValueStateValues = {
            'Enable':  True,
            'Disable': False
            }

        if 1 <= qualifier['Index'] <= 99 and value in ValueStateValues and qualifier['Source Name']:
            url = 'v2/configuration/input-cards/{}'.format(qualifier['Index'])
            data = dumps({
                          "enabled": ValueStateValues[value],
                          "sourceName": qualifier['Source Name']
                        })
            self.__SetHelper('InputCard', value, qualifier, url, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetInputCard')

    def UpdateInputCardSignalStatus(self, value, qualifier):

        if 1 <= qualifier['Index'] <= 99:
            url = 'v2/configuration/input-cards/{}'.format(qualifier['Index'])
            res = self.__UpdateHelper('InputCardSignalStatus', value, qualifier, url)
            if res:
                try:
                    ValueStateValues = {
                        True:  'Active',
                        False: 'Inactive'
                        }

                    value = ValueStateValues[res["hasSignal"]]
                    self.WriteStatus('InputCardSignalStatus', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Input Card Signal Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputCardSignalStatus')

    def UpdateOutputScreenStatus(self, value, qualifier):

        if 1 <= qualifier['Index'] <= 99:
            url = 'v2/configuration/video-outputs/{}'.format(qualifier['Index'])
            res = self.__UpdateHelper('OutputScreenStatus', value, qualifier, url)
            if res:
                try:
                    ValueStateValues = {
                        True: 'Connected',
                        False: 'Disconnected'
                        }

                    value = ValueStateValues[res["connected"]]
                    self.WriteStatus('OutputScreenStatus', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Output Screen Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputScreenStatus')

    def SetPairedButtonNavigation(self, value, qualifier):

        ValueStates = {
            'True':  'Connected',
            'False': 'Disconnected',
            '***End Of List***': '***End of list***'
        }

        if 'Page Up' == value:
            self.ButtonListStartingEntry -= self._NumberOfButtonSearch
        elif 'Page Down' == value and self.ButtonAdvance:
            self.ButtonListStartingEntry += self._NumberOfButtonSearch

        if self.ButtonListStartingEntry >= len(self.AllButtonsList):
            self.ButtonListStartingEntry = len(self.AllButtonsList) - 1

        if self.ButtonListStartingEntry < 0:
            self.ButtonListStartingEntry = 0

        self.ButtonAdvance = True
        
        Button = 1
        for a in self.AllButtonsList[self.ButtonListStartingEntry:]:
            self.WriteStatus('PairedButtonConnectionCount', a['connectionCount'], {'Button': Button})
            self.WriteStatus('PairedButtonStatus', a['status'], {'Button': Button})
            self.WriteStatus('PairedButtonConnectionStatus', ValueStates[str(a['connected']).title()], {'Button': Button})
            Button += 1
            if Button == self._NumberOfButtonSearch+1:
                break
        for a in range(Button,self._NumberOfButtonSearch+1):
            self.ButtonAdvance = False
            self.WriteStatus('PairedButtonConnectionCount', '', {'Button': a})
            self.WriteStatus('PairedButtonStatus', '', {'Button': a})
            self.WriteStatus('PairedButtonConnectionStatus', '', {'Button': a})

    def SetPairedButtonUpdate(self, value, qualifier):

        url = 'v2/configuration/buttons'
        res = self.__UpdateHelper('PairedButtonUpdate', value, qualifier, url)
        if res:
            try:
                self.AllButtonsList = res
                self.AllButtonsList.append({"status": "***End of list***",
                                            "connectionCount":  "***End of list***",
                                            "connected":  "***End of list***"
                                            })
                self.ButtonAdvance = True
                self.ButtonListStartingEntry = 0
                self.SetPairedButtonNavigation( None, None)
            except (ValueError, KeyError, IndexError):
                self.Error(['Button Update: Invalid/unexpected response'])
        else:
            self.AllButtonsList.append({"status": "***End of list***",
                                        "connectionCount":  "***End of list***",
                                        "connected":  "***End of list***"
                                        })
            self.ButtonAdvance = True
            self.ButtonListStartingEntry = 0
            self.SetPairedButtonNavigation( None, None)

    def SetReboot(self, value, qualifier):

        url = 'v2/operations/reboot'
        self.__SetHelper('Reboot', value, qualifier, url)

    def SetStandby(self, value, qualifier):

        url = 'v2/operations/standby'
        self.__SetHelper('Standby', value, qualifier, url)

    def UpdateSystemUseStatus(self, value, qualifier):

        url = 'v2/configuration/system/status'
        res = self.__UpdateHelper('SystemUseStatus', value, qualifier, url)
        if res:
            ValueStateValues = {
                True: 'True',
                False: 'False'
                }

            try:
                value = ValueStateValues[res["inUse"]]
                self.WriteStatus('SystemUseStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System Use Status: Invalid/unexpected response'])
                
            try:
                value = ValueStateValues[res["sharing"]]
                self.WriteStatus('SystemSharingStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System Sharing Status: Invalid/unexpected response'])

    def SetVideoMode(self, value, qualifier):

        ValueStateValues = ('Extended', 'Clone', 'Span')

        if value in ValueStateValues:
            url = 'v2/configuration/video'
            data = dumps({
                          "cecEnabled": True,
                          "mode": value
                        })
            self.__SetHelper('VideoMode', value, qualifier, url, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetVideoMode')

    def UpdateVideoMode(self, value, qualifier):

        url = 'v2/configuration/video'
        res = self.__UpdateHelper('VideoMode', value, qualifier, url)
        if res:
            try:
                value = res["mode"]
                self.WriteStatus('VideoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mode: Invalid/unexpected response'])

    def SetWiredRoomDock(self, value, qualifier):

        ValueStateValues = {
            'Enable':  True,
            'Disable': False
            }

        if value in ValueStateValues:
            url = 'v2/configuration/features/wired-roomdock'
            data = dumps({
                          "enabled": ValueStateValues[value]
                        })
            self.__SetHelper('WiredRoomDock', value, qualifier, url, data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetWiredRoomDock')

    def UpdateWiredRoomDock(self, value, qualifier):

        url = 'v2/configuration/features/wired-roomdock'
        res = self.__UpdateHelper('WiredRoomDock', value, qualifier, url)
        if res:
            try:
                ValueStateValues = {
                    True: 'Enable',
                    False: 'Disable'
                    }

                value = ValueStateValues[res["enabled"]]
                self.WriteStatus('WiredRoomDock', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Wired RoomDock: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url, data=None):

        self.Debug = True

        rootURL = self.RootURL
        url = '{}{}'.format(rootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Authorization': 'Basic {}'.format(self.__GetBasicAuthHeader()),
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}

        if command in ('Reboot', 'Standby'):
            method = 'POST'
        else:   
            method = 'PATCH'
        my_request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            res = urllib.request.urlopen(my_request, context=self._context, timeout=1)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
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

        rootURL = self.RootURL
        url = '{}{}'.format(rootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Authorization': 'Basic {}'.format(self.__GetBasicAuthHeader())}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = urllib.request.urlopen(my_request, context = self._context, timeout=1)
        except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err: # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err: # includes HTTP status code 100 and any invalid status code
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