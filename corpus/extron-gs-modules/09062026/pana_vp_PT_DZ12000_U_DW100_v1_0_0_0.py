from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self._DeviceID = '01'
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'LampHours': {'Parameters':['Number'], 'Status': {}},
            'LampSelect': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PictureinPicture': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            }

        self._DeviceIDValues = {
            'Broadcast': 'ZZ',
            'Group A': '0A',
            'Group B': '0B',
            'Group C': '0C',
            'Group D': '0D',
            'Group E': '0E',
            'Group F': '0F',
            'Group G': '0G',
            'Group H': '0H',
            'Group I': '0I',
            'Group J': '0J',
            'Group K': '0K',
            'Group L': '0L',
            'Group M': '0M',
            'Group N': '0N',
            'Group O': '0O',
            'Group P': '0P',
            'Group Q': '0Q',
            'Group R': '0R',
            'Group S': '0S',
            'Group T': '0T',
            'Group U': '0U',
            'Group V': '0V',
            'Group W': '0W',
            'Group X': '0X',
            'Group Y': '0Y',
            'Group Z': '0Z',
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        try:
            if value in self._DeviceIDValues:
                self._DeviceID = self._DeviceIDValues[value]
            elif 1 <= int(value) <= 64:
                self._DeviceID = value.zfill(2)
        except (ValueError, TypeError, KeyError):
            print('DeviceID Parameter is the wrong type. Range is from 1 - 64, Broadcast, or Group A to Group Z')


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {

            'Default': '\x02AD{0};VSE:0\x03',
            '4:3': '\x02AD{0};VSE:1\x03',
            '16:9': '\x02AD{0};VSE:2\x03',
            'Through': '\x02AD{0};VSE:5\x03',
            'HV Fit': '\x02AD{0};VSE:6\x03',
            'H Fit': '\x02AD{0};VSE:9\x03',
            'V Fit': '\x02AD{0};VSE:10\x03',
            'S1 Auto': '\x02AD{0};VSE:20\x03',
            'Video Auto': '\x02AD{0};VSE:300\x03'
        }

        AspectRatioCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Default',
            '1': '4:3',
            '2': '16:9',
            '5': 'Through',
            '6': 'HV Fit',
            '9': 'H Fit',
            '10': 'V Fit',
            '20': 'S1 Auto',
            '30': 'Video Auto'
        }

        AspectRatioCmdString = '\x02AD{0};QSE\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02AD{0};OAS\x03'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{0};OFZ:1\x03',
            'Off': '\x02AD{0};OFZ:0\x03'
        }

        FreezeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '\x02AD{0};QFZ\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': '\x02AD{0};IIS:RG1\x03',
            'RGB 2': '\x02AD{0};IIS:RG2\x03',
            'Video': '\x02AD{0};IIS:VID\x03',
            'S-Video': '\x02AD{0};IIS:SVD\x03',
            'DVI': '\x02AD{0};IIS:DVI\x03',
            'AUX': '\x02AD{0};IIS:AUX\x03'
        }

        InputCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'RG1': 'RGB 1',
            'RG2': 'RGB 2',
            'VID': 'Video',
            'SVD': 'S-Video',
            'DVI': 'DVI',
            'AUX': 'AUX'
        }

        InputCmdString = '\x02AD{0};QIN\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '\x02AD{0};ONK:0\x03',
            '1': '\x02AD{0};ONK:1\x03',
            '2': '\x02AD{0};ONK:2\x03',
            '3': '\x02AD{0};ONK:3\x03',
            '4': '\x02AD{0};ONK:4\x03',
            '5': '\x02AD{0};ONK:5\x03',
            '6': '\x02AD{0};ONK:6\x03',
            '7': '\x02AD{0};ONK:7\x03',
            '8': '\x02AD{0};ONK:8\x03',
            '9': '\x02AD{0};ONK:9\x03'
        }

        KeypadCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateLampHours(self, value, qualifier):

        lamp_number = qualifier['Number']
        if lamp_number in ['1', '2', '3', '4']:
            LampHoursCmdString = '\x02AD{0};Q$L:{1}\x03'.format(self._DeviceID, lamp_number)
            res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampHours', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Hours: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampHours')

    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Quad': '\x02AD{0};LPM:00\x03',
            'L1/L4': '\x02AD{0};LPM:01\x03',
            'L2/L3': '\x02AD{0};LPM:02\x03',
            'Dual': '\x02AD{0};LPM:03\x03',
            'L1/L2/L3': '\x02AD{0};LPM:04\x03',
            'L1/L2/L4': '\x02AD{0};LPM:05\x03',
            'L1/L3/L4': '\x02AD{0};LPM:06\x03',
            'L2/L3/L4': '\x02AD{0};LPM:07\x03',
            'Triple': '\x02AD{0};LPM:08\x03',
            'L1': '\x02AD{0};LPM:09\x03',
            'L2': '\x02AD{0};LPM:10\x03',
            'L3': '\x02AD{0};LPM:11\x03',
            'L4': '\x02AD{0};LPM:12\x03',
            'Single': '\x02AD{0};LPM:13\x03'
        }

        LampSelectCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        ValueStateValues = {
            '0': 'Quad',
            '1': 'L1/L4',
            '2': 'L2/L3',
            '3': 'Dual',
            '4': 'L1/L2/L3',
            '5': 'L1/L2/L4',
            '6': 'L1/L3/L4',
            '7': 'L2/L3/L4',
            '8': 'Triple',
            '9': 'L1',
            '10': 'L2',
            '11': 'L3',
            '12': 'L4',
            '13': 'Single'
        }

        LampSelectCmdString = '\x02AD{0};QSL\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Select: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': '\x02AD{0};OMN\x03',
            'Up': '\x02AD{0};OCU\x03',
            'Down': '\x02AD{0};OCD\x03',
            'Left': '\x02AD{0};OCL\x03',
            'Right': '\x02AD{0};OCR\x03',
            'Enter': '\x02AD{0};OEN\x03'
        }

        MenuNavigationCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{0};OOS:1\x03',
            'Off': '\x02AD{0};OOS:0\x03'
        }

        OnScreenDisplayCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        OnScreenDisplayCmdString = '\x02AD{0};QOS\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '\x02AD{0};QST\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureinPicture(self, value, qualifier):

        ValueStateValues = {
            'Off': '\x02AD{0};OPP:0\x03',
            'User 1': '\x02AD{0};OPP:1\x03',
            'User 2': '\x02AD{0};OPP:2\x03',
            'User 3': '\x02AD{0};OPP:3\x03'
        }

        PictureinPictureCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)

    def UpdatePictureinPicture(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'User 1',
            '2': 'User 2',
            '3': 'User 3'
        }

        PictureinPictureCmdString = '\x02AD{0};QPP\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('PictureinPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture in Picture: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': '\x02AD{0};VPM:DYN\x03',
            'Graphic': '\x02AD{0};VPM:GRA\x03',
            'User': '\x02AD{0};VPM:USR\x03',
            'Standard': '\x02AD{0};VPM:STD\x03',
            'Cinema': '\x02AD{0};VPM:CIN\x03',
            'Natural': '\x02AD{0};VPM:NAT\x03'
        }

        PictureModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'DYN': 'Dynamic',
            'GRA': 'Graphic',
            'USR': 'User',
            'STD': 'Standard',
            'CIN': 'Cinema',
            'NAT': 'Natural'
        }

        PictureModeCmdString = '\x02AD{0};QPM\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{0};PON\x03',
            'Off': '\x02AD{0};POF\x03'
        }

        PowerCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '0': 'Off',
            '3': 'Cooling Down',
            '1': 'Warming Up'
        }

        PowerCmdString = '\x02AD{0};Q$S\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '\x02AD{0};OSH:1\x03',
            'Off': '\x02AD{0};OSH:0\x03'
        }

        VideoMuteCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '\x02AD{0};QSH\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': 'Commands cannot be accepted.',
            '\x02ER402\x03': 'Parameter Error.'
        }

        if response in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID in self._DeviceIDValues:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID in self._DeviceIDValues:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

