import urllib.error
import urllib.request
import base64
from base64 import encodebytes
from re import findall, search
from base64 import encodebytes

class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername, devicePassword):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
        
        self.Unidirectional = 'False'
        self._compile_list = {}
        self.Subscription = {}
        self.Debug = False
        
        self.Models = {}
        
        self._Channel = '5'
        self._MaxPreset = 5        

        self.Commands = {
            'Home': { 'Status': {}},
            'MoveAbsolute': {'Parameters':['Elevation','Azimuth','Zoom'], 'Status': {}},
            'MoveContinuous': {'Parameters':['Pan','Tilt','Zoom'], 'Status': {}},
            'MoveMomentary': {'Parameters':['Pan','Tilt','Zoom','Duration'], 'Status': {}},
            'MoveRelative': {'Parameters':['Pan','Tilt','Zoom'], 'Status': {}},
            'PresetAdd': { 'Status': {}},
            'PresetAddName': { 'Status': {}},
            'PresetDelete': { 'Status': {}},
            'PresetNavigation': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetResult': {'Parameters':['Button'], 'Status': {}},
            'PresetSave': { 'Status': {}},
            'PresetUpdate': { 'Status': {}},
            }

        self.PresetName = ListNavigation()
        self.PresetPattern = ('\<PTZPreset\>[\r\n]*\<enabled\>(true|false)\</enabled\>[\r\n]*\<id\>([\s\S]*?)\</id\>[\r\n]*\<presetName\>([\s\S]*?)\</presetName\>[\r\n]*\<AbsoluteHigh\>[\r\n]*'
                              '\<elevation\>[0-9-]*\</elevation\>[\r\n]*\<azimuth\>[0-9-]*\</azimuth\>[\r\n]*\<absoluteZoom\>[0-9-]*\</absoluteZoom\>[\r\n]*\</AbsoluteHigh\>[\r\n]*\</PTZPreset\>')
        self.PresetMatches = []
        self.PossiblePresetIDs = {str(a) for a in range(1,91)}
        self.PossiblePresetIDs.update({str(a) for a in range(106,301)})
        self.Header = {'Content-Type' : 'text/xml'}
        if deviceUsername or devicePassword:
            Hash = encodebytes(':'.join([deviceUsername,devicePassword]).encode())
            self.Header['Authorization'] = ' '.join(['Basic',Hash.decode()[:-1]])

    @property
    def Channel(self):
        return self._Channel

    @Channel.setter
    def Channel(self, value):
        if 1 <= int(value) <= 5:
            self._Channel = str(value)
        else:
            self.Discard('Invalid channel range {}.')

    @property
    def MaxPreset(self):
        return self._MaxPreset

    @MaxPreset.setter
    def MaxPreset(self, value):
        if 1 <= int(value) <= 15:
            self._MaxPreset = int(value)
            self.PresetName.Max = self._MaxPreset

    def __ConstraintChecker(self, *args):
        try:
            for x in args:
                if not (x['Min'] <= x['Value'] <= x['Max']):
                    return False
            return True
        except:
            return False

    def SetHome(self, value, qualifier):

        ValueStateValues = {
            'Save' : '', 
            'Recall' : '/goto'
        }
        HomeCmdString = ''.join(['ISAPI/PTZCtrl/channels/',self._Channel,'/homeposition',ValueStateValues[value]])
        self.__SetHelper('Home', value, qualifier, url=HomeCmdString)

    def SetMoveAbsolute(self, value, qualifier):

        Elevation = {
            'Min' : -90,
            'Max' : 270,
            'Value' : qualifier['Elevation']
        }
        Azimuth = {
            'Min' : 0,
            'Max' : 360,
            'Value' : qualifier['Azimuth']
        }
        Zoom = {
            'Min' : 0,
            'Max' : 100,
            'Value' : qualifier['Zoom']
        }
        if self.__ConstraintChecker(Elevation, Azimuth, Zoom):
            MoveAbsoluteCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'absolute'])
            MoveAbsoluteData = ('<PTZData version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">'
                                '<AbsoluteHigh><elevation>{}</elevation><azimuth>{}</azimuth><absoluteZoom>{}</absoluteZoom></AbsoluteHigh>'
                                '</PTZData>').format(int(Elevation['Value']*10), int(Azimuth['Value']*10), int(Zoom['Value']*10))
            self.__SetHelper('MoveAbsolute', value, qualifier, url=MoveAbsoluteCmdString, data=MoveAbsoluteData)
        else:
            self.Discard('Invalid Command for SetMoveAbsolute')

    def SetMoveContinuous(self, value, qualifier):

        Pan = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Pan']
        }
        Tilt = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Tilt']
        }
        Zoom = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Zoom']
        }
        if self.__ConstraintChecker(Pan, Tilt, Zoom):
            MoveContinuousCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'continuous'])
            MoveContinuousData = ('<PTZData version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">'
                                  '<pan>{}</pan><tilt>{}</tilt><zoom>{}</zoom>'
                                  '</PTZData>').format(Pan['Value'], Tilt['Value'], Zoom['Value'])
            self.__SetHelper('MoveContinuous', value, qualifier, url=MoveContinuousCmdString, data=MoveContinuousData)
        else:
            self.Discard('Invalid Command for SetMoveContinuous')

    def SetMoveMomentary(self, value, qualifier):

        Pan = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Pan']
        }
        Tilt = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Tilt']
        }
        Zoom = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Zoom']
        }
        Duration = {
            'Min' : 0,
            'Max' : 20000,
            'Value' : qualifier['Duration']
        }

        if self.__ConstraintChecker(Pan, Tilt, Zoom, Duration):
            MoveMomentaryCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'momentary'])
            MoveMomentaryData = ('<PTZData version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">'
                                 '<pan>{}</pan><tilt>{}</tilt><zoom>{}</zoom><Momentary><duration>{}</duration></Momentary>'
                                 '</PTZData>').format(Pan['Value'], Tilt['Value'], Zoom['Value'], Duration['Value'])
            self.__SetHelper('MoveMomentary', value, qualifier, url=MoveMomentaryCmdString, data=MoveMomentaryData)
        else:
            self.Discard('Invalid Command for SetMoveMomentary')

    def SetMoveRelative(self, value, qualifier):

        Pan = {
            'Min' : -127,
            'Max' : 128,
            'Value' : qualifier['Pan']
        }
        Tilt = {
            'Min' : -127,
            'Max' : 128,
            'Value' : qualifier['Tilt']
        }
        Zoom = {
            'Min' : -100,
            'Max' : 100,
            'Value' : qualifier['Zoom']
        }
        if self.__ConstraintChecker(Pan, Tilt, Zoom):
            MoveRelativeCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'relative'])
            MoveRelativeData = ('<PTZData version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">'
                                '<Relative><positionX>{}</positionX><positionY>{}</positionY><relativeZoom>{}</relativeZoom></Relative>'
                                '</PTZData>').format(Pan['Value'] + 127, Tilt['Value'] + 127, Zoom['Value'])
            self.__SetHelper('MoveRelative', value, qualifier, url=MoveRelativeCmdString, data=MoveRelativeData)
        else:
            self.Discard('Invalid Command for SetMoveRelative')

    def SetPresetAdd(self, value, qualifier):
        self.Debug = True

        Name = qualifier['Name']
        if Name:
            self.SetPresetUpdate(None, None)
            ExistingPresetIDs = {Preset[1] for Preset in self.PresetMatches}
            FreeIDs = self.PossiblePresetIDs - ExistingPresetIDs
            if FreeIDs:
                ID = FreeIDs.pop()
                PresetSaveCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'presets',ID])
                PresetData = ''.join(['<PTZPreset version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema"><enabled>true</enabled><id>',ID,'</id><presetName>',Name,'</presetName></PTZPreset>'])
                self.__SetHelper('PresetSave', value, qualifier, url=PresetSaveCmdString, data=PresetData)
        else:
            self.Discard('Invalid Command for SetPresetAdd')

    def SetPresetDelete(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : self._MaxPreset
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line = self.ReadStatus('PresetResult', {'Button' : value})
            if Line not in self.PresetName.InvalidLines:
                ID = self.PresetMatches[self.PresetName.StartingEntry+value-1][1]
                PresetDeleteCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'presets',ID])
                self.__SetHelper('PresetDelete', value, qualifier, url=PresetDeleteCmdString, method='DELETE')
        else:
            self.Discard('Invalid Command for SetPresetDelete')

    def SetPresetNavigation(self, value, qualifier):
        self.Debug = True

        self.PresetName.Navigate(value, self.WriteStatus)

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : self._MaxPreset
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line = self.ReadStatus('PresetResult', {'Button' : value})
            if Line not in self.PresetName.InvalidLines:
                ID = self.PresetMatches[self.PresetName.StartingEntry+value-1][1]
                PresetRecallCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'presets',ID,'goto'])
                self.__SetHelper('PresetRecall', value, qualifier, url=PresetRecallCmdString)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : self._MaxPreset
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Line = self.ReadStatus('PresetResult', {'Button' : value})
            if Line not in self.PresetName.InvalidLines:
                ID = self.PresetMatches[self.PresetName.StartingEntry+value-1][1]
                PresetSaveCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'presets',ID])
                PresetData = ''.join(['<PTZPreset version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema"><enabled>true</enabled><id>',ID,'</id><presetName>',Line,'</presetName></PTZPreset>'])
                self.__SetHelper('PresetSave', value, qualifier, url=PresetSaveCmdString, data=PresetData)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPresetUpdate(self, value, qualifier):
        self.Debug = True

        PresetUpdateCmdString = '/'.join(['ISAPI/PTZCtrl/channels',self._Channel,'presets'])
        CurrentPresets = self.__UpdateHelper('PresetUpdate', value, qualifier, url=PresetUpdateCmdString)
        self.PresetName.Clear()
        self.PresetMatches = findall(self.PresetPattern, CurrentPresets)

        for Preset in self.PresetMatches:
            self.PresetName.Append(Preset[2])
        if self.PresetMatches:
            self.PresetName.End()
        else:
            self.PresetName.Empty()

        self.PresetName.Navigate(None, self.WriteStatus)

    def __CheckResponseForErrors(self, sourceCmdName, res):

        return res.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None, method='PUT'):
        self.Debug = True

        if data:
            data = data.encode()
        my_request = urllib.request.Request('{}{}'.format(self.RootURL, url), data=data, headers=self.Header, method=method)
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

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            my_request = urllib.request.Request('{}{}'.format(self.RootURL, url), data=data, headers=self.Header)
    
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            
    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


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

