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
            'ClearErrorStatus': {'Status': {}},
            'Deck': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'RecordMode': {'Status': {}},
            'Transport': {'Status': {}},
            }

        self.UpdateInputRegex = re.compile(b'[\x31-\x39]\x30[\x30-\x43][\x11-\x98][\x10-\x98](?:\x30|\x31)')
        self.UpdatePowerRegex = re.compile(b'[\x80-\xFF][\x00-\x80]{2}[\x00-\xFE][\x00-\xFF]')

    def SetClearErrorStatus(self, value, qualifier):

        ClearErrorStatusCmdString = b'\x56'
        self.__SetHelper('ClearErrorStatus', ClearErrorStatusCmdString, value, qualifier)

    def SetDeck(self, value, qualifier):

        ValueStateValues = {
            'HDD': b'\xF0\x34',
            'BD': b'\xF0\x38',
            'SD': b'\xF0\x3C'
        }

        DeckCmdString = ValueStateValues[value]
        self.__SetHelper('Deck', DeckCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': b'\xB8\x30\x31',
            'S-Video': b'\xB8\x30\x39',
            'DV': b'\xB8\x30\x34',
            'SDI': b'\xB8\x30\x36',
            'HDMI': b'\xB8\x30\x38'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            b'\x31': 'Video',
            b'\x39': 'S-Video',
            b'\x34': 'DV',
            b'\x36': 'SDI',
            b'\x38': 'HDMI'
            }
        RecordState = {
            b'\x30': 'XP',
            b'\x31': 'SP',
            b'\x32': 'LP',
            b'\x33': 'EP',
            b'\x40': 'DR1',
            b'\x41': 'DR2',
            b'\x42': 'DR3',
            b'\x43': 'DR4',
            b'\x3A': 'DR',
            b'\x3B': 'AF',
            b'\x3C': 'AN',
            b'\x3D': 'AL',
            b'\x3E': 'AE'
            }

        InputCmdString = b'\xB9'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[0:1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

            try:
                value1 = RecordState[res[2:3]]
                self.WriteStatus('RecordMode', value1, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def SetIRRemoteEmulation(self, value, qualifier):

        ValueStateValues = {
            'Input': b'\x01',
            'Stop': b'\x03',
            'FFwd/Speed +': b'\x06',
            'Rew/Speed -': b'\x07',
            'Power On/Off': b'\x0B',
            'Play': b'\x0C',
            'Pause/Still': b'\x0D',
            'Fwd Skip': b'\x14',
            'Rev Skip': b'\x15',
            'Audio': b'\x17',
            'Power Off': b'\x1A',
            'Power On': b'\x1D',
            '1': b'\x21',
            '2': b'\x22',
            '3': b'\x23',
            '4': b'\x24',
            '5': b'\x25',
            '6': b'\x26',
            '7': b'\x27',
            '8': b'\x28',
            '9': b'\x29',
            '*': b'\x2A',
            '0': b'\x2B',
            '#': b'\x2C',
            'Record Mode': b'\x31',
            'BD/DVD Deck': b'\x32',
            'Dubbing': b'\x34',
            'Setup': b'\x37',
            'OK/Enter': b'\x3C',
            'On Screen': b'\x3E',
            'HDD Deck': b'\x44',
            'Media Management': b'\x48',
            'Cursor 0 degrees': b'\x80',
            'Menu': b'\x81',
            'Cursor 90 degrees': b'\x82',
            'Cursor 180 degrees': b'\x84',
            'Cursor 270 degrees': b'\x86',
            'Open/Close': b'\x87',
            'Progressive': b'\x8E',
            'Top Menu': b'\x8F',
            'Mark': b'\x90',
            'CM Skip': b'\x96',
            'Rev Frame': b'\xAF',
            '-Slow D': b'\xB0',
            'Shuttle-C': b'\xB1',
            'Shuttle-B': b'\xB2',
            'Shuttle-A': b'\xB3',
            'Shuttle-2': b'\xB4',
            'Shuttle-1': b'\xB5',
            '-Slow B': b'\xB6',
            '-Slow C': b'\xB7',
            '+Slow C': b'\xB8',
            '+Slow B': b'\xB9',
            'Shuttle+1': b'\xBA',
            'Shuttle+2': b'\xBB',
            'Shuttle+A': b'\xBC',
            'Shuttle+B': b'\xBD',
            'Shuttle+C': b'\xBE',
            '+Slow D': b'\xBF',
            'Angle/Live Check': b'\xC0',
            'Subtitle': b'\xC4',
            'Record': b'\xCC',
            'Option': b'\xD3',
            'Return': b'\xD4',
            'Color Key Blue': b'\xD5',
            'Color Key Red': b'\xD7',
            'Jog -1/6': b'\xD9',
            'Jog +1/6': b'\xDA',
            'Jog +1': b'\xDB',
            'Instant Replay': b'\xDC',
            'Edit': b'\xDD',
            'Color Key Green': b'\xDE',
            'Color Key Yellow': b'\xDF',
            'Navigation': b'\xE0',
            'L-1 Y/C Input': b'\xE1',
            'L-1 Composite Input': b'\xE2',
            'Playback Setting': b'\xE3',
            'Delete': b'\xE4',
            'Information Correct': b'\xE5',
            'Fwd Frame': b'\xED',
            'Mode Lock': b'\xF2',
            'HDCP Auto': b'\xF3'
        }

        IRRemoteEmulationCmdString = b'\x9F' + ValueStateValues[value]
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x9F\x21',
            '2': b'\x9F\x22',
            '3': b'\x9F\x23',
            '4': b'\x9F\x24',
            '5': b'\x9F\x25',
            '6': b'\x9F\x26',
            '7': b'\x9F\x27',
            '8': b'\x9F\x28',
            '9': b'\x9F\x29',
            '0': b'\x9F\x2B',
            '*': b'\x9F\x2A',
            '#': b'\x9F\x2C'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x99',
            'Down': b'\x9A',
            'Left': b'\x9C',
            'Right': b'\x9B',
            'Display/Close Media Manage Menu': b'\x94',
            'Display/Close Top Menu': b'\x93',
            'Display Main Menu screen': b'\x97\x31',
            'Display Library Database Navigation screen': b'\x97\x32',
            'Display Editing screen': b'\x97\x35',
            'Display Dubbing screen': b'\x97\x37',
            'Close screen': b'\x97\x30',
            'Set': b'\x98',
            'Finalize': b'\x90',
            'Cancel Disc Finalization': b'\x91'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xA0',
            'Off': b'\xA1'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            0x00: 'On',
            0x08: 'Off'
            }
        DeviceStatusState = {
           0x10: 'Record Forbidden',
           0x08: 'Disc Not Inserted',
           0x00: 'Normal',
           0x04: 'Tray Open'
           }

        TransportByte4State = {
            0x10: 'Stop',
            0x02: 'Record',
            0x80: 'Play'
            }
        TransportByte5State = {
            0x80: 'Pause',
            0x10: 'Fast Forward',
            0x20: 'Rewind'
            }
        DeckState = {
            0x80: 'HDD',
            0xC0: 'BD',
            0xE0: 'SD'
            }

        PowerCmdString = b'\xD7'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value1 = PowerState[ord(res[3:4]) & 0x08]
                self.WriteStatus('Power', value1, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

            try:
                value2 = DeviceStatusState[ord(res[0:1]) & 0x1C]
                self.WriteStatus('DeviceStatus', value2, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

            try:
                transportByte4 = ord(res[3:4]) & 0x92
                transportByte5 = ord(res[4:5]) & 0xB0
                if transportByte5:
                    value3 = TransportByte5State[transportByte5]
                else:
                    value3 = TransportByte4State[transportByte4]
                self.WriteStatus('Transport', value3, None)
            except (KeyError, IndexError):
                print('Multiple transport states encountered')

            try:
                value4 = DeckState[ord(res[0:1]) & 0xE0]
                self.WriteStatus('Deck', value4, None)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetRecordMode(self, value, qualifier):

        ValueStateValues = {
            'XP': b'\xB8\x34\x30',
            'SP': b'\xB8\x34\x31',
            'LP': b'\xB8\x34\x32',
            'EP': b'\xB8\x34\x33',
            'DR': b'\xB8\x34\x3A',
            'AF': b'\xB8\x34\x3B',
            'AN': b'\xB8\x34\x3C',
            'AL': b'\xB8\x34\x3D',
            'AE': b'\xB8\x34\x3E',
            'DR1': b'\xB8\x34\x40',
            'DR2': b'\xB8\x34\x41',
            'DR3': b'\xB8\x34\x42',
            'DR4': b'\xB8\x34\x43'
        }

        RecordModeCmdString = ValueStateValues[value]
        self.__SetHelper('RecordMode', RecordModeCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop': b'\x3F',
            'Pause': b'\x4F',
            'Play': b'\x3A',
            'Fast Forward': b'\xAB',
            'Rewind': b'\xAC',
            'FF-Field Step': b'\xAD',
            'Rew-Field Step': b'\xAE',
            'Next Chapter': b'\x95',
            'Previous Chapter': b'\x96',
            'Record': b'\xCA',
            'Record Pause': b'\xCB',
            'Rec/Dub Request': b'\xFA',
            'Eject': b'\xA3',
            'Next Title': b'\x9D',
            'Previous Title': b'\x9E'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and sourceCmdName == 'Power':
            if ord(response[0:1]) & 0x01:
                print('{0}: RS-232C command error status. Clears using Clear Error Status command'.format(sourceCmdName))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=1)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        commandUpdate = {
            'Input': self.UpdateInputRegex,
            'Power': self.UpdatePowerRegex,
        }
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=commandUpdate[command])
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
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
