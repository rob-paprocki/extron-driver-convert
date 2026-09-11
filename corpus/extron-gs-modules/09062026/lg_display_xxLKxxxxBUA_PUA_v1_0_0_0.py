from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.DeviceID = 1
        self.Models = {
            '32LK610BPUA': self.lg_10_5006_3,
            '32LK610BBUA': self.lg_10_5006_3,
            '49LK5750PUA': self.lg_10_5006_2,
            '49LK5700BUA': self.lg_10_5006_2,
            '49LK5700PUA': self.lg_10_5006_2,
            '43LK5750PUA': self.lg_10_5006_2,
            '43LK5700BUA': self.lg_10_5006_2,
            '43LK5700PUA': self.lg_10_5006_2,
            }


        self.Commands = {
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'EnergySaving': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Input': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'OnScreenDisplay': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID = '{:02X}'.format(int(value))
        else:
            self.Error(['Device ID Out of Range'])

    def SetAspectRatio(self, value, qualifier):
                
        ValueStateValues = {
            'Normal':           '01',
            'Wide':             '02',
            'Zoom':             '04',
            'Original':         '06',
            'Just Scan':        '09',
            'Cinema Zoom 1':    '10',
            'Cinema Zoom 2':    '11',
            'Cinema Zoom 3':    '12',
            'Cinema Zoom 4':    '13',
            'Cinema Zoom 5':    '14',
            'Cinema Zoom 6':    '15',
            'Cinema Zoom 7':    '16',
            'Cinema Zoom 8':    '17',
            'Cinema Zoom 9':    '18',
            'Cinema Zoom 10':   '19',
            'Cinema Zoom 11':   '1A',
            'Cinema Zoom 12':   '1B',
            'Cinema Zoom 13':   '1C',
            'Cinema Zoom 14':   '1D',
            'Cinema Zoom 15':   '1E',
            'Cinema Zoom 16':   '1F'
        }
        
        if value in ValueStateValues:
            AspectRatioCmdString = 'kc {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):
                
        ValueStateValues = {
            'On':   '00',
            'Off':  '01'
        }
        
        if value in ValueStateValues:
            AudioMuteCmdString = 'ke {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetChannel(self, value, qualifier):
                
        ValueStateValues = {
            'Up':   '00',
            'Down': '01'
        }
        
        if value in ValueStateValues:
            ChannelCmdString = 'mc {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetClosedCaption(self, value, qualifier):
        
        ClosedCaptionCmdString = 'mc {id} 39\r'.format(id=self.DeviceID)
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetEnergySaving(self, value, qualifier):
                
        ValueStateValues = {
            'Off':          '00',
            'Minimum':      '01',
            'Medium':       '02',
            'Maximum':      '03',
            'Auto':         '04',
            'Screen Off':   '05'
        }
        
        if value in ValueStateValues:
            EnergySavingCmdString = 'jq {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('EnergySaving', EnergySavingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEnergySaving')

    def SetExecutiveMode(self, value, qualifier):
                
        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }
        
        if value in ValueStateValues:
            ExecutiveModeCmdString = 'km {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetInput(self, value, qualifier):
        
        if value in self.InputStates:
            InputCmdString = 'xb {id} {data}\r'.format(id=self.DeviceID, data=self.InputStates[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetKeypad(self, value, qualifier):
                
        ValueStateValues = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10',
            '-': '4C'
        }
        
        if value in ValueStateValues:
            KeypadCmdString = 'mc {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):
                
        ValueStateValues = {
            'Up':       '40',
            'Down':     '41',
            'Left':     '07',
            'Right':    '06',
            'Menu':     '43',
            'OK':       '44',
            'Exit':     '5B',
            'Back':     '28'
        }
        
        if value in ValueStateValues:
            MenuNavigationCmdString = 'mc {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On':   '01',
            'Off':  '00'
        }
        
        if value in ValueStateValues:
            OnScreenDisplayCmdString = 'kl {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def SetPowerOff(self, value, qualifier):
                
        PowerOffCmdString = 'ka {id} 00\r'.format(id=self.DeviceID)
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):
                
        ValueStateValues = {
            'On':               '01',
            'Off':              '00',
            'On (With OSD)':    '10'
        }
        
        if value in ValueStateValues:
            VideoMuteCmdString = 'kd {id} {data}\r'.format(id=self.DeviceID, data=ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {id} {data:02X}\r'.format(id=self.DeviceID, data=value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def lg_10_5006_2(self):
    
        self.InputStates = {
            'HDMI 1':       '90',
            'HDMI 2':       '91',
            'Component':    '40',
            'AV':           '20',
            'DTV':          '00',
            'ATV':          '10',
            'CADTV':        '01',
            'CATV':         '11'
        }
        


    def lg_10_5006_3(self):
    
        self.InputStates = {
            'HDMI 1':       '90',
            'HDMI 2':       '91',
            'HDMI 3':       '92',
            'Component':    '40',
            'AV':           '20',
            'DTV':          '00',
            'ATV':          '10',
            'CADTV':        '01',
            'CATV':         '11'
        }
        
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

