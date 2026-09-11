from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
import math
import binascii

class DeviceSerialClass:

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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'EnergySaving': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.DeviceID = 1

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9a-f]{2,3} OK(01|02|04|06|09|10|11|12|13|14|15|16|17|18|19|1a|1b|1c|1d|1e|1f|21|30|31)x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'e [0-9a-f]{2,3} OK(01|00)x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'q [0-9a-f]{2,3} OK(00|01|02|03|04|05)x'), self.__MatchEnergySaving, None)
            self.AddMatchString(re.compile(b'm [0-9a-f]{2,3} OK(01|00)x'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'b [0-9a-f]{2,3} OK(70|80|90|a0|91|a1|c0|d0|e0|e2)x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'a [0-9a-f]{2,3} OK(01|00)x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd [0-9a-f]{2,3} OK(01|00)x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9a-f]{2,3} OK([0-9a-f]{2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(c|e|m|b|a|d|f|x|q) [0-9a-f]{2,3} NG(.*?)x'), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9a-f]{2}x')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 0 <= int(value) <= 1000:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            print('Invalid Device ID Parameter.')

    def SetAspectRatio(self, value, qualifier):

        Value = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Original': '06',
            'Just Scan': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1a',
            'Cinema Zoom 12': '1b',
            'Cinema Zoom 13': '1c',
            'Cinema Zoom 14': '1d',
            'Cinema Zoom 15': '1e',
            'Cinema Zoom 16': '1f',
            '58:9': '21',
            'Vertical Zoom': '30',
            'All Direction Zoom': '31'
        }[value]

        AspectRatioCmdString = 'kc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        Value = {
            '01': '4:3',
            '02': '16:9',
            '04': 'Zoom',
            '06': 'Original',
            '09': 'Just Scan',
            '10': 'Cinema Zoom 1',
            '11': 'Cinema Zoom 2',
            '12': 'Cinema Zoom 3',
            '13': 'Cinema Zoom 4',
            '14': 'Cinema Zoom 5',
            '15': 'Cinema Zoom 6',
            '16': 'Cinema Zoom 7',
            '17': 'Cinema Zoom 8',
            '18': 'Cinema Zoom 9',
            '19': 'Cinema Zoom 10',
            '1a': 'Cinema Zoom 11',
            '1b': 'Cinema Zoom 12',
            '1c': 'Cinema Zoom 13',
            '1d': 'Cinema Zoom 14',
            '1e': 'Cinema Zoom 15',
            '1f': 'Cinema Zoom 16',
            '21': '58:9',
            '30': 'Vertical Zoom',
            '31': 'All Direction Zoom'
            }[match.group(1).decode()]

        self.WriteStatus('AspectRatio', Value, None)

    def SetAudioMute(self, value, qualifier):

        Value = {
            'On': '00',
            'Off': '01'
            }[value]

        AudioMuteCmdString = 'ke {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        Value = {
            '00': 'On',
            '01': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('AudioMute', Value, None)

    def SetEnergySaving(self, value, qualifier):

        Value = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04',
            'Screen Off': '05'
        }[value]

        EnergySavingCmdString = 'jq {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('EnergySaving', EnergySavingCmdString, value, qualifier)

    def UpdateEnergySaving(self, value, qualifier):

        EnergySavingCmdString = 'jq {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('EnergySaving', EnergySavingCmdString, value, qualifier)

    def __MatchEnergySaving(self, match, tag):

        Value = {
            '00': 'Off',
            '01': 'Minimum',
            '02': 'Medium',
            '03': 'Maximum',
            '04': 'Automatic',
            '05': 'Screen Off'
        }[match.group(1).decode()]

        self.WriteStatus('EnergySaving', Value, None)

    def SetExecutiveMode(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
            }[value]

        CmdString = 'km {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'km {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        Value = {
            '01': 'On',
            '00': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('ExecutiveMode', Value, None)

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': '00',
            'Off': '01'
        }[value]

        FreezeCmdString = 'kx {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        Value = {
            'DVI-D (PC)': '70',
            'DVI-D (DTV)': '80',
            'HDMI (DTV)': '90',
            'HDMI (PC)': 'a0',
            'OPS (DTV)': '91',
            'OPS (PC)': 'a1',
            'DisplayPort (DTV)': 'c0',
            'DisplayPort (PC)': 'd0',
            'SuperSign webOS Player': 'e0',
            'Multi Screen': 'e2'
        }[value]

        InputCmdString = 'xb {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xb {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        Value = {
            '70': 'DVI-D (PC)',
            '80': 'DVI-D (DTV)',
            '90': 'HDMI (DTV)',
            'a0': 'HDMI (PC)',
            '91': 'OPS (DTV)',
            'a1': 'OPS (PC)',
            'c0': 'DisplayPort (DTV)',
            'd0': 'DisplayPort (PC)',
            'e0': 'SuperSign webOS Player',
            'e2': 'Multi Screen'
        }[match.group(1).decode()]

        self.WriteStatus('Input', Value, None)

    def SetKeypad(self, value, qualifier):

        Value = {
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
        }[value]

        KeypadCmdString = 'mc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        Value = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Ok': '44',
            'Exit': '5b',
            'Back': '28'
            }[value]

        MenuNavigationCmdString = 'mc {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
            }[value]

        PowerCmdString = 'ka {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        Value = {
            '01': 'On',
            '00': 'Off'
            }[match.group(1).decode()]

        self.WriteStatus('Power', Value, None)

    def SetVideoMute(self, value, qualifier):

        Value = {
            'On': '01',
            'Off': '00'
            }[value]

        VideoMuteCmdString = 'kd {0} {1}\r'.format(self._DeviceID, Value)
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        Value = {
            '01': 'On',
            '00': 'Off'
            }[match.group(1).decode()]
        self.WriteStatus('VideoMute', Value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'kf {0} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'OK' in response:
            return response
        elif 'NG' in response:
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '00':
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

        ErrorState = {
            'c' : 'Aspect Ratio',
            'e' : 'Audio Mute',
            'b' : 'Input',
            'x' : 'Picture Mode',
            'a' : 'Power',
            'm' : 'Executive Mode',
            'd' : 'Video Mute',
            'f' : 'Volume',
            'q' : 'Energy Saving'
            }

        temp1 = ErrorState[match.group(1).decode()]
        temp2 = match.group(2).decode()
        value = 'Command: {0}. Error: {1}'.format(temp1,temp2)
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

class DeviceEthernetClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'EnergySaving': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PowerOff': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.CommandOIDDict = {
            'AspectRatio': '1.3.6.1.4.1.7824.300.3.3',
            'AudioMute': '1.3.6.1.4.1.7824.300.3.5',
            'EnergySaving': '1.3.6.1.4.1.7824.300.3.19',
            'ExecutiveMode': '1.3.6.1.4.1.7824.300.3.13',
            'Freeze': '1.3.6.1.4.1.7824.300.3.23',
            'Input': '1.3.6.1.4.1.7824.300.3.2',
            'Keypad': '1.3.6.1.4.1.7824.300.3.23',
            'MenuNavigation': '1.3.6.1.4.1.7824.300.3.23',
            'PowerOff': '1.3.6.1.4.1.7824.300.3.1',
            'VideoMute': '1.3.6.1.4.1.7824.300.3.4',
            'Volume': '1.3.6.1.4.1.7824.300.3.6'
            }

    @property
    def Writecommunity(self):
        return self._Writecommunity

    @Writecommunity.setter
    def Writecommunity(self, value):
        self._Writecommunity = value
        self.SNMP = SNMPDevice(value, self.CommandOIDDict)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '01',
            '16:9': '02',
            'Zoom': '04',
            'Original': '06',
            'Just Scan': '09',
            'Cinema Zoom 1': '10',
            'Cinema Zoom 2': '11',
            'Cinema Zoom 3': '12',
            'Cinema Zoom 4': '13',
            'Cinema Zoom 5': '14',
            'Cinema Zoom 6': '15',
            'Cinema Zoom 7': '16',
            'Cinema Zoom 8': '17',
            'Cinema Zoom 9': '18',
            'Cinema Zoom 10': '19',
            'Cinema Zoom 11': '1a',
            'Cinema Zoom 12': '1b',
            'Cinema Zoom 13': '1c',
            'Cinema Zoom 14': '1d',
            'Cinema Zoom 15': '1e',
            'Cinema Zoom 16': '1f',
            '58:9': '21',
            'Vertical Zoom': '30',
            'All Direction Zoom': '31'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '0x01',
            'Off': '0x00'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetEnergySaving(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
            'Minimum': '01',
            'Medium': '02',
            'Maximum': '03',
            'Automatic': '04',
            'Screen Off': '05'
        }

        EnergySavingCmdString = ValueStateValues[value]
        self.__SetHelper('EnergySaving', EnergySavingCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = 'BA'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVI-D (PC)': '70',
            'DVI-D (DTV)': '80',
            'HDMI (DTV)': '90',
            'HDMI (PC)': 'a0',
            'OPS (DTV)': '91',
            'OPS (PC)': 'a1',
            'DisplayPort (DTV)': 'c0',
            'DisplayPort (PC)': 'd0',
            'SuperSign webOS Player': 'e0',
            'Multi Screen': 'e2'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

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

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '40',
            'Down': '41',
            'Left': '07',
            'Right': '06',
            'Menu': '45',
            'Ok': '44',
            'Exit': '5b',
            'Back': '28'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '00'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0:02X}'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
                1: "Response message too large to transport",
                2: "The name of the requested object was not found",
                3: "A data type in the request did not match the data type in the SNMP agent",
                4: "The SNMP manager attempted to set a read-only parameter",
                5: "General Error",
                6: "The specified SNMP variable is not accessible.",
                7: "The value specifies a type that is inconsistent with the type required for the variable.",
                8: "The value specifies a length that is inconsistent with the length required for the variable.",
                9: "The value contains an Abstract Syntax Notation One (ASN.1) encoding that is inconsistent with the ASN.1 tag of the field.",
                10: "The value cannot be assigned to the variable.",
                11: "The variable does not exist, and the agent cannot create it.",
                12: "The value is inconsistent with values of other managed objects.",
                13: "Assigning the value to the variable requires allocation of resources that are currently unavailable.",
                14: "No validation errors occurred, but no variables were updated.",
                15: "No validation errors occurred. Some variables were updated because it was not possible to undo their assignment.",
                16: "An authorization error occurred.",
                17: "The variable exists but the agent cannot modify it.",
                18: "The variable does not exist; the agent cannot create it because the named object instance is inconsistent with the values of other managed objects."
               }

        if response[0] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0]]))
            response = ''
        else:
            response = response[1]
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        if hasattr(self, 'SNMP'):
            commandstring = self.SNMP.encodeMsg('Set', command, value)
            self.Send(commandstring)
        else:
            print('Writecommunity variable must be set. See communication sheet for details.')

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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
    
