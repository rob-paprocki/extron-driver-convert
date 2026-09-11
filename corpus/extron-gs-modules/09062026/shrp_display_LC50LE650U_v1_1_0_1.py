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
            'ChannelTV': { 'Status': {}},
            'ChannelTVCommand': { 'Status': {}},
            'ClosedCaptions': { 'Status': {}},
            'DigitalAirCommand': { 'Status': {}},
            'DigitalCableCommand1': { 'Status': {}},
            'DigitalCableCommand2': { 'Status': {}},
            'DigitalCableMajorCommand': { 'Status': {}},
            'DigitalCableMinorCommand': { 'Status': {}},
            'Input': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }





    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal'        : 'WIDE1   \r', 
            'Smart Stretch' : 'WIDE2   \r', 
            'Zoom 1'        : 'WIDE3   \r', 
            'Zoom 2'        : 'WIDE4   \r', 
            'Full Screen'   : 'WIDE5   \r', 
            'Dot by Dot'    : 'WIDE6   \r', 
            'Cinema'        : 'WIDE7   \r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1' : 'Normal', 
            '2' : 'Smart Stretch', 
            '3' : 'Zoom 1', 
            '4' : 'Zoom 2', 
            '5' : 'Full Screen', 
            '6' : 'Dot by Dot', 
            '7' : 'Cinema'
        }

        AspectRatioCmdString = 'WIDE????\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetChannelTV(self, value, qualifier):

        ValueStateValues = {
            'Up'   : 'CHUP0   \r', 
            'Down' : 'CHDW0   \r'
        }

        ChannelTVCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelTV', ChannelTVCmdString, value, qualifier)


    def SetChannelTVCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 1 <= int(tempValue) <= 135:
                ChannelTVCommandCmdString = 'DCCH{0:03d} \r'.format(int(tempValue))
                self.__SetHelper('ChannelTVCommand', ChannelTVCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelTVCommand')
        else:
            self.Discard('Invalid Command for SetChannelTVCommand')


    def SetClosedCaptions(self, value, qualifier):

        ClosedCaptionsCmdString = 'CLCP1   \r'
        self.__SetHelper('ClosedCaptions', ClosedCaptionsCmdString, value, qualifier)


    def SetDigitalAirCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 100 <= int(tempValue) <= 9999:
                DigitalAirCommandCmdString = 'DA2P{0:04d}\r'.format(int(tempValue))
                self.__SetHelper('DigitalAirCommand', DigitalAirCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDigitalAirCommand')
        else:
            self.Discard('Invalid Command for SetDigitalAirCommand')


    def SetDigitalCableCommand1(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 0 <= int(tempValue) <= 9999:
                DigitalCableCommand1CmdString = 'DC10{0:04d}\r'.format(int(tempValue))
                self.__SetHelper('DigitalCableCommand1', DigitalCableCommand1CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDigitalCableCommand1')


    def SetDigitalCableCommand2(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 0 <= int(tempValue) <= 6383:
                DigitalCableCommand2CmdString = 'DC11{0:04d}\r'.format(int(tempValue))
                self.__SetHelper('DigitalCableCommand2', DigitalCableCommand2CmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDigitalCableCommand2')


    def SetDigitalCableMajorCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 1 <= int(tempValue) <= 999:
                DigitalCableMajorCommandCmdString = 'DC2U{0:03d} \r'.format(int(tempValue))
                self.__SetHelper('DigitalCableMajorCommand', DigitalCableMajorCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDigitalCableMajorCommand')


    def SetDigitalCableMinorCommand(self, value, qualifier):

        tempValue = value
        if tempValue:
            if 0 <= int(tempValue) <= 999:
                DigitalCableMinorCommandCmdString = 'DC2L{0:03d} \r'.format(int(tempValue))
                self.__SetHelper('DigitalCableMinorCommand', DigitalCableMinorCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDigitalCableMinorCommand')


    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1' : 'IAVD1   \r', 
            'HDMI 2' : 'IAVD2   \r', 
            'HDMI 3' : 'IAVD3   \r', 
            'HDMI 4' : 'IAVD4   \r', 
            'AV'     : 'IAVD5   \r', 
            'PC'     : 'IAVD6   \r', 
            'USB'    : 'IAVD7   \r',
            'TV'     : 'ITVD0   \r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1' : 'HDMI 1', 
            '2' : 'HDMI 2', 
            '3' : 'HDMI 3', 
            '4' : 'HDMI 4', 
            '5' : 'AV', 
            '6' : 'PC', 
            '7' : 'USB'
        }

        InputCmdString = 'IAVD????\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'MUTE1   \r', 
            'Off' : 'MUTE2   \r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '2' : 'Off'
        }

        MuteCmdString = 'MUTE????\r'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'POWR1   \r', 
            'Off' : 'POWR0   \r'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        PowerCmdString = 'POWR????\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0:03d} \r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOLM????\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                self.Error(['{0} Communication error or incorrect command'.format(sourceCmdName)])
                response = ''
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                self.Error(['Invalid/Unexpected Response'])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
               
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

