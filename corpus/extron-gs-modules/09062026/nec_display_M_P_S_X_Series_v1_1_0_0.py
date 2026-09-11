from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack
from binascii import hexlify


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._DeviceID = 1
        self.Models = {
            'S401': self.nec_10_3166_normal,
            'S461': self.nec_10_3166_normal,
            'S521': self.nec_10_3166_normal,
            'M401': self.nec_10_3166_normal,
            'M521': self.nec_10_3166_normal,
            'P401': self.nec_10_3166_normal,
            'P461': self.nec_10_3166_normal,
            'P521': self.nec_10_3166_normal,
            'P701': self.nec_10_3166_normal,
            'X431BT': self.nec_10_3166_X431,
            'X461HB': self.nec_10_3166_normal,
            'X461UN': self.nec_10_3166_normal,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'ChannelStep': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixComp': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixHMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixMode': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixPosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixVMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self.groupID = {
            'Broadcast': 0x2A,
            'Group A': 0x31,
            'Group B': 0x32,
            'Group C': 0x33,
            'Group D': 0x34,
            'Group E': 0x35,
            'Group F': 0x36,
            'Group G': 0x37,
            'Group H': 0x38,
            'Group I': 0x39,
            'Group J': 0x3A,
        }

    def SetQualifierDeviceID(self, value):
        if value in self.groupID:
            return self.groupID[value]
        elif 1 <= int(value) <= 100:
            return 0x40 + int(value)
        else:
            return False

    def checkSumCalc(self, deviceID, cmdStr):
        checkSumStr = b'\x30' + bytes([deviceID]) + cmdStr + b'\x03'
        checksum = 0
        for i in checkSumStr:
            checksum ^= i
        return b'\x01' + checkSumStr + pack('>B', checksum) + b'\x0D'

    def SetAspectRatio(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            AspectRatioCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30' + self.SetAspectState[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            AspectRatioCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x30')
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = self.GetAspectState[res[23:24]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'On': b'\x31',
                'Off': b'\x32'
            }

            AudioMuteCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                b'\x31': 'On',
                b'\x32': 'Off'
            }

            AudioMuteCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x30\x38\x44')
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            AutoImageCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x30\x31\x45\x30\x30\x30\x31')
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetChannelStep(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'Up': b'\x31',
                'Down': b'\x32'
            }

            ChannelStepCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetInput(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'VGA': b'\x30\x31',
                'RGB/HV': b'\x30\x32',
                'DVI': b'\x30\x33',
                'Video 1': b'\x30\x35',
                'Video 2': b'\x30\x36',
                'S-Video': b'\x30\x37',
                'TV': b'\x30\x41',
                'DVD/HD1': b'\x30\x43',
                'Option': b'\x30\x44',
                'DVD/HD2': b'\x30\x45',
                'DisplayPort': b'\x30\x46',
                'HDMI': b'\x31\x31'
            }

            InputCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                b'\x30\x31': 'VGA',
                b'\x30\x32': 'RGB/HV',
                b'\x30\x33': 'DVI',
                b'\x30\x35': 'Video 1',
                b'\x30\x36': 'Video 2',
                b'\x30\x37': 'S-Video',
                b'\x30\x41': 'TV',
                b'\x30\x43': 'DVD/HD1',
                b'\x30\x44': 'Option',
                b'\x30\x45': 'DVD/HD2',
                b'\x30\x46': 'DisplayPort',
                b'\x31\x31': 'HDMI'
            }

            InputCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x30\x36\x30')
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetPictureMode(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'sRGB': b'\x31',
                'Hi-Bright': b'\x33',
                'Standard': b'\x34',
                'Cinema': b'\x35',
                'ISF-Day': b'\x36',
                'ISF-Night': b'\x37',
                'Ambient-1': b'\x42',
                'Ambient-2': b'\x43'
            }

            PictureModeCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x31\x41\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                b'\x31': 'sRGB',
                b'\x33': 'Hi-Bright',
                b'\x34': 'Standard',
                b'\x35': 'Cinema',
                b'\x36': 'ISF-Day',
                b'\x37': 'ISF-Night',
                b'\x42': 'Ambient-1',
                b'\x43': 'Ambient-2'
            }

            PictureModeCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x32\x31\x41')
            res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('PictureMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureMode')

    def SetPIPInput(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'VGA': b'\x30\x31',
                'RGB/HV': b'\x30\x32',
                'DVI': b'\x30\x33',
                'Video 1': b'\x30\x35',
                'Video 2': b'\x30\x36',
                'S-Video': b'\x30\x37',
                'TV': b'\x30\x41',
                'DVD/HD1': b'\x30\x43',
                'Option': b'\x30\x44',
                'DVD/HD2': b'\x30\x45',
                'DisplayPort': b'\x30\x46',
                'HDMI': b'\x31\x31'
            }

            PIPInputCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x37\x33\x30\x30' + ValueStateValues[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                b'\x30\x31': 'VGA',
                b'\x30\x32': 'RGB/HV',
                b'\x30\x33': 'DVI',
                b'\x30\x35': 'Video 1',
                b'\x30\x36': 'Video 2',
                b'\x30\x37': 'S-Video',
                b'\x30\x41': 'TV',
                b'\x30\x43': 'DVD/HD1',
                b'\x30\x44': 'Option',
                b'\x30\x45': 'DVD/HD2',
                b'\x30\x46': 'DisplayPort',
                b'\x31\x31': 'HDMI'
            }

            PIPInputCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x33')
            res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('PIPInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            PIPModeCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x37\x32\x30\x30\x30' + self.SetPIPModeState[value])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            PIPModeCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x32')
            res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
            if res:
                try:
                    value = self.GetPIPModeState[res[23:24]]
                    self.WriteStatus('PIPMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePIPMode')

    def SetPIPSize(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'Small': b'\x31',
                'Middle': b'\x32',
                'Large': b'\x33'
            }

            PIPSizeCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x37\x31\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                b'\x31': 'Small',
                b'\x32': 'Middle',
                b'\x33': 'Large'
            }

            PIPSizeCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x32\x37\x31')
            res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('PIPSize', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Size: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'On': b'\x31',
                'Off': b'\x34'
            }

            PowerCmdString = self.checkSumCalc(deviceID, b'\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                b'\x31': 'On',
                b'\x32': 'Stand-by',
                b'\x33': 'Suspend',
                b'\x34': 'Off'
            }

            PowerCmdString = self.checkSumCalc(deviceID, b'\x30\x41\x30\x36\x02\x30\x31\x44\x36')
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetTileMatrixComp(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'Enable': b'\x32',
                'Disable': b'\x31'
            }

            TileMatrixCompCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x44\x35\x30\x30\x30' + ValueStateValues[value])
            self.__SetHelper('TileMatrixComp', TileMatrixCompCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixComp')

    def SetTileMatrixHMonitor(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if 1 <= int(value) <= 10 and deviceID != 0:
            TileMatrixHMonitorCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x44\x30\x30\x30' + hexlify(int(value).to_bytes(1, 'big')).upper())
            self.__SetHelper('TileMatrixHMonitor', TileMatrixHMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixHMonitor')

    def SetTileMatrixMode(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            ValueStateValues = {
                'Disable and Display Frame': b'\x31',
                'Enable': b'\x32',
                'Disable and Erase Frame': b'\x33'
            }

            TileMatrixModeCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x44\x33\x30\x30\x30' + ValueStateValues[value])


            self.__SetHelper('TileMatrixMode', TileMatrixModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixMode')

    def SetTileMatrixPosition(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if 1 <= int(value) <= 100 and deviceID != 0:
            TileMatrixPositionCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x44\x32\x30\x30' + hexlify(int(value).to_bytes(1, 'big')).upper())
            self.__SetHelper('TileMatrixPosition', TileMatrixPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixPosition')

    def SetTileMatrixVMonitor(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if 1 <= int(value) <= 10 and deviceID != 0:
            TileMatrixVMonitorCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x32\x44\x31\x30\x30' + hexlify(int(value).to_bytes(1, 'big')).upper())
            self.__SetHelper('TileMatrixVMonitor', TileMatrixVMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixVMonitor')

    def SetVolume(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if 0 <= value <= 100 and deviceID != 0:
            VolumeCmdString = self.checkSumCalc(deviceID, b'\x30\x45\x30\x41\x02\x30\x30\x36\x32\x30\x30' + hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        deviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if deviceID != 0:
            VolumeCmdString = self.checkSumCalc(deviceID, b'\x30\x43\x30\x36\x02\x30\x30\x36\x32')
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and response[8:10].decode() == '01':
            self.Error(['{0}: An error occurred.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast' or 'Group' in qualifier['Device ID']:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast' or 'Group' in qualifier['Device ID']:
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
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def nec_10_3166_normal(self):
        self.SetAspectState = {
            'Normal': b'\x31',
            'Full': b'\x32',
            'Wide': b'\x33',
            'Zoom': b'\x34'
        }

        self.GetAspectState = {
            b'\x31': 'Normal',
            b'\x32': 'Full',
            b'\x33': 'Wide',
            b'\x34': 'Zoom'
        }

        self.SetPIPModeState = {
            'Off': b'\x31',
            'PIP': b'\x32',
            'POP': b'\x33',
            'Still': b'\x34',
            'Side by Side (Aspect)': b'\x35',
            'Side by Side (Full)': b'\x36'
        }

        self.GetPIPModeState = {
            b'\x31': 'Off',
            b'\x32': 'PIP',
            b'\x33': 'POP',
            b'\x34': 'Still',
            b'\x35': 'Side by Side (Aspect)',
            b'\x36': 'Side by Side (Full)'
        }

    def nec_10_3166_X431(self):
        self.SetAspectState = {
            'Normal': b'\x31',
            'Full': b'\x32',
            'Zoom': b'\x34',
            'Trim': b'\x35'
        }

        self.GetAspectState = {
            b'\x31': 'Normal',
            b'\x32': 'Full',
            b'\x34': 'Zoom',
            b'\x35': 'Trim'
        }

        self.SetPIPModeState = {
            'Off': b'\x31',
            'PIP': b'\x32',
            'POP': b'\x33',
            'Still': b'\x34',
            'Side by Side (Full)': b'\x36',
            'POP (Aspect Main)': b'\x37',
            'POP (Aspect Sub)': b'\x38'
        }

        self.GetPIPModeState = {
            b'\x31': 'Off',
            b'\x32': 'PIP',
            b'\x33': 'POP',
            b'\x34': 'Still',
            b'\x36': 'Side by Side (Full)',
            b'\x37': 'POP (Aspect Main)',
            b'\x38': 'POP (Aspect Sub)'
        }

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
