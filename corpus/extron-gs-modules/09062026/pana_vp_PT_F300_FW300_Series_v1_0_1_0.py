from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.5
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'PT-F300': self.pana_1_457_F300,
            'PT-F300E': self.pana_1_457_F300,
            'PT-F300EA': self.pana_1_457_F300,
            'PT-F300NT': self.pana_1_457_F300,
            'PT-F300NTE': self.pana_1_457_F300,
            'PT-F300NTEA': self.pana_1_457_F300,
            'PT-F300NTU': self.pana_1_457_F300,
            'PT-F300U': self.pana_1_457_F300,
            'PT-FW300U': self.pana_1_457_FW300,
            'PT-FW300NTU': self.pana_1_457_FW300,
            'PT-FW300': self.pana_1_457_FW300,
            'PT-FW300E': self.pana_1_457_FW300,
            'PT-FW300NTE': self.pana_1_457_FW300,
            'PT-FW300NTEA': self.pana_1_457_FW300,
            'PT-FW300EA': self.pana_1_457_FW300,
            'PT-FW300NT': self.pana_1_457_FW300,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'EDIDSetting': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiScreen': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'SideBySide': {'Status': {}},
            'Volume': {'Status': {}},
            'Wireless': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCommand = b'\x02VS1:' + self.AspectCommandStates[value] + b'\x03'
        self.__SetHelper('AspectRatio', AspectRatioCommand, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioQuery = b'\x02QS1\x03'
        res = self.__UpdateHelper('AspectRatio', AspectRatioQuery, value, qualifier)
        if res:
            try:
                value = self.AspectRatioStatusStates[res]
                self.WriteStatus('AspectRatio', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCommand = b'\x02OAS\x03'
        self.__SetHelper('AutoImage', AutoImageCommand, value, qualifier)

    def SetAVMute(self, value, qualifier):

        AVMuteStates = {
                         'Off': b'0',
                         'On': b'1'
                       }

        AVMuteCommand = b'\x02OSH:' + AVMuteStates[value] + b'\x03'
        self.__SetHelper('AVMute', AVMuteCommand, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        AVMuteStatus = {
                         b'\x021\x03': 'On',
                         b'\x020\x03': 'Off'
                       }

        AVMuteStatusQuery = b'\x02QSH\x03'
        res = self.__UpdateHelper('AVMute', AVMuteStatusQuery, value, qualifier)
        if res:
            try:
                value = AVMuteStatus[res]
                self.WriteStatus('AVMute', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdateAVMute')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStates = {
                                'Off': b'0',
                                'CC1': b'1',
                                'CC2': b'2',
                                'CC3': b'3',
                                'CC4': b'4'
                              }

        ClosedCaptionCommand = b'\x02OCC:' + ClosedCaptionStates[value] + b'\x03'
        self.__SetHelper('ClosedCaption', ClosedCaptionCommand, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionStates = {
                                b'\x020\x03': 'Off',
                                b'\x021\x03': 'CC1',
                                b'\x022\x03': 'CC2',
                                b'\x023\x03': 'CC3',
                                b'\x024\x03': 'CC4'
                              }
        ClosedCaptionQuery = b'\x02QCC\x03'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionQuery, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStates[res]
                self.WriteStatus('ClosedCaption', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdateClosedCaption')

    def SetEDIDSetting(self, value, qualifier):

        ValueStateValues = {
            'EDID1 (Moving image)': b'1',
            'EDID2 (PC)': b'2'
        }

        EDIDSettingCmdString = b'\x02OED:' + ValueStateValues[value] + b'\x03'
        self.__SetHelper('EDIDSetting', EDIDSettingCmdString, value, qualifier)

    def UpdateEDIDSetting(self, value, qualifier):

        ValueStateValues = {
            b'\x021\x03': 'EDID1 (Moving image)',
            b'\x022\x03': 'EDID2 (PC)'
        }

        EDIDSettingCmdString = b'\x02QED\x03'
        res = self.__UpdateHelper('EDIDSetting', EDIDSettingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('EDIDSetting', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdateEDIDSetting')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageQuery = b'\x02QFI:0\x03'
        res = self.__UpdateHelper('FilterUsage', FilterUsageQuery, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('FilterUsage', value, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        FreezeStates = {
                         'Off': b'0',
                         'On': b'1'
                       }

        FreezeCommand = b'\x02OFZ:' + FreezeStates[value] + b'\x03'
        self.__SetHelper('Freeze', FreezeCommand, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStatus = {
                         b'\x020\x03': 'Off',
                         b'\x021\x03': 'On'
                       }

        FreezeQuery = b'\x02QFZ\x03'
        res = self.__UpdateHelper('Freeze', FreezeQuery, value, qualifier)
        if res:
            try:
                value = FreezeStatus[res]
                self.WriteStatus('Freeze', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        InputStates = {
                        'Computer 1': b'RG1',
                        'DVI': b'DVI',
                        'Computer 2': b'RG2',
                        'Video': b'VID',
                        'S-Video': b'SVD',
                        'Network': b'NWP'
                      }
        InputCommand = b'\x02IIS:' + InputStates[value] + b'\x03'
        self.__SetHelper('Input', InputCommand, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStatus = {
                        b'\x02RG2\x03': 'Computer 2',
                        b'\x02DVI\x03': 'DVI',
                        b'\x02RG1\x03': 'Computer 1',
                        b'\x02NWP\x03': 'Network',
                        b'\x02VID\x03': 'Video',
                        b'\x02SVD\x03': 'S-Video'
                      }

        InputQuery = b'\x02QIN\x03'
        res = self.__UpdateHelper('Input', InputQuery, value, qualifier)
        if res:
            try:
                value = InputStatus[res]
                self.WriteStatus('Input', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageQuery = b'\x02Q$L\x03'
        res = self.__UpdateHelper('LampUsage', LampUsageQuery, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('LampUsage', value, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStates = {
                                 'Menu': b'OMN',
                                 'Enter': b'OEN',
                                 'Cursor Up': b'OCU',
                                 'Cursor Down': b'OCD',
                                 'Cursor Left': b'OCL',
                                 'Cursor Right': b'OCR'
                               }

        MenuCommand = b'\x02' + MenuNavigationStates[value] + b'\x03'
        self.__SetHelper('MenuNavigation', MenuCommand, value, qualifier)

    def SetMultiScreen(self, value, qualifier):

        MultiScreenCommand = b'\x02OML\x03'
        self.__SetHelper('MultiScreen', MultiScreenCommand, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        PictureModeStates = {
                              'Dynamic': b'DYN',
                              'Natural': b'NAT',
                              'Standard': b'STD',
                              'Black Board': b'BBD',
                              'Cinema': b'CIN'
                             }

        PictureCommand = b'\x02VPM:' + PictureModeStates[value] + b'\x03'
        self.__SetHelper('PictureMode', PictureCommand, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeStates = {
                              b'\x02DYN\x03': 'Dynamic',
                              b'\x02NAT\x03': 'Natural',
                              b'\x02STD\x03': 'Standard',
                              b'\x02BBD\x03': 'Black Board',
                              b'\x02CIN\x03': 'Cinema'
                            }

        PictureModeQuery = b'\x02QPM\x03'
        res = self.__UpdateHelper('PictureMode', PictureModeQuery, value, qualifier)
        if res:
            try:
                value = PictureModeStates[res]
                self.WriteStatus('PictureMode', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        PowerCommandState = {
                              'On': b'PON',
                              'Off': b'POF'
                            }

        PowerCommand = b'\x02' + PowerCommandState[value] + b'\x03'
        self.__SetHelper('Power', PowerCommand, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStatusStates = {
                              b'\x020\x03': 'Off',
                              b'\x021\x03': 'Warming Up',
                              b'\x022\x03': 'On',
                              b'\x023\x03': 'Cooling Down'
                            }

        PowerQueryCommand = b'\x02Q$S\x03'
        res = self.__UpdateHelper('Power', PowerQueryCommand, value, qualifier)
        if res:
            try:
                value = PowerStatusStates[res]
                self.WriteStatus('Power', value, None)
            except KeyError:
                print('Invalid/unexpected response for UpdatePower')

    def SetSideBySide(self, value, qualifier):

        SideBySideCommand = b'\x02ODW\x03'
        self.__SetHelper('SideBySide', SideBySideCommand, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
                              'Max': 63,
                              'Min': 0
                            }

        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:
            print('Invalid Command for SetVolume')
        else:
            VolumeCommand = b'\x02AVL:' + str(value).zfill(3).encode('utf-8') + b'\x03'
            self.__SetHelper('Volume', VolumeCommand, value, qualifier)

    def UpdateVolume(self, value, qualifier):

        VolumeCommandQuery = b'\x02QAV\x03'
        res = self.__UpdateHelper('Volume', VolumeCommandQuery, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('Volume', value, None)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def SetWireless(self, value, qualifier):

        WirelessStates = {
                           'Off': b'000',
                           '1': b'001',
                           '2': b'002',
                           '3': b'003',
                           '4': b'004',
                           'User 1': b'005',
                           'User 2': b'006',
                           'User 3': b'007',
                           'S-Map': b'008'
                         }

        WirelessCommand = b'\x02ONS:' + WirelessStates[value] + b'\x03'
        self.__SetHelper('Wireless', WirelessCommand, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {b'\x02ER402\x03': 'Inappropriate Command.',
                              b'\x02ER401\x03': 'Invalid Command Reply.'}

        if response in DEVICE_ERROR_CODES:
            print('{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False      

    def pana_1_457_F300(self):


        self.AspectCommandStates = {
            'Auto'    : b'0',
            '4:3'     : b'1',
            '16:9'    : b'2',
            'S4:3'    : b'3',
            'Through' : b'4'
            }

        self.AspectRatioStatusStates = {
            b'\x020\x03' : 'Auto',
            b'\x021\x03' : '4:3',
            b'\x022\x03' : '16:9',
            b'\x023\x03' : 'S4:3',
            b'\x024\x03' : 'Through'
            }


    def pana_1_457_FW300(self):

        self.AspectCommandStates = {
            'Auto'    : b'0',
            '4:3'     : b'1',
            '16:9'    : b'2',
            'H-Fit'   : b'3',
            'V-Fit'   : b'4',
            'HV-Fit'  : b'5',
            'Through' : b'6'
            }

        self.AspectRatioStatusStates = {
            b'\x020\x03' : 'Auto',
            b'\x021\x03' : '4:3',
            b'\x022\x03' : '16:9',
            b'\x023\x03' : 'H-Fit',
            b'\x024\x03' : 'V-Fit',
            b'\x025\x03' : 'HV-Fit',
            b'\x026\x03' : 'Through'
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
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
