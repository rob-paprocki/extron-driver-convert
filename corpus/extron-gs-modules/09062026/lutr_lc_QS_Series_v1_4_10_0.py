from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
import datetime

class DeviceClass:
    def __init__(self, Model):

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
        self.deviceUsername = 'nwk'
        self.devicePassword = 'nwk'
        self.Models = {
            'QSNE-2DAL-D': self.lutr_13_48_DAL,
            'QSN-2ECO-S': self.lutr_13_48_ECO,
            'Grafik Eye QS': self.lutr_13_48_GE,
            'HomeWorks QS System': self.lutr_13_48_HW,
            'myRoom plus': self.lutr_13_48_myRoom,
            'Quantum System': self.lutr_13_48_QS,
            'QSE-CI-NWK-E': self.lutr_13_48_QSE,
            'QSN-4S16-S': self.lutr_13_48_QSN4,
            'QSNE-4T10-D': self.lutr_13_48_QSN4,
            'QSN-4T16-S': self.lutr_13_48_QSN4,
            'QSNE-4S10-D': self.lutr_13_48_QSN4,
            'RadioRA 2': self.lutr_13_48_RA,
            'seeTouch QS': self.lutr_13_48_seeTouch,
            'Sivoia QS': self.lutr_13_48_SQ,
        }

        # Check if Model belongs to a subclass
        if len(Model) > 0:
            if Model not in self.Models:
                self.Error(['Model mismatch'])
            else:
                self.Models[Model]()

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AreaLevel': {'Parameters':['Integration ID', 'Fade Time', 'Delay Time'], 'Status': {}},
            'AreaScene': {'Parameters':['Integration ID'], 'Status': {}},
            'Button': {'Parameters':['Integration ID', 'Button'], 'Status': {}},
            'ContactClosureInput': {'Parameters':['Integration ID', 'Input'], 'Status': {}},
            'ContactClosureOutput': {'Parameters':['Integration ID', 'Output'], 'Status': {}},
            'DaylightMode': {'Parameters':['Integration ID'], 'Status': {}},
            'DeviceButton': {'Parameters':['Integration ID', 'Component Number'], 'Status': {}},
            'EcoSystemBallastOccupancySensor': {'Parameters':['Integration ID', 'Sensor'], 'Status': {}},
            'GrafikEyeScene': {'Parameters':['Integration ID'], 'Status': {}},
            'GrafikEyeShadeColumn': {'Parameters':['Integration ID', 'Column'], 'Status': {}},
            'GrafikEyeShadeColumnStatus': {'Parameters':['Integration ID','Column'], 'Status': {}},
            'GrafikEyeZoneLightLevel': {'Parameters':['Integration ID', 'Zone'], 'Status': {}},
            'GrafikEyeZoneLightRampLevel': {'Parameters':['Integration ID', 'Zone', 'Fade Time', 'Delay Time'], 'Status': {}},
            'HVACOperatingMode': {'Parameters':['Integration ID'], 'Status': {}},
            'IPAddress': { 'Status': {}},
            'LEDState': {'Parameters':['Integration ID', 'Component Number'], 'Status': {}},
            'LiftControl': {'Parameters':['Integration ID'], 'Status': {}},
            'LocalContactClosureInput': {'Parameters':['Integration ID'], 'Status': {}},
            'MasterLevelStep': {'Parameters':['Integration ID', 'Zone'], 'Status': {}},
            'OccupancyGroup': {'Parameters':['Integration ID'], 'Status': {}},
            'OccupancySensor': {'Parameters':['Integration ID', 'Number'], 'Status': {}},
            'OutputLevel': {'Parameters':['Integration ID'], 'Status': {}},
            'OutputLevelStep': {'Parameters':['Integration ID'], 'Status': {}},
            'QSEScene': {'Parameters':['Integration ID', 'Component Number'], 'Status': {}},
            'Scene': {'Parameters':['Integration ID', 'Area'], 'Status': {}},
            'ShadeGroupLevel': {'Parameters':['Integration ID', 'Delay Time'], 'Status': {}},
            'ShadeGroupLevelStatus': {'Parameters':['Integration ID'], 'Status': {}},
            'ShadeGroupPreset': {'Parameters':['Integration ID'], 'Status': {}},
            'ShadePosition': {'Parameters':['Integration ID'], 'Status': {}},
            'TiltControl': {'Parameters':['Integration ID'], 'Status': {}},
            'WirelessOccupancySensor': {'Parameters':['Integration ID', 'Sensor'], 'Status': {}},
            'ZoneControl': {'Parameters':['Integration ID'], 'Status': {}},
            'ZoneLevel': {'Parameters':['Integration ID'], 'Status': {}},            
            'ZoneLightLevel': {'Parameters':['Integration ID', 'Zone', 'Fade Time', 'Delay Time'], 'Status': {}},
            'ZoneLightLevelStatus': {'Parameters':['Integration ID', 'Zone'], 'Status': {}},
        }
        
        self.Authenticated = False

        if self.Unidirectional == 'False':
            
            if self.model in ['QSE', 'QS']:
                self.AddMatchString(re.compile(b'~AREA,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),6,([0-9]|[1-2][0-9]|3[0-2])\r\n'), self.__MatchAreaScene, None)
                self.AddMatchString(re.compile(b'~AREA,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),7,(1|2)\r\n'), self.__MatchDaylightMode, None)
                
            if self.model in ['GE', 'QSE']:
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),([1-5]),35,(3|4)\r\n'), self.__MatchContactClosureInput, None)
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),(1[1-5]),14,(0|100)\r\n'), self.__MatchContactClosureOutput, 'Polled')
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),(1[1-5]),(3|4)\r\n'), self.__MatchContactClosureOutput, 'Unsolicited')
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),([12][12789][0-59]),9,([0-3])\r\n'), self.__MatchGrafikEyeShadeColumnStatus, None)
            
            if self.model in ['GE', 'HW']:           
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),(7[0-9]{2}),(3|4)\r\n'), self.__MatchEcoSystemBallastOccupancySensor, None)
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),(5[0-9]{2}),(3|4)\r\n'), self.__MatchWirelessOccupancySensor, None)
                
            if self.model in ['GE', 'HW', 'QSE']:               
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),141,7,([0-9]|1[0-6])\r\n'), self.__MatchGrafikEyeScene, None)
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),([1-9]|1[0-9]|2[0-4]),14,([0-9]{1,3}\.[0-9]{1,3}|[0-9]{1,3})\r\n'), self.__MatchGrafikEyeZoneLightLevel, None)
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-fA-F0-9]{8}),163,(3|4)\r\n'), self.__MatchLocalContactClosureInput, None) 
                
            if self.model in ['HW', 'QS', 'RA']:             
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),(\d+),9,(1|0)\r\n'), self.__MatchLEDState, None)
                
            if self.model in ['HW', 'myRoom', 'RA']: 
                self.AddMatchString(re.compile(b'~HVAC,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),3,([1-8])'), self.__MatchHVACOperatingMode, None) # No '\r\n' based on customer feedback
                
            if self.model in ['DAL', 'ECO', 'HW', 'myRoom', 'QSE', 'QSN4', 'QS', 'SQ']:
                self.AddMatchString(re.compile(b'~OUTPUT,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),1,([0-9]{1,3}\.[0-9]{1,3}|[0-9]{1,3})\r\n'), self.__MatchOutputLevel, None) 
                
            if self.model in ['QSE']: 
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),([5-8]|1[0-3]),7,([0-9]|1[0-6])\r\n'), self.__MatchQSEScene, None)
            
            if self.model in ['DAL', 'ECO', 'QSN4']:
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),(4[0-2][0-9]|43[0-2]|1[0-3]|12[0-9][0-9]|1300),7,([0-9]|[1-2][0-9]|3[0-2])\r\n'), self.__MatchScene, None)
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),(\d+),14,([0-9]{1,3}\.[0-9]{1,3}|[0-9]{1,3})\r\n'), self.__MatchZoneLightLevelStatus, None)
            
            if self.model in ['myRoom', 'QSE', 'QS']:
                self.AddMatchString(re.compile(b'~SHADEGRP,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),1,([0-9]{1,3}\.[0-9]{1,3}|[0-9]{1,3})\r\n'), self.__MatchShadeGroupLevelStatus, None)
                self.AddMatchString(re.compile(b'~SHADEGRP,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),6,([1-9]|[1-2][0-9]|3[0-2])\r\n'), self.__MatchShadeGroupPreset, None)
            
            if self.model in ['SQ']:
                self.AddMatchString(re.compile(b'~DEVICE,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),0,14,([0-9]{1,3}\.[0-9]{1,3}|[0-9]{1,3})\r\n'), self.__MatchShadePosition, None)

            if self.model in ['RA']:
                self.AddMatchString(re.compile(b'~GROUP,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),3,(3|4|255)\r\n'), self.__MatchOccupancyGroup, None)
                self.AddMatchString(re.compile(b'~OUTPUT,([0-9a-zA-Z \-\.]+|0x[a-zA-Z0-9]{8}),1,([\d]{1,3}\.[\d]{2}|[0-9]{1,3})\r\n'), self.__MatchZoneLevel, None)
                
            self.AddMatchString(re.compile(b'~ETHERNET,0,([0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}\.[0-9]{1,3})\r\n'), self.__MatchIPAddress, None)    
            self.AddMatchString(re.compile(b'~ERROR,([1-6])'), self.__MatchError, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'Login:', re.I), self.__MatchUsername, None)
                self.AddMatchString(re.compile(b'Password:', re.I), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Passphrase:', re.I), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'login incorrect'), self.__MatchPasswordFailure, None)
                self.AddMatchString(re.compile(b'connection established'), self.__MatchLoginSuccessful, None)
            else:
                self.Authenticated = True

    def SetUsername(self, value, qualifier):

        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, qualifier):

        self.SetUsername( None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, qualifier):

        self.SetPassword( None, None)
        
    def __MatchPasswordFailure(self, match, tag):

        self.Authenticated = False
        self.Error(['Login Credentials are wrong. Please enter correct Password.'])
    
    def __MatchLoginSuccessful(self, match, tag):

        self.Authenticated = True

    def __TimeConvert(self, value):    
        
        if 0 <= value < 60:
            return str(value)  # SS
        elif 60 <= value < 3600:
            return str(datetime.timedelta(seconds=value))[2:]  # MM:SS
        elif 3600 <= value <= 14400:
            return str(datetime.timedelta(seconds=value))  # HH:MM:SS
        else:
            return None
        
    def SetAreaLevel(self, value, qualifier):
        
        fadeTime = self.__TimeConvert(qualifier['Fade Time'])
        delayTime = self.__TimeConvert(qualifier['Delay Time'])
        
        if 0 <= value <= 100 and qualifier['Integration ID'] and fadeTime and delayTime:
            self.__SetHelper('AreaLevel', '#AREA,{},1,{},{},{}\r\n'.format(qualifier['Integration ID'], value, fadeTime, delayTime), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAreaLevel')

    def SetAreaScene(self, value, qualifier):
        
        scene = 0 if value == 'Off' else int(value)
        if 0 <= scene <= 32 and qualifier['Integration ID']:
            self.__SetHelper('AreaScene', '#AREA,{},6,{}\r\n'.format(qualifier['Integration ID'], scene), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAreaScene')

    def UpdateAreaScene(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('AreaScene', '?AREA,{},6\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAreaScene')

    def __MatchAreaScene(self, match, tag):
        
        value = 'Off' if match.group(2).decode() == '0' else match.group(2).decode()
        self.WriteStatus('AreaScene', value, {'Integration ID': match.group(1).decode()})

    def SetButton(self, value, qualifier):

        ValueStateValues = {
            'Press'  : '3', 
            'Release': '4'
        }
        
        if value in ValueStateValues and qualifier['Integration ID'] and 1 <= qualifier['Button'] <= 100:
            self.__SetHelper('Button', '#DEVICE,{},{},{}\r\n'.format(qualifier['Integration ID'], qualifier['Button'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetButton')

    def UpdateButton(self, value, qualifier):
        
        statusUpdate = self.Commands['Button']['Status']
        if qualifier['Integration ID'] and 1 <= qualifier['Button'] <= 100:
            if qualifier['Integration ID'] not in statusUpdate and qualifier['Button'] not in statusUpdate:
                self.AddMatchString(re.compile('~DEVICE,({}),({}),([34])\r\n'.format(qualifier['Integration ID'], qualifier['Button']).encode()), self.__MatchButton, None)
        else:
            self.Discard('Invalid Command for UpdateButton')

    def __MatchButton(self, match, tag):

        ValueStateValues = {
            '3': 'Press',
            '4': 'Release'
        }

        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('Button', value, {'Integration ID': match.group(1).decode(), 'Button': int(match.group(2).decode())})
        except KeyError:
            self.Error(['Button: Invalid/unexpected response.'])
            
    def UpdateContactClosureInput(self, value, qualifier):

        
        if qualifier['Integration ID'] and 1 <= int(qualifier['Input']) <= 5:
            self.__UpdateHelper('ContactClosureInput', '?DEVICE,{},{},35\r\n'.format(qualifier['Integration ID'], qualifier['Input']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateContactClosureInput')

    def __MatchContactClosureInput(self, match, tag):
        
        ValueStateValues = {
            '3': 'Close', 
            '4': 'Open'
        }
        
        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('ContactClosureInput', value, {'Integration ID': match.group(1).decode(), 'Input': match.group(2).decode()})
        except KeyError:
            self.Error(['ContactClosureInput: Invalid/unexpected response.'])

    def SetContactClosureOutput(self, value, qualifier):
        
        OutputStates = {
            '1': '11', 
            '2': '12', 
            '3': '13', 
            '4': '14', 
            '5': '15'
        }

        ValueStateValues = {
            'Close': '100', 
            'Open' : '0'
        }
        
        if value in ValueStateValues and qualifier['Integration ID'] and qualifier['Output'] in OutputStates:
            self.__SetHelper('ContactClosureOutput', '#DEVICE,{},{},{}\r\n'.format(qualifier['Integration ID'], OutputStates[qualifier['Output']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetContactClosureOutput')

    def UpdateContactClosureOutput(self, value, qualifier):

        OutputStates = {
            '1': '11', 
            '2': '12', 
            '3': '13', 
            '4': '14', 
            '5': '15'
        }
        
        if qualifier['Integration ID'] and qualifier['Output'] in OutputStates:
            self.__UpdateHelper('ContactClosureOutput', '?DEVICE,{},{},14\r\n'.format(qualifier['Integration ID'], OutputStates[qualifier['Output']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateContactClosureOutput')

    def __MatchContactClosureOutput(self, match, tag):
        
        OutputStates = {
            '11': '1', 
            '12': '2', 
            '13': '3', 
            '14': '4', 
            '15': '5'
        }

        if tag == 'Polled':
            ValueStateValues = {'100': 'Close', '0': 'Open'}
        elif tag == 'Unsolicited':
            ValueStateValues = {'3': 'Close', '4': 'Open'}

        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('ContactClosureOutput', value, {'Integration ID': match.group(1).decode(), 'Output': OutputStates[match.group(2).decode()]})
        except KeyError:
            self.Error(['ContactClosureOutput: Invalid/unexpected response.'])

    def SetDaylightMode(self, value, qualifier):
        
        ValueStateValues = {
            'On' : '1', 
            'Off': '2'
        }
        
        if value in ValueStateValues and qualifier['Integration ID']:
            self.__SetHelper('DaylightMode', '#AREA,{},{}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDaylightMode')

    def UpdateDaylightMode(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('DaylightMode', '?AREA,{},7\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDaylightMode')

    def __MatchDaylightMode(self, match, tag):
        
        ValueStateValues = {
            '1': 'On', 
            '2': 'Off'
        }

        try:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('DaylightMode', value, {'Integration ID': match.group(1).decode()})
        except KeyError:
            self.Error(['DaylightMode: Invalid/unexpected response.'])

    def SetDeviceButton(self, value, qualifier):

        ValueStateValues = {
            'Press'  : '3', 
            'Release': '4'
        }
        
        if value in ValueStateValues and qualifier['Integration ID'] and qualifier['Component Number'] in self.deviceButtonList:
            self.__SetHelper('DeviceButton', '#DEVICE,{},{},{}\r\n'.format(qualifier['Integration ID'], qualifier['Component Number'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceButton')

    def UpdateDeviceButton(self, value, qualifier):
        
        statusUpdate = self.Commands['DeviceButton']['Status']
        if qualifier['Integration ID'] and qualifier['Component Number'] in self.deviceButtonList:
            if qualifier['Integration ID'] not in statusUpdate and qualifier['Component Number'] not in statusUpdate:
                self.AddMatchString(re.compile('~DEVICE,({}),({}),([34])\r\n'.format(qualifier['Integration ID'], qualifier['Component Number']).encode()), self.__MatchDeviceButton, None)
        else:
            self.Discard('Invalid Command for UpdateDeviceButton')
 
    def __MatchDeviceButton(self, match, tag):

        ValueStateValues = {
            '3': 'Press',
            '4': 'Release'
        }

        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('DeviceButton', value, {'Integration ID': match.group(1).decode(), 'Component Number': match.group(2).decode()})
        except KeyError:
            self.Error(['DeviceButton: Invalid/unexpected response.'])
            
    def __MatchEcoSystemBallastOccupancySensor(self, match, tag):

        ValueStateValues = {
            '3': 'Occupied', 
            '4': 'Unoccupied'
        }

        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('EcoSystemBallastOccupancySensor', value, {'Integration ID': match.group(1).decode(), 'Sensor': str(int(match.group(2).decode())-699)})
        except (ValueError, KeyError):
            self.Error(['EcoSystemBallastOccupancySensor: Invalid/unexpected response.'])
            
    def SetGrafikEyeScene(self, value, qualifier):
        
        scene = 0 if value == 'Off' else int(value)
        if 0 <= scene <= 16 and qualifier['Integration ID']:
            self.__SetHelper('GrafikEyeScene', '#DEVICE,{},141,7,{}\r\n'.format(qualifier['Integration ID'], scene), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGrafikEyeScene')
            
    def UpdateGrafikEyeScene(self, value, qualifier):

        
        if qualifier['Integration ID']:
            self.__UpdateHelper('GrafikEyeScene', '?DEVICE,{},141,7\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGrafikEyeScene')

    def __MatchGrafikEyeScene(self, match, tag):
        
        IntegrationID = match.group(1).decode()
        IntegrationID = IntegrationID[-8:].upper() if '0x' in IntegrationID else IntegrationID
        value = 'Off' if match.group(2).decode() == '0' else match.group(2).decode()
        self.WriteStatus('GrafikEyeScene', value, {'Integration ID': IntegrationID})
        
    def SetGrafikEyeShadeColumn(self, value, qualifier):

        key = 'Column {} {}'.format(qualifier['Column'], value)
        States = {
            'Column 1 Open'     : '38', 
            'Column 1 Preset 1' : '39', 
            'Column 1 Close'    : '40', 
            'Column 1 Lower'    : '41', 
            'Column 1 Raise'    : '47',
            'Column 2 Open'     : '44', 
            'Column 2 Preset 1' : '45', 
            'Column 2 Close'    : '46', 
            'Column 2 Lower'    : '52', 
            'Column 2 Raise'    : '53',
            'Column 3 Open'     : '50', 
            'Column 3 Preset 1' : '51', 
            'Column 3 Close'    : '56', 
            'Column 3 Lower'    : '57', 
            'Column 3 Raise'    : '58',
        }
        
        if key in States and qualifier['Integration ID']:
            self.__SetHelper('GrafikEyeShadeColumn', '#DEVICE,{},{}\r\n'.format(qualifier['Integration ID'], States[key]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGrafikEyeShadeColumn')

    def UpdateGrafikEyeShadeColumnStatus(self, value, qualifier):

        ColumnStates = {
            'Column 1 Open'     : '174',
            'Column 1 Preset 1' : '175',
            'Column 1 Close'    : '211',
            'Column 2 Open'     : '183',
            'Column 2 Preset 1' : '184',
            'Column 2 Close'    : '220',
            'Column 3 Open'     : '192',
            'Column 3 Preset 1' : '193',
            'Column 3 Close'    : '229'
        }

        if qualifier['Column'] in ColumnStates and qualifier['Integration ID']:
            GrafikEyeShadeColumnStatusCmdString = '?DEVICE,{},{},9\r\n'.format(qualifier['Integration ID'], ColumnStates[qualifier['Column']])
            self.__UpdateHelper('GrafikEyeShadeColumnStatus', GrafikEyeShadeColumnStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGrafikEyeShadeColumnStatus')

    def __MatchGrafikEyeShadeColumnStatus(self, match, tag):

        ColumnStates = {
            '174' : 'Column 1 Open',
            '175' : 'Column 1 Preset 1',
            '211' : 'Column 1 Close',
            '183' : 'Column 2 Open',
            '184' : 'Column 2 Preset 1',
            '220' : 'Column 2 Close',
            '192' : 'Column 3 Open',
            '193' : 'Column 3 Preset 1',
            '229' : 'Column 3 Close'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'Normal Flash',
            '3' : 'Rapid Flash'
        }

        IntegrationID = match.group(1).decode()
        qualifier = {
            'Integration ID' : IntegrationID[-8:].upper() if '0x' in IntegrationID else IntegrationID,
            'Column' : ColumnStates[match.group(2).decode()]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('GrafikEyeShadeColumnStatus', value, qualifier)

    def SetGrafikEyeZoneLightLevel(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Integration ID'] and 1 <= qualifier['Zone'] <= 24:
            self.__SetHelper('GrafikEyeZoneLightLevel', '#DEVICE,{},{},14,{}\r\n'.format(qualifier['Integration ID'], qualifier['Zone'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGrafikEyeZoneLightLevel')

    def UpdateGrafikEyeZoneLightLevel(self, value, qualifier):
        
        if qualifier['Integration ID'] and 1 <= qualifier['Zone'] <= 24:
            self.__UpdateHelper('GrafikEyeZoneLightLevel', '?DEVICE,{},{},14\r\n'.format(qualifier['Integration ID'], qualifier['Zone']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGrafikEyeZoneLightLevel')

    def __MatchGrafikEyeZoneLightLevel(self, match, tag):
        
        IntegrationID = match.group(1).decode()
        IntegrationID = IntegrationID[-8:].upper() if '0x' in IntegrationID else IntegrationID
        Zone = int(match.group(2).decode())
        value = int(float(match.group(3).decode()))
        self.WriteStatus('GrafikEyeZoneLightLevel', value, {'Integration ID': IntegrationID, 'Zone': Zone})

    def SetGrafikEyeZoneLightRampLevel(self, value, qualifier):
        
        fadeTime = self.__TimeConvert(qualifier['Fade Time'])
        delayTime = self.__TimeConvert(qualifier['Delay Time'])
        
        if 0 <= value <= 100 and qualifier['Integration ID'] and 1 <= qualifier['Zone'] <= 24 and fadeTime and delayTime:
            self.__SetHelper('GrafikEyeZoneLightRampLevel', '#DEVICE,{},{},14,{},{},{}\r\n'.format(qualifier['Integration ID'], qualifier['Zone'], value, fadeTime, delayTime), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGrafikEyeZoneLightRampLevel')

    def SetHVACOperatingMode(self, value, qualifier):

        ValueStateValues = {
            'Off'     : '1', 
            'Heat'    : '2', 
            'Cool'    : '3', 
            'Auto'    : '4', 
            'Em. Heat': '5', 
            'Fan'     : '7', 
            'Dry'     : '8' 
        }
        
        if value in ValueStateValues and qualifier['Integration ID']:
            HVACOperatingModeCmdString = '#HVAC,{},3,{}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value]) # No '\r\n' based on customer feedback
            self.__SetHelper('HVACOperatingMode', HVACOperatingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHVACOperatingMode')

    def UpdateHVACOperatingMode(self, value, qualifier):
        
        if qualifier['Integration ID']:
            HVACOperatingModeCmdString = '?HVAC,{},3\r\n'.format(qualifier['Integration ID'])
            self.__UpdateHelper('HVACOperatingMode', HVACOperatingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHVACOperatingMode')

    def __MatchHVACOperatingMode(self, match, tag):
        
        ValueStateValues = {
            '1': 'Off', 
            '2': 'Heat', 
            '3': 'Cool', 
            '4': 'Auto', 
            '5': 'Em. Heat', 
            '7': 'Fan', 
            '8': 'Dry', 
            '6': 'Locked Out'
        }

        qualifier = {}
        qualifier['Integration ID'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HVACOperatingMode', value, qualifier)

    def UpdateIPAddress(self, value, qualifier):

        self.__UpdateHelper('IPAddress', '?ETHERNET,0\r\n', value, qualifier)

    def __MatchIPAddress(self, match, tag):
        
        self.WriteStatus('IPAddress', match.group(1).decode(), None)

    def SetLEDState(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off': '0'
        }
        
        if value in ValueStateValues and qualifier['Integration ID'] and 1 <= qualifier['Component Number'] <= 5000: 
            self.__SetHelper('LEDState', '#DEVICE,{},{},{}\r\n'.format(qualifier['Integration ID'], qualifier['Component Number'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDState')

    def UpdateLEDState(self, value, qualifier):
        
        if qualifier['Integration ID'] and 1 <= qualifier['Component Number'] <= 5000: 
            self.__UpdateHelper('LEDState', '?DEVICE,{},{},9\r\n'.format(qualifier['Integration ID'], qualifier['Component Number']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLEDState')

    def __MatchLEDState(self, match, tag):
        
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Integration ID'] = match.group(1).decode()
        qualifier['Component Number'] = int(match.group(2).decode())
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('LEDState', value, qualifier)

    def SetLiftControl(self, value, qualifier):
        
        ValueStateValues = {
            'Raise': '14', 
            'Lower': '15', 
            'Stop' : '16'
        }
        
        if value in ValueStateValues and qualifier['Integration ID']:
            self.__SetHelper('LiftControl', '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLiftControl')

    def __MatchLocalContactClosureInput(self, match, tag):

        ValueStateValues = {
            '3': 'Occupied', 
            '4': 'Unoccupied'
        }

        try:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('LocalContactClosureInput', value, {'Integration ID': match.group(1).decode()})
        except KeyError:
            self.Error(['LocalContactClosureInput: Invalid/unexpected response.'])
            
    def SetMasterLevelStep(self, value, qualifier):

        ValueStateValues = {
            'Up'  : '18', 
            'Down': '19', 
            'Stop': '20'
        }

        if value in ValueStateValues and qualifier['Integration ID'] and 1 <= qualifier['Zone'] <= self.masterLevelStepMax:
            ZoneValue = self.zone if self.zone == 141 else self.zone + qualifier['Zone']
            self.__SetHelper('MasterLevelStep', '#DEVICE,{},{},{}\r\n'.format(qualifier['Integration ID'], ZoneValue, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterLevelStep')

    def UpdateOccupancyGroup(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('OccupancyGroup', '?GROUP,{0},3\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOccupancyGroup')

    def __MatchOccupancyGroup(self, match, tag):
        
        ValueStateValues = {
            '3'  : 'Occupied', 
            '4'  : 'Unoccupied', 
            '255': 'Unknown'
        }

        qualifier = {}
        qualifier['Integration ID'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OccupancyGroup', value, qualifier)

    def UpdateOccupancySensor(self, value, qualifier):

        statusUpdate = self.Commands['OccupancySensor']['Status']
        if qualifier['Integration ID'] and 1 <= int(qualifier['Number']) <= self.occupancyMax:
            if qualifier['Integration ID'] not in statusUpdate and qualifier['Number'] not in statusUpdate:
                self.AddMatchString(re.compile('~DEVICE,({}),({}),([34])\r\n'.format(qualifier['Integration ID'], int(qualifier['Number'])+self.occupancyAdd).encode()), self.__MatchOccupancySensor, None)
        else:
            self.Discard('Invalid Command for UpdateOccupancySensor')
            
    def __MatchOccupancySensor(self, match, tag):

        ValueStateValues = {
            '3': 'Occupied', 
            '4': 'Unoccupied'
        }

        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('OccupancySensor', value, {'Integration ID': match.group(1).decode(), 'Number': str(int(match.group(2).decode())-self.occupancyAdd)})
        except KeyError:
            self.Error(['OccupancySensor: Invalid/unexpected response.'])
            
    def SetOutputLevel(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Integration ID']:
            self.__SetHelper('OutputLevel', '#OUTPUT,{},1,{}\r\n'.format(qualifier['Integration ID'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('OutputLevel', '?OUTPUT,{}\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        
        value = int(float(match.group(2).decode()))
        self.WriteStatus('OutputLevel', value, {'Integration ID': match.group(1).decode()})

    def SetOutputLevelStep(self, value, qualifier):
        
        ValueStateValues = {
            'Up'   : '2', 
            'Down' : '3', 
            'Stop' : '4'
        }
        
        if value in ValueStateValues and qualifier['Integration ID']:
            self.__SetHelper('OutputLevelStep', '#OUTPUT,{},{}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevelStep')

    def SetQSEScene(self, value, qualifier):
        
        scene = 0 if value == 'Off' else int(value)
        if 0 <= scene <= 16 and qualifier['Integration ID'] and qualifier['Component Number'] in ['5', '6', '7', '8', '10', '11', '12', '13']:
            self.__SetHelper('QSEScene', '#DEVICE,{},{},7,{}\r\n'.format(qualifier['Integration ID'], qualifier['Component Number'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetQSEScene')
            
    def UpdateQSEScene(self, value, qualifier):
        
        if qualifier['Integration ID'] and qualifier['Component Number'] in ['5', '6', '7', '8', '10', '11', '12', '13']:
            self.__UpdateHelper('QSEScene', '?DEVICE,{},{},7\r\n'.format(qualifier['Integration ID'], qualifier['Component Number']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateQSEScene')

    def __MatchQSEScene(self, match, tag):
        
        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10': '10', 
            '11': '11', 
            '12': '12', 
            '13': '13', 
            '14': '14', 
            '15': '15', 
            '16': '16', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('QSEScene', value, {'Integration ID': match.group(1).decode(), 'Component Number': match.group(2).decode()})

    def SetScene(self, value, qualifier):
        
        scene = 0 if value == 'Off' else int(value)
        if 0 <= scene <= 16 and qualifier['Integration ID'] and 1 <= qualifier['Area'] <= self.sceneZoneMax:
            self.__SetHelper('Scene', '#DEVICE,{},{},7,{}\r\n'.format(qualifier['Integration ID'], self.sceneAreaAdd+qualifier['Area'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def UpdateScene(self, value, qualifier):
        
        if qualifier['Integration ID'] and 1 <= qualifier['Area'] <= self.sceneZoneMax:
            self.__UpdateHelper('Scene', '?DEVICE,{},{},7\r\n'.format(qualifier['Integration ID'], self.sceneAreaAdd+qualifier['Area']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateScene')

    def __MatchScene(self, match, tag):
        
        ValueStateValues = {
            '1' : '1', 
            '2' : '2', 
            '3' : '3', 
            '4' : '4', 
            '5' : '5', 
            '6' : '6', 
            '7' : '7', 
            '8' : '8', 
            '9' : '9', 
            '10': '10', 
            '11': '11', 
            '12': '12', 
            '13': '13', 
            '14': '14', 
            '15': '15', 
            '16': '16', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Scene', value, {'Integration ID': match.group(1).decode(), 'Area': match.group(2).decode()})

    def SetShadeGroupLevel(self, value, qualifier):
        
        delayTime = self.__TimeConvert(qualifier['Delay Time'])
        
        if 0 <= value <= 100 and qualifier['Integration ID'] and delayTime:
            self.__SetHelper('ShadeGroupLevel', '#SHADEGRP,{},1,{},{}\r\n'.format(qualifier['Integration ID'], value, delayTime), value, qualifier)
        else:
            self.Discard('Invalid Command for SetShadeGroupLevel')

    def UpdateShadeGroupLevelStatus(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('ShadeGroupLevelStatus', '?SHADEGRP,{}\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateShadeGroupLevelStatus')

    def __MatchShadeGroupLevelStatus(self, match, tag):

        value = int(float(match.group(2).decode()))
        self.WriteStatus('ShadeGroupLevelStatus', value, {'Integration ID': match.group(1).decode()})

    def SetShadeGroupPreset(self, value, qualifier):
        
        if 1 <= int(value) <= 30 and qualifier['Integration ID']:
            self.__SetHelper('ShadeGroupPreset', '#SHADEGRP,{},{}\r\n'.format(qualifier['Integration ID'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetShadeGroupPreset')

    def UpdateShadeGroupPreset(self, value, qualifier):

        if qualifier['Integration ID']:
            self.__UpdateHelper('ShadeGroupPreset', '?SHADEGRP,{},6\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateShadeGroupPreset')

    def __MatchShadeGroupPreset(self, match, tag):

        value = match.group(2).decode()
        self.WriteStatus('ShadeGroupPreset', value, {'Integration ID': match.group(1).decode()})

    def SetShadePosition(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Integration ID']:
            self.__SetHelper('ShadePosition', '#DEVICE,{},0,14,{},0\r\n'.format(qualifier['Integration ID'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetShadePosition')

    def UpdateShadePosition(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('ShadePosition', '?DEVICE,{},0,14\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateShadePosition')

    def __MatchShadePosition(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('ShadePosition', value, {'Integration ID': match.group(1).decode()})

    def SetTiltControl(self, value, qualifier):
        
        ValueStateValues = {
            'Raise': '11', 
            'Lower': '12', 
            'Stop' : '13'
        }

        if value in ValueStateValues and qualifier['Integration ID']:
            self.__SetHelper('TiltControl', '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTiltControl')

    def __MatchWirelessOccupancySensor(self, match, tag):

        ValueStateValues = {
            '3' : 'Occupied', 
            '4' : 'Unoccupied'
        }

        try:
            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('WirelessOccupancySensor', value, {'Integration ID': match.group(1).decode(),'Sensor': str(int(match.group(2).decode())-499)})
        except (ValueError, KeyError):
            self.Error(['WirelessOccupancySensor: Invalid/unexpected response.'])
            
    def SetZoneControl(self, value, qualifier):
        
        ValueStateValues = {
            'Raise': '2', 
            'Lower': '3', 
            'Stop' : '4'
        }

        if value in ValueStateValues and qualifier['Integration ID']:
            self.__SetHelper('ZoneControl', '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneControl')

    def SetZoneLevel(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Integration ID']:
            self.__SetHelper('ZoneLevel', '#OUTPUT,{0},1,{1}\r\n'.format(qualifier['Integration ID'], '%.2f' % value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneLevel')

    def UpdateZoneLevel(self, value, qualifier):
        
        if qualifier['Integration ID']:
            self.__UpdateHelper('ZoneLevel', '?OUTPUT,{0}\r\n'.format(qualifier['Integration ID']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneLevel')

    def __MatchZoneLevel(self, match, tag):
        
        qualifier = {}
        qualifier['Integration ID'] = match.group(1).decode()
        value = float(match.group(2).decode())
        self.WriteStatus('ZoneLevel', value, qualifier)

    def SetZoneLightLevel(self, value, qualifier):
        
        fadeTime = self.__TimeConvert(qualifier['Fade Time'])
        delayTime = self.__TimeConvert(qualifier['Delay Time'])
        
        if 0 <= value <= 100 and qualifier['Integration ID'] and 1 <= qualifier['Zone'] <= self.sceneZoneMax and fadeTime and delayTime:
            self.__SetHelper('ZoneLightLevel', '#DEVICE,{},{},14,{},{},{}\r\n'.format(qualifier['Integration ID'], self.zoneLevelAdd+qualifier['Zone'], value, fadeTime, delayTime), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoneLightLevel')

    def UpdateZoneLightLevelStatus(self, value, qualifier):
        
        if qualifier['Integration ID'] and 1 <= qualifier['Zone'] <= self.sceneZoneMax:
            self.__UpdateHelper('ZoneLightLevelStatus', '?DEVICE,{},{},14\r\n'.format(qualifier['Integration ID'], self.zoneLevelAdd+qualifier['Zone']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateZoneLightLevelStatus')

    def __MatchZoneLightLevelStatus(self, match, tag):

        value = int(float(match.group(3).decode()))
        self.WriteStatus('ZoneLightLevelStatus', value, {'Integration ID': match.group(1).decode(), 'Zone': int(match.group(2).decode())-self.zoneLevelAdd})

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Authenticated:
            self.Send(commandstring)
             
    def __UpdateHelper(self, command, commandstring, value, qualifier):
        
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.Authenticated:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        ERRORS = {
            '1': 'Parameter count mismatch',
            '2': 'Object does not exist',
            '3': 'Invalid action number',
            '4': 'Parameter data out of range',
            '5': 'Parameter data malformed',
            '6': 'Unsupported Command'
        }

        try:
            self.Error([ERRORS[match.group(1).decode()]])
        except KeyError:
            pass

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
    
    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = False
        else:
            self.Authenticated = True
        
    def lutr_13_48_GE(self):
        
        self.model = 'GE'
        self.zone = 141
        self.masterLevelStepMax = 24
        self.occupancyAdd = 40
        self.occupancyMax = 5
        self.deviceButtonList = [
            '1', '2', '3','4','5','6','7','8','9','10',
            '11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','38','39','40','41',
            '44','45','46','47','50','51','52','53','56',
            '57','58', '70','71','76','77','83','141'
        ]

    def lutr_13_48_ECO(self):
        
        self.model = 'ECO'
        self.zone = 1000
        self.masterLevelStepMax = 100
        self.sceneZoneMax = 100
        self.sceneAreaAdd = 1200
        self.zoneLevelAdd = 1000
        self.occupancyAdd = 135
        self.occupancyMax = 4
        
    def lutr_13_48_QSN4(self):
        
        self.model = 'QSN4'
        self.zone = 4
        self.masterLevelStepMax = 4
        self.sceneZoneMax = 4
        self.sceneAreaAdd = 9
        self.zoneLevelAdd = 4
        self.occupancyAdd = 33
        self.occupancyMax = 4

    def lutr_13_48_DAL(self):
        
        self.model = 'DAL'
        self.zone = 300
        self.masterLevelStepMax = 32
        self.sceneZoneMax = 32
        self.sceneAreaAdd = 400
        self.zoneLevelAdd = 300
        self.occupancyAdd = 150
        self.occupancyMax = 4

    def lutr_13_48_seeTouch(self):
        
        self.model = 'seeTouch'
        self.deviceButtonList = [
            '1', '2', '3','4','5','6','7','8',
            '9','10','16','17','18','19','25','26'
        ]

    def lutr_13_48_SQ(self):
    
        self.model = 'SQ'

    def lutr_13_48_QS(self):
        
        self.model = 'QS'
        self.deviceButtonList = [
            '1', '2', '3','4','5','6','7','8','9','10',
            '11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','38','39','40','41',
            '44','45','46','47','50','51','52','53','56',
            '57','58', '70','71','76','77','83','141'
        ]

    def lutr_13_48_HW(self):
        
        self.model = 'HW'
        self.zone = 141
        self.masterLevelStepMax = 24
        self.deviceButtonList = [
            '1', '2', '3','4','5','6','7','8','9','10',
            '11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24','38','39','40','41',
            '44','45','46','47','50','51','52','53','56',
            '57','58', '70','71','76','77','83','141'
        ]

    def lutr_13_48_QSE(self):
        
        self.model = 'QSE'
        self.zone = 141
        self.masterLevelStepMax = 24
        self.occupancyAdd = 40
        self.occupancyMax = 5

    def lutr_13_48_RA(self):
    
        self.model = 'RA'

    def lutr_13_48_myRoom(self):
    
        self.model = 'myRoom'

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self, Model)

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self, Model)

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        DeviceClass.__init__(self, Model) 

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()