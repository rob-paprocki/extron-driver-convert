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
        self.Models = {
            'LX1000': self.chri_1_1406_1,
            'LW600': self.chri_1_1406_1,
            'LX900': self.chri_1_1406_1,
            'LX1200': self.chri_1_1406_LX1200,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampSelect': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp'], 'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            }        

    def SetAspectRatio(self, value, qualifier):

        self.__SetHelper('AspectRatio', self.AspectRatios[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        res = self.__UpdateHelper('AspectRatio', 'CR SCREEN\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', self.AspectRatioStates[res[4]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', 'C89\r', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'Off': 'CF KEYDIS NONE\r',
            'Mode 2': 'CF KEYDIS RC\r',
            'Mode 1': 'CF KEYDIS KEY\r'
        }

        self.__SetHelper('ExecutiveMode', States[value], value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        States = {
            'E': 'Off',
            'C': 'Mode 2',
            'Y': 'Mode 1'
        }

        res = self.__UpdateHelper('ExecutiveMode', 'CR KEYDIS\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('ExecutiveMode', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateExecutiveMode')

    def UpdateFilterUsage(self, value, qualifier):

        res = self.__UpdateHelper('FilterUsage', 'CR FILH\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage', int(res[4:-1]), qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        States = {
            'On': 'C43\r',
            'Off': 'C44\r'
        }
        self.__SetHelper('Freeze', States[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            'N': 'On',
            'F': 'Off'
        }

        res = self.__UpdateHelper('Freeze', 'CR FREEZE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', States[res[5]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateFreeze')

    def SetInput(self, value, qualifier):

        Inputs = {

            'Input 1 Analog': 'CF INPUT1 ANALOG\r',
            'Input 1 Digital': 'CF INPUT1 DIGITAL\r',
            'Input 1 HDCP': 'CF INPUT1 HDCP\r',

            'Input 2 Analog': 'CF INPUT2 ANALOG\r',
            'Input 2 Video': 'CF INPUT2 VIDEO\r',
            'Input 2 S-Video': 'CF INPUT2 S-VIDEO\r',
            'Input 2 YPbPr': 'CF INPUT2 YPBPR\r',

            'Input 3 Analog': 'CF INPUT3 ANALOG\r',
            'Input 3 Digital': 'CF INPUT3 DIGITAL\r',
            'Input 3 HDCP': 'CF INPUT3 ANALOG\r',
            'Input 3 S-Video': 'CF INPUT3 S-VIDEO\r',
            'Input 3 SCART': 'CF INPUT3 SCART\r',
            'Input 3 SDI-1': 'CF INPUT3 SDI1\r',
            'Input 3 SDI-2': 'CF INPUT3 SDI2\r',
            'Input 3 Video': 'CF INPUT3 VIDEO\r',
            'Input 3 YPbPr': 'CF INPUT3 YPBPR\r',

            'Input 4 Analog': 'CF INPUT4 ANALOG\r',
            'Input 4 Digital': 'CF INPUT4 DIGITAL\r',
            'Input 4 HDCP': 'CF INPUT4 HDCP\r',
            'Input 4 S-Video': 'CF INPUT4 S-VIDEO\r',
            'Input 4 SCART': 'CF INPUT4 SCART\r',
            'Input 4 SDI-1': 'CF INPUT4 SDI1\r',
            'Input 4 SDI-2': 'CF INPUT4 SDI2\r',
            'Input 4 Video': 'CF INPUT4 VIDEO\r',
            'Input 4 YPbPr': 'CF INPUT4 YPBPR\r'
        }

        self.__SetHelper('Input', Inputs[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStates = {

            '1ANALOG\r': 'Input 1 Analog',
            '1DIGITAL\r': 'Input 1 Digital',
            '1HDCP\r': 'Input 1 HDCP',

            '2ANALOG\r': 'Input 2 Analog',
            '2VIDEO\r': 'Input 2 Video',
            '2S-VIDEO\r': 'Input 2 S-Video',
            '2YPBPR\r': 'Input 2 YPbPr',

            '3ANALOG\r': 'Input 3 Analog',
            '3DIGITAL\r': 'Input 3 Digital',
            '3HDCP\r': 'Input 3 HDCP',
            '3S-VIDEO\r': 'Input 3 S-Video',
            '3SCART\r': 'Input 3 SCART',
            '3SDI1\r': 'Input 3 SDI-1',
            '3SDI2\r': 'Input 3 SDI-2',
            '3VIDEO\r': 'Input 3 Video',
            '3YPBPR\r': 'Input 3 YPbPr',

            '4ANALOG\r': 'Input 4 Analog',
            '4DIGITAL\r': 'Input 4 Digital',
            '4HDCP\r': 'Input 4 HDCP',
            '4S-VIDEO\r': 'Input 4 S-Video',
            '4SCART\r': 'Input 4 SCART',
            '4SDI1\r': 'Input 4 SDI-1',
            '4SDI2\r': 'Input 4 SDI-2',
            '4VIDEO\r': 'Input 4 Video',
            '4YPBPR\r': 'Input 4 YPbPr'
        }
        res1 = self.__UpdateHelper('Input', 'CR INPUT\r', value, qualifier)
        res2 = self.__UpdateHelper('Input', 'CR SOURCE\r', value, qualifier)
        if res1 and res2:
            try:
                value = InputStates[res1[-2] + res2[4:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal': 'CF AUTOLAMPCONTRL NORMAL \r',
            'ECO': 'CF AUTOLAMPCONTRL ECO \r',
            'Auto': 'CF AUTOLAMPCONTRL AUTO \r'
        }

        self.__SetHelper('LampMode', States[value], value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        States = {
            'A': 'Normal',
            'C': 'ECO',
            'T': 'Auto'
        }

        res = self.__UpdateHelper('LampMode', 'CR AUTOLAMPCONTRL\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode', States[res[-3]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampMode')

    def SetLampSelect(self, value, qualifier):

        States = {
            'Full': 'CF LAMPMODE FULL \r',
            'Half': 'CF LAMPMODE HALF \r'
        }

        self.__SetHelper('LampSelect', States[value], value, qualifier)

    def UpdateLampSelect(self, value, qualifier):

        States = {
            'F': 'Full',
            'H': 'Half'
        }

        res = self.__UpdateHelper('LampSelect', 'CR LAMPMODE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampSelect', States[res[-5]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampSelect')

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', 'CR LAMPH\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage', int(res[4:8]), {'Lamp': '1'})
                self.WriteStatus('LampUsage', int(res[9:-1]), {'Lamp': '2'})
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', 'CR PROJH\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('OperationHours', int(res[4:-1]), qualifier)
            except (ValueError, ValueError):
                print('Invalid/Unexpected Response for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        States = {
            'On': 'C00\r',
            'Off': 'C01\r',
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            '00': 'On',
            '02': 'Invalid RS-232C Command',
            '04': 'Power Save',
            '10': 'Power Failure',
            '20': 'Cooling Down',
            '21': 'Cooling Down in process after turned Off due to lamp failure',
            '24': 'Power Save/Cooling Down in process',
            '28': 'Cooling Down in process due to abnormal temperature',
            '2C': 'Cooling Down in process after Power Off due to Shutter management',
            '40': 'Warming Up',
            '80': 'Off',
            '81': 'Standby after Cooling Down due to lamp failure',
            '88': 'Standby after Cooling Down due to abnormal temperature',
            '8C': 'Standby after Cooling Down due to Shutter management'
        }

        res = self.__UpdateHelper('Power', 'CR STATUS\r', value, qualifier)
        if res:

            try:
                result = res[4:6]
                if result in ['00', '02']:
                    self.WriteStatus('Power', 'On', qualifier)
                elif result == '40':
                    self.WriteStatus('Power', 'Warming Up', qualifier)
                elif result in ['04', '10', '80', '81', '88', '8C']:
                    self.WriteStatus('Power', 'Off', qualifier)
                elif result in ['20', '21', '24', '28', '2C']:
                    self.WriteStatus('Power', 'Cooling Down', qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

            try:
                result = res[4:6]
                if result in ['00', '04', '20', '24', '40', '80']:
                    self.WriteStatus('DeviceStatus', 'Normal', qualifier)
                else:
                    self.WriteStatus('DeviceStatus', States[result], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': 'C0D\r',
            'Off': 'C0E\r'
        }

        self.__SetHelper('VideoMute', States[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        States = {
            'N': 'On',
            'F': 'Off'
        }

        res = self.__UpdateHelper('VideoMute', 'CR VMUTE\r', value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        DEVICE_ERROR_CODES = {
            '?\r': 'Parameter designation error (wrong digit number, including invalid value, etc.).',
            '101\r': 'The function is not available in the selected Mode.',
            '102\r': 'Directly specified value or values are out of range.',
            '103\r': 'Command mismatched to Hardware (the command is for Optional function which is not implemented)',
            '201\r': 'Incremented or decremented value or values are beyond upper or lower limits.',
            '301\r': 'Not executable due to screen capturing in process. Prompting reissue of the command after a while.',
            '402\r': 'Not executable due to PIN code in operation. Prompting reissue of the command after a while.',
            }

        if response in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response]))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if res:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False        

    def chri_1_1406_1(self):

        self.AspectRatios = {
            'Normal' : 'CF SCREEN NORMAL\r', 
            'Full'   : 'CF SCREEN FULL\r'
        }   
            
        self.AspectRatioStates = {
            'N' : 'Normal', 
            'F' : 'Full'
        }

        self.AspectRatios = {
            'Normal' : 'CF SCREEN NORMAL\r', 
            'Wide'   : 'CF SCREEN WIDE\r'
        }   
            
        self.AspectRatioStates = {
            'N' : 'Normal', 
            'W' : 'Wide'
        }

    def chri_1_1406_LX1200(self):

        self.AspectRatios = {
            'Normal' : 'CF SCREEN NORMAL\r', 
            'Wide'   : 'CF SCREEN WIDE\r'
        }   
            
        self.AspectRatioStates = {
            'N' : 'Normal', 
            'W' : 'Wide'
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

