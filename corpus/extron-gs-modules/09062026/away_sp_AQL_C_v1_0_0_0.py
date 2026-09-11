import urllib.error
import urllib.request
import base64
from collections import defaultdict
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
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AuxiliaryLayerSource': {'Parameters': ['Auxiliary', 'Target', 'Source Type'], 'Status': {}},
            'AuxiliaryLayerSourceID': {'Parameters': ['Auxiliary', 'Target'], 'Status': {}},
            'AuxiliaryLayerSourceStatus': {'Parameters': ['Auxiliary', 'Target'], 'Status': {}},
            'AuxiliaryLayerSourceType': {'Parameters': ['Auxiliary', 'Target'], 'Status': {}},
            'AuxiliaryPresetRecall': {'Parameters': ['Auxiliary', 'Target'], 'Status': {}},
            'AuxiliarySingleTake': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'GlobalTake': {'Parameters': ['Screens', 'Auxiliary Screens'], 'Status': {}},
            'MasterPresetRecall': {'Parameters': ['Target'], 'Status': {}},
            'MultiviewerPresetRecall': {'Parameters': ['Multiviewer'], 'Status': {}},
            'MultiviewerSource': {'Parameters': ['Multiviewer', 'Widget', 'Source Type'], 'Status': {}},
            'MultiviewerSourceID': {'Parameters': ['Multiviewer', 'Widget'], 'Status': {}},
            'MultiviewerSourceType': {'Parameters': ['Multiviewer', 'Widget'], 'Status': {}},
            'ScreenLayerSource': {'Parameters': ['Screen', 'Layer', 'Target', 'Source Type'], 'Status': {}},
            'ScreenLayerSourceID': {'Parameters': ['Screen', 'Layer', 'Target'], 'Status': {}},
            'ScreenLayerSourceStatus': {'Parameters': ['Screen', 'Layer', 'Target'], 'Status': {}},
            'ScreenLayerSourceType': {'Parameters': ['Screen', 'Layer', 'Target'], 'Status': {}},
            'ScreenPresetRecall': {'Parameters': ['Screen', 'Target'], 'Status': {}},
            'ScreenSingleTake': {'Status': {}},
        }

    def SetAuxiliaryLayerSource(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        SourceTypeStates = {
            'None',
            'Input',
            'Image',
            'Screen',
        }

        auxiliary = qualifier['Auxiliary']
        target = qualifier['Target']
        source_type = qualifier['Source Type']

        if all([1 <= auxiliary <= 16,
                target in TargetStates,
                source_type in SourceTypeStates,
                1 <= value <= 16]):
            AuxiliaryLayerSourceCmdString = '/api/tpp/v1/auxiliary-screens/{auxiliary}/layers/1/presets/{target}/source'.format(auxiliary=int(auxiliary), target=target.lower())
            data = {
                'sourceType': source_type.lower(),
                'sourceId': int(value)
            }

            self.__SetHelper('AuxiliaryLayerSource', value, qualifier, url=AuxiliaryLayerSourceCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAuxiliaryLayerSource')

    def UpdateAuxiliaryLayerSourceID(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        auxiliary = qualifier['Auxiliary']
        target = qualifier['Target']

        if 1 <= auxiliary <= 16 and target in TargetStates:
            AuxiliaryLayerSourceIDCmdString = '/api/tpp/v1/auxiliary-screens/{auxiliary}/layers/1/presets/{target}/source'.format(auxiliary=int(auxiliary), target=target.lower())
            res = self.__UpdateHelper('AuxiliaryLayerSourceID', value, qualifier, url=AuxiliaryLayerSourceIDCmdString)
            if res:
                try:
                    value = int(res['sourceId'])
                    self.WriteStatus('AuxiliaryLayerSourceID', value, qualifier)
                except (ValueError, KeyError):
                    self.Error(['Auxiliary Layer Source ID: Invalid/unexpected response'])

                try:
                    ValueStateValues = {
                        'off': 'Off',
                        'open': 'Open',
                        'close': 'Close',
                        'out of capacity': 'Out of Capacity'
                    }

                    value = ValueStateValues[res['status']]
                    self.WriteStatus('AuxiliaryLayerSourceStatus', value, qualifier)
                except KeyError:
                    self.Error(['Auxiliary Layer Source Status: Invalid/unexpected response'])

                try:
                    ValueStateValues = {
                        'none': 'None',
                        'input': 'Input',
                        'image': 'Image',
                        'screen': 'Screen'
                    }

                    value = ValueStateValues[res['sourceType']]
                    self.WriteStatus('AuxiliaryLayerSourceType', value, qualifier)
                except KeyError:
                    self.Error(['Auxiliary Layer Source Type: Invalid/unexpected response'])
            else:
                self.Discard('Device Is Busy for UpdateAuxiliaryLayerSourceID')
        else:
            self.Discard('Device Is Busy for UpdateAuxiliaryLayerSourceID')

    def UpdateAuxiliaryLayerSourceStatus(self, value, qualifier):

        self.UpdateAuxiliaryLayerSourceID(value, qualifier)

    def UpdateAuxiliaryLayerSourceType(self, value, qualifier):

        self.UpdateAuxiliaryLayerSourceID(value, qualifier)

    def SetAuxiliaryPresetRecall(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        auxiliary = qualifier['Auxiliary']
        target = qualifier['Target']

        if 1 <= auxiliary <= 16 and target in TargetStates and 1 <= value <= 1000:
            AuxiliaryPresetRecallCmdString = '/api/tpp/v1/auxiliary-screens/{auxiliary}/load-memory'.format(auxiliary=int(auxiliary))
            data = {
                'memoryId': int(value),
                'target': target.lower()
            }

            self.__SetHelper('AuxiliaryPresetRecall', value, qualifier, url=AuxiliaryPresetRecallCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetAuxiliaryPresetRecall')

    def SetAuxiliarySingleTake(self, value, qualifier):

        if 1 <= value <= 16:
            AuxiliarySingleTakeCmdString = '/api/tpp/v1/auxiliary-screens/{auxiliary}/take'.format(auxiliary=int(value))
            self.__SetHelper('AuxiliarySingleTake', value, qualifier, url=AuxiliarySingleTakeCmdString)
        else:
            self.Discard('Invalid Command for SetAuxiliarySingleTake')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '/api/tpp/v1/system'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res:
            try:
                res = res['version']
                value = '{}.{}.{}'.format(int(res['major']), int(res['minor']), int(res['patch']))
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, KeyError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetGlobalTake(self, value, qualifier):

        screens = qualifier['Screens'].strip()
        auxiliary_screens = qualifier['Auxiliary Screens'].strip()

        try:
            screens = list(set(int(screen) for screen in screens.split(',') if screen))
            auxiliary_screens = list(set(int(aux) for aux in auxiliary_screens.split(',') if aux))
        except BaseException:
            self.Discard('Invalid Command for SetGlobalTake')
            return
        if (screens or auxiliary_screens) and all(1 <= i <= 16 for i in (screens + auxiliary_screens)):
            GlobalTakeCmdString = '/api/tpp/v1/take'
            data = {
                'screenIds': screens,
                'auxiliaryScreenIds': auxiliary_screens
            }

            self.__SetHelper('GlobalTake', value, qualifier, url=GlobalTakeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetGlobalTake')

    def SetMasterPresetRecall(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        target = qualifier['Target']

        if target in TargetStates and 1 <= value <= 500:
            MasterPresetRecallCmdString = '/api/tpp/v1/load-master-memory'
            data = {
                'memoryId': int(value),
                'target': target.lower()
            }

            self.__SetHelper('MasterPresetRecall', value, qualifier, url=MasterPresetRecallCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMasterPresetRecall')

    def SetMultiviewerPresetRecall(self, value, qualifier):

        multiviewer = qualifier['Multiviewer']

        if 1 <= multiviewer <= 2 and 1 <= value <= 50:
            MultiviewerPresetRecallCmdString = '/api/tpp/v1/multiviewers/{multiviewer}/load-memory'.format(multiviewer=int(multiviewer))
            data = {
                'memoryId': int(value)
            }

            self.__SetHelper('MultiviewerPresetRecall', value, qualifier, url=MultiviewerPresetRecallCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMultiviewerPresetRecall')

    def SetMultiviewerSource(self, value, qualifier):

        SourceTypeStates = {
            'None': 'none',
            'Input': 'input',
            'Image': 'image',
            'Screen Program': 'screen-program',
            'Screen Preview': 'screen-preview',
            'Auxiliary Screen Program': 'auxiliary-screen-program',
            'Timer': 'timer'
        }

        multiviewer = qualifier['Multiviewer']
        widget = qualifier['Widget']
        source_type = qualifier['Source Type']

        if all([1 <= multiviewer <= 2,
                1 <= widget <= 24,
                source_type in SourceTypeStates,
                1 <= value <= 16]):
            MultiviewerSourceCmdString = '/api/tpp/v1/multiviewers/{multiviewer}/widgets/{widget}/source'.format(multiviewer=int(multiviewer), widget=int(widget))
            data = {
                'sourceType': SourceTypeStates[source_type],
                'sourceId': int(value)
            }

            self.__SetHelper('MultiviewerSource', value, qualifier, url=MultiviewerSourceCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetMultiviewerSource')

    def UpdateMultiviewerSourceID(self, value, qualifier):

        multiviewer = qualifier['Multiviewer']
        widget = qualifier['Widget']

        if 1 <= multiviewer <= 2 and 1 <= widget <= 24:           
            MultiviewerSourceIDCmdString = '/api/tpp/v1/multiviewers/{multiviewer}/widgets/{widget}/source'.format(multiviewer=int(multiviewer), widget=int(widget))
            res = self.__UpdateHelper('MultiviewerSourceID', value, qualifier, url=MultiviewerSourceIDCmdString)
            if res:
                try:
                    value = int(res['sourceId'])
                    self.WriteStatus('MultiviewerSourceID', value, qualifier)
                except (ValueError, KeyError):
                    self.Error(['Multiviewer Source ID: Invalid/unexpected response'])

                try:
                    ValueStateValues = {
                        'none': 'None',
                        'input': 'Input',
                        'image': 'Image',
                        'screen-program': 'Screen Program',
                        'screen-preview': 'Screen Preview',
                        'auxiliary-screen-program': 'Auxiliary Screen Program',
                        'timer': 'Timer'
                    }

                    value = ValueStateValues[res['sourceType']]
                    self.WriteStatus('MultiviewerSourceType', value, qualifier)
                except KeyError:
                    self.Error(['Multiviewer Source Type: Invalid/unexpected response'])
        else:
                self.Discard('Device Is Busy for UpdateMultiviewerSourceID')
       
    def UpdateMultiviewerSourceType(self, value, qualifier):

        self.UpdateMultiviewerSourceID(value, qualifier)

    def SetScreenLayerSource(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        SourceTypeStates = {
            'None': 'none',
            'Color': 'color',
            'Input': 'input',
            'Image': 'image',
            'Screen': 'screen'
        }

        screen = qualifier['Screen']
        layer = qualifier['Layer']
        target = qualifier['Target']
        source_type = qualifier['Source Type']

        if all([1 <= screen <= 16,
                1 <= layer <= 32,
                target in TargetStates,
                source_type in SourceTypeStates,
                1 <= value <= 16]):
            ScreenLayerSourceCmdString = '/api/tpp/v1/screens/{screen}/layers/{layer}/presets/{target}/source'.format(screen=int(screen), layer=int(layer), target=target.lower())
            data = {
                'sourceType': SourceTypeStates[source_type],
                'sourceId': int(value)
            }

            self.__SetHelper('ScreenLayerSource', value, qualifier, url=ScreenLayerSourceCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetScreenLayerSource')

    def UpdateScreenLayerSourceID(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        screen = qualifier['Screen']
        layer = qualifier['Layer']
        target = qualifier['Target']

        if 1 <= screen <= 16 and 1 <= layer <= 32 and target in TargetStates:
            ScreenLayerSourceIDCmdString = '/api/tpp/v1/screens/{screen}/layers/{layer}/presets/{target}'.format(screen=int(screen), layer=int(layer), target=target.lower())
            res = self.__UpdateHelper('ScreenLayerSourceID', value, qualifier, url=ScreenLayerSourceIDCmdString)
            if res:
                try:
                    value = int(res['sourceId'])
                    self.WriteStatus('ScreenLayerSourceID', value, qualifier)
                except (ValueError, KeyError):
                    self.Error(['Screen Layer Source ID: Invalid/unexpected response'])

                try:
                    ValueStateValues = {
                        'off': 'Off',
                        'open': 'Open',
                        'close': 'Close',
                        'cross': 'Cross',
                        'flying': 'Flying',
                        'flying depth': 'Flying Depth',
                        'slave': 'Slave',
                        'mask': 'Mask',
                        'out of capacity': 'Out of Capacity'
                    }

                    value = ValueStateValues[res['status']]
                    self.WriteStatus('ScreenLayerSourceStatus', value, qualifier)
                except KeyError:
                    self.Error(['Screen Layer Source Status: Invalid/unexpected response'])

                try:
                    ValueStateValues = {
                        'none': 'None',
                        'color': 'Color',
                        'input': 'Input',
                        'image': 'Image',
                        'screen': 'Screen'
                    }

                    value = ValueStateValues[res['sourceType']]
                    self.WriteStatus('ScreenLayerSourceType', value, qualifier)
                except KeyError:
                    self.Error(['Screen Layer Source Type: Invalid/unexpected response'])
        else:
            self.Discard('Device Is Busy for UpdateScreenLayerSourceID')

    def UpdateScreenLayerSourceStatus(self, value, qualifier):

        self.UpdateScreenLayerSourceID(value, qualifier)

    def UpdateScreenLayerSourceType(self, value, qualifier):

        self.UpdateScreenLayerSourceID(value, qualifier)

    def SetScreenPresetRecall(self, value, qualifier):

        TargetStates = {
            'Preview',
            'Program'
        }

        screen = qualifier['Screen']
        target = qualifier['Target']

        if 1 <= screen <= 16 and target in TargetStates and 1 <= value <= 1000:
            ScreenPresetRecallCmdString = '/api/tpp/v1/screens/{screen}/load-memory'.format(screen=int(screen))
            data = {
                'memoryId': int(value),
                'target': target.lower()
            }

            self.__SetHelper('ScreenPresetRecall', value, qualifier, url=ScreenPresetRecallCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetScreenPresetRecall')

    def SetScreenSingleTake(self, value, qualifier):

        if 1 <= value <= 16:
            ScreenSingleTakeCmdString = '/api/tpp/v1/screens/{screen}/take'.format(screen=int(value))
            self.__SetHelper('ScreenSingleTake', value, qualifier, url=ScreenSingleTakeCmdString)
        else:
            self.Discard('Invalid Command for SetScreenSingleTake')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return json.loads(response.read().decode())
        except json.decoder.JSONDecodeError:
            return ''

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}{}'.format(self.RootURL.rstrip('/'), url)
        headers = {
            'Content-Type': 'application/json'
        }

        if data is not None:
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
            
        url = '{}{}'.format(self.RootURL.rstrip('/'), url)
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

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
