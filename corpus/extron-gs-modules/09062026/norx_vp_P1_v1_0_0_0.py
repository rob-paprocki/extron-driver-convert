from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'%0001 ESTATUS (\d+)\r\n'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'%0001 OSD (0|1)\r\n'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'%0001 SYSON (\d+)\r\n'), self.__MatchOperationHours, None)
            self.AddMatchString(re.compile(b'%0001 POWER ([0123])\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'%0001 SHUTTER (0|1)\r\n'), self.__MatchShutter, None)
            self.AddMatchString(re.compile(b'!0000?4\r\n'), self.__MatchError, None)

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = ':ESTATUS ?\r\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            1: 'Fan 1 Stopped',
            2: 'Fan 2 Stopped',
            3: 'Fan 3 Stopped',
            4: 'Fan 3 Stopped',  # to account for possible typo in protocol
            8: 'Critical temperature reached',
            16: 'Wrong source FPGA (SW update error)',
            32: 'Wrong display FPGA (SW update error)',
            64: 'Wrong LED FPGA (SW update error)',
            128: 'Wrong TI version FPGA (SW update error)',
            256: 'Hardware access error',
            0: 'Normal'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('DeviceStatus', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVI 1': '0',
            'DVI 2': '1',
            'Dual DVI': '2',
            'HDMI': '3',
            'DisplayPort': '4'
        }

        InputCmdString = ':INPUT {}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '#': '#',
            '*': '*'
        }

        KeypadCmdString = ':{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'MENU',
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'OK': 'OK',
            'Back': 'BACK'
        }

        MenuNavigationCmdString = ':{}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        OnScreenDisplayCmdString = ':OSD {}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayCmdString = ':OSD ?\r\n'
        self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def UpdateOperationHours(self, value, qualifier):

        OperationHoursCmdString = ':SYSON ?\r\n'
        self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)

    def __MatchOperationHours(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OperationHours', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PowerCmdString = ':POWER {}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = ':POWER ?\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '0': 'Off',
            '1': 'Warming Up',
            '3': 'Cooling Down'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShutterCmdString = ':SHUTTER {}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ShutterCmdString = ':SHUTTER ?\r\n'
        self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)

    def __MatchShutter(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Shutter', value, None)

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
        self.Error(['Device Response: Invalid Command'])

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True

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

