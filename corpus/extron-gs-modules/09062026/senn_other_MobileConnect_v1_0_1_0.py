from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import urllib
import json
import random
import re

class DeviceClass:
    def __init__(self, ipAddress, port):

        self._SSLVerifyMode = 'Off'

        if self._SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Debug = False
        self.Subscription = {}
        self._Token = ''
        self._NumberofChannelResults = 5
        self._NumberofStationResults = 5
        self.Models = {}


        self.Commands = {
            'ChannelAccessDetailsRefresh': { 'Status': {}},
            'ChannelAccessDetailsStatus': { 'Status': {}},
            'ChannelDetailsRefresh': { 'Status': {}},
            'ChannelDetailsSetCommand': {'Parameters': ['Type'], 'Status': {}},
            'ChannelDetailsStatus': {'Parameters':['Type'], 'Status': {}},
            'ChannelNavigation': { 'Status': {}},
            'ChannelRefresh': { 'Status': {}},
            'ChannelRegenerateAccessDetails': { 'Status': {}},
            'ChannelResults': {'Parameters':['Entry'], 'Status': {}},
            'ChannelResultSet': {'Parameters':['Entry'], 'Status': {}},
            'PinCodeCommand': { 'Status': {}},
            'PinCodeRefresh': { 'Status': {}},
            'PinCodeRegenerate': { 'Status': {}},
            'PinCodeStatus': { 'Status': {}},
            'QRCodeRefresh': { 'Status': {}},
            'QRCodeStatus': { 'Status': {}},
            'StationNavigation': { 'Status': {}},
            'StationRefresh': { 'Status': {}},
            'StationResults': {'Parameters':['Entry'], 'Status': {}},
            'StationResultSet': {'Parameters':['Entry'], 'Status': {}},
            'StationSerialNumberString': { 'Status': {}},
        }    
        
        self.StationSerialNumber = ''
        self.ChannelIndex = ''
        self.StationScroller = Scroller([], self._NumberofStationResults, end='*** End of List ***')
        self.ChannelScroller = Scroller([], self._NumberofChannelResults, end='*** End of list ***')

    @property
    def Token(self):
        return self._Token

    @Token.setter
    def Token(self, value):
        if value:
            self._Token = value
        else:
            print('Token required.')

    @property
    def NumberofChannelResults(self):
        return self._NumberofChannelResults

    @NumberofChannelResults.setter
    def NumberofChannelResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofChannelResults = value
            self.ChannelScroller = Scroller([], self._NumberofChannelResults, end='*** End of list ***')
        else:
            print('The value of NumberofChannelResults is outside of the range of allowable values.')

    @property
    def NumberofStationResults(self):
        return self._NumberofStationResults

    @NumberofStationResults.setter
    def NumberofStationResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofStationResults = value
            self.StationScroller = Scroller([], self._NumberofStationResults, end='*** End of List ***')
        else:
            print('The value of NumberofStationResults is outside of the range of allowable values.')

    def __WriteStation(self):
        for entry, info in enumerate(self.StationScroller, 1):
            if isinstance(info, dict):
                self.WriteStatus('StationResults', info['name'], {'Entry' : entry})
            else:
                self.WriteStatus('StationResults', info, {'Entry' : entry})

    def __WriteChannel(self):
        for entry, info in enumerate(self.ChannelScroller, 1):
            if isinstance(info, dict):
                self.WriteStatus('ChannelResults', info['name'], {'Entry' : entry})
            else:
                self.WriteStatus('ChannelResults', info, {'Entry' : entry})

    def SetChannelAccessDetailsRefresh(self, value, qualifier):

        if self.StationSerialNumber and self.ChannelIndex:
            ChannelAccessDetailsRefreshCmdString = 'public/api/v2.0/stations/{0}/channels/{1}/access'.format(self.StationSerialNumber, self.ChannelIndex)
            res = self.__UpdateHelper('ChannelAccessDetailsRefresh', value, qualifier, url=ChannelAccessDetailsRefreshCmdString)
            if res:
                try:
                    accessDetails = json.loads(res)
                    self.WriteStatus('ChannelAccessDetailsStatus', accessDetails['channelId'], None)
                except (json.decoder.JSONDecodeError, KeyError):
                    self.Error(['Channel Access Details Refresh: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetChannelAccessDetailsRefresh')

    def SetChannelDetailsRefresh(self, value, qualifier):

        if self.StationSerialNumber and self.ChannelIndex:
            ChannelDetailsRefreshCmdString = 'public/api/v2.0/stations/{0}/channels/{1}'.format(self.StationSerialNumber, self.ChannelIndex)
            res = self.__UpdateHelper('ChannelDetailsRefresh', value, qualifier, url=ChannelDetailsRefreshCmdString)
            if res:
                try:
                    channelDetails = json.loads(res)
                    self.WriteStatus('ChannelDetailsStatus', channelDetails['name'], {'Type' : 'Name'})
                    self.WriteStatus('ChannelDetailsStatus', str(channelDetails['index']), {'Type': 'Index'})
                    self.WriteStatus('ChannelDetailsStatus', str(channelDetails['enabled']), {'Type': 'Enabled'})
                    self.WriteStatus('ChannelDetailsStatus', str(channelDetails['hidden']), {'Type': 'Hidden'})
                    self.WriteStatus('ChannelDetailsStatus', str(channelDetails['streamAvailable']), {'Type': 'Stream Available'})
                    self.WriteStatus('ChannelDetailsStatus', str(channelDetails['pinSecured']), {'Type': 'Pin Secured'})
                except (json.decoder.JSONDecodeError, KeyError):
                    self.Error(['Channel Details Refresh: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetChannelDetailsRefresh')

    def SetChannelDetailsSetCommand(self, value, qualifier):

        TypeStates = ['Name', 'Enabled', 'Hidden']
        channelDetailsString = value

        if qualifier['Type'] in TypeStates and channelDetailsString and self.StationSerialNumber and self.ChannelIndex:
            if channelDetailsString == 'None':
                channelDetailsString = None
            elif channelDetailsString == 'True':
                channelDetailsString = True
            elif channelDetailsString == 'False':
                channelDetailsString = False

            data = json.dumps({qualifier['Type'] : channelDetailsString}).encode()
            ChannelDetailsSetCommandCmdString = 'public/api/v2.0/stations/{0}/channels/{1}'.format(self.StationSerialNumber, self.ChannelIndex)
            self.__SetHelper('ChannelDetailsSetCommand', value, qualifier, url=ChannelDetailsSetCommandCmdString, data=data, method='PUT')
        else:
            self.Discard('Invalid Command for SetChannelDetailsSetCommand')

    def SetChannelNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : self.ChannelScroller.previous,
            'Down'      : self.ChannelScroller.next,
            'Page Up'   : self.ChannelScroller.previous_page,
            'Page Down' : self.ChannelScroller.next_page
        }

        if value in ValueStateValues and self.ChannelScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WriteChannel()
        else:
            self.Discard('Invalid Command for SetChannelNavigation')

    def SetChannelRefresh(self, value, qualifier):

        if self.StationSerialNumber:
            self.ChannelScroller.clear()
            ChannelRefreshCmdString = 'public/api/v2.0/stations/{}/channels'.format(self.StationSerialNumber)
            res = self.__UpdateHelper('ChannelRefresh', value, qualifier, url=ChannelRefreshCmdString)
            if res:
                try:
                    channelList = json.loads(res)
                    for channel in channelList:
                        self.ChannelScroller.append(channel)
                except json.decoder.JSONDecodeError:
                    self.Error(['Channel Refresh: Invalid/unexpected response'])
            self.__WriteChannel()
        else:
            self.Discard('Invalid Command for SetChannelRefresh')

    def SetChannelRegenerateAccessDetails(self, value, qualifier):

        if self.StationSerialNumber and self.ChannelIndex:
            ChannelRegenerateAccessDetailsCmdString = 'public/api/v2.0/stations/{0}/channels/{1}/access'.format(self.StationSerialNumber, self.ChannelIndex)
            self.__SetHelper('ChannelRegenerateAccessDetails', value, qualifier, url=ChannelRegenerateAccessDetailsCmdString, data=None, method='POST')
        else:
            self.Discard('Invalid Command for SetChannelRegenerateAccessDetails')

    def SetChannelResultSet(self, value, qualifier):

        entry = int(qualifier['Entry'])

        if 1 <= entry <= self.ChannelScroller.window and self.ChannelScroller.offset + entry <= self.ChannelScroller.current_size:
            self.ChannelIndex = str(self.ChannelScroller[entry - 1]['index'])
        else:
            self.Discard('Invalid Command for SetChannelResultSet')

    def SetPinCodeCommand(self, value, qualifier):

        cmdstring = value
        if cmdstring and len(cmdstring) == 6 and self.StationSerialNumber and self.ChannelIndex:
            DeviceModeCmdString = 'public/api/v2.0/stations/{0}/channels/{1}/security/pin'.format(self.StationSerialNumber, self.ChannelIndex)
            data = {'pinCode' : '{}'.format(cmdstring)}
            data = json.dumps(data).encode()
            self.__SetHelper('PinCode', value, qualifier, url=DeviceModeCmdString, data=data, method='PUT')
        else:
            self.Discard('Invalid Command for SetPinCodeCommand')

    def SetPinCodeRefresh(self, value, qualifier):

        if self.StationSerialNumber and self.ChannelIndex:
            PinCodeRefreshCmdString = 'public/api/v2.0/stations/{0}/channels/{1}/security/pin'.format(self.StationSerialNumber, self.ChannelIndex)
            res = self.__UpdateHelper('PinCodeRefresh', value, qualifier, url=PinCodeRefreshCmdString)
            if res:
                try:
                    value = json.loads(res)['pinCode']
                    if value is None:
                        self.WriteStatus('PinCodeStatus', 'None', None)
                    else:
                        self.WriteStatus('PinCodeStatus', value, None)
                except (json.decoder.JSONDecodeError, KeyError):
                    self.Error(['Pin Code Refresh: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetPinCodeRefresh')

    def SetPinCodeRegenerate(self, value, qualifier):

        randomPin = ''
        for i in range(0, 6):
            randomPin += str(random.randint(0, 9))

    def SetQRCodeRefresh(self, value, qualifier):

        if self.StationSerialNumber and self.ChannelIndex:
            QRCodeRefreshCmdString = 'public/api/v2.0/stations/{0}/channels/{1}/access/qrcode.data'.format(self.StationSerialNumber, self.ChannelIndex)
            res = self.__UpdateHelper('QRCodeRefresh', value, qualifier, url=QRCodeRefreshCmdString)
            QRGen = TLPQRcode(None)
            if res:
                try:
                    qr = QRGen.GenerateQRString(res)
                    self.WriteStatus('QRCodeStatus', qr, None)
                except (json.decoder.JSONDecodeError, KeyError):
                    self.Error(['QR Code Refresh: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for SetQRCodeRefresh')

    def SetStationNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : self.StationScroller.previous,
            'Down'      : self.StationScroller.next,
            'Page Up'   : self.StationScroller.previous_page,
            'Page Down' : self.StationScroller.next_page
        }

        if value in ValueStateValues and self.StationScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WriteStation()
        else:
            self.Discard('Invalid Command for SetStationNavigation')

    def SetStationRefresh(self, value, qualifier):

        self.StationScroller.clear()

        StationRefreshCmdString = 'public/api/v2.0/stations'
        res = self.__UpdateHelper('StationRefresh', value, qualifier, url=StationRefreshCmdString)
        if res:
            try:
                stationList = json.loads(res)
                for station in stationList:
                    self.StationScroller.append(station)
            except json.decoder.JSONDecodeError:
                self.Error(['Station Refresh: Invalid/unexpected response'])
        self.__WriteStation()

    def SetStationResultSet(self, value, qualifier):

        entry = int(qualifier['Entry'])

        if 1 <= entry <= self.StationScroller.window and self.StationScroller.offset + entry <= self.StationScroller.current_size:
            self.StationSerialNumber = self.StationScroller[entry - 1]['serialNumber']
            
        else:
            self.Discard('Invalid Command for SetStationResultSet')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None, method=None):

        self.Debug = True
        url = '{0}{1}'.format(self.RootURL, url)
        headers = {
            'Authorization': 'Basic {}'.format(self._Token),
            'Content-Type' : 'application/json'
        }

        my_request = urllib.request.Request(url, headers=headers, data = data, method=method)

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 201, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None, method='GET'):

        url = '{0}{1}'.format(self.RootURL, url)

        headers = {
            'Authorization': 'Basic {}'.format(self._Token),
            'Content-Type':'application/json'
        }

        my_request = urllib.request.Request(url, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
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

class Scroller:
    def __init__(self, items, window, mark_end=True, end='', fill=''):

        self.__all_items = list(items)
        self.__filtered_items = []
        self.__filter_key = None
        self.__current_items = self.__all_items
        self.__offset = 0
        self.__window = max(1, window)
        self.__mark_end = mark_end
        self.__end = end
        self.__fill = fill
    
    def __getitem__(self, index):

        return self.view()[index]

    def __iter__(self):

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            yield item

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                yield self.end

            for i in range(fill_count - int(self.mark_end)):
                yield self.fill

    def __str__(self):

        s = 'Offset {}/{}, viewing ({{}}) {}/{} items ({})'.format(self.offset, self.max_offset, self.window, self.current_size, self.view())

        if not self.filtered:
            return s.format('all')
        else:
            return s.format('filtered')
    
    @property
    def current_items(self):

        return self.__current_items.copy()

    @property
    def all_items(self):

        return self.__all_items.copy()

    @property
    def filtered_items(self):

        return self.__filtered_items.copy()

    @property
    def current_size(self):

        return len(self.__current_items)

    @property
    def all_size(self):

        return len(self.__all_items)

    @property
    def filtered_size(self):

        return len(self.__filtered_items)

    @property
    def offset(self):

        self.__offset = min(self.__offset, self.max_offset)
        return self.__offset

    @offset.setter
    def offset(self, offset):

        if 0 <= offset <= self.max_offset:
            self.__offset = offset
            return

        raise Exception('offset value \'{}\' is out of range [0, {}]'.format(offset, self.max_offset))

    @property
    def window(self):

        return self.__window

    @property
    def mark_end(self):

        return self.__mark_end

    @property
    def end(self):

        return self.__end

    @property
    def fill(self):

        return self.__fill

    @property
    def filtered(self):

        return self.__filter_key is not None

    @property
    def max_offset(self):

        return max(0, self.current_size - self.window + int(self.mark_end))

    def view(self):

        return list(self.__iter__())

    def format(self, key):

        items = []

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            items.append(key(item))

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                items.append(self.end)

            for i in range(fill_count - int(self.mark_end)):
                items.append(self.fill)

        return items
    
    def clear(self):

        self.__all_items.clear()

        self.__filtered_items.clear()
        self.__filter_key = None

        self.__current_items = self.__all_items

        self.offset = 0

    def overwrite(self, items):

        self.clear()
        self.extend(items)

    def append(self, item):

        self.__all_items.append(item)

        if self.__filter_key is not None and self.__filter_key(item):
            self.__filtered_items.append(item)

    def extend(self, items):

        self.__all_items.extend(items)

        if self.__filter_key is not None:
            for item in items:
                if self.__filter_key(item):
                    self.__filtered_items.append(item)

    def filter(self, key):

        self.__filter_key = key

        if self.__filter_key is not None:
            self.__filtered_items = [item for item in self.__all_items if self.__filter_key(item)]
            self.__current_items = self.__filtered_items
        else:
            self.__filtered_items.clear()
            self.__current_items = self.__all_items

        self.offset = 0
    
    def scroll(self, steps):

        self.offset = max(0, min(self.offset + steps, self.max_offset))
    
    def previous(self):

        self.scroll(-1)

    def next(self):

        self.scroll(1)

    def previous_page(self):

        self.scroll(-self.window)

    def next_page(self):

        self.scroll(self.window)

    def first(self):

        self.offset = 0

    def last(self):

        self.offset = self.max_offset

class TLPQRcode:

    def __init__(self, label, shape='Square', border=1):
        self._label = label
        self._shape = shape
        self._border = border
        self._getstringqr = ''
        self._gettextqr = ''

    @property
    def Border(self):

        return self._border

    @Border.setter
    def Border(self, value):

        if type(value) is int:
            self._border = value

    @property
    def GetQRString(self):

        return self._getstringqr

    @property
    def GetQRText(self):

        return self._gettextqr

    def SetText(self, text):

        self._gettextqr = text
        self._label.SetText(self.GenerateQRString(text))


    def SetVisible(self, state):
        self._label.SetVisible(state)


    def GenerateQRString(self, text):

        _tempString = ''

        _qr = QRCode(border=self.Border)
        _qr.add_data(text)

        matrix = _qr.get_matrix()

        for y_axis in matrix:
            for x_axis in y_axis:
                if x_axis:
                    if self._shape == 'Square':
                        _tempString += 'g'
                    else:
                        _tempString += 'n'
                else:
                    _tempString += '  '

            _tempString += '\n'

        self._getstringqr = _tempString

        return self._getstringqr

class DataOverflowError(Exception):
    pass

ERROR_CORRECT_L = 1
ERROR_CORRECT_M = 0
ERROR_CORRECT_Q = 3
ERROR_CORRECT_H = 2

rsPoly_LUT = {
    7:  [1, 127, 122, 154, 164, 11, 68, 117],
    10: [1, 216, 194, 159, 111, 199, 94, 95, 113, 157, 193],
    13: [1, 137, 73, 227, 17, 177, 17, 52, 13, 46, 43, 83, 132, 120],
    15: [1, 29, 196, 111, 163, 112, 74, 10, 105, 105, 139, 132, 151,
        32, 134, 26],
    16: [1, 59, 13, 104, 189, 68, 209, 30, 8, 163, 65, 41, 229, 98, 50, 36, 59],
    17: [1, 119, 66, 83, 120, 119, 22, 197, 83, 249, 41, 143, 134, 85, 53, 125,
        99, 79],
    18: [1, 239, 251, 183, 113, 149, 175, 199, 215, 240, 220, 73, 82, 173, 75,
        32, 67, 217, 146],
    20: [1, 152, 185, 240, 5, 111, 99, 6, 220, 112, 150, 69, 36, 187, 22, 228,
        198, 121, 121, 165, 174],
    22: [1, 89, 179, 131, 176, 182, 244, 19, 189, 69, 40, 28, 137, 29, 123, 67,
        253, 86, 218, 230, 26, 145, 245],
    24: [1, 122, 118, 169, 70, 178, 237, 216, 102, 115, 150, 229, 73, 130, 72,
        61, 43, 206, 1, 237, 247, 127, 217, 144, 117],
    26: [1, 246, 51, 183, 4, 136, 98, 199, 152, 77, 56, 206, 24, 145, 40, 209,
        117, 233, 42, 135, 68, 70, 144, 146, 77, 43, 94],
    28: [1, 252, 9, 28, 13, 18, 251, 208, 150, 103, 174, 100, 41, 167, 12, 247,
        56, 117, 119, 233, 127, 181, 100, 121, 147, 176, 74, 58, 197],
    30: [1, 212, 246, 77, 73, 195, 192, 75, 98, 5, 70, 103, 177, 22, 217, 138,
        51, 181, 246, 72, 25, 18, 46, 228, 74, 216, 195, 11, 106, 130, 150]
              }

EXP_TABLE = list(range(256))

LOG_TABLE = list(range(256))

for i in range(8):
    EXP_TABLE[i] = 1 << i

for i in range(8, 256):
    EXP_TABLE[i] = (
        EXP_TABLE[i - 4] ^ EXP_TABLE[i - 5] ^ EXP_TABLE[i - 6] ^
        EXP_TABLE[i - 8])

for i in range(255):
    LOG_TABLE[EXP_TABLE[i]] = i

RS_BLOCK_OFFSET = {
    ERROR_CORRECT_L: 0,
    ERROR_CORRECT_M: 1,
    ERROR_CORRECT_Q: 2,
    ERROR_CORRECT_H: 3,
}

RS_BLOCK_TABLE = [

    [1, 26, 19],
    [1, 26, 16],
    [1, 26, 13],
    [1, 26, 9],
    [1, 44, 34],
    [1, 44, 28],
    [1, 44, 22],
    [1, 44, 16],
    [1, 70, 55],
    [1, 70, 44],
    [2, 35, 17],
    [2, 35, 13],
    [1, 100, 80],
    [2, 50, 32],
    [2, 50, 24],
    [4, 25, 9],
    [1, 134, 108],
    [2, 67, 43],
    [2, 33, 15, 2, 34, 16],
    [2, 33, 11, 2, 34, 12],
    [2, 86, 68],
    [4, 43, 27],
    [4, 43, 19],
    [4, 43, 15],
    [2, 98, 78],
    [4, 49, 31],
    [2, 32, 14, 4, 33, 15],
    [4, 39, 13, 1, 40, 14],
    [2, 121, 97],
    [2, 60, 38, 2, 61, 39],
    [4, 40, 18, 2, 41, 19],
    [4, 40, 14, 2, 41, 15],
    [2, 146, 116],
    [3, 58, 36, 2, 59, 37],
    [4, 36, 16, 4, 37, 17],
    [4, 36, 12, 4, 37, 13],
    [2, 86, 68, 2, 87, 69],
    [4, 69, 43, 1, 70, 44],
    [6, 43, 19, 2, 44, 20],
    [6, 43, 15, 2, 44, 16],
    [4, 101, 81],
    [1, 80, 50, 4, 81, 51],
    [4, 50, 22, 4, 51, 23],
    [3, 36, 12, 8, 37, 13],
    [2, 116, 92, 2, 117, 93],
    [6, 58, 36, 2, 59, 37],
    [4, 46, 20, 6, 47, 21],
    [7, 42, 14, 4, 43, 15],
    [4, 133, 107],
    [8, 59, 37, 1, 60, 38],
    [8, 44, 20, 4, 45, 21],
    [12, 33, 11, 4, 34, 12],
    [3, 145, 115, 1, 146, 116],
    [4, 64, 40, 5, 65, 41],
    [11, 36, 16, 5, 37, 17],
    [11, 36, 12, 5, 37, 13],
    [5, 109, 87, 1, 110, 88],
    [5, 65, 41, 5, 66, 42],
    [5, 54, 24, 7, 55, 25],
    [11, 36, 12, 7, 37, 13],
    [5, 122, 98, 1, 123, 99],
    [7, 73, 45, 3, 74, 46],
    [15, 43, 19, 2, 44, 20],
    [3, 45, 15, 13, 46, 16],
    [1, 135, 107, 5, 136, 108],
    [10, 74, 46, 1, 75, 47],
    [1, 50, 22, 15, 51, 23],
    [2, 42, 14, 17, 43, 15],
    [5, 150, 120, 1, 151, 121],
    [9, 69, 43, 4, 70, 44],
    [17, 50, 22, 1, 51, 23],
    [2, 42, 14, 19, 43, 15],
    [3, 141, 113, 4, 142, 114],
    [3, 70, 44, 11, 71, 45],
    [17, 47, 21, 4, 48, 22],
    [9, 39, 13, 16, 40, 14],
    [3, 135, 107, 5, 136, 108],
    [3, 67, 41, 13, 68, 42],
    [15, 54, 24, 5, 55, 25],
    [15, 43, 15, 10, 44, 16],
    [4, 144, 116, 4, 145, 117],
    [17, 68, 42],
    [17, 50, 22, 6, 51, 23],
    [19, 46, 16, 6, 47, 17],
    [2, 139, 111, 7, 140, 112],
    [17, 74, 46],
    [7, 54, 24, 16, 55, 25],
    [34, 37, 13],
    [4, 151, 121, 5, 152, 122],
    [4, 75, 47, 14, 76, 48],
    [11, 54, 24, 14, 55, 25],
    [16, 45, 15, 14, 46, 16],
    [6, 147, 117, 4, 148, 118],
    [6, 73, 45, 14, 74, 46],
    [11, 54, 24, 16, 55, 25],
    [30, 46, 16, 2, 47, 17],
    [8, 132, 106, 4, 133, 107],
    [8, 75, 47, 13, 76, 48],
    [7, 54, 24, 22, 55, 25],
    [22, 45, 15, 13, 46, 16],
    [10, 142, 114, 2, 143, 115],
    [19, 74, 46, 4, 75, 47],
    [28, 50, 22, 6, 51, 23],
    [33, 46, 16, 4, 47, 17],
    [8, 152, 122, 4, 153, 123],
    [22, 73, 45, 3, 74, 46],
    [8, 53, 23, 26, 54, 24],
    [12, 45, 15, 28, 46, 16],
    [3, 147, 117, 10, 148, 118],
    [3, 73, 45, 23, 74, 46],
    [4, 54, 24, 31, 55, 25],
    [11, 45, 15, 31, 46, 16],
    [7, 146, 116, 7, 147, 117],
    [21, 73, 45, 7, 74, 46],
    [1, 53, 23, 37, 54, 24],
    [19, 45, 15, 26, 46, 16],
    [5, 145, 115, 10, 146, 116],
    [19, 75, 47, 10, 76, 48],
    [15, 54, 24, 25, 55, 25],
    [23, 45, 15, 25, 46, 16],
    [13, 145, 115, 3, 146, 116],
    [2, 74, 46, 29, 75, 47],
    [42, 54, 24, 1, 55, 25],
    [23, 45, 15, 28, 46, 16],
    [17, 145, 115],
    [10, 74, 46, 23, 75, 47],
    [10, 54, 24, 35, 55, 25],
    [19, 45, 15, 35, 46, 16],
    [17, 145, 115, 1, 146, 116],
    [14, 74, 46, 21, 75, 47],
    [29, 54, 24, 19, 55, 25],
    [11, 45, 15, 46, 46, 16],
    [13, 145, 115, 6, 146, 116],
    [14, 74, 46, 23, 75, 47],
    [44, 54, 24, 7, 55, 25],
    [59, 46, 16, 1, 47, 17],
    [12, 151, 121, 7, 152, 122],
    [12, 75, 47, 26, 76, 48],
    [39, 54, 24, 14, 55, 25],
    [22, 45, 15, 41, 46, 16],
    [6, 151, 121, 14, 152, 122],
    [6, 75, 47, 34, 76, 48],
    [46, 54, 24, 10, 55, 25],
    [2, 45, 15, 64, 46, 16],
    [17, 152, 122, 4, 153, 123],
    [29, 74, 46, 14, 75, 47],
    [49, 54, 24, 10, 55, 25],
    [24, 45, 15, 46, 46, 16],
    [4, 152, 122, 18, 153, 123],
    [13, 74, 46, 32, 75, 47],
    [48, 54, 24, 14, 55, 25],
    [42, 45, 15, 32, 46, 16],
    [20, 147, 117, 4, 148, 118],
    [40, 75, 47, 7, 76, 48],
    [43, 54, 24, 22, 55, 25],
    [10, 45, 15, 67, 46, 16],
    [19, 148, 118, 6, 149, 119],
    [18, 75, 47, 31, 76, 48],
    [34, 54, 24, 34, 55, 25],
    [20, 45, 15, 61, 46, 16]

]

def glog(n):
    if n < 1:  # pragma: no cover
        raise ValueError("glog(%s)" % n)
    return LOG_TABLE[n]


def gexp(n):
    return EXP_TABLE[n % 255]

class Polynomial:

    def __init__(self, num, shift):
        if not num:  # pragma: no cover
            raise Exception("%s/%s" % (len(num), shift))

        for offset in range(len(num)):
            if num[offset] != 0:
                break
        else:
            offset += 1

        self.num = num[offset:] + [0] * shift

    def __getitem__(self, index):
        return self.num[index]

    def __iter__(self):
        return iter(self.num)

    def __len__(self):
        return len(self.num)

    def __mul__(self, other):
        num = [0] * (len(self) + len(other) - 1)

        for i, item in enumerate(self):
            for j, other_item in enumerate(other):
                num[i + j] ^= gexp(glog(item) + glog(other_item))

        return Polynomial(num, 0)

    def __mod__(self, other):

        this = self

        while True:
            difference = len(this) - len(other)

            if difference < 0:
                break

            ratio = glog(this[0]) - glog(other[0])

            num = [
                item ^ gexp(glog(other_item) + ratio)
                for item, other_item in zip(this, other)]
            if difference:
                num.extend(this[-difference:])

            this = Polynomial(num, 0)

        return this

class RSBlock:

    def __init__(self, total_count, data_count):
        self.total_count = total_count
        self.data_count = data_count


def make_rs_blocks(version, error_correction):
    if error_correction not in RS_BLOCK_OFFSET:  # pragma: no cover
        raise Exception(
            "bad rs block @ version: %s / error_correction: %s" %
            (version, error_correction))
    offset = RS_BLOCK_OFFSET[error_correction]
    rs_block = RS_BLOCK_TABLE[(version - 1) * 4 + offset]

    blocks = []

    for i in range(0, len(rs_block), 3):
        count, total_count, data_count = rs_block[i:i + 3]
        for j in range(count):
            blocks.append(RSBlock(total_count, data_count))

    return blocks

MODE_NUMBER = 1 << 0
MODE_ALPHA_NUM = 1 << 1
MODE_8BIT_BYTE = 1 << 2
MODE_KANJI = 1 << 3
MODE_SIZE_SMALL = {
    MODE_NUMBER: 10,
    MODE_ALPHA_NUM: 9,
    MODE_8BIT_BYTE: 8,
    MODE_KANJI: 8,
}
MODE_SIZE_MEDIUM = {
    MODE_NUMBER: 12,
    MODE_ALPHA_NUM: 11,
    MODE_8BIT_BYTE: 16,
    MODE_KANJI: 10,
}
MODE_SIZE_LARGE = {
    MODE_NUMBER: 14,
    MODE_ALPHA_NUM: 13,
    MODE_8BIT_BYTE: 16,
    MODE_KANJI: 12,
}

ALPHA_NUM = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'
ESCAPED_ALPHA_NUM = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ\\ \\$\\%\\*\\+\\-\\.\\/\\:'

RE_ALPHA_NUM = re.compile(b'^[' + ESCAPED_ALPHA_NUM + b']*\Z')
NUMBER_LENGTH = {3: 10, 2: 7, 1: 4}

PATTERN_POSITION_TABLE = [
    [],
    [6, 18],
    [6, 22],
    [6, 26],
    [6, 30],
    [6, 34],
    [6, 22, 38],
    [6, 24, 42],
    [6, 26, 46],
    [6, 28, 50],
    [6, 30, 54],
    [6, 32, 58],
    [6, 34, 62],
    [6, 26, 46, 66],
    [6, 26, 48, 70],
    [6, 26, 50, 74],
    [6, 30, 54, 78],
    [6, 30, 56, 82],
    [6, 30, 58, 86],
    [6, 34, 62, 90],
    [6, 28, 50, 72, 94],
    [6, 26, 50, 74, 98],
    [6, 30, 54, 78, 102],
    [6, 28, 54, 80, 106],
    [6, 32, 58, 84, 110],
    [6, 30, 58, 86, 114],
    [6, 34, 62, 90, 118],
    [6, 26, 50, 74, 98, 122],
    [6, 30, 54, 78, 102, 126],
    [6, 26, 52, 78, 104, 130],
    [6, 30, 56, 82, 108, 134],
    [6, 34, 60, 86, 112, 138],
    [6, 30, 58, 86, 114, 142],
    [6, 34, 62, 90, 118, 146],
    [6, 30, 54, 78, 102, 126, 150],
    [6, 24, 50, 76, 102, 128, 154],
    [6, 28, 54, 80, 106, 132, 158],
    [6, 32, 58, 84, 110, 136, 162],
    [6, 26, 54, 82, 110, 138, 166],
    [6, 30, 58, 86, 114, 142, 170]
]

G15 = (
    (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) |
    (1 << 0))
G18 = (
    (1 << 12) | (1 << 11) | (1 << 10) | (1 << 9) | (1 << 8) | (1 << 5) |
    (1 << 2) | (1 << 0))
G15_MASK = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1)

