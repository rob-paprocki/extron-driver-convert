# Copyright 2026, Extron. All rights reserved.

import json
import random
import urllib.error
import urllib.request

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

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
        self._DisplaySystemID = '1'
        self._NumberofPowerBoxEntries = 5
        self._NumberofSensorHostEntries = 5
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveSource': { 'Status': {}},
            'Luminance': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerBoxCurrentStatus': {'Parameters': ['Button'], 'Status': {}},
            'PowerBoxNavigation': { 'Status': {}},
            'PowerBoxOnlineStatus': {'Parameters': ['Button'], 'Status': {}},
            'PowerBoxProductNameStatus': {'Parameters': ['Button'], 'Status': {}},
            'PowerBoxUpdate': { 'Status': {}},
            'SensorHostAmbientLightSensorStatus': {'Parameters': ['Button'], 'Status': {}},
            'SensorHostIDStatus': {'Parameters': ['Button'], 'Status': {}},
            'SensorHostNavigation': { 'Status': {}},
            'SensorHostOnlineStatus': {'Parameters': ['Button'], 'Status': {}},
            'SensorHostSerialNumberStatus': {'Parameters': ['Button'], 'Status': {}},
            'SensorHostTemperatureStatus': {'Parameters': ['Button'], 'Status': {}},
            'SensorHostUpdate': { 'Status': {}},
        }

        self.powerAdvance = True
        self.powerBoxList = []
        self.powerBoxListStartingEntry = 0
        self.sensorAdvance = True
        self.sensorHostList = []
        self.sensorHostListStartingEntry = 0
        
        self.power_box_scroller = Scroller([], self._NumberofPowerBoxEntries, end='*** End of List ***')
        self.sensor_host_scroller = Scroller([], self._NumberofSensorHostEntries, end='*** End of List ***')
        
    @property
    def DisplaySystemID(self):
        return self._DisplaySystemID

    @DisplaySystemID.setter
    def DisplaySystemID(self, value):
        if int(value) == 0:
            self._DisplaySystemID = ''
        elif 1 <= int(value) <= 9999:
            self._DisplaySystemID = str(value)
        else:
            self.Error(['Display System ID Parameter is set to a wrong value.'])

    @property
    def NumberofPowerBoxEntries(self):
        return self._NumberofPowerBoxEntries

    @NumberofPowerBoxEntries.setter
    def NumberofPowerBoxEntries(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofPowerBoxEntries = value
            self.power_box_scroller = Scroller([], self._NumberofPowerBoxEntries, end='*** End of List ***')
        else:
            self.Error(['Missing Number of Power Box Entries Parameter.'])

    @property
    def NumberofSensorHostEntries(self):
        return self._NumberofSensorHostEntries

    @NumberofSensorHostEntries.setter
    def NumberofSensorHostEntries(self, value):
        self._NumberofSensorHostEntries = value
        if 1 <= int(value) <= 15:
            self._NumberofSensorHostEntries = value
            self.sensor_host_scroller = Scroller([], self._NumberofSensorHostEntries, end='*** End of List ***')
        else:
            self.Error(['Missing Number of Sensor Host Entries Parameter.'])

    def refresh_power_box_status(self):
        for button, entry in enumerate(self.power_box_scroller, 1):
            if entry not in [self.power_box_scroller.end, self.power_box_scroller.fill]:
                self.WriteStatus('PowerBoxCurrentStatus', entry['CurrentState'], {'Button': button})
                self.WriteStatus('PowerBoxOnlineStatus', str(entry['IsOnline']), {'Button': button})
                self.WriteStatus('PowerBoxProductNameStatus', entry['ProductName'], {'Button': button})
            else:
                self.WriteStatus('PowerBoxCurrentStatus', entry, {'Button': button})
                self.WriteStatus('PowerBoxOnlineStatus', entry, {'Button': button})
                self.WriteStatus('PowerBoxProductNameStatus', entry, {'Button': button})

    def refresh_sensor_host_status(self):
        for button, entry in enumerate(self.sensor_host_scroller, 1):
            if entry not in [self.sensor_host_scroller.end, self.sensor_host_scroller.fill]:
                self.WriteStatus('SensorHostAmbientLightSensorStatus', str(entry['AmbientLightSensors']), {'Button': button})
                self.WriteStatus('SensorHostIDStatus', entry['ID'], {'Button': button})
                self.WriteStatus('SensorHostOnlineStatus', str(entry['IsOnline']), {'Button': button})
                self.WriteStatus('SensorHostSerialNumberStatus', entry['SerialNumber'], {'Button': button})
                self.WriteStatus('SensorHostTemperatureStatus', str(entry['Temperatures']), {'Button': button})
            else:
                self.WriteStatus('SensorHostAmbientLightSensorStatus', entry, {'Button': button})
                self.WriteStatus('SensorHostIDStatus', entry, {'Button': button})
                self.WriteStatus('SensorHostOnlineStatus', entry, {'Button': button})
                self.WriteStatus('SensorHostSerialNumberStatus', entry, {'Button': button})
                self.WriteStatus('SensorHostTemperatureStatus', entry, {'Button': button})

    def SetActiveSource(self, value, qualifier):

        ValueStateValues = {
            'HDMI':         'hdmi',
            'SDI':          'sdi',
            'Test Pattern': 'testpattern'
        }

        if value in ValueStateValues:
            uri = 'webapi/JsonRPC'
            data = {
                'jsonrpc':  '2.0',
                'method':   'SetActiveSource',
                'params':   {
                    'DisplaySystemIds': self._DisplaySystemID,
                    'Source':           ValueStateValues[value]
                },
                'id':       str(random.randint(1000, 10000))
            }

            if self._DisplaySystemID == '':
                del data['params']['DisplaySystemIds']

            data = json.dumps(data, separators=(',', ':')).encode()

            self.__SetHelper('ActiveSource', value, qualifier, uri, data)
        else:
            self.Discard('Invalid Command for SetActiveSource')

    def UpdateActiveSource(self, value, qualifier):

        ValueStateValues = {
            'hdmi':         'HDMI',
            'sdi':          'SDI',
            'testpattern':  'Test Pattern'
        }

        uri = 'webapi/JsonRPC'
        data = json.dumps({
            'jsonrpc':  '2.0',
            'method':   'GetActiveSource',
            'params':   {
                'DisplaySystemId': self._DisplaySystemID
            },
            'id':       str(random.randint(1000, 10000))
        }, separators=(',', ':')).encode()

        res = self.__UpdateHelper('ActiveSource', value, qualifier, uri, data)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('ActiveSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Active Source: Invalid/unexpected response'])

    def SetLuminance(self, value, qualifier):

        if 0 <= value <= 880:
            uri = 'webapi/JsonRPC'
            data = {
                'jsonrpc':  '2.0',
                'method':   'SetLuminance',
                'params':   {
                    'DisplaySystemIds': self._DisplaySystemID,
                    'Value':            int(value)
                },
                'id':       str(random.randint(1000, 10000))
            }

            if self._DisplaySystemID == '':
                del data['params']['DisplaySystemIds']

            data = json.dumps(data, separators=(',', ':')).encode()

            self.__SetHelper('Luminance', value, qualifier, uri, data)
        else:
            self.Discard('Invalid Command for SetLuminance')

    def UpdateLuminance(self, value, qualifier):

        uri = 'webapi/JsonRPC'
        data = json.dumps({
            'jsonrpc':  '2.0',
            'method':   'GetLuminance',
            'params':   {
                'DisplaySystemId': self._DisplaySystemID
            },
            'id':       str(random.randint(1000, 10000))
        }, separators=(',', ':')).encode()

        res = self.__UpdateHelper('Luminance', value, qualifier, uri, data)
        if res:
            try:
                value = int(res['result']['CurrentValue'])
                if 0 <= value <= 880:
                    self.WriteStatus('Luminance', value, qualifier)
            except (ValueError, KeyError):
                self.Error(['Luminance: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   False,
            'Off':  True
        }

        if value in ValueStateValues:
            uri = 'webapi/JsonRPC'
            data = {
                'jsonrpc':  '2.0',
                'method':   'SetStandbyState',
                'params':   {
                    'DisplaySystemIds': self._DisplaySystemID,
                    'IsStandby':        ValueStateValues[value]
                },
                'id':       str(random.randint(1000, 10000))
            }

            if self._DisplaySystemID == '':
                del data['params']['DisplaySystemIds']

            data = json.dumps(data, separators=(',', ':')).encode()

            self.__SetHelper('Power', value, qualifier, uri, data)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'Running':      'On',
            'Standby':      'Off',
            'Undefined':    'Undefined'
        }

        uri = 'webapi/JsonRPC'
        data = json.dumps({
            'jsonrpc':  '2.0',
            'method':   'GetStandbyState',
            'params':   {
                'DisplaySystemId': self._DisplaySystemID
            },
            'id':       str(random.randint(1000, 10000))
        }, separators=(',', ':')).encode()

        res = self.__UpdateHelper('Power', value, qualifier, uri, data)
        if res:
            try:
                value = ValueStateValues[res['result']]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPowerBoxNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.power_box_scroller.previous,
            'Down':         self.power_box_scroller.next,
            'Page Up':      self.power_box_scroller.previous_page,
            'Page Down':    self.power_box_scroller.next_page
        }

        if value in ValueStateValues and self.power_box_scroller.current_size > 0:
            ValueStateValues[value]()
            self.refresh_power_box_status()
        else:
            self.Discard('Invalid Command for SetPowerBoxNavigation')
            
    def SetPowerBoxUpdate(self, value, qualifier):

        uri = 'webapi/JsonRPC'
        data = json.dumps({
            'jsonrpc':  '2.0',
            'method':   'GetPowerBoxInfo',
            'params':   {
                'DisplaySystemId': self._DisplaySystemID
            },
            'id':       str(random.randint(1000, 10000))
        }, separators=(',', ':')).encode()

        res = self.__UpdateHelper('PowerBoxUpdate', value, qualifier, uri, data)
        if res:
            try:
                self.power_box_scroller.overwrite(res['result'])
                self.refresh_power_box_status()
            except KeyError:
                self.Error(['Power Box Update: Invalid/unexpected response'])
                
    def SetSensorHostNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.sensor_host_scroller.previous,
            'Down':         self.sensor_host_scroller.next,
            'Page Up':      self.sensor_host_scroller.previous_page,
            'Page Down':    self.sensor_host_scroller.next_page
        }

        if value in ValueStateValues and self.sensor_host_scroller.current_size > 0:
            ValueStateValues[value]()
            self.refresh_sensor_host_status()
        else:
            self.Discard('Invalid Command for SetSensorHostNavigation')
            
    def SetSensorHostUpdate(self, value, qualifier):

        uri = 'webapi/JsonRPC'
        data = json.dumps({
            'jsonrpc':  '2.0',
            'method':   'GetSensorHostInfo',
            'params':   {
                'DisplaySystemId': self._DisplaySystemID
            },
            'id':       str(random.randint(1000, 10000))
        }, separators=(',', ':')).encode()

        res = self.__UpdateHelper('SensorHostUpdate', value, qualifier, uri, data)
        if res:
            try:
                self.sensor_host_scroller.overwrite(res['result'])
                self.refresh_sensor_host_status()
            except KeyError:
                self.Error(['Sensor Host Update: Invalid/unexpected response'])
                
    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = json.loads(response.read().decode())

            if 'error' not in response:
                return response

            self.Error(['An error occurred: {}: {}'.format(response['error']['code'], response['error']['message'])])
            return {}
        except json.decoder.JSONDecodeError:
            return {}

    def __SetHelper(self, command, value, qualifier, url, data=None):
        
        self.Debug = True

        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers=headers, method='POST')
        
        try:
            res = self.Opener.open(my_request, timeout=10)
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

        if self._DisplaySystemID != '':
            
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            url = '{0}{1}'.format(self.RootURL, url)
            headers = {'Content-Type': 'application/json'}
            my_request = urllib.request.Request(''.join([self.RootURL, url]), data=data, headers=headers, method='POST')

            try:
                res = self.Opener.open(my_request, timeout=10)
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
        else:
            self.Discard('Inappropriate Command ' + command)

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