from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:


    
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'CueList': {'Parameters':['Cue'], 'Status': {}},
            'Intensity': {'Parameters':['Master'], 'Status': {}},
            'MutexGroup': {'Parameters':['Group'], 'Status': {}},
            'StopAllCuelist': { 'Status': {}},
            }


    def SetCueList(self, value, qualifier):


        ValueStateValues = {
            'Play' : 'PC', 
            'Pause (Toggle)' : 'PP', 
            'Stop' : 'ST'
        }
        cue = int(qualifier['Cue'])
        if 1 <= cue <= 999:
            CueListCmdString = '{0}{1:03d}\r\n'.format(ValueStateValues[value], cue)
            self.__SetHelper('CueList', CueListCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCueList')

    def SetIntensity(self, value, qualifier):

        MasterStates = {
            'Grand Master' : '0', 
            'Cuelist Master 1' : '1', 
            'Cuelist Master 2' : '2', 
            'Cuelist Master 3' : '3', 
            'Cuelist Master 4' : '4', 
            'Cuelist Master 5' : '5', 
            'Cuelist Master 6' : '6', 
            'Cuelist Master 7' : '7', 
            'Cuelist Master 8' : '8', 
            'Cuelist Master 9' : '9', 
            'Cuelist Master 10' : '10', 
            'Cuelist Master 11' : '11', 
            'Cuelist Master 12' : '12', 
            'Cuelist Master 13' : '13', 
            'Cuelist Master 14' : '14', 
            'Cuelist Master 15' : '15', 
            'Cuelist Master 16' : '16', 
            'Cuelist Master 17' : '17', 
            'Cuelist Master 18' : '18', 
            'Cuelist Master 19' : '19', 
            'Cuelist Master 20' : '20', 
            'Cuelist Master 21' : '21', 
            'Cuelist Master 22' : '22', 
            'Cuelist Master 23' : '23', 
            'Cuelist Master 24' : '24', 
            'Cuelist Master 25' : '25', 
            'Cuelist Master 26' : '26', 
            'Cuelist Master 27' : '27', 
            'Cuelist Master 28' : '28', 
            'Cuelist Master 29' : '29', 
            'Cuelist Master 30' : '30', 
            'Cuelist Master 31' : '31', 
            'Cuelist Master 32' : '32', 
            'Cuelist Master 33' : '33', 
            'Cuelist Master 34' : '34', 
            'Cuelist Master 35' : '35', 
            'Cuelist Master 36' : '36', 
            'Cuelist Master 37' : '37', 
            'Cuelist Master 38' : '38', 
            'Cuelist Master 39' : '39', 
            'Cuelist Master 40' : '40', 
            'Cuelist Master 41' : '41', 
            'Cuelist Master 42' : '42', 
            'Cuelist Master 43' : '43', 
            'Cuelist Master 44' : '44', 
            'Cuelist Master 45' : '45', 
            'Cuelist Master 46' : '46', 
            'Cuelist Master 47' : '47', 
            'Cuelist Master 48' : '48', 
            'Cuelist Master 49' : '49', 
            'Cuelist Master 50' : '50', 
            'Cuelist Master 51' : '51', 
            'Cuelist Master 52' : '52', 
            'Cuelist Master 53' : '53', 
            'Cuelist Master 54' : '54', 
            'Cuelist Master 55' : '55', 
            'Cuelist Master 56' : '56', 
            'Cuelist Master 57' : '57', 
            'Cuelist Master 58' : '58', 
            'Cuelist Master 59' : '59', 
            'Cuelist Master 60' : '60', 
            'Cuelist Master 61' : '61', 
            'Cuelist Master 62' : '62', 
            'Cuelist Master 63' : '63', 
            'Cuelist Master 64' : '64', 
            'Cuelist Master 65' : '65', 
            'Cuelist Master 66' : '66', 
            'Cuelist Master 67' : '67', 
            'Cuelist Master 68' : '68', 
            'Cuelist Master 69' : '69', 
            'Cuelist Master 70' : '70', 
            'Cuelist Master 71' : '71', 
            'Cuelist Master 72' : '72', 
            'Cuelist Master 73' : '73', 
            'Cuelist Master 74' : '74', 
            'Cuelist Master 75' : '75', 
            'Cuelist Master 76' : '76', 
            'Cuelist Master 77' : '77', 
            'Cuelist Master 78' : '78', 
            'Cuelist Master 79' : '79', 
            'Cuelist Master 80' : '80', 
            'Cuelist Master 81' : '81', 
            'Cuelist Master 82' : '82', 
            'Cuelist Master 83' : '83', 
            'Cuelist Master 84' : '84', 
            'Cuelist Master 85' : '85', 
            'Cuelist Master 86' : '86', 
            'Cuelist Master 87' : '87', 
            'Cuelist Master 88' : '88', 
            'Cuelist Master 89' : '89', 
            'Cuelist Master 90' : '90', 
            'Cuelist Master 91' : '91', 
            'Cuelist Master 92' : '92', 
            'Cuelist Master 93' : '93', 
            'Cuelist Master 94' : '94', 
            'Cuelist Master 95' : '95', 
            'Cuelist Master 96' : '96', 
            'Cuelist Master 97' : '97', 
            'Cuelist Master 98' : '98', 
            'Cuelist Master 99' : '99', 
            'V-Master 1' : '129', 
            'V-Master 2' : '130', 
            'V-Master 3' : '131', 
            'V-Master 4' : '132', 
            'V-Master 5' : '133', 
            'V-Master 6' : '134', 
            'V-Master 7' : '135', 
            'V-Master 8' : '136', 
            'V-Master 9' : '137', 
            'V-Master 10' : '138', 
            'V-Master 11' : '139', 
            'V-Master 12' : '140', 
            'V-Master 13' : '141', 
            'V-Master 14' : '142', 
            'V-Master 15' : '143', 
            'V-Master 16' : '144', 
            'V-Master 17' : '145', 
            'V-Master 18' : '146', 
            'V-Master 19' : '147', 
            'V-Master 20' : '148', 
            'V-Master 21' : '149', 
            'V-Master 22' : '150', 
            'V-Master 23' : '151', 
            'V-Master 24' : '152', 
            'V-Master 25' : '153', 
            'V-Master 26' : '154', 
            'V-Master 27' : '155', 
            'V-Master 28' : '156', 
            'V-Master 29' : '157', 
            'V-Master 30' : '158', 
            'V-Master 31' : '159', 
            'V-Master 32' : '160', 
            'V-Master 33' : '161', 
            'V-Master 34' : '162', 
            'V-Master 35' : '163', 
            'V-Master 36' : '164', 
            'V-Master 37' : '165', 
            'V-Master 38' : '166', 
            'V-Master 39' : '167', 
            'V-Master 40' : '168', 
            'V-Master 41' : '169', 
            'V-Master 42' : '170', 
            'V-Master 43' : '171', 
            'V-Master 44' : '172', 
            'V-Master 45' : '173', 
            'V-Master 46' : '174', 
            'V-Master 47' : '175', 
            'V-Master 48' : '176', 
            'V-Master 49' : '177', 
            'V-Master 50' : '178', 
            'V-Master 51' : '179', 
            'V-Master 52' : '180', 
            'V-Master 53' : '181', 
            'V-Master 54' : '182', 
            'V-Master 55' : '183', 
            'V-Master 56' : '184', 
            'V-Master 57' : '185', 
            'V-Master 58' : '186', 
            'V-Master 59' : '187', 
            'V-Master 60' : '188', 
            'V-Master 61' : '189', 
            'V-Master 62' : '190', 
            'V-Master 63' : '191', 
            'V-Master 64' : '192', 
            'V-Master 65' : '193'
        }

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        master = qualifier['Master']
        if (master in MasterStates) and (ValueConstraints['Min'] <= value <= ValueConstraints['Max']):
            IntensityCmdString = 'IN{0:03d}{1:03d}\r\n'.format(int(MasterStates[master]), value)
            self.__SetHelper('Intensity', IntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIntensity')
    def SetMutexGroup(self, value, qualifier):


        ValueStateValues = {
            'Next'     : 'NX', 
            'Previous' : 'PV'
        }
        grp = int(qualifier['Group'])
        if 1 <= grp <= 999:
            MutexGroupCmdString = '{0}{1:03d}\r\n'.format(ValueStateValues[value], grp)
            self.__SetHelper('MutexGroup', MutexGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMutexGroup')

    def SetStopAllCuelist(self, value, qualifier):

        StopAllCuelistCmdString = 'ST000\r\n'
        self.__SetHelper('StopAllCuelist', StopAllCuelistCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

    
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

