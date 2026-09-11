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
        self.Models = {}
        self.Debug = False

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AssignID': {'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'BezelAdjust': {'Parameters': ['Device ID', 'Bezel'], 'Status': {}},
            'BezelWidth': {'Parameters': ['Device ID', 'Side'], 'Status': {}},
            'BlackLevel': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'Colors': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'Enlarge': {'Parameters': ['Device ID'], 'Status': {}},
            'IDCheck': {'Status': {}},
            'ImageLocation': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureInPicture': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPInput': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPSize': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'Sharpness': {'Parameters': ['Device ID'], 'Status': {}},
            'Tint': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
        }

        self.IDSent = False

        self.Callback = None
        self.valueCallback = None
        self.qualifierCallback = None
        self.ExpiryTime = 0
        self.SelectedID = '0'

        self.SetRegex = compile(b'OK \d{3}\r\n|ERR\r\n')
        self.UpdateRegex = compile(b'\d{1,3} \d{3}\r\n|ERR\r\n')

    def DeviceIDHandler(self, Callback, value, qualifier):

        if qualifier['Device ID'] == 'Broadcast':
            qualifier['Device ID'] = '0'
            if 'Update' in Callback:
                print('Invalid Command')
                return False

        self.Callback = Callback
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
            getattr(self, self.Callback)(self.valueCallback, self.qualifierCallback)

    def SetIDLK(self, CmdString, qualifier):

        self.ExpiryTime = time.monotonic() + 5
        self.Send(CmdString)
        if self.qualifierCallback['Device ID'] == '0':
            self.SelectedID = '0'
        self.IDLK_Callback()

    def __MatchDeviceOK(self, match, tag):

        self.SelectedID = str(int(match.group(2).decode()))

    def SetAspectRatio(self, value, qualifier):

        InputClass = {
            'DVI-D PC': 'PC',
            'D-SUB': 'PC',
            'HDMI PC': 'PC',
            'Component': 'AV',
            'Video': 'AV',
            'DVI-D AV': 'AV',
            'S-Video': 'AV',
            'HDMI AV': 'AV',
        }

        InputVal = qualifier['Input']

        States = {
            'PC': {
                'Normal': 2,
                'Wide'	: 1,
                'Dot by Dot': 3,
                'Zoom 1'	: 4,
                'Zoom 2'	: 5,
            },
            'AV' : {
                'Normal'	: 4,
                'Wide'		: 1,
                'Dot by Dot': 5,
                'Zoom 1'	: 2,
                'Zoom 2'	: 3,
            },
        }
        if InputVal:
            CmdString = 'WIDE{0: 4}\r\n'.format(States[ InputClass[InputVal] ][value])
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        InputClass = {
            'DVI-D PC'  : 'PC',
            'D-SUB'     : 'PC',
            'HDMI PC'   : 'PC',
            'Component' : 'AV',
            'Video'     : 'AV',
            'DVI-D AV'  : 'AV',
            'S-Video'   : 'AV',
            'HDMI AV'   : 'AV',
        }

        InputVal = qualifier['Input']

        States = {
            'PC' : {
                2   :  'Normal',
                1   :  'Wide',
                3   :  'Dot by Dot',
                4   :  'Zoom 1',
                5   :  'Zoom 2',
            },
            'AV' : {
                4   :  'Normal',
                1   :  'Wide',
                5   :  'Dot by Dot',
                2   :  'Zoom 1',
                3   :  'Zoom 2',
            },
        }
        if InputVal and self.DeviceIDHandler('UpdateAspectRatio', value, qualifier):
            res = self.__UpdateHelper('AspectRatio', 'WIDE????\r\n', value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('AspectRatio',  States[ InputClass[InputVal] ][int(res[0])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        States = {
            'On' : 1,
            'Off' : 0,
        }

        CmdString = 'MUTE{0: 4}\r\n'.format(States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            1	: 'On',
            0	: 'Off'
        }

        if self.DeviceIDHandler('UpdateAudioMute', value, qualifier):
            res = self.__UpdateHelper('AudioMute', 'MUTE????\r\n', value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('AudioMute',  States[int(res[0])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', b'AGIN0001\r\n', value, qualifier)

    def SetEnlarge(self, value, qualifier):

        States = {
            '2x2' : 1,
            '3x3' : 2,
            '4x4' : 3,
            '5x5' : 4,
            'Off' : 0,
        }
        CmdString = 'EMAG{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Enlarge', CmdString, value, qualifier)

    def UpdateEnlarge(self, value, qualifier):

        States = {
            1	:	'2x2',
            2	:	'3x3',
            3	:	'4x4',
            4	:	'5x5',
            0	:	'Off',
        }

        if self.DeviceIDHandler('UpdateEnlarge', value, qualifier):
            res = self.__UpdateHelper('Enlarge', 'EMAG????\r\n', value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('Enlarge',  States[int(res[0])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateEnlarge')

    def SetImageLocation(self, value, qualifier):

        States = {
            '1x1' : 11,'1x2' : 12,'1x3' : 13,'1x4' : 14,'1x5' : 15,
            '2x1' : 21,'2x2' : 22,'2x3' : 23,'2x4' : 24,'2x5' : 25,
            '3x1' : 31,'3x2' : 32,'3x3' : 33,'3x4' : 34,'3x5' : 35,
            '4x1' : 41,'4x2' : 42,'4x3' : 43,'4x4' : 44,'4x5' : 45,
            '5x1' : 51,'5x2' : 52,'5x3' : 53,'5x4' : 54,'5x5' : 55
        }

        CmdString = 'EPHV{0: 4}\r\n'.format(States[value])
        self.__SetHelper('ImageLocation', CmdString, value, qualifier)

    def UpdateImageLocation(self, value, qualifier):

        States = {
            11  : '1x1', 12	: '1x2',13 : '1x3',14   : '1x4',15 :    '1x5',
            21	: '2x1', 22	: '2x2',23 : '2x3',24	: '2x4',25 :	'2x5',
            31	: '3x1', 32	: '3x2',33 : '3x3',34	: '3x4',35 :	'3x5',
            41	: '4x1', 42	: '4x2',43 : '4x3',44	: '4x4',45 :	'4x5',
            51	: '5x1', 52	: '5x2',53 : '5x3',54	: '5x4',55 :	'5x5'
        }

        if self.DeviceIDHandler('UpdateImageLocation', value, qualifier):
            res = self.__UpdateHelper('ImageLocation', 'EPHV????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('ImageLocation',  States[int(res[0:2])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateImageLocation')

    def SetInput(self, value, qualifier):

        States = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            'DisplayPort'   : 14,
        }

        CmdString = 'INPS{0: 4}\r\n'.format(States[value])

        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            14  :   'DisplayPort',
        }

        if self.DeviceIDHandler('UpdateInput', value, qualifier):
            res = self.__UpdateHelper('Input', b'INPS????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('Input',  States[int(res[0:-6])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateInput')

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On'  : 0,
            'Off' : 1,
            'On2' : 2,
        }

        CmdString = 'LOSD{0: 4}\r\n'.format(States[value])
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        States = {
            0 : 'On',
            1 : 'Off',
            2 : 'On2',
        }

        if self.DeviceIDHandler('UpdateOnScreenDisplay', value, qualifier):
            res = self.__UpdateHelper('OnScreenDisplay', 'LOSD????\r\n', value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('OnScreenDisplay',  States[int(res[0])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPictureInPicture(self, value, qualifier):

        States = {
            'PIP'	: 1,
            'PBP 1'	: 2,
            'PBP 2' : 3,
            'Off'	: 0,
        }

        CmdString = 'MWIN{0: 4}\r\n'.format(States[value])
        self.__SetHelper('PictureInPicture', CmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        States = {
            1 : 'PIP',
            2 : 'PBP 1',
            3 : 'PBP 2',
            0 : 'Off'
        }

        if self.DeviceIDHandler('UpdatePictureInPicture', value, qualifier):
            res = self.__UpdateHelper('PictureInPicture', 'MWIN????\r\n', value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('PictureInPicture',  States[int(res[0])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdatePictureInPicture')

    def SetPIPInput(self, value, qualifier):

        States = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            'DisplayPort'   : 14,
        }

        CmdString = 'MWIP{0: 4}\r\n'.format(States[value])
        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        States = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            14  :   'DisplayPort',
        }

        if self.DeviceIDHandler('UpdatePIPInput', value, qualifier):
            res = self.__UpdateHelper('PIPInput', b'MWIP????\r\n', value, qualifier)
            if res:
                try:
                    self.WriteStatus('PIPInput',  States[int(res[0:-6])] , qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPSize(self, value, qualifier):

        if 1 <= int(value) <= 64:
            CmdString = 'MPSZ{0:>4}\r\n'.format(value)
            self.__SetHelper('PIPSize', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdatePIPSize(self, value, qualifier):

        if self.DeviceIDHandler('UpdatePIPSize', value, qualifier):
            res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n', value, qualifier)
            if res:
                try:
                    value = res[0:-6]
                    self.WriteStatus('PIPSize', value, qualifier)
                except (IndexError, ValueError):
                    print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        States = {
            'On'  : 1,
            'Off' : 0,
        }

        if self.DeviceIDHandler('SetPower', value, qualifier):
            CmdString = 'POWR{0: 4}\r\n'.format(States[value])
            self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Input signal waiting mode',
        }

        if self.DeviceIDHandler('UpdatePower', value, qualifier):
            res = self.__UpdateHelper('Power', 'POWR????\r\n', value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('Power',  States[res[0]] , qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        if self.DeviceIDHandler('UpdateVolume', value, qualifier) :
            res = self.__UpdateHelper('Volume', 'VOLM????\r\n' , value, qualifier)
            if res:
                try:
                    value = int(res[0:2].decode().strip(' '))
                    self.WriteStatus('Volume',  value , qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateVolume')

    def SetAssignID(self, value, qualifier):
        self.__SetHelper('AssignID', 'IDST001+\r\n', value, qualifier)

    def SetIDCheck(self, value, qualifier):
        self.__SetHelper('IDCheck', 'IDCK0000\r\n', value, qualifier)

    def SetContrast(self, value, qualifier):
        if 0 <= value <= 60:
            CmdString = 'CONT{0: 4}\r\n'.format(value)
            self.__SetHelper('Contrast', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateContrast(self, value, qualifier):

        if self.DeviceIDHandler('UpdateContrast', value, qualifier):
            res = self.__UpdateHelper('Contrast', 'CONT????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('Contrast', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateContrast')

    def SetBlackLevel(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'BLVL{0: 4}\r\n'.format(value)
            self.__SetHelper('BlackLevel', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBlackLevel(self, value, qualifier):

        if self.DeviceIDHandler('UpdateBlackLevel', value, qualifier):
            res = self.__UpdateHelper('BlackLevel', 'BLVL????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('BlackLevel', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateBlackLevel')

    def SetTint(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'TINT{0: 4}\r\n'.format(value)
            self.__SetHelper('Tint', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateTint(self, value, qualifier):

        if self.DeviceIDHandler('UpdateTint', value, qualifier):
            res = self.__UpdateHelper('Tint', 'TINT????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('Tint', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateTint')

    def SetColors(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'COLR{0: 4}\r\n'.format(value)
            self.__SetHelper('Colors', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateColors(self, value, qualifier):

        if self.DeviceIDHandler('UpdateColors', value, qualifier):
            res = self.__UpdateHelper('Tint', 'COLR????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('Colors', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateColors')

    def SetSharpness(self, value, qualifier):

        if 0 <= value <= 24:
            CmdString = 'SHRP{0: 4}\r\n'.format(value)
            self.__SetHelper('Sharpness', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateSharpness(self, value, qualifier):

        if self.DeviceIDHandler('UpdateSharpness', value, qualifier):
            res = self.__UpdateHelper('Sharpness', 'SHRP????\r\n', value, qualifier).decode()
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('Sharpness', int(value), qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateSharpness')

    def SetBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO',
            'Top'                   : 'BZCT',
            'Bottom'                : 'BZCB',
            'Right'                 : 'BZCR',
            'Left'                  : 'BZCL'
        }

        Value = {
            'On'  : '1',
            'Off' : '0'
        }

        CmdString = '{0}   {1}\r\n\r\n'.format(Bezel[qualifier['Bezel']], Value[value])
        self.__SetHelper('BezelAdjust', CmdString, value, qualifier)

    def UpdateBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO????\r\n',
            'Top'                   : 'BZCT????\r\n',
            'Bottom'                : 'BZCB????\r\n',
            'Right'                 : 'BZCR????\r\n',
            'Left'                  : 'BZCL????\r\n'
        }

        Values = {
            1: 'On',
            0: 'Off'
        }

        if self.DeviceIDHandler('UpdateBezelAdjust', value, qualifier):
            res = self.__UpdateHelper('BezelAdjust', Bezel[qualifier['Bezel']], value, qualifier).decode()
            if res:
                try:
                    self.WriteStatus('BezelAdjust', Values[int(res[0])], qualifier)
                except (ValueError, KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateBezelAdjust')

    def SetBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV',
            'Short' : 'BEZH'
        }

        if 0 <= value <= 100 and self.DeviceIDHandler('SetBezelWidth', value, qualifier):
            CmdString = '{0}{1:4}\r\n'.format(Sides[qualifier['Side']], value)
            self.__SetHelper('BezelWidth', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV????\r\n',
            'Short' : 'BEZH????\r\n'
        }

        if self.DeviceIDHandler('UpdateBezelWidth', value, qualifier):
            res = self.__UpdateHelper('BezelWidth', Sides[qualifier['Side']], value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('BezelWidth', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateBezelWidth')

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VLMP{0: 4}\r\n'.format(value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBrightness(self, value, qualifier):

        if self.DeviceIDHandler('UpdateBrightness', value, qualifier) :
            res = self.__UpdateHelper('Brightness', 'VLMP????\r\n', value, qualifier)
            if res:
                try:
                    value = int(res[0:-6])
                    self.WriteStatus('Brightness', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateBrightness')

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
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
                self.Subscription[command] = {'method' :{}}

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
            self._compile_list[regex_string] = {'callback': callback, 'para' :arg}


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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'BezelAdjust': {'Parameters': ['Bezel'], 'Status': {}},
            'BezelWidth': {'Parameters': ['Side'],'Status': {}},
            'BlackLevel': {'Status': {}},
            'Brightness': {'Status': {}},
            'Colors': {'Status': {}},
            'Contrast': {'Status': {}},
            'Enlarge': {'Status': {}},
            'ImageLocation': {'Status': {}},
            'Input': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Tint': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.AddMatchString(compile(b'Login:'), self.__MatchUsername, None)
        self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

    def __MatchUsername(self, match, tag):
        self.SetUsername()

    def __MatchPassword(self, match, tag):
        self.SetPassword()

    def SetUsername(self):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        InputClass = {
            'DVI-D PC': 'PC',
            'D-SUB': 'PC',
            'HDMI PC': 'PC',
            'DisplayPort': 'PC',
            'Component': 'AV',
            'Video': 'AV',
            'DVI-D AV': 'AV',
            'HDMI AV': 'AV',
        }

        InputVal = qualifier['Input']

        States = {
            'PC': {
                'Normal': 2,
                'Wide'	: 1,
                'Dot by Dot': 3,
                'Zoom 1'	: 4,
                'Zoom 2'	: 5,
            },
            'AV' : {
                'Normal'	: 4,
                'Wide'		: 1,
                'Dot by Dot': 5,
                'Zoom 1'	: 2,
                'Zoom 2'	: 3,
            },
        }

        CmdString = 'WIDE{0: 4}\r\n'.format(States[ InputClass[InputVal] ][value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        InputClass = {
            'DVI-D PC'    : 'PC',
            'D-SUB'       : 'PC',
            'HDMI PC'     : 'PC',
            'DisplayPort' : 'PC',
            'Component'   : 'AV',
            'Video'       : 'AV',
            'DVI-D AV'    : 'AV',
            'HDMI AV'     : 'AV',
        }

        InputVal = qualifier['Input']

        States = {
            'PC' : {
                2   :  'Normal',
                1   :  'Wide',
                3   :  'Dot by Dot',
                4   :  'Zoom 1',
                5   :  'Zoom 2',
            },
            'AV' : {
                4   :  'Normal',
                1   :  'Wide',
                5   :  'Dot by Dot',
                2   :  'Zoom 1',
                3   :  'Zoom 2',
            },
        }

        res = self.__UpdateHelper('AspectRatio', b'WIDE????\r\n' , value, qualifier)
        if res and InputVal:
            try:
                self.WriteStatus('AspectRatio',  States[ InputClass[InputVal] ][int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        States = {
            'On' : 1,
            'Off' : 0,
        }

        CmdString = 'MUTE{0: 4}\r\n'.format(States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            1	: 'On',
            0	: 'Off'
        }

        res = self.__UpdateHelper('AudioMute', b'MUTE????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute',  States[int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', b'AGIN0001\r\n', value, qualifier)

    def SetEnlarge(self, value, qualifier):

        States = {
            '2x2' : 1,
            '3x3' : 2,
            '4x4' : 3,
            '5x5' : 4,
            'Off' : 0,
        }

        CmdString = 'EMAG{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Enlarge', CmdString, value, qualifier)

    def UpdateEnlarge(self, value, qualifier):

        States = {
            1	:	'2x2',
            2	:	'3x3',
            3	:	'4x4',
            4	:	'5x5',
            0	:	'Off',
        }

        res = self.__UpdateHelper('Enlarge', b'EMAG????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Enlarge',  States[int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateEnlarge')

    def SetImageLocation(self, value, qualifier):

        States = {
            '1x1' : 11,'1x2' : 12,'1x3' : 13,'1x4' : 14,'1x5' : 15,
            '2x1' : 21,'2x2' : 22,'2x3' : 23,'2x4' : 24,'2x5' : 25,
            '3x1' : 31,'3x2' : 32,'3x3' : 33,'3x4' : 34,'3x5' : 35,
            '4x1' : 41,'4x2' : 42,'4x3' : 43,'4x4' : 44,'4x5' : 45,
            '5x1' : 51,'5x2' : 52,'5x3' : 53,'5x4' : 54,'5x5' : 55
        }

        CmdString = 'EPHV{0: 4}\r\n'.format(States[value])
        self.__SetHelper('ImageLocation', CmdString, value, qualifier)

    def UpdateImageLocation(self, value, qualifier):

        States = {
            11  : '1x1', 12	: '1x2',13 : '1x3',14   : '1x4',15 :    '1x5',
            21	: '2x1', 22	: '2x2',23 : '2x3',24	: '2x4',25 :	'2x5',
            31	: '3x1', 32	: '3x2',33 : '3x3',34	: '3x4',35 :	'3x5',
            41	: '4x1', 42	: '4x2',43 : '4x3',44	: '4x4',45 :	'4x5',
            51	: '5x1', 52	: '5x2',53 : '5x3',54	: '5x4',55 :	'5x5'
            }

        res = self.__UpdateHelper('ImageLocation', b'EPHV????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('ImageLocation',  States[int(res[0:2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateImageLocation')

    def SetInput(self, value, qualifier):

        States = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            'DisplayPort'   : 14,
        }

        CmdString = 'INPS{0: 4}\r\n'.format(States[value])

        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            14  :   'DisplayPort',
        }

        res = self.__UpdateHelper('Input', b'INPS????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Input',  States[int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateInput')

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On'  : 0,
            'Off' : 1,
            'On2' : 2,
        }

        CmdString = 'LOSD{0: 4}\r\n'.format(States[value])
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        States = {
            0 : 'On',
            1 : 'Off',
            2 : 'On2',
        }

        res = self.__UpdateHelper('OnScreenDisplay', b'LOSD????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('OnScreenDisplay',  States[int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateOnScreenDisplay')

    def SetPictureInPicture(self, value, qualifier):

        States = {
            'PIP'	: 1,
            'PBP 1'	: 2,
            'PBP 2' : 3,
            'Off'	: 0,
        }

        CmdString = 'MWIN{0: 4}\r\n'.format(States[value])
        self.__SetHelper('PictureInPicture', CmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        States = {
            1 : 'PIP',
            2 : 'PBP 1',
            3 : 'PBP 2',
            0 : 'Off'
        }

        res = self.__UpdateHelper('PictureInPicture', b'MWIN????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureInPicture',  States[int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdatePictureInPicture')

    def SetPIPInput(self, value, qualifier):


        States = {
            'DVI-D PC'		: 1,
            'D-SUB'		    : 2,
            'Component'	    : 3,
            'Video'		    : 4,
            'HDMI AV'		: 9,
            'HDMI PC'   	: 10,
            'DisplayPort'   : 14,
        }

        CmdString = 'MWIP{0: 4}\r\n'.format(States[value])
        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        States = {
            1	:	'DVI-D PC',
            2	:	'D-SUB',
            3	:	'Component',
            4	:	'Video',
            9	:	'HDMI AV',
            10	:	'HDMI PC',
            14  :   'DisplayPort',
        }

        res = self.__UpdateHelper('PIPInput', b'MWIP????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('PIPInput',  States[int(res[:-2])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPSize(self, value, qualifier):

        if 1 <= int(value) <= 64:
            CmdString = 'MPSZ{0:>4}\r\n'.format(value)
            self.__SetHelper('PIPSize', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdatePIPSize(self, value, qualifier):

        res = self.__UpdateHelper('PIPSize', 'MPSZ????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('PIPSize', res[:-2] , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdatePIPSize')

    def SetPower(self, value, qualifier):

        States = {
            'On'  : 1,
            'Off' : 0,
        }

        CmdString = 'POWR{0: 4}\r\n'.format(States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Input signal waiting mode',
        }

        res = self.__UpdateHelper('Power', 'POWR????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Power',  States[res[0]] , qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VOLM{0: 4}\r\n'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', 'VOLM????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateVolume')

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'CONT{0: 4}\r\n'.format(value)
            self.__SetHelper('Contrast', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateContrast(self, value, qualifier):

        res = self.__UpdateHelper('Contrast', 'CONT????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Contrast',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateContrast')

    def SetBlackLevel(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'BLVL{0: 4}\r\n'.format(value)
            self.__SetHelper('BlackLevel', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBlackLevel(self, value, qualifier):

        res = self.__UpdateHelper('BlackLevel', 'BLVL????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('BlackLevel',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateBlackLevel')

    def SetTint(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'TINT{0: 4}\r\n'.format(value)
            self.__SetHelper('Tint', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateTint(self, value, qualifier):

        res = self.__UpdateHelper('Tint', 'TINT????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Tint',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTint')

    def SetColors(self, value, qualifier):

        if 0 <= value <= 60:
            CmdString = 'COLR{0: 4}\r\n'.format(value)
            self.__SetHelper('Colors', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateColors(self, value, qualifier):

        res = self.__UpdateHelper('Tint', 'COLR????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Colors',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateColors')

    def SetSharpness(self, value, qualifier):

        if 0 <= value <= 24:
            CmdString = 'SHRP{0: 4}\r\n'.format(value)
            self.__SetHelper('Sharpness', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateSharpness(self, value, qualifier):

        res = self.__UpdateHelper('Sharpness', 'SHRP????\r\n' , value, qualifier)
        if res:
            try:
                self.WriteStatus('Sharpness',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateSharpness')

    def SetBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO',
            'Top'                   : 'BZCT',
            'Bottom'                : 'BZCB',
            'Right'                 : 'BZCR',
            'Left'                  : 'BZCL'
        }

        Value = {
            'On'  : '1',
            'Off' : '0'
        }

        CmdString = '{0}   {1}\r\n'.format(Bezel[qualifier['Bezel']], Value[value])
        self.__SetHelper('BezelAdjust', CmdString, value, qualifier)

    def UpdateBezelAdjust(self, value, qualifier):

        Bezel = {
            'Enable Bezel Adjust'   : 'BZCO????\r\n',
            'Top'                   : 'BZCT????\r\n',
            'Bottom'                : 'BZCB????\r\n',
            'Right'                 : 'BZCR????\r\n',
            'Left'                  : 'BZCL????\r\n'
        }

        Values = {
            1 : 'On',
            0 : 'Off'
        }

        res = self.__UpdateHelper('BezelAdjust', Bezel[qualifier['Bezel']] , value, qualifier)
        if res:
            self.WriteStatus('BezelAdjust', Values[int(res)], qualifier)

    def SetBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV',
            'Short' : 'BEZH'
        }

        if 0 <= value <= 100 :
            CmdString = '{0}{1: 4}\r\n'.format(   Sides[qualifier['Side']]   ,     value   )
            self.__SetHelper('BezelWidth', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBezelWidth(self, value, qualifier):

        Sides = {
            'Long'  : 'BEZV????\r\n',
            'Short' : 'BEZH????\r\n'
        }

        res = self.__UpdateHelper('BezelWidth', Sides[qualifier['Side']] , value, qualifier)
        if res:
            try:
                self.WriteStatus('BezelWidth',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateBezelWidth')

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 31:
            CmdString = 'VLMP{0: 4}\r\n'.format(value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            print('Invalid Command')

    def UpdateBrightness(self, value, qualifier):
        res = self.__UpdateHelper('Brightness', 'VLMP????\r\n', value, qualifier)
        if res:
            try:
                self.WriteStatus('Brightness',  int(res) , qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateBrightness')

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + str(commandstring.strip()), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return res

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
                self.Subscription[command] = {'method' :{}}

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
            self._compile_list[regex_string] = {'callback': callback, 'para' :arg}


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