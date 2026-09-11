from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

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
            'AudioMute': { 'Status': {}},
            'AutoAdjust': { 'Status': {}},
            'AutoScan': { 'Status': {}},
            'HDMIFullRange': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }


        self.GetAutoScan        = re.compile(b'[\x00-\xFF]\rAuto Scan = [01][\x00-\xFF]{4}\x03\x0C\xF1|\x03\x0B\xF2')
        self.GetHDMIFullRange   = re.compile(b'[\x00-\xFF]\rHDMI Full Range = [01][\x00-\xFF]{4}\x03\x0C\xF1|\x03\x0B\xF2')
        self.GetPower           = re.compile(b'[\x00-\xFF]\rPower : ON[\x00-\xFF]{4}\x03\x0C\xF1|[\x00-\xFF]\rPower : OFF[\x00-\xFF]{4}\x03\x0C\xF1|[\x00-\xFF]\rPower : [\x00-\xFF]{16}\x03\x0C\xF1|\x03\x0B\xF2')
        self.GetVolume          = re.compile(b'[\x00-\xFF]\rVolume = [0-9]{1,3}[\x00-\xFF]{4}\x03\x0C\xF1|\x03\x0B\xF2')

        self.CommandDeliRex = {
            'AutoScan' : self.GetAutoScan,
            'HDMIFullRange' : self.GetHDMIFullRange,
            'Power' : self.GetPower,
            'Volume' : self.GetVolume
            }

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x08\x22\x0A\x00\x00\x00\x01\xCB', 
            'Off' : b'\x08\x22\x0A\x00\x00\x00\x00\xCC'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetAutoAdjust(self, value, qualifier):

        AutoAdjustCmdString = b'\x08\x22\x07\x00\x00\x00\x00\xCF'
        self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)
    def SetAutoScan(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x08\x22\x17\x00\x00\x00\x01\xBE', 
            'Off' : b'\x08\x22\x17\x00\x00\x00\x00\xBF'
        }

        AutoScanCmdString = ValueStateValues[value]
        self.__SetHelper('AutoScan', AutoScanCmdString, value, qualifier)

    def UpdateAutoScan(self, value, qualifier):

        ValueStateValues = {
            0x31 : 'On', 
            0x30 : 'Off'
        }

        AutoScanCmdString = b'\x04\x21\x18\xC3'
        res = self.__UpdateHelper('AutoScan', AutoScanCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[14]]
                self.WriteStatus('AutoScan', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Scan : Invalid/Unexpected response'])

    def SetHDMIFullRange(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x08\x22\x19\x00\x00\x00\x01\xBC', 
            'Off' : b'\x08\x22\x19\x00\x00\x00\x00\xBD'
        }

        HDMIFullRangeCmdString = ValueStateValues[value]
        self.__SetHelper('HDMIFullRange', HDMIFullRangeCmdString, value, qualifier)

    def UpdateHDMIFullRange(self, value, qualifier):

        ValueStateValues = {
            0x31 : 'On', 
            0x30 : 'Off'
            }

        HDMIFullRangeCmdString = b'\x04\x21\x1A\xC1'
        res = self.__UpdateHelper('HDMIFullRange', HDMIFullRangeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[20]]
                self.WriteStatus('HDMIFullRange', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['HDMI Full Range : Invalid/Unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort' : b'\x08\x22\x02\x00\x00\x00\x00\xD4', 
            'HDMI' : b'\x08\x22\x05\x00\x00\x00\x00\xD1', 
            'VGA' : b'\x08\x22\x06\x00\x00\x00\x00\xD0'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x08\x22\xFD\x00\x00\x00\x00\xD9', 
            'Off' : b'\x08\x22\xFE\x00\x00\x00\x00\xD8', 
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x10' : 'On', 
            b'\x1A' : 'Off', 
            b'\x11' : 'Sleep'
        }

        PowerCmdString = b'\x04\x21\x16\xC5'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0:1]]
                self.WriteStatus('Power', value, qualifier)               
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/Unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CheckSum = 256 - 51 - value
            VolumeCmdString = pack('>BBBBBBBB', 0x08, 0x22, 0x09, 0x00, 0x00, 0x00, value, CheckSum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x04\x21\x0F\xCC'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                if res[17] == 3:
                    value = int(res[11:12].decode() + res[12:13].decode())
                elif res[18] == 3:
                    value = int(res[11:12].decode() + res[12:13].decode() + res[13:14].decode())
                else:
                    value = int(res[11:12].decode())
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {b'\x03\x0B\xF2' : 'Error occurred.'}

        if response in DEVICE_ERROR_CODES:
            errorString = '{0} Error: {1} {2}'.format(sourceCmdName, response, DEVICE_ERROR_CODES[response])
            self.Error([errorString])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.CommandDeliRex[command])
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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