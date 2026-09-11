from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import unpack

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
            'Amplitude': {'Parameters':['Segment'], 'Status': {}},
            'Distance': {'Parameters':['Segment'], 'Status': {}},
            'LaserPower': { 'Status': {}},
        }                
                                
        self.detectionRegex = re.compile(b'[\xA0-\xFF]\x01[\x00-\xFF]{3}')

    def UpdateLaserPower(self, value, qualifier):

        LaserPowerCmdString = b'\x01\x41\xC0\x10'
        res = self.__UpdateHelper('LaserPower', LaserPowerCmdString, value, qualifier)
        if res:
            try:
                value = res[-4]
                self.WriteStatus('LaserPower', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Laser Power: Invalid/unexpected response'])
            if len(res) > 11:
                validSegmentList = {
                    b'\x01' : 1,
                    b'\x11' : 2,
                    b'\x21' : 3,
                    b'\x31' : 4,
                    b'\x41' : 5,
                    b'\x51' : 6,
                    b'\x61' : 7,
                    b'\x71' : 8,
                    b'\x81' : 9,
                    b'\x91' : 10,
                    b'\xA1' : 11,
                    b'\xB1' : 12,
                    b'\xC1' : 13,
                    b'\xD1' : 14,
                    b'\xE1' : 15,
                    b'\xF1' : 16
                }

                detectionList = []
                try:
                    detectionList = re.findall(self.detectionRegex, res[3:-8])
                except (KeyError, TypeError, IndexError):
                    self.Error(['Laser Power: Detection messages not found.'])
                tempDict = {}
                try:
                    for i in range(len(detectionList)):
                        tempDict[validSegmentList[detectionList[i][4:5]]] = detectionList[i]
                except (KeyError, TypeError, IndexError):
                    self.Error(['Laser Power: Detections error'])
                for i in range(16):
                    if i + 1 in tempDict:
                        distance = unpack('<H', tempDict[i + 1][0:2])[0]
                        amplitude = round(unpack('<H', tempDict[i + 1][2:4])[0] / 64, 3)
                        self.WriteStatus('Distance', distance, {'Segment' : str(i + 1)})
                        self.WriteStatus('Amplitude', amplitude, {'Segment' : str(i + 1)})
                    else:  # Else just write 0 for that segment for both statuses
                        self.WriteStatus('Amplitude', 0, {'Segment' : str(i + 1)})
                        self.WriteStatus('Distance', 0, {'Segment' : str(i + 1)})
            else: #Write all 0 for no detections
                for i in range(16):
                    self.WriteStatus('Amplitude', 0, {'Segment': str(i + 1)})
                    self.WriteStatus('Distance', 0, {'Segment': str(i + 1)})
    
    def UpdateAmplitude(self, value, qualifier):
        self.UpdateLaserPower(value, qualifier)
    
    def UpdateDistance(self, value, qualifier):
        self.UpdateLaserPower(value, qualifier)
    
    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model =None):
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

