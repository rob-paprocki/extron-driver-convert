from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'AutoTransitionsControl': {'Status': {}},
            'CutTransitionsControl': {'Status': {}},
            'Source': {'Parameters': ['Bus Address'], 'Status': {}},
            'Tally': {'Parameters': ['Bus Address'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02ABST:(\d{2}):(\d{2}):([01])\x03'), self.__MatchSource, None)

    def SetAutoTransitionsControl(self, value, qualifier):

        ValueStateValues = {
            'BKGD': ':00',
            'Key': ':01',
            'PinP': ':04',
            'FTB': ':06'
        }

        AutoTransitionsControlCmdString = '\x02SAUT' + ValueStateValues[value] + ':0\x03'
        self.__SetHelper('AutoTransitionsControl', AutoTransitionsControlCmdString, value, qualifier)

    def SetCutTransitionsControl(self, value, qualifier):

        ValueStateValues = {
            'BKGD': ':00\x03',
            'KEY': ':01\x03'
        }

        CutTransitionsControlCmdString = '\x02SCUT' + ValueStateValues[value]
        self.__SetHelper('CutTransitionsControl', CutTransitionsControlCmdString, value, qualifier)

    def SetSource(self, value, qualifier):

        BusAddressStates = {
            'Bus A': '00',
            'Bus B': '01',
            'PGM': '02',
            'PVW': '03',
            'KEY-F': '04',
            'KEY-S': '05',
            'PinP': '10',
            'AUX': '12'
        }

        ValueStateValues = {
            'Input A': ':00\x03',
            'Input B': ':01\x03',
            'Input C': ':02\x03',
            'Input D': ':03\x03',
            'Input E': ':04\x03',
            'Input F': ':05\x03',
            'Input G': ':06\x03',
            'Input H': ':07\x03',
            'Input I': ':08\x03',
            'Input J': ':09\x03',
            'Input 1': ':50\x03',
            'Input 2': ':51\x03',
            'Input 3': ':52\x03',
            'Input 4': ':53\x03',
            'Input 5': ':54\x03',
            'Color Bars': ':70\x03',
            'Background': ':71\x03',
            'Black': ':72\x03',
            'Frame 1': ':73\x03',
            'Frame 2': ':74\x03',
            'PGM': ':77\x03',
            'PVW': ':78\x03',
            'Keyout': ':79\x03',
            'CLN': ':80\x03'
        }
        Address = BusAddressStates[qualifier['Bus Address']]
        SourceCmdString = '\x02SBUS:' + Address + ValueStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        BusAddressStates = {
            'Bus A': '00',
            'Bus B': '01',
            'PGM': '02',
            'PVW': '03',
            'KEY-F': '04',
            'KEY-S': '05',
            'PinP': '10',
            'AUX': '12'
        }
        Address = BusAddressStates[qualifier['Bus Address']]
        SourceCmdString = '\x02QBST:' + Address + '\x03'
        self.__UpdateHelper('Source', SourceCmdString, value, qualifier)

    def __MatchSource(self, match, tag):

        BusAddressStates = {
            '00': 'Bus A',
            '01': 'Bus B',
            '02': 'PGM',
            '03': 'PVW',
            '04': 'KEY-F',
            '05': 'KEY-S',
            '10': 'PinP',
            '12': 'AUX'
        }
        ValueStateValues = {
            '00': 'Input A',
            '01': 'Input B',
            '02': 'Input C',
            '03': 'Input D',
            '04': 'Input E',
            '05': 'Input F',
            '06': 'Input G',
            '07': 'Input H',
            '08': 'Input I',
            '09': 'Input J',
            '99': 'Input Not Assigned'
        }
        TallyStates = {
            '1': 'On',
            '0': 'Off'
        }

        temp = BusAddressStates[match.group(1).decode()]
        value1 = ValueStateValues[match.group(2).decode()]
        value2 = TallyStates[match.group(3).decode()]
        self.WriteStatus('Source', value1, {'Bus Address': temp})
        self.WriteStatus('Tally', value2, {'Bus Address': temp})

    def UpdateTally(self, value, qualifier):

        self.UpdateSource(value, qualifier)

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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