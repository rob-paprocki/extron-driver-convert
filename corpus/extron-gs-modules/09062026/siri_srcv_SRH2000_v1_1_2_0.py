from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
            'CategoryMode': {'Status': {}},
            'Channel': {'Status': {}},
            'NormalCategory': {'Status': {}},
            'PowerMode': {'Status': {}},
            'RestrictedCategory': {'Status': {}},
            'TruncatedCategory': {'Status': {}},
            }

        self.Sequence = 0

        self.GetCategoryMode = re.compile(b'\xA4\x03\x00[\x00-\xFF]\x80\x00\x60\x3B\x00\x00(\x00|\x01|\x02)\xFF')
        self.GetChannel = re.compile(b'\xA4\x03\x00[\x00-\xFF]\x80\x00\x60\x08\x00\x00[\x00-\xDF][\s\S]+')
        self.GetNormalCategory = re.compile(b'\xA4\x03\x00[\x00-\xFF]\x80\x00\x60\x09\x00\x00[\x00-\x33][\s\S]+')
        self.GetPowerMode = re.compile(b'\xA4\x03\x00[\x00-\xFF]\x80\x00\x60\x07\x00\x00(\x00|\x01|\x02|\x03)\xFF')
        self.GetRestrictedCategory = re.compile(b'\xA4\x03\x00[\x00-\xFF]\x80\x00\x60\x09\x00\x00[\x00-\x0B][\s\S]+')
        self.GetTruncatedCategory = re.compile(b'\xA4\x03\x00[\x00-\xFF]\x80\x00\x60\x09\x00\x00[\x00-\x1F][\s\S]+')

        self.CommandDeliRex = {
            'CategoryMode': self.GetCategoryMode,
            'Channel': self.GetChannel,
            'NormalCategory': self.GetNormalCategory,
            'PowerMode': self.GetPowerMode,
            'RestrictedCategory': self.GetRestrictedCategory,
            'TruncatedCategory': self.GetTruncatedCategory
            }

    def SetHeader(self, commandstring):
        self.Sequence = self.Sequence + 1 if self.Sequence < 255 else 0

        if self.Sequence == '\xA4':
            commandstring = b'\xA4\x03\x00\x1B\x53\x00' + commandstring
        elif self.Sequence == '\x1B':
            commandstring = b'\xA4\x03\x00\x1B\x1B\x00' + commandstring
        else:
            commandstring = b'\xA4\x03\x00' + bytes([self.Sequence]) + b'\x00' + commandstring
        return commandstring

    def SetCategoryMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0x00,
            'Restricted': 0x01,
            'Truncated': 0x02
        }

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x03 + 0x00 + 0x24 + ValueStateValues[value])
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            CategoryModeCmdString = pack('>6B', 0x03, 0x00, 0x24, ValueStateValues[value], 0x1B, 0x53)
        elif cks == 0x1B:
            CategoryModeCmdString = pack('>6B', 0x03, 0x00, 0x24, ValueStateValues[value], 0x1B, 0x1B)
        else:
            CategoryModeCmdString = pack('>5B', 0x03, 0x00, 0x24, ValueStateValues[value], cks)

        CategoryModeCmdString = self.SetHeader(CategoryModeCmdString)

        self.__SetHelper('CategoryMode', CategoryModeCmdString, value, qualifier)

    def UpdateCategoryMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Normal',
            b'\x01': 'Restricted',
            b'\x02': 'Truncated'
        }

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x02 + 0x40 + 0x3B)
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            CategoryModeCmdString = pack('>5B', 0x02, 0x40, 0x3B, 0x1B, 0x53)
        elif cks == 0x1B:
            CategoryModeCmdString = pack('>5B', 0x02, 0x40, 0x3B, 0x1B, 0x1B)
        else:
            CategoryModeCmdString = pack('>4B', 0x02, 0x40, 0x3B, cks)

        CategoryModeCmdString = self.SetHeader(CategoryModeCmdString)
        res = self.__UpdateHelper('CategoryMode', CategoryModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10:11]]
                self.WriteStatus('CategoryMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Category Mode: Invalid/unexpected response'])

    def SetChannel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 223
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x00 + 0x0A + value + 0x01 + 0x00 + 0x00)
            cks = (0x100 - addALL) & 0xFF

            if cks == 0xA4:
                ChannelCmdString = pack('>9B', 0x06, 0x00, 0x0A, value, 0x01, 0x00, 0x00, 0x1B, 0x53)
            elif cks == 0x1B:
                ChannelCmdString = pack('>9B', 0x06, 0x00, 0x0A, value, 0x01, 0x00, 0x00, 0x1B, 0x1B)
            else:
                ChannelCmdString = pack('>8B', 0x06, 0x00, 0x0A, value, 0x01, 0x00, 0x00, cks)

            ChannelCmdString = self.SetHeader(ChannelCmdString)

            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def UpdateChannel(self, value, qualifier):

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x40 + 0x08 + 0x00 + 0x00 + 0x00 + 0x00)
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            ChannelCmdString = pack('>9B', 0x06, 0x40, 0x08, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x53)
        elif cks == 0x1B:
            ChannelCmdString = pack('>9B', 0x06, 0x40, 0x08, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x1B)
        else:
            ChannelCmdString = pack('>8B', 0x06, 0x40, 0x08, 0x00, 0x00, 0x00, 0x00, cks)

        ChannelCmdString = self.SetHeader(ChannelCmdString)
        res = self.__UpdateHelper('Channel', ChannelCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10])
                self.WriteStatus('Channel', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Channel: Invalid/unexpected response'])

    def SetNormalCategory(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 51
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x00 + 0x0B + value + 0x01 + 0x00 + 0x00)
            cks = (0x100 - addALL) & 0xFF

            if cks == 0xA4:
                NormalCategoryCmdString = pack('>9B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, 0x1B, 0x53)
            elif cks == 0x1B:
                NormalCategoryCmdString = pack('>9B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, 0x1B, 0x1B)
            else:
                NormalCategoryCmdString = pack('>8B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, cks)

            NormalCategoryCmdString = self.SetHeader(NormalCategoryCmdString)

            self.__SetHelper('NormalCategory', NormalCategoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetNormalCategory')

    def UpdateNormalCategory(self, value, qualifier):

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x40 + 0x09 + 0x00 + 0x00 + 0x00 + 0x00)
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            NormalCategoryCmdString = pack('>9B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x53)
        elif cks == 0x1B:
            NormalCategoryCmdString = pack('>9B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x1B)
        else:
            NormalCategoryCmdString = pack('>8B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, cks)

        NormalCategoryCmdString = self.SetHeader(NormalCategoryCmdString)
        res = self.__UpdateHelper('NormalCategory', NormalCategoryCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10])
                self.WriteStatus('NormalCategory', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Normal Category: Invalid/unexpected response'])

    def SetPowerMode(self, value, qualifier):

        ValueStateValues = {
            'Sleep Mode': 0x00,
            'Safe Shutdown Mode': 0x01,
            'Managed Power Mode': 0x02,
            'Full Mode': 0x03
        }

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x03 + 0x00 + 0x08 + ValueStateValues[value])
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            PowerModeCmdString = pack('>6B', 0x03, 0x00, 0x08, ValueStateValues[value], 0x1B, 0x53)
        elif cks == 0x1B:
            PowerModeCmdString = pack('>6B', 0x03, 0x00, 0x08, ValueStateValues[value], 0x1B, 0x1B)
        else:
            PowerModeCmdString = pack('>5B', 0x03, 0x00, 0x08, ValueStateValues[value], cks)

        PowerModeCmdString = self.SetHeader(PowerModeCmdString)
        self.__SetHelper('PowerMode', PowerModeCmdString, value, qualifier)

    def UpdatePowerMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Sleep Mode',
            b'\x01': 'Safe Shutdown Mode',
            b'\x02': 'Managed Power Mode',
            b'\x03': 'Full Mode'
        }

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x02 + 0x40 + 0x07)
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            PowerModeCmdString = pack('>5B', 0x02, 0x40, 0x07, 0x1B, 0x53)
        elif cks == 0x1B:
            PowerModeCmdString = pack('>5B', 0x02, 0x40, 0x07, 0x1B, 0x1B)
        else:
            PowerModeCmdString = pack('>4B', 0x02, 0x40, 0x07, cks)

        PowerModeCmdString = self.SetHeader(PowerModeCmdString)
        res = self.__UpdateHelper('PowerMode', PowerModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[10:11]]
                self.WriteStatus('PowerMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power Mode: Invalid/unexpected response'])

    def SetRestrictedCategory(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 11
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x00 + 0x0B + value + 0x01 + 0x00 + 0x00)
            cks = (0x100 - addALL) & 0xFF

            if cks == 0xA4:
                RestrictedCategoryCmdString = pack('>9B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, 0x1B, 0x53)
            elif cks == 0x1B:
                RestrictedCategoryCmdString = pack('>9B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, 0x1B, 0x1B)
            else:
                RestrictedCategoryCmdString = pack('>8B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, cks)

            RestrictedCategoryCmdString = self.SetHeader(RestrictedCategoryCmdString)
            self.__SetHelper('RestrictedCategory', RestrictedCategoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRestrictedCategory')

    def UpdateRestrictedCategory(self, value, qualifier):

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x40 + 0x09 + 0x00 + 0x00 + 0x00 + 0x00)
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            RestrictedCategoryCmdString = pack('>9B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x53)
        elif cks == 0x1B:
            RestrictedCategoryCmdString = pack('>9B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x1B)
        else:
            RestrictedCategoryCmdString = pack('>8B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, cks)

        RestrictedCategoryCmdString = self.SetHeader(RestrictedCategoryCmdString)
        res = self.__UpdateHelper('RestrictedCategory', RestrictedCategoryCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10])
                self.WriteStatus('RestrictedCategory', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Restricted Category: Invalid/unexpected response'])

    def SetTruncatedCategory(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x00 + 0x0B + value + 0x01 + 0x00 + 0x00)
            cks = (0x100 - addALL) & 0xFF

            if cks == 0xA4:
                TruncatedCategoryCmdString = pack('>9B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, 0x1B, 0x53)
            elif cks == 0x1B:
                TruncatedCategoryCmdString = pack('>9B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, 0x1B, 0x1B)
            else:
                TruncatedCategoryCmdString = pack('>8B', 0x06, 0x00, 0x0B, value, 0x01, 0x00, 0x00, cks)

            TruncatedCategoryCmdString = self.SetHeader(TruncatedCategoryCmdString)
            self.__SetHelper('TruncatedCategory', TruncatedCategoryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTruncatedCategory')

    def UpdateTruncatedCategory(self, value, qualifier):

        addALL = (0xA4 + 0x03 + 0x00 + self.Sequence + 0x00 + 0x06 + 0x40 + 0x09 + 0x00 + 0x00 + 0x00 + 0x00)
        cks = (0x100 - addALL) & 0xFF

        if cks == 0xA4:
            TruncatedCategoryCmdString = pack('>9B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x53)
        elif cks == 0x1B:
            TruncatedCategoryCmdString = pack('>9B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, 0x1B, 0x1B)
        else:
            TruncatedCategoryCmdString = pack('>8B', 0x06, 0x40, 0x09, 0x00, 0x00, 0x00, 0x00, cks)

        TruncatedCategoryCmdString = self.SetHeader(TruncatedCategoryCmdString)
        res = self.__UpdateHelper('TruncatedCategory', TruncatedCategoryCmdString, value, qualifier)
        if res:
            try:
                value = int(res[10])
                self.WriteStatus('TruncatedCategory', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Truncated Category: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.CommandDeliRex[command])
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

