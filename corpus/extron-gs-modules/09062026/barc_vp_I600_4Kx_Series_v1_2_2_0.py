# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import json

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._AuthenticationPIN = 0
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActivateProfileCommand': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Contrast': { 'Status': {}},
            'Focus': { 'Status': {}},
            'FocusPosition': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LaserHours': { 'Status': {}},
            'LaserPower': { 'Status': {}},
            'LensShift': {'Parameters':['Step'], 'Status': {}},
            'LensShiftPositionHorizontalStatus': { 'Status': {}},
            'LensShiftPositionVerticalStatus': { 'Status': {}},
            'MenuCall': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'TestPatternSelect': { 'Status': {}},
            'Zoom': { 'Status': {}},
            'ZoomPosition': { 'Status': {}}
        }

        self.ResponseRegex = {
            'Brightness':                           re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?((-?\d.\d+)|(-?\d+))}(, ?\"id\": ?(\d+))?'),
            'Contrast':                             re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?((\d.\d+)|(\d+))}(, ?\"id\": ?(\d+))?'),
            'FocusPosition':                        re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(-?\d+)}(, ?\"id\": ?(\d+))?'),
            'Input':                                re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?\"(HDMI|DisplayPort|USB|BNC|HDBaseT)\"}(, ?\"id\": ?(\d+))?'),
            'LampMode':                             re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?\"(On|Off)\"}(, ?\"id\": ?(\d+))?'),
            'LaserHours':                           re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(\d+)}(, ?\"id\": ?(\d+))?'),
            'LaserPower':                           re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(\d+)}(, ?\"id\": ?(\d+))?'),
            'LensShiftPositionHorizontalStatus':    re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(-?\d+)}(, ?\"id\": ?(\d+))?'),
            'LensShiftPositionVerticalStatus':      re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(-?\d+)}(, ?\"id\": ?(\d+))?'),
            'Power':                                re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?\"(boot|eco|standby|ready|conditioning|on|deconditioning)\"}(, ?\"id\": ?(\d+))?'),
            'Shutter':                              re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?\"(Open|Closed)\"}(, ?\"id\": ?(\d+))?'),
            'TestPattern':                          re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(true|false)}(, ?\"id\": ?(\d+))?'),
            'TestPatternSelect':                    re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?"(internal:([0-9A-Za-z-]*))?"}(, ?\"id\": ?(\d+))?'),
            'ZoomPosition':                         re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?(-?\d+)}(, ?\"id\": ?(\d+))?'),
        }

        self.SetRegex = re.compile(b'\{\"jsonrpc\": ?\"2\.0\"(, ?\"id\": ?(\d+))?, ?\"result\": ?[tT]rue}')

    @property
    def AuthenticationPIN(self):
        return self._AuthenticationPIN

    @AuthenticationPIN.setter
    def AuthenticationPIN(self, value):
        self._AuthenticationPIN = int(value)

    def SetAuthenticate(self, value, qualifier):

        AuthenticationString = self.CommandHelper('authenticate')
        self.Send(AuthenticationString)

    def CommandHelper(self, method, parameters={}):
        baseDict = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 392,
            "params": {
                "code": self.AuthenticationPIN
            }
        }

        for key in parameters:
            baseDict["params"][key] = parameters[key]

        return json.dumps(baseDict, sort_keys=True)
    
    def SetActivateProfileCommand(self, value, qualifier):

        ActivateProfileCommandCmdString = self.CommandHelper('profile.activateprofile', {'name': value})
        self.__SetHelper('ActivateProfileCommand', ActivateProfileCommandCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        if -1 <= value <= 1:
            if value % 1 == 0:
                value = round(value)
            BrightnessCmdString = self.CommandHelper("property.set", {"property": "image.brightness", "value": value})
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = self.CommandHelper("property.get", {"property": "image.brightness"})
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = float(outputDict["result"])
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 2:
            if value % 1 == 0:
                value = round(value)
            ContrastCmdString = self.CommandHelper("property.set", {"property": "image.contrast", "value": value})
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        ContrastCmdString = self.CommandHelper("property.get", {"property": "image.contrast"})
        res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = float(outputDict["result"])
                self.WriteStatus('Contrast', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Contrast: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Forward': 'optics.focus.runforward',
            'Reverse': 'optics.focus.runreverse',
            'Stop': 'optics.focus.stop'
            }

        if value in ValueStateValues:
            FocusCmdString = self.CommandHelper(ValueStateValues[value])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusPosition(self, value, qualifier):

        if 0 <= value <= 65535:
            FocusPositionCmdString = self.CommandHelper("property.set", {"property": "optics.focus.target", "value": value})
            self.__SetHelper('FocusPosition', FocusPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusPosition')

    def UpdateFocusPosition(self, value, qualifier):

        FocusPositionCmdString = self.CommandHelper("property.get", {"property": "optics.focus.position"})
        res = self.__UpdateHelper('FocusPosition', FocusPositionCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = int(outputDict["result"])
                self.WriteStatus('FocusPosition', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Focus Position: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = [
            'HDMI',
            'DisplayPort',
            'USB',
            'BNC',
            'HDBaseT'
            ]

        if value in ValueStateValues:
            InputCmdString = self.CommandHelper("property.set", {"property": "image.window.main.source", "value": value})
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = self.CommandHelper("property.get", {"property": "image.window.main.source"})
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'HDMI': 'HDMI',
                    'DisplayPort': 'DisplayPort',
                    'USB': 'USB',
                    'BNC': 'BNC',
                    'HDBaseT': 'HDBaseT'
                }

                outputDict = json.loads(res)
                value = ValueStateValues[outputDict["result"]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = self.CommandHelper("property.get", {"property": "illumination.state"})
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'On': 'On',
                    'Off': 'Off'
                }
                outputDict = json.loads(res)
                value = ValueStateValues[outputDict["result"]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLaserHours(self, value, qualifier):

        LaserHoursCmdString = self.CommandHelper("property.get", {"property": "statistics.laser runtime.value"})
        res = self.__UpdateHelper('LaserHours', LaserHoursCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = int(outputDict["result"]) // 3600
                self.WriteStatus('LaserHours', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Laser Hours: Invalid/unexpected response'])

    def SetLaserPower(self, value, qualifier):

        if 0 <= value <= 100:
            LaserPowerCmdString = self.CommandHelper("property.set", {"property": "illumination.sources.laser.power", "value": value})
            self.__SetHelper('LaserPower', LaserPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLaserPower')

    def UpdateLaserPower(self, value, qualifier):

        LaserPowerCmdString = self.CommandHelper("property.get", {"property": "illumination.sources.laser.power"})
        res = self.__UpdateHelper('LaserPower', LaserPowerCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = int(outputDict["result"])
                self.WriteStatus('LaserPower', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Laser Power: Invalid/unexpected response'])

    def SetLensShift(self, value, qualifier):

        ValueStateValues = {
            'Up': 'optics.lensshift.vertical.stepreverse',
            'Down': 'optics.lensshift.vertical.stepforward',
            'Left': 'optics.lensshift.horizontal.stepreverse',
            'Right': 'optics.lensshift.horizontal.stepforward'
            }

        if 1 <= qualifier['Step'] <= 300 and value in ValueStateValues:
            LensShiftCmdString = self.CommandHelper(ValueStateValues[value], {"steps": qualifier['Step']})
            self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensShift')

    def UpdateLensShiftPositionHorizontalStatus(self, value, qualifier):

        LensShiftPositionHorizontalStatusCmdString = self.CommandHelper("property.get", {"property": "optics.lensshift.horizontal.position"})
        res = self.__UpdateHelper('LensShiftPositionHorizontalStatus', LensShiftPositionHorizontalStatusCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = int(outputDict["result"])
                self.WriteStatus('LensShiftPositionHorizontalStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Lens Shift Position Horizontal Status: Invalid/unexpected response'])

    def UpdateLensShiftPositionVerticalStatus(self, value, qualifier):

        LensShiftPositionVerticalStatusCmdString = self.CommandHelper("property.get", {"property": "optics.lensshift.vertical.position"})
        res = self.__UpdateHelper('LensShiftPositionVerticalStatus', LensShiftPositionVerticalStatusCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = int(outputDict["result"])
                self.WriteStatus('LensShiftPositionVerticalStatus', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Lens Shift Position Vertical Status: Invalid/unexpected response'])

    def SetMenuCall(self, value, qualifier):

        ValueStateValues = {
            'On':  True,
            'Off': False
            }

        if value in ValueStateValues:
            MenuCallCmdString = self.CommandHelper("property.set", {"property": "ui.menu", "value": ValueStateValues[value]})
            self.__SetHelper('MenuCall', MenuCallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuCall')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 'RC_MENU',
            'Left'  : 'RC_LEFT', 
            'Right' : 'RC_RIGHT', 
            'Up'    : 'RC_UP', 
            'Down'  : 'RC_DOWN', 
            'OK'    : 'RC_OK', 
            'Back'  : 'RC_BACK'
        }
        if value in ValueStateValues:
            MenuNavigationCmdString = self.CommandHelper("property.set", {"property": "keydispatcher.postevent", "key": ValueStateValues[value]})
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')   

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'system.poweron',
            'Off': 'system.poweroff',
            'ECO/Power Save': 'system.gotoeco'
            }

        if value in ValueStateValues:
            PowerCmdString = self.CommandHelper(ValueStateValues[value],  {"property": "system.state"})
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = self.CommandHelper("property.get", {"property": "system.state"})
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    'on': 'On',
                    'boot': 'Booting Up',
                    'eco': 'ECO/Power Save',
                    'standby': 'Off',
                    'ready': 'Off',
                    'conditioning': 'Warming Up',
                    'deconditioning': 'Cooling Down'
                    }

                outputDict = json.loads(res)
                value = ValueStateValues[outputDict["result"]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = [
            'Open',
            'Closed'
            ]

        if value in ValueStateValues:
            ShutterCmdString = self.CommandHelper("property.set", {"property": "optics.shutter.target", "value": value})
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = self.CommandHelper("property.get", {"property": "optics.shutter.target"})
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = outputDict["result"]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'On' : True, 
            'Off' : False
        }

        if value in ValueStateValues:
            TestPatternCmdString = self.CommandHelper("property.set", {"property": "image.testpattern.show", "value": ValueStateValues[value]})
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = self.CommandHelper("property.get", {"property": "image.testpattern.show"})
        res = self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = 'On' if outputDict["result"] else 'Off'
                self.WriteStatus('TestPattern', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Test Pattern: Invalid/unexpected response'])

    def SetTestPatternSelect(self, value, qualifier):

        ValueStateValues = {
            'Aspect':                   'aspect',
            'Focus-Green':              'focus-green',
            'Focus-bursts':             'focus-bursts',
            'White':                    'white',
            'Black':                    'black',
            'Red':                      'red',
            'Green':                    'green',
            'Blue':                     'blue',
            'Cyan':                     'cyan',
            'Magenta':                  'magenta',
            'Yellow':                   'yellow',
            'Color bars':               'colorbars',
            'Color gradients':          'color-gradients',
            'Checkerboard':             'checkerboard',
            'Cross hatch':              'crosshatch',
            'Geometry':                 'geometry',
            'Horizontal gray bars':     'horizontal-graybars',
            'Vertical gray bars':       'vertical-graybars',
            '3D Stereo':                '3d-stereo'
            }

        if value == 'None':
            testPatternID = ''
        elif value in ValueStateValues:
            testPatternID = "internal:{}".format(ValueStateValues[value])
        else:
            self.Discard('Invalid Command for SetTestPatternSelect')

        TestPatternSelectCmdString = self.CommandHelper("property.set", {"property": "image.testpattern.selected", "value": testPatternID})
        self.__SetHelper('TestPatternSelect', TestPatternSelectCmdString, value, qualifier)

    def UpdateTestPatternSelect(self, value, qualifier):

        TestPatternSelectCmdString = self.CommandHelper("property.get", {"property": "image.testpattern.selected"})
        res = self.__UpdateHelper('TestPatternSelect', TestPatternSelectCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    '': 'None',
                    'internal:aspect': 'Aspect',
                    'internal:focus-green': 'Focus-Green',
                    'internal:focus-bursts': 'Focus-bursts',
                    'internal:white': 'White',
                    'internal:black': 'Black',
                    'internal:red': 'Red',
                    'internal:green': 'Green',
                    'internal:blue': 'Blue',
                    'internal:cyan': 'Cyan',
                    'internal:magenta': 'Magenta',
                    'internal:yellow': 'Yellow',
                    'internal:colorbars': 'Color bars',
                    'internal:color-gradients': 'Color gradients',
                    'internal:checkerboard': 'Checkerboard',
                    'internal:crosshatch': 'Cross hatch',
                    'internal:geometry': 'Geometry',
                    'internal:horizontal-graybars': 'Horizontal gray bars',
                    'internal:vertical-graybars': 'Vertical gray bars',
                    'internal:3d-stereo': '3D Stereo'
                    }

                outputDict = json.loads(res)
                value = ValueStateValues[outputDict["result"]]
                self.WriteStatus('TestPatternSelect', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Test Pattern Select: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Forward': 'optics.zoom.runforward',
            'Reverse': 'optics.zoom.runreverse',
            'Stop': 'optics.zoom.stop'
            }

        if value in ValueStateValues:
            ZoomCmdString = self.CommandHelper(ValueStateValues[value])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def SetZoomPosition(self, value, qualifier):

        if 0 <= value <= 65535:
            ZoomPositionCmdString = self.CommandHelper("property.set", {"property": "optics.zoom.target", "value": value})
            self.__SetHelper('ZoomPosition', ZoomPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomPosition')

    def UpdateZoomPosition(self, value, qualifier):

        ZoomPositionCmdString = self.CommandHelper("property.get", {"property": "optics.zoom.position"})
        res = self.__UpdateHelper('ZoomPosition', ZoomPositionCmdString, value, qualifier)
        if res:
            try:
                outputDict = json.loads(res)
                value = int(outputDict["result"])
                self.WriteStatus('ZoomPosition', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Zoom Position: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.SetAuthenticate( None, None)
            self.Send(commandstring)
        else:
            self.SetAuthenticate(None, None)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.SetAuthenticate(None, None)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.ResponseRegex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())     

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetAuthenticate( None, None)

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()