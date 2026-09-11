from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
        self.Models = {
            'MDSC-2224 LED': self.barc_10_2658_LED,
            'MDSC-2226 LED': self.barc_10_2658_LED,
            'MDSC-2232 DDI': self.barc_10_2658_DDI,
            'MDSC-2242 LED': self.barc_10_2658_LED,
            'MDSC-2224 DDI': self.barc_10_2658_DDI,
            'MDSC-2224 DOI': self.barc_10_2658_LED,
            'MDSC-2224 MNA': self.barc_10_2658_MNA1,
            'MDSC-2232 MNA': self.barc_10_2658_MNA2,
            'MDSC-2226 DDI': self.barc_10_2658_DDI,
            'MDSC-2226 MNA': self.barc_10_2658_MNA2,
            'MDSC-2242 MNA': self.barc_10_2658_MNA1,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Backlight': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'LoadProfile': {'Status': {}},
            'OperationHours': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPLayout': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'PowerSavingMode': {'Status': {}},
            'ReleaseInfo': {'Status': {}},
            'SerialNumber': {'Status': {}},
            'SignalStatus': {'Parameters': ['Input'], 'Status': {}},
        }

        self.UpdateRegex = {
            'ExecutiveMode': re.compile(b'([0-1]|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'Input': re.compile(b'(11|10|9|8|7|6|5|4|3|0|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'LoadProfile': re.compile(b'([0-5]|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'OperationHours': re.compile(b'(\d{5}|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'PIPInput': re.compile(b'(11|10|9|8|7|6|5|4|3|0|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'PIPLayout': re.compile(b'([0-5]|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'PowerSavingMode': re.compile(b'([0-1]|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'Backlight': re.compile(b'(PS[01][01][012]00|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'ReleaseInfo': re.compile(b'(\d{2}\.\d{2}[A-Z]{2}LP\d\.\d{2}(LEDM|MNAM|DDIM)|Error \d{1,2}: ?[a-zA-Z 0-9]+)'),
            'SerialNumber': re.compile(b'(SN:[\x20-\x7F]{14})'),
        }
        self.SetRegex = re.compile(b'\x06|\d\d?|Error \d{1,2}: ?[a-zA-Z 0-9]+')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off',
            '2': 'Sensor not working'
        }
        SignalStatusValues = {
            '0': 'Present and valid signal',
            '1': 'Not present or bad signal',
        }
        BacklightCmdString = '\x1bps?'
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = SignalStatusValues[res[2]]
                self.WriteStatus('SignalStatus', value, {'Input': 'Main'})
            except (KeyError, IndexError, TypeError):
                print('Invalid/unexpected response for UpdateBacklight')
            try:
                value = SignalStatusValues[res[3]]
                self.WriteStatus('SignalStatus', value, {'Input': 'Secondary'})
            except (KeyError, IndexError, TypeError):
                print('Invalid/unexpected response for UpdateBacklight')
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError, TypeError):
                print('Invalid/unexpected response for UpdateBacklight')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '&&KEY,1;',
            'Off': '&&KEY,0;'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ExecutiveModeCmdString = '&&RV,KEY;'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdateExecutiveMode')

    def SetInput(self, value, qualifier):

        InputCmdString = '&&INP,{0};'.format(self.InputStates[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '&&RV,INP;'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputValues[res]
                self.WriteStatus('Input', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdateInput')

    def SetLoadProfile(self, value, qualifier):

        ValueStateValues = {
            'Factory': '0',
            'X-Ray': '1',
            'User 1': '2',
            'User 2': '3',
            'User 3': '4'
        }

        LoadProfileCmdString = '&&PRO,{0};'.format(ValueStateValues[value])
        self.__SetHelper('LoadProfile', LoadProfileCmdString, value, qualifier)

    def UpdateLoadProfile(self, value, qualifier):

        ValueStateValues = {
            '0': 'Factory',
            '1': 'X-Ray',
            '2': 'User 1',
            '3': 'User 2',
            '4': 'User 3'
        }

        LoadProfileCmdString = '&&RV,PRO;'
        res = self.__UpdateHelper('LoadProfile', LoadProfileCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('LoadProfile', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdateLoadProfile')

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = '\x1bh?'
        res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
                self.WriteStatus('OperationHours', value, qualifier)
            except ValueError:
                print('Invalid/unexpected response for UpdateOperationHours')

    def SetPIPInput(self, value, qualifier):

        PIPInputCmdString = '&&PIPI,{0};'.format(self.InputStates[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = '&&RV,PIPI;'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputValues[res]
                self.WriteStatus('PIPInput', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdatePIPInput')

    def SetPIPLayout(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Large': '1',
            'Small': '2',
            'Side By Side': '3',
            'Side By Side Tall': '4',
            'Side By Side Fill': '5'
        }

        PIPLayoutCmdString = '&&PIPL,{0};'.format(ValueStateValues[value])
        self.__SetHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)

    def UpdatePIPLayout(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Large',
            '2': 'Small',
            '3': 'Side By Side',
            '4': 'Side By Side Tall',
            '5': 'Side By Side Fill'
        }

        PIPLayoutCmdString = '&&RV,PIPL;'
        res = self.__UpdateHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PIPLayout', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdatePIPLayout')

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = '&&PIPT;'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPowerSavingMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1',
        }

        PowerSavingModeCmdString = '&&DPMS,{0};'.format(ValueStateValues[value])
        self.__SetHelper('PowerSavingMode', PowerSavingModeCmdString, value, qualifier)

    def UpdatePowerSavingMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On',
        }

        PowerSavingModeCmdString = '&&RV,DPMS;'
        res = self.__UpdateHelper('PowerSavingMode', PowerSavingModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PowerSavingMode', value, qualifier)
            except KeyError:
                print('Invalid/unexpected response for UpdatePowerSavingMode')

    def UpdateReleaseInfo(self, value, qualifier):

        ReleaseInfoCmdString = '\x1bR?'
        res = self.__UpdateHelper('ReleaseInfo', ReleaseInfoCmdString, value, qualifier)
        if res:
            value = res
            self.WriteStatus('ReleaseInfo', value, qualifier)

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = '\x1bSN?'
        res = self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)
        if res:
            try:
                value = res[3:]
                self.WriteStatus('SerialNumber', value, qualifier)
            except IndexError:
                print('Invalid/unexpected response for UpdateSerialNumber')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Error' in response:
            ErrorCode = re.search('\d', response)
            ErrorMessage = re.search('(: ?[a-zA-Z 0-9]+)', response)
            print('Error code from device: {}{}'.format(ErrorCode.group(0), ErrorMessage.group(0)))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex[command])
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

    def barc_10_2658_DDI(self):
        self.InputStates = {
            'SDI 1': '9',
            'DVI 1': '3',
            'DisplayPort': '10',
            'S-Video': '6',
            'Autosearch': '0',
            'RGB': '7',
            'Component': '8',
            'SDI 2': '11',
            'DVI 2': '4',
        }
        self.InputValues = {
            '9': 'SDI 1',
            '3': 'DVI 1',
            '10': 'DisplayPort',
            '6': 'S-Video',
            '0': 'Autosearch',
            '7': 'RGB',
            '8': 'Component',
            '11': 'SDI 2',
            '4': 'DVI 2'
        }

    def barc_10_2658_LED(self):
        self.InputStates = {
            'SDI': '9',
            'DVI': '3',
            'DisplayPort': '10',
            'S-Video': '6',
            'Autosearch': '0',
            'RGB': '7',
            'Component': '8'
        }
        self.InputValues = {
            '9': 'SDI',
            '3': 'DVI',
            '10': 'DisplayPort',
            '6': 'S-Video',
            '0': 'Autosearch',
            '7': 'RGB',
            '8': 'Component'
        }

    def barc_10_2658_MNA1(self):
        self.InputStates = {
            'DVI': '3',
            'DisplayPort': '10',
            'S-Video': '6',
            'Autosearch': '0',
            'RGB': '7',
            'Component': '8',
            'Nexxis': '11',
        }
        self.InputValues = {
            '3': 'DVI',
            '10': 'DisplayPort',
            '6': 'S-Video',
            '0': 'Autosearch',
            '7': 'RGB',
            '8': 'Component',
            '11': 'Nexxis'
        }

    def barc_10_2658_MNA2(self):
        self.InputStates = {
            'SDI': '9',
            'DVI': '3',
            'DisplayPort': '10',
            'S-Video': '6',
            'Autosearch': '0',
            'RGB': '7',
            'Component': '8',
            'Nexxis': '11',
        }
        self.InputValues = {
            '9': 'SDI',
            '3': 'DVI',
            '10': 'DisplayPort',
            '6': 'S-Video',
            '0': 'Autosearch',
            '7': 'RGB',
            '8': 'Component',
            '11': 'Nexxis'
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
