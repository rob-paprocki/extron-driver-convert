import urllib.error
import urllib.request
from json import loads, dumps

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
        self._NumberOfCodecSourceSearch = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CodecChannelName': {'Parameters':['Button'], 'Status': {}},
            'CodecDeviceName': {'Parameters':['Button'], 'Status': {}},
            'CodecSourceCommand': {'Parameters':['Codec Source Group', 'Codec Source ID', 'Codec Source Name', 'Codec Source URL'], 'Status': {}},
            'CodecSourceGroup': {'Parameters':['Button'], 'Status': {}},
            'CodecSourceID': {'Parameters':['Button'], 'Status': {}},
            'CodecSourceName': {'Parameters':['Button'], 'Status': {}},
            'CodecSourceNavigation': {'Status': {}},
            'CodecSourceUpdate': { 'Status': {}},
            'CodecSourceURL': {'Parameters':['Button'], 'Status': {}},
            'Mode': {'Status': {}},
            }

        self.CodecSourceAdvance = True
        self.CodecSourceList = []
        self.CodecSourceStartingEntry = 0

    @property
    def NumberOfCodecSourceSearch(self):
        return self._NumberOfCodecSourceSearch

    @NumberOfCodecSourceSearch.setter
    def NumberOfCodecSourceSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfCodecSourceSearch= int(value)
        else:
            self.Error(['The value of Number Of Codec Source Search is outside of the range of allowable values.'])
        
    def SetCodecSourceCommand(self, value, qualifier):

        source_grp = qualifier['Codec Source Group']
        source_id = qualifier['Codec Source ID']
        source_name = qualifier['Codec Source Name']
        source_url = qualifier['Codec Source URL']
        if source_grp and source_id and source_name and source_url:
            url = 'api/codec/decode/addSpec'
            data = dumps({
                          "group": source_grp,
                          "name": source_name,
                          "url": source_url,
                          "id": source_id
                        })
            self.__SetHelper('CodecSourceCommand', value, qualifier, url, data.encode())    
                    
        else:
            self.Discard('Invalid Command for SetCodecSourceCommand')

    def SetCodecSourceNavigation(self, value, qualifier):

        if 'Page Up' == value:
            self.CodecSourceStartingEntry -= self._NumberOfCodecSourceSearch
        elif 'Page Down' == value and self.CodecSourceAdvance:
            self.CodecSourceStartingEntry += self._NumberOfCodecSourceSearch

        if self.CodecSourceStartingEntry >= len(self.CodecSourceList):
            self.CodecSourceStartingEntry = len(self.CodecSourceList) - 1

        if self.CodecSourceStartingEntry < 0:
            self.CodecSourceStartingEntry = 0

        self.CodecSourceAdvance = True
        
        Button = 1
        for a in self.CodecSourceList[self.CodecSourceStartingEntry:]:
            self.WriteStatus('CodecDeviceName', a['device_name'], {'Button': Button})
            self.WriteStatus('CodecChannelName', a['channel_name'], {'Button': Button})
            self.WriteStatus('CodecSourceName', a['name'], {'Button': Button})
            self.WriteStatus('CodecSourceURL', a['url'], {'Button': Button})
            self.WriteStatus('CodecSourceGroup', a['group'], {'Button': Button})
            self.WriteStatus('CodecSourceID', a['id'], {'Button': Button})
            Button += 1
            if Button == self._NumberOfCodecSourceSearch+1:
                break
        for a in range(Button,self._NumberOfCodecSourceSearch+1):
            self.CodecSourceAdvance = False
            self.WriteStatus('CodecDeviceName', '', {'Button': a})
            self.WriteStatus('CodecChannelName', '', {'Button': a})
            self.WriteStatus('CodecSourceName', '', {'Button': a})
            self.WriteStatus('CodecSourceURL', '', {'Button': a})
            self.WriteStatus('CodecSourceGroup', '', {'Button': a})
            self.WriteStatus('CodecSourceID', '', {'Button': a})

    def SetCodecSourceUpdate(self, value, qualifier):
        self.Debug = True

        url = 'api/codec/discovery/scan'
        res = self.__UpdateHelper('CodecSourceUpdate', value, qualifier, url=url)
        if res:
            try:
                codecSourceList = []
                codecSources = res['data']
                for val in codecSources:
                    codecSourceList.append({"group": val["group"], "name": val["name"], "device_name": val["device_name"],
                                              "channel_name": val["channel_name"], "url": val["url"], "id": val["id"]})
                self.CodecSourceList = codecSourceList
                self.CodecSourceList.append({"group": "***End of list***", "name": "***End of list***", "device_name": "***End of list***",
                                              "channel_name": "***End of list***", "url": "***End of list***", "id": "***End of list***"})
                self.CodecSourceAdvance = True
                self.CodecSourceStartingEntry = 0
                self.SetCodecSourceNavigation(None, None)
            except (ValueError, KeyError, IndexError):
                self.Error(['Codec Source Update: Invalid/unexpected response'])

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Encoder': 'encode',
            'Decoder': 'decode'
            }

        if value in ValueStateValues:
            url = 'api/codec/mode/set?mode={}'.format(ValueStateValues[value])
            self.__SetHelper('Mode', value, qualifier, url=url)
        else:
            self.Discard('Invalid Command for SetMode')

    def UpdateMode(self, value, qualifier):

        url = 'api/codec/mode/get'
        res = self.__UpdateHelper('Mode', value, qualifier, url=url)
        if res:
            try:
                ValueStateValues = {
                    'encode': 'Encoder',
                    'decode': 'Decoder'
                    }

                value = ValueStateValues[res]
                self.WriteStatus('Mode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Mode: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)
        headers = {'Content-Type' : 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = urllib.request.urlopen(my_request, timeout=1)
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

        url = '{}{}'.format(self.RootURL, url)
        headers = {'Content-Type' : 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers)
        try:
            res = urllib.request.urlopen(my_request, timeout=1)
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
