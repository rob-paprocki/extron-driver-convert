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
            'AutoImage': { 'Status': {}},
            'Focus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'IntegratorRodTemperature': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampPower': {'Parameters':['Lamp Type'], 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'ScreenOrientation': { 'Status': {}},
            'Sharpness': { 'Status': {}},
            'Shutter': { 'Status': {}},
            }                                          

        
        self.Integator      = re.compile(r'\(SST\+TEMP!000 000 "([0-9]{2})')
        self.LampUsage      = re.compile(r'\(HIS![0-9]{4} ".*?" ".*?" ".*?" [0-9]{4} [0-9]{4} [0-9]{4} [0-9]{4} ([0-9]{4})\)')
        self.Power    = re.compile(r'\(PWR!0([0-1]{2}).*?\)')


    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', '(ASU)' , value, qualifier)

    def SetFocus(self, value, qualifier):

        if -2000 <= value <= 2800:
            self.__SetHelper('Focus', '(FCS {0})'.format(value) , value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        States = {
            'On'    : '(FRZ 1)', 
            'Off'   : '(FRZ 0)'
        }

        self.__SetHelper('Freeze', States[value] , value, qualifier)

    def UpdateIntegratorRodTemperature(self, value, qualifier):

        res = self.__UpdateHelper('IntegratorRodTemperature', '(SST+TEMP!000?)' , value, qualifier)
        if res:
            try:
                temp = self.Integator.findall(res)
                value = temp[0]
                self.WriteStatus('IntegratorRodTemperature', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Integrator Rod Temperature'])

    def SetLampMode(self, value, qualifier):

        States = {
            'Constant Power Mode'       : '(LPM 0)', 
            'Constant Intensity Mode'   : '(LPM 1)'
        }

        self.__SetHelper('LampMode', States[value] , value, qualifier)

    def SetLampPower(self, value, qualifier):

        Lamp = qualifier['Lamp Type']
        if 1000 <= value <= 6600 and Lamp in ['CDXL-20', 'CDXL-30', 'CDXL-45', 'CDXL-60']:
            if Lamp == 'CDXL-20' and 1000 <= value <= 2200:
                CmdString = '(LPP {})'.format(value)
            elif Lamp == 'CDXL-30' and 2000 <= value <= 3300:
                CmdString = '(LPP {})'.format(value)
            elif Lamp == 'CDXL-45' and 2300 <= value <= 4950:
                CmdString = '(LPP {})'.format(value)
            elif Lamp == 'CDXL-60' and 2750 <= value <= 6600:
                CmdString = '(LPP {})'.format(value)
            else:
                CmdString = ''
            if CmdString:
                self.__SetHelper('LampPower', CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetLampPower')
        else:
            self.Discard('Invalid Command for SetLampPower')
        
    def UpdateLampPower(self, value, qualifier):

        res = self.__UpdateHelper('LampPower', '(LPP?)' , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampPower',  int(res[5:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Lamp Power'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', '(HIS?)' , value, qualifier)
        if res:
            try:
                temp = self.LampUsage.findall(res)
                self.WriteStatus('LampUsage',  int(temp[0]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Lamp Usage'])

    def SetPower(self, value, qualifier):

        States = {
            'On'    : '(PWR 1)', 
            'Off'   : '(PWR 0)', 
        }

        self.__SetHelper('Power', States[value] , value, qualifier)
    def UpdatePower(self, value, qualifier):

        States = {
            '01' : 'On', 
            '00' : 'Off', 
            '11' : 'Warming Up', 
            '10' : 'Cooling Down'
        }

        res = self.__UpdateHelper('Power', '(PWR?)' , value, qualifier)
        if res:
            try:
                temp = self.Power.findall(res)
                self.WriteStatus('Power',  States[temp[0]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Power'])

    def SetScreenOrientation(self, value, qualifier):

        States = {
            'Front Projection'          : '(SOR 0)', 
            'Rear Projection'           : '(SOR 1)', 
            'Front Projection Inverted' : '(SOR 2)', 
            'Rear Projection Inverted'  : '(SOR 3)'
        }

        self.__SetHelper('ScreenOrientation', States[value] , value, qualifier)

    def SetSharpness(self, value, qualifier):


        if 0 <= value <= 100:
            self.__SetHelper('Sharpness', '(DTL {})'.format(value) , value, qualifier)
        else:
            self.Discard('Invalid Command for SetSharpness')


    def UpdateSharpness(self, value, qualifier):

        res = self.__UpdateHelper('Sharpness', '(DTL?)' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Sharpness',  int(res[5:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetShutter(self, value, qualifier):

        States = {
            'Open'  : '(SHU 0)', 
            'Close' : '(SHU 1)'
        }

        self.__SetHelper('Shutter', States[value] , value, qualifier)

    def UpdateShutter(self, value, qualifier):

        States = {
            '0' : 'Open', 
            '1' : 'Close'
        }

        res = self.__UpdateHelper('Shutter', '(SHU?)' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Shutter',  States[res[6]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Shutter'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b')')
            if not res:
                self.Error(['Invalid/unexpected response for {}'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b')')
            if not res:
                if command == 'Power':
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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

