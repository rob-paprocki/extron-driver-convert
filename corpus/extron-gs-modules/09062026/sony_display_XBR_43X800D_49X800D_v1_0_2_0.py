from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionAnalog': {'Status': {}},
            'ClosedCaptionDigital': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Standby': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.UpdateDelim = {
            'Input': b'(^\x70(\x00|\x01|\x02|\x03|\x04)(\x02|\x03)(\x01|\x02|\x03|\x04|\x05){1,2}[\x00-\xFF]$)',
            'Power': b'(^\x70(\x00|\x01|\x02|\x03|\x04)\x02(\x01|\x00)[\x00-\xFF]$)',
            'Volume': b'(^\x70(\x00|\x01|\x02|\x03|\x04)\x03\x01[\x00-\xFF]{2}$)',
        }

        self.CompiledRegex = {k: re.compile(v) for k, v in self.UpdateDelim.items()}

    def CalCRC(self, Data):
        Crc = 0
        for i in range(0, len(Data)):
            if type(Data[i]) is int:
                Crc += Data[i]
            else:
                Crc += ord(Data[i])
        return Crc & 0xFF

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Wide Zoom': 0x00,
            'Zoom': 0x02,
            'Normal': 0x03,
            'Normal (PC)': 0x05,
            'Full 1': 0x01,
            'Full 2': 0x06,
            'Full 3': 0x07
        }

        Data = [0x8C, 0x00, 0x44, 0x03, 0x01, ValueStateValues[value]]
        AspectRatioCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        Data = [0x8C, 0x00, 0x06, 0x03, 0x01, ValueStateValues[value]]
        AudioMuteCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        Data = [0x8C, 0x00, 0x10, 0x03, 0x01, ValueStateValues[value]]
        ClosedCaptionCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'CC1': 0x01,
            'CC2': 0x02,
            'CC3': 0x03,
            'CC4': 0x04,
            'Text1': 0x05,
            'Text2': 0x06,
            'Text3': 0x07,
            'Text4': 0x08
        }

        Data = [0x8C, 0x00, 0x10, 0x04, 0x02, 0x00, ValueStateValues[value]]
        ClosedCaptionAnalogCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'CC1': 0x07,
            'CC2': 0x08,
            'CC3': 0x09,
            'CC4': 0x0a,
            'Service1': 0x01,
            'Service2': 0x02,
            'Service3': 0x03,
            'Service4': 0x04,
            'Service5': 0x05,
            'Service6': 0x06
        }

        Data = [0x8C, 0x00, 0x10, 0x04, 0x02, 0x01, ValueStateValues[value]]
        ClosedCaptionDigitalCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': (0x02, 0x01),
            'Component': (0x03, 0x01),
            'HDMI 1': (0x04, 0x01),
            'HDMI 2': (0x04, 0x02),
            'HDMI 3': (0x04, 0x03),
            'HDMI 4': (0x04, 0x04)
        }

        if value == 'TV':
             InputCmdString = b'\x8C\x00\x02\x02\x01\x91'
        else:
            Data = [0x8C, 0x00, 0x02, 0x03, ValueStateValues[value][0], ValueStateValues[value][1]]
            InputCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            0x01: 'HDMI 1',
            0x02: 'HDMI 2',
            0x03: 'HDMI 3',
            0x04: 'HDMI 4'
        }

        Data = [0x83, 0x00, 0x02, 0xFF, 0xFF]
        InputCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[2] == 0x02 and res[3] == 0x01:
                    self.WriteStatus('Input', 'TV', qualifier)
                elif res[2] == 0x03 and res[3] == 0x02:
                    self.WriteStatus('Input', 'Video', qualifier)
                elif res[2] == 0x03 and res[3] == 0x03:
                    self.WriteStatus('Input', 'Component', qualifier)
                elif res[2] == 0x03 and res[3] == 0x04:
                    value = ValueStateValues[res[4]]
                    self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        Data = [0x8C, 0x00, 0x00, 0x02, ValueStateValues[value]]
        PowerCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Power', PowerCmdString, value, qualifier)  # Protocol has note about waiting for 20 seconds

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        Data = [0x83, 0x00, 0x00, 0xFF, 0xFF]
        PowerCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'Enable': 0x01,
            'Disable': 0x00
        }

        Data = [0x8C, 0x00, 0x01, 0x02, ValueStateValues[value]]
        StandbyCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x00,
            'Off': 0x01,
        }

        Data = [0x8C, 0x00, 0x0D, 0x03, 0x01, ValueStateValues[value]]
        VideoMuteCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Data = [0x8C, 0x00, 0x05, 0x03, 0x01, value]
            VolumeCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        Data = [0x83, 0x00, 0x05, 0xFF, 0xFF]
        VolumeCmdString = b''.join(pack('B', x) for x in Data) + pack('B', self.CalCRC(Data))
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[4])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: "Limit Over (Over max value).",
            0x02: "Limit Over (Under min value).",
            0x03: "Command Cancelled.",
            0x04: "Parse Error."
            }
        if response[1] in DEVICE_ERROR_CODES:
            self.Error(["Unrecognized Command {0} and error is {1}".format(sourceCmdName, DEVICE_ERROR_CODES[response[1]])])
            return b''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=3)
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        regex = self.CompiledRegex[command]
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
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