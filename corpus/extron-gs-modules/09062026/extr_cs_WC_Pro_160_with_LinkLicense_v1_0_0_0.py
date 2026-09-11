# Copyright 2025, Extron. All rights reserved.

import re
from extronlib.interface import SPInterface
from extronlib.system import Wait, ProgramLog

class SPIClass(SPInterface):
    def __init__(self, spd):
        super().__init__(spd)

        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.initializationChk = True
        self.VerboseDisabled = True

        self.Commands = {
            'AudioMute': {'Parameters':['Type'], 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'InputHDCPAuthorization': { 'Status': {}},
            'InputStatus': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }


        self.AddMatchString(re.compile(b'Amt(?P<port>[12])\*(?P<mode>[01])\r\n'), self.__MatchAudioMute, None)
        self.AddMatchString(re.compile(b'Amt(?P<analog>[01]) (?P<digital>[01])\r\n'), self.__MatchAudioMute, 'Query')
        self.AddMatchString(re.compile(b'Amt(?P<mode>[01])\r\n'), self.__MatchAudioMute, 'All')
        self.AddMatchString(re.compile(b'HdcpO(?P<port>[0-9]+)\*(?P<mode>[012])'), self.__MatchHDCPOutputStatus, None)
        self.AddMatchString(re.compile(b'HdcpE1\*(?P<value>0|1)'), self.__MatchInputHDCPAuthorization, None)
        self.AddMatchString(re.compile(b'In00 (?P<value>0|1)'), self.__MatchInputStatus, None)
        self.AddMatchString(re.compile(b'Vmt(?P<mode>[012])'), self.__MatchVideoMute, None)
        self.AddMatchString(re.compile(b'Vol(?P<value>[+-]?\d*)'), self.__MatchVolume, None)
        self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
        self.AddMatchString(re.compile(b'E([0-3][0-9])'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.VerboseDisabled = False

    def SetAudioMute(self, value, qualifier):

        OutputValues = {
            'All' : '0',
            'Analog' : '1',
            'Digital' : '2'
        }

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        try:
            if qualifier['Type'] in OutputValues and value in ValueStateValues:
                if qualifier['Type'] in ['Analog', 'Digital']:
                    AudioMuteCmdString = '{0}*{1}Z'.format(OutputValues[qualifier['Type']], ValueStateValues[value])
                else:
                    AudioMuteCmdString = '{0}Z'.format(ValueStateValues[value])
                self.__SendHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            else:
                self.Discard('AudioMute Error, invalid or missing channel or value ({0} - {1}).'.format(value , qualifier))

        except:
            self.Discard('AudioMute Error, {0} {1} do not have correct values.'.format(value , qualifier))

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__SendHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        OutputValues = {
            '0' : 'All',
            '1' : 'Analog',
            '2' : 'Digital'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        if tag == 'Query':
            analog = ValueStateValues[match.group('analog').decode()]
            digital = ValueStateValues[match.group('digital').decode()]
            self.WriteStatus('AudioMute', analog, {'Type': 'Analog'})
            self.WriteStatus('AudioMute', digital, {'Type': 'Digital'})
            if analog == digital:
                self.WriteStatus('AudioMute', digital, {'Type': 'All'})
        elif tag == 'All':
            mode = ValueStateValues[match.group('mode').decode()]
            self.WriteStatus('AudioMute', mode, {'Type': 'Analog'})
            self.WriteStatus('AudioMute', mode, {'Type': 'Digital'})
            self.WriteStatus('AudioMute', mode, {'Type': 'All'})
        else:
            mode = match.group('mode').decode()
            modeval = str(int(mode))
            value = ValueStateValues[modeval]

            qualifier = {}

            try:
                port = match.group('port').decode()
                if port is not None:
                    portval = str(int(port))
                    qualifier['Type'] = OutputValues[portval]

            except:
                qualifier['Type'] = 'All'

            self.WriteStatus('AudioMute', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'WO1HDCP|'
        self.__SendHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        mode = match.group('mode').decode()

        ValueStateValues = {
            '0' : 'No sink or source device detected',
            '1' : 'Sink or source detected with HDCP',
            '2' : 'Sink or source detected but no HDCP is present'
        }
        value = ValueStateValues[mode]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetInputHDCPAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            InputHDCPAuthorizationCmdString = 'wE1*{0}HDCP|'.format(ValueStateValues[value])
            self.__SendHelper('InputHDCPAuthorization', InputHDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputHDCPAuthorization.')

    def UpdateInputHDCPAuthorization(self, value, qualifier):

        InputHDCPAuthorizationCmdString = 'WE1HDCP|'
        self.__SendHelper('InputHDCPAuthorization', InputHDCPAuthorizationCmdString, value, qualifier)

    def __MatchInputHDCPAuthorization(self, match, tag):

        value = match.group('value').decode()

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[value]
        self.WriteStatus('InputHDCPAuthorization', value, None)

    def UpdateInputStatus(self, value, qualifier):

        InputStatusCmdString = 'w0LS|'
        self.__SendHelper('InputStatus', InputStatusCmdString, value, qualifier)

    def __MatchInputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No signal present',
            '1' : 'Signal present'
        }

        value = match.group('value').decode()
        value = ValueStateValues[value]
        self.WriteStatus('InputStatus', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Video & Sync' : '2',
            'Off' : '0'
        }

        VideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
        self.__SendHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__SendHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Video & Sync'
        }

        mode = match.group('mode').decode()
        modeval = str(int(mode))

        value = ValueStateValues[modeval]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        value = int(value)

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SendHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__SendHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group('value').decode())

        self.WriteStatus('Volume', value, None)

    def __SendHelper(self, command, commandstring, value, qualifier):
        if self.VerboseDisabled:
            self.Send('w3cv\r\n')
            @Wait(1)
            def SendCommandString():
                self.Send(commandstring)
            return

        self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number or port number',
            '13': 'Invalid parameter (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out (caused by direct write of global presets)',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Discard(DEVICE_ERROR_CODES[value])
        else:
            self.Discard('Unrecognized error code: ' + match.group(0).decode())

    def Discard(self, message):
        print('Module: {}'.format(__name__), 'Error Message: {}'.format(message), sep='\r\n')

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
