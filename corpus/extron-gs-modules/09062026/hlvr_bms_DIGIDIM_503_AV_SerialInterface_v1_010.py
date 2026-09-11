from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:

    
    
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'BroadcastLevel': { 'Status': {}},
            'BroadcastPower': { 'Status': {}},
            'BroadcastRecallLevel': { 'Status': {}},
            'ButtonPress': {'Parameters':['Device ID'], 'Status': {}},
            'GroupLevel': {'Parameters': ['Group'], 'Status': {}},
            'GroupPower': {'Parameters': ['Group'], 'Status': {}},
            'RecallGroupLevel': {'Parameters': ['Group'], 'Status': {}},
            'RecallAddressScene': {'Parameters': ['Address'], 'Status': {}},
            'BroadcastRecallScene': { 'Status': {}},
            'RecallGroupScene': {'Parameters': ['Group'], 'Status': {}},
            'RecallAddressLevel': {'Parameters': ['Address'], 'Status': {}},
            'AddressLevel': {'Parameters': ['Address'], 'Status': {}},
            'AddressPower': {'Parameters': ['Address'], 'Status': {}},
        }




    def SetBroadcastLevel(self, value, qualifier):

        LevelRange = {
            'Min' : 0,
            'Max' : 254
        }
        
        if LevelRange['Min'] <= value <= LevelRange['Max']:
            CommandString = b''.join([b'\x03\x51\xFE', value.to_bytes(1, 'big')])
            self.__SetHelper('BroadcastLevel', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBroadcastLevel')
    def SetBroadcastPower(self, value, qualifier):

        PowerControlsDic = {
            'On' : b'\x08',
            'Off' : b'\x07'
        }

        CommandString = b''.join([b'\x03\x51\xFF', PowerControlsDic[value]])
        self.__SetHelper('BroadcastPower', CommandString, value, qualifier)




    def SetBroadcastRecallLevel(self, value, qualifier):

        RecallLevelDic = {
            'Minimum' : b'\x06',
            'Maximum' : b'\x05'
        }

        CommandString = b''.join([b'\x03\x51\xFF', RecallLevelDic[value]])
        self.__SetHelper('BroadcastRecallLevel', CommandString, value, qualifier)


    

    def SetButtonPress(self, value, qualifier):

        DeviceIDStates = {
            '1' : b'\x01', 
            '2' : b'\x03', 
            '3' : b'\x05', 
            '4' : b'\x07', 
            '5' : b'\x09', 
            '6' : b'\x0B', 
            '7' : b'\x0D', 
            '8' : b'\x0F', 
            '9' : b'\x11', 
            '10' : b'\x13', 
            '11' : b'\x15', 
            '12' : b'\x17', 
            '13' : b'\x19', 
            '14' : b'\x1B', 
            '15' : b'\x1D', 
            '16' : b'\x1F', 
            '17' : b'\x21', 
            '18' : b'\x23', 
            '19' : b'\x25', 
            '20' : b'\x27', 
            '21' : b'\x29', 
            '22' : b'\x2B', 
            '23' : b'\x2D', 
            '24' : b'\x2F', 
            '25' : b'\x31', 
            '26' : b'\x33', 
            '27' : b'\x35', 
            '28' : b'\x37', 
            '29' : b'\x39', 
            '30' : b'\x3B', 
            '31' : b'\x3D', 
            '32' : b'\x3F', 
            '33' : b'\x41', 
            '34' : b'\x43', 
            '35' : b'\x45', 
            '36' : b'\x47', 
            '37' : b'\x49', 
            '38' : b'\x4B', 
            '39' : b'\x4D', 
            '40' : b'\x4F', 
            '41' : b'\x51', 
            '42' : b'\x53', 
            '43' : b'\x55', 
            '44' : b'\x57', 
            '45' : b'\x59', 
            '46' : b'\x5B', 
            '47' : b'\x5D', 
            '48' : b'\x5F', 
            '49' : b'\x61', 
            '50' : b'\x63', 
            '51' : b'\x65', 
            '52' : b'\x67', 
            '53' : b'\x69', 
            '54' : b'\x6B', 
            '55' : b'\x6D', 
            '56' : b'\x6F', 
            '57' : b'\x71', 
            '58' : b'\x73', 
            '59' : b'\x75', 
            '60' : b'\x77', 
            '61' : b'\x79', 
            '62' : b'\x7B', 
            '63' : b'\x7D', 
            '64' : b'\x7F'
        }

        ValueStateValues = {
            '1' : b'\x40', 
            '2' : b'\x41', 
            '3' : b'\x42', 
            '4' : b'\x43', 
            '5' : b'\x45', 
            '6' : b'\x46', 
            '7' : b'\x47', 
            '0' : b'\x44'
        }
        Deviceid = qualifier['Device ID']
        if Deviceid in DeviceIDStates:
            ButtonPressCmdString = b''.join([b'\x03\x59', DeviceIDStates[Deviceid], ValueStateValues[value]])
            self.__SetHelper('ButtonPress', ButtonPressCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButtonPress')

    

    def SetGroupLevel(self, value, qualifier):

        GroupDic = {
            '1' : b'\x80',
            '2' : b'\x82',
            '3' : b'\x84',
            '4' : b'\x86',
            '5' : b'\x88',
            '6' : b'\x8A',
            '7' : b'\x8C',
            '8' : b'\x8E',
            '9' : b'\x90',
            '10' : b'\x92',
            '11' : b'\x94',
            '12' : b'\x96',
            '13' : b'\x98',
            '14' : b'\x9A',
            '15' : b'\x9C',
            '16' : b'\x9E'
        }

        LevelRange = {
            'Min' : 0,
            'Max' : 254
        }

        Group = qualifier['Group']

        if Group in GroupDic:
            if LevelRange['Min'] <= value <= LevelRange['Max']:
                CommandString = b''.join([b'\x03\x51', GroupDic[Group], value.to_bytes(1, 'big')])
                self.__SetHelper('GroupLevel', CommandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetGroupLevel')
        else:
            self.Discard('Invalid Command for SetGroupLevel')
    def SetGroupPower(self, value, qualifier):

        PowerControlsDic = {
            'On' : b'\x08',
            'Off' : b'\x07'
        }

        GroupDic = {
            '1' : b'\x81',
            '2' : b'\x83',
            '3' : b'\x85',
            '4' : b'\x87',
            '5' : b'\x89',
            '6' : b'\x8B',
            '7' : b'\x8D',
            '8' : b'\x8F',
            '9' : b'\x91',
            '10' : b'\x93',
            '11' : b'\x95',
            '12' : b'\x97',
            '13' : b'\x99',
            '14' : b'\x9B',
            '15' : b'\x9D',
            '16' : b'\x9F'
        }

        Group = qualifier['Group']

        if Group in GroupDic:
            CommandString = b''.join([b'\x03\x51', GroupDic[Group], PowerControlsDic[value]])
            self.__SetHelper('GroupPower', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPower')




    def SetRecallGroupLevel(self, value, qualifier):

        RecallLevelDic = {
            'Minimum' : b'\x06',
            'Maximum' : b'\x05'
        }

        GroupDic = {
            '1' : b'\x81',
            '2' : b'\x83',
            '3' : b'\x85',
            '4' : b'\x87',
            '5' : b'\x89',
            '6' : b'\x8B',
            '7' : b'\x8D',
            '8' : b'\x8F',
            '9' : b'\x91',
            '10' : b'\x93',
            '11' : b'\x95',
            '12' : b'\x97',
            '13' : b'\x99',
            '14' : b'\x9B',
            '15' : b'\x9D',
            '16' : b'\x9F'
        }

        Group = qualifier['Group']

        if Group in GroupDic:
            CommandString = b''.join([b'\x03\x51', GroupDic[Group], RecallLevelDic[value]])
            self.__SetHelper('RecallGroupLevel', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallGroupLevel')



    def SetBroadcastRecallScene(self, value, qualifier):

        scene_limits = {
                'min' : 1,
                'max' : 16
                }
        
        scene = int(value)

        ok = scene_limits['min'] <= scene <= scene_limits['max']

        if ok:


            scene = (scene - 1) | 0x10
            
            CommandString = b''.join([b'\x03\x51\xFF', scene.to_bytes(1, 'big')])
            self.__SetHelper('BroadcastRecallScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBroadcastRecallScene')



    def SetRecallGroupScene(self, value, qualifier):

        GroupDic = {
            '1' : b'\x81',
            '2' : b'\x83',
            '3' : b'\x85',
            '4' : b'\x87',
            '5' : b'\x89',
            '6' : b'\x8B',
            '7' : b'\x8D',
            '8' : b'\x8F',
            '9' : b'\x91',
            '10' : b'\x93',
            '11' : b'\x95',
            '12' : b'\x97',
            '13' : b'\x99',
            '14' : b'\x9B',
            '15' : b'\x9D',
            '16' : b'\x9F'
        }

        scene_limits = {
                'min' : 1,
                'max' : 16
                }
        
        Group = qualifier['Group']
        scene = int(value)

        ok = Group in GroupDic
        ok &= scene_limits['min'] <= scene <= scene_limits['max']

        if ok:


            scene = (scene - 1) | 0x10
            
            CommandString = b''.join([b'\x03\x51', GroupDic[Group], scene.to_bytes(1, 'big')])
            self.__SetHelper('RecallGroupScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallGroupScene')



    def SetRecallAddressScene(self, value, qualifier):

        addr_limits = {
                'min' : 1,
                'max' : 63
                }

        scene_limits = {
                'min' : 1,
                'max' : 16
                }
        
        addr = int(qualifier['Address'])
        scene = int(value)

        ok = addr_limits['min'] <= addr <= addr_limits['max']
        ok &= scene_limits['min'] <= scene <= scene_limits['max']

        if ok:

            addr = ((addr - 1) << 1) | 0x01
            scene = (scene - 1) | 0x10
            
            CommandString = b''.join([b'\x03\x51', addr.to_bytes(1, 'big'), scene.to_bytes(1, 'big')])
            self.__SetHelper('RecallAddressScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallAddressScene')




    def SetRecallAddressLevel(self, value, qualifier):

        RecallLevelDic = {
            'Minimum' : b'\x06',
            'Maximum' : b'\x05'
        }
        
        short = int(qualifier['Address'])

        if short != 1:
            short = short - 1
            short = short << 1
            short = short | 1

        if 1 <= int(qualifier['Address']) <= 63:
            CommandString = b''.join([b'\x03\x51', short.to_bytes(1,'big'), RecallLevelDic[value]])
            self.__SetHelper('RecallAddressLevel', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallAddressLevel')




    def SetAddressLevel(self, value, qualifier):

        LevelRange = {
            'Min' : 0,
            'Max' : 254
        }

        short = int(qualifier['Address'])

        short = short - 1
        short = short << 1

        if 1 <= int(qualifier['Address']) <= 63:
            if LevelRange['Min'] <= value <= LevelRange['Max']:
                CommandString = b''.join([b'\x03\x51', short.to_bytes(1, 'big'), value.to_bytes(1, 'big')])
                self.__SetHelper('AddressLevel', CommandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetAddressLevel')
        else:
            self.Discard('Invalid Command for SetAddressLevel')
    def SetAddressPower(self, value, qualifier):

        PowerControlDic = {
            'On' : b'\x08',
            'Off' : b'\x07'
        }

        short = int(qualifier['Address'])

        if short != 1:
            short = short - 1
            short = short << 1
            short = short | 1

        if 1 <= int(qualifier['Address']) <= 63:
            CommandString = b''.join([b'\x03\x51', short.to_bytes(1, 'big'), PowerControlDic[value]])
            self.__SetHelper('AddressPower', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAddressPower')





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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

