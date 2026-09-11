from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveSceneCommand': { 'Status': {}},
            'ChangeSceneCommand': {'Parameters':['TX Device Name'], 'Status': {}},
            'Heartbeat': { 'Status': {}},
            'Input': {'Parameters':['TX Device Name'], 'Status': {}},
            'MatrixTie': {'Parameters':['TX Device Name','RX Device Name'], 'Status': {}},
            'MultiView': {'Parameters':['RX Device Name','TX Device List'], 'Status': {}},
            'SendSerialCommand': {'Parameters':['Baud Rate','Data Bits','Stop Bits','Parity','Add Carriage Return','Command Style','Hostname'], 'Status': {}},
            'SetVideoWallSceneCommand': {'Parameters':['TX Device Name','X Position','Y Position'], 'Status': {}},
            'RXTieStatus': {'Parameters':['RX Device Name'], 'Status': {}},
            }             
        if self.Unidirectional == 'False':
            self.SourceRegex = re.compile('source info: (.*) (vga|hdmi[1-4])\r\n', re.I)
            self.RXListRegex = re.compile('(.*) (.*)\r\n')

    def IsValidString(self, str):
        if str:
            if ' ' in str:
                return False
            elif ';' in str:
                return False
            elif '_' in str:
                return False
            elif '@' in str:
                return False
            elif '*' in str:
                return False
            elif '&' in str:
                return False
            else:
                return True
        else:
            return False

    def IsValidSerialString(self, str):
        if str:
            if ';' in str:
                return False
            elif '_' in str:
                return False
            elif '@' in str:
                return False
            elif '*' in str:
                return False
            elif '&' in str:
                return False
            else:
                return True
        else:
            return False
