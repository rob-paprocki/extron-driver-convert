from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:


    
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AbsoluteIntensity': { 'Status': {}},
            'LightsOff': { 'Status': {}},
            'RelativeIntensity': { 'Status': {}},
            'Show': { 'Status': {}},
        }





    def SetAbsoluteIntensity(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AbsoluteIntensityCmdString = 'X02{0:02X}'.format(value)
            self.__SetHelper('AbsoluteIntensity', AbsoluteIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAbsoluteIntensity')
    def SetLightsOff(self, value, qualifier):

        LightsOffCmdString = 'X0100'
        self.__SetHelper('LightsOff', LightsOffCmdString, value, qualifier)


    def SetRelativeIntensity(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            IntensityValue = (value ^ 255) + 1
            if IntensityValue > 255:
                IntensityValue = 255
            RelativeIntensityCmdString = 'X03{0:02X}'.format(IntensityValue)
            self.__SetHelper('RelativeIntensity', RelativeIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelativeIntensity')
    def SetShow(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 225
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ShowCmdString = 'X04{0:02X}'.format(value)
            self.__SetHelper('Show', ShowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShow')
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    
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

