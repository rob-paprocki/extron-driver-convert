from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import unpack


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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DMode': {'Status': {}},
            '4KMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Parameters': ['Lamp ID'], 'Status': {}},
            'Power': {'Status': {}},
            'Shutter': {'Status': {}},
            }

    def computeCHKSM(self, byte):

        lrc = 0
        for i in range(0, len(byte)):
            lrc ^= byte[i]
        return lrc.to_bytes(1, byteorder='big')

    def Set3DMode(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x00',
            'L-C/R-C': b'\x01',
            'L-A/R-A': b'\x02',
            'L-B/R-B': b'\x03',
            'L-B/R-C': b'\x0A'
        }
        string = b''.join([b'\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x00\x00\x80\x07\x00\x05\x00\x76\x02\x00', ValueStateValues[value]])
        CHKSM = self.computeCHKSM(string)
        CmdString = b''.join([b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x18', b'\xA5', string, CHKSM, b'\x5A'])
        self.__SetHelper('3DMode', CmdString, value, qualifier)

    def Set4KMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        string = b''.join([b'\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x00\x00\x80\x07\x00\x05\x00\x45\x02\x00', ValueStateValues[value]])
        CHKSM = self.computeCHKSM(string)
        CmdString = b''.join([b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x18', b'\xA5', string, CHKSM, b'\x5A'])
        self.__SetHelper('4KMode', CmdString, value, qualifier)

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x16\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x01\x01\x80\x05\x00\x03\x00\x1B\x04\x9B\x5A'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                resParse = unpack('>h', res[-6:-4])
                value = resParse[0]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (IndexError, ValueError):
                print('Invalid/unexpected response for UpdateFilterUsage')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'IMB': b'\x00',
            'HDMI 1': b'\x01',
            'HDMI 2': b'\x02',
            'AUX x 1': b'\x03'
        }
        string = b''.join([b'\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x00\x00\x80\x07\x00\x05\x00\x07\x02\x00', ValueStateValues[value]])
        CHKSM = self.computeCHKSM(string)
        InputCmdString = b''.join([b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x18', b'\xA5', string, CHKSM, b'\x5A'])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x16\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x31\x01\x80\x05\x00\x03\x00\x0D\x02\xBB\x5A'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                resParse = unpack('>h', res[-4:-2])
                value = resParse[0]
                if res[-7] == 0:
                    self.WriteStatus('LampUsage', value, {'Lamp ID': 'A1'})
                elif res[-7] == 1:
                    self.WriteStatus('LampUsage', value, {'Lamp ID': 'A2'})
                elif res[-7] == 2:
                    self.WriteStatus('LampUsage', value, {'Lamp ID': 'A3'})
                elif res[-7] == 3:
                    self.WriteStatus('LampUsage', value, {'Lamp ID': 'B1'})
                elif res[-7] == 4:
                    self.WriteStatus('LampUsage', value, {'Lamp ID': 'B2'})
                elif res[-7] == 5:
                    self.WriteStatus('LampUsage', value, {'Lamp ID': 'B3'})
            except (IndexError, ValueError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x19\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x17\x00\x80\x08\x00\x06\x40\x54\x2F\x00\x00\x00\xA0\x5A',
            'On': b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x19\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x17\x00\x80\x08\x00\x06\x40\x54\x2E\x00\x00\x00\xA1\x5A'
        }
        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x01': 'Start up',
            b'\x02': 'Start up Lamp',
            b'\x03': 'On',
            b'\x04': 'Cooling 1',
            b'\x05': 'Cooling 2'
        }
        PowerCmdString = b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x16\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x01\x01\x80\x05\x00\x03\x00\x02\x01\x87\x5A'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Open': b'\x01',
            'Close': b'\x00'
        }
        string = b''.join([b'\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x01\x00\x80\x06\x00\x04\x00\x2F\x01', ValueStateValues[value]])
        CHKSM = self.computeCHKSM(string)
        ShutterCmdString = b''.join([b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x17', b'\xA5', string, CHKSM, b'\x5A'])
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)

    def UpdateShutter(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Open',
            b'\x00': 'Close'
        }
        ShutterCmdString = b'\x02\x0A\x53\x4F\x4E\x59\x00\x70\x00\x16\xA5\x01\x00\x01\x00\x01\x03\x00\x01\x00\x01\x01\x01\x80\x05\x00\x03\x00\x2F\x01\xAA\x5A'
        res = self.__UpdateHelper('Shutter', ShutterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-3:-2]]
                self.WriteStatus('Shutter', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateShutter')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {

            b'\x01\x01': 'Undefined Command',
            b'\x01\x04': 'Size Error',
            b'\x01\x05': 'Select Error',
            b'\x01\x06': 'Range Over',
            b'\x01\x0A': 'Not Applicable',
            b'\x01\x0C': 'Data Error',
            b'\xF0\x10': 'Check Sum Error',
            b'\xF0\x20': 'Framing Error',
            b'\xF0\x30': 'Parity Error',
            b'\xF0\x40': 'Over Run Error',
            b'\xF0\x50': 'Other Communication Error'
        }
        if response:
            if response[-9:-8] == b'\x03':
                if response[-4:-2] in DEVICE_ERROR_CODES:
                    print(sourceCmdName + ' Error : ' + DEVICE_ERROR_CODES[response[-4:-2]])
                    response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
                self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x5A')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter += 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\x5A')
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
