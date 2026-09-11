from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify


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
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AutoPosition': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Image': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'StandbyMode': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.Authenticated = 'Not Needed'
        self.Certification = 'Not Received'

        self.MatchString = re.compile('\$AK(.{8})\r')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            res = self.SendAndWait(value, self.DefaultResponseTimeout, deliTag=b'\r')
            if res:
                if 'PRV=ERRA\r' in res.decode():
                    self.Error(['Error in Authentication with Device'])
                    self.Authenticated = 'Failed'
                else:
                    self.Authenticated = 'Admin'
            else:
                self.Certification = 'Not Received'
        else:
            self.MissingCredentialsLog('Password')

    def UpdatePassword(self):

        if self.Authenticated != 'Failed':
            res = self.SendAndWait('$AK\r', self.DefaultResponseTimeout, deliTag='\r')
            if res:
                MatchObject = re.search(self.MatchString, res)
                if MatchObject is not None:
                    inStr = MatchObject.group(1)
                    outStr = '{0}{1}'.format(inStr, self.Password)
                    m = hashlib.md5(outStr.encode())
                    cmdString = b''.join([hexlify(m.digest()), b'00vST\r'])
                    self.Certification = 'Received'
                    self.SetPassword(cmdString, None)
                else:
                    self.Certification = 'None'
        else:
            self.MissingCredentialsLog('Password')

    def Set3D(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ThreeDCmdString = '00TDE{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('3D', ThreeDCmdString, value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': '0',
            '16:9': '1',
            'Full': '2'
        }

        AspectRatioCmdString = '00SC{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'IN 1': '1',
            'IN 2': '2',
            'IN 3': '3',
            'Mix': '4'
        }

        AudioInputCmdString = '00AUDIO{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)

    def SetAutoPosition(self, value, qualifier):

        AutoPositionCmdString = '00r09\r'
        self.__SetHelper('AutoPosition', AutoPositionCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AVMuteCmdString = '00MUTE{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'CC 1': '1',
            'CC 2': '2',
            'CC 3': '3',
            'CC 4': '4',
            'T1': '5',
            'T2': '6'
        }

        ClosedCaptionCmdString = '00CC{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '000': 'Normal',
            '800': 'Fan Error',
            '400': 'Lamp Out or Not Lit',
            '200': 'Lamp Life has Expired',
            '100': 'Lamp Life is Expiring',
            '080': 'Temperature Error',
            '040': 'Temperature Warning',
            '020': 'Lamp Cover Open Error',
            '008': 'Other Component Abnormality'
        }

        DeviceStatusCmdString = '00vER\r'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:

                response = res[5:-1]
                if response in ValueStateValues:
                    value = ValueStateValues[res[5:-1]]
                else:
                    value = 'Multiple Errors or Warnings'
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Device Status: Invalid/Unexpected Response')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '00FRZ{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetImage(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Theater': '1',
            'Presentation': '2',
            'Standard': '3',
            'Black Board': '4',
            'White Board': '5',
            'User': '6'
        }

        ImageCmdString = '00IMAGE{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Image', ImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1': '00_r1\r',
            'Computer 2': '00_r2\r',
            'Video': '00_v1\r',
            'S-Video': '00_v2\r',
            'HDMI': '00_d1\r',
            'PC Less Presentation': '00_s1\r',
            'USB': '00_s2\r',
            'LAN': '00_n1\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'r1': 'Computer 1',
            'r2': 'Computer 2',
            'v1': 'Video',
            'v2': 'S-Video',
            'd1': 'HDMI',
            's1': 'PC Less Presentation',
            's2': 'USB',
            'n1': 'LAN'
        }

        InputCmdString = '00vl\r'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:-1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Input: Invalid/Unexpected Response')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': '0',
            'Low': '1'
        }

        LampModeCmdString = '00LM{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = '00vLE\r'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5:-1])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Lamp Usage: Invalid/Unexpected Response')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '00!\r',
            'Off': '00"\r'
        }

        PowerCmdString = ValueStateValues[value]

        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '2': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '3': 'Cooling Down',
            '4': 'Power Error',
            '5': 'On',
            '6': 'Awaiting Password Entry'
        }

        if 'Serial' not in self.ConnectionType and self.Certification == 'Not Received':
            self.UpdatePassword()
        else:
            PowerCmdString = '00vST\r'
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    res = res[-2]
                    self.WriteStatus('Power', ValueStateValues[res], qualifier)
                except (KeyError, IndexError):
                    print('Power: Invalid/unexpected response')

    def UpdateSignalStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Signal',
            '0': 'No Signal'
        }

        SignalStatusCmdString = '00vSM\r'
        res = self.__UpdateHelper('SignalStatus', SignalStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('SignalStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Signal Status: Invalid/Unexpected Response')

    def SetStandbyMode(self, value, qualifier):

        ValueStateValues = {
            'LAN': '0',
            'Low': '1',
            'Speaker Out': '2',
            'Monitor Out': '3'
        }

        StandbyModeCmdString = '00STBY{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('StandbyMode', StandbyModeCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 21
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '00VL{0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[-2] == 'N':
            print('{0}: Invalid/Unexpected Response'.format(sourceCmdName))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('{0}: Invalid/unexpected response'.format(command))
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or ('Serial' not in self.ConnectionType and self.Authenticated != 'Admin'):
            print('Inappropriate Command ', command)
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
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Certification = 'Not Received'
        self.Authenticated = 'Not Needed'

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