PAD0 = 0xEC
PAD1 = 0x11
_data_count = lambda block: block.data_count
BIT_LIMIT_TABLE = [
    [0] + [8*sum(map(_data_count, make_rs_blocks(version, error_correction)))
           for version in range(1, 41)]
    for error_correction in range(4)
]

def BCH_type_info(data):
        d = data << 10
        while BCH_digit(d) - BCH_digit(G15) >= 0:
            d ^= (G15 << (BCH_digit(d) - BCH_digit(G15)))

        return ((data << 10) | d) ^ G15_MASK

def BCH_type_number(data):
    d = data << 12
    while BCH_digit(d) - BCH_digit(G18) >= 0:
        d ^= (G18 << (BCH_digit(d) - BCH_digit(G18)))
    return (data << 12) | d

def BCH_digit(data):
    digit = 0
    while data != 0:
        digit += 1
        data >>= 1
    return digit


def pattern_position(version):
    return PATTERN_POSITION_TABLE[version - 1]

def make_mask_func(pattern):

    if pattern == 0:   # 000
        return lambda i, j: (i + j) % 2 == 0
    if pattern == 1:   # 001
        return lambda i, j: i % 2 == 0
    if pattern == 2:   # 010
        return lambda i, j: j % 3 == 0
    if pattern == 3:   # 011
        return lambda i, j: (i + j) % 3 == 0
    if pattern == 4:   # 100
        return lambda i, j: (int(i / 2) + int(j / 3)) % 2 == 0
    if pattern == 5:  # 101
        return lambda i, j: (i * j) % 2 + (i * j) % 3 == 0
    if pattern == 6:  # 110
        return lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0
    if pattern == 7:  # 111
        return lambda i, j: ((i * j) % 3 + (i + j) % 2) % 2 == 0
    raise TypeError("Bad mask pattern: " + pattern)  # pragma: no cover

