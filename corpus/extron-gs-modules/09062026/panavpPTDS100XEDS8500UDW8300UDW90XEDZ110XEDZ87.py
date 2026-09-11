from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

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

        self.DeviceID = '01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'LensShiftHorizontal': {'Parameters': ['Speed'], 'Status': {}},
            'LensShiftVertical': {'Parameters': ['Speed'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureinPicture': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Temperature': {'Parameters': ['Location'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        DeviceIDMatch = {
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

        LensDeviceIDMatch = {
            'Broadcast': '\x00',
            'Group A': '\x80',
            'Group B': '\x81',
            'Group C': '\x82',
            'Group D': '\x83',
            'Group E': '\x84',
            'Group F': '\x85',
            'Group G': '\x86',
            'Group H': '\x87',
            'Group I': '\x88',
            'Group J': '\x89',
            'Group K': '\x8A',
            'Group L': '\x8B',
            'Group M': '\x8C',
            'Group N': '\x8D',
            'Group O': '\x8E',
            'Group P': '\x8F',
            'Group Q': '\x90',
            'Group R': '\x91',
            'Group S': '\x92',
            'Group T': '\x93',
            'Group U': '\x94',
            'Group V': '\x95',
            'Group W': '\x96',
            'Group X': '\x97',
            'Group Y': '\x98',
            'Group Z': '\x99',
            '01': '\x01',
            '02': '\x02',
            '03': '\x03',
            '04': '\x04',
            '05': '\x05',
            '06': '\x06',
            '07': '\x07',
            '08': '\x08',
            '09': '\x09',
            '10': '\x0A',
            '11': '\x0B',
            '12': '\x0C',
            '13': '\x0D',
            '14': '\x0E',
            '15': '\x0F',
            '16': '\x10',
            '17': '\x11',
            '18': '\x12',
            '19': '\x13',
            '20': '\x14',
            '21': '\x15',
            '22': '\x16',
            '23': '\x17',
            '24': '\x18',
            '25': '\x19',
            '26': '\x1A',
            '27': '\x1B',
            '28': '\x1C',
            '29': '\x1D',
            '30': '\x1E',
            '31': '\x1F',
            '32': '\x20',
            '33': '\x21',
            '34': '\x22',
            '35': '\x23',
            '36': '\x24',
            '37': '\x25',
            '38': '\x26',
            '39': '\x27',
            '40': '\x28',
            '41': '\x29',
            '42': '\x2A',
            '43': '\x2B',
            '44': '\x2C',
            '45': '\x2D',
            '46': '\x2E',
            '47': '\x2F',
            '48': '\x30',
            '49': '\x31',
            '50': '\x32',
            '51': '\x33',
            '52': '\x34',
            '53': '\x35',
            '54': '\x36',
            '55': '\x37',
            '56': '\x38',
            '57': '\x39',
            '58': '\x3A',
            '59': '\x3B',
            '60': '\x3C',
            '61': '\x3D',
            '62': '\x3E',
            '63': '\x3F',
            '64': '\x40'
        }

        try:
            self.LensDeviceID = LensDeviceIDMatch[value]
            self._DeviceID = DeviceIDMatch.get(value, value)
        except KeyError:
            print('Invalid Device ID')


    def SetAspectRatio(self, value, qualifier):

        Values = {
            'Default': '0',
            '4:3': '1',
            '16:9': '2',
            'Through': '5',
            'HV Fit': '6',
            'H Fit': '9',
            'V Fit': '10',
            'S1 Auto': '20',
            'Vid Auto': '30'
        }

        AspectRatioCmdString = '\x02AD{0};VSE:{1}\x03'.format(self._DeviceID, Values[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        Values = {
            '0': 'Default',
            '1': '4:3',
            '2': '16:9',
            '5': 'Through',
            '6': 'HV Fit',
            '9': 'H Fit',
            '10': 'V Fit',
            '20': 'S1 Auto',
            '30': 'Vid Auto'
        }

        AspectRatioCmdString = '\x02AD{0};QSE\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = Values[res[1:-1].decode()]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Update Aspect Ratio provided an Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02AD{0};OAS\x03'.format(self._DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        SpeedStates = {
            'Slow': '\x00',
            'Normal': '\x01',
            'Fast': '\x02'
        }

        ValueStateValues = {
            'Forward': '\x00',
            'Backward': '\x01'
        }

        speed = qualifier['Speed']
        if speed in SpeedStates:
            FocusCmdString = '\x02{0}\xB1\x7C\x02{1}{2}\x03'.format(self.LensDeviceID, SpeedStates[speed], ValueStateValues[value])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

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
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Update Freeze provided an Invalid/Unexpected Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB 1': '\x02AD{0};IIS:RG1\x03',
            'RGB 2': '\x02AD{0};IIS:RG2\x03',
            'Video': '\x02AD{0};IIS:VID\x03',
            'S-Video': '\x02AD{0};IIS:SVD\x03',
            'DVI': '\x02AD{0};IIS:DVI\x03',
            'SDI': '\x02AD{0};IIS:SDI\x03',
            'HDMI': '\x02AD{0};IIS:HD1\x03'
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
            'SDI': 'SDI',
            'HD1': 'HDMI'
        }

        InputCmdString = '\x02AD{0};QIN\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Update Input provided an Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': '\x02AD{0};OLP:0\x03',
            'Eco': '\x02AD{0};OLP:1\x03'
        }

        LampModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Eco'
        }

        LampModeCmdString = '\x02AD{0};QLP\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Update Lamp Mode provided an Invalid/Unexpected Response for UpdateLampMode')

    def SetLampSelect(self, value, qualifier):

        ValueStateValues = {
            'Dual': '\x02AD{0};LPM:0\x03',
            'Single': '\x02AD{0};LPM:1\x03',
            'Lamp 1': '\x02AD{0};LPM:2\x03',
            'Lamp 2': '\x02AD{0};LPM:3\x03'
        }

        LampSelectCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('LampSelect', LampSelectCmdString, value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        ValueStateValues = {
            '0': 'Dual',
            '1': 'Single',
            '2': 'Lamp 1',
            '3': 'Lamp 2'
        }

        LampSelectCmdString = '\x02AD{0};QSL\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('LampSelect', LampSelectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('LampSelect', value, qualifier)
            except (KeyError, IndexError):
                print('Update Lamp Select provided an Invalid/Unexpected Response for UpdateLampSelect')

    def UpdateLampUsage(self, value, qualifier):

        lamp = qualifier['Lamp']
        if lamp in ['1', '2']:
            LampUsageCmdString = '\x02AD{0};Q$L:{1}\x03'.format(self._DeviceID, lamp)
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    print('Update Lamp Usage provided an Invalid/Unexpected Response for UpdateLampUsage')
        else:
            print('Invalid Command for UpdateLampUsage')

    def SetLensShiftHorizontal(self, value, qualifier):

        SpeedStates = {
            'Slow': '\x00',
            'Normal': '\x01',
            'Fast': '\x02',
            'Home': '\x80'
        }

        ValueStateValues = {
            'Right': '\x00',
            'Left': '\x01'
        }

        speed = qualifier['Speed']
        if speed in SpeedStates:
            LensShiftHorizontalCmdString = '\x02{0}\xB1\x7C\x00{1}{2}\x03'.format(self.LensDeviceID, SpeedStates[speed], ValueStateValues[value])
            self.__SetHelper('LensShiftHorizontal', LensShiftHorizontalCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLensShiftHorizontal')

    def SetLensShiftVertical(self, value, qualifier):

        SpeedStates = {
            'Slow': '\x00',
            'Normal': '\x01',
            'Fast': '\x02',
            'Home': '\x80'
        }

        ValueStateValues = {
            'Up': '\x00',
            'Down': '\x01'
        }

        speed = qualifier['Speed']
        if speed in SpeedStates:
            LensShiftVerticalCmdString = '\x02{0}\xB1\x7C\x01{1}{2}\x03'.format(self.LensDeviceID, SpeedStates[speed], ValueStateValues[value])
            self.__SetHelper('LensShiftVertical', LensShiftVerticalCmdString, value, qualifier)
        else:
            print('Invalid Command for SetLensShiftVertical')

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
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Update On Screen Display provided an Invalid/Unexpected Response for UpdateOnScreenDisplay')

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
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('PictureinPicture', value, qualifier)
            except (KeyError, IndexError):
                print('Update Picture in Picture provided an Invalid/Unexpected Response for UpdatePictureinPicture')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Natural': '\x02AD{0};VPM:NAT\x03',
            'Standard': '\x02AD{0};VPM:STD\x03',
            'Dynamic': '\x02AD{0};VPM:DYN\x03',
            'Cinema': '\x02AD{0};VPM:CIN\x03',
            'Graphic': '\x02AD{0};VPM:GRA\x03',
            'DICOM': '\x02AD{0};VPM:DIC\x03'
        }

        PictureModeCmdString = ValueStateValues[value].format(self._DeviceID)
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            'NAT': 'Natural',
            'STD': 'Standard',
            'DYN': 'Dynamic',
            'CIN': 'Cinema',
            'GRA': 'Graphic',
            'DIC': 'DICOM'
        }

        PictureModeCmdString = '\x02AD{0};QPM\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Update Picture Mode provided an Invalid/Unexpected Response for UpdatePictureMode')

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
            '1': 'Warming Up',
            '3': 'Cooling Down'
        }

        PowerCmdString = '\x02AD{0};Q$S\x03'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Update Power provided an Invalid/Unexpected Response for UpdatePower')

    def UpdateTemperature(self, value, qualifier):

        LocationStates = {
            'Intake Air': '0',
            'Around Lamp': '1',
            'Optics Module': '2'
        }

        location = qualifier['Location']
        if location in LocationStates:
            TemperatureCmdString = '\x02AD{0};QTM:{1}\x03'.format(self._DeviceID, LocationStates[location])
            res = self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
            if res:
                try:
                    valuex = res[1:-1].decode().split('/')
                    if valuex[1][0] == '-':
                        value = '-{0} Degrees Fahrenheit'.format(valuex[1][1:].lstrip("0"))
                    else:
                        value = '{0} Degrees Fahrenheit'.format(valuex[1].lstrip("0"))
                    self.WriteStatus('Temperature', value, qualifier)
                except (KeyError, IndexError):
                    print('Update Temperature provided an Invalid/Unexpected Response for UpdateTemperature')
        else:
            print('Invalid Command for UpdateTemperature')

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
                value = ValueStateValues[res[1:-1].decode()]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Update Video Mute provided an Invalid/Unexpected Response for UpdateVideoMute')

    def SetZoom(self, value, qualifier):

        SpeedStates = {
            'Slow': '\x00',
            'Normal': '\x01',
            'Fast': '\x02'
        }

        ValueStateValues = {
            'In': '\x00',
            'Out': '\x01'
        }

        speed = qualifier['Speed']
        if speed in SpeedStates:
            ZoomCmdString = '\x02{0}\xB1\x7C\x03{1}{2}\x03'.format(self.LensDeviceID, SpeedStates[speed], ValueStateValues[value])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {b'\x02ER401\x03': 'Invalid Command.',
                              b'\x02ER402\x03': 'Invalid Parameter'}

        if response in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = b''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        commandstring = commandstring.encode(encoding='iso-8859-1')

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ' or ('0A' <= self._DeviceID <= '0Z'):
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                print('Setting {} command does not provide any response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 'ZZ' or '0A' <= self._DeviceID <= '0Z':
            print('Inappropriate Command ', command)
            return b''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring.encode(encoding='iso-8859-1'), self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                return b''
            else:
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
