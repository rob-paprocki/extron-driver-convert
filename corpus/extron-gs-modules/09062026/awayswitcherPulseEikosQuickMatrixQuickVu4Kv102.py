import urllib.error
import urllib.request
from json import loads, dumps
from extronlib.system import ProgramLog


class DeviceClass:
    def __init__(self, ipAddress, port):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.Models = {}

        self.Commands = {
            'AuxiliaryLayerSource': {'Parameters': ['Target', 'Type'], 'Status': {}},
            'AuxiliaryPresetRecall': {'Parameters': ['Target'], 'Status': {}},
            'BackgroundLayerSource': {'Parameters': ['Screen ID', 'Target', 'Type'], 'Status': {}},
            'ForegroundLayerSource': {'Parameters': ['Screen ID', 'Target', 'Type'], 'Status': {}},
            'LiveLayerSource': {'Parameters': ['Screen ID', 'Layer ID', 'Target', 'Type'], 'Status': {}},
            'GlobalTake': {'Parameters': ['Screens', 'Auxiliary Screens'], 'Status': {}},
            'MasterPresetRecall': {'Parameters': ['Target'], 'Status': {}},
            'MultiviewerPresetRecall': {'Status': {}},
            'MultiviewerSource': {'Parameters': ['Widget ID', 'Type'], 'Status': {}},
            'ScreenPresetRecall': {'Parameters': ['Screen ID', 'Target'], 'Status': {}},
        }

    def SetAuxiliaryLayerSource(self, value, qualifier):

        TargetStates = ('Preview', 'Program')

        TypeStates = ('None', 'Input', 'Screen')

        target_val = qualifier['Target']
        type_val = qualifier['Type']
        if value and target_val in TargetStates and type_val in TypeStates:
            url = 'api/tpp/v1/auxiliary-screens/1/background-layer/presets/{}/source'.format(target_val.lower())
            data = dumps({
                "sourceType": type_val.lower(),
                "sourceId": value,
            })
            self.__SetHelper('AuxiliaryLayerSource', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetAuxiliaryLayerSource')

    def SetAuxiliaryPresetRecall(self, value, qualifier):

        TargetStates = ('Preview', 'Program')

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        target_val = qualifier['Target']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and target_val in TargetStates:
            url = 'api/tpp/v1/auxiliary-screens/1/load-memory'
            data = dumps({
                "target": target_val.lower(),
                "memoryId": value,
            })
            self.__SetHelper('AuxiliaryPresetRecall', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetAuxiliaryPresetRecall')

    def SetBackgroundLayerSource(self, value, qualifier):

        ScreenIDConstraints = {
            'Min': 1,
            'Max': 2
        }

        TargetStates = ('Preview', 'Program')

        TypeStates = ('None', 'Background-set')

        ValueConstraints = {
            'Min': 1,
            'Max': 8
        }

        scrn_id = qualifier['Screen ID']
        target_val = qualifier['Target']
        type_val = qualifier['Type']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
            ScreenIDConstraints['Min'] <= scrn_id <= ScreenIDConstraints['Max'] and type_val in TypeStates and target_val in TargetStates):
            url = 'api/tpp/v1/screens/{}/background-layer/presets/{}/source'.format(scrn_id, target_val.lower())
            data = dumps({
                "sourceType": type_val.lower(),
                "sourceId": value,
            })
            self.__SetHelper('BackgroundLayerSource', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetBackgroundLayerSource')

    def SetForegroundLayerSource(self, value, qualifier):

        ScreenIDConstraints = {
            'Min': 1,
            'Max': 2
        }

        TargetStates = ('Preview', 'Program')

        TypeStates = ('None', 'Foreground-image')

        ValueConstraints = {
            'Min': 1,
            'Max': 4
        }

        scrn_id = qualifier['Screen ID']
        target_val = qualifier['Target']
        type_val = qualifier['Type']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and
            ScreenIDConstraints['Min'] <= scrn_id <= ScreenIDConstraints['Max'] and type_val in TypeStates and target_val in TargetStates):
            url = 'api/tpp/v1/screens/{}/foreground-layer/presets/{}/source'.format(scrn_id, target_val.lower())
            data = dumps({
                "sourceType": type_val.lower(),
                "sourceId": value,
            })
            self.__SetHelper('ForegroundLayerSource', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetForegroundLayerSource')

    def SetLiveLayerSource(self, value, qualifier):

        ScreenIDConstraints = {
            'Min': 1,
            'Max': 2
        }

        LayerIDConstraints = {
            'Min': 1,
            'Max': 4
        }

        TargetStates = ('Preview', 'Program')

        TypeStates = ('None', 'Color', 'Input')

        scrn_id = qualifier['Screen ID']
        layer_id = qualifier['Layer ID']
        target_val = qualifier['Target']
        type_val = qualifier['Type']
        if (ScreenIDConstraints['Min'] <= scrn_id <= ScreenIDConstraints['Max'] and
            LayerIDConstraints['Min'] <= layer_id <= LayerIDConstraints['Max'] and
                type_val in TypeStates and target_val in TargetStates and value):
            url = 'api/tpp/v1/screens/{}/live-layers/{}/presets/{}/source'.format(scrn_id, layer_id, target_val.lower())
            data = dumps({
                "sourceType": type_val.lower(),
                "sourceId": value
            })
            self.__SetHelper('LiveLayerSource', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetLiveLayerSource')

    def SetGlobalTake(self, value, qualifier):

        screens = qualifier['Screens'].strip()
        auxiliary_screens = qualifier['Auxiliary Screens'].strip()

        try:
            screens = list(set(int(screen) for screen in screens.split(',') if screen))
            auxiliary_screens = list(set(int(aux) for aux in auxiliary_screens.split(',') if aux))
        except:
            self.Discard('Invalid Command for SetGlobalTake')
            return
        if screens or auxiliary_screens:
            url = 'api/tpp/v1/take'
            data = dumps({
                'screenIds': screens,
                'auxiliaryScreenIds': auxiliary_screens
            })

            self.__SetHelper('GlobalTake', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetGlobalTake')

    def SetMasterPresetRecall(self, value, qualifier):

        TargetStates = ('Preview', 'Program')

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        target_val = qualifier['Target']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and target_val in TargetStates:
            url = 'api/tpp/v1/load-master-memory'
            data = dumps({
                "target": target_val.lower(),
                "memoryId": value
            })
            self.__SetHelper('MasterPresetRecall', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetMasterPresetRecall')

    def SetMultiviewerPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            url = 'api/tpp/v1/multiviewer/load-memory'
            data = dumps({"memoryId": value})
            self.__SetHelper('MultiviewerPresetRecall', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetMultiviewerPresetRecall')

    def SetMultiviewerSource(self, value, qualifier):

        WidgetIDConstraints = {
            'Min': 1,
            'Max': 16
        }

        TypeStates = ('None', 'Input', 'Screen-Program', 'Screen-Preview', 'Timer')

        widget_id = qualifier['Widget ID']
        type_val = qualifier['Type']
        if value and WidgetIDConstraints['Min'] <= widget_id <= WidgetIDConstraints['Max'] and type_val in TypeStates:
            url = 'api/tpp/v1/multiviewer/widgets/{}/source'.format(widget_id)
            data = dumps({
                "sourceType": type_val.lower(),
                "sourceId": value
            })
            self.__SetHelper('MultiviewerSource', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetMultiviewerSource')

    def SetScreenPresetRecall(self, value, qualifier):

        ScreenIDConstraints = {
            'Min': 1,
            'Max': 2
        }

        TargetStates = ('Preview', 'Program')

        ValueConstraints = {
            'Min': 1,
            'Max': 200
        }

        scrn_id = qualifier['Screen ID']
        target_val = qualifier['Target']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 
            ScreenIDConstraints['Min'] <= scrn_id <= ScreenIDConstraints['Max'] and target_val in TargetStates):
            url = 'api/tpp/v1/screens/{}/load-memory'.format(scrn_id)
            data = dumps({
                "target": target_val.lower(),
                "memoryId": value
            })
            self.__SetHelper('ScreenPresetRecall', value, qualifier, url=url, data=data.encode('iso-8859-1'))
        else:
            self.Discard('Invalid Command for SetScreenPresetRecall')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url, data):
        self.Debug = True

        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(data)
        }

        url = ''.join([self.RootURL, url])

        my_request = urllib.request.Request(url, data, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=5)
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