def mode_sizes_for_version(version):
    if version < 10:
        return MODE_SIZE_SMALL
    elif version < 27:
        return MODE_SIZE_MEDIUM
    else:
        return MODE_SIZE_LARGE

def length_in_bits(mode, version):
    if mode not in (
            MODE_NUMBER, MODE_ALPHA_NUM, MODE_8BIT_BYTE, MODE_KANJI):
        raise TypeError("Invalid mode (%s)" % mode)  # pragma: no cover

    if version < 1 or version > 40:  # pragma: no cover
        raise ValueError(
            "Invalid version (was %s, expected 1 to 40)" % version)

    return mode_sizes_for_version(version)[mode]

def make_lost_point(modules):
    modules_count = len(modules)

    lost_point = 0

    lost_point = _lost_point_level1(modules, modules_count)
    lost_point += _lost_point_level2(modules, modules_count)
    lost_point += _lost_point_level3(modules, modules_count)
    lost_point += _lost_point_level4(modules, modules_count)

    return lost_point

def _lost_point_level1(modules, modules_count):
    lost_point = 0

    modules_range = range(modules_count)
    container = [0] * (modules_count + 1)

    for row in modules_range:
        this_row = modules[row]
        previous_color = this_row[0]
        length = 0
        for col in modules_range:
            if this_row[col] == previous_color:
                length += 1
            else:
                if length >= 5:
                    container[length] += 1
                length = 1
                previous_color = this_row[col]
        if length >= 5:
            container[length] += 1

    for col in modules_range:
        previous_color = modules[0][col]
        length = 0
        for row in modules_range:
            if modules[row][col] == previous_color:
                length += 1
            else:
                if length >= 5:
                    container[length] += 1
                length = 1
                previous_color = modules[row][col]
        if length >= 5:
            container[length] += 1

    lost_point += sum(container[each_length] * (each_length - 2)
        for each_length in range(5, modules_count + 1))

    return lost_point

