from extronlib.interface import SerialInterface, EthernetClientInterface
import base64
from base64 import b64encode
from re import compile
import urllib.error
import urllib.request
from struct import pack, unpack
    
class DeviceHTTPClass:


    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.deviceUsername = deviceUsername
            self.devicePassword = devicePassword
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoTune': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'CaptureContinue': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'LaserPointer': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'SlideShow': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }


        
        self.Power = compile('getlumensstatus=cPower:(0|1|2);zoomValue:([0-9]{1,2});birthness:\d+;cFreeze:(0|1);cLamp:(0|1);cContinueCapture:(0|1);cCaptureType:[0|1];cMachineStatus:([0-9]{1,2})')



    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        data = 'autoexposure={0}'.format(ValueStateValues[value])
        resource = 'vb.htm?' + data
        self.__SetHelper('AutoExposure', value, qualifier, resource)


    def SetAutoFocus(self, value, qualifier):

        data = 'autofocus'
        resource = 'vb.htm?' + data
        self.__SetHelper('AutoFocus', value, qualifier, resource)


    def SetAutoTune(self, value, qualifier):

        data = 'autotune'
        resource = 'vb.htm?' + data
        self.__SetHelper('AutoTune', value, qualifier, resource)


    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = 'brightnessset={0}'.format(value)
            resource = 'vb.htm?' + data
            self.__SetHelper('Brightness', value, qualifier, resource)
        else:
            self.Discard('Invalid Command for SetBrightness')
    def SetCaptureContinue(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        data = 'capture={0}'.format(ValueStateValues[value])
        resource = 'vb.htm?' + data
        self.__SetHelper('CaptureContinue', value, qualifier, resource)
    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        data = 'freeze={0}'.format(ValueStateValues[value])
        resource = 'vb.htm?' + data
        self.__SetHelper('Freeze', value, qualifier, resource)
    def SetImageRotation(self, value, qualifier):

        data = 'rotate'
        resource = 'vb.htm?' + data
        self.__SetHelper('ImageRotation', value, qualifier, resource)


    def SetLaserPointer(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01',
            'Off' : '00',  
        }

        data = 'lamp={0}'.format(ValueStateValues[value])
        resource = 'vb.htm?' + data
        self.__SetHelper('LaserPointer',value, qualifier, resource)
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Enter' : 'enteraction', 
            'Up'    : 'upaction', 
            'Down'  : 'downaction', 
            'Left'  : 'leftaction', 
            'Right' : 'rightaction'
        }

        data = ValueStateValues[value]
        resource = 'vb.htm?' + data
        self.__SetHelper('MenuNavigation',value, qualifier, resource)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        data = 'powerstatus={0}'.format(ValueStateValues[value])
        resource = 'vb.htm?' + data
        self.__SetHelper('Power', value, qualifier, resource)
    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            '2' : 'On', 
            '0' : 'Off',
            '1' : 'Warming Up'
        }
        
        LaserPointerStateValues = {
            '0' : 'Off', 
            '1' : 'On'
        }
        
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        
        StateValues = {
            '0'  : 'Preview Mode',
            '1'  : 'Annotate Mode', 
            '2'  : 'Mask Mode',
            '3'  : 'Password Mode', 
            '4'  : 'Record Mode', 
            '5'  : 'Pan Mode', 
            '6'  : 'Main OSD Mode', 
            '7'  : 'Thumbnail Mode', 
            '8'  : 'PIP Thumbnail Mode', 
            '9'  : 'Playback Mode', 
            '10' : 'PIP Mode', 
            '11' : 'Freeze Mode', 
            '12' : 'Slide Show Mode',
            '13' : 'Source PC Mode', 
            '14' : 'Fast Frame Mode', 
            '15' : 'C-Video Mode',
            '16' : 'Service Menu Mode', 
            '17' : 'Keypad Detect Mode', 
            '18' : 'Power Down Mode', 
            '18' : 'Burn-In Mode'
        }     
        
        resource = 'vb.htm?getlumensstatus'
        res = self.__UpdateHelper('Power', value, qualifier, resource)
        if res:
            try:
                rGroup = self.Power.search(res)
                Power = rGroup.group(1)
                Zoom = int(rGroup.group(2))
                Freeze = rGroup.group(3)
                LaserPointer = rGroup.group(4)
                Capture = rGroup.group(5)
                Status = rGroup.group(6)
                self.WriteStatus('Power', PowerStateValues[Power], qualifier)
                self.WriteStatus('LaserPointer', LaserPointerStateValues[LaserPointer], qualifier)
                self.WriteStatus('CaptureContinue', ValueStateValues[Capture], qualifier)
                self.WriteStatus('DeviceStatus', StateValues[Status], qualifier)
                self.WriteStatus('Freeze', ValueStateValues[Freeze], qualifier)
                self.WriteStatus('Zoom', Zoom, qualifier)
            except (KeyError, IndexError):
                self.__CheckResponseForErrors(['Invalid/Unexpected Response'])

    def SetSlideShow(self, value, qualifier):

        ValueStateValues = {
            'On'  : '01', 
            'Off' : '00'
        }

        data = 'slideshow={0}'.format(ValueStateValues[value])
        resource = 'vb.htm?' + data
        self.__SetHelper('SlideShow', value, qualifier, resource)


    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 32
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            data = 'zoomset={0}'.format(value)
            resource = 'vb.htm?' + data
            self.__SetHelper('Zoom', value, qualifier, resource)
        else:
            self.Discard('Invalid Command for SetZoom')
    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True





        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/html'} 
        

        my_request = urllib.request.Request(url, data=data, headers=headers, method = 'GET')

        try:
            res = self.Opener.open(my_request)
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
        
    def __UpdateHelper(self, command, value, qualifier, url='', data=None):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{0}/{1}'.format(self.RootURL.rstrip('/'), url)
        headers = {'Content-Type': 'text/html'} 
        

        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
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

            

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        Command = self.Commands[command]
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

