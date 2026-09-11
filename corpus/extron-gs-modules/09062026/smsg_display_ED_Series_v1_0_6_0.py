from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'SafetyLock': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWall': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallMode': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoWallSize': {'Parameters': ['Device ID', 'Row', 'Column'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}}
            }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x18(\x01|\x04|\x31|\x0B)[\x00-\xFF]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x14(\x14|\x18|\x0C|\x08|\x21|\x50)[\x00-\xFF]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x3C(\x01|\x00)[\x00-\xFF]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x11(\x01|\x00)[\x00-\xFF]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x5D(\x01|\x00)[\x00-\xFF]'), self.__MatchSafetyLock, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x84(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWall, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\\x5C(\x01|\x00)[\x00-\xFF]'), self.__MatchVideoWallMode, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x04\x41\x89([\x00-\xFF])([\x00-\x64])[\x00-\xFF]'), self.__MatchVideoWallSize, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x41\x12([\x00-\x64])[\x00-\xFF]'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'\xAA\xFF([\x00-\x64])\x03\x4E([\x00-\xFF])([\x00-\xFF])[\x00-\xFF]'), self.__MatchError, None)

    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return 254
        elif 0 <= int(ID) <= 99:
            return int(ID)
        else:
            print('Invalid Device ID provided')

    def SetAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           '16:9': 0x01,
           'Zoom': 0x04,
           'Wide Zoom': 0x31,
           '4:3': 0x0B
           }

        checksum = int(hex(0x18 + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x18, ID, 0x01, States[value], checksum)
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x18 + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x18, ID, 0x00, checksum)
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            b'\x01': '16:9',
            b'\x04': 'Zoom',
            b'\x31': 'Wide Zoom',
            b'\x0B': '4:3'
            }

        self.WriteStatus('AspectRatio', States[match.group(2)], {'Device ID': str(match.group(1)[0])})

    def SetAutoImage(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x3D + ID + 0x01 + 0x00)[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x3D, ID, 0x01, 0x00, checksum)
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           'PC': 0x14,
           'DVI': 0x18,
           'Input': 0x0C,
           'Component': 0x08,
           'HDMI': 0x21,
           'PlugIn Module': 0x50
           }

        checksum = int(hex(0x14 + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('BBBBBB', 0xAA, 0x14, ID, 0x01, States[value], checksum)
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x14 + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x14, ID, 0x00, checksum)
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
           b'\x14': 'PC',
           b'\x18': 'DVI',
           b'\x0C': 'Input',
           b'\x08': 'Component',
           b'\x21': 'HDMI',
           b'\x50': 'PlugIn Module'
           }

        self.WriteStatus('Input', States[match.group(2)], {'Device ID': str(match.group(1)[0])})

    def SetPIPMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           'On': 0x01,
           'Off': 0x00
           }

        checksum = int(hex(0x3C + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x3C, ID, 0x01, States[value], checksum)
        self.__SetHelper('PIPMode', CmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x3C + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x3C, ID, 0x00, checksum)
        self.__UpdateHelper('PIPMode', CmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        States = {
           b'\x01': 'On',
           b'\x00': 'Off'
           }

        self.WriteStatus('PIPMode', States[match.group(2)], {'Device ID': str(match.group(1)[0])})

    def SetPower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           'On': 0x01,
           'Off': 0x00
           }

        checksum = int(hex(0x11 + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x11, ID, 0x01, States[value], checksum)
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x11 + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x11, ID, 0x00, checksum)
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ID = match.group(1)[0]

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        value = States[match.group(2)]

        if 0 <= ID <= 99:
            self.WriteStatus('Power', value, {'Device ID': str(ID)})
        else:
            print('Invalid Response')

    def SetSafetyLock(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           'On': 0x01,
           'Off': 0x00
           }

        checksum = int(hex(0x5D + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x5D, ID, 0x01, States[value], checksum)
        self.__SetHelper('SafetyLock', CmdString, value, qualifier)

    def UpdateSafetyLock(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x5D + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x5D, ID, 0x00, checksum)
        self.__UpdateHelper('SafetyLock', CmdString, value, qualifier)

    def __MatchSafetyLock(self, match, tag):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
            }

        self.WriteStatus('SafetyLock', States[match.group(1)], {'Device ID': str(match.group(1)[0])})

    def SetVideoWall(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           'On': 0x01,
           'Off': 0x00
           }

        checksum = int(hex(0x84 + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x84, ID, 0x01, States[value], checksum)
        self.__SetHelper('VideoWall', CmdString, value, qualifier)

    def UpdateVideoWall(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x84 + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x84, ID, 0x00, checksum)
        self.__UpdateHelper('VideoWall', CmdString, value, qualifier)

    def __MatchVideoWall(self, match, tag):

        States = {
           b'\x01': 'On',
           b'\x00': 'Off'
           }

        self.WriteStatus('VideoWall', States[match.group(2)], {'Device ID': str(match.group(1)[0])})

    def SetVideoWallMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
           'Full': 0x01,
           'Natural': 0x00
           }

        checksum = int(hex(0x5C + ID + 0x01 + States[value])[-2:], 16)
        CmdString = pack('>BBBBBB', 0xAA, 0x5C, ID, 0x01, States[value], checksum)
        self.__SetHelper('VideoWallMode', CmdString, value, qualifier)

    def UpdateVideoWallMode(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x5C + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x5C, ID, 0x00, checksum)
        self.__UpdateHelper('VideoWallMode', CmdString, value, qualifier)

    def __MatchVideoWallMode(self, match, tag):

        States = {
           b'\x01': 'Full',
           b'\x00': 'Natural'
           }

        self.WriteStatus('VideoWallMode', States[match.group(2)], {'Device ID': str(match.group(1)[0])})

    def SetVideoWallSize(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        rowState = {
            '1': 0x10,
            '2': 0x20,
            '3': 0x30,
            '4': 0x40,
            '5': 0x50,
            '6': 0x60,
            '7': 0x70,
            '8': 0x80,
            '9': 0x90,
            '10': 0xA0,
            '11': 0xB0,
            '12': 0xC0,
            '13': 0xD0,
            '14': 0xE0,
            '15': 0xF0,
            }
        row = rowState[qualifier['Row']]
        column = int(qualifier['Column'])
        displayNum = int(value)

        if 0 < column <= 15:
            if 0 < displayNum <= 100:
                size = row + column
                if row <= 0x60 and column <= 15 and displayNum <= 90:
                    Valid = True
                elif row <= 0x70 and column < 15 and displayNum <= 98:
                    Valid = True
                elif row <= 0x80 and column < 13 and displayNum <= 96:
                    Valid = True
                elif row <= 0x90 and column < 12 and displayNum <= 99:
                    Valid = True
                elif row <= 0xA0 and column < 11:
                    Valid = True
                elif row <= 0xB0 and column < 10 and displayNum <= 99:
                    Valid = True
                elif row <= 0xC0 and column < 9 and displayNum <= 96:
                    Valid = True
                elif row <= 0xD0 and column < 8 and displayNum <= 91:
                    Valid = True
                elif row <= 0xE0 and column < 8 and displayNum <= 98:
                    Valid = True
                elif row <= 0xF0 and column < 7 and displayNum <= 90:
                    Valid = True
                else:
                    Valid = False
                if Valid:
                    checksum = int(hex(0x89 + ID + 0x02 + size + displayNum)[-2:], 16)
                    CmdString = pack('>BBBBBBB', 0xAA, 0x89, ID, 0x02, size, displayNum, checksum)
                    self.__SetHelper('VideoWallSize', CmdString, value, qualifier)
            else:
                print('Invalid Command for SetVideoWallSize')
        else:
            print('Invalid Command for SetVideoWallSize')

    def UpdateVideoWallSize(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x89 + ID)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x89, ID, 0x00, checksum)
        self.__UpdateHelper('VideoWallSize', CmdString, value, qualifier)

    def __MatchVideoWallSize(self, match, tag):

        value = str(match.group(3)[0])
        SIZE = match.group(2)[0]

        if SIZE < 0x20:
            row = '1'
            COL = SIZE - 0x10
        elif SIZE < 0x30:
            row = '2'
            COL = SIZE - 0x20
        elif SIZE < 0x40:
            row = '3'
            COL = SIZE - 0x30
        elif SIZE < 0x50:
            row = '4'
            COL = SIZE - 0x40
        elif SIZE < 0x60:
            row = '5'
            COL = SIZE - 0x50
        elif SIZE < 0x70:
            row = '6'
            COL = SIZE - 0x60
        elif SIZE < 0x80:
            row = '7'
            COL = SIZE - 0x70
        elif SIZE < 0x90:
            row = '8'
            COL = SIZE - 0x80
        elif SIZE < 0xA0:
            row = '9'
            COL = SIZE - 0x90
        elif SIZE < 0xB0:
            row = '10'
            COL = SIZE - 0xA0
        elif SIZE < 0xC0:
            row = '11'
            COL = SIZE - 0xB0
        elif SIZE < 0xD0:
            row = '12'
            COL = SIZE - 0xC0
        elif SIZE < 0xE0:
            row = '13'
            COL = SIZE - 0xD0
        elif SIZE < 0xF0:
            row = '14'
            COL = SIZE - 0xE0
        elif SIZE < 0xF7:
            row = '15'
            COL = SIZE - 0xF0

        qualifier = {
            'Column': str(COL),
            'Row': row,
            'Device ID': str(match.group(1)[0])
            }

        self.WriteStatus('VideoWallSize', value, qualifier)

    def SetVolume(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        if 0 <= value <= 100:
            checksum = int(hex(0x12 + ID + 0x01 + value)[-2:], 16)
            CmdString = pack('>BBBBBB', 0xAA, 0x12, ID, 0x01, value, checksum)
            self.__SetHelper('Volume', CmdString, value, qualifier)

    def UpdateVolume(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        checksum = int(hex(0x12 + ID + 0x00)[-2:], 16)
        CmdString = pack('>BBBBB', 0xAA, 0x12, ID, 0x00, checksum)
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', match.group(2)[0], {'Device ID': str(match.group(1)[0])})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Reject = False
        if 'Device ID' in qualifier:
            if qualifier['Device ID'] == 'Broadcast':
                Reject = True

        if self.Unidirectional == 'True' or Reject:
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        CommandList = {
            b'\x18' : 'AspectRatio',
            b'\x3D' : 'AutoImage',
            b'\x14' : 'Input',
            b'\x3C' : 'PIPMode',
            b'\x11' : 'Power',
            b'\x5D' : 'SafetyLock',
            b'\x84' : 'VideoWall',
            b'\x5C' : 'VideoWallMode',
            b'\x89' : 'VideoWallSize',
            b'\x12' : 'Volume',
        }
        
        if match.group(2) in CommandList:        
            errorstring = 'DeviceID: {0}, Command: {1}, Error Code: {2}'.format(match.group(1)[0], CommandList[match.group(2)], match.group(3)[0])
        else:
            errorstring = 'DeviceID: {0}, Command: {1}, Error Code: {2}'.format(match.group(1)[0], 'Unknown' , match.group(3[0]))
        print(errorstring)

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.') 

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it was matched with device expectancy. 
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)                
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True 

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