def _lost_point_level2(modules, modules_count):
    lost_point = 0

    modules_range = range(modules_count - 1)
    for row in modules_range:
        this_row = modules[row]
        next_row = modules[row + 1]
        modules_range_iter = iter(modules_range)
        for col in modules_range_iter:
            top_right = this_row[col + 1]
            if top_right != next_row[col + 1]:
                try:
                    next(modules_range_iter)
                except StopIteration:
                    pass
            elif top_right != this_row[col]:
                continue
            elif top_right != next_row[col]:
                continue
            else:
                lost_point += 3

    return lost_point

def _lost_point_level3(modules, modules_count):
    modules_range = range(modules_count)
    modules_range_short = range(modules_count-10)
    lost_point = 0

    for row in modules_range:
        this_row = modules[row]
        modules_range_short_iter = iter(modules_range_short)
        col = 0
        for col in modules_range_short_iter:
            if (
                        not this_row[col + 1]
                    and this_row[col + 4]
                    and not this_row[col + 5]
                    and this_row[col + 6]
                    and not this_row[col + 9]
                and (
                        this_row[col + 0]
                    and this_row[col + 2]
                    and this_row[col + 3]
                    and not this_row[col + 7]
                    and not this_row[col + 8]
                    and not this_row[col + 10]
                or
                        not this_row[col + 0]
                    and not this_row[col + 2]
                    and not this_row[col + 3]
                    and this_row[col + 7]
                    and this_row[col + 8]
                    and this_row[col + 10]
                    )
                ):
                lost_point += 40
            if this_row[col + 10]:
                try:
                    next(modules_range_short_iter)
                except StopIteration:
                    pass

    for col in modules_range:
        modules_range_short_iter = iter(modules_range_short)
        row = 0
        for row in modules_range_short_iter:
            if (
                        not modules[row + 1][col]
                    and modules[row + 4][col]
                    and not modules[row + 5][col]
                    and modules[row + 6][col]
                    and not modules[row + 9][col]
                and (
                        modules[row + 0][col]
                    and modules[row + 2][col]
                    and modules[row + 3][col]
                    and not modules[row + 7][col]
                    and not modules[row + 8][col]
                    and not modules[row + 10][col]
                or
                        not modules[row + 0][col]
                    and not modules[row + 2][col]
                    and not modules[row + 3][col]
                    and modules[row + 7][col]
                    and modules[row + 8][col]
                    and modules[row + 10][col]
                    )
                ):
                lost_point += 40
            if modules[row + 10][col]:
                try:
                    next(modules_range_short_iter)
                except StopIteration:
                    pass

    return lost_point

