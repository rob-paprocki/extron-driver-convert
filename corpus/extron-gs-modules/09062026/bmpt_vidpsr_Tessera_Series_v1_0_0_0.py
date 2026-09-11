from extronlib.system import Wait, ProgramLog
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
            'Brightness': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'TestPatternFormat': { 'Status': {}},
            'TestPatternType': { 'Status': {}},
            'VideoMute': { 'Status': {}},
        }
        
    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 10000:
            BrightnessCmdString = 'api/output/global-colour/brightness'
            data = {"data": value}
            self.__SetHelper('Brightness', value, qualifier, url=BrightnessCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'api/output/global-colour/brightness'
        res = self.__UpdateHelper('Brightness', value, qualifier, url=BrightnessCmdString)
        if res:
            try:
                value = int(res['brightness'])
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  True,
            'Off': False
            }

        if value in ValueStateValues:
            FreezeCmdString = 'api/override/freeze/enabled'
            data = {"data": ValueStateValues[value]}
            self.__SetHelper('Freeze', value, qualifier, url=FreezeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'api/override/freeze/enabled'
        res = self.__UpdateHelper('Freeze', value, qualifier, url=FreezeCmdString)
        if res:
            try:
                ValueStateValues = {
                    True:  'On',
                    False: 'Off'
                    }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 'hdmi',
            'SDI':  'sdi'
            }

        if value in ValueStateValues:
            InputCmdString = 'api/input/active/source/port-type'
            data = {"data": "{}".format(ValueStateValues[value])}
            self.__SetHelper('Input', value, qualifier, url=InputCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'api/input/active/source/port-type'
        res = self.__UpdateHelper('Input', value, qualifier, url=InputCmdString)
        if res:
            try:
                ValueStateValues = {
                    'hdmi': 'HDMI',
                    'sdi': 'SDI'
                    }

                value = ValueStateValues[res['port-type']]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetRecallCmdString = 'api/presets/active/number'
            data = {"data": int(value)}
            self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'On':  True,
            'Off': False
            }

        if value in ValueStateValues:
            TestPatternCmdString = 'api/override/test-pattern/enabled'
            data = {"data": ValueStateValues[value]}
            self.__SetHelper('TestPattern', value, qualifier, url=TestPatternCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'api/override/test-pattern/enabled'
        res = self.__UpdateHelper('TestPattern', value, qualifier, url=TestPatternCmdString)
        if res:
            try:
                ValueStateValues = {
                    True:  'On',
                    False: 'Off'
                    }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('TestPattern', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Test Pattern: Invalid/unexpected response'])

    def SetTestPatternFormat(self, value, qualifier):

        ValueStateValues = {
            'From Input':             'from-input',
            'Standard Dyanmic Range': 'standard-dynamic-range',
            'Perceptual Quantiser':   'percepual-quantiser',
            'Hybrid Log Gamma':       'hybrid-log-gamma'
            }

        if value in ValueStateValues:
            TestPatternFormatCmdString = 'api/override/test-pattern/format'
            data = {"data": "{}".format(ValueStateValues[value])}
            self.__SetHelper('TestPatternFormat', value, qualifier, url=TestPatternFormatCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetTestPatternFormat')

    def UpdateTestPatternFormat(self, value, qualifier):

        TestPatternFormatCmdString = 'api/override/test-pattern/format'
        res = self.__UpdateHelper('TestPatternFormat', value, qualifier, url=TestPatternFormatCmdString)
        if res:
            try:
                ValueStateValues = {
                    'from-input': 'From Input',
                    'standard-dynamic-range': 'Standard Dyanmic Range',
                    'percepual-quantiser': 'Perceptual Quantiser',
                    'hybrid-log-gamma': 'Hybrid Log Gamma'
                    }

                value = ValueStateValues[res['format']]
                self.WriteStatus('TestPatternFormat', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Test Pattern Format: Invalid/unexpected response'])

    def SetTestPatternType(self, value, qualifier):

        ValueStateValues = {
            'Brompton': 'brompton',
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue',
            'Cyan': 'cyan',
            'Magenta': 'magenta',
            'Yellow': 'yellow',
            'White': 'white',
            'Black': 'black',
            'Grid': 'grid',
            'Scrolling Grid': 'scrolling-grid',
            'Checkerboard': 'checkerboard',
            'Scrolling Checkerboard': 'scrolling-checkerboard',
            'Colour Bars': 'colour-bars',
            'Scrolling Colour Bars': 'scrolling-colour-bars',
            'Gradient': 'gradient',
            'Scrolling Gradient': 'scrolling-gradient',
            'Strobe': 'strobe',
            'SMPTE Bars': 'smpte-bars',
            'Scrolling SMPTE Bars': 'scrolling-smpte-bars',
            'Custom Colour': 'custom-colour',
            'Custom': 'custom',
            '45 Degree Grid': 'forty-five-degree-grid',
            'Scrolling 45 Degree Grid': 'scrolling-forty-five-degree-grid',
            'Custom Gradient': 'custom-gradient',
            'Scrolling Custom Gradient': 'scrolling-custom-gradient'
            }

        if value in ValueStateValues:
            TestPatternTypeCmdString = 'api/override/test-pattern/type'
            data = {"data": "{}".format(ValueStateValues[value])}
            self.__SetHelper('TestPatternType', value, qualifier, url=TestPatternTypeCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetTestPatternType')

    def UpdateTestPatternType(self, value, qualifier):

        TestPatternTypeCmdString = 'api/override/test-pattern/type'
        res = self.__UpdateHelper('TestPatternType', value, qualifier, url=TestPatternTypeCmdString)
        if res:
            try:
                ValueStateValues = {
                    'brompton': 'Brompton',
                    'red': 'Red',
                    'green': 'Green',
                    'blue': 'Blue',
                    'cyan': 'Cyan',
                    'magenta': 'Magenta',
                    'yellow': 'Yellow',
                    'white': 'White',
                    'black': 'Black',
                    'grid': 'Grid',
                    'scrolling-grid': 'Scrolling Grid',
                    'checkerboard': 'Checkerboard',
                    'scrolling-checkerboard': 'Scrolling Checkerboard',
                    'colour-bars': 'Colour Bars',
                    'scrolling-colour-bars': 'Scrolling Colour Bars',
                    'gradient': 'Gradient',
                    'scrolling-gradient': 'Scrolling Gradient',
                    'strobe': 'Strobe',
                    'smpte-bars': 'SMPTE Bars',
                    'scrolling-smpte-bars': 'Scrolling SMPTE Bars',
                    'custom-colour': 'Custom Colour',
                    'custom': 'Custom',
                    'forty-five-degree-grid': '45 Degree Grid',
                    'scrolling-forty-five-degree-grid': 'Scrolling 45 Degree Grid',
                    'custom-gradient': 'Custom Gradient',
                    'scrolling-custom-gradient': 'Scrolling Custom Gradient'
                    }

                value = ValueStateValues[res['type']]
                self.WriteStatus('TestPatternType', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Test Pattern Type: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':  True,
            'Off': False
            }

        if value in ValueStateValues:
            VideoMuteCmdString = 'api/override/blackout/enabled'
            data = {"data": ValueStateValues[value]}
            self.__SetHelper('VideoMute', value, qualifier, url=VideoMuteCmdString, data=data)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'api/override/blackout/enabled'
        res = self.__UpdateHelper('VideoMute', value, qualifier, url=VideoMuteCmdString)
        if res:
            try:
                ValueStateValues = {
                    True:  'On',
                    False: 'Off'
                    }

                value = ValueStateValues[res['enabled']]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        errors = ['Path not found', 'Bad operation', 'Not supported', 'Missing input parameter', 'Bad input parameter type',
                  'Bad input parameter value', 'Access denied', 'No project loaded', 'Object not found', 'Operation failed']

        try:
            res = json.loads(response.read().decode())
            if 'response-code' in res:
                if res['response-code'] in errors:
                    self.Error(['{0}: {1}'.format(sourceCmdName, res['response-code'])])
                    return ''
            return res
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'application/json'}
        if data is not None:
            data = json.dumps(data).encode()
        my_request = urllib.request.Request(url, data=data, headers=headers, method='PUT')

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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

        url = '{}{}'.format(self.RootURL, url) #self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1) # open() returns a http.client.HTTPResponse object if successful
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