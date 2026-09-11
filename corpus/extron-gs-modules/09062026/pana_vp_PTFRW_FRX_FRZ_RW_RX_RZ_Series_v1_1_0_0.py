from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify

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
        self.Models = {
            'PT-RW930': self.pana_1_2583_noSDI_Serial,
            'PT-RX110': self.pana_1_2583_noSDI_Serial,
            'PT-FRZ98C': self.pana_1_2583_SDI_Serial,
            'PT-FRW93C': self.pana_1_2583_noSDI_Serial,
            'PT-FRX110C': self.pana_1_2583_noSDI_Serial,
            'PT-RZ770': self.pana_1_2583_SDI_Serial,
            'PT-RW730': self.pana_1_2583_noSDI_Serial,
            'PT-FRZ78C': self.pana_1_2583_SDI_Serial,
            'PT-FRW73C': self.pana_1_2583_noSDI_Serial,
            'PT-RZ660': self.pana_1_2583_SDI_Serial,
            'PT-RW620': self.pana_1_2583_noSDI_Serial,
            'PT-FRZ67C': self.pana_1_2583_SDI_Serial,
            'PT-FRW62C': self.pana_1_2583_noSDI_Serial,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'LensShiftHorizontal': { 'Status': {}},
            'LensShiftVertical': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'Zoom': { 'Status': {}},
            }



    @property
    def DeviceID(self):
        if len(self._DeviceID) == 1:
            self._DeviceID = '0{0}'.format(self._DeviceID)
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto'           : '\x02AD{};VSE:0\x03',
            'Normal'         : '\x02AD{};VSE:1\x03',
            'Wide'           : '\x02AD{};VSE:2\x03',
            'Native'         : '\x02AD{};VSE:5\x03',
            'Full'           : '\x02AD{};VSE:6\x03',
            'Horizontal Fit' : '\x02AD{};VSE:9\x03', 
            'Vertical Fit'   : '\x02AD{};VSE:10\x03'
        }

        AspectRatioCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x020\x03'  : 'Auto',
            b'\x021\x03'  : 'Normal',
            b'\x022\x03'  : 'Wide',
            b'\x025\x03'  : 'Native',
            b'\x026\x03'  : 'Full',
            b'\x029\x03'  : 'Horizontal Fit',
            b'\x0210\x03' : 'Vertical Fit'
        }

        AspectRatioCmdString = '\x02AD{};QSE\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except KeyError:
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\x02AD{};OAS\x03'.format(self.DeviceID).encode()
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)


    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off' : '\x02AD{};OCC:0\x03', 
            '1'   : '\x02AD{};OCC:1\x03',
            '2'   : '\x02AD{};OCC:2\x03',
            '3'   : '\x02AD{};OCC:3\x03',
            '4'   : '\x02AD{};OCC:4\x03'
        }

        ClosedCaptionCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            b'\x020\x03' : 'Off',
            b'\x021\x03' : '1',
            b'\x022\x03' : '2',
            b'\x023\x03' : '3',
            b'\x024\x03' : '4'
        }

        ClosedCaptionCmdString = '\x02AD{};QCC\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except KeyError:
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Slow +'    : '\x02AD{};VXX:LNSI4=+00000\x03',
            'Slow -'    : '\x02AD{};VXX:LNSI4=+00001\x03',
            'Normal +'  : '\x02AD{};VXX:LNSI4=+00100\x03',
            'Normal -'  : '\x02AD{};VXX:LNSI4=+00101\x03',
            'Fast +'    : '\x02AD{};VXX:LNSI4=+00200\x03',
            'Fast -'    : '\x02AD{};VXX:LNSI4=+00201\x03'
        }

        FocusCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)


    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x02AD{};OFZ:1\x03',
            'Off' : '\x02AD{};OFZ:0\x03'
        }

        FreezeCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x021\x03' : 'On',
            b'\x020\x03' : 'Off'
        }

        FreezeCmdString = '\x02AD{};QFZ\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except KeyError:
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = self.InputValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = '\x02AD{};QIN\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStates[res]
                self.WriteStatus('Input', value, qualifier)
            except KeyError:
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : '\x02AD{};ONK:0\x03', 
            '1' : '\x02AD{};ONK:1\x03', 
            '2' : '\x02AD{};ONK:2\x03', 
            '3' : '\x02AD{};ONK:3\x03', 
            '4' : '\x02AD{};ONK:4\x03', 
            '5' : '\x02AD{};ONK:5\x03', 
            '6' : '\x02AD{};ONK:6\x03', 
            '7' : '\x02AD{};ONK:7\x03', 
            '8' : '\x02AD{};ONK:8\x03', 
            '9' : '\x02AD{};ONK:9\x03'
        }

        KeypadCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)


    def UpdateLampUsage(self, value, qualifier):

        if qualifier['Lamp'] in ['1','2']:
            LampUsageCmdString = '\x02AD{};Q$L:{}\x03'.format(self.DeviceID, qualifier['Lamp']).encode()
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1:-1])
                    self.WriteStatus('LampUsage', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetLensShiftHorizontal(self, value, qualifier):

        ValueStateValues = {
            'Slow +'   : '\x02AD{};VXX:LNSI2=+00000\x03',
            'Slow -'   : '\x02AD{};VXX:LNSI2=+00001\x03',
            'Normal +' : '\x02AD{};VXX:LNSI2=+00100\x03', 
            'Normal -' : '\x02AD{};VXX:LNSI2=+00101\x03', 
            'Fast +'   : '\x02AD{};VXX:LNSI2=+00200\x03',
            'Fast -'   : '\x02AD{};VXX:LNSI2=+00201\x03'
        }

        LensShiftHorizontalCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('LensShiftHorizontal', LensShiftHorizontalCmdString, value, qualifier)


    def SetLensShiftVertical(self, value, qualifier):

        ValueStateValues = {
            'Slow +'   : '\x02AD{};VXX:LNSI3=+00000\x03',
            'Slow -'   : '\x02AD{};VXX:LNSI3=+00001\x03',
            'Normal +' : '\x02AD{};VXX:LNSI3=+00100\x03', 
            'Normal -' : '\x02AD{};VXX:LNSI3=+00101\x03', 
            'Fast +'   : '\x02AD{};VXX:LNSI3=+00200\x03',
            'Fast -'   : '\x02AD{};VXX:LNSI3=+00201\x03'
        }

        LensShiftVerticalCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('LensShiftVertical', LensShiftVerticalCmdString, value, qualifier)


    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'     : '\x02AD{};OMN\x03',
            'Enter'    : '\x02AD{};OEN\x03',
            'Up'       : '\x02AD{};OCU\x03',
            'Down'     : '\x02AD{};OCD\x03',
            'Left'     : '\x02AD{};OCL\x03',
            'Right'    : '\x02AD{};OCR\x03',
            'Default'  : '\x02AD{};OST\x03',
            'Function' : '\x02AD{};FC1\x03'
        }

        MenuNavigationCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '\x02AD{};QVX:RTMS1\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic'   : '\x02AD{};VPM:DYN\x03',
            'Natural'   : '\x02AD{};VPM:NAT\x03',
            'Standard'  : '\x02AD{};VPM:STD\x03',
            'Cinema'    : '\x02AD{};VPM:CIN\x03',
            'Graphic'   : '\x02AD{};VPM:GRA\x03',
            'Dicom Sim' : '\x02AD{};VPM:DIC\x03', 
            'User'      : '\x02AD{};VPM:USR\x03',
            'REC709'    : '\x02AD{};VPM:709\x03'
        }

        PictureModeCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'\x02DYN\x03' : 'Dynamic',
            b'\x02NAT\x03' : 'Natural',
            b'\x02STD\x03' : 'Standard',
            b'\x02CIN\x03' : 'Cinema',
            b'\x02GRA\x03' : 'Graphic',
            b'\x02DIC\x03' : 'Dicom Sim',
            b'\x02USR\x03' : 'User',
            b'\x02709\x03' : 'REC709'
        }
        PictureModeCmdString = '\x02AD{};QPM\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PictureMode', value, qualifier)
            except KeyError:
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x02AD{};PON\x03',
            'Off' : '\x02AD{};POF\x03',
        }

        PowerCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x022\x03': 'On',
            b'\x021\x03': 'Warming Up',
            b'\x023\x03': 'Cooling Down',
            b'\x020\x03': 'Off'
        }

        PowerCmdString = '\x02AD{};Q$S\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Power', value, qualifier)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On'  : '\x02AD{};OSH:1\x03',
            'Off' : '\x02AD{};OSH:0\x03'
        }

        ShutterCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            b'\x021\x03' : 'On',
            b'\x020\x03' : 'Off'
        }

        ShutterCmdString = '\x02AD{};QSH\x03'.format(self.DeviceID).encode()
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Shutter', value, qualifier)
            except KeyError:
                self.Error(['Shutter: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Slow +'   : '\x02AD{};VXX:LNSI5=+00000\x03',
            'Slow -'   : '\x02AD{};VXX:LNSI5=+00001\x03',
            'Normal +' : '\x02AD{};VXX:LNSI5=+00100\x03', 
            'Normal -' : '\x02AD{};VXX:LNSI5=+00101\x03', 
            'Fast +'   : '\x02AD{};VXX:LNSI5=+00200\x03',
            'Fast -'   : '\x02AD{};VXX:LNSI5=+00201\x03'
        }

        ZoomCmdString = ValueStateValues[value].format(self.DeviceID).encode()
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '\x02ER401\x03': 'Invalid Command Reply.',
            '\x02ER402\x03': 'Invalid Parameter.'
        }

        if response in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()    

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x03')
                
            return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def pana_1_2583_SDI_Serial(self):

        self.InputValues = {
            'RGB 1'        : '\x02AD{};IIS:RG1\x03',
            'RGB 2'        : '\x02AD{};IIS:RG2\x03',
            'DVI'          : '\x02AD{};IIS:DVI\x03',
            'HDMI'         : '\x02AD{};IIS:HD1\x03',
            'SDI'          : '\x02AD{};IIS:SD1\x03',
            'Digital Link' : '\x02AD{};IIS:DL1\x03',
            'Video'        : '\x02AD{};IIS:VID\x03',
            'S-Video'      : '\x02AD{};IIS:SVD\x03'
        }
        self.InputStates = {
            b'\x02RG1\x03' : 'RGB 1',
            b'\x02RG2\x03' : 'RGB 2',
            b'\x02DVI\x03' : 'DVI',
            b'\x02HD1\x03' : 'HDMI',
            b'\x02SD1\x03' : 'SDI',
            b'\x02DL1\x03' : 'Digital Link',
            b'\x02VID\x03' : 'Video',
            b'\x02SVD\x03' : 'S-Video'
        }


    def pana_1_2583_noSDI_Serial(self):

        self.InputValues = {
            'RGB 1'        : '\x02AD{};IIS:RG1\x03',
            'RGB 2'        : '\x02AD{};IIS:RG2\x03',
            'DVI'          : '\x02AD{};IIS:DVI\x03',
            'HDMI'         : '\x02AD{};IIS:HD1\x03',
            'Digital Link' : '\x02AD{};IIS:DL1\x03',
            'Video'        : '\x02AD{};IIS:VID\x03',
            'S-Video'      : '\x02AD{};IIS:SVD\x03'
        }
        self.InputStates = {
            b'\x02RG1\x03' : 'RGB 1',
            b'\x02RG2\x03' : 'RGB 2',
            b'\x02DVI\x03' : 'DVI',
            b'\x02HD1\x03' : 'HDMI',
            b'\x02DL1\x03' : 'Digital Link',
            b'\x02VID\x03' : 'Video',
            b'\x02SVD\x03' : 'S-Video'
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

class DeviceEthernetClass:


    
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = 'panasonic'
        self.Models = {
            'PT-FRW62C': self.pana_1_2583_noSDI_Ethernet,
            'PT-FRW73C': self.pana_1_2583_noSDI_Ethernet,
            'PT-FRW93C': self.pana_1_2583_noSDI_Ethernet,
            'PT-FRX110C': self.pana_1_2583_noSDI_Ethernet,
            'PT-FRZ67C': self.pana_1_2583_SDI_Ethernet,
            'PT-FRZ78C': self.pana_1_2583_SDI_Ethernet,
            'PT-FRZ98C': self.pana_1_2583_SDI_Ethernet,
            'PT-RW620': self.pana_1_2583_noSDI_Ethernet,
            'PT-RW730': self.pana_1_2583_noSDI_Ethernet,
            'PT-RW930': self.pana_1_2583_noSDI_Ethernet,
            'PT-RX110': self.pana_1_2583_noSDI_Ethernet,
            'PT-RZ660': self.pana_1_2583_SDI_Ethernet,
            'PT-RZ770': self.pana_1_2583_SDI_Ethernet,
            }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': {'Parameters':['Lamp'], 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            }

        self.md5hash = ''
        self.Authentication = 'Undetermined'
        






                    

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-zA-Z0-9]{8})\r'), self.__MatchAuthentication, None)
            self.AddMatchString(re.compile(b'PJLINK 0\r'), self.__MatchNoAuthentication, None)
            self.UpdateDeviceStatusMatch = re.compile('%1ERST=([0-2]{6})\r')
            self.UpdateInputMatch = re.compile('%1INPT=(11|12|31|32|33|34)\r')
            self.UpdateLampUsageMatch = re.compile('%1LAMP=([0-9]{1,5}) [01] ([0-9]{1,5}) [01]\r')
            self.UpdatePowerMatch = re.compile('%1POWR=([0-3])\r')
            self.UpdateShutterMatch = re.compile('%1AVMT=3([01])\r')
            self.ErrorMatch = re.compile('ERR([1234A])\r')


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value

    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = rand_num + self.devicePassword
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Authentication = 'Authenticated'

    def __MatchNoAuthentication(self, match, tag):
        self.Authentication = 'Not Needed'



    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0 : 'Fan',
            1 : 'Light Source',
            2 : 'Temperature',
            4 : 'Filter',
            5 : 'Other'
        }

        DeviceStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateDeviceStatusMatch, res)
                if matchObject:
                    ErrorStrings = matchObject.group(1)
                    if ErrorStrings.count('1') + ErrorStrings.count('2') == 0:
                        value = 'Normal'
                    if ErrorStrings.count('1') + ErrorStrings.count('2') >= 2:
                        value = 'Multiple Errors/Warnings'
                    elif ErrorStrings.count('1') == 1:
                        index = ErrorStrings.index('1')
                        value = '{} Warning'.format(ValueStateValues[index])
                    elif ErrorStrings.count('2') == 1:
                        index = ErrorStrings.index('2')
                        value = '{} Error'.format(ValueStateValues[index])
                    self.WriteStatus('DeviceStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = '%1INPT {}\r'.format(self.InputValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        InputCmdString = '%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateInputMatch, res)
                if matchObject:
                    value = self.InputStates[matchObject.group(1)]
                    self.WriteStatus('Input', value, None)
            except KeyError:
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        if qualifier['Lamp'] in ['1', '2']:
            LampUsageCmdString = '%1LAMP ?\r'
            res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
            if res:
                try:
                    matchObject = re.search(self.UpdateLampUsageMatch, res)
                    if matchObject:
                        lamp1 = int(matchObject.group(1))
                        lamp2 = int(matchObject.group(2))
                        self.WriteStatus('LampUsage', lamp1, {'Lamp': '1'})
                        self.WriteStatus('LampUsage', lamp2, {'Lamp': '2'})
                except ValueError:
                    self.Error(['Lamp Usage: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        PowerCmdString = '%1POWR {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off',
            '3' : 'Warming Up',
            '2' : 'Cooling Down'
        }

        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdatePowerMatch, res)
                if matchObject:
                    value = ValueStateValues[matchObject.group(1)]
                    self.WriteStatus('Power', value, None)
            except KeyError:
                self.Error(['Power: Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On'  : '31',
            'Off' : '30'
        }

        ShutterCmdString = '%1AVMT {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        ShutterCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                matchObject = re.search(self.UpdateShutterMatch, res)
                if matchObject:
                    value = ValueStateValues[matchObject.group(1)]
                    self.WriteStatus('Shutter', value, qualifier)
            except KeyError:
                self.Error(['Shutter: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()
        if 'ERR' in response:
            MatchObject = re.search(self.ErrorMatch, response)
            if MatchObject:
                DEVICE_ERROR_CODES = {
                    '1' : 'Undefined control command',
                    '2' : 'Out of parameter range',
                    '3' : 'Busy state or no-acceptable period',
                    '4' : 'Timeout or no-acceptable period',
                    'A' : 'Password mismatch'
                }
                self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[MatchObject.group(1)])])
                if 'ERRA' in response:
                    self.Authentication = 'Invalid'
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Authentication == 'Authenticated':
            if command == 'UserDefinedCommand':
                commandstring = self.md5hash + commandstring
            else:
                commandstring = self.md5hash + commandstring.encode()

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authentication in ['Authenticated', 'Not Needed']:
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

                if self.Authentication == 'Authenticated':
                    commandstring = self.md5hash + commandstring.encode()
                    
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
                    
                return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)
            return''
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.md5hash = ''
        self.Authentication = 'Undetermined'
        

    def pana_1_2583_SDI_Ethernet(self):

        self.InputValues = {
            'RGB 1'        : '11',
            'RGB 2'        : '12',
            'DVI'          : '31',
            'HDMI'         : '32',
            'SDI'          : '34',
            'Digital Link' : '33'
        }
        self.InputStates = {
            '11' : 'RGB 1',
            '12' : 'RGB 2',
            '31' : 'DVI',
            '32' : 'HDMI',
            '34' : 'SDI',
            '33' : 'Digital Link'
        }


    def pana_1_2583_noSDI_Ethernet(self):

        self.InputValues = {
            'RGB 1'        : '11',
            'RGB 2'        : '12',
            'DVI'          : '31',
            'HDMI'         : '32',
            'Digital Link' : '33'
        }
        self.InputStates = {
            '11' : 'RGB 1',
            '12' : 'RGB 2',
            '31' : 'DVI',
            '32' : 'HDMI',
            '33' : 'Digital Link'
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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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