class DeviceSerialClass:


    
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'AutoWhiteBalance': { 'Status': {}},
            'Brightness': { 'Status': {}},
            'Capture': { 'Status': {}},
            'Color': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'FocusDiscrete': {'Parameters':['Speed'], 'Status': {}},
            'FocusStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'ImageMode': { 'Status': {}},
            'ImageRotation': { 'Status': {}},
            'LaserPointer': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'NegativeFilm': { 'Status': {}},
            'NightMode': { 'Status': {}},
            'Pan': { 'Status': {}},
            'Playback': { 'Status': {}},
            'PlaybackImagePage': { 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': { 'Status': {}},
            'SlideShow': { 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            'ZoomDiscrete': {'Parameters':['Speed'], 'Status': {}},
            'ZoomStatus': { 'Status': {}},
            }


    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = b'\xA0\xA3\x01\x00\x00\xAF'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)


    def SetAutoWhiteBalance(self, value, qualifier):

        AutoWhiteBalanceCmdString = b'\xA0\x22\x00\x00\x00\xAF'
        self.__SetHelper('AutoWhiteBalance', AutoWhiteBalanceCmdString, value, qualifier)


    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\xA0\x39\x01\x00\x00\xAF', 
            'Down'  : b'\xA0\x39\x00\x00\x00\xAF'
        }

        BrightnessCmdString = ValueStateValues[value]
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)


    def SetCapture(self, value, qualifier):

        ValueStateValues = {
            'Record'    : b'\xA0\xB2\x01\x00\x00\xAF', 
            'Capture'   : b'\xA0\xB2\x00\x00\x00\xAF'
        }

        CaptureCmdString = ValueStateValues[value]
        self.__SetHelper('Captures', CaptureCmdString, value, qualifier)


    def SetColor(self, value, qualifier):

        ValueStateValues = {
            'Photo' : b'\xA0\x37\x00\x00\x00\xAF', 
            'Gray'  : b'\xA0\x37\x01\x00\x00\xAF'
        }

        ColorCmdString = ValueStateValues[value]
        self.__SetHelper('Color', ColorCmdString, value, qualifier)
    def UpdateColor(self, value, qualifier):

        ValueStateValues = {
            0 : 'Photo', 
            1 : 'Gray'
        }

        ColorCmdString = b'\xA0\x88\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Color', ColorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Color', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetFocus(self, value, qualifier):

        SpeedStates = {
            '0' : b'\x00', 
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06'
        }

        ValueStateValues = {
            'Near' : b'\x00', 
            'Far' :  b'\x01'
        }

        if value == 'Stop':
            FocusCmdString = b'\xA0\x19\x00\x00\x00\xAF'
        else:
            FocusCmdString = b'\xA0\x1A' + ValueStateValues[value] + SpeedStates[qualifier['Speed']] + b'\x00\xAF'
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)


    def SetFocusDiscrete(self, value, qualifier):

        SpeedStates = {
            '0' : b'\x00', 
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 570
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FocusDiscreteCmdString = b'\xA0\x1B' + pack('<H', value) + SpeedStates[qualifier['Speed']] + b'\xAF'
            self.__SetHelper('FocusDiscrete', FocusDiscreteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusDiscrete')

    def UpdateFocusStatus(self, value, qualifier):

        FocusStatusCmdString = b'\xA0\x64\x00\x00\x00\xAF'
        res = self.__UpdateHelper('FocusStatus', FocusStatusCmdString, value, qualifier)
        if res:
            try:
                value = unpack('<H', res[2:4])[0]
                self.WriteStatus('FocusStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\xA0\x2C\x01\x00\x00\xAF', 
            'Off'   : b'\xA0\x2C\x00\x00\x00\xAF'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        FreezeCmdString = b'\xA0\x78\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetImageMode(self, value, qualifier):

        ValueStateValues = {
            'Normal'    : b'\xA0\xA9\x00\x00\x00\xAF', 
            'Slide'     : b'\xA0\xA9\x01\x00\x00\xAF', 
            'Film'      : b'\xA0\xA9\x02\x00\x00\xAF'
        }

        ImageModeCmdString = ValueStateValues[value]
        self.__SetHelper('ImageMode', ImageModeCmdString, value, qualifier)


    def SetImageRotation(self, value, qualifier):

        ValueStateValues = {
            '0'     : b'\xA0\xB4\x00\x00\x00\xAF', 
            '90'    : b'\xA0\xB4\x01\x00\x00\xAF', 
            '180'   : b'\xA0\xB4\x02\x00\x00\xAF', 
            '270'   : b'\xA0\xB4\x03\x00\x00\xAF'
        }

        ImageRotationCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRotation', ImageRotationCmdString, value, qualifier)


    def SetLaserPointer(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\xA0\xC1\x01\x00\x00\xAF', 
            'Off'   : b'\xA0\xC1\x00\x00\x00\xAF'
        }

        LaserPointerCmdString = ValueStateValues[value]
        self.__SetHelper('LaserPointer', LaserPointerCmdString, value, qualifier)
    def UpdateLaserPointer(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }


        LaserPointerCmdString = b'\xA0\x50\x00\x00\x00\xAF'
        res = self.__UpdateHelper('LaserPointer', LaserPointerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('LaserPointer', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'        : b'\xA0\xA0\x02\x00\x00\xAF', 
            'Down'      : b'\xA0\xA0\x03\x00\x00\xAF', 
            'Left'      : b'\xA0\xA0\x04\x00\x00\xAF', 
            'Right'     : b'\xA0\xA0\x05\x00\x00\xAF', 
            'Enter'     : b'\xA0\xA0\x01\x00\x00\xAF', 
            'Menu'      : b'\xA0\xA0\x06\x00\x00\xAF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetNegativeFilm(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\xA0\x36\x01\x00\x00\xAF', 
            'Off'   : b'\xA0\x36\x00\x00\x00\xAF'
        }

        NegativeFilmCmdString = ValueStateValues[value]
        self.__SetHelper('NegativeFilm', NegativeFilmCmdString, value, qualifier)
    def UpdateNegativeFilm(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }


        NegativeFilmCmdString = b'\xA0\x87\x00\x00\x00\xAF'
        res = self.__UpdateHelper('NegativeFilm', NegativeFilmCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('NegativeFilm', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetNightMode(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\xAB\x01\x00\x00\xAF', 
            'Off' : b'\xA0\xAB\x00\x00\x00\xAF'
        }

        NightModeCmdString = ValueStateValues[value]
        self.__SetHelper('NightMode', NightModeCmdString, value, qualifier)


    def SetPan(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\xA0\x26\x01\x00\x00\xAF', 
            'Off' : b'\xA0\x26\x00\x00\x00\xAF'
        }

        PanCmdString = ValueStateValues[value]
        self.__SetHelper('Pan', PanCmdString, value, qualifier)


    def SetPlayback(self, value, qualifier):

        ValueStateValues = {
            'Thumbnail'     : b'\xA0\xB3\x01\x00\x00\xAF',
            'PBP Thumbnail' : b'\xA0\xB3\x00\x00\x00\xAF'
        }

        PlaybackCmdString = ValueStateValues[value]
        self.__SetHelper('Playback', PlaybackCmdString, value, qualifier)


    def SetPlaybackImagePage(self, value, qualifier):

        ValueStateValues = {
            'Page Up'   : b'\xA0\x4A\x00\x00\x00\xAF', 
            'Page Down' : b'\xA0\x4A\x01\x00\x00\xAF'
        }

        PlaybackImagePageCmdString = ValueStateValues[value]
        self.__SetHelper('PlaybackImagePage', PlaybackImagePageCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\xA0\xB1\x01\x00\x00\xAF',
            'Off'   : b'\xA0\xB1\x00\x00\x00\xAF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        PowerCmdString = b'\xA0\xB7\x00\x00\x00\xAF'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Save' : b'\xA0\x03\x00\x01\x00\xAF', 
            'Load' : b'\xA0\x03\x00\x00\x00\xAF'
        }

        PresetCmdString = ValueStateValues[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)


    def SetSlideShow(self, value, qualifier):

        ValueStateValues = {
            'On'    : b'\xA0\x04\x01\x00\x00\xAF',
            'Off'   : b'\xA0\x04\x00\x00\x00\xAF'
        }

        SlideShowCmdString = ValueStateValues[value]
        self.__SetHelper('SlideShow', SlideShowCmdString, value, qualifier)


    def SetZoom(self, value, qualifier):

        SpeedStates = {
            '0' : b'\x00', 
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06'
        }

        ValueStateValues = {
            'Tele' : b'\x00', 
            'Wide' : b'\x01',
        }

        if value == 'Stop':
            ZoomCmdString = b'\xA0\x10\x00\x00\x00\xAF'
        else:
            ZoomCmdString = b'\xA0\x11' + ValueStateValues[value] + SpeedStates[qualifier['Speed']] + b'\x00\xAF'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)


    def SetZoomDiscrete(self, value, qualifier):

        SpeedStates = {
            '0' : b'\x00', 
            '1' : b'\x01', 
            '2' : b'\x02', 
            '3' : b'\x03', 
            '4' : b'\x04', 
            '5' : b'\x05', 
            '6' : b'\x06'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 69
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ZoomDiscreteCmdString = b'\xA0\x13' + pack('B', value) + b'\x00' + SpeedStates[qualifier['Speed']] + b'\xAF'
            self.__SetHelper('ZoomDiscrete', ZoomDiscreteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomDiscrete')
    def UpdateZoomStatus(self, value, qualifier):

        ZoomStatusCmdString = b'\xA0\x60\x00\x00\x00\xAF'
        res = self.__UpdateHelper('ZoomStatus', ZoomStatusCmdString, value, qualifier)
        if res:
            try:
                value = unpack('<H', res[2:4])[0]
                self.WriteStatus('ZoomStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            1 : 'Error in Command Packet',
            2 : 'Unsupported Command'
            }

        ErrorCode = DEVICE_ERROR_CODES.get(response[4] & 3)
        if ErrorCode:
            self.Error([ErrorCode])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            if not res:
                self.Error(['Invalid/Unexpected Response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

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
            
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xAF')
            
            return self.__CheckResponseForErrors(command, res)
            
            

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        Command = self.Commands[command]
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
class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class HTTPClass(DeviceHTTPClass):
    def __init__(self,ipAddress,port,deviceUsername=None,devicePassword=None,Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self,ipAddress,port,deviceUsername,devicePassword)
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