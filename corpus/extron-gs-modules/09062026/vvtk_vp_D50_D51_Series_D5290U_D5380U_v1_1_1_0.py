# How to use the Module in Main script
#
# import module by name of the py file
# import module
#
# Declare controller
# dvPro350 = ProcessorDevice('dvPro350')
#
# Specify communication settings if Serial
# SerialPort1 = module.SerialClass(dvPro350, 'COM1', Baud=19200, Model='SMX 200')
#
# Specify communication settings if Ethernet (for TCP)
# EthernetPort1 = module.EthernetClass('10.10.10.10', 23, Model='SMX 200')
#
# When using Ethernet Class:
# EthernetPort1.Connect() must be coded,
# Module does NOT connect to
# the device automatically.
#
# How to send a control command
# without qualifiers
# SerialPort1.Set('AudioMute', 'On')
#
# with qualifiers
# The 3rd argument (qualifier) must be specified as the example {'Input': 1}
# SerialPort1.Set('AudioMute', 'On',{'Input': 1})
#
# How  to send a control command with qualifier, but no value
# This example also show how to send multiple qualifier arguments
# SerialPort1.Set('MatrixTieCommand', None, {'Input': 1,'Ouput': 2,'TieType': 'Video'})
#
# How to send a update command
# Without qualifier
# SerialPort1.Update('AudioMute')
#
# How to send a update command
# With qualifier
# SerialPort1.Update('AudioMute',{'Input': 1})
#
# To avoid using delay after an Update command is called, it is recommended to use
# SubscribeStatus for commands that are query often, for logic or one time check
# use the example below
# How to subscribe to a command
# module.SubscribeStatus('Power',None, MethodToCall)
# any time we get status back for power from the device the Subscribed command
# 'Power' will call the Method defined 'MethodToCall'
# 'MethodToCall' must take 3 parameters (command, value, qualifier)
#
# def MethodToCall(command, value, qualifier)
#     if value == 'On':
#        Logic here
#     else:
#        Logic here
#
# All statuses of the Device will be store into a dictionary,
#
# Get Current Status of Audio Mute w/o qualifier.
# value will be equals to one of the states for the command requested
# value = SerialPort1.ReadStatus('AudioMute')
#
# Get Current Status of Audio Mute with qualifier
# value = SerialPort1.ReadStatus('AudioMute', {'Input': 1})
#
#####################################################################
# List of Models Supported by module
#####################################################################
# D5190HD,D5005,D5290U,D5380U,D5110W,D5010,D501ZAA,D501ZWAA,
#
#####################################################################
# REQUIRED VARIABLE SETTINGS
#####################################################################
# Unidirectional variable must be set to 'True' if status is not required
# Default value is 'False'
# Example: ModuleName.Unidirectional = 'True'

# ConnectionCounter variable must be set the number of queries that will be sent to the device
# before displaying 'Disconnected' if no response is received. Default value is 15.
# Example: ModuleName.ConnectionCounter = 5

# DeviceId variable must be set to the ID of the display
# DeviceId value ranges from '0' to '99'. Default value is '0'. '99' value is Broadcast.
# Example: ModuleName.DeviceId = 0

