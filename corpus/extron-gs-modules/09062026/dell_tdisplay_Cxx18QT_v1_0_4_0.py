from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog, Timer
import base64
import urllib.error
import urllib.request


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
        self.Models = {}

        self.Models = {
            'C5518QT': self.dell_39_3253_C5518QT,
            'C8618QT': self.dell_39_3253_C8618QT,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'OSDButtonLock': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        States = {
            '16:9': b'\x37\x51\x03\xEA\x33\x00\xBC',
            '4:3': b'\x37\x51\x03\xEA\x33\x02\xBE',
            '5:4': b'\x37\x51\x03\xEA\x33\x04\xB8'
        }

        self.__SetHelper('AspectRatio', States[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            0x00: '16:9',
            0x02: '4:3',
            0x04: '5:4'
        }

        res = self.__UpdateHelper('AspectRatio', b'\x37\x51\x02\xEB\x33\xBC', value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioInput(self, value, qualifier):

        States = {
            'HDMI/DP': b'\x37\x51\x03\xEA\xB2\x01\x3C',
            'PC': b'\x37\x51\x03\xEA\xB2\x02\x3F'
        }

        self.__SetHelper('AudioInput', States[value], value, qualifier)

    def UpdateAudioInput(self, value, qualifier):

        States = {
            0x01: 'HDMI/DP',
            0x02: 'PC'
        }

        res = self.__UpdateHelper('AudioInput', b'\x37\x51\x02\xEB\xB2\x3D', value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioInput', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Input: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': b'\x37\x51\x03\xEA\xB1\x01\x3F',
            'Off': b'\x37\x51\x03\xEA\xB1\x00\x3E',
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            0x01: 'On',
            0x00: 'Off'
        }

        res = self.__UpdateHelper('AudioMute', b'\x37\x51\x02\xEB\xB1\x3E', value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        self.__SetHelper('Input', self.Inputs[value], value, qualifier)

    def UpdateInput(self, value, qualifier):
        res = self.__UpdateHelper('Input', b'\x37\x51\x02\xEB\x62\xED', value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', self.InputStates[res[6]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetOSDButtonLock(self, value, qualifier):

        States = {
            'Lock': b'\x37\x51\x03\xEA\x84\x01\x0A',
            'Unlock': b'\x37\x51\x03\xEA\x84\x00\x0B'
        }

        self.__SetHelper('OSDButtonLock', States[value], value, qualifier)

    def UpdateOSDButtonLock(self, value, qualifier):

        States = {
            0x01: 'Lock',
            0x00: 'Unlock'
        }

        res = self.__UpdateHelper('OSDButtonLock', b'\x37\x51\x02\xEB\x84\x0B', value, qualifier)
        if res:
            try:
                self.WriteStatus('OSDButtonLock', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['OSD Button Lock: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\x37\x51\x03\xEA\x20\x01\xAE',
            'Off': b'\x37\x51\x03\xEA\x20\x00\xAF',
            'Standby': b'\x37\x51\x03\xEA\x20\x02\xAD'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            0x01: 'On',
            0x00: 'Off',
            0x02: 'Standby',
        }

        res = self.__UpdateHelper('Power', b'\x37\x51\x02\xEB\x20\xAF', value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', States[res[-2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:

            CmdString = b'\x37\x51\x03\xEA\xB0' + bytes([value])

            ChkSum = 0
            for i in range(0, len(CmdString)):
                ChkSum = ChkSum ^ CmdString[i]

            self.__SetHelper('Volume', CmdString + ChkSum.to_bytes(1, 'big'), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        res = self.__UpdateHelper('Volume', b'\x37\x51\x02\xEB\xB0\x3F', value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume', res[-2], qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: 'Timeout',
            0x02: 'Parameters Error',
            0x03: 'Not connected',
            0x04: 'Other Failure'
        }

        if response[4] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            delim = 11 if command == 'Input' else 8
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=delim)
            if not res:
                self.Error(['Invalid/Unexpected Response'])
            else:
                res = self.__CheckResponseForErrors(command + ':', res)

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

            delim = 11 if command == 'Input' else 8
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=delim)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def dell_39_3253_C5518QT(self):

        self.Inputs = {
            'HDMI 1': b'\x37\x51\x06\xEA\x62\x01\x00\x00\x00\xE9',
            'HDMI 2': b'\x37\x51\x06\xEA\x62\x02\x00\x00\x00\xEA',
            'HDMI 3': b'\x37\x51\x06\xEA\x62\x04\x00\x00\x00\xEC',
            'DisplayPort': b'\x37\x51\x06\xEA\x62\x08\x00\x00\x00\xE0',
            'VGA': b'\x37\x51\x06\xEA\x62\x40\x00\x00\x00\xA8'
        }

        self.InputStates = {
            0x01: 'HDMI 1',
            0x02: 'HDMI 2',
            0x04: 'HDMI 3',
            0x08: 'DisplayPort',
            0x40: 'VGA'
        }

    def dell_39_3253_C8618QT(self):
        self.Inputs = {
            'HDMI 1': b'\x37\x51\x06\xEA\x62\x01\x00\x00\x00\xE9',
            'HDMI 2': b'\x37\x51\x06\xEA\x62\x02\x00\x00\x00\xEA',
            'HDMI 3': b'\x37\x51\x06\xEA\x62\x04\x00\x00\x00\xEC',
            'HDMI 4': b'\x37\x51\x06\xEA\x62\x00\x04\x00\x00\xEC',
            'DisplayPort': b'\x37\x51\x06\xEA\x62\x08\x00\x00\x00\xE0',
            'VGA': b'\x37\x51\x06\xEA\x62\x40\x00\x00\x00\xA8'
        }

        self.InputStates = {
            0x01: 'HDMI 1',
            0x02: 'HDMI 2',
            0x04: 'HDMI 3',
            0x00: 'HDMI 4',
            0x08: 'DisplayPort',
            0x40: 'VGA'
        }

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


class DeviceHTTPClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {
            'C5518QT': self.dell_39_3253_C5518QT,
            'C8618QT': self.dell_39_3253_C5518QT,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'GetCookies': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        if deviceUsername is not None and devicePassword is not None:
            self.authentication = b'Basic ' + base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode())
        else:
            self.authentication = None

        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())
        self.Opener.add_handler(urllib.request.HTTPCookieProcessor())

        self.GetCookieTimer = Timer(3, self.GetCookieUpdate)
        self.UpdateGetCookies(None, None)

    def GetCookieUpdate(self, timer, count):
        self.UpdateGetCookies(None, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': {'redio_objname': 'Aspect1', 'radio_objvalue': '0', 'btnRadioChg': '', 'PrjSRC': '0', 'chgprojstatus': 'Apply'},
            '4:3': {'redio_objname': 'Aspect1', 'radio_objvalue': '2', 'btnRadioChg': '', 'PrjSRC': '2', 'chgprojstatus': 'Apply'},
            '5:4': {'redio_objname': 'Aspect1', 'radio_objvalue': '4', 'btnRadioChg': '', 'PrjSRC': '4', 'chgprojstatus': 'Apply'}
        }

        AspectRatioCmdString = '/tgi/status.tgi'
        data = urllib.parse.urlencode(ValueStateValues[value])
        self.__SetHelper('AspectRatio', value, qualifier, AspectRatioCmdString, data.encode())

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': {'redio_objname': 'Spk', 'radio_objvalue': '170', 'btnRadioChg': '', 'Spk': '1', 'Chgprojstatus': 'Apply'},
            'Off': {'redio_objname': 'Spk', 'radio_objvalue': '85', 'btnRadioChg': '', 'Spk': '0', 'Chgprojstatus': 'Apply'}
        }

        AudioMuteCmdString = '/tgi/status.tgi'
        data = urllib.parse.urlencode(ValueStateValues[value])
        self.__SetHelper('AudioMute', value, qualifier, AudioMuteCmdString, data.encode())

    def UpdateGetCookies(self, value, qualifier):

        GetCookiesCmdString = '/status.htm'
        self.__UpdateHelper('GetCookies', value, qualifier, GetCookiesCmdString)

    def SetInput(self, value, qualifier):

        InputCmdString = '/tgi/status.tgi'
        data = urllib.parse.urlencode(self.Inputs[value])
        self.__SetHelper('Input', value, qualifier, InputCmdString, data.encode())

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': {'PowerOn': 'Power ON'},
            'Off': {'PowerOff': 'Power OFF'},
        }

        PowerCmdString = '/tgi/status.tgi'
        data = urllib.parse.urlencode(ValueStateValues[value])
        self.__SetHelper('Power', value, qualifier, PowerCmdString, data.encode())

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '/tgi/status.tgi'
            Value = {'Volume': '{}'.format(value), 'btnVol': 'Apply'}
            data = urllib.parse.urlencode(Value)
            self.__SetHelper('Volume', value, qualifier, VolumeCmdString, data.encode())
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        print('in check response for errors')
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, resource, data=None):
        self.Debug = True

        ipadd = re.search('http://(\S+):[0-9]+/', self.RootURL)
        IPAddress = ipadd.group(1)
        url = 'http://{0}{1}'.format(IPAddress, resource)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        try:
            res = self.Opener.open(my_request)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, resource, data=None):

        ipadd = re.search('http://(\S+):[0-9]+/', self.RootURL)
        IPAddress = ipadd.group(1)
        url = 'http://{0}{1}'.format(IPAddress, resource)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
        
        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = b''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = b''
        except Exception as err:
            res = b''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = b''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def OnConnected(self):
        print('on connected')
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def dell_39_3253_C5518QT(self):
        self.Inputs = {
            'HDMI 1': {'redio_objname': 'PrjSRC', 'radio_objvalue': '1', 'btnRadioChg': '', 'PrjSRC': '1', 'chgprojstatus': 'Apply'},
            'HDMI 2': {'redio_objname': 'PrjSRC', 'radio_objvalue': '2', 'btnRadioChg': '', 'PrjSRC': '2', 'chgprojstatus': 'Apply'},
            'HDMI 3': {'redio_objname': 'PrjSRC', 'radio_objvalue': '4', 'btnRadioChg': '', 'PrjSRC': '4', 'chgprojstatus': 'Apply'},
            'DisplayPort': {'redio_objname': 'PrjSRC', 'radio_objvalue': '8', 'btnRadioChg': '', 'PrjSRC': '8', 'chgprojstatus': 'Apply'},
            'VGA': {'redio_objname': 'PrjSRC', 'radio_objvalue': '64', 'btnRadioChg': '', 'PrjSRC': '64', 'chgprojstatus': 'Apply'}
        }

    def dell_39_3253_C8618QT(self):
        self.Inputs = {
            'HDMI 1': {'redio_objname': 'PrjSRC', 'radio_objvalue': '1', 'btnRadioChg': '', 'PrjSRC': '1', 'chgprojstatus': 'Apply'},
            'HDMI 2': {'redio_objname': 'PrjSRC', 'radio_objvalue': '2', 'btnRadioChg': '', 'PrjSRC': '2', 'chgprojstatus': 'Apply'},
            'HDMI 3': {'redio_objname': 'PrjSRC', 'radio_objvalue': '4', 'btnRadioChg': '', 'PrjSRC': '4', 'chgprojstatus': 'Apply'},
            'HDMI 4': {'redio_objname': 'PrjSRC', 'radio_objvalue': '1024', 'btnRadioChg': '', 'PrjSRC': '1024', 'chgprojstatus': 'Apply'},
            'DisplayPort': {'redio_objname': 'PrjSRC', 'radio_objvalue': '8', 'btnRadioChg': '', 'PrjSRC': '8', 'chgprojstatus': 'Apply'},
            'VGA': {'redio_objname': 'PrjSRC', 'radio_objvalue': '64', 'btnRadioChg': '', 'PrjSRC': '64', 'chgprojstatus': 'Apply'}
        }

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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


class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])
