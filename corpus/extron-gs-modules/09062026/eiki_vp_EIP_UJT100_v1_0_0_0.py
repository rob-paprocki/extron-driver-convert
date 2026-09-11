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


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio'        : {'Status': {}},
            'AutoImage'          : {'Status': {}},
            'Focus'              : {'Status': {}},
            'Input'              : {'Status': {}},
            'LampMode'           : {'Status': {}},
            'LampStatus'         : {'Parameters':['Lamp'], 'Status': {}},
            'LampUsage'          : {'Parameters':['Lamp'], 'Status': {}},
            'MenuNavigation'     : {'Status': {}},
            'Power'              : {'Status': {}},
            'VideoMute'          : {'Status': {}},
            'Zoom'               : {'Status': {}}
            }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '5:4'       : '1', 
            '4:3'       : '2', 
            '16:10'     : '3', 
            '16:9'      : '4', 
            '1.88'      : '5', 
            '2.35'      : '6', 
            'Letterbox' : '7', 
            'Native'    : '8', 
            'Unscaled'  : '9'
        }

        AspectRatioCmdString = 'CF_ASPECT_{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1' : '5:4', 
            '2' : '4:3', 
            '3' : '16:10', 
            '4' : '16:9', 
            '5' : '1.88', 
            '6' : '2.35', 
            '7' : 'Letterbox', 
            '8' : 'Native', 
            '9' : 'Unscaled'
        }

        AspectRatioCmdString = 'CR_ASPECT\r\n'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Aspect Ratio query has invalid/unexpected response for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'C89\r\n'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)


    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far'  : 'C4A\r\n', 
            'Near' : 'C4B\r\n'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)


    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI'       : 'C36\r\n', 
            'HDBaseT'    : 'C38\r\n', 
            'VGA'        : 'C05\r\n', 
            'YUV1'       : 'C33\r\n', 
            'RGBHV/YUV2' : 'C54\r\n', 
            'SDI'        : 'C55\r\n', 
            '3D DVI'     : 'C52\r\n'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1' : 'HDMI', 
            '2' : 'HDBaseT', 
            '3' : 'VGA', 
            '4' : 'YUV1', 
            '5' : 'RGBHV/YUV2', 
            '6' : 'SDI', 
            '7' : '3D DVI'
        }

        InputCmdString = 'CR1\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Input query has invalid/unexpected response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco'                : '1', 
            'Normal'             : '2', 
            'Custom Power Level' : '3'
        }

        LampModeCmdString = 'CF_AUTOLAMPSONTROL_{0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Eco', 
            '2' : 'Normal', 
            '3' : 'Custom Power Level'
        }

        LampModeCmdString = 'CR_AUTOLAMPCONTROL\r\n'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Lamp Mode query has invalid/unexpected response for UpdateLampMode')

    def UpdateLampStatus(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        Lamp = qualifier['Lamp']
        LampStatusCmdString = 'CR7\r\n'
        res = self.__UpdateHelper('LampStatus', LampStatusCmdString, value, qualifier)
        if Lamp in ['1','2']:
            if res:
                try:
                    value = ValueStateValues[res[-3]]
                    self.WriteStatus('LampStatus', value, {'Lamp' : '1'})
                    value = ValueStateValues[res[-2]]
                    self.WriteStatus('LampStatus', value,{'Lamp' : '2'})
                except (KeyError, IndexError):
                    print('Lamp Mode query has invalid/unexpected response for UpdateLampStatus')
        else:
            print('Invalid Command for UpdateLampStatus')

    def UpdateLampUsage(self, value, qualifier):

        Lamp = qualifier['Lamp']
        LampUsageCmdString = 'CR3\r\n'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if Lamp in ['1','2']:
            if res:
                try:
                    value = int(res.split()[0])
                    self.WriteStatus('LampUsage', value, {'Lamp' : '1'})
                    value = int(res.split()[1])
                    self.WriteStatus('LampUsage', value, {'Lamp' : '2'})
                except (ValueError, IndexError):
                    print('Lamp Usage query has invalid/unexpected response for UpdateLampUsage')
        else:
            print('Invalid Command for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : 'C1C\r\n', 
            'Enter' : 'C3F\r\n', 
            'Up'    : 'C3C\r\n', 
            'Down'  : 'C3D\r\n', 
            'Left'  : 'C3A\r\n', 
            'Right' : 'C3B\r\n'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'C00\r\n', 
            'Off' : 'C01\r\n', 
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2' : 'On', 
            '0' : 'Off', 
            '1' : 'Warming Up', 
            '3' : 'Cooling Down'
        }

        PowerCmdString = 'CR0\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Power query has invalid/unexpected response for UpdatePower')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'C0D\r\n', 
            'Off' : 'C0E\r\n'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)


    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Zoom In'  : 'C46\r\n', 
            'Zoom Out' : 'C47\r\n'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if sourceCmdName == 'Power' and response[-2] == '4':
            print('Power Warning')
            return ''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r').decode()
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='None', CharDelay=0, Model=None):
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