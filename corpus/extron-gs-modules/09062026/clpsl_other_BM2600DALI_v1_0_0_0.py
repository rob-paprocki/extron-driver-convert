from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DimLevel': {'Parameters': ['Group Address'], 'Status': {}},
            'Scene': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep1': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep2': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep3': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep4': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep5': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep6': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep7': {'Parameters': ['Group Address'], 'Status': {}},
            'SequenceStep8': {'Parameters': ['Group Address'], 'Status': {}},
            'SwitchLight': {'Parameters': ['Group Address'], 'Status': {}},
        }
        self._ControllerID ='000'

    @property
    def ControllerID(self):
        return self._ControllerID

    @ControllerID.setter
    def ControllerID(self, value):
        if 0<= int(value) <= 254:
            self._ControllerID = '{0:03X}'.format(value)
        else:
            print('Invalid ControllerID entered, range is from 0 to 254')

    def SetDimLevel(self, value, qualifier):

        ValueStateValues = {
            'Up': '01',
            'Down': '02',
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            DimLevelCmdString = '${0}015007{1}80{2}00*'.format(self.ControllerID, GroupAddress, ValueStateValues[value])
            self.__SetHelper('DimLevel', DimLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimLevel')

    def SetScene(self, value, qualifier):

        ValueStateValues = {
            '0': '16',
            '1': '17',
            '2': '18',
            '3': '19',
            '4': '20',
            '5': '21',
            '6': '22',
            '7': '23',
            '8': '24',
            '9': '25',
            '10': '26',
            '11': '27',
            '12': '28',
            '13': '29',
            '14': '30',
            '15': '31'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SceneCmdString = '${0}015007{1}80{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def SetSequenceStep1(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            '11': '10',
            '12': '11',
            '13': '12',
            '14': '13',
            '15': '14',
            '16': '15',
            '17': '16',
            '18': '17',
            '19': '18',
            '20': '19',
            '21': '20',
            '22': '21',
            '23': '22',
            '24': '23',
            '25': '24',
            '26': '25',
            '27': '26',
            '28': '27',
            '29': '28',
            '30': '29',
            '31': '30',
            '32': '31'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep1CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep1', SequenceStep1CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep1')

    def SetSequenceStep2(self, value, qualifier):

        ValueStateValues = {
            '1': '32',
            '2': '33',
            '3': '34',
            '4': '35',
            '5': '36',
            '6': '37',
            '7': '38',
            '8': '39',
            '9': '40',
            '10': '41',
            '11': '42',
            '12': '43',
            '13': '44',
            '14': '45',
            '15': '46',
            '16': '47',
            '17': '48',
            '18': '49',
            '19': '50',
            '20': '51',
            '21': '52',
            '22': '53',
            '23': '54',
            '24': '55',
            '25': '56',
            '26': '57',
            '27': '58',
            '28': '59',
            '29': '60',
            '30': '61',
            '31': '62',
            '32': '63'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep2CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep2', SequenceStep2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep2')

    def SetSequenceStep3(self, value, qualifier):

        ValueStateValues = {
            '1': '64',
            '2': '65',
            '3': '66',
            '4': '67',
            '5': '68',
            '6': '69',
            '7': '70',
            '8': '71',
            '9': '72',
            '10': '73',
            '11': '74',
            '12': '75',
            '13': '76',
            '14': '77',
            '15': '78',
            '16': '79',
            '17': '80',
            '18': '81',
            '19': '82',
            '20': '83',
            '21': '84',
            '22': '85',
            '23': '86',
            '24': '87',
            '25': '88',
            '26': '89',
            '27': '90',
            '28': '91',
            '29': '92',
            '30': '93',
            '31': '94',
            '32': '95'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep3CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep3', SequenceStep3CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep3')

    def SetSequenceStep4(self, value, qualifier):

        ValueStateValues = {
            '1': '96',
            '2': '97',
            '3': '98',
            '4': '99',
            '5': '100',
            '6': '101',
            '7': '102',
            '8': '103',
            '9': '104',
            '10': '105',
            '11': '106',
            '12': '107',
            '13': '108',
            '14': '109',
            '15': '110',
            '16': '111',
            '17': '112',
            '18': '113',
            '19': '114',
            '20': '115',
            '21': '116',
            '22': '117',
            '23': '118',
            '24': '119',
            '25': '120',
            '26': '121',
            '27': '122',
            '28': '123',
            '29': '124',
            '30': '125',
            '31': '126',
            '32': '127'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep4CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep4', SequenceStep4CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep4')

    def SetSequenceStep5(self, value, qualifier):

        ValueStateValues = {
            '1': '128',
            '2': '129',
            '3': '130',
            '4': '131',
            '5': '132',
            '6': '133',
            '7': '134',
            '8': '135',
            '9': '136',
            '10': '137',
            '11': '138',
            '12': '139',
            '13': '140',
            '14': '141',
            '15': '142',
            '16': '143',
            '17': '144',
            '18': '145',
            '19': '146',
            '20': '147',
            '21': '148',
            '22': '149',
            '23': '150',
            '24': '151',
            '25': '152',
            '26': '153',
            '27': '154',
            '28': '155',
            '29': '156',
            '30': '157',
            '31': '158',
            '32': '159'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep5CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep5', SequenceStep5CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep5')

    def SetSequenceStep6(self, value, qualifier):

        ValueStateValues = {
            '1': '160',
            '2': '161',
            '3': '162',
            '4': '163',
            '5': '164',
            '6': '165',
            '7': '166',
            '8': '167',
            '9': '168',
            '10': '169',
            '11': '170',
            '12': '171',
            '13': '172',
            '14': '173',
            '15': '174',
            '16': '175',
            '17': '176',
            '18': '177',
            '19': '178',
            '20': '179',
            '21': '180',
            '22': '181',
            '23': '182',
            '24': '183',
            '25': '184',
            '26': '185',
            '27': '186',
            '28': '187',
            '29': '188',
            '30': '189',
            '31': '190',
            '32': '191'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep6CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep6', SequenceStep6CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep6')

    def SetSequenceStep7(self, value, qualifier):

        ValueStateValues = {
            '1': '192',
            '2': '193',
            '3': '194',
            '4': '195',
            '5': '196',
            '6': '197',
            '7': '198',
            '8': '199',
            '9': '200',
            '10': '201',
            '11': '202',
            '12': '203',
            '13': '204',
            '14': '205',
            '15': '206',
            '16': '207',
            '17': '208',
            '18': '209',
            '19': '210',
            '20': '211',
            '21': '212',
            '22': '213',
            '23': '214',
            '24': '215',
            '25': '216',
            '26': '217',
            '27': '218',
            '28': '219',
            '29': '220',
            '30': '221',
            '31': '222',
            '32': '223'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep7CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep7', SequenceStep7CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep7')

    def SetSequenceStep8(self, value, qualifier):

        ValueStateValues = {
            '1': '224',
            '2': '225',
            '3': '226',
            '4': '227',
            '5': '228',
            '6': '229',
            '7': '230',
            '8': '231',
            '9': '232',
            '10': '233',
            '11': '234',
            '12': '235',
            '13': '236',
            '14': '237',
            '15': '238',
            '16': '239',
            '17': '240',
            '18': '241',
            '19': '242',
            '20': '243',
            '21': '244',
            '22': '245',
            '23': '246',
            '24': '247',
            '25': '248',
            '26': '249',
            '27': '250',
            '28': '251',
            '29': '252',
            '30': '253',
            '31': '254',
            '32': '255'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            Value = '{:02X}'.format(int(ValueStateValues[value]))
            SequenceStep8CmdString = '${0}015007{1}82{2}00*'.format(self.ControllerID, GroupAddress, Value)
            self.__SetHelper('SequenceStep8', SequenceStep8CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceStep8')

    def SetSwitchLight(self, value, qualifier):

        ValueStateValues = {
            'On': '05',
            'Off': '00'
        }

        GA = int(qualifier['Group Address'])
        if 0 <= GA <= 128:
            GroupAddress = '{:03X}'.format(GA)
            SwitchLightCmdString = '${0}015007{1}80{2}00*'.format(self.ControllerID, GroupAddress, ValueStateValues[value])
            self.__SetHelper('SwitchLight', SwitchLightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchLight')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')


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
