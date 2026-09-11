from extronlib.interface import EthernetClientInterface, SerialInterface
import re


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'ChannelDirectCommand': {'Parameters': ['Number'], 'Status': {}},
            'ChannelDirectStatus': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'DTVChannelDirectCommand': {'Parameters': ['Number'], 'Status': {}},
            'DTVChannelDirectStatus': {'Status': {}},
            'DTVChannelStep': {'Status': {}},
            'DVBDirectChannelCommand': {'Status': {}},
            'DVBDirectChannelStatus': {'Parameters': ['Number'], 'Status': {}},
            'ExtensionInput': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal [AV]': '1',
            'Zoom 14:9 [AV]': '2',
            'Panorama [AV]': '3',
            'Full [AV]': '4',
            'Cinema 16:9 [AV]': '5',
            'Cinema 14:9 [AV]': '6',
            'Normal [PC]': '7',
            'Cinema [PC]': '8',
            'Full [PC]': '9',
            'Dot By Dot': '10',
            'Underscan [AV]': '11',
            'Auto': '12',
            'Original [AV]': '13'
        }

        AspectRatioCmdString = 'WIDE{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': 'Normal [AV]',
            '2': 'Zoom 14:9 [AV]',
            '3': 'Panorama [AV]',
            '4': 'Full [AV]',
            '5': 'Cinema 16:9 [AV]',
            '6': 'Cinema 14:9 [AV]',
            '7': 'Normal [PC]',
            '8': 'Cinema [PC]',
            '9': 'Full [PC]',
            '10': 'Dot By Dot',
            '11': 'Underscan [AV]',
            '12': 'Auto',
            '13': 'Original [AV]'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetChannelDirectCommand(self, value, qualifier):
        
        temp_value = qualifier['Number']
        if temp_value:
            if 1 <= int(temp_value) <= 99:
                ChannelDirectCommandCmdString = 'DCCH{0:04d}\r'.format(int(temp_value))
                self.__SetHelper('ChannelDirectCommand', ChannelDirectCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetChannelDirectCommand')
        else:
            print('Invalid Command for SetChannelDirectCommand')

    def UpdateChannelDirectStatus(self, value, qualifier):

        ChannelDirectStatusCmdString = 'DCCH????\r'
        res = self.__UpdateHelper('ChannelDirectStatus', ChannelDirectStatusCmdString, value, qualifier)
        if res:
            try:
                value = str(res[0:-1])
                self.WriteStatus('ChannelDirectStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateChannelDirectStatus')

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DW'
        }

        ChannelStepCmdString = 'CH{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetDTVChannelDirectCommand(self, value, qualifier):

        temp_value = qualifier['Number']
        if temp_value:
            if 1 <= int(temp_value) <= 9999:
                DTVChannelDirectCommandCmdString = 'DTVD{0:04d}\r'.format(int(temp_value))
                self.__SetHelper('DTVChannelDirectCommand', DTVChannelDirectCommandCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDTVChannelDirectCommand')
        else:
            print('Invalid Command for SetDTVChannelDirectCommand')

    def UpdateDTVChannelDirectStatus(self, value, qualifier):

        DTVChannelDirectStatusCmdString = 'DTVD????\r'
        res = self.__UpdateHelper('DTVChannelDirectStatus', DTVChannelDirectStatusCmdString, value, qualifier)
        if res:
            try:
                value = str(res[0:-1])
                self.WriteStatus('DTVChannelDirectStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDTVChannelDirectStatus')

    def SetDTVChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DW'
        }

        DTVChannelStepCmdString = 'DT{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('DTVChannelStep', DTVChannelStepCmdString, value, qualifier)

    def UpdateDVBDirectChannelStatus(self, value, qualifier):

        Num = int(qualifier['Number'])
        if 1 <= Num <= 4:
            DVBDirectChannelStatusCmdString = 'DSC{0}????\r'.format(Num)
            res = self.__UpdateHelper('DVBDirectChannelStatus', DVBDirectChannelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = str(res[0:-1])
                    self.WriteStatus('DVBDirectChannelStatus', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateDVBDirectChannelStatus')
        else:
                print('Invalid Command for UpdateDVBDirectChannelStatus')

    def SetDVBDirectChannelCommand(self, value, qualifier):

        temp_value = value
        Num = qualifier['Number']
        if (temp_value and temp_value.isdigit() and Num):
            if 1 <= int(temp_value) <= 9999:
                DVBDirectChannelCommandCmdString = 'DSC{0}{1:04d}\r'.format(Num, int(temp_value))
                self.__SetHelper('DVBDirectChannelCommand', DVBDirectChannelCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDVBDirectChannelCommand')

    def SetExtensionInput(self, value, qualifier):

        ValueStateValues = {
            'Y/C': '0',
            'CVBS': '1',
            'RGB': '2'
        }

        ExtensionInputCmdString = 'INP1{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('ExtensionInput', ExtensionInputCmdString, value, qualifier)

    def UpdateExtensionInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'Y/C',
            '1': 'CVBS',
            '2': 'RGB'
        }

        ExtensionInputCmdString = 'INP1????\r'
        res = self.__UpdateHelper('ExtensionInput', ExtensionInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('ExtensionInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateExtensionInput')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': 'ITVD    \r',
            'DTV': 'IDTV    \r',
            'Ext 1': 'IAVD1   \r',
            'Ext 2': 'IAVD2   \r',
            'HDMI 1': 'IAVD4   \r',
            'HDMI 2': 'IAVD5   \r',
            'HDMI 3': 'IAVD6   \r',
            'HDMI 4': 'IAVD7   \r',
            'PC': 'IAVD8   \r',
            'Ext 3': 'IAVD3   \r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'Ext 1',
            '2': 'Ext 2',
            '4': 'HDMI 1',
            '5': 'HDMI 2',
            '6': 'HDMI 3',
            '7': 'HDMI 4',
            '8': 'PC',
            '3': 'Ext 3'
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '2'
        }

        MuteCmdString = 'MUTE{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '2': 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = 'TEXT{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = 'TEXT????\r'
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '1',
            'Movie': '2',
            'Game': '3',
            'User': '4',
            'Dynamic (Fixed)': '5',
            'Dynamic': '6',
            'PC': '7',
            'x.v.Color': '8',
            'Auto': '100'
        }

        PictureModeCmdString = 'AVMD{0:4}\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'Standard',
            '2': 'Movie',
            '3': 'Game',
            '4': 'User',
            '5': 'Dynamic (Fixed)',
            '6': 'Dynamic',
            '7': 'PC',
            '8': 'x.v.Color',
            '100': 'Auto'
        }

        PictureModeCmdString = 'AVMD????\r'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = 'POWR{0}   \r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 60
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:4}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        response = response.decode()
        DEVICE_ERROR_CODES = {
            'ERR\r': 'Communication error or incorrect command',
            }
        if response:
            if response[0:5] in DEVICE_ERROR_CODES:
                ErrorString = '{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:5]])
                print(ErrorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

           

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
