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
            'AspectRatio': { 'Status': {}},
            'AVMode': { 'Status': {}},
            'ChannelDirectCommand': { 'Status': {}},
            'ChannelDirectStatus': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'DTVChannelDirectCommand': { 'Status': {}},
            'DTVChannelDirectStatus': { 'Status': {}},
            'DTVChannelStep': { 'Status': {}},
            'Input': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Normal'      : '1', 
            'Zoom (14:9)' : '2', 
            'Panorama'    : '3', 
            'Full'        : '4', 
            'Cinema 16:9' : '5', 
            'Cinema 14:9' : '6', 
            'Normal (PC)' : '7', 
            'Cinema (PC)' : '8', 
            'Full (PC)'   : '9', 
            'Dot by Dot'  : '10', 
            'Underscan'   : '11', 
            'Auto'        : '12', 
            'Original'    : '13'
        }

        self.__SetHelper('AspectRatio', 'WIDE{0:<4}\r'.format(States[value]) , value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            1 : 'Normal', 
            2 : 'Zoom (14:9)', 
            3 : 'Panorama', 
            4 : 'Full', 
            5 : 'Cinema 16:9', 
            6 : 'Cinema 14:9', 
            7 : 'Normal (PC)', 
            8 : 'Cinema (PC)', 
            9 : 'Full (PC)', 
           10 : 'Dot by Dot', 
           11 : 'Underscan', 
           12 : 'Auto', 
           13 : 'Original'
        }

        res = self.__UpdateHelper('AspectRatio', 'WIDE????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio',  States[int(res)] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAVMode(self, value, qualifier):

        States = {
            'Standard'        : '1', 
            'Movie'           : '2', 
            'Game'            : '3', 
            'User'            : '4', 
            'Dynamic (Fixed)' : '5', 
            'Dynamic'         : '6', 
            'PC'              : '7', 
            'x.v.Colour'      : '8', 
            'Auto'            : '100', 
        }

        self.__SetHelper('AVMode', 'AVMD{0:<4}\r'.format(States[value]) , value, qualifier)

    def UpdateAVMode(self, value, qualifier):

        States = {
            1 : 'Standard', 
            2 : 'Movie', 
            3 : 'Game', 
            4 : 'User', 
            5 : 'Dynamic (Fixed)', 
            6 : 'Dynamic', 
            7 : 'PC', 
            8 : 'x.v.Colour', 
          100 : 'Auto', 
        }

        res = self.__UpdateHelper('AVMode', 'AVMD????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AVMode',  States[int(res)] , qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mode: Invalid/unexpected response'])

    def SetChannelDirectCommand(self, value, qualifier):

        if value:
            if 1 <= int(value) <= 99:
                self.__SetHelper('ChannelDirectCommand', 'DCCH{0}  \r'.format(value.zfill(2)) , value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelDirectCommand')
        else:
            self.Discard('Invalid Command for SetChannelDirectCommand')

    def UpdateChannelDirectStatus(self, value, qualifier):

        res = self.__UpdateHelper('ChannelDirectStatus', 'DCCH????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('ChannelDirectStatus',   str(res[:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Channel Direct Status: Invalid/unexpected response'])

    def SetChannelStep(self, value, qualifier):

        States = {
            'Up'   : 'CHUP    \r',
            'Down' : 'CHDW    \r'
        }

        self.__SetHelper('ChannelStep', States[value] , value, qualifier)

    def SetDTVChannelDirectCommand(self, value, qualifier):

        if value:
            if 1 <= int(value) <= 999:
                self.__SetHelper('DTVChannelDirectCommand', 'DTVD{0} \r'.format(value.zfill(3)) , value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTVChannelDirectCommand')
        else:
            self.Discard('Invalid Command for SetDTVChannelDirectCommand')

    def UpdateDTVChannelDirectStatus(self, value, qualifier):

        res = self.__UpdateHelper('DTVChannelDirectStatus', 'DTVD????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('DTVChannelDirectStatus',  str(res[:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['DTV Channel Direct Status: Invalid/unexpected response'])

    def SetDTVChannelStep(self, value, qualifier):

        States = {
            'Up'   : 'DTUP    \r',
            'Down' : 'DTDW    \r'
        }

        self.__SetHelper('DTVChannelStep', States[value] , value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'HDMI 1'     : 'IAVD1   \r', 
            'HDMI 2'     : 'IAVD2   \r', 
            'HDMI 3'     : 'IAVD3   \r', 
            'HDMI 4'     : 'IAVD4   \r', 
            'Video 1'    : 'IAVD5   \r', 
            'Video 2'    : 'IAVD6   \r', 
            'PC'         : 'IAVD7   \r', 
            'Analog TV'  : 'ITVD    \r', 
            'Digital TV' : 'IDTV    \r'
        }

        if value != 'Analog TV' and value != 'Digital TV':
            self.__SetHelper('Input', States[value] , value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            1 : 'HDMI 1', 
            2 : 'HDMI 2', 
            3 : 'HDMI 3', 
            4 : 'HDMI 4', 
            5 : 'Video 1', 
            6 : 'Video 2', 
            7 : 'PC', 
        }

        res = self.__UpdateHelper('Input', 'IAVD????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Input',  States[int(res)] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        States = {
            'On'  : 1, 
            'Off' : 2
        }

        self.__SetHelper('Mute', 'MUTE{0:<4}\r'.format(States[value]) , value, qualifier)

    def UpdateMute(self, value, qualifier):

        States = {
            1 : 'On', 
            2 : 'Off'
        }

        res = self.__UpdateHelper('Mute', 'MUTE????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Mute',  States[int(res)] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On' : 'POWR1   \x0D',
            'Off': 'POWR0   \x0D', 
        }

        self.__SetHelper('Power', States[value] , value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            1 : 'On', 
            0 : 'Off'
        }

        res = self.__UpdateHelper('Power', 'POWR????\r' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Power',  States[int(res)] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'VOLM{0:03d} \r'.format(value) , value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', 'VOLM????\r' , value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {'ERR\r': 'Communication Error or Incorrect Command'}

        if response:
            if response in DEVICE_ERROR_CODES:
                self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response])])
                response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                if 'Power' == command:
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

