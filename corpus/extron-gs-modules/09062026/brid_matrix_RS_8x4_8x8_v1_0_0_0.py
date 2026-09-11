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
        self.OutputSize = 8
        self.Models = {
            'RS 8x8': self.brid_15_3271_8,
            'RS 8x4': self.brid_15_3271_4,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MatrixStatus': { 'Status': {}},
            'InputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Output'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            }



        self.OutputStatus = ['0' for i in range(0, self.OutputSize)]


    def __SetMatrixStatus(self, output, newInput, tag):

        
        oldInput = self.OutputStatus[int(output)-1]

        if oldInput != newInput:
            self.WriteStatus('OutputTieStatus', newInput, {'Output':output})
            for i in range(1, self.InputSize+1):
                if newInput == str(i):
                    self.WriteStatus('InputTieStatus', 'Tied', {'Input':newInput, 'Output':output})
                else:
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input':str(i), 'Output':output})#setting the new input tie status              
            self.OutputStatus[int(output)-1] = newInput
        else:
            self.OnConnected()


    def UpdateMatrixStatus(self, value, qualifier):

        MatrixStatusCmdString = '!03010300000000*58?'
        res = self.__UpdateHelper('MatrixStatus', MatrixStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == self.ResSize:                    
                    OutputList = res.decode()[15:-4].split(',')
                    for i in range(1,self.OutputSize+1):
                        self.__SetMatrixStatus(str(i), str(int(OutputList[i-1])+1), 'Tied')
                else:
                    self.Error(['Incomplete Response'])
            except (ValueError, KeyError, IndexError):
                self.Error(['Matrix Tie Status: Invalid/unexpected response'])


    def SetMatrixTieCommand(self, value, qualifier):

        Input = int(qualifier['Input']) - 1
        Output = int(qualifier['Output']) -1
        if 0<=Input<=self.InputSize and 0<=Output<=self.OutputSize:
            if Input == 0:
                DataSum = 180 + Output
            elif Output == 0:
                DataSum = 180 + Input
            else:
                DataSum = 164+ Input + Output
            CheckSum = '{0:02X}'.format((~DataSum) + 256)
            MatrixTieCommandCmdString = '!03010000000{0}0{1}*{2}?'.format(Output, Input, CheckSum)
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)


    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : '!03010400000000*47?', 
            '2' : '!03010400000100*56?', 
            '3' : '!03010400000200*55?', 
            '4' : '!03010400000300*54?'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)


    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1' : '!03010500000000*46?', 
            '2' : '!03010500000100*55?', 
            '3' : '!03010500000200*54?', 
            '4' : '!03010500000300*53?'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)


    def __CheckResponseForErrors(self, sourceCmdName, response):
        if response[5] == '8':
            self.Error(['{0}: Communication error/Invalid checksum or value'.format(sourceCmdName)])
            response=''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or 'Preset' in command:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='?')
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command , res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='?')
            
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                return self.__CheckResponseForErrors(command, res)

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def brid_15_3271_4(self):

        self.InputSize = 8
        self.OutputSize = 4
        self.ResSize = 30
        


    def brid_15_3271_8(self):

        self.InputSize = 8
        self.OutputSize = 8
        self.ResSize = 42



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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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