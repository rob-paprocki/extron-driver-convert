from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
class DeviceClass:



    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 10000
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True

        self.Debug = False
        self.Models = {}

        self.__input_names = ['None','RmA Cam Left',
                                'RmA Cam Right',
                                'RmA Aud Cam',
                                'Pres PC A',
                                'Playbck PC A',
                                'WP1 NAV',
                                'WP2 NAV',
                                'Lectern A NAV',
                                'WP4 NAV',
                                'WP3 SDI',#10
                                'WP4 SDI',
                                'Anno A',
                                'PolyFar A',
                                'Poly   Cont A',
                                'Control A',
                                'CATV A',
                                'RmB Cam Left',
                                'RmB Cam Right',
                                'RmB Aud Cam',
                                'Pres PC B',#20
                                'Playbck PC B',
                                'Lectern B NAV',
                                'WP6 NAV',
                                'WP7 NAV',
                                'WP5 SDI',
                                'WP6 SDI',
                                'Anno B',
                                'PolyFar B',
                                'Poly   Cont B',
                                'Control B',#30
                                'CATV B',
                                'In 32',
                                'Aux NAV',
                                'Aux SDI',
                                'In 35',
                                'In 36',
                                'In 37',
                                'In 38',
                                'In 39',
                                'In 40',#40
                                'In 41',
                                'In 42',
                                'In 43',
                                'In 44',
                                'HV In 1',
                                'HV In 2',
                                'HV In 3',
                                'HV In 4',
                                'In 49',
                                'In 50',#50
                                'In 51',
                                'Dead Route',
                                'In 53',
                                'SWR Aux 1',
                                'SWR Aux 2',
                                'SWR Aux 3',
                                'SWR Aux 4',
                                'SWR Aux 5',
                                'SWR Aux 6',
                                'SWR Aux 7',#60
                                'SWR Out ME 1',
                                'SWR Out MV',
                                'SWR Out PGM',
                                'SWR Out MiniME1',
                                'SWR Out MiniME2',
                                'SWR Out M1',
                                'SWR Out M2',
                                'SWR Out M3',
                                'SWR Out M4',
                                'Haivision 1 Audio',#70
                                'Haivision 2 Audio',
                                'Haivision 3 Audio',
                                'Haivision 4 Audio'
                                ]
        for i in range(5,65):
            self.__input_names.append('MADI {}'.format(i))

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'OutputTieStatus': {'Parameters':['Output'], 'Status': {}},
            }


        self.AddMatchString(compile(rb'([\x81-\x90][\x00])(.{16})'), self.__MatchOutputTieStatus, None)

    '''
    output numbers : [81][00]  thru [90][00]    feedback format  : 2 bytes output id, 16 bytes input name, 18 bytes total
    [84][00]
    '''

    def __MatchOutputTieStatus(self, match, tag):
        qualifier = dict()
        qualifier['Output'] = str(ord(match.group(1).decode('utf-16'))-128)
        input_name = match.group(2).decode().strip()
        if input_name in self.__input_names:
            value = self.__input_names.index(input_name)
            self.WriteStatus('OutputTieStatus', value, qualifier)
        else:
            print('Ross Matrix Error, unknown input: {}'.format(input_name))

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True
        self.InputList = []
        self.OutputList = []

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
            return None

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.OnConnected()
        self.__receiveBuffer += data
        index = 0  # Start of possible good data
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Hostname, IPPort=5727, Protocol='TCP', ServicePort=0, Model=None):
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
