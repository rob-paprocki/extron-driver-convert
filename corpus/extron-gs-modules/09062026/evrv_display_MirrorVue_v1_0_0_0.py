from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = b'\xFF'
        self.Models = {}

        self.Commands = {
            'Cancel': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Color': { 'Status': {}},
            'ECO': { 'Status': {}},
            'EPG': { 'Status': {}},
            'Favorite': { 'Status': {}},
            'Index': { 'Status': {}},
            'Info': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'List': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mix': { 'Status': {}},
            'MTS': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Page': { 'Status': {}},
            'PMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'Return': { 'Status': {}},
            'Reveal': { 'Status': {}},
            'Size': { 'Status': {}},
            'Sleep': { 'Status': {}},
            'SMode': { 'Status': {}},
            'SubP': { 'Status': {}},
            'TimeShift': { 'Status': {}},
            'Transport': { 'Status': {}},
            'Volume': { 'Status': {}},
            'Zoom': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Off':
            self._DeviceID = b'\xFF'
        elif 1 <= int(value) <= 254:
            self._DeviceID = bytes([int(value)])
        else:
            print('Invalid Device ID Parameter.')

    def SetCancel(self, value, qualifier):

        CancelCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x07\xF8'
        self.__SetHelper('Cancel', CancelCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x55\xAA',
            'Down'  : b'\x5A\xA5'
        }

        if value in ValueStateValues:
            ChannelCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetColor(self, value, qualifier):

        ValueStateValues = {
            'Red'       : b'\x46\xB9',
            'Green'     : b'\x4A\xB5',
            'Yellow'    : b'\x52\xAD',
            'Blue'      : b'\x5E\xA1'
        }

        if value in ValueStateValues:
            ColorCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Color', ColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColor')

    def SetECO(self, value, qualifier):

        ECOCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x00\xFF'
        self.__SetHelper('ECO', ECOCmdString, value, qualifier)

    def SetEPG(self, value, qualifier):

        EPGCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x15\xEA'
        self.__SetHelper('EPG', EPGCmdString, value, qualifier)

    def SetFavorite(self, value, qualifier):

        FavoriteCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x10\xEF'
        self.__SetHelper('Favorite', FavoriteCmdString, value, qualifier)

    def SetIndex(self, value, qualifier):

        IndexCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x08\xF7'
        self.__SetHelper('Index', IndexCmdString, value, qualifier)


    def SetInfo(self, value, qualifier):

        InfoCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x50\xAF'
        self.__SetHelper('Info', InfoCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x01\xFE'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0' : b'\x56\xA9',
            '1' : b'\x42\xBD',
            '2' : b'\x43\xBC',
            '3' : b'\x0F\xF0',
            '4' : b'\x1E\xE1',
            '5' : b'\x1D\xE2',
            '6' : b'\x1C\xE3',
            '7' : b'\x18\xE7',
            '8' : b'\x45\xBA',
            '9' : b'\x4C\xB3'
        }

        if value in ValueStateValues:
            KeypadCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetList(self, value, qualifier):

        ListCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x04\xFB'
        self.__SetHelper('List', ListCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu'  : b'\x4E\xB1',
            'Up'    : b'\x17\xE8',
            'Down'  : b'\x0D\xF2',
            'Right' : b'\x05\xFA',
            'Left'  : b'\x0C\xF3',
            'Ok'    : b'\x02\xFD',
            'Exit'  : b'\x1B\xE4'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMix(self, value, qualifier):

        MixCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x59\xA6'
        self.__SetHelper('Mix', MixCmdString, value, qualifier)

    def SetMTS(self, value, qualifier):

        MTSCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x11\xEE'
        self.__SetHelper('MTS', MTSCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x14\xEB'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPage(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x06\xF9',
            'Down'  : b'\x58\xA7'
        }

        if value in ValueStateValues:
            PageCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Page', PageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPage')

    def SetPMode(self, value, qualifier):

        PModeCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x4B\xB4'
        self.__SetHelper('PMode', PModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x0B\xF4'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetReturn(self, value, qualifier):

        ReturnCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\xFF\xF6'
        self.__SetHelper('Return', ReturnCmdString, value, qualifier)

    def SetReveal(self, value, qualifier):

        RevealCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x49\xB6'
        self.__SetHelper('Reveal', RevealCmdString, value, qualifier)

    def SetSize(self, value, qualifier):

        SizeCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x5F\xA0'
        self.__SetHelper('Size', SizeCmdString, value, qualifier)

    def SetSleep(self, value, qualifier):

        SleepCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x53\xAC'
        self.__SetHelper('Sleep', SleepCmdString, value, qualifier)

    def SetSMode(self, value, qualifier):

        SModeCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x5B\xA4'
        self.__SetHelper('SMode', SModeCmdString, value, qualifier)

    def SetSubP(self, value, qualifier):

        SubPCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x44\xBB'
        self.__SetHelper('SubP', SubPCmdString, value, qualifier)

    def SetTimeShift(self, value, qualifier):

        TimeShiftCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x0E\xF1'
        self.__SetHelper('TimeShift', TimeShiftCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'USB'       : b'\x57\xA8',
            'Previous'  : b'\x47\xB8',
            'Next'      : b'\x13\xEC',
            'Play'      : b'\x16\xE9',
            'Stop'      : b'\x12\xED',
            'Forward'   : b'\x4D\xB2',
            'Backward'  : b'\x4F\xB0',
            'HOME/REC'  : b'\x48\xB7'
        }

        if value in ValueStateValues:
            TransportCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'    : b'\x0A\xF5',
            'Down'  : b'\x40\xBF'
        }

        if value in ValueStateValues:
            VolumeCmdString = b'\xA0\xF0\x55' + self._DeviceID + ValueStateValues[value]
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def SetZoom(self, value, qualifier):

        ZoomCmdString = b'\xA0\xF0\x55' + self._DeviceID + b'\x57\xA8'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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