from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DirectArcPower': {'Parameters':['Unit ID','Address'], 'Status': {}},
            'Mode': {'Parameters':['Unit ID','Address'], 'Status': {}},
            'Scene': {'Parameters':['Unit ID','Address'], 'Status': {}}
        }

    def commandHelper(self, unitID, commandString):

        UnitIDStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x04',
            '4': b'\x08'
            }

        TransactionIDByte = self.DefineTransactionID()
        SequenceNumberByte = self.DefineSequenceNumber()

        commandLength = (len(commandString) + 13).to_bytes(2, byteorder="big")
        return b''.join([TransactionIDByte, b'\x00\x00', commandLength, UnitIDStates[unitID], b'\x17\x00\x65\x00\x05\x00\x64\x00\x06\x0C\x12', SequenceNumberByte, commandString])

    def DefineTransactionID(self):

        try:
            TransactionIDByte = self.TransactionID.to_bytes(2, byteorder="big")
        except:
            self.TransactionID = 1
            TransactionIDByte = self.TransactionID.to_bytes(2, byteorder="big")

        self.TransactionID += 1
        return TransactionIDByte

    def DefineSequenceNumber(self):

        try:
            SequenceNumberByte = self.SequenceNumber.to_bytes(1, byteorder="big")
        except:
            self.SequenceNumber = 1
            SequenceNumberByte = self.SequenceNumber.to_bytes(1, byteorder="big")

        self.SequenceNumber += 1
        return SequenceNumberByte
    
    def SetDirectArcPower(self, value, qualifier):

        AddressStates = {
            'A0'        : b'\x00',
            'A1'        : b'\x02',
            'A2'        : b'\x04',
            'A3'        : b'\x06',
            'A4'        : b'\x08',
            'A5'        : b'\x0A',
            'A6'        : b'\x0C',
            'A7'        : b'\x0E',
            'A8'        : b'\x10',
            'A9'        : b'\x12',
            'A10'       : b'\x14',
            'A11'       : b'\x16',
            'A12'       : b'\x18',
            'A13'       : b'\x1A',
            'A14'       : b'\x1C',
            'A15'       : b'\x1E',
            'A16'       : b'\x20',
            'A17'       : b'\x22',
            'A18'       : b'\x24',
            'A19'       : b'\x26',
            'A20'       : b'\x28',
            'A21'       : b'\x2A',
            'A22'       : b'\x2C',
            'A23'       : b'\x2E',
            'A24'       : b'\x30',
            'A25'       : b'\x32',
            'A26'       : b'\x34',
            'A27'       : b'\x36',
            'A28'       : b'\x38',
            'A29'       : b'\x3A',
            'A30'       : b'\x3C',
            'A31'       : b'\x3E',
            'A32'       : b'\x40',
            'A33'       : b'\x42',
            'A34'       : b'\x44',
            'A35'       : b'\x46',
            'A36'       : b'\x48',
            'A37'       : b'\x4A',
            'A38'       : b'\x4C',
            'A39'       : b'\x4E',
            'A40'       : b'\x50',
            'A41'       : b'\x52',
            'A42'       : b'\x54',
            'A43'       : b'\x56',
            'A44'       : b'\x58',
            'A45'       : b'\x5A',
            'A46'       : b'\x5C',
            'A47'       : b'\x5E',
            'A48'       : b'\x60',
            'A49'       : b'\x62',
            'A50'       : b'\x64',
            'A51'       : b'\x66',
            'A52'       : b'\x68',
            'A53'       : b'\x6A',
            'A54'       : b'\x6C',
            'A55'       : b'\x6E',
            'A56'       : b'\x70',
            'A57'       : b'\x72',
            'A58'       : b'\x74',
            'A59'       : b'\x76',
            'A60'       : b'\x78',
            'A61'       : b'\x7A',
            'A62'       : b'\x7C',
            'A63'       : b'\x7E',
            'G0'        : b'\x80',
            'G1'        : b'\x82',
            'G2'        : b'\x84',
            'G3'        : b'\x86',
            'G4'        : b'\x88',
            'G5'        : b'\x8A',
            'G6'        : b'\x8C',
            'G7'        : b'\x8E',
            'G8'        : b'\x90',
            'G9'        : b'\x92',
            'G10'       : b'\x94',
            'G11'       : b'\x96',
            'G12'       : b'\x98',
            'G13'       : b'\x9A',
            'G14'       : b'\x9C',
            'G15'       : b'\x9E',
            'All (Not Addressed)'  : b'\xFC',
            'All (DALI Broadcast)' : b'\xFE'
        }

        if 1 <= int(qualifier['Unit ID']) <= 4 and qualifier['Address'] in AddressStates and 0 <= value <= 254:
            DirectArcPowerCmdString = self.commandHelper(qualifier['Unit ID'], b'\x00\x03\x00\x00' + AddressStates[qualifier['Address']] + pack('B', value) + b'\x00\x04\x00\x00')
            self.__SetHelper('DirectArcPower', DirectArcPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDirectArcPower')

    def SetMode(self, value, qualifier):

        AddressStates = {
            'A0'        : b'\x01',
            'A1'        : b'\x03',
            'A2'        : b'\x05',
            'A3'        : b'\x07',
            'A4'        : b'\x09',
            'A5'        : b'\x0B',
            'A6'        : b'\x0D',
            'A7'        : b'\x0F',
            'A8'        : b'\x11',
            'A9'        : b'\x13',
            'A10'       : b'\x15',
            'A11'       : b'\x17',
            'A12'       : b'\x19',
            'A13'       : b'\x1B',
            'A14'       : b'\x1D',
            'A15'       : b'\x1F',
            'A16'       : b'\x21',
            'A17'       : b'\x23',
            'A18'       : b'\x25',
            'A19'       : b'\x27',
            'A20'       : b'\x29',
            'A21'       : b'\x2B',
            'A22'       : b'\x2D',
            'A23'       : b'\x2F',
            'A24'       : b'\x31',
            'A25'       : b'\x33',
            'A26'       : b'\x35',
            'A27'       : b'\x37',
            'A28'       : b'\x39',
            'A29'       : b'\x3B',
            'A30'       : b'\x3D',
            'A31'       : b'\x3F',
            'A32'       : b'\x41',
            'A33'       : b'\x43',
            'A34'       : b'\x45',
            'A35'       : b'\x47',
            'A36'       : b'\x49',
            'A37'       : b'\x4B',
            'A38'       : b'\x4D',
            'A39'       : b'\x4F',
            'A40'       : b'\x51',
            'A41'       : b'\x53',
            'A42'       : b'\x55',
            'A43'       : b'\x57',
            'A44'       : b'\x59',
            'A45'       : b'\x5B',
            'A46'       : b'\x5D',
            'A47'       : b'\x5F',
            'A48'       : b'\x61',
            'A49'       : b'\x63',
            'A50'       : b'\x65',
            'A51'       : b'\x67',
            'A52'       : b'\x69',
            'A53'       : b'\x6B',
            'A54'       : b'\x6D',
            'A55'       : b'\x6F',
            'A56'       : b'\x71',
            'A57'       : b'\x73',
            'A58'       : b'\x75',
            'A59'       : b'\x77',
            'A60'       : b'\x79',
            'A61'       : b'\x7B',
            'A62'       : b'\x7D',
            'A63'       : b'\x7F',
            'G0'        : b'\x81',
            'G1'        : b'\x83',
            'G2'        : b'\x85',
            'G3'        : b'\x87',
            'G4'        : b'\x89',
            'G5'        : b'\x8B',
            'G6'        : b'\x8D',
            'G7'        : b'\x8F',
            'G8'        : b'\x91',
            'G9'        : b'\x93',
            'G10'       : b'\x95',
            'G11'       : b'\x97',
            'G12'       : b'\x99',
            'G13'       : b'\x9B',
            'G14'       : b'\x9D',
            'G15'       : b'\x9F',
            'All (Not Addressed)'  : b'\xFD',
            'All (DALI Broadcast)' : b'\xFF'
        }

        ValueStateValues = {
            'Off'               : b'\x00',
            'Up'                : b'\x01',
            'Down'              : b'\x02',
            'Step Up'           : b'\x03',
            'Step Down'         : b'\x04',
            'Recall Max Level'  : b'\x05',
            'Recall Min Level'  : b'\x06'
        }

        if 1 <= int(qualifier['Unit ID']) <= 4 and qualifier['Address'] in AddressStates and value in ValueStateValues:
            ModeCmdString = self.commandHelper(qualifier['Unit ID'], b'\x00\x03\x00\x00' + AddressStates[qualifier['Address']] + ValueStateValues[value] + b'\x00\x04\x00\x00')
            self.__SetHelper('Mode', ModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMode')

    def SetScene(self, value, qualifier):

        AddressStates = {
            'A0'        : b'\x01',
            'A1'        : b'\x03',
            'A2'        : b'\x05',
            'A3'        : b'\x07',
            'A4'        : b'\x09',
            'A5'        : b'\x0B',
            'A6'        : b'\x0D',
            'A7'        : b'\x0F',
            'A8'        : b'\x11',
            'A9'        : b'\x13',
            'A10'       : b'\x15',
            'A11'       : b'\x17',
            'A12'       : b'\x19',
            'A13'       : b'\x1B',
            'A14'       : b'\x1D',
            'A15'       : b'\x1F',
            'A16'       : b'\x21',
            'A17'       : b'\x23',
            'A18'       : b'\x25',
            'A19'       : b'\x27',
            'A20'       : b'\x29',
            'A21'       : b'\x2B',
            'A22'       : b'\x2D',
            'A23'       : b'\x2F',
            'A24'       : b'\x31',
            'A25'       : b'\x33',
            'A26'       : b'\x35',
            'A27'       : b'\x37',
            'A28'       : b'\x39',
            'A29'       : b'\x3B',
            'A30'       : b'\x3D',
            'A31'       : b'\x3F',
            'A32'       : b'\x41',
            'A33'       : b'\x43',
            'A34'       : b'\x45',
            'A35'       : b'\x47',
            'A36'       : b'\x49',
            'A37'       : b'\x4B',
            'A38'       : b'\x4D',
            'A39'       : b'\x4F',
            'A40'       : b'\x51',
            'A41'       : b'\x53',
            'A42'       : b'\x55',
            'A43'       : b'\x57',
            'A44'       : b'\x59',
            'A45'       : b'\x5B',
            'A46'       : b'\x5D',
            'A47'       : b'\x5F',
            'A48'       : b'\x61',
            'A49'       : b'\x63',
            'A50'       : b'\x65',
            'A51'       : b'\x67',
            'A52'       : b'\x69',
            'A53'       : b'\x6B',
            'A54'       : b'\x6D',
            'A55'       : b'\x6F',
            'A56'       : b'\x71',
            'A57'       : b'\x73',
            'A58'       : b'\x75',
            'A59'       : b'\x77',
            'A60'       : b'\x79',
            'A61'       : b'\x7B',
            'A62'       : b'\x7D',
            'A63'       : b'\x7F',
            'G0'        : b'\x81',
            'G1'        : b'\x83',
            'G2'        : b'\x85',
            'G3'        : b'\x87',
            'G4'        : b'\x89',
            'G5'        : b'\x8B',
            'G6'        : b'\x8D',
            'G7'        : b'\x8F',
            'G8'        : b'\x91',
            'G9'        : b'\x93',
            'G10'       : b'\x95',
            'G11'       : b'\x97',
            'G12'       : b'\x99',
            'G13'       : b'\x9B',
            'G14'       : b'\x9D',
            'G15'       : b'\x9F',
            'All (Not Addressed)'  : b'\xFD',
            'All (DALI Broadcast)' : b'\xFF'
        }

        ValueStateValues = {
            '0'  : b'\x10',
            '1'  : b'\x11',
            '2'  : b'\x12',
            '3'  : b'\x13',
            '4'  : b'\x14',
            '5'  : b'\x15',
            '6'  : b'\x16',
            '7'  : b'\x17',
            '8'  : b'\x18',
            '9'  : b'\x19',
            '10' : b'\x1A',
            '11' : b'\x1B',
            '12' : b'\x1C',
            '13' : b'\x1D',
            '14' : b'\x1E',
            '15' : b'\x1F'
        }

        if 1 <= int(qualifier['Unit ID']) <= 4 and qualifier['Address'] in AddressStates and value in ValueStateValues:
            SceneCmdString = self.commandHelper(qualifier['Unit ID'], b'\x00\x03\x00\x00' + AddressStates[qualifier['Address']] + ValueStateValues[value] + b'\x00\x04\x00\x00')
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

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