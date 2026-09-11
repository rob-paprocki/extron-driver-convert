# Copyright 2026, Extron. All rights reserved.

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutomixerGateSet': {'Parameters':['Input'], 'Status': {}},
            'AutomixerGateStatus': {'Parameters':['Input'], 'Status': {}},               
            'DanteInputGain': {'Parameters':['Dante Device','Input'], 'Status': {}},
            'DanteInputMute': {'Parameters':['Dante Device','Input'], 'Status': {}},
            'DanteOutputAttenuation': {'Parameters':['Dante Device','Output'], 'Status': {}},
            'DanteOutputMute': {'Parameters':['Dante Device','Output'], 'Status': {}},
            'DantePresetRecall': {'Parameters':['Dante Device'], 'Status': {}},
            'DigitalInputGain': {'Parameters':['Input'], 'Status': {}},
            'GroupBassInputFilter': {'Parameters':['Group'], 'Status': {}},
            'GroupBassVirtualReturnFilter': {'Parameters':['Group'], 'Status': {}},
            'GroupMeterLevel': {'Parameters':['Group','Channel'], 'Status': {}},
            'GroupMeterMode': {'Parameters':['Group'], 'Status': {}},
            'GroupMeterResponseRate': { 'Status': {}},
            'GroupMeterSelect': { 'Status': {}},
            'GroupMicLineInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters':['Group'], 'Status': {}},
            'GroupPostMixerTrim': {'Parameters':['Group'], 'Status': {}},
            'GroupPreMixerGain': {'Parameters':['Group'], 'Status': {}},
            'GroupTrebleInputFilter': {'Parameters':['Group'], 'Status': {}},
            'GroupTrebleVirtualReturnFilter': {'Parameters':['Group'], 'Status': {}},
            'GroupVirtualReturnGain': {'Parameters':['Group'], 'Status': {}},
            'InputFilterBoostCut': {'Parameters':['Input','Filter'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'InputSignalLevelMonitor': {'Parameters':['Input', 'Monitoring Threshold'], 'Status': {}},
            'InputSource': {'Parameters':['Input'], 'Status': {}},
            'Macro': {'Parameters':['Macro'], 'Status': {}},
            'MixpointGain': {'Parameters':['Input','Output'], 'Status': {}},
            'MixpointMute': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'OutputPostmixerTrim': {'Parameters':['Output'], 'Status': {}},
            'OutputAttenuation': {'Parameters':['Output'], 'Status': {}},
            'PartNumber': { 'Status': {}},
            'PremixerGain': {'Parameters':['Input'], 'Status': {}},
            'PremixerMute': {'Parameters':['Input'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'VirtualReturnGain': {'Parameters':['Input'], 'Status': {}},
            'VirtualReturnMute': {'Parameters':['Input'], 'Status': {}}
        }



        self.DanteDevices = []
        self.GroupFunction = {} #This is to maintain a global dictionary of groups and their assigned functions
        self.VerboseDisabled = True
        self.EchoDisabled = True
        self.inputSignalLevelMonitorThreshold = {}
        self.groupMeterLevelDict = {}
        self.groupOID = {
            '40000' : 'Input 1',
            '40001' : 'Input 2',
            '40002' : 'Input 3',
            '40003' : 'Input 4',
            '40004' : 'Input 5',
            '40005' : 'Input 6',
            '40006' : 'Input 7',
            '40007' : 'Input 8',
            '40008' : 'Input 9',
            '40009' : 'Input 10',
            '40010' : 'Input 11',
            '40011' : 'Input 12',
            '40012' : 'Input 13',
            '40013' : 'Input 14',
            '40014' : 'Input 15',
            '40015' : 'Input 16',
            '40016' : 'Input 17',
            '40017' : 'Input 18',
            '40018' : 'Input 19',
            '40019' : 'Input 20',
            '40020' : 'Input 21',
            '40021' : 'Input 22',
            '40022' : 'Input 23',
            '40023' : 'Input 24',
            '40024' : 'Input 25',
            '40025' : 'Input 26',
            '40026' : 'Input 27',
            '40027' : 'Input 28',
            '40028' : 'Input 29',
            '40029' : 'Input 30',
            '40030' : 'Input 31',
            '40031' : 'Input 32',
            '40032' : 'Input 33',
            '40033' : 'Input 34',
            '40034' : 'Input 35',
            '40035' : 'Input 36',
            '40036' : 'Input 37',
            '40037' : 'Input 38',
            '40038' : 'Input 39',
            '40039' : 'Input 40',
            '40040' : 'Input 41',
            '40041' : 'Input 42',
            '40042' : 'Input 43',
            '40043' : 'Input 44',
            '40044' : 'Input 45',
            '40045' : 'Input 46',
            '40046' : 'Input 47',
            '40047' : 'Input 48',
            '60000' : 'AT Out 1',
            '60001' : 'AT Out 2',
            '60002' : 'AT Out 3',
            '60003' : 'AT Out 4',
            '60004' : 'AT Out 5',
            '60005' : 'AT Out 6',
            '60006' : 'AT Out 7',
            '60007' : 'AT Out 8',
            '60008' : 'AT Out 9',
            '60009' : 'AT Out 10',
            '60010' : 'AT Out 11',
            '60011' : 'AT Out 12',
            '60012' : 'AT Out 13',
            '60013' : 'AT Out 14',
            '60014' : 'AT Out 15',
            '60015' : 'AT Out 16',
            '60016' : 'AT Out 17',
            '60017' : 'AT Out 18',
            '60018' : 'AT Out 19',
            '60019' : 'AT Out 20',
            '60020' : 'AT Out 21',
            '60021' : 'AT Out 22',
            '60022' : 'AT Out 23',
            '60023' : 'AT Out 24',
            '60024' : 'AT Out 25',
            '60025' : 'AT Out 26',
            '60026' : 'AT Out 27',
            '60027' : 'AT Out 28',
            '60028' : 'AT Out 29',
            '60029' : 'AT Out 30',
            '60030' : 'AT Out 31',
            '60031' : 'AT Out 32',
            '60032' : 'AT Out 33',
            '60033' : 'AT Out 34',
            '60034' : 'AT Out 35',
            '60035' : 'AT Out 36',
            '60036' : 'AT Out 37',
            '60037' : 'AT Out 38',
            '60038' : 'AT Out 39',
            '60039' : 'AT Out 40',
            '60040' : 'AT Out 41',
            '60041' : 'AT Out 42',
            '60042' : 'AT Out 43',
            '60043' : 'AT Out 44',
            '60044' : 'AT Out 45',
            '60045' : 'AT Out 46',
            '60046' : 'AT Out 47',
            '60047' : 'AT Out 48'
        }

        self.MixpointOutputStateValues = {
            'AT Out#1' : '16',
            'AT Out#2' : '17',
            'AT Out#3' : '18',
            'AT Out#4' : '19',
            'AT Out#5' : '20',
            'AT Out#6' : '21',
            'AT Out#7' : '22',
            'AT Out#8' : '23',
            'AT Out#9' : '24',
            'AT Out#10' : '25',
            'AT Out#11' : '26',
            'AT Out#12' : '27',
            'AT Out#13' : '28',
            'AT Out#14' : '29',
            'AT Out#15' : '30',
            'AT Out#16' : '31',
            'AT Out#17' : '32',
            'AT Out#18' : '33',
            'AT Out#19' : '34',
            'AT Out#20' : '35',
            'AT Out#21' : '36',
            'AT Out#22' : '37',
            'AT Out#23' : '38',
            'AT Out#24' : '39',
            'AT Out#25' : '40',
            'AT Out#26' : '41',
            'AT Out#27' : '42',
            'AT Out#28' : '43',
            'AT Out#29' : '44',
            'AT Out#30' : '45',
            'AT Out#31' : '46',
            'AT Out#32' : '47',
            'AT Out#33' : '48',
            'AT Out#34' : '49',
            'AT Out#35' : '50',
            'AT Out#36' : '51',
            'AT Out#37' : '52',
            'AT Out#38' : '53',
            'AT Out#39' : '54',
            'AT Out#40' : '55',
            'AT Out#41' : '56',
            'AT Out#42' : '57',
            'AT Out#43' : '58',
            'AT Out#44' : '59',
            'AT Out#45' : '60',
            'AT Out#46' : '61',
            'AT Out#47' : '62',
            'AT Out#48' : '63',
            'V. Send A' : '00',
            'V. Send B' : '01',
            'V. Send C' : '02',
            'V. Send D' : '03',
            'V. Send E' : '04',
            'V. Send F' : '05',
            'V. Send G' : '06',
            'V. Send H' : '07',
            'V. Send I' : '08',
            'V. Send J' : '09',
            'V. Send K' : '10',
            'V. Send L' : '11',
            'V. Send M' : '12',
            'V. Send N' : '13',
            'V. Send O' : '14',
            'V. Send P' : '15'
        }

        self.MixpointOutputStateNames = {
            '16' : 'AT Out#1',
            '17' : 'AT Out#2',
            '18' : 'AT Out#3',
            '19' : 'AT Out#4',
            '20' : 'AT Out#5',
            '21' : 'AT Out#6',
            '22' : 'AT Out#7',
            '23' : 'AT Out#8',
            '24' : 'AT Out#9',
            '25' : 'AT Out#10',
            '26' : 'AT Out#11',
            '27' : 'AT Out#12',
            '28' : 'AT Out#13',
            '29' : 'AT Out#14',
            '30' : 'AT Out#15',
            '31' : 'AT Out#16',
            '32' : 'AT Out#17',
            '33' : 'AT Out#18',
            '34' : 'AT Out#19',
            '35' : 'AT Out#20',
            '36' : 'AT Out#21',
            '37' : 'AT Out#22',
            '38' : 'AT Out#23',
            '39' : 'AT Out#24',
            '40' : 'AT Out#25',
            '41' : 'AT Out#26',
            '42' : 'AT Out#27',
            '43' : 'AT Out#28',
            '44' : 'AT Out#29',
            '45' : 'AT Out#30',
            '46' : 'AT Out#31',
            '47' : 'AT Out#32',
            '48' : 'AT Out#33',
            '49' : 'AT Out#34',
            '50' : 'AT Out#35',
            '51' : 'AT Out#36',
            '52' : 'AT Out#37',
            '53' : 'AT Out#38',
            '54' : 'AT Out#39',
            '55' : 'AT Out#40',
            '56' : 'AT Out#41',
            '57' : 'AT Out#42',
            '58' : 'AT Out#43',
            '59' : 'AT Out#44',
            '60' : 'AT Out#45',
            '61' : 'AT Out#46',
            '62' : 'AT Out#47',
            '63' : 'AT Out#48',
            '00' : 'V. Send A',
            '01' : 'V. Send B',
            '02' : 'V. Send C',
            '03' : 'V. Send D',
            '04' : 'V. Send E',
            '05' : 'V. Send F',
            '06' : 'V. Send G',
            '07' : 'V. Send H',
            '08' : 'V. Send I',
            '09' : 'V. Send J',
            '10' : 'V. Send K',
            '11' : 'V. Send L',
            '12' : 'V. Send M',
            '13' : 'V. Send N',
            '14' : 'V. Send O',
            '15' : 'V. Send P'
        }

        self.MixpointInputStateValues = {
             'AT#1' : '200',
             'AT#2' : '201',
             'AT#3' : '202',
             'AT#4' : '203',
             'AT#5' : '204',
             'AT#6' : '205',
             'AT#7' : '206',
             'AT#8' : '207',
             'AT#9' : '208',
             'AT#10' : '209',
             'AT#11' : '210',
             'AT#12' : '211',
             'AT#13': '212',
             'AT#14' : '213',
             'AT#15' : '214',
             'AT#16' : '215',
             'AT#17' : '216',
             'AT#18' : '217',
             'AT#19' : '218',
             'AT#20' : '219',
             'AT#21' : '220',
             'AT#22' : '221',
             'AT#23' : '222',
             'AT#24' : '223',
             'AT#25' : '224',
             'AT#26' : '225',
             'AT#27' : '226',
             'AT#28' : '227',
             'AT#29' : '228',
             'AT#30' : '229',
             'AT#31' : '230',
             'AT#32' : '231',
             'AT#33' : '232',
             'AT#34' : '233',
             'AT#35' : '234',
             'AT#36' : '235',
             'AT#37' : '236',
             'AT#38' : '237',
             'AT#39' : '238',
             'AT#40' : '239',
             'AT#41' : '240',
             'AT#42' : '241',
             'AT#43' : '242',
             'AT#44' : '243',
             'AT#45' : '244',
             'AT#46' : '245',
             'AT#47' : '246',
             'AT#48' : '247',
             'V. Return A' : '248',
             'V. Return B' : '249',
             'V. Return C' : '250',
             'V. Return D' : '251',
             'V. Return E' : '252',
             'V. Return F' : '253',
             'V. Return G' : '254',
             'V. Return H' : '255',
             'V. Return I' : '256',
             'V. Return J' : '257',
             'V. Return K' : '258',
             'V. Return L' : '259',
             'V. Return M' : '260',
             'V. Return N' : '261',
             'V. Return O' : '262',
             'V. Return P' : '263'
        }
        self.MixpointInputStateNames = {
             '200' : 'AT#1',
             '201' : 'AT#2',
             '202' : 'AT#3',
             '203' : 'AT#4',
             '204' : 'AT#5',
             '205' : 'AT#6',
             '206' : 'AT#7',
             '207' : 'AT#8',
             '208' : 'AT#9',
             '209' : 'AT#10',
             '210' : 'AT#11',
             '211' : 'AT#12',
             '212' : 'AT#13',
             '213' : 'AT#14',
             '214' : 'AT#15',
             '215' : 'AT#16',
             '216' : 'AT#17',
             '217' : 'AT#18',
             '218' : 'AT#19',
             '219' : 'AT#20',
             '220' : 'AT#21',
             '221' : 'AT#22',
             '222' : 'AT#23',
             '223' : 'AT#24',
             '224' : 'AT#25',
             '225' : 'AT#26',
             '226' : 'AT#27',
             '227' : 'AT#28',
             '228' : 'AT#29',
             '229' : 'AT#30',
             '230' : 'AT#31',
             '231' : 'AT#32',
             '232' : 'AT#33',
             '233' : 'AT#34',
             '234' : 'AT#35',
             '235' : 'AT#36',
             '236' : 'AT#37',
             '237' : 'AT#38',
             '238' : 'AT#39',
             '239' : 'AT#40',
             '240' : 'AT#41',
             '241' : 'AT#42',
             '242' : 'AT#43',
             '243' : 'AT#44',
             '244' : 'AT#45',
             '245' : 'AT#46',
             '246' : 'AT#47',
             '247' : 'AT#48',
             '248' : 'V. Return A',
             '249' : 'V. Return B',
             '250' : 'V. Return C',
             '251' : 'V. Return D',
             '252' : 'V. Return E',
             '253' : 'V. Return F',
             '254' : 'V. Return G',
             '255' : 'V. Return H',
             '256' : 'V. Return I',
             '257' : 'V. Return J',
             '258' : 'V. Return K',
             '259' : 'V. Return L',
             '260' : 'V. Return M',
             '261' : 'V. Return N',
             '262' : 'V. Return O',
             '263' : 'V. Return P'
        }

        self.VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

        self.LevelTypes = {
            'GroupBassInputFilter'      : {'Min' : -24, 'Max' : 24},
            'GroupBassVirtualReturnFilter'  : {'Min': -24, 'Max': 24},
            'GroupMicLineInputGain'     : {'Min' : -18,  'Max' : 80},
            'GroupMixpointGain'         : {'Min' : -100,  'Max' : 12},
            'GroupOutputAttenuation'    : {'Min' : -100, 'Max' : 0},
            'GroupPostMixerTrim'        : {'Min' : -12,  'Max' : 12},
            'GroupPreMixerGain'         : {'Min' : -100, 'Max' : 12},
            'GroupTrebleInputFilter'    : {'Min': -24, 'Max': 24},
            'GroupTrebleVirtualReturnFilter': {'Min': -24, 'Max': 24},
            'GroupVirtualReturnGain'    : {'Min' : -100, 'Max' : 12},
            'MixpointGain'              : {'Min' : -100, 'Max' : 12},
            'OutputAttenuation'         : {'Min' : -100, 'Max' : 0},
            'PremixerGain'              : {'Min' : -100, 'Max' : 12},
            'VirtualReturnGain'         : {'Min' : -100, 'Max' : 12},
            'OutputPostmixerTrim'       : {'Min' : -12, 'Max' : 12},
            'DigitalInputGain'          : {'Min' : -18, 'Max' : 24},
            'DanteInputGain'            : {'Min': 0, 'Max': 42},
            'DanteOutputAttenuation'    : {'Min': -100, 'Max': 0}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DsJ(590[0-9]{2})\*([0-9]{1,4})\r\n'), self.__MatchAutomixerGateSet, None)
            self.AddMatchString(re.compile(b'DsV(590[0-9]{2})\*[10]\*([0-9]{1,4})\*?\d?\r\n'), self.__MatchAutomixerGateStatus, None) # this accounts for old fw and new fw 1.2 (\*?\d?)
            self.AddMatchString(re.compile(b'{dante@([A-Za-z0-9- ]+)}DsG(400[0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchDanteInputGain, None)
            self.AddMatchString(re.compile(b'{dante@([A-Za-z0-9- ]+)}DsM(400[0-4][0-9])\*([01])\r\n'), self.__MatchDanteInputMute, None)
            self.AddMatchString(re.compile(b'{dante@([A-Za-z0-9- ]+)}DsG(600[0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchDanteOutputAttenuation, None)
            self.AddMatchString(re.compile(b'{dante@([A-Za-z0-9- ]+)}DsM(600[0-4][0-9])\*([01])\r\n'), self.__MatchDanteOutputMute, None)
            self.AddMatchString(re.compile(b'ExprC([A-Za-z0-9- ]+)\*1\r\n'), self.__MatchDanteConnect, None)
            self.AddMatchString(re.compile(b'DsH400([0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchDigitalInputGain, None)
            self.AddMatchString(re.compile(b'(Pno60-1836-01)\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(re.compile(b'GrpmD([0-9]{1,2})\*([0-9 -]{1,5})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'GrpmO(\d{1,2})((:?\*\d{5})+)\r\n'), self.__MatchGroupMeterMember, None)
            self.AddMatchString(re.compile(b'GrpmV(\d{1,2})((:?\*\d{1,4})+)\r\n'), self.__MatchGroupMeterLevel, None)
            self.AddMatchString(re.compile(b'GrpuR(\d{1,2})\r\n'), self.__MatchGroupMeterResponseRate, None)
            self.AddMatchString(re.compile(b'GrpuG(\d{1,2})\r\n'), self.__MatchGroupMeterSelect, None)
            self.AddMatchString(re.compile(b'DsG41(\d)(\d{2})\*(-?\d{1,3})\r\n'), self.__MatchInputFilterBoostCut, None)
            self.AddMatchString(re.compile(b'DsM(400[0-4][0-9])\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'DsV(400[0-4][0-9])\*[01]\*([0-9]{1,4})\*[01]\r\n'), self.__MatchInputSignalLevelMonitor, 'Enabled')
            self.AddMatchString(re.compile(b'DsJ(400[0-4][0-9])\*0\r\n'), self.__MatchInputSignalLevelMonitor, 'Disabled')
            self.AddMatchString(re.compile(b'DsD(400[0-4][0-9])\*([0-9]{1,2})\r\n'), self.__MatchInputSource, None)
            self.AddMatchString(re.compile(b'DsG(2[0-9]{2})([0-9]{2})\*([0-9 -]{1,5})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(re.compile(b'DsM(2[0-9]{2})([0-9]{2})\*([01])\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(re.compile(b'DsM(600[0-4][0-9])\*([01])\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'DsG(601[0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchOutputPostmixerTrim, None)
            self.AddMatchString(re.compile(b'DsG(600[0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchOutputAttenuation, None)
            self.AddMatchString(re.compile(b'DsG(401[0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchPremixerGain, None)
            self.AddMatchString(re.compile(b'DsM(401[0-4][0-9])\*([01])\r\n'), self.__MatchPremixerMute, None)
            self.AddMatchString(re.compile(b'DsG(501[0-4][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchVirtualReturnGain, None)
            self.AddMatchString(re.compile(b'DsM(501[0-4][0-9])\*([01])\r\n'), self.__MatchVirtualReturnMute, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E([0-9]{2})\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def UpdatePartNumber(self, value, qualifier):

        cmdString = 'n'
        self.__UpdateHelper('PartNumber', cmdString, None, None)

    def __MatchPartNumber(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PartNumber', value, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def SetAutomixerGateSet(self, value, qualifier):

        InputStates = {
            'AT#1'   : '59000',
            'AT#2'   : '59001',
            'AT#3'   : '59002',
            'AT#4'   : '59003',
            'AT#5'   : '59004',
            'AT#6'   : '59005',
            'AT#7'   : '59006',
            'AT#8'   : '59007',
            'AT#9'   : '59008',
            'AT#10'  : '59009',
            'AT#11'  : '59010',
            'AT#12'  : '59011',
            'AT#13'  : '59012',
            'AT#14'  : '59013',
            'AT#15'  : '59014',
            'AT#16'  : '59015',
            'AT#17'  : '59016',
            'AT#18'  : '59017',
            'AT#19'  : '59018',
            'AT#20'  : '59019',
            'AT#21'  : '59020',
            'AT#22' : '59021',
            'AT#23' : '59022',
            'AT#24' : '59023',
            'AT#25' : '59024',
            'AT#26' : '59025',
            'AT#27' : '59026',
            'AT#28' : '59027',
            'AT#29' : '59028',
            'AT#30' : '59029',
            'AT#31' : '59030',
            'AT#32' : '59031',
            'AT#33' : '59032',
            'AT#34' : '59033',
            'AT#35' : '59034',
            'AT#36' : '59035',
            'AT#37' : '59036',
            'AT#38' : '59037',
            'AT#39' : '59038',
            'AT#40' : '59039',
            'AT#41' : '59040',
            'AT#42' : '59041',
            'AT#43' : '59042',
            'AT#44' : '59043',
            'AT#45' : '59044',
            'AT#46' : '59045',
            'AT#47' : '59046',
            'AT#48' : '59047',
        }

        ValueStateValues = {
            'Enable' : 1024,
            'Disable': 0
        }

        newinput = InputStates[qualifier['Input']]
        if value in ValueStateValues and newinput:
            AutomixerGateSetCmdString = 'wj{0}*{1}Au\r'.format(newinput, ValueStateValues[value])
            self.__SetHelper('AutomixerGateSet', AutomixerGateSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerGateSet')

    def __MatchAutomixerGateSet(self, match, tag):

        InputStates = {
            '59000' : 'AT#1',
            '59001' : 'AT#2',
            '59002' : 'AT#3',
            '59003' : 'AT#4',
            '59004' : 'AT#5',
            '59005' : 'AT#6',
            '59006' : 'AT#7',
            '59007' : 'AT#8',
            '59008' : 'AT#9',
            '59009' : 'AT#10',
            '59010' : 'AT#11',
            '59011' : 'AT#12',
            '59012' : 'AT#13' ,
            '59013' : 'AT#14' ,
            '59014' : 'AT#15' ,
            '59015' : 'AT#16' ,
            '59016' : 'AT#17' ,
            '59017' : 'AT#18' ,
            '59018' : 'AT#19' ,
            '59019' : 'AT#20' ,
            '59020' : 'AT#21' ,
            '59021' : 'AT#22',
            '59022' : 'AT#23',
            '59023' : 'AT#24',
            '59024' : 'AT#25',
            '59025' : 'AT#26',
            '59026' : 'AT#27',
            '59027' : 'AT#28',
            '59028' : 'AT#29',
            '59029' : 'AT#30',
            '59030' : 'AT#31',
            '59031' : 'AT#32',
            '59032' : 'AT#33',
            '59033' : 'AT#34',
            '59034' : 'AT#35',
            '59035' : 'AT#36',
            '59036' : 'AT#37',
            '59037' : 'AT#38',
            '59038' : 'AT#39',
            '59039' : 'AT#40',
            '59040' : 'AT#41',
            '59041' : 'AT#42',
            '59042' : 'AT#43',
            '59043' : 'AT#44',
            '59044' : 'AT#45',
            '59045' : 'AT#46',
            '59046' : 'AT#47',
            '59047' : 'AT#48',
        }

        channel = match.group(1).decode()
        qualifier = {'Input': InputStates[channel]}
        value = int(match.group(2))
        if value >= 1024:
            self.WriteStatus('AutomixerGateSet', 'Enable', qualifier)
        else:
            self.WriteStatus('AutomixerGateSet', 'Disable', qualifier)
            self.WriteStatus('AutomixerGateStatus', 'Off', qualifier)
            
    def __MatchAutomixerGateStatus(self, match, tag):

        InputStates = {
            '59000' : 'AT#1',
            '59001' : 'AT#2',
            '59002' : 'AT#3',
            '59003' : 'AT#4',
            '59004' : 'AT#5',
            '59005' : 'AT#6',
            '59006' : 'AT#7',
            '59007' : 'AT#8',
            '59008' : 'AT#9',
            '59009' : 'AT#10',
            '59010' : 'AT#11',
            '59011' : 'AT#12',
            '59012' : 'AT#13' ,
            '59013' : 'AT#14' ,
            '59014' : 'AT#15' ,
            '59015' : 'AT#16' ,
            '59016' : 'AT#17' ,
            '59017' : 'AT#18' ,
            '59018' : 'AT#19' ,
            '59019' : 'AT#20' ,
            '59020' : 'AT#21' ,
            '59021' : 'AT#22',
            '59022' : 'AT#23',
            '59023' : 'AT#24',
            '59024' : 'AT#25',
            '59025' : 'AT#26',
            '59026' : 'AT#27',
            '59027' : 'AT#28',
            '59028' : 'AT#29',
            '59029' : 'AT#30',
            '59030' : 'AT#31',
            '59031' : 'AT#32',
            '59032' : 'AT#33',
            '59033' : 'AT#34',
            '59034' : 'AT#35',
            '59035' : 'AT#36',
            '59036' : 'AT#37',
            '59037' : 'AT#38',
            '59038' : 'AT#39',
            '59039' : 'AT#40',
            '59040' : 'AT#41',
            '59041' : 'AT#42',
            '59042' : 'AT#43',
            '59043' : 'AT#44',
            '59044' : 'AT#45',
            '59045' : 'AT#46',
            '59046' : 'AT#47',
            '59047' : 'AT#48',
        }
        
        channel = match.group(1).decode()
        qualifier = {'Input': InputStates[channel]}
        value = int(match.group(2))
        if value >= 1024:
            self.WriteStatus('AutomixerGateStatus', 'On', qualifier)
        else:
            self.WriteStatus('AutomixerGateStatus', 'Off', qualifier)

    def ConnectToDante(self, value, qualifier):
        if value not in self.DanteDevices:
            if self.VerboseDisabled:
                self.Send('\x1bC{}*1EXPR\r\n'.format(value))

    def CheckEnableRemoteDante(self, dante_device):
        self.ConnectToDante( dante_device, None)

    def __MatchDanteConnect(self, match, tag):
        if match.group(1).decode() not in self.DanteDevices:
            self.DanteDevices.append(match.group(1).decode())

    def SetDanteInputGain(self, value, qualifier):

        dante_name = qualifier['Dante Device']
        channel = int(qualifier['Input'])
        if 1 <= channel <= 4 and self.__CheckValidLevelValue('DanteInputGain', value):
            level = round(value)
            commandString = '{{dante@{0}:wG{1}*{2:05d}AU}}\r\n'.format(dante_name, channel + 39999, level)
            self.__SetHelper('DanteInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDanteInputGain')

    def UpdateDanteInputGain(self, value, qualifier):

        dante_device = qualifier['Dante Device']
        self.CheckEnableRemoteDante(dante_device)
        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = '{{dante@{0}:wG{1}AU}}\r\n'.format(dante_device, channel + 39999)
            self.__UpdateHelper('DanteInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDanteInputGain')

    def __MatchDanteInputGain(self, match, tag):

        dante_device = match.group(1).decode()
        channel = str(int(match.group(2)) - 39999)
        qualifier = {'Input' : channel, 'Dante Device': dante_device}
        value = int(match.group(3))
        self.WriteStatus('DanteInputGain', value, qualifier)

    def SetDanteInputMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        dante_device = qualifier['Dante Device']
        channel = int(qualifier['Input'])
        if value in MuteStateValues and 1 <= channel <= 4:
            commandString = '{{dante@{0}:wM{1}*{2}AU}}\r\n'.format(dante_device, channel + 39999, MuteStateValues[value])
            self.__SetHelper('DanteInputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDanteInputMute')

    def UpdateDanteInputMute(self, value, qualifier):

        dante_device = qualifier['Dante Device']
        self.CheckEnableRemoteDante(dante_device)
        channel = int(qualifier['Input'])
        if 1 <= channel <= 4:
            commandString = '{{dante@{0}:wM{1}AU}}\r\n'.format(dante_device, channel + 39999)
            self.__UpdateHelper('DanteInputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDanteInputMute')

    def __MatchDanteInputMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        dante_device = match.group(1).decode()
        channel = str(int(match.group(2)) - 39999)
        qualifier = {'Input' : channel, 'Dante Device': dante_device}
        value = MuteStateNames[match.group(3).decode()]
        self.WriteStatus('DanteInputMute', value, qualifier)

    def SetDanteOutputAttenuation(self, value, qualifier):

        dante_device = qualifier['Dante Device']
        channel = int(qualifier['Output'])
        if 1 <= channel <= 4 and self.__CheckValidLevelValue('OutputAttenuation', value):
            level=round(value)
            commandString = '{{dante@{0}:wG{1}*{2:05d}AU}}\r\n'.format(dante_device, channel + 59999, level)
            self.__SetHelper('DanteOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDanteOutputAttenuation')

    def UpdateDanteOutputAttenuation(self, value, qualifier):

        dante_device = qualifier['Dante Device']
        self.CheckEnableRemoteDante(dante_device)
        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = '{{dante@{0}:wG{1}AU}}\r\n'.format(dante_device, channel + 59999)
            self.__UpdateHelper('DanteOutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDanteOutputAttenuation')

    def __MatchDanteOutputAttenuation(self, match, tag):

        dante_device = match.group(1).decode()
        channel = str(int(match.group(2)) - 59999)
        qualifier = {'Output' : channel, 'Dante Device': dante_device}
        value = int(match.group(3))
        self.WriteStatus('DanteOutputAttenuation', value, qualifier)

    def SetDanteOutputMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        dante_device = qualifier['Dante Device']
        channel = int(qualifier['Output'])
        if value in MuteStateValues and 1 <= channel <= 4:
            commandString = '{{dante@{0}:wM{1}*{2}AU}}\r\n'.format(dante_device, channel + 59999, MuteStateValues[value])
            self.__SetHelper('DanteOutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDanteOutputMute')

    def UpdateDanteOutputMute(self, value, qualifier):

        dante_device = qualifier['Dante Device']
        self.CheckEnableRemoteDante(dante_device)
        channel = int(qualifier['Output'])
        if 1 <= channel <= 4:
            commandString = '{{dante@{0}:wM{1}AU}}\r\n'.format(dante_device, channel + 59999)
            self.__UpdateHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDanteOutputMute')

    def __MatchDanteOutputMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        dante_device = match.group(1).decode()
        channel = str(int(match.group(2)) - 59999)
        qualifier = {'Output' : channel, 'Dante Device': dante_device}
        value = MuteStateNames[match.group(3).decode()]
        self.WriteStatus('DanteOutputMute', value, qualifier)

    def SetDantePresetRecall(self, value, qualifier):

        dante_device = qualifier['Dante Device']
        self.CheckEnableRemoteDante(dante_device)
        if 0 < int(value) <= 8:
            commandString = '{{dante@{0}:{1}.}}\r\n'.format(dante_device, value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDantePresetRecall')
    def SetDigitalInputGain(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        if 1 <= channel <= 48 and self.__CheckValidLevelValue('DigitalInputGain', value):
            level = round(value * 10)
            DigitalInputGainCmdString = 'wH{0}*{1:05d}AU\r\n'.format(channel + 39999, level)
            self.__SetHelper('DigitalInputGain', DigitalInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalInputGain')

    def UpdateDigitalInputGain(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        if 1 <= channel <= 48:
            DigitalInputGainCmdString = 'wH{0}AU\r\n'.format(channel + 39999)
            self.__UpdateHelper('DigitalInputGain', DigitalInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDigitalInputGain')

    def __MatchDigitalInputGain(self, match, tag):

        channel = str(int(match.group(1)) + 1)
        qualifier = {'Input': 'AT#' + channel}
        value = int(match.group(2)) / 10
        self.WriteStatus('DigitalInputGain', value, qualifier)

    def SetGroupMicLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupMicLineInputGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
            self.__SetHelper('GroupMicLineInputGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupMicLineInputGain')

    def UpdateGroupMicLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
            self.__UpdateHelper('GroupMicLineInputGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupMicLineInputGain')

    def SetGroupBassInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupBassInputFilter', value):
            level = round(value * 10)
            GroupBassInputFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupBassInputFilter'
            self.__SetHelper('GroupBassInputFilter', GroupBassInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBassInputFilter')

    def UpdateGroupBassInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            GroupBassInputFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupBassInputFilter'
            self.__UpdateHelper('GroupBassInputFilter', GroupBassInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupBassInputFilter')

    def SetGroupBassVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupBassVirtualReturnFilter', value):
            level = round(value * 10)
            GroupBassVirtualReturnFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupBassVirtualReturnFilter'
            self.__SetHelper('GroupBassVirtualReturnFilter', GroupBassVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBassVirtualReturnFilter')

    def UpdateGroupBassVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            GroupBassVirtualReturnFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupBassVirtualReturnFilter'
            self.__UpdateHelper('GroupBassVirtualReturnFilter', GroupBassVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupBassVirtualReturnFilter')

    def UpdateGroupMeterLevel(self, value, qualifier):

        if 1 <= int(qualifier['Group']) <= 64:
            if qualifier['Group'] not in self.groupMeterLevelDict:
                GroupMeterLevelCmdString = 'wO{}GRPM\r'.format(qualifier['Group'])
                self.__UpdateHelper('GroupMeterLevel', GroupMeterLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMeterLevel')

    def __MatchGroupMeterMember(self, match, tag):

        self.groupMeterLevelDict[match.group(1).decode()] = match.group(2).decode()[1:].split('*')

    def __MatchGroupMeterLevel(self, match, tag):

        group = match.group(1).decode()
        if group in self.groupMeterLevelDict:
            qualifier = {'Group' : group}
            res = match.group(2).decode()[1:].split('*')
            for index, items in enumerate(res):
                value = int('-' + items) / 10
                if value < -150:
                    value = -150.0
                channel = self.groupMeterLevelDict[group][index]
                qualifier['Channel'] = self.groupOID[channel]
                if -150 <= value <= 0:
                    self.WriteStatus('GroupMeterLevel', value, {'Group': group, 'Channel': self.groupOID[channel]})

    def SetGroupMeterMode(self, value, qualifier):

        ValueStateValues = {
            'Enable'  : '1',
            'Disable' : '0'
        }

        if 1 <= int(qualifier['Group']) <= 64 and value in ValueStateValues:
            GroupMeterModeCmdString =  'wD{0}*{1}GRPM\r'.format(qualifier['Group'], ValueStateValues[value])
            self.__SetHelper('GroupMeterMode', GroupMeterModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMeterMode')
    def SetGroupMeterResponseRate(self, value, qualifier):

        if 1 <= int(value) <= 10:
            GroupMeterResponseRateCmdString = 'wR{}GRPU\r'.format(value)
            self.__SetHelper('GroupMeterResponseRate', GroupMeterResponseRateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMeterResponseRate')

    def UpdateGroupMeterResponseRate(self, value, qualifier):

        GroupMeterResponseRateCmdString = 'wRGRPU\r'
        self.__UpdateHelper('GroupMeterResponseRate', GroupMeterResponseRateCmdString, value, qualifier)

    def __MatchGroupMeterResponseRate(self, match, tag):

        value = match.group(1).decode()
        if 1 <= int(value) <= 10:
            self.WriteStatus('GroupMeterResponseRate', value, None)

    def SetGroupMeterSelect(self, value, qualifier):

        if value == 'Off' or 1 <= int(value) <= 64:
            value = '0' if value == 'Off' else value
            GroupMeterSelectCmdString = 'wG{}GRPU\r'.format(value.rjust(2, '0'))
            self.__SetHelper('GroupMeterSelect', GroupMeterSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMeterSelect')

    def UpdateGroupMeterSelect(self, value, qualifier):

        GroupMeterSelectCmdString = 'wGGRPU\r'
        self.__UpdateHelper('GroupMeterSelect', GroupMeterSelectCmdString, value, qualifier)

    def __MatchGroupMeterSelect(self, match, tag):

        value = match.group(1).decode()
        if 0 <= int(value) <= 64:
            value = 'Off' if value == '0' else value
            self.WriteStatus('GroupMeterSelect', value, None)

    def SetGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupMixpointGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__SetHelper('GroupMixpointGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMixpointGain'
            self.__UpdateHelper('GroupMixpointGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        GroupMuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        group = qualifier['Group']
        if value in GroupMuteStateValues and 1 <= int(group) <= 64:
            commandString = 'wd{0}*{1}grpm\r\n'.format(group, GroupMuteStateValues[value])
            self.GroupFunction[group] = 'GroupMute'
            self.__SetHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupMute'
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupOutputAttenuation', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)

    def SetGroupPostMixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupPostMixerTrim', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupPostMixerTrim'
            self.__SetHelper('GroupPostMixerTrim', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupPostMixerTrim')

    def UpdateGroupPostMixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupPostMixerTrim'
            self.__UpdateHelper('GroupPostMixerTrim', commandString, value, qualifier)

    def SetGroupPreMixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupPreMixerGain', value):
            level = round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupPreMixerGain'
            self.__SetHelper('GroupPreMixerGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupPreMixerGain')

    def UpdateGroupPreMixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupPreMixerGain'
            self.__UpdateHelper('GroupPreMixerGain', commandString, value, qualifier)

    def SetGroupTrebleInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupTrebleInputFilter', value):
            level = round(value * 10)
            GroupTrebleInputFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupTrebleInputFilter'
            self.__SetHelper('GroupTrebleInputFilter', GroupTrebleInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTrebleInputFilter')

    def UpdateGroupTrebleInputFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            GroupTrebleInputFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupTrebleInputFilter'
            self.__UpdateHelper('GroupTrebleInputFilter', GroupTrebleInputFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupTrebleInputFilter')

    def SetGroupTrebleVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupTrebleVirtualReturnFilter', value):
            level = round(value * 10)
            GroupTrebleVirtualReturnFilterCmdString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupTrebleVirtualReturnFilter'
            self.__SetHelper('GroupTrebleVirtualReturnFilter', GroupTrebleVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTrebleVirtualReturnFilter')

    def UpdateGroupTrebleVirtualReturnFilter(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            GroupTrebleVirtualReturnFilterCmdString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupTrebleVirtualReturnFilter'
            self.__UpdateHelper('GroupTrebleVirtualReturnFilter', GroupTrebleVirtualReturnFilterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupTrebleVirtualReturnFilter')

    def SetGroupVirtualReturnGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64 and self.__CheckValidLevelValue('GroupVirtualReturnGain', value):
            level=round(value*10)
            commandString = 'wd{0}*{1:+06d}grpm\r\n'.format(group, level)
            self.GroupFunction[group] = 'GroupVirtualReturnGain'
            self.__SetHelper('GroupVirtualReturnGain', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetGroupVirtualReturnGain')

    def UpdateGroupVirtualReturnGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 64:
            commandString = 'wd{0}grpm\r\n'.format(group)
            self.GroupFunction[group] = 'GroupVirtualReturnGain'
            self.__UpdateHelper('GroupVirtualReturnGain', commandString, value, qualifier)

    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                        '1' : 'On',
                        '0' : 'Off'
                }
                qualifier = {'Group' : group}
                value = match.group(2).decode()[-1]
                self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
            elif command in ['GroupPreMixerGain', 'GroupOutputAttenuation',
                             'GroupMixpointGain', 'GroupPostMixerTrim',
                             'GroupVirtualReturnGain', 'GroupMicLineInputGain',
                             'GroupBassInputFilter', 'GroupBassVirtualReturnFilter',
                             'GroupTrebleInputFilter', 'GroupTrebleVirtualReturnFilter']:
                qualifier = {'Group' : group}
                value = int(match.group(2))/10
                self.WriteStatus(command, value, qualifier)

    def SetInputFilterBoostCut(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 48 and 1 <= int(qualifier['Filter']) <= 5 and -24.0 <= value <= 24.0:
            level = round(value*10)
            InputFilterBoostCutCmdString = 'wG41{0}{1:02d}*{2}AU\r\n'.format(int(qualifier['Filter']) - 1, int(qualifier['Input']) - 1, level)
            self.__SetHelper('InputFilterBoostCut', InputFilterBoostCutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputFilterBoostCut')

    def UpdateInputFilterBoostCut(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 48 and 1 <= int(qualifier['Filter']) <= 5:
            InputFilterBoostCutCmdString = 'wG41{0}{1:02d}AU\r\n'.format(int(qualifier['Filter']) - 1, int(qualifier['Input']) - 1)
            self.__UpdateHelper('InputFilterBoostCut', InputFilterBoostCutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputFilterBoostCut')

    def __MatchInputFilterBoostCut(self, match, tag):

        qualifier = {
            'Input' : str(int(match.group(2).decode()) + 1),
            'Filter' : str(int(match.group(1).decode()) + 1)
        }

        value = int(match.group(3)) / 10
        if -24.0 <= value <= 24.0:
            self.WriteStatus('InputFilterBoostCut', value, qualifier)

    def SetInputMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        channel = int(qualifier['Input'][3:])
        if value in MuteStateValues and 1 <= channel <= 48:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 39999, MuteStateValues[value])
            self.__SetHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        if 1 <= channel <= 48:
            commandString = 'wM{0}AU\r\n'.format(channel + 39999)
            self.__UpdateHelper('InputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = str(int(match.group(1)) - 39999)
        qualifier = {'Input' : 'AT#' + channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def UpdateInputSignalLevelMonitor(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        threshold = qualifier['Monitoring Threshold']
        if 1 <= channel <= 48 and -150 <= threshold <= 0:
            self.inputSignalLevelMonitorThreshold[channel] = threshold
            thresholdStr = str(abs(threshold) * 10)
            InputSignalLevelMonitorCmdString = 'wJ{0}*{1}AU\r'.format(channel + 39999, thresholdStr.zfill(4))
            self.__SetHelper('InputSignalLevelMonitor', InputSignalLevelMonitorCmdString, value, qualifier)

    def __MatchInputSignalLevelMonitor(self, match, tag):

        channel = int(match.group(1)) - 39999
        qualifier = {
            'Input' : 'AT#' + str(channel),
            'Monitoring Threshold' : self.inputSignalLevelMonitorThreshold[channel]
        }

        if tag == 'Disabled':
            self.WriteStatus('InputSignalLevelMonitor', 'Off', qualifier)
        else:
            thresholdStr = abs(self.inputSignalLevelMonitorThreshold[channel]) * 10
            if int(match.group(2)) > int(thresholdStr):
                self.WriteStatus('InputSignalLevelMonitor', 'Off', qualifier)
            else:
                self.WriteStatus('InputSignalLevelMonitor', 'On', qualifier)

    def SetInputSource(self, value, qualifier):

        ValueStateValues = {
            'AT#1'  : '1',
            'AT#2'  : '2',
            'AT#3'  : '3',
            'AT#4'  : '4',
            'AT#5'  : '5',
            'AT#6'  : '6',
            'AT#7'  : '7',
            'AT#8'  : '8',
            'AT#9'  : '9',
            'AT#10' : '10',
            'AT#11' : '11',
            'AT#12' : '12',
            'AT#13' : '13',
            'AT#14' : '14',
            'AT#15' : '15',
            'AT#16' : '16',
            'AT#17' : '17',
            'AT#18' : '18',
            'AT#19' : '19',
            'AT#20' : '20',
            'AT#21' : '21',
            'AT#22' : '22',
            'AT#23' : '23',
            'AT#24' : '24',
            'AT#25' : '25',
            'AT#26' : '26',
            'AT#27' : '27',
            'AT#28' : '28',
            'AT#29' : '29',
            'AT#30' : '30',
            'AT#31' : '31',
            'AT#32' : '32',
            'AT#33' : '33',
            'AT#34' : '34',
            'AT#35' : '35',
            'AT#36' : '36',
            'AT#37' : '37',
            'AT#38' : '38',
            'AT#39' : '39',
            'AT#40' : '40',
            'AT#41' : '41',
            'AT#42' : '42',
            'AT#43' : '43',
            'AT#44' : '44',
            'AT#45' : '45',
            'AT#46' : '46',
            'AT#47' : '47',
            'AT#48' : '48',
            'EXP1'  : '49',
            'EXP2'  : '50',
            'EXP3'  : '51',
            'EXP4'  : '52',
            'EXP5'  : '53',
            'EXP6'  : '54',
            'EXP7'  : '55',
            'EXP8'  : '56',
            'EXP9'  : '57',
            'EXP10'  : '58',
            'EXP11'  : '59',
            'EXP12'  : '60',
            'EXP13'  : '61',
            'EXP14'  : '62',
            'EXP15'  : '63',
            'EXP16'  : '64',
        }

        if value in ValueStateValues and 1 <= int(qualifier['Input'][3:]) <= 48:
            InputSourceCmdString = 'wD{0}*{1}AU\r'.format(int(qualifier['Input'][3:]) + 39999, ValueStateValues[value])
            self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSource')

    def UpdateInputSource(self, value, qualifier):

        if 1 <= int(qualifier['Input'][3:]) <= 48:
            InputSourceCmdString = 'wD{}AU\r'.format(int(qualifier['Input'][3:]) + 39999)
            self.__UpdateHelper('InputSource', InputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSource')

    def __MatchInputSource(self, match, tag):

        ValueStateValues = {
            '0'  : 'Analog',
            '1'  : 'AT#1',
            '2'  : 'AT#2',
            '3'  : 'AT#3',
            '4'  : 'AT#4',
            '5'  : 'AT#5',
            '6'  : 'AT#6',
            '7'  : 'AT#7',
            '8'  : 'AT#8',
            '9'  : 'AT#9',
            '10' : 'AT#10',
            '11' : 'AT#11',
            '12' : 'AT#12',
            '13' : 'AT#13',
            '14' : 'AT#14',
            '15' : 'AT#15',
            '16' : 'AT#16',
            '17' : 'AT#17',
            '18' : 'AT#18',
            '19' : 'AT#19',
            '20' : 'AT#20',
            '21' : 'AT#21',
            '22' : 'AT#22',
            '23' : 'AT#23',
            '24' : 'AT#24',
            '25' : 'AT#25',
            '26' : 'AT#26',
            '27' : 'AT#27',
            '28' : 'AT#28',
            '29' : 'AT#29',
            '30' : 'AT#30',
            '31' : 'AT#31',
            '32' : 'AT#32',
            '33' : 'AT#33',
            '34' : 'AT#34',
            '35' : 'AT#35',
            '36' : 'AT#36',
            '37' : 'AT#37',
            '38' : 'AT#38',
            '39' : 'AT#39',
            '40' : 'AT#40',
            '41' : 'AT#41',
            '42' : 'AT#42',
            '43' : 'AT#43',
            '44' : 'AT#44',
            '45' : 'AT#45',
            '46' : 'AT#46',
            '47' : 'AT#47',
            '48' : 'AT#48',
            '49' : 'EXP1',
            '50' : 'EXP2',
            '51' : 'EXP3',
            '52' : 'EXP4',
            '53' : 'EXP5',
            '54' : 'EXP6',
            '55' : 'EXP7',
            '56' : 'EXP8',
            '57' : 'EXP9',
            '58' : 'EXP10',
            '59' : 'EXP11',
            '60' : 'EXP12',
            '61' : 'EXP13',
            '62' : 'EXP14',
            '63' : 'EXP15',
            '64' : 'EXP16',
        }

        qualifier = {'Input' : 'AT#' + str(int(match.group(1)) - 39999)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSource', value, qualifier)

    def SetMacro(self, value, qualifier):

        ValueStateValues = {
            'Run': 'R',
            'Kill': 'K'
        }

        if value in ValueStateValues and 0 < int(qualifier['Macro']) < 65:
            MacroCmdString = '\x1b{0}{1}MCRO\r\n'.format(ValueStateValues[value], qualifier['Macro'])
            self.__SetHelper('Macro', MacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def SetMixpointGain(self, value, qualifier):

        inputQual = qualifier['Input']
        outputQual = qualifier['Output']
        if inputQual in self.MixpointInputStateValues and outputQual in self.MixpointOutputStateValues and self.__CheckValidLevelValue('MixpointGain', value):
            inputValue = self.MixpointInputStateValues[inputQual]
            outputValue = self.MixpointOutputStateValues[outputQual]
            level = round(value*10)
            commandString = 'wG{0}{1}*{2:05d}AU\r\n'.format(inputValue, outputValue, level)
            self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        inputQual = qualifier['Input']
        outputQual = qualifier['Output']
        if inputQual in self.MixpointInputStateValues and outputQual in self.MixpointOutputStateValues:
            inputValue = self.MixpointInputStateValues[inputQual]
            outputValue = self.MixpointOutputStateValues[outputQual]
            commandString = 'wG{0}{1}AU\r\n'.format(inputValue, outputValue)
            self.__UpdateHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixpointGain')

    def __MatchMixpointGain(self, match, tag):

        Input = self.MixpointInputStateNames[match.group(1).decode()]
        Output = self.MixpointOutputStateNames[match.group(2).decode()]
        value = int(match.group(3))/10
        qualifier = {'Input': Input, 'Output': Output}
        self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        inputQual = qualifier['Input']
        outputQual = qualifier['Output']
        if value in MuteStateValues and inputQual in self.MixpointInputStateValues and outputQual in self.MixpointOutputStateValues:
            inputValue = self.MixpointInputStateValues[inputQual]
            outputValue = self.MixpointOutputStateValues[outputQual]
            commandString = 'wM{0}{1}*{2}AU\r\n'.format(inputValue, outputValue, MuteStateValues[value])
            self.__SetHelper('MixpointMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointMute')

    def UpdateMixpointMute(self, value, qualifier):

        inputQual = qualifier['Input']
        outputQual = qualifier['Output']
        if inputQual in self.MixpointInputStateValues and outputQual in self.MixpointOutputStateValues:
            inputValue = self.MixpointInputStateValues[inputQual]
            outputValue = self.MixpointOutputStateValues[outputQual]
            commandString = 'wM{0}{1}AU\r\n'.format(inputValue, outputValue)
            self.__UpdateHelper('MixpointMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixpointMute')

    def __MatchMixpointMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        Input = self.MixpointInputStateNames[match.group(1).decode()]
        Output = self.MixpointOutputStateNames[match.group(2).decode()]
        value = MuteStateNames[match.group(3).decode()]
        qualifier = {'Input' : Input, 'Output' : Output}
        self.WriteStatus('MixpointMute', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }
        channel = int(qualifier['Output'][7:])
        if value in MuteStateValues and 1 <= channel <= 48:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 59999, MuteStateValues[value])
            self.__SetHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        channel = int(qualifier['Output'][7:])
        if 1 <= channel <= 48:
            commandString = 'wM{0}AU\r\n'.format(channel + 59999)
            self.__UpdateHelper('OutputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output' : 'AT Out#' + channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetOutputPostmixerTrim(self, value, qualifier):

        channel = qualifier['Output'][7:]
        if 0 < int(channel) < 49 and self.__CheckValidLevelValue('OutputPostmixerTrim', value):
            level=round(value*10)
            ChannelValue = int(channel) + 60099
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('OutputPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputPostmixerTrim')

    def UpdateOutputPostmixerTrim(self, value, qualifier):

        channel = qualifier['Output'][7:]
        if 0 < int(channel) < 49:
            ChannelValue = int(channel) + 60099
            commandString = 'wG{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('OutputPostmixerTrim', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputPostmixerTrim')

    def __MatchOutputPostmixerTrim(self, match, tag):

        channel = str(int(match.group(1)) - 60099)
        qualifier = {'Output' : 'AT Out#' + channel}
        value = int(match.group(2))/10
        self.WriteStatus('OutputPostmixerTrim', value, qualifier)

    def SetOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'][7:])
        if 1 <= channel <= 48 and self.__CheckValidLevelValue('OutputAttenuation', value):
            level=round(value*10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 59999, level)
            self.__SetHelper('OutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuation')

    def UpdateOutputAttenuation(self, value, qualifier):

        channel = int(qualifier['Output'][7:])
        if 1 <= channel <= 48:
            commandString = 'wG{0}AU\r\n'.format(channel + 59999)
            self.__UpdateHelper('OutputAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAttenuation')

    def __MatchOutputAttenuation(self, match, tag):

        channel = str(int(match.group(1)) - 59999)
        qualifier = {'Output' : 'AT Out#' + channel}
        value = int(match.group(2))/10
        self.WriteStatus('OutputAttenuation', value, qualifier)

    def SetPremixerGain(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        if 1 <= channel <= 48 and self.__CheckValidLevelValue('PremixerGain', value):
            level=round(value*10)
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(channel + 40099, level)
            self.__SetHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerGain')

    def UpdatePremixerGain(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        if 1 <= channel <= 48:
            commandString = 'wG{0}AU\r\n'.format(channel + 40099)
            self.__UpdateHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerGain')

    def __MatchPremixerGain(self, match, tag):

        channel = str(int(match.group(1)) - 40099)
        qualifier = {'Input' : 'AT#' + channel}
        value = int(match.group(2))/10
        self.WriteStatus('PremixerGain', value, qualifier)

    def SetPremixerMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        channel = int(qualifier['Input'][3:])
        if value in MuteStateValues and 1 <= channel <= 48:
            commandString = 'wM{0}*{1}AU\r\n'.format(channel + 40099, MuteStateValues[value])
            self.__SetHelper('PremixerMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerMute')

    def UpdatePremixerMute(self, value, qualifier):

        channel = int(qualifier['Input'][3:])
        if 1 <= channel <= 48:
            commandString = 'wM{0}AU\r\n'.format(channel + 40099)
            self.__UpdateHelper('PremixerMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerMute')

    def __MatchPremixerMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = str(int(match.group(1)) - 40099)
        qualifier = {'Input' : 'AT#' + channel}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('PremixerMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            commandString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 64:
            commandString1 = '\x1b[1*AU\r'
            commandString2 = '{0}*0*0*0,'.format(value)
            self.__SetHelper('PresetSave', commandString1, value, qualifier, 3)
            self.__SetHelper('PresetSave', commandString2, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVirtualReturnGain(self, value, qualifier):

        channel = qualifier['Input'][9:]
        if channel in self.VirtualChannels and self.__CheckValidLevelValue('VirtualReturnGain', value):
            level=round(value*10)
            ChannelValue = ord(channel) + 50035
            commandString = 'wG{0}*{1:05d}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnGain')

    def UpdateVirtualReturnGain(self, value, qualifier):

        channel = qualifier['Input'][9:]
        if channel in self.VirtualChannels:
            ChannelValue = ord(channel) + 50035
            commandString = 'wG{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualReturnGain')

    def __MatchVirtualReturnGain(self, match, tag):

        channel = chr(int(match.group(1)) - 50035)
        qualifier = {'Input' : 'VrtlRet #' + channel}
        value = int(match.group(2))/10
        self.WriteStatus('VirtualReturnGain', value, qualifier)

    def SetVirtualReturnMute(self, value, qualifier):

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        channel = qualifier['Input'][9:]
        if value in MuteStateValues and channel in self.VirtualChannels:
            ChannelValue = ord(channel) + 50035
            commandString = 'wM{0}*{1}AU\r\n'.format(ChannelValue, MuteStateValues[value])
            self.__SetHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnMute')

    def UpdateVirtualReturnMute(self, value, qualifier):

        channel = qualifier['Input'][9:]
        if channel in self.VirtualChannels:
            ChannelValue = ord(channel) + 50035
            commandString = 'wM{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualReturnMute')

    def __MatchVirtualReturnMute(self, match, tag):

        MuteStateNames = {
            '1' : 'On',
            '0' : 'Off'
        }

        channel = chr(int(match.group(1)) - 50035)
        qualifier = {'Input' : 'VrtlRet #' + channel}
        value =  MuteStateNames[match.group(2).decode()]
        self.WriteStatus('VirtualReturnMute', value, qualifier)

    def __CheckValidLevelValue(self, command, value):
        
        return self.LevelTypes[command]['Min'] <= value <= self.LevelTypes[command]['Max']

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        DeviceErrorCodes = {
            '10': 'Unrecognized command',
            '12': 'Invalid port number',
            '13': 'Invalid parameter (number is out of range)',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System/command timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device is not present',
            '26': 'Maximum connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '31': 'Attempt to break port passthrough when not set',
        }
        self.Error([DeviceErrorCodes.get(match.group(1).decode(), 'Unrecognized error code: {0}'.format(match.group(0).decode()))])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.EchoDisabled = True
        self.DanteDevices = []
        self.groupMeterLevelDict = {}

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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