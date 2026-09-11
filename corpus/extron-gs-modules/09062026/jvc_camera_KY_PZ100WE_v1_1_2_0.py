from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack, unpack
import time
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
        self._DeviceID = 0x81


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Focus': {'Parameters':['Speed'], 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters':['Pan Speed','Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters':['Action'], 'Status': {}},
            'Zoom': {'Parameters':['Speed'], 'Status': {}},
            }

        self.PrevSequence = 0
        self.StartSequence = 0
        self.LastResetTime = time.monotonic()



    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID= value
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            self.Error(['Device ID Out of Range'])
    def ResetSequence(self, value, qualifier):
        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')


    def IncSequenceNumber(self):

        if self.StartSequence == 0:
           ctime = time.monotonic()
           if ctime - self.LastResetTime > 15:
               self.LastResetTime = time.monotonic()
               self.ResetSequence( None, None)
           self.PrevSequence = 1
           Sequence = b'\x00\x00\x00\x01'
        else:

            self.PrevSequence = self.PrevSequence + 1 if self.PrevSequence < 4294967295 else 0
            Sequence = pack('>L', self.PrevSequence)
        return(Sequence)
        
    def SetHeader(self, command, commandstring):
        sequence = self.IncSequenceNumber()
        if command != 'UserDefinedCommand':
            commandstring = b''.join([b'\x01\x00\x00', pack('B', len(commandstring)), sequence, b'\x81', commandstring[1:]])
        else:
            commandstring = b''.join([b'\x01\x00\x00', pack('B', len(commandstring)), sequence, b'\x81', commandstring])
        return commandstring            

    def GetHeader(self, commandstring):
        sequence = self.IncSequenceNumber()
        commandstring = b''.join([b'\x01\x10\x00', pack('B', len(commandstring)), sequence, b'\x81', commandstring[1:]])
        return commandstring


    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02, 
            'Off' : 0x03
        }

        AutoFocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x38,ValueStateValues[value], 0xFF)

        if 'Serial' not in self.ConnectionType:
            AutoFocusCmdString = self.SetHeader('AutoFocus', AutoFocusCmdString)

        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }

        AutoFocusCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x38, 0xFF)

        if 'Serial' not in self.ConnectionType:
            AutoFocusCmdString = self.GetHeader(AutoFocusCmdString)

        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
        }

        ValueStateValues = {
            'Far'  : 0x20, 
            'Near' : 0x30 
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            FocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x08, speed, 0xFF)

            if 'Serial' not in self.ConnectionType:
                FocusCmdString = self.SetHeader('Focus', FocusCmdString)

            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')


    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 0x02, 
            'Down'  : 0x03,
            'Reset' : 0x00
        }

        IrisCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)

        if 'Serial' not in self.ConnectionType:
            IrisCmdString = self.SetHeader('Iris', IrisCmdString)

        self.__SetHelper('Iris', IrisCmdString, value, qualifier)


    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min' : 1,
            'Max' : 24
            }

        TiltSpeedConstraints = {
            'Min' : 1,
            'Max' : 20
            }

        ValueStateValues = {
            'Up'         : (0x03,0x01), 
            'Down'       : (0x03,0x02), 
            'Left'       : (0x01,0x03), 
            'Right'      : (0x02,0x03), 
            'Stop'       : (0x03,0x03), 
            'Up Left'    : (0x01,0x01),
            'Up Right'   : (0x02,0x01),
            'Down Left'  : (0x01,0x02),
            'Down Right' : (0x02,0x02),
            'Home'       : 0x04, 
            'Reset'      : 0x05
        }

        PanSpd  = int(qualifier['Pan Speed'])
        TiltSpd = int(qualifier['Tilt Speed'])

        if (PanSpeedConstraints['Min'] <= PanSpd <= PanSpeedConstraints['Max']) and (TiltSpeedConstraints['Min'] <= TiltSpd <= TiltSpeedConstraints['Max']):
            if value not in ('Home','Reset'):          
                PanTiltCmdString = pack('>9B', self.DeviceID, 0x01, 0x06, 0x01, PanSpd, TiltSpd, ValueStateValues[value][0],ValueStateValues[value][1], 0xFF)
            elif value in ('Home','Reset'): 
                PanTiltCmdString = pack('>5B', self.DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)

            if 'Serial' not in self.ConnectionType:
                PanTiltCmdString = self.SetHeader('PanTilt', PanTiltCmdString)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt') 


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 0x02,
            'Off' : 0x03
        }

        PowerCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
        if 'Serial' not in self.ConnectionType:
            PowerCmdString = self.SetHeader('Power', PowerCmdString)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x03' : 'Off'
        }

        PowerCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x00, 0xFF)

        if 'Serial' not in self.ConnectionType:
            PowerCmdString = self.GetHeader(PowerCmdString)

        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save'   : 0x01, 
            'Reset'  : 0x00, 
            'Recall' : 0x02
        }
        
        if 0 <= int(value) <= 15:
            PresetCmdString = pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, ActionStates[qualifier['Action']], int(value), 0xFF)
            if 'Serial' not in self.ConnectionType:
                PresetCmdString = self.SetHeader('Preset', PresetCmdString)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')


    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min' : 0,
            'Max' : 7
            }

        ValueStateValues = {
            'Tele' : 0x20, 
            'Wide' : 0x30  
        }

        if (SpeedConstraints['Min'] <= int(qualifier['Speed']) <= SpeedConstraints['Max']):
            if value == 'Stop':
                speed = 0x00
            else:
                speed = int(qualifier['Speed']) + ValueStateValues[value]
            ZoomCmdString =  pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, speed, 0xFF)

            if 'Serial' not in self.ConnectionType:
                ZoomCmdString = self.SetHeader('Zoom', ZoomCmdString)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')


    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if len(response) == 4:
                address, errorByte, errorCode, terminator = unpack('>4B', response)
                
                if (errorByte == 0x60) and ( errorCode == 0x02 ):
                    self.Error([sourceCmdName + ' Syntax Error'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x03 ):
                    self.Error([sourceCmdName + ' Command Buffer Full'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x04 ):
                    self.Error([sourceCmdName + ' Command Cancelled'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x05 ):
                    self.Error([sourceCmdName + ' No Socket'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x41 ):
                    self.Error([sourceCmdName + ' Command Not Executable'])
                    response = ''
                elif (errorByte == 0x60) and ( errorCode == 0x01 ):
                    self.Error([sourceCmdName + ' Message length error'])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Unexpected/Invalid response'.format(command)])
            else:
                if 'Serial' in self.ConnectionType:
                    res = self.__CheckResponseForErrors(command, res)
                else:
                    res = self.__CheckResponseForErrors(command, res[8:12])

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            self.StartSequence = 1
            if 'Serial' in self.ConnectionType:
                return self.__CheckResponseForErrors(command, res)
            else:

                return self.__CheckResponseForErrors(command, res[8:12])

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


        if 'Serial' not in self.ConnectionType:
            self.ResetSequence(None,None)
            self.StartSequence = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.StartSequence = 0
        

    
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model =None):
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