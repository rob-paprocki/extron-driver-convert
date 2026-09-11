from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Beam': {'Parameters': ['Beam'], 'Status': {}},
            'BeamActivity': {'Parameters': ['Beam'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'Gain': {'Parameters': ['Channel', 'Group'], 'Status': {}},
            'LEDBlink': {'Parameters': ['State'], 'Status': {}},
            'LEDBrightness': {'Parameters': ['State'], 'Status': {}},
            'LEDColor': {'Parameters': ['State'], 'Status': {}},
            'Mute': {'Parameters': ['Channel', 'Group'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'BFZONE ([1-9]|1[0-2]) ([01])\r'), self.__MatchBeam, None)
            self.AddMatchString(re.compile(b'BEAMREPORT ([01]{12})\r'), self.__MatchBeamActivity, None)
            self.AddMatchString(re.compile(b'VER (.+?)\r'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'GAIN ([1-4]) ([VSR]) (-?\d+(?:\.\d+)?)\r'), self.__MatchGain, None)
            self.AddMatchString(re.compile(b'LEDBLINK ([01]) ([01])\r'), self.__MatchLEDBlink, None)
            self.AddMatchString(re.compile(b'LEDBRIGHT ([01]) ([0-3])\r'), self.__MatchLEDBrightness, None)
            self.AddMatchString(re.compile(b'LEDCOLOR ([01]) ([1-8])\r'), self.__MatchLEDColor, None)
            self.AddMatchString(re.compile(b'MUTE ([1-9]|1[0-2]) ([VSBR]) ([01])\r'), self.__MatchMute, None)

    def SetBeam(self, value, qualifier):

        beam = int(qualifier['Beam'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= beam <= 12 and value in ValueStateValues:
            BeamCmdString = 'BFZONE {} {}\r\n'.format(beam, ValueStateValues[value])
            self.__SetHelper('Beam', BeamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBeam')

    def UpdateBeam(self, value, qualifier):

        beam = int(qualifier['Beam'])

        if 1 <= beam <= 12:
            BeamCmdString = 'BFZONE {}\r\n'.format(beam)
            self.__UpdateHelper('Beam', BeamCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeam')

    def __MatchBeam(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Beam': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Beam', value, qualifier)

    def UpdateBeamActivity(self, value, qualifier):

        beam = int(qualifier['Beam'])
        if 1 <= beam <= 12:

            BeamActivityCmdString = 'BEAMREPORT\r\n'
            self.__UpdateHelper('BeamActivity', BeamActivityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBeamActivity')

    def __MatchBeamActivity(self, match, tag):

        ValueStateValues = {
            '1': 'Active',

            '0': 'Not Active'
        }

        for beam, value in zip(range(12, 0, -1), match.group(1).decode()):
            qualifier = {
                'Beam': str(beam)
            }

            value = ValueStateValues[value]
            self.WriteStatus('BeamActivity', value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'VER\r\n'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        GroupStates = {
            'SmartMix':         'V',
            'Speaker':          'S',
            'AEC Reference':    'R'
        }
        group = qualifier['Group']

        if 1 <= channel <= 4 and group in GroupStates and -65 <= value <= 20:
            GainCmdString = 'GAIN {} {} {}\r\n'.format(channel, GroupStates[group], value)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def UpdateGain(self, value, qualifier):

        channel = int(qualifier['Channel'])

        GroupStates = {
            'SmartMix':         'V',
            'Speaker':          'S',
            'AEC Reference':    'R'
        }
        group = qualifier['Group']

        if 1 <= channel <= 4 and group in GroupStates:
            GainCmdString = 'GAIN {} {}\r\n'.format(channel, GroupStates[group])
            self.__UpdateHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGain')

    def __MatchGain(self, match, tag):

        GroupStates = {
            'V': 'SmartMix',
            'S': 'Speaker',
            'R': 'AEC Reference'
        }

        qualifier = {
            'Channel':  match.group(1).decode(),
            'Group':    GroupStates[match.group(2).decode()]
        }

        value = int(float(match.group(3).decode()))
        if -65 <= value <= 20:
            self.WriteStatus('Gain', value, qualifier)

    def SetLEDBlink(self, value, qualifier):

        StateStates = {
            'Muted':    '1',
            'Unmuted':  '0'
        }
        state = qualifier['State']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if state in StateStates and value in ValueStateValues:
            LEDBlinkCmdString = 'LEDBLINK {} {}\r\n'.format(StateStates[state], ValueStateValues[value])
            self.__SetHelper('LEDBlink', LEDBlinkCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBlink')

    def UpdateLEDBlink(self, value, qualifier):

        StateStates = {
            'Muted':    '1',
            'Unmuted':  '0'
        }
        state = qualifier['State']

        if state in StateStates:
            LEDBlinkCmdString = 'LEDBLINK {}\r\n'.format(StateStates[state])
            self.__UpdateHelper('LEDBlink', LEDBlinkCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDBlink')

    def __MatchLEDBlink(self, match, tag):

        StateStates = {
            '1': 'Muted',
            '0': 'Unmuted'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'State': StateStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LEDBlink', value, qualifier)

    def SetLEDBrightness(self, value, qualifier):

        StateStates = {
            'Muted':    '1',
            'Unmuted':  '0'
        }
        state = qualifier['State']

        ValueStateValues = {
            'Off':      '0',
            'High':     '1',
            'Medium':   '2',
            'Low':      '3'
        }

        if state in StateStates and value in ValueStateValues:
            LEDBrightnessCmdString = 'LEDBRIGHT {} {}\r\n'.format(StateStates[state], ValueStateValues[value])
            self.__SetHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBrightness')

    def UpdateLEDBrightness(self, value, qualifier):

        StateStates = {
            'Muted':    '1',
            'Unmuted':  '0'
        }
        state = qualifier['State']

        if state in StateStates:
            LEDBrightnessCmdString = 'LEDBRIGHT {}\r\n'.format(StateStates[state])
            self.__UpdateHelper('LEDBrightness', LEDBrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDBrightness')

    def __MatchLEDBrightness(self, match, tag):

        StateStates = {
            '1': 'Muted',
            '0': 'Unmuted'
        }

        ValueStateValues = {
            '0': 'Off',
            '1': 'High',
            '2': 'Medium',
            '3': 'Low'
        }

        qualifier = {
            'State': StateStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LEDBrightness', value, qualifier)

    def SetLEDColor(self, value, qualifier):

        StateStates = {
            'Muted':    '1',
            'Unmuted':  '0'
        }
        state = qualifier['State']

        ValueStateValues = {
            'Red':      '1',
            'Orange':   '2',
            'Yellow':   '3',
            'Green':    '4',
            'Blue':     '5',
            'Indigo':   '6',
            'Violet':   '7',
            'White':    '8'
        }

        if state in StateStates and value in ValueStateValues:
            LEDColorCmdString = 'LEDCOLOR {} {}\r\n'.format(StateStates[state], ValueStateValues[value])
            self.__SetHelper('LEDColor', LEDColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDColor')

    def UpdateLEDColor(self, value, qualifier):

        StateStates = {
            'Muted':    '1',
            'Unmuted':  '0'
        }
        state = qualifier['State']

        if state in StateStates:
            LEDColorCmdString = 'LEDCOLOR {}\r\n'.format(StateStates[state])
            self.__UpdateHelper('LEDColor', LEDColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDColor')

    def __MatchLEDColor(self, match, tag):

        StateStates = {
            '1': 'Muted',
            '0': 'Unmuted'
        }

        ValueStateValues = {
            '1': 'Red',
            '2': 'Orange',
            '3': 'Yellow',
            '4': 'Green',
            '5': 'Blue',
            '6': 'Indigo',
            '7': 'Violet',
            '8': 'White'
        }

        qualifier = {
            'State': StateStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LEDColor', value, qualifier)

    def SetMute(self, value, qualifier):

        channel = int(qualifier['Channel'])

        GroupStates = {
            'SmartMix':         'V',
            'Speaker':          'S',
            'Beam':             'B',
            'AEC Reference':    'R'
        }
        group = qualifier['Group']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= channel <= 12 and group in GroupStates and value in ValueStateValues:
            MuteCmdString = 'MUTE {} {} {}\r\n'.format(channel, GroupStates[group], ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        channel = int(qualifier['Channel'])

        GroupStates = {
            'SmartMix':         'V',
            'Speaker':          'S',
            'Beam':             'B',
            'AEC Reference':    'R'
        }
        group = qualifier['Group']

        if 1 <= channel <= 12 and group in GroupStates:
            MuteCmdString = 'MUTE {} {}\r\n'.format(channel, GroupStates[group])
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        GroupStates = {
            'V': 'SmartMix',
            'S': 'Speaker',
            'B': 'Beam',
            'R': 'AEC Reference'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Channel':  match.group(1).decode(),
            'Group':    GroupStates[match.group(2).decode()]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Mute', value, qualifier)

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()