#
    def SetActiveSceneCommand(self, value, qualifier):

        cmdString = value
        if self.IsValidString(cmdString):
            ActiveSceneCommandCmdString = 'scene active {0}\r\n'.format(cmdString)
            self.__SetHelper('ActiveSceneCommand', ActiveSceneCommandCmdString, None, qualifier)
        else:
            self.Discard('Inappropriate Command for SetActiveSceneCommand')

    def SetChangeSceneCommand(self, value, qualifier):

        cmdString = value
        TX_Name = qualifier['TX Device Name']
        if self.IsValidString(cmdString) and self.IsValidString(TX_Name):
            ChangeSceneCommandCmdString = 'scene change {0} {1}\r\n'.format(cmdString, TX_Name)
            self.__SetHelper('ChangeSceneCommand', ChangeSceneCommandCmdString, None, qualifier)
        else:
            self.Discard('Inappropriate Command for SetChangeSceneCommand')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1' : 'hdmi1', 
            'HDMI 2' : 'hdmi2', 
            'HDMI 3' : 'hdmi3', 
            'HDMI 4' : 'hdmi4', 
            'VGA'    : 'vga'
        }

        TX_Name = qualifier['TX Device Name']
        if self.IsValidString(TX_Name):
            InputCmdString = 'source set {0} {1}\r\n'.format(TX_Name, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            'hdmi1' : 'HDMI 1', 
            'hdmi2' : 'HDMI 2', 
            'hdmi3' : 'HDMI 3', 
            'hdmi4' : 'HDMI 4', 
            'vga' : 'VGA'
        }

        TX_Name = qualifier['TX Device Name']
        if self.IsValidString(TX_Name):
            InputCmdString = 'source get {0}\r\n'.format(TX_Name)
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                match = re.search(self.SourceRegex, res)
                qualifier = {}
                qualifier['TX Device Name'] = match.group(1)
                value = ValueStateValues[match.group(2)]
                self.WriteStatus('Input', value, qualifier)
            else:
                self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Inappropriate Command for UpdateInput')

    def SetMatrixTie(self, value, qualifier):

        TX_Name = qualifier['TX Device Name']
        RX_Name = qualifier['RX Device Name']

        if self.IsValidString(TX_Name) and self.IsValidString(RX_Name):
            MatrixTieCmdString = 'matrix set {0} {1}\r\n'.format(TX_Name, RX_Name)
            self.__SetHelper('MatrixTie', MatrixTieCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetMatrixTie')

    def SetMultiView(self, value, qualifier):

        TX_List = qualifier['TX Device List']
        RX_Name = qualifier['RX Device Name']
        if TX_List.replace(' ', '') and self.IsValidString(RX_Name):
            MultiViewCmdString = 'mv set {0} {1}\r\n'.format(RX_Name, TX_List)
            self.__SetHelper('MultiView', MultiViewCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetMultiView')

    def SetSendSerialCommand(self, value, qualifier):

        BaudRateStates = ['300', '600', '1200', '1800', '2400', '3600', '4800', '7200', '9600', '14400',
                          '19200', '28800', '38400', '57600', '115200']
        DataBitsStates = ['7', '8']
        StopBitsStates = ['1','2']

        ParityStates = {
            'None' : 'n', 
            'Even' : 'e', 
            'Odd' : 'o', 
            'Mark' : 'm', 
            'Space' : 's'
        }

        AddCarriageReturnStates = {
            'Enable' : 'on', 
            'Disable' : 'off'
        }

        CommandStyleStates = {
            'HEX' : 'on', 
            'ASCII' : 'off'
        }

        baud_ = qualifier['Baud Rate']
        data_ = qualifier['Data Bits']
        stop_ = qualifier['Stop Bits']
        host_ = qualifier['Hostname']

        cmdString = value
        if baud_ in BaudRateStates and data_ in DataBitsStates and stop_ in StopBitsStates and self.IsValidString(host_) and '"' not in cmdString and self.IsValidSerialString(cmdString):
            BDSP_Chars = '{0}-{1}{2}{3}'.format(baud_, data_, ParityStates[qualifier['Parity']], stop_)
            SerialCmdString = 'serial -b {0} -r {1} -h {2} "{3}" {4}\r\n'.format(BDSP_Chars, 
                                                                                 AddCarriageReturnStates[qualifier['Add Carriage Return']], 
                                                                                 CommandStyleStates[qualifier['Command Style']], cmdString, host_)
            self.__SetHelper('SendSerialCommand', SerialCmdString, None, qualifier)
        else:
            self.Discard('Inappropriate Command for SetSendSerialCommand')

    def SetSetVideoWallSceneCommand(self, value, qualifier):

        cmdString = value
        TX_Name = qualifier['TX Device Name']
        if self.IsValidString(TX_Name) and qualifier['X Position'] > 0 and qualifier['Y Position'] > 0 and self.IsValidString(cmdString):
            VideoWallSceneCmdString = 'scene set {0} {1} {2} {3}\r\n'.format(cmdString, qualifier['X Position'], qualifier['Y Position'], TX_Name)
            self.__SetHelper('SetVideoWallSceneCommand', VideoWallSceneCmdString, value, qualifier)
        else:
            self.Discard('Inappropriate Command for SetSetVideoWallSceneCommand')

    def UpdateRXTieStatus(self, value, qualifier):

        RXTieStatusCmdString = 'matrix get\r\n'
        res = self.__UpdateHelper('Heartbeat', RXTieStatusCmdString, value, qualifier)
        if res:
            tie_list = re.findall(self.RXListRegex, res[18:])
            for enum, entry in enumerate(tie_list):
                tx_name = entry[0]
                rx_name = entry[1]
                if tx_name != 'null':
                    self.WriteStatus('RXTieStatus', tx_name, {'RX Device Name' : rx_name})
                else:
                    self.WriteStatus('RXTieStatus', 'Untied', {'RX Device Name' : rx_name})
        else:
            self.Error(['RX Tie Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command + ':', res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command')
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if res: 
                return self.__CheckResponseForErrors(command, res.decode())            

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)

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

