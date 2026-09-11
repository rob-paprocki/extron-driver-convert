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
            '3DSync': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LaserMode': {'Status': {}},
            'LaserUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*3d=(off|auto|sbs|tb|fs|da|iv)#\r', re.I), self.__Match3DSync, None)
            self.AddMatchString(re.compile(b'\*asp=(4:3|16:9|16:10|AUTO|REAL|THEA|5:4|1.88|2.35)#\r', re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\*freeze=(on|off)#\r', re.I), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'\*sour=(RGB|RGB2|dvid|hdmi|dp|sdi|hdbaset)#\r', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\*lampm=(lnor|eco|cust)#\r', re.I), self.__MatchLaserMode, None)
            self.AddMatchString(re.compile(b'\*lsrtim=(\d+)#\r', re.I), self.__MatchLaserUsage, None)
            self.AddMatchString(re.compile(b'\*appmod=(bright|preseT|cine)#\r', re.I), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\*psour=(RGB|RGB2|dvid|hdmi|dp|sdi|hdbaset)#\r', re.I), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\*pip=(on|off)#\r', re.I), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\*pippos=(tl|tr|bl|br|pbp)#\r', re.I), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'\*pow=(on|off)#\r', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\*blank=(on|off)#\r', re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'(Illegal format|Block item|Unsupported item)\r', re.I), self.__MatchError, None)

    def Set3DSync(self, value, qualifier):

        ValueStateValues = {
            'Off': 'off',
            'Auto': 'auto',
            'Sync Side by Side': 'sbs',
            'Top Bottom': 'tb',
            'Frame Sequential': 'fs',
            'Inverter Disable': 'da',
            'Inverter Enable': 'iv'
        }

        cmdString = '\r*3d={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('3DSync', cmdString, value, qualifier)

    def Update3DSync(self, value, qualifier):

        cmdString = '\r*3d=?#\r'
        self.__UpdateHelper('3DSync', cmdString, value, qualifier)

    def __Match3DSync(self, match, tag):

        ValueStateValues = {
            'off': 'Off',
            'auto': 'Auto',
            'sbs': 'Sync Side by Side',
            'tb': 'Top Bottom',
            'fs': 'Frame Sequential',
            'da': 'Inverter Disable',
            'iv': 'Inverter Enable'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('3DSync', value, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10',
            'Auto': 'AUTO',
            'Real': 'REAL',
            'Theater Scope': 'THEA',
            '5:4': '5:4',
            '1.88': '1.88',
            '2.35': '2.35'
        }

        AspectRatioCmdString = '\r*asp={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = '\r*asp=?#\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '4:3': '4:3',
            '16:9': '16:9',
            '16:10': '16:10',
            'auto': 'Auto',
            'real': 'Real',
            'thea': 'Theater Scope',
            '5:4': '5:4',
            '1.88': '1.88',
            '2.35': '2.35'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '\r*auto#\r'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        FreezeCmdString = '\r*freeze={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '\r*freeze=?#\r'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1/YPbPr': 'RGB',
            'Computer 2/YPbPr': 'RGB2',
            'DVI-D': 'dvid',
            'HDMI': 'hdmi',
            'DisplayPort': 'dp',
            '3G-SDI': 'sdi',
            'HDBaseT': 'hdbaset'
        }

        InputCmdString = '\r*sour={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\r*sour=?#\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'rgb': 'Computer 1/YPbPr',
            'rgb2': 'Computer 2/YPbPr',
            'dvid': 'DVI-D',
            'hdmi': 'HDMI',
            'dp': 'DisplayPort',
            'sdi': '3G-SDI',
            'hdbaset': 'HDBaseT'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Input', value, None)

    def SetLaserMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'lnor',
            'Eco': 'eco',
            'Custom': 'cust'
        }

        LaserModeCmdString = '\r*lampm={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def UpdateLaserMode(self, value, qualifier):

        LaserModeCmdString = '\r*lampm=?#\r'
        self.__UpdateHelper('LaserMode', LaserModeCmdString, value, qualifier)

    def __MatchLaserMode(self, match, tag):

        ValueStateValues = {
            'lnor': 'Normal',
            'eco': 'Eco',
            'cust': 'Custom'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('LaserMode', value, None)

    def UpdateLaserUsage(self, value, qualifier):

        LaserUsageCmdString = '\r*lsrtim=?#\r'
        self.__UpdateHelper('LaserUsage', LaserUsageCmdString, value, qualifier)

    def __MatchLaserUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LaserUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu On': 'menu=on',
            'Menu Off': 'menu=off',
            'Up': 'up',
            'Down': 'down',
            'Right': 'right',
            'Left': 'left',
            'Enter': 'enter'
        }

        MenuNavigationCmdString = '\r*{}#\r'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Bright': 'bright',
            'Presentation': 'preseT',
            'Cinema': 'cine'
        }

        PictureModeCmdString = '\r*appmod={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = '\r*appmod=?#\r'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            'bright': 'Bright',
            'preset': 'Presentation',
            'cine': 'Cinema'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'Computer 1/YPbPr': 'RGB',
            'Computer 2/YPbPr': 'RGB2',
            'DVI-D': 'dvid',
            'HDMI': 'hdmi',
            'DisplayPort': 'dp',
            '3G-SDI': 'sdi',
            'HDBaseT': 'hdbaset'
        }

        PIPInputCmdString = '\r*psour={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '\r*psour=?#\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        ValueStateValues = {
            'rgb': 'Computer 1/YPbPr',
            'rgb2': 'Computer 2/YPbPr',
            'dvid': 'DVI-D',
            'hdmi': 'HDMI',
            'dp': 'DisplayPort',
            'sdi': '3G-SDI',
            'hdbaset': 'HDBaseT'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        PIPModeCmdString = '\r*pip={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = '\r*pip=?#\r'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': 'tl',
            'Top Right': 'tr',
            'Bottom Left': 'bl',
            'Bottom Right': 'br',
            'PBP': 'pbp'
        }

        PIPPositionCmdString = '\r*pippos={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = '\r*pippos=?#\r'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            'tl': 'Top Left',
            'tr': 'Top Right',
            'bl': 'Bottom Left',
            'br': 'Bottom Right',
            'pbp': 'PBP'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        PowerCmdString = '\r*pow={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '\r*pow=?#\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        VideoMuteCmdString = '\r*blank={}#\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '\r*blank=?#\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('VideoMute', value, None)

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

        value = match.group(0).decode()
        self.Error([value])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
