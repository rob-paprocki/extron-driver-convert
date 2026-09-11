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
        self._DeviceID = '01'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Date': { 'Status': {}},
            'DateStatus': { 'Status': {}},
            'DayofWeek': { 'Status': {}},
            'Display': {'Parameters': ['Effect', 'Color', 'Speed'], 'Status': {}},
            'TimeFormat': { 'Status': {}},
            'TimeofDay': {'Parameters': ['Type'], 'Status': {}},
            'TimeofDayStatus': { 'Status': {}},
        }

        if self.Unidirectional == 'False' or self.DeviceID != '00':
            self.AddMatchString(re.compile(b'\x02\x45\x3B([\s\S]{6})\x03[\s\S]{4}\x04'), self.__MatchDateStatus, None)
            self.AddMatchString(re.compile(b'\x02\x45\x26([\x31-\x37])\x03[\s\S]{4}\x04'), self.__MatchDayofWeek, None)
            self.AddMatchString(re.compile(b'\x02\x45\x20([\s\S]{4})\x03[\s\S]{4}\x04'), self.__MatchTimeofDayStatus, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 255:
            self._DeviceID = '{0:02X}'.format(int(value))

    def SetDate(self, value, qualifier):

        date = value
        if date:
            dateSplit = date.split('/')
            date = dateSplit[0].zfill(2) + dateSplit[1].zfill(2) + dateSplit[2][2:]
            DateCommandCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x45\x3B{1}\x04'.format(self.DeviceID, date)
            self.__SetHelper('Date', DateCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDateCommand')

    def UpdateDateStatus(self, value, qualifier):

        DateStatusCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x46\x3B\x04'.format(self.DeviceID)
        self.__UpdateHelper('DateStatus', DateStatusCmdString, value, qualifier)

    def __MatchDateStatus(self, match, tag):

        value = match.group(1).decode()
        date = value[:2] + '/' + value[2:4] + '/' + value[4:]
        self.WriteStatus('DateStatus', date, None)

    def SetDayofWeek(self, value, qualifier):

        ValueStateValues = {
            'Sunday'    : '\x31',
            'Monday'    : '\x32',
            'Tuesday'   : '\x33',
            'Wednesday' : '\x34',
            'Thursday'  : '\x35',
            'Friday'    : '\x36',
            'Saturday'  : '\x37'
        }

        if value in ValueStateValues:
            DayofWeekCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x45\x26{1}\x04'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('DayofWeek', DayofWeekCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDayofWeek')

    def UpdateDayofWeek(self, value, qualifier):

        DayofWeekCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x46\x26\x04'.format(self.DeviceID)
        self.__UpdateHelper('DayofWeek', DayofWeekCmdString, value, qualifier)

    def __MatchDayofWeek(self, match, tag):

        ValueStateValues = {
            '1': 'Sunday',
            '2': 'Monday',
            '3': 'Tuesday',
            '4': 'Wednesday',
            '5': 'Thursday',
            '6': 'Friday',
            '7': 'Saturday'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DayofWeek', value, None)

    def SetDisplay(self, value, qualifier):

        ColorStates = {
            'Red' :       '\x1C1', 
            'Green' :     '\x1C2', 
            'Amber' :     '\x1C3', 
            'Dim Red' :   '\x1C4', 
            'Dim Green' : '\x1C5', 
            'Brown' :     '\x1C6', 
            'Orange' :    '\x1C7', 
            'Yellow' :    '\x1C8', 
            'Color Mix' : '\x1CB', 
            'Autocolor' : '\x1CC'
        }
        
        EffectStates = {
            'Rotate' :            'a', 
            'Hold' :              'b', 
            'Flash' :             'c', 
            'Roll Up' :           'e', 
            'Roll Down' :         'f', 
            'Roll Left' :         'g', 
            'Roll Right' :        'h', 
            'Wipe Up' :           'i', 
            'Wipe Down' :         'j', 
            'Wipe Left' :         'k', 
            'Wipe Right' :        'l', 
            'Scroll' :            'm', 
            'Automode' :          'o', 
            'Compressed Rotate' : 't', 
            'Twinkle' :           'n0', 
            'Sparkle' :           'n1', 
            'Snow' :              'n2', 
            'Interlock' :         'n3'
        }

        SpeedStates = {
            'Slowest'   : '\x15',
            'Slow'      : '\x16',
            'Fast'      : '\x17',
            'Faster'    : '\x18',
            'Fastest'   : '\x19'
        }

        Effect = EffectStates.get(qualifier['Effect'])
        Color = ColorStates.get(qualifier['Color'])
        Speed = SpeedStates.get(qualifier['Speed'])

        if Effect and Color and Speed and value:
            DisplayCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02AA\x1B\x20{1}{2}{3}{4}\x04'.format(self.DeviceID, Effect, Color, Speed, value)
            self.__SetHelper('Display', DisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayCommand')

    def SetTimeFormat(self, value, qualifier):

        ValueStateValues = {
            'Standard' : '\x53',
            '24 Hour'  : '\x4D'
        }

        if value in ValueStateValues:
            TimeFormatCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x45\x27{1}\x04'.format(self.DeviceID, ValueStateValues[value])
            self.__SetHelper('TimeFormat', TimeFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimeFormat')

    def SetTimeofDay(self, value, qualifier):

        timeOfDay = value
        typeQual = qualifier['Type']
        if timeOfDay and typeQual in ['A.M.', 'P.M.', '24 Hour']:
            timeOfDay = timeOfDay.replace(':', '').zfill(4)
            if typeQual == 'P.M.':
                timeOfDay = str(int(timeOfDay) + 1200)
            elif typeQual == 'A.M.' and timeOfDay[:2] == '12':
                timeOfDay = str(int(timeOfDay) - 1200)
                timeOfDay = timeOfDay.zfill(4)
            TimeofDayCommandCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x45\x20{1}\x04'.format(self.DeviceID, timeOfDay)
            self.__SetHelper('TimeofDay', TimeofDayCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTimeofDayCommand')

    def UpdateTimeofDayStatus(self, value, qualifier):

        TimeofDayStatusCmdString = '\x00\x00\x00\x00\x00\x01Z{0}\x02\x46\x20\x04'.format(self.DeviceID)
        self.__UpdateHelper('TimeofDayStatus', TimeofDayStatusCmdString, value, qualifier)

    def __MatchTimeofDayStatus(self, match, tag):


        value = match.group(1).decode()
        timeOfDay = value[:2] + ':' + value[2:]
        self.WriteStatus('TimeofDayStatus', timeOfDay, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '00':
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

