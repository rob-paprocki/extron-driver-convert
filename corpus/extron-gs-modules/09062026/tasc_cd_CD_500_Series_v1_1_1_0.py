from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import time
from re import search


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoReady': {'Status': {}},
            'CDStatus': {'Status': {}},
            'CurrentTrackTime': {'Status': {}},
            'FadeMode': {'Status': {}},
            'FadeTime': {'Parameters': ['Fade Select'], 'Status': {}},
            'Index': {'Status': {}},
            'Jog': {'Status': {}},
            'Pitch': {'Status': {}},
            'PitchSpeed': {'Status': {}},
            'ReadyMode': {'Status': {}},
            'Repeat': {'Status': {}},
            'Shuttle': {'Status': {}},
            'TotalTrackTime': {'Status': {}},
            'TrackNumberSense': {'Status': {}},
            'TransportControl': {'Status': {}},
            'UserDefinedString': {'Status': {}}
            }               

    def SetAutoReady(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AutoReadyCmdString = '\n0360{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoReady', AutoReadyCmdString, value, qualifier)

    def UpdateAutoReady(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AutoReadyCmdString = '\n036FF\r'
        res = self.__UpdateHelper('AutoReady', AutoReadyCmdString, value, qualifier)
        if res:
            #try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('AutoReady', value, qualifier)
            #except (KeyError, IndexError):
                #print('Invalid/unexpected response for UpdateAutoReady')

    def UpdateCDStatus(self, value, qualifier):
        ValueStateValues = {
            '00': 'No Disc',
            '01': 'Preparing For Disc Ejection',
            '02': 'Ejecting',
            '10': 'Stop',
            '11': 'Play',
            '12': 'Ready',
            'FF': 'No Status'
        }

        CDStatusCmdString = '\n050\r'
        res = self.__UpdateHelper('CDStatus', CDStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:6]]
                self.WriteStatus('CDStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateCDStatus')

    def UpdateCurrentTrackTime(self, value, qualifier):
        CurrentTrackTimeCmdString = '\n057\r'
        res = self.__UpdateHelper('CurrentTrackTime', CurrentTrackTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{0}{1}{2}{3}:{4}{5}'.format(res[10], res[11], res[8], res[9], res[12], res[13])
                self.WriteStatus('CurrentTrackTime', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateCurrentTrackTime')

    def SetFadeMode(self, value, qualifier):
        ValueStateValues = {
            'In On/Out Off': '01',
            'In Off/Out On': '10',
            'In On/Out On': '11',
            'In Off/Out Off': '00'
        }

        FadeModeCmdString = '\n03E{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('FadeMode', FadeModeCmdString, value, qualifier)

    def UpdateFadeMode(self, value, qualifier):

        ValueStateValues = {
            '01': 'In On/Out Off',
            '10': 'In Off/Out On',
            '11': 'In On/Out On',
            '00': 'In Off/Out Off',
        }

        FadeModeCmdString = '\n03EFF\r'
        res = self.__UpdateHelper('FadeMode', FadeModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:6]]
                self.WriteStatus('FadeMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFadeMode')

    def SetFadeTime(self, value, qualifier):
        ValueConstraints = {
            'Min': 1,
            'Max': 30
            }

        fadeQualifier = {
            'In': '00',
            'Out': '01',
            }

        if 'In' or 'Out' in qualifier['Fade Select'] and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            FadeTimeCmdString = '\n02E{0}{1:02}\r'.format(fadeQualifier[qualifier['Fade Select']], value)
            self.__SetHelper('FadeTime', FadeTimeCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetFadeTime')

    def UpdateFadeTime(self, value, qualifier):

        fadeQualifier = {
            'In': '00',
            'Out': '01',
            }
        if 'In' or 'Out' in qualifier['Fade Select']:
            FadeTimeCmdString = '\n02E{0}FF\r'.format(fadeQualifier[qualifier['Fade Select']])
            res = self.__UpdateHelper('FadeTime', FadeTimeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[6:8])
                    self.WriteStatus('FadeTime', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateFadeTime')
        else:
            print('Invalid Command for UpdateFadeTime')

    def SetIndex(self, value, qualifier):
        ValueStateValues = {
            'Previous': '1',
            'Next': '0'
        }

        IndexCmdString = '\n01A1{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Index', IndexCmdString, value, qualifier)

    def SetJog(self, value, qualifier):
        ValueStateValues = {
            'On': '01',
            'Forward': '10',
            'Reverse': '11'
        }

        JogCmdString = '\n015{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Jog', JogCmdString, value, qualifier)

    def SetPitch(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PitchCmdString = '\n0350{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Pitch', PitchCmdString, value, qualifier)

    def UpdatePitch(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        PitchCmdString = '\n035FF\r'
        res = self.__UpdateHelper('Pitch', PitchCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Pitch', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePitch')

    def SetPitchSpeed(self, value, qualifier):
        ValueConstraints = {
            'Min': -16,
            'Max': 16
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempValue = float('{0:.2f}'.format(value)) 
            if tempValue < 0:
                data3 = 1                
                tempValue = int(tempValue * 10)
                tempValue = str(tempValue)[1:]                
                tempValue = '{0:03}'.format(int(tempValue)) 
            else:
                data3 = 0
                tempValue = int(tempValue * 10)
                tempValue = '{0:03}'.format(tempValue)

            PitchSpeedCmdString = '\n025{0}{1}{2}\r'.format(tempValue[1:], data3, tempValue[0])

            self.__SetHelper('PitchSpeed', PitchSpeedCmdString, value, qualifier, 3)
        else:
            print('Invalid Command for SetPitchSpeed')

    def UpdatePitchSpeed(self, value, qualifier):
        PitchSpeedCmdString = '\n025FF\r'
        res = self.__UpdateHelper('PitchSpeed', PitchSpeedCmdString, value, qualifier)
        if res:
            try:
                if res[6] == '1':
                    value = float(int('{0}{1}'.format(res[7], res[4:6])) * -1) / 10
                elif res[6] == '0':
                    value = float(int('{0}{1}'.format(res[7], res[4:6]))) / 10
                self.WriteStatus('PitchSpeed', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdatePitchSpeed')

    def SetReadyMode(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ReadyModeCmdString = '\n0140{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ReadyMode', ReadyModeCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):
        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        RepeatCmdString = '\n0370{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        RepeatCmdString = '\n037FF\r'
        res = self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('Repeat', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateRepeat')

    def SetShuttle(self, value, qualifier):
        ValueStateValues = {
            'Forward': '00',
            'Reverse': '01'
        }

        ShuttleCmdString = '\n016{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Shuttle', ShuttleCmdString, value, qualifier)

    def UpdateTotalTrackTime(self, value, qualifier):
        TotalTrackTimeCmdString = '\n05D\r'
        res = self.__UpdateHelper('TotalTrackTime', TotalTrackTimeCmdString, value, qualifier)
        if res:
            try:
                value = '{0}{1}{2}{3}:{4}{5}'.format(res[10], res[11], res[8], res[9], res[12], res[13])
                self.WriteStatus('TotalTrackTime', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateTotalTrackTime')

    def UpdateTrackNumberSense(self, value, qualifier):
        TrackNumberSenseCmdString = '\n055\r'
        res = self.__UpdateHelper('TrackNumberSense', TrackNumberSenseCmdString, value, qualifier)
        if res:
            try:
                value = int('{0}{1}{2}{3}'.format(res[8], res[9], res[6], res[7]))                
                self.WriteStatus('TrackNumberSense', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateTrackNumberSense')

    def SetTransportControl(self, value, qualifier):
        ValueStateValues = {
            'Stop': '10',
            'Play': '12',
            'Tray/Eject': '18',
            'Track Skip Next': '1A00',
            'Track Skip Previous': '1A01'
        }

        TransportControlCmdString = '\n0{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('TransportControl', TransportControlCmdString, value, qualifier, 3)

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                return res.decode()

            


    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        pass

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')
        
    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)    
        except AttributeError:
            print(command, 'does not support Update.')    

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        compile_list = self._compile_list
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True      

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
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
        if self.connectionFlag == False:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
