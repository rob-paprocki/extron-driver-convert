from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


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
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'IREmulation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*SAAMUT0{15}(0|1)\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\*SAINPT0{7}(0|1|3)0{7}([0-4])\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*SAPOWR0{15}(0|1)\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*SAPMUT0{15}(0|1)\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'\*SAVOLU0{13}([0-1][0-9]{2})\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\*SA(AMUT|INPT|PMUT|POWR|VOLU)(F|N){16}\n'), self.__MatchError, None)

        self.deliTagValues = {
            'AudioMute': '*SNAMUT',
            'Input': '*SNINPT',
            'Power': '*SNPOWR',
            'VideoMute': '*SNPMUT',
            'Volume': '*SAVOLU'
        }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'AMUT0000000000000001',
            'Off': b'AMUT0000000000000000'
        }

        AudioMuteCmdString = b''.join([b'*SC', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'*SEAMUT################\x0A'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'IRCC0000000000000033',
            'Down': b'IRCC0000000000000034'
        }

        ChannelCmdString = b''.join([b'*SC', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': b'INPT0000000000000000',
            'Video': b'INPT0000000300000001',
            'HDMI 1': b'INPT0000000100000001',
            'HDMI 2': b'INPT0000000100000002',
            'HDMI 3': b'INPT0000000100000003',
            'HDMI 4': b'INPT0000000100000004'
        }

        InputCmdString = b''.join([b'*SC', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'*SEINPT################\x0A'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'TV',
            '3': 'Video'
        }

        inputMatch = match.group(1).decode()

        if inputMatch == '1':
            value = 'HDMI {0}'.format(match.group(2).decode())
        else:
            value = ValueStateValues[inputMatch]
        self.WriteStatus('Input', value, None)

    def SetIREmulation(self, value, qualifier):

        ValueStateValues = {
            'Power Off': b'IRCC0000000000000000',
            'Input': b'IRCC0000000000000001',
            'GGuide': b'IRCC0000000000000002',
            'EPG': b'IRCC0000000000000003',
            'Favorites': b'IRCC0000000000000004',
            'Display': b'IRCC0000000000000005',
            'Home': b'IRCC0000000000000006',
            'Options': b'IRCC0000000000000007',
            'Return': b'IRCC0000000000000008',
            'Up': b'IRCC0000000000000009',
            'Down': b'IRCC0000000000000010',
            'Right': b'IRCC0000000000000011',
            'Left': b'IRCC0000000000000012',
            'Confirm': b'IRCC0000000000000013',
            'Red': b'IRCC0000000000000014',
            'Green': b'IRCC0000000000000015',
            'Yellow': b'IRCC0000000000000016',
            'Blue': b'IRCC0000000000000017',
            '1': b'IRCC0000000000000018',
            '2': b'IRCC0000000000000019',
            '3': b'IRCC0000000000000020',
            '4': b'IRCC0000000000000021',
            '5': b'IRCC0000000000000022',
            '6': b'IRCC0000000000000023',
            '7': b'IRCC0000000000000024',
            '8': b'IRCC0000000000000025',
            '9': b'IRCC0000000000000026',
            '0': b'IRCC0000000000000027',
            '11': b'IRCC0000000000000028',
            '12': b'IRCC0000000000000029',
            'Volume Up': b'IRCC0000000000000030',
            'Volume Down': b'IRCC0000000000000031',
            'Mute': b'IRCC0000000000000032',
            'Channel Up': b'IRCC0000000000000033',
            'Channel Down': b'IRCC0000000000000034',
            'Subtitle': b'IRCC0000000000000035',
            'Closed Caption': b'IRCC0000000000000036',
            'Enter': b'IRCC0000000000000037',
            'DOT': b'IRCC0000000000000038',
            'Analog': b'IRCC0000000000000039',
            'Teletext': b'IRCC0000000000000040',
            'Exit': b'IRCC0000000000000041',
            'Analog 2': b'IRCC0000000000000042',
            'AD': b'IRCC0000000000000043',
            'Digital': b'IRCC0000000000000044',
            'Analog?': b'IRCC0000000000000045',
            'BS': b'IRCC0000000000000046',
            'CS': b'IRCC0000000000000047',
            'BS/CS': b'IRCC0000000000000048',
            'Ddata': b'IRCC0000000000000049',
            'Picture Off': b'IRCC0000000000000050',
            'TV Radio': b'IRCC0000000000000051',
            'Theater': b'IRCC0000000000000052',
            'SEN': b'IRCC0000000000000053',
            'Internet Widgets': b'IRCC0000000000000054',
            'Internet Video': b'IRCC0000000000000055',
            'Netflix': b'IRCC0000000000000056',
            'Scene Select': b'IRCC0000000000000057',
            'Mode3D': b'IRCC0000000000000058',
            'iManual': b'IRCC0000000000000059',
            'Audio': b'IRCC0000000000000060',
            'Wide': b'IRCC0000000000000061',
            'Jump': b'IRCC0000000000000062',
            'PAP': b'IRCC0000000000000063',
            'MyEPG': b'IRCC0000000000000064',
            'Program Description': b'IRCC0000000000000065',
            'Write Chapter': b'IRCC0000000000000066',
            'TrackID': b'IRCC0000000000000067',
            'Ten Key': b'IRCC0000000000000068',
            'AppliCast': b'IRCC0000000000000069',
            'acTVila': b'IRCC0000000000000070',
            'Delete Video': b'IRCC0000000000000071',
            'Photo Frame': b'IRCC0000000000000072',
            'TV Pause': b'IRCC0000000000000073',
            'Keypad': b'IRCC0000000000000074',
            'Media': b'IRCC0000000000000075',
            'Sync Menu': b'IRCC0000000000000076',
            'Forward': b'IRCC0000000000000077',
            'Play': b'IRCC0000000000000078',
            'Rewind': b'IRCC0000000000000079',
            'Previous': b'IRCC0000000000000080',
            'Stop': b'IRCC0000000000000081',
            'Next': b'IRCC0000000000000082',
            'Record': b'IRCC0000000000000083',
            'Pause': b'IRCC0000000000000084',
            'Eject': b'IRCC0000000000000085',
            'Flash Plus': b'IRCC0000000000000086',
            'Flash Minus': b'IRCC0000000000000087',
            'Top Menu': b'IRCC0000000000000088',
            'Popup Menu': b'IRCC0000000000000089',
            'Rakuraku Start': b'IRCC0000000000000090',
            'One Touch Time Record': b'IRCC0000000000000091',
            'One Touch View': b'IRCC0000000000000092',
            'One Touch Record': b'IRCC0000000000000093',
            'One Touch Stop': b'IRCC0000000000000094',
            'DUX': b'IRCC0000000000000095',
            'Football Mode': b'IRCC0000000000000096',
            'Social': b'IRCC0000000000000097'
        }

        IREmulationCmdString = b''.join([b'*SC', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'POWR0000000000000001',
            'Off': b'POWR0000000000000000'
        }

        PowerCmdString = b''.join([b'*SC', ValueStateValues[value], b'\x0A'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'*SEPOWR################\x0A'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = b''.join([b'*SCPMUT0000000000000001\x0A'])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'*SEPMUT################\x0A'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b''.join([b'*SCVOLU0000000000000', '{0:03d}'.format(value).encode(), b'\x0A'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'*SEVOLU################\x0A'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command not in self.deliTagValues:
            self.Send(commandstring)
        else:

            res = self.SendAndWait(commandstring, 3.2, deliTag=self.deliTagValues[command])
            if not res:
                self.Error(['Invalid/unexpected response'])

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

        CommandValues = {
            'AMUT': 'Audio Mute',
            'INPT': 'Input',
            'POWR': 'Power',
            'PMUT': 'Video Mute',
            'VOLU': 'Volume'
        }
        value = match.group(1).decode()
        errorValue = match.group(2).decode()

        if errorValue[0] == 'F':
            errorString = 'Error: {0}'.format(CommandValues[value])
        elif errorValue[0] == 'N':
            errorString = 'Not Found: {0}'.format(CommandValues[value])
        else:
            errorString = 'Unknown Error.'

        self.Error([errorString])

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