def _lost_point_level4(modules, modules_count):
    dark_count = sum(map(sum, modules))
    percent = float(dark_count) / (modules_count**2)
    rating = int(abs(percent * 100 - 50) / 5)
    return rating * 10

def optimal_data_chunks(data, minimum=4):

    data = to_bytestring(data)
    re_repeat = (
        b'{' + str(minimum).encode('ascii') + b',}')
    num_pattern = re.compile(b'\d' + re_repeat)
    num_bits = _optimal_split(data, num_pattern)
    alpha_pattern = re.compile(
        b'[' + ESCAPED_ALPHA_NUM + b']' + re_repeat)
    for is_num, chunk in num_bits:
        if is_num:
            yield QRData(chunk, mode=MODE_NUMBER, check_data=False)
        else:
            for is_alpha, sub_chunk in _optimal_split(chunk, alpha_pattern):
                if is_alpha:
                    mode = MODE_ALPHA_NUM
                else:
                    mode = MODE_8BIT_BYTE
                yield QRData(sub_chunk, mode=mode, check_data=False)

def _optimal_split(data, pattern):
    while data:
        match = pattern.search(data)
        if not match:
            break
        start, end = match.start(), match.end()
        if start:
            yield False, data[:start]
        yield True, data[start:end]
        data = data[end:]
    if data:
        yield False, data