class ListNavigation:

    EndofList = '***End of list***'
    EmptyList = '***Not Available***'
    InvalidLines = (EndofList, EmptyList, None, '')
    StartingEntry = 0
    Max = 1

    def __init__(self):
        self.Empty()

    def Empty(self):
        self.List = [self.EmptyList]

    def Clear(self):
        self.List.clear()

    def Append(self, Line):
        if Line not in self.InvalidLines:
            self.List.append(Line)

    def End(self):
        self.List.append(self.EndofList)

    def Navigate(self, Direction, WriteFunction):
    
        if Direction == 'Page Up':
            self.StartingEntry -= self.Max
        elif Direction == 'Page Down':
            self.StartingEntry += self.Max
        elif Direction == 'Up':
            self.StartingEntry -= 1
        elif Direction == 'Down':
            self.StartingEntry += 1

        if self.StartingEntry + self.Max >= len(self.List):
            self.StartingEntry = len(self.List) - self.Max

        if self.StartingEntry < 0:
            self.StartingEntry = 0

        for Button,Line in enumerate(self.List[self.StartingEntry:self.StartingEntry+self.Max],1):
            WriteFunction('PresetResult', Line, {'Button': Button})
        for Button in range(Button + 1, self.Max + 1):
            WriteFunction('PresetResult', '', {'Button': Button})
