from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
import re


class DeviceClass:

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AntennaInput': {'Status': {}},
            'Input': {'Status': {}},
            'IRCodeToTV': {'Status': {}},
            'OSD': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PictureSize': {'Status': {}},
            'Power': {'Status': {}},
            'TeletextMode': {'Status': {}},
            'USBDevice': {'Status': {}},
            'Volume': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x58\x00\x01\x04([\x00-\xFF])[\x00-\xFF]{4}'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x58\x00\x00\x01([\x02|\x03])[\x00-\xFF]'), self.__MatchError, None)

    def InitilizeControl(self, value, qualifier):

        self.Send(b'\x58\x80\x00\x00\xD8')
        self.Send(b'\x58\x80\x15\x02\x00\x00\xEF')

    def SetAntennaInput(self, value, qualifier):

        States = {
            'Air': b'\x58\x80\x32\x01\x00\x0B',
            'Cable': b'\x58\x80\x32\x01\x80\x8B',
            }
        CmdString = States[value]
        self.__SetHelper('AntennaInput', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        States = {
            'RF': b'\x58\x80\x06\x01\x00\xDF',
            'AV': b'\x58\x80\x06\x01\x03\xE2',
            'Component': b'\x58\x80\x06\x01\x07\xE6',
            'PC': b'\x58\x80\x06\x01\x09\xE8',
            'HDMI 1': b'\x58\x80\x06\x01\x0B\xEA',
            'HDMI 2': b'\x58\x80\x06\x01\x0C\xEB',
            'HDMI 3': b'\x58\x80\x06\x01\x0D\xEC',
            'SCART': b'\x58\x80\x06\x01\x01\xE0',
            }
        CmdString = States[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def SetIRCodeToTV(self, value, qualifier):

        States = {
            'Power': b'\x58\x80\x05\x02\x07\x02\xE8',
            '1': b'\x58\x80\x05\x02\x07\x04\xEA',
            '2': b'\x58\x80\x05\x02\x07\x05\xEB',
            '3': b'\x58\x80\x05\x02\x07\x06\xEC',
            '4': b'\x58\x80\x05\x02\x07\x08\xEE',
            '5': b'\x58\x80\x05\x02\x07\x09\xEF',
            '6': b'\x58\x80\x05\x02\x07\x0A\xF0',
            '7': b'\x58\x80\x05\x02\x07\x0C\xF2',
            '8': b'\x58\x80\x05\x02\x07\x0d\xF3',
            '9': b'\x58\x80\x05\x02\x07\x0E\xF4',
            '0': b'\x58\x80\x05\x02\x07\x11\xF7',
            'Date': b'\x58\x80\x05\x02\x07\x23\x09',
            'Mute': b'\x58\x80\x05\x02\x07\x0F\xF5',
            'Vol Up': b'\x58\x80\x05\x02\x07\x07\xED',
            'Vol Down': b'\x58\x80\x05\x02\x07\x0B\xF1',
            'Ch Up': b'\x58\x80\x05\x02\x07\x12\xF8',
            'Ch Down': b'\x58\x80\x05\x02\x07\x10\xF6',
            'Source': b'\x58\x80\x05\x02\x07\x01\xE7',
            'P. Size': b'\x58\x80\x05\x02\x07\x3E\x24',
            'Sleep': b'\x58\x80\x05\x02\x07\x03\xE9',
            'Key Teletext': b'\x58\x80\x05\x02\x07\x2C\x12',
            'Teletext Red': b'\x58\x80\x05\x02\x07\x6C\x52',
            'Teletext Green': b'\x58\x80\x05\x02\x07\x14\xFA',
            'Teletext Yellow': b'\x58\x80\x05\x02\x07\x15\xFB',
            'Teletext Cyan': b'\x58\x80\x05\x02\x07\x16\xFC',
            'Up': b'\x58\x80\x05\x02\x07\x60\x46',
            'Down': b'\x58\x80\x05\x02\x07\x61\x47',
            'Right': b'\x58\x80\x05\x02\x07\x62\x48',
            'Left': b'\x58\x80\x05\x02\x07\x65\x4B',
            'Enter': b'\x58\x80\x05\x02\x07\x68\x4E',
            'TV': b'\x58\x80\x05\x02\x07\x1B\x01',
            'Exit': b'\x58\x80\x05\x02\x07\x2D\x13',
            'Guide': b'\x58\x80\x05\x02\x07\x4F\x35',
            'WiseLink': b'\x58\x80\x05\x02\x07\x8C\x72',
            'Return': b'\x58\x80\x05\x02\x07\x58\x3E',
            '3D': b'\x58\x80\x05\x02\x07\x9F\x85',
            'Info': b'\x58\x80\x05\x02\x07\x1F\x05',
            'Skip Forward': b'\x58\x80\x05\x02\x07\x4E\x34',
            'Skip Backward': b'\x58\x80\x05\x02\x07\x50\x36',
            'Play': b'\x58\x80\x05\x02\x07\x47\x2D',
            'Stop': b'\x58\x80\x05\x02\x07\x46\x2C',
            'Pause': b'\x58\x80\x05\x02\x07\x4A\x30',
            'Rewind': b'\x58\x80\x05\x02\x07\x45\x2B',
            'Forward': b'\x58\x80\x05\x02\x07\x48\x2E',
            }
        CmdString = States[value]
        self.__SetHelper('IRCodeToTV', CmdString, value, qualifier)

    def SetOSD(self, value, qualifier):

        States = {
            'Enable': b'\x58\x80\x16\x01\x00\xEF',
            'Disable': b'\x58\x80\x16\x01\x80\x6F',
            }
        CmdString = States[value]
        self.__SetHelper('OSD', CmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        States = {
            'Dynamic': b'\x58\x80\x1D\x01\x00\xF6',
            'Standard': b'\x58\x80\x1D\x01\x01\xF7',
            'Movie': b'\x58\x80\x1D\x01\x02\xF8',
            }
        CmdString = States[value]
        self.__SetHelper('PictureMode', CmdString, value, qualifier)

    def SetPictureSize(self, value, qualifier):

        States = {
            'Auto Wide': b'\x58\x80\x08\x01\x00\xE1',
            '16:9': b'\x58\x80\x08\x01\x01\xE2',
            'Just Scan': b'\x58\x80\x08\x01\x02\xE3',
            '4:3': b'\x58\x80\x08\x01\x03\xE4',
            }
        CmdString = States[value]
        self.__SetHelper('PictureSize', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\x58\x80\x01\x01\x80\x5A',
            'Off': b'\x58\x80\x01\x01\x00\xDA',
            }
        CmdString = States[value]
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x58\x80\x00\x00\xD8'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        TeleTextModeStates = {
            '1': 'On',
            '0': 'Off'
        }

        OSDStates = {
            '1': 'Enable',
            '0': 'Disable'
        }

        value = '{0:08b}'.format(ord(match.group(1)))
        self.WriteStatus('Power', ValueStateValues[value[3]], None)
        self.WriteStatus('TeletextMode', TeleTextModeStates[value[4]], None)
        self.WriteStatus('OSD', OSDStates[value[6]], None)

    def SetTeletextMode(self, value, qualifier):

        States = {
            'On': b'\x58\x80\x07\x01\x80\x60',
            'Off': b'\x58\x80\x07\x01\x00\xE0',
            }
        CmdString = States[value]
        self.__SetHelper('TeletextMode', CmdString, value, qualifier)

    def SetUSBDevice(self, value, qualifier):

        States = {
            'Enable': b'\x58\x80\x33\x01\x01\x0D',
            'Disable': b'\x58\x80\x33\x01\x00\x0C',
            }
        CmdString = States[value]
        self.__SetHelper('USBDevice', CmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }
        cks = 0xE6 + value & 0xFF
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            CmdString = pack('>BBBBBB', 0x58, 0x80, 0x0D, 0x01, value, cks)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorCodes = {
            '\x02' : 'Command not Acknowledged.',
            '\x03' : 'Command Unsupported.'
            }
        self.Error([ErrorCodes[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.InitilizeControl( None, None)

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