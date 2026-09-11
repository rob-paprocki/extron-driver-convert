from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'Focus': {'Parameters':['Focus Speed'], 'Status': {}},
            'FocusStandardMode': { 'Status': {}},
            'PanTilt': {'Parameters':['PanTilt Speed'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Zoom': {'Parameters':['Zoom Speed'], 'Status': {}},
            'ZoomStandardMode': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == '0':
            self._DeviceID = 0x80
        elif value == '1':
            self._DeviceID = 0x81
        else:
            self.Error(['Device ID Out of Range'])

    def SetFocus(self, value, qualifier):


        FocusSpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'Far'  : 0x20, 
            'Near' : 0x30
        }

        if (FocusSpeedConstraints['Min'] <= int(qualifier['Focus Speed']) <= FocusSpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Focus Speed']) + ValueStateValues[value]
            FocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')
    def SetFocusStandardMode(self, value, qualifier):

        
        ValueStateValues = {
            'Far'  : 0x02, 
            'Near' : 0x03
        }

        FocusStandardModeCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x08, ValueStateValues[value], 0xFF)
        self.__SetHelper('FocusStandardMode', FocusStandardModeCmdString, value, qualifier)
    def SetPanTilt(self, value, qualifier):

        
        PanTiltSpeedConstraints = {
            'Min' : 1,
            'Max' : 24
        }

        ValueStateValues = {
            'Up'         : [0x03, 0x01], 
            'Down'       : [0x03, 0x02], 
            'Left'       : [0x01, 0x03],  
            'Right'      : [0x02, 0x03],   
            'Stop'       : [0x03, 0x03]
        }

        Speed  = int(qualifier['PanTilt Speed'])

        if PanTiltSpeedConstraints['Min'] <= Speed <= PanTiltSpeedConstraints['Max']: 
            PanTiltCmdString = pack('>9B', self.DeviceID, 0x01, 0x06, 0x01, Speed, Speed, ValueStateValues[value][0], ValueStateValues[value][1], 0xFF)
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self. Discard('Invalid Command')
    def SetPresetRecall(self, value, qualifier):


        PresetStateValues = {
            'Min' : 1, 
            'Max' : 25
        }

        if PresetStateValues['Min'] <= int(value) <= PresetStateValues['Max']:
            PresetRecallCmdString =  pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x02, int(value), 0xFF)
            self.__SetHelper('PresetRecall',  PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):


        PresetStateValues = {
            'Min' : 1, 
            'Max' : 25
        }

        if PresetStateValues['Min'] <= int(value) <= PresetStateValues['Max']:
            PresetSaveCmdString =  pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x01, int(value), 0xFF)
            self.__SetHelper('PresetSave',  PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')
    def SetZoom(self, value, qualifier):

        
        ZoomSpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'In'  : 0x20, 
            'Out' : 0x30 
        }

        if (ZoomSpeedConstraints['Min'] <= int(qualifier['Zoom Speed']) <= ZoomSpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Zoom Speed']) + ValueStateValues[value]
            ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')
    def SetZoomStandardMode(self, value, qualifier):

        
        ValueStateValues = {
            'In'  : 0x02, 
            'Out' : 0x03
        }

        ZoomStandardModeCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, ValueStateValues[value], 0xFF)
        self.__SetHelper('ZoomStandardMode', ZoomStandardModeCmdString, value, qualifier)
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

