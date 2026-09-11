from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack


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
        self.__DisplayID = b'01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Type'], 'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PAPEnable': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x77\x30\x30(0|1|2|3)\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x67\x30\x30(0|1)\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72(\x73|\x68|\x69)\x30\x30(0|1)\x0D'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x6A\x30(00|01|03|04|05|06|07|09|10|11)\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x5D\x30\x30(0|1)\x0D'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\xBA\x30\x30(0|1|2)\x0D'), self.__MatchPAPEnable, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\xB1\x30\x30(0|1|2|3)\x0D'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\xBF\x30\x30(0|1|2|3)\x0D'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x6C\x30\x30(0|1)\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x38[\x30-\x39]{2}\x72\x66([0-9]{3})\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\x34[\x30-\x39]{2}\x2D\x0D'), self.__MatchError, None)

    @property
    def DisplayID(self):
        return self.__DisplayID

    @DisplayID.setter
    def DisplayID(self, value):
        if value == 'Broadcast':
            self.__DisplayID = b'\x39\x39'
        elif 1 <= int(value) <= 98:
            self.__DisplayID = bytes('{0:02d}'.format(int(value)), 'utf-8')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x30',
            '4:3': b'\x31',
            'Wide Zoom': b'\x32',
            'Zoom': b'\x33'
        }

        AspectRatioCmdString = b'\x38' + self.__DisplayID + b'\x73\x31\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x38' + self.__DisplayID + b'\x67\x77\x30\x30\x30\x0D'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': 'Full',
            '1': '4:3',
            '2': 'Wide Zoom',
            '3': 'Zoom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30'
        }

        AudioMuteCmdString = b'\x38' + self.__DisplayID + b'\x73\x36\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x38' + self.__DisplayID + b'\x67\x67\x30\x30\x30\x0D'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
         }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x38' + self.__DisplayID + b'\x73\x8F\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Button': b'\x45',
            'IR': b'\x42',
            'Button and IR': b'\x43'
        }

        ValueStateValues = {
            'On': b'\x30',
            'Off': b'\x31'
        }

        Type = qualifier['Type']
        if Type == 'Button' or Type == 'IR' or Type == 'Button and IR':
            ExecutiveModeCmdString = b'\x38' + self.__DisplayID + b'\x73' + TypeStates[Type] + b'\x30\x30' + ValueStateValues[value] + b'\x0D'
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Button': b'\x73',
            'IR': b'\x68',
            'Button and IR': b'\x69'
        }
        Type = qualifier['Type']
        if Type == 'Button' or Type == 'IR' or Type == 'Button and IR':
            ExecutiveModeCmdString = b'\x38' + self.__DisplayID + b'\x67' + TypeStates[Type] + b'\x30\x30\x30\x0D'
            self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateExecutiveMode')

    def __MatchExecutiveMode(self, match, tag):

        TypeStates = {
            b'\x73': 'Button',
            b'\x68': 'IR',
            b'\x69': 'Button and IR'
        }

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        Type = match.group(1)
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, {'Type': TypeStates[Type]})

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x30\x30',
            'HDMI': b'\x30\x31',
            'AV': b'\x30\x33',
            'YPbPr': b'\x30\x34',
            'S-Video': b'\x30\x35',
            'DVI': b'\x30\x36',
            'DisplayPort': b'\x30\x37',
            'Multi-Media': b'\x30\x39',
            'Network': b'\x31\x30',
            'USB Display': b'\x31\x31'
        }

        InputCmdString = b'\x38' + self.__DisplayID + b'\x73\x22\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x38' + self.__DisplayID + b'\x67\x6A\x30\x30\x30\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '00': 'VGA',
            '01': 'HDMI',
            '03': 'AV',
            '04': 'YPbPr',
            '05': 'S-Video',
            '06': 'DVI',
            '07': 'DisplayPort',
            '09': 'Multi-Media',
            '10': 'Network',
            '11': 'USB Display'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30'
        }

        OnScreenDisplayCmdString = b'\x38' + self.__DisplayID + b'\x73\x5B\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = b'\x38' + self.__DisplayID + b'\x67\x5D\x30\x30\x30\x0D'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPAPEnable(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x30',
            'PIP': b'\x31',
            'PBP': b'\x32'
        }

        PAPEnableCmdString = b'\x38' + self.__DisplayID + b'\x73\x8A\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('PAPEnable', PAPEnableCmdString, value, qualifier)

    def UpdatePAPEnable(self, value, qualifier):

        PAPEnableCmdString = b'\x38' + self.__DisplayID + b'\x67\xBA\x30\x30\x30\x0D'
        self.__UpdateHelper('PAPEnable', PAPEnableCmdString, value, qualifier)

    def __MatchPAPEnable(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PBP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PAPEnable', value, None)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x30',
            'Vivid': b'\x31',
            'Cinema': b'\x32',
            'Custom': b'\x33'
        }

        PictureModeCmdString = b'\x38' + self.__DisplayID + b'\x73\x81\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x38' + self.__DisplayID + b'\x67\xB1\x30\x30\x30\x0D'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'Vivid',
            '2': 'Cinema',
            '3': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Left': b'\x30',
            'Upper Right': b'\x31',
            'Lower Left': b'\x32',
            'Lower Right': b'\x33'
        }

        PIPPositionCmdString = b'\x38' + self.__DisplayID + b'\x73\x8E\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = b'\x38' + self.__DisplayID + b'\x67\xBF\x30\x30\x30\x0D'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            '0': 'Upper Left',
            '1': 'Upper Right',
            '2': 'Lower Left',
            '3': 'Lower Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30'
        }

        PowerCmdString = b'\x38' + self.__DisplayID + b'\x73\x21\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x38' + self.__DisplayID + b'\x67\x6C\x30\x30\x30\x0D'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Value = bytes('{0:03d}'.format(value), 'utf-8')
            VolumeCmdString = b'\x38' + self.__DisplayID + b'\x73\x35' + Value + b'\x0D'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x38' + self.__DisplayID + b'\x67\x66\x30\x30\x30\x0D'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.__DisplayID == b'\x39\x39':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        value = 'Invalid Command'
        print(value)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
