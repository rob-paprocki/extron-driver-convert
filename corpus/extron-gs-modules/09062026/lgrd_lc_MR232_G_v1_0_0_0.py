from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

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
            'CancelProportionalRampGroup': { 'Status': {}},
            'CancelProportionalRampRoom': { 'Status': {}},
            'CancelRampGroup': {'Parameters':['Target Level'], 'Status': {}},
            'CurrentDeviceType': {'Parameters':['Group ID'], 'Status': {}},
            'CurrentLevel': {'Parameters':['Group ID'], 'Status': {}},
            'LastError': {'Parameters':['Group ID'], 'Status': {}},
            'LastNonZeroLevel': {'Parameters':['Group ID'], 'Status': {}},
            'OverRideHouseToPreset': { 'Status': {}},
            'OverRideRoomToPreset': { 'Status': {}},
            'RampGroup': {'Parameters':['Group ID','Ramp Rate'], 'Status': {}},
            'RampRoom': {'Parameters':['Room Number','Ramp Rate'], 'Status': {}},
            'RecallHousePreset': { 'Status': {}},
            'RecallRoomPreset': {'Parameters':['Room Number'], 'Status': {}},
            'RevertOverRideHousePreset': { 'Status': {}},
            'RevertOverRideRoomPreset': {'Parameters':['Room Number'], 'Status': {}},
            'SaveHousePreset': { 'Status': {}},
            'SaveRoomPreset': {'Parameters':['Room Number','Fade Time'], 'Status': {}},
            'SetGroupToLastNonZero': { 'Status': {}},
            'SetRoomToLastNonZero': { 'Status': {}},
        }
        
        self.UpdateStatusRex=re.compile(b'GS,\s?(\d\d\d\d,\s?Not Responding)|(\d\d\d\d,\s?[0]\d\d\d,\s?[0]\d\d\d,\s?[0]\d\d\d,\s?[0]\d\d\d)')

    def SetCancelProportionalRampGroup(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 4095
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CancelProportionalRampGroupCmdString = 'CRAMP {0}\r'.format(value)
            self.__SetHelper('CancelProportionalRampGroup', CancelProportionalRampGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCancelProportionalRampGroup')

    def SetCancelProportionalRampRoom(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 127
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CancelProportionalRampRoomCmdString = 'CPRR {0}\r'.format(value)
            self.__SetHelper('CancelProportionalRampRoom', CancelProportionalRampRoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCancelProportionalRampRoom')

    def SetCancelRampGroup(self, value, qualifier):

        TargetLevelConstraints = {
            'Min' : 0,
            'Max' : 255
        }

        ValueConstraints = {
            'Min' : 1,
            'Max' : 4095
        }
        level = qualifier['Target Level']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and TargetLevelConstraints['Min'] <= level <= TargetLevelConstraints['Max']:
            CancelRampGroupCmdString = 'CRAMP {0} {1}\r'.format(value,level)
            self.__SetHelper('CancelRampGroup', CancelRampGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCancelRampGroup')

    def UpdateCurrentDeviceType(self, value, qualifier):

        self.UpdateCurrentLevel(value,qualifier)

    def UpdateCurrentLevel(self, value, qualifier):

        DeviceValues = {
            '0033' : 'Multi-location Controller', 
            '0034' : 'Room Preset Controller', 
            '0035' : 'House Preset Controller', 
            '0036' : 'Room Remote Preset Controller', 
            '0037' : 'House Remote Preset Controller', 
            '0065' : 'Dimmer or Plug-In Lamp Module', 
            '0066' : 'Relay/Switch (Non-Dimming) or Plug-In Appliance Module', 
            '0067' : 'Fan Controller'
        }

        ErrorValues = {
            '0134' : 'No-Load Detected', 
            '0132' : 'Overload Detected', 
            '0130' : 'Short Circuit Detected', 
            '0000' : 'No Error Detected'
        }

        CurrentLevelCmdString = 'STSG {0}\r'.format(qualifier['Group ID'])        
        res = self.__UpdateHelper('CurrentLevel', CurrentLevelCmdString, value, qualifier)
        if res:
            list = re.findall('\d\d\d\d',res) 
            if list:
                try:
                    groupID = int(list[0])                             
                    if groupID == qualifier['Group ID']:
                        try:
                            level = int(list[1])
                            if 0 <= level <= 255:
                                self.WriteStatus('CurrentLevel', level, qualifier)
                            else:
                                self.Error(['Current Level: Invalid/unexpected response'])
                        except (ValueError, IndexError):
                            self.Error(['Current Level: Invalid/unexpected response'])
                        try:
                            lnz = int(list[2])
                            if 0 <= lnz <= 255:
                                self.WriteStatus('LastNonZeroLevel', lnz, qualifier)
                            else:
                                self.Error(['Last Non Zero Level: Invalid/unexpected response'])
                        except (ValueError, IndexError):
                            self.Error(['Last Non Zero Level: Invalid/unexpected response'])
                        try:
                            type = DeviceValues[list[3]]
                            self.WriteStatus('CurrentDeviceType', type, qualifier)
                        except (KeyError, IndexError):
                            self.Error(['Current Device Type: Invalid/unexpected response'])        
                        try:
                            error = ErrorValues[list[4]]
                            self.WriteStatus('LastError', error, qualifier)
                        except (KeyError, IndexError):
                            self.Error(['Last Error: Invalid/unexpected response'])
                except (ValueError, IndexError):
                    self.Error(['Group ID: Invalid/unexpected response'])

    def UpdateLastError(self, value, qualifier):

        self.UpdateCurrentLevel(value, qualifier)

    def UpdateLastNonZeroLevel(self, value, qualifier):

        self.UpdateCurrentLevel(value,qualifier)

    def SetOverRideHouseToPreset(self, value, qualifier):

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'House-Off' : '11', 
            'House-On' : '12', 
            'Daylight' : '13', 
            'Panic' : '14'
        }

        OverRideHouseToPresetCmdString = 'ORHP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('OverRideHouseToPreset', OverRideHouseToPresetCmdString, value, qualifier)

    def SetOverRideRoomToPreset(self, value, qualifier):

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'User 11' : '11', 
            'User 12' : '12', 
            'User 13' : '13', 
            'User 14' : '14', 
            'User 15' : '15', 
            'Room-Off' : '16', 
            'Room-On' : '17'
        }

        OverRideRoomToPresetCmdString = 'ORRP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('OverRideRoomToPreset', OverRideRoomToPresetCmdString, value, qualifier)

    def SetRampGroup(self, value, qualifier):

        GroupIDConstraints = {
            'Min' : 1,
            'Max' : 4095
        }

        RampRateConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
        }

        groupID = qualifier['Group ID']
        rate = qualifier['Ramp Rate']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and GroupIDConstraints['Min'] <= groupID <= GroupIDConstraints['Max'] and RampRateConstraints['Min'] <= rate <= RampRateConstraints['Max']:
            RampGroupCmdString = 'RAMPG {0} {1} {2}\r'.format(groupID, value, rate)
            self.__SetHelper('RampGroup', RampGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRampGroup')

    def SetRampRoom(self, value, qualifier):

        RoomNumberConstraints = {
            'Min' : 1,
            'Max' : 127
        }

        RampRateConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
        }

        room = qualifier['Room Number']
        rate = qualifier['Ramp Rate']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and RoomNumberConstraints['Min'] <= room <= RoomNumberConstraints['Max'] and RampRateConstraints['Min'] <= rate <= RampRateConstraints['Max']:
            RampRoomCmdString = 'RAMPR {0} {1} {2}\r'.format(room, value, rate)
            self.__SetHelper('RampRoom', RampRoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRampRoom')

    def SetRecallHousePreset(self, value, qualifier):

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'House-Off' : '11', 
            'House-On' : '12', 
            'Daylight' : '13', 
            'Panic' : '14'
        }

        RecallHousePresetCmdString = 'RCHP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('RecallHousePreset', RecallHousePresetCmdString, value, qualifier)

    def SetRecallRoomPreset(self, value, qualifier):

        RoomNumberConstraints = {
            'Min' : 1,
            'Max' : 127
        }

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'User 11' : '11', 
            'User 12' : '12', 
            'User 13' : '13', 
            'User 14' : '14', 
            'User 15' : '15', 
            'Room-Off' : '16', 
            'Room-On' : '17'
        }

        room = qualifier['Room Number']
        if RoomNumberConstraints['Min'] <= room <= RoomNumberConstraints['Max']:
            RecallRoomPresetCmdString = 'RCRP {0} {1}\r'.format(room,ValueStateValues[value])
            self.__SetHelper('RecallRoomPreset', RecallRoomPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallRoomPreset')

    def SetRevertOverRideHousePreset(self, value, qualifier):

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'House-Off' : '11', 
            'House-On' : '12', 
            'Daylight' : '13', 
            'Panic' : '14'
        }

        if value == 'Previous':
            RevertOverRideHousePresetCmdString = 'RORHP\r'
        else:
            RevertOverRideHousePresetCmdString = 'RORHP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('RevertOverRideHousePreset', RevertOverRideHousePresetCmdString, value, qualifier)

    def SetRevertOverRideRoomPreset(self, value, qualifier):

        RoomNumberConstraints = {
            'Min' : 1,
            'Max' : 127
        }

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'User 11' : '11', 
            'User 12' : '12', 
            'User 13' : '13', 
            'User 14' : '14', 
            'User 15' : '15', 
            'Room-Off' : '16', 
            'Room-On' : '17'
        }

        room = qualifier['Room Number']
        if RoomNumberConstraints['Min'] <= room <= RoomNumberConstraints['Max']:
            if value == 'Previous':
                RevertOverRideRoomPresetCmdString = 'RORRP {0}\r'.format(room)
            else:
                RevertOverRideRoomPresetCmdString = 'RORRP {0} {1}\r'.format(room, ValueStateValues[value])
            self.__SetHelper('RevertOverRideRoomPreset', RevertOverRideRoomPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRevertOverRideRoomPreset')

    def SetSaveHousePreset(self, value, qualifier):

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10'
        }

        SaveHousePresetCmdString = 'SAVEHP {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SaveHousePreset', SaveHousePresetCmdString, value, qualifier)

    def SetSaveRoomPreset(self, value, qualifier):

        RoomNumberConstraints = {
            'Min' : 1,
            'Max' : 127
        }

        FadeTimeConstraints = {
            'Min' : 0,
            'Max' : 254
        }

        ValueStateValues = {
            'User 1' : '1', 
            'User 2' : '2', 
            'User 3' : '3', 
            'User 4' : '4', 
            'User 5' : '5', 
            'User 6' : '6', 
            'User 7' : '7', 
            'User 8' : '8', 
            'User 9' : '9', 
            'User 10' : '10', 
            'User 11' : '11', 
            'User 12' : '12', 
            'User 13' : '13', 
            'User 14' : '14', 
            'User 15' : '15'
        }

        room = qualifier['Room Number']
        time = qualifier['Fade Time']
        if RoomNumberConstraints['Min'] <= room <= RoomNumberConstraints['Max'] and FadeTimeConstraints['Min'] <= time <= FadeTimeConstraints['Max']:
            SaveRoomPresetCmdString = 'SAVERP {0} {1} {2}\r'.format(room, ValueStateValues[value], time)
            self.__SetHelper('SaveRoomPreset', SaveRoomPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveRoomPreset')

    def SetSetGroupToLastNonZero(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 4095
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SetGroupToLastNonZeroCmdString = 'LNZG {0}\r'.format(value)
            self.__SetHelper('SetGroupToLastNonZero', SetGroupToLastNonZeroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetGroupToLastNonZero')

    def SetSetRoomToLastNonZero(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 127
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SetRoomToLastNonZeroCmdString = 'LNZR {0}\r'.format(value)
            self.__SetHelper('SetRoomToLastNonZero', SetRoomToLastNonZeroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetRoomToLastNonZero')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'Not Responding' not in response:
            return response
        else:
            group = re.findall('\d\d\d\d',response)[0].strip('0')
            self.Error(['Error: Group {0} is not responding.'.format(group)])

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateStatusRex)
            if not res:
                return ''
            else:
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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