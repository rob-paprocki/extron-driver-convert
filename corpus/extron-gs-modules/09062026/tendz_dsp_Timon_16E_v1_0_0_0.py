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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Delay': { 'Status': {}},
            'DelayBypass': { 'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'LoadScene': { 'Status': {}},
            'MixerGain': {'Parameters':['Input'], 'Status': {}},
            'NoiseGateBypass': { 'Status': {}},
            'OutputGain': {'Parameters':['Output'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'SaveScene': { 'Status': {}},
            }


    def GetCmdString_set (self, Processor_ID, Processor_Index, Item, V0, V1, V2, V3, Start_Channel, End_Channel):
        Checksum  = (Processor_ID + Processor_Index + Item + V0 + V1 + V2 + V3 + Start_Channel + End_Channel) & 0xFF
        CmdString = bytes([0xA5, 0xAC, Processor_ID, Processor_Index, Item, V0, V1, V2, V3, Start_Channel, End_Channel, Checksum])
        return CmdString

    def GetCmdString_query (self, Processor_ID, Processor_Index, Item, V0, V1, V2, V3, Start_Channel, End_Channel):
        Checksum  = (Processor_ID + Processor_Index + Item + V0 + V1 + V2 + V3 + Start_Channel + End_Channel) & 0xFF
        CmdString = bytes([0xA5, 0xAD, Processor_ID, Processor_Index, Item, V0, V1, V2, V3, Start_Channel, End_Channel, Checksum])
        return CmdString

    def SetDelay(self, value, qualifier):

        if 0 <= value <= 2000:
            V0 = int(value/256) & 0xFF  # value: short high
            V1 = int(value%256) & 0xFF  # value: short low
            DelayCmdString = self.GetCmdString_set(0x07,0x00,0x02,V0,V1,0x00,0x00,0x00,0x00)
            self.__SetHelper('Delay', DelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelay')

    def SetDelayBypass(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        V0 = ValueStateValues[value]
        DelayBypassCmdString = self.GetCmdString_set(0x07,0x00,0x01,V0,0x00,0x00,0x00,0x00,0x00)
        self.__SetHelper('DelayBypass', DelayBypassCmdString, value, qualifier)
    def SetInputGain(self, value, qualifier):

        Input = qualifier['Input']
        if 1 <= int(Input) <= 8 and -72 <= value <= 12:
            temp = (value * 100) if (value > 0) else (0x10000 + value * 100)
            V0  = int(temp/256) & 0xFF     # value: short high
            V1  = int(temp%256) & 0xFF     # value: short low
            InputGainCmdString = self.GetCmdString_set(0x0C, 0x00, 0x04, V0, V1, 0x00, 0x00, int(Input)-1, int(Input)-1)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        Input = qualifier['Input']
        if 1 <= int(Input) <= 8:
            InputGainCmdString = self.GetCmdString_query(0x0C, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, int(Input)-1, int(Input)-1)
            res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            if res:
                try:
                    val = int.from_bytes(res[5:7],'big')
                    value = int(val/100) if val<=1200 else int((val-0x10000)/100)
                    if -72 <= value <= 12:
                        self.WriteStatus('InputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Input Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x00, 
            'Off' : 0x01
        }

        Input = qualifier['Input']
        if 1 <= int(Input) <= 8:
            V0 = ValueStateValues[value]
            InputMuteCmdString = self.GetCmdString_set(0x0C, 0x00, 0x02, V0, 0x00, 0x00, 0x00, int(Input)-1, int(Input)-1)
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        ValueStateValues = {
            0 : 'On', 
            1 : 'Off'
        }
        Input = qualifier['Input']
        if 1 <= int(Input) <= 8:
            InputMuteCmdString = self.GetCmdString_query(0x0C, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, int(Input)-1, int(Input)-1)
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[5]]
                    self.WriteStatus('InputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def SetLoadScene(self, value, qualifier):

        if 0 <= int(value) <= 8:
            V1 = int(value)
            LoadSceneCmdString = self.GetCmdString_set(0x00, 0x00, 0x01, 0x01, V1, 0x00, 0x00, 0x00, 0x00)
            self.__SetHelper('LoadScene', LoadSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadScene')
    def SetMixerGain(self, value, qualifier):

        Input = qualifier['Input']
        if 1 <= int(Input) <= 8 and -72 <= value <= 12:
            V0 = int(Input)-1
            temp = (value * 100) if (value > 0) else (0x10000 + value * 100)
            V1  = int(temp/256) & 0xFF     # value: short high
            V2  = int(temp%256) & 0xFF     # value: short low
            MixerGainCmdString = self.GetCmdString_set(0x06, 0x00, 0x04, V0, V1, V2, 0x00, 0x00, 0x00)
            self.__SetHelper('MixerGain', MixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerGain')

    def UpdateMixerGain(self, value, qualifier):

        Input = qualifier['Input']
        if 1 <= int(Input) <= 8:
            V0 = int(Input)-1
            MixerGainCmdString = self.GetCmdString_query(0x06, 0x00, 0x04, V0, 0x00, 0x00, 0x00, 0x00, 0x00)
            res = self.__UpdateHelper('MixerGain', MixerGainCmdString, value, qualifier)
            if res:
                try:
                    val = int.from_bytes(res[6:8],'big')
                    value = int(val/100) if val<=1200 else int((val-0x10000)/100)
                    if -72 <= value <= 12:
                        self.WriteStatus('MixerGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Mixer Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMixerGain')

    def SetNoiseGateBypass(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x01, 
            'Off' : 0x00
        }

        V0 =ValueStateValues[value]
        NoiseGateBypassCmdString = self.GetCmdString_set(0x01, 0x00, 0x01, V0, 0x00, 0x00, 0x00, 0x00, 0x00)
        self.__SetHelper('NoiseGateBypass', NoiseGateBypassCmdString, value, qualifier)

    def UpdateNoiseGateBypass(self, value, qualifier):

        ValueStateValues = {
            1 : 'On', 
            0 : 'Off'
        }

        NoiseGateBypassCmdString = self.GetCmdString_query(0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        res = self.__UpdateHelper('NoiseGateBypass', NoiseGateBypassCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('NoiseGateBypass', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Noise Gate Bypass: Invalid/unexpected response'])

    def SetOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if 1 <= int(Output) <= 8 and -72 <= value <= 12:
            temp = (value * 100) if (value > 0) else (0x10000 + value * 100)
            V0  = int(temp/256) & 0xFF     # value: short high
            V1  = int(temp%256) & 0xFF     # value: short low
            OutputGainCmdString = self.GetCmdString_set(0x0D, 0x00, 0x03, V0, V1, 0x00, 0x00, int(Output)-1, int(Output)-1 )
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if 1 <= int(Output) <= 8:
            OutputGainCmdString = self.GetCmdString_query(0x0D, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, int(Output)-1, int(Output)-1)
            res = self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
            if res:
                try:
                    val = int.from_bytes(res[5:7],'big')
                    value = int(val/100) if val<=1200 else int((val-0x10000)/100)
                    if -72 <= value <= 12:
                        self.WriteStatus('OutputGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Output Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x00, 
            'Off' : 0x01
        }

        Output = qualifier['Output']
        if 1 <= int(Output) <= 8:
            V0 = ValueStateValues[value]
            OutputMuteCmdString = self.GetCmdString_set(0x0D, 0x00, 0x01, V0, 0x00, 0x00, 0x00, int(Output)-1, int(Output)-1)
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        ValueStateValues = {
            0 : 'On', 
            1 : 'Off'
        }

        Output = qualifier['Output']
        if 1 <= int(Output) <= 8:
            OutputMuteCmdString = self.GetCmdString_query(0x0D, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, int(Output)-1, int(Output)-1)
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[5]]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Output Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def SetSaveScene(self, value, qualifier):

        if 0 <= int(value) <= 8:
            V0 = int(value)
            SaveSceneCmdString = self.GetCmdString_set (0x00, 0x00, 0x01, V0, 0x00, 0x00, 0x00, 0x00, 0x00)
            self.__SetHelper('SaveScene', SaveSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveScene')
    def __CheckResponseForErrors(self, sourceCmdName, response):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
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