def to_bytestring(data):

    if not isinstance(data, bytes):
        data = str(data).encode('utf-8')
    return data

def optimal_mode(data):

    if data.isdigit():
        return MODE_NUMBER
    if RE_ALPHA_NUM.match(data):
        return MODE_ALPHA_NUM
    return MODE_8BIT_BYTE

class QRData:

    def __init__(self, data, mode=None, check_data=True):

        if check_data:
            data = to_bytestring(data)

        if mode is None:
            self.mode = optimal_mode(data)
        else:
            self.mode = mode
            if mode not in (MODE_NUMBER, MODE_ALPHA_NUM, MODE_8BIT_BYTE):
                raise TypeError("Invalid mode (%s)" % mode)  # pragma: no cover
            if check_data and mode < optimal_mode(data):  # pragma: no cover
                raise ValueError(
                    "Provided data can not be represented in mode "
                    "{0}".format(mode))

        self.data = data

    def __len__(self):
        return len(self.data)

    def write(self, buffer):
        if self.mode == MODE_NUMBER:
            for i in range(0, len(self.data), 3):
                chars = self.data[i:i + 3]
                bit_length = NUMBER_LENGTH[len(chars)]
                buffer.put(int(chars), bit_length)
        elif self.mode == MODE_ALPHA_NUM:
            for i in range(0, len(self.data), 2):
                chars = self.data[i:i + 2]
                if len(chars) > 1:
                    buffer.put(
                        ALPHA_NUM.find(chars[0]) * 45 +
                        ALPHA_NUM.find(chars[1]), 11)
                else:
                    buffer.put(ALPHA_NUM.find(chars), 6)
        else:
            data = self.data
            for c in data:
                buffer.put(c, 8)

    def __repr__(self):
        return repr(self.data)

