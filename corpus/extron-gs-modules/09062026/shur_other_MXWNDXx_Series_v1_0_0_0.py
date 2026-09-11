# Copyright 2025, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'MXWNDX4': self.shur_31_17296_4,
            'MXWNDX4G': self.shur_31_17296_4,
            'MXWNDX8': self.shur_31_17296_8,
            'MXWNDX8G': self.shur_31_17296_8
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BatteryCharge': {'Parameters':['Port'], 'Status': {}},
            'BatteryHealth': {'Parameters':['Port'], 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'TimeTillBatteryFull': {'Parameters':['Port'], 'Status': {}},
            'TransmitterAvailability': {'Parameters':['Port'], 'Status': {}},
            'TransmitterStatus': {'Parameters':['Port'], 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'< REP ([1-8]) BATT_CHARGE ([01][0-9][0-9]) >'), self.__MatchBatteryCharge, None)
            self.AddMatchString(re.compile(b'< REP ([1-8]) BATT_HEALTH ([01][0-9][0-9]) >'), self.__MatchBatteryHealth, None)
            self.AddMatchString(re.compile(b'< REP FW_VER \{(\d+\.\d+\.\d+\.\d+\*?) } >'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'< REP ([1-8]) BATT_TIME_TO_FULL ([0-6][0-9][0-9][0-9][0-9]) >'), self.__MatchTimeTillBatteryFull, None)
            self.AddMatchString(re.compile(b'< REP ?B?A?Y? ([1-8]) TX_AVAILABLE (YES|NO) >'), self.__MatchTransmitterAvailability, None)
            self.AddMatchString(re.compile(b'< REP BAY ([1-8]) TX_STATUS (ACTIVE|MUTED|ON_CHARGER|UNKNOWN) >'), self.__MatchTransmitterStatus, None)

            self.AddMatchString(re.compile(b'< REP ([1-8]) (BATT_HEALTH|BATT_CHARGE) (253|255) >'), self.__MatchError, None)

    def UpdateBatteryCharge(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            BatteryChargeCmdString = '< GET {} BATT_CHARGE >'.format(qualifier['Port'])
            self.__UpdateHelper('BatteryCharge', BatteryChargeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryCharge')

    def __MatchBatteryCharge(self, match, tag):

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BatteryCharge', value, qualifier)

    def UpdateBatteryHealth(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            BatteryHealthCmdString = '< GET {} BATT_HEALTH >'.format(qualifier['Port'])
            self.__UpdateHelper('BatteryHealth', BatteryHealthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBatteryHealth')

    def __MatchBatteryHealth(self, match, tag):

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('BatteryHealth', value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '< GET FW_VER >'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def UpdateTimeTillBatteryFull(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            TimeTillBatteryFullCmdString = '< GET {} BATT_TIME_TO_FULL >'.format(qualifier['Port'])
            self.__UpdateHelper('TimeTillBatteryFull', TimeTillBatteryFullCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTimeTillBatteryFull')

    def __MatchTimeTillBatteryFull(self, match, tag):

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 65532:
            self.WriteStatus('TimeTillBatteryFull', value, qualifier)

    def UpdateTransmitterAvailability(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            TransmitterAvailabilityCmdString = '< GET BAY {} TX_AVAILABLE >'.format(qualifier['Port'])
            self.__UpdateHelper('TransmitterAvailability', TransmitterAvailabilityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterAvailability')

    def __MatchTransmitterAvailability(self, match, tag):

        ValueStateValues = {
            'YES': 'Available',
            'NO': 'Not Available'
            }

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterAvailability', value, qualifier)

    def UpdateTransmitterStatus(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= self.ports:
            TransmitterStatusCmdString = '< GET BAY {} TX_STATUS >'.format(qualifier['Port'])
            self.__UpdateHelper('TransmitterStatus', TransmitterStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitterStatus')

    def __MatchTransmitterStatus(self, match, tag):

        ValueStateValues = {
            'ACTIVE': 'Undocked & Unmuted',
            'MUTED': 'Undocked & Muted',
            'ON_CHARGER': 'Docked',
            'UNKNOWN': 'Offline/Unlinked'
            }

        qualifier = {}
        qualifier['Port'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitterStatus', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):
        self.counter = 0

        CommandStateValues = {
            'BATT_HEALTH': 'Battery Health',
            'BATT_CHARGE': 'Battery Charge',
        }

        ErrorStateValues = {
            '253': 'Error',
            '255': 'Unknown Exception',
        }

        port = match.group(1).decode()
        command = CommandStateValues[match.group(2).decode()]
        error = ErrorStateValues[match.group(3).decode()]
        self.Error(['Error: An {} has occurred for command {} on port {}.'.format(error, command, port)])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def shur_31_17296_4(self):

        self.ports = 4

    def shur_31_17296_8(self):

        self.ports = 8

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()