from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DeviceId = '1'

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }
        
        if self.DeviceId == 'All':
            self.DeviceId = '99'
        elif int(self.DeviceId) >= 0 and int(self.DeviceId) < 99:
            self.DeviceId = '{0:02d}'.format(int(self.DeviceId))

    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            'Fill': 'S03010',
            '16:9': 'S03012',
            '4:3': 'S03011',
            'Letterbox': 'S03013',
            'Native': 'S03014',
            '2.35:1': 'S03015'
        }

        AspectRatioCmdString = 'V{0}{1}\r'.format(self.DeviceId, ValueStateValues[value])

        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier, 3)

    def UpdateAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '0': 'Fill',
            '2': '16:9',
            '1': '4:3',
            '3': 'Letterbox',
            '4': 'Native',
            '5': '2.35:1'
        }

        AspectRatioCmdString = 'V{0}G0301\r'.format(self.DeviceId)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Aspect Ratio')

    def SetAudioMute(self, value, qualifier):
        AudioMuteCmdString = 'V{0}S0413\r'.format(self.DeviceId)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)


    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = 'V{0}S0003'.format(self.DeviceId)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)


    def SetFreeze(self, value, qualifier):
        ValueStateValues = {
            'On': 'S03041',
            'Off': 'S03040'
        }

        FreezeCmdString = 'V{0}{1}\r'.format(self.DeviceId, ValueStateValues[value])

        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier, 3)

    def UpdateFreeze(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        FreezeCmdString = 'V{0}G0304\r'.format(self.DeviceId)
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Freeze')

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'RGB 1': 'S0201',
            'RGB 2': 'S0202',
            'DVI': 'S0203',
            'Video': 'S0204',
            'S Video': 'S0205',
            'HDMI': 'S0206',
            'BNC': 'S0207',
            'Component': 'S0208',
            'DisplayPort': 'S0210'

        }

        InputCmdString = 'V{0}{1}\r'.format(self.DeviceId, ValueStateValues[value])

        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        ValueStateValues = {
            '1': 'RGB 1',
            '2': 'RGB 2',
            '3': 'DVI',
            '4': 'Video',
            '5': 'S Video',
            '6': 'HDMI',
            '7': 'BNC',
            '8': 'Component',
            '10': 'DisplayPort'
        }

        InputCmdString = 'V{0}G0220\r'.format(self.DeviceId)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier, 2)
        if res:
            try:
                value = ValueStateValues[res[1:]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Input')

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = 'V{0}G0004\r'.format(self.DeviceId)
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier, 4)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('LampUsage', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Lamp Usage')

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Menu': 'S0411',
            'Up': 'S0401',
            'Down': 'S0402',
            'Left': 'S0403',
            'Right': 'S0404',
            'Enter': 'S0420',
            'Exit': 'S0406'
        }

        MenuNavigationCmdString = 'V{0}{1}\r'.format(self.DeviceId, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier, 3)


    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': 'S0001',
            'Off': 'S0002',
        }

        PowerCmdString = 'V{0}{1}\r'.format(self.DeviceId, ValueStateValues[value])

        self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)

    def UpdatePower(self, value, qualifier):
        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
            '3': 'Cooling Down'
        }

        PowerCmdString = 'V{0}G0007\r'.format(self.DeviceId)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Power')

    def SetVideoMute(self, value, qualifier):
        ValueStateValues = {
            'On': 'S03021',
            'Off': 'S03020'
        }

        VideoMuteCmdString = 'V{0}{1}\r'.format(self.DeviceId, ValueStateValues[value])

        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 3)

    def UpdateVideoMute(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = 'V{0}G0302\r'.format(self.DeviceId)
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1:]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Video Mute')

    def SetVolume(self, value, qualifier):
        VolumeConstraints = {
            'Min': 0,
            'Max': 10
        }

        if VolumeConstraints['Min'] <= int(value) <= VolumeConstraints['Max']:
            VolumeCmdString = 'V{0}S0305{1}\r'.format(self.DeviceId, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'V{0}G0305\r'.format(self.DeviceId)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier, 2)
        if res:
            try:
                value = int(res[1:])
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid response for Volume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'F' in response:
            print('{0} {1}'.format(sourceCmdName, 'Fail'))
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=re.compile(b'P|F'))
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + str(value), res.decode())
            
    def __UpdateHelper(self, command, commandstring, value, qualifier, length=1):

        UpdateRegex = {
            'AspectRatio': re.compile(b'F|P[0-5]'),
            'Freeze': re.compile(b'F|P[01]'),
            'Input': re.compile(b'F|P[0-9]{' + str(length).encode() + b'}'),
            'LampUsage': re.compile(b'F|P[0-9]{' + str(length).encode() + b'}'),
            'Power': re.compile(b'F|P[123]'),
            'VideoMute': re.compile(b'F|P[01]'),
            'Volume': re.compile(b'F|P[0-9]{' + str(length).encode() + b'}')
            }

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=UpdateRegex[command])
            if not res:
                if length <= 1:
                    return ''
                else:
                    return self.__UpdateHelper(command, commandstring, value, qualifier, length - 1)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

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

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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
