from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.Models = {
            'PowerLite 1930': self.epsn_1_278_0X,
            'PowerLite 1940W': self.epsn_1_278_0W,
            'PowerLite 1945W': self.epsn_1_278_5W,
            'PowerLite 1950': self.epsn_1_278_0X,
            'PowerLite 1955': self.epsn_1_278_5X,
            'PowerLite 1960': self.epsn_1_278_0X,
            'PowerLite 1965': self.epsn_1_278_5X,
            'EB-1930': self.epsn_1_278_0X,
            'EB-1940W': self.epsn_1_278_0W,
            'EB-1945W': self.epsn_1_278_5W,
            'EB-1950': self.epsn_1_278_0X,
            'EB-1955': self.epsn_1_278_5X,
            'EB-1960': self.epsn_1_278_0X,
            'EB-1965': self.epsn_1_278_5X,
            'EB-C740W': self.epsn_1_278_0W,
            'EB-C755XN': self.epsn_1_278_5X,
            'EB-C764XN': self.epsn_1_278_4X,
            'EB-C754XN': self.epsn_1_278_4X,
            'EB-C750X': self.epsn_1_278_0X,
            'EB-C745XN': self.epsn_1_278_5X,
            'EB-C740X': self.epsn_1_278_0X,
            'EB-501KG': self.epsn_1_278_0X,
            'EB-451KG': self.epsn_1_278_5X,
            'EB-C745WN': self.epsn_1_278_5W,
            'EB-C765XN': self.epsn_1_278_5X,
            'EB-C760X': self.epsn_1_278_0X,
            'EB-1964': self.epsn_1_278_4X,
            'PowerLite 1964': self.epsn_1_278_4X,
            'EB-1954': self.epsn_1_278_4X,
            'EB-1935': self.epsn_1_278_5X,
            'PowerLite 1935': self.epsn_1_278_5X,
            'PowerLite 1954': self.epsn_1_278_4X,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AVMute': { 'Status': {}},
            'ClosedCaption': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT=([0-6])0\r:'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'MUTE=(ON|OFF)\r:'), self.__MatchAVMute, None)
            self.AddMatchString(re.compile(b'CCAP=(00|1[1-2])\r:'), self.__MatchClosedCaption, None)
            self.AddMatchString(re.compile(b'ERR=([0-1][0-9A-F])\r:'), self.__MatchDeviceStatus, None) # only for serial connection
            self.AddMatchString(re.compile(b'ERR\r:'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'FREEZE=(ON|OFF)\r:'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'SOURCE=(11|14|1F|21|24|2F|30|41|51|52|53|54|70)\r:'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'LUMINANCE=(00|01)\r:'), self.__MatchLampMode, None)
            self.AddMatchString(re.compile(b'LAMP=([0-9]{1,5})\r:'), self.__MatchLampUsage, None)
            self.AddMatchString(re.compile(b'PWR=(0[0-5])\r:'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'VOL=([0-9]{1,3})\r:'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        CommandString = 'ASPECT {0}0\r'.format(self.AspectRatioValues[value])
        self.__SetHelper('AspectRatio', CommandString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CommandString = 'ASPECT?\r'
        self.__UpdateHelper('AspectRatio', CommandString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        value = self.AspectRatioStates[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        CommandString = 'KEY 4A\r'
        self.__SetHelper('AutoImage', CommandString, value, qualifier)
    def SetAVMute(self, value, qualifier):

        AVMuteControls = {
                            'On' : 'ON',
                            'Off': 'OFF'
                         }

        CommandString = 'MUTE {0}\r'.format(AVMuteControls[value])
        self.__SetHelper('AVMute', CommandString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        CommandString = 'MUTE?\r'
        self.__UpdateHelper('AVMute', CommandString, value, qualifier)

    def __MatchAVMute(self, match, tag):

        AVMuteNames = {
                        'ON' : 'On',
                        'OFF': 'Off'
                    }

        value = AVMuteNames[match.group(1).decode()]
        self.WriteStatus('AVMute', value, None)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionControls = {
                                  'CC1' : '11',
                                  'CC2' : '12',
                                  'Off' : '00'
                                }

        CommandString = 'CCAP {0}\r'.format(ClosedCaptionControls[value])
        self.__SetHelper('ClosedCaption', CommandString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        CommandString = 'CCAP?\r'
        self.__UpdateHelper('ClosedCaption', CommandString, value, qualifier)

    def __MatchClosedCaption(self, match, tag):

        ClosedCaptionNames = {
                               '11' : 'CC1',
                               '12' : 'CC2',
                               '00' : 'Off'
                             }

        value = ClosedCaptionNames[match.group(1).decode()]
        self.WriteStatus('ClosedCaption', value, None)

    def UpdateDeviceStatus(self, value, qualifier):

        CommandString = 'ERR?\r'
        self.__UpdateHelper('DeviceStatus', CommandString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        DeviceStatusNames = {
                              '00' : 'Normal',
                              '01' : 'Fan error',
                              '03' : 'Lamp failure at power on',
                              '04' : 'High internal temperature error',
                              '06' : 'Lamp error',
                              '07' : 'Open lamp cover door error',
                              '08' : 'Cinema filter error',
                              '09' : 'Electric dual-layered capacitor is disconnected',
                              '0A' : 'Auto iris error',
                              '0B' : 'Subsystem error',
                              '0C' : 'Low air flow error',
                              '0D' : 'Air filter air flow sensor error',
                              '0E' : 'Power supply unit error (Ballast)',
                              '0F' : 'Shutter error',
                              '10' : 'Cooling system error (peltiert element)',
                              '11' : 'Cooling system error (pump)',
                              '12' : 'Static iris error',
                              '13' : 'Power supply unit error (Disagreement of Ballast)',
                              '14' : 'Exhaust shutter error',
                              '15' : 'Obstacle detection error',
                              '16' : 'IF board discernment error'

                            }

        value = DeviceStatusNames[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeControls = {
                           'On' : 'ON',
                           'Off': 'OFF'
                         }

        CommandString = 'FREEZE {0}\r'.format(FreezeControls[value])
        self.__SetHelper('Freeze', CommandString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        CommandString = 'FREEZE?\r'
        self.__UpdateHelper('Freeze', CommandString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeNames = {
                        'ON' : 'On',
                        'OFF' : 'Off'
                      }

        value = FreezeNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetInput(self, value, qualifier):


        CommandString = 'SOURCE {0}\r'.format(self.InputValues[value])
        self.__SetHelper('Input', CommandString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CommandString = 'SOURCE?\r'
        self.__UpdateHelper('Input', CommandString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = self.InputStates[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetLampMode(self, value, qualifier):

        LampModeControls = {
                             'Normal'   : '00',
                             'Eco'      : '01'
                           }

        CommandString = 'LUMINANCE {0}\r'.format(LampModeControls[value])
        self.__SetHelper('LampMode', CommandString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        CommandString = 'LUMINANCE?\r'
        self.__UpdateHelper('LampMode', CommandString, value, qualifier)

    def __MatchLampMode(self, match, tag):

        LampModeNames = {
                          '00' : 'Normal',
                          '01' : 'Eco'
                        }

        value = LampModeNames[match.group(1).decode()]
        self.WriteStatus('LampMode', value, None)

    def UpdateLampUsage(self, value, qualifier):

        CommandString = 'LAMP?\r'
        self.__UpdateHelper('LampUsage', CommandString, value, qualifier)

    def __MatchLampUsage(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('LampUsage', value, None)

    def SetMenuNavigation(self, value, qualifier):

        MenuControls = {
                         'Up'   : '35',
                         'Down' : '36',
                         'Left' : '37',
                         'Right': '38',
                         'Menu' : '03',
                         'Enter': '16',
                         'ESC'  : '05'
                       }

        CommandString = 'KEY {0}\r'.format(MenuControls[value])
        self.__SetHelper('MenuNavigation', CommandString, value, qualifier)
    def SetPower(self, value, qualifier):

        PowerControls = {
                          'On'  : 'ON',
                          'Off' : 'OFF'
                        }

        CommandString = 'PWR {0}\r'.format(PowerControls[value])
        self.__SetHelper('Power', CommandString, value, qualifier)

    def UpdatePower(self, value, qualifier):


        CommandString = 'PWR?\r'
        self.__UpdateHelper('Power', CommandString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerNames = {
                       '00' : 'Off',
                       '01' : 'On',
                       '02' : 'Warming Up',
                       '03' : 'Cooling Down',
                       '04' : 'Off',
                       '05' : 'Abnormal Standby'
                     }

        value = PowerNames[match.group(1).decode()]
        self.WriteStatus('Power', value, None)


    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
                             'Min' : 0,
                             'Max' : 20
                            }
        VolumeTable = {
                        0 : 0,
                        1 : 12,
                        2 : 24,
                        3 : 36,
                        4 : 48,
                        5 : 60,
                        6 : 73,
                        7 : 85,
                        8 : 97,
                        9 : 109,
                        10 : 121,
                        11 : 134,
                        12 : 146,
                        13 : 158,
                        14 : 170,
                        15 : 182,
                        16 : 195,
                        17 : 207,
                        18 : 219,
                        19 : 231,
                        20 : 243
                      }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'VOL {0}\r'.format(VolumeTable[value])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'VOL?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(int(match.group(1))/12)
        self.WriteStatus('Volume', value, None)

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
        self.counter = 0

        self.Error(['An error occurred'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def epsn_1_278_0W(self):

        self.InputValues = {
            'Computer 1 (Auto)'      : '1F',
            'Computer 1 (RGB)'       : '11',
            'Computer 1 (Component)' : '14',
            'Computer 2 (Auto)'      : '2F',
            'Computer 2 (RGB)'       : '21',
            'Computer 2 (Component)' : '24',
            'HDMI'                   : '30',
            'Video'                  : '41',
            'USB Display'            : '51',
            'USB'                    : '52',
            'LAN'                    : '53',
            'DisplayPort'            : '70'
        }
        self.InputStates = {
            '1F' :  'Computer 1 (Auto)',
            '11' :  'Computer 1 (RGB)',
            '14' :  'Computer 1 (Component)',
            '2F' :  'Computer 2 (Auto)',
            '21' :  'Computer 2 (RGB)',
            '24' :  'Computer 2 (Component)',
            '30' :  'HDMI',
            '41' :  'Video',
            '51' :  'USB Display',
            '52' :  'USB',
            '53' :  'LAN',
            '70' :  'DisplayPort'
        }

        self.AspectRatioValues = {
            'Normal' : '0',
            '16:9'   : '2',
            'Full'   : '4',
            'Zoom'   : '5',
            'Native' : '6',
            'Auto'   : '3',
        }
        self.AspectRatioStates = {
            '0' : 'Normal',
            '2' : '16:9',
            '4' : 'Full',
            '5' : 'Zoom',
            '6' : 'Native',
            '3' : 'Auto'
        }



    def epsn_1_278_0X(self):

        self.InputValues = {
            'Computer 1 (Auto)'      : '1F',
            'Computer 1 (RGB)'       : '11',
            'Computer 1 (Component)' : '14',
            'Computer 2 (Auto)'      : '2F',
            'Computer 2 (RGB)'       : '21',
            'Computer 2 (Component)' : '24',
            'HDMI'                   : '30',
            'Video'                  : '41',
            'USB Display'            : '51',
            'USB'                    : '52',
            'LAN'                    : '53',
            'DisplayPort'            : '70'
        }
        self.InputStates = {
            '1F' :  'Computer 1 (Auto)',
            '11' :  'Computer 1 (RGB)',
            '14' :  'Computer 1 (Component)',
            '2F' :  'Computer 2 (Auto)',
            '21' :  'Computer 2 (RGB)',
            '24' :  'Computer 2 (Component)',
            '30' :  'HDMI',
            '41' :  'Video',
            '51' :  'USB Display',
            '52' :  'USB',
            '53' :  'LAN',
            '70' :  'DisplayPort'
        }

        self.AspectRatioValues = {
            'Normal' : '0',
            '4:3'    : '1',
            '16:9'   : '2',
            'Auto'   : '3',
        }
        self.AspectRatioStates = {
            '0' : 'Normal',
            '1' : '4:3',
            '2' : '16:9',
            '3' : 'Auto'
        }



    def epsn_1_278_4W(self):

        self.InputValues = {
            'Computer 1 (Auto)'      : '1F',
            'Computer 1 (RGB)'       : '11',
            'Computer 1 (Component)' : '14',
            'Computer 2 (Auto)'      : '2F',
            'Computer 2 (RGB)'       : '21',
            'Computer 2 (Component)' : '24',
            'HDMI'                   : '30',
            'Video'                  : '41',
            'USB Display'            : '51',
            'USB 1'                  : '52',
            'USB 2'                  : '54',
            'LAN'                    : '53'
        }
        self.InputStates = {
            '1F' :  'Computer 1 (Auto)',
            '11' :  'Computer 1 (RGB)',
            '14' :  'Computer 1 (Component)',
            '2F' :  'Computer 2 (Auto)',
            '21' :  'Computer 2 (RGB)',
            '24' :  'Computer 2 (Component)',
            '30' :  'HDMI',
            '41' :  'Video',
            '51' :  'USB Display',
            '52' :  'USB 1',
            '54' :  'USB 2',
            '53' :  'LAN'
        }

        self.AspectRatioValues = {
            'Normal' : '0',
            '16:9'   : '2',
            'Full'   : '4',
            'Zoom'   : '5',
            'Native' : '6',
            'Auto'   : '3',
        }
        self.AspectRatioStates = {
            '0' : 'Normal',
            '2' : '16:9',
            '4' : 'Full',
            '5' : 'Zoom',
            '6' : 'Native',
            '3' : 'Auto'
        }



    def epsn_1_278_4X(self):

        self.InputValues = {
            'Computer 1 (Auto)'      : '1F',
            'Computer 1 (RGB)'       : '11',
            'Computer 1 (Component)' : '14',
            'Computer 2 (Auto)'      : '2F',
            'Computer 2 (RGB)'       : '21',
            'Computer 2 (Component)' : '24',
            'HDMI'                   : '30',
            'Video'                  : '41',
            'USB Display'            : '51',
            'USB 1'                  : '52',
            'USB 2'                  : '54',
            'LAN'                    : '53'
        }
        self.InputStates = {
            '1F' :  'Computer 1 (Auto)',
            '11' :  'Computer 1 (RGB)',
            '14' :  'Computer 1 (Component)',
            '2F' :  'Computer 2 (Auto)',
            '21' :  'Computer 2 (RGB)',
            '24' :  'Computer 2 (Component)',
            '30' :  'HDMI',
            '41' :  'Video',
            '51' :  'USB Display',
            '52' :  'USB 1',
            '54' :  'USB 2',
            '53' :  'LAN'
        }

        self.AspectRatioValues = {
            'Normal' : '0',
            '4:3'    : '1',
            '16:9'   : '2',
            'Auto'   : '3',
        }
        self.AspectRatioStates = {
            '0' : 'Normal',
            '1' : '4:3',
            '2' : '16:9',
            '3' : 'Auto'
        }



    def epsn_1_278_5W(self):

        self.InputValues = {
            'Computer 1 (Auto)'      : '1F',
            'Computer 1 (RGB)'       : '11',
            'Computer 1 (Component)' : '14',
            'Computer 2 (Auto)'      : '2F',
            'Computer 2 (RGB)'       : '21',
            'Computer 2 (Component)' : '24',
            'HDMI'                   : '30',
            'Video'                  : '41',
            'USB Display'            : '51',
            'USB 1'                  : '52',
            'USB 2'                  : '54',
            'LAN'                    : '53',
            'DisplayPort'            : '70'
        }
        self.InputStates = {
            '1F' :  'Computer 1 (Auto)',
            '11' :  'Computer 1 (RGB)',
            '14' :  'Computer 1 (Component)',
            '2F' :  'Computer 2 (Auto)',
            '21' :  'Computer 2 (RGB)',
            '24' :  'Computer 2 (Component)',
            '30' :  'HDMI',
            '41' :  'Video',
            '51' :  'USB Display',
            '52' :  'USB 1',
            '54' :  'USB 2',
            '53' :  'LAN',
            '70' :  'DisplayPort'
        }

        self.AspectRatioValues = {
            'Normal' : '0',
            '16:9'   : '2',
            'Full'   : '4',
            'Zoom'   : '5',
            'Native' : '6',
            'Auto'   : '3',
        }
        self.AspectRatioStates = {
            '0' : 'Normal',
            '2' : '16:9',
            '4' : 'Full',
            '5' : 'Zoom',
            '6' : 'Native',
            '3' : 'Auto'
        }



    def epsn_1_278_5X(self):

        self.InputValues = {
            'Computer 1 (Auto)'      : '1F',
            'Computer 1 (RGB)'       : '11',
            'Computer 1 (Component)' : '14',
            'Computer 2 (Auto)'      : '2F',
            'Computer 2 (RGB)'       : '21',
            'Computer 2 (Component)' : '24',
            'HDMI'                   : '30',
            'Video'                  : '41',
            'USB Display'            : '51',
            'USB 1'                  : '52',
            'USB 2'                  : '54',
            'LAN'                    : '53',
            'DisplayPort'            : '70'
        }
        self.InputStates = {
            '1F' :  'Computer 1 (Auto)',
            '11' :  'Computer 1 (RGB)',
            '14' :  'Computer 1 (Component)',
            '2F' :  'Computer 2 (Auto)',
            '21' :  'Computer 2 (RGB)',
            '24' :  'Computer 2 (Component)',
            '30' :  'HDMI',
            '41' :  'Video',
            '51' :  'USB Display',
            '52' :  'USB 1',
            '54' :  'USB 2',
            '53' :  'LAN',
            '70' :  'DisplayPort'
        }

        self.AspectRatioValues = {
            'Normal' : '0',
            '4:3'    : '1',
            '16:9'   : '2',
            'Auto'   : '3',
        }
        self.AspectRatioStates = {
            '0' : 'Normal',
            '1' : '4:3',
            '2' : '16:9',
            '3' : 'Auto'
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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'ESC/VP.net\x10\x03\x00\x00\x00\x00')
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
