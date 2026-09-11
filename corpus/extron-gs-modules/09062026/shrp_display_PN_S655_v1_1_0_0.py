from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
from re import compile, search
import time

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
            'AspectRatio': {'Parameters': ['Device ID', 'Input'], 'Status': {}},
            'AssignID': {'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'IDCheck': {'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Mute': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}}
        }

        self.IDSent = False

        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '0'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(WAIT\r\n)?OK (\d\d\d)\r\n'), self.__MatchDeviceOK, None)

        self.SetRegex = compile(b'OK \d{3}\r\n|ERR\r\n')
        self.UpdateRegex = compile(b'\d{1,3} \d{3}\r\n|ERR\r\n')

    def DeviceIDHandler(self, Callback, value, qualifier):

        if qualifier['Device ID'] == 'Broadcast':
            qualifier['Device ID'] = '0'
            if 'Update' in Callback:
                self.Discard('Invalid Command')
                return False

        self.Callback = getattr(self, Callback)
        self.valueCallback = value
        self.qualifierCallback = qualifier

        if self.SelectedID == qualifier['Device ID']:
            self.IDSent = False
            self.ExpiryTime = 0
            return True

        elif (self.ExpiryTime != 0) and (self.ExpiryTime <= time.monotonic()):
            self.IDSent = False
            self.ExpiryTime = 0
            print('Response timeout: Unable to set Device ID')

        else:
            return self.IDLK_Callback()

    def IDLK_Callback(self):

        if not self.IDSent:
            self.IDSent = True
            CmdString = 'IDLK{0:04d}\r\n'.format(int(self.qualifierCallback['Device ID']))
            self.SetIDLK(CmdString, None)

        else:
            self.Callback(self.valueCallback, self.qualifierCallback)

    def SetIDLK(self, CmdString, qualifier):
        self.ExpiryTime = time.monotonic() + 5
        self.Send(CmdString)

        if self.qualifierCallback['Device ID'] == '0':
            self.SelectedID = '0'

        self.IDLK_Callback()

    def __MatchDeviceOK(self, match, tag):
        self.SelectedID = str(int(match.group(2).decode()))

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide': [1, 1],
            'Normal': [2, 4],
            'Dot by Dot': [3, 5],
            'Zoom 1': [4, 2],
            'Zoom 2': [5, 3]
        }

        inputStatus = qualifier['Input']
        if inputStatus:
            if 'PC' in inputStatus:
                aspectVal = ValueStateValues[value][0]
            elif 'AV' in inputStatus:
                aspectVal = ValueStateValues[value][1]
            else:
                print('Invalid Command for SetAspectRatio')
            AspectRatioCmdString = 'WIDE{0: 4}\r\n'.format(aspectVal)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1': ['Wide', 'Wide'],
            '2': ['Normal', 'Zoom 1'],
            '3': ['Dot by Dot', 'Zoom 2'],
            '4': ['Zoom 1', 'Normal'],
            '5': ['Zoom 2', 'Dot by Dot']
        }

        inputStatus = qualifier['Input']
        if inputStatus:
            if 'PC' in inputStatus:
                aspectVal = 0
            elif 'AV' in inputStatus:
                aspectVal = 1
            else:
                print('Invalid Command for UpdateAspectRatio')

            if self.DeviceIDHandler('UpdateAspectRatio', value, qualifier):
                res = self.__UpdateHelper('AspectRatio', 'WIDE????\r\n', value, qualifier)
                if res:
                    try:
                        value = ValueStateValues[res[0]][aspectVal]
                        self.WriteStatus('AspectRatio', value, qualifier)
                    except (KeyError, IndexError):
                        print('Invalid/unexpected response for UpdateAspectRatio')
        else:
            print('Invalid Command for UpdateAspectRatio')

    def SetAssignID(self, value, qualifier):
        self.__SetHelper('AssignID', 'IDST001+\r\n', value, qualifier)

    def SetIDCheck(self, value, qualifier):
        self.__SetHelper('IDCheck', 'IDCK0000\r\n', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        self.__SetHelper('AutoImage', 'AGIN0001\r\n', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'PC1 DVI-D': 1,
            'PC3 D-SUB': 2,
            'AV3 Component': 3,
            'AV5 Video': 4,
            'PC4 RGB': 6,
            'AV1 DVI-D': 7,
            'AV4 S-Video': 8,
            'AV2 HDMI': 9,
            'PC2 HDMI': 10
        }

        InputCmdString = 'INPS{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1 ': 'PC1 DVI-D',
            '2 ': 'PC3 D-SUB',
            '3 ': 'AV3 Component',
            '4 ': 'AV5 Video',
            '6 ': 'PC4 RGB',
            '7 ': 'AV1 DVI-D',
            '8 ': 'AV4 S-Video',
            '9 ': 'AV2 HDMI',
            '10': 'PC2 HDMI'
        }

        if self.DeviceIDHandler('UpdateInput', value, qualifier):
            res = self.__UpdateHelper('Input', 'INPS????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0:2]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateInput')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        MuteCmdString = 'MUTE{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if self.DeviceIDHandler('UpdateMute', value, qualifier):
            res = self.__UpdateHelper('Mute', 'MUTE????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('Mute', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateMute')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': 0,
            'Off': 1
        }

        OnScreenDisplayCmdString = 'LOSD{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        if self.DeviceIDHandler('UpdateOnScreenDisplay', value, qualifier):
            res = self.__UpdateHelper('OnScreenDisplay', 'LOSD????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('OnScreenDisplay', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'PC1 DVI-D': 1,
            'PC3 D-SUB': 2,
            'AV3 Component': 3,
            'AV5 Video': 4,
            'PC4 RGB': 6,
            'AV1 DVI-D': 7,
            'AV4 S-Video': 8,
            'AV2 HDMI': 9,
            'PC2 HDMI': 10
        }

        PIPInputCmdString = 'MWIP{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '1 ': 'PC1 DVI-D',
            '2 ': 'PC3 D-SUB',
            '3 ': 'AV3 Component',
            '4 ': 'AV5 Video',
            '6 ': 'PC4 RGB',
            '7 ': 'AV1 DVI-D',
            '8 ': 'AV4 S-Video',
            '9 ': 'AV2 HDMI',
            '10': 'PC2 HDMI'
        }

        if self.DeviceIDHandler('UpdatePIPInput', value, qualifier):
            res = self.__UpdateHelper('PIPInput', 'MWIP????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0:2]]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off'   : 0, 
            'PIP'   : 1, 
            'PbyP'  : 2,
            'PbyP2' : 3
        }

        PIPModeCmdString = 'MWIN{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PbyP',
            '3': 'PbyP2'
        }

        if self.DeviceIDHandler('UpdatePIPMode', value, qualifier):
            res = self.__UpdateHelper('PIPMode', 'MWIN????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('PIPMode', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPSize(self, value, qualifier):

        if 1 <= int(value) <= 12:
            PIPSizeCmdString = 'MPSZ{0: 4}\r\n'.format(int(value))
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            '1 ': '1',
            '2 ': '2',
            '3 ': '3',
            '4 ': '4',
            '5 ': '5',
            '6 ': '6',
            '7 ': '7',
            '8 ': '8',
            '9 ': '9',
            '10': '10',
            '11': '11',
            '12': '12'
        }

        if self.DeviceIDHandler('UpdatePIPSize', value, qualifier):
            res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0:2]]
                    self.WriteStatus('PIPSize', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0,
        }

        PowerCmdString = 'POWR{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode'
        }

        if self.DeviceIDHandler('UpdatePower', value, qualifier):
            res = self.__UpdateHelper('Power', 'POWR????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if self.DeviceIDHandler('UpdateVolume', value, qualifier):
            res = self.__UpdateHelper('Volume', 'VOLM????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if response[:3] == 'ERR':
                ErrorString = '{0}:Communication error or incorrect command'.format(sourceCmdName)
                print(ErrorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex).decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex).decode()
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
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class DeviceEthernetClass:
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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'],'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername(None, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide': [1, 1],
            'Normal': [2, 4],
            'Dot by Dot': [3, 5],
            'Zoom 1': [4, 2],
            'Zoom 2': [5, 3]
        }

        inputStatus = qualifier['Input']
        if inputStatus:
            if 'PC' in inputStatus:
                aspectVal = ValueStateValues[value][0]
            elif 'AV' in inputStatus:
                aspectVal = ValueStateValues[value][1]
            else:
                print('Invalid Command for SetAspectRatio')
            AspectRatioCmdString = 'WIDE{0: 4}\r\n'.format(aspectVal)
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

        else:
            print('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '1': ['Wide', 'Wide'],
            '2': ['Normal', 'Zoom 1'],
            '3': ['Dot by Dot', 'Zoom 2'],
            '4': ['Zoom 1', 'Normal'],
            '5': ['Zoom 2', 'Dot by Dot']
        }

        inputStatus = qualifier['Input']
        if inputStatus:
            if 'PC' in inputStatus:
                aspectVal = 0
            elif 'AV' in inputStatus:
                aspectVal = 1
            else:
                print('Invalid Command for UpdateAspectRatio')
            res = self.__UpdateHelper('AspectRatio', 'WIDE????\r\n', value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]][aspectVal]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAspectRatio')
        else:
            print('Invalid Command for UpdateAspectRatio')

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', b'AGIN0001\r\n', value, qualifier)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'PC1 DVI-D': 1,
            'PC3 D-SUB': 2,
            'AV3 Component': 3,
            'AV5 Video': 4,
            'PC4 RGB': 6,
            'AV1 DVI-D': 7,
            'AV4 S-Video': 8,
            'AV2 HDMI': 9,
            'PC2 HDMI': 10
        }

        InputCmdString = 'INPS{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        ValueStateValues = {
            '1': 'PC1 DVI-D',
            '2': 'PC3 D-SUB',
            '3': 'AV3 Component',
            '4': 'AV5 Video',
            '6': 'PC4 RGB',
            '7': 'AV1 DVI-D',
            '8': 'AV4 S-Video',
            '9': 'AV2 HDMI',
            '10': 'PC2 HDMI'
        }

        res = self.__UpdateHelper('Input', 'INPS????\r\n', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')


    def SetMute(self, value, qualifier):
        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        MuteCmdString = 'MUTE{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)


    def UpdateMute(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        res = self.__UpdateHelper('Mute', 'MUTE????\r\n', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')


    def SetOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            'On': 0,
            'Off': 1
        }

        OnScreenDisplayCmdString = 'LOSD{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)


    def UpdateOnScreenDisplay(self, value, qualifier):
        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        res = self.__UpdateHelper('OnScreenDisplay', 'LOSD????\r\n', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('OnScreenDisplay', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')


    def SetPIPInput(self, value, qualifier):
        ValueStateValues = {
            'PC1 DVI-D': 1,
            'PC3 D-SUB': 2,
            'AV3 Component': 3,
            'AV5 Video': 4,
            'PC4 RGB': 6,
            'AV1 DVI-D': 7,
            'AV4 S-Video': 8,
            'AV2 HDMI': 9,
            'PC2 HDMI': 10
        }

        PIPInputCmdString = 'MWIP{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)


    def UpdatePIPInput(self, value, qualifier):
        ValueStateValues = {
            '1': 'PC1 DVI-D',
            '2': 'PC3 D-SUB',
            '3': 'AV3 Component',
            '4': 'AV5 Video',
            '6': 'PC4 RGB',
            '7': 'AV1 DVI-D',
            '8': 'AV4 S-Video',
            '9': 'AV2 HDMI',
            '10': 'PC2 HDMI'
        }

        res = self.__UpdateHelper('PIPInput', 'MWIP????\r\n', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[:-2]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPInput')


    def SetPIPMode(self, value, qualifier):
        ValueStateValues = {
            'Off': 0,
            'PIP': 1,
            'PbyP': 2,
            'PbyP2': 3
        }

        PIPModeCmdString = 'MWIN{0: 4}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)


    def UpdatePIPMode(self, value, qualifier):
        ValueStateValues = {
            '0': 'Off',
            '1': 'PIP',
            '2': 'PbyP',
            '3': 'PbyP2'
        }

        res = self.__UpdateHelper('PIPMode', 'MWIN????\r\n', value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePIPMode')

    def SetPIPSize(self, value, qualifier):
        if 1 <= int(value) <= 12:
            CmdString = 'MPSZ{0: 4}\r\n'.format(int(value))
            self.__SetHelper('PIPSize', CmdString, value, qualifier)

        else:
            print('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):
        res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n', value, qualifier)
        if res:
            try:
                value = int(res)
                if 1 <= value <= 12:
                    self.WriteStatus('PIPSize', str(value), qualifier)
                else:
                    print('Invalid/unexpected response for UpdatePIPSize')
            except (ValueError):
                print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):
        States = {
            'On': 1,
            'Off': 0
        }

        CmdString = 'POWR{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        States = {
            '1': 'On',
            '0': 'Off',
            '2': 'Input signal waiting mode'
        }

        res = self.__UpdateHelper('Power', 'POWR????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[res[0]], qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):
        if 0 <= value <= 31:
            CmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        res = self.__UpdateHelper('Volume', 'VOLM????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', int(res), qualifier)
            except (ValueError):
                print('Invalid/unexpected response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response:
            if response[:3] == 'ERR':
                ErrorString = '{0}:Communication error or incorrect command'.format(sourceCmdName)
                print(ErrorString)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n').decode()
            if not res:
                if command == 'Power':
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):
    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
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