class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()
                
class SNMPDeviceException(Exception):
    pass

class SNMPDevice():
    def __init__(self, community, CommandOIDDict):
        self.community = community
        self.CommandOIDDict = CommandOIDDict
        self.oidList = {}
        for command in CommandOIDDict:
            self.oidList[command] = self.__BuildOID(self.CommandOIDDict[command])
        self.community = community
        self.communityString = b'\x04'+pack('>B', len(self.community))+self.community.encode()
        self.GetNext = False

    def addOID(self, command, oid):
        if command in self.oidList:
            raise SNMPDeviceException('Command/UID already associated with a different OID')
        self.oidList[command] = self.__BuildOID(oid)

    def getOID(self, command):
        if command not in self.oidList:
            raise SNMPDeviceException('Command/UID not in OID List of the device')
        return self.__RebuildOIDString(self.oidList[command])

    def decodeOID(self, msg, command = None, OID = None):
        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if OID is None and command is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')
        try:
            if OID is not None:
                oidIndex = msg.index(self.__BuildOID(OID))
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex-1]
            OID = msg[oidIndex: oidIndex+oidLength]
            value = self.__RebuildOIDString(OID)
            return value
        except ValueError:
            raise SNMPDeviceException('OID for that command/UID not found in the message')

    def encodeMsg(self, queryType, command=None, value = None, OID = None):
        if command not in self.oidList and OID is None:
            raise SNMPDeviceException('Command/UID not in CommandOIDDict')

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
            }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04'+ pack('>B', valueLen)+ valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:])/2)*2))
                valueLen = len(valueBytes)
                if valueLen < 2:                             ##fix to make Int32        11/03/14
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02'+ pack('>B', valueLen)+ valueBytes
            else:
                raise TypeError('Value is not of type int or string')
        else:
            valueMsg = b'\x05\x00'
            
        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
            else:
                oid = self.oidList[command]
        else:
            oid = self.nextOID
            self.GetNext = False
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        oidMsg = b'\x06' + pack('>B', len(oid)) + oid
        varbindMsg = b'\x30' + pack('>B', len(oidMsg+valueMsg)) + oidMsg+valueMsg
        varbindListMsg = b'\x30' + pack('>B', len(varbindMsg)) + varbindMsg
        snmpPduMsg = pduType + pack('>B', len(requestID+error+errorIndex+varbindListMsg)) + requestID + error + errorIndex + varbindListMsg
        snmpMsg = b'\x30' + pack('>B', len(snmpVersion+self.communityString+snmpPduMsg)) + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg            

    def encodeMsgMultiOID(self, queryType, command=None, value = None, OID = None, NextOID = None):
        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. At least one must be specified')

        typeDict = {
            'Get': b'\xA0',
            'Set': b'\xA3',
            'Get-Next': b'\xA1'
            }

        if queryType not in typeDict:
            raise SNMPDeviceException('Query type is not Get or Set')

        if value is not None:
            if type(value) == str:
                valueBytes = value.encode()
                valueLen = len(valueBytes)
                valueMsg = b'\x04'+ pack('>B', valueLen)+ valueBytes
            elif type(value) == int:
                valueBytes = binascii.unhexlify(hex(value)[2:].zfill(math.ceil(len(hex(value)[2:])/2)*2))
                valueLen = len(valueBytes)
                if valueLen < 2:
                    valueLen = 2
                    valueBytes = b'\x00' + valueBytes
                valueMsg = b'\x02'+ pack('>B', valueLen)+ valueBytes
            else:
                pass
        else:
            valueMsg = b'\x05\x00'
            
        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
        else:
            oid = self.nextOID
            self.GetNext = False

        varbindListMsg= b''
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        for command2do in command:
            if NextOID:
                oid = self.oidList[command2do]+ pack('>B', NextOID)
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg+valueMsg)) + oidMsg+valueMsg
            varbindListMsg +=  varbindMsg
        if len(varbindListMsg) < 128:
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg
        elif len(varbindListMsg) < 4096:
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg))  + varbindListMsg

        pduLen = len(requestID+error+errorIndex+varbindListMsg)
        if pduLen < 128:
            pduLenMsg = pack('>B', pduLen)
        elif pduLen < 4096:
            pduLenMsg = b'\x81' + pack('>B', pduLen)

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg
        snmpLen = len(snmpVersion+self.communityString+snmpPduMsg)
        if snmpLen < 128:
            snmpLenMsg = pack('>B', snmpLen)
        elif snmpLen < 4096:
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg
        return snmpMsg            


    def decodeMsg(self, msg, command = None, OID = None):
        ValueTypeDict = {
            2  : 'Integer',
            4  : 'Octet String',
            5  : 'Null',
            6  : 'OID',
            64 : 'IPAdddress',
            65 : 'Counter32',
            66 : 'Gauge',
            67 : 'Timeticks',
            68 : 'Opaque',
            69 : 'NsapAddress',
            70 : 'Counter64',
            }

        oidIndex = -1
        valueType = '???'

        if command is None and OID is None:
            raise SNMPDeviceException('Command/UID and OID not specified. You must specify at least one')

        try:
            if OID is not None:
                cutomOIDHex = self.__BuildOID(OID)
                oidIndex = msg.index(cutomOIDHex)
            else:
                oidIndex = msg.index(self.oidList[command])
            oidLength = msg[oidIndex-1]
            self.nextOID = msg[oidIndex: oidIndex+oidLength]
            valueIndex = oidIndex+oidLength
            valueType = ValueTypeDict[msg[valueIndex]]
            valueLen = msg[valueIndex+1]
            if valueType == 'Octet String':
                value = msg[valueIndex+2:valueIndex+2+valueLen].decode()
            elif valueType == 'Null':
                value = None
            elif valueType in  ['Integer', 'Timeticks', 'Counter32', 'Gauge']:
                valueBytes = msg[valueIndex+2:valueIndex+2+valueLen]
                value = int(binascii.hexlify(valueBytes), 16)
            elif valueType == 'OID':
                value = self.__RebuildOIDString(msg[valueIndex+2:valueIndex+2+valueLen])
            elif valueType == 'IPAdddress':
                valueBytes = msg[valueIndex+2:valueIndex+2+valueLen]
                ipAddress = [byte for byte in valueBytes]
                value = '.'.join([str(i) for i in ipAddress])
            error = self.__DecodeError(msg)
            if OID is not None:
                oidCheck = self.nextOID != cutomOIDHex
            else:
                oidCheck = self.nextOID != self.oidList[command]
            if oidCheck and error == 0:
                self.GetNext = True
                return (error, value, self.encodeMsg('Get-Next', command = command))
            return (error, value)
        except ValueError:
            pass
        except KeyError:
            pass

    def __DecodeError(self, msg):
        try:
            pduIndex = msg.index(self.community.encode())+len(self.community.encode())
            requestIdIndex = pduIndex + 2
            ErrorIndex = requestIdIndex + 2 + msg[requestIdIndex+1]
            error = msg[ErrorIndex + 2]
            return error
        except ValueError:
            pass
                
    def __BuildOID(self, oidValue):
        try:
            oidValueNumberList = [int(i) for i in oidValue.split('.')]
        except ValueError:
            raise SNMPDeviceException('OIDs supplied is of invalid type/format')

        oid = pack('>B', 40*oidValueNumberList[0]+oidValueNumberList[1])
        for number in oidValueNumberList[2:]:
            if number < 128:
                oid += pack('>B', number)
            else:
                oid += self.__ConvertToMultipleBytes(number)
        return oid

    def __ConvertToMultipleBytes(self, number):
        binaryNumberSplit = re.findall('[0-1]{7}', bin(number)[2:].zfill(math.ceil(len(bin(number)[2:])/7)*7))
        return pack('>'+'B'*len(binaryNumberSplit), *[int(i, 2) if e == len(binaryNumberSplit)-1 else int(i, 2)+0x80 for e, i in enumerate(binaryNumberSplit)])

    def __RebuildOIDString(self, oidBytes):
        if oidBytes[0] == 43:
            oid = [1, 3]
        else:
            oid = [0, 0]
        highBitCheck = False
        oidbin = ''
        for byte in oidBytes[1:]:
            if byte < 127:
                if highBitCheck:
                    oidbin += bin(byte)[2:].zfill(7)
                    oid.append(int(oidbin, 2))
                    oidbin = ''
                    highBitCheck = False
                else:
                    oid.append(byte)
            else:
                oidbin += bin(byte-0x80)[2:].zfill(7)
                highBitCheck = True
        return '.'.join([str(i) for i in oid])
