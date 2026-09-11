from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify

class DeviceSerialClass:

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
        self.Models = {
            'XJ-F210WN': self.casi_1_2220_FXXX,
            'XJ-F200WN': self.casi_1_2220_FXXX,
            'XJ-F20XN': self.casi_1_2220_FXX,
            'XJ-F100W': self.casi_1_2220_FXXX,
            'XJ-F10X': self.casi_1_2220_FXX,
            'XJ-V10X': self.casi_1_2220_VXX,
            'XJ-V100W': self.casi_1_2220_VXXX,
            'XJ-V110W': self.casi_1_2220_VXXX,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampHours': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'MicInputLevel': {'Status': {}},
            'Power': {'Status': {}},
            'Transport': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        
    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '(ARZ{0})'.format(self.AspectValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '(ARZ?)'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.AspectStates[res[res.index(',') + 1:-1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Normal',
            '1': 'Fan Error',
            '2': 'Temperature Error',
            '7': 'Light Error',
            '16': 'Other Error'
        }

        DeviceStatusCmdString = '(STS?)'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[res.index(',') + 1:-1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '(FRZ1)',
            'Off': '(FRZ0)'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = '(FRZ?)'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[res.index(',') + 1:-1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputCmdString = '(SRC{0})'.format(self.InputValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '(SRC?)'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStates[res[res.index(',') + 1:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = '(LMP?)'
        res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[res.index(',') + 1:-1])
                self.WriteStatus('LampHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Hours: Invalid/unexpected response'])

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '(KEY1)',
            'Down': '(KEY2)',
            'Left': '(KEY3)',
            'Right': '(KEY4)',
            'Escape': '(KEY6)',
            'Enter': '(KEY5)',
            'Menu': '(KEY11)'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMicInputLevel(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3'
        }

        MicInputLevelCmdString = '(MIC{0})'.format(ValueStateValues[value])
        self.__SetHelper('MicInputLevel', MicInputLevelCmdString, value, qualifier)

    def UpdateMicInputLevel(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3'
        }

        MicInputLevelCmdString = '(MIC?)'
        res = self.__UpdateHelper('MicInputLevel', MicInputLevelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[res.index(',') + 1:-1]]
                self.WriteStatus('MicInputLevel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mic Input Level: Invalid/unexpected response'])

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '(MUT1)',
            'Off': '(MUT0)'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteCmdString = '(MUT?)'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[res.index(',') + 1:-1]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '(PWR1)',
            'Off': '(PWR0)'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PowerCmdString = '(PWR?)'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[res.index(',') + 1:-1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play/Pause': '(KEY26)',
            'Rewind': '(KEY27)',
            'Fast Forward': '(KEY28)',
            'Previous': '(KEY29)',
            'Next': '(KEY30)'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '(BLK1)',
            'Off': '(BLK0)'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = '(BLK?)'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[res.index(',') + 1:-1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 30
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '(VOL{0})'.format(str(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '(VOL?)'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[res.index(',') + 1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == '(?)':
            self.Error(['Unrecognized Command'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=')')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b')')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def casi_1_2220_FXXX(self):
        self.InputValues = {
            'RGB' : '0', 
            'Component' : '1', 
            'Video' : '2', 
            'Auto' : '6', 
            'HDMI 1' : '7', 
            'HDMI 2' : '14', 
            'Network' : '8', 
            'CASIO USB Tool' : '13', 
            'USB Display' : '12', 
            'File Viewer' : '11', 
            'S-Video' : '9'
        }
        self.InputStates = {
            '0' : 'RGB', 
            '1' : 'Component', 
            '2' : 'Video', 
            '6' : 'Auto', 
            '7' : 'HDMI 1', 
            '14' : 'HDMI 2', 
            '8' : 'Network', 
            '13' : 'CASIO USB Tool', 
            '12' : 'USB Display', 
            '11' : 'File Viewer', 
            '9' : 'S-Video'
        }    
        self.AspectValues = {
            'Normal A'   : '0',
            'Normal B'   : '2', 
            '16:9'       : '1', 
            'Letter Box' : '3', 
            'Full'       : '4', 
            'True'       : '5', 
            '4:3'        : '6', 
            '16:10'      : '7'
        }
        self.AspectStates = {
            '1' : '16:9', 
            '3' : 'Letter Box', 
            '4' : 'Full', 
            '5' : 'True', 
            '6' : '4:3', 
            '7' : '16:10', 
            '0' : 'Normal A', 
            '2' : 'Normal B'
        }        

    def casi_1_2220_FXX(self):
        self.InputValues = {
            'RGB' : '0', 
            'Component' : '1', 
            'Video' : '2', 
            'Auto' : '6', 
            'HDMI 1' : '7', 
            'HDMI 2' : '14', 
            'Network' : '8', 
            'CASIO USB Tool' : '13', 
            'USB Display' : '12', 
            'File Viewer' : '11', 
            'S-Video' : '9'
        }
        self.InputStates = {
            '0' : 'RGB', 
            '1' : 'Component', 
            '2' : 'Video', 
            '6' : 'Auto', 
            '7' : 'HDMI 1', 
            '14' : 'HDMI 2', 
            '8' : 'Network', 
            '13' : 'CASIO USB Tool', 
            '12' : 'USB Display', 
            '11' : 'File Viewer', 
            '9' : 'S-Video'
        }    
        self.AspectValues = {
            'Normal A'   : '0',
            'Normal B'   : '2', 
            '16:9'       : '1', 
            'Full'       : '4', 
            '4:3'        : '6', 
            '16:10'      : '7'
        }
        self.AspectStates = {
            '1' : '16:9', 
            '4' : 'Full', 
            '6' : '4:3', 
            '7' : '16:10', 
            '0' : 'Normal A', 
            '2' : 'Normal B'
        }       

    def casi_1_2220_VXXX(self):
        self.InputValues = {
            'RGB' : '0', 
            'Component' : '1', 
            'Auto' : '6', 
            'HDMI' : '7'
        }
        self.InputStates = {
            '0' : 'RGB', 
            '1' : 'Component', 
            '6' : 'Auto', 
            '7' : 'HDMI'
        }
        self.AspectValues = {
            'Normal A'   : '0',
            'Normal B'   : '2', 
            '16:9'       : '1', 
            'Letter Box' : '3', 
            'Full'       : '4', 
            'True'       : '5', 
            '4:3'        : '6', 
            '16:10'      : '7'
        }
        self.AspectStates = {
            '1' : '16:9', 
            '3' : 'Letter Box', 
            '4' : 'Full', 
            '5' : 'True', 
            '6' : '4:3', 
            '7' : '16:10', 
            '0' : 'Normal A', 
            '2' : 'Normal B'
        }       

    def casi_1_2220_VXX(self):
        self.InputValues = {
            'RGB' : '0', 
            'Component' : '1', 
            'Auto' : '6', 
            'HDMI' : '7'
        }
        self.InputStates = {
            '0' : 'RGB', 
            '1' : 'Component', 
            '6' : 'Auto', 
            '7' : 'HDMI'
        }
        self.AspectValues = {
            'Normal A'   : '0',
            'Normal B'   : '2', 
            '16:9'       : '1', 
            'Full'       : '4', 
            '4:3'        : '6', 
            '16:10'      : '7'
        }
        self.AspectStates = {
            '1' : '16:9', 
            '4' : 'Full', 
            '6' : '4:3', 
            '7' : '16:10', 
            '0' : 'Normal A', 
            '2' : 'Normal B'
        }       

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
        self.Models = {}
        self.devicePassword = None
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AVMute': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'LampHours': {'Status': {}},
            'Power': {'Status': {}},
        }

        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'PJLINK 1 ([a-f0-9]{8})\r'), self.__MatchPassword, None)

    def SetPassword(self, value, qualifier):
        self.Send(value)

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            inStr = match.group(1).decode()
            outStr = inStr + self.devicePassword
            encrypted = hashlib.md5(outStr.encode())
            password = hexlify(encrypted.digest()) + b'%1POWR ?\r'
            self.Authenticated = 'Admin'
            self.SetPassword(password, None)
        else:
            self.MissingCredentialsLog('Password')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '21',
            'Off': '20'
        }

        AudioMuteCmdString = '%1AVMT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateAVMute(value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '31',
            'Off': '30'
        }

        AVMuteCmdString = '%1AVMT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            '31': 'On',
            '30': 'Off',
            '21': 'On'
        }


        AVMuteCmdString = '%1AVMT ?\r'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = res[7:-1]
                if value == '30':
                    self.WriteStatus('AVMute', 'Off', qualifier)
                    self.WriteStatus('AudioMute', 'Off', qualifier)
                elif value == '31':
                    self.WriteStatus('AVMute', 'On', qualifier)
                    self.WriteStatus('AudioMute', 'Off', qualifier)
                elif value == '21':
                    self.WriteStatus('AVMute', 'Off', qualifier)
                    self.WriteStatus('AudioMute', 'On', qualifier)
            except (IndexError):
                self.Error(['AV / Audio Mute: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'Fan',
            1: 'Lamp',
            2: 'Temperature',
            3: 'Cover',
            4: 'Filter',
            5: 'Other',
        }

        DeviceStatusCmdString = '%1ERST ?\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                status = res[7:-1]
                if status.count('0') == 6:
                    value = 'Normal'
                elif status.count('1') + status.count('2') > 2:
                    value = 'Multiple Warnings / Errors'
                elif status.count('1') == 1:
                    index = status.index('1')
                    value = '{0} Warning'.format(ValueStateValues[index])
                elif status.count('2') == 1:
                    index = status.index('2')
                    value = '{0} Error'.format(ValueStateValues[index])
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'RGB': '11',
            'Component': '23',
            'Video': '21',
            'HDMI 1': '31',
            'HDMI 2': '32',
            'Network': '51',
            'USB Display': '52',
            'S-Video': '22'
        }

        InputCmdString = '%1INPT {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '11': 'RGB',
            '23': 'Component',
            '21': 'Video',
            '31': 'HDMI 1',
            '32': 'HDMI 2',
            '51': 'Network',
            '52': 'USB Display',
            '22': 'S-Video'
        }

        InputCmdString = '%1INPT ?\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampHours(self, value, qualifier):

        LampHoursCmdString = '%1LAMP ?\r'
        res = self.__UpdateHelper('LampHours', LampHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[7:-3])
                self.WriteStatus('LampHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }

        PowerCmdString = '%1POWR {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'Cooling Down',
            '3': 'Warming Up'
        }

        PowerCmdString = '%1POWR ?\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'ERR1': "Undefined command.",
            'ERR2': "Out of parameter.",
            'ERR3': "Unavailable time.",
            'ERR4': "Projector failure.",
            'ERRA': "Invalid password."
        }

        if 'ERR' in response:
            self.Error([sourceCmdName + ' ' + DEVICE_ERROR_CODES[response[7:-1]]])
            if 'ERRA' in response:
                self.Authenticated = 'None'
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command')
            return ''

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())

        else:
            self.Discard('Inappropriate Command ' + command)
            return''

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
        
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
