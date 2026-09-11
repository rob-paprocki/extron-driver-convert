from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'CuelistLevel': {'Parameters': ['Cuelist'], 'Status': {}},
            'GoToCuelist': { 'Status': {}},
            'GoToCuelistCue': {'Parameters': ['Cuelist'], 'Status': {}},
            'LoadAction': { 'Status': {}},
            'LoadSchedule': { 'Status': {}},
            'PauseCuelist': { 'Status': {}},
            'ReleaseCuelist': { 'Status': {}},
        }

    def SetCuelistLevel(self, value, qualifier):

        cuelist = qualifier['Cuelist']

        if 1 <= cuelist <= 99999 and 0 <= value <= 100:
            CuelistLevelCmdString = '$mx,sql,{:05d},{:03d}\r'.format(cuelist, value)
            self.__SetHelper('CuelistLevel', CuelistLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCuelistLevel')

    def SetGoToCuelist(self, value, qualifier):

        if 1 <= value <= 99999:
            GoToCuelistCmdString = '$mx,gql,{:05d}\r'.format(value)
            self.__SetHelper('GoToCuelist', GoToCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoToCuelist')
    def SetGoToCuelistCue(self, value, qualifier):

        cuelist = qualifier['Cuelist']

        if 1 <= cuelist <= 99999 and 1 <= value <= 99999:
            GoToCuelistCueCmdString = '$mx,gtq,{:05d},{:05d}\r'.format(cuelist, value)
            self.__SetHelper('GoToCuelistCue', GoToCuelistCueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoToCuelistCue')
    def SetLoadAction(self, value, qualifier):

        if 1 <= value <= 9999:
            LoadActionCmdString = '$act,load,{:04d}\r'.format(value)
            self.__SetHelper('LoadAction', LoadActionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadAction')
    def SetLoadSchedule(self, value, qualifier):

        if 1 <= value <= 9999:
            LoadScheduleCmdString = '$sch,load,{:04d}\r'.format(value)
            self.__SetHelper('LoadSchedule', LoadScheduleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadSchedule')
    def SetPauseCuelist(self, value, qualifier):

        if 1 <= value <= 99999:
            PauseCuelistCmdString = '$mx,pql,{:05d}\r'.format(value)
            self.__SetHelper('PauseCuelist', PauseCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPauseCuelist')
    def SetReleaseCuelist(self, value, qualifier):

        if 1 <= value <= 99999:
            ReleaseCuelistCmdString = '$mx,rql,{:05d}\r'.format(value)
            self.__SetHelper('ReleaseCuelist', ReleaseCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleaseCuelist')
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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



class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'CuelistLevel': {'Parameters': ['Cuelist'], 'Status': {}},
            'GoToCuelist': { 'Status': {}},
            'GoToCuelistCue': {'Parameters': ['Cuelist'], 'Status': {}},
            'LoadAction': { 'Status': {}},
            'LoadSchedule': { 'Status': {}},
            'PauseCuelist': { 'Status': {}},
            'ReleaseCuelist': { 'Status': {}},
        }


    def SetCuelistLevel(self, value, qualifier):

        cuelist = qualifier['Cuelist']

        if 1 <= cuelist <= 99999 and 0 <= value <= 255:
            CuelistLevelCmdString = 'SQL {},{}\r\n'.format(cuelist, value)
            self.__SetHelper('CuelistLevel', CuelistLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCuelistLevel')

    def SetGoToCuelist(self, value, qualifier):

        if 1 <= value <= 99999:
            GoToCuelistCmdString = 'GQL {}\r\n'.format(value)
            self.__SetHelper('GoToCuelist', GoToCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoToCuelist')
    def SetGoToCuelistCue(self, value, qualifier):

        cuelist = qualifier['Cuelist']

        if 1 <= cuelist <= 99999 and 1 <= value <= 99999:
            GoToCuelistCueCmdString = 'GTQ {},{}\r\n'.format(cuelist, value)
            self.__SetHelper('GoToCuelistCue', GoToCuelistCueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoToCuelistCue')
    def SetLoadAction(self, value, qualifier):

        if 1 <= value <= 9999:
            LoadActionCmdString = 'ACT {}\r\n'.format(value)
            self.__SetHelper('LoadAction', LoadActionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadAction')
    def SetLoadSchedule(self, value, qualifier):

        if 1 <= value <= 9999:
            LoadScheduleCmdString = 'GSC {}\r\n'.format(value)
            self.__SetHelper('LoadSchedule', LoadScheduleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadSchedule')
    def SetPauseCuelist(self, value, qualifier):

        if 1 <= value <= 99999:
            PauseCuelistCmdString = 'PQL {}\r\n'.format(value)
            self.__SetHelper('PauseCuelist', PauseCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPauseCuelist')
    def SetReleaseCuelist(self, value, qualifier):

        if 1 <= value <= 99999:
            ReleaseCuelistCmdString = 'RQL {}\r\n'.format(value)
            self.__SetHelper('ReleaseCuelist', ReleaseCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleaseCuelist')
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=4800, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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