class BitBuffer:

    def __init__(self):
        self.buffer = []
        self.length = 0

    def __repr__(self):
        return ".".join([str(n) for n in self.buffer])

    def get(self, index):
        buf_index = int(index / 8)
        return ((self.buffer[buf_index] >> (7 - index % 8)) & 1) == 1

    def put(self, num, length):
        for i in range(length):
            self.put_bit(((num >> (length - i - 1)) & 1) == 1)

    def __len__(self):
        return self.length

    def put_bit(self, bit):
        buf_index = self.length // 8
        if len(self.buffer) <= buf_index:
            self.buffer.append(0)
        if bit:
            self.buffer[buf_index] |= (0x80 >> (self.length % 8))
        self.length += 1

def create_bytes(buffer, rs_blocks):
    offset = 0

    maxDcCount = 0
    maxEcCount = 0

    dcdata = [0] * len(rs_blocks)
    ecdata = [0] * len(rs_blocks)

    for r in range(len(rs_blocks)):

        dcCount = rs_blocks[r].data_count
        ecCount = rs_blocks[r].total_count - dcCount

        maxDcCount = max(maxDcCount, dcCount)
        maxEcCount = max(maxEcCount, ecCount)

        dcdata[r] = [0] * dcCount

        for i in range(len(dcdata[r])):
            dcdata[r][i] = 0xff & buffer.buffer[i + offset]
        offset += dcCount
        if ecCount in rsPoly_LUT:
            rsPoly = Polynomial(rsPoly_LUT[ecCount], 0)
        else:
            rsPoly = Polynomial([1], 0)
            for i in range(ecCount):
                rsPoly = rsPoly * Polynomial([1, gexp(i)], 0)

        rawPoly = Polynomial(dcdata[r], len(rsPoly) - 1)

        modPoly = rawPoly % rsPoly
        ecdata[r] = [0] * (len(rsPoly) - 1)
        for i in range(len(ecdata[r])):
            modIndex = i + len(modPoly) - len(ecdata[r])
            if (modIndex >= 0):
                ecdata[r][i] = modPoly[modIndex]
            else:
                ecdata[r][i] = 0

    totalCodeCount = 0
    for rs_block in rs_blocks:
        totalCodeCount += rs_block.total_count

    data = [None] * totalCodeCount
    index = 0

    for i in range(maxDcCount):
        for r in range(len(rs_blocks)):
            if i < len(dcdata[r]):
                data[index] = dcdata[r][i]
                index += 1

    for i in range(maxEcCount):
        for r in range(len(rs_blocks)):
            if i < len(ecdata[r]):
                data[index] = ecdata[r][i]
                index += 1

    return data

def create_data(version, error_correction, data_list):

    buffer = BitBuffer()
    for data in data_list:
        buffer.put(data.mode, 4)
        buffer.put(len(data), length_in_bits(data.mode, version))
        data.write(buffer)
    rs_blocks = make_rs_blocks(version, error_correction)
    bit_limit = 0
    for block in rs_blocks:
        bit_limit += block.data_count * 8

    if len(buffer) > bit_limit:
        raise exceptions.DataOverflowError(
            "Code length overflow. Data size (%s) > size available (%s)" %
            (len(buffer), bit_limit))
    for i in range(min(bit_limit - len(buffer), 4)):
        buffer.put_bit(False)
    delimit = len(buffer) % 8
    if delimit:
        for i in range(8 - delimit):
            buffer.put_bit(False)
    bytes_to_fill = (bit_limit - len(buffer)) // 8
    for i in range(bytes_to_fill):
        if i % 2 == 0:
            buffer.put(PAD0, 8)
        else:
            buffer.put(PAD1, 8)

    return create_bytes(buffer, rs_blocks)

def make(data=None, **kwargs):
    qr = QRCode(**kwargs)
    qr.add_data(data)
    return qr.make_image()


def _check_version(version):
    if version < 1 or version > 40:
        raise ValueError(
            "Invalid version (was %s, expected 1 to 40)" % version)

def _check_box_size(size):
    if int(size) <= 0:
        raise ValueError(
            "Invalid box size (was %s, expected larger than 0)" % size)

def _check_mask_pattern(mask_pattern):
    if mask_pattern is None:
        return
    if not isinstance(mask_pattern, int):
        raise TypeError(
            "Invalid mask pattern (was %s, expected int)" % type(mask_pattern))
    if mask_pattern < 0 or mask_pattern > 7:
        raise ValueError(
            "Mask pattern should be in range(8) (got %s)" % mask_pattern)

