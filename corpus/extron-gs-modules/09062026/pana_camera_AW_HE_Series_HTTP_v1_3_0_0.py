import urllib.error
import urllib.request
import base64
from re import compile

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None):
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.connectionCounter = 15

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'AW-HE2': self.pana_19_7_2,
            'AW-HE50': self.pana_19_7_50,
            'AW-HE2PJ': self.pana_19_7_2,
            'AW-HE50S': self.pana_19_7_50,
            'AW-HE60': self.pana_19_7_50,
            'AW-HE60SE': self.pana_19_7_50,
            'AW-HE120': self.pana_19_7_50,
            'AW-HE130': self.pana_19_7_130,
            'AW-HE130KE': self.pana_19_7_130,
            'AW-HE130KEJ': self.pana_19_7_130,
            'AW-HE130WEJ': self.pana_19_7_130,
            'AW-HE130WE': self.pana_19_7_130,
            'AW-HE40HKE': self.pana_19_7_50,
            'AW-HE40HKP': self.pana_19_7_50,
            'AW-HE40HWE': self.pana_19_7_50,
            'AW-HE40HWP': self.pana_19_7_50,
            'AW-HE40SKE': self.pana_19_7_50,
            'AW-HE40SKP': self.pana_19_7_50,
            'AW-HE40SWE': self.pana_19_7_50,
            'AW-HE40SWP': self.pana_19_7_50,
            'AW-HE65HKMC': self.pana_19_7_50,
            'AW-HE65HWMC': self.pana_19_7_50,
            'AW-HE65SKMC': self.pana_19_7_50,
            'AW-HE65SWMC': self.pana_19_7_50,
            'AW-HE70HK': self.pana_19_7_50,
            'AW-HE70HW': self.pana_19_7_50,
            'AW-HE70SK': self.pana_19_7_50,
            'AW-HE70SW': self.pana_19_7_50,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'AutoIris': {'Status': {}},
            'ColorBar': {'Status': {}},
            'Detail': {'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Installation': {'Status': {}},
            'IrisPosition': {'Status': {}},
            'MainPinPMode': {'Status': {}},
            'PanTilt': {'Parameters':['Speed'], 'Status': {}},
            'PinP': {'Status': {}},
            'PinPDisplayPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters':['Type'], 'Status': {}},
            'PresetRecallStatus': {'Status': {}},
            'ResetPanTiltPosition': {'Status': {}},
            'ResetZoom': {'Status': {}},
            'Tally': {'Status': {}},
            'TallyInput': {'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}}
        }

        self.Detail = compile('ODT:(0|1|2)')
        self.ColorBar = compile('OBR:(0|1)')
        self.AutoIris = compile('d3(0|1)')
        self.AutoFocus = compile('d1(0|1)')
        self.MainPinPMode = compile('cMP(0|1)')
        self.PinPDisplayPosition = compile('pD(0|1|2|3)')
        self.PinP = compile('[oO]P:(0|1)')
        self.Power = compile('p(0|1)')
        self.Preset = compile('s([0-99]{2})')
        self.TallyInput = compile('tAE(0|1)')
        self.Tally = compile('dA(0|1)')
        self.Err = compile('ER(1|2|3)')

    def SetAutoFocus(self, value, qualifier):
        if self.Model != 'HE2':
            self.SetAutoFocus50(value, qualifier)
        else:
            FocusValues = {
                'Auto'  : '1',
                'Manual': '0'
                }

            data = 'cmd=OAF:{0}&res=1'.format(FocusValues[value])
            self.__SetHelper('AutoFocus', value, qualifier, url='', data=data)

    def SetAutoFocus50(self, value, qualifier):
        
        FocusValues = {
            'Auto'  : '1',
            'Manual': '0'
            }

        data = 'cmd=%23D1{0}&res=1'.format(FocusValues[value])
        self.__SetHelper('AutoFocus', value, qualifier, url='', data=data)

    def UpdateAutoFocus(self, value, qualifier):
        if self.Model != 'HE2':
            self.UpdateAutoFocus50(value, qualifier)
        else:
            print('AutoFocus does not support Update.')

    def UpdateAutoFocus50(self, value, qualifier):

        AutoFocus50StateNames = {
            '0' : 'Manual',
            '1' : 'Auto'
            }
        data = 'cmd=%23D1&res=1'
        res = self.__UpdateHelper('AutoFocus', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.AutoFocus.search(res)
                if mGroup is not None:
                    AutoFocus50Value = mGroup.group(1)
                else:
                    AutoFocus50Value = ''
                self.WriteStatus('AutoFocus', AutoFocus50StateNames[AutoFocus50Value], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateAutoFocus')

    def SetAutoIris(self, value, qualifier):
        
        AutoIrisValues = {
            'On' : '1',
            'Off': '0'
            }

        data = 'cmd=%23D3{0}&res=1'.format(AutoIrisValues[value])
        self.__SetHelper('AutoIris', value, qualifier, url='', data=data)

    def UpdateAutoIris(self, value, qualifier):

        AutoIrisStateNames = {
            '0' : 'Off',
            '1' : 'On'
            }
        data = 'cmd=%23D3&res=1'
        res = self.__UpdateHelper('AutoIris', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.AutoIris.search(res)
                if mGroup is not None:
                    AutoIrisValue = mGroup.group(1)
                else:
                    AutoIrisValue = ''
                self.WriteStatus('AutoIris', AutoIrisStateNames[AutoIrisValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateAutoIris')

    def SetColorBar(self, value, qualifier):
        
        ColorBarValues = {
            'On' : '1',
            'Off': '0'
            }

        if self.Model == 'HE2':
            data = 'cmd=DGB:{0}&res=1'.format(ColorBarValues[value])
        else:
            data = 'cmd=DCB:{0}&res=1'.format(ColorBarValues[value])
        self.__SetHelper('ColorBar', value, qualifier, url='', data=data)

    def UpdateColorBar(self, value, qualifier):

        ColorBarStateNames = {
            '0' : 'Off',
            '1' : 'On'
            }
        data = 'cmd=QBR&res=1'
        res = self.__UpdateHelper('ColorBar', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.ColorBar.search(res)
                if mGroup is not None:
                    ColorBarValue = mGroup.group(1)
                else:
                    ColorBarValue = ''
                self.WriteStatus('ColorBar', ColorBarStateNames[ColorBarValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateColorBar')

    def SetDetail(self, value, qualifier):

        data = 'cmd=ODT:{0}&res=1'.format(self.DetailValues[value])
        self.__SetHelper('Detail', value, qualifier, url='', data=data)

    def UpdateDetail(self, value, qualifier):

        data = 'cmd=QDT&res=1'
        res = self.__UpdateHelper('Detail', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Detail.search(res)
                if mGroup is not None:
                    DetailValue = mGroup.group(1)
                else:
                    DetailValue = ''
                
                self.WriteStatus('Detail', self.DetailStateNames[DetailValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateDetail')

    def SetFocus(self, value, qualifier):

        FocusConstraints = {
            'Min' : 1,
            'Max' : 49
            }
        
        Speed = qualifier['Speed']
        data = ''
        if Speed < FocusConstraints['Min'] or Speed > FocusConstraints['Max']:
            print('Invalid Command for SetFocus')
        else:
            if value == 'Near':
                data = 'cmd=%23F{0}&res=1'.format(str(50-Speed).zfill(2))
            elif value == 'Far':
                data = 'cmd=%23F{0}&res=1'.format(str(50+Speed).zfill(2))
            else :
                data = 'cmd=%23F50&res=1'
            self.__SetHelper('Focus', value, qualifier, url='', data=data)

    def SetInstallation(self, value, qualifier):
        
        InstallationValues = {
            'Desktop' : '0',
            'Hanging' : '1'
            }

        data = 'cmd=%23INS{0}&res=1'.format(InstallationValues[value])
        self.__SetHelper('Installation', value, qualifier, url='', data=data)

    def SetIrisPosition(self, value, qualifier):
        if self.Model != 'HE2':
            self.SetIrisPosition50(value, qualifier)
        else:
            IrisValues = {
                'Close' : '555',
                'Open'  : 'FFF'
                }

            data = 'cmd=%23AXI{0}&res=1'.format(IrisValues[value])
            self.__SetHelper('IrisPosition', value, qualifier, url='', data=data)

    def SetIrisPosition50(self, value, qualifier):

        IrisConstraints = {
            'Min' : 0,
            'Max' : 20
            }
        if value < IrisConstraints['Min'] or value > IrisConstraints['Max']:
            print('Invalid Command for SetIrisPosition')
        else:
            hexvalue = hex(1365 + value*136)
            data = 'cmd=%23AXI{0}&res=1'.format(hexvalue[2:].upper())
            self.__SetHelper('IrisPosition', value, qualifier, url='', data=data)

    def SetMainPinPMode(self, value, qualifier):
        
        MainPinPModeValues = {
            'Main' : '0',
            'PinP' : '1'
            }

        data = 'cmd=%23CMP{0}&res=1'.format(MainPinPModeValues[value])
        self.__SetHelper('MainPinPMode', value, qualifier, url='', data=data)

    def UpdateMainPinPMode(self, value, qualifier):

        MainPinPModeStateNames = {
            '0' : 'Main',
            '1' : 'PinP'
            }
        data = 'cmd=%23CMP&res=1'
        res = self.__UpdateHelper('MainPinPMode', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.MainPinPMode.search(res)
                if mGroup is not None:
                    MainPinPModeValue = mGroup.group(1)
                else:
                    MainPinPModeValue = ''
                self.WriteStatus('MainPinPMode', MainPinPModeStateNames[MainPinPModeValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateMainPinPMode')

    def SetPanTilt(self, value, qualifier):

        PanTiltConstraints = {
            'Min' : 1,
            'Max' : 49
            }
        Speed = qualifier['Speed']
        data = ''
        if Speed < PanTiltConstraints['Min'] or Speed > PanTiltConstraints['Max']:
            print('Invalid Command for SetPanTilt')
        else:
            if value == 'Left':
                data = 'cmd=%23P{0}&res=1'.format(str(50-Speed).zfill(2))
            elif value == 'Right':
                data = 'cmd=%23P{0}&res=1'.format(str(50+Speed).zfill(2))
            elif value == 'Up':
                data = 'cmd=%23T{0}&res=1'.format(str(50+Speed).zfill(2))
            elif value == 'Down':
                data = 'cmd=%23T{0}&res=1'.format(str(50-Speed).zfill(2))
            else :
                data = 'cmd=%23PTS5050&res=1'
            self.__SetHelper('PanTilt', value, qualifier, url='', data=data)

    def SetPinPDisplayPosition(self, value, qualifier):
        
        PinPDisplayPositionValues = {
            'Lower Right' : '1',
            'Upper Right' : '0',
            'Lower Left'  : '2',
            'Upper Left'  : '3'
            }

        data = 'cmd=%23PD{0}&res=1'.format(PinPDisplayPositionValues[value])
        self.__SetHelper('PinPDisplayPosition', value, qualifier, url='', data=data)

    def UpdatePinPDisplayPosition(self, value, qualifier):

        PinPDisplayPositionStateNames = {
            '1':'Lower Right',
            '0':'Upper Right',
            '2':'Lower Left',
            '3':'Upper Left'
            }
        data = 'cmd=%23PD&res=1'
        res = self.__UpdateHelper('PinPDisplayPosition', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.PinPDisplayPosition.search(res)
                if mGroup is not None:
                    PinPDisplayPositionValue = mGroup.group(1)
                else:
                    PinPDisplayPositionValue = ''
                self.WriteStatus('PinPDisplayPosition', PinPDisplayPositionStateNames[PinPDisplayPositionValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdatePinPDisplayPosition')

    def SetPinP(self, value, qualifier):
        
        PinPValues = {
            'On' : '1',
            'Off': '0'
            }

        data = 'cmd=OP:{0}&res=1'.format(PinPValues[value])
        self.__SetHelper('PinP', value, qualifier, url='', data=data)

    def UpdatePinP(self, value, qualifier):

        PinPStateNames = {
            '0' : 'Off',
            '1' : 'On'
            }
        data = 'cmd=OP&res=1'
        res = self.__UpdateHelper('PinP', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.PinP.search(res)
                if mGroup is not None:
                    PinPValue = mGroup.group(1)
                else:
                    PinPValue = ''
                self.WriteStatus('PinP', PinPStateNames[PinPValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdatePinP')

    def SetPower(self, value, qualifier):
        
        PowerValues = {
            'On'     : '1',
            'Standby': '0'
            }

        data = 'cmd=%23O{0}&res=1'.format(PowerValues[value])
        self.__SetHelper('Power', value, qualifier, url='', data=data)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            '0' : 'Standby',
            '1' : 'On'
            }

        data = 'cmd=%23O&res=1'
        res = self.__UpdateHelper('Power', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Power.search(res)
                if mGroup is not None:
                    PowerValue = mGroup.group(1)
                else:
                    PowerValue = ''
                self.WriteStatus('Power', PowerStateNames[PowerValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdatePower')

    def SetPreset(self, value, qualifier):
        
        SaveRecall = qualifier['Type']
        if self.PresetConstraints['Min'] <= int(value) <= self.PresetConstraints['Max']:
            preset = int(value) - 1
            data = 'cmd=%23{0}{1}&res=1'.format(self.SaveRecallValues[SaveRecall], str(preset).zfill(2))
            self.__SetHelper('Preset', value, qualifier, url='', data=data)
        else:
            print('Invalid Command for SetPreset')

    def UpdatePresetRecallStatus(self, value, qualifier):

        data = 'cmd=%23S&res=1'
        res = self.__UpdateHelper('PresetRecallStatus', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Preset.search(res)
                if mGroup is not None:
                    PresetValue = int(mGroup.group(1))+1
                    self.WriteStatus('PresetRecallStatus', PresetValue, qualifier)
                else:
                    return
            except ValueError:
                print('Invalid/unexpected response for UpdatePresetRecallStatus')

    def SetResetPanTiltPosition(self, value, qualifier):
        data = 'cmd=%23APC80008000&res=1'
        self.__SetHelper('ResetPanTiltPosition', value, qualifier, url='', data=data)

    def SetResetZoom(self, value, qualifier):
        data = 'cmd=%23AXZ555&res=1'
        self.__SetHelper('ResetZoom', value, qualifier, url='', data=data)

    def SetTallyInput(self, value, qualifier):
        
        TallyInputValues = {
            'Disable' : '0',
            'Enable'  : '1'
            }

        data = 'cmd=%23TAE{0}&res=1'.format(TallyInputValues[value])
        self.__SetHelper('TallyInput', value, qualifier, url='', data=data)

    def UpdateTallyInput(self, value, qualifier):

        TallyInputStateNames = {
            '0' : 'Disable',
            '1' : 'Enable'
            }
        data = 'cmd=%23TAE&res=1'
        res = self.__UpdateHelper('TallyInput', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.TallyInput.search(res)
                if mGroup is not None:
                    TallyInputValue = mGroup.group(1)
                else:
                    TallyInputValue = ''
                self.WriteStatus('TallyInput', TallyInputStateNames[TallyInputValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateTallyInput')

    def SetTally(self, value, qualifier):
        
        TallyValues = {
            'On' : '1',
            'Off': '0'
            }

        data = 'cmd=%23DA{0}&res=1'.format(TallyValues[value])
        self.__SetHelper('Tally', value, qualifier, url='', data=data)

    def UpdateTally(self, value, qualifier):

        TallyStateNames = {
            '0' : 'Off',
            '1' : 'On'
            }

        data = 'cmd=%23DA&res=1'
        res = self.__UpdateHelper('Tally', value, qualifier, url='', data=data)
        if res:
            try:
                mGroup = self.Tally.search(res)
                if mGroup is not None:
                    TallyValue = mGroup.group(1)
                else:
                    TallyValue = ''
                self.WriteStatus('Tally', TallyStateNames[TallyValue], None)
            except KeyError:
                print('Invalid/unexpected response for UpdateTally')

    def SetZoom(self, value, qualifier):

        ZoomConstraints = {
            'Min' : 1,
            'Max' : 49
            }
        
        Speed = qualifier['Speed']
        data = ''
        if Speed < ZoomConstraints['Min'] or Speed > ZoomConstraints['Max']:
            print('Invalid Command for SetZoom')
        else:
            if value == 'Wide':
                data = 'cmd=%23Z{0}&res=1'.format(str(50-Speed).zfill(2))
            elif value == 'Tele':
                data = 'cmd=%23Z{0}&res=1'.format(str(50+Speed).zfill(2))
            else:
                data = 'cmd=%23Z50&res=1'
            self.__SetHelper('Zoom', value, qualifier, url='', data=data)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()

        DEVICE_ERROR_CODES = {
            'ER1': 'Unsupported command',
            'ER2': 'Busy',
            'ER3': 'Outside acceptable range'
            }

        if res[0:3].upper() in DEVICE_ERROR_CODES:
            print('Device Error: {0}, Command: {1}'.format(DEVICE_ERROR_CODES[res[0:3].upper()], sourceCmdName))
            res = ''
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        if command in ['ColorBar', 'Detail', 'MainPinPMode', 'PinP', 'PinPDisplayPosition']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            url = '{0}/cgi-bin/aw_ptz?{1}'.format(self.RootURL.rstrip('/'), data)

        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()

        my_request = urllib.request.Request(url, data=None, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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

        if command in ['ColorBar', 'Detail', 'MainPinPMode', 'PinP', 'PinPDisplayPosition']:
            url = '{0}/cgi-bin/aw_cam?{1}'.format(self.RootURL.rstrip('/'), data)
        else:
            url = '{0}/cgi-bin/aw_ptz?{1}'.format(self.RootURL.rstrip('/'), data)

        headers = {}
        if self.authentication is not None:
            headers['Authorization'] = self.authentication.decode()
        my_request = urllib.request.Request(url, data=None, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=1)
        except urllib.error.HTTPError as err:
            print('{0} {1} - {2}'.format(command, err.code, err.reason))
            res = ''
        except urllib.error.URLError as err:
            print('{0} {1}'.format(command, err.reason))
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                print('{0} {1} - {2}'.format(command, res.status, res.msg))
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

    def pana_19_7_2(self):

        self.Model = 'HE2'
        self.SaveRecallValues = {
            'Save'   : 'M',
            'Recall' : 'R',
            'Delete' : 'C'
            }
        self.PresetConstraints = {
            'Min' : 1,
            'Max' : 9
            }

    def pana_19_7_50(self): 

        self.Model = 'HE50'
        self.DetailValues = {
            'Low' : '1',
            'Off' : '0',
            'High': '2'
            }
        self.DetailStateNames = {
            '0' : 'Off',
            '1' : 'Low',
            '2' : 'High'
            }
        self.SaveRecallValues = {
            'Save'   : 'M',
            'Recall' : 'R'
            }
        self.PresetConstraints = {
            'Min' : 1,
            'Max' : 100
            }

    def pana_19_7_130(self):

        self.Model = 'HE130'
        self.DetailValues = {
            'On' : '1',
            'Off': '0'
            }
        self.DetailStateNames = {
            '0' : 'Off',
            '1' : 'On',
            '2' : 'On'
            }
        self.SaveRecallValues = {
            'Save'   : 'M',
            'Recall' : 'R'
            }
        self.PresetConstraints = {
            'Min' : 1,
            'Max' : 100
            }

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
