import base64
import urllib.error
import urllib.request
import json

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'RLNK-P415': self.matl_20_4701_4,
            'RLNK-P420': self.matl_20_4701_4,
            'RLNK-P920R-SP': self.matl_20_4701_9,
            'RLNK-P915R-SP': self.matl_20_4701_9,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Current': { 'Status': {}},
            'Firmware': { 'Status': {}},
            'Frequency': { 'Status': {}},
            'OutletControl': {'Parameters':['Outlet'], 'Status': {}},
            'OutletCurrent': {'Parameters':['Outlet'], 'Status': {}},
            'OutletVoltage': {'Parameters':['Outlet'], 'Status': {}},
            'PowerkVA': { 'Status': {}},
            'SurgeProtectorStatus': { 'Status': {}},
            'TotalCurrentDraw': { 'Status': {}},
            'Voltage': { 'Status': {}},
        }

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = 'model/pdu/0'
        data = {
                "jsonrpc" : "2.0",
                "method": "getMetaData",
                "id": 42
        }

        res = self.__UpdateHelper('Firmware', value, qualifier, FirmwareCmdString, data=data)
        if res:
            try:
                value = res['result']['_ret_']['fwRevision']
                self.WriteStatus('Firmware', value, qualifier)
                current = res['result']['_ret_']['nameplate']['rating']['current']
                self.WriteStatus('Current', current, qualifier)
                frequency = res['result']['_ret_']['nameplate']['rating']['frequency']
                self.WriteStatus('Frequency', frequency, qualifier)
                power = res['result']['_ret_']['nameplate']['rating']['power']
                self.WriteStatus('PowerkVA', power, qualifier)
                voltage = res['result']['_ret_']['nameplate']['rating']['voltage']
                self.WriteStatus('Voltage', voltage, qualifier)
            except (ValueError, IndexError, KeyError):
                self.Error(['Firmware: Invalid/unexpected response'])

    def SetOutletControl(self, value, qualifier):

        ValueStateValues = {
            'On'  : 1,
            'Off' : 0
        }

        if value in ValueStateValues and 1 <= int(qualifier['Outlet']) <= self.OutletSize:
            data = {
                "jsonrpc" : "2.0",
                "method" : "setPowerState",
                "params" : {
                    "pstate" : ValueStateValues[value]
                },
                "id" : 23
            }

            OutletControlCmdString = 'model/pdu/0/outlet/{}'.format(int(qualifier['Outlet']) - 1)
            self.__SetHelper('OutletControl', value, qualifier, OutletControlCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def UpdateOutletControl(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= self.OutletSize:
            data = {
                "jsonrpc" : "2.0",
                "method" : "getState", 
                "id" : 23
            }

            OutletControlCmdString = 'model/pdu/0/outlet/{}'.format(int(qualifier['Outlet']) - 1)
            res = self.__UpdateHelper('OutletControl', value, qualifier, url=OutletControlCmdString, data=data)
            if res:
                try:
                    ValueStateValues = {
                        1 : 'On',
                        0 : 'Off'
                    }

                    value = ValueStateValues[res['result']['_ret_']['powerState']]
                    self.WriteStatus('OutletControl', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Outlet Control: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletControl')

    def UpdateOutletCurrent(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= self.OutletSize:
            data = {
                "jsonrpc" : "2.0",
                "method" : "getReading",
                "id" : 23
            }

            OutletCurrentCmdString = 'model/pdu/0/outlet/{}/current'.format(int(qualifier['Outlet']) - 1)
            res = self.__UpdateHelper('OutletCurrent', value, qualifier, url=OutletCurrentCmdString, data=data)
            if res:
                try:
                    value = round(res['result']['_ret_']['value'], 3)
                    self.WriteStatus('OutletCurrent', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Outlet Current: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletCurrent')

    def UpdateOutletVoltage(self, value, qualifier):

        if 1 <= int(qualifier['Outlet']) <= self.OutletSize:
            data = {
                "jsonrpc" : "2.0",
                "method" : "getReading",
                "id" : 23
            }

            OutletVoltageCmdString = 'model/pdu/0/outlet/{}/voltage'.format(int(qualifier['Outlet']) - 1)
            res = self.__UpdateHelper('OutletVoltage', value, qualifier, url=OutletVoltageCmdString, data=data)
            if res:
                try:
                    value = round(res['result']['_ret_']['value'], 3)
                    self.WriteStatus('OutletVoltage', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Outlet Voltage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutletVoltage')

    def UpdateSurgeProtectorStatus(self, value, qualifier):

        data = {
            "jsonrpc" : "2.0",
            "method" : "getSensors",
            "id" : 23
        }

        SurgeProtectorStatusCmdString = 'model/pdu/0/inlet/0'
        res = self.__UpdateHelper('SurgeProtectorStatus', value, qualifier, url=SurgeProtectorStatusCmdString, data=data)
        if res:
            try:
                value = str(res['result']['_ret_']['surgeProtectorStatus'])
                self.WriteStatus('SurgeProtectorStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Surge Protector Status: Invalid/unexpected response'])

    def UpdateTotalCurrentDraw(self, value, qualifier):

        data = {
            "jsonrpc" : "2.0",
            "method" : "getReading",
            "id" : 23
        }
        
        TotalCurrentDrawCmdString = 'model/pdu/0/inlet/0/current'
        res = self.__UpdateHelper('TotalCurrentDraw', value, qualifier, url=TotalCurrentDrawCmdString, data=data)
        if res:
            try:
                value = round(res['result']['_ret_']['value'], 3)
                self.WriteStatus('TotalCurrentDraw', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Total Current Draw: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            try:
                res = json.loads(response.read().decode())
            except json.decoder.JSONDecodeError:
                self.Error(['{}: Invalid Response'.format(sourceCmdName)])
                res = ''
            return res
        return response

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}{1}'.format(self.RootURL, url)

        headers = {
            'Content-Type'  : 'text/plain',
            'Authorization' : self.authentication
        }

        if data:  # If command body exists, encode it
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}{1}'.format(self.RootURL, url)

        headers = {
            'Content-Type'  : 'text/plain',
            'Authorization' : self.authentication
        }

        if data:  # If command body exists, encode it
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request, timeout=10) # open() returns a http.client.HTTPResponse object if successful
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

    def matl_20_4701_4(self):
        self.OutletSize = 4

    def matl_20_4701_9(self):
        self.OutletSize = 9

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
