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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoEDIDMode': { 'Status': {}},
            'CableStatus': {'Parameters':['ID'], 'Status': {}},
            'EncoderStatus': {'Parameters':['ID'], 'Status': {}},
            'Input': {'Parameters':['Encoder ID'], 'Status': {}},
            'InputFPSStatus': {'Parameters':['ID'], 'Status': {}},
            'Join': {'Parameters':['Encoder ID','Decoder ID'], 'Status': {}},
            'PresetRecallCommand': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'autoEdidMode=(enabled|disabled)(\r\n)?'), self.__MatchAutoEDIDMode, None)
            self.AddMatchString(re.compile(b'diagnostics device (.+)\r\n[\w\W]+ error=(1|0),[\w\W]+Zyper\$'), self.__MatchEncoderStatus, None)
            self.AddMatchString(re.compile(b'device[\s\S]*?device\.gen; model=[\s\S]*?(?=Success)(\r\n)?'), self.__MatchCableStatus, None)

    def UpdateAutoEDIDMode(self, value, qualifier):

        AutoEDIDModeCmdString = 'show server config\r\n'
        self.__UpdateHelper('AutoEDIDMode', AutoEDIDModeCmdString, value, qualifier)

    def __MatchAutoEDIDMode(self, match, tag):

        ValueStateValues = {
            'enabled':  'On',
            'disabled': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoEDIDMode', value, None)

    def UpdateCableStatus(self, value, qualifier):

        id_ = qualifier['ID']
        if id_ != '':
            CableStatusCmdString = 'show device status {}\r\n'.format(id_)
            self.__UpdateHelper('CableStatus', CableStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCableStatus')

    def __MatchCableStatus(self, match, tag):

        qualifier = {}

        res = match.group(0).decode()
        name = re.search('name=.*?(?=,)',res)
        qualifier['ID'] = name.group(0).split('=')[1]

        cableStatus = re.search('cableConnected=(connected|disconnected)', res)
        self.WriteStatus('CableStatus', cableStatus.group(1).title(), qualifier)

        fps = re.search('inputFps=(\d+\.\d{2})?(?=,)', res)
        self.WriteStatus('InputFPSStatus', fps.group(0).split('=')[1], qualifier)

    def UpdateEncoderStatus(self, value, qualifier):

        EncoderStatusCmdString = 'diagnostics device {}\r\n'.format(qualifier['ID'])
        self.__UpdateHelper('EncoderStatus', EncoderStatusCmdString, value, qualifier)

    def __MatchEncoderStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Online',
            '1': 'Offline'
            }

        qualifier = {}
        qualifier['ID'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('EncoderStatus', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1':      'hdmi',
            'HDMI 2':      'hdmiOptionalIn',
            'USB-C':       'usbc',
            'Auto':        'auto',
            'DisplayPort': 'displayPort',
            'SDI':         'hdsdi',
            '12G SDI':     '12gsdi',
            'Component':   'component',
            'Composite':   'composite',
            'S-Video':     's-video',
            'VGA':         'vga'
            }

        encoder_id = qualifier['Encoder ID']

        if encoder_id != '' and value in ValueStateValues:
            InputCmdString = 'set device {} videoPort {}\r\n'.format(encoder_id, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInputFPSStatus(self, value, qualifier):

        self.UpdateCableStatus(value, qualifier)

    def SetJoin(self, value, qualifier):

        ValueStateValues = {
            'Analog Audio':   'analogAudio',
            'Dante Audio':    'danteAudio',
            'Fast Switched':  'fastSwitched',
            'HDMI Audio':     'hdmiAudio',
            'Video':          'video',
            'Video Wall':     'videoWall',
            'USB':            'usb'
            }
        
        encoder_ID = qualifier['Encoder ID']
        decoder_ID = qualifier['Decoder ID']

        if value in ValueStateValues:
            JoinCmdString = 'join {} {} {}\r\n'.format(encoder_ID, decoder_ID, ValueStateValues[value])
            self.__SetHelper('Join', JoinCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetJoin')

    def SetPresetRecallCommand(self, value, qualifier):

        preset = value
        if preset != '':
            PresetRecallCommandCmdString = 'run preset {}\r\n'.format(preset)
            self.__SetHelper('PresetRecallCommand', PresetRecallCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallCommand')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

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