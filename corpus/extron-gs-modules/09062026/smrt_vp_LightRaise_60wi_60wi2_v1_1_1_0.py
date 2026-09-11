from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
import math
import binascii
import re

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Fill' : 'fill', 
            'Match' : 'match', 
            '16:9' : '16:9'
            }

        AspectRatioCmdString = 'set aspectratio={0}\r'.format(AspectRatioState[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'i' : 'Fill', 
            'a' : 'Match', 
            '6' : '16:9'
            }

        AspectRatioCmdString = 'get aspectratio\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[res.find('=')+2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        AudioMuteCmdString = 'set mute={0}\r'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            'n' : 'On', 
            'f' : 'Off'
            }

        AudioMuteCmdString = 'get mute\r'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[res.find('=')+2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            'CC1' : 'cc1', 
            'CC2' : 'cc2',
            'Off' : 'off'
            }

        ClosedCaptionCmdString = 'set cc={0}\r'.format(ClosedCaptionState[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionState = {
            '1' : 'CC1', 
            '2' : 'CC2',
            'f' : 'Off'
            }

        ClosedCaptionCmdString = 'get cc\r'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionState[res[res.find('=')+3]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        FreezeCmdString = 'set videofreeze={0}\r'.format(FreezeState[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
            'n' : 'On', 
            'f' : 'Off'
            }

        FreezeCmdString = 'get videofreeze\r'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[res.find('=')+2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA' : 'VGA1', 
            'Composite' : 'Composite', 
            'HDMI' : 'HDMI1'
            }

        InputCmdString = 'set input={0}\r'.format(InputState[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            'V' : 'VGA',
            'v' : 'VGA',
            'C' : 'Composite',
            'c' : 'Composite', 
            'H' : 'HDMI',
            'h' : 'HDMI'
            }

        InputCmdString = 'get input\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[res.find('=')+1] == ' ':
                    value = InputState[res[res.find('=')+2]]
                else:
                    value = InputState[res[res.find('=')+1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = 'get lamphrs\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[res.find('=')+1:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = 'get syshrs\r'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res[res.find('=')+1:-1])
                self.WriteStatus('OperationHours', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On' : ('on\r', 40), 
            'Off' : ('off now\r', 130)
            }

        PowerCmdString = PowerState[value][0]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, PowerState[value][1])

    def UpdatePower(self, value, qualifier):

        PowerState = {
            'o' : 'On', 
            'i' : 'Off', 
            }

        PowerCmdString = 'get powerstate\r'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[res.find('=')+1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On' : 'on', 
            'Off' : 'off'
            }

        VideoMuteCmdString = 'set videomute={0}\r'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            'n' : 'On', 
            'f' : 'Off'
            }

        VideoMuteCmdString = 'get videomute\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[res.find('=')+2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : -20,
            'Max' : 20
            }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'set volume={0}\r'.format(str(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[res.find('=')+1:-1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x3E')
            if not res:
                self.Error(['No response received'])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x3E')
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


class DeviceEthernetClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Writecommunity = private
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'OperationHours': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.CommandObjectIDDict = {
            'AspectRatio':    '1.3.6.1.4.1.29485.3.2.8.2.7.0',
            'AudioMute':      '1.3.6.1.4.1.29485.3.2.8.3.2.0',
            'ClosedCaption':  '1.3.6.1.4.1.29485.3.2.8.3.3.0',
            'DeviceStatus':   '1.3.6.1.4.1.29485.3.2.8.7.1.0',
            'Freeze':         '1.3.6.1.4.1.29485.3.2.8.2.13.0',
            'Input':          '1.3.6.1.4.1.29485.3.2.8.2.1.0',
            'LampUsage':      '1.3.6.1.4.1.29485.3.2.8.6.3.0',
            'OperationHours': '1.3.6.1.4.1.29485.3.2.8.6.15.0',
            'Power':          '1.3.6.1.4.1.29485.3.2.8.1.0',
            'VideoMute':      '1.3.6.1.4.1.29485.3.2.8.2.12.0',
            'Volume':         '1.3.6.1.4.1.29485.3.2.8.3.1.0',
        }

        
                
    @property
    def Writecommunity(self):
        return self.privateCommunityString

    @Writecommunity.setter
    def Writecommunity(self, value):
        self.privateCommunityString = value
        self.SNMP = SNMPDevice(self.privateCommunityString, self.CommandObjectIDDict)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill':  1,
            'Match': 2,
            '16:9':  3,
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            1: 'Fill',
            2: 'Match',
            3: '16:9',
        }

        res = self.__UpdateHelper('AspectRatio', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':  2,
            'Off': 1
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off',
        }

        res = self.__UpdateHelper('AudioMute', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': 1,
            'CC1': 2,
            'CC2': 3,
        }

        ClosedCaptionCmdString = ValueStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            1: 'Off',
            2: 'CC1',
            3: 'CC2',
        }

        res = self.__UpdateHelper('ClosedCaption', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'Normal',
            2: 'Over Temperature',
            3: 'Fan Lock',
            4: 'Lamp Error',
            5: 'Color Wheel Break',
            6: 'Lamp Overheat',
            7: 'Lamp Driver Error',
        }

        res = self.__UpdateHelper('DeviceStatus', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  2,
            'Off': 1,
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off',
        }

        res = self.__UpdateHelper('Freeze', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA':       1,
            'Composite': 3,
            'HDMI':      5,
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            1: 'VGA',
            3: 'Composite',
            5: 'HDMI',
        }

        res = self.__UpdateHelper('Input', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        res = self.__UpdateHelper('LampUsage', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('LampUsage', value, qualifier)
            except ValueError:
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def UpdateOperationHours(self, value, qualifier):

        res = self.__UpdateHelper('OperationHours', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('OperationHours', value, qualifier)
            except ValueError:
                self.Error(['Operation Hours: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  [1, 60],
            'Off': [2, 120],
        }

        PowerCmdString = ValueStateValues[value][0]
        self.__SetHelper('Power', PowerCmdString, qualifier, ValueStateValues[value][1])

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            2: 'Off',
            3: 'Warming Up',
            4: 'Cooling Down',
        }

        res = self.__UpdateHelper('Power', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':  2,
            'Off': 1,
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off',
        }

        res = self.__UpdateHelper('VideoMute', value, qualifier)
        if str(res):
            try:
                value = ValueStateValues[res]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 40,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.__SetHelper('Volume', value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', value, qualifier)
        if str(res):
            try:
                value = int(res)
                self.WriteStatus('Volume', value, qualifier)
            except ValueError:
                self.Error(['Volume: Invalid/unexpected response'])

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
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0]])])
            response = ''
        else:
            response = response[1]

        return response

    def __SetHelper(self, command, value, qualifier):
        self.Debug = True



        command_string = self.SNMP.encodeMsg('Set', command, value)
        self.Send(command_string)


    def __UpdateHelper(self, command, value, qualifier):

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

            commandstring = self.SNMP.encodeMsg('Get', command)
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                decoded_res = self.SNMP.decodeMsg(res, command)
                return self.__CheckResponseForErrors(command, decoded_res)

            

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])


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

    def encodeMsgMultiOID(self, queryType, command=None, value = None, OID = None, NextOID = None):    ## 06/10/15


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
                pass
        else:
            valueMsg = b'\x05\x00'

        if not self.GetNext:
            if OID is not None:
                oid = self.__BuildOID(OID)
        else:
            oid = self.nextOID
            self.GetNext = False

        varbindListMsg= b''                              ## 6/10/15
        errorIndex = b'\x02\x01\x01'
        error = b'\x02\x01\x00'
        requestID = b'\x02\x01\x01'
        snmpVersion = b'\x02\x01\x01'
        pduType = typeDict[queryType]
        for command2do in command:                  ## --------------------------------
            if NextOID:
                oid = self.oidList[command2do]+ pack('>B', NextOID)         ## 6/10/15
            else:
                oid = self.oidList[command2do]

            oidMsg = b'\x06' + pack('>B', len(oid)) + oid
            varbindMsg = b'\x30' + pack('>B', len(oidMsg+valueMsg)) + oidMsg+valueMsg
            varbindListMsg +=  varbindMsg   ## accumulate OIDs
        if len(varbindListMsg) < 128:                                              ## 6/10/15
            varbindListMsg = b'\x30' + pack('>B', len(varbindListMsg)) + varbindListMsg             ## 6/10/15
        elif len(varbindListMsg) < 4096:                                           ## 6/10/15
            varbindListMsg = b'\x30\x81' + pack('>B', len(varbindListMsg))  + varbindListMsg  ## 6/10/15

        pduLen = len(requestID+error+errorIndex+varbindListMsg)               ## 6/10/15
        if pduLen < 128:                                              ## 6/10/15
            pduLenMsg = pack('>B', pduLen)                            ## 6/10/15
        elif pduLen < 4096:                                           ## 6/10/15
            pduLenMsg = b'\x81' + pack('>B', pduLen)                  ## 6/10/15

        snmpPduMsg = pduType + pduLenMsg + requestID + error + errorIndex + varbindListMsg   ## 6/10/15

        snmpLen = len(snmpVersion+self.communityString+snmpPduMsg)               ## 6/10/15
        if snmpLen < 128:                                              ## 6/10/15
            snmpLenMsg = pack('>B', snmpLen)                           ## 6/10/15
        elif snmpLen < 4096:                                           ## 6/10/15
            snmpLenMsg = b'\x81' + pack('>B', snmpLen)                 ## 6/10/15

        snmpMsg = b'\x30' + snmpLenMsg + snmpVersion + self.communityString + snmpPduMsg  ## 6/10/15
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

        oidIndex = -1  ################################temp 6/10/15
        valueType = '???'  ################################temp 6/10/15

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
