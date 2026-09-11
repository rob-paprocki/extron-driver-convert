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
            'AudioInputFormat': {'Parameters':['Slot'], 'Status': {}},
            'AudioMute': {'Parameters':['Slot'], 'Status': {}},
            'AudioOutputVolume': {'Parameters':['Slot'], 'Status': {}},
            'FanSpeed': {'Parameters':['Fan'], 'Status': {}},
            'FanStatus': {'Parameters':['Fan'], 'Status': {}},
            'FiberLinkStatus': {'Parameters':['Slot','Connection'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Slot'], 'Status': {}},
            'Power': {'Parameters':['Slot'], 'Status': {}},
            'PowerSupplyStatus': {'Parameters':['Power Supply'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Slot'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Slot'], 'Status': {}},
            'InputSignalStatus': {'Parameters':['Slot'], 'Status': {}},
            'OutputResolution': {'Parameters':['Slot'], 'Status': {}},
            'SlotStatus': {'Parameters':['Slot'], 'Status': {}},
            'Temperature': { 'Status': {}},
            'VideoMute': {'Parameters':['Slot'], 'Status': {}}
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Sts[0-9]+\.[0-9]+ [0-9]+\.[0-9]+ \+([0-9]+\.[0-9]+)F ([0-9]{5}) ([0-9]{5}) ([0-9]{5}) ([0-9]{5}) ([0-2]) ([0-2])'), self.__MatchTemperatureFanSpeed, None)
            self.AddMatchString(re.compile(b'{([0-4])}AfmtI([0-2])'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(re.compile(b'{([0-4])}Amt1\*(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'{([0-4])}Amt(0|1)\r\n'), self.__MatchAudioMute, 'Query')
            self.AddMatchString(re.compile(b'{([0-4])}Vol(\d+)\r\n'), self.__MatchAudioOutputVolume, None)
            self.AddMatchString(re.compile(b'FAILED: Fan ([1-4])\r\n'), self.__MatchFailedFanStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}Inf00\*SFPALnk([01]) SFPBLnk([01]).*\r\n'), self.__MatchFiberLinkStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}HdcpE([0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'{([0-4])}HdcpI([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}Sts04\*([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}SigI([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}Rate(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'PowrS([1-4])\*([01])\r\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'Slot([01])([01])([01])([01]) PS([0-2])([0-2])'), self.__MatchSlotStatus, None)
            self.AddMatchString(re.compile(b'{([0-4])}Vmt([0-2])\r\n'), self.__MatchVideoMute, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None) # Echo Mode for SSH 

    def __MatchEchoMode(self, match, qualifier):
        
        self.EchoDisabled = False
       
    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioInputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto' : '0', 
            'Digital' : '1', 
            'Analog' : '2'
        }
        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for SetAudioInputFormat')
        else:
            AudioInputFormatCmdString = '{{{0}:wI{1}AFMT\r}}\r'.format(qualifier['Slot'], ValueStateValues[value])
            self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def UpdateAudioInputFormat(self, value, qualifier):

        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for UpdateAudioInputFormat')
        else:
            AudioInputFormatCmdString = '{{{0}:wIAFMT\r}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def __MatchAudioInputFormat(self, match, tag):

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : 'Digital', 
            '2' : 'Analog'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioInputFormat', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Slot']) <= 4 and value in ValueStateValues:
            AudioMuteCmdString = '{{{0}:1*{1}Z}}\r'.format(qualifier['Slot'], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4:
            AudioMuteCmdString = '{{{0}:1Z}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAudioOutputVolume(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4 and 0 <= value <= 100:
            AudioOutputVolumeCmdString = '{{{0}:{1}V}}\r'.format(qualifier['Slot'], value)
            self.__SetHelper('AudioOutputVolume', AudioOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputVolume')

    def UpdateAudioOutputVolume(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4:
            AudioOutputVolumeCmdString = '{{{0}:V}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('AudioOutputVolume', AudioOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutputVolume')

    def __MatchAudioOutputVolume(self, match, tag):

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('AudioOutputVolume', value, qualifier)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = '}\r\nSI'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
    
    def __MatchTemperatureFanSpeed(self, match, tag):

        self.WriteStatus('Temperature', float(match.group(1).decode()), None)
        fan1 = int(match.group(2).decode())
        if fan1 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '1'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '1'})
        fan2 = int(match.group(3).decode())
        if fan2 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '2'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '2'})
        fan3 = int(match.group(4).decode())
        if fan3 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '3'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '3'})
        fan4 = int(match.group(5).decode())
        if fan4 == 0:
            self.WriteStatus('FanStatus', 'Failed', {'Fan': '4'})
        else:
            self.WriteStatus('FanStatus', 'Normal', {'Fan': '4'})
        
        self.WriteStatus('FanSpeed', fan1, {'Fan': '1'})
        self.WriteStatus('FanSpeed', fan2, {'Fan': '2'})
        self.WriteStatus('FanSpeed', fan3, {'Fan': '3'})
        self.WriteStatus('FanSpeed', fan4, {'Fan': '4'})
    
    def __MatchFailedFanStatus(self, match, tag):

        qual = match.group(1).decode()
        value = 'Failed'
        self.WriteStatus('FanStatus', value, {'Fan': qual})

    def UpdateFiberLinkStatus(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4 and qualifier['Connection'] in ['SFP A', 'SFP B']:
            FiberLinkStatusCmdString = '{{{0}:i|}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('FiberLinkStatus', FiberLinkStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFiberLinkStatus')

    def __MatchFiberLinkStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Detected',
            '0' : 'Not Detected'
        }
        
        self.WriteStatus('FiberLinkStatus', ValueStateValues[match.group(2).decode()], {'Slot' : match.group(1).decode(), 'Connection' : 'SFP A'})
        self.WriteStatus('FiberLinkStatus', ValueStateValues[match.group(3).decode()], {'Slot' : match.group(1).decode(), 'Connection' : 'SFP B'})

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')
        else:
            HDCPAuthorizedDeviceCmdString = '{{{0}:wE{1}Hdcp\r}}\r'.format(qualifier['Slot'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPAuthorizedDeviceCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')
        else:
            HDCPAuthorizedDeviceCmdString = '{{{0}:wEHdcp\r}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPAuthorizedDeviceCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):
        
        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')
        else:
            HDCPInputStatusCmdString = '{{{0}:wIHdcp\r}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
            
    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'Source Connected and HDCP',
            '2': 'Source Connected and No HDCP'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):
        
        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')
        else:
            HDCPOutputStatusCmdString = '{{{0}:wOHdcp\r}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
            
    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Sink Detected', 
            '1' : 'Sink Detected with HDCP', 
            '2' : 'Sink Detected with No HDCP'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):
        
        slot = int(qualifier['Slot'])
        if slot < 1 or slot > 4:
            self.Discard('Invalid Command for UpdateInputSignalStatus')
        else:
            InputSignalStatusCmdString = '{{{0}:4S}}\r\n'.format(qualifier['Slot'])
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
            
    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'Not Active', 
            '1' : 'Active', 
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60Hz)': '10',
            '800x600 (60Hz)': '11',
            '1024x768 (60Hz)': '12',
            '1280x768 (60Hz)': '13',
            '1280x800 (60Hz)': '14',
            '1280x1024 (60Hz)': '15',
            '1360x768 (60Hz)': '16',
            '1366x768 (60Hz)': '17',
            '1440x900 (60Hz)': '18',
            '1400x1050 (60Hz)': '19',
            '1600x900 (60Hz)': '20',
            '1680x1050 (60Hz)': '21',
            '1600x1200 (60Hz)': '22',
            '1920x1200 (60Hz)': '23',
            '480p (59.94Hz)': '24',
            '480p (60Hz)': '25',
            '576p (50Hz)': '26',
            '720p (25Hz)': '29',
            '720p (29.97Hz)': '30',
            '720p (30Hz)': '31',
            '720p (50Hz)': '32',
            '720p (59.94Hz)': '33',
            '720p (60Hz)': '34',
            '1080i (50Hz)': '35',
            '1080i (59.94Hz)': '36',
            '1080i (60Hz)': '37',
            '1080p (23.98Hz)': '38',
            '1080p (24Hz)': '39',
            '1080p (25Hz)': '40',
            '1080p (29.97Hz)': '41',
            '1080p (30Hz)': '42',
            '1080p (50Hz)': '43',
            '1080p (59.94Hz)': '44',
            '1080p (60Hz)': '45',
            '2048x1080 (23.98Hz)': '46',
            '2048x1080 (24Hz)': '47',
            '2048x1080 (25Hz)': '48',
            '2048x1080 (29.97Hz)': '49',
            '2048x1080 (30Hz)': '50',
            '2048x1080 (50Hz)': '51',
            '2048x1080 (59.94Hz)': '52',
            '2048x1080 (60Hz)': '53',
            '2048x1200 (60Hz)': '54',
            '2048x1536 (60Hz)': '55',
            '2560x1080 (60Hz)': '56',
            '2560x1440 (60Hz)': '57',
            '2560x1600 (60Hz)': '58',
            '3840x2160 (23.98Hz)': '59',
            '3840x2160 (24Hz)': '60',
            '3840x2160 (25Hz)': '61',
            '3840x2160 (29.97Hz)': '62',
            '3840x2160 (30Hz)': '63',
            '3840x2160 (50Hz)': '64',
            '3840x2160 (59.94Hz)': '65',
            '3840x2160 (60Hz)': '66',
            '4096x2160 (23.98Hz)': '69',
            '4096x2160 (24Hz)': '70',
            '4096x2160 (25Hz)': '71',
            '4096x2160 (29.97Hz)': '72',
            '4096x2160 (30Hz)': '73',
            '4096x2160 (50Hz)': '74',
            '4096x2160 (59.94Hz)': '75',
            '4096x2160 (60Hz)': '76',
            'Custom Rate 1': '201',
            'Scaler Bypass Mode': '199'
        }

        if 1 <= int(qualifier['Slot']) <= 4 and value in ValueStateValues:
            OutputResolutionCmdString = '{{{0}:w{1}RATE\r}}\r'.format(qualifier['Slot'], ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4:
            OutputResolutionCmdString = '{{{0}:wRATE\r}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputResolution')

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10': '640x480 (60Hz)',
            '11': '800x600 (60Hz)',
            '12': '1024x768 (60Hz)',
            '13': '1280x768 (60Hz)',
            '14': '1280x800 (60Hz)',
            '15': '1280x1024 (60Hz)',
            '16': '1360x768 (60Hz)',
            '17': '1366x768 (60Hz)',
            '18': '1440x900 (60Hz)',
            '19': '1400x1050 (60Hz)',
            '20': '1600x900 (60Hz)',
            '21': '1680x1050 (60Hz)',
            '22': '1600x1200 (60Hz)',
            '23': '1920x1200 (60Hz)',
            '24': '480p (59.94Hz)',
            '25': '480p (60Hz)',
            '26': '576p (50Hz)',
            '29': '720p (25Hz)',
            '30': '720p (29.97Hz)',
            '31': '720p (30Hz)',
            '32': '720p (50Hz)',
            '33': '720p (59.94Hz)',
            '34': '720p (60Hz)',
            '35': '1080i (50Hz)',
            '36': '1080i (59.94Hz)',
            '37': '1080i (60Hz)',
            '38': '1080p (23.98Hz)',
            '39': '1080p (24Hz)',
            '40': '1080p (25Hz)',
            '41': '1080p (29.97Hz)',
            '42': '1080p (30Hz)',
            '43': '1080p (50Hz)',
            '44': '1080p (59.94Hz)',
            '45': '1080p (60Hz)',
            '46': '2048x1080 (23.98Hz)',
            '47': '2048x1080 (24Hz)',
            '48': '2048x1080 (25Hz)',
            '49': '2048x1080 (29.97Hz)',
            '50': '2048x1080 (30Hz)',
            '51': '2048x1080 (50Hz)',
            '52': '2048x1080 (59.94Hz)',
            '53': '2048x1080 (60Hz)',
            '54': '2048x1200 (60Hz)',
            '55': '2048x1536 (60Hz)',
            '56': '2560x1080 (60Hz)',
            '57': '2560x1440 (60Hz)',
            '58': '2560x1600 (60Hz)',
            '59': '3840x2160 (23.98Hz)',
            '60': '3840x2160 (24Hz)',
            '61': '3840x2160 (25Hz)',
            '62': '3840x2160 (29.97Hz)',
            '63': '3840x2160 (30Hz)',
            '64': '3840x2160 (50Hz)',
            '65': '3840x2160 (59.94Hz)',
            '66': '3840x2160 (60Hz)',
            '69': '4096x2160 (23.98Hz)',
            '70': '4096x2160 (24Hz)',
            '71': '4096x2160 (25Hz)',
            '72': '4096x2160 (29.97Hz)',
            '73': '4096x2160 (30Hz)',
            '74': '4096x2160 (50Hz)',
            '75': '4096x2160 (59.94Hz)',
            '76': '4096x2160 (60Hz)',
            '201': 'Custom Rate 1',
            '199': 'Scaler Bypass Mode'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputResolution', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        if 1 <= int(qualifier['Slot']) <= 4 and value in ValueStateValues:
            PowerCmdString = 'wS{0}*{1}POWR\r'.format(qualifier['Slot'], ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4:
            PowerCmdString = 'wS{0}POWR\r'.format(qualifier['Slot'])
            res = self.__UpdateHelper_Sync('Power', PowerCmdString, value, qualifier)
            if res:
                powerstate = res[5]
                ValueStateValues = {
                    '0': 'Off',
                    '1': 'On'
                }
                self.WriteStatus('Power', ValueStateValues[powerstate], qualifier)
                
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Power', value, qualifier)

    def __MatchSlotStatus(self, match, tag):

        PowerSupplyStateValues = {
            '1' : 'On', 
            '0' : 'Failed', 
            '2' : 'Not Installed'
        }

        SlotStateValues = {
            '1': 'Installed', 
            '0': 'Not Installed'
        }

        qualifier = {}
        Slot1 = match.group(1).decode()
        Slot2 = match.group(2).decode()
        Slot3 = match.group(3).decode()
        Slot4 = match.group(4).decode()

        PowerSupply1 = match.group(5).decode()
        PowerSupply2 = match.group(6).decode()

        self.WriteStatus('SlotStatus', SlotStateValues[Slot1], {'Slot' : '1'})
        self.WriteStatus('SlotStatus', SlotStateValues[Slot2], {'Slot' : '2'})
        self.WriteStatus('SlotStatus', SlotStateValues[Slot3], {'Slot' : '3'})
        self.WriteStatus('SlotStatus', SlotStateValues[Slot4], {'Slot' : '4'})
        self.WriteStatus('PowerSupplyStatus', PowerSupplyStateValues[PowerSupply1], {'Power Supply' : '1'})
        self.WriteStatus('PowerSupplyStatus', PowerSupplyStateValues[PowerSupply2], {'Power Supply' : '2'})
    
    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Mute Video Only': '1',
            'Mute Video and Sync': '2',
            'Off': '0'
        }

        if 1 <= int(qualifier['Slot']) <= 4 and value in ValueStateValues:
            VideoMuteCmdString = '{{{0}:{1}B}}\r'.format(qualifier['Slot'], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        if 1 <= int(qualifier['Slot']) <= 4:
            VideoMuteCmdString = '{{{0}:B}}\r'.format(qualifier['Slot'])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'Mute Video Only',
            '2': 'Mute Video and Sync',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Slot'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, qualifier)

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

    def __UpdateHelper_Sync(self, command, commandstring, value, qualifier):
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
                    self.SendAndWait(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
                
    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E10': "Invalid command",
            'E11': "Invalid preset number",
            'E12': "Invalid output number/port number",
            'E13': "Invalid parameter (out of range)",
            'E14': "Command not available for this configuration",
            'E17': "Invalid command for this signal type",
            'E18': 'System/command timed out',
            'E21': 'Invalid room number',
            'E22': "Busy",
            'E24': "Privilege violation",
            'E25': "Device not present",
            'E26': "Maximum number of connections exceeded",
            'E28': "Bad filename/file not found"
        }

        if response:
            for k, _ in DEVICE_ERROR_CODES.items():
                if k in response:
                    self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[k])])
                    response = ''
        return response

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': "Invalid output number/port number",
            '13': 'Invalid parameter',
            '14': 'Invalid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System/command timed out',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found',
        }
        
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
    
    #######################################################    
    # RECOMMENDED not to modify the code below this point #
    #######################################################

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