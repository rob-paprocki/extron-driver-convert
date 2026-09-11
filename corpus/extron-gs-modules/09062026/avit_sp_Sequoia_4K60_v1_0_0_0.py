import re
import json
import urllib.error
import urllib.request

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
            'CustomPresetCommand': {'Parameters': ['Action'], 'Status': {}},
            'DefaultLayout': { 'Status': {}},
            'FullScreenMode': { 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'LatestPreset': {'Parameters': ['Action'], 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'OperationMode': { 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'Route': {'Parameters': ['Input', 'Output', 'Window'], 'Status': {}},
            'Temperature': { 'Status': {}},
            'UserIconPreset': {'Parameters': ['Action'], 'Status': {}},
            'WindowAspectRatio': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabelCommand': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabelStatus': {'Parameters': ['Window'], 'Status': {}},
            'WindowMute': {'Parameters': ['Window'], 'Status': {}},
            'WindowPositionandSize': {'Parameters': ['Window', 'X', 'Y', 'Width', 'Height', 'Keep Aspect', 'Fit to Window', 'Show', 'Resolution'], 'Status': {}},
            'WindowTieStatus': {'Parameters': ['Window'], 'Status': {}},
        }

        self.custom_preset_regex = re.compile('^[a-zA-Z0-9\.\-\_]+$')
        self.window_label_regex = re.compile('^[^{}]+$'.format(re.escape('<>!@#&$%^*"\'`/\\,.:;?=')))

    def SetCustomPresetCommand(self, value, qualifier):

        name = value

        ActionStates = {
            'Load':     'load',
            'Save':     'save',
            'Delete':   'del'
        }
        action = qualifier['Action']

        if name and self.custom_preset_regex.match(name) and action in ActionStates:
            CustomPresetCommandCmdString = 'command.cgi?cmd=2060&param={{"func":"{}","type":"custom_preset","io":"ob","location":1,"port":1,"name":"{}"}}'.format(ActionStates[action], name)
            self.__SetHelper('CustomPresetCommand', value, qualifier, url=CustomPresetCommandCmdString)
        else:
            self.Discard('Invalid Command for SetCustomPresetCommand')

    def SetDefaultLayout(self, value, qualifier):

        ValueStateValues = {
            'Quad':                 '1',
            '3 Small + 1 Large':    '2',
            '1 Large + 3 Small':    '3'
        }

        if value in ValueStateValues:
            DefaultLayoutCmdString = 'command.cgi?cmd=2060&param={{"func":"load","type":"default","io":"ob","location":1,"port":1,"data":{{"default_layout":{}}}}}'.format(ValueStateValues[value])
            self.__SetHelper('DefaultLayout', value, qualifier, url=DefaultLayoutCmdString)
        else:
            self.Discard('Invalid Command for SetDefaultLayout')

    def SetFullScreenMode(self, value, qualifier):

        ValueStateValues = {
            'Multiview':    '0',
            '1':            '1',
            '2':            '2',
            '3':            '3',
            '4':            '4'
        }

        if value in ValueStateValues:
            FullScreenModeCmdString = 'command.cgi?cmd=Ext&param={{"func":"set","type":"global_option","port":1,"data":{{"full":{}}}}}'.format(ValueStateValues[value])
            self.__SetHelper('FullScreenMode', value, qualifier, url=FullScreenModeCmdString)
        else:
            self.Discard('Invalid Command for SetFullScreenMode')

    def UpdateInputSignalStatus(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 4:
            ValueStateValues = {
                1: 'Active',
                0: 'Not Active'
            }

            InputSignalStatusCmdString = 'command.cgi?cmd=Info&param={"func":"get","type":"signals"}'
            res = self.__UpdateHelper('InputSignalStatus', value, qualifier, url=InputSignalStatusCmdString)
            if res:
                try:
                    for obj in res:
                        if 1 <= obj['input'] <= 4:
                            qualifier = {
                                'Input': str(obj['input'])
                            }

                            value = ValueStateValues[obj['signal']]
                            self.WriteStatus('InputSignalStatus', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Input Signal Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def SetLatestPreset(self, value, qualifier):

        ActionStates = {
            'Load': 'load',
            'Save': 'set'
        }
        action = qualifier['Action']

        if action in ActionStates:
            LatestPresetCmdString = 'command.cgi?cmd=2060&param={{"func":"{}","type":"preset","io":"ob","location":1,"port":1,"data":{{"preset_num":15}}}}'.format(ActionStates[action])
            self.__SetHelper('LatestPreset', value, qualifier, url=LatestPresetCmdString)
        else:
            self.Discard('Invalid Command for SetLatestPreset')
            
    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            OnScreenDisplayCmdString = 'command.cgi?cmd=Info&param={{"func":"set","type":"osd","port":1,"en":{}}}'.format(ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', value, qualifier, url=OnScreenDisplayCmdString)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def SetOperationMode(self, value, qualifier):

        ValueStateValues = {
            'Host':             '0',
            'Window 1 Remote':  '1',
            'Window 2 Remote':  '2',
            'Window 3 Remote':  '3',
            'Window 4 Remote':  '4'
        }

        if value in ValueStateValues:
            OperationModeCmdString = 'command.cgi?cmd=Ext&param={{"func":"set","type":"enter_remote","port":1,"winid":{}}}'.format(ValueStateValues[value])
            self.__SetHelper('OperationMode', value, qualifier, url=OperationModeCmdString)
        else:
            self.Discard('Invalid Command for SetOperationMode')

    def SetOutputResolution(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'Auto':           '0',
            '3840x2160 60Hz': '99',
            '3840x2160 50Hz': '98',
            '3840x2160 30Hz': '96',
            '3840x2160 25Hz': '95',
            '1920x1080 60Hz': '74',
            '1920x1080 50Hz': '70',
            '1280x1024 60Hz': '143',
            '1280x1024 50Hz': '205'
        }

        if 1 <= output <= 5 and value in ValueStateValues:
            OutputResolutionCmdString = 'command.cgi?cmd=2060&param={{"func":"set","type":"resolution","io":"ob","location":1,"port":{},"mode":{}}}'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputResolution', value, qualifier, url=OutputResolutionCmdString)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputTieStatus(self, value, qualifier):

        output = int(qualifier['Output'])
        if 2 <= output <= 5:
            OutputTieStatusCmdString = 'command.cgi?cmd=2060&param={"func":"get","type":"route2win"}'
            res = self.__UpdateHelper('OutputTieStatus', value, qualifier, url=OutputTieStatusCmdString)
            if res:
                Input_ValueStateValues = {
                    1: '1',
                    2: '2',
                    3: '3',
                    4: '4',
                    0: 'Multiview',
                    5: 'Multiview'
                }

                Window_ValueStateValues = {
                    1: '1',
                    2: '2',
                    3: '3',
                    4: '4'
                }

                for obj in res:
                    try:
                        if 2 <= obj['output'][0]['port'] <= 5:
                            qualifier = {
                                'Output': str(obj['output'][0]['port'])
                            }

                            value = Input_ValueStateValues[obj['input']]
                            self.WriteStatus('OutputTieStatus', value, qualifier)

                            continue
                    except (KeyError, IndexError, AttributeError):
                        self.Error(['Output Tie Status: Invalid/unexpected response'])

                        self.Error([str(obj)])
                    try:
                        if obj['output'][0]['port'] == 1:
                            qualifier = {
                                'Window': Window_ValueStateValues[obj['output'][0]['winid']]
                            }

                            value = Input_ValueStateValues[obj['input']]
                            self.WriteStatus('WindowTieStatus', value, qualifier)
                    except (KeyError, IndexError, AttributeError):
                        self.Error(['Window Tie Status: Invalid/unexpected response'])
                        self.Error([str(obj)])
        else:
            self.Discard('Invalid Command for UpdateOutputTieStatus')

    def SetRoute(self, value, qualifier):

        InputStates = {
            '1':            '1',
            '2':            '2',
            '3':            '3',
            '4':            '4',
            'Multiview':    '0'
        }
        input_ = qualifier['Input']
        output = int(qualifier['Output'])
        window = int(qualifier['Window'])

        if input_ in InputStates and 1 <= output <= 5 and 1 <= window <= 4:
            if input_ == 'Multiview' and output in [1, 5]:
                self.Discard('Invalid Command for SetRoute')
                return
            if 2 <= output <= 4:
                window = 254
            elif output == 5:
                window = 1

            RouteCmdString = 'command.cgi?cmd=2060&param={{"func":"set","type":"route2win","route":[{{"input":{},"output":[{{"port":{},"winid":{}}}]}}]}}'.format(InputStates[input_], output, window)
            self.__SetHelper('Route', value, qualifier, url=RouteCmdString)
        else:
            self.Discard('Invalid Command for SetRoute')

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'command.cgi?cmd=Info&param={"func":"get","type":"device"}'
        res = self.__UpdateHelper('Temperature', value, qualifier, url=TemperatureCmdString)
        if res:
            try:
                ValueStateValues = {
                    0:      'Auto',
                    99:     '3840x2160 60Hz',
                    98:     '3840x2160 50Hz',
                    96:     '3840x2160 30Hz',
                    95:     '3840x2160 25Hz',
                    74:     '1920x1080 60Hz',
                    70:     '1920x1080 50Hz',
                    143:    '1280x1024 60Hz',
                    205:    '1280x1024 50Hz'
                }

                for output, resolution in enumerate(res['resolution'], 1):
                    value = ValueStateValues[resolution]
                    self.WriteStatus('OutputResolution', value, {'Output': str(output)})

                    if output == 5:
                        break
            except (ValueError, IndexError, AttributeError):
                self.Error(['Output Resolution: Invalid/unexpected response'])
            try:
                value = int(res['temp'])
                self.WriteStatus('Temperature', value, None)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Temperature: Invalid/unexpected response'])

    def SetUserIconPreset(self, value, qualifier):

        ActionStates = {
            'Load': 'load',
            'Save': 'set'
        }
        action = qualifier['Action']

        if action in ActionStates and 1 <= int(value) <= 5:
            UserIconPresetCmdString = 'command.cgi?cmd=2060&param={{"func":"{}","type":"preset","io":"ob","location":1,"port":1,"data":{{"preset_num":{}}}}}'.format(ActionStates[action], int(value))
            self.__SetHelper('UserIconPreset', value, qualifier, url=UserIconPresetCmdString)
        else:
            self.Discard('Invalid Command for SetUserIconPreset')

    def SetWindowAspectRatio(self, value, qualifier):

        window = int(qualifier['Window'])

        ValueStateValues = {
            'Full': '0',
            'Auto': '1',
            '16:9': '2',
            '4:3':  '3'
        }

        if 1 <= window <= 4 and value in ValueStateValues:
            WindowAspectRatioCmdString = 'command.cgi?cmd=Ext&param={{"func":"set","type":"win","port":1,"winid":{},"data":{{"aspect":{}}}}}'.format(window, ValueStateValues[value])
            self.__SetHelper('WindowAspectRatio', value, qualifier, url=WindowAspectRatioCmdString)
        else:
            self.Discard('Invalid Command for SetWindowAspectRatio')

    def SetWindowLabelCommand(self, value, qualifier):

        label = value
        window = int(qualifier['Window'])

        if label and self.window_label_regex.match(label) and 1 <= window <= 4:
            WindowLabelCommandCmdString = 'command.cgi?cmd=Info&param={{"func":"set","type":"genlabel","label":[{{"port":{},"label":"{}"}}]}}'.format(window, label)
            self.__SetHelper('WindowLabelCommand', value, qualifier, url=WindowLabelCommandCmdString)
        else:
            self.Discard('Invalid Command for SetWindowLabelCommand')

    def UpdateWindowLabelStatus(self, value, qualifier):

        window = int(qualifier['Window'])

        if 1 <= window <= 4:
            WindowLabelStatusCmdString = 'command.cgi?cmd=Info&param={"func":"get","type":"label","board":"sib"}'
            res = self.__UpdateHelper('WindowLabelStatus', value, qualifier, url=WindowLabelStatusCmdString)
            if res:
                try:
                    for window, label in enumerate(res['sib_label'], 1):
                        self.WriteStatus('WindowLabelStatus', label, {'Window': str(window)})

                        if window == 4:
                            break
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Window Label Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateWindowLabelStatus')

    def SetWindowMute(self, value, qualifier):

        window = int(qualifier['Window'])

        ValueStateValues = {
            'On':   '0',
            'Off':  '1'
        }

        if 1 <= window <= 4 and value in ValueStateValues:
            WindowMuteCmdString = 'command.cgi?cmd=Ext&param={{"func":"set","type":"win","port":1,"winid":{},"data":{{"show":{}}}}}'.format(window, ValueStateValues[value])
            self.__SetHelper('WindowMute', value, qualifier, url=WindowMuteCmdString)
        else:
            self.Discard('Invalid Command for SetWindowMute')

    def SetWindowPositionandSize(self, value, qualifier):

        window = int(qualifier['Window'])
        x = int(qualifier['X'])
        y = int(qualifier['Y'])
        w = int(qualifier['Width'])
        h = int(qualifier['Height'])

        KeepAspectStates = {
            'On':   '1',
            'Off':  '0',
            '16:9': '2',
            '4:3':  '3'
        }
        keep_aspect = qualifier['Keep Aspect']

        FittoWindowStates = {
            'On':   '1',
            'Off':  '0'
        }
        fit_to_window = qualifier['Fit to Window']

        ShowStates = {
            'On':   '1',
            'Off':  '0'
        }
        show = qualifier['Show']

        ResolutionStates = {
            '3840x2160': '3840,2160',
            '1920x1080': '1920,1080',
            '1280x1024': '1280,1024'
        }
        resolution = qualifier['Resolution']

        if 1 <= window <= 4 and 0 <= x <= 3840 and 0 <= y <= 2160 and 960 <= w <= 3840 and 540 <= h <= 2160 and keep_aspect in KeepAspectStates and fit_to_window in FittoWindowStates and show in ShowStates and resolution in ResolutionStates:
            WindowPositionandSizeCmdString = 'command.cgi?cmd=2060&param={{"func":"set","type":"position","io":"ob","location":1,"port":1,"win":[{{"id":{},"data":[{},{},{},{},{},{},{},{}]}}],"global_option":[0,0,0,0,0],"resolution":[{}],"default_layout":0,"preset":0}}'.format(window, x, y, w, h, window - 1, KeepAspectStates[keep_aspect], FittoWindowStates[fit_to_window], ShowStates[show], ResolutionStates[resolution])
            self.__SetHelper('WindowPositionandSize', value, qualifier, url=WindowPositionandSizeCmdString)
        else:
            self.Discard('Invalid Command for SetWindowPositionandSize')

    def UpdateWindowTieStatus(self, value, qualifier):

        window = int(qualifier['Window'])

        if 1 <= window <= 4:
            self.UpdateOutputTieStatus(None, {'Output': '2'})
        else:
            self.Discard('Invalid Command for UpdateWindowTieStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            response = response.read().decode().strip()
            
            if response in ['Wrong Format', 'Unsupported Type']:
                self.Error(['An error occurred: {}: {}'.format(sourceCmdName, response)])
                return {}
            elif response in ['Success']:
                return {}
            else:
                return json.loads(response, strict=False)
        except json.decoder.JSONDecodeError:
            self.Error(['An error occurred: {}.'.format(sourceCmdName)])
            return {}

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}cgi-bin/{}'.format(self.RootURL, url)
        headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1)
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

        url = '{}cgi-bin/{}'.format(self.RootURL, url)
        headers = {}

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=1)
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