class QRCode:

    def __init__(self, version=None,
                 error_correction=ERROR_CORRECT_M,
                 box_size=10, border=4,
                 mask_pattern=None):
        _check_box_size(box_size)
        self.version = version and int(version)
        self.error_correction = int(error_correction)
        self.box_size = int(box_size)
        self.border = int(border)
        _check_mask_pattern(mask_pattern)
        self.mask_pattern = mask_pattern

        self.clear()

    def clear(self):

        self.modules = None
        self.modules_count = 0
        self.data_cache = None
        self.data_list = []

    def add_data(self, data, optimize=20):

        if isinstance(data, QRData):
            self.data_list.append(data)
        else:
            if optimize:
                self.data_list.extend(
                    optimal_data_chunks(data, minimum=optimize))
            else:
                self.data_list.append(QRData(data))
        self.data_cache = None

    def make(self, fit=True):

        if fit or (self.version is None):
            self.best_fit(start=self.version)
        if self.mask_pattern is None:
            self.makeImpl(False, self.best_mask_pattern())
        else:
            self.makeImpl(False, self.mask_pattern)

    def makeImpl(self, test, mask_pattern):
        _check_version(self.version)
        self.modules_count = self.version * 4 + 17
        self.modules = [None] * self.modules_count

        for row in range(self.modules_count):

            self.modules[row] = [None] * self.modules_count

            for col in range(self.modules_count):
                self.modules[row][col] = None   # (col + row) % 3

        self.setup_position_probe_pattern(0, 0)
        self.setup_position_probe_pattern(self.modules_count - 7, 0)
        self.setup_position_probe_pattern(0, self.modules_count - 7)
        self.setup_position_adjust_pattern()
        self.setup_timing_pattern()
        self.setup_type_info(test, mask_pattern)

        if self.version >= 7:
            self.setup_type_number(test)

        if self.data_cache is None:
            self.data_cache = create_data(
                self.version, self.error_correction, self.data_list)
        self.map_data(self.data_cache, mask_pattern)

    def setup_position_probe_pattern(self, row, col):
        for r in range(-1, 8):

            if row + r <= -1 or self.modules_count <= row + r:
                continue

            for c in range(-1, 8):

                if col + c <= -1 or self.modules_count <= col + c:
                    continue

                if (0 <= r and r <= 6 and (c == 0 or c == 6)
                        or (0 <= c and c <= 6 and (r == 0 or r == 6))
                        or (2 <= r and r <= 4 and 2 <= c and c <= 4)):
                    self.modules[row + r][col + c] = True
                else:
                    self.modules[row + r][col + c] = False

    def best_fit(self, start=None):

        if start is None:
            start = 1
        _check_version(start)
        mode_sizes = mode_sizes_for_version(start)
        buffer = BitBuffer()
        for data in self.data_list:
            buffer.put(data.mode, 4)
            buffer.put(len(data), mode_sizes[data.mode])
            data.write(buffer)

        needed_bits = len(buffer)

        self.version = start
        end = len(BIT_LIMIT_TABLE[self.error_correction])

        while (self.version < end and
               needed_bits > BIT_LIMIT_TABLE[self.error_correction][self.version]):
            self.version += 1

        if self.version == 41:
            raise DataOverflowError()
        if mode_sizes is not mode_sizes_for_version(self.version):
            self.best_fit(start=self.version)
        return self.version

    def best_mask_pattern(self):

        min_lost_point = 0
        pattern = 0

        for i in range(8):
            self.makeImpl(True, i)

            lost_point = make_lost_point(self.modules)

            if i == 0 or min_lost_point > lost_point:
                min_lost_point = lost_point
                pattern = i

        return pattern

    def setup_timing_pattern(self):
        for r in range(8, self.modules_count - 8):
            if self.modules[r][6] is not None:
                continue
            self.modules[r][6] = (r % 2 == 0)

        for c in range(8, self.modules_count - 8):
            if self.modules[6][c] is not None:
                continue
            self.modules[6][c] = (c % 2 == 0)

    def setup_position_adjust_pattern(self):
        pos = pattern_position(self.version)

        for i in range(len(pos)):

            for j in range(len(pos)):

                row = pos[i]
                col = pos[j]

                if self.modules[row][col] is not None:
                    continue

                for r in range(-2, 3):

                    for c in range(-2, 3):

                        if (r == -2 or r == 2 or c == -2 or c == 2 or
                                (r == 0 and c == 0)):
                            self.modules[row + r][col + c] = True
                        else:
                            self.modules[row + r][col + c] = False

    def setup_type_number(self, test):
        bits = BCH_type_number(self.version)

        for i in range(18):
            mod = (not test and ((bits >> i) & 1) == 1)
            self.modules[i // 3][i % 3 + self.modules_count - 8 - 3] = mod

        for i in range(18):
            mod = (not test and ((bits >> i) & 1) == 1)
            self.modules[i % 3 + self.modules_count - 8 - 3][i // 3] = mod

    def setup_type_info(self, test, mask_pattern):
        data = (self.error_correction << 3) | mask_pattern
        bits = BCH_type_info(data)
        for i in range(15):

            mod = (not test and ((bits >> i) & 1) == 1)

            if i < 6:
                self.modules[i][8] = mod
            elif i < 8:
                self.modules[i + 1][8] = mod
            else:
                self.modules[self.modules_count - 15 + i][8] = mod
        for i in range(15):

            mod = (not test and ((bits >> i) & 1) == 1)

            if i < 8:
                self.modules[8][self.modules_count - i - 1] = mod
            elif i < 9:
                self.modules[8][15 - i - 1 + 1] = mod
            else:
                self.modules[8][15 - i - 1] = mod
        self.modules[self.modules_count - 8][8] = (not test)

    def map_data(self, data, mask_pattern):
        inc = -1
        row = self.modules_count - 1
        bitIndex = 7
        byteIndex = 0

        mask_func = make_mask_func(mask_pattern)

        data_len = len(data)

        for col in range(self.modules_count - 1, 0, -2):

            if col <= 6:
                col -= 1

            col_range = (col, col-1)

            while True:

                for c in col_range:

                    if self.modules[row][c] is None:

                        dark = False

                        if byteIndex < data_len:
                            dark = (((data[byteIndex] >> bitIndex) & 1) == 1)

                        if mask_func(row, c):
                            dark = not dark

                        self.modules[row][c] = dark
                        bitIndex -= 1

                        if bitIndex == -1:
                            byteIndex += 1
                            bitIndex = 7

                row += inc

                if row < 0 or self.modules_count <= row:
                    row -= inc
                    inc = -inc
                    break

    def get_matrix(self):

        if self.data_cache is None:
            self.make()

        if not self.border:
            return self.modules

        width = len(self.modules) + self.border*2
        code = [[False]*width] * self.border
        x_border = [False]*self.border
        for module in self.modules:
            code.append(x_border + module + x_border)
        code += [[False]*width] * self.border

        return code