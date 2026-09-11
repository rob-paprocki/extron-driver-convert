from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
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
            'Level': {'Parameters':['Group'], 'Status': {}},
            'LightIntensity': {'Parameters':['Group'], 'Status': {}},
            'PresetRecall': {'Parameters':['Group'], 'Status': {}},
            'PresetSave': {'Parameters':['Group'], 'Status': {}},
            }





    def SetLevel(self, value, qualifier):

        GroupStates = {
            '0' : 0x80, 
            '1' : 0x82, 
            '2' : 0x84, 
            '3' : 0x86, 
            '4' : 0x88, 
            '5' : 0x8A, 
            '6' : 0x8C, 
            '7' : 0x8E, 
            '8' : 0x90, 
            '9' : 0x92, 
            '10' : 0x94, 
            '11' : 0x96, 
            '12' : 0x98, 
            '13' : 0x9A, 
            '14' : 0x9C, 
            '15' : 0x9E,
            'All' : 0xFE
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 65
            }


        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if value > 0:
                hexValue = 124 + 2 * value
            else:
                hexValue = 0

            LevelCmdString = self.__CommandWithChecksum(pack('<BBBBBB', 0xA3, 0x00, 0x00, 0x00, GroupStates[qualifier['Group']], hexValue))
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevel')
    def UpdateLevel(self, value, qualifier):


        GroupStates = {
            '0' : 0x81, 
            '1' : 0x83, 
            '2' : 0x85, 
            '3' : 0x87, 
            '4' : 0x89, 
            '5' : 0x8B, 
            '6' : 0x8D, 
            '7' : 0x8F, 
            '8' : 0x91, 
            '9' : 0x93, 
            '10' : 0x95, 
            '11' : 0x97, 
            '12' : 0x99, 
            '13' : 0x9B, 
            '14' : 0x9D, 
            '15' : 0x9F
        }

        GroupValue = qualifier['Group']
        if not GroupValue == 'All':
            LevelCmdString = self.__CommandWithChecksum(pack('<BBBBBB', 0x83, 0x00, 0x00, 0x00, GroupStates[GroupValue], 0xA0))
            res = self.__UpdateHelper('Level', LevelCmdString, value, qualifier)
            if not res == '':
                try:
                    if res == 0:
                        value = 0
                    else:
                        value = int((res - 124) / 2)
                    self.WriteStatus('Level', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Level: Invalid/unexpected response'])
        else:
            self.Discard('Inappropriate Command for UpdateLevel')

    def SetLightIntensity(self, value, qualifier):

        GroupStates = {
            '0' : b'\x81', 
            '1' : b'\x83', 
            '2' : b'\x85', 
            '3' : b'\x87', 
            '4' : b'\x89', 
            '5' : b'\x8B', 
            '6' : b'\x8D', 
            '7' : b'\x8F', 
            '8' : b'\x91', 
            '9' : b'\x93', 
            '10' : b'\x95', 
            '11' : b'\x97', 
            '12' : b'\x99', 
            '13' : b'\x9B', 
            '14' : b'\x9D', 
            '15' : b'\x9F',
            'All' : b'\xFF'
        }

        ValueStateValues = {
            'Step Up'   : b'\x03', 
            'Step Down' : b'\x04', 
            'Maximum'   : b'\x05', 
            'Minimum'   : b'\x06', 
            'Off'       : b'\x00'
        }

        LightIntensityCmdString = self.__CommandWithChecksum(b'\xA3\x00\x00\x00' + GroupStates[qualifier['Group']] + ValueStateValues[value])
        self.__SetHelper('LightIntensity', LightIntensityCmdString, value, qualifier)


    def SetPresetRecall(self, value, qualifier):

        GroupStates = {
            '0' : b'\x81', 
            '1' : b'\x83', 
            '2' : b'\x85', 
            '3' : b'\x87', 
            '4' : b'\x89', 
            '5' : b'\x8B', 
            '6' : b'\x8D', 
            '7' : b'\x8F', 
            '8' : b'\x91', 
            '9' : b'\x93', 
            '10' : b'\x95', 
            '11' : b'\x97', 
            '12' : b'\x99', 
            '13' : b'\x9B', 
            '14' : b'\x9D', 
            '15' : b'\x9F',
            'All' : b'\xFF'
        }

        ValueStateValues = {
            '1' : b'\x10', 
            '2' : b'\x11', 
            '3' : b'\x12', 
            '4' : b'\x13', 
            '5' : b'\x14', 
            '6' : b'\x15', 
            '7' : b'\x16', 
            '8' : b'\x17', 
            '9' : b'\x18', 
            '10' : b'\x19', 
            '11' : b'\x1A', 
            '12' : b'\x1B', 
            '13' : b'\x1C', 
            '14' : b'\x1D', 
            '15' : b'\x1E', 
            '16' : b'\x1F'
        }

        PresetRecallCmdString = self.__CommandWithChecksum(b'\xA3\x00\x00\x00' + GroupStates[qualifier['Group']] + ValueStateValues[value])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)


    def SetPresetSave(self, value, qualifier):

        GroupStates = {
            '0' : b'\x81', 
            '1' : b'\x83', 
            '2' : b'\x85', 
            '3' : b'\x87', 
            '4' : b'\x89', 
            '5' : b'\x8B', 
            '6' : b'\x8D', 
            '7' : b'\x8F', 
            '8' : b'\x91', 
            '9' : b'\x93', 
            '10' : b'\x95', 
            '11' : b'\x97', 
            '12' : b'\x99', 
            '13' : b'\x9B', 
            '14' : b'\x9D', 
            '15' : b'\x9F',
            'All' : b'\xFF'
        }

        ValueStateValues = {
            '1' : b'\x40', 
            '2' : b'\x41', 
            '3' : b'\x42', 
            '4' : b'\x43', 
            '5' : b'\x44', 
            '6' : b'\x45', 
            '7' : b'\x46', 
            '8' : b'\x47', 
            '9' : b'\x48', 
            '10' : b'\x49', 
            '11' : b'\x4A', 
            '12' : b'\x4B', 
            '13' : b'\x4C', 
            '14' : b'\x4D', 
            '15' : b'\x4E', 
            '16' : b'\x4F'
        }

        GroupValue = GroupStates[qualifier['Group']]
        InitialCmdString = self.__CommandWithChecksum(b'\xA3\x00\x00\x00' + GroupValue + b'\x21')
        PresetSaveCmdString = self.__CommandWithChecksum(b'\xA3\x00\x00\x00' + GroupValue + ValueStateValues[value])

        self.__SetHelper('PresetSave', InitialCmdString, value, qualifier)
        self.__SetHelper('PresetSave', InitialCmdString, value, qualifier)
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)


    def __CommandWithChecksum(self, command):

        checksum = 0x00
        for x in command:
            checksum = checksum ^ x
        return command + pack('<B', checksum)

    def __CheckResponseForErrors(self, sourceCmdName, response):


        DEVICE_ERROR_CODES = {
            1 : 'Checksum Error',
            2 : 'Short Circuit',
            3 : 'Receive Error'
            }

        ErrorCheck = DEVICE_ERROR_CODES.get(response)
        if ErrorCheck:
            self.Error(['Command: {0}, Error: {1}'.format(sourceCmdName, ErrorCheck)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            return self.__CheckResponseForErrors(command, res[1])

            

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

